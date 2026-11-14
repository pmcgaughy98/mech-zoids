import sys,json
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/mantis_m/surface-restoration-v1-2026-11-10');d,b=read_glb(OUT/'mantis-restored-six-limbs-rigged-v1.glb');pp=[];tt=[];ws=[];js=[];offset=0
for pr in d['meshes'][0]['primitives']:
 p=accessor(d,b,pr['attributes']['POSITION']);pp.append(p);tt.append(accessor(d,b,pr['indices']).reshape(-1,3).astype(np.int64)+offset);offset+=len(p);ws.append(accessor(d,b,pr['attributes']['WEIGHTS_0']));js.append(accessor(d,b,pr['attributes']['JOINTS_0']))
pos=np.concatenate(pp);tri=np.concatenate(tt);m,e,g,deg=topology(pos,tri);report={'vertices':len(pos),'triangles':len(tri),'boundary_edges':sum(len(v)==1 for v in e.values()),'over_shared_edges':sum(len(v)>2 for v in e.values()),'collapsed':len(deg),'weights_finite':bool(np.isfinite(np.concatenate(ws)).all()),'weight_sum_max_error':float(abs(np.concatenate(ws).sum(1)-1).max()),'joint_index_max':int(np.concatenate(js).max())};assert not g and not deg and all(len(v)==2 for v in e.values());(OUT/'export-topology-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
