"""Blender 4.2+ integration. API-targeted, not runtime-tested in this environment.

Builds in a new, owned scene. Never clears the user's current scene.
Meshes are linked, not copied. Preview lighting is deliberately separate.
"""
import json
from pathlib import Path
from math import radians
import bpy
from mathutils import Vector
from .layout import build_world,validate_world,stats
from .mesh import linear

OWNER = 'bluehige.cozy_city.v1'
SCENE = 'CC_CozyCity'
ROOT = Path(__file__).resolve().parent.parent


def owned(data):
    data['cc_owner'] = OWNER
    return data


def remove_scene(scene):
    if scene is None or scene.get('cc_owner') != OWNER:
        return
    objects = list(scene.objects)
    bpy.data.scenes.remove(scene)
    for obj in objects:
        if obj.get('cc_owner')==OWNER and not obj.users_scene:
            bpy.data.objects.remove(obj,do_unlink=True)
    for groups in (bpy.data.collections,bpy.data.meshes,bpy.data.cameras,
                   bpy.data.lights,bpy.data.worlds,bpy.data.materials):
        changed=True
        while changed:
            changed=False
            for item in list(groups):
                if item.get('cc_owner')==OWNER and item.users==0:
                    groups.remove(item);changed=True


def make_material():
    mat=owned(bpy.data.materials.new('CC_VertexColour'))
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    bs=nodes.get('Principled BSDF')
    col=nodes.new('ShaderNodeVertexColor');col.layer_name='Color'
    mat.node_tree.links.new(col.outputs['Color'],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.88
    mat.use_backface_culling=True
    return mat


def make_mesh(recipe,material):
    mesh=owned(bpy.data.meshes.new('CC_'+recipe.name))
    mesh.from_pydata(recipe.vertices,[],recipe.faces)
    mesh.update();mesh.materials.append(material)
    attr=mesh.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    colors=[]
    for c in recipe.colors:
        rgba=[linear(v) for v in c]+[1.0]
        colors.extend(rgba*3)
    attr.data.foreach_set('color',colors)
    mesh.color_attributes.active_color_index=0
    mesh['cc_asset']=recipe.name
    # Flat shading is the mesh default. Do not add bevel/subdivision modifiers.
    return mesh


def camera(scene,col,name,location,target,scale):
    data=owned(bpy.data.cameras.new(name))
    obj=owned(bpy.data.objects.new(name,data));col.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=scale;data.clip_end=2000
    return obj


def preview(scene,col,size):
    scene.camera=camera(scene,col,'CC_Overview',(size*.85,-size*1.05,size*.9),(0,0,3),size*1.6)
    camera(scene,col,'CC_TownSquare',(42,-58,43),(0,0,6),85)
    camera(scene,col,'CC_Top',(0,-.01,size*1.5),(0,0,0),size*1.8)
    light=owned(bpy.data.lights.new('CC_Sun','SUN'))
    light.energy=2.2;light.angle=.16;light.color=(1,.93,.81)
    sun=owned(bpy.data.objects.new('CC_Sun',light));col.objects.link(sun)
    sun.rotation_euler=(radians(26),radians(-22),radians(-35))
    world=owned(bpy.data.worlds.new('CC_World'));world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.63,.77,.81,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.55
    scene.world=world
    scene.render.engine='CYCLES'
    scene.cycles.samples=48;scene.cycles.use_denoising=True
    scene.render.resolution_x=1920;scene.render.resolution_y=1080
    scene.render.resolution_percentage=100
    try: scene.view_settings.view_transform='AgX'
    except (TypeError,ValueError): pass


def build_scene(values=None):
    if bpy.app.version<(4,2,0):
        raise RuntimeError('Blender 4.2 or newer is the target API.')
    world=build_world(values)
    errors=validate_world(world)
    if errors: raise ValueError('\n'.join(errors[:20]))
    old=bpy.data.scenes.get(SCENE)
    if old is not None and old.get('cc_owner')!=OWNER:
        raise RuntimeError('A user-owned CC_CozyCity scene already exists. Rename it; it will not be deleted.')
    previous=bpy.context.window.scene if bpy.context.window else None
    scene=owned(bpy.data.scenes.new(SCENE+'__BUILDING'))
    try:
        if bpy.context.window: bpy.context.window.scene=scene
        scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
        material=make_material()
        meshes={k:make_mesh(m,material) for k,m in world['assets'].items()}
        collections={}
        for it in world['instances']:
            category=world['assets'][it['asset']].category
            if category not in collections:
                c=owned(bpy.data.collections.new('CC_'+category))
                scene.collection.children.link(c);collections[category]=c
            obj=owned(bpy.data.objects.new(it['name'],meshes[it['asset']]))
            collections[category].objects.link(obj)
            obj.location=it['location'];obj.rotation_euler=(0,0,it['angle'])
            obj.scale=(it['scale'],)*3
            obj['cc_role']='instance';obj['cc_asset']=it['asset']
            obj['cc_cell']=it['cell'];obj['cc_zone']=it['zone']
        previews=owned(bpy.data.collections.new('CC_Preview_Cameras_Lights'))
        scene.collection.children.link(previews)
        preview(scene,previews,world['config']['map_size'])
        scene['cc_config']=json.dumps(world['config'])
        scene['cc_stats']=json.dumps(stats(world));scene['cc_root']=str(ROOT)
        if hasattr(scene,'cc_settings'):
            scene.cc_settings.preset=world['config']['preset']
            scene.cc_settings.seed=world['config']['seed']
            scene.cc_settings.trees=world['config']['trees'];scene.cc_settings.cars=world['config']['cars']
    except Exception:
        if bpy.context.window and previous: bpy.context.window.scene=previous
        remove_scene(scene)
        raise
    remove_scene(old)
    scene.name=SCENE
    if bpy.context.screen:
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.clip_end=2000
                area.spaces.active.shading.type='MATERIAL'
                area.spaces.active.region_3d.view_perspective='CAMERA'
    print('Cozy City created:',stats(world))
    return scene


def export_current_scene(output=None):
    """Exports actual edited scene meshes, not a regenerated seed/layout."""
    scene=bpy.context.scene
    if scene.get('cc_owner')!=OWNER:
        raise RuntimeError('Switch to the generated CC_CozyCity scene first.')
    output=Path(output) if output else ROOT/'output'/'edited_city.glb'
    output.parent.mkdir(parents=True,exist_ok=True)
    if bpy.context.mode!='OBJECT':
        raise RuntimeError('Switch to Object Mode before exporting.')
    view=bpy.context.view_layer
    selected=list(bpy.context.selected_objects);active=view.objects.active
    objects=[o for o in scene.objects if o.type=='MESH' and o.get('cc_role')=='instance']
    unavailable=[o.name for o in objects if o.name not in view.objects or not o.visible_get(view_layer=view)]
    if unavailable:
        raise RuntimeError('Unhide all generated collections/objects before exporting: '+', '.join(unavailable[:5]))
    try:
        for obj in selected: obj.select_set(False)
        for obj in objects: obj.select_set(True)
        if objects: view.objects.active=objects[0]
        result=bpy.ops.export_scene.gltf(filepath=str(output),export_format='GLB',
                    use_selection=True,export_yup=True,export_extras=True,
                    export_cameras=False,export_lights=False)
        if 'FINISHED' not in result: raise RuntimeError('Blender glTF exporter did not finish.')
        placements=[dict(name=o.name,asset=o.get('cc_asset'),
                        matrix_world=[list(row) for row in o.matrix_world]) for o in objects]
        output.with_suffix('.placements.json').write_text(json.dumps(dict(
            coordinates='Blender world matrix; metres, Z up. GLB is Y up.',instances=placements),indent=2),encoding='utf-8')
    finally:
        for obj in objects: obj.select_set(False)
        for obj in selected: obj.select_set(True)
        view.objects.active=active
    return output


class CC_Settings(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(name='Preset',items=[('city','City / 도시','300 m'),('village','Village / 마을','180 m')])
    seed: bpy.props.IntProperty(name='Seed / 배치 번호',default=42,min=0,max=2147483647)
    trees: bpy.props.BoolProperty(name='Trees / 나무',default=True)
    cars: bpy.props.BoolProperty(name='Cars / 차량',default=True)


class CC_OT_build(bpy.types.Operator):
    bl_idname='cc.build';bl_label='Generate / 생성·재생성'
    bl_description='Replace only the previous generated scene; manual edits there are replaced'
    def invoke(self,context,event):
        return context.window_manager.invoke_confirm(self,event)
    def execute(self,context):
        p=context.scene.cc_settings
        try: build_scene(dict(preset=p.preset,seed=p.seed,trees=p.trees,cars=p.cars))
        except Exception as e:
            self.report({'ERROR'},str(e));return {'CANCELLED'}
        return {'FINISHED'}


class CC_OT_export(bpy.types.Operator):
    bl_idname='cc.export';bl_label='Export edited scene / GLB 내보내기'
    def execute(self,context):
        try: path=export_current_scene()
        except Exception as e:
            self.report({'ERROR'},str(e));return {'CANCELLED'}
        self.report({'INFO'},str(path));return {'FINISHED'}


class CC_PT_panel(bpy.types.Panel):
    bl_label='Cozy City';bl_idname='CC_PT_panel'
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Cozy City'
    def draw(self,context):
        p=context.scene.cc_settings
        for field in ('preset','seed','trees','cars'): self.layout.prop(p,field)
        self.layout.operator('cc.build');self.layout.operator('cc.export')
        self.layout.label(text='Rebuild replaces generated-scene edits.')


def register():
    if hasattr(bpy.types.Scene,'cc_settings'): del bpy.types.Scene.cc_settings
    classes=(CC_Settings,CC_OT_build,CC_OT_export,CC_PT_panel)
    for cls in reversed(classes):
        old=getattr(bpy.types,cls.__name__,None)
        if old: bpy.utils.unregister_class(old)
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.cc_settings=bpy.props.PointerProperty(type=CC_Settings)
