import bpy, json
from pathlib import Path
from mathutils import Vector

OUT=Path(__file__).parent
SRC=Path('D:/dev/new-mech-rpg/art/arena_models/cobra.glb')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SRC))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
print('AVAILABLE ACTIONS',[(a.name,[s.identifier for s in a.slots]) for a in bpy.data.actions],flush=True)
idle=next(a for a in bpy.data.actions if a.name=='Cobra_Idle' or a.name.startswith('Cobra_Idle|'))
rig.animation_data_create()
for track in rig.animation_data.nla_tracks:track.mute=True
rig.animation_data.action=idle
if idle.slots:rig.animation_data.action_slot=idle.slots[0]
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16
scene.render.resolution_x=1024;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Neutral Reference');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.6,.6,.6,1)
scene.view_settings.view_transform='Standard'
obs=[o for o in scene.objects if o.type=='MESH'];pts=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in obs:
 ev=o.evaluated_get(dg);me=ev.to_mesh();pts.extend(ev.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
lo=Vector(tuple(min(v[i] for v in pts) for i in range(3)));hi=Vector(tuple(max(v[i] for v in pts) for i in range(3)));center=(lo+hi)/2;span=max(hi-lo)
for off,power in [((3,-4,6),500),((-4,-2,3),350),((2,4,4),500)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(off));l=bpy.context.object;l.data.energy=power;l.data.size=4;l.rotation_euler=(center-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=span*1.2
for name,off in [('front',(0,-6,.4)),('side',(6,0,.4)),('back',(0,6,.4)),('hero',(4,-6,2))]:
 cam.location=center+Vector(off);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/('cobra-current-'+name+'.png'));bpy.ops.render.render(write_still=True)
print('CURRENT COBRA REFERENCES RENDERED',flush=True)
