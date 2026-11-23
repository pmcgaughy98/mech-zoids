import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10');from diagnose import *
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output']);ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0]
assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'] and bb[:len(ab)]==ab
for k in ['nodes','skins','materials','images','textures','samplers','scenes','scene','animations']:assert a.get(k)==b.get(k),k
for k,idx in ap['attributes'].items():
 if k not in ['POSITION','NORMAL']:assert np.array_equal(accessor(a,ab,idx),accessor(b,bb,bp['attributes'][k])),k
oldp=accessor(a,ab,ap['attributes']['POSITION']);p=accessor(b,bb,bp['attributes']['POSITION']);oldn=accessor(a,ab,ap['attributes']['NORMAL']);n=accessor(b,bb,bp['attributes']['NORMAL']);t=accessor(b,bb,bp['indices']).reshape(-1,3);oldtri=accessor(a,ab,ap['indices']).reshape(-1,3);remove=set(r['removed_face_ids']);kept=[i for i in range(len(oldtri)) if i not in remove];assert np.array_equal(t,oldtri[kept]) and len(t)==25960
mask=np.zeros(len(p),dtype=bool);mask[r['changed_row_ids']]=True;assert mask.sum()==2532 and np.array_equal(p[~mask],oldp[~mask]) and np.array_equal(n[~mask],oldn[~mask]);assert (oldp[mask,2]<-1.8).all() and (abs(oldp[mask,0])>.08).all();assert np.isfinite(p).all() and np.isfinite(n).all() and abs(np.linalg.norm(n,axis=1)-1).max()<1e-4
_,ee,groups,deg=topology(p,t);assert not groups and not deg and sum(len(fs)>2 for fs in ee.values())==2 and all(len(fs) in [2,4] for fs in ee.values())
used=np.unique(t);w=accessor(b,bb,bp['attributes']['WEIGHTS_0'])[used];j=accessor(b,bb,bp['attributes']['JOINTS_0'])[used];assert np.isfinite(w).all() and abs(w.sum(1)-1).max()<1e-5 and j.max()<37 and len(b['skins'][0]['joints'])==37
# Check each modified triangle against the continuous deformation's Jacobian at its centroid.
namespace={'__file__':str(ROOT/'repair_model.py')};script=(ROOT/'repair_model.py').read_text();exec(script[:script.index('changed=np.linalg')],namespace);warp=namespace['warp'];affected=mask[t].any(1);origpts=oldp[t[affected]].astype(float);centers=origpts.mean(1);h=1e-5;J=np.stack([(warp(centers+np.eye(3)[i]*h)-warp(centers-np.eye(3)[i]*h))/(2*h) for i in range(3)],axis=2);assert np.linalg.det(J).min()>.15
origface=np.cross(origpts[:,1]-origpts[:,0],origpts[:,2]-origpts[:,0]);predicted=np.linalg.solve(J.transpose(0,2,1),origface[...,None])[...,0];newpts=p[t[affected]].astype(float);actual=np.cross(newpts[:,1]-newpts[:,0],newpts[:,2]-newpts[:,0]);dot=(actual*predicted).sum(1);assert (dot>0).all(),('inverted local triangles',int((dot<=0).sum()))
e=json.loads((ROOT/'model-entry.json').read_text());refhash={}
for v,item in e['views'].items():
 sha=hashlib.sha256((BASE/item['path'].removeprefix('res://')).read_bytes()).hexdigest();assert sha==item['sha256'];refhash[v]=sha
assert hashlib.sha256((BASE/e['source_model']['path'].removeprefix('res://')).read_bytes()).hexdigest()==r['source_sha256']
panels=[];measure=json.loads((ROOT/'panel-measurements.json').read_text())
for row in measure:
 ids=[kept.index(fi) for fi in row['face_ids']];points=p[t[ids]].mean(1);ev,vec=np.linalg.eigh(np.cov(points.T));axis=vec[:,-1];axis*=np.sign(axis[0]);angle=float(np.degrees(np.arctan2(axis[1],axis[0])));assert abs(angle)<3
 panels.append({'side':row['side'],'before_angle_xy_degrees':row['original_panel_angle_xy_degrees'],'after_angle_xy_degrees':angle})
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':25960,'joint_count':37,'boundary_edges':0,'over_shared_edges':2,'collapsed_triangles':0,'healthy_source_triangles_retained':25960,'local_vertex_rows_changed':2532,'all_other_positions_normals_unchanged':True,'all_uv_skin_rows_skeleton_rest_binds_materials_textures_unchanged':True,'source_binary_prefix_preserved':True,'modified_triangles_tested':int(affected.sum()),'local_triangle_inversions':0,'minimum_centroid_jacobian_determinant':float(np.linalg.det(J).min()),'rear_panel_alignment':panels,'original_reference_sha256':refhash,'downloaded_input_sha256':r['source_sha256'],'intact_pre_remesh_available':False}
(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
