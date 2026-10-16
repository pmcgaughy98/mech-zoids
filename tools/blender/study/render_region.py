# Close-ups of one region of a model from three fixed directions (outer side, back, rear three-quarter), cavity
# shaded, to inspect how a part is built.   -- <file> <out_prefix> cx cy cz extent
import bpy, sys
from mathutils import Vector
args = sys.argv[sys.argv.index("--") + 1:]
p, out = args[0], args[1]
c = Vector((float(args[2]), float(args[3]), float(args[4])))
ext = float(args[5])
bpy.ops.wm.read_factory_settings(use_empty=True)
(bpy.ops.import_scene.fbx if p.lower().endswith(".fbx") else bpy.ops.import_scene.gltf)(filepath=p)
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
sh.color_type = "TEXTURE"
sh.show_cavity = True
sh.cavity_type = "BOTH"
scene.world = bpy.data.worlds.new("w")
scene.world.color = (0.18, 0.19, 0.21)
scene.render.resolution_x, scene.render.resolution_y = 700, 700
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
scene.collection.objects.link(cam)
scene.camera = cam
cam.data.type = "ORTHO"
cam.data.clip_end = 200
for name, view in (("side", (-1, 0, 0)), ("back", (0, -1, 0)), ("q34", (-1, -1, -0.35))):
    d = Vector(view).normalized()
    cam.location = c - d * 40
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = ext
    scene.render.filepath = "%s_%s.png" % (out, name)
    bpy.ops.render.render(write_still=True)
print("RENDERED")
