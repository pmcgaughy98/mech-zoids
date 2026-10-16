# Look-compare (Claude, 2026-10-13): the machine's blend beside Preston's reference at the model's exact height, side
# orthographic, rendered headless. Same picture the live-Blender version made, but repeatable from the shell.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b docs/art/3d/<id>.blend -P tools/art/look_compare.py -- <id> <out.png>
import bpy, math, bmesh, sys
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
mid, out = argv[0], argv[1]
ref = "docs/art/reference/starters/%s.png" % mid
sc = bpy.context.scene
ob = max((o for o in sc.objects if o.type == "MESH"), key=lambda o: o.dimensions.length)
rig = next((o for o in sc.objects if o.type == "ARMATURE"), None)
if rig:
    rig.data.pose_position = "REST"
for o in sc.objects:
    if o.type in ("CAMERA", "LIGHT"):
        o.hide_render = True
img = bpy.data.images.load(bpy.path.abspath("//../../../" + ref) if not ref.startswith("/") else ref)
h = ob.dimensions.z; w = h * img.size[0] / img.size[1]
me = bpy.data.meshes.new("reference_plane"); bm = bmesh.new()
y0 = ob.location.y - ob.dimensions.y / 2 - 0.8
vs = [bm.verts.new((0, y0, 0)), bm.verts.new((0, y0 - w, 0)), bm.verts.new((0, y0 - w, h)), bm.verts.new((0, y0, h))]
f = bm.faces.new(vs); uv = bm.loops.layers.uv.new()
for loop, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
    loop[uv].uv = co
bm.to_mesh(me); bm.free()
pl = bpy.data.objects.new("reference_plane", me); sc.collection.objects.link(pl)
mat = bpy.data.materials.new("reference_mat"); mat.use_nodes = True; nt = mat.node_tree
tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
nt.links.new(tex.outputs["Color"], next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"]); me.materials.append(mat)
span = ob.dimensions.y + w + 0.8
cam_data = bpy.data.cameras.new("compare_cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = max(h * 2.0, span) * 1.1
cam = bpy.data.objects.new("compare_cam", cam_data); sc.collection.objects.link(cam); sc.camera = cam
cam.location = Vector((14, (y0 - w + ob.location.y + ob.dimensions.y / 2) / 2, h / 2)); cam.rotation_euler = (math.radians(90), 0, math.radians(90))
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "FLAT"; sc.display.shading.color_type = "TEXTURE"
sc.render.resolution_x, sc.render.resolution_y = 1400, 700; sc.render.film_transparent = False
sc.world = sc.world or bpy.data.worlds.new("w"); sc.world.color = (0.86, 0.86, 0.86)
sc.render.filepath = bpy.path.abspath("//../../../" + out) if not out.startswith("/") else out
bpy.ops.render.render(write_still=True)
print("LOOK_COMPARE %s -> %s model %s" % (mid, out, tuple(round(v, 2) for v in ob.dimensions)))
