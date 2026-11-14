"""Blender-only gallery proxies. Originals and gameplay assets are never modified."""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT / 'art/model_catalog'
sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog_artist_workspace import make_workspace
manifest = json.loads((CAT/'catalog.json').read_text(encoding='utf-8'))
out = CAT/'display'
out.mkdir(exist_ok=True)
records = []
for entry in manifest['entries']:
    target = ROOT / entry['display_model'].removeprefix('res://')
    report_path = target.with_suffix('.json')
    if target.exists() and report_path.exists():
        records.append(json.loads(report_path.read_text()))
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    source = ROOT / entry['source_model']['path'].removeprefix('res://')
    bpy.ops.import_scene.gltf(filepath=str(source))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert meshes, entry['id']
    original_triangles = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    assert not any(o.type == 'ARMATURE' for o in bpy.context.scene.objects), 'Static gallery sources expected'
    make_workspace(ROOT, CAT, entry, meshes)
    for obj in meshes:
        assert obj.data.uv_layers, f'No UVs: {entry["id"]}'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        if original_triangles > 40000:
            mod = obj.modifiers.new('Gallery display reduction only', 'DECIMATE')
            mod.ratio = 40000 / original_triangles
            bpy.ops.object.modifier_apply(modifier=mod.name)
        assert len(obj.data.polygons) > 0
    texture_sizes = []
    for image in bpy.data.images:
        if image.size[0] > 1024 or image.size[1] > 1024:
            scale = 1024/max(image.size)
            image.scale(max(1, round(image.size[0]*scale)), max(1, round(image.size[1]*scale)))
            image.pack()
        if image.size[0] > 0:
            texture_sizes.append(list(image.size))
    # Uniform gallery scale: fit each silhouette in a 2.8 m horizontal cell,
    # up to 2.5 m tall. These are comparison sizes, not gameplay scale decisions.
    coords = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    low = Vector(tuple(min(c[a] for c in coords) for a in range(3)))
    high = Vector(tuple(max(c[a] for c in coords) for a in range(3)))
    dimensions = high-low
    assert min(dimensions) > 0
    scale = min(2.8/max(dimensions.x, dimensions.y), 2.5/dimensions.z)
    triangles = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    assert 0 < triangles <= 41000
    assert all(max(s) <= 1024 for s in texture_sizes)
    # Pre-export optimization validation: static mesh, UVs, bounded triangle
    # count, 1K maps. Visual/runtime gate is performed in Godot separately.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', use_selection=True,
                             export_animations=False, export_yup=True)
    record = {'id': entry['id'], 'source_sha256': entry['source_model']['sha256'],
              'source_triangles': original_triangles, 'display_triangles': triangles,
              'texture_sizes': texture_sizes, 'gallery_scale': scale,
              'blender_bounds_min': list(low), 'blender_bounds_max': list(high),
              'validation': 'PASS: static mesh, UVs, triangle/texture limits; engine visual review separate',
              'purpose': 'Gallery proxy only; not an approved match asset or retopology'}
    report_path.write_text(json.dumps(record, indent=2))
    records.append(record)
    print('CATALOG DISPLAY', entry['id'], triangles, flush=True)
(CAT/'display-report.json').write_text(json.dumps(records, indent=2))
print('CATALOG DISPLAY COMPLETE', len(records), flush=True)
