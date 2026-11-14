import bpy,bmesh,json
from pathlib import Path
from array import array
src=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-polish-v1/gorilla-source.glb')
out=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-cleanup-v1')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
def stats(me):
 bm=bmesh.new();bm.from_mesh(me)
 r={'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'wire_edges':sum(e.is_wire for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'custom_normals':me.has_custom_normals}
 bm.free();return r
report={'source':str(src),'weld_distance_source_units':1e-6,'changes':[]}
for ob in objects:
 me=ob.data
 before=stats(me)
 # Corner-domain storage carries each split normal through the positional weld.
 saved=me.attributes.new('_source_corner_normal','FLOAT_VECTOR','CORNER')
 values=array('f',[0.0])*(len(me.loops)*3)
 me.corner_normals.foreach_get('vector',values)
 saved.data.foreach_set('vector',values)
 bm=bmesh.new();bm.from_mesh(me)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
 bm.to_mesh(me);bm.free();me.update()
 normals=[tuple(v.vector) for v in me.attributes['_source_corner_normal'].data]
 me.normals_split_custom_set(normals)
 me.attributes.remove(me.attributes['_source_corner_normal'])
 welded=stats(me)
 bpy.context.view_layer.objects.active=ob
 ob.select_set(True)
 mod=ob.modifiers.new('topology_connected_reduction','DECIMATE')
 mod.decimate_type='COLLAPSE';mod.ratio=100000/len(me.polygons);mod.use_collapse_triangulate=True
 bpy.ops.object.modifier_apply(modifier=mod.name)
 after=stats(ob.data)
 report['changes'].append({'object':ob.name,'imported':before,'after_weld':welded,'after_reduction':after})
 print(json.dumps(report['changes'][-1]),flush=True)
path=out/'gorilla-connected-100k-4k.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_animations=False,export_yup=True,export_image_format='AUTO')
for ob in objects:
 ob['source']='Current MeshForge Gorilla_s'
 ob['articulation_status']='Static mesh only; no rig, no weights. Weld-before-reduction cleanup pilot.'
 ob['chosen_visual_direction']='Refined D; applied separately in Godot preview.'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'gorilla-connected-cleanup.blend'))
(out/'cleanup-report.json').write_text(json.dumps(report,indent=2))
print('CONNECTED CLEANUP COMPLETE',flush=True)
