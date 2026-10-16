"""Render separate texture snapshots using the creature factory's own sprite renderer.
Never writes a live machine asset, source .blend, or installed sprite.
"""
from pathlib import Path
import os
import bpy
import bmesh

ROOT = Path(__file__).resolve().parents[2]
JOB = ROOT / 'docs/art/3d/gorilla-texture-2026-10-13'
source = (ROOT / 'tools/blender/render_sprite_views.py').read_text(encoding='utf-8')
needle = 'ROOT = os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", ".."))'
assert source.count(needle) == 1
source = source.replace(needle, 'ROOT = ' + repr(str(ROOT)))
(JOB / 'sprite-renderer-snapshot.py').write_text(source, encoding='utf-8')
# Exact stance and pixel settings from tools/art/ape_round.sh, inspected 2026-10-13.
os.environ['SPRITE_STANCE'] = 'base=19;R_leg=16;L_leg=3;L_arm=27'
os.environ['SPRITE_CLIP'] = 'stance'
os.environ['SPRITE_VIEWS'] = 'e s se'
for version in ('before', 'after'):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(JOB / version / 'ape_l.glb'))
    for rig in [o for o in bpy.context.scene.objects if o.type == 'ARMATURE']:
        rotation = rig.rotation_quaternion.to_euler('XYZ') if rig.rotation_mode == 'QUATERNION' else rig.rotation_euler.copy()
        rig.rotation_mode = 'XYZ'  # the native factory renderer turns the rig with Euler angles
        rig.rotation_euler = rotation
    # glTF splits vertices at UV and normal boundaries. Restore connected geometry
    # for the renderer's loose-part ID pass; existing face-corner UVs are retained.
    for ob in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.000001)
        bm.to_mesh(ob.data)
        bm.free()
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        bsdf = next((n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf and bsdf.inputs['Base Color'].is_linked:
            node = bsdf.inputs['Base Color'].links[0].from_node
            if node.type == 'TEX_IMAGE':
                material.node_tree.nodes.active = node
    os.environ['SPRITE_OUT'] = str(JOB / version / 'sprite-renders')
    exec(compile(source, str(ROOT / 'tools/blender/render_sprite_views.py'), 'exec'), {'__name__': '__main__'})
print('GORILLA_TEXTURE_SPRITE_PREVIEW_DONE')
