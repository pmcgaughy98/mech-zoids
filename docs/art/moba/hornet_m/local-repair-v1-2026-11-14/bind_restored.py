import sys,copy,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hornet_m/local-repair-v1-2026-11-14');SRC=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_hornet_touchup_remeshed_25k_20261111_character.glb');rig,rb=read_glb(SRC);old=copy.deepcopy(rig);surface,sb=read_glb(OUT/'restored-six-leg-surface-STATIC-STAGING.glb');rp=rig['meshes'][0]['primitives'][0];rpos=accessor(rig,rb,rp['attributes']['POSITION']);rj=accessor(rig,rb,rp['attributes']['JOINTS_0']);rw=accessor(rig,rb,rp['attributes']['WEIGHTS_0'])
binary=rb+b'\0'*((-len(rb))%4);shift=len(binary);binary+=sb;view_offset=len(rig['bufferViews']);accessor_offset=len(rig['accessors']);image_offset=len(rig.get('images',[]));texture_offset=len(rig.get('textures',[]));sampler_offset=len(rig.get('samplers',[]));material_offset=len(rig.get('materials',[]))
for v in surface['bufferViews']:
 v=copy.deepcopy(v);v['byteOffset']=v.get('byteOffset',0)+shift;v['buffer']=0;rig['bufferViews'].append(v)
for a in surface['accessors']:
 a=copy.deepcopy(a);a['bufferView']+=view_offset;rig['accessors'].append(a)
for image in surface.get('images',[]):
 image=copy.deepcopy(image);image['bufferView']+=view_offset;rig.setdefault('images',[]).append(image)
rig.setdefault('samplers',[]).extend(copy.deepcopy(surface.get('samplers',[])))
for texture in surface.get('textures',[]):
 texture=copy.deepcopy(texture)
 if 'source' in texture:texture['source']+=image_offset
 if 'sampler' in texture:texture['sampler']+=sampler_offset
 rig.setdefault('textures',[]).append(texture)
def remap_material(x):
 if isinstance(x,dict):
  for key,value in x.items():
   if key.endswith('Texture') and isinstance(value,dict) and 'index' in value:value['index']+=texture_offset
   else:remap_material(value)
 elif isinstance(x,list):
  for v in x:remap_material(v)
for material in surface.get('materials',[]):
 material=copy.deepcopy(material);remap_material(material);rig.setdefault('materials',[]).append(material)
def append(data,component,kind):
 global binary
 binary+=b'\0'*((-len(binary))%4);offset=len(binary);raw=data.tobytes();binary+=raw;view=len(rig['bufferViews']);rig['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':34962});ai=len(rig['accessors']);rig['accessors'].append({'bufferView':view,'componentType':component,'count':len(data),'type':kind});return ai
tree=cKDTree(rpos);meshes=[];stats=[]
joint_names=[rig['nodes'][node]['name'] for node in rig['skins'][0]['joints']];removed_joint_indices=[];body_joint=joint_names.index('Bone_000')
for mesh in surface['meshes']:
 mesh=copy.deepcopy(mesh)
 for pr in mesh['primitives']:
  p=accessor(surface,sb,pr['attributes']['POSITION']);distance,ids=tree.query(p,k=4);factors=1/np.maximum(distance,1e-5)**4;factors/=factors.sum(1)[:,None];dense=np.zeros((len(p),51),dtype=np.float32)
  for k in range(4):
   for col in range(4):np.add.at(dense,(np.arange(len(p)),rj[ids[:,k],col]),factors[:,k]*rw[ids[:,k],col])
  # The approved middle walking pair is gone. Keep its skeleton intact, but
  # bind any residual influence around its sockets to the existing body parent.
  dense[:,body_joint]+=dense[:,removed_joint_indices].sum(1);dense[:,removed_joint_indices]=0
  joints=np.argsort(dense,axis=1)[:,-4:][:,::-1].astype('u1');weights=np.take_along_axis(dense,joints,axis=1);weights/=weights.sum(1)[:,None];assert np.isfinite(weights).all()
  stats.append({'vertices':len(p),'distance_mean':float(distance[:,0].mean()),'distance_99pct':float(np.percentile(distance[:,0],99)),'distance_max':float(distance[:,0].max())})
  for key in list(pr['attributes']):pr['attributes'][key]+=accessor_offset
  pr['indices']+=accessor_offset;pr['material']=pr.get('material',0)+material_offset;pr['attributes']['JOINTS_0']=append(joints,5121,'VEC4');pr['attributes']['WEIGHTS_0']=append(weights.astype('<f4'),5126,'VEC4')
 meshes.append(mesh)
rig['meshes']=meshes
for key in ['extensionsUsed','extensionsRequired']:
 if key in surface:rig[key]=sorted(set(rig.get(key,[])+surface[key]))
rig['buffers'][0]['byteLength']=len(binary);encoded=json.dumps(rig,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);binary+=b'\0'*((-len(binary))%4);target=OUT/'hornet-rigged-local-repair-v1.glb';target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(binary),0x004e4942)+binary)
for key in ['nodes','skins','scenes','scene','animations']:assert rig.get(key)==old.get(key),key
assert binary[:len(rb)]==rb
report={'source_rig':str(SRC),'source_rig_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'skeleton_nodes_bind_transforms_skins_scenes_unchanged':True,'original_rig_buffer_retained':True,'weights':'Transferred from actual downloaded rig using four nearest surface samples, inverse fourth power, strongest four influences normalized. UV-seam duplicates use identical point queries. Current six-leg skeleton and all its controls retained; no removed-chain reassignment.','removed_limb_weight_joints':[joint_names[i] for i in removed_joint_indices],'surface_materials':'Restored original source materials and embedded textures, plus local cut-root finish; downloaded materials retained in archive buffer/JSON.','distance_stats':stats};(OUT/'rig-transfer-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
