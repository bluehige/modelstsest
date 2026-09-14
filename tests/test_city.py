import hashlib
import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from cozy_city.layout import build_world,validate_world,stats,config
from cozy_city.export import glb_bytes,export_world,expanded
from cozy_city.mesh import Mesh,rgb,cross,sub
from cozy_city.assets import gable


class CityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.city=build_world();cls.village=build_world({'preset':'village'})
        cls.glb=glb_bytes(cls.city)
        size,kind=struct.unpack_from('<I4s',cls.glb,12)
        cls.doc=json.loads(cls.glb[20:20+size]);cls.json_size=size

    def test_default_sizes(self):
        self.assertEqual(stats(self.city)['map_size_m'],300)
        self.assertEqual(stats(self.village)['map_size_m'],180)

    def test_default_buildings(self):
        self.assertEqual(len(self.city['lots']),93)
        self.assertEqual(len(self.village['lots']),29)

    def test_default_geometry(self):
        self.assertEqual(validate_world(self.city),[])
        self.assertEqual(validate_world(self.village),[])

    def test_deterministic(self):
        self.assertEqual(hashlib.sha256(self.glb).digest(),hashlib.sha256(glb_bytes(build_world())).digest())

    def test_seed_changes_layout(self):
        self.assertNotEqual(self.city['instances'],build_world({'seed':43})['instances'])

    def test_preset_and_seed_sweep(self):
        for preset in ('city','village'):
            for seed in (0,1,7,99,2147483647):
                with self.subTest(preset=preset,seed=seed):
                    self.assertEqual(validate_world(build_world(dict(preset=preset,seed=seed))),[])

    def test_minimum_and_maximum_settings(self):
        for blocks,block_size,road in ((3,38,7),(5,38,16),(7,60,16)):
            with self.subTest(blocks=blocks):
                w=build_world(dict(blocks=blocks,block_size=block_size,road_width=road))
                self.assertEqual(validate_world(w),[])

    def test_bad_config(self):
        for values in ({'preset':'forest'},{'seed':True},{'seed':-1},{'blocks':4},
                       {'road_width':0},{'block_size':float('nan')},{'trees':1},{'unknown':0}):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):config(values)

    def test_toggles_remove_only_optional_categories(self):
        other=build_world(dict(trees=False,cars=False))
        cats=stats(other)['categories']
        self.assertNotIn('Trees',cats);self.assertNotIn('Vehicles',cats)
        def buildings(w):
            return [(i['asset'],i['location'],i['angle']) for i in w['instances']
                    if w['assets'][i['asset']].category=='Buildings']
        self.assertEqual(buildings(self.city),buildings(other))

    def test_names_unique(self):
        names=[i['name'] for i in self.city['instances']]
        self.assertEqual(len(names),len(set(names)))

    def test_meshes_shared(self):
        self.assertLess(len(self.city['assets']),len(self.city['instances'])/10)
        self.assertEqual(len(self.doc['meshes']),len(self.city['assets']))

    def test_triangle_budget(self):
        self.assertLess(stats(self.city)['placed_triangles'],250000)
        self.assertLess(stats(self.village)['placed_triangles'],80000)

    def test_glb_header(self):
        magic,version,total=struct.unpack_from('<4sII',self.glb)
        self.assertEqual((magic,version,total),(b'glTF',2,len(self.glb)))
        self.assertEqual(len(self.glb)%4,0)

    def test_glb_chunks(self):
        pos=20+self.json_size
        length,kind=struct.unpack_from('<I4s',self.glb,pos)
        self.assertEqual(kind,b'BIN\0');self.assertEqual(pos+8+length,len(self.glb))

    def test_glb_buffer_ranges(self):
        for view in self.doc['bufferViews']:
            self.assertEqual(view['byteOffset']%4,0)
            self.assertLessEqual(view['byteOffset']+view['byteLength'],self.doc['buffers'][0]['byteLength'])

    def test_glb_accessors(self):
        for m in self.doc['meshes']:
            attrs=m['primitives'][0]['attributes']
            counts=[self.doc['accessors'][v]['count'] for v in attrs.values()]
            self.assertEqual(len(set(counts)),1)
            self.assertEqual(counts[0]%3,0)

    def test_glb_nodes_and_axis(self):
        self.assertEqual(len(self.doc['nodes'])-1,len(self.city['instances']))
        root=self.doc['nodes'][0]
        self.assertAlmostEqual(root['rotation'][0],-math.sqrt(.5))
        self.assertEqual(len(root['children']),len(self.city['instances']))

    def test_flat_normals(self):
        m=next(iter(self.city['assets'].values()))
        pos,normals,colors=expanded(m)
        for i in range(0,len(normals),9):
            self.assertEqual(normals[i:i+3],normals[i+3:i+6])
            self.assertAlmostEqual(sum(v*v for v in normals[i:i+3]),1)
        self.assertTrue(all(0<=c<=1 for c in colors))

    def test_gable_outward_volume(self):
        m=Mesh('test');gable(m,8,10,6,3,rgb('bb8866'))
        volume=sum(sum(m.vertices[f[0]][k]*cross(m.vertices[f[1]],m.vertices[f[2]])[k]
                       for k in range(3))/6 for f in m.faces)
        self.assertGreater(volume,119)

    def test_reject_degenerate_mesh(self):
        w=build_world({'preset':'village'})
        m=next(iter(w['assets'].values()))
        m.faces[0]=(0,0,0)
        self.assertTrue(any('degenerate' in e for e in validate_world(w)))

    def test_export_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_world(self.village,tmp)
            self.assertTrue((Path(tmp)/'city.glb').is_file())
            text=(Path(tmp)/'preview.html').read_text(encoding='utf-8')
            self.assertNotIn('__CITY_DATA__',text)
            with self.assertRaises(FileExistsError):export_world(self.village,tmp)
            export_world(self.village,tmp,force=True)


if __name__=='__main__':unittest.main()
