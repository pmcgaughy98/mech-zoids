import bpy, math, os, sys, json
import numpy as np

out = sys.argv[sys.argv.index("--") + 1]
os.makedirs(out, exist_ok=True)
res = {}
scn = bpy.context.scene
R = 64
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1.0)
bpy.ops.object.shade_smooth()
cd = bpy.data.cameras.new("Cam"); cd.type = 'ORTHO'; cd.ortho_scale = 2.2
cam = bpy.data.objects.new("Cam", cd); scn.collection.objects.link(cam)
cam.location = (0, -5, 0); cam.rotation_euler = (math.radians(90), 0, 0)  # looks along +Y
scn.camera = cam
scn.render.resolution_x = R; scn.render.resolution_y = R; scn.render.resolution_percentage = 100
scn.render.film_transparent = True
vl = scn.view_layers[0]
res["ctx_view_layer"] = bpy.context.view_layer.name if bpy.context.view_layer else None
vl.use_pass_normal = True
vl.use_pass_z = True
res["use_compositing_default"] = scn.render.use_compositing
scn.render.use_compositing = False


def set_ml():
    s = scn.render.image_settings
    if hasattr(s, "media_type"):
        s.media_type = 'MULTI_LAYER_IMAGE'
    try:
        s.file_format = 'OPEN_EXR_MULTILAYER'
    except TypeError:
        s.file_format = 'OPEN_EXR'
    s.color_depth = '32'


def read(p):
    import OpenImageIO as oiio
    inp = oiio.ImageInput.open(p); spec = inp.spec(); names = list(spec.channelnames)
    px = np.array(inp.read_image(0, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
    inp.close()
    nidx = [i for i, n in enumerate(names) if "Normal" in n]
    H = spec.height
    pick = lambda row, col: [round(float(px[row, col, i]), 3) for i in nidx]
    return {"channels": names,
            "normal_center": pick(H // 2, H // 2),
            "normal_top(screen up)": pick(int(H * 0.19), H // 2),
            "normal_right(screen right)": pick(H // 2, int(H * 0.81))}


for eng in ['CYCLES', 'BLENDER_EEVEE']:
    try:
        scn.render.engine = eng
        if eng == 'CYCLES':
            scn.cycles.samples = 1; scn.cycles.device = 'CPU'
        set_ml()
        scn.render.filepath = os.path.join(out, eng + "_ws_")
        bpy.ops.render.render(write_still=True)
        f = [x for x in os.listdir(out) if x.startswith(eng + "_ws_")]
        res[eng + "_write_still"] = read(os.path.join(out, f[0])) if f else "no file"
        p2 = os.path.join(out, eng + "_save_render.exr")
        bpy.data.images['Render Result'].save_render(p2, scene=scn)
        res[eng + "_save_render"] = read(p2)
    except Exception as e:
        res[eng] = "error: " + str(e)[:300]

print("RESULT_JSON " + json.dumps(res))
