from diagnose import *
import copy,hashlib
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/base-reshape-v2-2026-11-10')
SOURCE=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10/cobra-rigged-local-repair-v1.glb')
d,blob=read_glb(SOURCE);old=copy.deepcopy(d);prim=d['meshes'][0]['primitives'][0];attrs=prim['attributes'];p=accessor(d,blob,attrs['POSITION']);n=accessor(d,blob,attrs['NORMAL']);uv=accessor(d,blob,attrs['TEXCOORD_0']);j=accessor(d,blob,attrs['JOINTS_0']);w=accessor(d,blob,attrs['WEIGHTS_0']);tri=accessor(d,blob,prim['indices']).reshape(-1,3);nj=len(d['skins'][0]['joints']);cx=.06688863
def vertex(i):
 weights=np.zeros(nj);np.add.at(weights,j[i],w[i]);return {'p':p[i].astype(float),'n':n[i].astype(float),'uv':uv[i].astype(float),'w':weights}
verts=[vertex(i) for i in range(len(p))]
def mix(a,b,t):return {k:a[k]*(1-t)+b[k]*t for k in a}
def split(poly,fn):
 inside=[];outside=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=fn(a['p']);db=fn(b['p']);ia=da>=-1e-9;ib=db>=-1e-9
  (inside if ia else outside).append(a)
  if ia!=ib:
   q=mix(a,b,float(da/(da-db)));inside.append(q);outside.append(q)
 return inside,outside
def triangulate(poly):return [[poly[0],poly[i],poly[i+1]] for i in range(1,len(poly)-1)]
planes=[lambda v:v[0]-cx,lambda v:.62-v[1],lambda v:v[2]-.32]
outside=[];donor=[]
for ids in tri:
 original=[verts[i] for i in ids];poly=original
 for fn in planes:
  if not poly:break
  poly,rejected=split(poly,fn);outside.extend(triangulate(rejected))
 poly=original
 for fn in [lambda v:cx-v[0],planes[1],planes[2]]:
  if not poly:break
  poly,_=split(poly,fn)
 for t in triangulate(poly):
  mt=[]
  for v in t:
   v={k:a.copy() for k,a in v.items()};v['p'][0]=2*cx-v['p'][0];v['n'][0]*=-1;mt.append(v)
  donor.append(list(reversed(mt)))
def key(v):return tuple(np.round(v['p'],6))
def boundary(faces):
 edges=collections.defaultdict(list)
 for fi,t in enumerate(faces):
  for ei in range(3):
   a,b=t[ei],t[(ei+1)%3];ka,kb=key(a),key(b)
   if ka==kb:continue
   edges[tuple(sorted((ka,kb)))].append((fi,ei,a,b))
 return [v[0] for v in edges.values() if len(v)==1]
de=boundary(donor);oe=boundary(outside)
assert len(de)>8 and len(oe)>8,(len(de),len(oe))
# Order the donor perimeter; its winding is opposite the retained body's hole.
by_start={key(a):(fi,ei,a,b) for fi,ei,a,b in de};ordered=[];edge=de[0];start=key(edge[2])
for _ in range(len(de)):
 ordered.append(edge);end=key(edge[3]);edge=by_start[end]
assert key(edge[2])==start and len({key(e[2]) for e in ordered})==len(de)
starts=np.array([e[2]['p'] for e in ordered]);ends=np.array([e[3]['p'] for e in ordered]);vec=ends-starts;length=np.linalg.norm(vec,axis=1);cum=np.r_[0,np.cumsum(length)];total=cum[-1]
def project(point):
 t=np.clip(np.sum((point-starts)*vec,axis=1)/(length*length),0,1);q=starts+t[:,None]*vec;idx=int(np.argmin(np.sum((q-point)**2,axis=1)));return float(cum[idx]+t[idx]*length[idx]),q[idx],float(np.linalg.norm(q[idx]-point))
def donor_at(s):
 s=s%total;idx=min(int(np.searchsorted(cum,s,side='right')-1),len(ordered)-1);t=(s-cum[idx])/length[idx];return mix(ordered[idx][2],ordered[idx][3],t)
outer_map={};anchor=[];max_snap=0
for _,_,a,b in oe:
 for v in [a,b]:
  k=key(v)
  if k in outer_map:continue
  s,q,dist=project(v['p']);outer_map[k]=(s,q);anchor.append((s,v));max_snap=max(max_snap,dist)
assert max_snap<.16,max_snap
# Preserve perimeter order when a tiny jagged source edge would project back
# along the donor curve. This prevents locally folded stitch triangles.
from scipy.optimize import isotonic_regression
outer_by_start={key(a):(fi,ei,a,b) for fi,ei,a,b in oe};ordered_outer=[];edge=oe[0]
for _ in range(len(oe)):
 ordered_outer.append(edge);edge=outer_by_start[key(edge[3])]
assert len({key(e[2]) for e in ordered_outer})==len(oe)
arc=np.array([outer_map[key(e[2])][0] for e in ordered_outer]);unwrapped=np.unwrap(arc/total*2*np.pi)*total/(2*np.pi);sign=1 if unwrapped[-1]>unwrapped[0] else -1;step=3e-6
fitted=isotonic_regression(sign*unwrapped-np.arange(len(arc))*step,increasing=True).x+np.arange(len(arc))*step
for e,s in zip(ordered_outer,sign*fitted):outer_map[key(e[2])]=(float(s%total),donor_at(s)['p'])
def near_delta(a,b):return (b-a+total/2)%total-total/2
# Combine both sets of perimeter samples. Snap retained cut vertices to the
# donor contour and subdivide both meshes at precisely the same positions.
samples=sorted(set(round(float(s%total),9) for s in list(cum[:-1])+[v[0] for v in outer_map.values()]))
anchor_sa=np.array([outer_map[key(a)][0] for _,_,a,b in oe]);anchor_sb=np.array([outer_map[key(b)][0] for _,_,a,b in oe]);anchor_span=(anchor_sb-anchor_sa+total/2)%total-total/2
def outer_at(s):
 part=(s-anchor_sa+total/2)%total-total/2;t=np.divide(part,anchor_span,out=np.full_like(part,-10),where=abs(anchor_span)>1e-10);valid=np.where((t>=-1e-6)&(t<=1+1e-6))[0];assert len(valid),('No anchor',s)
 idx=int(valid[np.argmin(abs(anchor_span[valid]))]);return mix(oe[idx][2],oe[idx][3],float(np.clip(t[idx],0,1)))
canonical={s:donor_at(s) for s in samples}
for s,v in canonical.items():v['w']=outer_at(s)['w']
def sample_between(sa,sb):
 span=near_delta(sa,sb);items=[]
 for s in samples:
  t=near_delta(sa,s)/span if abs(span)>1e-10 else -1
  if 1e-6<t<1-1e-6:items.append((t,s))
 return sorted(items)
def nearest_sample(s):return min(samples,key=lambda q:abs(near_delta(s,q)))
def rebuild(faces,bound_edges,is_outer):
 lookup={(fi,ei):(a,b) for fi,ei,a,b in bound_edges};result=[]
 for fi,t in enumerate(faces):
  poly=[];modified=False
  for ei,a in enumerate(t):
   b=t[(ei+1)%3];ka=key(a)
   if is_outer and ka in outer_map:
    s=nearest_sample(outer_map[ka][0]);a={k:v.copy() for k,v in a.items()};a['p']=canonical[s]['p'];a['w']=canonical[s]['w'];modified=True
   elif not is_outer:
    sa,q,dist=project(a['p'])
    if dist<2e-6:
     s=nearest_sample(sa);a={k:v.copy() for k,v in a.items()};a['p']=canonical[s]['p'];a['w']=canonical[s]['w'];modified=True
    elif dist<.10:
     # Preserve donor weights inside, fade to the retained ring's weights.
     anchor_w=outer_at(sa)['w'];blend=(1-dist/.10)**2;a={k:v.copy() for k,v in a.items()};a['w']=a['w']*(1-blend)+anchor_w*blend
   poly.append(a)
   if (fi,ei) in lookup:
    oa,ob=lookup[(fi,ei)]
    sa=outer_map[key(oa)][0] if is_outer else project(oa['p'])[0];sb=outer_map[key(ob)][0] if is_outer else project(ob['p'])[0]
    for tt,s in sample_between(sa,sb):
     v=mix(oa,ob,tt) if is_outer else donor_at(s);v['p']=canonical[s]['p'];v['w']=canonical[s]['w'];poly.append(v);modified=True
  if len(poly)==3:result.append(poly)
  else:
   center={k:sum(v[k] for v in poly)/len(poly) for k in poly[0]}
   result.extend([[center,poly[i],poly[(i+1)%len(poly)]] for i in range(len(poly))])
 return result
newfaces=rebuild(outside,oe,True)+rebuild(donor,de,False)
# Serialize per-corner rows, preserving UV seams and a coherent shared rig.
rows=[];indices=[];dedup={};dropped=0
def original_signature(v):return b''.join(v[k].astype('<f4').tobytes() for k in ['p','n','uv','w'])
original_rows={original_signature(v):i for i,v in enumerate(verts)};reused_original_rows=set()
for t in newfaces:
 pp=np.array([v['p'] for v in t]);area=np.linalg.norm(np.cross(pp[1]-pp[0],pp[2]-pp[0]))
 if area<1e-11:dropped+=1;continue
 ids=[]
 for v in t:
  weights=v['w'];js=np.argsort(weights)[-4:][::-1];ws=weights[js];ws=ws/ws.sum();nn=v['n'];nn=nn/max(np.linalg.norm(nn),1e-10)
  original_index=original_rows.get(original_signature(v))
  if original_index is not None:
   oi=original_index;row=(p[oi],n[oi],uv[oi],j[oi],w[oi]);reused_original_rows.add(oi)
  else:row=(v['p'].astype('<f4'),nn.astype('<f4'),v['uv'].astype('<f4'),js.astype('u1'),ws.astype('<f4'))
  k=b''.join(x.tobytes() for x in row)
  if k not in dedup:dedup[k]=len(rows);rows.append(row)
  ids.append(dedup[k])
 indices.append(ids)
pos=np.array([r[0] for r in rows]);idx=np.array(indices,dtype='<u4');mapping,edges,groups,deg=topology(pos,idx)
tiny_or_duplicate=[];seen=set()
for fi,t in enumerate(idx):
 k=tuple(sorted(mapping[t]))
 if len(set(k))<3 or k in seen:tiny_or_duplicate.append(fi)
 else:seen.add(k)
if tiny_or_duplicate:
 idx=np.delete(idx,tiny_or_duplicate,axis=0);mapping,edges,groups,deg=topology(pos,idx)
micro_closures=[]
if groups and not any(len(v)>2 for v in edges.values()):
 for g in groups:
  ids=set(g['vertices']);assert len(ids)==3 and g['edge_count']==3 and np.linalg.norm(np.array(g['max'])-g['min'])<.003
  edge,fs=next((e,fs) for e,fs in edges.items() if set(e)<=ids and len(fs)==1);face=idx[fs[0]]
  a,b=next((int(a),int(b)) for a,b in zip(face,np.roll(face,-1)) if tuple(sorted((int(mapping[a]),int(mapping[b]))))==edge)
  missing=next(iter(ids-{int(mapping[a]),int(mapping[b])}));c=next(int(v) for t in idx for v in t if mapping[v]==missing)
  micro_closures.append([b,a,c])
 idx=np.concatenate([idx,np.array(micro_closures,dtype=idx.dtype)]);mapping,edges,groups,deg=topology(pos,idx)
stats={'vertices':len(pos),'triangles':len(idx),'boundary_edges':sum(len(v)==1 for v in edges.values()),'over_shared_edges':sum(len(v)>2 for v in edges.values()),'collapsed':len(deg),'boundary_components':[{k:v for k,v in g.items() if k!='vertices'} for g in groups]}
(OUT/'patch-topology.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2),flush=True)
if any(len(v)>2 for v in edges.values()):print('OVER_SHARED',[(list(e),fs,pos[list(e)].tolist()) for e,fs in edges.items() if len(fs)>2],flush=True)
assert not groups and not deg and all(len(v)==2 for v in edges.values()),'Patch is not closed'
binary=blob
def add_accessor(data,component,kind,target,position=False):
 global binary
 binary+=b'\0'*((-len(binary))%4);offset=len(binary);raw=data.tobytes();binary+=raw;view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target});a={'bufferView':view,'componentType':component,'count':len(data),'type':kind}
 if position:a.update(min=data.min(0).tolist(),max=data.max(0).tolist())
 ai=len(d['accessors']);d['accessors'].append(a);return ai
for col,name,component,kind in [(0,'POSITION',5126,'VEC3'),(1,'NORMAL',5126,'VEC3'),(2,'TEXCOORD_0',5126,'VEC2'),(3,'JOINTS_0',5121,'VEC4'),(4,'WEIGHTS_0',5126,'VEC4')]:prim['attributes'][name]=add_accessor(np.array([r[col] for r in rows]),component,kind,34962,name=='POSITION')
prim['indices']=add_accessor(idx.reshape(-1,1),5125,'SCALAR',34963);d['buffers'][0]['byteLength']=len(binary);encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4);target=OUT/'cobra-rigged-base-reshape-v2.glb';target.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary)
for k in ['nodes','skins','materials','textures','images','samplers','animations']:assert d.get(k)==old.get(k)
report={'method':'Replace only left lower-body patch with mirrored healthy right-side geometry/UVs; conform and resample cut ring; transfer existing rig weights locally with boundary fade. Rejected radial-shrink test is not delivered.','source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'patch_region_gltf':{'left_x_min':cx,'height_max':.62,'front_z_min':.32},'retained_cut_ring_max_snap_m':max_snap,'source_triangle_count':len(tri),'retained_outside_triangles':len(outside),'mirrored_patch_triangles':len(donor),'original_vertex_rows_reused_byte_exact':len(reused_original_rows),'removed_degenerate_subtriangles':dropped,'sub_3mm_seam_corner_closures':micro_closures,'skeleton_nodes_bind_transforms_materials_textures_unchanged':True,'local_weights_transferred':True,'binary_original_prefix_preserved':binary[:len(blob)]==blob,'topology':stats}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
