# The pygmy hippo machine, the creature factory's third product (Claude, 2026-10-12).
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_hippo_m.py
# Parts from the gorilla's kit (build_ape_l_v2.py, MECH_KIT_IMPORT=1), rig and walk from the shared quadruped rig
# (quad_rig.py, proven on the pangolin). Design from the real animal (San Diego Zoo, Louisville Zoo, SDZG fact sheet,
# 2026-10-12): a barrel body whose back slopes forward (shoulders lower than the rump, for pushing through forest
# undergrowth), a rounder, narrower head than the river hippo's on a proportionally longer neck, eyes on the sides of
# the head rather than on top, longer legs, four free toes with nails, tusk-like incisors and canines.
# Colours: Preston's proposal in scripts/data/machines.gd, "Desert Dusk" (plum, dark plum, dusk salmon, teal eyes).
# Weapons from the same file: Gape Crush (the jaw, cream tusks), Pressure Jets (two valves above the snout), Wake
# Charge (a bow ram on the chest).
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
wpn = _load("weapons", "weapons.py")
import importlib.util as _gu
_gs = _gu.spec_from_file_location("greebles", os.path.join(os.path.dirname(os.path.abspath(__file__)), "greebles.py"))
greebles = _gu.module_from_spec(_gs)
_gs.loader.exec_module(greebles)   # the detail pass (2026-10-14)
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "hippo_m.blend")

PAL = {   # material keys the kit's parts use, with this machine's colours
    "main": "9a72a2",        # plum armour; blind review (2026-10-15): his pink plates two value steps brighter (was 6b4e71)
    "trim": "2e2235",        # dark plum: panel trim, nails
    "accent": "c98b6b",      # dusk salmon: belly, lips, the bow ram (the real animal's pink underside)
    "frame": "5d5866",       # grey-violet limbs and joints
    "frame_dark": "2a2630",  # the body under the plates; blind review (2026-10-15): near-black joints and seams (was 3c3644)
    "face": "5d5866",
    "tusk": "e8dcc0",        # cream tusks
    "toe": "d8c8a0",         # p41: the toe caps' cream, a little deeper, so the lit bevels stay cream (e8dcc0 clipped to
                             # white on 8-9% of the toe pixels and the pixelizer read those as grey dots)
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
        m.diffuse_color = kit.srgb(h)   # the sprite render reads the viewport colour (no texture bake here)
        kit.MATS[key] = m


# ---- the body: a barrel, the back sloping down to the shoulders, armour plates on its real surface ------------
P46 = os.environ.get("HIPPO_P46", "1") == "1"   # p46 (2026-10-19, after the cloud model pass's judges: "the legs stand a
# little tall against the reference; the toes are uniform"): body 15 cm lower (p40's height, on p41's pillar feet; 0.18 took only 2 px off), toes graded. HIPPO_P46=0 rebuilds p41.
# p47 (2026-10-20, Codex's hippo sheet; Preston: "go both"): Codex's body is a long low barrel, 1.81 to 1.88 times as
# wide as tall in its side view and sprite against our 1.45 to 1.49 (his own painting measured 1.56). Preston took the
# middle, about 1.65: every front-to-back position scales with SQ, so 0.9 to 1.2 stretches the barrel, moves the legs
# apart and the head forward, while the head, legs and toes keep their size (1.04 measured 1.53: the 35-degree side
# view hides length; the slope gave 1.2 for 1.65). The back gear bigger (Codex's grey share
# 7% against our 2 to 3%). HIPPO_P47=0 builds p46.
P47 = P46 and os.environ.get("HIPPO_P47", "1") == "1"
SQ, LIFT = (1.2 if P47 else 0.9), (0.1 if P46 else 0.25)
# p48 (2026-10-20, factory pass part by part against Codex's sprite; Preston: "go hippo next"): Codex's hippo carries a grey
# hose tail curled up off the rump (ours a short stub pointing down, hidden), and its upper legs read as rounded plum
# thighs and shoulders, dark only at the cuff and hoof (ours grey columns top to bottom). The tail three grey hose
# segments curling up and back with dark rings between, below the back's top; the upper columns plum under a bigger
# outer plate. HIPPO_P48=0 builds p47.
P48 = P47 and os.environ.get("HIPPO_P48", "1") == "1"   # p41 model pass (2026-10-16, judges: "feet read as flat bricks", the reference stands on pillars): the body 15 cm higher on longer legs (was 0.1).   # Mechabeast V2 (2026-10-14): a little taller (p28 at 1.0, 0.2 overshot: front-right view 0.802 to 0.763)   # r10 (look-compare): legs 10 cm shorter, the body sits low as his (width/height 1.79 against 1.97); was 0.1
TOP = [(-1.05 * SQ, 1.26 + LIFT), (-0.75 * SQ, 1.45 + LIFT), (-0.3 * SQ, 1.51 + LIFT), (0.3 * SQ, 1.55 + LIFT),
       (0.8 * SQ, 1.55 + LIFT), (1.12 * SQ, 1.35 + LIFT)]   # (y, top height); Mechabeast V2 blind review 3 (2026-10-15): a taller back, his shoulders as high as the rump (the overlay: his top stood above ours over the shoulders; was 1.12, 1.33, 1.43, 1.53)
BOTTOM = 0.5 + LIFT
HALF_W = 0.64


def top_at(y):
    for (y0, z0), (y1, z1) in zip(TOP, TOP[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return TOP[0][1] if y < TOP[0][0] else TOP[-1][1]


def body():
    side = [(-1.08 * SQ, 0.7 + LIFT)] + TOP + [(y * SQ, z + LIFT) for y, z in ((1.2, 1.05), (1.08, 0.66), (0.6, 0.5), (-0.6, 0.5), (-0.98, 0.58))]
    front = kit.mirror_x([(x, z + LIFT) for x, z in ((0.2, 1.56), (0.46, 1.45), (0.61, 1.22), (HALF_W, 0.98), (0.58, 0.72), (0.42, 0.55),
                          (0.18, 0.49))])
    core = kit.profile_solid("torso_core", "frame_dark", (0, 0, 0), side, front, chamfer=0.03)
    # four bands of plates along the back; each band: a saddle plate on top, two upper flank plates, two lower flank
    # plates, all placed on the core's real surface (kit.on_surface) and laid flush to it
    for row, y in enumerate((-0.86 * SQ, -0.52 * SQ, -0.18 * SQ, 0.16 * SQ, 0.5 * SQ, 0.84 * SQ)):   # v2: six bands
        t = top_at(y)
        zc, b = (t + BOTTOM) / 2, (t - BOTTOM) / 2
        pitch = math.degrees(math.atan2(-(top_at(y + 0.05) - top_at(y - 0.05)), 0.1))
        for j, (th, w, h, mat) in enumerate(((0, 0.44, 0.3, "main"), (-40, 0.42, 0.3, "main"), (40, 0.42, 0.3, "main"),
                                             (-80, 0.4, 0.3, "main"), (80, 0.4, 0.3, "main"),
                                             (-114, 0.34, 0.28, "accent"), (114, 0.34, 0.28, "accent"))):   # v3: flush
            rt = math.radians(th)
            aim = Vector((HALF_W * math.sin(rt), y, zc + b * math.cos(rt)))
            normal = (math.sin(rt) / HALF_W, 0, math.cos(rt) / b)
            c = kit.on_surface(core, aim, normal, 0.03)
            tilt = math.degrees(math.atan2(math.sin(rt) / HALF_W, math.cos(rt) / b))
            if mat == "main" and abs(th) < 90:   # v6: a pair of dark rivets on each upper hull plate
                for dy in (-0.13, 0.13):
                    rv = kit.on_surface(core, aim + Vector((0, dy, 0)), normal, 0.045)   # v7: nearly flush (0.075 fringed the outline)
                    kit.shell("rivet_%d_%d_%d" % (row, j, dy > 0), "trim", rv, (0.045, 0.045, 0.03),
                              (-90 - pitch, tilt, 0), 0.5, levels=0)
            kit.plate("armor_%d_%d" % (row, j), mat, c, w, h, 0.06, (-90 - pitch, tilt, 0), bend=0.3, bevel=0.012,
                      recess=0.02, rim=0.05)   # v3: flush hull panels; v4: each an inset panel in a raised rim
    # salmon belly plates, the pink underside of the real animal
    for k, y in enumerate((-0.45 * SQ, 0.05 * SQ, 0.55 * SQ)):
        c = kit.on_surface(core, (0, y, 0.6 + LIFT), (0, 0, -1), 0.02)
        kit.plate("belly_%d" % k, "accent", c, 0.62, 0.42, 0.05, (90, 0, 0), bend=0.2, bevel=0.01)
    # Wake Charge: a bow ram across the chest, salmon, with dark trim ribs
    c = kit.on_surface(core, (0, -1.0 * SQ, 0.7 + LIFT), (0, -1, 0), 0.04)   # v2: down on the chest, below the neck
    kit.plate("bow_ram", "tusk", c + Vector((0, -0.02, 0.0)), 0.9, 0.5, 0.16, (14, 0, 0), bend=0.55, bevel=0.015)   # w3: the ram sits on the chest (w2 floated)
    kit.shell("bow_edge", "trim", c + Vector((0, -0.12, -0.22)), (0.84, 0.14, 0.12), (14, 0, 0), 0.5, levels=1)
    for sd in (-1, 1):
        kit.cyl("bow_piston_%d" % sd, "frame_dark", c + Vector((sd * 0.3, 0.1, 0.1)), c + Vector((sd * 0.3, 0.4, 0.16)), 0.06, 8)
    for s in (-1, 0, 1):
        kit.segment("bow_rib_%d" % s, "trim", c + Vector((s * 0.22, -0.06, 0.17)), c + Vector((s * 0.22, -0.02, -0.17)),
                    0.06, 0.05, 0.5)
    for sd in (-1, 1):   # v3
        for k in range(3):
            c = kit.on_surface(core, (sd * HALF_W, (-0.36 + 0.09 * k) * SQ, 1.02 + LIFT), (sd, 0, 0), 0.08)
            kit.shell("vent_%d_%d" % (sd, k), "trim", c, (0.05, 0.05, 0.24), (0, 0, 0), 0.5, levels=0)
        for k, y in enumerate((0.3, 0.62)):
            c = kit.on_surface(core, (sd * HALF_W, y * SQ, 1.2 + LIFT), (sd, 0, 0.3), 0.08)
            kit.shell("runlight_%d_%d" % (sd, k), "eye_src", c, (0.07, 0.09, 0.07), (0, 0, 0), 0.0, levels=0)
    # a short dorsal spine of dark trim between the saddle plates
    for k, y in enumerate((-0.48 * SQ, 0.0, 0.5 * SQ)):
        c = kit.on_surface(core, (0, y, 1.5 + LIFT), (0, 0, 1), 0.06)
        kit.shell("spine_%d" % k, "trim", c, (0.16, 0.24, 0.1), (0, 0, 0), 0.5, levels=1)


# ---- the tail: short, a stub with a dark tuft ----------------------------------------------------------------
TAIL = [Vector((0, 1.16 * SQ, 1.24 + LIFT)), Vector((0, 1.38 * SQ, 1.06 + LIFT)), Vector((0, 1.48 * SQ, 0.86 + LIFT))]
if P48:   # the hose: up and back off the rump, curling over to point back and down at the tip
    TAIL = [Vector((0, 1.14 * SQ, 1.26 + LIFT)), Vector((0, 1.26 * SQ, 1.44 + LIFT)), Vector((0, 1.42 * SQ, 1.52 + LIFT)),
            Vector((0, 1.56 * SQ, 1.4 + LIFT))]


def tail():
    if P48:
        for k in range(len(TAIL) - 1):
            kit.segment("tail_core_%d" % k, "frame", TAIL[k], TAIL[k + 1], 0.1, 0.09, 0.5)
            if k:   # a dark ring at each joint, the hose's bands
                d = (TAIL[k + 1] - TAIL[k]).normalized()
                kit.cyl("tail_core_%d_ring" % k, "trim", TAIL[k] - d * 0.03, TAIL[k] + d * 0.03, 0.115, 12)
        kit.shell("tail_core_%d_tip" % (len(TAIL) - 2), "trim", TAIL[-1], (0.14, 0.14, 0.14), (0, 0, 0), 0.5, levels=1)
        return
    kit.segment("tail_core_0", "frame", TAIL[0], TAIL[1], 0.16, 0.14, 0.5)
    kit.segment("tail_core_1", "trim", TAIL[1], TAIL[2], 0.11, 0.09, 0.5)


def tail_bone(name):
    if name.startswith("tail_core_"):
        return int(name.split("_")[2])
    return None


# ---- the head: round and narrow on a longer neck, eyes on the sides, the Pressure Jets above the snout --------
HC = Vector((0, -1.62 * SQ, 0.84 + LIFT))   # p19 (column profile): 12 cm lower again, his head top sits well below the back   # factory pass (2026-10-13): 12 cm lower, his head hangs below the back line; was 1.08
HEAD_SQ = 0.74   # p11 (look-compare): his head is a compact rounded block; ours ran long and flat (was 0.84)


def head():
    hc = HC
    # round 4 (Preston: the neck had a gap and was too thin): a thick neck from inside the chest to inside the head,
    # nearly as wide as the head, in the body's plum, with three armour bands over its top
    kit.segment("neck_core", "main", Vector((0, -0.8 * SQ, 1.1 + LIFT)), hc + Vector((0, 0.12 * HEAD_SQ, 0.02)), 0.9, 0.84, 0.5)
    for k in range(3):   # neck bands
        c = kit.on_surface(bpy.data.objects["neck_core"], Vector((0, (-1.0 - 0.14 * k) * SQ, 1.5 + LIFT)), (0, 0, 1), 0.03)
        kit.plate("neckplate_%d" % k, "main", c, 0.72, 0.16, 0.05, (-86, 0, 0), bend=0.45, bevel=0.01, recess=0.012, rim=0.03)
    side = [(0.3, -0.02), (0.26, 0.24), (0.05, 0.34), (-0.3, 0.32), (-0.64, 0.3), (-0.78, 0.18), (-0.8, -0.14),
            (-0.7, -0.26), (-0.4, -0.26), (0.2, -0.18)]   # head part 3: the muzzle box deeper and squarer
    front = kit.mirror_x([(0.18, 0.34), (0.32, 0.24), (0.4, 0.02), (0.38, -0.16), (0.26, -0.22)])   # head part: broader
    head_core = kit.profile_solid("head_core", "main", hc, side, front, chamfer=0.015)   # v3: plum
    # armour cap over the crown and down the snout
    for k, (dy, dz, w, ang) in enumerate(((0.06, 0.33, 0.42, -88), (-0.2, 0.3, 0.46, -84), (-0.46, 0.25, 0.56, -80),
                                          (-0.66, 0.16, 0.6, -40))):   # v2: armour down the broad muzzle
        kit.plate("headplate_%d" % k, "main", hc + Vector((0, dy, dz)), w, 0.26, 0.05, (ang, 0, 0), bend=0.4, bevel=0.01,
                  recess=0.015, rim=0.04)   # v4
    for sd in (-1, 1):   # v2: cheek plates, plum, down the sides of the muzzle
        kit.plate("headplate_cheek_%d" % sd, "main", kit.on_surface(head_core, hc + Vector((sd * 0.3, -0.42, 0.02)), (sd, 0, 0), 0.03), 0.4, 0.26, 0.05,
                  (0, 0, sd * 84), bend=0.3, bevel=0.01)
    # the lower jaw (Gape Crush): a salmon-lipped plum jaw, cream tusks rising from its front corners
    jaw_side = [(0.1, -0.16), (-0.3, -0.2), (-0.68, -0.16), (-0.72, -0.28), (-0.55, -0.38), (0.05, -0.32)]
    jaw_front = kit.mirror_x([(0.3, -0.16), (0.32, -0.28), (0.22, -0.38)])   # v2: matches the broader muzzle
    kit.profile_solid("head_jaw", "main", hc, jaw_side, jaw_front, chamfer=0.012)
    kit.segment("head_lip", "accent", hc + Vector((-0.31, -0.7, -0.17)), hc + Vector((0.31, -0.7, -0.17)), 0.1, 0.09, 0.5)
    for sd in (-1, 1):   # v2: salmon lips run back along both sides
        kit.segment("head_lipside_%d" % sd, "accent", hc + Vector((sd * 0.31, -0.7, -0.17)), hc + Vector((sd * 0.3, -0.2, -0.18)),
                    0.09, 0.08, 0.5)
    for s in (-1, 1):
        kit.segment("head_tusk_%d" % s, "tusk", hc + Vector((s * 0.34, -0.22, -0.3)), hc + Vector((s * 0.42, -0.34, -0.02)),
                    0.14, 0.12, 0.5)   # p10 (Preston): the tusk at the corner of the mouth line, as his reference, rising from the jaw hinge
        # eyes on the sides of the head, in dark sockets
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.3, -0.2, 0.22)), (0.1, 0.24, 0.13), (0, 0, 0), 0.5, levels=1)   # head part 3: the eye high on the skull, above the muzzle
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.35, -0.2, 0.22)), (0.05, 0.18, 0.08), (0, 0, 0), 0.0, levels=0)
        kit.cyl("ear_%d" % s, "trim", hc + Vector((s * 0.17, 0.12, 0.3)), hc + Vector((s * 0.23, 0.16, 0.42)), 0.09, 12)   # head part: ring ears
        kit.cyl("ear_%d_hole" % s, "frame_dark", hc + Vector((s * 0.19, 0.14, 0.34)), hc + Vector((s * 0.24, 0.17, 0.43)), 0.045, 10)
        kit.disc("head_hinge_%d" % s, hc + Vector((s * 0.36, -0.02, -0.1)), 0.11, depth=0.12)   # head part: the jaw hinge bolt
        # Pressure Jets: two valve barrels above the snout, dark muzzles
        base = hc + Vector((s * 0.16, 0.06, 0.5))   # head part 2: the cannon mounts behind the eyes, barrels forward over the crown
        kit.shell("head_jetbase_%d" % s, "frame_dark", base, (0.24, 0.36, 0.2), (0, 0, 0), 0.5, levels=1)
        kit.cyl("head_jet_%d" % s, "frame_dark", base + Vector((0, -0.1, 0.04)), base + Vector((0, -0.42, 0.0)), 0.1, 10)   # p11: stub barrels; the long ones read as a bar ahead of the head in the look-compare
        kit.cyl("head_jetmuzzle_%d" % s, "tusk", base + Vector((0, -0.4, 0.0)), base + Vector((0, -0.52, -0.01)), 0.12, 10)
        kit.cyl("head_jettank_%d" % s, "frame_dark", base + Vector((0, 0.18, 0.0)), base + Vector((0, 0.5, -0.04)), 0.11, 12)
        kit.cyl("head_jetvalve_%d" % s, "accent", base + Vector((0, 0.5, -0.04)), base + Vector((0, 0.55, -0.05)), 0.09, 12)
        # nostrils on top of the snout tip
        kit.shell("head_nostril_%d" % s, "trim", hc + Vector((s * 0.13, -0.68, 0.18)), (0.08, 0.07, 0.05), (0, 0, 0), 0.5, levels=0)


# ---- legs: pillar legs, longer than the river hippo's, nailed toes round a dark hoof ---------------------------
STAGGER = 0.1
JOINTS = {}

# p41 model pass (2026-10-16; blind judges: "feet read as flat bricks", "make the legs thick upright columns with toe
# pads about twice as big, distinct toes"; reference docs/art/reference/starters/hippo_m.png). Until p40 each leg segment
# was a slab 0.9 m front to back and 0.4 m tall, the foot pad hid under a ring of four cream cubes, and from the side the
# four feet ran together into one cream strip. Now: an upright square column (0.44 m) per segment in grey, a big purple
# plate on its outer face and one on its front, a round knee wheel, a dark ankle cuff, a dark round hoof wider than the
# leg, and five big rounded cream toes round the hoof's front with dark gaps between them. Sizes are for the x4.4
# pixelize (about 33 sprite px per metre): every shape at least 4 sprite px, the dark toe gaps 1 to 2.
FRONT_Y, HIND_Y = -0.8 * SQ, 0.9 * SQ   # columns nearer the barrel's ends, so the four feet stand apart (were -0.66, 0.74)
FRONT_STAGGER = 0.03   # the fore pair nearly level (0.1 in p40), so the far fore foot clears the near one in the side view
COL = 0.22        # column half-thickness (the slabs were 0.35 x 0.46)
HOOF_R, HOOF_H = 0.33, 0.4
TOE = (0.2, 0.24, 0.3)   # toe cap (wide, deep, tall): about 7 x 10 sprite px, twice p40's visible cream (6 x 5)
TOE_ANG, TOE_RAD = (-80, -40, 0, 40, 80), 0.31   # five round the front: the battle camera (55 degrees off the nose) sees
# three of them face on, as the reference's three front toes (four in p41a showed two and a sliver)


def legs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        fo, ho = Vector((0, s * FRONT_STAGGER, 0)), Vector((0, -s * STAGGER, 0))
        sh = Vector((s * 0.44, FRONT_Y, 0.86 + LIFT)) + fo
        el = Vector((s * 0.46, FRONT_Y + 0.08, 0.54 + LIFT * 0.5)) + fo   # the elbow a little back, so the IK bends it the right way
        wr = Vector((s * 0.46, FRONT_Y - 0.02, 0.17)) + fo
        hp = Vector((s * 0.44, HIND_Y, 0.95 + LIFT)) + ho
        kn = Vector((s * 0.46, HIND_Y - 0.08, 0.58 + LIFT * 0.5)) + ho   # the knee a little forward
        an = Vector((s * 0.46, HIND_Y + 0.02, 0.17)) + ho
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: wr + Vector((0, -0.2, -0.12)),
                       "hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: an + Vector((0, -0.2, -0.12))})
        for pre, a, b, c in (("front", sh, el, wr), ("hind", hp, kn, an)):
            # the columns: square, chamfered, grey (a value step lighter than the dark underbody and the hoof)
            kit.limb_solid("%s_upper_%d" % (pre, s), "main" if P48 else "frame", a, b, (s, 0, 0), [(0, COL + 0.02, COL + 0.02), (1, COL, COL)],
                           [(0, COL + 0.02), (1, COL)], chamfer=0.06)
            kit.limb_solid("%s_lower_%d" % (pre, s), "frame", b, c + Vector((0, 0, 0.12)), (s, 0, 0), [(0, COL, COL), (1, COL - 0.01, COL - 0.01)],
                           [(0, COL), (1, COL - 0.01)], chamfer=0.06)
            up, lo = bpy.data.objects["%s_upper_%d" % (pre, s)], bpy.data.objects["%s_lower_%d" % (pre, s)]
            # the round knee / elbow wheel on the outer face
            kit.disc("%s_knee_%d" % (pre, s) if pre == "hind" else "front_elbow_%d" % s, b + Vector((s * (COL + 0.04), 0, 0)), 0.13, depth=0.08)
            # the hip / shoulder wheel on the hull side, over the column's top
            kit.disc("%s_scale_%d_disc" % (pre, s), Vector((a.x + s * (COL + 0.08), a.y, a.z - 0.04)), 0.26 if pre == "hind" else 0.22, depth=0.12)
            # purple armour: a big plate on the outer face of the upper column, one on its front, a shin guard on the front
            kit.plate("%s_scale_%d" % (pre, s), "main", kit.on_surface(up, a.lerp(b, 0.55 if P48 else 0.72), (s, 0, 0), 0.03), 0.6 if P48 else 0.54, 0.66 if P48 else 0.5,
                      0.06, (-4, 0, s * 84), bend=0.4, bevel=0.012, recess=0.015, rim=0.04)
            kit.plate("%s_scale_front_%d" % (pre, s), "main", kit.on_surface(up, a.lerp(b, 0.72), (0, -1, 0), 0.03), 0.48, 0.46,
                      0.06, (0, 0, 0), bend=0.35, bevel=0.012)
            kit.plate("%s_shin_%d" % (pre, s), "main", kit.on_surface(lo, b.lerp(c, 0.42), (0, -1, 0), 0.03), 0.42, 0.24,
                      0.05, (-6, 0, 0), bend=0.35, bevel=0.01)
            # the ankle cuff and the hoof: dark, the hoof wider than the column
            kit.cyl("%s_shin_%d_cuff" % (pre, s), "frame_dark", Vector((c.x, c.y, HOOF_H - 0.02)), Vector((c.x, c.y, HOOF_H + 0.08)), COL + 0.06, 16)
            hc = Vector((c.x, c.y - 0.04, HOOF_H / 2))
            kit.drum("%s_foot_%d" % (pre, s), "frame_dark", hc, (0, 0, 1), HOOF_R, HOOF_H, round_=0.3, segments=20)
            # big rounded cream toes round the hoof's front, dark hoof between them
            for k, ang in enumerate(TOE_ANG):
                a_ = math.radians(ang)
                p = Vector((hc.x + TOE_RAD * math.sin(a_), hc.y - TOE_RAD * math.cos(a_), TOE[2] / 2))
                # p46: graded toes as the reference's, the middle one biggest, the outer pair small and low
                g = (0.72, 0.88, 1.08, 0.88, 0.72)[k] if P46 else 1.0
                size = (TOE[0] * g, TOE[1] * (0.85 + 0.15 * g), TOE[2] * g)
                if P46:
                    p = Vector((p.x, p.y, size[2] / 2))
                kit.shell("%s_claw_%d_%d" % (pre, s, k), "toe", p, size, (0, 0, ang), 0.3, levels=1)   # each faces out
                # from the hoof's centre (p40's turned the other way, so neighbouring toes met corner to corner)


CFG = {
    "battle_set": "hippo_m",   # battle clips: tools/blender/attacks.py (2026-10-13)
    "name": "hippo_m",
    "head": ("head_", "headplate", "neck", "eye_", "ear_"),
    "tail_bone": tail_bone,
    "tail_points": TAIL,
    "tail_sway": 1.4,
    "body_bone": ((0, 0.7 * SQ, 1.0 + LIFT), (0, -0.7 * SQ, 1.0 + LIFT)),
    "head_bone": ((0, -0.95 * SQ, 1.08 + LIFT), (0, -2.2 * SQ, 1.0 + LIFT)),
    "joints": JOINTS,
    "stride": 0.26,
    # hippo pass (2026-10-13): the battle stance by foot positions (quad_rig.battle_pose_for), his stride: near fore paw
    # forward under the jaw, far fore a little forward, near hind back, far hind forward. dy < 0 is forward.
    "battle_feet": {"R_arm": (0.0, 0.0), "L_arm": (-0.4, 0.0), "R_leg": (0.0, 0.0), "L_leg": (0.0, 0.0)},   # p41: the columns stand upright on their feet; only the far fore foot reaches forward, under the jaw, clear of the near one (was -0.02, -0.3, 0.0, -0.06)   # Mechabeast V2 blind review (2026-10-15): legs planted upright under the body, feet spaced as his four (was -0.45, -0.25, 0.0, -0.55)   # p19 (column profile): hind feet toward the middle, his lowest feet are mid-length   # p17: fore paws further forward, under his jaw
    "stance": "clip=battle;frame=1",
    "crouch": 0.04,
    "front_path": (0.04, 0.0, 0.09, -15),   # back, down, lift, curl
    "hind_path": (-0.04, 0.0, 0.1, 0),
}


# ---- the loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"). Roster moves get
# hardware; move None marks a spare hardpoint, DRAFT, Preston's to name. Shared builders: tools/blender/weapons.py.
def loadout():
    on, T = wpn.on, "torso_core"
    L = [
        {"slot": "turret", "move": None, "kind": "cannon", "note": "spare: a short twin cannon on the front of the back",
         "args": {"base": on(kit, T, (0.5, 0.25, 1.0), (0, 0, 1), 0.1), "direction": (0, -1, 0.05), "length": 0.55, "r": 0.07 if P47 else 0.05, "barrels": 2,
                  **({"housing": (0.46, 0.5, 0.28)} if P47 else {})}},
        {"slot": "torpedo", "move": None, "kind": "missile_pod", "note": "spare: two torpedo tubes on the back, forward",
         "args": {"center": on(kit, T, (0.5, 0.6, 1.0), (0, 0, 1), 0.13), "size": (0.62, 0.74, 0.3) if P47 else (0.5, 0.6, 0.22), "rows": 1, "cols": 2, "rot": (-8, 0, 0)}},
    ]
    for sd in (-1, 1):
        a = on(kit, T, (0.0 if sd < 0 else 1.0, 0.72, 0.55), (sd, 0, 0), 0.1)
        L.append({"slot": "thruster" + ("L" if sd == 1 else "R"), "move": "Wake Charge", "kind": "jet",
                  "note": "a water thruster on each flank, the surge behind the charge", "args": {"a": a, "b": a + Vector((0, 0.36, -0.04)), "r": 0.09}})
    return L


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    tail()
    head()
    for o in list(bpy.context.scene.objects):   # reference pass 2: a shorter, rounder muzzle (his head is compact)
        if o.type == "MESH" and o.name.startswith(("head_", "headplate", "eye_", "ear_")):
            o.location.y = HC.y + (o.location.y - HC.y) * HEAD_SQ
            o.scale.y *= HEAD_SQ
    for o in list(bpy.context.scene.objects):   # factory pass: his head a little bigger, 1.12x about HC
        if o.type == "MESH" and o.name.startswith(("head_", "headplate", "eye_", "ear_")):
            o.location = HC + (o.location - HC) * 1.12
            o.scale = tuple(v * 1.12 for v in o.scale)
    legs()
    wpn.build_loadout(kit, "hippo_m", loadout())
    greebles.run(kit, wpn, lambda n: quad.bone_for(n, CFG), skip_prefix=("front_", "hind_"))   # p41: the legs stay a
    # few big clean shapes (their panels and bolts were 1-2 sprite px each and read as speckle)
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "hippo_m"
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("HIPPO_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
