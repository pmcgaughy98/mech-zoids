"""Isolated front-leg reconstruction from the same model's healthy middle legs."""
import sys,json,copy,struct,hashlib,collections
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb,accessor,topology
ROOT=Path(__file__).parent/'front-leg-review-2026-11-13'
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/gold_beetle_objective/front-leg-restoration-v2-2026-11-13');OUT.mkdir(exist_ok=True)
SOURCE=Path('D:/dev/new-mech-rpg/docs/art/moba/gold_beetle_objective/repair-v1-2026-11-11/gold_beetle-objective-repaired-v1.glb')
d,blob=read_glb(SOURCE);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0]
attrs={k:accessor(d,blob,v) for k,v in pr['attributes'].items()};names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']]
oldtri=accessor(d,blob,pr['indices']).reshape(-1,3);noriginal=len(attrs['POSITION'])
data={k:[row.copy() for row in a] for k,a in attrs.items()}
ibm=accessor(d,blob,d['skins'][0]['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
bind=np.linalg.inv(ibm);nbody=names.index('Bone_001');level=.30;record=[]
def jid(n):return names.index(f'Bone_{n:03}')
def field(bones):return (attrs['WEIGHTS_0']*np.isin(attrs['JOINTS_0'],[jid(n) for n in bones])).sum(1)
def dense(j,w):
 a=np.zeros(len(names));np.add.at(a,j,w);return a
def skin(a):
 ji=np.argsort(a)[-4:][::-1];ww=a[ji];ww/=ww.sum();return ji.astype(attrs['JOINTS_0'].dtype),ww.astype(np.float32)
def add(row):
 i=len(data['POSITION'])
 for k in data:data[k].append(np.asarray(row[k],dtype=attrs[k].dtype))
 return i
def interpolate(u,v,t):
 row={k:(data[k][u]*(1-t)+data[k][v]*t) for k in data if k not in ['JOINTS_0','WEIGHTS_0']}
 normal=row['NORMAL'];row['NORMAL']=normal/max(np.linalg.norm(normal),1e-12)
 row['JOINTS_0'],row['WEIGHTS_0']=skin(dense(data['JOINTS_0'][u],data['WEIGHTS_0'][u])*(1-t)+dense(data['JOINTS_0'][v],data['WEIGHTS_0'][v])*t)
 return add(row)
def clip(tri,values,positive,cut_level=level):
 output=[];cache={};removed=[]
 for fi,ft in enumerate(tri):
  vals=values[ft]-cut_level;inside=vals>=0 if positive else vals<=0
  if inside.all():output.append(list(map(int,ft)));continue
  if not inside.any():removed.append(fi);continue
  poly=[]
  for k in range(3):
   q=(k+1)%3;u=int(ft[k]);v=int(ft[q])
   if inside[k]:poly.append(u)
   if inside[k]!=inside[q]:
    key=tuple(sorted((u,v)))
    if key not in cache:cache[key]=interpolate(u,v,float(vals[k]/(vals[k]-vals[q])))
    poly.append(cache[key])
  output.extend([[poly[0],poly[k],poly[k+1]] for k in range(1,len(poly)-1)])
 return np.asarray(output,dtype=np.int64),removed
def boundary(tri):
 pos=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(pos,tri)
 assert not deg
 loops=[]
 for g in groups:
  assert set(g['degrees'])=={2},g
  es={e:fs[0] for e,fs in edges.items() if len(fs)==1 and e[0] in set(g['vertices'])}
  nxt={};raw={}
  for e,fi in es.items():
   ft=tri[fi]
   for a,b in zip(ft,np.roll(ft,-1)):
    ma,mb=int(mp[a]),int(mp[b])
    if tuple(sorted((ma,mb)))==e:nxt[ma]=mb;raw[ma]=int(a)
  first=next(iter(nxt));order=[first];cur=nxt[first]
  while cur!=first:order.append(cur);cur=nxt[cur];assert len(order)<1000
  loops.append(np.asarray([raw[i] for i in order]))
 return loops
body=oldtri.copy();fields={}
for side,front in [('right',[11,12,13]),('left',[14,15,16])]:
 values=field(front);fields[side]=values
 # New clip vertices from the opposite leg are outside this leg's influence.
 if len(data['POSITION'])>len(values):values=np.pad(values,(0,len(data['POSITION'])-len(values)))
 body,removed=clip(body,values,False)
loops=boundary(body);assert len(loops)==2
bridges=[];donors=[]
for side,front,middle in [('right',[11,12,13],[5,6,7]),('left',[14,15,16],[8,9,10])]:
 sign=1 if side=='right' else -1
 a=next(x for x in loops if np.asarray(data['POSITION'])[x,0].mean()*sign>0)
 values=field(middle);donor,_=clip(oldtri,values,True,.45)
 # The skin field also includes a sliver of the magazine's copper frame.
 # Keep the actual leg below that frame, without cutting the gold shin plate.
 donor,_=clip(donor,level+(.620-np.asarray(data['POSITION'])[:,1]),True)
 roots=boundary(donor);assert len(roots)==1
 broot=roots[0];used=np.unique(donor)
 delta=bind[jid(front[-1]),:3,3]-bind[jid(middle[-1]),:3,3]
 posa=np.asarray(data['POSITION'])[a];posb=np.asarray(data['POSITION'])[broot]+delta
 collar_offset=posa.mean(0)+np.array([sign*.045,0,0])-posb.mean(0)
 mapping={};bone_map={jid(m):jid(f) for m,f in zip(middle,front)}
 root_tree=cKDTree(np.asarray(data['POSITION'])[broot])
 # Retain the healthy leg shape and its scale. Only the gray root collar blends
 # to the preserved recipient body's opening; the foot stays at floor height.
 for vi in used:
  row={k:data[k][vi].copy() for k in data}
  # A clipped vertex carries exactly the contour influence value.
  distance=float(root_tree.query(row['POSITION'])[0]);blend=float(np.clip(1-distance/.16,0,1))
  row['POSITION']=row['POSITION']+delta+collar_offset*blend
  weights=np.zeros(len(names))
  for j,w in zip(row['JOINTS_0'],row['WEIGHTS_0']):weights[bone_map.get(int(j),nbody)]+=w
  row['JOINTS_0'],row['WEIGHTS_0']=skin(weights)
  mapping[int(vi)]=add(row)
 donor=np.vectorize(mapping.get)(donor).astype(np.int64);donors.append(donor)
 b=np.asarray([mapping[int(i)] for i in broot])[::-1]
 pos=np.asarray(data['POSITION'])
 # Match the two ordered contours geometrically; preserve each boundary edge.
 b=np.roll(b,-int(np.argmin(np.linalg.norm(pos[b]-pos[a[0]],axis=1))))
 def progress(r):
  lengths=np.linalg.norm(pos[np.roll(r,-1)]-pos[r],axis=1);return np.r_[0,np.cumsum(lengths)]/lengths.sum()
 pa=progress(a);pb=progress(b);i=j=0;faces=[]
 while i<len(a) or j<len(b):
  if j==len(b) or (i<len(a) and pa[i+1]<=pb[j+1]):
   faces.append([int(a[(i+1)%len(a)]),int(a[i%len(a)]),int(b[j%len(b)])]);i+=1
  else:
   faces.append([int(a[i%len(a)]),int(b[j%len(b)]),int(b[(j+1)%len(b)])]);j+=1
 bridges.extend(faces)
 record.append({'side':side,'source_healthy_middle_bones':[f'Bone_{v:03}' for v in middle],
  'recipient_native_front_bones':[f'Bone_{v:03}' for v in front],
  'healthy_leg_translation_m':delta.tolist(),'gray_root_blend_offset_m':collar_offset.tolist(),
  'retained_body_contour_vertices':len(a),'donor_contour_vertices':len(b),
  'healthy_leg_triangles':len(donor),'bridge_triangles':len(faces)})
alltri=np.concatenate([body,*donors,np.asarray(bridges)]);pos=np.asarray(data['POSITION'],dtype=np.float32)
mp,edges,groups,deg=topology(pos,alltri)
assert not groups and not deg,(groups,deg)
areas=np.linalg.norm(np.cross(pos[alltri[:,1]]-pos[alltri[:,0]],pos[alltri[:,2]]-pos[alltri[:,0]]),axis=1)/2
assert areas.min()>1e-12,float(areas.min())
# Ensure an oriented closed surface at every new ordinary edge.
bad=[]
for edge,fs in edges.items():
 if len(fs)!=2:continue
 dirs=[]
 for fi in fs:
  ft=mp[alltri[fi]]
  dirs.extend(int(a<b) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(a),int(b))))==edge)
 if sum(dirs)!=1:bad.append(edge)
assert not bad,('Inconsistent winding',bad[:10])
outblob=blob+b'\0'*((-len(blob))%4)
def append(array,component,kind,target):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);offset=len(outblob);raw=array.tobytes();outblob+=raw
 view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target})
 ai=len(d['accessors']);a={'bufferView':view,'componentType':component,'count':len(array),'type':kind}
 if kind=='VEC3' and array.shape[1]==3:a['min']=array.min(0).tolist();a['max']=array.max(0).tolist()
 d['accessors'].append(a);return ai
for key in data:
 old=d['accessors'][pr['attributes'][key]];array=np.asarray(data[key],dtype=attrs[key].dtype)
 pr['attributes'][key]=append(array,old['componentType'],old['type'],34962)
pr['indices']=append(np.concatenate([body,*donors]).astype('<u2').reshape(-1,1),5123,'SCALAR',34963)
collar=copy.deepcopy(pr);collar['indices']=append(np.asarray(bridges,dtype='<u2').reshape(-1,1),5123,'SCALAR',34963)
collar['material']=len(d['materials']);d['materials'].append({'name':'Local gray shoulder collar','pbrMetallicRoughness':{'baseColorFactor':[.075,.08,.09,1],'metallicFactor':.65,'roughnessFactor':.48}})
d['meshes'][0]['primitives'].append(collar);d['buffers'][0]['byteLength']=len(outblob)
for key in ['nodes','skins','images','textures','samplers','scenes','scene','animations']:assert d.get(key)==original.get(key),key
assert d['materials'][:-1]==original['materials']
encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);outblob+=b'\0'*((-len(outblob))%4)
dest=OUT/'gold_beetle-front-legs-restored-v2.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(outblob))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(outblob),0x004e4942)+outblob)
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'triangles':len(alltri),'joint_count':23,'boundary_edges':0,'collapsed_triangles':0,'minimum_triangle_area_m2':float(areas.min()),'over_shared_edges':sum(len(fs)>2 for fs in edges.values()),'legs':record,'original_vertex_rows':noriginal,'new_vertex_rows':len(pos)-noriginal,'unchanged_original_attribute_rows':True,'original_skeleton_hierarchy_rest_binds_preserved':True,'original_materials_and_textures_preserved':True,'added_material':'Local gray shoulder collar','intact_pre_remesh_available':False,'scope':'Both fused front legs replaced from the same model healthy middle legs. Six walking legs retained. Original front chains preserved; donor weights remapped locally.'}
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
