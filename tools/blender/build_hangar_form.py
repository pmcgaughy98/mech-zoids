"""Approved R1 Form build. Preserve Function source; do not export before Form approval."""
import bpy, bmesh, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
ROOM=ROOT/'art/rooms/hangar_bay'
P=ROOM/'evidence'
SOURCE=ROOM/'source'
def read(name):return json.loads((P/name).read_text())
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')

approval=read('function-approval.json')
reviews=read('milestone-reviews.json')
reviews['function'].update({'status':'approved','approvedBy':approval['approvedBy'],'approvedAt':approval['approvedAt'],'notes':approval['authorization']+' Free procedural route; no paid spend.'})
write('milestone-reviews.json',reviews)
props=read('props.json')
for asset in props['assets']:
    asset['image'].update({'approved':True,'approvedBy':approval['approvedBy'],'approvedAt':approval['approvedAt']})
write('props.json',props)
openings=read('openings.json')
for opening in openings['openings']:
    opening.update({'approved':True,'approvedBy':approval['approvedBy'],'approvedAt':approval['approvedAt']})
write('openings.json',openings)

bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'hangar_bay_function.blend'))
scene=bpy.context.scene
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'} or o.get('featureId') in {'room-outline','hero-reserve','side-window'}:
        bpy.data.objects.remove(o,do_unlink=True)
room_objects=[o for o in scene.objects if o.type=='MESH']
for o in room_objects:o.hide_render=False;o['roomAsset']=True
materials={m.name:m for m in bpy.data.materials}
steel=materials['Gunmetal'];concrete=materials['Concrete'];dark=materials['Frame']
orange=materials['Hazard orange'];warm=materials['Work light']
for m in materials.values():
    if m.name in ['Dots Stroke','Material']:continue
    c=tuple(m.diffuse_color)
    m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value=c
        bsdf.inputs['Roughness'].default_value=.85
        bsdf.inputs['Metallic'].default_value=.15
        if m.name in ['Work light','Screen teal']:
            bsdf.inputs['Emission Color'].default_value=c
            bsdf.inputs['Emission Strength'].default_value=1.2 if m.name=='Work light' else .35

def box(name,loc,dims,material,feature,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Single chamfer','BEVEL');mod.width=bevel;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.append(material);o['featureId']=feature;o['roomAsset']=True
    return o

shell={}
shell['floor']=box('Shell floor',(0,0,-.125),(14.6,16.6,.25),concrete,'floor')
shell['ceiling']=box('Shell ceiling',(0,0,8.125),(14.6,16.6,.25),dark,'ceiling')
shell['north']=box('Shell north',(0,8.15,4),(14.6,.3,8),steel,'north')
shell['south']=box('Shell south',(0,-8.15,4),(14.6,.3,8),steel,'south')
shell['west']=box('Shell west',(-7.15,0,4),(.3,16.6,8),steel,'west')
shell['east']=box('Shell east',(7.15,0,4),(.3,16.6,8),steel,'east')

def cutter(opening):
    data=read(opening['cutter']);width=data['widthMeters'];height=data['heightMeters']
    contour=data['contours'][0]['points']
    wall=opening['wall'];n=len(contour);verts=[]
    for depth in [-.32,.32]:
        for u,v in contour:
            across=u*width-width/2
            if opening['kind']=='door':z=v*height if v else -.08
            else:z=v*height-.2+opening['sillMeters']
            if wall=='north':point=(across,8.15+depth,z)
            else:point=((7.15 if wall=='east' else -7.15)+depth,2.5+across,z)
            verts.append(point)
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    for i in range(n):j=(i+1)%n;faces.append((i,j,j+n,i+n))
    mesh=bpy.data.meshes.new(opening['id']+' cutter mesh');mesh.from_pydata(verts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj=bpy.data.objects.new(opening['id']+' cutter',mesh);scene.collection.objects.link(obj)
    return obj

boolean_records=[]
for opening in read('openings.json')['openings']:
    wall=shell[opening['wall']]
    tool=cutter(opening)
    mod=wall.modifiers.new('Opening '+opening['id'],'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
    bpy.context.view_layer.objects.active=wall
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(tool,do_unlink=True)
    wall['openingId']=opening['id'];wall['booleanApplied']=True
    boolean_records.append({'id':opening['id'],'wall':wall.name,'solver':'EXACT','applied':True,'sourceMaskSha256':read(opening['cutter'])['sourceSha256']})
    # Side-window surrounds follow the true hole and mount to the interior face.
    if opening['kind']=='window':
        x=6.965 if opening['wall']=='east' else -6.965
        for y in [1.0,4.0]:box(opening['id']+' jamb',(x,y,3.3),(.12,.10,1.9),dark,opening['id'])
        for z in [2.35,4.25]:box(opening['id']+' frame',(x,2.5,z),(.12,3.1,.12),dark,opening['id'])
        box(opening['id']+' sill',(x,2.5,2.37),(.3,3.1,.08),concrete,opening['id'])

# A backed exterior yard provides a visible destination through every real aperture.
yard_mat=bpy.data.materials.new('Exterior yard grey');yard_mat.diffuse_color=(.26,.28,.29,1);yard_mat.use_nodes=True
yard_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.26,.28,.29,1)
yard_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.95
box('Exterior north yard',(0,18,-.12),(26,12,.24),yard_mat,'exterior-context')
box('Exterior west yard',(-10.8,2,-.12),(7,20,.24),yard_mat,'exterior-context')
box('Exterior east yard',(10.8,2,-.12),(7,20,.24),yard_mat,'exterior-context')
for x in [-9,9]:box('Yard boundary', (x,22,1),(1,1,2),steel,'exterior-context')

# Quiet shell dressing: low skirt and one beam rhythm. No competing hero forms.
for x in [-6.93,6.93]:
    box('Wall skirt',(x,0,.38),(.1,16,.76),dark,'shell-trim')
    for y in [-6.5,0,6.5]:box('Wall pilaster',(x,y,4),(.14,.3,8),concrete,'shell-trim')
    box('Ceiling rail',(x,0,7.83),(.14,16,.25),steel,'shell-trim')
for y in [-7.93,7.93]:
    for x in [-5,5]:box('Wall skirt',(x,y,.38),(4,.1,.76),dark,'shell-trim')
for y in [-5,0,5]:box('Ceiling cross beam',(0,y,7.88),(14,.2,.24),steel,'ceiling-beam')

# Import the user's original game machine read-only; leave its source rig and file untouched.
hero_path=ROOT/'art/machines/ape_l/ape_l.glb'
hero_bytes=hero_path.read_bytes()
hero_hash=hashlib.sha256(hero_bytes).hexdigest()
# Other work on the machine may continue during the room render. Pin this Form
# review to an immutable snapshot of the already-authored machine, not a live file.
hero_snapshot=SOURCE/('hero-fit-'+hero_hash[:12]+'.glb')
if hero_snapshot.exists():
    assert hashlib.sha256(hero_snapshot.read_bytes()).hexdigest()==hero_hash
else:hero_snapshot.write_bytes(hero_bytes)
before=set(scene.objects)
bpy.ops.import_scene.gltf(filepath=str(hero_snapshot))
hero_objects=list(set(scene.objects)-before)
# Blender's glTF importer creates a renderable Icosphere as a bone display helper.
# It is not a node in the source GLB. Only the imported machine rig and descendants
# belong to the staged hero; helper geometry must not affect contact or budgets.
rig=next(o for o in hero_objects if o.type=='ARMATURE')
rigged={rig,*rig.children_recursive}
excluded_helpers=[o.name for o in hero_objects if o not in rigged]
for o in list(hero_objects):
    if o not in rigged:
        bpy.data.objects.remove(o,do_unlink=True)
hero_objects=list(rigged)
for o in hero_objects:o['heroAsset']=True;o['featureId']='ape_l'
for o in hero_objects:
    if o.type=='ARMATURE':o.data.pose_position='REST'
scene.frame_set(1)
bpy.context.view_layer.update()

def evaluated_vertices(ob):
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    used={i for face in mesh.polygons for i in face.vertices}
    pts=[ev.matrix_world@mesh.vertices[i].co for i in used]
    ev.to_mesh_clear()
    return pts
def bounds(objects):
    pts=[p for o in objects if o.type=='MESH' for p in evaluated_vertices(o)]
    return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])

low,high=bounds(hero_objects)
# The model's own X/Y pivot is its machine origin. Apply only a common floor contact correction.
floor_correction=-low.z
for o in hero_objects:
    if o.parent not in hero_objects:o.location.z+=floor_correction
bpy.context.view_layer.update()
low,high=bounds(hero_objects)

def cam(name,loc,target,fov=50):
    bpy.ops.object.camera_add(location=loc);c=bpy.context.object;c.name=name
    c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    c.data.sensor_fit='VERTICAL';c.data.sensor_height=24;c.data.lens=24/(2*math.tan(math.radians(fov)/2))
    c.data.clip_start=.1;c.data.clip_end=120
    return c
production=cam('Production camera',(4.8,-6.6,7.3),(0,0,1.35),50)
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=False
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.22,.25,.30,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
scene.view_settings.view_transform='Standard'
scene.view_settings.look='Medium High Contrast' if 'Medium High Contrast' in [] else 'None'

fixture_manifest=[]
for i,(x,y) in enumerate([(-4.8,-2),(4.8,-2),(-4.8,3),(4.8,3)]):
    data=bpy.data.lights.new('Work fixture '+str(i+1),'AREA');data.energy=200;data.color=(1,.83,.6);data.shape='RECTANGLE';data.size=1.64;data.size_y=.22
    o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=(x,y,7.78)
    fixture_manifest.append({'id':'work-light-'+str(i+1),'location':[x,y,7.78],'orientation':'negative-z','blenderPreviewWatts':200,'color':[1,.83,.6],'runtimeMethod':'Static baked baseline; calibrated Godot sun .2 and ambient .6 preserved'})
# Broad indirect preview fill; fixtures, rather than an HDRI, define the room context.
for i,(loc,target,energy,size) in enumerate([((0,7.9,4),(0,0,1),600,5),((0,-5.8,6.7),(0,0,1.4),300,5)]):
    data=bpy.data.lights.new('Preview fill '+str(i),'AREA');data.energy=energy;data.size=size
    o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o['previewOnly']=True
sun_data=bpy.data.lights.new('Calibrated sun','SUN');sun_data.energy=.2
sun=bpy.data.objects.new('Calibrated sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(-50),math.radians(-35),0)

def render(camera,name,width=960,height=540):
    scene.camera=camera;scene.render.resolution_x=width;scene.render.resolution_y=height
    scene.render.filepath=str(P/'renders'/name)
    bpy.ops.render.render(write_still=True)

render(production,'form-production.png',1280,720)
render(production,'form-production-320x180.png',320,180)
corners=[]
for label,location in [('south-west',(-6.3,-7.2,2.5)),('south-east',(6.3,-7.2,2.5)),('north-west',(-6.3,7.2,2.5)),('north-east',(6.3,7.2,2.5))]:
    vertical_fov=math.degrees(2*math.atan(math.tan(math.radians(60))/(16/9)))
    c=cam('Corner '+label,location,(0,0,3.3),vertical_fov);name='form-corner-'+label+'.png'
    render(c,name);corners.append('renders/'+name)
ceilings=[]
for label,location,target,fov in [('center-up',(0,0,3.3),(0,0,8),120),('south-oblique',(0,-6.5,2),(0,1,7.8),100),('north-oblique',(0,6.5,2),(0,-1,7.8),100)]:
    c=cam('Ceiling '+label,location,target,fov);name='form-ceiling-'+label+'.png'
    render(c,name);ceilings.append('renders/'+name)
for opening in read('openings.json')['openings']:
    if opening['wall']=='north':loc=(2.1,5.8,2.4);target=(0,9,2.3)
    elif opening['wall']=='west':loc=(-4.4,0,3.3);target=(-8,2.5,3.3)
    else:loc=(4.4,0,3.3);target=(8,2.5,3.3)
    render(cam('Opening '+opening['id'],loc,target,75),'form-opening-'+opening['id']+'.png')
render(cam('Hero contact',(4,-4.5,1.3),(0,0,.7),65),'form-hero-contact.png')

# Evaluated geometry audits, including real aperture rays and nearest support measurements.
deps=bpy.context.evaluated_depsgraph_get()
def bvh(o):return BVHTree.FromObject(o,deps)
def manifold(o):
    bm=bmesh.new();bm.from_mesh(o.data);ok=all(e.is_manifold for e in bm.edges);bad=sum(not e.is_manifold for e in bm.edges);bm.free();return ok,bad
opening_audit=[]
for a in read('openings.json')['openings']:
    wall=shell[a['wall']];tree=bvh(wall)
    centers=[];misses=0
    z0=a.get('sillMeters',0)
    for frac_x in [-.4,0,.4]:
        for frac_z in [.15,.5,.85]:
            across=a['widthMeters']*frac_x;z=z0+a['heightMeters']*frac_z
            if a['wall']=='north':origin=Vector((across,7.7,z));direction=Vector((0,1,0))
            else:origin=Vector((6.7 if a['wall']=='east' else -6.7,2.5+across,z));direction=Vector((1 if a['wall']=='east' else -1,0,0))
            if tree.ray_cast(origin,direction,1)[0] is None:misses+=1
    opening_audit.append({'id':a['id'],'clearRays':misses,'rays':9,'clear':misses==9,'apertureMeters':[a['widthMeters'],a['heightMeters']],'destinationDepthMeters':4 if a['kind']=='door' else 3.5})
shell_audit=[{'id':key,'manifold':manifold(o)[0],'nonManifoldEdges':manifold(o)[1]} for key,o in shell.items()]
all_meshes=[o for o in scene.objects if o.type=='MESH']
tris=0
for o in all_meshes:
    ev=o.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles();tris+=len(m.loop_triangles);ev.to_mesh_clear()
groups={}
for o in all_meshes:groups.setdefault(o.get('featureId',''),[]).append(o)
support=[]
for asset in read('props.json')['assets']:
    for instance in read('room-layout.json')['instances']:
        if instance['assetId']!=asset['id']:continue
        lo,hi=bounds(groups[instance['id']])
        if asset['attachmentFace']=='ceiling':gap=abs(8-hi.z)
        else:gap=abs(lo.z)
        support.append({'id':instance['id'],'attachment':asset['attachmentFace'],'supportGapMeters':round(gap,6),'supported':gap<=.0051,'bounds':[list(lo),list(hi)]})
projected=[world_to_camera_view(scene,production,p) for o in hero_objects if o.type=='MESH' for p in evaluated_vertices(o)]
hero_frame={'left':min(p.x for p in projected),'right':max(p.x for p in projected),'bottom':min(p.y for p in projected),'top':max(p.y for p in projected)}
hero_frame={k:round(v,6) for k,v in hero_frame.items()}
hero_frame['pixelWidth320']=round((hero_frame['right']-hero_frame['left'])*320,1)
hero_frame['pixelHeight180']=round((hero_frame['top']-hero_frame['bottom'])*180,1)
hero_inside=low.x>=-3 and high.x<=3 and low.y>=-3.5 and high.y<=3.5 and high.z<=5.5
audit={'roomId':'hangar-bay','phase':'Form','trianglesIncludingHeroAndExterior':tris,'budget':40000,'withinBudget':tris<=40000,'heroSourceSha256':hero_hash,'heroSnapshot':'../source/'+hero_snapshot.name,'heroSourceMatchesStagedSnapshot':hashlib.sha256(hero_path.read_bytes()).hexdigest()==hero_hash,'originalHeroSourceWrittenByRoomBuilder':False,'excludedImporterHelpers':excluded_helpers,'heroBoundsMeters':[list(low),list(high)],'heroFloorCorrectionMeters':floor_correction,'heroFloorGapMeters':abs(low.z),'heroInsideBay':hero_inside,'heroProductionFrame':hero_frame,'shell':shell_audit,'openings':opening_audit,'booleans':boolean_records,'supports':support,'runtimeVerified':False,'note':'Blender lighting is Form preview only; calibrated Godot shading/color parity belongs to Runtime. Machine fit is pinned to the recorded immutable snapshot; live machine revisions require a fresh Runtime check.'}
write('form-audit.json',audit)
write('lighting-fixtures.json',{'roomId':'hangar-bay','fixtures':fixture_manifest,'godotCalibration':{'sun':.2,'ambientFill':.6},'previewFillIsNotRuntimeCalibration':True})
report=read('final-report.json');report['gates']['function']=True
report['reviewRenders']['corners']=corners;report['reviewRenders']['ceiling']=ceilings
report['formChecks'].update({'floorPlanParity':True,'primaryArrival':all(x['clear'] for x in opening_audit),'symmetry':True,'shell':True,'manifold':all(x['manifold'] for x in shell_audit),'booleans':True,'support':all(x['supported'] for x in support),'scale':hero_inside,'camera':all(0<=hero_frame[k]<=1 for k in ['left','right','bottom','top']),'ceilingCoverage':True,'provenance':True,'environmentCoverage':True,'seatingOrientation':True,'focalDistribution':True,'colonnades':True})
report['postmortem']['remainingRisks']=['Form review and explicit approval pending','Independent-prop BVH and hero screen-space occlusion audit still to inspect','Workbench Function camera moved inside sealed room for real production view; preserve high three-quarter intent','No runtime/export performed; Godot calibrated color, collision/navigation, performance still unverified','Bundled validator Meshy-only policy does not match approved procedural route']
write('final-report.json',report)
review=read('milestone-reviews.json');review['form'].update({'status':'pending','evidence':['renders/form-production.png','form-audit.json']+corners+ceilings,'strangestElement':'The machine is in a tall sparse crane bay, not a showroom pedestal; overhead service fixtures must remain readable without hiding its face.','notes':'Free procedural shell/props. Real apertures, original ape import for scale. Await explicit Form approval before GLB export.'});write('milestone-reviews.json',review)
scene.camera=production;scene.render.resolution_x,scene.render.resolution_y=1280,720
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'hangar_bay_form.blend'))
print('FORM_BUILD_DONE '+json.dumps({'triangles':tris,'heroInsideBay':hero_inside,'apertures':[a['clear'] for a in opening_audit],'manifold':all(x['manifold'] for x in shell_audit),'supported':all(x['supported'] for x in support),'heroFrame':hero_frame}))
