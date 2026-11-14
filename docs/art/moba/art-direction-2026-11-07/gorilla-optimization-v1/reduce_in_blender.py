import bpy,json,time
from pathlib import Path
from mathutils import Vector
src=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-polish-v1/gorilla-source.glb')
out=Path('D:/dev/new-mech-rpg/docs/art/moba/art-direction-2026-11-07/gorilla-optimization-v1')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
def stats(ob):
 ob.data.calc_loop_triangles()
 world=[ob.matrix_world@Vector(c) for c in ob.bound_box]
 return {'object':ob.name,'triangles':len(ob.data.loop_triangles),'vertices':len(ob.data.vertices),'materials':len(ob.data.materials),
 'bounds_min':[min(p[i] for p in world) for i in range(3)],'bounds_max':[max(p[i] for p in world) for i in range(3)]}
source_stats=[stats(ob) for ob in meshes]
source_data={ob:ob.data.copy() for ob in meshes}
report={'source':str(src),'source_stats':source_stats,'method':'Blender collapse decimate; no remesh, no weld, no smooth or topology repair; UV data retained','variants':[]}
for target in [100000,40000]:
 start=time.time()
 for ob in meshes:
  ob.data=source_data[ob].copy()
  bpy.context.view_layer.objects.active=ob
  ob.select_set(True)
  mod=ob.modifiers.new(name=f'isolated_reduction_{target}',type='DECIMATE')
  mod.decimate_type='COLLAPSE'
  mod.ratio=target/sum(x['triangles'] for x in source_stats)
  mod.use_collapse_triangulate=True
  bpy.ops.object.modifier_apply(modifier=mod.name)
  ob.select_set(False)
 actual=[stats(ob) for ob in meshes]
 path=out/f'gorilla-{target//1000}k-4k.glb'
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',export_animations=False,export_yup=True,export_image_format='AUTO')
 report['variants'].append({'requested_triangles':target,'actual_stats':actual,'file':path.name,'seconds':round(time.time()-start,2),'file_bytes':path.stat().st_size})
 print('VARIANT',json.dumps(report['variants'][-1]),flush=True)
(out/'reduction-report.json').write_text(json.dumps(report,indent=2))
print('REDUCTION COMPLETE',flush=True)
