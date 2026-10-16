"""World-space support, independent-prop BVH, ceiling and camera checks for R1."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
ROOM=ROOT/'art/rooms/hangar_bay';P=ROOM/'evidence'
def read(name):return json.loads((P/name).read_text())
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
bpy.ops.wm.open_mainfile(filepath=str(ROOM/'source/hangar_bay_form.blend'))
scene=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get()
def meshdata(objects):
    verts=[];faces=[]
    for ob in objects:
        ev=ob.evaluated_get(deps);m=ev.to_mesh();base=len(verts)
        verts.extend(ev.matrix_world@v.co for v in m.vertices)
        faces.extend([base+i for i in f.vertices] for f in m.polygons)
        ev.to_mesh_clear()
    return verts,faces
def bounds(verts):return Vector([min(p[k] for p in verts) for k in range(3)]),Vector([max(p[k] for p in verts) for k in range(3)])
def overlaps(a,b):return all(a[0][k]<b[1][k]-.0001 and b[0][k]<a[1][k]-.0001 for k in range(3))
group_meshes={}
for ob in scene.objects:
    if ob.type=='MESH' and not ob.hide_render:group_meshes.setdefault(ob.get('featureId',''),[]).append(ob)
instance_ids=[a['id'] for a in read('room-layout.json')['instances']]
groups={}
for group in instance_ids+['ape_l']:
    v,f=meshdata(group_meshes[group]);groups[group]={'bounds':bounds(v),'tree':BVHTree.FromPolygons(v,f,all_triangles=False)}
collisions=[];tested=0
keys=list(groups)
for i,key in enumerate(keys):
    for other in keys[i+1:]:
        tested+=1
        a,b=groups[key],groups[other]
        if overlaps(a['bounds'],b['bounds']):
            hits=a['tree'].overlap(b['tree'])
            if hits:collisions.append({'a':key,'b':other,'intersectingTriangles':len(hits)})

# A point above the real visible hero gives the center-up ceiling camera a clear sightline.
ceiling=scene.objects['Shell ceiling']
cv,cf=meshdata([ceiling]);ceiling_tree=BVHTree.FromPolygons(cv,cf)
attachment=[]
for a in read('props.json')['assets']:
    if a['attachmentFace']!='ceiling':continue
    for instance in read('room-layout.json')['instances']:
        if instance['assetId']!=a['id']:continue
        lo,hi=groups[instance['id']]['bounds'];size=hi-lo
        center=(lo+hi)/2
        ray_origin=Vector((center.x,center.y,hi.z-.01))
        loc,norm,index,distance=ceiling_tree.ray_cast(ray_origin,Vector((0,0,1)),.1)
        dot=abs(norm.z) if norm else 0
        attachment.append({'id':instance['id'],'shortestDimensionAxis':'z' if size.z<=min(size.x,size.y) else 'other','supportDistanceMeters':round(distance-.01,6) if distance else None,'shortAxisNormalDot':dot,'attached':loc is not None and abs(distance-.01)<=.0051 and dot>=.95,'largestFaceParallelToCeiling':size.z<=min(size.x,size.y)})

hero_verts,hero_faces=meshdata(group_meshes['ape_l'])
cam=scene.objects['Production camera'];hero_tree=groups['ape_l']['tree']
room_meshes=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.get('heroAsset') and o.get('featureId') not in ['floor-markers','circulation','ingress-props']]
rv,rf=meshdata(room_meshes);room_tree=BVHTree.FromPolygons(rv,rf)
# Sample the hero's visible surface from the production camera. Ignore vertices on the back.
front=0;occluded=0
for v in hero_verts[::max(1,len(hero_verts)//2000)]:
    delta=v-cam.location;length=delta.length
    first=hero_tree.ray_cast(cam.location,delta.normalized(),length+.01)
    if first[0] is None or first[3]<length-.035:continue
    front+=1
    block=room_tree.ray_cast(cam.location,delta.normalized(),max(0,length-.04))
    if block[0] is not None:occluded+=1

# Floor and ceiling enclosure rays should only escape through scheduled openings.
shell_objs=[o for o in scene.objects if o.name.startswith('Shell ')]
sv,sf=meshdata(shell_objs);shell_tree=BVHTree.FromPolygons(sv,sf)
enclosure=[]
for direction in [Vector((1,0,0)),Vector((-1,0,0)),Vector((0,-1,0)),Vector((0,0,1)),Vector((0,0,-1))]:
    hit=shell_tree.ray_cast(Vector((0,0,4)),direction,30)
    enclosure.append({'direction':list(direction),'hitsShell':hit[0] is not None,'distance':round(hit[3],5) if hit[3] else None})
# North at z=6 is above the door, so it must hit retained wall.
hit=shell_tree.ray_cast(Vector((0,0,6)),Vector((0,1,0)),30)
enclosure.append({'direction':[0,1,0],'testHeight':6,'hitsShell':hit[0] is not None,'distance':round(hit[3],5) if hit[3] else None})

audit=read('form-audit.json')
audit.update({'independentPropsBVH':{'pairsTested':tested,'collisions':collisions,'passed':not collisions},'ceilingAttachments':attachment,'heroScreenOcclusion':{'frontSurfaceSamples':front,'occludedSamples':occluded,'occludedFraction':round(occluded/max(1,front),5),'passed':front>0 and occluded==0},'shellEnclosureRays':enclosure,'enclosurePassed':all(x['hitsShell'] for x in enclosure)})
write('form-audit.json',audit)
report=read('final-report.json')
report['formChecks'].update({'collisions':not collisions,'heroClearance':audit['heroInsideBay'] and not collisions,'attachmentOrientation':all(x['attached'] for x in attachment),'ceilingAttachmentOrientation':all(x['attached'] and x['largestFaceParallelToCeiling'] for x in attachment),'screenClearance':front>0 and occluded==0,'shell':all(x['hitsShell'] for x in enclosure)})
report['postmortem']['corrections']=['Excluded Blender-importer-generated bone-display Icosphere from staged hero bounds and geometry; source GLB unchanged','Center-up camera moved above hero to show actual ceiling','Reduced preview fixture/fill intensity to preserve material separation','Production camera moved inside sealed shell while retaining high three-quarter view']
report['postmortem']['remainingRisks']=['Form approval pending','Final room textures and ambient-occlusion baking remain pending','Actual Godot metal finish/color parity, current animation pose bounds, runtime collision/navigation and performance remain unverified','Bundled validator is Meshy-only; procedural user instruction applies instead','Blender preview lamps are not a substitute for Godot light calibration']
write('final-report.json',report)
print('FORM_SPATIAL_AUDIT '+json.dumps({'propPairs':tested,'collisions':collisions,'attached':all(x['attached'] for x in attachment),'heroSamples':front,'heroOccluded':occluded,'enclosure':all(x['hitsShell'] for x in enclosure)}))
