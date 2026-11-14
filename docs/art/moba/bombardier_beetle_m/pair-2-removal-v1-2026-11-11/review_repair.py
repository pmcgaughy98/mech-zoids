import bpy,json,math,hashlib,itertools,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
ROOT=Path(__file__).parent
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/pair-2-removal-v1-2026-11-11')
sources={'before':'D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb','intact':'D:/dev/new-mech-rpg/art/model_catalog/sources/bombardier_beetle_front - Hunyuan 3D v3.1 Pro.glb','after':str(OUT/'bombardier-beetle-six-legs-rigged-v1.glb')}
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.view_settings.view_transform='AgX'
center=Vector((0,0,.85));span=2.68278265
for offset,power,scale in [((2,-3,4),1000,3),((-3,-1,2),700,3),((0,3,3),1000,2)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*span);l=bpy.context.object;l.data.energy=power*span*span;l.data.shape='DISK';l.data.size=scale*span;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000
report={'tested_sha256':hashlib.sha256(Path(sources['after']).read_bytes()).hexdigest(),'poses':[],'joint_count':64}
def shot(name,target,offset,scale=3.4):
 if '--final' in sys.argv and not (name.startswith('after-') or name.startswith('pose-')):return
 cam.data.ortho_scale=scale;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','intact','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=sources[version]);ob=next(o for o in scene.objects if o.type=='MESH' and (version=='intact' or len(o.vertex_groups)))
 if version=='before':
  pts=[ob.matrix_world@v.co for v in ob.data.vertices];tree=KDTree(len(pts))
  for i,p in enumerate(pts):tree.insert(p,i)
  tree.balance()
 if version=='intact':
  pts=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices]);sample=pts[::60];best=None
  for perm in itertools.permutations(range(3)):
   for signs in itertools.product([-1,1],repeat=3):
    rot=np.eye(3)[list(perm)]*np.array(signs)[:,None]
    if np.linalg.det(rot)<0:continue
    rp=pts@rot.T;lo=rp.min(0);hi=rp.max(0);factor=span/max(hi-lo);mid=(lo+hi)/2;dest=(sample@rot.T-mid)*factor+np.array(center);score=sum(tree.find(Vector(v))[2] for v in dest)/len(dest)
    if best is None or score<best[0]:best=(score,rot,factor,mid)
  score,rot,factor,mid=best;transform=np.eye(4);transform[:3,:3]=rot*factor;transform[:3,3]=np.array(center)-mid*factor;ob.matrix_world=Matrix(transform.tolist())@ob.matrix_world
  conv=np.array([[1,0,0],[0,0,1],[0,-1,0]])
  report['intact_alignment']={'matrix_blender':transform.tolist(),'rotation_basis_godot':(conv@rot@conv.T).tolist(),'uniform_scale':factor,'sample_mean_distance_m':score}
 bpy.context.view_layer.update()
 for name,offset in [('front',(0,-10,.1)),('side',(10,0,.1)),('right',(-10,0,.1)),('back',(0,10,.1)),('underside',(0,0,-10)),('top',(0,0,10)),('three-quarter',(7,-10,5))]:shot(version+'-'+name,center,offset)
 if version!='intact':
  patches=json.loads((OUT/'repair-verification.json').read_text())['caps']
  for pi,patch in enumerate(patches):
   lo=Vector(patch['bounds'][0]);hi=Vector(patch['bounds'][1]);mid=(lo+hi)/2;target=Vector((mid.x,-mid.z,mid.y));shot(version+'-patch-'+str(pi+1),target,(6 if mid.x>0 else -6,-2,1),.9)
 if version=='after':
  rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==64
  rest_bases={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones}
  for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
  bpy.context.view_layer.update()
  dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();surface_ids=np.unique([i for f in me.polygons for i in f.vertices]);rest=np.array([tuple(me.vertices[i].co) for i in surface_ids]);ev.to_mesh_clear();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
  tests=[('front-left','Bone_052',10),('front-right','Bone_058',-10),('middle-left','Bone_028',10),('middle-right','Bone_033',-10),('rear-left','Bone_018',10),('rear-right','Bone_023',-10),('head','Bone_047',8),('body','Bone_007',6),('removed-left-control','Bone_038',20),('removed-right-control','Bone_043',-20)]
  for label,bone,angle in tests:
   for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
   pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(me.vertices[i].co) for i in surface_ids]);gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());diff=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all();assert diff.max()<1e-6 if label.startswith('removed-') else diff.max()>.001;ev.to_mesh_clear()
   report['poses'].append({'label':label,'bone':bone,'local_x_degrees':angle,'max_displacement_m':float(diff.max()),'vertices_moved_over_1mm':int((diff>.001).sum()),'uv_split_seam_gap_m':gap});shot('pose-'+label,center,(7,-10,5))
  for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
  bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'bombardier-beetle-six-legs-rigged-v1.blend'))
(OUT/'visual-deformation-check.json').write_text(json.dumps(report,indent=2));print('REVIEW COMPLETE',json.dumps(report),flush=True)
