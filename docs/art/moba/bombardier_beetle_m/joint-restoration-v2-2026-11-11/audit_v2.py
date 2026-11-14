import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/joint-restoration-v2-2026-11-11');target=OUT/'bombardier-beetle-joints-restored-v2.glb';d,b=read_glb(target);pp=[];tt=[];seen={};offset=0
for pr in d['meshes'][0]['primitives']:
 ai=pr['attributes']['POSITION']
 if ai not in seen:
  p=accessor(d,b,ai);seen[ai]=offset;pp.append(p);offset+=len(p)
 tt.append(accessor(d,b,pr['indices']).reshape(-1,3).astype(np.int64)+seen[ai])
pos=np.concatenate(pp);tri=np.concatenate(tt);m,e,g,deg=topology(pos,tri);pr=d['meshes'][0]['primitives'][0];w=accessor(d,b,pr['attributes']['WEIGHTS_0']);j=accessor(d,b,pr['attributes']['JOINTS_0'])
cap_pr=d['meshes'][0]['primitives'][1];cap_tri=accessor(d,b,cap_pr['indices']).reshape(-1,3);cap_pos=accessor(d,b,cap_pr['attributes']['POSITION']);cp=cap_pos[cap_tri];cross=np.cross(cp[:,1]-cp[:,0],cp[:,2]-cp[:,0]);outward=bool(np.all(cross[:,0]*cp[:,:,0].mean(1)>0))
report={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'unique_attribute_positions':len(pos),'triangles':len(tri),'primitives':len(d['meshes'][0]['primitives']),'boundary_edges':sum(len(v)==1 for v in e.values()),'over_shared_edges':sum(len(v)>2 for v in e.values()),'collapsed':len(deg),'weights_finite':bool(np.isfinite(w).all()),'weight_sum_max_error':float(abs(w.sum(1)-1).max()),'joint_index_max':int(j.max()),'socket_faces_outward':outward};assert not g and not deg and all(len(v)==2 for v in e.values());assert report['weights_finite'] and report['joint_index_max']<64 and outward
(OUT/'export-topology-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
