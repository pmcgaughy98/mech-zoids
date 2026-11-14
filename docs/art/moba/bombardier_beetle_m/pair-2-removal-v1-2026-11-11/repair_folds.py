import sys,json,copy,hashlib,struct
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/input-review-2026-11-11')
SRC=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb')
d,b=read_glb(SRC);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);t=accessor(d,b,pr['indices']).reshape(-1,3);mp,ed,groups,deg=topology(p,t);removed=[]
for g in groups:
 ids=set(g['vertices']);assert len(ids)==3 and g['edge_count']==2
 root=[fs for e,fs in ed.items() if set(e)<=ids and len(fs)==3];assert len(root)==1
 fins=[f for f in root[0] if set(mp[t[f]])==ids];assert len(fins)==1;removed.extend(fins)
assert len(removed)==4
keep=np.ones(len(t),dtype=bool);keep[removed]=False;nt=t[keep];_,ae,ag,ad=topology(p,nt);assert not ag and not ad and all(len(v)==2 for v in ae.values())
blob=b+b'\0'*((-len(b))%4);offset=len(blob);raw=nt.astype('<u2').tobytes();blob+=raw;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':34963});ai=len(d['accessors']);d['accessors'].append({'bufferView':vi,'componentType':5123,'count':int(nt.size),'type':'SCALAR'});pr['indices']=ai;d['buffers'][0]['byteLength']=len(blob)
encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);blob+=b'\0'*((-len(blob))%4);target=OUT/'beetle-rigged-local-cleanup-STAGING.glb';target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(blob))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(blob),0x004e4942)+blob)
for key in ['nodes','skins','materials','textures','images','samplers','scenes','scene','animations']:assert d.get(key)==original.get(key)
assert blob[:len(b)]==b
report={'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'removed_triangle_ids':removed,'before_triangles':len(t),'after_triangles':len(nt),'before_boundary_edges':8,'before_over_shared_edges':4,'after_boundary_edges':0,'after_over_shared_edges':0,'all_original_vertex_attributes_and_rig_bytes_unchanged':True,'anatomy':'Still eight walking legs. Awaiting user selection before six-leg correction. Not promoted to Workshop.'}
(OUT/'local-cleanup-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
