import bpy,json,math,hashlib
from pathlib import Path
import numpy as np
from mathutils import Vector,Matrix
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13');BASE=Path('D:/dev/new-mech-rpg')
report=json.loads((OUT/'repair-verification.json').read_text());entry=next(e for e in json.loads((BASE/'art/model_catalog/catalog.json').read_text())['entries'] if e['id']=='shoebill')
native=OUT/'shoebill-backplate-repaired-v1.blend';bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;cam=scene.camera
def shot(name,target,offset,size):
 cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for ob in list(bpy.data.objects):
 if ob.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(ob,do_unlink=True)
source=BASE/entry['source_model']['path'].removeprefix('res://');assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['source_model']['sha256']
bpy.ops.import_scene.gltf(filepath=str(source));bpy.context.view_layer.update();objects=[o for o in scene.objects if o.type=='MESH'];coords=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box];lo=Vector(tuple(min(p[i] for p in coords) for i in range(3)));hi=Vector(tuple(max(p[i] for p in coords) for i in range(3)));scale=1.7/(hi.z-lo.z)
transform=Matrix.Translation(Vector((-(lo.x+hi.x)/2*scale,-(lo.y+hi.y)/2*scale,-lo.z*scale)))@Matrix.Scale(scale,4)
for ob in objects:ob.matrix_world=transform@ob.matrix_world
bpy.context.view_layer.update()
for name,offset in [('front',(0,-5,.1)),('left',(5,0,.1)),('right',(-5,0,.1)),('back',(0,5,.1))]:shot('intact-'+name,(0,0,.85),offset,2.006)
original_scale=scale
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;cam=scene.camera;rig=next(o for o in scene.objects if o.type=='ARMATURE');objects=[o for o in scene.objects if o.type=='MESH' and len(o.vertex_groups)];assert len(rig.data.bones)==38
rest_bases={p.name:p.matrix_basis.copy() for p in rig.pose.bones}
def surface():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();points=[]
 for ob in objects:
  ev=ob.evaluated_get(dg);me=ev.to_mesh();ids=np.unique([v for f in me.polygons for v in f.vertices]);points.extend(tuple(me.vertices[int(i)].co) for i in ids);ev.to_mesh_clear()
 return np.asarray(points)
rest=surface();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
tests=[('backplate-body','Bone_003',6),('lower-body','Bone_002',6),('head','Bone_016',6),('bill','Bone_015',6),('wing-left','Bone_021',8),('wing-right','Bone_025',-8),('wing-tip-left','Bone_019',8),('wing-tip-right','Bone_023',-8),('leg-left','Bone_009',8),('leg-right','Bone_014',-8),('knee-left','Bone_008',8),('knee-right','Bone_013',-8),('foot-left','Bone_005',8),('foot-right','Bone_010',-8)]
checks={'tested_sha256':report['output_sha256'],'joint_count':38,'intact_source_sha256':entry['source_model']['sha256'],'intact_source_to_rig_height_scale':original_scale,'poses':[]}
for label,bone,angle in tests:
 for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
 pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);posed=surface();diff=np.linalg.norm(posed-rest,axis=1);gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());assert np.isfinite(posed).all() and diff.max()>.001;assert gap<1e-6,(label,gap)
 checks['poses'].append({'label':label,'bone':bone,'degrees':angle,'max_displacement_m':float(diff.max()),'coincident_surface_gap_m':gap})
 if label=='backplate-body':shot('pose-'+label,(0,.38,1.16),(3,5,2),.88)
 else:shot('pose-'+label,(0,0,.85),(4,5,2) if 'wing' in label or label=='lower-body' else (4,-5,2),2.006)
for pb in rig.pose.bones:pb.matrix_basis=rest_bases[pb.name]
bpy.context.view_layer.update()
for key,ref in entry['views'].items():
 path=BASE/ref['path'].removeprefix('res://');assert hashlib.sha256(path.read_bytes()).hexdigest()==ref['sha256'];im=bpy.data.images.load(str(path),check_existing=True);im.name='ORIGINAL_SHOEBILL_'+key;im.pack();im.use_fake_user=True
text=bpy.data.texts.new('MODEL_REVIEW_PROVENANCE');text.write(json.dumps({'input_sha256':report['source_sha256'],'repaired_sha256':report['output_sha256'],'intact_body_archive':entry['source_model'],'reference_views':entry['views'],'scope':report['scope'],'source_body_has_original_backplate':'Original archive is body quality reference. Current fitted moon plate is retained.'},indent=2))
cam.location=Vector((4,5,2.85));cam.rotation_euler=(Vector((0,0,.85))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.006;bpy.ops.wm.save_as_mainfile(filepath=str(native));(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('SHOEBILL RIG REVIEW PASS',json.dumps(checks),flush=True)
