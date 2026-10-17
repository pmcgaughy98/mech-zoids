# The pangolin machine, the creature factory's first product after the gorilla (Claude, 2026-10-12).
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_pangolin_m.py
# Reuses the gorilla's part kit (tools/blender/build_ape_l_v2.py, loaded with MECH_KIT_IMPORT=1). Design from the real
# animal (Wikipedia "Pangolin", WildAid, 2026-10-12): the whole body and tail covered in overlapping armour scales like a
# pine cone, a small pointed head, short legs, big curved front claws tucked under the feet when walking, a long heavy
# tail. Colours: Preston's proposal in scripts/data/machines.gd (ochre scales, madder trim, delft snout, teal eyes).
# Rig: the shared quadruped rig (quad_rig.py, which began as this file's v16-v18 rig); walk and idle clips; the sprite
# stance is written to docs/art/3d/pangolin_m.stance for SPRITE_STANCE.
import re
import bmesh
import bpy, importlib.util, math, os, sys
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
os.environ["MECH_KIT_IMPORT"] = "1"
spec = importlib.util.spec_from_file_location("mech_kit", os.path.join(HERE, "build_ape_l_v2.py"))
kit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kit)
_qspec = importlib.util.spec_from_file_location("quad_rig", os.path.join(HERE, "quad_rig.py"))
quad = importlib.util.module_from_spec(_qspec)
_qspec.loader.exec_module(quad)
_wspec = importlib.util.spec_from_file_location("weapons", os.path.join(HERE, "weapons.py"))
wpn = importlib.util.module_from_spec(_wspec)
_wspec.loader.exec_module(wpn)
import importlib.util as _gu
_gs = _gu.spec_from_file_location("greebles", os.path.join(os.path.dirname(os.path.abspath(__file__)), "greebles.py"))
greebles = _gu.module_from_spec(_gs)
_gs.loader.exec_module(greebles)   # the detail pass (2026-10-14)
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "pangolin_m.blend")

PAL = {   # material keys the kit's parts use, with this machine's colours
    "main": "da8600",        # ochre scales
    "trim": "a02010",        # madder: claws and trim
    "accent": "407090",      # delft: the snout
    "frame": "5f636b",       # grey limbs and joints (v2: darker, the pale limbs read washed out)
    "frame_dark": "4a4c53",  # the dark body under the scales (v2: lighter, less of the silhouette near-black)
    "face": "45464c",        # the bare face (p42: darker than the limbs' grey, so the head reads apart from the legs; was 55575e)
    "light": "a02010",       # part pass: the joint rings read red-centred, as in Preston's reference
    "eye_src": "5fe1d0",     # the eyes: the sprite render keeps this teal
    "claw": "d0281a",        # p42: the claws a clear bright red (judges: "large red claws", "in clear red"); trim stays madder
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


# ---- the body: a dark arched core, covered in rows of overlapping scales ---------------------------------------
TOP = [(-0.9, 1.22), (-0.65, 1.44), (-0.3, 1.52), (0.15, 1.42), (0.6, 1.16), (0.9, 0.84)]   # p20 (column profile): the dome stays high to its front, his armour runs up to the head   # ref-5 part pass (2026-10-13): the dome peaks forward over the shoulders, steep to the head (his); reference pass had the peak mid-back
BOTTOM = 0.42


def top_at(y):
    for (y0, z0), (y1, z1) in zip(TOP, TOP[1:]):
        if y0 <= y <= y1:
            return z0 + (z1 - z0) * (y - y0) / (y1 - y0)
    return TOP[0][1] if y < TOP[0][0] else TOP[-1][1]


def half_width(y):
    return 0.56 * math.sqrt(max(0.12, 1 - ((y - 0.0) / 1.05) ** 2))


def body():
    side = [(-0.95, 0.5), (-0.95, 1.05)] + [(y, z) for y, z in TOP] + [(0.95, 0.5), (0.6, 0.4), (-0.6, 0.4)]   # v14
    front = kit.mirror_x([(0.1, 1.47), (0.29, 1.42), (0.49, 1.22), (0.56, 0.96), (0.5, 0.7), (0.38, 0.52),
                          (0.26, 0.42)])   # reference pass: the dome follows the higher back, a touch slimmer low down
    core = kit.profile_solid("torso_shell", "frame_dark", (0, 0, 0), side, front, chamfer=0.02)
    if SCALE_TILES:
        scale_tiles(core)
        return
    row = 0
    y = -0.86
    while y <= 0.92:
        t, a = top_at(y), half_width(y)
        zc, b = (t + BOTTOM) / 2 + 0.04, (t - BOTTOM) / 2 + 0.04
        a = a + 0.07   # v10: the ellipse is now only the aim; v13 places each scale on the real surface below
        n = max(3, int(round(math.pi * (a + b) / 2 / 0.36 * 1.9)))   # p6 (look-compare): denser scales, the grey core showed between them
        for j in range(n):
            th = math.radians(-140 + 280 * (j + 0.5 * (row % 2)) / n)   # alternate rows offset, like a pine cone
            if abs(th) > math.radians(140):   # v9/v10: down the flanks to the belly line
                continue
            x, z = a * math.sin(th), zc + b * math.cos(th)
            tilt = math.degrees(math.atan2(math.sin(th) / a, math.cos(th) / b))
            pitch = math.degrees(math.atan2(-(top_at(y + 0.05) - top_at(y - 0.05)), 0.1))   # v2: follow the back's slope
            c = kit.on_surface(core, (x, y, z), (math.sin(th) / a, 0, math.cos(th) / b), 0.045)   # v13: kit ray cast
            kit.plate("scale_%d_%d" % (row, j), "main", c, 0.36, 0.44, 0.05, (-78 - pitch, tilt, 0), bend=0.35,   # p6: smaller, overlapping
                      taper=0.55,   # v3: leaf-shaped, narrowing to the rear tip like a real pangolin scale
                      bevel=0.01)
        row += 1
        y += 0.24   # p6: rows closer


# Model pass p42 (2026-10-16; blind judges: "the pangolin's scales are not in ordered rows"). The leaf plates above
# (bent, tapered, overlapping by more than half side by side) shrank to slivers and speckle at x4.4. The reference
# has chunky bevelled tiles in rings round the body, a dark gap between rings, each tile overlapping the one below it
# like roof shingles. So: SCALE_RINGS rings across the back, tiles about 10 x 8 sprite px each, the gap between rings
# about 2 px of the dark core (the seam), each tile's lower edge lifted over the tile below and its rear edge over the
# next ring (real pangolin scales point to the tail).
SCALE_TILES = True
# rings: (centre along the body, forward lean of the tiles, degrees left bare at the spine). The first is a collar on the
# core's flat front wall beside the head (it showed as a dark slab in the side view), leaning forward, the spine left to
# the neck plates
SCALE_RINGS = ((-0.95, 1.0, 30), (-0.80, 0, 0), (-0.49, 0, 0), (-0.18, 0, 0), (0.13, 0, 0), (0.44, 0, 0), (0.74, 0, 0))
TILE_LEN = 0.25     # along the body; leaves a 0.06 dark seam to the next ring
TILE_W = 0.32       # round the body (arc), the tiles about touching
TILE_T = 0.09       # thickness: 3 sprite px, its lower face the shaded seam under each tile
TILE_ARC = 128      # degrees from the spine down each flank


def scale_tiles(core):
    """The rings of tiles. Spacing round each ring is measured on the core's real surface (ray cast every 2 degrees),
    so the flank tiles touch as the top ones do (spacing on the aiming ellipse left 4 cm gaps down the flanks)."""
    for r, (y, lean, arc0) in enumerate(SCALE_RINGS):
        t, a = top_at(y), half_width(y) + 0.02
        zc, b = (t + BOTTOM) / 2 + 0.04, (t - BOTTOM) / 2 + 0.02
        slope = (top_at(y + 0.05) - top_at(y - 0.05)) / 0.1
        da = (half_width(y + 0.05) - half_width(y - 0.05)) / 0.1
        samples = []   # (th, surface point, normal) every 2 degrees down both flanks
        for th in range(-TILE_ARC, TILE_ARC + 1, 2):
            if abs(th) < arc0:
                continue
            rt = math.radians(th)
            n0 = Vector((math.sin(rt) / a, 0, math.cos(rt) / b)).normalized()
            nrm = n0.copy()
            nrm.y = -slope * max(0.0, n0.z) - da * abs(n0.x) - lean   # follow the back's slope and the body's taper
            nrm.normalize()
            aim = Vector((a * math.sin(rt), y, zc + b * math.cos(rt)))
            hit = kit.surface_hit(core, aim + nrm * 3.0, -nrm)
            if hit:
                samples.append((th, hit[0], nrm))
        for half in ((s_ for s_ in samples if s_[0] < 0), (s_ for s_ in samples if s_[0] >= 0)) if arc0 else (samples,):
            run = list(half)
            if len(run) < 2:
                continue
            ss = [0.0]
            for (_, p0, _), (_, p1, _) in zip(run, run[1:]):
                ss.append(ss[-1] + (p1 - p0).length)
            n = max(1, int(round(ss[-1] / TILE_W)))
            step = ss[-1] / n
            # alternate rings half a tile round, pine-cone style; their end tiles are half tiles
            if r % 2 == 0 or arc0:
                tiles = [(step * (j + 0.5), step) for j in range(n)]
            else:
                tiles = [(step * 0.25, step * 0.5)] + [(step * j, step) for j in range(1, n)] + [(ss[-1] - step * 0.25, step * 0.5)]
            for s, wide in tiles:
                i = min(range(len(ss)), key=lambda q: abs(ss[q] - s))
                th, p, nrm = run[i]
                xa = Vector((0, 1, 0)).cross(nrm).normalized()   # round the body (+x on the spine), toward larger th
                ya = nrm.cross(xa).normalized()                 # along the body, toward the tail
                frame = Matrix((xa, ya, nrm)).transposed()
                down = 1 if th > 0 else -1                      # which way "down the flank" runs along xa
                lift = frame @ Matrix.Rotation(math.radians(-10 * down if abs(th) > 12 else 0), 3, "Y") \
                    @ Matrix.Rotation(math.radians(7), 3, "X")   # lower edge out over the tile below; rear edge out over the next ring
                c = p + nrm * (TILE_T / 2 + 0.012)
                k = len([o for o in bpy.data.objects if o.name.startswith("scale_%d_" % r)])
                ob = kit.shell("scale_%d_%d" % (r, k), "main", (0, 0, 0), (wide * 0.94, TILE_LEN, TILE_T), (0, 0, 0), crease=0.4, levels=1)
                ob.matrix_world = Matrix.Translation(c) @ lift.to_4x4()


# ---- the tail: a tapering curve down to the ground, scaled on top and sides ----------------------------------
def tail_point(t):
    p0, p1, p2 = Vector((0, 0.85, 0.78)), Vector((0, 1.85, 0.55)), Vector((0, 2.7, 0.12))   # ref-5: a straight decline to the tip, his (the 0.8 control held it level then high); reference pass: a longer tail
    return p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t ** 2


def tail():
    k_max = 9
    for k in range(k_max):
        t0, t1 = k / k_max, (k + 1) / k_max
        a, b = tail_point(t0), tail_point(t1)
        r = 0.32 * (1 - t0) + 0.06
        kit.segment("tail_core_%d" % k, "frame_dark", a, b, 2 * r, 1.6 * r, 0.5)
        pitch = math.degrees(math.atan2(-(b - a).z, (b - a).y))   # the tail slopes down: tip the scales with it
        mid = (a + b) / 2
        for j, th in enumerate((-70, -25, 25, 70) if r > 0.18 else (-40, 40)):
            rt = math.radians(th)
            c = mid + Vector((r * math.sin(rt), 0, 0.8 * r * math.cos(rt) + 0.03))
            kit.plate("tailscale_%d_%d" % (k, j), "trim" if k >= 6 else "main", c, 0.34 * r / 0.3 + 0.08, 0.42, 0.045, (-78 - pitch, th, 0),   # v2: lie flat along the tail (v1 sign stood them up)
                      bend=0.35, bevel=0.01)
    kit.segment("tail_tip", "trim", tail_point(0.95), tail_point(1.0) + Vector((0, 0.24, -0.05)), 0.18, 0.05, 0.5)   # v6: blade


# ---- the head: small and pointed, bare grey face, delft snout, two rows of small scales on top ---------------
HC = Vector((0, -1.02, 0.90))   # the head's centre (ref-5: 0.74, his head hangs low; p42: 16 cm up, so the snout's
# underside clears the front feet in the side view: "the snout merges with the front leg")
HEAD_TILT = 6   # p42: degrees nose-up about the head's back (main())


def head():
    hc = HC
    # p42: a longer wedge with a level jaw line rising to the tip (the reference's snout runs well past the front feet,
    # background showing under it); before: the wedge ended at -0.55 and its jaw sloped down onto the claws
    side = [(0.2, -0.12), (0.22, 0.08), (0.08, 0.2), (-0.15, 0.16), (-0.46, 0.06), (-0.62, 0.0), (-0.62, -0.06),
            (-0.42, -0.11), (-0.1, -0.19)]
    front = kit.mirror_x([(0.12, 0.2), (0.22, 0.06), (0.24, -0.04), (0.16, -0.18)])
    kit.profile_solid("head_core", "face", hc, side, front, chamfer=0.012)
    snout_side = [(-0.56, 0.03), (-0.68, -0.01), (-0.72, -0.04), (-0.69, -0.08), (-0.56, -0.08)]   # p42: the tip block moved out with the wedge
    snout_front = kit.mirror_x([(0.08, 0.04), (0.11, -0.03), (0.08, -0.09)])
    snout = kit.profile_solid("snout", "face", hc, snout_side, snout_front, chamfer=0.01)   # v6: metal, no canopy; p42: the dark face grey
    for s in (-1, 1):   # nostril vents at the tip
        kit.groove(snout, hc + Vector((s * 0.025, -0.71, -0.045)), hc + Vector((s * 0.075, -0.71, -0.045)), (0, -1, 0),
                   w=0.03, d=0.025, mat="trim")
    for k in range(3):   # scale plates down the top of the snout (p42: three, bigger and thicker, so the snout reads gold on top)
        y = -0.36 - 0.13 * k
        z = 0.17 + (y + 0.15) * 0.33 + 0.02
        kit.plate("snoutscale_%d" % k, "main", hc + Vector((0, y, z)), 0.22 - 0.03 * k, 0.17, 0.05, (-72, 0, 0),
                  bend=0.25, bevel=0.01)
    for s in (-1, 1):
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.165, -0.2, 0.07)), (0.12, 0.13, 0.11), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.18, -0.2, 0.07)), (0.09, 0.09, 0.07), (0, 0, 0), 0.0, levels=0)
        kit.cyl("ear_%d" % s, "frame", hc + Vector((s * 0.2, 0.05, 0.08)), hc + Vector((s * 0.25, 0.05, 0.08)), 0.06, 12)
    for r, (dy, dz, n) in enumerate(((-0.3, 0.13, 2), (-0.12, 0.18, 3), (0.08, 0.21, 3))):   # head part: three rows, bigger
        for j in range(n):
            x = (j - (n - 1) / 2) * 0.13
            kit.plate("headscale_%d_%d" % (r, j), "main", hc + Vector((x, dy, dz + 0.03 - abs(x) * 0.3)), 0.2, 0.22,   # head part: bigger gold crown scales
                      0.04, (-80, x * 120, 0), bend=0.3, bevel=0.008)


# ---- legs: short; front feet with big curved claws tucked under, hind feet flat ------------------------------
STAGGER = 0.12   # v2: a diagonal gait stance, near and far legs apart, so the side view shows four feet


def legs():
    for s in (-1, 1):
        fo, ho = Vector((0, s * STAGGER - 0.12, 0)), Vector((0, -s * STAGGER, 0))   # r10 part pass: front legs 12 cm forward (red under the head in the overlay)
        sh = Vector((s * 0.42, -0.55, 0.62)) + fo
        el = Vector((s * 0.5, -0.62, 0.34)) + fo
        wr = Vector((s * 0.5, -0.72, 0.14)) + fo
        side = "L" if s == 1 else "R"
        JOINT.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr,
                      "fingers." + side: Vector((s * 0.5, -0.97, 0.06)) + fo})
        kit.limb_solid("front_upper_%d" % s, "frame", sh, el, (s, 0, 0), [(0, 0.34, 0.31), (1, 0.28, 0.26)], [(0, 0.34), (1, 0.28)])   # r4: thicker, the reference's columns
        kit.limb_solid("front_lower_%d" % s, "frame", el, wr, (s, 0, 0), [(0, 0.28, 0.26), (1, 0.25, 0.23)], [(0, 0.28), (1, 0.25)])   # r4
        kit.plate("front_shin_%d" % s, "main", el.lerp(wr, 0.45) + Vector((s * 0.28, -0.06, 0.02)), 0.34, 0.32, 0.045,
                  (-8, 0, s * 70), bend=0.35, bevel=0.01)   # v2: scales down the forearm
        kit.plate("front_scale_%d" % s, "main", sh.lerp(el, 0.4) + Vector((s * 0.33, -0.04, 0.04)), 0.38, 0.42, 0.05,
                  (-15, 0, s * 70), bend=0.35, bevel=0.01)
        kit.disc("front_elbow_%d" % s, el, 0.1)
        # v2, giant pangolin (Wikipedia): curls its front paws and walks on the outside of the wrists: the foot rolls
        # outward onto its outer edge, claws tucked in
        # p42 (judges: "feet about 1.5x bigger with three distinct red claws"): the foot 1.4x wide and long, rolled less
        # (28 to 12 degrees) so its top reads as a broad grey paw; before (0.3, 0.36, 0.15) at z 0.09
        kit.shell("front_foot_%d" % s, "frame", Vector((s * 0.52, -0.78, 0.135)) + fo, (0.42, 0.5, 0.2), (0, s * 12, 0), 0.5, levels=1)
        claws(s, "front", Vector((s * 0.52, -0.99, 0.13)) + fo, 0.17, 0.07, 1.0)   # claw pass (2026-10-13): three red hooks fanned forward, his; p42: one thick curved cone each
        # v2, giant pangolin (Wikipedia): "most of its weight on its columnar rear legs": straight under the hip
        hp = Vector((s * 0.42, 0.55, 0.62)) + ho
        kn = Vector((s * 0.46, 0.57, 0.36)) + ho
        an = Vector((s * 0.46, 0.6, 0.12)) + ho
        JOINT.update({"hp." + side: hp, "kn." + side: kn, "an." + side: an,
                      "toe." + side: Vector((s * 0.46, 0.25, 0.05)) + ho})
        kit.limb_solid("hind_upper_%d" % s, "frame", hp, kn, (s, 0, 0), [(0, 0.36, 0.34), (1, 0.29, 0.27)], [(0, 0.36), (1, 0.29)])   # r5: hind columns thicker, as the front
        kit.limb_solid("hind_lower_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.29, 0.27), (1, 0.24, 0.22)], [(0, 0.29), (1, 0.24)])   # r5
        kit.plate("hind_shin_%d" % s, "main", kn.lerp(an, 0.45) + Vector((s * 0.26, 0.04, 0.02)), 0.3, 0.28, 0.045,
                  (-8, 0, s * 70), bend=0.35, bevel=0.01)   # v2: scales down the shin
        kit.plate("hind_scale_%d" % s, "main", hp.lerp(kn, 0.4) + Vector((s * 0.33, 0.02, 0.04)), 0.36, 0.38, 0.05,
                  (-15, 0, s * 70), bend=0.35, bevel=0.01)
        kit.disc("hind_knee_%d" % s, kn, 0.11)
        kit.shell("hind_foot_%d" % s, "frame", Vector((s * 0.46, 0.5, 0.085)) + ho, (0.4, 0.6, 0.16), (0, 0, 0), 0.5, levels=1)   # p42: 1.4x (was (0.28, 0.46, 0.11) at z 0.06)
        claws(s, "hind", Vector((s * 0.46, 0.23, 0.1)) + ho, 0.12, 0.056, 0.85)



def claws(s, pre, front, spread, r0, size):
    """Three hooked claws from a foot's front edge (claw pass, 2026-10-13, as the wolf's). p42: each claw one thick
    curved cone (hook()) instead of two thin segments (0.07 m: about 2 sprite px, they read as red flecks), about 4 px
    thick at the base, `spread` apart sideways and fanned in pitch: the outer claw short and steep, the middle one
    longest, the inner one flatter, so the side view shows three separate tips as well as the front view."""
    for k, (dx, pitch, length, curl, yaw) in enumerate(((1, 62, 0.26, 18, 34), (0, 36, 0.33, 22, 0), (-1, 0, 0.3, 38, 48))):
        base = front + Vector((s * dx * spread, 0, 0.04 * (dx < 0)))   # the inner claw a little higher on the foot
        hook("%s_claw_%d_%d" % (pre, s, k), "claw", base, pitch, length * size, r0, curl, yaw=s * dx * yaw)   # splayed: the tips about 0.3 m apart


def hook(name, mat, base, pitch, length, r0, curl, yaw=0.0, rings=6, sides=8):
    """A tapered claw curving forward (-y) and down: it leaves `base` tipped `pitch` degrees below level and turns
    `curl` degrees further down by its tip, kept above the ground. One closed mesh, so it is one piece in the sprite."""
    pts, dirs = [Vector(base)], []
    step = length / rings
    for i in range(rings + 1):
        a = math.radians(pitch + curl * i / rings)
        dirs.append(Matrix.Rotation(math.radians(yaw), 3, "Z") @ Vector((0, -math.cos(a), -math.sin(a))))   # yaw > 0 splays toward +x
    for i in range(rings):
        pts.append(pts[-1] + dirs[i] * step)
    low = min(p.z for p in pts)
    if low < 0.02:   # lift the whole claw so its tip stays on the ground line
        pts = [p + Vector((0, 0, 0.02 - low)) for p in pts]
    bm = bmesh.new()
    loops = []
    for i, (p, d) in enumerate(zip(pts[:-1], dirs[:-1])):
        r = r0 * (1 - i / rings) ** 0.8
        u = Vector((0, 0, 1)).cross(d).normalized()
        if u.x < 0:
            u = -u
        v = d.cross(u).normalized()
        loops.append([bm.verts.new(p + u * (0.85 * r * math.cos(2 * math.pi * k / sides)) + v * (r * math.sin(2 * math.pi * k / sides)))
                      for k in range(sides)])
    tip = bm.verts.new(pts[-1])
    bm.faces.new(loops[0][::-1])
    for la, lb in zip(loops, loops[1:]):
        for k in range(sides):
            bm.faces.new((la[k], la[(k + 1) % sides], lb[(k + 1) % sides], lb[k]))
    for k in range(sides):
        bm.faces.new((loops[-1][k], loops[-1][(k + 1) % sides], tip))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(kit.MATS[mat])
    return ob


def weapons():
    for s in (-1, 1):   # Scale Shot: a launcher rack on each shoulder, three madder barrels angled forward and up
        base = kit.on_surface(bpy.data.objects["torso_shell"], (s * 0.33, -0.3, 1.4), (s * 0.5, 0, 1), 0.05 + (0.05 if SCALE_TILES else 0))   # reference pass 2: low on the back, behind the head; p42: up onto the tiles
        kit.shell("launcher_%d" % s, "frame", base, (0.26, 0.36, 0.14), (-10, 0, -s * 12), 0.5, levels=1)   # reference pass 2: lower profile
        for k in range(3):
            x = s * 0.33 + (k - 1) * 0.085
            kit.cyl("launcher_%d_barrel_%d" % (s, k), "trim", Vector((x, -0.5, base.z + 0.07)),
                    Vector((x, -0.78, base.z + 0.15)), 0.045, 8)


# ---- rig and clips: the shared quadruped rig (tools/blender/quad_rig.py, lifted from this file's v18; factory pass,
# 2026-10-12). Front legs ride upper_arm / forearm / hand, hind legs thigh / shin / foot, three tail bones. ----------
JOINT = {}   # recorded by legs()
TAIL_K = 9   # tail(): k_max


def tail_bone(name):
    if name.startswith(("tail_core_", "tailscale_")):
        # the segment number k: "tail_core_<k>", "tailscale_<k>_<j>" (2026-10-16, bind_audit.py: split("_")[2] read j
        # for the scales, so rows rode the wrong tail bone and the roll forked the tail)
        return min(2, 3 * int(re.match(r"tail(?:_core|scale)_(\d+)", name).group(1)) // TAIL_K)
    if name.startswith("tail_tip"):
        return 2
    return None


CFG = {
    "battle_set": "pangolin_m",   # battle clips: tools/blender/attacks.py (2026-10-13)
    "name": "pangolin_m",
    "head": ("head_core", "snout", "eye_", "ear_", "headscale", "nostril"),
    "tail_bone": tail_bone,
    "tail_points": [tail_point(t) for t in (0.0, 1 / 3, 2 / 3, 1.0)],
    "body_bone": ((0, 0.6, 0.9), (0, -0.6, 0.9)),
    "head_bone": ((0, -0.87, 0.8 + HC.z - 0.74), (0, -1.62, 0.75 + HC.z - 0.74)),   # p42: rides up with the head
    "joints": JOINT,
    "stride": 0.24,
    "crouch": 0.04,
    "front_path": (0.08, 0.0, 0.08, -15),     # back, down, lift, curl (v18)
    "hind_path": (-0.03, -0.013, 0.09, 0),    # the hind path 1.3 cm lower: measured contact offset (v18b)
}


# ---- the loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"). Roster moves get
# hardware; move None marks a spare hardpoint, DRAFT, Preston's to name. Shared builders: tools/blender/weapons.py.
def loadout():
    A, on, T = wpn.anchor, wpn.on, "torso_shell"
    return [
        {"slot": "roll", "move": "Ball Roll", "kind": "spikes", "note": "Delft-blue studs along the spine, what it rolls on",
         "args": {"points": [on(kit, T, (0.5, fy, 1.0), (0, 0, 1), 0.0) for fy in (0.3, 0.45, 0.6, 0.75)],
                  "length": 0.3, "r": 0.06, "direction": (0, 0.2, 1)}},
        {"slot": "chin", "move": None, "kind": "gatling", "prefix": "snout_", "note": "spare: a rotary gun under the snout",
         "args": {"base": A("snout", (0.5, 0.45, 0.0), (0, 0, -0.06)), "direction": (0, -1, 0), "length": 0.3, "ring": 0.05, "r": 0.02}},   # pass 3: shorter, it set the front of the sprite
        {"slot": "vls", "move": None, "kind": "missile_pod", "note": "spare: a 2x3 launcher on the rump, firing up and forward",
         "args": {"center": on(kit, T, (0.5, 0.78, 1.0), (0, 0, 1), 0.2), "size": (0.4, 0.26, 0.16), "rows": 2, "cols": 3, "rot": (-70, 0, 0)}},
    ]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    tail()
    head()
    for o in list(bpy.context.scene.objects):   # ref-5 (2026-10-13): his head is a quarter larger; the head group 1.25x about its centre
        if o.type == "MESH" and o.name.startswith(("head_core", "snout", "eye_", "ear_", "headscale", "nostril")):
            o.location = HC + (o.location - HC) * 1.25
            o.scale = tuple(v * 1.25 for v in o.scale)
            # p42: the head tipped HEAD_TILT degrees nose-up about its back, so the snout's underside runs level and
            # clears the far front foot's claws in the side view (they touched it there)
            piv = HC + Vector((0, 0.25, 0))
            bpy.context.view_layer.update()
            o.matrix_world = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-HEAD_TILT), 4, "X") @ Matrix.Translation(-piv) @ o.matrix_world
    legs()
    weapons()
    for k, (y, z, w, h) in enumerate(((-0.98, 1.16, 0.56, 0.42), (-1.1, 1.02, 0.48, 0.36), (-1.2, 0.9, 0.4, 0.3))):   # p20: overlapping scales over the neck, the armour reaching the head (his)
        kit.plate("neckscale_%d" % k, "main", Vector((0, y, z)), w, h, 0.06, (-58 + 6 * k, 0, 0), bend=0.45, taper=0.7, bevel=0.012)
    wpn.build_loadout(kit, "pangolin_m", loadout())
    greebles.run(kit, wpn, lambda n: quad.bone_for(n, CFG), skip_prefix=("scale_", "tailscale", "snoutscale", "neckscale", "headscale"))
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "pangolin_m"
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("PANGOLIN_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
