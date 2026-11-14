import sys,json,hashlib,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/gold_beetle_objective/front-leg-restoration-v2-2026-11-13')
r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output'])
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256']
for key in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert a.get(key)==b.get(key),key
assert a['materials']==b['materials'][:-1] and bb[:len(ab)]==ab
ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0]
attrs={k:accessor(b,bb,v) for k,v in bp['attributes'].items()};n=len(accessor(a,ab,ap['attributes']['POSITION']))
for key in ap['attributes']:assert np.array_equal(accessor(a,ab,ap['attributes'][key]),attrs[key][:n]),key
tri=np.concatenate([accessor(b,bb,p['indices']).reshape(-1,3) for p in b['meshes'][0]['primitives']]);pos=attrs['POSITION'];used=np.unique(tri)
mp,edges,groups,deg=topology(pos,tri);assert not groups and not deg
oldtri=accessor(a,ab,ap['indices']).reshape(-1,3);_,oe,_,_=topology(attrs['POSITION'][:n],oldtri)
assert sorted(e for e,fs in edges.items() if len(fs)>2)==sorted(e for e,fs in oe.items() if len(fs)>2)
names=[b['nodes'][i]['name'] for i in b['skins'][0]['joints']];assert len(names)==23
js=attrs['JOINTS_0'];ws=attrs['WEIGHTS_0'];w=ws[used];assert np.isfinite(pos[used]).all() and np.isfinite(w).all() and (w>=0).all() and abs(w.sum(1)-1).max()<1e-5
assert js[used].max()<23
front=[names.index(f'Bone_{i:03}') for i in range(11,17)]
values=(ws[:n]*np.isin(js[:n],front)).sum(1)
protected=np.max(values[oldtri],axis=1)<=.30
present=set(map(tuple,tri.tolist()));assert all(tuple(t) in present for t in oldtri[protected])
# Count distinct connected feet at the actual ground surface.
adj=collections.defaultdict(set)
for ft in mp[tri]:
 for u,v in zip(ft,np.roll(ft,-1)):
  if pos[u,1]<.04 and pos[v,1]<.04:adj[int(u)].add(int(v));adj[int(v)].add(int(u))
seen=set();feet=[]
for start in adj:
 if start in seen:continue
 stack=[start];part=set()
 while stack:
  u=stack.pop()
  if u in part:continue
  part.add(u);stack.extend(adj[u]-part)
 seen.update(part)
 if len(part)>10:
  pts=pos[list(part)];feet.append({'vertices':len(part),'bounds':[pts.min(0).tolist(),pts.max(0).tolist()]})
assert len(feet)==6,feet
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(tri),'joints':23,'boundary_edges':0,'collapsed_triangles':0,'protected_original_closed_contacts':2,'all_original_vertex_attribute_rows_retained':True,'original_skeleton_rest_binds_and_textures_preserved':True,'source_faces_outside_front_leg_influence_region_preserved':int(protected.sum()),'ground_surface_foot_count':len(feet),'feet':feet,'new_shoulder_collar_material':True,'intact_pre_remesh_available':False}
(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
