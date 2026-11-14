import sys,json,hashlib,collections,io
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13')
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_shoebill_single_material_25k_20261111_character.glb')
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='c0afacfd4294556e98220d6e89996a6e246430ffaf58ec3805941bd8240cb4a0'
d,b=read_glb(SOURCE);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);uv=accessor(d,b,pr['attributes']['TEXCOORD_0']);j=accessor(d,b,pr['attributes']['JOINTS_0']);w=accessor(d,b,pr['attributes']['WEIGHTS_0']);mp,edges,groups,deg=topology(p,t)
adj=[set() for _ in t]
for e,fs in edges.items():
 if len(fs)==2:a,c=fs;adj[a].add(c);adj[c].add(a)
seen=set();comps=[]
for start in range(len(t)):
 if start in seen:continue
 pending=[start];part=set()
 while pending:
  f=pending.pop()
  if f in part:continue
  part.add(f);pending.extend(adj[f]-part)
 seen.update(part);ids=np.asarray(sorted(part));pts=p[t[ids]];part_edges={e:fs for e,fs in edges.items() if any(f in part for f in fs)}
 row={'faces':ids.tolist(),'count':len(ids),'bounds':[pts.reshape(-1,3).min(0).tolist(),pts.reshape(-1,3).max(0).tolist()],'boundary_edges':sum(len(fs)==1 for fs in part_edges.values()),'over_shared_contacts':sum(len(fs)>2 for fs in part_edges.values()),'signed_volume':float(np.einsum('ij,ij->i',pts[:,0],np.cross(pts[:,1],pts[:,2])).sum()/6)};comps.append(row)
print('COMPONENTS',[(i,{k:v for k,v in c.items() if k!='faces'}) for i,c in enumerate(comps) if c['count']>2],flush=True)
(ROOT/'face-components.json').write_text(json.dumps(comps,indent=2))
names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']];rows=[]
for bi,name in enumerate(names):
 weight=(w*(j==bi)).sum(1);sel=weight>.3
 if sel.any():rows.append({'bone':name,'vertices':int(sel.sum()),'center':p[sel].mean(0).round(4).tolist()})
(ROOT/'joint-regions.json').write_text(json.dumps(rows,indent=2));print('JOINTS',rows,flush=True)
view=d['bufferViews'][d['images'][0]['bufferView']];tex=Image.open(io.BytesIO(b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])).convert('RGB');tex.save(ROOT/'source-basecolor.png');rgb=np.array(tex)
for label,coords in [('centroid',uv[t].mean(1))]:
 # glTF's numeric UV origin maps directly to PNG row order.
 xy=np.clip(coords*np.array(tex.size),0,np.array(tex.size)-1).astype(int);color=rgb[xy[:,1],xy[:,0]]/255
 np.savez(ROOT/'mesh-analysis.npz',positions=p,triangles=t,uv=uv,triangle_rgb=color)
print('TEXTURE',tex.size,flush=True)
