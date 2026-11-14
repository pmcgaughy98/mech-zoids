import sys,json,copy,struct,hashlib,collections,shutil
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13')
dest=OUT/'electric-eel-rigged-local-repair-v1.glb';archive=OUT/'electric-eel-surface-only-staged.glb';sr=OUT/'surface-only-verification.json'
if not archive.exists():
 assert hashlib.sha256(dest.read_bytes()).hexdigest()=='5b6c148cc4bdee94a4f2e88b39148b5c20d027023ab113af8bdf6da3eb0c7828'
 shutil.copy2(dest,archive);shutil.copy2(OUT/'repair-verification.json',sr)
stage=json.loads(sr.read_text());d,blob=read_glb(archive);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];attrs={k:accessor(d,blob,v) for k,v in pr['attributes'].items()};pos=attrs['POSITION'];tri=accessor(d,blob,pr['indices']).reshape(-1,3)
cut_y=.695;cut_z=-5.48;data={k:[row.copy() for row in a] for k,a in attrs.items()};names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']];removed=[names.index(f'Bone_{i:03}') for i in [46,47,48]];parent=names.index('Bone_033')
parents={ci:pi for pi,n in enumerate(d['nodes']) for ci in n.get('children',[])};assert d['nodes'][parents[d['skins'][0]['joints'][names.index('Bone_048')]]]['name']=='Bone_033'
def skin(j,w):
 a=np.zeros(len(names));np.add.at(a,j,w);return a
def sparse(a):
 ji=np.argsort(a)[-4:][::-1];w=a[ji];w/=w.sum();return ji.astype(attrs['JOINTS_0'].dtype),w.astype('<f4')
def add(row):
 i=len(data['POSITION'])
 for k in data:data[k].append(np.asarray(row[k],dtype=attrs[k].dtype))
 return i
cache={};kept=[];uncut=[];cut=[]
def clip(poly,axis,bound,greater):
 result=[]
 for u,v in zip(poly,poly[1:]+poly[:1]):
  fu=float(data['POSITION'][u][axis]-bound);fv=float(data['POSITION'][v][axis]-bound);iu=fu>=0 if greater else fu<=0;iv=fv>=0 if greater else fv<=0
  if iu:result.append(u)
  if iu!=iv:
   edge=(axis,)+tuple(sorted((u,v)))
   if edge not in cache:
    t=fu/(fu-fv);row={key:data[key][u]*(1-t)+data[key][v]*t for key in attrs if key not in ['JOINTS_0','WEIGHTS_0']};row['POSITION'][axis]=bound;row['NORMAL']/=np.linalg.norm(row['NORMAL']);row['JOINTS_0'],row['WEIGHTS_0']=sparse(skin(data['JOINTS_0'][u],data['WEIGHTS_0'][u])*(1-t)+skin(data['JOINTS_0'][v],data['WEIGHTS_0'][v])*t);cache[edge]=add(row)
   result.append(cache[edge])
 return result
def emit(poly):
 for i in range(1,len(poly)-1):
  ft=[poly[0],poly[i],poly[i+1]];a,b,c=np.asarray(data['POSITION'])[ft]
  if np.linalg.norm(np.cross(b-a,c-a))>1e-10:kept.append(ft)
for fi,ft in enumerate(tri):
 if pos[ft,1].max()<=cut_y or pos[ft,2].min()>=cut_z:kept.append(ft.tolist());uncut.append(fi);continue
 cut.append(fi);front=clip(ft.tolist(),2,cut_z,True);split=[]
 for u,v in zip(front,front[1:]+front[:1]):
  split.append(u);pu,pv=data['POSITION'][u],data['POSITION'][v]
  if abs(pu[2]-cut_z)<1e-6 and abs(pv[2]-cut_z)<1e-6 and (pu[1]-cut_y)*(pv[1]-cut_y)<0:
   split.append(next(i for i in clip([u,v],1,cut_y,False) if i not in [u,v]))
 if split:
  first=next((i for i,v in enumerate(split) if abs(data['POSITION'][v][2]-cut_z)>1e-6),0);split=split[first:]+split[:first]
 emit(split);emit(clip(clip(ft.tolist(),2,cut_z,False),1,cut_y,False))
new=np.asarray(kept,dtype=np.int64);p=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(p,new)
# Subdivide neighboring source edges where the exact two-plane cut meets an
# otherwise unchanged triangle. This closes T junctions without moving it.
while len(groups)>1:
 small=next(g for g in groups if g['edge_count']==3);vs=small['vertices'];pair=max(((u,v) for u in vs for v in vs if u<v),key=lambda uv:np.linalg.norm(p[uv[0]]-p[uv[1]]));middle=next(v for v in vs if v not in pair);fi=edges[tuple(sorted(pair))][0];ft=new[fi];u,v=next((int(u),int(v)) for u,v in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[u]),int(mp[v]))))==tuple(sorted(pair)));other=next(int(k) for k in ft if k not in [u,v]);mid=next(k for k in clip([u,v],2,cut_z,False) if k not in [u,v]);assert np.linalg.norm(data['POSITION'][mid]-p[middle])<1e-6
 source_id=next((i for i in uncut if np.array_equal(tri[i],ft)),None)
 if source_id is not None:uncut.remove(source_id);cut.append(source_id)
 new=np.concatenate([np.delete(new,fi,0),np.array([[u,mid,other],[mid,v,other]])]);p=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(p,new)
assert len(groups)==1 and not deg,groups
# Retain every uncut source triangle, including the tiny closed four-face source detail.
print('CUT BOUNDS',pos[tri[cut]].min((0,1)),pos[tri[cut]].max((0,1)),flush=True)
assert np.array(cut).size and np.max(pos[tri[cut]][:, :, 2]) < -5.3
guard=np.where((pos[tri].mean(1)[:,2]<-5.65)&(pos[tri].max(1)[:,1]<.70))[0];assert set(guard)<=set(uncut)
changed=[]
for vi in np.unique(new):
 a=skin(data['JOINTS_0'][vi],data['WEIGHTS_0'][vi])
 if a[removed].sum()>0:
  a[parent]+=a[removed].sum();a[removed]=0;data['JOINTS_0'][vi],data['WEIGHTS_0'][vi]=sparse(a);changed.append(int(vi))
g=groups[0];ids=set(g['vertices']);nxt={};raw={}
for edge,fs in edges.items():
 if len(fs)!=1 or not set(edge)<=ids:continue
 ft=new[fs[0]];u,v=next((int(u),int(v)) for u,v in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[u]),int(mp[v]))))==edge);nxt[int(mp[u])]=int(mp[v]);raw[int(mp[u])]=u
first=next(iter(nxt));order=[first];cur=nxt[first]
while cur!=first:order.append(cur);cur=nxt[cur];assert len(order)<300
ring=[raw[i] for i in order][::-1];points=p[ring];corners=[i for i,pt in enumerate(points) if abs(pt[1]-cut_y)<1e-6 and abs(pt[2]-cut_z)<1e-6];assert len(corners)==2,corners
a,b=corners;loops=[ring[a:b+1],ring[b:]+ring[:a+1]];captri=[];normals=[]
for loop in loops:
 pts=p[loop];center=pts.mean(0);normal=np.cross(pts-center,np.roll(pts,-1,axis=0)-center).sum(0);normal/=np.linalg.norm(normal);normals.append(normal.tolist());capring=[];inner=[];center_skin=np.mean([skin(data['JOINTS_0'][i],data['WEIGHTS_0'][i]) for i in loop],axis=0)
 for vi,point in zip(loop,pts):
  row={k:data[k][vi].copy() for k in data};row['NORMAL']=normal;capring.append(add(row));row['POSITION']=center+(point-center)*.88;inner.append(add(row))
 row={k:data[k][loop[0]].copy() for k in data};row['POSITION']=center;row['NORMAL']=normal;row['JOINTS_0'],row['WEIGHTS_0']=sparse(center_skin);ci=add(row)
 for i in range(len(loop)):
  k=(i+1)%len(loop);captri.extend([[capring[i],capring[k],inner[k]],[capring[i],inner[k],inner[i]],[inner[i],inner[k],ci]])
captri=np.asarray(captri,dtype=np.int64);alltri=np.concatenate([new,captri]);p=np.asarray(data['POSITION']);mp,ee,gg,dd=topology(p,alltri);contacts=[list(e) for e,fs in ee.items() if len(fs)>2];assert not gg and not dd and len(contacts)==1
assert all(len(fs)==2 or (len(fs)==4 and list(e) in contacts) for e,fs in ee.items())
used=np.unique(alltri);jj=np.asarray(data['JOINTS_0']);ww=np.asarray(data['WEIGHTS_0']);assert not np.any((ww[used]>1e-8)&np.isin(jj[used],removed))
outblob=blob+b'\0'*((-len(blob))%4)
def append(a,component,kind,target):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);offset=len(outblob);outblob+=a.tobytes();vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':target});ai=len(d['accessors']);entry={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if kind=='VEC3':entry['min']=a.min(0).tolist();entry['max']=a.max(0).tolist()
 d['accessors'].append(entry);return ai
for k in data:
 old=d['accessors'][pr['attributes'][k]];pr['attributes'][k]=append(np.asarray(data[k],dtype=attrs[k].dtype),old['componentType'],old['type'],34962)
pr['indices']=append(new.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr=copy.deepcopy(pr);cappr['indices']=append(captri.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr['material']=len(d['materials']);d['materials'].append({'name':'Upper prong closed blue mounting plate','pbrMetallicRoughness':{'baseColorFactor':[.012,.055,.14,1],'metallicFactor':.72,'roughnessFactor':.34}});d['meshes'][0]['primitives'].append(cappr);d['buffers'][0]['byteLength']=len(outblob);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);outblob+=b'\0'*((-len(outblob))%4);dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(outblob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(outblob),0x004e4942)+outblob)
for k in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert d.get(k)==original.get(k)
assert d['materials'][:-1]==original['materials']
report=copy.deepcopy(stage);report.update({'surgery_input':str(archive),'surgery_input_sha256':stage['output_sha256'],'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'final_triangles':len(alltri),'selected_prong':1,'remaining_prongs':[2,3],'removed_skin_chains':['Bone_046','Bone_047','Bone_048'],'residual_influence_reassigned_to':'Bone_033','locally_reassigned_rows':len(changed),'local_reassigned_row_ids':changed,'staged_faces_cut_or_removed':cut,'staged_faces_retained_exactly':len(uncut),'lower_prong_guard_faces_retained':len(guard),'upper_socket_closure':{'bounds':[g['min'],g['max']],'boundary_vertices':len(ring),'plane_normals':normals,'triangles':len(captri)},'original_position_normal_uv_rows_preserved':True,'skeleton_rest_binds_original_materials_textures_preserved':True,'new_geometric_vertices':len(data['POSITION'])-len(pos),'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved':False,'scope':'User selected upper prong 1. Retained the two lower prongs and closed the upper mounting opening. Six pre-existing surface gaps and malformed strips repaired. Original 56-joint hierarchy, rest/binds, healthy shapes and textures preserved; residual deleted-chain weights reassigned locally to existing Bone_033.'})
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['holes_closed','removed_face_ids','local_reassigned_row_ids','staged_faces_cut_or_removed']},indent=2))
