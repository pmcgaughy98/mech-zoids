import struct,json,io,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image
def read(path):
 with path.open('rb') as f:
  f.read(12);n,t=struct.unpack('<II',f.read(8));d=json.loads(f.read(n))
  n,t=struct.unpack('<II',f.read(8));b=f.read(n)
 return d,b
def geometry_hashes(d,b):
 ids=set()
 for mesh in d['meshes']:
  for primitive in mesh['primitives']:
   for acc in list(primitive['attributes'].values())+[primitive['indices']]:
    ids.add(d['accessors'][acc]['bufferView'])
 return {str(i):hashlib.sha256(b[d['bufferViews'][i].get('byteOffset',0):d['bufferViews'][i].get('byteOffset',0)+d['bufferViews'][i]['byteLength']]).hexdigest() for i in sorted(ids)}
src=Path(sys.argv[1]);dst=Path(sys.argv[2]);size=int(sys.argv[3])
d,b=read(src); before=geometry_hashes(d,b)
assert len(d['buffers'])==1
normal_ids={d['textures'][m['normalTexture']['index']]['source'] for m in d['materials'] if 'normalTexture' in m}
replacements={};report=[]
for index,im in enumerate(d.get('images',[])):
 v=d['bufferViews'][im['bufferView']];start=v.get('byteOffset',0)
 image=Image.open(io.BytesIO(b[start:start+v['byteLength']])).convert('RGB')
 old=image.size
 image=image.resize((size,size),Image.Resampling.BOX if index in normal_ids else Image.Resampling.LANCZOS)
 if index in normal_ids:
  a=np.asarray(image,dtype=np.float32)/127.5-1
  a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-6)
  image=Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
 stream=io.BytesIO();image.save(stream,format='PNG')
 replacements[im['bufferView']]=stream.getvalue()
 im['mimeType']='image/png'
 report.append({'name':im.get('name'),'old_size':old,'size':[size,size],'normal_renormalized':index in normal_ids})
data=bytearray()
for i,v in enumerate(d['bufferViews']):
 data.extend(b'\0'*((-len(data))%4))
 start=v.get('byteOffset',0);piece=replacements.get(i,b[start:start+v['byteLength']])
 v['byteOffset']=len(data);v['byteLength']=len(piece)
 data.extend(piece)
d['buffers'][0]['byteLength']=len(data)
js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
data.extend(b'\0'*((-len(data))%4))
with dst.open('wb') as f:
 f.write(struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(data)))
 f.write(struct.pack('<II',len(js),0x4E4F534A));f.write(js)
 f.write(struct.pack('<II',len(data),0x004E4942));f.write(data)
dd,bb=read(dst);assert geometry_hashes(dd,bb)==before,'Texture-only derivative changed geometry buffers'
summary={'source':str(src),'output':str(dst),'geometry_buffers_identical':True,'images':report,'bytes_before':src.stat().st_size,'bytes_after':dst.stat().st_size}
dst.with_suffix('.texture-report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
