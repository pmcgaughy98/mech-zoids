# Take a finished model apart and measure how it is built (Claude, 2026-10-11; Preston: "replicate some models by
# reverse engineering ... then use that to skill up"). Welds the seams a game export splits, then reports: pieces,
# triangles per piece, how many edges are smooth / chamfered / hard, chamfer width, and texture pixels per metre.
# Heights are normalised to 2.9 m so numbers compare with the gorilla. Reference models stay outside the project.
#   blender -b --factory-startup -P tools/blender/disassemble_model.py -- <model.fbx|.glb> <mesh name prefix>
# The pixels-per-metre line assumes a 1024 px sheet: double it for 2048.
"""Take a finished model apart: split into loose pieces, then measure how the pieces are made."""
import bpy, bmesh, glob, math, sys, statistics as st
from mathutils import Vector
f = sys.argv[sys.argv.index("--") + 1]
prefix = sys.argv[sys.argv.index("--") + 2]
bpy.ops.wm.read_factory_settings(use_empty=True)
(bpy.ops.import_scene.fbx if f.lower().endswith(".fbx") else bpy.ops.import_scene.gltf)(filepath=f)
ob = next(o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix))
me = ob.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.transform(bm, matrix=ob.matrix_world, verts=bm.verts)
h = max(v.co.z for v in bm.verts) - min(v.co.z for v in bm.verts)
k = 2.9 / h   # normalise to the gorilla's height so numbers compare
bmesh.ops.scale(bm, vec=(k, k, k), verts=bm.verts)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0015)   # weld the seams the game export split
bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# loose pieces
seen = set(); pieces = []
for f0 in bm.faces:
    if f0.index in seen: continue
    stack = [f0]; part = []
    seen.add(f0.index)
    while stack:
        f1 = stack.pop(); part.append(f1)
        for e in f1.edges:
            for f2 in e.link_faces:
                if f2.index not in seen: seen.add(f2.index); stack.append(f2)
    pieces.append(part)
tris = [sum(len(f.verts) - 2 for f in p) for p in pieces]
dims = []
for p in pieces:
    vs = {v for f in p for v in f.verts}
    lo = Vector([min(v.co[i] for v in vs) for i in range(3)]); hi = Vector([max(v.co[i] for v in vs) for i in range(3)])
    dims.append(sorted(hi - lo))
thin = sum(1 for d in dims if d[0] < 0.08 * d[2])
# edge sharpness: dihedral angle between faces
angles = [math.degrees(e.calc_face_angle()) for e in bm.edges if len(e.link_faces) == 2]
def share(lo, hi): return sum(1 for a in angles if lo <= a < hi) / len(angles)
# chamfer widths: short edges that are not smooth
sharp_len = [e.calc_length() for e in bm.edges if len(e.link_faces) == 2 and 25 <= math.degrees(e.calc_face_angle()) < 70]
# texel density: texture px per metre from UV vs world area (assume the colour map's size)
uv = bm.loops.layers.uv.active
area_w = sum(f.calc_area() for f in bm.faces)
def uv_area(f):
    pts = [l[uv].uv for l in f.loops]; a = 0
    for i in range(len(pts)): a += pts[i].x * pts[(i + 1) % len(pts)].y - pts[(i + 1) % len(pts)].x * pts[i].y
    return abs(a) / 2
area_uv = sum(uv_area(f) for f in bm.faces) if uv else 0
mats = len({f.material_index for f in bm.faces})
print("DIS %s: %d tris, %d pieces (median %d tris, largest %d), thin plates %d of %d" % (prefix, sum(tris), len(pieces), st.median(tris), max(tris), thin, len(pieces)))
print("DIS edges: smooth <25 deg %.0f%%, chamfer 25-70 %.0f%%, hard 70-110 %.0f%%, sharper %.0f%%" % (100*share(0,25), 100*share(25,70), 100*share(70,110), 100*share(110,181)))
print("DIS chamfer edge length median %.3f m (bevel width proxy)" % (st.median(sharp_len) if sharp_len else 0))
print("DIS texture: UV coverage %.2f of the sheet over %.1f m2 of surface; at 1024 px that is %.0f px per metre; %d material slots" % (area_uv, area_w, (area_uv ** 0.5) * 1024 / max(area_w, 1e-6) ** 0.5, mats))
