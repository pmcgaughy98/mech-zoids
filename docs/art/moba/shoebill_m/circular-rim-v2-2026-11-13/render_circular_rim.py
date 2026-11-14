import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13');OLD=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13')
r=json.loads((OUT/'repair-verification.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(OLD/'shoebill-backplate-repaired-v1.blend'));scene=bpy.context.scene;scene.cycles.samples=16;scene.render.resolution_x=800;scene.render.resolution_y=800
for o in list(bpy.data.objects):
 if o.type in ['MESH','ARMATURE','EMPTY']:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=r['output']);bpy.context.view_layer.update();cam=scene.camera
shots=[('plate-back',(0,.38,1.16),(0,5,.1),.88),('plate-three-quarter',(0,.38,1.16),(3,5,2),.88),('plate-top',(0,.38,1.16),(1,3,4),.88),('back',(0,0,.85),(0,5,.1),2.006),('left',(0,0,.85),(5,0,.1),2.006),('front',(0,0,.85),(0,-5,.1),2.006),('right',(0,0,.85),(-5,0,.1),2.006),('three-quarter',(0,0,.85),(4,5,2),2.006),('underside',(0,0,.85),(0,0,-5),2.006)]
for name,target,offset,size in shots:
 cam.data.ortho_scale=size;cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/('after-'+name+'.png'));bpy.ops.render.render(write_still=True)
 if '--fast' in sys.argv and name=='plate-three-quarter':print('CIRCULAR RIM PREVIEW COMPLETE',flush=True);sys.exit(0)
text=bpy.data.texts.new('CIRCULAR_RIM_V2_PROVENANCE');text.write(json.dumps(r,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(Path(r['output']).with_suffix('.blend')));print('CIRCULAR RIM REVIEW COMPLETE',flush=True)
