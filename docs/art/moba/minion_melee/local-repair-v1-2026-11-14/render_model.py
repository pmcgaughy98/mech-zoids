import bpy,json,sys,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/minion_melee/local-repair-v1-2026-11-14');BASE=Path('D:/dev/new-mech-rpg');cfg=json.loads((ROOT/'input-audit.json').read_text());entry=json.loads((ROOT/'model-entry.json').read_text());version=sys.argv[sys.argv.index('--')+1];source=Path(cfg['source']) if version=='before' else BASE/entry['source_model']['path'].removeprefix('res://') if version=='intact' else OUT/'melee-minion-rigged-local-repair-v1.glb'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source));bpy.context.view_layer.update();scene=bpy.context.scene;objects=[o for o in scene.objects if o.type=='MESH' and (version=='intact' or len(o.vertex_groups))]
def bounds():
 pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box];return Vector(tuple(min(p[i] for p in pts) for i in range(3))),Vector(tuple(max(p[i] for p in pts) for i in range(3)))
lo,hi=bounds();scale=1.7/(hi.z-lo.z) if version=='intact' else 1
if version=='intact':
 trans=Matrix.Translation(Vector((-(lo.x+hi.x)/2*scale,-(lo.y+hi.y)/2*scale,-lo.z*scale)))@Matrix.Scale(scale,4)
 for ob in objects:ob.matrix_world=trans@ob.matrix_world
 bpy.context.view_layer.update();lo,hi=bounds()
center=(lo+hi)/2;span=max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in range(3));size=span*1.18
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.world=bpy.data.worlds.new('Review');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.17,.20,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.view_settings.view_transform='AgX'
for offset,power in [((2,-3,4),1000),((-3,-1,2),700),((0,3,3),1000)]:
 bpy.ops.object.light_add(type='AREA',location=center+Vector(offset)*span);o=bpy.context.object;o.data.energy=power*span*span;o.data.size=span*3;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO';cam.data.clip_end=10000
def shot(name,target,offset,frame=size):
 cam.data.ortho_scale=frame;cam.location=Vector(target)+Vector(offset)*span;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
for name,offset in [('front',(0,-5,.1)),('left',(5,0,.1)),('right',(-5,0,.1)),('back',(0,5,.1)),('top',(0,0,5)),('underside',(0,0,-5)),('three-quarter',(3,-5,3))]:
 if '--focus' in sys.argv and name not in ['front','back']:continue
 frame=max(cfg['bounds'][1][0]-cfg['bounds'][0][0],1.7)*1.18 if name in ['front','back'] else size
 shot(version+'-'+name,center,offset,frame)
(OUT/(version+'-render-metadata.json')).write_text(json.dumps({'height_scale':scale,'bounds':[list(lo),list(hi)],'camera_size':size},indent=2))
if version=='after':
 for k,ref in entry['views'].items():
  im=bpy.data.images.load(str(BASE/ref['path'].removeprefix('res://')),check_existing=True);im.name='ORIGINAL_MELEE_MINION_'+k;im.pack();im.use_fake_user=True
 bpy.ops.wm.save_as_mainfile(filepath=str(source.with_suffix('.blend')))
print('RENDER COMPLETE',version,flush=True)
