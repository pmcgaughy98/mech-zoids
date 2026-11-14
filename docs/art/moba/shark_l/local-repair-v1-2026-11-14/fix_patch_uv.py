import copy,hashlib,json,struct,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb,accessor,topology
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shark_l/local-repair-v1-2026-11-14');rp=OUT/'repair-verification.json';r=json.loads(rp.read_text());path=Path(r['output']);d,b=read_glb(path);pr=d['meshes'][0]['primitives'][0];arrays={k:accessor(d,b,a) for k,a in pr['attributes'].items()};p=arrays['POSITION'];uv=arrays['TEXCOORD_0'];tri=accessor(d,b,pr['indices']).reshape(-1,3);patch_id=len(tri)-7+3;raw=tri[patch_id].copy();assert raw.tolist()==r['holes_closed'][3]['triangle'];mp,edges,groups,deg=topology(p,tri);corners=set(mp[raw]);candidates=[]
for fi,face in enumerate(tri[:-7]):
    if len(set(mp[face])&corners)<2:continue
    pts=p[face];tex=uv[face];mat=(pts[1:]-pts[0]).T;coords=np.linalg.lstsq(mat,(p[raw]-pts[0]).T,rcond=None)[0].T;weights=np.column_stack([1-coords.sum(1),coords]);clamped=np.maximum(weights,0);clamped/=clamped.sum(1)[:,None];mapped=clamped@tex;perimeter=float(sum(np.linalg.norm(mapped[i]-mapped[(i+1)%3]) for i in range(3)));normal=np.cross(pts[1]-pts[0],pts[2]-pts[0]);normal/=np.linalg.norm(normal);align=float(normal@np.array(r['holes_closed'][3]['normal']))
    if align>.5 and perimeter<.05:candidates.append((perimeter,fi,mapped))
assert candidates
perimeter,face_id,mapped=min(candidates,key=lambda item:item[:2]);count=len(p);out=b+b'\0'*(-len(b)%4)
def append_accessor(data,template,target):
    global out
    out+=b'\0'*(-len(out)%4);view=len(d['bufferViews']);packed=np.ascontiguousarray(data).tobytes();d['bufferViews'].append({'buffer':0,'byteOffset':len(out),'byteLength':len(packed),'target':target});out+=packed;access=copy.deepcopy(template);access.update({'bufferView':view,'byteOffset':0,'count':len(data)});index=len(d['accessors']);d['accessors'].append(access);return index
old_attributes=dict(pr['attributes'])
for key,arr in arrays.items():
    extra=arr[raw].copy()
    if key=='TEXCOORD_0':extra=mapped.astype(arr.dtype)
    full=np.concatenate([arr,extra]);pr['attributes'][key]=append_accessor(full,d['accessors'][old_attributes[key]],34962)
tri[patch_id]=np.arange(count,count+3);template=d['accessors'][pr['indices']];pr['indices']=append_accessor(tri.reshape(-1,1).astype('<u2'),template,34963);d['buffers'][0]['byteLength']=len(out);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*(-len(js)%4);out+=b'\0'*(-len(out)%4);path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(out))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(out),0x004e4942)+out)
r['output_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();r['new_geometric_vertices']=0;r['new_attribute_rows']=3;r['uv_repair']={'patch':4,'source_neighbor_face':face_id,'method':'Three duplicate corner rows, original positions/normals/joints/weights copied exactly; UVs sampled inside one adjacent healthy texture island to avoid atlas stripe.','old_corner_rows':raw.tolist(),'new_corner_rows':list(range(count,count+3)),'uv':mapped.tolist(),'uv_perimeter':perimeter};r['scope']+=' Three duplicate corner rows on closure 4 use one healthy neighboring UV island. All original attribute/skin rows remain exact; duplicate skin rows copy the same corners.';rp.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['uv_repair']));print('SHA256',r['output_sha256'])
