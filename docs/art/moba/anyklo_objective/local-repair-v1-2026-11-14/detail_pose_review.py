import bpy,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera
rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==37

def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for face in me.polygons for i in face.vertices]);pts.extend(tuple(ev.matrix_world@me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(pts)
def reset():
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
def shot(name,target,offset,frame):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);checks={'tested_sha256':r['output_sha256'],'joint_count':37,'original_controls_tested':37,'poses':[],'no_surface_motion':[],'rendered_poses':[],'surface_motion_threshold_m':.001,'scope':'All 37 native controls tested in pitch; four tail controls additionally tested in yaw. Restored rest pose. Surface motion below 1 mm is classified separately.'}
render_bones=[0,3,5,7,8,11,12,13,16,17,18,24,27,28,31,32,33,35,36]
for bone,axis in [(i,0) for i in range(37)]+[(i,2) for i in [33,34,35,36]]:
 reset();pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';degrees=8 if bone%2==0 else -8;pb.rotation_euler[axis]+=math.radians(degrees);posed=surface();diff=float(np.linalg.norm(posed-rest,axis=1).max());gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and gap<1e-6,(bone,axis,diff,gap)
 label=f'bone-{bone:03}-'+('pitch' if axis==0 else 'yaw');item={'label':label,'bone':pb.name,'axis':'X' if axis==0 else 'Z','degrees':degrees,'max_displacement_m':diff,'coincident_surface_gap_m':gap};checks['poses' if diff>.001 else 'no_surface_motion'].append(item)
 if axis==0 and bone in render_bones:
  shot('pose-'+label,(0,0,.85),(4,-6,2.5),6.2);checks['rendered_poses'].append(label)
 if axis==2 and bone in [33,36]:shot('tail-pose-'+label,(0,2.1,1.05),(3,5,2),2.15)
reset();bpy.context.view_layer.update()
for im in list(bpy.data.images):
 if im.name.startswith('ORIGINAL_ANYKLO'):bpy.data.images.remove(im)
e=json.loads((ROOT/'model-entry.json').read_text())
for v,ref in e['views'].items():
 im=bpy.data.images.load(str(BASE/ref['path'].removeprefix('res://')),check_existing=False);im.name='ORIGINAL_ANYKLO_'+v;im.pack();im.use_fake_user=True
text=bpy.data.texts.new('ANYKLO_REPAIR_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('ANYKLO RIG CHECK PASS',len(checks['poses'])+len(checks['no_surface_motion']),'checks, max seam gap',max(x['coincident_surface_gap_m'] for x in checks['poses']),flush=True)
