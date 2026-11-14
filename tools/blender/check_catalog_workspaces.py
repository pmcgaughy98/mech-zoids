"""Reopen saved native workspaces and check packed references and source geometry."""
import bpy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAT = ROOT/'art/model_catalog'
entries = json.loads((CAT/'catalog.json').read_text())['entries']
results = []
for entry in entries:
    source_report = json.loads((CAT/'display'/f'{entry["id"]}.json').read_text())
    path = CAT/'workspaces'/f'{entry["id"]}.blend'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    assert scene['catalog_id'] == entry['id']
    assert scene['source_sha256'] == entry['source_model']['sha256']
    working = bpy.data.collections['01 WORKING MODEL - edit this']
    meshes = [o for o in working.objects if o.type == 'MESH']
    triangles = sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    assert triangles == source_report['source_triangles'], (entry['id'], triangles)
    assert not any(o.modifiers for o in meshes), 'Source workspace must precede display decimation'
    refs = [o for o in bpy.data.collections['02 FOUR SOURCE SHEETS - locked reference boards'].objects if o.type == 'MESH']
    assert len(refs) == 4 and all(o.hide_select for o in refs)
    found = set()
    for board in refs:
        image = next(n.image for n in board.active_material.node_tree.nodes if n.type == 'TEX_IMAGE')
        assert image.packed_file is not None, (entry['id'], image.name)
        digest = hashlib.sha256(image.packed_file.data).hexdigest()
        found.add(digest)
    assert found == {v['sha256'] for v in entry['views'].values()}, entry['id']
    assert scene.camera and 'START HERE - model and reference provenance.txt' in bpy.data.texts
    # Ensure solid textured editing view uses base color, not a normal/ORM map.
    for obj in meshes:
        for mat in obj.data.materials:
            if mat and mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED' and node.inputs['Base Color'].is_linked:
                        texture = node.inputs['Base Color'].links[0].from_node
                        if texture.type == 'TEX_IMAGE':
                            mat.node_tree.nodes.active = texture
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.overlay.show_extras = False
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    results.append({'id':entry['id'], 'full_source_triangles':triangles, 'packed_reference_hashes':'PASS', 'editable_mesh':'PASS'})
    print('WORKSPACE VERIFIED', entry['id'], triangles, flush=True)
folder = ROOT/'reports/model_catalog'
folder.mkdir(parents=True, exist_ok=True)
(folder/'workspace-verification.json').write_text(json.dumps(results, indent=2))
print('ALL NATIVE WORKSPACES VERIFIED', len(results), flush=True)
