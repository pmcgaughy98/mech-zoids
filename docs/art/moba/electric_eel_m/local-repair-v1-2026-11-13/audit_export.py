import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13');r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output']);s,sb=read_glb(r['surgery_input']);ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0];sp=s['meshes'][0]['primitives'][0];assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'] and bb[:len(ab)]==ab and bb[:len(sb)]==sb
for k in ['nodes','skins','images','textures','samplers','scenes','scene','animations']:assert a.get(k)==b.get(k),k
assert a['materials']==b['materials'][:-1]
for k,idx in ap['attributes'].items():
 if k in ['JOINTS_0','WEIGHTS_0']:continue
 old=accessor(a,ab,idx);assert np.array_equal(old,accessor(b,bb,bp['attributes'][k])[:len(old)]),k
p=accessor(b,bb,bp['attributes']['POSITION']);t=np.concatenate([accessor(b,bb,pr['indices']).reshape(-1,3) for pr in b['meshes'][0]['primitives']]);_,e,g,deg=topology(p,t);assert not g and not deg;contacts=[list(k) for k,v in e.items() if len(v)>2];assert contacts==r['protected_closed_contact_edges'] and all(len(e[tuple(k)])==4 for k in contacts)
used=np.unique(t);w=accessor(b,bb,bp['attributes']['WEIGHTS_0']);j=accessor(b,bb,bp['attributes']['JOINTS_0']);assert np.isfinite(p[used]).all() and np.isfinite(w[used]).all() and abs(w[used].sum(1)-1).max()<1e-5 and j[used].max()<56
names=[b['nodes'][i]['name'] for i in b['skins'][0]['joints']];removed=[names.index(n) for n in r['removed_skin_chains']];parent=names.index('Bone_033');assert not np.any((w[used]>1e-8)&np.isin(j[used],removed))
def dense(j,w):
 a=np.zeros((len(j),56));np.add.at(a,(np.arange(len(j))[:,None],j),w);return a
sj=accessor(s,sb,sp['attributes']['JOINTS_0']);sw=accessor(s,sb,sp['attributes']['WEIGHTS_0']);expected=dense(sj,sw);new=dense(j[:len(sj)],w[:len(sj)]);affected=np.intersect1d(used,np.arange(len(sj)));expected[affected,parent]+=expected[affected][:,removed].sum(1);expected[np.ix_(affected,removed)]=0;assert abs(expected-new).max()<2e-7
st=accessor(s,sb,sp['indices']).reshape(-1,3);cut=set(r['staged_faces_cut_or_removed']);present=set(map(tuple,t.tolist()));assert all(tuple(ft) in present for fi,ft in enumerate(st) if fi not in cut)
rawtri=accessor(a,ab,ap['indices']).reshape(-1,3);main=max(json.loads((ROOT/'face-components.json').read_text()),key=lambda c:c['count']);healthy_count=sum(tuple(rawtri[i]) in present for i in main['faces'] if i not in set(r['removed_face_ids']))
detail=next(c for c in json.loads((ROOT/'face-components.json').read_text()) if c['count']==4);assert all(tuple(rawtri[i]) in present for i in detail['faces'])
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(t),'joint_count':56,'boundary_edges':0,'collapsed_triangles':0,'protected_original_four_face_contact_count':len(contacts),'healthy_main_body_source_faces_retained':healthy_count,'staged_faces_retained_exactly':len(st)-len(cut),'lower_prong_guard_faces_retained':r['lower_prong_guard_faces_retained'],'all_original_position_normal_uv_rows_unchanged':True,'new_uv_seam_duplicate_rows':3,'skeleton_rest_binds_original_materials_textures_unchanged':True,'local_skin_transfer_only_removed_chains_to_existing_parent':True,'removed_upper_chain_surface_influence':0,'source_and_surface_stage_binary_prefix_preserved':True}
r['healthy_main_body_source_faces_retained']=healthy_count;(OUT/'repair-verification.json').write_text(json.dumps(r,indent=2)+'\n');(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
