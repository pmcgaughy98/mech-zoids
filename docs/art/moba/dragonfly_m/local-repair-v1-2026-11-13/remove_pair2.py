import sys,json,copy,struct,hashlib,collections,shutil
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13');cfg=json.loads((ROOT/'input-audit.json').read_text());d,blob=read_glb(cfg['source']);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];attrs={k:accessor(d,blob,v) for k,v in pr['attributes'].items()};pos=attrs['POSITION'];originaltri=accessor(d,blob,pr['indices']).reshape(-1,3);comps=json.loads((ROOT/'face-components.json').read_text());flaps=[f for c in comps if c['count']==1 for f in c['faces']];tri=np.delete(originaltri,flaps,axis=0);fields=np.load(ROOT/'cut-fields.npz');values=fields['field'];level=.25;data={k:[row.copy() for row in a] for k,a in attrs.items()};names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']];removed_bones=[names.index(f'Bone_{i:03}') for i in range(22,28)];body=names.index('Bone_001')
parents={ci:pi for pi,n in enumerate(d['nodes']) for ci in n.get('children',[])}
assert all(d['nodes'][parents[d['skins'][0]['joints'][names.index(name)]]]['name']=='Bone_001' for name in ['Bone_024','Bone_027'])
def skin(j,w):
 a=np.zeros(len(names));np.add.at(a,j,w);return a
def sparse(a):
 ji=np.argsort(a)[-4:][::-1];w=a[ji];w/=w.sum();return ji.astype(attrs['JOINTS_0'].dtype),w.astype('<f4')
def add(row):
 i=len(data['POSITION'])
 for k in data:data[k].append(np.asarray(row[k],dtype=attrs[k].dtype))
 return i
cache={};kept=[]
for ft in tri:
 f=values[ft]-level;inside=f<=0
 if inside.all():kept.append(ft.tolist());continue
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
new=np.asarray(kept,dtype=np.int64);p=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(p,new);adj=[set() for _ in new]
for fs in edges.values():
 if len(fs)==2:a,b=fs;adj[a].add(b);adj[b].add(a)
seen=set();parts=[]
for start in range(len(new)):
 if start in seen:continue
 stack=[start];part=set()
 while stack:
  f=stack.pop()
  if f in part:continue
  part.add(f);stack.extend(adj[f]-part)
 seen.update(part);parts.append(sorted(part))
largest=max(parts,key=len);scraps=[part for part in parts if part is not largest];new=new[largest];mp,edges,groups,deg=topology(p,new);assert len(groups)==2 and all(g['edge_count']>40 for g in groups),groups
# Remove only residual skin from the deleted chains; keep the original skeleton.
changed=[]
for vi in np.unique(new):
 a=skin(data['JOINTS_0'][vi],data['WEIGHTS_0'][vi])
 if a[removed_bones].sum()>0:
  a[body]+=a[removed_bones].sum();a[removed_bones]=0;data['JOINTS_0'][vi],data['WEIGHTS_0'][vi]=sparse(a);changed.append(int(vi))
captri=[];caps=[]
for g in groups:
 ids=set(g['vertices']);nxt={};raw={}
 for edge,fs in edges.items():
  if len(fs)!=1 or not set(edge)<=ids:continue
  ft=new[fs[0]];u,v=next((int(u),int(v)) for u,v in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[u]),int(mp[v]))))==edge);nxt[int(mp[u])]=int(mp[v]);raw[int(mp[u])]=u
 first=next(iter(nxt));order=[first];cur=nxt[first]
 while cur!=first:order.append(cur);cur=nxt[cur];assert len(order)<300
 ring=[raw[i] for i in order][::-1];points=p[ring];center=points.mean(0)
 # Round the newly cut contour, without moving any original source vertex.
 _,_,basis=np.linalg.svd(points-center,full_matrices=False);uv=(points-center)@basis[:2].T;radii=np.max(abs(uv),axis=0);angles=np.arctan2(uv[:,1]/radii[1],uv[:,0]/radii[0]);smooth=center+np.c_[np.cos(angles)*radii[0],np.sin(angles)*radii[1]]@basis[:2]
 for vi,point in zip(ring,smooth):
  aliases=np.where(mp==mp[vi])[0];assert np.all(aliases>=len(pos)),('Protected original contour vertex',vi)
  for alias in aliases:data['POSITION'][alias]=point.astype('<f4');p[alias]=point
 points=p[ring];normal=np.cross(points-np.roll(points,1,axis=0),np.roll(points,-1,axis=0)-points).sum(0);normal/=np.linalg.norm(normal);direction=np.array([np.sign(center[0]),0,0]);center_in=center-direction*.008;inner=[]
 for vi,point in zip(ring,points):
  row={k:data[k][vi].copy() for k in data};row['POSITION']=center_in+(point-center)*.82;row['NORMAL']=direction;inner.append(add(row))
 a=np.mean([skin(data['JOINTS_0'][i],data['WEIGHTS_0'][i]) for i in ring],axis=0);row={k:data[k][ring[0]].copy() for k in data};row['POSITION']=center-direction*.012;row['NORMAL']=direction;row['JOINTS_0'],row['WEIGHTS_0']=sparse(a);ci=add(row)
 for i in range(len(ring)):
  k=(i+1)%len(ring);captri.extend([[ring[i],ring[k],inner[k]],[ring[i],inner[k],inner[i]],[inner[i],inner[k],ci]])
 caps.append({'bounds':[g['min'],g['max']],'border_vertices':len(ring)})
captri=np.asarray(captri,dtype=np.int64);alltri=np.concatenate([new,captri]);p=np.asarray(data['POSITION']);mp,ee,gg,dd=topology(p,alltri);assert not gg and not dd and all(len(fs)==2 for fs in ee.values())
used=np.unique(alltri);jj=np.asarray(data['JOINTS_0']);ww=np.asarray(data['WEIGHTS_0']);assert not np.any((ww[used]>1e-8)&np.isin(jj[used],removed_bones))
outblob=blob+b'\0'*((-len(blob))%4)
def append(a,component,kind,target):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);offset=len(outblob);raw=a.tobytes();outblob+=raw;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target});ai=len(d['accessors']);entry={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if kind=='VEC3':entry['min']=a.min(0).tolist();entry['max']=a.max(0).tolist()
 d['accessors'].append(entry);return ai
for k in data:
 old=d['accessors'][pr['attributes'][k]];pr['attributes'][k]=append(np.asarray(data[k],dtype=attrs[k].dtype),old['componentType'],old['type'],34962)
pr['indices']=append(new.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr=copy.deepcopy(pr);cappr['indices']=append(captri.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cappr['material']=len(d['materials']);d['materials'].append({'name':'Recessed teal leg sockets','pbrMetallicRoughness':{'baseColorFactor':[.025,.13,.14,1],'metallicFactor':.3,'roughnessFactor':.5}});d['meshes'][0]['primitives'].append(cappr);d['buffers'][0]['byteLength']=len(outblob);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);outblob+=b'\0'*((-len(outblob))%4);dest=OUT/'dragonfly-rigged-local-repair-v1.glb'
stage=json.loads((OUT/'topology-staging-verification.json').read_text());archive=OUT/'dragonfly-topology-only-staged.glb'
if not archive.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==stage['output_sha256']:shutil.copy2(dest,archive)
dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(outblob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(outblob),0x004e4942)+outblob)
for k in ['nodes','skins','images','textures','samplers','scenes','scene','animations']:assert d.get(k)==original.get(k)
assert d['materials'][:-1]==original['materials']
report={'source':cfg['source'],'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'joint_count':46,'before_triangles':len(originaltri),'final_triangles':len(alltri),'removed_flaps':15,'selected_pair':2,'remaining_pairs':[1,3,4],'remaining_legs':6,'removed_skin_chains':[f'Bone_{i:03}' for i in range(22,28)],'residual_influence_reassigned_to':'Bone_001','locally_reassigned_rows':len(changed),'detached_tip_scrap_triangles':sum(len(s) for s in scraps),'closures':caps,'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'skeleton_rest_binds_original_materials_textures_preserved':True,'original_position_normal_uv_rows_preserved':True,'new_material':'Recessed teal leg sockets','scope':'User selected pair 2. Removed outer-front pair, retained front/middle/rear pairs and four wings. Local sockets and 15 malformed flaps repaired.'};(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
