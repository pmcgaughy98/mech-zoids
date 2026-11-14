import json,sys,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']]
def weight(nums):return (w*np.isin(j,[names.index(f'Bone_{n:03}') for n in nums])).sum(1)
other=np.max([weight(c) for c in [[4,5,6],[7,8,9],[10,11,12],[13,14,15],[16,17,18],[19,20,21]]],axis=0)
f=weight([22,23,24,25,26,27])-2*other
for level in [.15,.25,.35,.45]:
 adj=collections.defaultdict(set)
 for ft in t:
  field=f[ft]-level;hits=[]
  for a,b in [(0,1),(1,2),(2,0)]:
   if (field[a]>0)!=(field[b]>0):hits.append(tuple(np.round(p[ft[a]]+(p[ft[b]]-p[ft[a]])*field[a]/(field[a]-field[b]),6)))
  if len(hits)==2:adj[hits[0]].add(hits[1]);adj[hits[1]].add(hits[0])
 seen=set();rows=[]
 for start in adj:
  if start in seen:continue
  stack=[start];part=set()
  while stack:
   v=stack.pop()
   if v in part:continue
   part.add(v);stack.extend(adj[v]-part)
  seen.update(part);pts=np.array(list(part));rows.append((len(part),all(len(adj[v])==2 for v in part),pts.min(0).round(3).tolist(),pts.max(0).round(3).tolist()))
 print(level,rows)
np.savez(ROOT/'cut-fields.npz',field=f,protected=other)
