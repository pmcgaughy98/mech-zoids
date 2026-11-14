import bpy,json,math,sys
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/falcon_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera
def shot(name,target,offset,frame):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','after']:
 if '--poses-only' in sys.argv:continue
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=r['source'] if version=='before' else r['output']);bpy.context.view_layer.update()
 for i,cap in enumerate(r['holes_closed']):
  if '--feet-only' in sys.argv:continue
  center=(np.array(cap['bounds'][0])+np.array(cap['bounds'][1]))/2;normal=cap['normal'];target=(center[0],-center[2],center[1]);offset=Vector((normal[0],-normal[2],normal[1]))*5;frame=max(.22,float(np.linalg.norm(np.array(cap['bounds'][1])-cap['bounds'][0]))*4);shot(f'{version}-patch-{i+1}',target,offset,frame)
 if '--feet-only' not in sys.argv:
  shot(version+'-head',(0,-.95,1.35),(3,-5,2),1.1);shot(version+'-tail',(0,.95,.55),(3,5,2),1.1)
 bpy.ops.object.light_add(type='AREA',location=(1,-.1,-2));fill=bpy.context.object;fill.data.energy=90;fill.data.size=2;fill.rotation_euler=(Vector((.48,-.4,.12))-fill.location).to_track_quat('-Z','Y').to_euler();shot(version+'-feet',(.48,-.40,.12),(.2,.2,-5),1.05);bpy.data.objects.remove(fill,do_unlink=True)
 bpy.ops.object.light_add(type='AREA',location=(-1,-.1,-2));fill=bpy.context.object;fill.data.energy=90;fill.data.size=2;fill.rotation_euler=(Vector((-.48,-.4,.12))-fill.location).to_track_quat('-Z','Y').to_euler();shot(version+'-feet-left',(-.48,-.40,.12),(-.2,.2,-5),1.05);bpy.data.objects.remove(fill,do_unlink=True)
 if '--feet-only' not in sys.argv:
  for i,cap in enumerate(r['toe_socket_closures']):
   cx,cy,cz=cap['center'];nx,ny,nz=cap['normal'];target=Vector((cx,-cz,cy));normal=Vector((nx,-nz,ny));bpy.ops.object.light_add(type='AREA',location=target+normal*1.5);fill=bpy.context.object;fill.data.energy=20;fill.data.size=1;fill.rotation_euler=(-normal).to_track_quat('-Z','Y').to_euler();shot(f'{version}-toe-socket-{i+1}',target,normal*5,.35);bpy.data.objects.remove(fill,do_unlink=True)
if '--feet-only' in sys.argv:sys.exit(0)
rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==45
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);pts.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(pts)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);tests=[('body-root',0,6),('tail-base',4,8),('tail-tip',2,-8),('wing-right',18,8),('wing-right-tip',17,10),('wing-left',20,-8),('wing-left-tip',19,-10),('neck',24,6),('head',22,6),('beak',21,-6),('leg-right',12,8),('ankle-right',10,-8),('foot-right',9,6),('leg-left',16,-8),('ankle-left',14,8),('foot-left',13,-6),('toe-right',32,8),('toe-left',44,-8),('rear-toe-right',26,8),('rear-toe-left',36,-8),('removed-right-root',28,10),('removed-right-tip',27,12),('removed-left-root',38,-10),('removed-left-tip',37,-12)];checks={'tested_sha256':r['output_sha256'],'joint_count':45,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();diff=float(np.linalg.norm(posed-rest,axis=1).max());gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and (diff<1e-7 if label.startswith('removed-') else diff>.001) and gap<1e-6,(label,diff,gap);checks['poses'].append({'label':label,'bone':pb.name,'degrees':angle,'max_displacement_m':diff,'coincident_surface_gap_m':gap})
 target=(0,-.85,1.25) if label in ['head','beak','neck'] else (0,.75,.55) if 'tail-' in label else (0,-.35,.3) if any(t in label for t in ['foot-','toe-','ankle-']) else (0,0,.85);frame=1.4 if label in ['head','beak','neck'] or 'tail-' in label or any(t in label for t in ['foot-','toe-','ankle-']) else 2.9
 shot('pose-'+label,target,(3,5,2) if 'tail-' in label else (5,-6,3),frame)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update();text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('FALCON POSE CHECK PASS',len(checks['poses']),flush=True)
