import sys,json,copy,struct,hashlib,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/falcon_m/local-repair-v1-2026-11-13');stage=json.loads((OUT/'surface-only-verification.json').read_text());src=OUT/'falcon-surface-only-staged.glb';assert hashlib.sha256(src.read_bytes()).hexdigest()==stage['output_sha256'];d,blob=read_glb(src);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];attrs={k:accessor(d,blob,v) for k,v in pr['attributes'].items()};pos=attrs['POSITION'];tri=accessor(d,blob,pr['indices']).reshape(-1,3);fields=np.load(ROOT/'toe-cut-fields.npz');values=fields['field'];level=.10;data={k:[row.copy() for row in a] for k,a in attrs.items()};names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']];chains={names.index(f'Bone_{i:03}'):names.index(f'Bone_{parent:03}') for i,parent in [(27,9),(28,9),(37,13),(38,13)]};removed=list(chains)
parents={ci:pi for pi,n in enumerate(d['nodes']) for ci in n.get('children',[])}
for bone,parent in [(28,9),(38,13)]:assert d['nodes'][parents[d['skins'][0]['joints'][names.index(f'Bone_{bone:03}')]]]['name']==f'Bone_{parent:03}'
def skin(j,w):
 a=np.zeros(len(names));np.add.at(a,j,w);return a
def sparse(a):
 ji=np.argsort(a)[-4:][::-1];w=a[ji];w/=w.sum();return ji.astype(attrs['JOINTS_0'].dtype),w.astype('<f4')
def add(row):
 i=len(data['POSITION'])
 for k in data:data[k].append(np.asarray(row[k],dtype=attrs[k].dtype))
 return i
cache={};kept=[];uncut=[];cut=[]
for fi,ft in enumerate(tri):
 f=values[ft]-level;inside=f<=0
 if inside.all():kept.append(ft.tolist());uncut.append(fi);continue
 cut.append(fi)
 if not inside.any():continue
 poly=[]
 for i in range(3):
  k=(i+1)%3;u=int(ft[i]);v=int(ft[k])
  if inside[i]:poly.append(u)
  if inside[i]!=inside[k]:
   edge=tuple(sorted((u,v)))
   if edge not in cache:
    t=float(f[i]/(f[i]-f[k]));row={key:attrs[key][u]*(1-t)+attrs[key][v]*t for key in attrs if key not in ['JOINTS_0','WEIGHTS_0']};row['NORMAL']/=np.linalg.norm(row['NORMAL']);row['JOINTS_0'],row['WEIGHTS_0']=sparse(skin(attrs['JOINTS_0'][u],attrs['WEIGHTS_0'][u])*(1-t)+skin(attrs['JOINTS_0'][v],attrs['WEIGHTS_0'][v])*t);cache[edge]=add(row)
   poly.append(cache[edge])
 kept.extend([[poly[0],poly[i],poly[i+1]] for i in range(1,len(poly)-1)])
new=np.asarray(kept,dtype=np.int64);p=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(p,new);assert len(groups)==2 and not deg,groups
assert pos[tri[cut]][:,:,1].max()<.20 and np.abs(pos[tri[cut]][:,:,0]).min()>.45
guard=np.where((fields['protected'][tri].min(1)>.25)&(pos[tri].max(1)[:,1]<.25))[0];assert set(guard)<=set(uncut)
changed=[]
for vi in np.unique(new):
 a=skin(data['JOINTS_0'][vi],data['WEIGHTS_0'][vi])
 if a[removed].sum()>0:
  for bone,parent in chains.items():a[parent]+=a[bone];a[bone]=0
  data['JOINTS_0'][vi],data['WEIGHTS_0'][vi]=sparse(a);changed.append(int(vi))
captri=[];caps=[]
for g in groups:
 ids=set(g['vertices']);nxt={};raw={}
 for edge,fs in edges.items():
  if len(fs)!=1 or not set(edge)<=ids:continue
  ft=new[fs[0]];u,v=next((int(u),int(v)) for u,v in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[u]),int(mp[v]))))==edge);nxt[int(mp[u])]=int(mp[v]);raw[int(mp[u])]=u
 first=next(iter(nxt));order=[first];cur=nxt[first]
 while cur!=first:order.append(cur);cur=nxt[cur];assert len(order)<300
 ring=[raw[i] for i in order][::-1];pts=p[ring];center=pts.mean(0)
 # Follow the actual cut edge so nearby original toe-pad faces stay undistorted.
 pts=p[ring];normal=np.cross(pts-center,np.roll(pts,-1,axis=0)-center).sum(0);normal/=np.linalg.norm(normal);capring=[]
 for vi,point in zip(ring,pts):
  row={k:data[k][vi].copy() for k in data};row['NORMAL']=normal;capring.append(add(row))
 # Ear-clip the actual concave mounting contour; a center fan folds over its notches.
 _,_,basis=np.linalg.svd(pts-center,full_matrices=False);u=basis[0];v=np.cross(normal,u);uv=np.c_[(pts-center)@u,(pts-center)@v];order=list(range(len(ring)));local=[]
 def cross(a,b):return float(a[0]*b[1]-a[1]*b[0])
 while len(order)>3:
  ears=[]
  for ii,bb in enumerate(order):
   aa=order[ii-1];cc=order[(ii+1)%len(order)];a,b,c=uv[[aa,bb,cc]];area=cross(b-a,c-a)
   if area<=1e-12:continue
   others=[uv[k] for k in order if k not in [aa,bb,cc]]
   if any(cross(b-a,q-a)>=-1e-12 and cross(c-b,q-b)>=-1e-12 and cross(a-c,q-c)>=-1e-12 for q in others):continue
   ears.append((float(np.linalg.norm(pts[aa]-pts[cc])),ii,[aa,bb,cc]))
  assert ears,('Non-simple mounting contour',g['center'],len(order))
  _,ii,ft=min(ears);local.append(ft);order.pop(ii)
 local.append(order);captri.extend([[capring[i] for i in ft] for ft in local]);cap_pts=pts[np.asarray(local)];norms=np.cross(cap_pts[:,1]-cap_pts[:,0],cap_pts[:,2]-cap_pts[:,0]);assert np.all(norms@normal>0)
 caps.append({'bounds':[g['min'],g['max']],'center':center.tolist(),'normal':normal.tolist(),'boundary_vertices':len(ring),'closure_triangles':len(local),'minimum_projected_normal_dot':float((norms@normal/np.linalg.norm(norms,axis=1)).min()),'side':'positive-X' if center[0]>0 else 'negative-X'})
captri=np.asarray(captri,dtype=np.int64);alltri=np.concatenate([new,captri]);p=np.asarray(data['POSITION']);mp,ee,gg,dd=topology(p,alltri);contacts=[list(e) for e,fs in ee.items() if len(fs)>2];assert not gg and not dd and len(contacts)==1 and all(len(fs) in [2,4] for fs in ee.values())
used=np.unique(alltri);jj=np.asarray(data['JOINTS_0']);ww=np.asarray(data['WEIGHTS_0']);assert not np.any((ww[used]>1e-8)&np.isin(jj[used],removed))
outblob=blob+b'\0'*((-len(blob))%4)
def append(a,component,kind,target):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);offset=len(outblob);outblob+=a.tobytes();vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':a.nbytes,'target':target});ai=len(d['accessors']);entry={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if kind=='VEC3':entry['min']=a.min(0).tolist();entry['max']=a.max(0).tolist()
 d['accessors'].append(entry);return ai
for k in data:
 old=d['accessors'][pr['attributes'][k]];pr['attributes'][k]=append(np.asarray(data[k],dtype=attrs[k].dtype),old['componentType'],old['type'],34962)
pr['indices']=append(new.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr=copy.deepcopy(pr);cappr['indices']=append(captri.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr['material']=len(d['materials']);d['materials'].append({'name':'Closed rear-toe gunmetal mounting sockets','pbrMetallicRoughness':{'baseColorFactor':[.065,.069,.078,1],'metallicFactor':.52,'roughnessFactor':.48}});d['meshes'][0]['primitives'].append(cappr);d['buffers'][0]['byteLength']=len(outblob);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);outblob+=b'\0'*((-len(outblob))%4);dest=OUT/'falcon-rigged-local-repair-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(outblob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(outblob),0x004e4942)+outblob)
for k in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert d.get(k)==original.get(k)
assert d['materials'][:-1]==original['materials']
report=copy.deepcopy(stage);report.update({'surgery_input':str(src),'surgery_input_sha256':stage['output_sha256'],'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'final_triangles':len(alltri),'anatomy_review_resolved':True,'selected_toe':1,'toes_per_foot':4,'forward_toes_per_foot':3,'rear_toes_per_foot':1,'removed_skin_chains':['Bone_027','Bone_028','Bone_037','Bone_038'],'residual_influence_mapping':{names[k]:names[v] for k,v in chains.items()},'locally_reassigned_rows':len(changed),'local_reassigned_row_ids':changed,'staged_faces_cut_or_removed':cut,'staged_faces_retained_exactly':len(uncut),'retained_toe_guard_faces':len(guard),'toe_socket_closures':caps,'original_position_normal_uv_rows_preserved':True,'skeleton_rest_binds_original_materials_textures_preserved':True,'new_attribute_rows':len(data['POSITION'])-len(pos),'all_original_vertex_attribute_rows_weights_materials_skeleton_rest_binds_preserved':False,'scope':'User approved removing marked outer rear toe 1 on both feet. Retained three forward toes and one rear toe per foot; closed gunmetal mounting sockets. Chest opening and 26 malformed surface triangles repaired. Original 45-joint hierarchy/rest/binds and textures preserved; only removed-chain residual skin reassigned locally to the existing foot parents Bone_009 and Bone_013.'})
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['holes_closed','removed_face_ids','local_reassigned_row_ids','staged_faces_cut_or_removed']},indent=2))
