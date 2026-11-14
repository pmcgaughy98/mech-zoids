import bpy,json,math,hashlib
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/spider_m/surface-restoration-v1-2026-11-10');ROOT=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'spider-rigged-inspection.blend'));scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=12;scene.render.resolution_x=720;scene.render.resolution_y=720
sources={'before':'D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_spider_textured_25k_20261111_character.glb','intact':'D:/dev/new-mech-rpg/art/model_catalog/sources/spider_front - Hunyuan 3D v3.1 Pro.glb','after':str(OUT/'spider-restored-eight-legs-rigged-v1.glb')};report={'sha256':hashlib.sha256(Path(sources['after']).read_bytes()).hexdigest(),'poses':[]}
def shot(name,target,offset,scale=3.6):
 cam.data.ortho_scale=scale;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for version in ['before','intact','after']:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=sources[version]);ob=next(o for o in scene.objects if o.type=='MESH' and (version=='intact' or len(o.vertex_groups)))
 if version=='intact':
  pts=np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices]);lo=pts.min(0);hi=pts.max(0);fit=2.8764856/max(hi-lo);ob.matrix_world=Matrix.Translation(Vector((0,0,.85)))@Matrix.Diagonal((fit,fit,fit,1))@Matrix.Translation(-Vector((lo+hi)/2))@ob.matrix_world;report['intact_display_scale']=fit
 bpy.context.view_layer.update()
 for name,offset in [('front',(0,-9,.1)),('side',(9,0,.1)),('right',(-9,0,.1)),('back',(0,9,.1)),('underside',(0,0,-9)),('top',(0,0,9)),('three-quarter',(6,-9,6))]:shot(version+'-'+name,(0,0,.85),offset)
 if version=='after':
  rig=next(o for o in scene.objects if o.type=='ARMATURE');assert len(rig.data.bones)==52;dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();rest=np.array([tuple(v.co) for v in me.vertices]);ev.to_mesh_clear();_,first,inverse=np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
  for bone,angle in [('Bone_012',10),('Bone_017',-10),('Bone_022',10),('Bone_027',-10),('Bone_032',10),('Bone_037',-10),('Bone_042',10),('Bone_047',-10),('Bone_007',8)]:
   for pb in rig.pose.bones:pb.matrix_basis.identity()
   pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x=math.radians(angle);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);me=ev.to_mesh();posed=np.array([tuple(v.co) for v in me.vertices]);gap=float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max());disp=np.linalg.norm(posed-rest,axis=1);assert np.isfinite(posed).all() and disp.max()>.001;report['poses'].append({'bone':bone,'angle_x':angle,'max_displacement':float(disp.max()),'moved_vertices_over_1mm':int((disp>.001).sum()),'uv_split_seam_gap_m':gap});ev.to_mesh_clear();shot('pose-'+bone,(0,0,.85),(6,-9,6))
  for pb in rig.pose.bones:pb.matrix_basis.identity()
  bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'spider-restored-eight-legs-rigged-v1.blend'))
(OUT/'visual-rig-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
