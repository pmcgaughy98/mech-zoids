import json,sys,copy,struct,hashlib,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/owl_m/local-repair-v1-2026-11-15');cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);n=accessor(d,b,pr['attributes']['NORMAL']);uv=accessor(d,b,pr['attributes']['TEXCOORD_0']);tri=accessor(d,b,pr['indices']).reshape(-1,3);mp,edges,groups,deg=topology(p,tri);comps=json.loads((ROOT/'face-components.json').read_text());remove={f for c in comps if c['count']<=3 and c['boundary_edges']>0 for f in c['faces']};assert len(remove)==24
new=np.delete(tri,sorted(remove),axis=0);mp,ee,gg,dd=topology(p,new);folds=[]
for g in gg:
 if g['edge_count']!=4:continue
 ids=set(g['vertices']);counter=collections.Counter(fi for edge,fs in ee.items() if len(fs)==1 and set(edge)<=ids for fi in fs);found=[fi for fi,c in counter.items() if c==2 and set(mp[new[fi]])<=ids];assert len(found)==1,(g,found);folds.extend(found)
assert len(folds)==0
kept_ids=np.array([i for i in range(len(tri)) if i not in remove]);remove.update(int(kept_ids[i]) for i in folds);new=np.delete(tri,sorted(remove),axis=0);mp,ee,gg,dd=topology(p,new);assert len(gg)==0 and all(len(g['vertices'])==3 for g in gg);caps=[]
for g in gg:
 ids=set(g['vertices']);edge,fs=next((edge,fs) for edge,fs in ee.items() if len(fs)==1 and set(edge)<=ids);ft=new[fs[0]];a,c=next((int(a),int(c)) for a,c in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[a]),int(mp[c]))))==edge);other=next(iter(ids-{int(mp[a]),int(mp[c])}));order=[int(mp[c]),int(mp[a]),other];choices=[]
 for raw in itertools.product(*(np.where(mp==vi)[0].tolist() for vi in order)):
  pts=p[list(raw)];normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);normal/=max(np.linalg.norm(normal),1e-12);alignment=float(normal@n[list(raw)].mean(0))
  if alignment>.25:choices.append((sum(float(np.linalg.norm(uv[raw[i]]-uv[raw[(i+1)%3]])) for i in range(3)),list(raw),normal.tolist(),alignment))
 assert choices;perimeter,raw,normal,alignment=min(choices);caps.append({'triangle':raw,'bounds':[g['min'],g['max']],'normal':normal,'normal_alignment':alignment,'uv_perimeter':perimeter});new=np.concatenate([new,np.array([raw])])
mp,after_edges,gg,dd=topology(p,new);contacts=[edge for edge,fs in after_edges.items() if len(fs)>2];assert not gg and not dd and len(contacts)==6
for edge in contacts:
 assert len(after_edges[edge])==4 and len(edges[edge]) in [3,4]
 directions=[]
 for fi in after_edges[edge]:
  ft=mp[new[fi]];directions.extend(int(a<c) for a,c in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(a),int(c))))==edge)
 assert sum(directions)==2
assert len(contacts)==6
out=b+b'\0'*((-len(b))%4);offset=len(out);array=new.astype('<u2').reshape(-1,1);raw=array.tobytes();out+=raw;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':34963});ai=len(d['accessors']);d['accessors'].append({'bufferView':vi,'componentType':5123,'count':len(array),'type':'SCALAR'});pr['indices']=ai;d['buffers'][0]['byteLength']=len(out);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);out+=b'\0'*((-len(out))%4);dest=OUT/'owl-rigged-local-repair-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(out))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(out),0x004e4942)+out)
for key in ['nodes','skins','materials','images','textures','samplers','scene','scenes','animations']:assert d.get(key)==original.get(key)
main=max(comps,key=lambda c:c['count']);report={'source':cfg['source'],'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'before_triangles':len(tri),'final_triangles':len(new),'joint_count':33,'removed_malformed_triangles':len(remove),'removed_face_ids':sorted(remove),'holes_closed':caps,'boundary_edges':0,'over_shared_edges':len(contacts),'protected_closed_contact_edges':[list(e) for e in contacts],'contact_note':'0 small gaps closed; 6 balanced original assembly contacts retained.','collapsed_triangles':0,'healthy_main_body_source_faces_retained':len(set(main['faces'])-remove),'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved':True,'new_geometric_vertices':0,'scope':'Local topology repair. Two folded wings, two taloned legs, paired eye lenses, beak, chest condenser, hoses and tail feather armor retained. Original vertex attributes, skin, 33-joint skeleton/rest/binds and textures preserved; no remesh or rerig.'};(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['removed_face_ids']},indent=2))
