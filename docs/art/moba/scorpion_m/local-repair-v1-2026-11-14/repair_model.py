import copy, hashlib, json, struct, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, 'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb, accessor, topology
ROOT = Path(__file__).parent
OUT = Path('D:/dev/new-mech-rpg/docs/art/moba/scorpion_m/local-repair-v1-2026-11-14')
cfg = json.loads((ROOT/'input-audit.json').read_text())
d, blob = read_glb(cfg['source'])
original = copy.deepcopy(d)
pr = d['meshes'][0]['primitives'][0]
p = accessor(d, blob, pr['attributes']['POSITION'])
t = accessor(d, blob, pr['indices']).reshape(-1, 3)
components = json.loads((ROOT/'face-components.json').read_text())
removed = sorted(f for c in components if c['count'] <= 2 and c['boundary_edges'] > 0 and c['over_shared_contacts'] == 1 for f in c['faces'])
assert len(removed) == 23
repaired = np.delete(t, removed, axis=0)
mapping, edges, groups, deg = topology(p, repaired)
assert not groups and not deg and all(len(fs) == 2 for fs in edges.values())
result_blob = blob + b'\0' * (-len(blob) % 4)
raw = repaired.astype('<u2').tobytes()
view = len(d['bufferViews'])
d['bufferViews'].append({'buffer': 0, 'byteOffset': len(result_blob), 'byteLength': len(raw), 'target': 34963})
result_blob += raw
index = len(d['accessors'])
d['accessors'].append({'bufferView': view, 'componentType': 5123, 'count': repaired.size, 'type': 'SCALAR'})
pr['indices'] = index
d['buffers'][0]['byteLength'] = len(result_blob)
js = json.dumps(d, separators=(',', ':')).encode()
js += b' ' * (-len(js) % 4)
result_blob += b'\0' * (-len(result_blob) % 4)
dest = OUT/'scorpion-rigged-local-repair-v1.glb'
dest.write_bytes(struct.pack('<III', 0x46546c67, 2, 28 + len(js) + len(result_blob)) + struct.pack('<II', len(js), 0x4e4f534a) + js + struct.pack('<II', len(result_blob), 0x004e4942) + result_blob)
for key in ['nodes','skins','materials','images','textures','samplers','scene','scenes','animations']:
    assert d.get(key) == original.get(key), key
report = {
    'source': cfg['source'], 'source_sha256': cfg['sha256'],
    'output': str(dest), 'output_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
    'before_triangles': len(t), 'final_triangles': len(repaired), 'joint_count': 52,
    'removed_malformed_triangles': len(removed), 'removed_face_ids': removed,
    'holes_closed': [], 'boundary_edges': 0, 'over_shared_edges': 0, 'collapsed_triangles': 0,
    'healthy_source_faces_retained': len(repaired),
    'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved': True,
    'new_geometric_vertices': 0,
    'scope': 'Remove 21 single-triangle flaps and one two-triangle folded fragment. Retain eight walking legs, both pincers, two side vessels and the complete raised tail. Original vertex attributes, weights, 52-joint rig, rest/binds and textures remain exact. No remesh or rerig.',
    'limitations': 'Existing baked texture roughness and grouped rig controls remain. No authored animation clips.'
}
(OUT/'repair-verification.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
