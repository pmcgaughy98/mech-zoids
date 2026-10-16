import bpy, math, os, sys, json
import numpy as np

out = sys.argv[sys.argv.index("--") + 1]
os.makedirs(out, exist_ok=True)
res = {"blender": bpy.app.version_string}
scn = bpy.context.scene
R = 64
OS = 2.2

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=64, radius=1.0)
bpy.ops.object.shade_smooth()
cd = bpy.data.cameras.new("Cam"); cd.type = 'ORTHO'; cd.ortho_scale = OS
cam = bpy.data.objects.new("Cam", cd); scn.collection.objects.link(cam)
# Front view: camera at -Y looking toward +Y, so world space != camera space
cam.location = (0, -5, 0); cam.rotation_euler = (math.radians(90), 0, 0)
scn.camera = cam
scn.render.resolution_x = R; scn.render.resolution_y = R; scn.render.resolution_percentage = 100
scn.render.film_transparent = True
res["default_view_transform"] = scn.view_settings.view_transform


def set_fmt(multilayer=False):
    s = scn.render.image_settings
    if hasattr(s, "media_type"):
        try:
            s.media_type = 'MULTI_LAYER_IMAGE' if multilayer else 'IMAGE'
        except Exception as e:
            res.setdefault("fmt_err", []).append(str(e))
    if multilayer:
        try:
            s.file_format = 'OPEN_EXR_MULTILAYER'
        except TypeError:
            s.file_format = 'OPEN_EXR'
        s.color_depth = '32'
    else:
        s.file_format = 'PNG'; s.color_mode = 'RGBA'; s.color_depth = '8'


def render(path):
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    # find written file
    d = os.path.dirname(path); b = os.path.basename(path)
    for f in os.listdir(d):
        if f.startswith(b):
            return os.path.join(d, f)
    return None


def srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def analyse_png(p):
    img = bpy.data.images.load(p)
    img.colorspace_settings.name = 'Non-Color'
    a = np.array(img.pixels[:]).reshape(R, R, 4)  # rows bottom->top
    xs = ((np.arange(R) + 0.5) / R - 0.5) * OS
    X, Y = np.meshgrid(xs, xs)  # Y increases with row index = upward
    r2 = X ** 2 + Y ** 2
    m = (r2 < 0.85) & (a[..., 3] > 0.99)
    Z = np.sqrt(np.clip(1 - r2, 0, 1))
    exp = np.stack([X, Y, Z], -1) * 0.5 + 0.5
    got = a[..., :3]
    out = {
        "mae_vs_linear_encoding_0_255": float(np.abs(got[m] - exp[m]).mean() * 255),
        "mae_vs_srgb_encoded_0_255": float(np.abs(got[m] - srgb(exp[m])).mean() * 255),
        "center_rgb": [round(float(v) * 255) for v in a[R // 2, R // 2, :3]],
        "right_rgb(x=+0.69)": [round(float(v) * 255) for v in a[R // 2, int(R * 0.81), :3]],
        "top_rgb(y=+0.69,row from bottom)": [round(float(v) * 255) for v in a[int(R * 0.81), R // 2, :3]],
        "expected_right_linear": [round(float(v) * 255) for v in exp[R // 2, int(R * 0.81)]],
        "expected_top_linear": [round(float(v) * 255) for v in exp[int(R * 0.81), R // 2]],
        "edge_alpha_values": sorted(set(round(float(v), 2) for v in a[..., 3].ravel()))[:12],
    }
    return out


def exr_channels(p):
    try:
        import OpenImageIO as oiio
        inp = oiio.ImageInput.open(p)
        spec = inp.spec()
        names = list(spec.channelnames)
        px = inp.read_image(0, 0, 0, spec.nchannels, "float")
        inp.close()
        px = np.array(px).reshape(spec.height, spec.width, spec.nchannels)
        c = px[spec.height // 2, spec.width // 2]
        nidx = [i for i, n in enumerate(names) if "Normal" in n]
        return {"channels": names, "center_normal": {names[i]: round(float(c[i]), 3) for i in nidx}}
    except Exception as e:
        data = open(p, "rb").read(20000)
        return {"oiio_error": str(e), "has_Normal_in_header": b"Normal" in data}


# ---------- 1. Matcap EXR content ----------
try:
    import OpenImageIO as oiio
    mp = None
    for base in [bpy.utils.system_resource('DATAFILES', path="studiolights/matcap")]:
        if base and os.path.isdir(base):
            for f in os.listdir(base):
                if f.startswith("check_normal"):
                    res.setdefault("normal_matcaps_on_disk", []).append(f)
                    if f == "check_normal+y.exr":
                        mp = os.path.join(base, f)
    if mp:
        inp = oiio.ImageInput.open(mp); spec = inp.spec()
        px = np.array(inp.read_image(0, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
        inp.close()
        res["matcap_exr"] = {"size": [spec.width, spec.height], "channels": list(spec.channelnames),
                             "center": [round(float(v), 4) for v in px[spec.height // 2, spec.width // 2, :3]],
                             "right_mid(top-down file)": [round(float(v), 4) for v in px[spec.height // 2, int(spec.width * 0.85), :3]],
                             "top_mid(top-down file)": [round(float(v), 4) for v in px[int(spec.height * 0.15), spec.width // 2, :3]]}
except Exception as e:
    res["matcap_exr_err"] = str(e)

# ---------- 2. Workbench matcap renders ----------
scn.render.engine = 'BLENDER_WORKBENCH'
sh = scn.display.shading
sh.light = 'MATCAP'
res["matcaps_loaded"] = [sl.name for sl in bpy.context.preferences.studio_lights if sl.type == 'MATCAP' and 'normal' in sl.name]
sh.studio_light = 'check_normal+y.exr'
sh.color_type = 'SINGLE'
for attr, val in [("show_cavity", False), ("show_shadows", False), ("show_object_outline", False),
                  ("show_specular_highlight", False), ("show_xray", False)]:
    try:
        setattr(sh, attr, val)
    except Exception as e:
        res.setdefault("shading_attr_err", []).append(f"{attr}: {e}")
scn.display.render_aa = 'OFF'
res["single_color_default"] = [round(v, 3) for v in sh.single_color]
set_fmt(False)

runs = {}
for label, vt, col in [("Standard_white", "Standard", (1, 1, 1)),
                       ("Raw_white", "Raw", (1, 1, 1)),
                       ("default_vt_white", res["default_view_transform"], (1, 1, 1)),
                       ("Standard_defaultgrey0.8", "Standard", (0.8, 0.8, 0.8))]:
    try:
        scn.view_settings.view_transform = vt
        scn.view_settings.look = 'None'
        scn.view_settings.exposure = 0.0; scn.view_settings.gamma = 1.0
        sh.single_color = col
        p = render(os.path.join(out, "wb_" + label + "_"))
        runs[label] = analyse_png(p)
    except Exception as e:
        runs[label] = {"error": str(e)}
res["workbench_runs"] = runs

# Workbench: does a Normal pass exist?
try:
    scn.view_settings.view_transform = 'Standard'
    bpy.context.view_layer.use_pass_normal = True
    set_fmt(True)
    p = render(os.path.join(out, "wb_passes_"))
    res["workbench_multilayer"] = exr_channels(p)
except Exception as e:
    res["workbench_multilayer"] = {"error": str(e)}

# ---------- 3. Cycles / EEVEE normal pass space ----------
mat = bpy.data.materials.new("M")
bpy.data.objects[0].data.materials.append(mat) if bpy.data.objects[0].type == 'MESH' else None
for eng in ['CYCLES', 'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT']:
    try:
        scn.render.engine = eng
    except TypeError as e:
        res.setdefault("engine_errors", {})[eng] = str(e)[:300]
        continue
    try:
        if eng == 'CYCLES':
            scn.cycles.samples = 1
            scn.cycles.device = 'CPU'
        bpy.context.view_layer.use_pass_normal = True
        set_fmt(True)
        p = render(os.path.join(out, eng + "_passes_"))
        res[eng + "_normal_pass"] = exr_channels(p)
    except Exception as e:
        res[eng + "_normal_pass"] = {"error": str(e)}

print("RESULT_JSON " + json.dumps(res))
