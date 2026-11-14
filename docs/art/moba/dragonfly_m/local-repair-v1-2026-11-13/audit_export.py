import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output']);ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0];assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'] and bb[:len(ab)]==ab
for k in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert a.get(k)==b.get(k)
assert a['materials']==b['materials'][:-1]
attrs={k:accessor(b,bb,v) for k,v in bp['attributes'].items()};n=len(accessor(a,ab,ap['attributes']['POSITION']))
for k in ['POSITION','NORMAL','TEXCOORD_0']:assert np.array_equal(accessor(a,ab,ap['attributes'][k]),attrs[k][:n])
t=np.concatenate([accessor(b,bb,p['indices']).reshape(-1,3) for p in b['meshes'][0]['primitives']]);pos=attrs['POSITION'];used=np.unique(t);j=attrs['JOINTS_0'];w=attrs['WEIGHTS_0'];assert np.isfinite(pos[used]).all() and np.isfinite(w[used]).all() and abs(w[used].sum(1)-1).max()<1e-5
names=[b['nodes'][i]['name'] for i in b['skins'][0]['joints']];removed=[names.index(f'Bone_{i:03}') for i in range(22,28)];assert not np.any((w[used]>1e-8)&np.isin(j[used],removed));_,e,g,deg=topology(pos,t);assert not g and not deg and all(len(fs)==2 for fs in e.values())
oldtri=accessor(a,ab,ap['indices']).reshape(-1,3);originalpos=accessor(a,ab,ap['attributes']['POSITION']);f=np.load(ROOT/'cut-fields.npz');protected=(f['protected'][oldtri].min(1)>=.25)&(originalpos[oldtri,1].min(1)>.80);present=set(map(tuple,t.tolist()));assert all(tuple(ft) in present for ft in oldtri[protected])
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(t),'joint_count':46,'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'retained_neighbor_joint_faces_verified':int(protected.sum()),'original_position_normal_uv_rows_retained':True,'original_skeleton_rest_binds_material_texture_data_retained':True,'removed_chains_have_zero_used_surface_influence':True,'selected_pair':2,'remaining_pairs':[1,3,4]};(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
