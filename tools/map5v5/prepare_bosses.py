"""Separate existing objective-boss viewing copies. No generation, rig replacement or encounter logic."""
import bpy, pathlib, json, hashlib, tempfile
from mathutils import Vector, Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=ROOT/'art/environment/foundry_5v5'
TEMP=ROOT.parent/'_scratch/map5v5/blender-temp';TEMP.mkdir(parents=True,exist_ok=True);tempfile.tempdir=str(TEMP)
bpy.context.preferences.filepaths.save_version=0
SOURCES={
 'gold_beetle':('Meshy_AI_coinclaw_mech_remeshed_25k_20261111_character.glb',3.8,9.0),
 'wyvern':('Meshy_AI_Cyber_Wyvern_Sentinel_1110211655_texture.glb',6.5,12.0),
}
for kind,(filename,height,span) in SOURCES.items():
    source=pathlib.Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged')/filename
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))
    nodes=list(bpy.context.scene.objects);meshes=[o for o in nodes if o.type=='MESH']
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    dimensions=hi-lo;factor=min(height/dimensions.z,span/max(dimensions.x,dimensions.y))
    root=bpy.data.objects.new('Objective_'+kind,None);bpy.context.collection.objects.link(root)
    # Keep the full original bone/weight hierarchy; a parent transforms the viewing copy uniformly.
    for o in nodes:
        if o.parent is None:
            world=o.matrix_world.copy();o.parent=root;o.matrix_world=world
    root.scale=Vector((factor,)*3)
    root.location=Vector((-(lo.x+hi.x)*.5,-(lo.y+hi.y)*.5,-lo.z))*factor
    images=[]
    for im in bpy.data.images:
        if im.type!='IMAGE':continue
        _=im.size[:]
        if not im.has_data:continue
        if max(im.size)>1024:
            ratio=1024/max(im.size);im.scale(round(im.size[0]*ratio),round(im.size[1]*ratio))
        if not im.packed_file:im.pack()
        images.append({'name':im.name,'size':list(im.size)})
    bones=sum(len(o.data.bones) for o in nodes if o.type=='ARMATURE')
    tris=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons)
    if tris>30000:raise RuntimeError('Boss viewing-copy budget exceeded')
    out=BASE/'runtime';out.mkdir(parents=True,exist_ok=True)
    workspace=BASE/'workspaces';workspace.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(workspace/(kind+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    dest=out/(kind+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest),export_format='GLB',export_yup=True,export_animations=False,use_selection=True)
    dimensions_godot=[dimensions.x*factor,dimensions.z*factor,dimensions.y*factor]
    meta={'asset':kind,'existing_source':str(source),'raw_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'runtime_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'triangles':tris,'preserved_bones':bones,'images':images,
        'draft_dimensions_godot_m':dimensions_godot,'uniform_scale':factor,'pivot':'ground centered, +Y up',
        'stage':'existing rigged model, no authored clips; static objective placement preview, no combat or rewards',
        'generation_spend_this_lane':0,'source_modified':False}
    (out/(kind+'.json')).write_text(json.dumps(meta,indent=2),encoding='utf8')
    print('BOSS_VIEW_READY',kind,tris,'triangles',bones,'bones',dimensions_godot)
