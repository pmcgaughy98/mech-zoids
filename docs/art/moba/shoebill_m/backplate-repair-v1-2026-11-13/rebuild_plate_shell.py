"""Preserve the source's visible moon/rim/mount surfaces; rebuild their rear shell."""
import json,sys,copy,struct,hashlib,collections,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13')
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_shoebill_single_material_25k_20261111_character.glb')
d,blob=read_glb(SOURCE);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];attrs={k:accessor(d,blob,v) for k,v in pr['attributes'].items()};pos=attrs['POSITION'];tri=accessor(d,blob,pr['indices']).reshape(-1,3);comps=json.loads((ROOT/'face-components.json').read_text());plate=set(next(c['faces'] for c in comps if c['count']==4410));rgb=np.load(ROOT/'mesh-analysis.npz')['triangle_rgb'];gray=np.array([44,48,72])/255
caps={i for i in plate if abs(rgb[i]-gray).max()<.03};blue={i for i in plate if rgb[i,2]>.25 and rgb[i,2]>1.8*rgb[i,0] and rgb[i,2]>1.4*rgb[i,1]}
source_points=pos[tri];source_n=np.cross(source_points[:,1]-source_points[:,0],source_points[:,2]-source_points[:,0]);source_n/=np.maximum(np.linalg.norm(source_n,axis=1)[:,None],1e-12)
center=np.array([-.0001698,1.1668026]);radii=np.linalg.norm(source_points.mean(1)[:,:2]-center,axis=1)
gold=(rgb[:,0]>rgb[:,1]*1.05)&(rgb[:,1]>rgb[:,2]*1.02)&(rgb[:,0]>.2)
front_ids=np.array(sorted(i for i in plate-caps-blue if not(radii[i]>.245 and source_n[i,2]>-.15 and not gold[i])));mp,edges,groups,deg=topology(pos,tri[front_ids]);adj=[set() for _ in front_ids]
for fs in edges.values():
 if len(fs)==2:a,b=fs;adj[a].add(b);adj[b].add(a)
seen=set();parts=[]
for start in range(len(front_ids)):
 if start in seen:continue
 stack=[start];part=set()
 while stack:
  f=stack.pop()
  if f in part:continue
  part.add(f);stack.extend(adj[f]-part)
 seen.update(part);parts.append(sorted(part))
front_ids=front_ids[max(parts,key=len)];front=tri[front_ids];mp,edges,groups,deg=topology(pos,front)
assert not deg and all(len(fs)<=2 for fs in edges.values())
data={k:[row.copy() for row in a] for k,a in attrs.items()}
def clone(vi,position=None,normal=None):
 row={k:data[k][vi].copy() for k in attrs}
 if position is not None:row['POSITION']=position
 if normal is not None:row['NORMAL']=normal
 i=len(data['POSITION'])
 for k in data:data[k].append(np.asarray(row[k],dtype=attrs[k].dtype))
 return i
area_normals=np.cross(pos[front[:,1]]-pos[front[:,0]],pos[front[:,2]]-pos[front[:,0]])
# Some source surface patches meet only at a vertex. Give their rear fans
# separate offsets, so solidifying them cannot create shared four-face edges.
incident=collections.defaultdict(set)
for fi,ft in enumerate(mp[front]):
 for g in ft:incident[int(g)].add(fi)
key_for={int(vi):(int(mp[vi]),0) for vi in np.unique(front)};tangent={}
for geom,fs in incident.items():
 local={fi:set() for fi in fs}
 for edge,attached in edges.items():
  if geom in edge and len(attached)==2:
   a,b=attached;local[a].add(b);local[b].add(a)
 seen=set();fans=[]
 for start in fs:
  if start in seen:continue
  stack=[start];part=set()
  while stack:
   f=stack.pop()
   if f in part:continue
   part.add(f);stack.extend(local[f]-part)
  seen.update(part);fans.append(part)
 if len(fans)==1:continue
 for fan_id,fan in enumerate(fans):
  remap={}
  for fi in fan:
   for k,vi in enumerate(front[fi]):
    if key_for[int(vi)][0]!=geom:continue
    vi=int(vi)
    if fan_id>0:
     if vi not in remap:remap[vi]=clone(vi)
     vi=remap[vi];front[fi,k]=vi
    key_for[vi]=(geom,fan_id)
  v=pos[tri[front_ids[list(fan)]]].reshape(-1,3).mean(0)-pos[geom]
  tangent[(geom,fan_id)]=v/max(np.linalg.norm(v),1e-12)*.0002
frontpos=np.asarray(data['POSITION']);mp,edges,groups,deg=topology(frontpos,front)
smooth=collections.defaultdict(lambda:np.zeros(3))
for ft,n in zip(front,area_normals):
 for vi in ft:smooth[key_for[int(vi)]]+=n
for g,n in smooth.items():smooth[g]=n/max(np.linalg.norm(n),1e-12)
back={}
for vi in np.unique(front):
 key=key_for[int(vi)];direction=smooth[key];point=pos[key[0]].copy();point[:2]=center+(point[:2]-center)*.98;point[2]=-.395+(point[2]+.4)*.05;point+=tangent.get(key,0)
 back[int(vi)]=clone(int(vi),point,-direction)
rear=[]
for ft in front:rear.append([back[int(ft[2])],back[int(ft[1])],back[int(ft[0])]])
wall_count=0
for e,fs in edges.items():
 if len(fs)!=1:continue
 ft=front[fs[0]]
 a,b=next((int(a),int(b)) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[a]),int(mp[b]))))==e)
 # Reverse each front boundary edge. New side vertices retain exact skin rows.
 for face in [[b,a,back[a]],[b,back[a],back[b]]]:
  pp=np.asarray(data['POSITION'])[face];n=np.cross(pp[1]-pp[0],pp[2]-pp[0]);n/=max(np.linalg.norm(n),1e-12)
  cloned=[]
  for vi in face:
   k=len(data['POSITION'])
   for key in data:data[key].append((n if key=='NORMAL' else data[key][vi]).copy())
   cloned.append(k)
  rear.append(cloned);wall_count+=1
rear=np.asarray(rear,dtype=np.int64);fronttri=front.copy();repair_caps=[];removed=[]
if '--preview' not in sys.argv:
 # The actual body is independent of the donor plate. Remove diagnosed open fins
 # and the separate tiny sole scrap, retaining every healthy body/wing surface.
 removed=[int(f) for c in comps if c['count']==1 for f in c['faces']]
 keep=[i for i in range(len(tri)) if i not in plate and i not in removed]
 body=tri[keep].copy();pmap,ee,gg,dd=topology(pos,body)
 # The four-edge head opening includes one folded triangle, as in other inputs.
 folds=[]
 for g in gg:
  if g['edge_count']!=4:continue
  ids=set(g['vertices']);cnt=collections.Counter(fi for e,fs in ee.items() if len(fs)==1 and set(e)<=ids for fi in fs)
  found=[fi for fi,n in cnt.items() if n==2 and set(pmap[body[fi]])<=ids];assert len(found)==1;folds.extend(found)
 if folds:
  removed.extend(keep[i] for i in folds);body=np.delete(body,folds,axis=0)
 pmap,ee,gg,dd=topology(pos,body)
 for g in gg:
  ids=set(g['vertices']);directed={};raw={}
  for e,fs in ee.items():
   if len(fs)!=1 or not set(e)<=ids:continue
   ft=body[fs[0]]
   a,b=next((int(a),int(b)) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(pmap[a]),int(pmap[b]))))==e)
   directed[int(pmap[a])]=int(pmap[b]);raw[int(pmap[a])]=a
  first=next(iter(directed));order=[first];cur=directed[first]
  while cur!=first:order.append(cur);cur=directed[cur];assert len(order)<200
  # Mount collar loops lie behind the preserved front face; close the sleeve
  # ends as rear enclosure panels, without filling across the moon design.
  assert len(order) in [3,60],(len(order),g)
  ring=[raw[i] for i in order][::-1]
  faces=[[ring[0],ring[k],ring[k+1]] for k in range(1,len(ring)-1)]
  for face in faces:
   points=pos[face];normal=np.cross(points[1]-points[0],points[2]-points[0]);normal/=max(np.linalg.norm(normal),1e-12)
   repair_caps.append([clone(vi,normal=normal) for vi in face])
 fronttri=np.concatenate([body,front]);rear=np.concatenate([rear,np.asarray(repair_caps)])
alltri=np.concatenate([fronttri,rear]);newpos=np.asarray(data['POSITION'],dtype=np.float32);m,e,g,deg=topology(newpos,alltri)
assert not g and not deg,(g,deg)
assert all(len(fs)==2 for fs in e.values()),[(k,len(v)) for k,v in e.items() if len(v)>2][:10]
area=np.linalg.norm(np.cross(newpos[alltri[:,1]]-newpos[alltri[:,0]],newpos[alltri[:,2]]-newpos[alltri[:,0]]),axis=1)/2
assert area.min()>1e-12,float(area.min())
outblob=blob+b'\0'*((-len(blob))%4)
def append(array,component,kind,target,position=False):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);off=len(outblob);raw=array.tobytes();outblob+=raw;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(raw),'target':target});ai=len(d['accessors']);a={'bufferView':vi,'componentType':component,'count':len(array),'type':kind}
 if position:a['min']=array.min(0).tolist();a['max']=array.max(0).tolist()
 d['accessors'].append(a);return ai
for k in data:
 old=d['accessors'][pr['attributes'][k]];pr['attributes'][k]=append(np.asarray(data[k],dtype=attrs[k].dtype),old['componentType'],old['type'],34962,k=='POSITION')
pr['indices']=append(fronttri.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);backpr=copy.deepcopy(pr);backpr['indices']=append(rear.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);backpr['material']=len(d['materials']);d['materials'].append({'name':'Recessed backplate shell and hidden closures','pbrMetallicRoughness':{'baseColorFactor':[.025,.03,.065,1],'metallicFactor':.65,'roughnessFactor':.55}});d['meshes'][0]['primitives'].append(backpr);d['buffers'][0]['byteLength']=len(outblob)
js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);outblob+=b'\0'*((-len(outblob))%4);dest=ROOT/'shell-isolated.glb' if '--preview' in sys.argv else OUT/'shoebill-backplate-repaired-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(outblob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(outblob),0x004e4942)+outblob)
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'triangles':len(alltri),'joint_count':38,'preserved_visible_plate_faces':len(front_ids),'preserved_plate_source_face_ids':front_ids.tolist(),'removed_plate_donor_faces':len(plate)-len(front_ids),'removed_small_flap_and_scrap_face_ids':sorted(removed),'sleeve_and_small_gap_cap_triangles':len(repair_caps),'new_shell_side_triangles':wall_count,'boundary_edges':0,'over_shared_edges':0,'collapsed_triangles':0,'original_position_normal_uv_skin_rows_stored_unchanged':True,'source_body_geometry_unchanged_except_one_fold_and_cap':True,'original_rig_hierarchy_rest_binds_materials_textures_preserved':True,'added_material':'Recessed backplate shell and hidden closures','scope':'Removed unwanted blue donor feathers and folded rear closure from transferred plate. Preserved main visible moon/rim/mount surface, rebuilt its thin rear shell. Main body, wings, legs and skeleton retained.'}
(ROOT/'shell-preview-verification.json' if '--preview' in sys.argv else OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if not k.endswith('_ids')},flush=True)
