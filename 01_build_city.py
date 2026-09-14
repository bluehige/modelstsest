"""Blender: Scripting > Open this file > Alt+P. Extract the whole package first."""
import sys
import json
from pathlib import Path
import bpy

candidates=[]
if globals().get('__file__'): candidates.append(Path(__file__).resolve().parent)
text=getattr(getattr(bpy.context,'space_data',None),'text',None)
if text and text.filepath: candidates.append(Path(bpy.path.abspath(text.filepath)).resolve().parent)
root=next((p for p in candidates if (p/'cozy_city'/'blender_scene.py').is_file()),None)
if root is None: raise RuntimeError('Extract the complete repository and open 01_build_city.py. Do not paste it into an unnamed text block.')
if str(root) not in sys.path: sys.path.insert(0,str(root))
# Reload this package only; never clear unrelated Python modules.
for name in list(sys.modules):
    if name=='cozy_city' or name.startswith('cozy_city.'): del sys.modules[name]
from cozy_city.blender_scene import register,build_scene
register()
cfg=json.loads((root/'city_config.json').read_text(encoding='utf-8'))
build_scene(cfg)
