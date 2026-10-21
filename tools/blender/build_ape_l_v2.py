# Gorilla type (ape_l), version 2: rounded armour shells instead of boxes (Claude, 2026-10-11; Preston: "it was a good
# start, all it needs is a skillup"). What changed, from hard-surface practice (docs/plan/3d-pivot-2026-10-11.md):
#   - Armour is subdivision shells: a small box cage smoothed twice, with creased edges so the rims stay defined.
#     That gives the swelling, plated-muscle look of the concept instead of bricks.
#   - Limbs are stacks of shells over a dark machine frame (pistons, cables, round joint discs).
#   - Proportions are measured from the blueprint (docs/art/3d/concepts/blueprint_views.png): front is 0.74 x as wide
#     as tall, side 0.93 x as long as tall; the script renders front and side silhouettes and scores the overlap.
# Version 1 (tools/blender/build_ape_l.py) stays as it was.
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_ape_l_v2.py
# Model space: metres, Z up, facing -Y. About 2.6 m to the top of the rack.
import bpy, bmesh, math, os, re
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_GLB = os.path.join(ROOT, "art", "machines", "ape_l", "ape_l.glb")
OUT_BLEND = os.path.join(ROOT, "docs", "art", "3d", "ape_l_v2.blend")
OUT_VIEWS = os.path.join(ROOT, "docs", "art", "3d", "ape_l_views")
OUT_SIL = os.path.join(ROOT, "docs", "art", "3d", "silhouette")
HEX = {"main": "5c804a", "trim": "3e5a33", "accent": "d98a40", "frame": "8a8d92", "frame_dark": "45474c",
       "face": "65666c", "light": "1fb8c4",
       "steel": "c2c6cb"}   # measured from Preston's picked sprite, 2026-10-11; steel: model pass 2 (2026-10-16), light joint faces
MATS = {}


def srgb(h):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), 1.0)


def make_materials():
    for key, h in HEX.items():
        m = bpy.data.materials.new("ape_" + key)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = srgb(h)
        b.inputs["Roughness"].default_value = {"accent": 0.4, "frame": 0.45, "frame_dark": 0.5, "face": 0.5}.get(key, 0.62)
        b.inputs["Metallic"].default_value = {"accent": 0.7, "frame": 0.55, "frame_dark": 0.5, "face": 0.4}.get(key, 0.1)
        if key == "light":
            b.inputs["Emission Color"].default_value = srgb(h)
            b.inputs["Emission Strength"].default_value = 0.8
        tex = os.path.join(ROOT, "art", "machines", "ape_l", "textures", key + ".png")
        if os.path.exists(tex):
            node = m.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = bpy.data.images.load(tex)
            node.interpolation = "Closest"
            m.node_tree.links.new(node.outputs["Color"], b.inputs["Base Color"])
        MATS[key] = m


def _finish(ob, mat):
    ob.data.materials.append(MATS[mat])
    return ob


def shell(name, mat, center, size, rot=(0, 0, 0), crease=0.55, levels=2, squash=None, panel=True):
    """An armour shell: a box cage smoothed by subdivision; crease (0..1) keeps the rims defined.
    squash = (top, bottom) widths as fractions, to taper the cage before smoothing (a dome, a wedge)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=center, rotation=[math.radians(a) for a in rot])
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if squash:
        top, bottom = squash
        for v in ob.data.vertices:
            f = top if v.co.z > 0 else bottom
            v.co.x *= f
            v.co.y *= 0.5 + 0.5 * f
    if levels > 0:
        # Bevel, then smooth (the hard-surface order): rounded rims with flat faces between them, so a shell
        # reads as a machined plate instead of a pillow. Lower crease = rounder.
        small = min(size)
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=small * min(0.45, 0.08 + 0.3 * (1.0 - crease)),
                        offset_type="OFFSET", segments=1, profile=0.5, affect="EDGES",
                        clamp_overlap=True)
        if panel and levels >= 2 and small >= 0.3:
            # A raised panel inset into every big face: the plate edge catches the light like a real seam.
            big = sorted(bm.faces, key=lambda f: f.calc_area(), reverse=True)[:6]
            bmesh.ops.inset_individual(bm, faces=big, thickness=small * 0.09, depth=small * 0.025, use_even_offset=True)
        bm.to_mesh(ob.data)
        bm.free()
    # No smoothing pass: the bevels plus auto smooth give rounded rims with flat faces, at a game budget.
    return _finish(ob, mat)


def dome(name, mat, center, radii, segments=12, rings=7):
    """A faceted ellipsoid, partly sunk into what it sits on: reads as a rounded armour dome."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1, location=center)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = radii
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(ob, mat)


def fuse(names, fillet=0.012):
    """Union several parts into one casting (exact boolean, keeping each part's material), then fillet only the
    sharp junctions where they met, so they stop reading as separate shapes pushed into each other."""
    obs = [bpy.data.objects[n] for n in names if n in bpy.data.objects]
    base = obs[0]
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    for o in obs[1:]:
        m = base.modifiers.new("fuse", "BOOLEAN")
        m.operation = "UNION"
        m.solver = "EXACT"
        m.material_mode = "TRANSFER"
        m.object = o
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(o)
    if fillet > 0:
        b = base.modifiers.new("fillet", "BEVEL")
        b.width = fillet
        b.segments = 2
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)   # the chamfers (45 degrees) stay crisp; the junctions get filleted
        b.harden_normals = False
    return base


def groove(ob, a, b, normal, w=0.03, d=0.03, mat="frame_dark"):
    """A dark panel line cut into a solid (pass 22, the boolean panel workflow): a thin box from a to b lying on the
    surface, w wide, cut d deep along `normal`, with the cutter's material on the new faces so the seam reads dark.
    Applied straight away, before the solid's chamfer, so the seam's edges get chamfered like the rest."""
    a, b = Vector(a), Vector(b)
    dn = (b - a).normalized()
    n = Vector(normal)
    n = (n - dn * n.dot(dn)).normalized()
    x = dn.cross(n)
    bpy.ops.mesh.primitive_cube_add(size=1)
    cut = bpy.context.active_object
    cut.name = ob.name + "_groove"
    cut.scale = (w, 2 * d, (b - a).length)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    cut.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((x, n, dn)).transposed().to_4x4()
    cut.data.materials.append(MATS[mat])
    m = ob.modifiers.new("groove", "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.solver = "EXACT"
    m.material_mode = "TRANSFER"
    m.object = cut
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cut)


_BVH = {}


def surface_hit(target, origin, direction, reach=6.0):
    """Where a ray from `origin` along `direction` first meets the built part `target`: (point, outward normal) in
    world space, or None on a miss. Cast from outside toward the part to land on its outer skin. The part's tree is
    cached by name, so build the target fully before placing anything on it."""
    from mathutils.bvhtree import BVHTree
    tree = _BVH.get(target.name)
    if tree is None:
        bpy.context.view_layer.update()
        tree = _BVH[target.name] = BVHTree.FromObject(target, bpy.context.evaluated_depsgraph_get())
    mw = target.matrix_world
    inv = mw.inverted()
    loc, nor, _, _ = tree.ray_cast(inv @ Vector(origin), (inv.to_3x3() @ Vector(direction)).normalized(), reach)
    if loc is None:
        return None
    return mw @ loc, (inv.transposed().to_3x3() @ nor).normalized()


def on_surface(target, center, outward, standoff):
    """`center` moved onto `target`'s real surface along `outward`, then `standoff` off it. Falls back to `center`
    when the ray misses (the part does not cover that spot)."""
    d = Vector(outward).normalized()
    hit = surface_hit(target, Vector(center) + d * 3.0, -d)
    return hit[0] + hit[1] * standoff if hit else Vector(center)


def plate_on(target, name, mat, aim, outward, w, h, t, standoff=0.03, up=(0, 0, 1), **kw):
    """A plate laid flat on `target`'s real surface where a ray along -`outward` toward `aim` meets it: its face turned
    to the surface normal there, its height running as close to `up` as the surface allows (kangaroo v2: hand-set
    rotations on a leaning body stood the plates up as shards). Returns None on a miss."""
    d = Vector(outward).normalized()
    hit = surface_hit(target, Vector(aim) + d * 3.0, -d)
    if not hit:
        return None
    pt, n = hit
    u = Vector(up) - Vector(up).dot(n) * n
    if u.length < 1e-3:
        u = Vector((0, -1, 0)) - Vector((0, -1, 0)).dot(n) * n
    zx = u.normalized()
    yx = -n
    xx = yx.cross(zx)
    rot = Matrix((xx, yx, zx)).transposed().to_euler("XYZ")
    return plate(name, mat, pt + n * standoff, w, h, t, tuple(math.degrees(r) for r in rot), **kw)


def plate(name, mat, center, w, h, t, rot=(0, 0, 0), bend=0.0, taper=1.0, bevel=0.012, recess=0.0, rim=0.06):
    """A thin armour plate with real thickness, the way Fall of Cybertron layers armour over a frame: a sheet w by h
    facing -Y, its sides bent back by `bend`, its top edge `taper` times as wide as the bottom, solidified inward to
    thickness t and given one crisp bevel. Rotate it into place; the front face stays where `center` puts it."""
    bm = bmesh.new()
    nx, ny = 4, 3
    rows = []
    for j in range(ny + 1):
        v = j / ny - 0.5
        row = []
        for i in range(nx + 1):
            u = i / nx - 0.5
            row.append(bm.verts.new((u * w * (1 + (taper - 1) * (v + 0.5)), bend * (2 * u) ** 2 * w * 0.5, v * h)))
        rows.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    if recess > 0:   # a framed panel: the centre sinks inside a raised rim, like Grimlock's chest armour
        # use_boundary: the plate is an open sheet; without it inset_region did nothing at all (found 2026-10-12, hippo
        # v5: every recessed plate since the gorilla had come out flat)
        bmesh.ops.inset_region(bm, faces=list(bm.faces), thickness=rim, depth=-recess, use_even_offset=True,
                               use_boundary=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = center
    ob.rotation_euler = [math.radians(a) for a in rot]
    sol = ob.modifiers.new("thickness", "SOLIDIFY")
    sol.thickness = t
    sol.offset = -1.0
    bev = ob.modifiers.new("edge", "BEVEL")
    bev.width = bevel
    bev.segments = 1
    bev.limit_method = "ANGLE"
    bev.angle_limit = math.radians(30)
    return _finish(ob, mat)


def plate_along(name, mat, a, b, outward, w, t=0.08, bend=0.35, taper=1.0, offset=0.2, trim_ends=0.06, recess=0.0):
    """A thin armour plate running along a limb from a to b, facing `outward` (made perpendicular to the limb), set
    `offset` metres out from the limb's axis: armour wrapped around a frame strut, with gaps where the frame shows."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    o = Vector(outward)
    o = (o - d * o.dot(d)).normalized()
    length = (b - a).length * (1 - 2 * trim_ends)
    ob = plate(name, mat, (0, 0, 0), w, length, t, (0, 0, 0), bend=bend, taper=taper, recess=recess, rim=min(0.06, w * 0.15))
    y = -o
    x = y.cross(d)
    rot = Matrix((x, y, d)).transposed().to_4x4()
    ob.matrix_world = Matrix.Translation((a + b) / 2 + o * offset) @ rot
    return ob


def drum(name, mat, center, axis, radius, depth, round_=0.95, segments=24):
    """A rounded barrel pod: a short cylinder with heavily rounded rims. Learned by rebuilding Grimlock's shoulder pod
    in the replication exercise (2026-10-11): his pod is a barrel, not a sphere or a flat drum."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius, depth=depth)
    rims = [e for e in bm.edges if all(abs(abs(v.co.z) - depth / 2) < 1e-4 for v in e.verts) and len(e.link_faces) == 2
            and any(len(f.verts) > 4 for f in e.link_faces)]
    bmesh.ops.bevel(bm, geom=rims, offset=min(depth, radius) * round_, offset_type="OFFSET", segments=4, profile=0.5,
                    affect="EDGES", clamp_overlap=True)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world = Matrix.Translation(center) @ Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4()
    return _finish(ob, mat)


def glow_ring(name, center, axis, r_in, r_out, segments=12, gap=0.3, depth=0.02, trench=True):
    """A segmented glowing ring, thin segments set flush in a dark trench: the Cybertron joint light, learned from
    Grimlock's shoulder pod in the replication exercise (2026-10-11)."""
    ax = Vector(axis).normalized()
    c = Vector(center)
    q = Vector((0, 0, 1)).rotation_difference(ax)
    if trench:
        cyl(name + "_trench", "frame_dark", c - ax * depth, c + ax * 0.004, r_out + 0.025, 16)
    mid = (r_in + r_out) / 2
    for i in range(segments):
        a = (i + 0.5) / segments * 2 * math.pi
        bpy.ops.mesh.primitive_cube_add(size=1, location=c + ax * 0.006 + q @ Vector((math.cos(a) * mid, math.sin(a) * mid, 0.0)))
        o = bpy.context.active_object
        o.name = "%s_%d" % (name, i)
        o.scale = (r_out - r_in, 2 * math.pi * mid / segments * (1 - gap), 0.012)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = q @ Matrix.Rotation(a, 3, "Z").to_quaternion()
        _finish(o, "light")


def _prism(name, poly2d, plane, depth, offset):
    """A polygon extruded straight through: plane 'YZ' extrudes along X, 'XZ' along Y."""
    bm = bmesh.new()

    def p3(u, v, w):
        return Vector(offset) + Vector({"YZ": (w, u, v), "XZ": (u, w, v), "XY": (u, v, w)}[plane])
    a = [bm.verts.new(p3(u, v, -depth / 2)) for u, v in poly2d]
    b = [bm.verts.new(p3(u, v, depth / 2)) for u, v in poly2d]
    n = len(poly2d)
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def profile_solid(name, mat, center, side_yz, front_xz, chamfer=0.012, top_xy=None):
    """One continuous sculpted solid from two outlines: the side profile (y, z) and the front profile (x, z) are each
    extruded straight through and only their overlap is kept, then the edges are chamfered. Learned in the replication
    exercise on Grimlock's head (2026-10-11): boxes with planks read as shapes put together (outline overlap 0.55-0.76);
    a profile solid matched 0.72-0.89 and reads as one sculpted piece."""
    a = _prism(name, side_yz, "YZ", 4.0, center)
    b = _prism(name + "_f", front_xz, "XZ", 4.0, center)
    a.data.materials.append(MATS[mat])   # every outline carries the material, so the cut leaves no empty slot
    b.data.materials.append(MATS[mat])
    cutters = [b]
    if top_xy:
        c = _prism(name + "_t", top_xy, "XY", 4.0, center)
        c.data.materials.append(MATS[mat])
        cutters.append(c)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = a
    a.select_set(True)
    for cutter in cutters:
        m = a.modifiers.new("cut", "BOOLEAN")
        m.operation = "INTERSECT"
        m.solver = "EXACT"
        m.object = cutter
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(cutter)
    if chamfer > 0:
        bv = a.modifiers.new("chamfer", "BEVEL")
        bv.width = chamfer
        bv.segments = 1
        bv.limit_method = "ANGLE"
        bv.angle_limit = math.radians(35)
    return a


def limb_solid(name, mat, a, b, outward, depth, width, chamfer=0.015, grooves=()):
    """One sculpted armour solid along a limb segment from a to b, the way Grimlock's legs are built (replication round
    four, 2026-10-11: his leg is one solid with lights set into it, copied at 0.74-0.97 outline overlap).
    depth: [(t, out, in)] how far the solid reaches toward `outward` and away from it at fraction t along the limb;
    width: [(t, half_width)] sideways. Both become outlines of a profile solid, then it is turned into place."""
    a, b = Vector(a), Vector(b)
    length = (b - a).length
    side = [(-o, (t - 0.5) * length) for t, o, i in depth] + [(i, (t - 0.5) * length) for t, o, i in reversed(depth)]
    front = [(w, (t - 0.5) * length) for t, w in width] + [(-w, (t - 0.5) * length) for t, w in reversed(width)]
    ob = profile_solid(name, mat, (0, 0, 0), side, front, chamfer=chamfer)
    for ga, gb, gn in grooves:   # panel lines (pass 23): local coords, x sideways, -y toward `outward`, z along the limb
        groove(ob, ga, gb, gn, w=0.025, d=0.025)
    d = (b - a).normalized()
    o = Vector(outward)
    o = (o - d * o.dot(d)).normalized()
    y = -o
    x = y.cross(d)
    ob.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((x, y, d)).transposed().to_4x4()
    return ob


def segment(name, mat, a, b, w, h, crease=0.5, side=(1, 0, 0)):
    """A chamfered box running from a to b, `w` wide (toward `side`) and `h` thick: one finger segment
    (replication round five, Grimlock's hand: fingers are tapered segments with gaps and knuckle caps between)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    length = d.length
    d = d.normalized()
    ob = shell(name, mat, (0, 0, 0), (w, h, length * 1.04), (0, 0, 0), crease, levels=1)
    sx = Vector(side)
    sx = (sx - d * sx.dot(d)).normalized()
    y = d.cross(sx)
    ob.matrix_world = Matrix.Translation((a + b) / 2) @ Matrix((sx, y, d)).transposed().to_4x4()
    return ob


def mirror_x(half):
    """A symmetric front profile from its right half, listed top to bottom."""
    return list(half) + [(-x, z) for x, z in reversed(half)]


def light_housing(name, center, axis, r):
    """A round light set in a housing (replication round three, Grimlock's chest lights)."""
    ax = Vector(axis).normalized()
    c = Vector(center)
    cyl(name + "_housing", "frame_dark", c - ax * 0.03, c + ax * 0.03, r, 12)
    cyl(name + "_lamp", "light", c, c + ax * 0.034, r * 0.62, 12)


def inlay(name, a, b, r=0.014):
    """A glowing strip tucked along a plate edge (replication round three, Grimlock's chest inlays)."""
    cyl(name, "light", a, b, r, 6)


def cyl(name, mat, a, b, radius, verts=10):
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=d.length, location=(a + b) / 2)
    ob = bpy.context.active_object
    ob.name = name
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return _finish(ob, mat)


# Gorilla model pass (2026-10-16; blind judges: "the gorilla's guns and joints should read as cylinders with a shine").
# Only the gorilla's own build rounds them; the creature factory imports this file as a kit and keeps the flat discs.
ROUND_JOINTS = os.environ.get("MECH_KIT_IMPORT") != "1"
# v76 (2026-10-19, after Codex's gorilla reference; Preston: "knuckles proportions were generated correctly so make sure
# theres five and it looks right on the model"): each fist a big back-of-hand block over a row of five grey segments and
# five chunky orange knuckle blocks on the ground (no thumb, no knuckle spikes, no curled three-segment fingers), and
# the black hubs on the fists and shoulders become layered light-grey wheels. APE_V76=0 builds v71.
V76 = os.environ.get("APE_V76", "1") == "1"
# v77 (2026-10-19, the rest of Codex's gorilla; Preston: "go"): the ballast blocks in a row along the spine (Codex's
# rack along the top) instead of across the back, the throwing arm gone with them; one big grey forward cannon on the
# right of the back in place of the shoulder gatling; the rear stretched STRETCH m and lowered up to REAR_DROP m
# (Codex's sprite is 1.47 times as wide as tall against our 1.25, its rump lower than the shoulders); hind legs HT times
# thicker with a layered grey ankle wheel, as the fists'. APE_V77=0 builds v76.
V77 = V76 and os.environ.get("APE_V77", "1") == "1"
STRETCH, REAR_DROP = (0.3, 0.2) if V77 else (0.0, 0.0)
HT = 1.3 if V77 else 1.0
# v77b: the haymaker's lean back pivots the body about its middle and the grounding then stands the hind feet on the
# floor; with the hind feet 0.3 m further back the same 12 degrees lifted the whole leap about 9 cm (the fist 3 sprite rows
# higher at 320x180). The lean scaled by the lever (about 1.24 against 1.54 m) and the hop 2 cm lower keep v76's apex.
LEAN, AIR = (0.8, 0.10) if V77 else (1.0, 0.12)
# v78 (2026-10-20, factory pass part by part against Codex's sprite; Preston: "go gorilla next"): its back cannon is a
# light grey barrel with dark bands (ours one dark bar), its hind haunch is broken into plates (ours a big flat pale
# face: the near thigh armour, 3359 render px, lit by the camera; v77 made it 1.3x thicker), its visor a thicker teal
# band. A light-steel barrel with two dark bands, a framed plate on each thigh's outer face, the visor 7 to 10 cm tall.
# Synthesis, Legacy's Iron Kong (docs/art/reference/legacy/iron_kong.png, structure only): its hind legs read as separate
# columns because they are a step darker than the body with a highlight only on top edges; the thigh and shin armour in
# the darker green (trim 3e5a33) under the lighter framed plate.
# (Its hind legs reach further back: a stance change, not this pass.) APE_V78=0 builds v77.
V78 = V77 and os.environ.get("APE_V78", "1") == "1"
# v79 (2026-10-20, Codex's v77 audit: "a loose grey disc below the falling rear leg" in the death frames). The disc was
# v77's ankle wheel: two of its pieces took the ankle disc's names, Blender renamed them ".001", and the bone rule read
# neither; now "ankle_wheel_<side>_<n>" on the shin, so the wheel follows the leg. Also the knee seam
# ring was named "knee_<side>_seam", which the bone rule cannot read (text after the side), so it rode the body bone and
# stayed behind when the leg fell; the bind audit treats the body as the catch-all and never flagged it. The bone rule now
# strips "_seam" as it strips "_ring" and "_hub", so it rides the shin with the knee disc. (A first try renamed it
# "knee_<side>_1": the detail pass skips names with "seam", so the ring became a greeble host and shifted the pass's
# panel/vent/layer cycle over the whole model, 232 fewer triangles and every frame changed.) APE_V79=0 builds v78.
V79 = V78 and os.environ.get("APE_V79", "1") == "1"


def round_rim(ob, offset, segments=3):
    """Round the outer (+z) cap rim of a kit cylinder, so it catches a light crescent on top and a dark one below."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    top = max(v.co.z for v in bm.verts)
    rim = [e for e in bm.edges if all(abs(v.co.z - top) < 1e-5 for v in e.verts)]
    bmesh.ops.bevel(bm, geom=rim, offset=offset, offset_type="OFFSET", segments=segments, profile=0.5, affect="EDGES")
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def disc(name, center, radius, axis=(1, 0, 0), depth=0.12):
    """A round joint like Preston's sprite: a grey disc, an orange ring, a dark hub."""
    c, ax = Vector(center), Vector(axis).normalized()
    if c.x < 0 and ax.x > 0:
        ax = -ax   # discs face outward on the right side too
    if ROUND_JOINTS:
        # 16 sides and rounded rims on the disc and the hub instead of three flat 10-sided plates (model pass 1)
        # pass 2: a light steel face against the dark hub, so the joint reads as a bright ring at sprite size
        round_rim(cyl(name, "steel", c - ax * depth / 2, c + ax * depth / 2, radius, 16), min(depth * 0.7, radius * 0.26))
        cyl(name + "_ring", "accent", c + ax * (depth / 2 - 0.01), c + ax * (depth / 2 + 0.025), radius * 0.66, 16)
        round_rim(cyl(name + "_hub", "frame_dark", c + ax * depth / 2, c + ax * (depth / 2 + 0.065), radius * 0.42, 12),
                  min(0.05, radius * 0.17))
        return
    cyl(name, "frame", c - ax * depth / 2, c + ax * depth / 2, radius, 10)
    cyl(name + "_ring", "accent", c + ax * depth / 2, c + ax * (depth / 2 + 0.025), radius * 0.72, 10)
    # pass 35 (Preston: less Fall of Cybertron): no glow ring; a plain bolt head like his master's discs
    cyl(name + "_hub", "frame_dark", c + ax * depth / 2, c + ax * (depth / 2 + 0.05), radius * 0.42, 8)


def limb_shells(name, mat, a, b, width, depth, count, crease=0.5, bulge=1.0):
    """A limb as a stack of overlapping shells from a to b, slightly bigger in the middle (muscle)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    seg = d.length / count
    for k in range(count):
        t = (k + 0.5) / count
        swell = 1.0 + (bulge - 1.0) * (1.0 - abs(t - 0.5) * 2.0)
        ob = shell("%s_%d" % (name, k), mat, a + d * t, (width * swell, depth * swell, seg * 1.22), crease=crease,
                   squash=(1.0, 0.84))
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = q


def limb(name, mat, a, b, w0, d0, w1, d1, bulge=1.0, rings=4, levels=0):
    """One continuous armoured limb from a to b: eight-sided rings (a chamfered box section), width going w0 -> w1
    and depth d0 -> d1, swelling by `bulge` in the middle, ends capped. Faceted and light, like finished low-poly
    mechs, instead of a stack of boxes. The ends sink into the joints (overlap hides the seam)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    length = d.length
    bm = bmesh.new()
    loops = []
    for i in range(rings):
        t = i / (rings - 1)
        sw = 1.0 + (bulge - 1.0) * math.sin(math.pi * t)
        w = (w0 + (w1 - w0) * t) * sw / 2
        dd = (d0 + (d1 - d0) * t) * sw / 2
        z = -length / 2 + length * t
        c = 0.38   # how much the box corners are cut
        pts = [(w, dd * (1 - c)), (w * (1 - c), dd), (-w * (1 - c), dd), (-w, dd * (1 - c)),
               (-w, -dd * (1 - c)), (-w * (1 - c), -dd), (w * (1 - c), -dd), (w, -dd * (1 - c))]
        loops.append([bm.verts.new((x, y, z)) for x, y in pts])
    for i in range(rings - 1):
        for j in range(8):
            bm.faces.new((loops[i][j], loops[i][(j + 1) % 8], loops[i + 1][(j + 1) % 8], loops[i + 1][j]))
    caps = [bm.faces.new(list(reversed(loops[0]))), bm.faces.new(loops[-1])]
    bmesh.ops.inset_individual(bm, faces=caps, thickness=min(w0, d0, w1, d1) * 0.2, depth=0)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    ob.location = (a + b) / 2
    if levels > 0:
        mod = ob.modifiers.new("subd", "SUBSURF")
        mod.levels = levels
        mod.render_levels = levels
    return _finish(ob, mat)


JOINTS = {}   # rig joint positions, recorded by build()


def build():
    """Layout read from Preston's three sprite views (side, rear three-quarter, back), 2026-10-11. Pass 4: armour is
    many smaller rounded plates over dark cores so dark seams show between them, like the sprite; the crest is
    shingled rounded plates; hind legs splay; fists and toes are chunkier; more grey discs and machinery show."""
    lean = -12
    # Built the Fall of Cybertron way (2026-10-11, pass 11): grey machinery underneath, armour as thin plates with real
    # thickness and crisp bevels layered over it, gaps between plates where the frame shows. Layout stays the sprite's.
    # Frame and machinery
    # The torso as one sculpted mass (pass 16, the profile-solid lesson from Grimlock's head): side outline hunched high
    # at the shoulders and sloping to the rump, front outline broad and rounded, top outline narrowing to the rump.
    # pass 26 (2D pivot): rump lowered so the back slopes harder from the shoulders, the hunch of Preston's sprites
    torso_side = [(-1.19, 1.05), (-1.22, 1.6),   # pass 38: chest 0.14 deeper
                   (-0.95, 1.95), (-0.6, 2.12), (-0.1, 2.06), (0.35, 1.86), (0.75, 1.56),
                  (1.0, 1.3), (1.02, 1.12), (0.85, 1.0), (0.2, 0.95), (-0.6, 0.98)]
    torso_front = mirror_x([(0.28, 2.14), (0.48, 2.02), (0.58, 1.75), (0.58, 1.35), (0.5, 1.06), (0.3, 0.96)])
    torso_top = [(-0.6, -1.12), (0.6, -1.12), (0.6, -0.3), (0.5, 0.6), (0.4, 1.06), (-0.4, 1.06), (-0.5, 0.6), (-0.6, -0.3)]
    profile_solid("torso_shell", "main", (0, 0, 0), torso_side, torso_front, chamfer=0.02, top_xy=torso_top)
    shell("chest_frame", "frame", (0, -0.98, 1.4), (0.9, 0.36, 0.6), (lean, 0, 0), 0.7, levels=1)   # pass 50 (Preston: "get rid of grey"): 14 cm back, behind the armour; its front at y -1.30 stood proud of the tucked shield
    shell("neck_core", "frame_dark", (0, -1.24, 1.66), (0.56, 0.52, 0.42), (lean, 0, 0), 0.6, levels=1)
    for k in range(3):   # neck cables from the chest up into the head
        cyl("neck_cable_%d" % k, "frame", ((k - 1) * 0.14, -1.0, 1.6), ((k - 1) * 0.12, -1.36, 1.74), 0.045, 8)
    # Back armour: framed plates laid over the torso's top, shingled front to back
    for k, (y, z, w, tilt) in enumerate([(-0.62, 2.17, 0.92, -80), (-0.1, 2.13, 0.88, -88), (0.38, 1.97, 0.8, -100),
                                         (0.78, 1.72, 0.68, -112)]):
        plate("back_plate_%d" % k, "main", (0, y, z), w, 0.44, 0.06, (lean + tilt, 0, 0), bend=0.8, recess=0.02, rim=0.06)
    plate("rump_plate", "trim", (0, 1.06, 1.2), 0.66, 0.36, 0.06, (-8, 0, 180), bend=0.35, recess=0.02, rim=0.05)
    # Weapons (2026-10-12): Ballast Throw. A throwing arm on the rack: a grey rail along the spine behind the blocks,
    # a pivot drum at its base and an orange claw folded over the rearmost block.
    if not V77:   # v77: the blocks run along the spine now; the arm sat where they are
        cyl("ballast_rail", "frame", (0, 0.3, 2.0), (0, 0.68, 1.97), 0.06, 8)   # pass 35: shorter, inside the silhouette
        cyl("ballast_pivot", "frame_dark", (-0.1, 0.68, 1.97), (0.1, 0.68, 1.97), 0.08, 12)
        for sd in (-1, 1):
            segment("ballast_claw_%d" % sd, "accent", (sd * 0.1, 0.1, 2.04), (sd * 0.22, -0.1, 2.16), 0.07, 0.07, 0.4)
        shell("ballast_clawbase", "accent", (0, 0.12, 2.04), (0.3, 0.14, 0.1), (0, 0, 0), 0.5, levels=1)
    shell("rump_slot", "frame_dark", (0, 1.08, 1.22), (0.3, 0.04, 0.06), (lean, 0, 0), 0.6, levels=1)
    # Chest in bands, learned from Grimlock's chest: an upper framed band, a dark band with three round teal lights,
    # the big orange framed shield below with glowing inlays along its bottom edges
    plate("chest_upper", "accent", (0, -1.26, 1.63), 1.0, 0.14, 0.08, (lean + 24, 0, 0), bend=0.9, recess=0.015, rim=0.03)   # pass 47 (Preston: the top plate at the collar hangs too): tucked +12 deg and flush, as the shield in pass 46
    shell("chest_band", "frame_dark", (0, -1.21, 1.555), (0.8, 0.1, 0.1), (lean + 24, 0, 0), 0.6, levels=1)   # pass 49: back with the tucked collar band (it stood 4 cm proud of it in v56)
    for k in range(3):
        light_housing("chest_light_%d" % k, ((k - 1) * 0.22, -1.27, 1.555), (0, -1, 0), 0.045)   # pass 49: with the band
    # pass 46 (Preston, 2026-10-13: the orange chest armour "looks like its hanging off in front rather than tightly folding
    # against its chest... grab it from behind and bring it to the chest"): the shield was tipped -18 deg, which swings its
    # bottom edge forward; +12 tucks it back, and it sits flush on the chest front (torso front y -1.22) instead of 14 cm off it
    plate("chest_shield", "accent", (0, -1.28, 1.36), 0.8, 0.76, 0.1, (lean + 24, 0, 0), bend=0.8, taper=1.6,   # pass 50: taller, up to the collar band where the grey frame showed (Preston: the orange "where grey plate is")
          recess=0.025, rim=0.06)
    for s in (-1, 1):
        inlay("chest_inlay_%d" % s, (s * 0.06, -1.22, 1.0), (s * 0.3, -1.2, 1.04))   # pass 46: follows the tucked shield
        # pass 38: orange plates wrapping round the chest, angled out and forward, so the chest shows in profile as in
        # Preston's side sprite (the shoulder pod hid the front shield from the side)
        plate("chest_side_%d" % s, "accent", (s * 0.46, -1.24, 1.38), 0.46, 0.6, 0.08, (lean + 20, 0, s * 40), bend=0.4,   # pass 48: tucked at the bottom but 40 deg (30 hid the orange in profile and bared the grey frame in front; 55 hung like flaps)
              recess=0.012, rim=0.03)
        # pass 41: the orange runs on down the front of the body below it, as in Preston's side sprite (his chest plate
        # covers the front from chin to belly; ours stopped at the arm)
        plate("belly_side_%d" % s, "accent", (s * 0.38, -1.12, 1.06), 0.38, 0.34, 0.08, (lean + 26, 0, s * 32), bend=0.4,   # pass 46: up, in and tucked under (hung low and splayed in the front views)
              recess=0.012, rim=0.03)
    for s in (-1, 1):
        side = "L" if s > 0 else "R"
        for k, (y, z) in enumerate([(-0.42, 1.4), (0.3, 1.3)]):   # big enough to cover the torso's sides
            plate("flank_plate_%d_%d" % (s, k), "main", (s * 0.6, y, z), 0.9, 0.7, 0.08, (lean, 0, s * 90), bend=0.35,
                  recess=0.02, rim=0.06)
        inlay("flank_inlay_%d" % s, (s * 0.64, -0.82, 1.05), (s * 0.64, 0.66, 0.95))
        disc("flank_disc_%d" % s, (s * 0.62, -0.04, 1.28), 0.12)
        cyl("belly_piston_%d" % s, "frame", (s * 0.42, -0.6, 1.05), (s * 0.5, 0.45, 1.0), 0.06, 8)
        # Shoulders: a grey core under a pauldron of three plates (top, outer, front) and a raised cap
        c = Vector((s * 0.84, -0.6, 1.6))
        shell("shoulder_core_%d" % s, "frame", c, (0.62, 0.7, 0.6), (lean, 0, 0), 0.6, levels=1)
        plate("shoulder_top_%d" % s, "main", c + Vector((0, 0, 0.36)), 0.9, 0.92, 0.09, (lean - 90, 0, s * 8), bend=0.5,
              recess=0.02, rim=0.07)
        # the outer shoulder: a rounded barrel pod with a segmented glow ring and a raised hub, rebuilt from Grimlock's
        # shoulder pod in the replication exercise
        pod_axis = Vector((s, 0, -0.25)).normalized()
        pod_c = c + Vector((s * 0.2, 0, 0.06))   # pass 28: in and up, higher narrower shoulders (front view measure)
        drum("shoulder_outer_%d" % s, "main", pod_c, pod_axis, 0.42, 0.5)
        pod_face = pod_c + pod_axis * 0.25
        cyl("shoulder_podring_%d" % s, "frame" if V76 else "frame_dark", pod_face - pod_axis * 0.01, pod_face + pod_axis * 0.025, 0.24, 16)   # Mechabeast V2 pass (2026-10-14): a black hub as his   # pass 35: a plain disc, not a segmented glow pod
        cyl("shoulder_podhub_%d" % s, "frame", pod_face - pod_axis * 0.02, pod_face + pod_axis * 0.03, 0.15, 16)
        cyl("shoulder_podcap_%d" % s, "steel" if V76 else "frame_dark", pod_face + pod_axis * 0.03, pod_face + pod_axis * 0.05, 0.08, 12)
        plate("shoulder_front_%d" % s, "main", c + Vector((0, -0.44, -0.02)), 0.78, 0.6, 0.08, (lean, 0, 0), bend=0.35)
        plate("shoulder_cap_%d" % s, "trim", c + Vector((s * 0.02, 0.02, 0.45)), 0.52, 0.56, 0.06, (lean - 90, 0, s * 8), bend=0.4)
        disc("neck_joint_%d" % s, (s * 0.46, -0.9, 1.72), 0.14)
        # Arms: a grey strut in each segment wrapped by outer, front and back plates
        sh, el, wr = (s * 0.98, -0.76, 1.32), (s * 1.3, -0.96, 0.92), (s * 1.22, -1.1, 0.45)   # V2 pass (2026-10-14): elbows bowed out, his arms arch from the shoulder to the fist (was 1.1)
        JOINTS["shoulder." + side], JOINTS["elbow." + side], JOINTS["wrist." + side] = sh, el, wr
        JOINTS["knuckle." + side] = (s * 1.24, -1.22, 0.1)   # pass 31: the hand points down, under the wrist
        cyl("upper_frame_%d" % s, "frame", sh, el, 0.17, 8)
        limb_solid("upper_armor_%d" % s, "main", sh, el, (s, 0, 0), [(0, 0.26, 0.26), (0.4, 0.39, 0.286), (1, 0.286, 0.234)],   # pass 34: 30% thicker (side view: limbs too thin under the torso)
                   [(0, 0.3), (0.5, 0.32), (1, 0.26)],
                   grooves=[((gx, -0.295, -0.03), (gx, -0.226, 0.22), (0, -0.96, 0.27)) for gx in (-0.12, 0.12)])
        inlay("upperslit_%d" % s, Vector(sh).lerp(Vector(el), 0.3) + Vector((s * 0.3, -0.06, 0)),
              Vector(sh).lerp(Vector(el), 0.7) + Vector((s * 0.27, -0.06, 0)), r=0.018)
        disc("elbow_%d" % s, el, 0.16, depth=0.58)   # pass 36
        cyl("fore_frame_%d" % s, "frame", el, wr, 0.18, 8)
        limb_solid("fore_armor_%d" % s, "main", el, wr, (s, 0, 0), [(0, 0.325, 0.286), (0.6, 0.52, 0.39), (1, 0.481, 0.351)],   # pass 34: 30% thicker (side view: limbs too thin under the torso)
                   [(0, 0.26), (0.7, 0.34), (1, 0.32)],
                   grooves=[((gx, -0.32, 0.06), (gx, -0.30, 0.23), (0, -1, 0.1)) for gx in (-0.12, 0.12)])
        # Twin hydraulic cylinders on the back of the forearm (pass 23): the gorilla's forearm muscle as machinery,
        # the exposed actuation layer the Horizon machines show between their plates. They ride the forearm bone.
        fd = Vector(wr) - Vector(el)
        fl = fd.length
        fd.normalize()
        back = Vector((0, 1, 0))
        back = (back - fd * back.dot(fd)).normalized()
        def on_back(t, dx):   # a point at fraction t along the forearm, on its back face (half-width 0.26 to 0.33)
            return Vector(el) + fd * (fl * t) + back * (0.27 + 0.09 * t) + Vector((s * dx, 0, 0))
        for k, dx in enumerate((-0.09, 0.09)):
            cyl("fore_piston_%d_%d" % (s, k), "frame", on_back(0.15, dx), on_back(0.55, dx), 0.045, 10)
            cyl("fore_rod_%d_%d" % (s, k), "frame_dark", on_back(0.5, dx), on_back(0.9, dx), 0.028, 8)
        for k in range(2):   # round teal lights in a row on the forearm's outer face, like Grimlock's leg lights
            light_housing("forelight_%d_%d" % (s, k), Vector(el).lerp(Vector(wr), 0.38 + 0.3 * k) + Vector((s * 0.31, 0, 0)),
                          (s, 0, 0), 0.06)
        disc("wrist_%d" % s, wr, 0.15, depth=0.6)
        # Fists, rebuilt from Grimlock's hand (replication round five): a back-of-hand block with a rounded top, and
        # fingers of three tapering segments each, curled for knuckle-walking (forward and down, then tucked under),
        # with grey knuckle barrels at the joints and a three-segment thumb.
        # Pass 31: columnar, as real gorillas stand (research 2026-10-12): the hand straight under the forearm, palm
        # facing back; from the knuckle row the fingers drop straight down, the middle segments lie on the ground
        # carrying the weight, the fingertips curl up into the palm; the outer finger is held off the ground.
        hand_before = set(bpy.context.scene.objects)
        shell("fist_%d" % s, "accent", (s * 1.24, -1.16, 0.38), (0.62, 0.36, 0.44), (0, 0, 0), 0.35)   # pass 41: a squarer, bigger block (Preston's second reference)
        if V76:   # v76: a layered light-grey wheel on the fist's outer side: grey rim, light steel ring, grey hub, light cap
            cyl("fist_%d_ring" % s, "frame", (s * 1.53, -1.16, 0.4), (s * 1.58, -1.16, 0.4), 0.15, 20)
            cyl("fist_%d_ring_2" % s, "steel", (s * 1.57, -1.16, 0.4), (s * 1.6, -1.16, 0.4), 0.11, 20)
            cyl("fist_%d_hub" % s, "frame", (s * 1.59, -1.16, 0.4), (s * 1.62, -1.16, 0.4), 0.065, 16)
            cyl("fist_%d_hub_2" % s, "steel", (s * 1.61, -1.16, 0.4), (s * 1.63, -1.16, 0.4), 0.03, 12)
            # five knuckles across the fist's 0.62 m: a grey segment under the hand block, an orange knuckle block on
            # the ground in front of it, each a separate piece with a gap so the five read at sprite size
            for k in range(5):
                x = s * 1.24 + (k - 2) * 0.124
                shell("knucklecap_%d_%d" % (s, k), "frame", (x, -1.33, 0.185), (0.11, 0.12, 0.095), (0, 0, 0), 0.35, levels=1)   # v76b: forward, a grey band between the hand and the knuckles as his
                shell("finger_%d_%d" % (s, k), "accent", (x, -1.31, 0.075), (0.112, 0.2, 0.13), (0, 0, 0), 0.4, levels=1)
        cyl("fist_%d_ring" % s, "frame_dark", (s * 1.53, -1.16, 0.4), (s * 1.58, -1.16, 0.4), 0.12, 16) if not V76 else None   # V2 pass: a black hub on the fist's outer side, as his
        cyl("fist_%d_hub" % s, "frame", (s * 1.56, -1.16, 0.4), (s * 1.6, -1.16, 0.4), 0.06, 12) if not V76 else None
        for k in (range(4) if not V76 else ()):
            x = s * 1.24 + (k - 1.5) * 0.15
            lift = 0.05 if k == (3 if s > 0 else 0) else 0.0
            j1, j2, j3, j4 = (x, -1.28, 0.24 + lift), (x, -1.3, 0.09 + lift), (x, -1.1, 0.07 + lift), (x, -1.08, 0.18 + lift)
            for n, (a_, b_, w, h) in enumerate([(j1, j2, 0.13, 0.13), (j2, j3, 0.125, 0.12), (j3, j4, 0.11, 0.1)]):
                segment("finger_%d_%d" % (s, k * 3 + n), "accent", a_, b_, w, h, 0.45)
            for n, j in enumerate((j1, j2)):
                cyl("knucklecap_%d_%d" % (s, k * 2 + n), "frame_dark", Vector(j) - Vector((0.065, 0, 0)), Vector(j) + Vector((0.065, 0, 0)), 0.075, 10)   # V2 pass: black rollers between the orange knuckles, as his
        t1, t2, t3, t4 = (s * 1.0, -1.16, 0.4), (s * 0.98, -1.28, 0.3), (s * 1.0, -1.32, 0.18), (s * 1.04, -1.26, 0.12)
        for n, (a_, b_, w, h) in enumerate([(t1, t2, 0.13, 0.13), (t2, t3, 0.12, 0.12), (t3, t4, 0.1, 0.1)] if not V76 else []):
            segment("thumb_%d_%d" % (s, n), "accent", a_, b_, w, h, 0.45)
        plate("handplate_%d" % s, "accent", (s * 1.24, -1.33, 0.36), 0.56, 0.34, 0.06, (-5, 0, 0), bend=0.4,
              recess=0.02, rim=0.05)   # framed armour on the back of the hand, like Grimlock's wrist plate
        if not V76:   # v76: the knuckle row is the guard now
            shell("knuckle_guard_%d" % s, "accent", (s * 1.24, -1.34, 0.16), (0.62, 0.08, 0.1), (0, 0, 0), 0.6, levels=1)
        # Pass 36 (Preston: "bigger hands, its knuckles look thin compared to arm" after the forearms went 30% thicker):
        # the whole hand 1.35 times larger about its base, so the knuckles stay on the ground.
        HAND_GROW, hand_base = 1.9, Vector((s * 1.24, -1.2, 0.05))   # ref-4 part pass (2026-10-13): 1.9, his fists stand bigger in the SE view; pass 45 (part pass): 1.7, fists region 0.605 to 0.630; pass 41 had 1.35 to 1.5
        for o in set(bpy.context.scene.objects) - hand_before:
            o.location = hand_base + (o.location - hand_base) * HAND_GROW
            o.scale = tuple(v * HAND_GROW for v in o.scale)
        # Weapons (2026-10-12): Piston Knuckles. A hydraulic accumulator tank on the back of each upper arm, feeding the
        # fist through a line down the forearm; a row of four orange knuckle spikes on each fist's leading face.
        tank_a, tank_b = Vector(sh) + Vector((s * 0.1, 0.22, -0.06)), Vector(el) + Vector((s * 0.06, 0.2, 0.1))
        cyl("upper_tank_%d" % s, "frame_dark", tank_a, tank_b, 0.13, 12)
        cyl("upper_tankcap_%d_0" % s, "accent", tank_a - (tank_b - tank_a).normalized() * 0.03, tank_a, 0.1, 12)
        cyl("upper_tankcap_%d_1" % s, "accent", tank_b, tank_b + (tank_b - tank_a).normalized() * 0.03, 0.1, 12)
        cyl("fist_line_%d" % s, "frame_dark", Vector(el) + Vector((s * 0.14, 0.12, 0.0)), Vector(wr) + Vector((s * 0.12, 0.08, 0.1)), 0.04, 8)
        for k in (range(4) if not V76 else ()):   # v76: no spikes, Codex's fists have clean knuckles
            x = s * 1.24 + (k - 1.5) * 0.14
            segment("knuckle_spike_%d_%d" % (s, k), "accent", Vector((x, -1.4, 0.14)), Vector((x, -1.58, 0.1)), 0.09, 0.09, 0.4)
        # Hind legs: splayed, short and bent; plated struts, a disc knee, a green foot with orange claws
        hind_before = set(bpy.context.scene.objects)
        hp, kn, an = (s * 0.66, 0.62, 1.02), (s * 0.84, 0.76, 0.55), (s * 0.86, 0.88, 0.2)
        JOINTS["hip." + side], JOINTS["knee." + side], JOINTS["ankle." + side] = hp, kn, an
        JOINTS["toe." + side] = (s * 0.9, 0.46, 0.08)
        disc("hip_joint_%d" % s, (s * 0.92, 0.62, 1.04), 0.18)   # pass 36: smaller bolt, as the master's
        cyl("hip_piston_%d" % s, "frame", (s * 0.5, 0.3, 1.2), (s * 0.78, 0.74, 0.62), 0.05, 8)
        cyl("thigh_frame_%d" % s, "frame", hp, kn, 0.2 * HT, 8)
        limb_solid("thigh_armor_%d" % s, "trim" if V78 else "main", hp, kn, (s, 0, 0), [(t, w * HT, d * HT) for t, w, d in ((0, 0.39, 0.338), (0.4, 0.442, 0.364), (1, 0.312, 0.26))],   # pass 34: 30% thicker (side view: limbs too thin under the torso)
                   [(t, w * HT) for t, w in ((0, 0.3), (0.5, 0.32), (1, 0.24))],
                   grooves=[((gx, -0.333, -0.03), (gx, -0.247, 0.24), (0, -0.95, 0.3)) for gx in (-0.12, 0.12)])
        if V78:   # a framed plate on the thigh's outer face, so seams break the big lit face (Codex's haunch plates)
            bpy.context.view_layer.update()
            plate_on(bpy.data.objects["thigh_armor_%d" % s], "thigh_plate_%d" % s, "main", Vector(hp).lerp(Vector(kn), 0.42),
                     (s, 0, 0), 0.44 * HT, 0.5, 0.05, standoff=0.015, up=tuple(Vector(hp) - Vector(kn)), bend=0.3,
                     recess=0.02, rim=0.05)
        disc("knee_%d" % s, kn, 0.21, depth=0.6)   # pass 42: the reference's knee discs are the biggest joints on it (pass 36 had 0.16)
        cyl("knee_%d_seam" % s, "frame_dark", Vector(kn) + Vector((0, 0, 0.19)), Vector(kn) + Vector((0, 0, 0.23)), 0.3, 12)   # pass 42: a dark seam between thigh and shin
        cyl("shin_core_%d" % s, "frame", kn, an, 0.17 * HT, 8)
        limb_solid("shin_armor_%d" % s, "trim" if V78 else "main", kn, an, (0, -1, 0), [(t, w * HT, d * HT) for t, w, d in ((0, 0.26, 0.208), (1, 0.312, 0.234))], [(t, w * HT) for t, w in ((0, 0.2), (1, 0.24))],   # pass 34: 30% thicker (side view: limbs too thin under the torso)
                   grooves=[((gx, -0.205, -0.14), (gx, -0.235, 0.14), (0, -0.99, -0.11)) for gx in (-0.09, 0.09)])
        # Feet (pass 24): a sculpted foot solid rising to the ankle hump (the profile-solid lesson), three toes of two
        # tapering segments with knuckle caps (the fingers' construction, from Grimlock's hand), a dark heel pad, an
        # ankle disc and a heel piston down from behind the shin (the Horizon legs' exposed tendon cylinder).
        foot_side = [(-0.3, 0.02), (-0.3, 0.12), (-0.12, 0.26), (0.14, 0.3), (0.3, 0.24), (0.36, 0.1), (0.3, 0.02)]
        foot_front = mirror_x([(0.14, 0.3), (0.25, 0.2), (0.26, 0.02)])
        foot = profile_solid("foot_%d" % s, "main", (0, 0, 0), foot_side, foot_front, chamfer=0.012)
        foot.matrix_world = Matrix.Translation((s * 0.88, 0.74, 0.0)) @ Matrix.Rotation(math.radians(s * -10), 4, "Z")
        for k in range(3):
            x = s * 0.9 + (k - 1) * 0.19
            j1, j2, j3 = (x, 0.46, 0.13), (x, 0.28, 0.1), (x, 0.1, 0.06)
            segment("toe_%d_%d" % (s, k * 2), "accent", j1, j2, 0.17, 0.15, 0.45)
            segment("toe_%d_%d" % (s, k * 2 + 1), "accent", j2, j3, 0.15, 0.12, 0.45)
            cyl("toecap_%d_%d" % (s, k), "frame", Vector(j2) - Vector((0.085, 0, 0)), Vector(j2) + Vector((0.085, 0, 0)), 0.07, 10)
        # Pass 25: the heel block is orange again, as in the sprite's rear view (pass 24's dark pad cost 2 points of orange)
        shell("heel_%d" % s, "accent", (s * 0.86, 1.12, 0.08), (0.3, 0.16, 0.14), (0, 0, 0), 0.5, levels=1)
        disc("ankle_%d" % s, an, 0.14, depth=0.5)
        if V77:   # v77: a layered light-grey wheel on the ankle's outer face, as the fists' (Codex's hind leg)
            ax = an[0] + s * 0.32   # HIND_IN below pulls each piece's centre in by 0.8, not the disc's depth: 0.32 clears the ankle disc's face
            for i, (nm, mat, x0, x1, r) in enumerate((("ring", "frame", 0.0, 0.05, 0.2), ("ring_2", "steel", 0.04, 0.07, 0.15),
                                                      ("hub", "frame", 0.06, 0.09, 0.085), ("hub_2", "steel", 0.08, 0.1, 0.04))):
                # v79: own names on the shin; "ankle_<side>_ring"/"_hub" were the ankle disc's, so Blender renamed these
                # ".001" and the bone rule dropped them to the body (Codex's loose disc in the death frames)
                cyl(("ankle_wheel_%d_%d" % (s, i + 1)) if V79 else ("ankle_%d_%s" % (s, nm)), mat, (ax + s * x0 * 1.25, an[1], an[2]), (ax + s * x1 * 1.25, an[1], an[2]), r, 20)
        cyl("heel_piston_%d" % s, "frame", (s * 0.8, 0.96, 0.5), (s * 0.84, 1.08, 0.16), 0.04, 8)
        cyl("heel_rod_%d" % s, "frame_dark", (s * 0.82, 1.02, 0.33), (s * 0.85, 1.1, 0.1), 0.025, 8)
        # Pass 27: Preston, "the rear legs should connect to the rear more". The whole hind leg moves back so the hip
        # sits inside the rump instead of under the middle of the body; joints move with it so the rig follows.
        # Pass 28: and pulled in under the body (the back view's stance was 0.80 of the height wide, Preston's 0.35)
        HIND_BACK, HIND_IN = 0.36, 0.8   # ref-4 part pass (2026-10-13): 14 cm further back, his hind toes reach past ours (hind region 0.788); pass 27 had 0.22
        for o in set(bpy.context.scene.objects) - hind_before:
            o.location.y += HIND_BACK
            o.location.x *= HIND_IN
        for j in ("hip.", "knee.", "ankle.", "toe."):
            x, y, z = JOINTS[j + side]
            JOINTS[j + side] = (x * HIND_IN, y + HIND_BACK, z)
    # Pelvis (pass 30). Preston: "from the rear it doesn't look like there's a pelvis." Real gorilla (research,
    # docs/reference/gorilla-posture-2026-10-12.md): a long, narrow pelvis with tall, narrow ilium blades, the hip
    # joints at the back end of the body. Built as a grey frame beam between the hip joints, a sacrum block at the
    # base of the spine, a tall narrow green blade rising from each hip toward the spine, and a rump plate over it.
    cyl("pelvis_beam", "frame", (-0.72, 0.84, 1.04), (0.72, 0.84, 1.04), 0.11, 10)
    shell("sacrum", "frame", (0, 1.0, 1.2), (0.46, 0.3, 0.5), (0, 0, 0), 0.6, levels=1)
    for s in (-1, 1):
        limb_solid("ilium_%d" % s, "main", (s * 0.6, 0.86, 1.04), (s * 0.24, 1.02, 1.52), (s, 0, 0),
                   [(0, 0.16, 0.14), (0.5, 0.14, 0.12), (1, 0.1, 0.1)], [(0, 0.3), (0.5, 0.34), (1, 0.22)])
    plate("rump_plate", "main", (0, 1.1, 1.36), 0.6, 0.42, 0.07, (25, 0, 0), bend=0.5, recess=0.012, rim=0.04)
    head_before = set(bpy.context.scene.objects)
    # Head, sculpted as one piece (2026-10-11, pass 14, from the replication exercise on Grimlock's head): profiles
    # drawn from Preston's sprite. Side: a crest dome rising at the back, a brow ridge jutting over the eyes, a flat
    # face, the muzzle jutting forward and down, the jaw sweeping back to the throat. Front: a narrow crest top
    # widening to brow and cheeks, tapering to the jaw. Green helmet and grey face are two profile solids.
    hc = (0, -1.2, 2.08)
    H = Vector(hc)
    # Pass 22, the head as a mechanical skull (how the Horizon machines and Grimlock are built: a shell over a dark
    # skull, a separate hinged jaw with its actuators showing, lens eyes in sockets). The green cranium is now the
    # brow and dome only, with dark panel lines cut along its sides; below it the nose, lip and a separate lower jaw
    # are grey over a dark muzzle core, with hinge discs and jaw pistons at the cheeks.
    # Pass 31 (Preston: "still a bulky robot monkey head; make it a mech gorilla head"). A gorilla's head is conical
    # from the sagittal crest (highest toward the back), with a continuous straight brow shelf over deep-set eyes
    # (Dian Fossey Gorilla Fund, SeaWorld, Smithsonian National Zoo; docs/reference/gorilla-posture-2026-10-12.md).
    # Side: brow shelf jutting forward, forehead sloping back and up to a crest peak behind the middle, steep drop
    # to the nape. Front: narrow at the crest, widest at brow and cheeks.
    # pass 32: the back of the head slopes into the back; the front ends in the brow shelf
    helmet_side = [(0.3, -0.14), (0.38, 0.1), (0.3, 0.36), (0.17, 0.55), (0.08, 0.59), (-0.05, 0.55), (-0.23, 0.44),
                   (-0.41, 0.31), (-0.55, 0.26), (-0.58, 0.15), (-0.45, 0.1), (-0.4, -0.04), (-0.3, -0.12), (-0.1, -0.26),
                   (0.1, -0.3)]
    # pass 32: narrow crest, widest at the brow, stops at cheek level so the face and jowls are the widest part below
    helmet_front = mirror_x([(0.0425, 0.59), (0.17, 0.54), (0.306, 0.45), (0.374, 0.31), (0.391, 0.16), (0.348, 0.0), (0.255, -0.12), (0.136, -0.18)])   # pass 39: 15% narrower (Preston's front view)
    # pass 37 (Preston: "I want it to look the same, colour-wise and design"): his sprites build the dome from two or
    # three chunky plates with dark lines between them; sliced here with the top outline, the skull showing in the gaps.
    dome = {}   # pass 40: six plates, each slice split into left and right halves (more plate lines, his front view)
    for k, (y0, y1) in enumerate(((-0.7, -0.17), (-0.15, 0.12), (0.14, 0.5))):
        for side, (x0, x1) in ((-1, (-0.6, -0.012)), (1, (0.012, 0.6))):
            dome[(k, side)] = profile_solid("helmet_%d_%s" % (k, "r" if side > 0 else "l"), "main", hc, helmet_side,
                                            helmet_front, chamfer=0.015, top_xy=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    helmet = dome[(1, 1)]
    profile_solid("crest_ridge", "trim", H + Vector((0, 0, 0.035)), helmet_side, mirror_x([(0.05, 0.75), (0.05, 0.3)]),
                  chamfer=0.01, top_xy=[(-0.1, -0.55), (0.1, -0.55), (0.1, 0.42), (-0.1, 0.42)])   # pass 39: sagittal crest
    for s in (-1, 1):   # a panel line along each side of the dome
        groove(dome[(1, s)], H + Vector((s * 0.38, -0.3, 0.1)), H + Vector((s * 0.38, 0.3, 0.1)), (s, 0, 0))   # on the narrower dome
    skull_side = [(0.25, -0.23), (0.3, 0.05), (0.25, 0.33), (0.15, 0.5), (0.07, 0.54), (-0.05, 0.5), (-0.22, 0.4),
                  (-0.4, 0.22), (-0.46, 0.12), (-0.46, 0.0), (-0.46, -0.22), (-0.34, -0.3), (-0.1, -0.31), (0.1, -0.28)]
    skull_front = mirror_x([(0.034, 0.54), (0.153, 0.5), (0.281, 0.41), (0.348, 0.28), (0.365, 0.14), (0.332, 0.0), (0.246, -0.25), (0.111, -0.31)])   # pass 39: 15% narrower (Preston's front view)
    profile_solid("skull", "face", hc, skull_side, skull_front, chamfer=0.01)   # pass 37: a mid-grey face, as in his sprites
    shell("muzzle_core", "frame_dark", H + Vector((0, -0.36, -0.12)), (0.36, 0.26, 0.24), (lean, 0, 0), 0.5, levels=1)
    # the snout: one sculpted grey mass under the eye band, rounded at the tip (the profile-solid lesson again),
    # with the nostrils cut into its front as dark grooves and the mouth line as the dark gap above the jaw
    muzzle_side = [(-0.3, -0.05), (-0.5, -0.05), (-0.56, -0.09), (-0.61, -0.16), (-0.59, -0.27), (-0.3, -0.29)]   # pass 40: longer
    muzzle_front = mirror_x([(0.204, -0.05), (0.264, -0.09), (0.281, -0.15), (0.246, -0.23)])   # pass 39: 15% narrower (Preston's front view)   # broad, flaring at the nostrils
    shell("nose_bridge", "face", H + Vector((0, -0.5, -0.12)), (0.09, 0.08, 0.08), (lean, 0, 0), 0.6, levels=1)   # 38b: below the visor   # pass 32: broad, flaring at the nostrils
    muzzle = profile_solid("muzzle", "face", hc, muzzle_side, muzzle_front, chamfer=0.012)
    for s in (-1, 1):
        groove(muzzle, H + Vector((s * 0.05, -0.59, -0.11)), H + Vector((s * 0.19, -0.59, -0.11)), (0, -0.894, 0.447),
               w=0.03, d=0.02)
    jaw_side = [(-0.21, 0.0), (-0.2, -0.1), (-0.13, -0.16), (0.05, -0.16), (0.16, -0.08), (0.18, 0.0)]   # pass 40: taller
    jaw_front = mirror_x([(0.238, 0.0), (0.23, -0.08), (0.153, -0.13)])   # pass 39: 15% narrower (Preston's front view)   # pass 32: a massive jaw
    profile_solid("jaw", "main", H + Vector((0, -0.36, -0.3)), jaw_side, jaw_front, chamfer=0.01)
    for s in (-1, 1):
        cyl("jaw_hinge_%d" % s, "frame", H + Vector((s * 0.19, -0.19, -0.28)), H + Vector((s * 0.25, -0.19, -0.28)), 0.06, 10)
        cyl("jaw_piston_%d" % s, "frame", H + Vector((s * 0.2, -0.12, -0.04)), H + Vector((s * 0.17, -0.34, -0.38)), 0.025, 8)
    if False: plate("crown", "main", H + Vector((0, -0.08, 0.5)), 0.4, 0.5, 0.03, (lean - 90, 0, 0), bend=0.5, recess=0.01, rim=0.04)
    if False: plate("nape", "main", H + Vector((0, 0.42, 0.2)), 0.5, 0.45, 0.06, (lean + 140, 0, 0), bend=0.6)
    # pass 31b: the crest fin read as a sail on top; the dome's own profile carries the sagittal crest now
    for k, (y, z, w, h, tilt) in enumerate([(-1.0, 2.55, 0.5, 0.3, -96), (-0.8, 2.42, 0.48, 0.3, -116)]):
        pass   # pass 32: the shingles stuck out of the new dome as shards; the dome's own profile is the crest
    for s in (-1, 1):
        shell("cheek_%d" % s, "trim", (s * 0.31, -1.42, 1.88), (0.16, 0.3, 0.32), (lean, 0, s * 12), 0.6, levels=1)
        plate("cheek_plate_%d" % s, "trim", (s * 0.36, -1.42, 1.87), 0.3, 0.3, 0.05, (lean - 5, 0, s * 40), bend=0.25,
              recess=0.012, rim=0.03)   # angular cheek armour over the jaw hinge
        pass   # pass 38: the two lens eyes became one visor line (below)
        pass   # pass 31: the two angled brows became one straight brow bar (below)
        # pass 37b: up and forward, clear of the shoulder pod in the side view
        cyl("ear_%d" % s, "frame", (s * 0.32, -1.26, 2.2), (s * 0.41, -1.26, 2.2), 0.15, 16)   # pass 37: a big ear disc
        cyl("ear_%d_hub" % s, "frame_dark", (s * 0.4, -1.26, 2.2), (s * 0.42, -1.26, 2.2), 0.1, 16)
        cyl("ear_%d_cap" % s, "frame", (s * 0.415, -1.26, 2.2), (s * 0.43, -1.26, 2.2), 0.045, 12)
    # pass 38 (Preston: "the face visor thing ... the eye one line across"): one dark visor band sunk across the face
    # under the brow shelf, one teal line across it, run just past the skull sides so the line shows in profile
    shell("socket_visor", "frame_dark", (0, -1.64, 2.07), (0.38, 0.1, 0.085), (lean, 0, 0), 0.5, levels=1)
    plate("eye_visor", "light", (0, -1.76, 2.07), 0.78, 0.1 if V78 else 0.07, 0.03, (lean, 0, 0), bend=0.45)   # 38c: flat, proud of the face, out of the brow's shadow
    # pass 32c: raised and slimmer; its lower edge blocked the eyes from the sprite camera (a ray test found it)
    for s in (-1, 1):   # pass 40: two brow plates, one over each eye, with a seam between (his front view); green (39b)
        plate("brow_bar_%d" % s, "main", (s * 0.19, -1.79, 2.29), 0.36, 0.13, 0.15, (lean - 30, 0, -s * 6), bend=0.12)
    # under the chin: layered throat plates closing the gap from the jaw back to the chest
    plate("jaw_throat_0", "accent", (0, -1.5, 1.65), 0.5, 0.26, 0.07, (lean + 80, 0, 0), bend=0.45)
    plate("jaw_throat_1", "accent", (0, -1.32, 1.61), 0.56, 0.26, 0.07, (lean + 95, 0, 0), bend=0.5)
    # The sprite's head is big and sits forward of and above the shoulders: grow the head group 15% about its
    # centre and drop it slightly so the crest stays the top of the machine.
    pivot, grow = Vector((0, -1.3, 2.05)), 0.92   # pass 27: Preston, "the head's too big" (was 1.15), scaled at the neck
    for o in set(bpy.context.scene.objects) - head_before:
        o.location = pivot + (o.location - pivot) * grow + Vector((0, 0.14, -0.24))   # pass 44 (part pass, 2026-10-13): 16 cm back over the shoulders, head overlay 0.656 to 0.760; render_sprite_views EYES follows this offset. pass 35: lower still, below the shoulder hump
        o.scale = tuple(v * grow for v in o.scale)
    for s in (-1, 1):   # glow strips: chest vents either side of the shield
        shell("chest_glow_%d" % s, "light", (s * 0.36, -1.26, 1.52), (0.04, 0.03, 0.22), (lean - 6, 0, 0), 0.0, levels=0)
    if not V77:
        shell("rack_glow", "light", (0, 0.04, 1.75), (0.9, 0.03, 0.03), (lean, 0, 0), 0.0, levels=0)
    # Ballast: three grey blocks with orange caps, straight across the back, side by side (Preston, 2026-10-12: the
    # back view is right; the front view only made them look like they climbed the back). Pass 26 had run them along
    # the spine; reverted.
    BACK_UP = 0.12   # ref-4 part pass (2026-10-13): the rack 12 cm higher, his back stands taller over the shoulders (back region 0.653, red along the top)
    if not V77:
        shell("rack_mount", "frame", (0, 0.04, 1.62 + BACK_UP), (0.72, 0.4, 0.24), (lean, 0, 0), 0.6, levels=1)
        shell("rack_frame", "frame", (0, 0.04, 1.72 + BACK_UP), (1.1, 0.44, 0.1), (lean, 0, 0), 0.7, levels=1)
        for k in range(3):
            x = (k - 1) * 0.36   # pass 29: smaller, closer, lower and further back, on the back below the head crest
            shell("ballast_%d" % k, "frame", (x, 0.04, 1.88 + BACK_UP), (0.34, 0.4, 0.38), (lean, 0, 0), 0.7, levels=1)
            shell("ballast_cap_%d" % k, "accent", (x, 0.0, 2.11 + BACK_UP), (0.37, 0.42, 0.13), (lean, 0, 0), 0.5, levels=1)
    else:   # v77: Codex's rack along the top: a grey rail down the spine, three blocks in a row on it with orange caps
        zb = lambda y: 2.12 - 0.21 * y   # the back's slope (lean -12)
        shell("rack_mount", "frame", (0, 0.0, 1.95), (0.36, 1.2, 0.2), (lean, 0, 0), 0.6, levels=1)
        shell("rack_frame", "frame", (0, 0.0, zb(0.0) - 0.16), (0.52, 1.36, 0.08), (lean, 0, 0), 0.7, levels=1)
        for k, y in enumerate((-0.42, 0.0, 0.42)):
            shell("ballast_%d" % k, "frame", (0, y, zb(y)), (0.44, 0.44, 0.34), (lean, 0, 0), 0.7, levels=1)
            shell("ballast_cap_%d" % k, "accent", (0, y - 0.01, zb(y) + 0.2), (0.47, 0.46, 0.11), (lean, 0, 0), 0.5, levels=1)
    # (pass 24: the feet are separate pieces like the fists now, nothing is fused)


def uv_box(ob, size=2.8):   # 2.8 m per texture tile: big calm panels, not Lego bricks
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.cube_project(cube_size=size, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")


def join_into_one():
    obs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    for o in obs:
        uv_box(o)
        bpy.context.view_layer.objects.active = o
        for m in list(o.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.join()
    ob = bpy.context.active_object
    ob.name = "ape_l"
    sharpen(ob)
    return ob


def sharpen(ob, angle=40, weight=50):
    """Crisp chamfers in the game file (pass 21). Until now the hard edges came from a shade-auto-smooth modifier,
    and the export keeps modifiers off (the rig has to stay live), so every chamfer shipped smeared: the probe found
    3,485 hard edges in the exported model and none of them split-shaded. Now the sharp edges are marked in the
    mesh itself, and a Weighted Normal modifier (by face area, the hard-surface standard the report confirmed) is
    applied so a big flat plate shades flat right up to its chamfer instead of bulging toward the bevel faces."""
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.faces_shade_smooth()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(angle))
    bpy.ops.mesh.mark_sharp()
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    wn = ob.modifiers.new("weighted", "WEIGHTED_NORMAL")
    wn.mode = "FACE_AREA"
    wn.weight = weight
    wn.keep_sharp = True
    bpy.ops.object.modifier_apply(modifier=wn.name)


def lights_and_camera(scene):
    world = bpy.data.worlds.new("world")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.05, 0.055, 0.065, 1)
    bg.inputs["Strength"].default_value = 0.9
    for rot, energy in (((50, 0, -35), 3.2), ((120, 0, 150), 1.5)):
        bpy.ops.object.light_add(type="SUN", location=(0, 0, 10))
        sun = bpy.context.active_object
        sun.rotation_euler = [math.radians(a) for a in rot]
        sun.data.energy = energy
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.type = "ORTHO"
    scene.camera = cam
    return cam, bg


def render_views(ob, cam):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 480
    scene.render.resolution_y = 360
    os.makedirs(OUT_VIEWS, exist_ok=True)
    cam.data.ortho_scale = 4.4
    target = Vector((0, 0, 1.25))
    elev = math.radians(30)
    for k, name in enumerate(["e", "ne", "n", "nw", "w", "sw", "s", "se"]):
        ob.rotation_euler = (0, 0, math.radians(k * 45) + math.radians(90))
        cam.location = target + Vector((0, -8 * math.cos(elev), 8 * math.sin(elev)))
        cam.rotation_euler = (math.radians(90) - elev, 0, 0)
        scene.render.filepath = os.path.join(OUT_VIEWS, "%s.png" % name)
        bpy.ops.render.render(write_still=True)
    ob.rotation_euler = (0, 0, 0)
    # Head close-ups: front three-quarter and the sprite's side profile (head to the right)
    cam.data.ortho_scale = 1.6
    head = Vector((0, -1.45, 2.02))
    for name, d in (("face", (-0.75, -1.0, 0.12)), ("face_side", (-1.0, -0.18, 0.06))):
        view = Vector(d).normalized()
        cam.location = head + view * 8
        cam.rotation_mode = "QUATERNION"
        cam.rotation_quaternion = (-view).to_track_quat("-Z", "Y")
        scene.render.filepath = os.path.join(OUT_VIEWS, "%s.png" % name)
        bpy.ops.render.render(write_still=True)
    cam.rotation_mode = "XYZ"


def render_silhouettes(ob, cam, bg):
    """Flat black front and side silhouettes on white, matching the blueprint's straight-on views."""
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0, 0, 0)
    scene.display.shading.background_type = "VIEWPORT"
    scene.display.shading.background_color = (1, 1, 1)
    scene.render.resolution_x = 600
    scene.render.resolution_y = 600
    os.makedirs(OUT_SIL, exist_ok=True)
    cam.data.ortho_scale = 3.4
    ob.rotation_euler = (0, 0, 0)
    # front: camera in front (-Y) looking +Y; side: camera at +X looking -X, so the head is on the left like the blueprint
    for name, loc, rot in (("front", (0, -10, 1.3), (90, 0, 0)), ("side", (10, 0, 1.3), (90, 0, 90))):
        cam.location = loc
        cam.rotation_euler = [math.radians(a) for a in rot]
        scene.render.filepath = os.path.join(OUT_SIL, "%s.png" % name)
        bpy.ops.render.render(write_still=True)
    # Preston's rear three-quarter sprite angle, for scoring: an outline and a flat-colour (albedo) render
    view = Vector((-0.62, 0.72, 0.38)).normalized()
    target = Vector((0, -0.2, 1.35))
    cam.location = target + view * 12
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (-view).to_track_quat("-Z", "Y")
    cam.data.ortho_scale = 4.6
    scene.render.filepath = os.path.join(OUT_SIL, "rear34.png")
    bpy.ops.render.render(write_still=True)
    scene.display.shading.color_type = "TEXTURE"
    scene.render.filepath = os.path.join(OUT_SIL, "rear34_color.png")
    bpy.ops.render.render(write_still=True)
    scene.display.shading.color_type = "SINGLE"
    cam.rotation_mode = "XYZ"


def uv_coverage(me, layer):
    """How much of the texture sheet the UV islands cover (1.0 = the whole sheet, once over)."""
    bm = bmesh.new()
    bm.from_mesh(me)
    uv = bm.loops.layers.uv[layer]
    total = 0.0
    for f in bm.faces:
        pts = [l[uv].uv for l in f.loops]
        total += abs(sum(pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y
                         for i in range(len(pts)))) / 2
    bm.free()
    return total


def bake_atlas(ob, size=2048):
    """Bake the machine into one 1024 px texture set on a fresh UV layout: colour, a surface-detail (normal) map and a
    metal/roughness map. Targets measured from Fall of Cybertron gameplay (2026-10-11): worn, desaturated metal, about
    four times our edge detail, shine on edges, shadows not crushed. Panel seams, rivets and vents in the painted
    panels become real grooves in the normal map; convex rims wear to bare steel that is metallic and shiny; creases
    collect grime. Glowing parts keep their own emissive material."""
    import numpy as np
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    me = ob.data
    for i, m in enumerate(me.materials):   # safety: an empty slot would stop the bake
        if m is None:
            me.materials[i] = MATS["frame_dark"]
    base_uv = me.uv_layers[0].name
    atlas = me.uv_layers.new(name="atlas")
    me.uv_layers.active = atlas
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.004)
    # Pack the pieces tightly: the first layout used only 24% of the sheet (44 texture px per metre against Grimlock's
    # 171-502, measured by taking his model apart). Packing plus 2048 px raises the density several times.
    # Pack by the islands' real outlines (pass 21): the box packer left 57% of the sheet empty (coverage 0.43).
    bpy.ops.uv.pack_islands(rotate=True, rotate_method="ANY", shape_method="CONCAVE", margin_method="FRACTION",
                            margin=0.003)
    bpy.ops.object.mode_set(mode="OBJECT")
    print("ATLAS coverage %.2f of the sheet" % uv_coverage(me, "atlas"))

    def new_img(name, data=False):
        img = bpy.data.images.new(name, size, size, float_buffer=False, is_data=data)
        return img
    targets = []
    for m in me.materials:
        nt = m.node_tree
        uvn = nt.nodes.new("ShaderNodeUVMap")
        uvn.uv_map = base_uv   # the painted panels keep reading the box projection
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        for n in list(nt.nodes):
            if n.type == "TEX_IMAGE":
                nt.links.new(uvn.outputs["UV"], n.inputs["Vector"])
                if bsdf is not None:
                    # Surface detail: a 3x finer copy of the painted panels drives a strong bump, so seams, rivets
                    # and vents become grooves (Cybertron normal maps measured 17x our first attempt's detail)
                    fine = nt.nodes.new("ShaderNodeTexImage")
                    hpath = os.path.join(ROOT, "art", "machines", "ape_l", "textures",
                                         m.name.split(".")[0].replace("ape_", "") + "_height.png")
                    fine.image = bpy.data.images.load(hpath) if os.path.exists(hpath) else n.image
                    fine.image.colorspace_settings.is_data = True
                    mapping = nt.nodes.new("ShaderNodeMapping")
                    mapping.inputs["Scale"].default_value = (3.0, 3.0, 3.0)
                    nt.links.new(uvn.outputs["UV"], mapping.inputs["Vector"])
                    nt.links.new(mapping.outputs["Vector"], fine.inputs["Vector"])
                    bump = nt.nodes.new("ShaderNodeBump")
                    bump.inputs["Strength"].default_value = 1.0
                    bump.inputs["Distance"].default_value = 0.03
                    nt.links.new(fine.outputs["Color"], bump.inputs["Height"])
                    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        t = nt.nodes.new("ShaderNodeTexImage")
        nt.nodes.active = t
        targets.append(t)

    def bake(kind, img, samples, **kw):
        for t in targets:
            t.image = img
            t.id_data.nodes.active = t
        scene.cycles.samples = samples
        bpy.ops.object.bake(type=kind, uv_layer="atlas", margin=6, **kw)
        return np.array(img.pixels[:]).reshape(size, size, 4)
    col = bake("DIFFUSE", new_img("ape_bake_color"), 8, pass_filter={"COLOR"})
    ao = bake("AO", new_img("ape_bake_ao", True), 128)[:, :, :1]
    img_nrm = new_img("ape_l_atlas_normal", True)
    # High-to-low bake, the way finished game art is made (pass 18): a high-detail copy with rounded edges everywhere
    # (and the panel detail from the height textures) is baked onto the game model's surface-detail map.
    hi = ob.copy()
    hi.data = ob.data.copy()
    bpy.context.scene.collection.objects.link(hi)
    rb = hi.modifiers.new("round", "BEVEL")
    rb.width = 0.018
    rb.segments = 3
    rb.limit_method = "ANGLE"
    rb.angle_limit = math.radians(30)
    bpy.ops.object.select_all(action="DESELECT")
    hi.select_set(True)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bake("NORMAL", img_nrm, 8, normal_space="TANGENT", use_selected_to_active=True, cage_extrusion=0.03,
         max_ray_distance=0.08)
    bpy.data.objects.remove(hi)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob

    def emit_bake(name, per_material, samples=4):
        """Bake a per-material value (or the curvature) through each material's emission."""
        for m, t in zip(me.materials, targets):
            nt = m.node_tree
            emit = nt.nodes.new("ShaderNodeEmission")
            key = m.name.split(".")[0].replace("ape_", "")
            if per_material is None:
                geo = nt.nodes.new("ShaderNodeNewGeometry")
                nt.links.new(geo.outputs["Pointiness"], emit.inputs["Color"])
            else:
                v = per_material.get(key, per_material["main"])
                emit.inputs["Color"].default_value = (v[0], v[1], 0.0, 1.0)
            out_node = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            nt.links.new(emit.outputs["Emission"], out_node.inputs["Surface"])
        return bake("EMIT", new_img(name, True), samples)
    # paint is a glossy coat over metal; frames are bare metal (roughness, metallic)
    surface = emit_bake("ape_bake_surface", {"main": (0.42, 0.15), "trim": (0.45, 0.15), "accent": (0.4, 0.2),
                                             "frame": (0.5, 0.45), "frame_dark": (0.55, 0.4), "face": (0.45, 0.4),
                                             "light": (0.3, 0.0)})
    edge = emit_bake("ape_bake_edge", None)[:, :, :1]

    def soften(a, r=2):
        """Box-blur a baked layer: the bake's sample grain otherwise lands in the texture as pixel speckle."""
        out = a.copy()
        for axis in (0, 1):
            acc = np.zeros_like(out)
            for d in range(-r, r + 1):
                acc += np.roll(out, d, axis=axis)
            out = acc / (2 * r + 1)
        return out
    ao, edge = soften(ao), soften(edge, 1)
    convex = np.clip((edge - 0.56) * 6.0, 0.0, 1.0)    # sharp rims and corners only: worn to bare steel
    crease = np.clip((0.5 - edge) * 5.0, 0.0, 1.0)     # inside corners: grime
    steel = np.array([0.6, 0.61, 0.62])
    rgb = col[:, :, :3] * (0.55 + 0.45 * ao ** 1.2) * (1.0 - 0.3 * crease)
    rgb = rgb * (1.0 - 0.45 * convex) + steel * 0.45 * convex
    out = col.copy()
    out[:, :, :3] = np.clip(rgb, 0, 1)
    rough = np.clip(surface[:, :, 0] - 0.18 * convex[:, :, 0] + 0.2 * crease[:, :, 0], 0.15, 0.9)
    metal = np.clip(surface[:, :, 1] + 0.8 * convex[:, :, 0], 0.0, 1.0)
    orm = np.ones_like(col)
    orm[:, :, 0] = ao[:, :, 0]
    orm[:, :, 1] = rough
    orm[:, :, 2] = metal

    def save(name, arr, data):
        img = new_img(name, data)
        img.pixels[:] = arr.ravel()
        img.filepath_raw = os.path.join(ROOT, "art", "machines", "ape_l", "textures", name + ".png")
        img.file_format = "PNG"
        img.save()
        return img
    final = save("atlas", out, False)
    orm_img = save("atlas_orm", orm, True)
    img_nrm.filepath_raw = os.path.join(ROOT, "art", "machines", "ape_l", "textures", "atlas_normal.png")
    img_nrm.file_format = "PNG"
    img_nrm.save()
    body = bpy.data.materials.new("ape_body")
    body.use_nodes = True
    nt = body.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = final
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    otex = nt.nodes.new("ShaderNodeTexImage")
    otex.image = orm_img
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(otex.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    ntex = nt.nodes.new("ShaderNodeTexImage")
    ntex.image = img_nrm
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nmap.uv_map = "atlas"
    nt.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    light_idx = [i for i, m in enumerate(me.materials) if m.name.startswith("ape_light")]
    keep = [p.material_index in light_idx for p in me.polygons]
    me.materials.clear()
    me.materials.append(body)
    eye = bpy.data.materials.new("ape_eye")   # fresh: the bakes above rewired the original glow material
    eye.use_nodes = True
    eb = next(n for n in eye.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    eb.inputs["Base Color"].default_value = srgb(HEX["light"])
    eb.inputs["Emission Color"].default_value = srgb(HEX["light"])
    eb.inputs["Emission Strength"].default_value = 1.2
    me.materials.append(eye)
    for p, lit in zip(me.polygons, keep):
        p.material_index = 1 if lit else 0
    me.uv_layers.remove(me.uv_layers[base_uv])
    me.uv_layers.active = me.uv_layers["atlas"]
    return final


BONE_OF = {"upper_frame": "upper_arm", "upper_arm": "upper_arm", "shoulder_joint": "upper_arm",
           "elbow": "forearm", "fore_frame": "forearm", "forearm": "forearm", "fore_guard": "forearm",
           "piston_sleeve": "forearm", "piston_rod": "forearm", "wrist_cuff": "forearm",
           "fist": "hand", "finger": "hand", "handplate": "hand", "fore_piston": "forearm", "fore_rod": "forearm",
           "toecap": "foot", "ankle": "foot", "ankle_wheel": "shin", "heel_piston": "shin", "heel_rod": "shin", "knucklecap": "hand", "handglow": "hand", "forelight": "forearm", "upperslit": "upper_arm", "upper_armor": "upper_arm", "fore_armor": "forearm", "thigh_armor": "thigh", "shin_armor": "shin", "upper_plate": "upper_arm", "fore_plate": "forearm", "thigh_plate": "thigh", "thigh_frame": "thigh", "hip_piston": "thigh", "calf_plate": "shin", "shin_core": "shin", "wrist": "forearm", "arm_slot": "upper_arm", "finger_joint": "hand", "thumb": "hand", "knuckle_guard": "hand",
           "hip_joint": "thigh", "thigh": "thigh", "knee": "shin", "shin_frame": "shin", "shin_plate": "shin",
           "upper_tank": "upper_arm", "upper_tankcap": "upper_arm", "knuckle_spike": "hand", "fist_line": "forearm",
           "foot": "foot", "toe": "foot", "heel": "foot", "shin": "shin"}
HEAD_PARTS = ("helmet", "brow", "face", "muzzle", "eye", "crest", "ear", "jaw", "mouth", "cheek", "socket", "nostril",
              "skull", "nose", "lip", "crown", "nape")


def bone_for(name):
    """Which bone a part rides on. Machines are rigid: every part follows exactly one bone, weight 1."""
    if name.startswith(HEAD_PARTS):
        return "head"
    m = re.match(r"^(.*?)_(-1|1)(_\d+)?$", name.replace("_hub", "").replace("_ring", "").replace("_glow", "").replace("_housing", "").replace("_lamp", "").replace("_seam", "" if V79 else "_seam"))
    if m and m.group(1) in BONE_OF:
        return "%s.%s" % (BONE_OF[m.group(1)], "L" if m.group(2) == "1" else "R")
    return "body"


def tag_parts():
    for o in bpy.context.scene.objects:
        if o.type == "MESH":
            vg = o.vertex_groups.new(name=bone_for(o.name))
            vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    if os.environ.get("BIND_NAMES"):   # tools/blender/bind_audit.py: which part rides which bone, before the join
        import json
        rows = []
        for o in bpy.context.scene.objects:
            if o.type == "MESH" and o.vertex_groups:
                c = sum((o.matrix_world @ v.co for v in o.data.vertices), __import__("mathutils").Vector()) / max(1, len(o.data.vertices))
                rows.append({"name": o.name, "bone": o.vertex_groups[0].name, "verts": len(o.data.vertices), "center": [round(x, 3) for x in c]})
        with open(os.environ["BIND_NAMES"], "w") as fh:
            json.dump(rows, fh, indent=0)


def make_rig(ob):
    arm_data = bpy.data.armatures.new("ape_l_rig")
    rig = bpy.data.objects.new("ape_l_rig", arm_data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(name, head, tail, parent=None):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.align_roll(Vector((1, 0, 0)).cross((b.tail - b.head).normalized()))   # local X = world X: pitch is swing
        if parent:
            b.parent = eb[parent]
        return b
    bone("body", (0, 0.66, 1.15), (0, -0.62, 1.7))
    bone("head", (0, -0.85, 2.08), (0, -1.55, 2.08), "body")
    J = JOINTS
    for side in ("L", "R"):
        bone("upper_arm." + side, J["shoulder." + side], J["elbow." + side], "body")
        bone("forearm." + side, J["elbow." + side], J["wrist." + side], "upper_arm." + side)
        bone("hand." + side, J["wrist." + side], J["knuckle." + side], "forearm." + side)
        bone("thigh." + side, J["hip." + side], J["knee." + side], "body")
        bone("shin." + side, J["knee." + side], J["ankle." + side], "thigh." + side)
        bone("foot." + side, J["ankle." + side], J["toe." + side], "shin." + side)
    bpy.ops.object.mode_set(mode="OBJECT")
    ob.parent = rig
    mod = ob.modifiers.new("rig", "ARMATURE")
    mod.object = rig
    return rig


def knuckle_walk(rig):
    """Prepare the rig for the clips: 24 fps, Euler rotations."""
    bpy.context.scene.render.fps = 24
    rig.animation_data_create()
    for b in rig.pose.bones:
        b.rotation_mode = "XYZ"


def walk_pose(t):
    """A knuckle-walk loop in place, timed from gorilla gait measurements (Ito et al. 2025, Scientific Reports):
    diagonal sequence, each limb on the ground about two thirds of the cycle, the hind foot landing about half a
    cycle before the hand on the same side; arms are stiff columns (swing from the shoulder, little elbow bend),
    the hind legs bend more and push. 36 frames at 24 fps = 1.5 s, inside the measured 1.1-1.8 s."""
    contact = {"arm.L": 0.0, "arm.R": 0.507, "leg.L": 0.475, "leg.R": 0.986}   # stance onset per limb
    duty = 0.66

    def phase(c):
        u = (t - c) % 1.0
        if u < duty:                      # stance: the limb sweeps from forward to back
            return -1.0 + 2.0 * u / duty, 0.0
        v = (u - duty) / (1.0 - duty)     # swing: back to forward, lifted
        e = 0.5 - 0.5 * math.cos(math.pi * v)
        return 1.0 - 2.0 * e, math.sin(math.pi * v)
    p = {"stance": []}   # animation pass 1 (2026-10-12): the limbs on the ground this frame, for grounding
    for side in ("L", "R"):
        if (t - contact["arm." + side]) % 1.0 < duty:
            p["stance"].append("hand." + side)
        if (t - contact["leg." + side]) % 1.0 < duty:
            p["stance"].append("foot." + side)
        sw, lift = phase(contact["arm." + side])
        p["upper_arm." + side] = (15 * sw - 12 * lift, 0, 0)   # animation pass 1: the swing hand cleared the floor by -0.2 m
        p["forearm." + side] = (40 * lift, 0, 0)
        p["hand." + side] = (35 * lift, 0, 0)
        sw, lift = phase(contact["leg." + side])
        p["thigh." + side] = (17 * sw - 10 * lift, 0, 0)
        p["shin." + side] = (38 * lift, 0, 0)
        p["foot." + side] = (-18 * lift, 0, 0)
    p["body"] = (0, 2.5 * math.sin(2 * math.pi * t), 0)   # weight shifts side to side
    p["head"] = (3 * math.cos(4 * math.pi * t), 0, 0)
    return p


def gait_pose(t):
    """Animation pass 1 (2026-10-12, from reports/Gorilla mech animation foundation.md): the walk re-centred so the
    limbs sweep about the vertical instead of about the forward-leaning rest pose. Measured on the posed mesh over a
    grid of offsets (scratchpad walk_grid.py): with the upper arms 40 deg back and the thighs 30 deg back, the
    planted hand floats at most 0.03 m and a foot 0.08 m, and the swinging hand dips 0.05 m under the floor (the old
    walk: 0.24 m float, 0.19 m dip). The 'walk' clip stays as the battle-stance source; this is the loop to animate."""
    p = walk_pose(t)
    for side in ("L", "R"):
        sw, lift = p["upper_arm." + side][0], p["forearm." + side][0] / 40.0   # recover the phase terms
        sw = (sw + 12 * lift) / 15.0
        # pass 1b: the rest arm leans 20.7 deg ahead of the shoulder and the leg 9.7 deg ahead of the hip (joints.py), so
        # the old sweep never passed vertical; a knuckle-walk lands the hand about 20 deg ahead and lifts it about
        # 10 deg behind. 14 deg back on the arm and 10 on the thigh centre the sweeps (the contact grid's 40/30 folded
        # the limbs under the belly: numbers without a posture constraint).
        p["upper_arm." + side] = (15 * sw - 20 * lift + 14, 0, 0)
        p["forearm." + side] = (55 * lift, 0, 0)
        p["hand." + side] = (40 * lift, 0, 0)
        p["thigh." + side] = (p["thigh." + side][0] + 10, 0, 0)
    return p


def _ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def stash(rig, act, name):
    """Move an action onto its own NLA track, so every clip exports under its own name."""
    track = rig.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, 1, act)
    rig.animation_data.action = None


def clip(rig, name, frames, pose, grounded=True):
    """Key one clip. pose(t) returns {bone: (rx, ry, rz) degrees} and optionally "body_move": world offset in metres.
    Bones it leaves out return to rest, so clips never inherit each other's poses. With grounded, every frame is
    measured and the body lifted so the lowest point of the posed machine sits on the floor: the body is the root
    of the skeleton, so tilting or dropping it would otherwise push the limbs through the ground (the first death
    clip sank 1.29 m)."""
    pb = rig.pose.bones
    body_rest = rig.data.bones["body"].matrix_local.to_3x3().inverted()
    mesh = next(c for c in rig.children if c.type == "MESH")
    poses = []
    rig.animation_data.action = None
    for track in rig.animation_data.nla_tracks:   # stored clips must not leak into the measurement
        track.mute = True
    for b in pb:   # settle at rest first: the first measurement otherwise saw the previous clip (a 0.14 m error)
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    bpy.context.view_layer.update()
    for f in range(frames + 1):
        p = pose(f / frames)
        move = Vector(p.get("body_move", (0, 0, 0)))
        if grounded:
            for b in pb:
                b.rotation_euler = [math.radians(v) for v in p.get(b.name, (0, 0, 0))]
            pb["body"].location = body_rest @ move
            bpy.context.view_layer.update()
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            ev = mesh.evaluated_get(dg)
            me = ev.to_mesh()
            stance = p.get("stance")
            if stance:
                gidx = {mesh.vertex_groups[n].index for n in stance if n in mesh.vertex_groups}
                zs = [(mesh.matrix_world @ v.co).z for v, ov in zip(me.vertices, mesh.data.vertices)
                      if any(g.group in gidx and g.weight > 0.5 for g in ov.groups)]
                low = min(zs) if zs else min((mesh.matrix_world @ v.co).z for v in me.vertices)
            else:
                low = min((mesh.matrix_world @ v.co).z for v in me.vertices)
            ev.to_mesh_clear()
            move = move + Vector((0, 0, -low))
            move = move + Vector((0, 0, p.get("air", 0.0)))   # 2026-10-15: a pose may leave the floor (the punch's leap); grounding alone always put it back down
        poses.append((p, move))
    act = bpy.data.actions.new(name)
    rig.animation_data.action = act
    for f, (p, move) in enumerate(poses):
        for b in pb:
            b.rotation_euler = [math.radians(v) for v in p.get(b.name, (0, 0, 0))]
            b.keyframe_insert("rotation_euler", frame=f + 1)
        pb["body"].location = body_rest @ move
        pb["body"].keyframe_insert("location", frame=f + 1)
    stash(rig, act, name)
    for track in rig.animation_data.nla_tracks:
        track.mute = False
    return act


def idle_pose(t):
    """Two-second breathing loop: the chest rises and falls, the head looks left then right."""
    br = math.sin(2 * math.pi * t)
    return {"body": (1.5 * br, 0, 0), "head": (-2 * br, 0, 12 * math.sin(2 * math.pi * t + 0.6)),
            "upper_arm.L": (-1.5 * br, 0, 0), "upper_arm.R": (-1.5 * br, 0, 0),
            "body_move": (0, 0, 0.018 * br)}


def _seg(t, a, b):
    """0 before a, eased 0 to 1 between a and b, 1 after b."""
    return _ease((t - a) / max(b - a, 1e-6))


def _pulse(t, a, b, c, d):
    """Rises a to b, holds to c, falls to d."""
    return _seg(t, a, b) * (1 - _seg(t, c, d))


# RIG_SIGNS, measured on the posed rig 2026-10-15 (Claude; a Blender probe of bone heads and tails). The clips written
# before this guessed several of these and got them backwards (slam's "rear-up", throw's "tilt back" and whip, the
# punch's elbow fold):
#   body X+ pitches FORWARD (front down, hind legs lift); X- leans back.   body Y+ rolls toward the camera (near R
#   side down, the far side and its pods UP, so the silhouette grows taller).
#   upper_arm X+ swings the arm down > back > up > forward (shoulder extension first); X- swings it forward and up
#   in front.   upper_arm.R Z+ lifts the hanging elbow out to the near side; once the arm is raised past vertical
#   Z acts the other way (Z- takes it out: the throw's reach, measured by a Z sweep).
#   forearm X- FLEXES the elbow (from hanging, the hand comes forward and up); X+ bends it backward.
#   head X+ nods down; X- looks up.   thigh X+ takes the foot back; shin X- folds the knee, X+ straightens it.
# The near side in the E view is R (x < 0); forward is -Y.
# THE CAMERA (render_sprite_views.py turns the rig 70 degrees for the E view, E_TURN 20, under an 18-degree elevation):
# forward and the near side both come TOWARD the camera, and anything nearer the camera draws LOWER on screen, about
# 0.31 m per metre nearer. A fist punched level at shoulder height (2 m forward of the body) draws at chest height,
# tucked in front of the body (blind review round 2 of the punch); aim forward reaches about 25 degrees up to read
# level. Arms raised back over the top draw behind the head mass, not above it (the slam, round 2).


def punch_pose(t):
    """Piston Knuckles as an overhand haymaker (2026-10-15, Preston: "looks like its just flicking its wrist foward after
    winding it. I want it to look like a winding arching punch as its jumping towards the other mech"). The old pose
    (punch_pose_v1) only pitched the upper arm back and forward from the knuckle-walk stance, so the fist never rose
    and the drive read as a wrist flick. Synthesis (research_notes/Gorilla haymaker punch/): heavy punches in shipped
    games (Hugo, Zangief, Potemkin, Donkey Kong) hold ONE wind-up pose as the telegraph, swing in a frame or two,
    hold the impact as hitstop and recover long; the body leads and the arm drags, then snaps; the fist must break the
    silhouette above the head at the top. The near (right) fist travels one arc over the top: the upper arm's +X takes
    the hanging arm back (90), up (180) and forward (270). Source frames (36 = 1.5 s) the sprite clip samples:
      0-3 anticipation crouch, fist lifting; 4-9 wind-up to the top: fist cocked high behind the shoulder, elbow up,
      body turned away and reared, weight back; 9-12 the top held; 12-16 launch: the body leaps forward and up, the
      torso unwinds, the arm drags; 16-21 the swing over the top and down; 21 contact, held to 22; 22-25 landing squash
      with the fist past the target, the head snapping forward late; 25-32 settle."""
    f = t * 36
    crouch = _seg(f, 0, 3) * (1 - _seg(f, 3, 8))
    wind = _seg(f, 2, 9)
    launch = _seg(f, 12, 16)
    swing = _seg(f, 16, 21)
    land = _seg(f, 21, 24) * (1 - _seg(f, 25, 31))
    settle = _seg(f, 25, 32)
    head_snap = _seg(f, 21, 23) * (1 - _seg(f, 25, 31))
    lunge = launch * (1 - settle)
    hop = math.sin(math.pi * min(1.0, max(0.0, (f - 12) / 10)))     # off the ground 12-22: the apex at 17, mid-swing
    plant = _seg(f, 21, 25)                                           # the hind feet come back down after contact
    load = wind * (1 - launch)                                        # hind legs bent under the lean, released by the jump
    # Preston (2026-10-15, mid-pass): "it should lean back while bending and cocking the elbow back and up like pulling
    # a lawnmower cable then punch". Measured in the blend (bone positions per frame, prev4): with the upper arm at 125
    # the elbow sat level with the shoulder, inside the back's outline, so the wind-up read as a fist curled at the chest;
    # and the 30-degree forward pitch at contact kept the hind feet 0.85 m up through the landing, a stretched crawl.
    # The lean back tips a back-pointing arm downward, so the upper arm goes to 180 for an elbow about 40 degrees above
    # the back horizontal, and the forearm folds to 165 so the fist comes in to the chest: the cable pulled. The swing
    # (prev5) still showed no arch: the fist went from the chest straight forward, never above the head, and f24/f28
    # were the same sprawl. So the forearm half opens during the leap (165 to 70) while the elbow keeps rising, which
    # carries the fist up over the head (about 0.9 m above the shoulder at f17), then the swing (to 21, the contact)
    # brings it over and down at the same shallow drive; the forward pitch at contact is 12, the plant brings the hind
    # feet down after it, and the settle starts at 25 so f28 is already on the way back.
    # The fold uses forearm +X, which by RIG_SIGNS bends the elbow past straight. A flexed version (-X: the fist by the
    # ribs, then cocked behind the head) was rendered and judged blind against this one the same day and lost 4 to 6: at
    # sprite size the +X fold shows the fist arcing over the top, and no reviewer saw a backward elbow. Kept on purpose.
    # Three blind rounds (2026-10-15) tried variants of this installed version: contact at 278 with a leg-bend
    # crouch won 6-5 at confidence 2; contact at 255 crossing to the centre line with a harder twist lost 5-6 at
    # confidence 3. No clear gain, so the installed version stays. What every round flagged in all versions: the hit
    # frame draws the fist low and tucked (THE CAMERA in RIG_SIGNS: a forward reach comes toward the camera and draws
    # lower), the anticipation frame barely dips, and the cable pull's forearm crosses the chest.
    ua = 168 * wind + 20 * launch + 104 * swing + 8 * land + 68 * settle   # 0, 168 cocked, 188 over the head, 292 contact, 360 down
    fa = 165 * wind - 95 * launch - 80 * swing + 10 * settle            # the cable fold, opened overhead in the leap, snapped straight
    hd = 25 * wind - 45 * swing + 20 * settle   # the wrist cocked, the knuckles lead at contact
    return {"upper_arm.R": (ua, 0, -12 * wind + 12 * swing), "forearm.R": (fa, 0, 0), "hand.R": (hd, 0, 0),
            "upper_arm.L": (-10 * wind + 22 * swing - 12 * settle, 0, 10 * wind - 10 * swing), "forearm.L": (8 * wind - 8 * settle, 0, 0),
            # body X: negative leans BACK onto the hind legs (the render showed +X lifting the hind legs: v1's "pitches up"
            # had the sign backwards), positive pitches forward over the front
            "body": (-12 * LEAN * wind + 24 * swing - 8 * plant - 4 * settle + 6 * crouch, 0, -24 * wind + 14 * launch + 24 * swing - 14 * settle),
            "head": (14 * wind - 6 * launch - 10 * swing + 2 * settle + 12 * head_snap, 0, 14 * wind - 8 * launch - 12 * swing + 6 * settle),   # eyes stay on the target
            # the hind legs coil deep under the lean (2026-10-15 battle capture: battle.gd stands the player's feet on screen row
            # 121, so the canvas starts 10 rows above the screen and the reared elbow was cut by up to 7 rows). Measured in
            # the rig: shin -X folds the knee (+X straightens it, so v2's "+10 squash" stood the legs up), thigh +X takes
            # the foot back; thigh +20 / shin -25 lowers the hip 0.11 m with the foot still under it.
            "thigh.L": (12 * load - 14 * lunge + 8 * land, 0, 0), "thigh.R": (12 * load + 16 * lunge + 8 * land, 0, 0),
            "shin.L": (-16 * load - 12 * land, 0, 0), "shin.R": (-16 * load - 12 * land, 0, 0),
            "body_move": (0, 0.10 * load - 0.50 * lunge, 0), "air": AIR * hop,   # the leap, kept after grounding
            "stance": ["hand.L", "foot.L", "foot.R"] + (["hand.R"] if f < 2 or f > 33 else [])}


def punch_pose_v1(t):
    """Piston Knuckles, right fist. Animation pass 2 (2026-10-12, from reports/Gorilla mech animation foundation.md):
    wind-up 0-0.40 (weight rocks back onto the hind legs, the body pitches up and turns away, the fist draws back,
    the free hand plants wider), hold 0.40-0.50, strike 0.50-0.58 (the fist past the target, the body lunges and
    turns in, the forearm driven straight), hold 0.58-0.72, settle 0.72-1.0 in parts: body first, arm 3 frames
    later, head 5 frames later. 36 frames = 1.5 s."""
    wind = _pulse(t, 0.0, 0.40, 0.50, 0.58)
    strike = _pulse(t, 0.50, 0.58, 0.72, 0.86)
    arm_settle = _pulse(t, 0.50, 0.58, 0.72 + 3 / 36, 0.94)
    head_settle = _pulse(t, 0.50, 0.58, 0.72 + 5 / 36, 1.0)
    return {"upper_arm.R": (30 * wind - 62 * arm_settle, 0, 0), "forearm.R": (40 * wind - 24 * arm_settle, 0, 0),   # 2b: fist forward, not over the head
            "hand.R": (18 * wind - 18 * arm_settle, 0, 0),
            "upper_arm.L": (-6 * wind - 10 * strike, 0, 8 * wind), "forearm.L": (6 * wind, 0, 0),
            "body": (8 * wind - 5 * strike, 0, -14 * wind + 16 * strike),
            "head": (-6 * wind + 8 * head_settle, 0, 10 * wind - 12 * head_settle),
            "thigh.L": (6 * wind - 10 * strike, 0, 0), "thigh.R": (6 * wind + 12 * strike, 0, 0),
            "shin.L": (8 * wind, 0, 0), "shin.R": (8 * wind, 0, 0),
            "body_move": (0, 0.10 * wind - 0.24 * strike, 0.02 * strike),
            "stance": ["hand.L", "foot.L", "foot.R"] + (["hand.R"] if t < 0.1 or t > 0.94 else [])}


def slam_pose_v1(t):
    """Quake Slam, both fists into the ground. Rear-up 0-0.35 (both arms rise, the chest pitches up over the hind
    legs, the head holds level a beat longer), hold 0.35-0.45, drop 0.45-0.53 (arms driven down, the body pitches
    forward and compresses), post-impact crouch hold 0.53-0.70, shudder 0.70-0.80 (1 to 2% of height), settle
    0.80-1.0 with the twin broken: the right arm lifts 3 frames before the left, the head last."""
    rear = _pulse(t, 0.0, 0.35, 0.45, 0.53)
    head_rear = _pulse(t, 0.04, 0.38, 0.45, 0.53)
    impact = _pulse(t, 0.45, 0.53, 0.70, 0.92)
    arm_r = _pulse(t, 0.45, 0.53, 0.70, 0.86)
    arm_l = _pulse(t, 0.45, 0.53, 0.70 + 3 / 36, 0.94)
    head_impact = _pulse(t, 0.47, 0.55, 0.72, 1.0)
    shud = math.sin(2 * math.pi * (t - 0.70) / 0.05) * _pulse(t, 0.70, 0.72, 0.76, 0.80) if 0.70 <= t <= 0.80 else 0.0
    return {"upper_arm.R": (-95 * rear + 22 * arm_r, 0, 0), "upper_arm.L": (-95 * rear + 22 * arm_l, 0, 0),
            "forearm.R": (45 * rear + 12 * arm_r, 0, 0), "forearm.L": (45 * rear + 12 * arm_l, 0, 0),
            "hand.R": (-25 * rear + 10 * arm_r, 0, 0), "hand.L": (-25 * rear + 10 * arm_l, 0, 0),
            "body": (38 * rear - 9 * impact, 0, 0), "head": (-24 * head_rear + 10 * head_impact, 0, 0),   # 2b: taller rear-up
            "thigh.L": (30 * rear - 8 * impact, 0, 0), "thigh.R": (30 * rear - 8 * impact, 0, 0),
            "shin.L": (20 * rear + 10 * impact, 0, 0), "shin.R": (20 * rear + 10 * impact, 0, 0),
            "body_move": (0, 0.16 * rear - 0.10 * impact, 0.12 * rear - 0.10 * impact + 0.03 * shud),
            "stance": ["foot.L", "foot.R"] + (["hand.L", "hand.R"] if t < 0.05 or t > 0.5 else [])}


def throw_pose_v1(t):
    """Ballast Throw, right arm. Tear 0-0.35 (the arm reaches back and up over the shoulder to the rack, the torso
    turns toward it and tilts back over the hind legs, hips locked), load hold 0.35-0.45, hurl 0.45-0.55 (the arm
    whips forward over the top, the torso turns in and the body lunges), plant 0.55-0.70 (the hand comes down to
    the ground), settle 0.70-1.0 in parts. The block itself is a separate sprite or effect."""
    tear = _pulse(t, 0.0, 0.35, 0.45, 0.55)
    hurl = _pulse(t, 0.45, 0.55, 0.62, 0.78)
    plant = _seg(t, 0.55, 0.70)
    arm_settle = 1 - _seg(t, 0.72, 0.96)
    head_settle = 1 - _seg(t, 0.76, 1.0)
    return {"upper_arm.R": (115 * tear - 100 * hurl * arm_settle - 10 * plant * arm_settle, 0, -10 * tear),
            "forearm.R": (60 * tear + 10 * hurl, 0, 0), "hand.R": (-20 * tear - 25 * hurl, 0, 0),
            "upper_arm.L": (-8 * tear - 6 * hurl, 0, 6 * tear), "forearm.L": (8 * tear, 0, 0),
            "body": (14 * tear - 6 * hurl, 0, 22 * tear - 18 * hurl),
            "head": (-8 * tear + 6 * hurl * head_settle, 0, 20 * tear - 16 * hurl * head_settle),
            "thigh.L": (10 * tear - 8 * hurl, 0, 0), "thigh.R": (10 * tear + 10 * hurl, 0, 0),
            "shin.L": (10 * tear, 0, 0), "shin.R": (10 * tear, 0, 0),
            "body_move": (0, 0.12 * tear - 0.20 * hurl, 0.02 * tear),
            "stance": ["hand.L", "foot.L", "foot.R"] + (["hand.R"] if t < 0.04 or t > 0.72 else [])}


def slam_pose(t):
    """Quake Slam, both fists into the ground (rebuilt 2026-10-15 with RIG_SIGNS: v1's "rear-up" was body +38, a
    forward bow, which drove the unstanced fists through the floor in frames 2-4, the camera cut Codex reported).
    Raise 0-0.35: both arms swing up in front to overhead, elbows flexed so the fists sit behind the head, the chest
    lifts a little (the lean is small: the battle screen starts 10 canvas rows above the gorilla's top, see the punch).
    Hold 0.35-0.45. Drop 0.45-0.53: the arms come over the front and down, straightening, the body pitches forward
    into it and both fists hit the floor ahead. Crouch hold 0.53-0.70, shudder 0.70-0.80, settle 0.80-1.0 with the
    twin broken: the right arm lifts 3 frames before the left, the head last."""
    up = _seg(t, 0.0, 0.35)
    down = _seg(t, 0.45, 0.53)
    impact = _pulse(t, 0.45, 0.53, 0.70, 0.92)
    rec_r = _seg(t, 0.70, 0.86)
    rec_l = _seg(t, 0.70 + 3 / 36, 0.94)
    head_up = _seg(t, 0.04, 0.38)
    head_impact = _pulse(t, 0.47, 0.55, 0.72, 1.0)
    shud = math.sin(2 * math.pi * (t - 0.70) / 0.05) * _pulse(t, 0.70, 0.72, 0.76, 0.80) if 0.70 <= t <= 0.80 else 0.0
    # blind review round 1: the raised fists read as a band around the head (flexed too far), the hind feet rose 10 px at
    # impact (a 16-degree forward pitch onto fists planted far ahead), and the shudder frame matched the hold exactly
    # round 2: the fists still sat on top of the head; the arms go a little past vertical and the elbows open more
    # (-182 laid the arms back over the top, behind the head mass: THE CAMERA in RIG_SIGNS; -150 holds them straight up)
    ua_r = -150 * up + 130 * down + 20 * rec_r    # 0, -150 straight up (raised in front), -20 fists into the floor ahead, 0
    ua_l = -150 * up + 130 * down + 20 * rec_l
    fa = -6 * up + 6 * down                       # straight: the fists high above the head; straight at impact
    # the near arm comes in toward the centre line (away from the camera, so it draws higher): the fists meet over the head
    return {"upper_arm.R": (ua_r, 0, -25 * up + 25 * rec_r), "upper_arm.L": (ua_l, 0, 0), "forearm.R": (fa, 0, 0), "forearm.L": (fa, 0, 0),
            "body": (-6 * up + 9 * down - 3 * _seg(t, 0.70, 0.94) + 3 * shud, 0, 0),
            "head": (6 * head_up - 6 * down + 12 * head_impact, 0, 0),   # holds level against the lean, then drops with the blow
            "thigh.L": (12 * impact, 0, 0), "thigh.R": (12 * impact, 0, 0), "shin.L": (-32 * impact, 0, 0), "shin.R": (-32 * impact, 0, 0),
            "body_move": (0, -0.10 * down + 0.10 * _seg(t, 0.70, 0.94), 0),
            "stance": ["foot.L", "foot.R"] + (["hand.L", "hand.R"] if t < 0.03 or t >= 0.52 else [])}


def throw_pose(t):
    """Ballast Throw, right arm (rebuilt 2026-10-15 with RIG_SIGNS: v1 leaned forward where it meant back, and its
    "whip over the top" ran the arm back down behind the body). Tear 0-0.35: the arm reaches back and up over the
    shoulder to the back rack, elbow flexed, the torso turns toward it and leans back, hips locked. Load hold
    0.35-0.45. Hurl 0.45-0.55: the arm keeps going over the top and whips forward straight, the torso turns in and the
    body lunges. Plant 0.55-0.70: the hand comes down to the ground. Settle 0.70-1.0 in parts. The block itself is a
    separate sprite or effect."""
    tear_up = _seg(t, 0.0, 0.35)
    tear = _pulse(t, 0.0, 0.35, 0.45, 0.55)
    hurl_up = _seg(t, 0.45, 0.55)
    hurl = _pulse(t, 0.45, 0.55, 0.62, 0.78)
    plant = _seg(t, 0.55, 0.70)
    settle = _seg(t, 0.70, 0.96)
    head_settle = 1 - _seg(t, 0.76, 1.0)
    # (first render: at 115 the flexed forearm pointed back-DOWN, the hand by the hind legs; the elbow has to be up so
    # the flexed forearm points back over the shoulder to the rack)
    # blind review round 1: the hand stayed inside the back's outline at the rack, and the 18-degree forward pitch of the
    # lunge put the whole machine in the air (hind feet 9-23 px up)
    # round 2: the hand still sat at mid-flank, hidden by the torso; it goes higher and out to the near side. Round 3:
    # the raised arm vanished: at X 185 alone the hand crosses to the far side (x +0.13, measured), behind the body.
    # A Z sweep on the raised arm (Z acts differently once the arm is up: +55 hung it under the body) put Z -60 at the
    # elbow out on the near side and the hand up behind the shoulder at 2.5 m, at the rack.
    return {"upper_arm.R": (185 * tear_up + 115 * hurl_up + 60 * plant, 0, -60 * tear),   # 185 elbow up at the rack, 300 release, 360 planted
            "forearm.R": (-30 * tear_up + 30 * hurl_up, 0, 0), "hand.R": (-20 * tear - 25 * hurl, 0, 0),
            "upper_arm.L": (-8 * tear - 6 * hurl, 0, 6 * tear), "forearm.L": (-8 * tear, 0, 0),
            "body": (-10 * tear_up + 6 * hurl_up + 4 * settle, 0, 22 * tear - 18 * hurl),
            "head": (6 * tear - 4 * hurl * head_settle, 0, 20 * tear - 16 * hurl * head_settle),
            "thigh.L": (-8 * hurl, 0, 0), "thigh.R": (10 * hurl, 0, 0),
            "shin.L": (-8 * tear, 0, 0), "shin.R": (-8 * tear, 0, 0),
            "body_move": (0, 0.12 * tear - 0.20 * hurl, 0),
            "stance": ["hand.L", "foot.L", "foot.R"] + (["hand.R"] if t < 0.04 or t > 0.66 else [])}


def hit_pose(t):
    """Struck from the front: a sharp jolt back on frame 3, head snapped back, arms flung, then a heavy recovery."""
    k = _ease(t / 0.15) * (1 - _ease((t - 0.25) / 0.75))
    return {"body": (10 * k, 0, 0), "head": (-22 * k, 0, 0), "upper_arm.L": (14 * k, 0, 0),
            "upper_arm.R": (14 * k, 0, 0), "forearm.L": (10 * k, 0, 0), "forearm.R": (10 * k, 0, 0),
            "body_move": (0, 0.16 * k, 0.03 * k)}


def death_pose_v1(t):
    """Shut-down collapse: the arms buckle, the body drops and rolls onto its side, the head falls; holds at the end."""
    buckle = _ease(t / 0.4)
    fall = _ease((t - 0.25) / 0.55)
    return {"upper_arm.L": (-25 * buckle, 0, 0), "upper_arm.R": (-25 * buckle, 0, 0),
            "forearm.L": (55 * buckle, 0, 0), "forearm.R": (55 * buckle, 0, 0),
            "thigh.L": (20 * fall, 0, 0), "thigh.R": (20 * fall, 0, 0), "shin.L": (35 * fall, 0, 0), "shin.R": (35 * fall, 0, 0),
            "body": (8 * fall, 32 * fall, 0), "head": (18 * fall, 0, 15 * fall),
            "body_move": (0.12 * fall, 0, -0.6 * fall)}


def death_pose(t):
    """Shut-down collapse (rebuilt 2026-10-15): v1 rolled the body 32 degrees toward the camera, which stood the far
    side and its pods up (the silhouette 29 px taller, the top 11 rows above the battle screen) and read as a lift.
    Blind review round 1 of the rebuild: a 5-degree jolt back lifted the first frame 8 px, the pitch eased back after
    its lowest point (a rebound), and the tucked hind legs read as resting. Now: the head snaps as the power cuts, the
    arms give way forward and flat so the chest drops onto them, the pitch only ever goes down, the hind legs splay out
    behind so the belly and rump settle on the floor, a small roll toward the camera, the head droops last; held."""
    jolt = _pulse(t, 0.0, 0.06, 0.10, 0.22)
    give = _seg(t, 0.06, 0.42)    # round 2: the second frame still matched idle, so the arms give and the head sags sooner
    fall = _seg(t, 0.22, 0.72)
    sag = _seg(t, 0.10, 0.28)
    droop = _seg(t, 0.45, 0.95)
    # (the hips only come down if the hind legs swing far back: at 34 degrees the hips dropped 0.17 m and the body
    # stayed as tall as idle on one hind foot, and at 75 the near foot still held the hips 0.4 m up; 90 lays them out behind (100 tipped the feet 0.4 m up), and the body slides forward 0.3 m as it falls
    # so the legs stay inside the canvas, which cannot grow left)
    return {"upper_arm.L": (-50 * give, 0, 0), "upper_arm.R": (-50 * give, 0, 18 * give),   # forward and down onto the floor, the near one out
            "forearm.L": (-15 * give, 0, 0), "forearm.R": (-15 * give, 0, 0),
            "thigh.L": (90 * fall, 0, 0), "thigh.R": (90 * fall, 0, 0), "shin.L": (20 * fall, 0, 0), "shin.R": (20 * fall, 0, 0),   # laid out behind
            "body": (-2 * jolt + 14 * give - 14 * fall, 6 * fall, 0), "head": (-16 * jolt + 10 * sag + 26 * droop, 0, 14 * droop),
            "body_move": (0, -0.30 * fall, 0)}


def animation_set(rig):
    """Walk plus the first combat set (Preston, 2026-10-11: finished characters ship 7-17 clips, ours had one)."""
    clip(rig, "walk", 36, walk_pose)
    clip(rig, "gait", 36, gait_pose)   # animation pass 1: the loop to animate; "walk" stays the stance source
    clip(rig, "idle", 48, idle_pose)
    clip(rig, "punch", 36, punch_pose)   # animation pass 2: 1.5 s, the report's phase split
    clip(rig, "slam", 36, slam_pose)
    clip(rig, "throw", 36, throw_pose)
    clip(rig, "hit", 20, hit_pose)
    clip(rig, "death", 48, death_pose)
    for b in rig.pose.bones:   # back to the rest pose, so the size report, stills and saved file show the stance
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    bpy.context.view_layer.update()


# The loadout (2026-10-13, Preston: "weaponize it up ... wired up for later refinement"): the roster's three moves
# already have hardware (Piston Knuckles, the ballast rack, the fists); two spare hardpoints, DRAFT, his to name.
def weaponize():
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("weapons", os.path.join(os.path.dirname(os.path.abspath(__file__)), "weapons.py"))
    wpn = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wpn)
    A = wpn.anchor
    wpn.build_loadout(sys.modules[__name__], "ape_l", [
        {"slot": "shgun", "move": None, "kind": "gatling", "note": "spare: a rotary gun on the right shoulder",
         "args": {"base": A("shoulder_top_-1", (0.5, 0.45, 1.0), (0, 0, 0.1)), "direction": (0, -1, 0), "length": 0.8, "ring": 0.07, "r": 0.03}}
        if not V77 else
        {"slot": "backgun", "move": None, "kind": "cannon", "note": "spare: one big forward cannon along the right of the back (v77, Codex's)",
         "args": {"base": (-0.36, 0.22, 2.12), "direction": (0, -1, 0.1), "length": 1.2, "r": 0.12, "housing": (0.32, 0.42, 0.3),
                  "mat": "frame", "barrel_mat": "steel" if V78 else "frame", "tip_mat": "frame_dark"}},
        {"slot": "pod", "move": None, "kind": "missile_pod", "note": "spare: a 2x3 launcher on the left shoulder",
         "args": {"center": A("shoulder_top_1", (0.5, 0.5, 1.0), (0, 0, 0.15)), "size": (0.42, 0.36, 0.26), "rows": 2, "cols": 3, "rot": (-20, 0, 0)}},
    ])
    if V78:   # two dark bands round the back cannon's light barrel (named "barrel" so the detail pass leaves them)
        d = Vector((0, -1, 0.1)).normalized()
        a = Vector((-0.36, 0.22, 2.12)) + d * 0.42 * 0.3   # where weapons.cannon starts the barrel
        for k, f in enumerate((0.3, 0.62)):
            cyl("wpn_backgun_barrelband%d" % k, "frame", a + d * (1.2 * f), a + d * (1.2 * f + 0.07), 0.15, 16)


def _greebles():
    """The detail pass (tools/blender/greebles.py, 2026-10-14) on the gorilla's parts, checked against its bone rule."""
    import importlib.util, sys
    here = os.path.dirname(os.path.abspath(__file__))
    g, w = [importlib.util.spec_from_file_location(n, os.path.join(here, n + ".py")) for n in ("greebles", "weapons")]
    gm, wm = importlib.util.module_from_spec(g), importlib.util.module_from_spec(w)
    g.loader.exec_module(gm)
    w.loader.exec_module(wm)
    gm.run(sys.modules[__name__], wm, bone_for)


def _stretch_rear():
    """v77: everything behind the middle moves back STRETCH m, blended over the mid-body (smoothstep from y -0.6 to 0.8)
    so the torso stretches smoothly, and drops by up to REAR_DROP m in proportion to its height, so the feet stay on the
    floor and the hind legs come out squatter. The big body pieces bend vertex by vertex; every other part moves whole
    (discs and wheels stay round). The rig's joints move the same way."""
    y0, y1, ztop = -0.6, 0.8, 2.2

    def f(p):
        u = max(0.0, min(1.0, (p[1] - y0) / (y1 - y0)))
        w = u * u * (3 - 2 * u)
        return Vector((p[0], p[1] + STRETCH * w, p[2] - REAR_DROP * w * max(0.0, min(1.0, p[2] / ztop))))
    bpy.context.view_layer.update()
    bent = moved = 0
    for o in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
        M = o.matrix_world.copy()
        if o.name.startswith(("torso_shell", "rack_frame", "rack_mount", "back_plate")) and not re.search(r"_9\d\d$", o.name):
            if o.data.users > 1:
                o.data = o.data.copy()
            Mi = M.inverted()
            for v in o.data.vertices:
                v.co = Mi @ f(M @ v.co)
            bent += 1
        elif len(o.data.vertices):
            c = M @ (sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices))
            o.location += f(c) - c
            moved += 1
    for k, p in list(JOINTS.items()):
        JOINTS[k] = tuple(f(Vector(p)))
    print("V77 stretch: %d bent, %d moved" % (bent, moved))


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    build()
    weaponize()
    _greebles()
    if V77:
        _stretch_rear()
    tag_parts()
    ob = join_into_one()
    bake_atlas(ob)
    rig = make_rig(ob)
    knuckle_walk(rig)
    animation_set(rig)
    dims = tuple(round(v, 3) for v in ob.dimensions)
    os.makedirs(os.path.dirname(OUT_GLB), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    rig.select_set(True)
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, use_selection=True, export_format="GLB", export_apply=False,
                              export_skins=True, export_animations=True, export_animation_mode="NLA_TRACKS")
    rig.data.pose_position = "REST"   # stills and silhouettes show the rest pose
    cam, bg = lights_and_camera(bpy.context.scene)
    render_views(ob, cam)
    render_silhouettes(ob, cam, bg)
    rig.data.pose_position = "POSE"
    bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
    tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
    print("APE_L_V2_DONE dims=%s triangles=%d" % (dims, tris))


# The creature factory (2026-10-12) imports this file as its part kit (shell, plate, profile_solid, limb_solid, ...):
# with MECH_KIT_IMPORT=1 set, loading it builds nothing.
if os.environ.get("MECH_KIT_IMPORT") != "1":
    main()
