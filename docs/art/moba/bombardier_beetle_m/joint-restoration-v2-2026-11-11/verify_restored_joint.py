import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb,accessor,topology
BASE=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m');OUT=BASE/'joint-restoration-v2-2026-11-11'
def load(path):
 d,b=read_glb(path);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);return d,b,pr,p,t
sd,sb,sp,pos,st=load(BASE/'input-review-2026-11-11/beetle-rigged-local-cleanup-STAGING.glb');n=len(pos)
_,_,_,_,old=load(BASE/'pair-2-removal-v1-2026-11-11/bombardier-beetle-six-legs-rigged-v1.glb');target=OUT/'bombardier-beetle-joints-restored-v2.glb';d,b,pr,p,t=load(target)
source_set={tuple(sorted(map(int,f))) for f in st};old_set={tuple(sorted(map(int,f))) for f in old if max(f)<n};new_set={tuple(sorted(map(int,f))) for f in t if max(f)<n}
distance=np.full(n,np.inf)
for side in [-1,1]:
 a=np.array([side*.4925,.7609,.46634]);end=np.array([side*.6602,.4465,.70737]);ab=end-a;u=np.clip(((pos-a)@ab)/(ab@ab),0,1);distance=np.minimum(distance,np.linalg.norm(pos-(a+u[:,None]*ab),axis=1))
protected=np.flatnonzero(distance<.18);pf=st[np.isin(st,protected).any(1)];protected_set={tuple(sorted(map(int,f))) for f in pf};missing=protected_set-new_set;restored=(protected_set&new_set)-old_set;assert not missing and restored
for name in ['POSITION','NORMAL','TEXCOORD_0']:assert np.array_equal(accessor(d,b,pr['attributes'][name])[:n],accessor(sd,sb,sp['attributes'][name])),name
alltri=np.concatenate([accessor(d,b,v['indices']).reshape(-1,3).astype(np.int64) for v in d['meshes'][0]['primitives']]);mp,edges,groups,deg=topology(p,alltri);foot_edges=[e for e in edges if p[e[0],1]<.18 and p[e[1],1]<.18];neighbors={}
for a,c in foot_edges:neighbors.setdefault(a,set()).add(c);neighbors.setdefault(c,set()).add(a)
seen=set();feet=[]
for start in neighbors:
 if start in seen:continue
 pending=[start];part=set()
 while pending:
  vi=pending.pop()
  if vi in part:continue
  part.add(vi);pending.extend(neighbors[vi]-part)
 seen.update(part)
 if len(part)>10:feet.append({'vertices':len(part),'center_gltf':p[list(part)].mean(0).tolist()})
assert len(feet)==6,feet
report={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'protected_source_joint_faces':len(protected_set),'protected_faces_missing_after_v2':len(missing),'source_joint_faces_restored_relative_to_v1':len(restored),'all_source_shoulder_faces_restored_relative_to_v1':len((source_set&new_set)-old_set),'protected_source_position_normal_uv_values_unchanged':True,'low_foot_surface_components':feet,'foot_component_count':len(feet)}
(OUT/'restored-joint-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
