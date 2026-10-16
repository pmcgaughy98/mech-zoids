# The black wolf machine, the creature factory's sixth starter (Claude, 2026-10-12; Preston: "a black wolf with
# blood red accents ... use the synthesis and creature factory then mass manufacture it").
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_wolf_m.py
# Parts from the gorilla's kit (build_ape_l_v2.py, MECH_KIT_IMPORT=1), rig and walk from the shared quadruped rig
# (quad_rig.py). Design from the real animal (San Diego Zoo Wildlife Alliance fact sheet, National Wildlife
# Federation, 2026-10-12): shoulder height 66-84 cm, head and body 100-160 cm, tail 35-56 cm; a muscular build with
# long legs and a narrow, keel-like chest built for distance running; forelegs pressed in, elbows turned in and paws
# out; feet large and flexible, four toes on the ground; an elongate skull tapering to a narrow muzzle; a bushy
# tail, often black-tipped; a mane of erectile hair along the neck and shoulders. Built about 1.6 times life size
# so it stands with the other starters. Structure study only from the Legacy canid sprites in
# docs/art/reference/legacy/ (width to height about 1.4-1.5, legs about 13-14% of the height as free columns).
# Colours: near-black armour, charcoal frame, blood-red accents, teal eyes. Weapons (DRAFT, Claude's proposal for
# Preston): Fang Lunge (the jaw, red fangs), Howl Burst (a red-grilled emitter in the throat), Shadow Dash (red
# blade fins on the shoulders and hips, the lunge itself).
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
weapons = _load("weapons", "weapons.py")
import importlib.util as _gu
_gs = _gu.spec_from_file_location("greebles", os.path.join(os.path.dirname(os.path.abspath(__file__)), "greebles.py"))
greebles = _gu.module_from_spec(_gs)
_gs.loader.exec_module(greebles)   # the detail pass (2026-10-14)
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "wolf_m.blend")

PAL = {
    "main": "1a1a1f",        # near-black armour
    "trim": "5a0a0e",        # dried blood: panel trim, fang roots, tail tip
    "accent": "e01818",      # bright red: mane plates, fins, claws, fangs (2026-10-15, Mechabeast V2 blind review: his red is a saturated e01818, ours read as maroon; was b3131a)
    "frame": "4a4a54",       # grey limbs and joints, lighter than the body (the reference's legs read as steel)
    "frame_dark": "121214",  # the body under the plates
    "face": "4a4a54",
    "tusk": "c42a2a",        # the fangs (the kit's "tusk" slot)
    "light": "9a9aa4",       # 2026-10-15, Mechabeast V2 blind review 2: his limb plating is near-white, ours read lavender-grey (was 6e6e7c)
    "blade": "d4d4da",       # 2026-10-15, blind review 2: the tail spikes, big pale blades as his
    "claw": "ff3028",        # 2026-10-15, blind review 2: the talons in his brightest red
    "eye_src": "5fe1d0",     # teal eyes (player faction; Preston may want red)
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


# ---- the body: lean, a deep keel chest, the back level from withers to croup, a tucked belly ----------------
SH = 1.6                      # shoulder height (v5: legs a third longer, the reference's stilted stance)
UP = 0.55                     # ref-5 part pass (2026-10-13): legs 25 cm longer, his legs are near half the height (ours a third); v5 had 0.3: everything above the legs lifted so the feet stay on the floor
TOP = [(-1.05, 1.36 + UP), (-0.6, 1.42 + UP), (-0.1, 1.38 + UP), (0.4, 1.34 + UP), (0.85, 1.3 + UP), (1.1, 1.18 + UP)]   # (y, top height)
HALF_W = 0.36


def top_at(y):
    for (y0, z0), (y1, z1) in zip(TOP, TOP[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return TOP[0][1] if y < TOP[0][0] else TOP[-1][1]


def bottom_at(y):
    """The keel: deepest just behind the forelegs, rising to a tucked waist and a light croup."""
    pts = [(-1.1, 0.85 + UP), (-0.7, 0.48 + UP), (-0.2, 0.55 + UP), (0.4, 0.72 + UP), (0.9, 0.8 + UP), (1.15, 0.95 + UP)]   # v12: a deeper body (look-compare: ours ran long and thin)
    for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return pts[0][1] if y < pts[0][0] else pts[-1][1]


def body():
    side = [(-1.12, 1.0 + UP)] + TOP + [(y, z + UP) for y, z in ((1.18, 1.0), (1.12, 0.93), (0.9, 0.8), (0.4, 0.72), (-0.2, 0.55), (-0.7, 0.48), (-1.1, 0.85))]
    front = kit.mirror_x([(x, z + UP) for x, z in ((0.14, 1.42), (0.3, 1.32), (HALF_W, 1.1), (0.34, 0.9), (0.24, 0.7), (0.1, 0.62))])
    core = kit.profile_solid("torso_core", "frame_dark", (0, 0, 0), side, front, chamfer=0.025)
    # five bands of black plates on the real surface: a saddle, two upper flank and two lower flank plates
    for row, y in enumerate((-0.82, -0.44, -0.06, 0.32, 0.72)):
        t, b0 = top_at(y), bottom_at(y)
        zc, b = (t + b0) / 2, (t - b0) / 2
        pitch = math.degrees(math.atan2(-(top_at(y + 0.05) - top_at(y - 0.05)), 0.1))
        for j, (th, w, h, mat) in enumerate(((0, 0.32, 0.3, "accent"), (-48, 0.3, 0.28, "main"), (48, 0.3, 0.28, "main"),   # V2 (v70): red-topped back, his
                                             (-96, 0.26, 0.24, "main"), (96, 0.26, 0.24, "main"))):
            rt = math.radians(th)
            aim = Vector((HALF_W * math.sin(rt), y, zc + b * math.cos(rt)))
            normal = (math.sin(rt) / HALF_W, 0, math.cos(rt) / b)
            c = kit.on_surface(core, aim, normal, 0.03)
            tilt = math.degrees(math.atan2(math.sin(rt) / HALF_W, math.cos(rt) / b))
            if abs(th) == 48 and row % 2 == 0:   # V2 (v72): red upper flank plates on alternate bands, his red reads from the side
                mat = "accent"
            kit.plate("armor_%d_%d" % (row, j), mat, c, w, h, 0.05, (-90 - pitch, tilt, 0), bend=0.3, bevel=0.01,
                      recess=0.015, rim=0.04)
            if abs(th) <= 48:   # v11 detail pass: two dark rivets and a seam on each upper plate (his plates carry bolts and lines)
                for dy in (-0.09, 0.09):
                    rv = kit.on_surface(core, aim + Vector((0, dy, 0)), normal, 0.045)
                    kit.shell("rivet_%d_%d_%d" % (row, j, dy > 0), "trim", rv, (0.035, 0.035, 0.025), (-90 - pitch, tilt, 0), 0.5, levels=0)
                sm = kit.on_surface(core, aim, normal, 0.05)
                kit.shell("seam_%d_%d" % (row, j), "frame_dark", sm, (0.012, h * 0.4, 0.012), (-90 - pitch, tilt, 0), 0.5, levels=0)
    # the mane: raked blood-red plates over the withers and the back of the neck, standing off the black
    for k, (y, z, w) in enumerate(((-0.95, 1.4 + UP, 0.42), (-0.76, 1.44 + UP, 0.46), (-0.56, 1.46 + UP, 0.46), (-0.36, 1.44 + UP, 0.42))):
        c = kit.on_surface(core, (0, y, z), (0, -0.35, 1), 0.07)
        kit.plate("mane_%d" % k, "accent", c, w, 0.34, 0.06, (-58, 0, 0), bend=0.35, bevel=0.01, taper=0.4)   # v2: bigger, raked
    # the keel chest, dark grey, and the Howl Burst emitter: a red-ribbed grille in the throat
    c = kit.on_surface(core, (0, -1.05, 0.95 + UP), (0, -1, -0.2), 0.03)
    kit.plate("chest_keel", "frame", c, 0.4, 0.5, 0.08, (12, 0, 0), bend=0.5, bevel=0.012)
    for k in range(3):
        kit.segment("howl_rib_%d" % k, "accent", c + Vector((-0.14, -0.06, 0.14 - 0.1 * k)), c + Vector((0.14, -0.06, 0.14 - 0.1 * k)),
                    0.035, 0.03, 0.5)
    # belly: dark grey plates under the tuck
    for k, y in enumerate((-0.5, 0.0, 0.5)):
        c = kit.on_surface(core, (0, y, bottom_at(y)), (0, 0, -1), 0.02)
        kit.plate("belly_%d" % k, "frame", c, 0.36, 0.34, 0.04, (90, 0, 0), bend=0.2, bevel=0.01)
    # Shadow Dash: a blood-red blade fin over each shoulder and each hip, swept back
    for sd in (-1, 1):
        for name, y, z in (("fin_sh_%d" % sd, -0.7, 1.2 + UP), ("fin_hp_%d" % sd, 0.75, 1.14 + UP)):
            c = kit.on_surface(core, (sd * HALF_W, y, z), (sd, 0, 0.2), 0.04)
            kit.plate(name, "accent", c, 0.18, 0.62, 0.05, (-30, 0, sd * 84), bend=0.1, bevel=0.008, taper=0.3)   # v2: bigger fins


# ---- the tail: long and bushy, carried level, black with a blood-red tip ------------------------------------
TAIL = [Vector((0, 1.12, 1.22 + UP)), Vector((0, 1.42, 1.13 + UP)), Vector((0, 1.72, 1.0 + UP)), Vector((0, 2.02, 0.84 + UP)), Vector((0, 2.32, 0.64 + UP))]   # 2026-10-15, Mechabeast V2 blind review 2: the tip drooped 26 cm, his tail falls lower-left (column profile: his tip 0.29-0.40 of the height, ours 0.16-0.30)   # Mechabeast V2 pass (2026-10-14): nearly level at back height, as his V2 reference (it drooped to knee height)   # wolf part pass (2026-10-13): long and steep, down to about knee height as his; v17's slope was too shallow, v12 had angled it up
TAIL_K = 4


def tail():
    for k in range(TAIL_K):
        r0, r1 = (0.17, 0.21, 0.2, 0.15)[k], (0.21, 0.2, 0.15, 0.1)[k]   # wolflike: a bushy brush, thickest mid-tail; was 0.17 to 0.09 straight
        kit.segment("tail_core_%d" % k, "main" if k < 3 else "accent", TAIL[k], TAIL[k + 1], r0 * 1.2, r1 * 1.2, 0.5)   # 2026-10-15 blind review: a bright red tip, his (was dried-blood trim)
        kit.plate("tail_core_%d_plate" % k, "accent" if k == 3 else "main", TAIL[k].lerp(TAIL[k + 1], 0.5) + Vector((0, 0, r0 * 1.1)),
                  0.18, 0.3, 0.035, (-70 - 8 * k, 0, 0), bend=0.4, bevel=0.008)
    # 2026-10-15, Mechabeast V2 blind review 2: his tail spikes are big white curved blades, ours tiny grey ticks. Now
    # that the tail droops as his (v82), six pale hooked blades on the first three segments, raked back toward the
    # tip (v77-v79 tried them on the high tail and lost side outline). None on the red tip, his has none; v83's raked
    # blades ran together into one pale crest, so these stand steeper and slimmer, each its own blade.
    for k in range(3):
        r0 = (0.17, 0.21, 0.2)[k]
        a, b = TAIL[k], TAIL[k + 1]
        back = (b - a).normalized()
        for j in range(2):
            c = a.lerp(b, 0.25 + 0.5 * j) + Vector((0, 0, r0 * 1.05))
            mid = c + Vector((0, 0, 0.18)) + back * 0.02
            tip = c + Vector((0, 0, 0.3)) + back * 0.1
            kit.segment("tail_core_%d_fin%d" % (k, j), "blade", c - back * 0.02, mid, 0.07, 0.11, 0.5)
            kit.segment("tail_core_%d_fin%d_tip" % (k, j), "blade", mid, tip, 0.05, 0.06, 0.5)


def tail_bone(name):
    if name.startswith("tail_core_"):
        return int(name.split("_")[2])
    return None


# ---- the head: an elongate skull on a thick neck, a narrow muzzle, erect ears, red fangs ---------------------
HC = Vector((0, -1.66, 1.48 + UP))   # wolf pass 4 (column profile): 10 cm lower, his back line sits higher against the ear tips; was 1.58   # wolflike pass (2026-10-13, Preston: "make wolf look more wolflike"): the head carried above the back on a rising neck; was (-1.72, 1.36)


def head():
    hc = HC
    kit.segment("neck_core", "main", Vector((0, -0.95, 1.22 + UP)), hc + Vector((0, 0.18, -0.02)), 0.5, 0.42, 0.5)
    for k in range(3):
        c = kit.on_surface(bpy.data.objects["neck_core"], Vector((0, -1.12 - 0.18 * k, 1.45 + UP)), (0, -0.2, 1), 0.03)
        kit.plate("neckplate_%d" % k, "accent" if k < 2 else "main", c, 0.36, 0.16, 0.04, (-74, 0, 0), bend=0.4, bevel=0.008, taper=0.3)
    side = [(0.26, 0.0), (0.22, 0.22), (0.04, 0.3), (-0.18, 0.28), (-0.275, 0.16), (-0.425, 0.1), (-0.59, 0.04), (-0.635, -0.06), (-0.59, -0.14), (-0.388, -0.16), (-0.1, -0.2), (0.2, -0.16)]   # muzzle pass (2026-10-13, column profile): 25% shorter beyond the eyes, his head is 16% of the length, ours was 22%   # wolflike: a domed forehead and a stop down to the muzzle   # v2: muzzle 20% shorter (v1 read as a crocodile)
    front = kit.mirror_x([(0.12, 0.26), (0.24, 0.16), (0.27, 0.0), (0.22, -0.14), (0.12, -0.2)])
    skull = kit.profile_solid("head_core", "main", hc, side, front, chamfer=0.012,
                              top_xy=kit.mirror_x([(0.27, 0.3), (0.27, 0.0), (0.22, -0.275), (0.15, -0.463), (0.1, -0.65)]))   # wolflike: the muzzle tapers to a narrow nose
    for k, (dy, dz, w, ang) in enumerate(((0.0, 0.25, 0.3, -88), (-0.275, 0.2, 0.26, -80), (-0.515, 0.1, 0.2, -70))):
        kit.plate("headplate_%d" % k, "main", hc + Vector((0, dy, dz)), w, 0.22, 0.04, (ang, 0, 0), bend=0.4, bevel=0.008,
                  recess=0.012, rim=0.03)
    # the lower jaw and the Fang Lunge: red fangs at the front corners
    jaw_side = [(0.1, -0.14), (-0.275, -0.18), (-0.545, -0.14), (-0.575, -0.24), (-0.425, -0.3), (0.05, -0.28)]
    jaw_front = kit.mirror_x([(0.2, -0.14), (0.21, -0.24), (0.14, -0.3)])
    kit.profile_solid("head_jaw", "main", hc, jaw_side, jaw_front, chamfer=0.01,
                      top_xy=kit.mirror_x([(0.21, 0.12), (0.21, -0.1), (0.16, -0.35), (0.1, -0.59)]))
    for s in (-1, 1):
        kit.segment("head_fang_%d" % s, "tusk", hc + Vector((s * 0.15, -0.53, -0.1)), hc + Vector((s * 0.16, -0.56, -0.36)), 0.06, 0.035, 0.5)
        kit.segment("head_fang_low_%d" % s, "tusk", hc + Vector((s * 0.13, -0.485, -0.32)), hc + Vector((s * 0.14, -0.47, -0.1)), 0.05, 0.03, 0.5)
        # eyes: a visor slot each side, forward on the skull
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.2, -0.34, 0.1)), (0.07, 0.2, 0.09), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.235, -0.34, 0.1)), (0.04, 0.15, 0.05), (0, 0, 0), 0.0, levels=0)
        # erect triangular ears, black with a red inner face
        base = hc + Vector((s * 0.12, 0.08, 0.24))
        kit.plate("ear_%d" % s, "main", base + Vector((s * 0.02, 0.0, 0.18)), 0.2, 0.34, 0.04, (-10, 0, s * 38), bend=0.5, taper=0.2, bevel=0.008)   # v47 (column profile): turned out so the side view shows two broad ears, his
        kit.plate("ear_%d_inner" % s, "accent", base + Vector((s * 0.02, -0.02, 0.17)), 0.11, 0.24, 0.015, (-10, 0, s * 38), bend=0.5, taper=0.2, bevel=0.004)
        kit.disc("head_hinge_%d" % s, hc + Vector((s * 0.25, -0.1, -0.1)), 0.08, depth=0.1)
        # red cheek fins swept back along the jaw hinge
        kit.plate("head_fin_%d" % s, "accent", hc + Vector((s * 0.26, 0.05, -0.02)), 0.08, 0.26, 0.03, (0, 0, s * 70), bend=0.1, taper=0.3, bevel=0.006)
    kit.shell("head_nose", "trim", hc + Vector((0, -0.63, -0.03)), (0.08, 0.07, 0.07), (0, 0, 0), 0.5, levels=1)
    # pass 2 detail (foundation): a red brow crest, two antenna masts behind the ears, a chin guard
    kit.plate("head_crest", "accent", hc + Vector((0, -0.2, 0.27)), 0.07, 0.42, 0.04, (-86, 0, 0), bend=0.2, taper=0.4, bevel=0.006)
    for s in (-1, 1):
        weapons.antenna(kit, "head_mast_%d" % s, hc + Vector((s * 0.16, 0.2, 0.2)), hc + Vector((s * 0.2, 0.46, 0.42)))
    kit.plate("head_chin", "frame", hc + Vector((0, -0.365, -0.31)), 0.22, 0.3, 0.03, (90, 0, 0), bend=0.3, bevel=0.006)


# ---- legs: long, the elbows in and the paws out, big flexible feet with four red claws -----------------------
STAGGER = 0.1   # v10: both forelegs show side by side as in his sprite (0.06 hid the far one)
JOINTS = {}


def legs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        fo, ho = Vector((0, s * STAGGER - 0.1, 0)), Vector((0, -s * STAGGER, 0))   # V2 (v70): forelegs 10 cm forward, his near paw reaches under the head
        sh = Vector((s * 0.26, -0.86, 1.67)) + fo   # wolf pass 4: the shoulder 20 cm forward so the fore paw reaches under the nose without leaving the floor   # ref-5: +0.25 with UP   # pass 2 (open A): the foreleg reaches forward to a paw ahead of the chest   # v9: the upper arm runs down and forward from the chest, the forearm drops vertical ahead of it (his forelegs)
        el = Vector((s * 0.25, -0.8, 1.0)) + fo   # v52: partway (v51 at -0.62 cost the SE view); v51 (column profile): the elbow back and lower, a longer foreleg (about 1.8 m against 1.5) so the reaching paw stays on the floor; it was lifted, out of reach   # ref-5 part pass (2026-10-13): the elbow back under the shoulder, the forearm slants well forward to a paw ahead of the chest (his; front region 0.358)
        wr = Vector((s * 0.27, -1.36, 0.3)) + fo
        hp = Vector((s * 0.26, 0.78, 1.65)) + ho   # ref-5: +0.25 with UP   # v7: the reference's digitigrade Z: knee forward, hock back, foot forward
        kn = Vector((s * 0.27, 0.56, 1.1)) + ho   # pass 2 (open A): the hock back behind the hip, his hind feet trail
        an = Vector((s * 0.27, 1.16, 0.56)) + ho
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: wr + Vector((0, -0.22, -0.26)),
                       "hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: an + Vector((0, -0.34, -0.42))})
        JOINTS["fingers." + side] = wr + Vector((0, -0.2, -0.26))
        for pre, a, b, c, w0, w1 in (("front", sh, el, wr, 0.13, 0.1), ("hind", hp, kn, an, 0.2, 0.12)):   # v10: forelegs slimmer, his are lean columns
            kit.limb_solid("%s_upper_%d" % (pre, s), "frame", a, b, (s, 0, 0), [(0, w0, w0 - 0.02), (1, w1, w1 - 0.02)], [(0, w0), (1, w1)])
            kit.limb_solid("%s_lower_%d" % (pre, s), "frame", b, c, (s, 0, 0), [(0, w1, w1 - 0.02), (1, w1 - 0.03, w1 - 0.04)], [(0, w1), (1, w1 - 0.03)])
            kit.disc("%s_knee_%d" % (pre, s) if pre == "hind" else "front_elbow_%d" % s, b + Vector((s * 0.2, 0, 0)), 0.19, depth=0.12)   # synthesis pass (2026-10-13): bigger and proud of the armour, his reference and the Zoids rips show big joint hubs   # v5: the reference's big joint discs
            kit.disc("%s_scale_%d_hub" % (pre, s), a + Vector((s * 0.3, 0, -0.04)), 0.17, depth=0.1)
            kit.disc("%s_shin_%d_wrist" % (pre, s), c + Vector((s * 0.03, 0, 0.04)), 0.09, depth=0.18)   # v10: a wrist and ankle disc, his joints
            up, lo = bpy.data.objects["%s_upper_%d" % (pre, s)], bpy.data.objects["%s_lower_%d" % (pre, s)]
            kit.plate("%s_scale_%d" % (pre, s), "main", kit.on_surface(up, a.lerp(b, 0.45), (s, 0, 0), 0.025), 0.22, 0.34,
                      0.045, (-6, 0, s * 84), bend=0.35, bevel=0.008, recess=0.012, rim=0.03)   # black thigh and shoulder plates
            kit.plate("%s_shin_%d" % (pre, s), "main", kit.on_surface(lo, b.lerp(c, 0.4), (s, 0, 0), 0.02), 0.14, 0.26,
                      0.035, (-4, 0, s * 84), bend=0.35, bevel=0.008)
            # the paw: a big flexible foot, dark, four blood-red claws forward
            if pre == "hind":   # pass 2: the pastern, a thin strut from the high hock to a paw on the floor
                c = c + Vector((0, -0.1, -0.3))
                kit.limb_solid("hind_foot_meta_%d" % s, "frame", an, c, (s, 0, 0), [(0, 0.1, 0.08), (1, 0.08, 0.07)], [(0, 0.1), (1, 0.08)])
                kit.disc("hind_foot_hock_%d" % s, an + Vector((s * 0.03, 0, 0)), 0.09, depth=0.18)
            # pass 2 detail: a hydraulic ram along each upper limb, riding the upper bone
            weapons.piston(kit, "%s_upper_pst" % pre, a + (b - a) * 0.1 + Vector((s * 0.12, 0.06, 0)), a + (b - a) * 0.85 + Vector((s * 0.12, 0.06, 0)), 0.035, sfx="_%d" % s)
            foot_c = c + Vector((0, -0.08, -0.14))   # v4: the paw's sole on the floor; the claws grow from its front edge
            kit.shell("%s_foot_%d" % (pre, s), "frame_dark", foot_c, (0.22, 0.34, 0.2), (0, 0, 0), 0.5, levels=1)   # Legacy pass (v61): big feet
            kit.plate("%s_foot_%d_cap" % (pre, s), "main", foot_c + Vector((0, -0.02, 0.1)), 0.24, 0.24, 0.03, (-70, 0, 0), bend=0.4, bevel=0.006)
            # v49 (Preston: "the claws look like one line instead of 3"): three hooked claws, fanned so the side view shows
            # each one. Four claws side by side at one angle stacked into a single red line from the side. Each claw is
            # a knuckle segment and a hook curling down; the middle claw reaches longest and lowest, the outer two shorter
            # and higher, so their tips sit at different points along the paw.
            # 2026-10-15, Mechabeast V2 blind review 2: his talons are big bright red hooks about as long as the toe block;
            # ours read as one- or two-pixel streaks (hidden in the paw armour). Now about twice as thick and long, three
            # segments each (knuckle, hook, point) curling down to the floor, fanned wider. Reach kept near the old claws
            # (v81 reached 0.64 m and the wider sprite cost 0.024 of side outline); the extra length goes into the curl.
            for k, (dx, ty, tz) in enumerate(((-0.14, -0.38, 0.02), (0.0, -0.46, -0.06), (0.14, -0.33, 0.04))):
                base = Vector((foot_c.x + dx * 0.7, foot_c.y - 0.14, foot_c.z + 0.1))
                knuckle = Vector((foot_c.x + dx, foot_c.y + ty * 0.7, foot_c.z + tz + 0.16))
                bend = Vector((foot_c.x + dx * 1.15, foot_c.y + ty * 1.02, foot_c.z + tz + 0.04))
                tip = Vector((foot_c.x + dx * 1.25, foot_c.y + ty, foot_c.z + tz - 0.12))
                kit.segment("%s_claw_%d_%d" % (pre, s, k), "claw", base, knuckle, 0.14, 0.13, 0.5)
                kit.segment("%s_claw_%d_%d" % (pre, s, 10 + k), "claw", knuckle, bend, 0.12, 0.1, 0.5)
                kit.segment("%s_claw_%d_%d" % (pre, s, 20 + k), "claw", bend, tip, 0.08, 0.06, 0.5)


# ---- pass 2 detail layer (2026-10-13, Preston: "add more pieces and parts, it kind of looks like a bare prototype";
# foundation for a Codex reference, not refined): spine ridge, flank vents, exhaust stacks, a neck collar, belly
# cables, tail joint rings.
def details():
    core = bpy.data.objects["torso_core"]
    for k, y in enumerate((-0.2, 0.05, 0.3, 0.55, 0.8, 1.0)):
        c = kit.on_surface(core, (0, y, top_at(y) + 0.1), (0, 0, 1), 0.1)
        kit.plate("spine_%d" % k, "accent", c, 0.22, 0.32, 0.08, (-80, 0, 0), bend=0.2, taper=0.7, bevel=0.01)   # V2 (v68): taller, his back stands higher with red plates   # V2: bigger red plates along the back, his
    for sd in (-1, 1):
        c = kit.on_surface(core, (sd * HALF_W, 0.15, (top_at(0.15) + bottom_at(0.15)) / 2 + 0.05), (sd, 0, 0), 0.04)
        weapons.vent(kit, "flank_vent_%d" % sd, c, 0.2, 0.3, (0, sd * 90, 0), slats=3)
        weapons.jet(kit, "exhaust_%d" % sd, "", (sd * 0.14, 0.92, top_at(0.92) - 0.06), (sd * 0.2, 1.1, top_at(0.92) + 0.16), 0.05)
        weapons.cable(kit, "belly_cable_%d" % sd, [(sd * 0.12, -0.7, bottom_at(-0.7) + 0.02), (sd * 0.14, -0.2, bottom_at(-0.2) - 0.02),
                                                   (sd * 0.12, 0.4, bottom_at(0.4) - 0.01)], 0.025)
    kit.cyl("neck_collar", "trim", Vector((0, -0.9, 1.24 + UP)), Vector((0, -1.0, 1.26 + UP)), 0.3, 12)
    for k in range(1, TAIL_K):
        kit.cyl("tail_core_%d_ring" % k, "accent" if k == 3 else "frame", TAIL[k] - (TAIL[k + 1] - TAIL[k]).normalized() * 0.03,
                TAIL[k] + (TAIL[k + 1] - TAIL[k]).normalized() * 0.03, 0.16 - 0.02 * k, 10)


# ---- armor pass (2026-10-13, Preston on the ChatGPT render of v26: "still looks like a naked canine, parts stripped
# robot with weapons"): sleeves over every limb segment, shoulder and hip pads, armored paws, neck plates, cheek
# guards and a helmet, tail side armor. Black armor, red trim; the grey frame shows only at the joints.
def armor():
    G = 1.2   # the head group's scale in main(); head parts made here are placed in the scaled frame
    for s in (-1, 1):
        sd = "L" if s == 1 else "R"
        sh, el, wr = JOINTS["sh." + sd], JOINTS["el." + sd], JOINTS["wr." + sd]
        hp, kn, an = JOINTS["hp." + sd], JOINTS["kn." + sd], JOINTS["an." + sd]
        out = Vector((s * 0.02, 0, 0))
        # Legacy pass (2026-10-14, v61): every leg sleeve, guard and paw thicker; Legacy legs are armoured columns with big
        # feet (our wolf filled 0.37 of its box against Legacy's median 0.51, tools/art/legacy_gap.py)
        kit.segment("front_scale_sleeve_%d" % s, "main", sh.lerp(el, 0.05) + out, sh.lerp(el, 0.88) + out, 0.4, 0.48, 0.5)   # v29: bulkier, a muscled shoulder (v28 0.22)
        kit.segment("front_shin_guard_%d" % s, "light",   # synthesis pass: light steel lower legs, his reference
                    el.lerp(wr, 0.1) + out, el.lerp(wr, 0.8) + out, 0.3, 0.34, 0.5)
        kit.segment("hind_scale_sleeve_%d" % s, "main", hp.lerp(kn, 0.0) + out, hp.lerp(kn, 0.88) + out, 0.5, 0.56, 0.5)   # v29: a heavy haunch (v28 0.3)
        kit.segment("hind_shin_guard_%d" % s, "light",
                    kn.lerp(an, 0.1) + out, kn.lerp(an, 0.8) + out, 0.3, 0.34, 0.5)
        paw = an + Vector((0, -0.1, -0.3))
        kit.segment("hind_foot_guard_%d" % s, "light",
                    an.lerp(paw, 0.12), an.lerp(paw, 0.78), 0.26, 0.3, 0.5)
        for pre, a, b in (("front_scale", sh, el), ("front_shin", el, wr), ("hind_scale", hp, kn), ("hind_shin", kn, an)):
            w = 0.25 if pre == "front_scale" else (0.3 if pre == "hind_scale" else 0.17)   # Legacy pass (v61): sit on the thicker sleeves
            kit.segment("%s_stripe_%d" % (pre, s), "accent", a.lerp(b, 0.25) + Vector((s * w, 0, 0)), a.lerp(b, 0.65) + Vector((s * w, 0, 0)), 0.03, 0.05, 0.5)
        # shoulder and hip pads, a red rim under each
        kit.shell("front_scale_pad_%d" % s, "main", sh + Vector((s * 0.24, -0.02, 0.0)), (0.16, 0.56, 0.5), (0, 0, 0), 0.6, levels=1)
        kit.shell("front_scale_padrim_%d" % s, "accent", sh + Vector((s * 0.25, -0.02, -0.27)), (0.17, 0.54, 0.06), (0, 0, 0), 0.5, levels=0)
        kit.shell("hind_scale_pad_%d" % s, "main", hp + Vector((s * 0.27, 0.0, -0.06)), (0.16, 0.62, 0.52), (0, 0, 0), 0.6, levels=1)
        kit.shell("hind_scale_padrim_%d" % s, "accent", hp + Vector((s * 0.28, 0.0, -0.34)), (0.17, 0.6, 0.06), (0, 0, 0), 0.5, levels=0)
        # armored paws
        for pre, c in (("front_foot", wr + Vector((0, -0.08, -0.14))), ("hind_foot", paw + Vector((0, -0.08, -0.14)))):
            kit.shell("%s_armor_%d" % (pre, s), "main", c + Vector((0, -0.04, 0.13)), (0.36, 0.42, 0.14), (-10, 0, 0), 0.6, levels=1)
        # neck plates down each side, following the neck's rise
        n0, n1 = Vector((0, -0.95, 1.22 + UP)), HC + Vector((0, 0.18, -0.02))
        pitch = math.degrees(math.atan2(-(n1.z - n0.z), -(n1.y - n0.y)))
        for k, t in enumerate((0.22, 0.5, 0.78)):
            kit.shell("neck_side_%d_%d" % (s, k), "main" if k != 1 else "trim", n0.lerp(n1, t) + Vector((s * 0.24, 0, -0.02)), (0.08, 0.26, 0.34), (pitch, 0, 0), 0.6, levels=1)
        # cheek guards along the jaw hinge
        kit.shell("head_cheek_%d" % s, "main", HC + Vector((s * 0.25, -0.1, -0.1)) * G, (0.07, 0.36, 0.2), (0, 0, 0), 0.6, levels=1)
    core = bpy.data.objects["torso_core"]
    for k, (ang, w, h, mat) in enumerate(((0, 0.5, 0.36, "main"), (-40, 0.36, 0.34, "accent"), (40, 0.36, 0.34, "accent"),
                                         (-75, 0.34, 0.4, "main"), (75, 0.34, 0.4, "main"))):   # v29: a ruff over the withers and shoulders
        rt = math.radians(ang)
        c = kit.on_surface(core, (HALF_W * math.sin(rt), -0.82, top_at(-0.82) - 0.1 + 0.1 * math.cos(rt)), (math.sin(rt), -0.3, math.cos(rt)), 0.1)
        kit.plate("ruff_%d" % k, mat, c, w, h, 0.06, (-62, 0, -ang * 0.9), bend=0.4, bevel=0.01, taper=0.55)
    kit.shell("head_helm", "main", HC + Vector((0, 0.02, 0.3)) * G, (0.44, 0.46, 0.08), (-8, 0, 0), 0.6, levels=1)
    kit.shell("chest_armor", "main", kit.on_surface(bpy.data.objects["torso_core"], (0, -1.05, 1.05 + UP), (0, -1, 0.1), 0.06), (0.62, 0.12, 0.5), (12, 0, 0), 0.6, levels=1)
    # tail side armor on each segment
    for k in range(TAIL_K):
        a, b = TAIL[k], TAIL[k + 1]
        r0 = (0.17, 0.21, 0.2, 0.15)[k]
        tp = math.degrees(math.atan2(b.z - a.z, b.y - a.y))
        for j, sd in enumerate((-1, 1)):
            kit.shell("tail_core_%d_side%d" % (k, j), "main" if k < 3 else "accent", a.lerp(b, 0.5) + Vector((sd * r0 * 1.1, 0, 0)), (0.035, (b - a).length * 0.7, r0 * 1.25), (tp, 0, 0), 0.6, levels=1)   # v29: slimmer (v28 read as a block chain)


# ---- the loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"). The roster's three
# moves get hardware; two spare hardpoints are DRAFT (move None), Preston's to name. tools/blender/weapons.py.
def loadout():
    A = weapons.anchor
    L = [
        {"slot": "fang", "move": "Fang Lunge", "kind": "spikes", "prefix": "head_", "note": "red teeth along the upper jaw",
         "args": {"points": [A("head_core", (fx, fy, 0.18)) for fx in (0.22, 0.78) for fy in (0.06, 0.14, 0.22)],
                  "length": 0.1, "r": 0.03, "direction": (0, 0, -1), "mat": "tusk"}},
        {"slot": "howl", "move": "Howl Burst", "kind": "emitter", "prefix": "neck_", "note": "the throat emitter",
         "args": {"center": A("neck_core", (0.5, 0.2, 0.12)), "direction": (0, -1, -0.35), "r": 0.11}},
        {"slot": "rail", "move": None, "kind": "cannon", "note": "spare: a long rail gun on the right of the back",
         "args": {"base": (-0.2, 0.0, top_at(0.0) + 0.12), "direction": (0, -1, 0.04), "length": 1.05, "r": 0.05,
                  "housing": (0.2, 0.46, 0.17)}},
    ]
    for sd in (-1, 1):
        side = "L" if sd == 1 else "R"
        el, wr = JOINTS["el." + side], JOINTS["wr." + side]
        L.append({"slot": "dash" + side, "move": "Shadow Dash", "kind": "blade", "prefix": "front_shin_", "suffix": "_%d" % sd,
                  "note": "a swept blade on the outside of each forearm",
                  "args": {"center": el.lerp(wr, 0.35) + Vector((sd * 0.11, 0.06, 0)), "w": 0.08, "h": 0.42, "rot": (-20, 0, sd * 84)}})
        L.append({"slot": "pod" + side, "move": None, "kind": "missile_pod", "note": "spare: a 2x2 launcher on each haunch",
                  "args": {"center": (sd * 0.28, 0.48, top_at(0.48) + 0.08), "size": (0.22, 0.3, 0.2), "rows": 2, "cols": 2, "rot": (-25, 0, 0)}})
    return L


CFG = {
    "battle_set": "wolf_m",   # battle clips: tools/blender/attacks.py (2026-10-13)
    "name": "wolf_m",
    "head": ("head_", "headplate", "neck", "eye_", "ear_"),
    "tail_bone": tail_bone,
    "tail_points": TAIL,
    "tail_sway": 1.6,
    "body_bone": ((0, 0.75, 1.1), (0, -0.75, 1.15)),
    "head_bone": ((0, -1.0, 1.25), (0, -2.6, 1.3)),
    "joints": JOINTS,
    "stride": 0.34,
    # ref-5 pass 3 (2026-10-13): the battle stance by foot positions (quad_rig.battle_pose_for), his long stride: near
    # fore paw far forward under the nose, far fore paw back, near hind paw back, far hind paw forward. dy < 0 is forward.
    "stance": "clip=battle;frame=1",
    "battle_feet": {"R_arm": (-0.6, 0.0), "L_arm": (0.2, 0.0), "R_leg": (0.25, 0.0), "L_leg": (-0.55, 0.0)},   # V2: hind feet 25-30 cm back, his stalking reach   # v47: far fore back to two-thirds of the length (column profile); v37: all forward, his fore paw under the nose
    "crouch": 0.03,
    "front_path": (0.06, 0.0, 0.14, -8),   # back, down, lift, curl: a trotting reach (v3: less curl, the paw stayed on the leg)
    "hind_path": (-0.06, 0.0, 0.14, 0),
}


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    tail()
    head()
    for o in list(bpy.context.scene.objects):   # v12 (look-compare): his head is bigger; the head group 1.2x about HC
        if o.type == "MESH" and o.name.startswith(("head_", "headplate", "eye_", "ear_")):
            o.location = HC + (o.location - HC) * 1.2
            o.scale = tuple(v * 1.2 for v in o.scale)
    details()
    legs()
    armor()
    weapons.build_loadout(kit, "wolf_m", loadout())
    greebles.run(kit, weapons, lambda n: quad.bone_for(n, CFG), skip_prefix=("torso_core",))   # v71: the core is under armour already; its layer plate hid the red back
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "wolf_m"
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("WOLF_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
