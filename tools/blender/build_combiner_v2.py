"""The combination machine, v2: one chimera beast from all six (Claude, 2026-10-19; Preston: "Rather than megazord or
humanoid mecha combination I'd like all the zoids to combine into one ultimate mecha-beast. So all parts detach and
combine into one rather than each mecha beast becoming one specific body part").

    "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup -P tools/blender/build_combiner_v2.py

Each machine is built from parts the factory tags to bones, and its finished mesh keeps one vertex group per bone
(body, head, tail.N, upper_arm/forearm/hand, thigh/shin/foot). v2 detaches those groups from all six machines in their
rest pose and reassembles them into one quadruped (docs/reference/combiner-v2-2026-10-19.md: the synthesis):
  front half  gorilla body with its arms as the knuckle-walking forelegs (its own head and legs left off)
  head        wolf head, on the gorilla's neck
  hindquarters hippo body, behind the gorilla's
  hind legs   kangaroo legs, under the hippo body
  back armour pangolin body laid over the hippo's back; pangolin tail off the rump
  wings       shoebill wings on the shoulders; the shoebill head rising from the back (the chimera's second head)
A proposal: Preston decides the mapping. Output docs/art/3d/combiner_v2.blend for the factory's sprite renderer.
"""
import bmesh, bpy, math, os, re
from mathutils import Matrix, Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "docs", "art", "3d", "combiner_v2.blend")
FILES = {"ape_l": "ape_l_v2"}
SCALE = {"ape_l": 1.5, "wolf_m": 1.25, "hippo_m": 1.35, "kangaroo_m": 1.35, "pangolin_m": 1.3, "shoebill_m": 1.0}
ARM = re.compile(r"^(upper_arm|forearm|hand)\.")
LEG = re.compile(r"^(thigh|shin|foot)\.")


def load(mid):
    """The machine's mesh in its rest pose, scaled, with its vertex groups (one per bone)."""
    path = os.path.join(ROOT, "docs", "art", "3d", FILES.get(mid, mid) + ".blend")
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = list(src.objects)
    objs = [o for o in dst.objects if o is not None]
    meshes = [o for o in objs if o.type == "MESH"]
    body = max(meshes, key=lambda o: len(o.data.polygons))
    bpy.context.scene.collection.objects.link(body)
    for m in list(body.modifiers):
        body.modifiers.remove(m)   # the rig's armature: rest pose is the mesh as built
    body.parent = None
    body.matrix_world = Matrix.Scale(SCALE[mid], 4) @ body.matrix_world
    for o in objs:
        if o is not body and o.users_scene == ():
            pass
    print("GROUPS %s %s" % (mid, sorted({g.name for g in body.vertex_groups})))
    return body


def part(src, name, keep):
    """A copy of src holding only the vertices whose strongest group matches keep(group name)."""
    ob = src.copy()
    ob.data = src.data.copy()
    ob.name = name
    bpy.context.scene.collection.objects.link(ob)
    names = {g.index: g.name for g in ob.vertex_groups}
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    dl = bm.verts.layers.deform.active
    drop = []
    for v in bm.verts:
        w = v[dl] if dl else {}
        best = max(w.items(), key=lambda kv: kv[1])[0] if w else None
        if best is None or not keep(names.get(best, "")):
            drop.append(v)
    bmesh.ops.delete(bm, geom=drop, context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def bbox(o):
    """From the vertices themselves (bound_box stays stale after a bmesh cut until the depsgraph updates)."""
    mw = o.matrix_world
    cs = [mw @ v.co for v in o.data.vertices] or [mw.translation]
    return (Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))),
            Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs))))


def move(objs, d):
    for o in objs:
        o.matrix_world = Matrix.Translation(d) @ o.matrix_world
    bpy.context.view_layer.update()


def union(objs):
    bs = [bbox(o) for o in objs]
    return (Vector((min(b[0].x for b in bs), min(b[0].y for b in bs), min(b[0].z for b in bs))),
            Vector((max(b[1].x for b in bs), max(b[1].y for b in bs), max(b[1].z for b in bs))))


bpy.ops.wm.read_factory_settings(use_empty=True)
M = {mid: load(mid) for mid in SCALE}
bpy.context.view_layer.update()

# front half: the gorilla's body and arms, forelegs on the floor
g_front = part(M["ape_l"], "g_front", lambda n: n == "body" or bool(ARM.match(n)))
g_head = part(M["ape_l"], "g_head_ref", lambda n: n == "head")
gmn, gmx = union([g_front])
move([g_front, g_head], Vector((-(gmn.x + gmx.x) / 2, -1.6 - (gmn.y + gmx.y) / 2, -gmn.z)))
g_body = part(M["ape_l"], "g_body_ref", lambda n: n == "body")   # only for measuring
move([g_body], Vector((-(gmn.x + gmx.x) / 2, -1.6 - (gmn.y + gmx.y) / 2, -gmn.z)))
bmn, bmx = bbox(g_body)
hmn, hmx = bbox(g_head)

# head: the wolf's, where the gorilla's head was, a little forward
w_head = part(M["wolf_m"], "w_head", lambda n: n == "head")
a, b = bbox(w_head)
move([w_head], Vector((-(a.x + b.x) / 2, bmn.y + 0.35 - b.y, bmx.z - 0.55 - (b.z - a.z) / 2 - (a.z + b.z) / 2 + (b.z - a.z) / 2)))   # its back sunk 35 cm into the body's front, its top level with the shoulders

# hindquarters: the hippo's body behind the gorilla's
h_body = part(M["hippo_m"], "h_body", lambda n: n == "body")
a, b = bbox(h_body)
move([h_body], Vector((-(a.x + b.x) / 2, bmx.y - 0.35 - a.y, (bmn.z + bmx.z) / 2 - 0.15 - (a.z + b.z) / 2)))
hbmn, hbmx = bbox(h_body)

# hind legs: the kangaroo's, under the rear of the hippo body, feet on the floor
k_legs = part(M["kangaroo_m"], "k_legs", lambda n: bool(LEG.match(n)))
a, b = bbox(k_legs)
move([k_legs], Vector((-(a.x + b.x) / 2, (hbmn.y + hbmx.y) / 2 + 0.25 - (a.y + b.y) / 2, -a.z)))

# back armour: the pangolin's body over the hippo's back; its tail off the rump
p_body = part(M["pangolin_m"], "p_shell", lambda n: n == "body")
a, b = bbox(p_body)
move([p_body], Vector((-(a.x + b.x) / 2, (hbmn.y + hbmx.y) / 2 - 0.3 - (a.y + b.y) / 2, hbmx.z - 0.45 - a.z)))
p_tail = part(M["pangolin_m"], "p_tail", lambda n: n.startswith("tail"))
a, b = bbox(p_tail)
move([p_tail], Vector((-(a.x + b.x) / 2, hbmx.y - 0.35 - a.y, (hbmn.z + hbmx.z) / 2 + 0.1 - b.z + (b.z - a.z) * 0.35)))

# wings on the shoulders, the shoebill's head rising from the back between them
s_wings = part(M["shoebill_m"], "s_wings", lambda n: bool(ARM.match(n)))
a, b = bbox(s_wings)
move([s_wings], Vector((-(a.x + b.x) / 2, (bmn.y + bmx.y) / 2 + 0.2 - (a.y + b.y) / 2, bmx.z - 0.55 - a.z)))
s_head = part(M["shoebill_m"], "s_head", lambda n: n == "head")
a, b = bbox(s_head)
move([s_head], Vector((-(a.x + b.x) / 2, (bmn.y + bmx.y) / 2 + 0.55 - (a.y + b.y) / 2, bmx.z + 0.15 - a.z)))

keep = [g_front, w_head, h_body, k_legs, p_body, p_tail, s_wings, s_head]
for o in list(bpy.context.scene.objects):
    if o not in keep:
        bpy.data.objects.remove(o, do_unlink=True)
for o in keep:
    a, b = bbox(o)
    print("COMBINER_PART %-8s x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (o.name, a.x, b.x, a.y, b.y, a.z, b.z))
bpy.ops.object.select_all(action="DESELECT")
for o in keep:
    o.select_set(True)
bpy.context.view_layer.objects.active = keep[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.join()
ob = bpy.context.view_layer.objects.active
ob.name = "combiner_v2"
mn, mx = bbox(ob)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print("COMBINER_DONE dims=%s tris=%d" % (tuple(round(v, 2) for v in (mx - mn)), sum(len(p.vertices) - 2 for p in ob.data.polygons)))
