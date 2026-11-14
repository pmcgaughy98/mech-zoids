import sys,json,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);ns=d['skins'][0]['joints'];names=[d['nodes'][i]['name'] for i in ns];parents={ci:pi for pi,n in enumerate(d['nodes']) for ci in n.get('children',[])};ib=accessor(d,b,d['skins'][0]['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
for i,n in enumerate(names):
 if int(n[-3:])>=9:print(n,'parent',d['nodes'][parents[ns[i]]]['name'],'bind',np.linalg.inv(ib[i])[:3,3].round(3).tolist())
removed=[names.index(f'Bone_{i:03}') for i in [27,28,37,38]];upper=(w*np.isin(j,removed)).sum(1);other=(w*np.isin(j,[names.index(f'Bone_{i:03}') for i in [25,29,30,31,32,33,34,35,39,40,41,42,43,44]])).sum(1);field=upper-2*other
for level in [.1,.2,.3]:
 adj=collections.defaultdict(set)
 for ft in t:
  f=field[ft]-level;hits=[]
  for a,b in [(0,1),(1,2),(2,0)]:
   if (f[a]>0)!=(f[b]>0):hits.append(tuple(np.round(p[ft[a]]+(p[ft[b]]-p[ft[a]])*f[a]/(f[a]-f[b]),6)))
  if len(hits)==2:adj[hits[0]].add(hits[1]);adj[hits[1]].add(hits[0])
 seen=set();parts=[]
 for start in adj:
  if start in seen:continue
  stack=[start];part=set()
  while stack:
   v=stack.pop()
   if v in part:continue
   part.add(v);stack.extend(adj[v]-part)
  seen.update(part);pts=np.array(list(part));parts.append((len(part),all(len(adj[v])==2 for v in part),pts.min(0).round(3).tolist(),pts.max(0).round(3).tolist()))
 print('LEVEL',level,parts)
np.savez(ROOT/'toe-cut-fields.npz',field=field,protected=other)
