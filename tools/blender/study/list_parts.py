# How a finished machine is split into parts, and how it is built overall. Height normalised to 2.9 m.
import bpy, bmesh, sys, math, statistics as st
from mathutils import Vector
p = sys.argv[sys.argv.index("--") + 1]
if p.lower().endswith(".blend"):
    bpy.ops.wm.open_mainfile(filepath=p)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    (bpy.ops.import_scene.fbx if p.lower().endswith(".fbx") else bpy.ops.import_scene.gltf)(filepath=p)
dg = bpy.context.evaluated_depsgraph_get()
obs = [o for o in bpy.data.objects if o.type == "MESH"]
lo = Vector((1e9,) * 3)
hi = Vector((-1e9,) * 3)
for o in obs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        lo = Vector(map(min, lo, w))
        hi = Vector(map(max, hi, w))
k = 2.9 / max(hi.z - lo.z, 1e-6)
rows = []
angles = []
sharp_len = []
total = 0
for o in obs:
    me = o.evaluated_get(dg).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.transform(bm, matrix=o.matrix_world, verts=bm.verts)
    bmesh.ops.scale(bm, vec=(k, k, k), verts=bm.verts)
    tris = sum(len(f.verts) - 2 for f in bm.faces)
    total += tris
    if bm.verts:
        vs = [v.co for v in bm.verts]
        mn = Vector([min(v[i] for v in vs) for i in range(3)])
        mx = Vector([max(v[i] for v in vs) for i in range(3)])
        rows.append((o.name, tris, (mn + mx) / 2, mx - mn, len(o.data.materials)))
    for e in bm.edges:
        if len(e.link_faces) == 2:
            a = math.degrees(e.calc_face_angle())
            angles.append(a)
            if 25 <= a < 70:
                sharp_len.append(e.calc_length())
    bm.free()
    o.evaluated_get(dg).to_mesh_clear()
print("PARTS %s: %d mesh objects, %d tris, %d materials, size %.2f x %.2f x %.2f m (x y z)" % (
    p.split("/")[-1], len(obs), total, len(bpy.data.materials), (hi.x - lo.x) * k, (hi.y - lo.y) * k, 2.9))
def share(a, b): return 100.0 * sum(1 for x in angles if a <= x < b) / max(len(angles), 1)
print("PARTS edges: smooth <25 %.0f%%, chamfer 25-70 %.0f%%, hard 70-110 %.0f%%, sharper %.0f%%; chamfer edge median %.3f m" % (
    share(0, 25), share(25, 70), share(70, 110), share(110, 181), st.median(sharp_len) if sharp_len else 0))
rows.sort(key=lambda r: -r[2].z)
print("PARTS top parts by height (name, tris, centre y z, size x y z):")
for name, tris, c, s, nm in rows[:40]:
    print("  %-30s %6d  c(%.2f %.2f %.2f) s(%.2f %.2f %.2f) mats %d" % (name[:30], tris, c.x, c.y, c.z, s.x, s.y, s.z, nm))
