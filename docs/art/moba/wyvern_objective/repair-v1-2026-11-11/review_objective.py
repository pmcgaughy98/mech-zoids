import bpy,json,sys,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).parent;mid=sys.argv[sys.argv.index('--')+1];cfg=json.loads((ROOT/mid/'input-audit.json').read_text());OUT=Path(f'D:/dev/new-mech-rpg/docs/art/moba/{mid}_objective/repair-v1-2026-11-11');verification=json.loads((OUT/'repair-verification.json').read_text());sources={'before':cfg['input'],'after':verification['output']};report={'tested_sha256':verification['output_sha256'],'joint_count':cfg['joint_count'],'poses':[],'intact_pre_remesh_source_available':False}
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.21,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.view_settings.view_transform='AgX';center=Vector((0,0,.85));span=2.8348842 if mid=='gold_beetle' else 3.3099244;frame=3.4 if mid=='gold_beetle' else 4.0
for offset,power,scale in [((2,-3,4),1000,3),((-3,-1,2),700,3),((0,3,3),1000,2)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*span);light=bpy.context.object;light.data.energy=power*span*span;light.data.shape='DISK';light.data.size=scale*span;light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000
def shot(name,target,offset,scale=None):
 cam.data.ortho_scale=frame if scale is None else scale;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=sources[version]);ob=next(o for o in scene.objects if o.type=='MESH' and len(o.vertex_groups));bpy.context.view_layer.update()
 for view,offset in [('front',(0,-10,.1)),('side',(10,0,.1)),('right',(-10,0,.1)),('back',(0,10,.1)),('underside',(0,0,-10)),('top',(0,0,10)),('three-quarter',(7,-10,5))]:shot(version+'-'+view,center,offset,2.6 if mid=='wyvern' and view in ['front','back'] else frame)
 if mid=='gold_beetle':
  for i,patch in enumerate(verification['holes_closed']):
   lo=Vector(patch['bounds'][0]);hi=Vector(patch['bounds'][1]);p=(lo+hi)/2;shot(version+'-patch-'+str(i+1),(p.x,-p.z,p.y),(-6,1,2),.45)
  for side,label in [(-1,'left'),(1,'right')]:shot(version+'-coin-stack-'+label,(side*.95,.0,.91),(side*6,0,1),1.1)
  shot(version+'-mandibles',(0,-1.04,.58),(4,-6,1),1.7)
 else:
  shot(version+'-underchest',(0,-.73,.48),(4,-6,-2),1.5)
  for side,label in [(-1,'left'),(1,'right')]:shot(version+'-wing-joint-'+label,(side*.43,-.54,1.21),(side*6,-3,1),1.25)
  shot(version+'-head',(0,-1.30,.75),(4,-6,1),1.4)
 if version=='after':
  rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==cfg['joint_count'];rest_bases={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones}
  for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();surface_ids=np.unique([i for f in me.polygons for i in f.vertices]);rest=np.array([tuple(me.vertices[i].co) for i in surface_ids]);ev.to_mesh_clear();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
  if mid=='gold_beetle':tests=[('front-left','Bone_016',10),('front-right','Bone_013',-10),('middle-left','Bone_010',10),('middle-right','Bone_007',-10),('rear-left','Bone_019',10),('rear-right','Bone_022',-10),('head','Bone_004',8),('mandibles','Bone_002',6),('shell','Bone_001',5)]
  else:tests=[('wing-left','Bone_041',8),('wing-right','Bone_045',-8),('hind-left','Bone_013',10),('hind-right','Bone_008',-10),('neck','Bone_002',6),('jaw','Bone_022',8),('tail-root','Bone_021',8),('tail-mid','Bone_018',-8),('removed-front-left','Bone_032',20),('removed-front-right','Bone_037',-20)]
  for label,bone,angle in tests:
   for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
   pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(me.vertices[i].co) for i in surface_ids]);gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());diff=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all();assert diff.max()<1e-6 if label.startswith('removed-') else diff.max()>.001;ev.to_mesh_clear();report['poses'].append({'label':label,'bone':bone,'local_x_degrees':angle,'max_displacement_m':float(diff.max()),'vertices_moved_over_1mm':int((diff>.001).sum()),'coincident_surface_gap_m':gap});shot('pose-'+label,center,(7,-10,5))
  for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
  bpy.context.view_layer.update()
  for view,ref in cfg['references'].items():
   im=bpy.data.images.load(ref['path'],check_existing=True);im.name='ORIGINAL_'+mid+'_'+view;im.pack();im.use_fake_user=True
  text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps({'category':'Objective','input':cfg['input'],'input_sha256':cfg['sha256'],'repaired_glb_sha256':verification['output_sha256'],'reference_sheets':cfg['references'],'pre_remesh_original_available':False,'scope':'Preserved native skeleton. Review copy; not installed into authored map runtime.'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{mid}-objective-repaired-v1.blend'))
(OUT/'visual-deformation-check.json').write_text(json.dumps(report,indent=2));print('OBJECTIVE REVIEW COMPLETE',mid,json.dumps(report),flush=True)
