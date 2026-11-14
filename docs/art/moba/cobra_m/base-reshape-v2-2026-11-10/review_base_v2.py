import bpy,json,math,sys,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/base-reshape-v2-2026-11-10')
OLD=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10')
bpy.ops.wm.open_mainfile(filepath=str(OLD/'cobra-rigged-local-repair-v1.blend'))
scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=16
def shot(name,center,offset,scale):
 cam.data.ortho_scale=scale;cam.location=Vector(center)+Vector(offset);cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
report={'poses':[],'tested_glb_sha256':hashlib.sha256((OUT/'cobra-rigged-base-reshape-v2.glb').read_bytes()).hexdigest()}
for version in ['before','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 path=OLD/'cobra-rigged-local-repair-v1.glb' if version=='before' else OUT/'cobra-rigged-base-reshape-v2.glb'
 bpy.ops.import_scene.gltf(filepath=str(path));ob=next(o for o in scene.objects if o.type=='MESH' and len(o.vertex_groups));rig=next(o for o in scene.objects if o.type=='ARMATURE')
 if '--final' not in sys.argv:
  for name,offset in [('left',(3,0,.2)),('right',(-3,0,.2)),('front',(0,-3,.15)),('back',(0,3,.15)),('base-three-quarter',(2,-3,1)),('underside',(0,0,-3))]:
   if version=='after' or not (OUT/(version+'-'+name+'.png')).exists():shot(version+'-'+name,(.067,-.85,.3),offset,1.5)
  if version=='after' or not (OUT/(version+'-whole.png')).exists():shot(version+'-whole',(0,0,.85),(6,-9,6),3.6)
 if version=='after' and '--final' in sys.argv:
  for name,offset in [('front',(0,-9,.15)),('side',(9,0,.15)),('right',(-9,0,.15)),('back',(0,9,.15)),('underside',(0,-.9,-9)),('three-quarter',(6,-9,6))]:shot('repaired-'+name,(0,0,.85),offset,3.114*1.16)
 if version=='after':
  dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();rest=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear()
  for bone,angle in [('Bone_001',8),('Bone_001',-8),('Bone_014',10),('Bone_014',-10)]:
   for pb in rig.pose.bones:pb.matrix_basis.identity()
   pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x=math.radians(angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(v.co) for v in me.vertices]);disp=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all() and disp.max()>.001
   t=np.array([tuple(f.vertices) for f in me.polygons if len(f.vertices)==3]);edges=np.concatenate([t[:,[0,1]],t[:,[1,2]],t[:,[2,0]]]);length0=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1);length1=np.linalg.norm(posed[edges[:,0]]-posed[edges[:,1]],axis=1);ratios=length1[length0>1e-4]/length0[length0>1e-4]
   buckets={}
   for vi,point in enumerate(rest):buckets.setdefault(tuple(np.round(point,6)),[]).append(vi)
   seams=[float(np.linalg.norm(posed[ids]-posed[ids[0]],axis=1).max()) for ids in buckets.values() if len(ids)>1]
   report['poses'].append({'bone':bone,'local_x_degrees':angle,'finite':True,'vertices_moved_over_1mm':int((disp>.001).sum()),'max_displacement':float(disp.max()),'edge_stretch_ratio_99th_percentile':float(np.percentile(ratios,99)),'edge_stretch_ratio_max':float(ratios.max()),'maximum_uv_split_position_gap_m':max(seams,default=0)});ev.to_mesh_clear();shot(f'pose-{bone}-{angle}',(.067,-.85,.3),(2,-3,1),1.5)
  for pb in rig.pose.bones:pb.matrix_basis.identity()
  bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cobra-base-reshape-v2.blend'))
(OUT/'deformation-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
