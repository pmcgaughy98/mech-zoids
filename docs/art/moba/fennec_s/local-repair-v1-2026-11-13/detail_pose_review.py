import bpy,json,math,sys
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/fennec_s/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera
def shot(name,target,offset,frame):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','after']:
 if '--rear-only' in sys.argv:continue
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=r['source'] if version=='before' else r['output']);bpy.context.view_layer.update()
 for i,cap in enumerate(r['holes_closed']):
  center=(np.array(cap['bounds'][0])+np.array(cap['bounds'][1]))/2;nx,ny,nz=cap['normal'];target=Vector((center[0],-center[2],center[1]));normal=Vector((nx,-nz,ny));bpy.ops.object.light_add(type='AREA',location=target+normal*1.5);fill=bpy.context.object;fill.data.energy=12;fill.data.size=1;fill.rotation_euler=(-normal).to_track_quat('-Z','Y').to_euler();shot(f'{version}-patch-{i+1}',target,normal*5,.18);bpy.data.objects.remove(fill,do_unlink=True)
 shot(version+'-head',(0,-1.02,.9),(3,-5,2),1.0);shot(version+'-ears',(0,-.7,1.25),(2,-5,2),1.25);shot(version+'-tail',(0,.7,.48),(3,5,2),1.55)
rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==44
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);pts.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(pts)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);tests=[('body-root',0,6),('neck',1,6),('head',3,6),('muzzle',37,6),('ear-right',40,8),('ear-right-tip',38,8),('ear-left',43,-8),('ear-left-tip',41,-8),('front-leg-right',24,8),('front-ankle-right',22,-8),('front-leg-left',19,-8),('front-ankle-left',17,8),('rear-leg-right',9,8),('rear-ankle-right',7,-8),('rear-leg-left',14,-8),('rear-ankle-left',12,8),('tail-root',33,8),('tail-mid',30,-8),('tail-tip',25,8)];checks={'tested_sha256':r['output_sha256'],'joint_count':44,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();diff=float(np.linalg.norm(posed-rest,axis=1).max());gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and diff>.001 and gap<1e-6,(label,diff,gap);checks['poses'].append({'label':label,'bone':pb.name,'degrees':angle,'max_displacement_m':diff,'coincident_surface_gap_m':gap})
 target=(0,-.8,1.1) if label.startswith('ear-') else (0,-1,.85) if label in ['head','neck','muzzle'] else (0,.6,.5) if 'tail-' in label else (0,0,.85);frame=1.4 if label.startswith('ear-') else 1.1 if label in ['head','neck','muzzle'] else 1.8 if 'tail-' in label else 3
 if '--rear-only' not in sys.argv or label.startswith('rear-'):shot('pose-'+label,target,(3,5,2) if 'tail-' in label else (5,-6,3),frame)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update();text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('FENNEC POSE CHECK PASS',len(checks['poses']),flush=True)
