import sys,json,collections,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);print('PRIMITIVES',len(d['meshes'][0]['primitives']),'MODE',pr.get('mode',4),'ROWS',len(p),'EXACT_UNIQUE',len(np.unique(p,axis=0)));tree=cKDTree(p);results=[]
for tol in [1e-6,3e-6,6e-6,1e-5,3e-5,1e-4]:
 parent=np.arange(len(p))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for u,v in tree.query_pairs(tol):
  a=find(u);c=find(v);parent[c]=a
 mp=np.array([find(i) for i in range(len(p))]);wt=mp[t];edges=collections.Counter(tuple(sorted((int(a),int(c)))) for ft in wt for a,c in zip(ft,np.roll(ft,-1)));row={'tolerance':tol,'unique_positions':len(np.unique(mp)),'boundary_edges':sum(n==1 for n in edges.values()),'over_shared_edges':sum(n>2 for n in edges.values()),'collapsed_triangles':sum(len(set(ft))<3 for ft in wt)};results.append(row);print(row)
files=[]
for path in [Path('D:/user/Downloads/hornet_front - 6 legs touchup.glb'),Path('D:/dev/new-mech-rpg/art/model_catalog/sources/hornet_front - Hunyuan 3D v3.1 Pro.glb')]:
 doc,blob=read_glb(path);meshes=[]
 for mesh in doc['meshes']:
  for pp in mesh['primitives']:
   pp0=accessor(doc,blob,pp['attributes']['POSITION']);tt=accessor(doc,blob,pp['indices']).reshape(-1,3);meshes.append({'vertices':len(pp0),'triangles':len(tt),'bounds':[pp0.min(0).tolist(),pp0.max(0).tolist()]})
 files.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'joint_count':sum(len(s['joints']) for s in doc.get('skins',[])),'primitives':meshes});print(files[-1])
(ROOT/'precision-and-baseline-audit.json').write_text(json.dumps({'weld_tolerances':results,'quality_baselines':files},indent=2)+'\n')
