import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/needle-length-study-2026-11-10');OLD=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10')
bpy.ops.wm.open_mainfile(filepath=str(OLD/'hummingbird-needle-topology-v2.blend'));scene=bpy.context.scene;cam=scene.camera;scene.cycles.samples=16
for label,path in [('current',OLD/'hummingbird-rigged-needle-topology-v2.glb'),('shorter-20',OUT/'shorter-20-REVIEW-ONLY.glb'),('shorter-30',OUT/'shorter-30-REVIEW-ONLY.glb')]:
 for o in list(bpy.data.objects):
  if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(path))
 for name,center,offset,scale in [('side',(0,-.38,1.25),(8,0,0),2.5),('whole',(0,0,.85),(7,-10,5),4.55)]:
  cam.data.ortho_scale=scale;cam.location=Vector(center)+Vector(offset);cam.rotation_euler=(Vector(center)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(label+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('LENGTH REVIEW RENDER COMPLETE',flush=True)
