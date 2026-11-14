import sys,json,copy,hashlib,struct,collections
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb,accessor,topology
ROOT=Path(__file__).parent
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/joint-restoration-v2-2026-11-11');OUT.mkdir(parents=True,exist_ok=True)
SRC=Path('D:/dev/new-mech-rpg/docs/art/moba/bombardier_beetle_m/input-review-2026-11-11/beetle-rigged-local-cleanup-STAGING.glb')
RAW=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bombardier_beetle_remeshed_25k_20261108_character.glb')
d,blob=read_glb(SRC);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];arrays={k:accessor(d,blob,a) for k,a in pr['attributes'].items()};pos=arrays['POSITION'];tri=accessor(d,blob,pr['indices']).reshape(-1,3);n=len(pos)
mapping,edges,groups,deg=topology(pos,tri);assert not groups and not deg and all(len(v)==2 for v in edges.values())
joint_names=[d['nodes'][i]['name'] for i in d['skins'][0]['joints']];removed_names=[f'Bone_{i:03}' for i in range(34,44)];removed_joints=[joint_names.index(v) for v in removed_names];body=joint_names.index('Bone_001');assert len(joint_names)==64
distal_joints=[joint_names.index(f'Bone_{i:03}') for i in list(range(34,38))+list(range(39,43))]
field=(arrays['WEIGHTS_0']*np.isin(arrays['JOINTS_0'],distal_joints)).sum(1).astype(float)
adj=np.array(list(edges));degree=np.bincount(adj.ravel(),minlength=n)
for _ in range(4):
 sums=np.zeros(n);np.add.at(sums,adj[:,0],field[adj[:,1]]);np.add.at(sums,adj[:,1],field[adj[:,0]]);next_field=.5*field+.5*sums/np.maximum(degree,1);field=next_field[mapping]
level=.250001
# Restore the source ball joints and shared shoulder armor. Protect the full
# upper-front-leg capsule independently of the generic skin-weight labels.
ball_distance=np.full(n,np.inf)
for side in [-1,1]:
 a=np.array([side*.4925,.7609,.46634]);b=np.array([side*.6602,.4465,.70737]);ab=b-a;t=np.clip(((pos-a)@ab)/(ab@ab),0,1);dist=np.linalg.norm(pos-(a+t[:,None]*ab),axis=1);ball_distance=np.minimum(ball_distance,dist)
field*=np.clip((ball_distance-.20)/.04,0,1)
protected_ball_rows=np.flatnonzero(ball_distance<.18)
protected_faces=np.flatnonzero(np.isin(tri,protected_ball_rows).any(1))
assert np.all(field[tri[protected_faces]]<=level), 'Source ball-joint faces must remain whole'

values={k:[row.copy() for row in a] for k,a in arrays.items()};cache={};kept=[];deleted_faces=0;clipped_faces=0
def cross_vertex(a,b):
 key=tuple(sorted((int(a),int(b))))
 if key in cache:return cache[key]
 t=float((level-field[a])/(field[b]-field[a]));idx=len(values['POSITION'])
 for name,ar in arrays.items():
  if name=='JOINTS_0' or name=='WEIGHTS_0':continue
  v=ar[a].astype(float)*(1-t)+ar[b].astype(float)*t
  if name=='NORMAL':v/=max(np.linalg.norm(v),1e-20)
  values[name].append(v.astype(ar.dtype))
 dense=np.zeros(64)
 for vi,factor in [(a,1-t),(b,t)]:
  np.add.at(dense,arrays['JOINTS_0'][vi],arrays['WEIGHTS_0'][vi]*factor)
 ji=np.argsort(dense)[-4:][::-1];ww=dense[ji];ww/=ww.sum();values['JOINTS_0'].append(ji.astype(arrays['JOINTS_0'].dtype));values['WEIGHTS_0'].append(ww.astype(arrays['WEIGHTS_0'].dtype));cache[key]=idx;return idx
for ft in tri:
 inside=[field[v]<=level for v in ft]
 if all(inside):kept.append(ft.tolist());continue
 if not any(inside):deleted_faces+=1;continue
 clipped_faces+=1;poly=[]
 for a,b in zip(ft,np.roll(ft,-1)):
  ia=field[a]<=level;ib=field[b]<=level
  if ia:poly.append(int(a))
  if ia!=ib:poly.append(cross_vertex(int(a),int(b)))
 for k in range(1,len(poly)-1):kept.append([poly[0],poly[k],poly[k+1]])
main=np.array(kept,dtype=np.int64);attrs={k:np.array(v,dtype=arrays[k].dtype) for k,v in values.items()};p=attrs['POSITION'];mp,ed,gg,dd=topology(p,main);assert not dd and gg
# Exact source seam copies share geometry and query the same classification.
# Preserve the largest connected body; reject only cut-created disconnected scraps.
used=set(main.ravel());neighbors=collections.defaultdict(set)
for e in ed:
 a,b=e;neighbors[a].add(b);neighbors[b].add(a)
seen=set();components=[]
for start in neighbors:
 if start in seen:continue
 pending=[start];part=set()
 while pending:
  v=pending.pop()
  if v in part:continue
  part.add(v);pending.extend(neighbors[v]-part)
 seen.update(part);components.append(part)
scrap_count=0
if len(components)>1:
 largest=max(components,key=len);discard=set().union(*(v for v in components if v is not largest));scrap_count=sum(mp[f[0]] in discard for f in main);main=np.array([f for f in main if mp[f[0]] not in discard],dtype=np.int64);mp,ed,gg,dd=topology(p,main)
assert len(gg)==2,('Expected two local socket contours',[(len(v['vertices']),v['edge_count']) for v in gg])
# At the narrow distal neck, make only the new small closure ring planar.
# Preserve every original source position, including the restored front balls.
contour_offsets=[];fitting_centers=[]
for g in gg:
 members=set(g['vertices']);nb=collections.defaultdict(set)
 for e,fs in ed.items():
  if len(fs)==1 and set(e)<=members:a,b=e;nb[a].add(b);nb[b].add(a)
 cycle=[min(members)];previous=None
 while True:
  nxt=next(v for v in nb[cycle[-1]] if v!=previous)
  if nxt==cycle[0]:break
  previous=cycle[-1];cycle.append(nxt);assert len(cycle)<=len(members)
 pts=p[cycle].astype(float);mid=pts.mean(0);_,_,basis=np.linalg.svd(pts-mid,full_matrices=False);axes=basis[:2];q=(pts-mid)@axes.T;qc=(q.min(0)+q.max(0))/2;mid=mid+qc@axes;q-=qc
 radii=(q.max(0)-q.min(0))*.48;start=np.arctan2(q[0,1]/radii[1],q[0,0]/radii[0]);area=np.sum(q[:,0]*np.roll(q[:,1],-1)-np.roll(q[:,0],-1)*q[:,1]);sign=1 if area>0 else -1
 lengths=np.linalg.norm(np.roll(q,-1,axis=0)-q,axis=1);angles=start+sign*2*np.pi*np.r_[0,np.cumsum(lengths[:-1])]/lengths.sum();rounded=mid+np.column_stack([radii[0]*np.cos(angles),radii[1]*np.sin(angles)])@axes;fitting_centers.append(mid)
 for v,c in zip(cycle,rounded):
  copies=np.where(mp==v)[0];assert np.all(copies>=n)
  for vi in copies:contour_offsets.append(float(np.linalg.norm(p[vi]-c)));p[vi]=c
used=np.unique(main);j=attrs['JOINTS_0'];w=attrs['WEIGHTS_0'];changed=[]
for vi in used:
 if not np.any((w[vi]>0)&np.isin(j[vi],removed_joints)):continue
 dense=np.zeros(64,dtype=np.float32);np.add.at(dense,j[vi],w[vi]);dense[body]+=dense[removed_joints].sum();dense[removed_joints]=0;ji=np.argsort(dense)[-4:][::-1];ww=dense[ji];ww/=ww.sum();j[vi]=ji;w[vi]=ww
 if vi<n:changed.append(int(vi))
def tessellate(points):
 # Ear clipping on the best-fit plane, retaining the contour's 3D winding.
 centered=points-points.mean(0);_,_,v=np.linalg.svd(centered,full_matrices=False);q=centered@v[:2].T
 def cross(a,b,c):
  ab=q[b]-q[a];ac=q[c]-q[a];return float(ab[0]*ac[1]-ab[1]*ac[0])
 area=sum(q[i,0]*q[(i+1)%len(q),1]-q[(i+1)%len(q),0]*q[i,1] for i in range(len(q)));sign=1 if area>0 else -1;ids=list(range(len(q)));result=[]
 while len(ids)>3:
  found=False
  for k,b in enumerate(ids):
   a=ids[k-1];c=ids[(k+1)%len(ids)]
   if sign*cross(a,b,c)<=1e-12:continue
   if any(sign*cross(a,b,x)>=-1e-12 and sign*cross(b,c,x)>=-1e-12 and sign*cross(c,a,x)>=-1e-12 for x in ids if x not in [a,b,c]):continue
   result.append([a,b,c]);ids.pop(k);found=True;break
  if not found:raise RuntimeError('Socket contour cannot be triangulated without overlaps')
 result.append(ids);return np.array(result,dtype=np.int64)
caps=[];bevel=[];cap_reports=[];extra={k:[] for k in attrs};base=len(p)
for gi,g in enumerate(gg):
 members=set(g['vertices']);assert all(int(v)==2 for v in g['degrees'])
 directed=[];raw={}
 for e,fs in ed.items():
  if len(fs)!=1 or not set(e)<=members:continue
  ft=main[fs[0]]
  for a,b in zip(ft,np.roll(ft,-1)):
   if tuple(sorted((int(mp[a]),int(mp[b]))))==e:directed.append((int(mp[a]),int(mp[b])));raw[int(mp[a])]=int(a);raw[int(mp[b])]=int(b)
 nxt=dict(directed);cycle=[directed[0][0]]
 while nxt[cycle[-1]]!=cycle[0]:cycle.append(nxt[cycle[-1]]);assert len(cycle)<=len(members)
 assert set(cycle)==members;cycle=cycle[::-1];ids=[raw[v] for v in cycle];points=p[ids].astype(float);ct=tessellate(points);normal=np.cross(points[ct[:,1]]-points[ct[:,0]],points[ct[:,2]]-points[ct[:,0]]).sum(0);normal/=np.linalg.norm(normal)
 start=base+len(extra['POSITION']);count=len(ids);center=fitting_centers[gi]
 for ring in [0,1]:
  for name,a in attrs.items():
   for vi in ids:
    value=a[vi].copy()
    if name=='POSITION' and ring==1:value=(center+.82*(value-center)-normal*.012).astype(a.dtype)
    if name=='NORMAL':
     radial=p[vi]-center;radial/=np.linalg.norm(radial);value=normal if ring==1 else normal*.8+radial*.2;value=(value/np.linalg.norm(value)).astype(a.dtype)
    extra[name].append(value)
 for i in range(count):
  nxt=(i+1)%count;bevel.extend([[start+i,start+nxt,start+count+nxt],[start+i,start+count+nxt,start+count+i]])
 caps.extend((ct+start+count).tolist());cap_reports.append({'contour_vertices':len(ids),'cap_triangles':len(ct)+2*count,'inner_disk_triangles':len(ct),'bevel_triangles':2*count,'bounds':[points.min(0).tolist(),points.max(0).tolist()]})
attrs={k:np.concatenate([a,np.array(extra[k],dtype=a.dtype)]) for k,a in attrs.items()};caps=np.array(caps,dtype=np.int64);bevel=np.array(bevel,dtype=np.int64);alltri=np.concatenate([main,caps,bevel]);_,ae,ag,ad=topology(attrs['POSITION'],alltri);assert not ag and not ad and all(len(v)==2 for v in ae.values())
used=np.unique(alltri);assert not np.any((attrs['WEIGHTS_0'][used]>1e-8)&np.isin(attrs['JOINTS_0'][used],removed_joints))
unchanged=np.setdiff1d(np.arange(n),changed)
for name,a in arrays.items():
 assert np.array_equal(attrs[name][:n] if name not in ['JOINTS_0','WEIGHTS_0'] else attrs[name][unchanged],a if name not in ['JOINTS_0','WEIGHTS_0'] else a[unchanged]),name
out_blob=blob+b'\0'*((-len(blob))%4)
def append_array(a,component,kind,target):
 global out_blob
 out_blob+=b'\0'*((-len(out_blob))%4);offset=len(out_blob);data=a.tobytes();out_blob+=data;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':target});ai=len(d['accessors']);acc={'bufferView':vi,'componentType':component,'count':len(a),'type':kind}
 if kind=='VEC3' and target==34962:acc.update(min=a.min(0).tolist(),max=a.max(0).tolist())
 d['accessors'].append(acc);return ai
attr_ids={}
for name,a in attrs.items():
 old=d['accessors'][pr['attributes'][name]];attr_ids[name]=append_array(a,old['componentType'],old['type'],34962)
main_pr=copy.deepcopy(pr);main_pr['attributes']=attr_ids;main_pr['indices']=append_array(main.astype('<u2').reshape(-1,1),5123,'SCALAR',34963)
cap_pr=copy.deepcopy(main_pr);cap_pr['indices']=append_array(caps.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);cap_pr['material']=len(d['materials']);d['materials'].append({'name':'Recessed blue joint blanking plate','pbrMetallicRoughness':{'baseColorFactor':[.02,.035,.12,1],'metallicFactor':.3,'roughnessFactor':.6}})
bevel_pr=copy.deepcopy(main_pr);bevel_pr['indices']=append_array(bevel.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);bevel_pr['material']=len(d['materials']);d['materials'].append({'name':'Local gold joint closure bevel','pbrMetallicRoughness':{'baseColorFactor':[.55,.35,.12,1],'metallicFactor':.45,'roughnessFactor':.5}});d['meshes'][0]['primitives']=[main_pr,cap_pr,bevel_pr];d['buffers'][0]['byteLength']=len(out_blob)
encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);out_blob+=b'\0'*((-len(out_blob))%4);dest=OUT/'bombardier-beetle-joints-restored-v2.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(out_blob))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(out_blob),0x004e4942)+out_blob)
for key in ['nodes','skins','scenes','scene','animations','images','textures','samplers']:assert d.get(key)==original.get(key),key
assert d['materials'][:len(original['materials'])]==original['materials'];assert out_blob[:len(blob)]==blob
report={'source_rig':str(RAW),'source_rig_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'staged_cleanup_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'decision':'Preston selected walking pair 2. Keep pairs 1, 3 and 4: six walking legs.','joint_count':64,'removed_joint_influences':removed_names,'skeleton_hierarchy_rest_binds_skins_scenes_unchanged':True,'original_binary_prefix_retained':True,'original_positions_normals_uvs_unchanged':True,'unchanged_original_skin_rows':len(unchanged),'locally_reassigned_original_skin_rows':len(changed),'changed_original_skin_row_ids':changed,'source_vertex_rows':n,'new_vertex_rows':len(attrs['POSITION'])-n,'surface_vertices_split_at_contour':base-n,'cut_classification':'Distal pair-2 chains only; retain original upper mounts as shoulder armor. Four field-smoothing steps and independent front-ball capsule protection; continuous level .250001.', 'protected_front_ball_source_rows':len(protected_ball_rows), 'protected_front_ball_source_faces':len(protected_faces),'socket_finish':'New narrow-neck contour only: two light fairing iterations and best-fit-plane closure. All original ball-joint, shoulder and body surface positions retained.','max_new_contour_finish_offset_m':max(contour_offsets),'deleted_source_triangles':deleted_faces,'clipped_source_triangles':clipped_faces,'cut_scrap_triangles_removed':scrap_count,'caps':cap_reports,'final_triangles':len(alltri),'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'weights_finite':bool(np.isfinite(attrs['WEIGHTS_0']).all()),'weight_sum_max_error':float(np.abs(attrs['WEIGHTS_0'].sum(1)-1).max()),'remaining_surface_removed_chain_weight':0,'scope':'Restore source front ball joints and shared shoulder armor damaged by v1; keep walking pair 2 removed at its own distal joint. No remesh or rerig.'}
report['socket_finish']='Only new narrow-neck contours rounded to local ellipses in their own joint planes; small gold bevels surround blue closure disks inset 12 mm. All original ball-joint, shoulder and body positions retained.'
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='changed_original_skin_row_ids'},indent=2),flush=True)
