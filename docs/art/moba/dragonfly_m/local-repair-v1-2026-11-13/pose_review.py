import bpy,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==46
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);points.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(points)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);tests=[('front-left',6,10),('front-right',9,-10),('middle-left',15,10),('middle-right',12,-10),('rear-left',18,10),('rear-right',21,-10),('lower-wing-left',33,8),('lower-wing-right',35,-8),('upper-wing-left',37,8),('upper-wing-right',39,-8),('head',3,6),('antenna-left',45,6),('antenna-right',42,-6),('tail-root',31,8),('tail-middle',30,-8),('removed-pair2-left',27,20),('removed-pair2-right',24,-20)];checks={'tested_sha256':r['output_sha256'],'joint_count':46,'poses':[]};cam=s.camera;span=2.3158
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());diff=float(np.linalg.norm(posed-rest,axis=1).max());assert np.isfinite(posed).all() and gap<1e-6,(label,gap);assert diff<1e-6 if label.startswith('removed-') else diff>.001,(label,diff)
 checks['poses'].append({'label':label,'bone':pb.name,'degrees':angle,'max_displacement_m':diff,'coincident_surface_gap_m':gap});target=Vector((0,-.09,.87)) if 'front' in label or 'removed' in label else Vector((0,0,.85));cam.data.ortho_scale=.95 if target.y<0 else 2.733;cam.location=target+Vector((4,-5,2))*span;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('pose-'+label+'.png'));bpy.ops.render.render(write_still=True)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update()
for side in [-1,1]:
 target=Vector((side*.24,-.09,.91));cam.data.ortho_scale=.45;cam.location=target+Vector((side*5,-3,2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('socket-'+('left' if side<0 else 'right')+'.png'));bpy.ops.render.render(write_still=True)
text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('DRAGONFLY POSE CHECK PASS',len(checks['poses']),flush=True)
