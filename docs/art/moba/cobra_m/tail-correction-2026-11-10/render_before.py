import bpy,math,json
from pathlib import Path
from mathutils import Vector
out=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/tail-correction-2026-11-10')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/cobra-source.glb')
ob=next(o for o in bpy.context.scene.objects if o.type=='MESH')
bpy.context.view_layer.objects.active=ob;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
lo=Vector([min(v.co[i] for v in ob.data.vertices) for i in range(3)])
hi=Vector([max(v.co[i] for v in ob.data.vertices) for i in range(3)])
center=(lo+hi)*.5
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=10;scene.cycles.use_denoising=True
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('ReviewWorld');scene.world.color=(.28,.28,.28)
scene.view_settings.view_transform='AgX'
def aim(o,point):
 o.rotation_euler=(point-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=1.15;scene.camera=cam
for loc,power,size in [((2,-3,4),350,3),((-2,2,3),300,3),((0,0,-2),90,2)]:
 bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.data.energy=power;light.data.shape='DISK';light.data.size=size;aim(light,center)
views=[('front',Vector((0,-3,0))),('side',Vector((3,0,0))),('back',Vector((0,3,0))),('underside',Vector((0,0,-3))),('top',Vector((0,0,3))),('three-quarter',Vector((2,-3,2)))]
for name,offset in views:
 cam.location=center+offset;aim(cam,center)
 scene.render.filepath=str(out/f'before-{name}.png');bpy.ops.render.render(write_still=True)
(out/'render-settings.json').write_text(json.dumps({'center':list(center),'lo':list(lo),'hi':list(hi),'ortho_scale':1.15,'resolution':[640,640],'views':[(name,list(offset)) for name,offset in views]},indent=2))
bpy.ops.wm.save_as_mainfile(filepath='D:/dev/_scratch/mech-art-direction/cobra-tail-2026-11-10/before-scene.blend')
print('COBRA SOURCE REVIEW COMPLETE',flush=True)
