import bpy,json,math,sys
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());native=Path(r['output']).with_suffix('.blend');bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera
def shot(name,target,offset,frame):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=r['source'] if version=='before' else r['output']);bpy.context.view_layer.update()
 for i,cap in enumerate(r['holes_closed']):
  if '--fork-only' in sys.argv:continue
  if '--finish-only' in sys.argv and (version!='after' or i!=5):continue
  center=(np.array(cap['bounds'][0])+np.array(cap['bounds'][1]))/2;normal=cap['normal'];target=(center[0],-center[2],center[1]);offset=Vector((normal[0],-normal[2],normal[1]))*5;frame=max(.25,float(np.linalg.norm(np.array(cap['bounds'][1])-cap['bounds'][0]))*4);shot(f'{version}-patch-{i+1}',target,offset,frame)
 if '--finish-only' not in sys.argv:
  if '--fork-only' not in sys.argv:shot(version+'-head',(0,-5.2,.8),(5,-6,3),4.0)
  shot(version+'-fork',(0,5.85,.6),(5,6,3),2.0)
if '--fork-only' in sys.argv:sys.exit(0)
rig=next(o for o in s.objects if o.type=='ARMATURE');objects=[o for o in s.objects if o.type=='MESH' and len(o.vertex_groups)];bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones};assert len(bases)==56
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([i for f in me.polygons for i in f.vertices]);pts.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(pts)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True);tests=[('body-root',0,6),('body-mid',4,8),('body-rear',17,-8),('tail-root',23,8),('fork-right',33,8),('fork-left',37,-8),('removed-upper-root',48,8),('removed-upper-mid',47,12),('removed-upper-tip',46,12),('head-right',49,6),('head-left',38,-6),('fin-right',53,10),('fin-left',55,-10),('dorsal-rear',10,6),('dorsal-mid',22,6),('dorsal-front',32,-6),('dorsal-fore',42,6),('head-roof',51,-6)];checks={'tested_sha256':r['output_sha256'],'joint_count':56,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
 pb=rig.pose.bones[f'Bone_{bone:03}'];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();diff=float(np.linalg.norm(posed-rest,axis=1).max());gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and (diff<1e-7 if label.startswith('removed-') else diff>.001) and gap<1e-6,(label,diff,gap)
 checks['poses'].append({'label':label,'bone':pb.name,'degrees':angle,'max_displacement_m':diff,'coincident_surface_gap_m':gap})
 if '--finish-only' not in sys.argv:shot('pose-'+label,(0,-4.8,.8) if 'head' in label or 'fin-' in label else (0,5.3,.65) if 'fork' in label else (0,0,.85),(12,-5,4),4.5 if 'head' in label or 'fin-' in label else 3.5 if 'fork' in label else 15)
for pb in rig.pose.bones:pb.matrix_basis=bases[pb.name]
bpy.context.view_layer.update();text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('ELECTRIC EEL POSE CHECK PASS',len(checks['poses']),flush=True)
