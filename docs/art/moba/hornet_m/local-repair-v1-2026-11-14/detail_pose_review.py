import bpy,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hornet_m/local-repair-v1-2026-11-14');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera
def shot(name,target,offset,frame):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=r['source'] if version=='before' else r['output']);bpy.context.view_layer.update();shot(version+'-head',(0,-1.05,.92),(3,-5,2),1.4);shot(version+'-wings',(0,.15,1.05),(3,-5,5),3.4)
 bpy.ops.object.light_add(type='AREA',location=(0,0,-3));fill=bpy.context.object;fill.data.energy=120;fill.data.size=3;fill.rotation_euler=(Vector((0,0,.4))-fill.location).to_track_quat('-Z','Y').to_euler();shot(version+'-underside-detail',(0,-.1,.4),(.1,.1,-5),3.3);bpy.data.objects.remove(fill,do_unlink=True)
rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==51
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);pts.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(pts)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);tests=[('body-root',0,6),('body-mid',1,6),('head',22,6),('face',20,6),('lower-front',44,6),('antenna-right',47,8),('antenna-right-tip',45,8),('antenna-left',50,-8),('antenna-left-tip',48,-8),('leg-left-A',27,8),('leg-left-A-tip',23,10),('leg-right-A',32,-8),('leg-right-A-tip',28,-10),('leg-left-B',9,8),('leg-left-B-tip',5,10),('leg-right-B',14,-8),('leg-right-B-tip',10,-10),('wing-right',37,8),('wing-right-tip',33,8),('wing-left',42,-8),('wing-left-tip',38,-8),('abdomen-root',19,8),('abdomen-mid',17,-8),('stinger',15,8)];checks={'tested_sha256':r['output_sha256'],'joint_count':51,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();diff=float(np.linalg.norm(posed-rest,axis=1).max());gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and diff>.001 and gap<1e-6,(label,diff,gap);checks['poses'].append({'label':label,'bone':pb.name,'degrees':angle,'max_displacement_m':diff,'coincident_surface_gap_m':gap})
 if label.startswith('antenna-'):target=(0,-1,1.15);frame=1.7;offset=(3,-5,2)
 elif label in ['head','face','lower-front']:target=(0,-1.05,.8);frame=1.6;offset=(3,-5,2)
 elif label.startswith('leg-'):target=(0,-.3,.4);frame=2.4;offset=(5,-6,3)
 elif label.startswith('wing-'):target=(0,.1,1.05);frame=3.5;offset=(3,-5,5)
 elif label.startswith('abdomen-') or label=='stinger':target=(0,.85,.55);frame=1.9;offset=(3,5,2)
 else:target=(0,0,.85);frame=3.6;offset=(3,-5,3)
 shot('pose-'+label,target,offset,frame)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update();text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('HORNET POSE CHECK PASS',len(checks['poses']),flush=True)
