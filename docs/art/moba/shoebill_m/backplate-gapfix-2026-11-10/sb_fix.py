import bpy, bmesh, math, json, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=r"D:/dev/_scratch/moba-look/shoebill"
mode=sys.argv[sys.argv.index("--")+1]
body=bpy.data.objects["Shoebill_Recipient_BODY_UNBOUND"]; plate=bpy.data.objects["Moon_Backplate_DONOR_UNBOUND"]
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); return BVHTree.FromBMesh(bm)
rep={}
if mode=="fix":
    SHIFT=0.0215   # plate front 0.2025 -> 0.181, just proud of the 0.178 cut
    plate.location.y-=SHIFT
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    tb=bvh(body); tp=bvh(plate)
    cx,cz,R=0.0,0.756,0.176; N=60
    front=[];back=[]
    for i in range(N):
        a=2*math.pi*i/N; x=cx+R*math.cos(a); z=cz+R*math.sin(a)
        hp=tp.ray_cast(Vector((x,-1.0,z)),Vector((0,1,0))); fy=(hp[0].y if hp[0] else 0.181)+0.004  # tucked inside the plate
        hb=tb.ray_cast(Vector((x,1.0,z)),Vector((0,-1,0))); by=(hb[0].y if hb[0] else 0.178)-0.006   # sunk into the body
        front.append((x,fy,z)); back.append((x*0.97,by,cz+(z-cz)*0.97))  # slight taper toward the body
    me=bpy.data.meshes.new("Backplate_Mount_Collar")
    verts=front+back; faces=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
    me.from_pydata(verts,[],faces); me.update()
    col=bpy.data.objects.new("Backplate_Mount_Collar",me); body.users_collection[0].objects.link(col)
    for p in me.polygons: p.use_smooth=False
    m=bpy.data.materials.new("Backplate_Mount_Collar_Mat"); m.use_nodes=True
    bsdf=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value=(0.055,0.06,0.10,1); bsdf.inputs["Roughness"].default_value=0.65; bsdf.inputs["Metallic"].default_value=0.4
    me.materials.append(m)
    col.parent=bpy.data.objects["Backplate_BIND_TARGET_PENDING_RIG"]; col.matrix_parent_inverse=col.parent.matrix_world.inverted()
    depth=[round(f[1]-b[1],3) for f,b in zip(front,back)]
    rep={"plate_shift_y":-SHIFT,"collar_ring_radius":R,"collar_segments":N,"collar_depth_min":min(depth),"collar_depth_max":max(depth)}
    # re-probe gap: any straight-through line of sight beside the plate? sample just outside the collar, inside the rim
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    tc=bvh(col); tp=bvh(plate); tb=bvh(body); open_=0; tot=0
    for i in range(72):
        a=2*math.pi*i/72
        for r in (0.10,0.14,0.16,0.172,0.178):
            x=r*math.cos(a); z=0.756+r*math.sin(a)
            # side view rays along +-x through the gap band: between body surface and plate front
            hb=tb.ray_cast(Vector((x,1.0,z)),Vector((0,-1,0)))
            hp=tp.ray_cast(Vector((x,-1.0,z)),Vector((0,1,0)))
            if not hp[0]: continue
            tot+=1
            gap=hp[0].y-(hb[0].y if hb[0] else 0.178)
            if gap>0.004:
                mid=Vector((x,(hp[0].y+(hb[0].y if hb[0] else 0.178))/2,z))
                # is this air pocket enclosed by the collar? cast outward radially
                d=Vector((math.cos(a),0,math.sin(a)))
                if not tc.ray_cast(mid,d,0.3)[0]: open_+=1
    rep["air_samples"]=tot; rep["air_samples_visible_through_side"]=open_
# render 3 views, ortho, close on the back
sc=bpy.context.scene
for o in [o for o in bpy.data.objects if o.type in ("CAMERA","LIGHT")]: bpy.data.objects.remove(o)
try: sc.render.engine="BLENDER_EEVEE_NEXT"
except TypeError:
    try: sc.render.engine="BLENDER_EEVEE"
    except TypeError: pass
sc.render.resolution_x=800; sc.render.resolution_y=800
w=sc.world or bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True
bg=next(n for n in w.node_tree.nodes if n.type=="BACKGROUND"); bg.inputs[0].default_value=(0.05,0.05,0.06,1); bg.inputs[1].default_value=0.8
L=bpy.data.objects.new("key",bpy.data.lights.new("key","SUN")); L.data.energy=3.5; L.rotation_euler=(math.radians(50),0,math.radians(150)); sc.collection.objects.link(L)
cam=bpy.data.objects.new("cam",bpy.data.cameras.new("cam")); cam.data.type="ORTHO"; cam.data.ortho_scale=0.62; sc.collection.objects.link(cam); sc.camera=cam
tgt=Vector((0,0.17,0.76))
for name,pos in (("side",(2.0,0.17,0.80)),("threeq",(1.4,1.5,1.05)),("top",(0.6,1.2,2.2))):
    cam.location=pos; cam.rotation_euler=(tgt-Vector(pos)).to_track_quat("-Z","Y").to_euler()
    sc.render.filepath=f"{W}/{mode}_{name}.png"; bpy.ops.render.render(write_still=True)
if mode=="fix":
    bpy.ops.wm.save_as_mainfile(filepath=f"{W}/shoebill-moon-backplate-GAPFIX-UNBOUND.blend",copy=True)
    for o in [o for o in bpy.data.objects if o.type in ("CAMERA","LIGHT")]: bpy.data.objects.remove(o)
    bpy.ops.export_scene.gltf(filepath=f"{W}/shoebill-moon-backplate-GAPFIX-UNBOUND.glb",export_format="GLB")
json.dump(rep,open(f"{W}/fix_{mode}.json","w"),indent=1)
