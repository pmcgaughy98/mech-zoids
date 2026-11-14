"""Run with Blender --background --python this_file -- wall [pillar camp landmark].
Retains immutable provider exports; produces grounded, meter-scale runtime copies.
"""
import bpy, hashlib, json, pathlib, sys, tempfile
from mathutils import Vector, Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=ROOT/'art/environment/foundry_5v5'
TEMP=ROOT.parent/'_scratch/map5v5/blender-temp'
TEMP.mkdir(parents=True,exist_ok=True);tempfile.tempdir=str(TEMP)
bpy.context.preferences.filepaths.save_version=0
SIZES={'wall':(6,2.6,1.6),'pillar':(2.4,4,2.4),'camp':(3.6,3.2,3.6),'landmark':(5.2,5,5.2)}
BUDGET={'wall':5000,'pillar':4000,'camp':6000,'landmark':8000}
for kind in sys.argv[sys.argv.index('--')+1:]:
    source=BASE/'source'/kind/'raw_refine.glb'
    if not source.exists():raise RuntimeError('No succeeded textured source: '+kind)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    before=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    # Blender Z-up; exported glTF Y-up. Center ground pivot and exact envelope per module.
    target=Vector((SIZES[kind][0],SIZES[kind][2],SIZES[kind][1]))
    scale=Vector(tuple(target[i]/(hi-lo)[i] for i in range(3)))
    shift=Vector((-(lo.x+hi.x)*.5,-(lo.y+hi.y)*.5,-lo.z))
    bake=Matrix.Diagonal((*scale,1))@Matrix.Translation(shift)
    for o in meshes:
        world=o.matrix_world.copy()
        o.parent=None;o.matrix_world=Matrix.Identity(4)
        o.data.transform(bake@world);o.data.update()
        if before>BUDGET[kind]:
            bpy.context.view_layer.objects.active=o
            dec=o.modifiers.new('Runtime silhouette budget','DECIMATE');dec.ratio=BUDGET[kind]/before
            bpy.ops.object.modifier_apply(modifier=dec.name)
    images=[]
    for im in bpy.data.images:
        if im.type!='IMAGE':continue
        _=im.size[:] # Force lazy glTF image decode before checking data/resizing.
        if not im.has_data:continue
        if max(im.size)>1024:
            ratio=1024/max(im.size);im.scale(round(im.size[0]*ratio),round(im.size[1]*ratio))
        if not im.packed_file:im.pack()
        images.append({'name':im.name,'size':list(im.size)})
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    if len(meshes)>1:bpy.ops.object.join()
    obj=bpy.context.view_layer.objects.active;obj.name='Foundry_'+kind
    after=sum(len(p.vertices)-2 for p in obj.data.polygons)
    if after>BUDGET[kind]*1.04:raise RuntimeError('Triangle budget failed')
    if len(obj.data.materials)>4:raise RuntimeError('Material budget failed')
    runtime=BASE/'runtime';runtime.mkdir(parents=True,exist_ok=True)
    workspace=BASE/'workspaces';workspace.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(workspace/(kind+'.blend')))
    dest=runtime/(kind+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',use_selection=True,export_yup=True,export_animations=False)
    meta={'asset':kind,'raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'runtime_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
          'raw_triangles':before,'runtime_triangles':after,'materials':len(obj.data.materials),'images':images,'dimensions_godot_xyz_m':SIZES[kind],
          'pivot':'bottom center','up':'+Y','front':'+Z; symmetric environment module','collision':'separate authored foundation boxes; generated mesh excluded from nav',
          'sockets':{'wall':'X ends at -3/+3m; visual skin only','pillar':'2.4m square footprint','camp':'3.6m square footprint','landmark':'5.2m square footprint'}[kind],
          'provider_metadata':'../source/'+kind+'/refine-status.json','license':'Provider API output, paid account; no third-party assets intentionally supplied. No per-file license string supplied by API.'}
    (runtime/(kind+'.json')).write_text(json.dumps(meta,indent=2),encoding='utf8')
    print('MODULE_READY',kind,after,'triangles',len(obj.data.materials),'materials')
