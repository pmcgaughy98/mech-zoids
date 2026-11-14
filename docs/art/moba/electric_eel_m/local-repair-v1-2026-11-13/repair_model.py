import json,sys,copy,struct,hashlib,collections,itertools,io
from PIL import Image
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13');cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);n=accessor(d,b,pr['attributes']['NORMAL']);uv=accessor(d,b,pr['attributes']['TEXCOORD_0']);tri=accessor(d,b,pr['indices']).reshape(-1,3);mp,edges,groups,deg=topology(p,tri);comps=json.loads((ROOT/'face-components.json').read_text());remove={f for c in comps if c['count']<=3 and c['boundary_edges']>0 for f in c['faces']};assert len(remove)==64
new=np.delete(tri,sorted(remove),axis=0);mp,ee,gg,dd=topology(p,new);folds=[]
for g in gg:
 if g['edge_count']!=4:continue
 ids=set(g['vertices']);counter=collections.Counter(fi for edge,fs in ee.items() if len(fs)==1 and set(edge)<=ids for fi in fs);found=[fi for fi,c in counter.items() if c==2 and set(mp[new[fi]])<=ids];assert len(found)==1,(g,found);folds.extend(found)
assert len(folds)==5
kept_ids=np.array([i for i in range(len(tri)) if i not in remove]);remove.update(int(kept_ids[i]) for i in folds);new=np.delete(tri,sorted(remove),axis=0);mp,ee,gg,dd=topology(p,new);assert len(gg)==6 and all(g['edge_count']==3 for g in gg);caps=[]
for g in gg:
 ids=set(g['vertices']);edge,fs=next((edge,fs) for edge,fs in ee.items() if len(fs)==1 and set(edge)<=ids);ft=new[fs[0]];a,c=next((int(a),int(c)) for a,c in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[a]),int(mp[c]))))==edge);other=next(iter(ids-{int(mp[a]),int(mp[c])}));order=[int(mp[c]),int(mp[a]),other];choices=[]
 for raw in itertools.product(*(np.where(mp==vi)[0].tolist() for vi in order)):
  points=p[list(raw)];normal=np.cross(points[1]-points[0],points[2]-points[0]);normal/=max(np.linalg.norm(normal),1e-12);alignment=float(normal@n[list(raw)].mean(0))
  if alignment>.25:choices.append((sum(float(np.linalg.norm(uv[raw[i]]-uv[raw[(i+1)%3]])) for i in range(3)),list(raw),normal.tolist(),alignment))
 assert choices;perimeter,raw,normal,alignment=min(choices);caps.append({'triangle':raw,'bounds':[g['min'],g['max']],'normal':normal,'normal_alignment':alignment,'uv_perimeter':perimeter});new=np.concatenate([new,np.array([raw])])
mp,after_edges,gg,dd=topology(p,new);contacts=[edge for edge,fs in after_edges.items() if len(fs)>2];assert not gg and not dd and len(contacts)==1
for edge in contacts:
 assert len(after_edges[edge])==len(edges[edge])==4
 directions=[]
 for fi in after_edges[edge]:
  ft=mp[new[fi]];directions.extend(int(a<c) for a,c in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(a),int(c))))==edge)
 assert sum(directions)==2
detail=next(c for c in comps if c['count']==4);assert detail['signed_volume']>0 and all(i not in remove for i in detail['faces'])
out=b+b'\0'*((-len(b))%4)
def append(array,component,kind,target):
 global out
 out+=b'\0'*((-len(out))%4);offset=len(out);data=array.tobytes();out+=data;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':target});ai=len(d['accessors']);entry={'bufferView':vi,'componentType':component,'count':len(array),'type':kind}
 if kind=='VEC3':entry['min']=array.min(0).tolist();entry['max']=array.max(0).tolist()
 d['accessors'].append(entry);return ai
# The final closure crosses an existing bad UV strip. Give only its three
# corners a small healthy bronze sample from the same nearby collar texture.
image=d['images'][0];view=d['bufferViews'][image['bufferView']];tex=Image.open(io.BytesIO(b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])).convert('RGB');pixels=np.array(tex)/255.;centers=p[tri].mean(1);uvcenters=uv[tri].mean(1);target=(np.array(caps[-1]['bounds'][0])+np.array(caps[-1]['bounds'][1]))/2;choices=[]
for fi in np.argsort(np.linalg.norm(centers-target,axis=1)):
 if fi in remove or np.linalg.norm(centers[fi]-target)>.6:continue
 xy=(uvcenters[fi]*np.array(tex.size)).astype(int);x,y=xy
 if not(5<=x<tex.width-5 and 5<=y<tex.height-5):continue
 rgb=pixels[y,x];patch=pixels[y-4:y+5,x-4:x+5]
 if rgb[0]>.4 and rgb[1]>.2 and rgb[0]>rgb[2]*1.15 and rgb[0]>rgb[1]*1.05 and patch.std((0,1)).max()<.10:choices.append((float(np.linalg.norm(centers[fi]-target)),int(fi),uvcenters[fi]));break
assert choices;_,sample_face,sample_uv=choices[0];oldcap=caps[-1]['triangle'];count=len(p);new_ids=np.arange(count,count+3);new[-1]=new_ids
for key,idx in list(pr['attributes'].items()):
 array=accessor(original,b,idx);extra=array[oldcap].copy()
 if key=='TEXCOORD_0':extra=np.asarray(sample_uv+np.array([[0,-2],[2,2],[-2,2]])/np.array(tex.size),dtype=array.dtype)
 old=d['accessors'][idx];pr['attributes'][key]=append(np.concatenate([array,extra]),old['componentType'],old['type'],34962)
caps[-1]['original_triangle_corners']=oldcap;caps[-1]['triangle']=new_ids.tolist();caps[-1]['uv_finish_source_face']=sample_face
pr['indices']=append(new.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);d['buffers'][0]['byteLength']=len(out);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);out+=b'\0'*((-len(out))%4);dest=OUT/'electric-eel-rigged-local-repair-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(out))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(out),0x004e4942)+out)
for key in ['nodes','skins','materials','images','textures','samplers','scene','scenes','animations']:assert d.get(key)==original.get(key)
main=max(comps,key=lambda c:c['count']);report={'source':cfg['source'],'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'before_triangles':len(tri),'final_triangles':len(new),'joint_count':56,'removed_malformed_triangles':len(remove),'removed_face_ids':sorted(remove),'holes_closed':caps,'boundary_edges':0,'over_shared_edges':1,'protected_closed_contact_edges':[list(e) for e in contacts],'contact_note':'Original positive-volume closed four-triangle assembly detail retained; its balanced four-face source contact is unchanged.','collapsed_triangles':0,'healthy_main_body_source_faces_retained':len(set(main['faces'])-remove),'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved':True,'new_geometric_vertices':0,'uv_seam_duplicate_rows':3,'scope':'Local topology repair with three duplicate UV corners for one bronze closure. Original body, fins, head, tail, rig and all original rows retained. Tail-prong selection pending.'};(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['removed_face_ids','holes_closed']},indent=2))
