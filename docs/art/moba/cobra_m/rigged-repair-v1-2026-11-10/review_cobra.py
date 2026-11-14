import bpy,bmesh,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).parent
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10')
SOURCES={'intact':'D:/dev/new-mech-rpg/docs/art/moba/cobra_m/tail-correction-2026-11-10/cobra_front - single tail corrected.glb','remeshed':'D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_cobra_remeshed_25k_20261111_character.glb','repaired':str(OUT/'cobra-rigged-local-repair-v1.glb')}
# Blender's Python may not include scipy; its mathutils KDTree is used below instead.
from mathutils.kdtree import KDTree
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.view_settings.view_transform='AgX'
center=Vector((0,0,.85));size=3.114
for offset,power,scale in [((2,-3,4),1000,3),((-3,-1,2),700,3),((0,3,3),1000,2)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*size);l=bpy.context.object;l.data.energy=power*size*size;l.data.shape='DISK';l.data.size=scale*size;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.16;cam.data.clip_end=10000
views=[('front',(0,-3,.05)),('side',(3,0,.05)),('back',(0,3,.05)),('underside',(0,-.3,-3)),('top',(0,0,3)),('three-quarter',(2,-3,2))]
right_only='--right-only' in sys.argv
if right_only:views=[('right',(-3,0,.05))]
report={'sources':SOURCES,'comparison_note':'Intact comparator is our accepted single-tail full-detail correction, not claimed as independently verified exact Meshy upload. Display alignment only; no source changed.','views':views,'poses':[]}
def render(name,target,offset,scale):
 cam.data.ortho_scale=scale;cam.location=Vector(target)+Vector(offset)*size;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
def bounds(o):
 pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));return lo,hi
for version in ['remeshed','intact','repaired']:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=SOURCES[version]);added=set(bpy.data.objects)-before
 meshes=[o for o in added if o.type=='MESH' and (version=='intact' or any(m.type=='ARMATURE' for m in o.modifiers))];assert len(meshes)==1
 ob=meshes[0];rig=next((o for o in added if o.type=='ARMATURE'),None)
 if version=='remeshed':
  lo,hi=bounds(ob);center=(lo+hi)/2;target_span=hi-lo
  refpts=[ob.matrix_world@v.co for v in ob.data.vertices];tree=KDTree(len(refpts))
  for i,p in enumerate(refpts):tree.insert(p,i)
  tree.balance()
 if version=='intact':
  # Only turn/scale/translate the separate review instance. Pick the best
  # cardinal rotation against the remeshed surface; preserve a uniform scale.
  coords=[ob.matrix_world@v.co for v in ob.data.vertices];best=None
  for yaw in [0,math.pi/2,math.pi,3*math.pi/2]:
   rot=Matrix.Rotation(yaw,4,'Z');pts=[rot@p for p in coords];lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));factor=max(target_span)/max(hi-lo);mid=(lo+hi)/2;transform=Matrix.Translation(center)@Matrix.Diagonal((factor,factor,factor,1))@Matrix.Translation(-mid)@rot
   errors=[tree.find(transform@p)[2] for p in coords[::30]];score=sum(errors)/len(errors)
   if best is None or score<best[0]:best=(score,transform,yaw,factor)
  ob.matrix_world=best[1]@ob.matrix_world;report['intact_display_alignment']={'mean_nearest_sample_distance_m':best[0],'yaw_degrees':math.degrees(best[2]),'uniform_scale':best[3],'matrix':[list(row) for row in best[1]]}
 bpy.context.view_layer.update()
 for name,offset in views:render(version+'-'+name,center,offset,size*1.16)
 if version!='intact' and not right_only:
  patches=json.loads((OUT/'repair-verification.json').read_text())['holes_closed']
  for i,p in enumerate(patches):
   gl=(Vector(p['bounds'][0])+Vector(p['bounds'][1]))/2;target=Vector((gl.x,-gl.z,gl.y));offset=(3,0,1) if i in [0,2] else (0,-3,1)
   render(version+f'-patch-{i+1}',target,offset,.22)
 if version=='repaired' and not right_only:
  dg=bpy.context.evaluated_depsgraph_get();base=ob.evaluated_get(dg).to_mesh();rest=np.array([tuple(ob.matrix_world@v.co) for v in base.vertices]);ob.evaluated_get(dg).to_mesh_clear()
  for label,bones,angle in [('tail-left',['Bone_010','Bone_008'],12),('tail-right',['Bone_010','Bone_008'],-12),('neck',['Bone_016'],8)]:
   for pb in rig.pose.bones:pb.matrix_basis.identity()
   for bone in bones:pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x=math.radians(angle)
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(ob.matrix_world@v.co) for v in me.vertices]);disp=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all() and disp.max()>.001
   report['poses'].append({'label':label,'bones':bones,'local_x_degrees':angle,'vertices_moved_over_1mm':int((disp>.001).sum()),'maximum_displacement_m':float(disp.max()),'finite':True});ev.to_mesh_clear()
   render('pose-'+label,center,(2,-3,2),size*1.16)
  for pb in rig.pose.bones:pb.matrix_basis.identity()
  bpy.context.view_layer.update()
  # Save the exact imported rig in an editable review scene, not a re-export.
  bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'cobra-rigged-local-repair-v1.blend'))
 for o in list(added):bpy.data.objects.remove(o,do_unlink=True)
if not right_only:(OUT/'visual-and-deformation-check.json').write_text(json.dumps(report,indent=2))
print('REVIEW COMPLETE',json.dumps(report['poses']),flush=True)
