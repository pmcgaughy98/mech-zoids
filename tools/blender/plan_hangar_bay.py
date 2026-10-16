"""R1 Function evidence only. No final shell, export, or Godot integration."""
import bpy, math, json, hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ROOM = ROOT / 'art/rooms/hangar_bay'
PKG = ROOM / 'evidence'
SOURCE = ROOM / 'source'
SOURCE.mkdir(parents=True, exist_ok=True)
(SOURCE / '.gdignore').write_text('')
(PKG / '.gdignore').write_text('')
def write(name, value):
    (PKG / name).write_text(json.dumps(value, indent=2) + '\n')
def read(name):
    return json.loads((PKG / name).read_text())

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x, scene.render.resolution_y = 960, 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = 'BOTH'
scene.display.shading.show_object_outline = True
scene.display.shading.background_type = 'WORLD'
scene.world.color = (0.055,0.065,0.075)
scene.view_settings.view_transform = 'Standard'

def mat(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color,1)
    return m
steel = mat('Gunmetal',(.20,.23,.26))
concrete = mat('Concrete',(.36,.38,.40))
dark = mat('Frame',(.08,.09,.105))
orange = mat('Hazard orange',(.72,.31,.09))
teal = mat('Screen teal',(.10,.58,.62))
warm = mat('Work light',(.82,.70,.48))
materials = [steel,concrete,dark,orange,teal,warm]
def finish(ob, name, material, group, layer='lower-room'):
    ob.name = name
    ob.data.materials.append(material)
    ob['featureId'],ob['planLayer'] = group,layer
    return ob
def box(name, loc, dims, material=steel, group='', layer='lower-room', bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod=o.modifiers.new('Single chamfer','BEVEL');mod.width=bevel;mod.segments=1
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return finish(o,name,material,group,layer)
def cylinder(name, loc, radius, depth, material=steel, group='', layer='lower-room', axis='z'):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=radius, depth=depth, location=loc)
    o=bpy.context.object
    if axis=='x':o.rotation_euler.y=math.pi/2
    if axis=='y':o.rotation_euler.x=math.pi/2
    return finish(o,name,material,group,layer)
def beam(name,a,b,width,material,group,layer='lower-room'):
    mid=(Vector(a)+Vector(b))/2
    o=box(name,mid,(width,width,(Vector(b)-Vector(a)).length),material,group,layer)
    o.rotation_euler=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_euler()
    return o
def camera(name,loc,target,scale=None,fov=42):
    bpy.ops.object.camera_add(location=loc)
    o=bpy.context.object;o.name=name
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    if scale:o.data.type='ORTHO';o.data.ortho_scale=scale
    else:o.data.lens=36/(2*math.tan(math.radians(fov)/2))
    return o
def render(cam,path,width=960,height=720):
    scene.camera=cam
    scene.render.resolution_x,scene.render.resolution_y=width,height
    scene.render.filepath=str(PKG/path)
    bpy.ops.render.render(write_still=True)

specs=[
 ('gantry-crane','Overhead lift for armor and ballast, parked clear of hero',[8.8,8.0,6.5],1,3500,'freestanding','negative-y'),
 ('tool-cart','Mobile tools at mechanic station',[1.2,.65,1.1],1,1000,'floor','negative-y'),
 ('parts-rack','Shelved spare armor and frame parts',[2.4,.7,2.2],1,1400,'floor','negative-y'),
 ('ballast-pallet','Three heavy ballast blocks, grey bodies with orange caps',[1.8,1.2,.85],2,900,'floor','negative-y'),
 ('coolant-tanks','Closed coolant service with visible grounded tanks and pipework',[1.4,.8,1.6],1,1200,'floor','negative-y'),
 ('service-console','Machine/deck service point with readable teal screen',[1.3,.8,1.45],1,1000,'floor','negative-y'),
 ('cable-tray','Protected overhead cable distribution',[4.0,.45,.18],2,600,'ceiling','negative-z'),
 ('work-light','Flat flush-mounted warm work lights',[1.8,.3,.2],4,400,'ceiling','negative-z')]
prototype_objects={}
def prototype(kind):
    before=set(bpy.data.objects)
    g=kind
    layer='reflected-ceiling' if kind in ['cable-tray','work-light'] else 'lower-room'
    if kind=='gantry-crane':
        for x in [-4.05,4.05]:
            for y in [-3.65,3.65]:
                box(g+' foot',(x,y,.06),(.65,.65,.12),dark,g)
                box(g+' post',(x,y,3.25),(.24,.28,6.5),steel,g)
            box(g+' rail',(x,0,6.24),(.30,7.6,.38),steel,g,'reflected-ceiling')
        box(g+' bridge',(0,2.7,6.25),(8.4,.45,.50),steel,g,'reflected-ceiling')
        box(g+' trolley',(-2.8,2.7,5.95),(.75,.75,.4),orange,g,'reflected-ceiling',.06)
        beam(g+' cable',(-2.8,2.7,5.8),(-2.8,2.7,4.3),.05,dark,g,'reflected-ceiling')
        box(g+' hook',(-2.8,2.7,4.2),(.25,.18,.2),dark,g,'reflected-ceiling')
    elif kind=='tool-cart':
        box(g+' cabinet',(0,0,.62),(1.15,.6,.78),steel,g,bevel=.045)
        box(g+' top',(0,0,1.05),(1.2,.65,.1),concrete,g)
        for z in [.43,.64,.85]:
            box(g+' drawer',(0,-.31,z),(1.02,.025,.14),dark,g)
            box(g+' handle',(0,-.34,z),(.45,.05,.04),orange,g)
        for x in [-.44,.44]:
            for y in [-.22,.22]:cylinder(g+' wheel',(x,y,.12),.12,.08,dark,g,axis='x')
    elif kind=='parts-rack':
        for x in [-1.08,1.08]:
            for y in [-.28,.28]:box(g+' post',(x,y,1.1),(.12,.12,2.2),steel,g)
        for z in [.08,.8,1.5]:box(g+' shelf',(0,0,z),(2.4,.7,.08),concrete,g)
        for x in [-.72,0,.72]:
            o=box(g+' armor',(x,0,1.77),(.46,.18,.52),steel,g,bevel=.08);o.rotation_euler.x=.18
            cylinder(g+' joint',(x,0,1.03),.18,.35,dark,g,axis='y')
        beam(g+' rear brace',(-1.1,.3,.1),(1.1,.3,2.1),.075,dark,g)
    elif kind=='ballast-pallet':
        for y in [-.44,0,.44]:box(g+' bearer',(0,y,.08),(1.8,.16,.16),dark,g)
        box(g+' deck',(0,0,.2),(1.8,1.2,.09),steel,g)
        for x in [-.57,0,.57]:
            box(g+' block',(x,0,.52),(.47,.82,.54),concrete,g,bevel=.035)
            box(g+' cap',(x,0,.81),(.48,.84,.08),orange,g,bevel=.02)
    elif kind=='coolant-tanks':
        box(g+' base',(0,0,.08),(1.4,.8,.16),dark,g)
        for x in [-.37,.37]:
            cylinder(g+' tank',(x,0,.85),.29,1.35,steel,g)
            cylinder(g+' valve',(x,0,1.57),.1,.06,orange,g)
            box(g+' band',(x,-.29,1.03),(.35,.025,.1),orange,g)
        beam(g+' pipe',(-.37,-.34,.4),(.37,-.34,.4),.09,steel,g)
    elif kind=='service-console':
        box(g+' plinth',(0,0,.07),(1.3,.8,.14),dark,g)
        box(g+' pedestal',(0,.12,.55),(.75,.4,.9),steel,g,bevel=.035)
        o=box(g+' panel',(0,0,1.18),(1.3,.15,.5),steel,g,bevel=.035);o.rotation_euler.x=-.40
        o=box(g+' screen',(0,-.086,1.19),(1.08,.025,.3),teal,g);o.rotation_euler.x=-.40
        box(g+' keyboard',(0,-.25,.98),(1.1,.42,.08),dark,g)
    elif kind=='cable-tray':
        box(g+' bottom',(0,0,.03),(4,.45,.06),dark,g,layer)
        for y in [-.2,.2]:box(g+' lip',(0,y,.09),(4,.05,.18),steel,g,layer)
        for x in [-1.8,-1.2,-.6,0,.6,1.2,1.8]:box(g+' rung',(x,0,.04),(.06,.45,.06),steel,g,layer)
        for y in [-.09,0,.09]:box(g+' cable',(0,y,.075),(3.8,.04,.04),dark,g,layer)
    elif kind=='work-light':
        box(g+' housing',(0,0,.1),(1.8,.3,.2),dark,g,layer,bevel=.025)
        box(g+' lens',(0,0,.006),(1.64,.22,.018),warm,g,layer)
    return list(set(bpy.data.objects)-before)

positions={
 'gantry-crane':[(0,0,0,0)],
 'tool-cart':[(-5.6,-1.5,0,-math.pi/2)],
 'parts-rack':[(-5.2,6.5,0,0)],
 'ballast-pallet':[(-5.4,4.2,0,0),(5.4,4.2,0,0)],
 'coolant-tanks':[(5.8,6.4,0,0)],
 'service-console':[(5.5,-1.8,0,math.pi/2)],
 'cable-tray':[(-6.3,0,7.82,math.pi/2),(6.3,0,7.82,math.pi/2)],
 'work-light':[(-4.8,-2,7.8,0),(4.8,-2,7.8,0),(-4.8,3,7.8,0),(4.8,3,7.8,0)]}

assets=[];instances=[]
for kind,function,dims,count,poly,mount,front in specs:
    objects=prototype(kind);prototype_objects[kind]=objects
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render=o not in objects
    biggest=max(dims)
    camera_height=-biggest*1.3 if kind=='work-light' else biggest*1.3
    cam=camera('reference '+kind,(biggest*1.5,-biggest*2,camera_height),(0,0,dims[2]*.45),biggest*2)
    render(cam,'images/'+kind+'.png',640,480)
    cam.hide_render=True
    prompt=f'Procedural Blender reference: {function}. Dimensions {dims} m, chunky flat color shapes, gunmetal/concrete, orange caps/trim, teal screens only. Grounded supports, complete front and back, no machine-green room paint. Exact geometry is produced by plan_hangar_bay.py.'
    assets.append({'id':kind,'function':function,'description':'Original chunky procedural prototype; review before final build','class':'reusable','dimensionsMeters':dims,'intendedInstances':count,'attachmentFace':mount,'semanticFront':front,'targetPolycount':poly,'productionMethod':'Blender procedural; no Meshy','rejectionCriteria':['Outside declared dimensional envelope','Floating or missing support','Intersects central hero reserve or circulation','Noisy details disappear at 320x180'],'image':{'prompt':prompt,'generator':'Blender 5.2 Workbench orthographic render of original procedural prototype','source':'images/'+kind+'.png','approved':False,'approvedBy':''},'attempts':[]})
    # Keep the first prototype as the first room instance, duplicate geometry for repetitions.
    for idx,(x,y,z,rotation) in enumerate(positions[kind]):
        group=kind+'-'+str(idx+1)
        instances.append({'id':group,'assetId':kind,'location':[x,y,z],'rotationDegrees':[0,0,math.degrees(rotation)],'scale':[1,1,1]})
        active=objects if idx==0 else [o.copy() for o in objects]
        if idx:
            for o in active:bpy.context.collection.objects.link(o)
        for o in active:
            # Repeated assets duplicate the already placed first instance only when its transform is zero.
            local=o.location.copy()
            if idx and positions[kind][0][:3] != (0,0,0):
                px,py,pz,pr=positions[kind][0]
                local-=Vector((px,py,pz))
                c,s=math.cos(-pr),math.sin(-pr)
                local=Vector((local.x*c-local.y*s,local.x*s+local.y*c,local.z))
                o.rotation_euler.z-=pr
            c,s=math.cos(rotation),math.sin(rotation)
            o.location=(local.x*c-local.y*s+x,local.x*s+local.y*c+y,local.z+z)
            o.rotation_euler.z+=rotation;o['featureId']=group
            o.hide_render=False

# Function spatial study: floor, low perimeter guides and scheduled aperture indicators only.
# A final sealed shell and Boolean cuts belong to Form, after approval.
floor=box('Floor extent',(0,0,-.1),(14,16,.2),concrete,'room-outline')
apron=box('Exterior apron',(0,10,-.1),(8,4,.2),concrete,'exterior-apron')
for x in [-7,7]:box('Side boundary',(x,0,.35),(.15,16,.7),steel,'room-outline')
box('South boundary',(0,-8,.35),(14,.15,.7),steel,'room-outline')
for x in [-5,5]:box('North boundary',(x,8,.35),(4,.15,.7),steel,'room-outline')
for x in [-3.1,3.1]:box('Door reveal',(x,8,2.5),(.2,.4,5),steel,'bay-door')
box('Door lintel',(0,8,5.1),(6.4,.4,.2),steel,'bay-door','reflected-ceiling')
for x in [-6.6,6.6]:
    for y in [-6.5,6.5]:box('Engaged column',(x,y,4),(.3,.4,8),steel,'columns')
for x in [-3,3]:box('Bay side mark',(x,0,.005),(.07,7,.01),orange,'floor-markers')
for y in [-3.5,3.5]:box('Bay end mark',(0,y,.005),(6,.07,.01),orange,'floor-markers')
# Staff lanes stay beside the parked machine and inside the gantry posts.
for x in [-2.95,2.95]:
    for y in [-6,-4,-2,0,2,4,6]:box('Staff lane dash',(x,y,.007),(.055,.65,.012),warm,'circulation')
# Entrance/apron threshold markings and modest sign bracket.
for x in [-2.5,-1.5,-.5,.5,1.5,2.5]:box('Apron stripe',(x,8.2,.007),(.3,.6,.012),orange,'ingress-props')
box('Bay sign',(0,8,5.5),(1.8,.12,.4),dark,'main-sign','reflected-ceiling')
for x in [-6.7,6.7]:box('West window reference' if x<0 else 'East window reference',(x,2.5,3.2),(.1,3,1.8),teal,'side-window')
# A wire envelope is deliberately a reserve, never a fake finished machine.
for x in [-1.7,1.7]:
    for y in [-1.2,1.2]:beam('Hero envelope',(x,y,.03),(x,y,2.7),.025,teal,'hero-reserve')
for z in [.03,2.7]:
    for x in [-1.7,1.7]:beam('Hero envelope',(x,-1.2,z),(x,1.2,z),.025,teal,'hero-reserve')
    for y in [-1.2,1.2]:beam('Hero envelope',(-1.7,y,z),(1.7,y,z),.025,teal,'hero-reserve')

mesh_objects=[o for o in bpy.data.objects if o.type=='MESH']
for o in mesh_objects:o.hide_render=False
production=camera('Function production camera',(14,-23,17),(0,1,3),fov=56)
scene.render.film_transparent=False
render(production,'renders/function-visual-target.png',1280,720)
render(production,'renders/function-320x180.png',320,180)
scene.render.film_transparent=True

# Orthographic projections of the same authored mesh objects; labels added in external UI only.
original_colors={m.name:tuple(m.diffuse_color) for m in materials}
for m in materials:m.diffuse_color=(.6,.6,.6,1)
scene.display.shading.light='FLAT';scene.display.shading.show_shadows=False
scene.display.shading.show_cavity=False
scene.display.shading.object_outline_color=(.0,.0,.0)
plan_cam=camera('Lower plan',(0,1,30),(0,1,0),26)
for o in mesh_objects:
    o.hide_render=o.get('planLayer')=='reflected-ceiling' or o['featureId']=='hero-reserve'
render(plan_cam,'plans/lower-room.png',1100,1100)
for o in mesh_objects:o.hide_render=o.get('planLayer')!='reflected-ceiling'
render(plan_cam,'plans/reflected-ceiling.png',1100,1100)
for o in mesh_objects:o.hide_render=False
for name,location in [('north',(0,30,4)),('south',(0,-30,4)),('east',(30,0,4)),('west',(-30,0,4))]:
    c=camera('Elevation '+name,location,(0,0,4),19)
    render(c,'plans/elevation-'+name+'.png',1100,620)
for m in materials:m.diffuse_color=original_colors[m.name]
scene.display.shading.light='STUDIO';scene.display.shading.show_shadows=True
scene.camera=production
scene.render.resolution_x,scene.render.resolution_y=1280,720
scene.render.film_transparent=False

surfaces=[{'id':'floor','dimensionsMeters':[14,16,.25],'center':[0,0,-.125]},
 {'id':'ceiling','dimensionsMeters':[14,16,.25],'center':[0,0,8.125]},
 {'id':'north','dimensionsMeters':[14,.3,8],'center':[0,8.15,4]},
 {'id':'south','dimensionsMeters':[14,.3,8],'center':[0,-8.15,4]},
 {'id':'west','dimensionsMeters':[.3,16,8],'center':[-7.15,0,4]},
 {'id':'east','dimensionsMeters':[.3,16,8],'center':[7.15,0,4]}]
brief=read('room-brief.json')
brief.update({'purpose':'Home maintenance hangar presenting the selected animal machine between missions; Function proposal, nothing here is canon','runtimeSurface':'Godot 4.7.2 future scenes/rooms/hangar_bay.tscn; existing 2D base unchanged','boundsMeters':[14,16,8],
 'hero':{'id':'ape_l','role':'Machine in central maintenance cradle, at origin facing -Y (camera)','reservedBoundsMeters':[6,7,5.5]},
 'symmetry':{'mode':'bilateral','order':2,'appliesTo':['architecture','barriers','circulation','repeatedProps'],'exceptions':['Tool cart on west, console on east: mechanic and pilot stations differ in function','Parts rack west and coolant tanks east: different service jobs; both outside reserve','Gantry trolley parked rear-left for clear hero silhouette']},
 'circulation':{'description':'Two 1.2m staff lanes at x=+/-2.95m, beside the parked machine and inside the gantry posts, from south approach to north 6m bay door and 4m apron. Machine remains parked during base interactions.','minimumClearanceMeters':1.2,'centerLines':[[[-2.95,-6,0],[-2.95,6,0]],[[2.95,-6,0],[2.95,6,0]]]},
 'productionCamera':{'viewport':[320,180],'location':[14,-23,17],'target':[0,1,3],'verticalFovDegrees':56},
 'performanceBudget':{'maxSceneTriangles':40000,'maxVLowBytes':8000000,'maxHighTextureBytes':4194304},
 'creditBudget':{'maximumCredits':0,'approvalRequired':True},
 'artifacts':{'floorPlan':'plans/lower-room.png','reflectedCeilingPlan':'plans/reflected-ceiling.png','planMetadata':'plan-metadata.json','wallElevations':['plans/elevation-'+d+'.png' for d in ['north','south','east','west']],'visualTarget':'renders/function-visual-target.png','openingContactSheet':'masks/opening-contact-sheet.png'},
 'lightingContract':{'sunEnergy':.2,'ambientFillEnergy':.6,'notes':'Calibrated Godot values retained at Runtime; Blender Workbench preview does not prove lighting parity'},
 'heroModelPath':'res://art/machines/ape_l/ape_l.glb'})
write('room-brief.json',brief)
props=read('props.json');props['generation']={'provider':'blender-procedural','apiModel':None,'hardCreditCeiling':0,'maxChargedAttemptsPerAsset':2,'pricingVerifiedAt':'2026-10-11','pricingSource':'https://docs.meshy.ai/en/api/pricing','note':'No Meshy requested. meshy-5 retired Oct 10; task R1 explicitly prefers free procedural props.'};props['assets']=assets;write('props.json',props)
layout=read('room-layout.json');layout.update({'surfaces':surfaces,'instances':instances,'productionCamera':brief['productionCamera'],'phase':'Function prototypes; surfaces scheduled only, final shell not built'});write('room-layout.json',layout)
plan=read('plan-metadata.json');plan.update({'coverage':['room-outline','cutouts','openings','exterior-apron','main-sign','ingress-props','floor-markers','barriers','columns','circulation','placed-features'],'features':[{'id':o.name,'featureId':o['featureId'],'layer':o.get('planLayer'),'centerMeters':list(o.location),'dimensionsMeters':list(o.dimensions)} for o in mesh_objects],'barriers':'No freestanding rail barriers proposed; gantry posts and room shell define bay boundaries','cutouts':'North bay door and two symmetric side windows; masks and final Boolean schedule in openings.json','heroReserve':{'center':[0,0,0],'bayFootprint':[6,7],'displayProxy':[3.4,2.4,2.7],'source':'Task R1 dimensions, not runtime model fit'}});write('plan-metadata.json',plan)
openings=read('openings.json');openings['primaryArrival']={'openingId':'bay-door','exception':''};openings['openings']=[
 {'id':'bay-door','kind':'door','wall':'north','widthMeters':6,'heightMeters':5,'thresholdMeters':0,'depthMeters':.3,'destination':'Four-metre exterior dispatch apron, with open yard beyond','mask':'masks/bay-door.png','cutter':'masks/bay-door.json','approved':False},
 {'id':'west-window','kind':'window','wall':'west','widthMeters':3,'heightMeters':1.8,'sillMeters':2.4,'depthMeters':.3,'destination':'Visible exterior yard beyond thick wall reveal; non-traversable','mask':'masks/west-window.png','cutter':'masks/west-window.json','approved':False},
 {'id':'east-window','kind':'window','wall':'east','widthMeters':3,'heightMeters':1.8,'sillMeters':2.4,'depthMeters':.3,'destination':'Visible exterior yard beyond thick wall reveal; non-traversable','mask':'masks/east-window.png','cutter':'masks/east-window.json','approved':False}];write('openings.json',openings)
reviews=read('milestone-reviews.json');reviews['function'].update({'status':'pending','evidence':['plans/lower-room.png','plans/reflected-ceiling.png','images/prop-contact-sheet.png','masks/opening-contact-sheet.png','renders/function-visual-target.png'],'strangestElement':'The teal wire box is only the measured hero reserve; it promises no finished machine or runtime interaction. Actual ape fit belongs to Form.','notes':'Await Preston approval of layout, eight reference prototypes, and opening dimensions. Procedural path requested in CODEX_TASKS_3D_ROOMS.md.'});write('milestone-reviews.json',reviews)
report=read('final-report.json');report['postmortem']['remainingRisks']=['Function approval pending','Actual ape_l pose/animation bounds and occlusion not verified until Form','Workbench preview is not calibrated Godot lighting','Bundled validator is Meshy-only despite explicit procedural task; record this incompatibility without inventing approvals'];write('final-report.json',report)
stats={'phase':'Function-only','prototypeTriangles':sum(len(p.vertices)-2 for o in mesh_objects for p in o.data.polygons),'roomBudgetTriangles':40000,'heroTriangleReserve':11000,'assetFamilyCount':8,'instanceCount':len(instances),'paidCreditsUsed':0,'machineModelUnchanged':True,'openBlenderUntouched':True}
write('function-measurements.json',stats)
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/'hangar_bay_function.blend'))
print('FUNCTION_EVIDENCE_READY '+json.dumps(stats))
