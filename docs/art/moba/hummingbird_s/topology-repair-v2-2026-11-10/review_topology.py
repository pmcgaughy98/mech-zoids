import bpy,json,math,hashlib,itertools,sys
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10')
sources={'before':'D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10/hummingbird-rigged-straight-needle-v1.glb','intact':'D:/dev/new-mech-rpg/art/model_catalog/sources/hummingbird_front - Hunyuan 3D v3.1 Pro.glb','after':str(OUT/'hummingbird-rigged-needle-topology-v2.glb')}
bpy.ops.wm.open_mainfile(filepath='D:/dev/_scratch/mech-art-direction/hummingbird-needle-2026-11-10/hummingbird-inspection.blend');scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=16;scene.render.resolution_x=720;scene.render.resolution_y=720
report={'tested_sha256':hashlib.sha256(Path(sources['after']).read_bytes()).hexdigest(),'poses':[]}
def shot(name,target,offset,scale):
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
    rp=pts@rot.T;lo=rp.min(0);hi=rp.max(0);factor=3.9312416/max(hi-lo);mid=(lo+hi)/2;dest=(sample@rot.T-mid)*factor+np.array([0,0,.85]);score=sum(tree.find(Vector(v))[2] for v in dest)/len(dest)
    if best is None or score<best[0]:best=(score,rot,factor,mid)
  score,rot,factor,mid=best;transform=np.eye(4);transform[:3,:3]=rot*factor;transform[:3,3]=np.array([0,0,.85])-mid*factor;ob.matrix_world=Matrix(transform.tolist())@ob.matrix_world;report['intact_alignment']={'matrix':transform.tolist(),'uniform_scale':factor,'sample_mean_distance':score}
 bpy.context.view_layer.update()
 for name,offset in [('front',(0,-10,.15)),('side',(10,0,.15)),('right',(-10,0,.15)),('back',(0,10,.15)),('underside',(0,0,-10)),('three-quarter',(7,-10,5))]:shot(version+'-'+name,(0,0,.85),offset,4.55)
 if version!='intact':
  patches=json.loads((OUT/'repair-verification.json').read_text())['holes_closed']
  for pi,patch in enumerate(patches):
   lo=Vector(patch['bounds'][0]);hi=Vector(patch['bounds'][1]);mid=(lo+hi)/2;center=Vector((mid.x,-mid.z,mid.y));offset=Vector((0,-3,5)) if pi<2 else Vector((0,3,5))
   shot(version+'-patch-'+str(pi+1),center,offset,.22)
 if version!='intact':
  for name,offset in [('needle-side',(8,0,0)),('needle-top',(0,0,8)),('needle-angle',(6,-8,3))]:shot(version+'-'+name,(0,-.79,1.18),offset,1.48)
 if version=='after':
  rig=next(o for o in scene.objects if o.type=='ARMATURE');dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();rest=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear()
  for bone,axis,angle in [('Bone_005',0,10),('Bone_016',0,15),('Bone_020',0,-15)]:
   for pb in rig.pose.bones:pb.matrix_basis.identity()
   pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler[axis]=math.radians(angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(v.co) for v in me.vertices]);diff=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all() and diff.max()>.001;ev.to_mesh_clear();report['poses'].append({'bone':bone,'axis':axis,'degrees':angle,'max_displacement':float(diff.max()),'vertices_moved_over_1mm':int((diff>.001).sum()),'finite':True});shot('pose-'+bone+'-'+str(axis),(0,-.79,1.18),(6,-8,3),1.65)
  for pb in rig.pose.bones:pb.matrix_basis.identity()
  bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'hummingbird-needle-topology-v2.blend'))
(OUT/'visual-deformation-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
