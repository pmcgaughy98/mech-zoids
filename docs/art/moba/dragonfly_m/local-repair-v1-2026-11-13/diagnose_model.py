import sys,json,hashlib,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13');OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_dragonfly_remeshed_25k_20261111_character.glb');d,b=read_glb(SOURCE);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);mp,edges,groups,deg=topology(p,t);adj=[set() for _ in t]
for fs in edges.values():
 if len(fs)==2:a,c=fs;adj[a].add(c);adj[c].add(a)
seen=set();comps=[]
for start in range(len(t)):
 if start in seen:continue
 stack=[start];part=set()
 while stack:
  f=stack.pop()
  if f in part:continue
  part.add(f);stack.extend(adj[f]-part)
 seen.update(part);ids=np.array(sorted(part));pts=p[t[ids]];ee={e:fs for e,fs in edges.items() if any(f in part for f in fs)};comps.append({'faces':ids.tolist(),'count':len(ids),'boundary_edges':sum(len(fs)==1 for fs in ee.values()),'over_shared_contacts':sum(len(fs)>2 for fs in ee.values()),'bounds':[pts.reshape(-1,3).min(0).tolist(),pts.reshape(-1,3).max(0).tolist()],'signed_volume':float(np.einsum('ij,ij->i',pts[:,0],np.cross(pts[:,1],pts[:,2])).sum()/6)})
j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);rows=[]
for bi,ni in enumerate(d['skins'][0]['joints']):
 sel=(w*(j==bi)).sum(1)>.3
 if sel.any():rows.append({'bone':d['nodes'][ni]['name'],'vertices':int(sel.sum()),'center':p[sel].mean(0).round(3).tolist()})
report={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'triangles':len(t),'joint_count':len(d['skins'][0]['joints']),'clips':len(d.get('animations',[])),'boundary_edges':sum(len(fs)==1 for fs in edges.values()),'over_shared_edges':sum(len(fs)>2 for fs in edges.values()),'bounds':[p.min(0).tolist(),p.max(0).tolist()],'boundary_groups':groups,'joint_regions':rows}
(ROOT/'input-audit.json').write_text(json.dumps(report,indent=2));(ROOT/'face-components.json').write_text(json.dumps(comps,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['boundary_groups','joint_regions']}));print('COMPONENTS',collections.Counter((c['count'],c['boundary_edges'],c['over_shared_contacts']) for c in comps));print('HOLES',[(g['edge_count'],g['min'],g['max']) for g in groups if g['edge_count']>2]);print('JOINTS',rows)
