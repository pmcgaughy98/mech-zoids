# A stand-in room to prove the room stage wiring (Claude, 2026-10-12): a 14 x 16 x 8 m box shell open on the camera
# side, with the floor's top at the origin, a bay marking and two crates. Follows the room contract in
# scripts/scenes/room_stage_3d.gd. Codex's hangar replaces it.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/make_test_room.py
import bpy, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "art", "rooms", "test_box", "test_box.glb")
MATS = {}


def mat(key, hex_):
    if key not in MATS:
        m = bpy.data.materials.new(key)
        m.use_nodes = True
        c = [int(hex_[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*lin, 1.0)
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
        MATS[key] = m
    return MATS[key]


def box(name, key, hex_, center, size):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    ob.data.materials.append(mat(key, hex_))
    return ob


bpy.ops.wm.read_factory_settings(use_empty=True)
w, d, h = 14.0, 16.0, 8.0
box("floor", "floor", "2c3036", (0, 0, -0.1), (w, d, 0.2))
box("wall_back", "wall", "4a4f57", (0, d / 2 - 0.15, h / 2), (w, 0.3, h))
for s in (-1, 1):
    box("wall_side_%d" % s, "wall", "4a4f57", (s * (w / 2 - 0.15), 0, h / 2), (0.3, d, h))
box("ceiling", "wall", "3b3f46", (0, 0, h + 0.1), (w, d, 0.2))
for s in (-1, 1):   # the bay marking: orange lines either side of the stand point
    box("bay_line_%d" % s, "trim", "d98a40", (s * 3.2, 0, 0.005), (0.1, 7.0, 0.01))
box("crate_0", "crate", "8a8d92", (-5.0, 5.0, 0.6), (1.6, 1.2, 1.2))
box("crate_1", "crate", "8a8d92", (5.2, 4.0, 0.45), (1.2, 1.2, 0.9))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, use_selection=True, export_format="GLB", export_apply=True,
                          export_animations=False)
print("TEST_ROOM_DONE", OUT)
