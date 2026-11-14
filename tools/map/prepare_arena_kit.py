"""Blender --background --python tools/map/prepare_arena_kit.py -- wall_piece tower_head:flip ...

Turns the Meshy exports (art/environment/arena_3v3/source/<asset>/raw_refine.glb, kept as they came) into runtime
GLBs in art/environment/arena_3v3/runtime/: metre scale, bottom-centre pivot, glTF +Y up, the asset's envelope from
meshy_arena_batch.py, decimated to a triangle budget, textures at most 1K. After Codex's tools/map5v5/prepare_modules.py.

The long horizontal side is turned onto the depth axis (Godot z); ":flip" turns the asset half round, for a turret
whose barrels came out facing +z (the arena's turret aims down -z).
"""
import bpy, hashlib, json, math, pathlib, sys, tempfile
from mathutils import Matrix, Vector

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT / 'art/environment/arena_3v3'
TEMP = ROOT.parent / '_scratch/map3v3/blender-temp'
TEMP.mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(TEMP)
bpy.context.preferences.filepaths.save_version = 0
SIZES = {'wall_piece': (2.0, 3.0, 1.2), 'tower_base': (2.8, 2.95, 2.8), 'tower_head': (2.4, 0.9, 4.0),
         'core': (5.0, 4.35, 5.0), 'rock_slag': (7.0, 3.5, 7.0), 'rock_scrap': (6.0, 3.0, 6.0),
         'refinery': (10.0, 12.0, 10.0), 'wall_run': (2.0, 3.0, 1.2), 'rock_cold': (6.0, 3.0, 6.0),
         'rock_boulder': (6.0, 3.0, 6.0)} # Godot x, y (up), z
BUDGET = {'wall_piece': 900, 'tower_base': 3000, 'tower_head': 2500, 'core': 5000, 'rock_slag': 2500,
          'rock_scrap': 2500, 'refinery': 3000, 'wall_run': 900, 'rock_cold': 2500,
          'rock_boulder': 2500}
LONG_ON_DEPTH = {'tower_head'} # a turret is longer front to back

for arg in sys.argv[sys.argv.index('--') + 1:]:
    kind, _, opt = arg.partition(':')
    source = BASE / 'source' / kind / 'raw_refine.glb'
    if not source.exists(): # a library model (Patch search: Poly Haven, Kenney; CC0, credit in CREDITS.md), kept as it came
        source = BASE / 'source' / kind / 'raw.glb'
    if not source.exists():
        print('SKIP', kind, 'no textured export')
        continue
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    before = sum(len(p.vertices) - 2 for o in meshes for p in o.data.polygons)
    for o in meshes: # world transforms into the mesh data, so the export has none
        world = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        o.data.transform(world)
    turn = 0.0
    pts = [v.co for o in meshes for v in o.data.vertices]
    span = Vector(tuple(max(p[i] for p in pts) - min(p[i] for p in pts) for i in range(3)))
    if kind in LONG_ON_DEPTH and span.x > span.y:
        turn += math.pi / 2 # Blender y is glTF -z: the long side onto depth
    if opt == 'flip':
        turn += math.pi
    if turn:
        for o in meshes:
            o.data.transform(Matrix.Rotation(turn, 4, 'Z'))
    pts = [v.co for o in meshes for v in o.data.vertices]
    lo = Vector(tuple(min(p[i] for p in pts) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    w, h, d = SIZES[kind]
    target = Vector((w, d, h)) # Blender is z up
    scale = Vector(tuple(target[i] / (hi - lo)[i] for i in range(3)))
    shift = Vector((-(lo.x + hi.x) * 0.5, -(lo.y + hi.y) * 0.5, -lo.z))
    bake = Matrix.Diagonal((*scale, 1.0)) @ Matrix.Translation(shift)
    for o in meshes:
        o.data.transform(bake)
        o.data.update()
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = 'Arena_' + kind
    tris = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    if tris > BUDGET[kind]:
        dec = obj.modifiers.new('budget', 'DECIMATE')
        dec.ratio = BUDGET[kind] / tris
        bpy.ops.object.modifier_apply(modifier=dec.name)
    after = sum(len(p.vertices) - 2 for p in obj.data.polygons)
    images = []
    for im in bpy.data.images:
        if im.type != 'IMAGE':
            continue
        _ = im.size[:] # glTF images decode lazily
        if not im.has_data:
            continue
        if max(im.size) > 1024:
            r = 1024 / max(im.size)
            im.scale(round(im.size[0] * r), round(im.size[1] * r))
        if not im.packed_file:
            im.pack()
        images.append({'name': im.name, 'size': list(im.size)})
    runtime = BASE / 'runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    dest = runtime / (kind + '.glb')
    bpy.ops.export_scene.gltf(filepath=str(dest), export_format='GLB', use_selection=True, export_yup=True,
                              export_animations=False)
    meta = {'asset': kind, 'raw_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'runtime_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(), 'raw_triangles': before,
            'runtime_triangles': after, 'materials': len(obj.data.materials), 'images': images,
            'size_godot_xyz_m': SIZES[kind], 'turned_deg': round(math.degrees(turn)), 'pivot': 'bottom centre',
            'up': '+Y', 'collision': 'none: the blockout keeps its own bodies and nav mesh',
            'provider_metadata': '../source/' + kind + ('/refine-status.json' if source.name == 'raw_refine.glb' else '/CREDITS.md')}
    (runtime / (kind + '.json')).write_text(json.dumps(meta, indent=2), encoding='utf8')
    print('KIT_READY', kind, before, '->', after, 'triangles', len(obj.data.materials), 'materials', images)
