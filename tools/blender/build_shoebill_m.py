# The shoebill machine, the creature factory's fourth product and its first bird (Claude, 2026-10-12).
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_shoebill_m.py
# Parts from the gorilla's kit (build_ape_l_v2.py), rig from bird_rig.py (built on quad_rig.py's leg IK). Design from
# the real bird (Wikipedia "Shoebill", Dallas World Aquarium, 2026-10-12): 1.1-1.4 m tall and statue-like; a head
# large for the body on a neck shorter and thicker than a heron's; a huge bulbous bill, the upper mandible strongly
# keeled and ending in a sharp hooked nail, with cutting edges; long dark legs and exceptionally large feet (middle
# toe about 17 cm on a 22-25 cm tarsus); broad wings; blue-grey plumage with darker slate flight feathers; elongated
# breast feathers; a rounded tail. Built about 1.8 times life size.
# Colours: Preston's proposal in scripts/data/machines.gd, "Blue Hour Cool" (blue, deep blue, gold, teal eyes).
# Weapons from the same file: Bill Clamp (the bill), Stillwater Lance (a beam from the bill's hook: a lens under the
# nail), Wing Buffet (armoured gold leading edges on the wings).
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
bird = _load("bird_rig", "bird_rig.py")
wpn = _load("weapons", "weapons.py")
import importlib.util as _gu
_gs = _gu.spec_from_file_location("greebles", os.path.join(os.path.dirname(os.path.abspath(__file__)), "greebles.py"))
greebles = _gu.module_from_spec(_gs)
_gs.loader.exec_module(greebles)   # the detail pass (2026-10-14)
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "shoebill_m.blend")
LIFT = 0.5   # blind review 4 (2026-10-15): 0.63 for 10% longer legs cost 0.05 outline (p81), kept 0.5. part pass legs (2026-10-13): his bare legs are about 40% of the height with the body high on them; ours showed a quarter. Was 0.3 (p15; p5: the body rides higher still on long thin legs (the reference's legs are near half its height)
PITCH = 0   # p18: the body is built level and small; his is wider than tall (p15: -42; reference pass 4: a little less upright, for width (round 3 was 35): the upper body stands up about the hips (the reference stands upright, neck straight
              # up, wings hanging as a cloak); the head keeps a level bill, tipped 10 degrees down
HARD = os.environ.get("SHOEBILL_HARD", "1") == "1"   # p86 hard armour; SHOEBILL_HARD=0 builds p85's body and wings
P87 = HARD and os.environ.get("SHOEBILL_P87", "1") == "1"   # p87 big smooth plates; SHOEBILL_P87=0 builds p86 again

PAL = {
    "main": "7fa3d4",        # light blue plates (reference 82a6d7, the dominant colour)
    "pale": "8aaedf",        # blind review 4 (2026-10-15): a step darker, ours ran washed out next to his; was 92b6e6. blind review 2 (2026-10-15): the big torso plates a step lighter, his pale sky-blue
    "trim": "223562",        # deep blue: the flight feathers, tail, bill nail (reference 223562)
    "accent": "d9b56a",      # muted gold: the bill, the wings' leading edges (reference cfad6b)
    "frame": "6a7080",       # p23: steel-grey legs and joints as his (4c5058 read as black columns)
    "frame_dark": "2f333b",  # the body under the plates, the toes
    "face": "4a6fa5",
    "plate": "8cb4ee",       # p86: the hard body blocks, as bright as the toon light allows without its centre band
                             # clipping them to grey (a4c6f4 clipped 9% of their pixels out of the blue family)
    "plate_lo": "7ea6e2",    # p86: the under-side row a step darker
    "mid": "6d93cc",         # p86: the lower coverts and the feathers' lit edges, between the plates and the navy
    "seam": "070b18",        # p86: the frame under the plates, a navy near-black as his seams (090d1d, 070a18); in the
                             # blue family it also sets the dark end of the blue ramp, so the plates land on 82a6d7
    "light": "8a8d92",
    "eye_src": "5fe1d0",     # teal eyes and the Lance lens (player faction)
}
if HARD:   # p86: the deep blue a step darker, so it stays the ramp's darkest blue over the near-black seams
    PAL["trim"] = "1b2d58"
if P87:
    # p87 plate colours by which way the plate faces the battle views. The toon matcap lights a face by how squarely it
    # faces the camera and the pixelizer maps value to the blue ramp on a fixed scale (its 98th percentile is the
    # clipped highlight, V 1), so the albedo sets which shade a plate's median lands on. Measured on the E/SE/S/NE
    # sprites: 86b8f8 everywhere put the side plates and chest on a9c4e6/cfe0f3 (82a6d7 at 7.5% of the E sprite);
    # side plates 7aa6e2 and the chest 6f9ad2 put their medians on 82a6d7 (12.3%), the round 2 judges' dominant colour
    PAL["plate"] = "7aa6e2"       # side plates and covert; saturation 0.46 keeps the clipped light band out of grey
    PAL["plate_lo"] = "7cacec"    # belly and thigh cover, turned down and away from the camera
    PAL["plate_top"] = "86b8f8"   # the back plate, seen edge-on from the 18-degree camera, keeps the brightest blue
    PAL["chest"] = "6f9ad2"       # the chest faces the camera squarely in E, SE and S
    PAL["feather_hi"] = "5a80bf"   # p87: the blades' light top strip (6890cc landed on a9c4e6, p87d: pale again)
    PAL["feather"] = "14224a"   # p87: the primaries a navy below trim, so the blade bodies land on the ramp's two darkest
    # blues (round 2 judges: "the blade tips are pale light blue; in the reference the blades are deep navy")
for _kv in filter(None, os.environ.get("SHOEBILL_PAL", "").split(",")):   # experiments: SHOEBILL_PAL="plate=7ea8e4,mid=..."
    PAL[_kv.split("=")[0]] = _kv.split("=")[1]


def make_materials():
    for key, h in PAL.items():
        m = bpy.data.materials.new("mech_" + key if key != "eye_src" else "eye_src")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = kit.srgb(h)
        b.inputs["Roughness"].default_value = 0.5
        m.diffuse_color = kit.srgb(h)
        kit.MATS[key] = m


# ---- hard armour (model pass p86, 2026-10-16) ------------------------------------------------------------------
# Blind judges on the detail sprites: "the shoebill's body reads as puffy blocks", "the wing reads as one slab". The
# sprite is the render shrunk 4.4x (one sprite pixel is about 3 cm here), so a plate needs flat faces (one tone each,
# no bend: a bent plate shades as a gradient, a pillow), a crisp chamfer (the lit lip), and a dark gap to its neighbour
# wide enough to win its sprite pixels (GAP, 11 cm: one to two pixels of near-black navy seam, as his 090d1d seams).
def hard_block(name, mat, center, xax, yax, zax, size, chamfer=0.025):
    """A hard armour block: a box size (sx, sy, sz) along the axes xax, yax, zax, flat faces and one 45-degree chamfer
    on every edge (sharpen() keeps the chamfers split-shaded, so each face stays one flat tone)."""
    import bmesh
    from mathutils import Matrix
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= size[0]
        v.co.y *= size[1]
        v.co.z *= size[2]
    if chamfer > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(chamfer, min(size) * 0.4), offset_type="OFFSET", segments=1,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = Matrix.Translation(Vector(center)) @ Matrix((Vector(xax).normalized(), Vector(yax).normalized(),
                                                                    Vector(zax).normalized())).transposed().to_4x4()
    return kit._finish(ob, mat)


# ---- the body: an egg, front high, plated in blue; long breast plates; a rounded deep-blue tail ---------------
def body():
    side = [(-0.5, 1.45), (-0.42, 1.7), (-0.1, 1.8), (0.34, 1.72), (0.7, 1.45), (0.84, 1.2), (0.66, 0.98),
            (0.22, 0.88), (-0.24, 0.94), (-0.48, 1.16)]   # round 3: a fatter egg
    front = kit.mirror_x([(0.16, 1.8), (0.36, 1.66), (0.46, 1.4), (0.42, 1.12), (0.22, 0.92)])
    side = [(y * 1.1 - 0.12, (z - 1.34) * 0.98 + 1.25 + LIFT) for y, z in side]   # pass 2 neck/body: the egg 12 cm forward, his breast pushes out under the neck (red at the front in both overlays); p22: p19's depth
    front = [(x * 1.0, (z - 1.34) * 0.98 + 1.25 + LIFT) for x, z in front]
    if P87:
        # p87: the same outlines lofted as a smooth rounded egg, then cut into seven big plates a side
        core = smooth_egg("torso_core", "seam", side, front)
        big_body(core)
        return
    if HARD:
        # p86: the egg is the dark frame under the armour; only the seams between the blocks show it
        core = kit.profile_solid("torso_core", "seam", (0, 0, 0), side, front, chamfer=0.03)
        hard_body(core)
        return
    core = kit.profile_solid("torso_core", "main", (0, 0, 0), side, front, chamfer=0.03)   # p16: the core light blue, so bare egg reads as pale body not a dark slab
    # Mechabeast V2 blind review 2 (2026-10-15): four large pale plates a side with clean seams, not 28 small plates;
    # his torso reads as big sky-blue plates, ours read as navy fragments (a navy rear band stood up as shards, p76)
    for row, th in enumerate((0, 62, 112)):   # top, upper flank, lower flank
        for col, y in enumerate((-0.34, 0.06)):
            for s in ((1,) if th == 0 else (-1, 1)):
                rt = math.radians(th)
                out = Vector((s * math.sin(rt), 0, math.cos(rt)))
                aim = Vector((s * 0.5 * math.sin(rt), y, LIFT + 1.25 + 0.45 * math.cos(rt)))
                kit.plate_on(core, "plate_%d_%d_%d" % (row, col, s), "pale", aim, out,
                             0.42, 0.38 if th else 0.3, 0.05, standoff=0.02, bend=0.3, bevel=0.01)
    # blind review 2 (2026-10-15): one big pale breast plate pushed forward under the neck; his chest and belly stand
    # ahead of ours (overlay red at the front, rows 0.45-0.55)
    kit.shell("plate_chest", "pale", Vector((0, -0.62, 1.1 + LIFT)), (0.6, 0.35, 0.45), (-20, 0, 0), 0.45, levels=2)
    # blind review 4 (2026-10-15): navy panel lines on the pale chest so the plating reads (his chest has seams and a
    # vent of three slots); named plate_ so the detail pass leaves them
    chest = bpy.data.objects["plate_chest"]
    pts = lambda x, z: kit.on_surface(chest, Vector((x, -0.62, z + LIFT)), (0, -1, 0.3), 0.0)
    for k, z in enumerate((1.26, 0.96)):   # two seams across
        kit.segment("plate_chestline_%d" % k, "trim", pts(-0.3, z), pts(0.3, z), 0.04, 0.04, 0.5)
    for k, x in enumerate((-0.2, -0.12, -0.04)):   # the vent
        kit.segment("plate_chestvent_%d" % k, "trim", pts(x, 1.18), pts(x, 1.04), 0.04, 0.04, 0.5)
    # elongated breast feathers: long blades hanging down the chest
    for k, x in enumerate((-0.16, -0.05, 0.05, 0.16)):
        c = kit.on_surface(core, Vector((x, -0.4, LIFT + 1.3)), (0, -1, -0.2), 0.03)
        kit.plate("breast_%d" % k, "main", c, 0.13, 0.46, 0.04, (8, 0, x * 60), bend=0.3, taper=0.5, bevel=0.008)
    tail()


def tail():
    # the rounded tail: a fan of deep-blue plates sloping down behind
    for k, x in enumerate((-0.18, 0.0, 0.18)):
        kit.plate("tail_%d" % k, "trim", Vector((x, 0.82, LIFT + 1.14 - abs(x) * 0.2)), 0.2, 0.36, 0.04, (-120, 0, x * 80),
                  bend=0.3, taper=0.7, bevel=0.008)


ZC = 1.25 + LIFT   # the egg's middle height


REAR_Y = 0.5   # behind this the rear end is two cap plates, upper and lower (cut round the axis there, the narrowing
# rear end was mostly seam and the seams met in a star: the N view showed a black back)
GAP = 0.11   # m between neighbouring plates: the seam; at 0.05 and 0.08 (1.6, 2.6 sprite px) the block vote lost most of them
BODY_COLS = ((-0.56, -0.2), (-0.2, 0.15), (0.15, REAR_Y))   # along the body (y), front to back
BODY_ROWS = (((-24, 24), "plate"), ((24, 66), "plate"), ((66, 112), "plate"), ((112, 172), "plate_lo"))
# degrees round the body from the top: the back, the shoulder, the side, the under side
CHEST_Y = -0.56   # the egg's front ahead of this is the chest, cut in two across at CHEST_Z
CHEST_Z = 1.34 + LIFT


def hull_plate(core, name, mat, cuts, t=0.06, flat=0.0):
    """An armour plate cut from the hull itself: the core's surface kept inside the half-spaces `cuts` (each a point and
    a normal; the side the normal points to is kept), thickened outward by t and chamfered. Neighbouring plates follow
    the egg exactly, so nothing floats; the GAP left between their cuts is the seam where the dark core shows."""
    import bmesh
    dg = bpy.context.evaluated_depsgraph_get()
    eo = core.evaluated_get(dg)
    me = eo.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    eo.to_mesh_clear()
    bm.transform(core.matrix_world)
    for co, no in cuts:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=Vector(co),
                               plane_no=Vector(no), clear_inner=True)
    if not bm.faces:
        bm.free()
        print("BLOCK_MISS", name)
        return None
    if flat > 0:   # p87: pressed toward a plane over the patch (outward only, so it never sinks into the egg): a big
        # plate's face turns calm, one tone under the toon light, and its rim stands off the egg as a thick edge
        n = sum((f.normal * f.calc_area() for f in bm.faces), Vector()).normalized()
        top = max(v.co.dot(n) for v in bm.verts)
        for v in bm.verts:
            v.co += n * (flat * (top - v.co.dot(n)))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    sol = ob.modifiers.new("thickness", "SOLIDIFY")
    sol.thickness = t
    sol.offset = 1.0
    sol.use_even_offset = True
    bev = ob.modifiers.new("edge", "BEVEL")
    bev.width = 0.02
    bev.segments = 1
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(60)   # the plate's rim (90 degrees) chamfered; the egg's facet creases (about 35) kept
    return kit._finish(ob, mat)


def _wedge(th0, th1, s):
    """Half-spaces keeping the angles th0..th1 round the body axis (degrees from the top, toward side s), GAP/2 in."""
    out = []
    for th, keep in ((th0, 1), (th1, -1)):
        r = math.radians(th)
        n = Vector((s * math.cos(r), 0, -math.sin(r))) * keep   # toward growing angle for the lower bound
        out.append((Vector((0, 0, ZC)) + n * GAP / 2, n))
    return out


def _span(y0, y1):
    return [(Vector((0, y0 + GAP / 2, 0)), Vector((0, 1, 0))), (Vector((0, y1 - GAP / 2, 0)), Vector((0, -1, 0)))]


def hard_body(core):
    """p86: the egg's own surface cut into big light-blue plates, four along it and four round each side, with GAP
    seams where the dark core shows; the chest two plates with a three-slot vent; his reference's torso is big
    sky-blue plates on a near-black frame."""
    for r, (ths, mat) in enumerate(BODY_ROWS):
        for s in ((1,) if ths[0] < 0 else (-1, 1)):
            for c, (y0, y1) in enumerate(BODY_COLS):
                hull_plate(core, "plate_hb_%d_%d_%d" % (r, c, s), mat, _span(y0, y1) + _wedge(ths[0], ths[1], s))
    front = (Vector((0, CHEST_Y - GAP / 2, 0)), Vector((0, -1, 0)))
    hull_plate(core, "plate_chest_up", "plate", [front, (Vector((0, 0, CHEST_Z + GAP / 2)), Vector((0, 0, 1)))])
    hull_plate(core, "plate_chest_lo", "plate", [front, (Vector((0, 0, CHEST_Z - GAP / 2)), Vector((0, 0, -1)))])
    rear = (Vector((0, REAR_Y + GAP / 2, 0)), Vector((0, 1, 0)))
    hull_plate(core, "plate_hb_rear_up", "plate", [rear, (Vector((0, 0, ZC + 0.12 + GAP / 2)), Vector((0, 0.5, 1)))])
    hull_plate(core, "plate_hb_rear_lo", "plate_lo", [rear, (Vector((0, 0, ZC + 0.12 - GAP / 2)), Vector((0, -0.5, -1)))])
    for k, x in enumerate((-0.2, -0.11, -0.02)):   # his chest vent: three dark slots on the lower chest plate
        hit = kit.surface_hit(core, Vector((x, -3.0, CHEST_Z - 0.15)), Vector((0, 1, 0)))
        if hit:
            p = hit[0] + hit[1] * 0.06
            kit.segment("plate_chestvent_%d" % k, "frame_dark", p + Vector((0, 0, 0.08)), p - Vector((0, 0, 0.08)), 0.05, 0.04, 0.5)
    tail()


# ---- p87 (model pass round 2, 2026-10-17): big smooth plates -------------------------------------------------
# Round 2 judges on p86: "the body reads as crumpled foil / low-poly crystal: many small facets 3 to 6 px across
# alternating light, mid and dark". Cause: profile_solid's egg is the overlap of two straight prisms, so its skin is
# flat facets meeting at 20-35 degrees, and every hull plate cut from it carried four to six of them; under the toon
# light each facet took its own band. Fix: loft the same two outlines as rounded cross-sections (a superellipse at
# each height), cut fewer, bigger plates from it, and press each plate half flat (P87_FLAT), so a plate is one gentle
# curve with a chamfered rim: under the toon light it takes one main tone, and the pixelizer adds its lit top row and
# its seam.
def _extent(poly, z):
    """Where the horizontal line at height z crosses the closed outline poly [(u, z)]: (min u, max u) or None."""
    us = []
    n = len(poly)
    for i in range(n):
        (u0, z0), (u1, z1) = poly[i], poly[(i + 1) % n]
        if (z0 - z) * (z1 - z) <= 0 and z0 != z1:
            us.append(u0 + (u1 - u0) * (z - z0) / (z1 - z0))
    return (min(us), max(us)) if len(us) >= 2 else None


EGG_N = 2.6   # superellipse exponent: 2 an ellipse (too soft, p85's pillows), 4 near a rounded box (the crate)


def smooth_egg(name, mat, side, front, rings=26, segs=44):
    """The body: the side outline (y, z) and front outline (x, z) lofted as superellipse cross-sections, so it keeps
    p86's outline from the side and the front but its skin is one smooth surface."""
    import bmesh
    z0 = max(min(z for _, z in side), min(z for _, z in front)) + 1e-4
    z1 = min(max(z for _, z in side), max(z for _, z in front)) - 1e-4
    bm = bmesh.new()
    loops = []
    for i in range(1, rings):
        z = z0 + (z1 - z0) * (1 - math.cos(math.pi * i / rings)) / 2
        ys, xs = _extent(side, z), _extent(front, z)
        if not ys or not xs:
            continue
        a = max(abs(xs[0]), abs(xs[1]))
        yc, b = (ys[0] + ys[1]) / 2, (ys[1] - ys[0]) / 2
        a = min(a, b * 1.6 + 0.03)   # the top and bottom close as a dome, not a ridge across
        ring = []
        for k in range(segs):
            t = 2 * math.pi * k / segs
            c, s_ = math.cos(t), math.sin(t)
            x = a * math.copysign(abs(c) ** (2 / EGG_N), c)
            y = yc + b * math.copysign(abs(s_) ** (2 / EGG_N), s_)
            ring.append(bm.verts.new((x, y, z)))
        loops.append(ring)
    for r0, r1 in zip(loops, loops[1:]):
        for k in range(segs):
            bm.faces.new((r0[k], r0[(k + 1) % segs], r1[(k + 1) % segs], r1[k]))
    for ring, zc in ((loops[0], z0), (loops[-1], z1)):   # pole caps: a fan to the ring's centre, nudged to the end
        c = sum((v.co for v in ring), Vector()) / len(ring)
        c.z = zc
        p = bm.verts.new(c)
        for k in range(segs):
            bm.faces.new((ring[k], ring[(k + 1) % segs], p))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return kit._finish(ob, mat)


P87_GAP = float(os.environ.get("SHOEBILL_GAP", "0.035"))   # seam (m); one sprite px is about 3 cm. The pixelizer draws
# a one-px seam two shades down on every plate's lower and right edge where it meets another part, so the gap only
# has to keep the plates separate pieces; at 0.08 (p87a) the navy egg won its own 1-2 px beside that line
P87_FLAT = float(os.environ.get("SHOEBILL_FLAT", "0.5"))   # how far each plate is pressed flat (0 follows the egg)
P87_T = 0.055      # plate thickness
P87_CHEST_Y = -0.46   # the chest plate is the egg ahead of this (p86's -0.56 left a small cap; his chest is big)
SPLIT_Y = -0.05    # the side rows split front / back here (shoulder ahead of the wing, flank under it)
UNDER_Y = -0.12    # the under row: belly ahead, thigh cover over the hips behind
BACK_TH = 32       # degrees from the top: the back plate across both sides (42 in p87d: a flat top seen edge-on
# from the 18-degree camera, the toon light's dark band over the whole upper back)
SIDE_TH = 102      # the side row (shoulder, flank) down to here; under it the belly and thigh cover


def big_body(core):
    """p87: seven big plates a side as his reference's torso (chest, back, shoulder, flank, belly, thigh cover, rear
    cap), each one gentle curve with a chamfered rim, on the near-black navy egg that shows as one seam between them."""
    global GAP
    keep = GAP
    GAP = P87_GAP   # _wedge / _span read it
    try:
        rows = (("shoulder", "flank", (BACK_TH, SIDE_TH), "plate"), ("belly", "thigh", (SIDE_TH, 180), "plate_lo"))
        for s in (-1, 1):
            for fore, aft, (t0, t1), mat in rows:
                split = SPLIT_Y if fore == "shoulder" else UNDER_Y
                hull_plate(core, "plate_%s_%d" % (fore, s), mat, _span(P87_CHEST_Y, split) + _wedge(t0, t1, s), t=P87_T, flat=P87_FLAT)
                hull_plate(core, "plate_%s_%d" % (aft, s), mat, _span(split, REAR_Y) + _wedge(t0, t1, s), t=P87_T, flat=P87_FLAT)
        hull_plate(core, "plate_back", "plate_top", _span(P87_CHEST_Y, REAR_Y) + _wedge(-BACK_TH, BACK_TH, 1), t=P87_T, flat=P87_FLAT)
        hull_plate(core, "plate_chest", "chest", [(Vector((0, P87_CHEST_Y - GAP / 2, 0)), Vector((0, -1, 0)))], t=P87_T, flat=P87_FLAT)
        rear = (Vector((0, REAR_Y + GAP / 2, 0)), Vector((0, 1, 0)))   # the rear cap upper and lower: the N/NE views
        hull_plate(core, "plate_rear_up", "plate", [rear, (Vector((0, 0, ZC + 0.08 + GAP / 2)), Vector((0, 0.5, 1)))], t=P87_T, flat=P87_FLAT)
        hull_plate(core, "plate_rear_lo", "plate_lo", [rear, (Vector((0, 0, ZC + 0.08 - GAP / 2)), Vector((0, -0.5, -1)))], t=P87_T, flat=P87_FLAT)
    finally:
        GAP = keep
    for k, x in enumerate((-0.13, -0.02) if P95 else (-0.2, -0.11, -0.02)):   # his chest vent: dark slots on the chest plate (p95: two, Codex's)
        # p95: hit the chest plate itself (the core lies under it, so p87 to p94's slots were buried behind the plate)
        hit = kit.surface_hit(bpy.data.objects["plate_chest"] if P95 else core, Vector((x, -3.0, CHEST_Z - 0.15)), Vector((0, 1, 0)))
        if hit:
            p = hit[0] + hit[1] * (0.02 if P95 else 0.05)
            hl, r0, r1 = (0.13, 0.065, 0.055) if P95 else (0.08, 0.05, 0.04)
            kit.segment("plate_chestvent_%d" % k, "frame_dark", p + Vector((0, 0, hl)), p - Vector((0, 0, hl)), r0, r1, 0.5)
    tail()


# ---- the head: big on a short thick neck, the huge keeled gold bill ending in a hooked nail -------------------
HC = Vector((0, -0.5, 2.25 + LIFT))   # p18: the head on a longer neck above the small body


def head():
    hc = HC
    kit.segment("neck_core", "main", Vector((0, -0.2, 1.55 + LIFT)), hc + Vector((0, 0.1, -0.1)), 0.4, 0.34, 0.5)   # p23: thicker and blue-plated as his, not a thin grey rod
    for k in range(3):   # p8: dark rings down the neck column
        t = 0.2 + 0.28 * k
        a = Vector((0, -0.28, 1.58 + LIFT)).lerp(hc + Vector((0, 0.12, -0.12)), t)
        kit.segment("neck_ring_%d" % k, "frame_dark", a, a + Vector((0, -0.01, 0.04)), 0.34, 0.34, 0.5)
    for k in range(4):   # p8: the chest grille, four grey slats
        kit.segment("neck_grille_%d" % k, "frame", Vector(((k - 1.5) * 0.09, -0.52, 1.72 + LIFT)), Vector(((k - 1.5) * 0.09, -0.5, 1.42 + LIFT)), 0.04, 0.03, 0.5)
    for k in range(3):   # feathered neck plates down its front and back
        c = kit.on_surface(bpy.data.objects["neck_core"], Vector((0, -0.34 - 0.03 * k, LIFT + 1.66 + 0.13 * k)), (0, -1, 0.2), 0.02)
        kit.plate("neckplate_%d" % k, "main", c, 0.3, 0.18, 0.04, (-20, 0, 0), bend=0.4, bevel=0.008)
    side = [(0.2, 0.0), (0.16, 0.17), (0.0, 0.23), (-0.18, 0.19), (-0.25, 0.02), (-0.21, -0.14), (0.0, -0.18), (0.16, -0.12)]
    front = kit.mirror_x([(0.1, 0.23), (0.17, 0.1), (0.19, -0.04), (0.13, -0.18)])   # reference pass: slimmer skull
    skull = kit.profile_solid("head_core", "main", hc, side, front, chamfer=0.015)
    # a small crest tuft at the back of the head
    for k in range(5):   # p25: his spiky crest, five raked deep-blue blades fanned over the back of the head
        kit.plate("crest_%d" % k, "trim", hc + Vector(((k - 2) * 0.06, 0.16 + 0.03 * abs(k - 2), 0.22 - 0.02 * abs(k - 2))), 0.1, 0.46 if P95 else 0.26, 0.03,
                  (-130, 0, (k - 2) * 16), bend=0.2, taper=0.3, bevel=0.006)
    # the upper mandible: bulbous and keeled, the shoe
    up_side = [(-0.16, 0.16), (-0.36, 0.22), (-0.6, 0.18), (-0.78, 0.09), (-0.87, 0.0), (-0.8, -0.06), (-0.5, -0.06),
               (-0.16, -0.05)]   # ref-5 head (2026-10-13): deep at the base, pointed at the tip (p45's thin wedge read as a blade from the side, E 0.587 to 0.543)   # v2: deeper and more bulbous, the shoe
    up_front = kit.mirror_x([(0.07, 0.21), (0.16, 0.11), (0.18, 0.0), (0.17, -0.05)])   # reference pass: slimmer, as the skull
    kit.profile_solid("bill_upper", "accent", hc, [(y * 1.3, z * 1.28) for y, z in up_side], [(x * 1.12, z * 1.28) for x, z in up_front], chamfer=0.012,
                      top_xy=kit.mirror_x([(0.21, 0.0), (0.21, -0.3), (0.15, -0.75), (0.08, -1.16)]))   # ref-5: narrowing to the tip   # p24: long again (p23 at 1.1 long read as a clam), deeper than p22   # round 7: the shoe longer
    kit.segment("bill_keel", "accent", hc + Vector((0, -0.2, 0.17)), hc + Vector((0, -0.86, 0.11)), 0.06, 0.06, 0.5)
    # Mechabeast V2 blind review 4 (2026-10-15): his bill ends in a sharp downward hook, gold over a navy tip, well
    # below the bill line; ours ended in a small blue drip. The nail gold, then a navy tip curling down and back
    kit.segment("bill_nail", "accent", hc + Vector((0, -0.98, 0.06)), hc + Vector((0, -1.17, -0.1)), 0.12, 0.12, 0.5)   # head part 2: the hooked nail, bigger
    kit.segment("bill_nail_mid", "accent", hc + Vector((0, -1.17, -0.1)), hc + Vector((0, -1.15, -0.26)), 0.1, 0.1, 0.5)
    kit.segment("bill_nail_tip", "trim", hc + Vector((0, -1.15, -0.26)), hc + Vector((0, -1.07, -0.41)), 0.08, 0.06, 0.5)   # curling down
    lo_side = [(-0.16, -0.05), (-0.74, -0.06), (-0.62, -0.13), (-0.4, -0.17), (-0.16, -0.15)]   # ref-5: the lower edge rises to the tip
    lo_front = kit.mirror_x([(0.16, -0.05), (0.16, -0.12), (0.11, -0.18)])
    kit.profile_solid("bill_lower", "accent", hc, [(y * 1.3, z * 1.28) for y, z in lo_side], [(x * 1.12, z * 1.28) for x, z in lo_front], chamfer=0.01)
    for s in (-1, 1):
        # cutting edges: a dark line along each side of the gape
        kit.segment("bill_edge_%d" % s, "trim", hc + Vector((s * 0.2, -0.18, -0.05)), hc + Vector((s * 0.19, -0.84, -0.06)),
                    0.03, 0.03, 0.5)
        pass   # head part 2: no notches (they read as teeth); the Bill Clamp is the dark cutting edge itself
        # the real bill's dark markings, a few blotches
        for k, (dy, dz) in enumerate(((-0.34, 0.06), (-0.52, 0.03))):
            kit.shell("bill_spot_%d_%d" % (s, k), "trim", hc + Vector((s * 0.2, dy, dz + 0.03)), (0.03, 0.08, 0.05), (0, 0, 0), 0.5, levels=0)
        # eyes, set forward for binocular vision, in dark sockets
        kit.shell("eye_%d_socket" % s, "frame_dark", hc + Vector((s * 0.17, -0.12, 0.07)), (0.08, 0.11, 0.1), (0, 0, 0), 0.5, levels=1)
        kit.shell("eye_%d" % s, "eye_src", hc + Vector((s * 0.2, -0.13, 0.07)), (0.05, 0.08, 0.07), (0, 0, 0), 0.0, levels=0)
    # Stillwater Lance: a lens under the hooked nail
    pass   # p15 (Preston): no gun on the head until the shape is right
    if not P93:
        kit.cyl("bill_lancemuzzle", "frame_dark", hc + Vector((0, -0.95, 0.15)), hc + Vector((0, -1.04, 0.14)), 0.06, 10)
    for sd in (-1, 1):   # p5: the reference's grey jaw bolt at the back of the skull
        kit.disc("head_jawbolt_%d" % sd, hc + Vector((sd * 0.2, 0.08, -0.04)), 0.09, depth=0.1)
    if not P93:
        kit.shell("bill_lens", "eye_src", hc + Vector((0, -0.95, -0.09)), (0.05, 0.05, 0.05), (0, 0, 0), 0.0, levels=0)


# ---- wings: folded along the sides; blue coverts, deep-blue primaries back to the tail, gold leading edges -----
def slab(name, mat, origin, xax, yax, poly, t, chamfer=0.015):
    """A flat plate cut from the polygon `poly` (local u along xax, v along yax), `t` thick and centred on that plane,
    flat faces and a crisp chamfer: a feather blade or a backing plate."""
    import bmesh
    from mathutils import Matrix
    xax, yax = Vector(xax).normalized(), Vector(yax).normalized()
    zax = xax.cross(yax).normalized()
    bm = bmesh.new()
    a = [bm.verts.new((u, v, t / 2)) for u, v in poly]
    b = [bm.verts.new((u, v, -t / 2)) for u, v in poly]
    bm.faces.new(a)
    bm.faces.new(b[::-1])
    n = len(poly)
    for i in range(n):
        bm.faces.new((a[i], b[i], b[(i + 1) % n], a[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if chamfer > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(chamfer, t * 0.4), offset_type="OFFSET", segments=1,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = Matrix.Translation(Vector(origin)) @ Matrix((xax, yax, zax)).transposed().to_4x4()
    return kit._finish(ob, mat)


def feather(name, mat, root, d, up, length, h, t, cut=0.7):
    """A feather blade from `root` along `d`, `h` tall across `up`: the top edge runs the full length and the tip is cut
    back at an angle, so a stack of them ends in a staircase of points (his wing)."""
    return slab(name, mat, root, d, up, [(0, -h / 2), (length - cut * h, -h / 2), (length, h / 2), (0, h / 2)], t)


FEATHERS = (10, 21, 32, 43)   # p86: four primaries, degrees below the back line, each running back to FAN_REACH so the
# tips stand in one column with background between them (his fan). Swept against his side view: p86g's fan (12 to 48
# degrees, the top blade 1.25 long) hung below and reached past his wing, outline 0.648 to 0.568; this one 0.681 (E)
# and 0.643 (SE) with the four blades still apart at the tips
P90 = os.environ.get("SHOEBILL_P90", "1") == "1"   # p90 (2026-10-19, refine pass part by part against Preston's painting):
# his primaries hang down and back as long navy blades ending near knee height; ours fanned out sideways (10 to 43
# degrees). Steeper, each capped at FEATHER_MAX so the lowest stays off the floor. SHOEBILL_P90=0 builds p89.
if P90:
    FEATHERS = (28, 38, 48, 58)
P94 = os.environ.get("SHOEBILL_P94", "1") == "1"   # p94: the lower bill on its own jaw bone; =0 builds p93
# p95 (2026-10-20, Codex's shoebill sheet; Preston: "go"): its crest stands up as a spiky tuft and its chest plate carries two
# bold dark slits; ours had a low crest and three 1-2 px slots. Crest blades 0.26 to 0.36 m; the vent two slots, longer
# and wider. (Its wing is already two calm plates, p87; its battle sprite's width matches ours, 0.78 against 0.77.)
P95 = P94 and os.environ.get("SHOEBILL_P95", "1") == "1"   # =0 builds p94
# p96 (2026-10-20, factory pass part by part against Codex's sprite; Preston: "go shoebill next"): the body, bill, crest,
# chest and wing match; Codex's legs are about twice as thick, dark tubes with big gold collars and thick toes with big
# gold claws, where ours read as 1 to 2 px lines. Earlier passes thinned them on purpose to Preston's painting (r10 "thin
# grey rods", p63 "his legs fill half what ours did"), so halfway: shins and tarsi 1.5x, collars and joint blocks 1.3x,
# toes 1.2x, claws 1.25x. SHOEBILL_P96=0 builds p95.
P96 = P95 and os.environ.get("SHOEBILL_P96", "1") == "1"
LW, CW, TW, KW = (1.5, 1.3, 1.2, 1.25) if P96 else (1.0, 1.0, 1.0, 1.0)
P93 = os.environ.get("SHOEBILL_P93", "1") == "1"   # p93: the head gun and the breast guns removed; =0 builds p92
P92 = os.environ.get("SHOEBILL_P92", "1") == "1"   # p92: hips mirrored; =0 builds p91
P91 = os.environ.get("SHOEBILL_P91", "1") == "1"   # p91: thighs flared up into the hull, gold hip rings; =0 builds p90
FEATHER_MAX = 0.95 if P90 else 99.0
FAN_REACH = float(os.environ.get("SHOEBILL_FAN_REACH", "1.05"))   # p87 tried 1.16 (longer blades): outline E 0.677 to 0.645
FEATHER_H = 0.15   # each blade's height across: 5 sprite px, about 4 after the 35-degree turn
COVERT_SLOPE = 16   # p86: degrees the covert rows slope down toward the back
FEATHER_CUT = 1.5   # p87: the tip's slant, in blade heights (p86 0.7: a short stub that broke into 1 px spurs)
EDGE_H = 0.04       # p87: the light top strip, about one sprite px
EDGE_SEG = 0.17     # p87: strip pieces about 5 sprite px long (under the pixelizer's 160 render px "thin" area)
EDGE_IN = 0.03      # p87: set one sprite px in from the blade's top, under the blade's dark outline (on the outline
# itself the pixelizer's silhouette pass painted it dark: p87a)


def hard_wing(s, sh, el, wr, tip):
    """p86: the folded wing as hard plates. Coverts: two rows of three flat plates sloping down and back along the fold
    (p86f's level rows read as a grid of tiles), the upper row light blue and outboard (a shingle over the lower), the
    lower row mid blue; a grey joint disc at the front. Primaries: four flat deep-blue blades fanned from under the
    coverts, 11 degrees apart, each with a lit top edge, so each blade reads as its own 4-5 px band ending in its own
    point, on a near-black backing plate that turns the gaps near the root into seams."""
    out = Vector((s, 0, 0.18)).normalized()   # the faces tipped up a little, so the toon light separates the rows
    a = Vector((0, math.cos(math.radians(COVERT_SLOPE)), -math.sin(math.radians(COVERT_SLOPE))))
    a = (a - out * a.dot(out)).normalized()
    c = out.cross(a)
    if P87:
        # p87: the six covert tiles (each 3-6 sprite px, the "crumpled foil" on the upper wing) merged into two long
        # plates, a light one over a mid one, so the upper wing reads as two calm plates with one seam between
        for row, (start, mat, h, ln) in enumerate((((0.64, -0.26, 1.565), "plate", 0.28, 0.9),   # the upper one tall
                                                   # enough to cover the wing's upper limb (its pointed top showed as speckle)
                                                   ((0.6, -0.16, 1.31), "mid", 0.2, 0.84))):
            ctr = Vector((s * start[0], start[1], start[2] + LIFT)) + a * (0.31 * 1)
            hard_block("wing_upper_cov_%d_%d" % (s, row), mat, ctr, a, c, out, (ln, h, 0.07), chamfer=0.026)
    else:
        for row, (start, mat, h) in enumerate((((0.64, -0.26, 1.53), "plate", 0.2), ((0.6, -0.16, 1.31), "mid", 0.19))):
            for k in range(3):
                ctr = Vector((s * start[0], start[1], start[2] + LIFT)) + a * (0.31 * k)
                hard_block("wing_upper_cov_%d_%d" % (s, row * 3 + k), mat, ctr, a, c, out, (0.27, h, 0.07), chamfer=0.022)
    kit.disc("wing_upper_%d_bolt" % s, Vector((s * 0.7, -0.24, 1.4 + LIFT)), 0.12, depth=0.08)   # his grey shoulder disc
    if P87:   # round 2 judges: "the tan ring sits on noisy facets; it needs a dark ring around it to read as a mount"
        kit.cyl("wing_upper_%d_boltseat" % s, "seam", Vector((s * 0.6, -0.24, 1.4 + LIFT)),
                Vector((s * 0.68, -0.24, 1.4 + LIFT)), 0.15, 16)   # its face 6 cm behind the disc's: at 0.715 its rim
        # crossed in front of the far wing's disc in the turned battle pose (W view)
    roots = []
    for k, deg in enumerate(FEATHERS):
        th = math.radians(deg)
        d = Vector((0, math.cos(th), -math.sin(th)))
        up = Vector((0, math.sin(th), math.cos(th)))
        root = Vector((s * (0.52 - 0.022 * k), 0.14 + 0.05 * k, 1.33 + LIFT - 0.1 * k))
        ln = min(FEATHER_MAX, (FAN_REACH - root.y) / math.cos(th))
        roots.append((root, d))
        if P87:
            # p87: a deep navy blade with one thin light strip near its top edge (about one sprite px), the tip cut on
            # a long clean slant; p86's 6 cm strip in 'face' won two px a blade and the blades read pale. The strip is
            # short pieces laid end to end: the pixelizer turns any part of 16+ px that sits on another part into a
            # seam two shades down (p87b: one long strip went dark), and a piece under 160 render px wins its pixels
            feather("wing_hand_%d_%d" % (s, k), "feather", root, d, up, ln, FEATHER_H, 0.05, cut=FEATHER_CUT)
            e0 = root + up * (FEATHER_H / 2 - EDGE_IN - EDGE_H / 2) + Vector((s * 0.03, 0, 0))
            e_len = ln - FEATHER_CUT * EDGE_IN - 0.02
            nseg = max(1, int(math.ceil(e_len / EDGE_SEG)))
            for j in range(nseg):
                u0, u1 = e_len * j / nseg, e_len * (j + 1) / nseg
                if j < nseg - 1:
                    slab("wing_hand_%d_%d_edge%d" % (s, k, j), "feather_hi", e0 + d * u0, d, up,
                         [(0, -EDGE_H / 2), (u1 - u0, -EDGE_H / 2), (u1 - u0, EDGE_H / 2), (0, EDGE_H / 2)], 0.02, chamfer=0.006)
                else:
                    feather("wing_hand_%d_%d_edge%d" % (s, k, j), "feather_hi", e0 + d * u0, d, up, u1 - u0, EDGE_H, 0.02, cut=FEATHER_CUT)
            continue
        feather("wing_hand_%d_%d" % (s, k), "trim", root, d, up, ln, FEATHER_H, 0.05)
        feather("wing_hand_%d_%d_edge" % (s, k), "face", root + up * (FEATHER_H / 2 - 0.03) + Vector((s * 0.03, 0, 0)), d, up, ln - 0.06, 0.06, 0.02)
    (r0, d0), (r3, d3) = roots[0], roots[-1]
    back = [r0 + Vector((0, 0, 0.06)), r0 + d0 * 0.8, r3 + d3 * 0.62, r3 - Vector((0, 0, 0.06))]
    xb = s * 0.45
    slab("wing_hand_%d_back" % s, "seam", Vector((xb, 0, 0)), (0, 1, 0), (0, 0, 1), [(p.y, p.z) for p in back], 0.04)


JOINTS = {}
WING_DROP = 8   # blind review (2026-10-15): degrees the folded wing tips down about the shoulder


def wings():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        sh = Vector((s * 0.38, -0.12, 1.55 + LIFT))   # p19: the wing folds down the small body's side
        el = Vector((s * 0.46, 0.3, 1.42 + LIFT))
        wr = Vector((s * 0.46, 0.0, 1.25 + LIFT))
        tip = Vector((s * 0.3, 1.3, 1.0 + LIFT))   # part pass body/wing (2026-10-13): the primaries fan back past the rump and down as his (red at the lower back in the overlay); p19: 0.98, 0.92
        JOINTS.update({"sh." + side: sh, "el." + side: el, "wr." + side: wr, "fingers." + side: tip})
        kit.limb_solid("wing_upper_%d" % s, "trim" if P87 else "main", sh, el, (s, 0, 0),
                       [(0, 0.2, 0.16), (1, 0.16, 0.12)], [(0, 0.2), (1, 0.16)] if P87 else [(0, 0.34), (1, 0.28)])   # p87: less tall (width is
                       # its height here), under the upper covert; at 0.34 its top stood above the covert as a navy fin   # p15: pale folded wing   # p7: dark under the blocks, so the gaps read
        if not HARD:
            kit.disc("wing_upper_%d_bolt" % s, sh + Vector((s * 0.16, 0.02, 0.02)), 0.1, depth=0.2)   # p7: the grey shoulder bolt
        kit.limb_solid("wing_fore_%d" % s, "trim" if P87 else "main", el, wr, (s, 0, 0), [(0, 0.16, 0.12), (1, 0.12, 0.1)],
                       [(0, 0.17), (1, 0.14)] if P87 else [(0, 0.3), (1, 0.24)])   # p6: light blue   # p87: its top under the covert
        # Wing Buffet: gold armour along the leading edge (the top of the folded forearm)
        lz = -0.1 if P87 else 0.0   # p87: tucked under the upper covert; its tip showed over it as one stray tan pixel
        kit.segment("wing_lead_%d" % s, "accent", el + Vector((s * 0.04, 0.02, 0.16 + lz)), wr + Vector((s * 0.04, -0.1, 0.18 + lz)), 0.12, 0.14, 0.5)   # w3: along the leading edge (w2 poked through the coverts)
        kit.segment("wing_lead_%d_edge" % s, "frame_dark", el + Vector((s * 0.04, 0.02, 0.26 + lz)), wr + Vector((s * 0.04, -0.1, 0.28 + lz)), 0.06, 0.06, 0.5)
        if HARD:
            hard_wing(s, sh, el, wr, tip)
            continue
        # coverts: overlapping plates on the side of the folded wing
        for k in range(6):   # p5: six big rounded light-blue blocks in two columns, the reference's stacked plates
            col, rowk = k % 2, k // 2
            c = sh.lerp(el, 0.1 + 0.3 * rowk) + Vector((s * 0.14, 0.24 * col - 0.12, -0.04 - 0.14 * rowk))
            kit.shell("wing_upper_cov_%d_%d" % (s, k), "main", c, (0.16, 0.26, 0.3), (0, 10, 0), 0.45, levels=2)   # p7: separate blocks with dark gaps between
        for k in range(4):   # p6: a smaller fan under the blocks
            a = sh.lerp(el, 0.55) + Vector((s * 0.1, 0.1 * k - 0.1, -0.5 - 0.03 * k))
            b = a + Vector((s * 0.02, 0.18 + 0.05 * k, -0.1 - 0.03 * k))   # p15: the under-fan tucked up
            kit.segment("wing_fore_%d_fan%d" % (s, k), "trim", a, b, 0.03, 0.09, 0.5)
        # primaries: long deep-blue blades from the wrist back past the tail, stacked
        for k in range(4):   # Mechabeast V2 blind review (2026-10-15): four stepped navy blades, not six into one slab (part pass had six)
            a = wr + Vector((s * (0.07 - 0.014 * k), 0.06 + 0.05 * k, 0.02 - 0.07 * k))   # r4: primaries carried higher
            b = tip + Vector((-s * 0.016 * k, -0.11 * k, -0.03 - 0.11 * k))   # blind review: each lower blade shorter and lower, a staircase of tips as his
            kit.segment("wing_hand_%d_%d" % (s, k), "trim", a, b, 0.04, 0.22, 0.5)
            up = Vector((s * 0.035, 0, 0.1))   # blind review: a lighter edge along each blade's top, his feather separations
            kit.segment("wing_hand_%d_%dhl" % (s, k), "face", a + up, b + up + Vector((0, -0.04, 0)), 0.03, 0.04, 0.5)
    # blind review (2026-10-15): the whole wing 8 degrees down about the shoulder and 8 cm lower; his wing hangs lower
    # (column profile p71: our wing tip 0.06 of the height above his)
    from mathutils import Matrix
    piv = Vector((0, -0.12, 1.55 + LIFT))
    M = Matrix.Translation((0, 0, -0.08)) @ Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-WING_DROP), 4, "X") @ Matrix.Translation(-piv)
    for o in list(bpy.context.scene.objects):
        if o.type == "MESH" and o.name.startswith("wing_"):
            o.matrix_world = M @ o.matrix_world
    for k in list(JOINTS):
        if k.split(".")[0] in ("sh", "el", "wr", "fingers"):
            JOINTS[k] = M @ JOINTS[k]


# ---- legs: long and dark, the ankle low, the bare tarsus, very long toes --------------------------------------
STAGGER = 0.36   # blind review 2 (2026-10-15): feet further apart, as his; was 0.3. pass 2: further apart, his legs splay (0.2 in the first pass); part pass legs (2026-10-13): his two legs stand apart with a gap in the side view; at 0.06 ours overlapped into one column (legs part 2 had 0.06)


def legs():
    for s in (-1, 1):
        side = "L" if s == 1 else "R"
        o = Vector((0, s * STAGGER - (0.1 if s == -1 else 0.0), 0))   # blind review 2 (2026-10-15): the near leg 10 cm further forward (p78 overlay: his front leg ahead of ours)
        # Mechabeast V2 blind review 2 (2026-10-15): hip, knee and ankle nearly in line and the tarsus upright, so each
        # leg reads as one straight strut (ours bowed back into a C); the legs 27 cm forward, his stand under the breast (p77 at 15 cm: overlay red ahead of both legs)
        oh = Vector((0, -0.05, 0)) if P92 else o   # p92 (Preston: "Still a gap ... compare to the other hip"): the hips
        # mirrored, both at the mean of the two staggers, so both thighs leave the hull at the same place (the far hip
        # 0.36 m back hid its thigh behind the hull and its gold ring hung under it in S); the knees go halfway, the
        # feet keep the full stagger, so the legs still separate in the side view
        hp = Vector((s * 0.17, -0.15, 0.8 + LIFT)) + oh   # p18: the hips inside the small body's bottom; legs nearly 40% of the height
        kn = Vector((s * 0.26, -0.2, 0.6 + LIFT * 0.85)) + (oh + (o - oh) * 0.5)   # ref-5 part pass (2026-10-13): the legs splay apart to the feet, his stand with a gap between them
        if s == 1 and os.environ.get("SHOEBILL_P89", "1") == "1" and not P92:   # p92 mirrored: no far-knee drop. p89: the far knee 12 cm lower (longer thigh, shorter shin).
            kn = kn + Vector((0, 0, -0.12))   # The 18-degree camera draws the far leg higher, so its knee sat at the hull's
            # bottom edge and the hull hid the thigh: the leg read as hanging from its gold collar
        an = Vector((s * 0.3, -0.21, 0.4)) + o   # blind review 2: the ankle low, his ankle ring sits just above the toes
        tb = Vector((s * 0.32, -0.21, 0.08)) + o
        JOINTS.update({"hp." + side: hp, "kn." + side: kn, "an." + side: an, "toe." + side: tb})
        # p89 (2026-10-19, Preston: "what would be its left leg ... is floating and not connected to torso"): the far (+x)
        # thigh is there in 3D (22 render rows from the hull to the knee in E) but in the hull's light blue it merged into
        # the belly plates at sprite size, so the far leg seemed to start at its gold knee collar under the body. The far
        # thigh and shin plate take the mid blue, the far-limb convention, so the leg reads from the hip down.
        fl = "mid" if (s == 1 and os.environ.get("SHOEBILL_P89", "1") == "1") else "main"   # SHOEBILL_P89=0 builds p87
        if P91:   # p91 (2026-10-19, Preston: "its leg is still not connected"): both thighs read as blocks hung under the
            # hull's dark bottom edge. His thighs are broad armour that runs up into the body, with gold rings at the joints:
            # the thigh starts 14 cm higher inside the hull, flares to 0.24 m at the top, and a gold ring marks the hip
            top = hp + Vector((0, 0, 0.14))
            kit.limb_solid("leg_thigh_%d" % s, fl, top, kn, (s, 0, 0), [(0, 0.24, 0.2), (0.55, 0.16, 0.14), (1, 0.1, 0.09)], [(0, 0.24), (0.55, 0.16), (1, 0.1)])
            ax_ = (kn - hp).normalized()
            kit.cyl("leg_thigh_ring_%d" % s, "accent", hp + ax_ * 0.06, hp + ax_ * 0.13, 0.16, 16)
        else:
            kit.limb_solid("leg_thigh_%d" % s, fl, hp, kn, (s, 0, 0), [(0, 0.15, 0.13), (1, 0.1, 0.09)], [(0, 0.15), (1, 0.1)])   # p63 (column profile): thinner, his legs fill half what ours did at shin height   # r10: slimmer thighs
        kit.limb_solid("leg_shin_%d" % s, "frame", kn, an, (s, 0, 0), [(0, 0.06 * LW, 0.055 * LW), (1, 0.05 * LW, 0.045 * LW)], [(0, 0.06 * LW), (1, 0.05 * LW)])   # r10 (look-compare): his legs are thin grey rods
        kit.plate("leg_shin_plate_%d" % s, fl, kn.lerp(an, 0.25) + Vector((s * 0.08, 0, 0)), 0.16, 0.22, 0.04,
                  (-10, 0, s * 84), bend=0.4, bevel=0.008)   # the feathered top of the shin
        # Mechabeast V2 blind review 4 (2026-10-15): joint names end in the side, so bird_rig binds them to their own leg
        # ("leg_shin_1_knee" bound to shin.R and floated off as stray gold specks); a gold collar round the leg at knee
        # and ankle, his bright gold rings
        axis = (an - kn).normalized()
        for nm, pt in (("leg_ankle_%d" % s, an), ("leg_shin_knee_%d" % s, kn)):   # legs part 2: gold hex joint blocks, as the reference
            kit.shell(nm, "accent", pt + Vector((s * 0.02, 0, 0)), (0.11 * CW, 0.1 * CW, 0.11 * CW), (0, 0, 0), 0.4, levels=1)   # blind review 2 (2026-10-15): smaller still, his small knee joint; was 0.14   # p67: smaller, to suit the thinner legs (his joints are small gold rings)
            kit.shell(nm.replace("_%d" % s, "_hub_%d" % s), "frame_dark", pt + Vector((s * 0.1, 0, 0)), (0.05, 0.08, 0.08), (0, 0, 0), 0.5, levels=0)
            lo, hi = (0.0, 0.08) if pt is kn else (-0.1, -0.02)   # on the shin: just under the knee, just over the ankle
            kit.cyl(nm.replace("_%d" % s, "_ring_%d" % s), "accent", pt + axis * lo, pt + axis * hi, (0.12 if pt is kn else 0.1) * CW, 12)
        kit.limb_solid("leg_foot_%d" % s, "frame", an, tb, (s, 0, 0), [(0, 0.055 * LW, 0.05 * LW), (1, 0.05 * LW, 0.045 * LW)], [(0, 0.055 * LW), (1, 0.05 * LW)])   # r10: thin tarsus
        # three very long forward toes splayed, one hind toe; dark, with gold claw tips
        for k, ang in enumerate((-24, 0, 24, 180)):
            r = math.radians(ang)
            ln = 0.3 if ang == 180 else (0.5 if ang == 0 else 0.46)   # p59 (column profile): toes shorter, ours ran past his   # pass 2: longer toes, his spread wide forward; legs part had 0.26/0.5/0.42
            d = Vector((s * 0 + math.sin(r) * (1 if s == 1 else -1), -math.cos(r), 0))
            tip = tb + d * ln + Vector((0, 0, -0.05))
            kit.segment("toe_%d_%d" % (s, k), "frame", tb + Vector((0, 0, 0.02)), tip, 0.1 * TW, 0.12 * TW, 0.5)   # legs part 2: toes raised, with gaps between
            cw, ch = (0.13, 0.12) if (P87 and ang == 180) else (0.1, 0.09)   # p87: the hind claw a size up (its dark
            # shade alone read as one stray brown pixel at the back toe)
            kit.segment("toe_claw_%d_%d" % (s, k), "accent", tip - d * 0.04, tip + d * 0.16 * KW + Vector((0, 0, -0.02)), cw * KW, ch * KW, 0.5)   # blind review 4 (2026-10-15): bigger gold claw tips, his read at sprite size; was 0.09 long
            jc = tb + d * (ln * 0.5) + Vector((0, 0, -0.04))   # gold toe joints; blind review 4: built here, named by side (disc's "_ring" names bound to the R foot)
            kit.cyl("toe_jnt_%d_%d" % (s, k), "frame", jc - Vector((0, 0, 0.03)), jc + Vector((0, 0, 0.03)), 0.045, 10)
            kit.cyl("toe_jring_%d_%d" % (s, k), "accent", jc + Vector((0, 0, 0.03)), jc + Vector((0, 0, 0.055)), 0.032, 10)


def stand_up():
    """Pitch everything but the legs about the hip line by PITCH; then turn the head back so the bill stays level
    (minus 10 degrees). The wing joints and the body / head bones follow, so the rig matches the standing mesh."""
    from mathutils import Matrix
    piv = Vector((0, 0.12, 1.12 + LIFT))
    R = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(PITCH), 4, "X") @ Matrix.Translation(-piv)
    hc_new = R @ HC
    Rh = Matrix.Translation(hc_new) @ Matrix.Rotation(math.radians(-PITCH + 8), 4, "X") @ Matrix.Translation(-hc_new)   # p26: +8 (+20 hung the bill below the head); positive tips the bill DOWN (positive about X lowers the -Y tip; p22-p24 at -12 raised it, the head overlay showed it)
    head_parts = ("head_", "bill", "eye_", "crest")
    for o in list(bpy.context.scene.objects):
        if o.type != "MESH" or o.name.startswith(("leg_", "toe_")):
            continue
        o.matrix_world = R @ o.matrix_world
        if o.name.startswith(head_parts):
            o.matrix_world = Rh @ o.matrix_world
    for k in list(JOINTS):
        if k.split(".")[0] in ("sh", "el", "wr", "fingers"):
            JOINTS[k] = R @ JOINTS[k]
    CFG["body_bone"] = tuple(R @ Vector(v) for v in CFG["body_bone"])
    CFG["head_bone"] = (R @ Vector(CFG["head_bone"][0]), Rh @ (R @ Vector(CFG["head_bone"][1])))


CFG = {
    "battle_set": "shoebill_m",   # battle clips: tools/blender/attacks.py (2026-10-13)
    "name": "shoebill_m",
    "head": ("head_", "bill", "eye_", "neck", "crest"),
    "stance": "clip=battle;frame=1",   # battle pose by leg (bird_rig.battle_pose_for, 2026-10-13); was base=1;R_leg=6;L_leg=24
    "battle_legs": {"R": (-0.12, -0.02, 22), "L": (0.05, -0.02, 22)},   # blind review 2 (2026-10-15): ankles in reach of the straight legs, near leg leaning forward, far leg near upright, his inverted V (p77: L 0.2 leaned too far back) (p63: R -0.16, L 0.14, dz 0)   # p63: wider splay, his near leg stands further out
    "battle_head": (-8, 0, 0),   # p60 (column profile): the bill rides higher in his; negative lifts it (p59 at +4 tipped it down); the walk frame had -3   # near foot a little forward, both legs splayed out 12 degrees: his legs stand apart   # part pass (2026-10-13): near leg 22, far leg 2, the widest planted stride (legs 0.294 to 0.359)
    "body_bone": ((0, 0.6, 1.3 + LIFT), (0, -0.35, 1.6 + LIFT)),
    "head_bone": ((0, -0.28, 1.6 + LIFT), (0, -1.3, 2.1 + LIFT)),
    "joints": JOINTS,
    "stride": 0.36,
    "crouch": 0.04,
    "leg_path": (0.0, 0.12, 25),   # back, lift, tarsus tuck in swing
}


# ---- the loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"). Roster moves get
# hardware; move None marks a spare hardpoint, DRAFT, Preston's to name. Shared builders: tools/blender/weapons.py.
def loadout():
    A, on, T = wpn.anchor, wpn.on, "torso_core"
    if P93:   # p93 (2026-10-19, Preston: the shoebill pivots to its real bird's weapons, bill-clatter gunfire, the
        # decapitating bill, sentry stillness and a lunge; "you have permission to remove top weapon also the two bulbs
        # sticking out of chest that look like nipples"): the Lance gun on the head and the two breast guns go; the
        # bill's clamp teeth stay. SHOEBILL_P93=0 builds p92.
        return [{"slot": "clamp", "move": "Apex Decapitation", "kind": "spikes", "prefix": "bill_", "note": "teeth along the upper bill's edge",
                 "args": {"points": [A("bill_upper", (fx, fy, 0.05)) for fx in (0.15, 0.85) for fy in (0.2, 0.45)], "length": 0.08, "r": 0.025, "direction": (0, 0, -1)}}]
    L = [
        {"slot": "lance", "move": "Stillwater Lance", "kind": "cannon", "prefix": "head_", "note": "the beam gun on top of the head, as his reference",
         "args": {"base": A("head_core", (0.5, 0.55, 1.0), (0, 0, 0.11)), "direction": (0, -1, 0), "length": 1.15, "r": 0.04, "housing": (0.13, 0.3, 0.11),
                  "post": A("head_core", (0.5, 0.55, 0.85))}},   # p62 (Preston: "the gun isnt attached on top of head" in the side view): a pylon from the skull, the mount 5 cm lower   # ref-5: a long thin barrel on a small mount, his   # p42: up clear of the crest (p41 hid it)
        {"slot": "clamp", "move": "Bill Clamp", "kind": "spikes", "prefix": "bill_", "note": "teeth along the upper bill's edge",
         "args": {"points": [A("bill_upper", (fx, fy, 0.05)) for fx in (0.15, 0.85) for fy in (0.2, 0.45)], "length": 0.08, "r": 0.025, "direction": (0, 0, -1)}},
    ]
    for sd in (-1, 1):
        L.append({"slot": "root" + ("L" if sd == 1 else "R"), "move": None, "kind": "cannon", "note": "spare: a gun on each side of the breast",
                  "args": {"base": on(kit, T, (0.3 if sd < 0 else 0.7, 0.0, 0.62), (0, -1, 0), 0.06), "direction": (0, -1, 0), "length": 0.22, "r": 0.045}})   # p61 (column profile): shorter, they reached past his chest gun   # p42: on the breast, ahead of the folded wing (p41 hid them)
    return L


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    body()
    head()
    for o in list(bpy.context.scene.objects):   # p18: his head and bill are a quarter of the height; the head group 1.4x about HC
        if o.type == "MESH" and o.name.startswith(("head_", "bill", "eye_", "crest")):
            o.location = HC + (o.location - HC) * 1.05
            o.scale = tuple(v * 1.05 for v in o.scale)   # part pass head (2026-10-13): 1.05; at 1.25 the bill was as wide as the body (head overlay 42% ours-only); p19: 1.4 overshot
    wings()
    legs()
    wpn.build_loadout(kit, "shoebill_m", loadout())
    stand_up()
    greebles.run(kit, wpn, lambda n: bird.bone_for(n, CFG), skip_prefix=("leg_foot", "leg_shin", "toe", "plate_", "torso_core")
                 + (("wing_",) if HARD else ()))   # blind review 2: no panels on the torso plates (their seams were the noise); p86: none on the wing either (its bolts and vents were the speckle on the coverts)
    if P94:   # p94 (2026-10-19, Preston: "do it"): the lower bill rides its own jaw bone, hinged at the back of the gape and
        # parented to the head, so the bill really claps (Bill Clatter), gapes and bites (Apex Decapitation, Sentry Lunge).
        # The bone is laid along the finished lower bill (after the head's scale and the stand-up turn); positive rx
        # opens it, as positive rx tips the head down.
        jaw = bpy.data.objects["bill_lower"]
        jaw.name = "jaw_bill_lower"
        bpy.context.view_layer.update()
        cs = [jaw.matrix_world @ v.co for v in jaw.data.vertices]
        back = max(cs, key=lambda c: c.y)
        tip = min(cs, key=lambda c: c.y)
        hinge = Vector((0, back.y, max(c.z for c in cs)))
        CFG["extra_bones"] = [("jaw", tuple(hinge), (0, tip.y, (tip.z + hinge.z) / 2), "head")]
        CFG["part_bones"] = (("jaw_", "jaw"),)
    bird.tag_parts(CFG)
    ob = kit.join_into_one()
    ob.name = "shoebill_m"
    os.makedirs(os.path.dirname(OUT_BLEND), exist_ok=True)
    bird.rig_and_clips(ob, CFG, kit, OUT_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("SHOEBILL_DONE dims=%s triangles=%d" % (tuple(round(v, 3) for v in ob.dimensions), tris))


main()
