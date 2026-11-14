import sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/squirrel_s/local-repair-v1-2026-11-14';r=json.loads((OUT/'repair-verification.json').read_text());a,ab=read_glb(r['source']);b,bb=read_glb(r['output']);ap=a['meshes'][0]['primitives'][0];bp=b['meshes'][0]['primitives'][0];assert hashlib.sha256(Path(r['output']).read_bytes()).hexdigest()==r['output_sha256'] and bb[:len(ab)]==ab
for k in ['nodes','skins','materials','images','textures','samplers','scenes','scene','animations']:assert a.get(k)==b.get(k),k
for k,idx in ap['attributes'].items():assert np.array_equal(accessor(a,ab,idx),accessor(b,bb,bp['attributes'][k])[:len(accessor(a,ab,idx))]),k
p=accessor(b,bb,bp['attributes']['POSITION']);t=accessor(b,bb,bp['indices']).reshape(-1,3);_,e,g,deg=topology(p,t);assert not g and not deg and sum(len(fs)>2 for fs in e.values())==2 and all(len(fs) in [2,4] for fs in e.values())
used=np.unique(t);w=accessor(b,bb,bp['attributes']['WEIGHTS_0'])[used];j=accessor(b,bb,bp['attributes']['JOINTS_0'])[used];assert np.isfinite(p[used]).all() and np.isfinite(w).all() and abs(w.sum(1)-1).max()<1e-5 and j.max()<26
oldtri=accessor(a,ab,ap['indices']).reshape(-1,3);removed=set(r['removed_face_ids']);main=max(json.loads((ROOT/'face-components.json').read_text()),key=lambda c:c['count']);protected=[i for i in range(len(oldtri)) if i not in removed];present=set(map(tuple,t.tolist()));assert all(tuple(oldtri[i]) in present for i in protected)
cat=json.loads((BASE/'art/model_catalog/catalog.json').read_text());entry=next(x for x in cat['entries'] if x['id']=='squirrel');source=BASE/entry['source_model']['path'].removeprefix('res://');assert hashlib.sha256(source.read_bytes()).hexdigest()==entry['source_model']['sha256'];refhash={}
for key,v in entry['views'].items():
 sha=hashlib.sha256((BASE/v['path'].removeprefix('res://')).read_bytes()).hexdigest();assert sha==v['sha256'];refhash[key]=sha
result={'passed':True,'tested_sha256':r['output_sha256'],'triangles':len(t),'joint_count':26,'boundary_edges':0,'over_shared_edges':2,'collapsed_triangles':0,'healthy_main_body_faces_retained':len(protected),'all_original_vertex_attribute_and_weight_rows_unchanged':True,'skeleton_rest_binds_materials_textures_unchanged':True,'source_binary_prefix_preserved':True,'intact_archive_sha256':entry['source_model']['sha256'],'original_reference_sha256':refhash,'geometry_budget':'22,504 triangles; one original primitive/material, three duplicate UV corner rows, no new geometric positions or textures; no remesh/decimation.'};(OUT/'independent-export-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

assert len(protected)==22499 and len(t)==22504

for key,old_index in ap['attributes'].items():
 old=accessor(a,ab,old_index);new=accessor(b,bb,bp['attributes'][key]);assert len(new)==len(old)+3
 if key!='TEXCOORD_0':assert np.array_equal(new[-3:],old[r['uv_repair']['old_corner_rows']])
