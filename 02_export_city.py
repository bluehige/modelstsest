"""Blender: export the current edited CC_CozyCity scene to output/edited_city.glb."""
import sys
from pathlib import Path
import bpy

candidates=[]
if globals().get('__file__'): candidates.append(Path(__file__).resolve().parent)
text=getattr(getattr(bpy.context,'space_data',None),'text',None)
if text and text.filepath: candidates.append(Path(bpy.path.abspath(text.filepath)).resolve().parent)
root=next((p for p in candidates if (p/'cozy_city'/'blender_scene.py').is_file()),None)
if root is None: raise RuntimeError('Open 02_export_city.py from the extracted complete repository.')
if str(root) not in sys.path: sys.path.insert(0,str(root))
from cozy_city.blender_scene import export_current_scene
print('Exported:',export_current_scene(root/'output'/'edited_city.glb'))
