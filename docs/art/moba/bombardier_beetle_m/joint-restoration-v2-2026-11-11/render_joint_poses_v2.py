import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/joint-restoration-v2-2026-11-11')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'bombardier-beetle-joints-restored-v2.blend'));scene=bpy.context.scene;cam=scene.camera;rig=next(o for o in scene.objects if o.type=='ARMATURE');rest={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones}
for side,label,bone,angle in [(-1,'left','Bone_052',10),(1,'right','Bone_058',-10)]:
 for pb in rig.pose.bones:pb.matrix_basis=rest[pb.name]
 pb=rig.pose.bones[bone];pb.rotation_mode='XYZ';pb.rotation_euler.x+=math.radians(angle);bpy.context.view_layer.update();target=Vector((side*.78,-.55,.62));cam.data.ortho_scale=1.05;cam.location=target+Vector((side*6,-2,1));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'pose-front-joint-{label}.png');bpy.ops.render.render(write_still=True)
print('Restored front-joint motion close-ups rendered.',flush=True)
