import bpy,json,sys,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/gold_beetle_objective/front-leg-restoration-v2-2026-11-13')
report=json.loads((OUT/'repair-verification.json').read_text());source=Path(report['output'])
bpy.ops.wm.open_mainfile(filepath='D:/dev/new-mech-rpg/docs/art/moba/gold_beetle_objective/repair-v1-2026-11-11/gold_beetle-objective-repaired-v1.blend')
scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
for ob in list(bpy.data.objects):
 if ob.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=report['source'] if '--before-only' in sys.argv else str(source));bpy.context.view_layer.update()
cam=scene.camera;cam.data.type='ORTHO'
def shot(name,target,offset,scale):
 cam.data.ortho_scale=scale;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
views=[('three-quarter',(0,0,.85),(7,-10,5),3.4),('front',(0,0,.85),(0,-10,.1),3.4),('side',(0,0,.85),(10,0,.1),3.4),('front-leg-outside',(.8,-.60,.36),(6,0,1),1.25),('front-leg-ahead',(.8,-.60,.36),(3,-6,1),1.25),('front-leg-behind',(.8,-.60,.36),(3,6,1),1.25),('opposite-front',(-.8,-.60,.36),(-6,0,1),1.25),('back',(0,0,.85),(0,10,.1),3.4),('right',(0,0,.85),(-10,0,.1),3.4),('underside',(0,0,.85),(0,0,-10),3.4),('top',(0,0,.85),(0,0,10),3.4)]
for name,target,offset,scale in views:
 if '--poses-only' in sys.argv:break
 if '--before-only' in sys.argv and name not in ['front-leg-outside','front-leg-ahead','front-leg-behind','opposite-front']:continue
 shot(('before-' if '--before-only' in sys.argv else 'after-')+name,target,offset,scale)
 if '--fast' in sys.argv and name=='front-leg-behind':print('PREVIEW COMPLETE',flush=True);sys.exit(0)
if '--before-only' in sys.argv:print('MATCHED BEFORE CLOSEUPS COMPLETE',flush=True);sys.exit(0)
rig=next(ob for ob in scene.objects if ob.type=='ARMATURE');meshes=[ob for ob in scene.objects if ob.type=='MESH' and len(ob.vertex_groups)];assert len(rig.data.bones)==23
rest_bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones}
def evaluated_surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();arr=[]
 for ob in meshes:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);arr.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(arr)
rest=evaluated_surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
tests=[('front-left','Bone_016',12),('front-left-ankle','Bone_015',12),('front-right','Bone_013',-12),('front-right-ankle','Bone_012',-12),('middle-left','Bone_010',10),('middle-right','Bone_007',-10),('rear-left','Bone_019',10),('rear-right','Bone_022',-10),('head','Bone_004',8),('mandibles','Bone_002',6),('shell','Bone_001',5)]
checks={'tested_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'joint_count':23,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
 pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle)
 posed=evaluated_surface();diff=np.linalg.norm(posed-rest,axis=1);gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and diff.max()>.001;assert gap<1e-6,(label,gap)
 checks['poses'].append({'label':label,'bone':bone,'degrees':angle,'max_displacement_m':float(diff.max()),'coincident_surface_gap_m':gap})
 target=(.8,-.60,.36) if label.startswith('front-right') else (-.8,-.60,.36) if label.startswith('front-left') else (0,0,.85)
 offset=(6,-3,1) if label.startswith('front-right') else (-6,-3,1) if label.startswith('front-left') else (7,-10,5)
 shot('pose-'+label,target,offset,1.4 if label.startswith('front-') else 3.4)
for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
bpy.context.view_layer.update();cam.data.ortho_scale=3.4;cam.location=Vector((7,-10,5.85));cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler()
text=bpy.data.texts.new('FRONT_LEG_REPAIR_V2');text.write(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(source.with_suffix('.blend')))
(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('FRONT LEG REVIEW PASS',json.dumps(checks),flush=True)
