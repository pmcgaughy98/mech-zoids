# The red kangaroo machine, the fifth starter (Claude, 2026-10-12; animal chosen by Claude at Preston's request for the
# fast striker role, "not canine or feline", "make it red"). Draft design for Preston to approve or change.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_kangaroo_m.py
# Parts from the gorilla's kit (build_ape_l_v2.py), rig built here on quad_rig.py's make_rig and ik2. Design from the
# real animal (Australian Museum, SDZG fact sheet, WWF, 2026-10-12): the largest marsupial, about 1.5 m tall, body up
# to 1.4 m, a thick tail up to 1 m used as a prop, a deer-like head with a long muzzle and large ears; males orange-red
# with a whitish underside, a black-and-white patch on each side of the muzzle and a broad white stripe from the corner
# of the mouth to the ear; over 56 km/h. Built about 1.5 times life size, standing alert on its long hind feet and tail.
# Loadout pivot (Preston, 2026-10-12: "Remove cannon that is in area of phallus ... pivot to having jetboosters" and a
# close-quarters boxing loadout): Impact Boxing Gloves (pneumatic fists, hydraulic pistons on the forearms),
# Pouch Flak Gun (hidden behind a closed ventral hatch, nothing protrudes), Tail Spring (a jet-boosted leap off the
# tail). Hip booster pods built the way the Zoids Vs. Blade Liger rip carries its: paired cylinders on the hip
# armour, axis along the body, a flared nozzle facing back (structure studied, nothing copied).
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
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "kangaroo_m.blend")

PAL = {
    "main": "d4553a",        # orange-red armour (reference: e6724c lit, ae301d shadow)
    "trim": "2b2429",        # charcoal: panel trim, tail bands, claws (reference 231b1e)
    "accent": "e6724c",      # lighter orange: the underside, the muzzle stripe (no cream in the reference)
    "frame": "3a3a40",       # charcoal limbs and joints (reference 303036)
    "frame_dark": "1c1518",  # the body under the plates, the muzzle patch
    "face": "d4553a",
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


# ---- the body: a pear leaning forward, heavy at the hips, red plates, cream belly and the pouch mortar ---------
HIP = Vector((0, 0.25, 0.98))
LEAN = 0.06   # p23 (Blender look-compare, 2026-10-13): his kangaroo stands upright, chest forward, head high on a straight neck; 0.2 leaned the whole torso 45 deg into a crouch


def body():
    side = [(0.58, 0.95), (0.52, 1.25), (0.32, 1.58), (0.08, 1.86), (-0.16, 1.98), (-0.36, 1.86), (-0.46, 1.58),
            (-0.5, 1.2), (-0.38, 0.92), (0.02, 0.76), (0.3, 0.72)]   # p34: the lower belly further forward; ref-5 part pass (2026-10-13): a deep rounded chest and belly pushed forward, his; was flat at y -0.3
    front = kit.mirror_x([(0.22, 1.98), (0.36, 1.78), (0.44, 1.5), (0.5, 1.12), (0.44, 0.82), (0.24, 0.7)])   # ref pass 2: broader still
    side = [(y - LEAN * (z - 0.9), z) for y, z in side]   # reference pass: the torso leans forward from the hips
    core = kit.profile_solid("torso_core", "main", (0, 0, 0), side, front, chamfer=0.03)   # v2: red
    # back and flank plates in bands up the leaning body, on its real surface
    for row, (y, z) in enumerate(((0.45, 1.05), (0.33, 1.3), (0.2, 1.52), (0.04, 1.72), (-0.1, 1.9))):   # round 5: five rows
        for j, th in enumerate((0, -50, 50, -95, 95)):
            rt = math.radians(th)
            aim = Vector((0.4 * math.sin(rt), y - LEAN * (z - 0.9), z))
            out = Vector((math.sin(rt), 0.75 * math.cos(rt), 0.65 * math.cos(rt)))   # back and up, then sideways
            # round 4: rounded armour blocks on the surface, like the reference's chunky plates, instead of flat sheets
            c = kit.on_surface(core, aim + out * 0.3, out, 0.09)   # round 5: smaller rounded blocks standing off the
            # charcoal core, so the dark gaps show between them as in the reference
            kit.shell("plate_%d_%d" % (row, j), "main", c, (0.24, 0.2, 0.2), (-40 - 8 * row, th * 0.9, 0), 0.4, levels=2)
    # the cream underside down the chest and belly
    for k, z in enumerate((1.62, 1.36, 1.1)):
        c = kit.on_surface(core, Vector((0, -0.4 - LEAN * (z - 0.9), z)), (0, -1, 0.1), 0.03)
        kit.plate("belly_%d" % k, "accent", c, 0.34 - 0.02 * k, 0.24, 0.045, (8, 0, 0), bend=0.35, bevel=0.01)
    # Pouch Flak Gun: a closed ventral hatch, flat to the belly, with a dark seam across it and two latch discs.
    # The gun is concealed (Preston's loadout text), so nothing protrudes.
    c = kit.on_surface(core, Vector((0, -0.3, 0.95)), (0, -1, -0.2), 0.05)   # the pouch stays at the hips
    hatch = kit.shell("pouch_hatch", "trim", c, (0.3, 0.08, 0.16), (14, 0, 0), 0.6, levels=1)
    kit.groove(hatch, c + Vector((-0.2, -0.085, 0.0)), c + Vector((0.2, -0.085, 0.0)), (0, -1, -0.2), w=0.03, d=0.02)
    for sd in (-1, 1):
        kit.disc("pouch_latch_%d" % sd, c + Vector((sd * 0.22, -0.06, 0.08)), 0.04, axis=(0, -1, -0.2), depth=0.03)
    # Jet boosters: a pod on each hip behind the lowest plate row, cylinder housing, dark throat, flared trim nozzle
    for sd in (-1, 1):
        a, b = Vector((sd * 0.38, 0.26, 1.36)), Vector((sd * 0.4, 0.6, 1.28))   # r10 (back region 0.22): pods shorter and tucked to the hips, still clear of the plates
        ax = (b - a).normalized()
        kit.cyl("booster_%d_mount" % sd, "frame_dark", a - ax * 0.08, a + ax * 0.1, 0.11, 10)
        kit.cyl("booster_%d" % sd, "frame", a, b, 0.17, 14)
        kit.cyl("booster_%d_band" % sd, "trim", a + ax * 0.14, a + ax * 0.2, 0.185, 14)
        kit.cyl("booster_%d_nozzle" % sd, "trim", b - ax * 0.02, b + ax * 0.12, 0.2, 14)
        kit.cyl("booster_%d_throat" % sd, "frame_dark", b + ax * 0.07, b + ax * 0.14, 0.14, 12)


# ---- the tail: thick, curving down to the ground behind, the prop the animal leans on --------------------------
def tail_point(t):
    p0, p1, p2 = Vector((0, 0.52, 0.98)), Vector((0, 1.3, 0.3)), Vector((0, 2.0, 0.12))   # p15: lies along the ground for its outer half (his)
    return p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t ** 2


TAIL_K = 9   # p15: his nine rounded segments


def tail():
    pass   # p15: the Tail Spring rings are the dark gaps between segments now (the fat root rings read as a beehive)
    for k in range(TAIL_K):
        t0, t1 = k / TAIL_K, (k + 1) / TAIL_K
        a, b = tail_point(t0), tail_point(t1)
        r = 0.43 * (1 - t0) + 0.075 * t0   # p15: measured from his sprite (root 0.29 of height, tip 0.05)
        pitch0 = math.degrees(math.atan2(-(b - a).z, (b - a).y))
        kit.shell("tail_core_%d" % k, "main", (a + b) / 2, (2 * r, (b - a).length * 0.9, 1.9 * r), (pitch0, 0, 0), 0.5, levels=2)   # p18: full extents (the kit's shell takes sizes, not radii; p15-p17 were half size inside the core)
        gap = kit.segment("tail_core_%d_gap" % k, "trim", a, b, 1.3 * r, 1.2 * r, 0.5)   # the dark core showing between barrels
        pitch = math.degrees(math.atan2(-(b - a).z, (b - a).y))
        kit.plate_on(bpy.data.objects["tail_core_%d" % k], "tail_plate_%d" % k, "accent", (a + b) / 2, (0, 0.3, 1),
                     1.7 * r + 0.06, 0.12, 0.045, 0.01, up=tuple(b - a), bend=0.6, bevel=0.01)   # v2: maroon bands
    # Mechabeast V2 blind review (2026-10-15): lit orange bands, his tail is clean orange segments; the charcoal ones read as noise


def tail_bone(name):
    if name.startswith(("tail_core_", "tail_plate_")):
        return min(3, 4 * int(name.split("_")[2]) // TAIL_K)
    return None


# ---- the head: deer-like, long muzzle, tall ears, the white stripe from mouth to ear, black-and-white patch ----
HC = Vector((0, -0.5, 2.5))   # kangaroo pass 3 (2026-10-13, column profile): 15 cm back, his ears stand 8% of the width behind ours; ref-5 pass 2 (p37's 12 cm raise made the whole taller, dropped): 7 cm back, the snout ran past his (blue at the tip); ref-5 p35: forward and a little lower, his snout leads (head region 0.580); head pass (2026-10-13, Preston: "its way off. Ears are uneven"): the head higher on a longer neck, his; p24 had (-0.56, 2.38)   # p24: seated on the neck (p23's floated above it in the look-compare)


def head():
    hc = HC
    kit.segment("neck_core", "frame", Vector((0, -0.42, 1.9)), hc + Vector((0, 0.1, 0.0)), 0.22, 0.22, 0.5)   # head pass: slimmer, his neck is a thin column   # p24: the neck runs into the head, leaning forward
    c = kit.on_surface(bpy.data.objects["neck_core"], Vector((0, -0.24 - LEAN * 1.18, 2.08)), (0, -1, 0.3), 0.02)
    kit.plate("neckplate_0", "accent", c, 0.2, 0.2, 0.04, (-20, 0, 0), bend=0.4, bevel=0.008)
    side = [(0.15, 0.0), (0.12, 0.17), (0.0, 0.21), (-0.12, 0.18), (-0.2, 0.08), (-0.37, 0.05), (-0.49, 0.02), (-0.52, -0.04), (-0.48, -0.08), (-0.28, -0.11), (-0.14, -0.16), (0.1, -0.14)]   # p37: snout 10% shorter   # head pass p32: a rounded skull, then a step down to a long narrow snout (his); p31 was one wedge   # head pass: the long muzzle he liked, longer, sloping to the nose   # p24 (head overlay): muzzle 12% shorter and the tip raised; blue ran along our drooping beak
    front = kit.mirror_x([(0.1, 0.24), (0.16, 0.06), (0.15, -0.06), (0.08, -0.19)])
    skull = kit.profile_solid("head_core", "main", hc, side, front, chamfer=0.012,
                              top_xy=kit.mirror_x([(0.16, 0.2), (0.16, -0.12), (0.09, -0.24), (0.07, -0.6)]))   # head pass: narrows to the nose (ours was a box)
    kit.plate("head_cap", "main", hc + Vector((0, -0.08, 0.16)), 0.2, 0.3, 0.04, (-84, 0, 0), bend=0.45, bevel=0.008, recess=0.01, rim=0.03)
    kit.shell("head_nose", "trim", hc + Vector((0, -0.51, -0.02)), (0.08, 0.06, 0.08), (0, 0, 0), 0.5, levels=1)   # part pass: a dark nose tip
    for k in range(3):   # part pass: the neck as a segmented charcoal column
        t = 0.2 + 0.28 * k
        a = Vector((0, -0.5, 1.84)).lerp(hc + Vector((0, 0.08, -0.06)), t)
        kit.segment("neck_ring_%d" % k, "trim", a, a + Vector((0, -0.02, 0.05)), 0.3, 0.3, 0.5)
    for s in (-1, 1):
        # the broad white stripe from the corner of the mouth to the ear, and the dark muzzle patch below it
        kit.segment("head_stripe_%d" % s, "accent", hc + Vector((s * 0.11, -0.36, -0.06)), hc + Vector((s * 0.14, 0.02, 0.06)),
                    0.035, 0.05, 0.5, side=(1, 0, 0))
        kit.shell("head_patch_%d" % s, "frame_dark", kit.on_surface(skull, hc + Vector((s * 0.12, -0.3, -0.04)), (s, 0, 0), 0.0),
                  (0.03, 0.1, 0.05), (0, 0, 0), 0.5, levels=0)
        kit.disc("eye_%d_ring" % s, hc + Vector((s * 0.13, -0.05, 0.05)), 0.09, depth=0.08)   # p32: the eye on the skull, his   # p20: his round ringed lens, not a visor bar
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.175, -0.05, 0.05)), (0.04, 0.1, 0.1), (0, 0, 0), 0.0, levels=0)
        kit.disc("head_jawdisc_%d" % s, hc + Vector((s * 0.15, 0.1, 0.02)), 0.1, depth=0.1)   # p32: the big grey ring behind the eye, his   # head part 2: at the hinge
        # tall ears: red plates with a cream inner face
        base = hc + Vector((s * 0.1, 0.04 + (-0.09 if s > 0 else 0.0), 0.15))   # Mechabeast V2 blind review (2026-10-15): the far ear 9 cm ahead of the near one; 8 cm behind put it exactly behind the near ear in the turned side camera, so one ear showed   # p39 (Preston: "one ear is floating or one is missing"): the far ear back on the skull, 8 cm behind the near one (p38's 20 cm left it floating behind the head); p37: 0.2, a gap between the ears as his   # p32: the far ear a little behind the near one so both show from the side, his   # head part 2: ears closer together
        # Mechabeast V2 blind review (2026-10-15): roll 14 to 5, his two ears both stand upright
        tilt = -3   # ref-5 pass 2: near upright, his ears stand straight up; was -14 # head pass: both ears the same, upright and a little back, his (p24 laid one back at -30, the other at 0: uneven)
        # p24 (head overlay): the back ear was missing from the silhouette; laid further back and taller
        kit.plate("ear_%d" % s, "main", base + Vector((s * 0.03, 0.02 - 0.02 * tilt / 10, 0.18)), 0.17, 0.5, 0.06, (tilt, 0, s * 5), bend=0.6,
                  taper=0.45, bevel=0.008)   # part pass: taller ears, a lighter inner panel
        kit.plate("ear_%d_inner" % s, "accent", base + Vector((s * 0.03, -0.015 - 0.02 * tilt / 10, 0.17)), 0.1, 0.32, 0.02, (tilt, 0, s * 5),
                  bend=0.5, taper=0.45, bevel=0.006)


# ---- arms: short, held up in a guard; legs: huge thighs, knee forward, long hind feet flat on the ground --------
STAGGER = 0.16   # legs part: both legs show in the side view
JOINTS = {}


def limbs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        sh = Vector((s * 0.28, -0.34 - LEAN * 0.84, 1.74))   # ref-5: the arms 14 cm forward with the chest   # reference pass: the arms ride the leaning chest
        el = Vector((s * 0.32, -0.52 - LEAN * 0.56, 1.58))   # pass 3: the guard higher, his arms reach forward at shoulder height
        wr = Vector((s * 0.3, -0.76 - LEAN * 0.66, 1.84))   # p42: a little back and higher, the gloves overshot his at chest height   # factory pass (2026-10-13): the guard further forward, his gloves lead
        fi = Vector((s * 0.29, -0.86 - LEAN * 0.6, 1.8))
        o = Vector((0, s * STAGGER, 0))
        hp = HIP + Vector((s * 0.24, 0, 0)) + o
        kn = Vector((s * 0.3, -0.5, 0.74)) + o   # pass 3: further forward at mid height, his   # ref-5 p34: the knee forward and up, his thigh runs forward to it
        an = Vector((s * 0.26, 0.24, 0.13)) + o
        toe = Vector((s * 0.26, -0.42, 0.05)) + o   # Mechabeast V2 blind review (2026-10-15): 8 cm further forward, his long feet   # pass 3: shorter forward, ours ran past his toes
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: fi,
                       "hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: toe})
        # arms (the gorilla's arm part names, so they ride upper_arm / forearm / hand)
        kit.limb_solid("upper_arm_%d" % s, "frame_dark", sh, el, (s, 0, 0), [(0, 0.14, 0.13), (1, 0.12, 0.11)], [(0, 0.15), (1, 0.13)])   # torso part: charcoal arms
        kit.disc("upper_arm_%d_shoulder" % s, sh + Vector((s * 0.1, 0, 0)), 0.12, depth=0.2)   # torso part 2: grey bolt discs at shoulder and hip, as the reference
        kit.limb_solid("forearm_%d" % s, "frame", el, wr, (s, 0, 0), [(0, 0.1, 0.09), (1, 0.09, 0.08)], [(0, 0.11), (1, 0.1)])
        kit.plate("fore_plate_%d" % s, "main", el.lerp(wr, 0.5) + Vector((s * 0.05, -0.02, 0.04)), 0.14, 0.2, 0.035,
                  (-60, 0, s * 70), bend=0.4, bevel=0.008)
        kit.shell("fist_%d" % s, "frame", wr + Vector((0, -0.06, -0.02)), (0.17, 0.16, 0.15), (0, 0, 0), 0.5, levels=1)   # boxing glove
        kit.plate("fist_%d_knuckle" % s, "accent", wr + Vector((0, -0.2, 0.0)), 0.22, 0.14, 0.04, (0, 0, 0), bend=0.5, bevel=0.008)
        kit.cyl("fore_plate_%d_piston" % s, "frame_dark", el + Vector((s * 0.04, 0.1, 0.02)), wr + Vector((s * 0.04, 0.08, 0.04)), 0.045, 10)
        kit.cyl("fore_plate_%d_pistoncap" % s, "accent", wr + Vector((s * 0.04, 0.085, 0.04)), wr + Vector((s * 0.04, 0.05, 0.045)), 0.055, 10)
        for k in range(3):
            kit.segment("finger_%d_%d" % (s, k), "accent", wr + Vector(((k - 1) * 0.04, -0.12, -0.03)),   # torso part: orange claws
                        wr + Vector(((k - 1) * 0.035, -0.16, -0.09)), 0.03, 0.03, 0.5)
        # hind legs: a huge armoured thigh, the shin back down to the heel, the long foot flat on the ground
        kit.limb_solid("thigh_frame_%d" % s, "main", hp, kn, (s, 0, 0), [(0, 0.39, 0.36), (1, 0.29, 0.26)], [(0, 0.34), (1, 0.26)])   # Mechabeast V2 blind review (2026-10-15): 1.3x, his big orange thigh; the legs read as a grey lump   # legs part 3: a compact thigh block, the reference's
        kit.disc("thigh_frame_%d_hip" % s, hp + Vector((s * 0.22, 0, 0)), 0.2, depth=0.2)   # Mechabeast V2 blind review (2026-10-15): his round hip joint, 0.14 to 0.2   # torso part 2: hip bolt
        thigh = bpy.data.objects["thigh_frame_%d" % s]
        for k, (t, w, h) in enumerate(()):   # legs part 4: no thigh plate (it read as a slab over the shin)
            kit.plate_on(thigh, "thigh_plate_%d_%d" % (s, k), "main", hp.lerp(kn, t), (s, -0.2, 0), w, h, 0.05, 0.02,
                         up=tuple(hp - kn), bend=0.4, bevel=0.01, recess=0.012, rim=0.035)   # v2: flush
        kit.limb_solid("shin_core_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.22, 0.2), (1, 0.16, 0.15)], [(0, 0.22), (1, 0.16)])   # Mechabeast V2 blind review (2026-10-15): frame grey, the near-black shin was the dark slab at the front   # legs part: a charcoal shin column
        shin = bpy.data.objects["shin_core_%d" % s]
        kit.plate_on(shin, "calf_plate_%d" % s, "main", kn.lerp(an, 0.5), (s, -0.3, 0), 0.24, 0.56, 0.04, 0.02,   # Mechabeast V2 blind review (2026-10-15): larger, orange over the dark shin slab
                     up=tuple(kn - an), bend=0.4, bevel=0.01)   # v2: flush
        # Piston Kick: a piston along the back of each shin
        kit.cyl("heel_piston_%d" % s, "frame_dark", kn + Vector((0, 0.14, 0.02)), kn.lerp(an, 0.65) + Vector((0, 0.14, 0)), 0.075, 10)   # weapons pass: Piston Kick
        kit.cyl("heel_rod_%d" % s, "accent", kn.lerp(an, 0.65) + Vector((0, 0.14, 0)), an + Vector((0, 0.1, 0.02)), 0.04, 8)
        kit.cyl("heel_head_%d" % s, "trim", kn + Vector((0, 0.14, 0.06)), kn + Vector((0, 0.14, 0.0)), 0.09, 10)
        kit.disc("knee_%d" % s, kn + Vector((s * 0.04, 0, 0)), 0.17, depth=0.3)   # legs part: the reference's big knee bolt
        kit.disc("ankle_%d" % s, an + Vector((s * 0.02, 0, 0)), 0.1, depth=0.2)
        # the long hind foot, flat, with the big fourth toe and claws at the front
        kit.shell("foot_%d" % s, "main", an.lerp(toe, 0.5) + Vector((0, -0.1, -0.04)), (0.18, 0.9, 0.12), (0, 0, 0), 0.5, levels=1)   # Mechabeast V2 blind review (2026-10-15): orange, his feet are orange with grey toes   # legs part: a long foot
        kit.shell("toecap_%d" % s, "main", an.lerp(toe, 0.6) + Vector((0, -0.06, 0.05)), (0.17, 0.5, 0.1), (0, 0, 0), 0.5, levels=1)   # orange over the whole front
        for k, (dx, dy, dz) in enumerate(((-0.06, -0.12, 0.02), (0.05, -0.18, -0.02))):   # claw pass (2026-10-13): bigger, light, fanned; dark claws on a dark foot vanished
            kit.segment("toe_%d_%d" % (s, k), "frame", toe + Vector((dx * 0.6, 0.04, 0.02)), toe + Vector((dx, dy, dz)), 0.07, 0.06, 0.5)


KBONES = (("upper_arm", "upper_arm"), ("forearm", "forearm"), ("fore_plate", "forearm"), ("fist", "hand"),
          ("finger", "hand"), ("thigh", "thigh"), ("shin", "shin"), ("calf", "shin"), ("heel", "shin"),
          ("knee", "shin"), ("ankle", "foot"), ("foot", "foot"), ("toecap", "foot"), ("toe", "foot"))


def kangaroo_bone(n):
    """The bone a part rides (2026-10-14: out of tag_parts so the detail pass can check its pieces against it)."""
    import re
    if n.startswith(("head_", "neck", "eye_", "ear_")):
        return "head"
    if tail_bone(n) is not None:
        return "tail.%d" % tail_bone(n)
    for prefix, b in KBONES:
        if n.startswith(prefix):
            m = re.search(r"_(-1|1)(?:_[A-Za-z0-9]+)*$", n)   # 2026-10-15: also "_1_hip", "_1_ring" (those rode the .R bone on both sides)
            return "%s.%s" % (b, "L" if m and m.group(1) == "1" else "R")
    return "body"


def tag_parts():
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        vg = o.vertex_groups.new(name=kangaroo_bone(o.name))
        vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")


# ---- the hop: both feet together; a crouch on the ground, then flight with the tail lifted -------------------------
HOP_FRAMES = 24
CROUCH, FLIGHT, STRIDE = 0.12, 0.26, 0.4


def hop_pose(t):
    """In place. Ground phase (first 35%): the body sinks and rises, the feet planted flat, sliding back under the hips
    from front to back. Flight: the body up, the legs reach back then swing forward, toes pointed, the tail lifted as
    a counterweight. The body bone pivots at the hips, so leaning it leaves the hip joints where they are."""
    g = 0.35
    if t < g:
        u = t / g
        dz, sw, foot = -CROUCH * math.sin(math.pi * u), -1 + 2 * u, 0.0
        fly = 0.0
    else:
        u = (t - g) / (1 - g)
        dz = FLIGHT * math.sin(math.pi * u)
        sw = math.cos(math.pi * u)            # back (1) to forward (-1)
        foot = 40 * math.sin(math.pi * u)     # toes point down in the air (round 6: more)
        fly = math.sin(math.pi * u)
    lean = 6 * fly
    p = {"body_move": (0, 0, dz), "body": (lean, 0, 0)}
    J = JOINTS
    for side in ("L", "R"):
        r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
        a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
        # on the ground the target rises as the body sinks, so the feet stay planted; in the air the feet tuck up a little
        up = -dz if t < g else 0.32 * fly   # round 6: the feet tuck well up under the body in flight
        w1, w2 = quad.ik2(a, b, (a[0] + b[0] + sw * STRIDE / 2, a[1] + b[1] + up))
        p["thigh." + side] = (w1 - lean, 0, 0)
        p["shin." + side] = (w2 - w1, 0, 0)
        p["foot." + side] = (-w2 + foot, 0, 0)
        p["upper_arm." + side] = (-6 * fly, 0, 0)
        p["forearm." + side] = (-8 * fly, 0, 0)
    sink = max(0.0, -dz) / CROUCH   # the tail root lifts as the body sinks, so the prop does not dig into the ground
    p["tail.0"] = (14 * fly + 9 * sink, 0, 0)
    for i in range(1, 4):
        p["tail.%d" % i] = (6 * fly, 0, 0)
    p["head"] = (-lean - 3 * fly, 0, 0)
    return p


BATTLE_FEET = {"R": 0.45, "L": -0.7}   # Mechabeast V2 blind review (2026-10-15): the near foot 25 cm less far back, his sits under the hip (ours stuck out as a grey lump)
BATTLE_RISE, BATTLE_TAIL = 0.25, 2   # Mechabeast V2 blind review (2026-10-15): 10 to 2, column profile put our tail 7% of the height above his, which slopes down-left   # V2 (p50): his kangaroo stands tall on extended legs, the tail higher   # Mechabeast V2 (2026-10-14): a split boxing stance, the near foot back, the far one forward


def battle_pose(t):
    """The battle stance: the hop's planted crouch (its frame 2) with the feet split front to back by BATTLE_FEET metres
    (positive is back), each leg solved by IK so the feet stay flat on the floor."""
    t0 = 2 / HOP_FRAMES
    p = hop_pose(t0)
    dz = p["body_move"][2]
    sw = -1 + 2 * t0 / 0.35
    rise = BATTLE_RISE   # standing tall: the body up, the feet held on the floor, so the legs straighten
    p["body_move"] = (0, 0, dz + rise)
    p["tail.0"] = (p.get("tail.0", (0, 0, 0))[0] + BATTLE_TAIL, 0, 0)
    J = JOINTS
    for side in ("L", "R"):
        r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
        a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
        w1, w2 = quad.ik2(a, b, (a[0] + b[0] + sw * STRIDE / 2 + BATTLE_FEET[side], a[1] + b[1] - dz - rise))
        p["thigh." + side] = (w1, 0, 0)
        p["shin." + side] = (w2 - w1, 0, 0)
        p["foot." + side] = (-w2, 0, 0)
    return p


def idle_pose(t):
    br = math.sin(2 * math.pi * t)
    return {"body": (1.0 * br, 0, 0), "head": (-1.5 * br, 0, 12 * math.sin(2 * math.pi * t + 0.6)),
            "upper_arm.L": (3 * br, 0, 0), "upper_arm.R": (3 * br, 0, 0), "body_move": (0, 0, 0.01 * br),
            "tail.3": (0, 0, 4 * math.sin(2 * math.pi * t))}


CFG = {
    "name": "kangaroo_m",
    "body_bone": (HIP, (0, -0.2 - LEAN, 1.9)),
    "head_bone": ((0, -0.5, 1.84), (0, -1.5, 2.3)),
    "tail_points": [tail_point(t) for t in (0.0, 0.25, 0.5, 0.75, 1.0)],
    "joints": JOINTS,
}


# ---- the loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"). Roster moves get
# hardware; move None marks a spare hardpoint, DRAFT, Preston's to name. Shared builders: tools/blender/weapons.py.
def loadout():
    on, T = wpn.on, "torso_core"
    return [
        {"slot": "rockets", "move": None, "kind": "missile_pod", "note": "spare: a 3x2 rocket pod on the right shoulder",
         "args": {"center": on(kit, T, (0.12, 0.48, 0.9), (-1, 0, 0.7), 0.36), "size": (0.3, 0.36, 0.36), "rows": 3, "cols": 2, "rot": (-15, 0, 0)}},   # p30: 0.12 sank under the shoulder plates
        {"slot": "shgun", "move": None, "kind": "gatling", "note": "spare: a rotary gun on the left shoulder",
         "args": {"base": on(kit, T, (0.88, 0.35, 0.92), (1, 0, 0.7), 0.32), "direction": (0, -1, 0.1), "length": 0.6, "ring": 0.06, "r": 0.025}},
    ]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    tail()
    head()
    limbs()
    for o in list(bpy.context.scene.objects):   # round 4: a bigger head (the reference's head is a quarter larger)
        if o.type == "MESH" and o.name.startswith(("head_", "eye_", "ear_")):
            o.location = HC + (o.location - HC) * 1.08   # head pass: his head is small on the long neck; round 4 had 1.25
            o.scale *= 1.08   # head part 4: back to the round-4 size (1.45 overshot)
    wpn.build_loadout(kit, "kangaroo_m", loadout())
    greebles.run(kit, wpn, kangaroo_bone, skip_prefix=("tail_",))   # Mechabeast V2 blind review (2026-10-15): the tail kept bare, its vents were dark noise
    tag_parts()
    ob = kit.join_into_one()
    ob.name = "kangaroo_m"
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    rig = quad.make_rig(ob, CFG)
    kit.knuckle_walk(rig)
    kit.clip(rig, "walk", HOP_FRAMES, hop_pose, grounded=False)   # it moves by hopping: the hop is its walk clip
    kit.clip(rig, "idle", 48, idle_pose)
    atk = _load("attacks", "attacks.py")   # battle clips (2026-10-13): from the hop's stance frame 3, held
    kit.clip(rig, "battle", 2, battle_pose)   # V2: the split stance the sprites and battle clips stand in
    atk.bake(kit, rig, "kangaroo_m", atk.fixed_stance(battle_pose, 0))
    with open(OUT_BLEND.replace(".blend", ".stance"), "w") as f:
        f.write("clip=battle;frame=1")   # V2 (2026-10-14): the split battle stance (was base=3, the hop's shallow crouch)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("KANGAROO_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
