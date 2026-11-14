import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
R=Path('D:/dev/_scratch/gorilla-free-animation')
O=Path('D:/dev/new-mech-rpg/docs/art/moba/ape_l/free-animation-test-2026-11-07')
bpy.ops.wm.open_mainfile(filepath='D:/dev/new-mech-rpg/docs/art/3d/ape_l_v2.blend')
ape=bpy.data.objects['ape_l'];target=bpy.data.objects['ape_l_rig']
target.animation_data_clear()
for b in target.pose.bones:b.matrix_basis=Matrix.Identity(4)
for o in list(bpy.data.objects):
    if o not in [ape,target]:bpy.data.objects.remove(o,do_unlink=True)
original=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(R/'upstream/static/assets/kaiju/model.glb'))
donor=next(o for o in set(bpy.data.objects)-original if o.type=='ARMATURE')
donormesh=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Dinosaur'))
for o in list(set(bpy.data.objects)-original):
    if o not in [donor,donormesh]:bpy.data.objects.remove(o,do_unlink=True)
before=set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(R/'upstream/static/assets/kaiju/animations/attack.glb'))
animrig=next(o for o in set(bpy.data.objects)-before if o.type=='ARMATURE')
action=animrig.animation_data.action
donor.animation_data_create();donor.animation_data.action=action
donor.animation_data.action_slot=animrig.animation_data.action_slot
for o in list(set(bpy.data.objects)-before):bpy.data.objects.remove(o,do_unlink=True)
scene=bpy.context.scene;scene.render.fps=30
def setframe(f):scene.frame_set(int(f),subframe=f-int(f))
mapping={'upper_arm.R':'front_leg_upper_r','forearm.R':'front_leg_lower_r','hand.R':'hand_r'}
# Transfer the donor's world-space rotation change relative to its first pose.
# The support limbs and torso keep the gorilla's rest posture.
scene.frame_set(0);bpy.context.view_layer.update()
reference={n:donor.pose.bones[n].matrix.to_quaternion().copy() for n in mapping.values()}
samples={}
for f in range(32):
    setframe(f*24/30);bpy.context.view_layer.update()
    samples[f]={n:donor.pose.bones[n].matrix.to_quaternion().copy() for n in mapping.values()}
target.animation_data_create();ta=bpy.data.actions.new('CC0_Attack_right_arm_overlay_TEST');target.animation_data.action=ta
for f in range(32):
    scene.frame_set(f)
    for name,src in mapping.items():
        pb=target.pose.bones[name];pb.rotation_mode='QUATERNION'
        delta=samples[f][src]@reference[src].inverted()
        # Damp donor rotation to keep the heavy mechanical joints inside a modest test range.
        delta=delta.slerp(Matrix.Identity(3).to_quaternion(),0.3)
        rest=pb.bone.matrix_local.to_quaternion()
        desired=(delta@rest).to_matrix().to_4x4();desired.translation=pb.bone.head_local
        if pb.parent:
            parent_rest=pb.parent.bone.matrix_local
            desired=pb.parent.matrix@parent_rest.inverted()@desired
        pb.matrix=desired
        pb.keyframe_insert(data_path='rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
# Fixed floor offset, calculated from the unanimated support vertices.
scene.frame_set(0);bpy.context.view_layer.update()
support_groups={g.index for g in ape.vertex_groups if g.name in ['hand.L','foot.L','foot.R']}
floor=min((ape.matrix_world@v.co).z for v in ape.data.vertices if any(g.group in support_groups for g in v.groups))
target.location.z=-floor
# Minimal shoulder-pitch correction when the transferred fist intersects the floor.
handgroup=ape.vertex_groups['hand.R'].index
handpoints=[v.co.copy() for v in ape.data.vertices if any(g.group==handgroup for g in v.groups)]
invbind=target.data.bones['hand.R'].matrix_local.inverted()
corrections=[]
for f in range(32):
    scene.frame_set(f);bpy.context.view_layer.update()
    upper=target.pose.bones['upper_arm.R'];q=upper.rotation_quaternion.copy()
    def clearance():
        mat=target.matrix_world@target.pose.bones['hand.R'].matrix@invbind
        return min((mat@p).z for p in handpoints)
    if clearance() < 0.002:
        candidates=[]
        for deg in range(-90,91,2):
            upper.rotation_quaternion=Quaternion((1,0,0),math.radians(deg))@q
            bpy.context.view_layer.update()
            z=clearance()
            if z>=0.002:candidates.append((abs(deg),deg,z))
        if not candidates:raise RuntimeError('No floor-safe pitch')
        _,deg,z=min(candidates)
        upper.rotation_quaternion=Quaternion((1,0,0),math.radians(deg))@q
        upper.keyframe_insert(data_path='rotation_quaternion',frame=f)
        corrections.append({'frame':f,'pitch_degrees':deg,'min_z':z})
    else:upper.rotation_quaternion=q
(O/'floor-corrections.json').write_text(json.dumps(corrections,indent=2))
for m in bpy.data.materials:
    if m.use_nodes:
        bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if bs:m.diffuse_color=bs.inputs['Base Color'].default_value
for o in [donor,donormesh]:o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH'
scene.display.shading.show_specular_highlight=True
scene.display.shading.background_type='WORLD';scene.world.color=(0.035,0.043,0.055)
scene.render.resolution_x=600;scene.render.resolution_y=420;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-0.025));ground=bpy.context.object;ground.name='Review floor';ground.color=(0.12,0.15,0.18,1)
mat=bpy.data.materials.new('Review floor');mat.diffuse_color=(0.12,0.15,0.18,1);ground.data.materials.append(mat)
def camera(pos,look,scale):
    bpy.ops.object.camera_add(location=pos);c=bpy.context.object;c.rotation_euler=(Vector(look)-c.location).to_track_quat('-Z','Y').to_euler();c.data.type='ORTHO';c.data.ortho_scale=scale;scene.camera=c
camera((-7,-9,6.8),(0,0,1.1),6.2)
scene.frame_start=0;scene.frame_end=31
bpy.ops.wm.save_as_mainfile(filepath=str(O/'legacy-gorilla-attack-test.blend'))
metrics=[]
for f in range(32):
    scene.frame_set(f);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();ev=ape.evaluated_get(dep);me=ev.to_mesh()
    groups={g.name:g.index for g in ape.vertex_groups}
    r={'frame':f}
    for name in ['hand.L','hand.R','foot.L','foot.R']:
        pts=[ev.matrix_world@v.co for v in me.vertices if any(g.group==groups[name] for g in ape.data.vertices[v.index].groups)]
        r[name]={'min_z':min(v.z for v in pts),'center':[sum(v[i] for v in pts)/len(pts) for i in range(3)]}
    ev.to_mesh_clear();metrics.append(r)
(O/'contact-samples.json').write_text(json.dumps(metrics,indent=2))
mode=sys.argv[-1] if '--' in sys.argv else 'samples'
frames=range(32) if mode=='full' else [0,8,16,24,31]
for kind in ['gorilla','donor']:
    isape=kind=='gorilla';ape.hide_render=not isape;donormesh.hide_render=isape
    for view,pos in [('threequarter',(-7,-9,6.8)),('side',(-9,0,4.7))]:
        c=scene.camera;c.location=pos;look=Vector((0,0,1.1));c.rotation_euler=(look-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=6.2 if isape else 6.8
        for f in frames:
            setframe(f if isape else f*24/30)
            p=R/'renders'/kind/view/f'{f:03d}.png';p.parent.mkdir(parents=True,exist_ok=True)
            scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
print('DONE',mode)
