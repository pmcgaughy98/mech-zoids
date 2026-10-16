# The factory gorilla (Claude, 2026-10-12): the same Gorilla type as build_ape_l_v2.py, rebuilt through the creature
# factory to see whether the mass-manufacture path beats the 43-pass hand build. Preston: "Mass manufacture another
# gorilla, I just want to see if it comes out better or not." New id ape2_l so the approved ape_l is untouched.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_ape2_l.py
# Parts from the kit (build_ape_l_v2.py, MECH_KIT_IMPORT=1): profile_solid, limb_solid, plate_on / on_surface, shell,
# segment, disc, cyl, groove. Rig and walk from quad_rig.py (front legs are the arms: upper_arm / forearm / hand).
# Design from the first gorilla's research (docs/reference/gorilla-posture-2026-10-12.md): columnar knuckle-walking
# arms with the weight on the backs of the middle phalanges, elbows straight; shoulders high and the back sloping
# down to a long, narrow pelvis; a conical sagittal crest, a straight brow ridge, deep-set eyes, a broad muzzle.
# Proportions taken from the first gorilla's joints so the two are comparable. Colours: Preston's Gorilla type
# (main 4a7a3c, trim 2c4a2a, accent a8763e, teal eyes). Weapons: Piston Knuckles (the fists), Ballast Throw (the
# orange ballast blocks across the back), Quake Slam (both fists).
import bpy, importlib.util, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ["MECH_KIT_IMPORT"] = "1"


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kit = _load("mech_kit", "build_ape_l_v2.py")
quad = _load("quad_rig", "quad_rig.py")
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "ape2_l.blend")

PAL = {
    "main": "4a7a3c",        # green armour
    "trim": "2c4a2a",        # dark green: panel trim, the crest
    "accent": "a8763e",      # orange: fists, ballast, chest shield rim
    "frame": "5f636b",       # grey struts and joints
    "frame_dark": "4a4c53",  # the body under the plates
    "face": "55575e",        # the bare face
    "light": "8a8d92",
    "eye_src": "5fe1d0",     # teal eyes (player faction)
}


def make_materials():
    for key, h in PAL.items():
        m = bpy.data.materials.new("mech_" + key if key != "eye_src" else "eye_src")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = kit.srgb(h)
        b.inputs["Roughness"].default_value = 0.5
        m.diffuse_color = kit.srgb(h)
        kit.MATS[key] = m


# ---- the body: high shoulders, a back sloping down to a long narrow pelvis, armour on the real surface -----------
def body():
    # side profile (y forward is negative): the shoulder hump at the front, the rump low at the back
    side = [(-0.95, 1.15), (-1.0, 1.7), (-0.82, 2.12), (-0.45, 2.28), (0.0, 2.14), (0.45, 1.8), (0.82, 1.42),
            (0.98, 1.1), (0.9, 0.86), (0.5, 0.78), (-0.2, 0.82), (-0.7, 0.92)]   # v2: taller front, the master's hump
    front = kit.mirror_x([(0.3, 2.28), (0.74, 2.06), (0.96, 1.7), (0.94, 1.25), (0.76, 0.9), (0.4, 0.78)])
    side = [(y * 0.8, z) for y, z in side]   # v3: a compact torso, as the master's (ours was 1.33 wide to tall, his 1.06)
    core = kit.profile_solid("torso_core", "frame_dark", (0, 0, 0), side, front, chamfer=0.03)   # v3: dark core under rounded blocks
    # back and flank plates in four bands, inset panels, laid flat on the surface
    for row, (y, z) in enumerate(((-0.56, 2.1), (-0.2, 2.22), (0.16, 2.08), (0.5, 1.75))):   # v3: four rows of rounded blocks
        for j, th in enumerate((0, -40, 40, -78, 78, -110, 110)):
            rt = math.radians(th)
            aim = Vector((0.95 * math.sin(rt), y, z - 0.6 + 0.6 * math.cos(rt)))
            out = Vector((math.sin(rt), 0.0, math.cos(rt)))
            c = kit.on_surface(core, aim + out * 0.3, out, 0.08)
            w = 0.5 if th == 0 else 0.42
            kit.plate_on(core, "plate_%d_%d" % (row, j), "main", aim, out, w, 0.34, 0.07, 0.03, bend=0.3, bevel=0.015,
                         recess=0.025, rim=0.05)   # v4: inset panels again (v3's rounded blocks read as bubbles)
            rv = kit.on_surface(core, aim + out * 0.3, out, 0.075)
            kit.shell("rivet_%d_%d" % (row, j), "trim", rv, (0.06, 0.06, 0.03), (0, th * 0.9, 0), 0.5, levels=0)
    # Ballast Throw: three orange ballast blocks in a row across the back, with caps (the first gorilla's "yellow
    # things", kept straight across so the front and back views agree)
    for k in range(3):
        x = (k - 1) * 0.36
        c = kit.on_surface(core, Vector((x, 0.04, 2.2)), (0, 0, 1), 0.1)
        kit.shell("ballast_%d" % k, "accent", c, (0.3, 0.34, 0.26), (0, 0, 0), 0.5, levels=1, panel=True)
        kit.shell("ballast_cap_%d" % k, "trim", c + Vector((0, 0, 0.16)), (0.24, 0.28, 0.06), (0, 0, 0), 0.5, levels=0)
    # chest shield: a broad green plate with an orange rim, over the chest between the shoulders
    c = kit.on_surface(core, Vector((0, -1.0, 1.65)), (0, -1, 0.15), 0.04)
    kit.plate("chest_shield", "main", c, 1.1, 0.7, 0.08, (-12, 0, 0), bend=0.4, bevel=0.015, recess=0.025, rim=0.07)
    kit.plate("chest_rim", "accent", c + Vector((0, -0.03, -0.42)), 1.0, 0.12, 0.06, (-12, 0, 0), bend=0.4, bevel=0.01)
    for sd in (-1, 1):
        kit.plate("chest_side_%d" % sd, "main", kit.on_surface(core, Vector((sd * 0.9, -0.6, 1.35)), (sd, -0.4, 0), 0.03),
                  0.46, 0.5, 0.06, (0, 0, sd * 80), bend=0.3, bevel=0.012, recess=0.02, rim=0.05)
    # belly: dark plates with grey gaps
    for k, y in enumerate((-0.5, 0.0, 0.45)):
        kit.plate("belly_%d" % k, "trim", kit.on_surface(core, Vector((0, y, 0.74)), (0, 0, -1), 0.02), 0.62, 0.36, 0.05,
                  (90, 0, 0), bend=0.25, bevel=0.01)
    # pelvis: a long narrow beam back to the rump, a sacrum plate, and a rump plate
    kit.segment("pelvis_beam", "frame", Vector((0, 0.4, 1.0)), Vector((0, 0.86, 0.95)), 0.5, 0.34, 0.5)   # v3: with the shorter torso
    kit.plate("sacrum", "main", Vector((0, 0.72, 1.26)), 0.48, 0.4, 0.06, (-70, 0, 0), bend=0.35, bevel=0.012, recess=0.02, rim=0.05)
    kit.plate("rump_plate", "trim", Vector((0, 0.88, 1.05)), 0.6, 0.34, 0.06, (-10, 0, 180), bend=0.35, bevel=0.012)
    # flank joint discs with a glow ring, like the first gorilla
    for sd in (-1, 1):
        kit.disc("flank_disc_%d" % sd, (sd * 0.94, -0.04, 1.4), 0.12)


# ---- the head: low under the shoulder hump, a conical crest, a straight brow, deep-set eyes, a broad muzzle -----
HC = Vector((0, -1.3, 1.95))   # v3


def head():
    hc = HC
    kit.segment("neck_core", "frame_dark", Vector((0, -0.78, 1.9)), hc + Vector((0, 0.1, 0.0)), 0.56, 0.5, 0.5)
    side = [(0.25, -0.1), (0.24, 0.16), (0.08, 0.34), (-0.12, 0.38), (-0.32, 0.3), (-0.44, 0.1), (-0.5, -0.1),
            (-0.4, -0.28), (-0.1, -0.32), (0.18, -0.26)]
    front = kit.mirror_x([(0.1, 0.4), (0.28, 0.3), (0.38, 0.05), (0.34, -0.2), (0.2, -0.32)])
    skull = kit.profile_solid("head_core", "frame", hc, side, front, chamfer=0.015)   # v4: grey mech skull
    # helmet: a conical dome of six plates on the skull's real surface, a dark crest ridge along the top
    for j, (th, dy) in enumerate(((-30, 0.0), (30, 0.0), (-70, 0.02), (70, 0.02), (-30, -0.22), (30, -0.22))):
        rt = math.radians(th)
        aim = hc + Vector((0.3 * math.sin(rt), dy, 0.1 + 0.3 * math.cos(rt)))
        kit.plate_on(skull, "helmet_%d" % j, "main", aim, (math.sin(rt), 0.1, math.cos(rt)), 0.3, 0.3, 0.06, 0.025,
                     bend=0.35, bevel=0.01, recess=0.012, rim=0.035)   # v4: a fuller helmet over the grey skull
    kit.segment("crest_ridge", "trim", hc + Vector((0, 0.22, 0.42)), hc + Vector((0, -0.3, 0.5)), 0.1, 0.18, 0.5)   # v4: a taller conical crest
    # a straight brow ridge in two green bars, the eyes set deep beneath it
    for sd in (-1, 1):
        kit.shell("brow_bar_%d" % sd, "main", hc + Vector((sd * 0.14, -0.4, 0.12)), (0.24, 0.14, 0.08), (12, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d_socket" % sd, "frame_dark", hc + Vector((sd * 0.15, -0.4, 0.0)), (0.16, 0.12, 0.12), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % sd, "eye_src", hc + Vector((sd * 0.15, -0.47, 0.0)), (0.09, 0.06, 0.07), (0, 0, 0), 0.0, levels=0)
        kit.cyl("ear_%d" % sd, "frame", hc + Vector((sd * 0.34, 0.0, 0.08)), hc + Vector((sd * 0.42, 0.0, 0.08)), 0.09, 12)
        kit.plate("cheek_%d" % sd, "trim", hc + Vector((sd * 0.33, -0.26, -0.14)), 0.22, 0.22, 0.04, (0, 0, sd * 84), bend=0.3, bevel=0.008)
    # the broad muzzle and jaw, grey, with a dark nostril groove
    muzzle = kit.shell("muzzle", "frame", hc + Vector((0, -0.56, -0.18)), (0.48, 0.3, 0.24), (0, 0, 0), 0.5, levels=1)
    kit.groove(muzzle, hc + Vector((-0.1, -0.71, -0.1)), hc + Vector((0.1, -0.71, -0.1)), (0, -1, 0), w=0.04, d=0.02, mat="frame_dark")
    kit.shell("jaw", "main", hc + Vector((0, -0.44, -0.36)), (0.52, 0.5, 0.14), (0, 0, 0), 0.5, levels=1)
    kit.plate("head_cap", "trim", hc + Vector((0, -0.1, 0.46)), 0.22, 0.3, 0.04, (-84, 0, 0), bend=0.4, bevel=0.008)


# ---- arms and legs: columnar knuckle-walking arms on fists; short splayed hind legs ----------------------------
STAGGER = 0.12
JOINTS = {}


def limbs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        fo, ho = Vector((0, s * STAGGER, 0)), Vector((0, -s * STAGGER, 0))
        # arms: the first gorilla's joints; the hand points down under the wrist, the fist rests on the knuckles
        sh = Vector((s * 1.0, -0.86, 1.78)) + fo   # v3: columnar arms, the master's: shoulder high and forward
        el = Vector((s * 1.12, -1.0, 1.08)) + fo
        wr = Vector((s * 1.22, -1.1, 0.5)) + fo
        kn_ = Vector((s * 1.24, -1.18, 0.1)) + fo
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: kn_ + Vector((0, -0.2, -0.04))})
        kit.limb_solid("front_upper_%d" % s, "main", sh, el, (s, 0, 0), [(0, 0.5, 0.44), (0.4, 0.54, 0.46), (1, 0.4, 0.34)], [(0, 0.5), (1, 0.4)])   # v2: green
        kit.limb_solid("front_lower_%d" % s, "main", el, wr, (s, 0, 0), [(0, 0.42, 0.36), (1, 0.34, 0.3)], [(0, 0.42), (1, 0.34)])
        up, lo = bpy.data.objects["front_upper_%d" % s], bpy.data.objects["front_lower_%d" % s]
        kit.plate_on(up, "front_scale_%d" % s, "main", sh.lerp(el, 0.45), (s, -0.3, 0), 0.42, 0.44, 0.06, 0.02, up=tuple(sh - el),
                     bend=0.4, bevel=0.012, recess=0.02, rim=0.05)
        kit.plate_on(up, "front_scale_front_%d" % s, "main", sh.lerp(el, 0.5), (0, -1, 0), 0.32, 0.4, 0.05, 0.02, up=tuple(sh - el),
                     bend=0.4, bevel=0.01)
        kit.plate_on(lo, "front_shin_%d" % s, "main", el.lerp(wr, 0.45), (s, -0.3, 0), 0.36, 0.42, 0.05, 0.02, up=tuple(el - wr),
                     bend=0.4, bevel=0.012, recess=0.02, rim=0.05)
        kit.disc("front_elbow_%d" % s, el, 0.2, depth=0.52)
        kit.disc("front_wrist_%d" % s, wr, 0.16, depth=0.5)
        kit.disc("front_scale_%d_shoulder" % s, sh + Vector((s * 0.1, 0, 0.1)), 0.22, depth=0.5)   # v3: a shoulder disc
        # Piston Knuckles: a big fist, four orange finger segments curled under, the knuckles on the ground
        kit.shell("front_foot_%d" % s, "accent", kn_ + Vector((0, 0.02, 0.24)), (0.74, 0.6, 0.5), (0, 0, 0), 0.5, levels=1)   # v4: bigger fist
        for k in range(4):
            x = kn_.x + (k - 1.5) * 0.16
            a = Vector((x, kn_.y - 0.2, kn_.z + 0.22)); b = Vector((x, kn_.y - 0.3, kn_.z + 0.02))
            kit.segment("front_claw_%d_%d" % (s, k), "accent", a, b, 0.11, 0.12, 0.5)
            kit.segment("front_claw_%d_%d" % (s, k + 4), "accent", b, Vector((x, kn_.y - 0.16, kn_.z - 0.04)), 0.11, 0.1, 0.5)
        kit.plate("front_claw_%d_plate" % s, "main", kn_ + Vector((0, -0.08, 0.42)), 0.5, 0.3, 0.06, (-8, 0, 0), bend=0.4, bevel=0.012,
                  recess=0.02, rim=0.05)   # framed armour on the back of the hand
        # hind legs: the first gorilla's splayed, short, bent legs (after its HIND_IN / HIND_BACK moves)
        hp = Vector((s * 0.53, 0.66, 1.02)) + ho   # v3: hips forward with the shorter torso
        kn = Vector((s * 0.67, 0.8, 0.55)) + ho
        an = Vector((s * 0.69, 0.92, 0.2)) + ho
        toe = Vector((s * 0.72, 0.5, 0.06)) + ho
        JOINTS.update({"hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: toe})
        kit.limb_solid("hind_upper_%d" % s, "main", hp, kn, (s, 0, 0), [(0, 0.44, 0.4), (1, 0.34, 0.3)], [(0, 0.44), (1, 0.34)])   # v2: green
        kit.limb_solid("hind_lower_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.32, 0.3), (1, 0.26, 0.24)], [(0, 0.32), (1, 0.26)])
        hup, hlo = bpy.data.objects["hind_upper_%d" % s], bpy.data.objects["hind_lower_%d" % s]
        kit.plate_on(hup, "hind_scale_%d" % s, "main", hp.lerp(kn, 0.45), (s, 0.2, 0), 0.4, 0.4, 0.06, 0.02, up=tuple(hp - kn),
                     bend=0.4, bevel=0.012, recess=0.02, rim=0.05)
        kit.plate_on(hlo, "hind_shin_%d" % s, "main", kn.lerp(an, 0.45), (s, 0.2, 0), 0.3, 0.32, 0.05, 0.02, up=tuple(kn - an),
                     bend=0.4, bevel=0.012)
        kit.disc("hind_knee_%d" % s, kn, 0.2, depth=0.5)
        kit.cyl("hind_knee_%d_piston" % s, "frame_dark", hp + Vector((0, 0.14, -0.04)), kn + Vector((0, 0.16, 0.02)), 0.05, 8)
        # a green foot with an orange heel and three orange claws forward
        kit.shell("hind_foot_%d" % s, "main", an.lerp(toe, 0.4) + Vector((0, 0, -0.02)), (0.3, 0.6, 0.18), (0, 0, 0), 0.5, levels=1)
        kit.shell("hind_foot_%d_heel" % s, "accent", an + Vector((0, 0.12, -0.06)), (0.26, 0.16, 0.14), (0, 0, 0), 0.5, levels=1)
        for k in range(3):
            x = toe.x + (k - 1) * 0.1
            kit.segment("hind_claw_%d_%d" % (s, k), "accent", Vector((x, toe.y + 0.04, 0.1)), Vector((x, toe.y - 0.14, 0.04)), 0.08, 0.07, 0.5)


CFG = {
    "name": "ape2_l",
    "head": ("head_", "helmet", "crest", "brow", "eye_", "ear_", "cheek", "muzzle", "jaw", "neck"),
    "tail_bone": None,
    "tail_points": [],
    "body_bone": ((0, 0.75, 1.1), (0, -0.75, 1.9)),
    "head_bone": ((0, -0.8, 1.9), (0, -2.0, 1.85)),
    "joints": JOINTS,
    "stride": 0.3,
    "crouch": 0.04,
    "front_path": (0.0, 0.0, 0.1, 0),   # back, down, lift, curl: the fist stays level, knuckles down
    "hind_path": (-0.03, 0.0, 0.1, 0),
}


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    head()
    for o in list(bpy.context.scene.objects):   # v2: the head a fifth bigger about its centre (the master's head is large)
        if o.type == "MESH" and o.name.startswith(("head_", "helmet", "crest", "brow", "eye_", "ear_", "cheek", "muzzle", "jaw")):
            o.location = HC + (o.location - HC) * 1.4 + Vector((0, -0.1, 0.05))   # v3: the master's head is big
            o.scale *= 1.4
    limbs()
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "ape2_l"
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("APE2_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
