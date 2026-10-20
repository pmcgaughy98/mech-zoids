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
import bpy, bmesh, importlib.util, math, os
from mathutils import Matrix, Vector

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

P71 = os.environ.get("KANGAROO_P71", "1") == "1"   # p71 (2026-10-19, refine pass part by part against Preston's painting):
# the hip boosters, rocket pod and shoulder gun mid grey as his (his pods are light-to-mid grey with dark grilles; ours
# were charcoal and read as one near-black mass behind the body). KANGAROO_P71=0 builds p70.
POD = "light" if P71 else "frame"
P72 = os.environ.get("KANGAROO_P72", "1") == "1"   # p72 (2026-10-19, Preston: "the middle pillar like gun thing bottom of
# torso looks like a phallus. So we will put a pouch there but the cannon will shoot from there but more near stomach"):
# the pillar was the left shin, stood under the belly by the split stance (its foot 0.7 m forward); that foot goes back
# beside the right one. A rounded pouch covers the lower belly; the Pouch Flak Gun moves up to the stomach behind a
# top-hinged hatch, and flips out on two deploy bones (hatch, cannon). KANGAROO_P72=0 builds p71.
# p73 (2026-10-20, Codex's kangaroo sheet, codex_reference_pack_2026-10-19/returned/; Preston: "go"). Codex kept the
# design; measured on the grid, its orange share matches ours (52-53% against 51-54%) but ours is darker (30% near-black
# against 24-25%), most of the extra on the hips: the joint discs' thick near-black rims and the detail pass's vents and
# rams on the thighs and shins. Codex's discs are a big grey face in a thin dark rim; its torso is a smooth egg where
# our back plates step out of the outline; its tail is thicker at the root. So: joint faces 0.68 to 0.82 of the rim,
# thighs and shins bare of the detail pass, the armour slabs thinner and flush, the tail root thicker with an even
# taper. KANGAROO_P73=0 builds p72.
P73 = P72 and os.environ.get("KANGAROO_P73", "1") == "1"
PT, PS, PB = (0.04, 0.005, 0.018) if P73 else (0.07, 0.02, 0.035)
# p74 (2026-10-20, factory pass part by part against Codex's sprite; Preston: "go kangaroo next"): Codex's stands tall,
# the body lifted so each leg reads as a Z under the torso (orange thigh, big grey hip disc, dark shin back to a grey
# ankle disc, long orange foot); ours sat squat, the lower legs pressed into a dark lump at the floor. The stance rise
# 0.25 to 0.4 m (the IK keeps the feet on the floor), the tail pitched 4.3 degrees further down so its tip stays on the
# floor, and the ankle disc 0.11 to 0.15 m with its shine bead. KANGAROO_P74=0 builds p73.
P74 = P73 and os.environ.get("KANGAROO_P74", "1") == "1"   # armour slab thickness, standoff, rim bevel

PAL = {
    "main": "d4553a",        # orange-red armour (reference: e6724c lit, ae301d shadow)
    "trim": "2b2429",        # charcoal: panel trim, tail bands, claws (reference 231b1e)
    "accent": "e6724c",      # lighter orange: the underside, the muzzle stripe (no cream in the reference)
    "frame": "3a3a40",       # charcoal limbs and joints (reference 303036)
    "frame_dark": "1c1518",  # the body under the plates, the muzzle patch
    "face": "d4553a",
    "light": "8a8d92",
    "steel": "c8cacd",       # model pass p69 (2026-10-17): the light inner face of the hip, knee and ankle joints
    "jointface": "7a7c82",   # p70 (2026-10-17): the mid-grey joint face (judges: p69's light face round a dark hub read inverted)
    "glint": "ffffff",       # p70: the one white shine on a joint face, upper left
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


def armour_plates(core):
    """p70 (2026-10-17; all three judges: "the torso and shoulders are covered in round orange blobs, like bubbles or
    cobblestones ... the reference has flat, angular plates with hard edges"; "merge them into 2 to 3 larger plates").
    p69 had 25 chamfered blocks, 0.24 x 0.2 x 0.2 m, standing 9 cm off the core in five rows: at sprite size each was a
    6 px lump. Now seven flat slabs laid on the core's real faces (its back is one flat face, its sides flat strips),
    each one tone with a hard chamfered rim, so the pixelizer gives each a lit top lip and an own-colour seam:
    three stacked across the back, two up each side above the thigh. They stand 2 cm proud on a flat sheet (bend 0).
    Names start 'armor_' (body bone) and the greeble pass skips them. 'plate_nape', one small plate under the neck, keeps
    the greeble pass's host count where p69's 25 'plate_' blocks had it (25 out, 1 in: 24, a multiple of its 2, 3 and 4
    cycles), so every other part gets the same panel, vent or layer as in p69."""
    for row, (y, z, w, h) in enumerate(((0.46, 1.1, 0.66, 0.36), (0.32, 1.44, 0.62, 0.32), (0.1, 1.74, 0.5, 0.26))):
        kit.plate_on(core, "armor_back_%d" % row, "main", Vector((0, y - LEAN * (z - 0.9), z)), (0, 1, 0.25), w, h, PT,
                     standoff=PS, bend=0.0, bevel=PB)
    for s in (-1, 1):
        for row, (y, z, w, h) in enumerate(((0.04, 1.4, 0.56, 0.3), (-0.06, 1.7, 0.46, 0.26))):
            kit.plate_on(core, "armor_side_%d_%d" % (s, row), "main", Vector((s * 0.2, y - LEAN * (z - 0.9), z)),
                         (s, 0, 0.12), w, h, PT, standoff=PS, bend=0.0, bevel=PB)
    kit.plate_on(core, "plate_nape", "main", Vector((0, -0.12 - LEAN, 1.9)), (0, 0.8, 0.6), 0.26, 0.16, 0.05,
                 standoff=0.02, bend=0.0, bevel=0.025)


def pouch_and_gun(core):
    """p72: the pouch over the lower belly, and the Pouch Flak Gun moved up to the stomach behind a hatch.
    Pouch: a rounded shell in the lighter orange with a darker lip along its top, as a kangaroo's pouch opening.
    Hatch: an orange plate hinged along its top edge (bone "hatch", head at the hinge), over a dark recess, so the
    opening reads when it swings up. Gun: a dark barrel stowed pointing down inside the body behind the hatch (bone
    "cannon", head at its pivot); the flak clip swings it 90 degrees forward through the open hatch."""
    zc = 1.14   # the stomach, just above the pouch (1.28 sat at the chest, behind the near arm in E)
    n = Vector((0, -1, 0.1)).normalized()
    c = kit.on_surface(core, Vector((0, -0.4 - LEAN * (zc - 0.9), zc)), (0, -1, 0.1), 0.03)
    kit.plate("flak_recess", "frame_dark", c + n * -0.01, 0.44, 0.4, 0.03, (8, 0, 0), bend=0.35, bevel=0.008)
    kit.plate("flak_hatch", "accent", c + n * 0.02, 0.4, 0.36, 0.05, (8, 0, 0), bend=0.35, bevel=0.01)
    kit.segment("flak_hatch_seam", "trim", c + n * 0.05 + Vector((-0.16, 0, -0.18)), c + n * 0.05 + Vector((0.16, 0, -0.18)), 0.03, 0.02, 0.4)
    top, bot = c + Vector((0, 0.0, 0.18)), c + Vector((0, -0.03, -0.18))
    # the Pouch Cannon (Preston, 2026-10-19: "A little bigger, like a pirate cannon. This attack will be pouch cannon"):
    # a fat iron barrel with two raised bands, a flared muzzle and a knob at the breech, stowed pointing up inside the
    # chest (0.55 m would not fit pointing down) and swung 90 degrees forward and down through the open hatch
    gp = c + Vector((0, 0.2, -0.08))   # its pivot, 20 cm inside the surface in the hatch's lower half
    L = 0.55
    up = Vector((0, 0, 1))
    kit.cyl("flak_gun", "frame", gp, gp + up * L, 0.11, 16)
    for k, f in enumerate((0.18, 0.62)):   # raised bands
        kit.cyl("flak_gun_band%d" % k, POD, gp + up * (L * f), gp + up * (L * f + 0.05), 0.125, 16)
    kit.cyl("flak_gun_muzzle", POD, gp + up * (L - 0.07), gp + up * (L + 0.02), 0.145, 16)   # the flared lip
    kit.cyl("flak_gun_bore", "frame_dark", gp + up * (L - 0.02), gp + up * (L + 0.025), 0.08, 12)
    kit.cyl("flak_gun_breech", "frame", gp + up * -0.06, gp + up * 0.02, 0.12, 16)
    kit.cyl("flak_gun_knob", POD, gp + up * -0.13, gp + up * -0.06, 0.06, 12)   # the cascabel
    CFG["extra_bones"] = [("hatch", tuple(top), tuple(bot), "body"),
                          ("cannon", tuple(gp), tuple(gp + up * L), "body")]
    # the pouch: below the hatch, over the lower belly and the groin
    pc = kit.on_surface(core, Vector((0, -0.34 - LEAN * (0.9 - 0.9), 0.9)), (0, -1, -0.1), 0.06)
    kit.shell("pouch", "accent", pc + Vector((0, -0.04, 0)), (0.44, 0.2, 0.28), (6, 0, 0), 0.7, levels=2)
    kit.segment("pouch_lip", "trim", pc + Vector((-0.2, -0.13, 0.14)), pc + Vector((0.2, -0.13, 0.14)), 0.035, 0.03, 0.5)


def body():
    side = [(0.58, 0.95), (0.52, 1.25), (0.32, 1.58), (0.08, 1.86), (-0.16, 1.98), (-0.36, 1.86), (-0.46, 1.58),
            (-0.5, 1.2), (-0.38, 0.92), (0.02, 0.76), (0.3, 0.72)]   # p34: the lower belly further forward; ref-5 part pass (2026-10-13): a deep rounded chest and belly pushed forward, his; was flat at y -0.3
    front = kit.mirror_x([(0.22, 1.98), (0.36, 1.78), (0.44, 1.5), (0.5, 1.12), (0.44, 0.82), (0.24, 0.7)])   # ref pass 2: broader still
    side = [(y - LEAN * (z - 0.9), z) for y, z in side]   # reference pass: the torso leans forward from the hips
    core = kit.profile_solid("torso_core", "main", (0, 0, 0), side, front, chamfer=0.03)   # v2: red
    armour_plates(core)
    # the cream underside down the chest and belly
    for k, z in enumerate((1.62,) if P72 else (1.62, 1.36, 1.1)):   # p72: the hatch and the pouch take the lower two
        c = kit.on_surface(core, Vector((0, -0.4 - LEAN * (z - 0.9), z)), (0, -1, 0.1), 0.03)
        kit.plate("belly_%d" % k, "accent", c, 0.34 - 0.02 * k, 0.24, 0.045, (8, 0, 0), bend=0.35, bevel=0.01)
    # Pouch Flak Gun: a closed ventral hatch, flat to the belly, with a dark seam across it and two latch discs.
    # The gun is concealed (Preston's loadout text), so nothing protrudes.
    if P72:
        pouch_and_gun(core)
        return
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
        kit.cyl("booster_%d" % sd, POD, a, b, 0.17, 14)
        kit.cyl("booster_%d_band" % sd, "trim", a + ax * 0.14, a + ax * 0.2, 0.185, 14)
        kit.cyl("booster_%d_nozzle" % sd, "trim", b - ax * 0.02, b + ax * 0.12, 0.2, 14)
        kit.cyl("booster_%d_throat" % sd, "frame_dark", b + ax * 0.07, b + ax * 0.14, 0.14, 12)


# ---- the tail: thick, curving down to the ground behind, the prop the animal leans on --------------------------
# p70 (2026-10-17; all three judges: p69's tail "is still nearly level and the tip floats about a third of body height
# above the ground"; "thick for most of its length, tapering only at the end"; "a lit top edge and a shaded underside
# to each segment so it reads as overlapping plates"). A cubic that drops steeply off the rump and eases out along the
# floor: at rest the tip's underside sits 4 cm off the floor, so the field idle stays planted; the battle stance
# (BATTLE_TAIL, BATTLE_CURL) pitches it further down, which cancels the stance's 0.17 m rise, and curls it toward the
# near side, so in battle the tip rests 2.5 cm off the floor behind the rear foot, the third contact point (measured on
# the posed mesh). p69 was a quadratic (0.48, 1.04) / (1.25, 0.66) / (2.05, 0.16), tip 0.30 m off the floor in the stance.
# The end's 1.946 (not 1.95): the E sprite's pixel grid starts at the tail tip, and at 1.95 the near eye's 2 px wide
# lens fell inside one sprite column (a 1 px eye); 7 mm shorter splits it over two again, as in p69.
TAIL_P = (Vector((0, 0.48, 1.04)), Vector((0, 0.8, 0.72)), Vector((0, 1.25, 0.3)), Vector((0, 1.946, 0.13)))


def tail_point(t):
    p0, p1, p2, p3 = TAIL_P
    return p0 * (1 - t) ** 3 + p1 * 3 * t * (1 - t) ** 2 + p2 * 3 * t * t * (1 - t) + p3 * t ** 3


TAIL_K = 6   # p69: six segments (p15's nine read as a fringe of thin fins, then as a stack of coins once pitched right)
# p70: root-end radius per segment, thick for four segments and tapering over the last two (p69 shrank every segment by
# 0.82: 0.25, 0.21, 0.17, 0.14, 0.115, 0.094, a thin spike by the tip)
TAIL_R = (0.32, 0.29, 0.26, 0.22, 0.18, 0.13) if P73 else (0.27, 0.27, 0.26, 0.23, 0.18, 0.12)   # p73: thicker at the root, an even taper (Codex's)
TAIL_LEN = (1.15, 1.1, 1.05, 1.0, 0.9, 0.8)   # p70: relative segment lengths along the curve, each about as long as tall
TAIL_TAPER = 0.86   # p70: each segment's tip end is this much of its root end, so the next one's root end steps out past it


def _tail_t():
    """Curve parameters of the segment ends, spaced by arc length in TAIL_LEN proportions."""
    n = 400
    pts = [tail_point(i / n) for i in range(n + 1)]
    acc = [0.0]
    for p, q in zip(pts, pts[1:]):
        acc.append(acc[-1] + (q - p).length)
    out, k = [0.0], 1
    for e in [sum(TAIL_LEN[:j + 1]) / sum(TAIL_LEN) * acc[-1] for j in range(TAIL_K)]:
        while k < n and acc[k] < e:
            k += 1
        f = (e - acc[k - 1]) / max(1e-9, acc[k] - acc[k - 1])
        out.append((k - 1 + f) / n)
    out[-1] = 1.0
    return out


TAIL_T = _tail_t()


def tail_plate(name, a, b, r, taper=TAIL_TAPER):
    """p70: one tail segment from a (root end) to b: an eight-sided armour prism 2r wide and 1.9r tall at its root end,
    `taper` of that at its tip end. Its four long edges are chamfered by a fifth of its height, so from the battle camera
    it shows a lit top chamfer, a mid side and a dark chamfer under it (p69's barrel was a box with a 2 cm round-over,
    one flat tone per segment); the end rims get a small chamfer only. Laid along a->b with its height in the tail's
    vertical plane."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    d.normalize()
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        s = 1.0 if v.co.y < 0 else taper
        v.co.x *= 2 * r * s
        v.co.z *= 1.9 * r * s
        v.co.y *= L
    long_edges = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().y) > 0.9]
    bmesh.ops.bevel(bm, geom=long_edges, offset=0.2 * 1.9 * r * taper, offset_type="OFFSET", segments=1, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    ends = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().y) < 0.5]
    bmesh.ops.bevel(bm, geom=ends, offset=0.025, offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES",
                    clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    side = Vector((1, 0, 0))
    up = side.cross(d)
    ob.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((side, d, up)).transposed().to_4x4()
    return kit._finish(ob, "main")


def tail():
    pass   # p15: the Tail Spring rings are the dark gaps between segments now (the fat root rings read as a beehive)
    for k in range(TAIL_K):
        t0, t1 = TAIL_T[k], TAIL_T[k + 1]
        a, b = tail_point(t0), tail_point(t1)
        r = TAIL_R[k]
        seg = (b - a).length
        gap = 0.1 + 0.08 * seg   # p69: a dark band between segments, the core showing through (p70a 0.07 + 0.06 seg drew 1 px lines)
        dn = (b - a).normalized()
        tail_plate("tail_core_%d" % k, a + dn * gap / 2, b - dn * gap / 2, r)
        # the dark core between segments, inside the eight-sided section at the narrow end (p69: 1.55 by 1.5 r)
        kit.segment("tail_core_%d_gap" % k, "trim", a, b, 1.5 * r, 1.45 * r, 0.3)
    # Mechabeast V2 blind review (2026-10-15): lit orange bands, his tail is clean orange segments; the charcoal ones read as noise
    # p69: the accent top plates are gone; on the short p69a barrels they read as a second stripe per segment


def tail_bone(name):
    if name.startswith(("tail_core_", "tail_plate_")):
        k = int(name.split("_")[2])
        return min(3, int(2 * (TAIL_T[k] + TAIL_T[k + 1])))   # p69: by the segment's middle along the tail (4 bones)
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
STAGGER = 0.0 if P72 else 0.16   # p72 (Preston: "make sure legs are mirroring each other"): no front-back offset; was 0.16, the left hip 32 cm behind the right   # legs part: both legs show in the side view
JOINTS = {}


def joint(name, center, radius, depth=0.16, glint=0.028):
    """model pass p69 (2026-10-17; judges: "the joint discs need definition"): the Zoids Legacy joint read, a dark rim, a
    clearly lighter inner face and one shine, in pieces big enough to survive the x4.4 downscale (the gorilla's render-side
    tries moved about one sprite pixel because its discs were too small). A near-black rim cylinder and a face standing
    3 cm proud with a rounded edge; p70: the face mid grey with one white bead (glint, its radius; 0 for none) and no hub
    (p69: a light steel face round a small dark hub, which the judges read as inverted). The kit's disc() was a charcoal
    disc under an orange ring: dark on dark at sprite size. Faces outward
    (+x on the far side, -x on the near side). Names stay '<limb prefix>_joint_<side>_<piece>' for the bone rule."""
    c = Vector(center)
    ax = Vector((-1, 0, 0)) if c.x < 0 else Vector((1, 0, 0))
    kit.cyl(name + "_rim", "frame_dark", c - ax * depth, c, radius, 20)
    # (p69f tried the face domed, its outer half rounded over: more shading on the hip but the hub slid off-centre and
    # the knee went muddy at sprite size; the flat face reads as a clean light ring, lit top half, around a dark hub)
    # p70 (2026-10-17; craft judge: "the read is inverted: a light grey or white outer ring around a dark centre, where
    # Legacy wants a dark rim, a lighter inner face and a single specular pixel. Keep the size and swap the values"):
    # no dark hub; the face mid grey and a little smaller (0.78 to 0.68 of the rim), so the near-black rim shows as a
    # ring 2 sprite px wide on the hip; one white bead on the face's upper left (back and up on the near side, the side
    # the E and SE views show; forward and up on the far side, which W shows) for the shine.
    face = kit.cyl(name + "_face", "jointface", c - ax * 0.02, c + ax * 0.03, radius * (0.82 if P73 else 0.68), 20)
    kit.round_rim(face, radius * 0.14, segments=2)
    if glint:
        back = 1.0 if c.x < 0 else -1.0
        g = c + ax * 0.035 + Vector((0, back * 0.55, 0.84)).normalized() * radius * 0.36
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=glint, location=g)
        kit._finish(bpy.context.active_object, "glint").name = name + "_glint"


JOINT_SKIP = ("thigh_joint", "knee_joint", "ankle_joint")   # p69: greebles kept off the joints (a bolt on the face broke the read)


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
        # p70: light steel (read judge: "make one fist a clear grey block with a lighter top face so the boxing arm
        # reads"; his fists are light grey). It also sets the top of the pixelizer's grey stretch, which would otherwise
        # fall on the joint faces and draw them light again however dark their colour
        kit.shell("fist_%d" % s, "steel", wr + Vector((0, -0.06, -0.02)), (0.17, 0.16, 0.15), (0, 0, 0), 0.5, levels=1)   # boxing glove
        kit.plate("fist_%d_knuckle" % s, "accent", wr + Vector((0, -0.2, 0.0)), 0.22, 0.14, 0.04, (0, 0, 0), bend=0.5, bevel=0.008)
        kit.cyl("fore_plate_%d_piston" % s, "frame_dark", el + Vector((s * 0.04, 0.1, 0.02)), wr + Vector((s * 0.04, 0.08, 0.04)), 0.045, 10)
        kit.cyl("fore_plate_%d_pistoncap" % s, "accent", wr + Vector((s * 0.04, 0.085, 0.04)), wr + Vector((s * 0.04, 0.05, 0.045)), 0.055, 10)
        for k in range(3):
            kit.segment("finger_%d_%d" % (s, k), "accent", wr + Vector(((k - 1) * 0.04, -0.12, -0.03)),   # torso part: orange claws
                        wr + Vector(((k - 1) * 0.035, -0.16, -0.09)), 0.03, 0.03, 0.5)
        # hind legs: a huge armoured thigh, the shin back down to the heel, the long foot flat on the ground
        kit.limb_solid("thigh_frame_%d" % s, "main", hp, kn, (s, 0, 0), [(0, 0.39, 0.36), (1, 0.29, 0.26)], [(0, 0.34), (1, 0.26)])   # Mechabeast V2 blind review (2026-10-15): 1.3x, his big orange thigh; the legs read as a grey lump   # legs part 3: a compact thigh block, the reference's
        # p69: the hip joint as joint() (dark rim, light face, hub), 13 sprite px across, its face outside the thigh's
        # outer side (0.63 m out at the hip; the old disc's face sat at 0.56, inside it, and showed only past the thigh's
        # end) and 0.28 of the way down the thigh, so the whole disc lies on the thigh as his does
        joint("thigh_joint_%d" % s, hp.lerp(kn, 0.28) + Vector((s * 0.42, 0, 0)), 0.2)   # Mechabeast V2 blind review (2026-10-15): his round hip joint, 0.14 to 0.2   # torso part 2: hip bolt
        thigh = bpy.data.objects["thigh_frame_%d" % s]
        for k, (t, w, h) in enumerate(()):   # legs part 4: no thigh plate (it read as a slab over the shin)
            kit.plate_on(thigh, "thigh_plate_%d_%d" % (s, k), "main", hp.lerp(kn, t), (s, -0.2, 0), w, h, 0.05, 0.02,
                         up=tuple(hp - kn), bend=0.4, bevel=0.01, recess=0.012, rim=0.035)   # v2: flush
        kit.limb_solid("shin_core_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.22, 0.2), (1, 0.16, 0.15)], [(0, 0.22), (1, 0.16)])   # Mechabeast V2 blind review (2026-10-15): frame grey, the near-black shin was the dark slab at the front   # legs part: a charcoal shin column
        shin = bpy.data.objects["shin_core_%d" % s]
        kit.plate_on(shin, "calf_plate_%d" % s, "main", kn.lerp(an, 0.5), (s, -0.3, 0), 0.24, 0.56, 0.04, 0.02,   # Mechabeast V2 blind review (2026-10-15): larger, orange over the dark shin slab
                     up=tuple(kn - an), bend=0.4, bevel=0.01)   # v2: flush
        if P71:   # p71: an orange plate on the shin's front as well. The calf plate faces out, so on the far leg it faces away
            # from the camera and E showed the bare charcoal column as a tall near-black slab (3564 render px of it); the far
            # one faces in and forward, toward the E and SE cameras (straight forward hid behind the belly)
            kit.plate_on(shin, "calf_front_%d" % s, "main", kn.lerp(an, 0.45), (0, -1, 0) if P72 else ((-0.8, -0.6, 0) if s == 1 else (0, -1, 0)), 0.3, 0.6, 0.04, 0.02,   # p72: both face forward, mirrored
                         up=tuple(kn - an), bend=0.4, bevel=0.01)
        # Piston Kick: a piston along the back of each shin
        kit.cyl("heel_piston_%d" % s, "frame_dark", kn + Vector((0, 0.14, 0.02)), kn.lerp(an, 0.65) + Vector((0, 0.14, 0)), 0.075, 10)   # weapons pass: Piston Kick
        kit.cyl("heel_rod_%d" % s, "accent", kn.lerp(an, 0.65) + Vector((0, 0.14, 0)), an + Vector((0, 0.1, 0.02)), 0.04, 8)
        kit.cyl("heel_head_%d" % s, "trim", kn + Vector((0, 0.14, 0.06)), kn + Vector((0, 0.14, 0.0)), 0.09, 10)
        joint("knee_joint_%d" % s, kn + Vector((s * 0.32, 0, 0)), 0.16, depth=0.2)   # legs part: the reference's big knee bolt; p69: joint(), face at 0.62 m out (the old one sat inside the thigh and shin)
        joint("ankle_joint_%d" % s, an + Vector((s * 0.19, 0, 0)), 0.15 if P74 else 0.11, depth=0.14, glint=0.024 if P74 else 0)   # p69: joint(), 7 sprite px across; p70: no bead, a 5 px face has no room for one
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
    if n.startswith("flak_hatch"):   # p72: the deploy bones
        return "hatch"
    if n.startswith("flak_gun"):
        return "cannon"
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


BATTLE_FEET = {"R": 0.3, "L": 0.3} if P72 else {"R": 0.45, "L": -0.7}   # p72: both feet 0.3 m back, mirrored (with STAGGER 0)   # p72: the left foot back beside the right (at -0.7 its shin stood under the belly)
# was   # Mechabeast V2 blind review (2026-10-15): the near foot 25 cm less far back, his sits under the hip (ours stuck out as a grey lump)
BATTLE_RISE, BATTLE_TAIL = (0.4, -20.2) if P74 else (0.25, -15.9)   # p70: -15.9, the tail pitched about 10 degrees down past the hop's crouch lift (9 x 0.68), which takes the new tail's tip from 0.2 m to 2.5 cm off the floor in the stance (tuned on the posed mesh); p69: -6, the hop's crouch already lifts the tail 6 degrees and the new curve carries the slope (the battle tail.0 nets 0)   # Mechabeast V2 blind review (2026-10-15): 10 to 2, column profile put our tail 7% of the height above his, which slopes down-left   # V2 (p50): his kangaroo stands tall on extended legs, the tail higher   # Mechabeast V2 (2026-10-14): a split boxing stance, the near foot back, the far one forward


BATTLE_CURL = (0, 4, 5, 6)   # p70: degrees of yaw per tail bone in the stance, the tip about 0.3 m toward the near side: the E camera, turned 20 degrees, lifts whatever lies further back, and this brings the tip 2 sprite px nearer the ground line there; (0, 6, 8, 10) gained 2 px more in E but lifted the W tip 13 px off its ground line


def battle_pose(t):
    """The battle stance: the hop's planted crouch (its frame 2) with the feet split front to back by BATTLE_FEET metres
    (positive is back), each leg solved by IK so the feet stay flat on the floor."""
    t0 = 2 / HOP_FRAMES
    p = hop_pose(t0)
    dz = p["body_move"][2]
    sw = -1 + 2 * t0 / 0.35
    rise = BATTLE_RISE   # standing tall: the body up, the feet held on the floor, so the legs straighten
    p["body_move"] = (0, 0, dz + rise)
    p["tail.0"] = (p.get("tail.0", (0, 0, 0))[0] + BATTLE_TAIL, 0, BATTLE_CURL[0])
    for i in range(1, 4):   # p70: the curl toward the near side (positive rz swings a tail bone toward -x)
        p["tail.%d" % i] = (p.get("tail.%d" % i, (0, 0, 0))[0], 0, BATTLE_CURL[i])
    J = JOINTS
    for side in ("L", "R"):
        r, m, e = J["hp." + side], J["kn." + side], J["an." + side]
        a, b = (m.y - r.y, m.z - r.z), (e.y - m.y, e.z - m.z)
        w1, w2 = quad.ik2(a, b, (a[0] + b[0] + sw * STRIDE / 2 + BATTLE_FEET[side], a[1] + b[1] - dz - rise))
        p["thigh." + side] = (w1, 0, 0)
        p["shin." + side] = (w2 - w1, 0, 0)
        p["foot." + side] = (-w2, 0, 0)
    return p


TAIL_BRACE = {"kick": 0.0, "flak": 1.25}   # p70: degrees of tail lift per degree of lean back, per clip (default TAIL_BRACE_K)
TAIL_BRACE_K = 1.05


def tail_brace(battle_clips):
    """p70: the tail rests on the floor in the stance now, and every battle frame is grounded on its lowest point, so
    any lean back (b_idle's breath 0.8 degrees, b_hit's jolt 5, Pouch Flak Gun's recoil 17) would push the tail through
    the floor and lift both feet off it. In every clip the tail root lifts TAIL_BRACE_K degrees for each degree the body
    leans back, so the tail stays braced on the floor and the feet stay planted. Tail Spring keeps its own tail swing
    (it leans back onto the tail on purpose). p69 did this for the flak clip alone (0.45 degrees per degree, its tail
    was 0.3 m up). Wraps attacks.clips inside this build only; attacks.py is shared."""
    def wrapped(machine, stance):
        out = battle_clips(machine, stance)

        def brace(pose, k):
            def f(t):
                p = pose(t)
                lean = max(0.0, -p.get("body", (0, 0, 0))[0])   # negative rx leans back on this rig
                rx, ry, rz = p.get("tail.0", (0, 0, 0))
                p["tail.0"] = (rx + k * lean, ry, rz)
                return p
            return f
        return {n: (fr, brace(pose, TAIL_BRACE.get(n, TAIL_BRACE_K))) for n, (fr, pose) in out.items()}
    return wrapped


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
HARDPOINTS = {"rockets": ((0.12, 0.48, 0.9), (-1, 0, 0.7), 0.36), "shgun": ((0.88, 0.35, 0.92), (1, 0, 0.7), 0.32)}   # p70: shared with weapon_mounts()


def loadout():
    on, T = wpn.on, "torso_core"
    return [
        {"slot": "rockets", "move": None, "kind": "missile_pod", "note": "spare: a 3x2 rocket pod on the right shoulder",
         "args": {"center": on(kit, T, *HARDPOINTS["rockets"]), "size": (0.3, 0.36, 0.36), "rows": 3, "cols": 2, "rot": (-15, 0, 0), "mat": POD}},   # p30: 0.12 sank under the shoulder plates
        {"slot": "shgun", "move": None, "kind": "gatling", "note": "spare: a rotary gun on the left shoulder",
         "args": {"base": on(kit, T, *HARDPOINTS["shgun"]), "direction": (0, -1, 0.1), "length": 0.6, "ring": 0.06, "r": 0.025, "mat": POD}},
    ]


def weapon_mounts():
    """p70: the shoulder weapons stand 0.32 to 0.36 m off the torso (as since p30); p69's tall rounded blocks filled that
    gap, the flat p70 plates do not, and the far gatling floated in the NW and W views. A grey pylon from the torso to
    each weapon. Built after the greeble pass, so it does not shift that pass's host order."""
    for slot, (f, d, standoff) in HARDPOINTS.items():
        a = wpn.on(kit, "torso_core", f, d, 0.0)
        b = wpn.on(kit, "torso_core", f, d, standoff - 0.05)
        kit.cyl("wpn_%s_mount" % slot, "frame", a, b, 0.075, 10)


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
    greebles.run(kit, wpn, kangaroo_bone, skip_prefix=("tail_", "armor_") + JOINT_SKIP + (("thigh_frame", "shin_core") if P73 else ()))   # Mechabeast V2 blind review (2026-10-15): the tail kept bare, its vents were dark noise
    # p70 (craft judge: "torso behind the arm: large near-black panels with little interior structure, so they read as
    # holes"): the greeble pass's vent on each flank of the torso (a 0.4 by 0.7 m charcoal plate with slats) goes; the
    # side armour plates cover that face now
    for o in list(bpy.context.scene.objects):
        if o.name.startswith("torso_core_9") and o.data.materials and o.data.materials[0] in (kit.MATS["frame_dark"], kit.MATS["trim"]):
            bpy.data.objects.remove(o, do_unlink=True)
    weapon_mounts()
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
    atk.clips = tail_brace(atk.clips)   # p70: this build only (attacks.bake looks clips up at call time); attacks.py is shared
    atk.bake(kit, rig, "kangaroo_m", atk.fixed_stance(battle_pose, 0))
    with open(OUT_BLEND.replace(".blend", ".stance"), "w") as f:
        f.write("clip=battle;frame=1")   # V2 (2026-10-14): the split battle stance (was base=3, the hop's shallow crouch)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("KANGAROO_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
