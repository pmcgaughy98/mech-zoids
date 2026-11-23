import bpy, json, math
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT = Path(__file__).parent
OUT = Path('D:/dev/new-mech-rpg/docs/art/moba/cat_m/local-repair-v1-2026-11-15')
r = json.loads((OUT/'repair-verification.json').read_text())
native = Path(r['output']).with_suffix('.blend')
bpy.ops.wm.open_mainfile(filepath=str(native))
s = bpy.context.scene
cam = s.camera

def shot(name, target, offset, frame):
    cam.data.ortho_scale = frame
    cam.location = Vector(target) + Vector(offset)
    cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath = str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)

for version in ['before', 'after']:
    for ob in list(bpy.data.objects):
        if ob.type in ['MESH','ARMATURE','EMPTY']:
            bpy.data.objects.remove(ob, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=r['source'] if version=='before' else r['output'])
    bpy.context.view_layer.update()
    for i,cap in enumerate(r['holes_closed']):
        center=(np.array(cap['bounds'][0])+np.array(cap['bounds'][1]))/2
        normal=Vector((cap['normal'][0],-cap['normal'][2],cap['normal'][1]))
        target=Vector((center[0],-center[2],center[1]))
        bpy.ops.object.light_add(type='AREA',location=target+normal*1.5)
        fill=bpy.context.object;fill.data.energy=12;fill.data.size=1
        fill.rotation_euler=(-normal).to_track_quat('-Z','Y').to_euler()
        shot(f'{version}-patch-{i+1}',target,normal*5,.12)
        bpy.data.objects.remove(fill,do_unlink=True)

rig = next(ob for ob in s.objects if ob.type=='ARMATURE')
objects = [ob for ob in s.objects if ob.type=='MESH' and len(ob.vertex_groups)]
bases = {p.name:p.matrix_basis.copy() for p in rig.pose.bones}
assert len(bases)==48
def surface():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objects:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        ids = np.unique([i for face in me.polygons for i in face.vertices])
        pts.extend(tuple(ev.matrix_world @ me.vertices[int(i)].co) for i in ids)
        ev.to_mesh_clear()
    return np.asarray(pts)

rest = surface()
_, first, inverse = np.unique(np.round(rest,6),axis=0,return_index=True,return_inverse=True)
checks = {'tested_sha256':r['output_sha256'],'joint_count':48,'poses':[],'no_surface_motion':[],'rendered_poses':[],'surface_motion_threshold_m':.001,'classification':'Below 1 mm is classified separately; small nonzero motion may occur.'}
render_bones = [0, 2, 3, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47]
for bone in range(48):
    for pb in rig.pose.bones:
        pb.matrix_basis = bases[pb.name]
    pb = rig.pose.bones[f'Bone_{bone:03}']
    pb.rotation_mode='XYZ'
    pb.rotation_euler.x += math.radians(8 if bone%2==0 else -8)
    posed = surface()
    diff = float(np.linalg.norm(posed-rest,axis=1).max())
    gap = float(np.linalg.norm(posed-posed[first[inverse]],axis=1).max())
    assert np.isfinite(posed).all() and gap<1e-6, (bone,diff,gap)
    item = {'label':f'bone-{bone:03}','bone':pb.name,'degrees':8 if bone%2==0 else -8,'max_displacement_m':diff,'coincident_surface_gap_m':gap}
    if diff>.001:
        checks['poses'].append(item)
    else:
        checks['no_surface_motion'].append(item)
    if bone in render_bones:
        shot('pose-'+item['label'], (0,0,.85), (4,-6,2.5), 6.2)
        checks['rendered_poses'].append(item['label'])
for pb in rig.pose.bones:
    pb.matrix_basis = bases[pb.name]
bpy.context.view_layer.update()
text = bpy.data.texts.new('MODEL_REVIEW_PROVENANCE')
text.write(json.dumps(r,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(native))
(OUT/'visual-deformation-check.json').write_text(json.dumps(checks,indent=2)+'\n')
print('CAT POSE CHECK PASS',len(checks['poses']),'moving joints,',len(checks['no_surface_motion']),'with no measurable surface motion',flush=True)
