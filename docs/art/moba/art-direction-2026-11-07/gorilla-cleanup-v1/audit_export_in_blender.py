import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
src=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1/gorilla-connected-100k-2k.glb')
out=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
def components(bm):
 bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
 unseen=set(bm.verts)
 result=[]
 while unseen:
  first=unseen.pop();stack=[first];vs=[first]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in unseen:unseen.remove(n);stack.append(n);vs.append(n)
  faces={f for v in vs for f in v.link_faces}
  lo=[min(v.co[i] for v in vs) for i in range(3)]
  hi=[max(v.co[i] for v in vs) for i in range(3)]
  result.append({'vertices':len(vs),'faces':len(faces),'lo':lo,'hi':hi,'center':[(lo[i]+hi[i])/2 for i in range(3)],'dimensions':[hi[i]-lo[i] for i in range(3)]})
 return sorted(result,key=lambda x:x['faces'],reverse=True)
report=[]
for ob in objects:
 bm=bmesh.new();bm.from_mesh(ob.data)
 for v in bm.verts:v.co=ob.matrix_world@v.co
 original_components=components(bm)
 before=len(bm.verts)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 welded_components=components(bm)
 report.append({'object':ob.name,'uv_seam_split_vertices':before,'position_welded_vertices':len(bm.verts),'connected_components_before':len(original_components),'connected_components_after_position_weld':len(welded_components),'top_components':welded_components[:40],
 'boundary_edges_after_weld':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges_after_weld':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'wire_edges':sum(e.is_wire for e in bm.edges),'isolated_vertices':sum(not v.link_edges for v in bm.verts),'custom_normals':ob.data.has_custom_normals,
 'small_components_under_10_faces':[c for c in welded_components if c['faces']<10]})
 bm.free()
(out/'exported-topology-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2)[:9000],flush=True)
print('AUDIT COMPLETE; SOURCE UNMODIFIED',flush=True)
