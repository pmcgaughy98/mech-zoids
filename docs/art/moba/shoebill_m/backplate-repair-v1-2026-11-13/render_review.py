import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix

OUT=Path(__file__).parent
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_shoebill_single_material_25k_20261111_character.glb')
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
version=args[0] if args else 'before'
source=SOURCE if version=='before' else OUT/'shoebill-backplate-repaired-v1.glb'
if version=='intact':source=Path('D:/dev/new-mech-rpg/art/model_catalog/sources/shoebill_front - Hunyuan 3D v3.1 Pro.glb')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=800;scene.render.resolution_y=800;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Review Studio');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.12,.12,.12,1)
scene.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
objects=[o for o in scene.objects if o.type=='MESH' and (version=='intact' or len(o.vertex_groups))]
points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
if version=='intact':
 scale=1.7/(hi.z-lo.z)
 transform=Matrix.Translation(Vector((-(lo.x+hi.x)/2*scale,-(lo.y+hi.y)/2*scale,-lo.z*scale)))@Matrix.Scale(scale,4)
 for obj in objects:obj.matrix_world=transform@obj.matrix_world
 bpy.context.view_layer.update()
 points=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
 lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
center=(lo+hi)/2;span=max(hi-lo)
for offset,power in [((3,-4,5),900),((-4,-1,3),650),((1,4,4),1000)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset))
 light=bpy.context.object;light.data.energy=power;light.data.size=4
 light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO'
def shot(name,target,offset,size):
 cam.location=Vector(target)+Vector(offset);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
 scene.render.filepath=str(OUT/(version+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
for name,offset in [('front',(0,-5,.1)),('left',(5,0,.1)),('right',(-5,0,.1)),('back',(0,5,.1)),('top',(0,0,5)),('underside',(0,0,-5)),('three-quarter',(4,5,2))]:
 shot(name,center,offset,span*1.18)
for name,offset in [('plate-back',(0,5,.1)),('plate-three-quarter',(3,5,2)),('plate-top',(1,3,4))]:
 if version=='intact':break
 shot(name,(0,.38,1.16),offset,.88)
rig=next((o for o in scene.objects if o.type=='ARMATURE'),None)
report={'bounds_blender':[list(lo),list(hi)],'bones':[{'name':b.name,'head':list(rig.matrix_world@b.head_local),'tail':list(rig.matrix_world@b.tail_local)} for b in rig.data.bones] if rig else []}
(OUT/(version+'-blender-inspection.json')).write_text(json.dumps(report,indent=2))
if version=='after' and '--render-only' not in args:
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'shoebill-backplate-repaired-v1.blend'))
print('SHOEBILL RENDER DONE',version,flush=True)
