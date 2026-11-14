import json,sys,hashlib,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output'])
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']
for key in ['nodes','skins','images','textures','samplers','scenes','scene','animations']:assert a.get(key)==b.get(key),key
assert b['materials'][:-1]==a['materials'] and bb[:len(ab)]==ab
ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0];attrs={k:accessor(b,bb,v) for k,v in bp['attributes'].items()}
for key,ai in ap['attributes'].items():
 old=accessor(a,ab,ai);assert np.array_equal(old,attrs[key][:len(old)]),key
tri=np.concatenate([accessor(b,bb,p['indices']).reshape(-1,3) for p in b['meshes'][0]['primitives']]);pos=attrs['POSITION'];mp,edges,groups,deg=topology(pos,tri);assert not groups and not deg and all(len(fs)==2 for fs in edges.values())
areas=np.linalg.norm(np.cross(pos[tri[:,1]]-pos[tri[:,0]],pos[tri[:,2]]-pos[tri[:,0]]),axis=1)/2;assert areas.min()>1e-12
used=np.unique(tri);j=attrs['JOINTS_0'][used];w=attrs['WEIGHTS_0'][used];assert j.max()<38 and np.isfinite(pos[used]).all() and np.isfinite(w).all() and (w>=0).all() and abs(w.sum(1)-1).max()<1e-5
oldtri=accessor(a,ab,ap['indices']).reshape(-1,3);present=set(map(tuple,tri.tolist()));comps=json.loads((ROOT/'face-components.json').read_text());body=next(c['faces'] for c in comps if c['count']==21286);removed=set(r['removed_small_flap_and_scrap_face_ids']);protected=[i for i in body if i not in removed]
assert len(protected)==21285 and all(tuple(oldtri[i]) in present for i in protected)
# Fan splits may clone an original front vertex without changing its attributes.
front_positions=pos[accessor(b,bb,bp['indices']).reshape(-1,3)]
assert len(r['preserved_plate_source_face_ids'])==1820
for i in r['preserved_plate_source_face_ids']:
 coordinates=accessor(a,ab,ap['attributes']['POSITION'])[oldtri[i]]
 assert tuple(oldtri[i]) in present or any(np.array_equal(v,coordinates) for v in front_positions)
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(tri),'joints':38,'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'minimum_triangle_area_m2':float(areas.min()),'source_body_wing_leg_faces_retained':len(protected),'source_visible_plate_faces_retained':1820,'source_attribute_rows_preserved':True,'original_binary_prefix_preserved':True,'skeleton_hierarchy_rest_binds_material_texture_data_preserved':True,'new_weights':'Copied from corresponding retained source vertices; no original skin rows changed.','scope':'Donor-plate artifact removal/rear-shell reconstruction, local flap/gap repairs and hidden mounting-sleeve closures.'}
(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
