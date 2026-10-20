"""The combination machine, v1 (Claude, 2026-10-19; Preston: "use creature factory and everything else that we use to
mass manufacture the new combination creature for all 6. It doesn't have to be perfect right now obviously just v1.
Use the synthesis as well").

    "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_combiner_v1.py

Takes the six finished machines straight from the factory (docs/art/3d/<id>.blend), freezes each in its rest pose,
turns and scales it into one body part and joins them into docs/art/3d/combiner_v1.blend, which the factory's sprite
renderer takes like any machine. Nothing is remodelled: v1 is the proportion and silhouette test.

Proportions measured from Fall of Cybertron's Bruticus (structure only; docs/reference/combiner-v1-2026-10-19.md),
as fractions of the combined height H: legs 0 to 0.40 H, stance 0.52 H wide; torso to 0.85 H; arms from the
shoulders at 0.80 H down to the fists at 0.32 H, 0.89 H across; the back unit rising past the head.
Assignment (a proposal, Preston's to change): gorilla torso and head, wolf left arm (its head the fist), kangaroo
right arm (its gloves at the hand), hippo left leg (its head the foot), pangolin right leg, shoebill on the back.
"""
import bpy, math, os
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "docs", "art", "3d", "combiner_v1.blend")
H = 9.0   # the combined height in metres (Bruticus stands about 3.1 times one member's height)
# id: (role, long-axis rotation, target height of the part as a fraction of H, centre x, bottom z, centre y), all * H
X90 = Matrix.Rotation(math.radians(90), 4, "X")     # nose (-y) down: a limb with the head at the hand or foot
XM90 = Matrix.Rotation(math.radians(-90), 4, "X")   # nose up: the torso, head on top, belly to the front
I = Matrix.Identity(4)
SLOTS = {
    "ape_l":      ("torso",     XM90, 0.50, 0.0,   0.38,  0.0),
    "wolf_m":     ("left arm",  X90,  0.50, 0.36,  0.30, -0.02),
    "kangaroo_m": ("right arm", X90,  0.50, -0.36, 0.30, -0.02),
    "hippo_m":    ("left leg",  X90,  0.42, 0.15,  0.0,   0.0),
    "pangolin_m": ("right leg", X90,  0.42, -0.15, 0.0,   0.0),
    "shoebill_m": ("back",      I,    0.62, 0.0,   0.48,  0.16),
}
FILES = {"ape_l": "ape_l_v2"}   # the gorilla's current build writes ape_l_v2.blend (ape_l.blend is an old one)
# the side of +x is the machine's left when it faces -y (the factory's convention: .L is +x)


def load(mid):
    path = os.path.join(ROOT, "docs", "art", "3d", FILES.get(mid, mid) + ".blend")
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    objs = [o for o in dst.objects if o is not None]
    for o in objs:
        bpy.context.scene.collection.objects.link(o)
    rig = next((o for o in objs if o.type == "ARMATURE"), None)
    if rig:
        rig.data.pose_position = "REST"
    meshes = [o for o in objs if o.type == "MESH"]
    body = max(meshes, key=lambda o: len(o.data.polygons))
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(body.evaluated_get(dg))
    frozen = bpy.data.objects.new(mid + "_part", me)
    frozen.matrix_world = body.matrix_world.copy()
    bpy.context.scene.collection.objects.link(frozen)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    return frozen


def bbox(o):
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs)))
    mx = Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs)))
    return mn, mx


def place(o, rot, height, cx, bottom, cy):
    o.matrix_world = rot @ o.matrix_world
    bpy.context.view_layer.update()
    mn, mx = bbox(o)
    k = height * H / (mx.z - mn.z)
    o.matrix_world = Matrix.Scale(k, 4) @ o.matrix_world
    bpy.context.view_layer.update()
    mn, mx = bbox(o)
    c = (mn + mx) / 2
    o.matrix_world = Matrix.Translation(Vector((cx * H - c.x, cy * H - c.y, bottom * H - mn.z))) @ o.matrix_world
    bpy.context.view_layer.update()
    return k


bpy.ops.wm.read_factory_settings(use_empty=True)
parts = []
for mid, (role, rot, hgt, cx, bottom, cy) in SLOTS.items():
    o = load(mid)
    k = place(o, rot, hgt, cx, bottom, cy)
    mn, mx = bbox(o)
    print("COMBINER_PART %-11s %-9s scale %.2f  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (mid, role, k, mn.x, mx.x, mn.y, mx.y, mn.z, mx.z))
    parts.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in parts:
    o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.name = "combiner_v1"
mn, mx = bbox(ob)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("COMBINER_DONE dims=%s tris=%d" % (tuple(round(v, 2) for v in (mx - mn)), sum(len(p.vertices) - 2 for p in ob.data.polygons)))
