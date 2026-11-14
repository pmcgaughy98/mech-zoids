import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/falcon_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output']);s,sb=read_glb(r['surgery_input']);ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0];sp=s['meshes'][0]['primitives'][0];assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'] and bb[:len(ab)]==ab and bb[:len(sb)]==sb
for k in ['nodes','skins','images','textures','samplers','scenes','scene','animations']:assert a.get(k)==b.get(k),k
assert a['materials']==b['materials'][:-1]
for k,idx in ap['attributes'].items():
 if k in ['JOINTS_0','WEIGHTS_0']:continue
 old=accessor(a,ab,idx);assert np.array_equal(old,accessor(b,bb,bp['attributes'][k])[:len(old)]),k
p=accessor(b,bb,bp['attributes']['POSITION']);t=np.concatenate([accessor(b,bb,pr['indices']).reshape(-1,3) for pr in b['meshes'][0]['primitives']]);_,e,g,deg=topology(p,t);assert not g and not deg;contacts=[list(k) for k,v in e.items() if len(v)>2];assert contacts==r['protected_closed_contact_edges'] and all(len(e[tuple(k)])==4 for k in contacts)
used=np.unique(t);w=accessor(b,bb,bp['attributes']['WEIGHTS_0']);j=accessor(b,bb,bp['attributes']['JOINTS_0']);assert np.isfinite(p[used]).all() and np.isfinite(w[used]).all() and abs(w[used].sum(1)-1).max()<1e-5 and j[used].max()<45
names=[b['nodes'][i]['name'] for i in b['skins'][0]['joints']];removed=[names.index(n) for n in r['removed_skin_chains']];assert not np.any((w[used]>1e-8)&np.isin(j[used],removed))
def dense(j,w):
 a=np.zeros((len(j),45));np.add.at(a,(np.arange(len(j))[:,None],j),w);return a
sj=accessor(s,sb,sp['attributes']['JOINTS_0']);sw=accessor(s,sb,sp['attributes']['WEIGHTS_0']);expected=dense(sj,sw);new=dense(j[:len(sj)],w[:len(sj)]);affected=np.intersect1d(used,np.arange(len(sj)));
for bone,parent in r['residual_influence_mapping'].items():
 bi=names.index(bone);pi=names.index(parent);expected[affected,pi]+=expected[affected,bi];expected[affected,bi]=0
assert abs(expected-new).max()<2e-7
st=accessor(s,sb,sp['indices']).reshape(-1,3);cut=set(r['staged_faces_cut_or_removed']);present=set(map(tuple,t.tolist()));assert all(tuple(ft) in present for fi,ft in enumerate(st) if fi not in cut)
rawtri=accessor(a,ab,ap['indices']).reshape(-1,3);main=max(json.loads((ROOT/'face-components.json').read_text()),key=lambda c:c['count']);healthy_count=sum(tuple(rawtri[i]) in present for i in main['faces'] if i not in set(r['removed_face_ids']))
detail=next(c for c in json.loads((ROOT/'face-components.json').read_text()) if c['count']==4);assert all(tuple(rawtri[i]) in present for i in detail['faces'])
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(t),'joint_count':45,'boundary_edges':0,'collapsed_triangles':0,'protected_original_four_face_contact_count':len(contacts),'healthy_main_body_source_faces_retained':healthy_count,'staged_faces_retained_exactly':len(st)-len(cut),'retained_toe_guard_faces':r['retained_toe_guard_faces'],'all_original_position_normal_uv_rows_unchanged':True,'skeleton_rest_binds_original_materials_textures_unchanged':True,'local_skin_transfer_only_removed_chains_to_existing_parent':True,'removed_toe_chain_surface_influence':0,'source_and_surface_stage_binary_prefix_preserved':True}
captri=accessor(b,bb,b['meshes'][0]['primitives'][1]['indices']).reshape(-1,3);off=0
for cap in r['toe_socket_closures']:
 count=cap['closure_triangles'];pts=p[captri[off:off+count]];norm=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);assert np.all(norm@np.asarray(cap['normal'])>0);off+=count
assert off==len(captri);result['inverted_projected_closure_triangles']=0
oldp=accessor(a,ab,ap['attributes']['POSITION']);added=p[np.unique(t)[np.unique(t)>=len(oldp)]];distance=cKDTree(oldp).query(added)[0];new_positions=np.unique(np.round(added[distance>1e-6],6),axis=0);r.pop('new_geometric_vertices',None);r['new_geometric_positions']=len(new_positions);r['healthy_main_body_source_faces_retained']=healthy_count;(OUT/'repair-verification.json').write_text(json.dumps(r,indent=2)+'\n');(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
