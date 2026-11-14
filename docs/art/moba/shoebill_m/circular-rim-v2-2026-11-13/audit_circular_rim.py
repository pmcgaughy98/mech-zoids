import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output'])
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'];assert bb[:len(ab)]==ab
for key in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert a.get(key)==b.get(key),key
assert b['meshes'][0]['primitives'][:2]==a['meshes'][0]['primitives'] and b['materials'][:2]==a['materials']
ps=[];ts=[];offset=0
for pr in b['meshes'][0]['primitives']:
 p=accessor(b,bb,pr['attributes']['POSITION']);t=accessor(b,bb,pr['indices']).reshape(-1,3);used,inverse=np.unique(t,return_inverse=True);ps.append(p[used]);ts.append(inverse.reshape(-1,3)+offset);offset+=len(used)
 w=accessor(b,bb,pr['attributes']['WEIGHTS_0'])[used];j=accessor(b,bb,pr['attributes']['JOINTS_0'])[used];assert np.isfinite(w).all() and abs(w.sum(1)-1).max()<1e-5 and j.max()<38
p=np.concatenate(ps);t=np.concatenate(ts);_,edges,groups,deg=topology(p,t);assert not groups and not deg and all(len(fs)==2 for fs in edges.values())
pr=b['meshes'][0]['primitives'][2];frame=accessor(b,bb,pr['attributes']['POSITION']);outer=frame.reshape(192,11,3)[:,6,:2];radius=np.linalg.norm(outer-np.array(r['plate_center_gltf_xy']),axis=1);error=float(abs(radius-.290).max());assert error<1e-6
names=[b['nodes'][i]['name'] for i in b['skins'][0]['joints']];j=accessor(b,bb,pr['attributes']['JOINTS_0']);w=accessor(b,bb,pr['attributes']['WEIGHTS_0']);assert np.all(j[:,0]==names.index('Bone_003')) and np.all(w[:,0]==1) and np.all(w[:,1:]==0)
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(t),'joint_count':38,'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'maximum_outer_circle_radius_error_m':error,'source_primitives_weights_materials_and_binary_preserved':True,'new_frame_rigidly_bound_to_existing_bone':'Bone_003','new_frame_vertices':len(frame)}
(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
