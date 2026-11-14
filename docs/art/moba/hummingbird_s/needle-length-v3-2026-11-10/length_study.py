import sys,copy,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/needle-length-study-2026-11-10');OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10/hummingbird-rigged-needle-topology-v2.glb');original,blob=read_glb(SOURCE);op=original['meshes'][0]['primitives'][0];p=accessor(original,blob,op['attributes']['POSITION']);norm=accessor(original,blob,op['attributes']['NORMAL']);reports=[]
for label,factor in [('shorter-20',.8),('shorter-30',.7)]:
 d=copy.deepcopy(original);pr=d['meshes'][0]['primitives'][0];new=p.copy();nn=norm.copy();mask=p[:,2]>.30;dz=(p[mask,2]-.30)*(factor-1);new[mask,2]+=dz;new[mask,1]+=dz*((1.075-1.26)/(1.355058789-.30));jac=np.array([[1,0,0],[0,1,((1.075-1.26)/(1.355058789-.30))*(factor-1)],[0,0,factor]]);normal=norm[mask]@np.linalg.inv(jac);nn[mask]=normal/np.linalg.norm(normal,axis=1)[:,None]
 payload=blob
 for name,values in [('POSITION',new),('NORMAL',nn)]:
  payload+=b'\0'*((-len(payload))%4);offset=len(payload);raw=values.astype('<f4').tobytes();payload+=raw;view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':34962});a={'bufferView':view,'componentType':5126,'count':len(values),'type':'VEC3'}
  if name=='POSITION':a.update(min=values.min(0).tolist(),max=values.max(0).tolist())
  ai=len(d['accessors']);d['accessors'].append(a);pr['attributes'][name]=ai
 d['buffers'][0]['byteLength']=len(payload);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);payload+=b'\0'*((-len(payload))%4);target=OUT/(label+'-REVIEW-ONLY.glb');target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(payload))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(payload),0x004e4942)+payload)
 for key in ['nodes','skins','materials','images','textures','animations']:assert d.get(key)==original.get(key)
 assert np.array_equal(new[~mask],p[~mask])
 reports.append({'candidate':label,'shaft_length_factor':factor,'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'rig_weights_body_materials_preserved':True,'review_only':True})
(OUT/'candidate-verification.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
