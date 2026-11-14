import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/falcon_m/local-repair-v1-2026-11-13');bpy.ops.wm.open_mainfile(filepath=str(OUT/'falcon-rigged-local-repair-v1.blend'));s=bpy.context.scene;cam=s.camera;target=Vector((.48,-.4,.12));cam.location=target+Vector((.2,.2,-5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.05;bpy.context.view_layer.update();marks={}
for name,p in [('outer_rear',(.709,.02,.21)),('central_rear',(.469,.019,.135)),('inner_front',(.165,.022,.612)),('central_front',(.489,.026,.844)),('outer_front',(.745,.027,.605))]:
 q=world_to_camera_view(s,cam,Vector((p[0],-p[2],p[1])));marks[name]=[q.x*720,(1-q.y)*720]
(OUT/'foot-label-pixels.json').write_text(json.dumps(marks,indent=2));print(marks)
