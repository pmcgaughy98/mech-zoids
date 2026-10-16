# Head-only close-ups of a machine: side, head-on, three-quarter and top, cavity shaded. The head is taken as the
# front end of the long axis (pass "B" as the third argument if it is at the other end), top 60% of the height.
import bpy, sys
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
p, out, end = args[0], args[1], (args[2] if len(args) > 2 else "A")
if p.lower().endswith(".blend"):
    bpy.ops.wm.open_mainfile(filepath=p)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    (bpy.ops.import_scene.fbx if p.lower().endswith(".fbx") else bpy.ops.import_scene.gltf)(filepath=p)
scene = bpy.context.scene
obs = [o for o in bpy.data.objects if o.type == "MESH"]
lo = Vector((1e9,) * 3)
hi = Vector((-1e9,) * 3)
for o in obs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        lo = Vector(map(min, lo, w))
        hi = Vector(map(max, hi, w))
size = hi - lo
L = 0 if size.x > size.y else 1
sgn = -1 if end == "A" else 1
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "TEXTURE"
sh.show_cavity = True
sh.cavity_type = "BOTH"
if scene.world is None:
    scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.18, 0.19, 0.21)
scene.render.resolution_x, scene.render.resolution_y = 800, 800
scene.render.film_transparent = False
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_end = 200
ec = (lo + hi) / 2
ec[L] = (lo[L] if sgn < 0 else hi[L]) - sgn * size[L] * 0.13
ec.z = lo.z + size.z * 0.72
ext = size.z * 0.5
side = Vector((0, 1, 0)) if L == 0 else Vector((1, 0, 0))
along = Vector((0, 0, 0))
along[L] = sgn
def shoot(view_dir, name):
    d = Vector(view_dir).normalized()
    cam.location = ec - d * 40
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = ext
    scene.render.filepath = "%s_%s.png" % (out, name)
    bpy.ops.render.render(write_still=True)
shoot(side, "side")
shoot(-along, "front")
shoot((-along + side).normalized() + Vector((0, 0, -0.5)), "q34")
shoot(Vector((0, 0, -1)) + side * 0.001, "top")
print("RENDERED", out)
