# Do the hard edges shade crisp in the exported file? (Claude, 2026-10-12, pass 21.) This found that every chamfer on
# the gorilla had shipped smeared: the sharpening lived in a modifier, and the export keeps modifiers off so the rig
# stays live. Game files for comparison: Grimlock 77% and Megatron 83% of hard edges split-shaded; ours was 0%, now 70%.
#   blender -b --factory-startup -P tools/blender/probe_hard_edges.py -- <model.glb|.fbx> [more files]
# Records each face corner's shading normal, welds the export's split vertices back together, then at every edge whose
# faces meet at more than 30 degrees compares the two sides: split (a crisp chamfer) or averaged (a smeared edge).
import bpy, bmesh, sys, math
from mathutils import Vector
for p in sys.argv[sys.argv.index("--") + 1:]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    (bpy.ops.import_scene.fbx if p.lower().endswith(".fbx") else bpy.ops.import_scene.gltf)(filepath=p)
    ob = max((o for o in bpy.data.objects if o.type == "MESH"), key=lambda o: len(o.data.polygons))
    me = ob.data
    cn = [Vector(c.vector) for c in me.corner_normals]
    key = {}
    for poly in me.polygons:
        for li in range(poly.loop_start, poly.loop_start + poly.loop_total):
            v = me.vertices[me.loops[li].vertex_index].co
            key[(poly.index, round(v.x, 4), round(v.y, 4), round(v.z, 4))] = cn[li]
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.faces.layers.int.new("orig")
    for f in bm.faces:
        f[lay] = f.index
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.normal_update()
    hard = split = 0
    for e in bm.edges:
        if len(e.link_faces) != 2:
            continue
        a, b = e.link_faces
        if math.degrees(a.normal.angle(b.normal, 0.0)) < 30:
            continue
        v = e.verts[0].co
        k = (round(v.x, 4), round(v.y, 4), round(v.z, 4))
        na, nb = key.get((a[lay],) + k), key.get((b[lay],) + k)
        if na is None or nb is None:
            continue
        hard += 1
        if math.degrees(na.angle(nb, 0.0)) > 5:
            split += 1
    tris = sum(len(q.vertices) - 2 for q in me.polygons)
    print("NRM %s [%s]: verts %d, tris %d, hard edges %d, split-shaded %d (%.0f%%)"
          % (p.split("/")[-1], ob.name, len(me.vertices), tris, hard, split, 100.0 * split / max(hard, 1)))
