"""Read final exports independently and verify the preserved source surfaces/rig."""
import sys, json, hashlib, collections
from pathlib import Path
import numpy as np
sys.path.insert(0, 'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb, accessor, topology
ROOT = Path(__file__).parent
BASE = Path('D:/dev/new-mech-rpg')
for mid in ['gold_beetle', 'wyvern']:
    cfg = json.loads((ROOT/mid/'input-audit.json').read_text())
    out = BASE/f'docs/art/moba/{mid}_objective/repair-v1-2026-11-11'
    repair = json.loads((out/'repair-verification.json').read_text())
    source = Path(cfg['input']); final = Path(repair['output'])
    assert hashlib.sha256(source.read_bytes()).hexdigest() == cfg['sha256']
    assert hashlib.sha256(final.read_bytes()).hexdigest() == repair['output_sha256']
    a, ab = read_glb(source); b, bb = read_glb(final)
    ap = a['meshes'][0]['primitives'][0]; bp = b['meshes'][0]['primitives'][0]
    for key in ['nodes','skins','materials','images','textures','samplers','scenes','scene','animations']:
        assert a.get(key) == b.get(key), key
    assert bb[:len(ab)] == ab
    attrs = {k:accessor(b, bb, v) for k,v in bp['attributes'].items()}
    for key in ap['attributes']:
        if mid == 'wyvern' and key in ['JOINTS_0','WEIGHTS_0']: continue
        assert np.array_equal(accessor(a,ab,ap['attributes'][key]),attrs[key]),key
    tri = accessor(b,bb,bp['indices']).reshape(-1,3)
    atri = accessor(a,ab,ap['indices']).reshape(-1,3)
    mp,edges,groups,deg = topology(attrs['POSITION'],tri)
    assert not groups and not deg
    over = [list(e) for e,fs in edges.items() if len(fs)>2]
    assert sorted(over) == sorted(repair['protected_closed_contact_edges'])
    assert all(len(edges[tuple(e)])==4 for e in over)
    remaining = collections.Counter(map(tuple,tri.tolist()))
    comps = json.loads((ROOT/mid/'face-components.json').read_text())
    main = max(comps,key=lambda c:c['count'])
    removed = set(repair['removed_fold_triangle_ids'])
    healthy = [i for i in main['faces'] if i not in removed]
    assert all(remaining[tuple(atri[i])] for i in healthy)
    assert len(healthy) == repair['healthy_source_body_faces_retained']
    used = np.unique(tri)
    weights = attrs['WEIGHTS_0'][used]
    assert np.isfinite(weights).all() and (weights>=0).all()
    assert np.max(np.abs(weights.sum(1)-1)) < 1e-5
    names = [b['nodes'][i]['name'] for i in b['skins'][0]['joints']]
    assert len(names) == cfg['joint_count']
    if mid == 'wyvern':
        forbidden = [names.index(f'Bone_{i:03}') for i in range(28,38)]
        assert not np.any((weights>1e-8)&np.isin(attrs['JOINTS_0'][used],forbidden))
        assert all(not remaining[tuple(atri[i])] for pair in repair['removed_extra_foreleg_face_ids'] for i in pair)
        assert len(healthy)==22970
    poses = json.loads((out/'visual-deformation-check.json').read_text())
    assert poses['tested_sha256'] == repair['output_sha256']
    assert len(poses['poses']) == (9 if mid=='gold_beetle' else 10)
    assert all(p['coincident_surface_gap_m']<1e-6 for p in poses['poses'])
    result = {'id':mid, 'passed':True,'tested_sha256':repair['output_sha256'],
        'triangles':len(tri),'joint_count':len(names),'boundary_edges':0,'collapsed_triangles':0,
        'protected_original_four_face_contacts':len(over),'healthy_source_body_faces_retained':len(healthy),
        'source_rig_rest_binds_materials_preserved':True,'source_binary_prefix_preserved':True,
        'unchanged_vertex_attributes':'all' if mid=='gold_beetle' else 'positions, normals, UVs; documented local skin reassignment',
        'pose_count':len(poses['poses']),'maximum_pose_seam_gap_m':max(p['coincident_surface_gap_m'] for p in poses['poses']),
        'anatomy':repair['anatomy'],'intact_pre_remesh_available':False}
    (out/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
