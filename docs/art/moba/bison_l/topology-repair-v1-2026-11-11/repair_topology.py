import sys
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_bison_remeshed_25k_20261108_character.glb')
import copy,hashlib,itertools
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/bison_l/topology-repair-v1-2026-11-11')
OUT.mkdir(parents=True,exist_ok=True)
doc,blob=read_glb(SOURCE);original=copy.deepcopy(doc)
prim=doc['meshes'][0]['primitives'][0];pos=accessor(doc,blob,prim['attributes']['POSITION']);uv=accessor(doc,blob,prim['attributes']['TEXCOORD_0']);norm=accessor(doc,blob,prim['attributes']['NORMAL']);tri=accessor(doc,blob,prim['indices']).reshape(-1,3)
mapping,edges,groups,deg=topology(pos,tri)
remove=[];patches=[]
for g in groups:
 ids=set(g['vertices'])
 if len(ids)==3 and g['edge_count']==2:
  common=[(k,v) for k,v in edges.items() if set(k)<=ids and len(v)==3]
  assert len(common)==1
  fins=[i for i in common[0][1] if set(mapping[tri[i]])==ids]
  if not fins:
   root_edge=common[0][0]
   candidates=[]
   for seed in common[0][1]:
    pending=[seed];component=set()
    while pending and len(component)<100:
     f=pending.pop()
     if f in component:continue
     component.add(f);ft=mapping[tri[f]]
     for a,b in zip(ft,np.roll(ft,-1)):
      edge=tuple(sorted((int(a),int(b))))
      if edge!=root_edge:pending.extend(x for x in edges[edge] if x not in component)
    if not pending:candidates.append(component)
   assert candidates,('No local flap',g)
   component=min(candidates,key=len)
   print('TESSELLATED FIN',len(component),sorted(component),flush=True)
   fins=sorted(component)
  assert fins
  remove.extend(fins)
 elif len(ids)==4 and g['edge_count']==4 and g['degrees']=={2:4}:
  # A thin doubled-back flap forms two sides of each four-edge opening.
  # Remove that flap first, then close the resulting triangular opening.
  boundary_faces=collections.Counter(f for e,fs in edges.items() if set(e)<=ids and len(fs)==1 for f in fs)
  fins=[f for f,c in boundary_faces.items() if c==2 and set(mapping[tri[f]])<=ids]
  assert len(fins)==1,('Ambiguous opening',fins)
  remove.append(fins[0])
  hole_edges={e:[f for f in fs if f!=fins[0]] for e,fs in edges.items() if set(e)<=ids}
  directed=[];raws=collections.defaultdict(list)
  for edge,fs in hole_edges.items():
   if len(fs)==1:
    face=tri[fs[0]]
    for a,b in zip(face,np.roll(face,-1)):
     if tuple(sorted((int(mapping[a]),int(mapping[b]))))==edge:
      directed.append((int(mapping[a]),int(mapping[b])));raws[int(mapping[a])].append(int(a));raws[int(mapping[b])].append(int(b))
  cycle=[directed[0][0]]
  for _ in range(2):cycle.append(next(b for a,b in directed if a==cycle[-1]))
  assert next(b for a,b in directed if a==cycle[-1])==cycle[0]
  # Reverse the bordering surface winding to close the opening outward.
  cycle=list(reversed(cycle))
  # Retain existing attributes; choose a compact existing UV island for the patch.
  options=itertools.product(*(sorted(set(raws[v])) for v in cycle))
  raw=list(min(options,key=lambda ids:sum(float(np.linalg.norm(uv[ids[i]]-uv[ids[(i+1)%3]])) for i in range(3))))
  if set(cycle)=={26742,26744,26956}:
   # The nearest bordering island samples the orange vent texture. Include
   # all existing corner copies at these exact positions; the compact grey
   # island gives the local strut finish without changing any UV data.
   options=itertools.product(*(np.where(mapping==v)[0].tolist() for v in cycle))
   raw=list(min(options,key=lambda ids:sum(float(np.linalg.norm(uv[ids[i]]-uv[ids[(i+1)%3]])) for i in range(3))))
  seam_spread=max(float(np.linalg.norm(uv[a]-uv[b])) for v in cycle for a in raws[v] for b in raws[v])
  print('Hole',cycle,'UV corner split spread',seam_spread,flush=True)
  candidates=[[raw]]
  def score(ts):
   pts=pos[np.array(ts)];cross=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);length=np.linalg.norm(cross,axis=1);ns=cross/length[:,None];expected=norm[np.array(ts)].mean(1);expected/=np.linalg.norm(expected,axis=1)[:,None]
   return float((ns*expected).sum()) if min(length)>1e-10 else -100
  chosen=max(candidates,key=score);assert score(chosen)>.25,('Bad patch normals',score(chosen))
  patches.append({'boundary_vertices':cycle,'raw_indices':raw,'new_triangles':chosen,'uv_seam_spread':seam_spread,'bounds':[g['min'],g['max']],'normal_alignment_score':score(chosen)})
 elif len(ids)==3 and g['edge_count']==3:
  enclosed=[i for i,t in enumerate(mapping[tri]) if set(t)==ids]
  if enclosed:
   assert len(enclosed)==1
   assert all(len(edges[e])==1 for e in edges if set(e)<=ids)
   remove.extend(enclosed) # An isolated malformed triangle, not a hole.
 elif len(ids)==5 and g['edge_count']==4:
  roots=[e for e,fs in edges.items() if set(e)<=ids and len(fs)==3]
  assert len(roots)==2,('Unexpected tessellated fin roots',roots)
  root_edges=set(roots);candidates=[]
  for seed in set(f for e in roots for f in edges[e]):
   pending=[seed];component=set()
   while pending and len(component)<100:
    f=pending.pop()
    if f in component:continue
    component.add(f);ft=mapping[tri[f]]
    for a,b in zip(ft,np.roll(ft,-1)):
     edge=tuple(sorted((int(a),int(b))))
     if edge not in root_edges:pending.extend(x for x in edges[edge] if x not in component)
   if not pending:candidates.append(component)
  assert candidates,('No local fin',g)
  component=set().union(*(c for c in candidates if len(c)<10 and all(set(mapping[tri[f]])<=ids for f in c)))
  assert 1<len(component)<10
  remove.extend(component)
 elif len(ids)==4 and g['edge_count']==3:
  faces=set(f for e,fs in edges.items() if set(e)<=ids for f in fs)
  flaps=[f for f in faces if set(mapping[tri[f]])<=ids]
  assert len(flaps)==2
  remove.extend(flaps)
 else:raise RuntimeError(('Unhandled boundary',g))
assert len(patches)==2
remove=sorted(set(remove));print('REMOVAL COUNT',len(remove),flush=True)
keep=np.ones(len(tri),dtype=bool);keep[remove]=False
newtri=np.concatenate([tri[keep],np.array([t for p in patches for t in p['new_triangles']],dtype=tri.dtype)])
_,after_edges,after_groups,after_deg=topology(pos,newtri)
for g in after_groups:
 print('REMAINING',g,flush=True)
 ids=set(g['vertices']);assert len(ids)==3 and g['edge_count']==3
 edge,fs=next((e,fs) for e,fs in after_edges.items() if set(e)<=ids and len(fs)==1);face=newtri[fs[0]]
 a,b=next((int(a),int(b)) for a,b in zip(face,np.roll(face,-1)) if tuple(sorted((int(mapping[a]),int(mapping[b]))))==edge);missing=next(iter(ids-{int(mapping[a]),int(mapping[b])}));options=[int(v) for t in newtri for v in t if mapping[v]==missing]
 c=options[0];order=[int(mapping[b]),int(mapping[a]),missing];raw_options=[np.where(mapping==v)[0].tolist() for v in order]
 chosen=list(min(itertools.product(*raw_options),key=lambda ids:sum(float(np.linalg.norm(uv[ids[i]]-uv[ids[(i+1)%3]])) for i in range(3))));print('FINAL PATCH UV',chosen,uv[chosen].tolist(),flush=True);pts=pos[chosen];cross=np.cross(pts[1]-pts[0],pts[2]-pts[0]);alignment=float(np.dot(cross/np.linalg.norm(cross),norm[chosen].mean(0)));assert alignment>.25,alignment
 newtri=np.concatenate([newtri,np.array([chosen],dtype=newtri.dtype)]);patches.append({'boundary_vertices':sorted(ids),'new_triangles':[chosen],'bounds':[g['min'],g['max']],'normal_alignment_score':alignment,'note':'Local triangular opening after malformed-flap cleanup.'})
_,after_edges,after_groups,after_deg=topology(pos,newtri)
closed_fin_faces=set()
for root_edge,fs in after_edges.items():
 if len(fs)<=2:continue
 for seed in fs:
  pending=[seed];component=set()
  while pending and len(component)<500:
   f=pending.pop()
   if f in component:continue
   component.add(f);ft=mapping[newtri[f]]
   for a,b in zip(ft,np.roll(ft,-1)):
    edge=tuple(sorted((int(a),int(b))))
    if edge!=root_edge:pending.extend(x for x in after_edges[edge] if x not in component)
  if not pending and len(component)==4:
   points=pos[newtri[list(component)].ravel()]
   assert max(points.max(0)-points.min(0))<.035
   closed_fin_faces.update(component)
assert len(closed_fin_faces)==4
kept_original=np.flatnonzero(keep)
assert max(closed_fin_faces)<len(kept_original)
remove=sorted(set(remove)|{int(kept_original[f]) for f in closed_fin_faces})
newtri=np.delete(newtri,sorted(closed_fin_faces),axis=0)
_,after_edges,after_groups,after_deg=topology(pos,newtri)
assert not after_groups and not after_deg and all(len(v)==2 for v in after_edges.values())
newblob=blob+b'\0'*((-len(blob))%4);offset=len(newblob);idxbytes=newtri.astype('<u2').tobytes();newblob+=idxbytes
view=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(idxbytes),'target':34963})
acc=len(doc['accessors']);doc['accessors'].append({'bufferView':view,'componentType':5123,'count':int(newtri.size-3),'type':'SCALAR'})
prim['indices']=acc
cap_accessor=len(doc['accessors']);doc['accessors'].append({'bufferView':view,'byteOffset':int((newtri.size-3)*2),'componentType':5123,'count':3,'type':'SCALAR'})
cap_material=len(doc['materials']);doc['materials'].append({'name':'Local grey strut closure','pbrMetallicRoughness':{'baseColorFactor':[.045,.03,.06,1],'metallicFactor':.3,'roughnessFactor':.65}})
cap_primitive=copy.deepcopy(prim);cap_primitive['indices']=cap_accessor;cap_primitive['material']=cap_material;doc['meshes'][0]['primitives'].append(cap_primitive)
doc['buffers'][0]['byteLength']=len(newblob)
encoded=json.dumps(doc,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);newblob+=b'\0'*((-len(newblob))%4)
target=OUT/'bison-rigged-local-repair-v1.glb'
target.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(newblob))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(newblob),0x004e4942)+newblob)
check,checkblob=read_glb(target)
assert checkblob[:len(blob)]==blob
for key in ['nodes','skins','images','textures','samplers','animations','scenes','scene']:
 assert check.get(key)==original.get(key),key
assert check['materials'][:len(original['materials'])]==original['materials']
for key,a in prim['attributes'].items():assert np.array_equal(accessor(check,checkblob,a),accessor(original,blob,a)),key
areas=np.linalg.norm(np.cross(pos[tri[remove,1]]-pos[tri[remove,0]],pos[tri[remove,2]]-pos[tri[remove,0]]),axis=1)/2
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'scope':'Local topology repair and one-triangle grey closure finish. No surface reconstruction or quality restoration claimed.','removed_fin_triangle_ids':remove,'removed_fin_area_total_m2':float(areas.sum()),'removed_fin_area_max_m2':float(areas.max()),'holes_closed':patches,'before':{'triangles':len(tri),'boundary_edges':sum(len(v)==1 for v in edges.values()),'edges_over_two_faces':sum(len(v)>2 for v in edges.values())},'after':{'triangles':len(newtri),'boundary_edges':0,'edges_over_two_faces':0},'preservation':{'all_original_binary_bytes_unchanged':True,'existing_positions_normals_uvs_joints_weights_byte_identical':True,'nodes_skins_images_textures_samplers_animations_scene_json_unchanged':True,'original_materials_unchanged':True,'new_materials':1,'new_vertices':0,'source_untouched':True},'method':'Append replacement triangle index accessors; assign only the second new closure to a local grey material. Keep original entire binary buffer as immutable prefix, including unused original indices. No Blender re-export or weight transfer.'}
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['holes_closed','removed_fin_triangle_ids']},indent=2))
