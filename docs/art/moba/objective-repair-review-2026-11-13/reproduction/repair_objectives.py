import sys,json,copy,hashlib,struct,collections,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg')
for mid in ['gold_beetle','wyvern']:
 cfg=json.loads((ROOT/mid/'input-audit.json').read_text());src=Path(cfg['input']);assert hashlib.sha256(src.read_bytes()).hexdigest()==cfg['sha256'];d,blob=read_glb(src);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];attrs={k:accessor(d,blob,ai) for k,ai in pr['attributes'].items()};pos=attrs['POSITION'];uv=attrs['TEXCOORD_0'];normal=attrs['NORMAL'];tri=accessor(d,blob,pr['indices']).reshape(-1,3);mp,edges,groups,deg=topology(pos,tri);comps=json.loads((ROOT/mid/'face-components.json').read_text());main_component=max(comps,key=lambda v:v['count']);remove=set();flaps=set();extra_legs=[];caps=[]
 for c in comps:
  if c['count']<=2 and c['boundary_edges']>0 and c['over_shared_roots']>0:flaps.update(c['faces'])
 if mid=='gold_beetle':
  inverted=[c for c in comps if c['count']<100 and c.get('signed_volume_m3',1)<0 and c['boundary_edges']==0];assert len(inverted)==1 and inverted[0]['count']==22
  flaps.update(inverted[0]['faces'])
  for g in groups:
   if len(g['vertices'])!=4 or g['edge_count']!=4:continue
   ids=set(g['vertices']);border_faces=collections.Counter(f for e,fs in edges.items() if set(e)<=ids and len(fs)==1 for f in fs);folds=[f for f,count in border_faces.items() if count==2 and set(mp[tri[f]])<=ids];assert len(folds)==1;flaps.update(folds)
 else:
  # The two closed inner forelegs are additional to the hind legs and wing arms.
  extra_legs=[c for c in comps if 1000<c['count']<2000 and c['bounds'][1][1]<.7 and c['bounds'][0][2]>.5];assert len(extra_legs)==2 and sum(v['count'] for v in extra_legs)==2772
 remove.update(flaps)
 for c in extra_legs:remove.update(c['faces'])
 keep=np.ones(len(tri),dtype=bool);keep[list(remove)]=False;newtri=tri[keep].astype(np.int64);_,ae,ag,ad=topology(pos,newtri)
 for g in ag:
  ids=set(g['vertices']);assert len(ids)==3 and g['edge_count']==3,('Unexpected repair contour',mid,g)
  edge,fs=next((e,fs) for e,fs in ae.items() if set(e)<=ids and len(fs)==1);ft=newtri[fs[0]];a,b=next((int(a),int(b)) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(mp[a]),int(mp[b]))))==edge);missing=next(iter(ids-{int(mp[a]),int(mp[b])}));order=[int(mp[b]),int(mp[a]),missing]
  options=itertools.product(*(np.where(mp==vi)[0].tolist() for vi in order));valid=[]
  for raw in options:
   pts=pos[list(raw)];cross=np.cross(pts[1]-pts[0],pts[2]-pts[0]);length=np.linalg.norm(cross)
   if length<1e-10:continue
   alignment=float(cross/length@normal[list(raw)].mean(0))
   if alignment>.25:valid.append((sum(float(np.linalg.norm(uv[raw[i]]-uv[raw[(i+1)%3]])) for i in range(3)),list(raw),alignment))
  assert valid;perimeter,raw,alignment=min(valid);caps.append({'new_triangles':[raw],'bounds':[g['min'],g['max']],'normal_alignment_score':alignment,'uv_perimeter':perimeter});newtri=np.concatenate([newtri,np.array([raw])])
 _,ae,ag,ad=topology(pos,newtri);assert not ag and not ad
 contacts=[e for e,fs in ae.items() if len(fs)>2]
 print('POST REPAIR',mid,'caps',len(caps),'contacts',[(e,len(ae[e]),pos[list(e)].tolist()) for e in contacts],flush=True)
 if mid=='gold_beetle':
  assert len(caps)==1 and len(contacts)==2
  for e in contacts:
   assert len(ae[e])==len(edges[e])==4
   directions=[]
   for fi in ae[e]:
    ft=mp[newtri[fi]]
    directions.extend(int(a<b) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(a),int(b))))==e)
   assert sum(directions)==2 # Original closed surfaces meet along this edge.
 else:
  assert not caps and len(contacts)==8
  for e in contacts:
   assert len(ae[e])==4 and len(edges[e])>=4
   directions=[]
   for fi in ae[e]:
    ft=mp[newtri[fi]];directions.extend(int(a<b) for a,b in zip(ft,np.roll(ft,-1)) if tuple(sorted((int(a),int(b))))==e)
   assert sum(directions)==2
  # Preserve the small, closed, outward-facing jaw detail at its original contact.
  jaw=next(c for c in comps if c['count']==6 and c['boundary_edges']==0 and c['signed_volume_m3']>0);jaw_vertices=set(mp[tri[jaw['faces']]].ravel());assert any(set(e)<=jaw_vertices for e in contacts)
 used=np.unique(newtri);changed=[];removed_joints=[];body_parent=None
 if mid=='wyvern':
  names=[d['nodes'][ni]['name'] for ni in d['skins'][0]['joints']];removed_names=[f'Bone_{i:03}' for i in range(28,38)];removed_joints=[names.index(name) for name in removed_names];parents={ci:pi for pi,node in enumerate(d['nodes']) for ci in node.get('children',[])};ni={node['name']:i for i,node in enumerate(d['nodes']) if 'name' in node};parent_names=[d['nodes'][parents[ni[name]]]['name'] for name in ['Bone_032','Bone_037']];assert parent_names[0]==parent_names[1]=='Bone_002';body_parent=names.index('Bone_002')
  j=attrs['JOINTS_0'];w=attrs['WEIGHTS_0']
  for vi in used:
   if not np.any((w[vi]>0)&np.isin(j[vi],removed_joints)):continue
   dense=np.zeros(len(names),dtype=np.float32);np.add.at(dense,j[vi],w[vi]);dense[body_parent]+=dense[removed_joints].sum();dense[removed_joints]=0;ji=np.argsort(dense)[-4:][::-1];ww=dense[ji];ww/=ww.sum();j[vi]=ji;w[vi]=ww;changed.append(int(vi))
  assert not np.any((w[used]>1e-8)&np.isin(j[used],removed_joints))
 out_blob=blob+b'\0'*((-len(blob))%4)
 def append(data,component,kind,target):
  global out_blob
  out_blob+=b'\0'*((-len(out_blob))%4);offset=len(out_blob);raw=data.tobytes();out_blob+=raw;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target});ai=len(d['accessors']);d['accessors'].append({'bufferView':vi,'componentType':component,'count':len(data),'type':kind});return ai
 if changed:
  for name in ['JOINTS_0','WEIGHTS_0']:
   old=d['accessors'][pr['attributes'][name]];pr['attributes'][name]=append(attrs[name],old['componentType'],old['type'],34962)
 pr['indices']=append(newtri.astype('<u2').reshape(-1,1),5123,'SCALAR',34963);d['buffers'][0]['byteLength']=len(out_blob);encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);out_blob+=b'\0'*((-len(out_blob))%4);out=BASE/f'docs/art/moba/{mid}_objective/repair-v1-2026-11-11';out.mkdir(parents=True,exist_ok=True);dest=out/f'{mid}-objective-repaired-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(out_blob))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(out_blob),0x004e4942)+out_blob)
 for key in ['nodes','skins','materials','images','textures','samplers','scenes','scene','animations']:assert d.get(key)==original.get(key),key
 assert out_blob[:len(blob)]==blob
 for name in ['POSITION','NORMAL','TEXCOORD_0']:assert np.array_equal(attrs[name],accessor(original,blob,original['meshes'][0]['primitives'][0]['attributes'][name]))
 # Every healthy body/wing/hip face remains original; only the gold hole's fold changes.
 retained_body=set(main_component['faces'])-remove;assert len(set(main_component['faces'])-retained_body)==(1 if mid=='gold_beetle' else 0)
 report={'id':mid,'name':cfg['name'],'category':'objective','source':str(src),'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'joint_count':cfg['joint_count'],'before_triangles':len(tri),'final_triangles':len(newtri),'removed_fold_triangles':len(flaps),'removed_fold_triangle_ids':sorted(flaps),'removed_extra_foreleg_triangles':sum(c['count'] for c in extra_legs),'removed_extra_foreleg_face_ids':[c['faces'] for c in extra_legs],'healthy_source_body_faces_retained':len(retained_body),'holes_closed':caps,'boundary_edges':0,'over_shared_edges':len(contacts),'protected_closed_contact_edges':[list(e) for e in contacts],'contact_note':'Two unchanged source four-face contacts between otherwise closed assembly surfaces.' if mid=='gold_beetle' else 'One original contact between the closed jaw detail and main body.','unclassified_nonmanifold_edges':0,'collapsed_triangles':0,'skeleton_hierarchy_rest_binds_skins_scenes_materials_unchanged':True,'original_binary_prefix_unchanged':True,'original_position_normal_uv_rows_unchanged':True,'all_skin_rows_unchanged':not changed,'locally_reassigned_skin_rows':len(changed),'changed_skin_row_ids':changed,'removed_joint_influences':[f'Bone_{i:03}' for i in range(28,38)] if changed else [],'residual_removed_joint_influence_reassigned_to':'Bone_002' if changed else None,'new_vertices':0,'intact_pre_remesh_source_available':False,'anatomy':'Six walking legs, paired mandibles and coin shell retained.' if mid=='gold_beetle' else 'Extra inner walking forelegs removed; two hind legs and two wing forelimbs retained. Closed jaw detail preserved.'}
 if mid=='wyvern':report['contact_note']='Eight original four-face contacts between closed assembly surfaces, including a small closed jaw detail. No new contact edges introduced.'
 (out/'repair-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if not k.endswith('_ids')},indent=2),flush=True)
