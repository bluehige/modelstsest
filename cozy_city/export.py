"""Standard-library glTF 2.0 / GLB export; shared meshes, flat normals, vertex colours."""
import json
import struct
from math import sin, cos, sqrt
from pathlib import Path
from .mesh import sub, cross, unit, linear
from .layout import stats, validate_world
from . import __version__


def expanded(mesh, linear_colors=True):
    pos, normals, colors = [], [], []
    for f,c in zip(mesh.faces,mesh.colors):
        a,b,d = (mesh.vertices[i] for i in f)
        normal = unit(cross(sub(b,a),sub(d,a)))
        col = tuple(linear(v) for v in c) if linear_colors else c
        for i in f:
            pos.extend(mesh.vertices[i]); normals.extend(normal); colors.extend((*col,1.0))
    return pos,normals,colors


def glb_bytes(world):
    errors = validate_world(world)
    if errors:
        raise ValueError('\n'.join(errors[:20]))
    binary = bytearray()
    doc = dict(asset=dict(version='2.0',generator='Cozy City '+__version__),
               scene=0,scenes=[dict(nodes=[0])],
               nodes=[dict(name='CC_Zup_to_Yup',rotation=[-sqrt(.5),0,0,sqrt(.5)],children=[])],
               meshes=[],buffers=[],bufferViews=[],accessors=[],
               materials=[dict(name='CC_VertexColour',
                               pbrMetallicRoughness=dict(baseColorFactor=[1,1,1,1],metallicFactor=0,roughnessFactor=.88),
                               doubleSided=False)])
    def accessor(values, width, bounds=False):
        while len(binary)%4: binary.append(0)
        offset = len(binary)
        binary.extend(struct.pack('<'+'f'*len(values),*values))
        view = len(doc['bufferViews'])
        doc['bufferViews'].append(dict(buffer=0,byteOffset=offset,byteLength=len(values)*4,target=34962))
        a = dict(bufferView=view,componentType=5126,count=len(values)//width,type=f'VEC{width}')
        if bounds:
            a['min']=[min(values[i::width]) for i in range(width)]
            a['max']=[max(values[i::width]) for i in range(width)]
        doc['accessors'].append(a)
        return len(doc['accessors'])-1
    mesh_ids = {}
    for key,m in world['assets'].items():
        pos,normals,colors = expanded(m)
        attrs = dict(POSITION=accessor(pos,3,True),NORMAL=accessor(normals,3),COLOR_0=accessor(colors,4))
        mesh_ids[key]=len(doc['meshes'])
        doc['meshes'].append(dict(name=key,primitives=[dict(attributes=attrs,material=0,mode=4)]))
    for it in world['instances']:
        node = dict(name=it['name'],mesh=mesh_ids[it['asset']],translation=list(it['location']),
                    rotation=[0,0,sin(it['angle']/2),cos(it['angle']/2)],scale=[it['scale']]*3,
                    extras=dict(cc_asset=it['asset'],cc_cell=it['cell'],cc_zone=it['zone']))
        doc['nodes'][0]['children'].append(len(doc['nodes']))
        doc['nodes'].append(node)
    doc['buffers']=[dict(byteLength=len(binary))]
    doc['extras']=dict(coordinates='glTF Y-up; authoring data are Z-up metres',stats=stats(world))
    raw = json.dumps(doc,separators=(',',':'),allow_nan=False).encode()
    raw += b' '*((-len(raw))%4)
    binary.extend(b'\0'*((-len(binary))%4))
    size = 12+8+len(raw)+8+len(binary)
    return (struct.pack('<4sII',b'glTF',2,size)+struct.pack('<I4s',len(raw),b'JSON')+raw+
            struct.pack('<I4s',len(binary),b'BIN\0')+binary)


def manifest(world):
    return dict(schema_version=1,generator_version=__version__,coordinates='metres; +Z up; +X right; building front -Y',
                config=world['config'],stats=stats(world),instances=world['instances'],
                assets={k:dict(category=m.category,triangles=len(m.faces),bounds=m.bounds())
                        for k,m in world['assets'].items()},
                building_bounds=world['lots'],points_of_interest=world['points_of_interest'],
                limitations=['Building bounds are metadata, not physics colliders.',
                             'No interiors, LOD, navigation, or runtime game logic.'])


def export_world(world, output, force=False):
    output = Path(output)
    files = ['city.glb','manifest.json','preview.html']
    if not force and any((output/f).exists() for f in files):
        raise FileExistsError('Generated files already exist. Choose another folder or pass --force.')
    output.mkdir(parents=True,exist_ok=True)
    (output/'city.glb').write_bytes(glb_bytes(world))
    (output/'manifest.json').write_text(json.dumps(manifest(world),indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    template = (Path(__file__).parent/'viewer.html').read_text(encoding='utf-8')
    data = dict(size=world['config']['map_size'],stats=stats(world),instances=world['instances'],
                assets={k:expanded(m) for k,m in world['assets'].items()})
    payload = json.dumps(data,separators=(',',':'),allow_nan=False).replace('</','<\\/')
    (output/'preview.html').write_text(template.replace('__CITY_DATA__',payload),encoding='utf-8')
    return stats(world)
