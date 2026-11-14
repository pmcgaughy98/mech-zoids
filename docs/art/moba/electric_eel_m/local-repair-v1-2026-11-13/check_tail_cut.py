import sys,json,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());d,b=read_glb(r['output']);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']]
def weight(nums):return (w*np.isin(j,[names.index(f'Bone_{n:03}') for n in nums])).sum(1)
other=weight([34,35,36,37,43,44,45]);field=weight([46,47,48])-2*other
for level in [.15,.25,.4,.55]:
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
 print(level,parts)
np.savez(ROOT/'tail-cut-fields.npz',field=field,protected=other)
