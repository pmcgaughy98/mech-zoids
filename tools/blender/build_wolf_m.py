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
#
# Model pass v85 (2026-10-16, blind judges on the detail sprites: "the wolf's red is scattered rather than a few defined
# plates, and its feet and head are weak"; tail spikes pale and tiny). The sprite is the render shrunk about 4.4x
# (x4.4 pixelize at SPRITE_ORTHO 5.6: one sprite pixel is about 3 cm), so anything under 2 to 3 sprite px turns to
# speckle. This pass trades many small red bits for a few big red plates, each a single piece: three red saddles
# (withers, mid back, croup) wrapping the top and the upper flank, a red square on each shoulder and hip pad round a
# dark panel (his hip plate's red square), the brow, the nose, the fangs, the claws and the tail tip. The small red bits
# are gone or grey: limb stripes, pad rims, rivets, spine fins, the four raked mane plates, cheek fins, hinge rings,
# missile caps, jet rings, rail tip, the red greeble layer plates and slats; the forearm blades are near-black.
# Paws: a dark heel block, three dark toes staggered so each red claw (one swept hook each) stands apart from the side.
# Head: a grey wedge skull over a dark lower jaw (the jaw line is the value step), a red brow and nose, a bigger cyan
# eye. Tail: four big pale hooked spikes, one piece each.
import bmesh, bpy, importlib.util, math, os, re
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
    "tusk": "e01818",        # the fangs (the kit's "tusk" slot); v85: the accent red, his fangs are the plates' red (was c42a2a)
    "light": "9a9aa4",       # 2026-10-15, Mechabeast V2 blind review 2: his limb plating is near-white, ours read lavender-grey (was 6e6e7c)
    "blade": "d4d4da",       # 2026-10-15, blind review 2: the tail spikes, big pale blades as his
    "claw": "e01818",        # v85: the accent red; ff3028 (blind review 2, his brightest red) landed on the ramp's salmon top shades
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


# ---- v85 helpers: single-piece shapes, so the detail pixelizer draws each as one clean shape (no seams inside) ------
def _bezier(p0, p1, p2, n):
    return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (i / (n - 1) for i in range(n))]


def sweep(name, mat, pts, radii, side=(1, 0, 0), sides=8):
    """A closed tube along the points, its cross-section an ellipse of radii (rx toward `side`, ry across): one piece
    for a claw, a fang or a hooked spike. A radius near zero makes a point."""
    pts = [Vector(p) for p in pts]
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        sx = Vector(side) - t * Vector(side).dot(t)
        sx = sx.normalized() if sx.length > 1e-6 else t.orthogonal().normalized()
        sy = t.cross(sx)
        rx, ry = radii[i]
        rings.append([bm.verts.new(p + sx * rx * math.cos(2 * math.pi * k / sides) + sy * ry * math.sin(2 * math.pi * k / sides))
                      for k in range(sides)])
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return kit._finish(ob, mat)


def band(name, mat, y0, y1, th_max, standoff=0.035, t=0.07, ny=8, nt=16, bevel=0.014):
    """A curved armour band laid on the torso core's real surface from y0 to y1, wrapping from -th_max to +th_max
    degrees about the body's long axis (0 is the top): one big red saddle plate instead of a top plate, two flank plates,
    rivets, seams and a spine fin."""
    core = bpy.data.objects["torso_core"]
    bm = bmesh.new()
    go, gi = [], []
    for i in range(ny + 1):
        y = y0 + (y1 - y0) * i / ny
        tz, bz = top_at(y), bottom_at(y)
        zc, b = (tz + bz) / 2, (tz - bz) / 2
        ro, ri = [], []
        for j in range(nt + 1):
            th = math.radians(-th_max + 2 * th_max * j / nt)
            aim = Vector((HALF_W * math.sin(th), y, zc + b * math.cos(th)))
            nrm = Vector((math.sin(th) / HALF_W, 0, math.cos(th) / b)).normalized()
            hit = kit.surface_hit(core, aim + nrm * 3.0, -nrm)
            p = hit[0] if hit else aim
            ro.append(bm.verts.new(p + nrm * (standoff + t)))
            ri.append(bm.verts.new(p + nrm * standoff))
        go.append(ro)
        gi.append(ri)
    for i in range(ny):
        for j in range(nt):
            bm.faces.new((go[i][j], go[i][j + 1], go[i + 1][j + 1], go[i + 1][j]))
            bm.faces.new((gi[i][j], gi[i + 1][j], gi[i + 1][j + 1], gi[i][j + 1]))
        for j in (0, nt):
            bm.faces.new((go[i][j], go[i + 1][j], gi[i + 1][j], gi[i][j]))
    for i in (0, ny):
        for j in range(nt):
            bm.faces.new((go[i][j], gi[i][j], gi[i][j + 1], go[i][j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bev = ob.modifiers.new("edge", "BEVEL")
    bev.width = bevel
    bev.segments = 1
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(30)
    return kit._finish(ob, mat)


def wolf_disc(name, center, radius, axis=(1, 0, 0), depth=0.12, ring=True):
    """The kit's joint disc for this machine only: the red ring wider (0.44r to 0.8r, about 2.5 sprite px on a knee;
    the kit's 0.42r to 0.72r read as a broken one-pixel circle) and none on small discs, where it was a red speck."""
    c, ax = Vector(center), Vector(axis).normalized()
    if c.x < 0 and ax.x > 0:
        ax = -ax
    kit.cyl(name, "frame", c - ax * depth / 2, c + ax * depth / 2, radius, 12)
    if ring:
        kit.cyl(name + "_ring", "accent", c + ax * depth / 2, c + ax * (depth / 2 + 0.03), radius * 0.8, 14)
    kit.cyl(name + "_hub", "frame_dark", c + ax * depth / 2, c + ax * (depth / 2 + 0.06), radius * 0.44, 10)


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
        for j, (th, w, h, mat) in enumerate(((0, 0.32, 0.3, "main"), (-48, 0.3, 0.28, "main"), (48, 0.3, 0.28, "main"),   # v85: grey; the red is the saddles (red_plates())
                                             (-96, 0.26, 0.24, "main"), (96, 0.26, 0.24, "main"))):
            if row in SADDLE_ROWS and abs(th) <= 48:   # v85: a red saddle covers these (one piece instead of three plates)
                continue
            rt = math.radians(th)
            aim = Vector((HALF_W * math.sin(rt), y, zc + b * math.cos(rt)))
            normal = (math.sin(rt) / HALF_W, 0, math.cos(rt) / b)
            c = kit.on_surface(core, aim, normal, 0.03)
            tilt = math.degrees(math.atan2(math.sin(rt) / HALF_W, math.cos(rt) / b))
            kit.plate("armor_%d_%d" % (row, j), mat, c, w, h, 0.05, (-90 - pitch, tilt, 0), bend=0.3, bevel=0.01,
                      recess=0.015, rim=0.04)
            # v85: the v11 rivets (3.5 cm, one sprite px of dark red) and seams (1.2 cm) are gone: speckle at sprite size
    # the mane: v85, a red saddle over the withers (red_plates()); the four raked red plates (v2) overlapped at four
    # angles and read as a crumpled red patch at sprite size. The raked red neck plates keep the mane's rise.
    # the keel chest, dark grey, and the Howl Burst emitter in the throat (v85: the three thin red ribs, 1 sprite px
    # each, are gone; the emitter keeps its red rim)
    c = kit.on_surface(core, (0, -1.05, 0.95 + UP), (0, -1, -0.2), 0.03)
    kit.plate("chest_keel", "frame", c, 0.4, 0.5, 0.08, (12, 0, 0), bend=0.5, bevel=0.012)
    # belly: dark grey plates under the tuck
    for k, y in enumerate((-0.5, 0.0, 0.5)):
        c = kit.on_surface(core, (0, y, bottom_at(y)), (0, 0, -1), 0.02)
        kit.plate("belly_%d" % k, "frame", c, 0.36, 0.34, 0.04, (90, 0, 0), bend=0.2, bevel=0.01)
    # Shadow Dash: v85 moves the red from the swept blade fins (thin red slivers behind the pads from the side) to a big
    # red plate on each shoulder and hip pad (red_plates()); the forearm blades stay, near-black.


SADDLE_ROWS = (0, 2, 4)   # v85: the back bands under the three red saddles (withers, mid back, croup)


def red_plates():
    """v85, after the greebles so none land on them: the few big red plates. Three saddles (withers, mid back, croup), each
    wrapping the top and the upper flank (about 12 to 20 by 8 to 16 sprite px from the side, one piece each); a red square
    plate on each shoulder and hip pad, behind the pad's dark greeble panel, so it reads as a red square about 3 px wide
    round a dark centre with a hub (his hip plate's red square)."""
    band("saddle_withers", "accent", -1.0, -0.62, 64)
    band("saddle_mid", "accent", -0.26, 0.12, 64)
    band("saddle_croup", "accent", 0.54, 0.92, 64)
    for s in (-1, 1):
        sd = "L" if s == 1 else "R"
        for pre, j, face, size in (("front_scale", JOINTS["sh." + sd], 0.32, 0.42), ("hind_scale", JOINTS["hp." + sd], 0.35, 0.46)):   # v85b: bigger, so the red border round the greeble panel is about 3 px
            c = j + Vector((s * (face + 0.012), 0, -0.04))   # on the pad's outer face (pad centre j + 0.24 or 0.27, 0.16 thick)
            kit.plate("%s_%d_redplate" % (pre, s), "accent", c, size, size, 0.04, (0, 0, s * 90), bend=0.0, bevel=0.01)
            kit.cyl("%s_%d_hub" % (pre, s), "frame_dark", c, c + Vector((s * 0.05, 0, 0)), 0.08, 10)


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
    # v85 (judges: the spikes read pale and tiny, 4 to 6 px, a fringe): four big hooked spikes, each ONE swept piece
    # (the two-piece blades split into two small shapes at sprite size), about 6 sprite px long at the base and 11 tall,
    # 8 px apart, smaller toward the tip, curving back toward it. Named "spine" so the greebles leave them bare.
    for n, (f, sc) in enumerate(((0.14, 1.0), (0.4, 0.95), (0.66, 0.88), (0.92, 0.78))):
        u = f * 3
        k = min(int(u), 2)
        a, b = TAIL[k], TAIL[k + 1]
        r0 = (0.17, 0.21, 0.2)[k]
        back = (b - a).normalized()
        base = a.lerp(b, u - k) + Vector((0, 0, r0 * 0.6))   # rooted in the tail's top plate
        up = Vector((0, 0, 1))
        pts = _bezier(base, base + up * 0.34 * sc - back * 0.03, base + up * 0.52 * sc + back * 0.26 * sc, 7)   # v85b: taller (v85a showed 4-6 px above the plates)
        rad = [(0.05, 0.15 * sc), (0.048, 0.135 * sc), (0.044, 0.114 * sc), (0.038, 0.088 * sc), (0.03, 0.06 * sc), (0.02, 0.034 * sc), (0.007, 0.007)]   # v85c: fatter, a pale core inside the dark outline
        sweep("tail_core_%d_spine%d" % (k, n), "blade", pts, rad, side=(1, 0, 0))


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
    # v85 (judges: the head is weak and muddy): a grey wedge skull ("face", a step lighter than the near-black armour)
    # over a dark lower jaw, so the jaw line is a value step the downscale keeps; a big red brow plate over the eye, a
    # red nose block, a bigger cyan eye in a dark socket, grey ears with red inner faces. Gone: the hinge discs (a red
    # ring speck on the cheek), the thin red cheek fins and the 7 cm brow crest.
    skull = kit.profile_solid("head_core", "face", hc, side, front, chamfer=0.012,
                              top_xy=kit.mirror_x([(0.27, 0.3), (0.27, 0.0), (0.22, -0.275), (0.15, -0.463), (0.1, -0.65)]))   # wolflike: the muzzle tapers to a narrow nose
    kit.plate("headplate_0", "face", hc + Vector((0, 0.0, 0.25)), 0.3, 0.22, 0.04, (-88, 0, 0), bend=0.4, bevel=0.008, recess=0.012, rim=0.03)
    kit.plate("headplate_1", "accent", hc + Vector((0, -0.19, 0.27)), 0.54, 0.42, 0.05, (-78, 0, 0), bend=0.7, bevel=0.01, taper=0.75)   # the red brow, his: bent down over the skull sides so the side view shows it as a band over the eye
    kit.plate("headplate_2", "face", hc + Vector((0, -0.5, 0.1)), 0.22, 0.24, 0.04, (-70, 0, 0), bend=0.4, bevel=0.008)
    # the lower jaw, 4 cm lower so the grey skull's lower edge shows above it, and the Fang Lunge: red fangs
    jaw_side = [(y, z - 0.04) for y, z in ((0.1, -0.14), (-0.275, -0.18), (-0.545, -0.14), (-0.575, -0.24), (-0.425, -0.3), (0.05, -0.28))]
    jaw_front = kit.mirror_x([(0.2, -0.18), (0.21, -0.28), (0.14, -0.34)])
    kit.profile_solid("head_jaw", "main", hc, jaw_side, jaw_front, chamfer=0.01,
                      top_xy=kit.mirror_x([(0.21, 0.12), (0.21, -0.1), (0.16, -0.35), (0.1, -0.59)]))
    kit.shell("head_mouth", "frame_dark", hc + Vector((0, -0.3, -0.19)), (0.34, 0.5, 0.06), (0, 0, 0), 0.5, levels=0)   # the dark mouth line between
    for s in (-1, 1):
        # one tapered swept piece per fang (two box segments read as two specks): the upper canine long, the lower short
        a = hc + Vector((s * 0.15, -0.5, -0.12))
        sweep("head_fang_%d" % s, "tusk", _bezier(a, a + Vector((0, -0.03, -0.14)), a + Vector((0, 0.01, -0.3)), 5),
              [(0.05, 0.05), (0.045, 0.045), (0.036, 0.036), (0.022, 0.022), (0.006, 0.006)])
        a = hc + Vector((s * 0.12, -0.34, -0.3))
        sweep("head_fang_low_%d" % s, "tusk", _bezier(a, a + Vector((0, -0.02, 0.08)), a + Vector((0, 0.0, 0.16)), 4),
              [(0.04, 0.04), (0.032, 0.032), (0.018, 0.018), (0.005, 0.005)])
        # eyes: a visor slot each side under the brow, bigger (about 8 by 3 sprite px after the head's 1.2 scale)
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.205, -0.32, 0.1)), (0.08, 0.26, 0.12), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.24, -0.32, 0.1)), (0.04, 0.2, 0.07), (0, 0, 0), 0.0, levels=0)
        # erect triangular ears, grey with a red inner face
        base = hc + Vector((s * 0.12, 0.08, 0.24))
        kit.plate("ear_%d" % s, "face", base + Vector((s * 0.02, 0.0, 0.2)), 0.22, 0.38, 0.05, (-10, 0, s * 38), bend=0.5, taper=0.2, bevel=0.008)   # v47 (column profile): turned out so the side view shows two broad ears, his
        kit.plate("ear_%d_inner" % s, "accent", base + Vector((s * 0.02, -0.025, 0.18)), 0.13, 0.26, 0.015, (-10, 0, s * 38), bend=0.5, taper=0.2, bevel=0.004)
    kit.shell("head_nose", "accent", hc + Vector((0, -0.62, -0.04)), (0.15, 0.1, 0.13), (0, 0, 0), 0.5, levels=1)   # v85: a red nose block, his (was a 7 cm dark red bead)
    # pass 2 detail (foundation): two antenna masts behind the ears (v85: thicker, the red tip about 2 px), a chin guard
    for s in (-1, 1):
        weapons.antenna(kit, "head_mast_%d" % s, hc + Vector((s * 0.16, 0.2, 0.2)), hc + Vector((s * 0.2, 0.46, 0.42)), r=0.024)
    kit.plate("head_chin", "main", hc + Vector((0, -0.365, -0.35)), 0.22, 0.3, 0.03, (90, 0, 0), bend=0.3, bevel=0.006)


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
            wolf_disc("%s_knee_%d" % (pre, s) if pre == "hind" else "front_elbow_%d" % s, b + Vector((s * 0.2, 0, 0)), 0.19, depth=0.12)   # synthesis pass (2026-10-13): bigger and proud of the armour, his reference and the Zoids rips show big joint hubs   # v5: the reference's big joint discs
            # v85: the shoulder and hip hub discs are now a red square plate with a dark hub (red_plates())
            wolf_disc("%s_shin_%d_wrist" % (pre, s), c + Vector((s * 0.03, 0, 0.04)), 0.09, depth=0.18, ring=False)   # v10: a wrist and ankle disc, his joints (v85: no red ring, a 4 px red speck)
            up, lo = bpy.data.objects["%s_upper_%d" % (pre, s)], bpy.data.objects["%s_lower_%d" % (pre, s)]
            kit.plate("%s_scale_%d" % (pre, s), "main", kit.on_surface(up, a.lerp(b, 0.45), (s, 0, 0), 0.025), 0.22, 0.34,
                      0.045, (-6, 0, s * 84), bend=0.35, bevel=0.008, recess=0.012, rim=0.03)   # black thigh and shoulder plates
            kit.plate("%s_shin_%d" % (pre, s), "main", kit.on_surface(lo, b.lerp(c, 0.4), (s, 0, 0), 0.02), 0.14, 0.26,
                      0.035, (-4, 0, s * 84), bend=0.35, bevel=0.008)
            # the paw: a big flexible foot, dark, four blood-red claws forward
            if pre == "hind":   # pass 2: the pastern, a thin strut from the high hock to a paw on the floor
                c = c + Vector((0, -0.1, -0.3))
                kit.limb_solid("hind_foot_meta_%d" % s, "frame", an, c, (s, 0, 0), [(0, 0.1, 0.08), (1, 0.08, 0.07)], [(0, 0.1), (1, 0.08)])
                wolf_disc("hind_foot_hock_%d" % s, an + Vector((s * 0.03, 0, 0)), 0.09, depth=0.18, ring=False)
            # pass 2 detail: a hydraulic ram along each upper limb, riding the upper bone
            weapons.piston(kit, "%s_upper_pst" % pre, a + (b - a) * 0.1 + Vector((s * 0.12, 0.06, 0)), a + (b - a) * 0.85 + Vector((s * 0.12, 0.06, 0)), 0.035, sfx="_%d" % s)
            PAWS.append((pre, s, c + Vector((0, -0.08, -0.14))))   # v4: the paw's sole on the floor; v85: built in paws()


PAWS = []


def paws():
    """v85 (judges: the feet are weak; the claws a red blob): each paw a dark heel block and three dark toes, staggered
    so that from the side the outer toe sits back and the inner one forward (about 5 to 6 sprite px apart on screen),
    each with one red claw, a single swept hook about 3 px thick curling down to the floor in front of its toe. Built
    after the greebles so no panels or bolts land on the blocks. History: v49 (Preston: "the claws look like one line
    instead of 3") fanned them; 2026-10-15 (blind review 2) made them twice as thick in three segments each, which at
    sprite size merged into one red blob with salmon highlights."""
    for pre, s, fc in PAWS:
        kit.shell("%s_foot_%d" % (pre, s), "main", fc + Vector((0, 0.07, 0.02)), (0.36, 0.32, 0.24), (0, 0, 0), 0.6, levels=1)   # the heel block
        for k, (dx, dy, ln) in enumerate(((0.14, 0.17, 1.0), (0.0, 0.0, 1.12), (-0.14, -0.17, 1.06))):   # outer, middle, inner (v85e: wider stagger, the far paws' claws merged; a little longer)
            x = fc.x + s * dx
            toe_c = Vector((x, fc.y - 0.13 + dy, fc.z - 0.01))
            kit.shell("%s_foot_%d_toe%d" % (pre, s, k), "frame_dark", toe_c, (0.12, 0.24, 0.16), (0, 0, 0), 0.6, levels=1)
            front = toe_c.y - 0.12
            # v85d: a steep talon hooking down in front of its toe (v85c's reached 0.2 m forward, longer than the toes'
            # stagger, so the three overlapped on screen and merged into one red band at x4.4)
            p0 = Vector((x, front + 0.06, toe_c.z + 0.04))
            p1 = Vector((x, front - 0.15 * ln, toe_c.z + 0.07))
            p2 = Vector((x, front - 0.12 * ln, toe_c.z - 0.12 * ln))
            sweep("%s_claw_%d_%d" % (pre, s, k), "claw", _bezier(p0, p1, p2, 7),
                  [(0.055, 0.065), (0.054, 0.063), (0.05, 0.058), (0.045, 0.05), (0.036, 0.038), (0.022, 0.022), (0.006, 0.006)])


# ---- pass 2 detail layer (2026-10-13, Preston: "add more pieces and parts, it kind of looks like a bare prototype";
# foundation for a Codex reference, not refined): spine ridge, flank vents, exhaust stacks, a neck collar, belly
# cables, tail joint rings.
def details():
    core = bpy.data.objects["torso_core"]
    # v85: the six red spine fins (V2 v68) are gone; the red back is three saddles now (red_plates())
    for sd in (-1, 1):
        c = kit.on_surface(core, (sd * HALF_W, 0.15, (top_at(0.15) + bottom_at(0.15)) / 2 + 0.05), (sd, 0, 0), 0.04)
        weapons.vent(kit, "flank_vent_%d" % sd, c, 0.2, 0.3, (0, sd * 90, 0), slats=3, slat_mat="frame")   # v85: grey slats (dark red was speckle)
        weapons.jet(kit, "exhaust_%d" % sd, "", (sd * 0.14, 0.92, top_at(0.92) - 0.06), (sd * 0.2, 1.1, top_at(0.92) + 0.16), 0.05, tip_mat="frame")
        weapons.cable(kit, "belly_cable_%d" % sd, [(sd * 0.12, -0.7, bottom_at(-0.7) + 0.02), (sd * 0.14, -0.2, bottom_at(-0.2) - 0.02),
                                                   (sd * 0.12, 0.4, bottom_at(0.4) - 0.01)], 0.025)
    kit.cyl("neck_collar", "frame_dark", Vector((0, -0.9, 1.24 + UP)), Vector((0, -1.0, 1.26 + UP)), 0.3, 12)   # v85: was dark red
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
        # v85: the red limb stripes (3 to 5 cm, a broken one-pixel red line on every leg) are gone
        # shoulder and hip pads (v85: the thin red rims under them are gone; a red square plate on each, red_plates())
        kit.shell("front_scale_pad_%d" % s, "main", sh + Vector((s * 0.24, -0.02, 0.0)), (0.16, 0.56, 0.5), (0, 0, 0), 0.6, levels=1)
        kit.shell("hind_scale_pad_%d" % s, "main", hp + Vector((s * 0.27, 0.0, -0.06)), (0.16, 0.62, 0.52), (0, 0, 0), 0.6, levels=1)
        # armored paws: v85, the heel block in paws()
        # neck plates down each side, following the neck's rise
        n0, n1 = Vector((0, -0.95, 1.22 + UP)), HC + Vector((0, 0.18, -0.02))
        pitch = math.degrees(math.atan2(-(n1.z - n0.z), -(n1.y - n0.y)))
        for k, t in enumerate((0.22, 0.5, 0.78)):
            kit.shell("neck_side_%d_%d" % (s, k), "main", n0.lerp(n1, t) + Vector((s * 0.24, 0, -0.02)), (0.08, 0.26, 0.34), (pitch, 0, 0), 0.6, levels=1)   # v85: the middle one no longer dark red
        # cheek guards along the jaw hinge (v85: the skull's grey, not a dark patch under the eye)
        kit.shell("head_cheek_%d" % s, "face", HC + Vector((s * 0.25, -0.1, -0.1)) * G, (0.07, 0.36, 0.2), (0, 0, 0), 0.6, levels=1)
    core = bpy.data.objects["torso_core"]
    for k, (ang, w, h, mat) in enumerate(((0, 0.5, 0.36, "main"), (-40, 0.36, 0.34, "accent"), (40, 0.36, 0.34, "accent"),
                                         (-75, 0.34, 0.4, "main"), (75, 0.34, 0.4, "main"))):   # v29: a ruff over the withers and shoulders
        if k < 3:   # v85: the top three would stand over the withers saddle; the two side plates stay
            continue
        rt = math.radians(ang)
        c = kit.on_surface(core, (HALF_W * math.sin(rt), -0.82, top_at(-0.82) - 0.1 + 0.1 * math.cos(rt)), (math.sin(rt), -0.3, math.cos(rt)), 0.1)
        kit.plate("ruff_%d" % k, mat, c, w, h, 0.06, (-62, 0, -ang * 0.9), bend=0.4, bevel=0.01, taper=0.55)
    # v85: no helm shell; it sat over the back half of the red brow and hid it from the side (headplate_0 is the crown)
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
        {"slot": "fang", "move": "Fang Lunge", "kind": "spikes", "prefix": "head_", "note": "pale teeth along the upper jaw (v85: were 2 px red ticks beside the fangs; his teeth are pale)",
         "args": {"points": [A("head_core", (fx, fy, 0.18)) for fx in (0.22, 0.78) for fy in (0.1, 0.2)],
                  "length": 0.1, "r": 0.04, "direction": (0, 0, -1), "mat": "light"}},
        {"slot": "howl", "move": "Howl Burst", "kind": "emitter", "prefix": "neck_", "note": "the throat emitter",
         "args": {"center": A("neck_core", (0.5, 0.2, 0.12)), "direction": (0, -1, -0.35), "r": 0.11}},
        {"slot": "rail", "move": None, "kind": "cannon", "note": "spare: a long rail gun on the left of the back (v85: was the right, where its barrel cut the red saddle in the side view)",
         "args": {"base": (0.2, 0.0, top_at(0.0) + 0.12), "direction": (0, -1, 0.04), "length": 1.05, "r": 0.05,
                  "housing": (0.2, 0.46, 0.17), "tip_mat": "frame"}},
    ]
    for sd in (-1, 1):
        side = "L" if sd == 1 else "R"
        el, wr = JOINTS["el." + side], JOINTS["wr." + side]
        L.append({"slot": "dash" + side, "move": "Shadow Dash", "kind": "blade", "prefix": "front_shin_", "suffix": "_%d" % sd,
                  "note": "a swept blade on the outside of each forearm (v85: near-black, a dark fin on the light forearm; red there read as a stray streak)",
                  "args": {"center": el.lerp(wr, 0.35) + Vector((sd * 0.13, 0.06, 0)), "w": 0.16, "h": 0.46, "rot": (-20, 0, sd * 84), "mat": "main"}})   # v85b: twice as wide, one red fin shape (an 8 cm sliver was a broken red line)
        L.append({"slot": "pod" + side, "move": None, "kind": "missile_pod", "note": "spare: a 2x2 launcher on each haunch",
                  "args": {"center": (sd * 0.28, 0.42, top_at(0.42) + 0.08), "size": (0.22, 0.3, 0.2), "rows": 2, "cols": 2, "rot": (-25, 0, 0),
                           "cap": "frame"}})   # v85: grey tube rims (eight 2 px red caps were speckle), 6 cm forward of the croup saddle
    return L


def tidy_greebles():
    """v85, this machine only (greebles.py is shared): the detail pass puts a red layer plate on one host in four and
    dark red slats in its vents; at sprite size those were red specks across the grey. A greeble on a red host stays
    red (it merges into the plate); a red or dark red greeble on any other host takes the host's colour (slats: grey)."""
    inv = {m.name: k for k, m in kit.MATS.items()}
    changed = 0
    for o in list(bpy.context.scene.objects):
        if o.type != "MESH" or not re.search(r"_9\d\d$", o.name) or not o.data.materials:
            continue
        host = bpy.data.objects.get(o.name[:-4])
        hk = inv.get(host.data.materials[0].name) if host and host.data.materials else None
        pk = inv.get(o.data.materials[0].name)
        new = None
        if hk == "accent" and pk != "accent":
            new = "accent"
        elif hk != "accent" and pk == "accent":
            new = hk or "main"
        elif pk == "trim":
            new = "frame"
        if new:
            for i in range(len(o.data.materials)):
                o.data.materials[i] = kit.MATS[new]
            changed += 1
    print("TIDY greebles recoloured %d" % changed)


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
    greebles.run(kit, weapons, lambda n: quad.bone_for(n, CFG), skip_prefix=("torso_core", "neckplate", "head_", "headplate", "ear_"))   # v71: the core is under armour already; its layer plate hid the red back. v85: the head and the red neck plates bare too (panels and bolts on them read as mud and crumpled red at sprite size)
    tidy_greebles()
    red_plates()
    paws()
    quad.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "wolf_m"
    quad.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("WOLF_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
