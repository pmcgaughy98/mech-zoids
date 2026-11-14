import bpy,json,math
from pathlib import Path
import numpy as np
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==38
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);points.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(points)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
old=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13/visual-deformation-check.json');tests=json.loads(old.read_text())['poses'];checks={'tested_sha256':r['output_sha256'],'joint_count':38,'poses':[]}
for test in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 label=test['label'];pb=rig.pose.bones[test['bone']];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(test['degrees']);posed=surface();gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());diff=float(np.linalg.norm(posed-rest,axis=1).max());assert np.isfinite(posed).all() and gap<1e-6 and diff>.001,(label,gap,diff)
 checks['poses'].append({'label':label,'bone':test['bone'],'degrees':test['degrees'],'max_displacement_m':diff,'coincident_surface_gap_m':gap})
 target=Vector((0,.38,1.16)) if label in ['backplate-body','lower-body','wing-left','wing-right'] else Vector((0,0,.85));offset=Vector((3,5,2)) if target.z>1 else Vector((4,-5,2));cam=s.camera;cam.data.ortho_scale=.95 if target.z>1 else 2.006;cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('pose-'+label+'.png'));bpy.ops.render.render(write_still=True)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update();cam=s.camera;target=Vector((0,.38,1.16));cam.location=target+Vector((3,5,2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.95
provenance=bpy.data.texts.get('MODEL_REVIEW_PROVENANCE')
if provenance:provenance.name='BACKPLATE_V1_PROVENANCE_ARCHIVE'
text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('CIRCULAR RIM POSE CHECK PASS',len(checks['poses']),flush=True)
