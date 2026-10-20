# Render the gorilla as a sprite source (Claude, 2026-10-12, 2D pivot): eight views, one fixed framing and scale,
# transparent background, flat albedo colour (Workbench, no normal or roughness maps, so planes stay flat), one key
# light from above-left. The glow material is split: the two eye lenses stay teal, every other glow ring turns grey
# (the design's joints are grey discs). tools/art/pixelize_render.py then turns each render into pixel art.
#   blender -b docs/art/3d/ape_l_v2.blend -P tools/blender/render_sprite_views.py
import bpy, json, math, os
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", ".."))
OUT = os.path.join(ROOT, "docs", "art", "2d", "ape_l", "renders")
os.makedirs(OUT, exist_ok=True)
# the lens centres in build_ape_l_v2.py after the head group's scale (0.92 about (0, -1.3, 2.05)) and move (0, 0.04, -0.1)
# pass 38 (2026-10-12): the eyes are one visor line across x -0.36..0.36 at (y -1.685, z 2.07); sample it every 0.06
EYES = [Vector((0, -1.3, 2.05)) + (Vector((x * 0.05, y, 2.07)) - Vector((0, -1.3, 2.05))) * 0.92 + Vector((0, 0.14, -0.24))   # gorilla pass 44 (2026-10-13): the head group moved 16 cm back; these points must follow it or the visor renders grey
        for x in range(-8, 9) for y in (-1.76, -1.68)]
scene = bpy.context.scene

# the machine: the biggest mesh; stand it at rest pose
ob = max((o for o in scene.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))
# Pose (pass 34): a clip frame instead of the rest pose, e.g. SPRITE_CLIP=walk SPRITE_FRAME=10. A real gorilla stands
# staggered, near and far limbs at different points; at rest the pairs hide behind each other from the side.
# default pose (pass 42): walk frame 19 (best side outline, Preston: "side view looks awesome") with the near rear leg
# from frame 13, planted instead of trailing in the air. The full mixed stance was stiffer and scored lower (0.561).
CLIP = os.environ.get("SPRITE_CLIP", "stance")
os.environ.setdefault("SPRITE_STANCE", "base=19;R_leg=13")
FRAME = int(os.environ.get("SPRITE_FRAME", "19"))
VIEWS = os.environ.get("SPRITE_VIEWS", "e ne n nw w sw s se").split()
OUT = os.environ.get("SPRITE_OUT", OUT); os.makedirs(OUT, exist_ok=True)
rig = next((o for o in scene.objects if o.type == "ARMATURE"), None)
# The battle stance (pass 42): every limb planted and staggered, mixed bone by bone from two walk frames. From the side
# the camera sees the machine's right (R) side: the near arm planted and back so the chest shows, the near leg planted
# forward; the far arm a little forward and the far leg back. Body and head from frame 1.
STANCE = {"body": 1, "head": 1, "upper_arm.R": 1, "forearm.R": 1, "hand.R": 1, "thigh.R": 1, "shin.R": 1, "foot.R": 1,
          "upper_arm.L": 31, "forearm.L": 31, "hand.L": 31, "thigh.L": 31, "shin.L": 31, "foot.L": 31}
# SPRITE_STANCE overrides it: "base=19;R_arm=13;R_leg=13" (base frame for every bone, then per-limb frames)
if os.environ.get("SPRITE_STANCE"):
    spec = dict(kv.split("=") for kv in os.environ["SPRITE_STANCE"].split(";"))
    if "clip" in spec:   # 2026-10-13: a stance held from a named clip (quad_rig's "battle" pose by foot positions)
        CLIP, FRAME = spec["clip"], int(spec.get("frame", 1))
    base = int(spec.get("base", 19))
    STANCE = {b: base for b in STANCE}
    limbs = {"R_arm": ("upper_arm.R", "forearm.R", "hand.R"), "L_arm": ("upper_arm.L", "forearm.L", "hand.L"),
             "R_leg": ("thigh.R", "shin.R", "foot.R"), "L_leg": ("thigh.L", "shin.L", "foot.L")}
    for limb, bones in limbs.items():
        if limb in spec:
            for b in bones:
                STANCE[b] = int(spec[limb])
if rig and CLIP == "stance":
    rig.data.pose_position = "POSE"
    for tr in rig.animation_data.nla_tracks:
        tr.mute = tr.name != "walk"
    basis = {}
    for f in sorted(set(STANCE.values())):
        scene.frame_set(f)
        for bname, fb in STANCE.items():
            if fb == f:
                basis[bname] = rig.pose.bones[bname].matrix_basis.copy()
    for tr in rig.animation_data.nla_tracks:
        tr.mute = True   # nothing animates over the held pose
    for bname, m in basis.items():
        rig.pose.bones[bname].matrix_basis = m
    bpy.context.view_layer.update()
elif rig:
    if CLIP:
        rig.data.pose_position = "POSE"
        for tr in rig.animation_data.nla_tracks:
            tr.mute = tr.name != CLIP
        scene.frame_set(FRAME)
    else:
        rig.data.pose_position = "REST"
for o in scene.objects:   # hide everything else (old lights and cameras are not used by Workbench anyway)
    if o.type == "MESH" and o is not ob:
        o.hide_render = True

# split the glow material: eyes teal, the rest grey
me = ob.data
glow_idx = [i for i, m in enumerate(me.materials) if m and m.name.startswith("ape_eye")]
grey = bpy.data.materials.new("sprite_disc"); grey.diffuse_color = (0.55, 0.57, 0.6, 1)
teal = bpy.data.materials.new("sprite_eye"); teal.diffuse_color = (0.12, 0.72, 0.77, 1)
me.materials.append(grey); gi = len(me.materials) - 1
me.materials.append(teal); ti = len(me.materials) - 1
eyes = 0
for p in me.polygons:
    if p.material_index in glow_idx:
        c = ob.matrix_world @ p.center
        if min((c - e).length for e in EYES) < 0.09:
            p.material_index = ti; eyes += 1
        else:
            p.material_index = gi
print("SPRITE glow faces split: %d eye faces" % eyes)

# Split the joined mesh back into its parts so a second pass can colour each part flat (a part-ID map); the
# pixelizer draws a dark line wherever two parts meet, the plate lines of a hand-drawn sprite.
bpy.context.view_layer.objects.active = ob
for o in scene.objects:
    o.select_set(o is ob)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
print("SPRITE parts:", len(parts))

# Workbench: albedo texture, studio light, no cavity or specular; transparent film
scene.render.engine = "BLENDER_WORKBENCH"
sh = scene.display.shading
sh.light = "STUDIO"
# untextured machines (no bake yet, e.g. a new factory creature) render in their flat material colours
HAS_TEX = any(n.type == "TEX_IMAGE" for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes)
COLOR_TYPE = "TEXTURE" if HAS_TEX else "MATERIAL"
sh.color_type = COLOR_TYPE
# Legacy look knobs (2026-10-14, Preston: "Still doesn't look like it could pass as a zoids sprite"; gap measured in
# docs/reference/sprite-rules-legacy-2026-10-14-gap.md). Off by default so older rounds re-render the same.
#   SPRITE_CAVITY=1: ridges catch light and creases darken (a Legacy plate's lit edge and panel line)
#   SPRITE_SPECULAR=1: metal highlights   SPRITE_ELEV=deg (default 10)   SPRITE_E_TURN=deg: the side view turned that
#   far toward the viewer, as Legacy battle sprites sit a little off side-on (the battle draws the side view)
sh.show_cavity = os.environ.get("SPRITE_CAVITY") == "1"
if sh.show_cavity:
    sh.cavity_type = "BOTH"
    sh.cavity_ridge_factor, sh.cavity_valley_factor = float(os.environ.get("SPRITE_RIDGE", "1.6")), float(os.environ.get("SPRITE_VALLEY", "1.0"))
    sh.curvature_ridge_factor, sh.curvature_valley_factor = float(os.environ.get("SPRITE_RIDGE", "1.6")), float(os.environ.get("SPRITE_VALLEY", "1.0"))
sh.show_specular_highlight = os.environ.get("SPRITE_SPECULAR") == "1"
NORMALS = os.environ.get("SPRITE_NORMALS") == "1"   # also write <view>_n.png, a normal map for 2D lighting
PIECES = os.environ.get("SPRITE_PIECES") == "1"   # also write <view>_piece.png and parts.json (the detail pixelizer)


def _lin(c):   # sRGB display value -> scene-linear, so a flat colour renders back to the value it was given
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
MATCAP = os.environ.get("SPRITE_MATCAP", "")   # e.g. toon.exr: banded light, mid and dark faces per part (Legacy plates)
sh.show_shadows = True   # pass 43: light from the upper left with cast shadows, as Legacy sprites are lit
sh.shadow_intensity = 0.55
scene.display.light_direction = (-0.3, -0.3, 0.9)   # mostly from above, a little left and front
scene.display.shadow_shift = 0.05
sh.studiolight_rotate_z = math.radians(-20)   # key light from above, a little to the left
scene.render.film_transparent = True
# SPRITE_ORTHO widens the frame for a long machine; the resolution grows with it so every machine renders at the same
# pixels per metre (640 px for 4.4 m) and pixelizes at the same scale (x4.4): sizes stay true between machines.
ORTHO = float(os.environ.get("SPRITE_ORTHO", "4.4"))
scene.render.resolution_x = scene.render.resolution_y = int(round(640 * ORTHO / 4.4))
scene.view_settings.view_transform = "Standard"

# Sprite proportion (pass 34, 2026-10-12): the whole machine 15% shorter front to back, so the trunk reads short and
# deep like a real gorilla's and like Preston's side sprite. Applied in the machine's own axes, so all eight views agree.
SQUASH_Y = float(os.environ.get("SPRITE_SQUASH_Y", "1.0"))   # per run (2026-10-13, wolf part pass); the gorilla tried 0.85 in pass 34: worse (0.551 to 0.518)
cam_data = bpy.data.cameras.new("sprite_cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = ORTHO
cam = bpy.data.objects.new("sprite_cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
target = Vector((0, 0, float(os.environ.get("SPRITE_TARGET_Z", "1.25"))))   # SPRITE_TARGET_Z (2026-10-19): the combiner stands 9.9 m tall
elev = math.radians(float(os.environ.get("SPRITE_ELEV", "10")))   # near side-on like Legacy battle sprites and Preston's side sprite (25 showed a flat top)
for k, name in enumerate(["e", "ne", "n", "nw", "w", "sw", "s", "se"]):
    if name not in VIEWS:
        continue
    turn = math.radians(k * 45) + math.radians(90)
    if name == "e":
        turn -= math.radians(float(os.environ.get("SPRITE_E_TURN", "0")))
    turn += math.radians(float(os.environ.get("SPRITE_TURN", "0")))   # every view turned this far (matching a reference's angle, 2026-10-14)
    if rig:   # turn the rig: every part rides it, so the pose turns with the machine
        rig.rotation_euler = (0, 0, turn)
        rig.scale = (1, SQUASH_Y, 1)
    else:
        for o in parts:
            o.rotation_euler = (0, 0, turn)
            o.scale = (1, SQUASH_Y, 1)
    el = math.radians(float(os.environ["SPRITE_SIDE_ELEV"])) if name in ("e", "w") and os.environ.get("SPRITE_SIDE_ELEV") else elev   # the side views
    # alone (the battle draws the side view): a long machine seen from higher shows its whole back in the front and
    # back views and they outgrow the rest (wolf at 24 degrees, 2026-10-14)
    cam.location = target + Vector((0, -10 * math.cos(el), 10 * math.sin(el)))
    cam.rotation_euler = (math.radians(90) - el, 0, 0)
    sh.light, sh.color_type = ("MATCAP" if MATCAP else "STUDIO"), COLOR_TYPE
    if MATCAP:
        sh.studio_light = MATCAP
    scene.render.filepath = os.path.join(OUT, "%s.png" % name)
    bpy.ops.render.render(write_still=True)
    sh.light, sh.color_type = "FLAT", "RANDOM"   # the part-ID pass
    scene.render.filepath = os.path.join(OUT, "%s_id.png" % name)
    bpy.ops.render.render(write_still=True)
    if NORMALS:   # the normal pass (lighting slice, 2026-10-14; reports/Lit pixel sprites in Godot.md): the bundled
        # check_normal+y matcap under Standard writes camera-space normals as n*0.5+0.5, Y up, as Godot reads them
        # (1.4/255 off on a test sphere); white single colour, no shadows, cavity, specular or AA, then restored
        keep = (sh.show_shadows, sh.show_cavity, sh.show_specular_highlight, scene.display.render_aa, sh.single_color[:])
        sh.light, sh.color_type = "MATCAP", "SINGLE"
        sh.studio_light = "check_normal+y.exr"
        sh.single_color = (1, 1, 1)
        sh.show_shadows = sh.show_cavity = sh.show_specular_highlight = False
        scene.display.render_aa = "OFF"
        scene.render.filepath = os.path.join(OUT, "%s_n.png" % name)
        bpy.ops.render.render(write_still=True)
        sh.show_shadows, sh.show_cavity, sh.show_specular_highlight, scene.display.render_aa, sh.single_color = keep
    if PIECES:   # the piece pass (2026-10-16, detail pass; Codex's finish reports): one exact colour per piece, no
        # antialiasing, shading or cavity, so the pixelizer knows which piece every pixel is (the _id pass above is
        # antialiased and cavity-shaded: about 40,000 colours on the gorilla). Index i+1 is coded in 16 levels per
        # channel (decoded by nearest level, so colour management cannot shift it) and the piece list goes beside it.
        keep = (sh.show_shadows, sh.show_cavity, sh.show_specular_highlight, scene.display.render_aa)
        sh.light, sh.color_type = "FLAT", "OBJECT"
        sh.show_shadows = sh.show_cavity = sh.show_specular_highlight = False
        scene.display.render_aa = "OFF"
        for i, o in enumerate(parts):
            k = i + 1
            o.color = tuple(_lin(((k >> s) & 15) / 15.0) for s in (8, 4, 0)) + (1.0,)
        scene.render.filepath = os.path.join(OUT, "%s_piece.png" % name)
        bpy.ops.render.render(write_still=True)
        sh.show_shadows, sh.show_cavity, sh.show_specular_highlight, scene.display.render_aa = keep
        if not os.path.exists(os.path.join(OUT, "parts.json")):
            rows = []
            for i, o in enumerate(parts):
                vg = {g.index: g.name for g in o.vertex_groups}
                w = {}
                for v in o.data.vertices:
                    for g in v.groups:
                        w[vg.get(g.group, "?")] = w.get(vg.get(g.group, "?"), 0.0) + g.weight
                mats = [p.material_index for p in o.data.polygons]
                mi = max(set(mats), key=mats.count) if mats else -1
                mat = o.data.materials[mi].name if 0 <= mi < len(o.data.materials) and o.data.materials[mi] else ""
                rows.append({"index": i + 1, "name": o.name, "bone": max(w, key=w.get) if w else "", "material": mat,
                             "verts": len(o.data.vertices)})
            json.dump(rows, open(os.path.join(OUT, "parts.json"), "w"), indent=0)
print("SPRITE_RENDERS_DONE", OUT)
