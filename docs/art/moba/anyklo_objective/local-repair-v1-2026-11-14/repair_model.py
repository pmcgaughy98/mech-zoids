import json,sys,copy,struct,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14')
cfg=json.loads((ROOT/'input-audit.json').read_text());d,b=read_glb(cfg['source']);original=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0]
p=accessor(d,b,pr['attributes']['POSITION']);n=accessor(d,b,pr['attributes']['NORMAL']);tri=accessor(d,b,pr['indices']).reshape(-1,3);comps=json.loads((ROOT/'face-components.json').read_text());removed={f for c in comps if c['count']<=3 and c['boundary_edges']>0 for f in c['faces']};assert len(removed)==15
newtri=np.delete(tri,sorted(removed),axis=0)
rotations={};measures=[]
for sign in [-1,1]:
    measured=next(x for x in json.loads((ROOT/'panel-measurements.json').read_text()) if x['side']==sign)
    axis=np.array(measured['original_panel_axis']);target=np.array([1.,0,0]);v=np.cross(axis,target);co=float(axis@target);K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]);R=np.eye(3)+K+K@K/(1+co)
    pivot=np.array([sign*.3,1.15,-2.23]);rotations[sign]=(R,pivot)
    measures.append({'side':sign,'source_rear_panel_axis':axis.tolist(),'target_rear_panel_axis':[1,0,0],'rotation_degrees':float(np.degrees(np.arccos(co))),'pivot':pivot.tolist(),'rotation_matrix':R.tolist()})
def smooth(t):
    t=np.clip(t,0,1);return t*t*(3-2*t)
def warp(points):
    pp=np.asarray(points,dtype=float);result=pp.copy()
    for sign,(R,pivot) in rotations.items():
        w=smooth((pp[:,0]*sign-.08)/.22)*smooth((-pp[:,2]-1.8)/.16)
        moved=(pp-pivot)@R.T+pivot
        result+=(moved-pp)*w[:,None]
    return result
changed=np.linalg.norm(warp(p)-p,axis=1)>1e-9
newp=p.copy();newp[changed]=warp(p[changed]).astype('f4')
# The local, continuous collar transition keeps shared positions together and leaves the shaft untouched.
points=p[changed].astype(float);h=1e-5;J=np.stack([(warp(points+np.eye(3)[i]*h)-warp(points-np.eye(3)[i]*h))/(2*h) for i in range(3)],axis=2);det=np.linalg.det(J)
assert det.min()>.15,('folded collar transition',float(det.min()))
newn=n.copy();normal=np.linalg.solve(J.transpose(0,2,1),n[changed].astype(float)[...,None])[...,0];normal/=np.linalg.norm(normal,axis=1)[:,None];newn[changed]=normal.astype('f4')
mp,edges,groups,deg=topology(newp,newtri);contacts=[e for e,fs in edges.items() if len(fs)>2];assert not groups and not deg and len(contacts)==2 and all(len(edges[e])==4 for e in contacts)
assert np.array_equal(newp[~changed],p[~changed]) and np.array_equal(newn[~changed],n[~changed])
blob=bytearray(b)
def append_array(arr,kind,component,target):
    while len(blob)%4:blob.extend(b'\0')
    offset=len(blob);raw=arr.tobytes();blob.extend(raw);vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(raw),'target':target});ai=len(d['accessors']);item={'bufferView':vi,'componentType':component,'count':len(arr),'type':kind}
    if kind=='VEC3' and np.array_equal(arr,newp):item.update({'min':arr.min(0).tolist(),'max':arr.max(0).tolist()})
    d['accessors'].append(item);return ai
pr['attributes']['POSITION']=append_array(newp.astype('<f4'),'VEC3',5126,34962)
pr['attributes']['NORMAL']=append_array(newn.astype('<f4'),'VEC3',5126,34962)
pr['indices']=append_array(newtri.astype('<u2').reshape(-1,1),'SCALAR',5123,34963)
d['buffers'][0]['byteLength']=len(blob);js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);blob+=b'\0'*((-len(blob))%4)
dest=OUT/'anyklo-rigged-tail-mallet-v1.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob)
for k in ['nodes','skins','materials','images','textures','samplers','scenes','scene','animations']:assert d.get(k)==original.get(k)
report={'source':cfg['source'],'source_sha256':cfg['sha256'],'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'before_triangles':len(tri),'final_triangles':len(newtri),'joint_count':37,'removed_malformed_triangles':len(removed),'removed_face_ids':sorted(removed),'boundary_edges':0,'over_shared_edges':2,'collapsed_triangles':0,'protected_contact_edges':[list(e) for e in contacts],'changed_vertex_rows':int(changed.sum()),'unchanged_vertex_rows':int((~changed).sum()),'changed_row_ids':np.where(changed)[0].tolist(),'changed_bounds':[p[changed].min(0).tolist(),p[changed].max(0).tolist()],'maximum_local_vertex_displacement_m':float(np.linalg.norm(newp-p,axis=1).max()),'minimum_local_jacobian_determinant':float(det.min()),'lobe_alignment':measures,'all_original_skin_uv_materials_skeleton_rest_binds_preserved':True,'source_binary_prefix_preserved':True,'scope':'Rename cyber tortoise to anyklo. Align the two tail hammer lobes to a shared transverse mallet axis using local rotations with continuous collar transitions. Only tail-head positions/normals and 15 malformed triangle indices changed. Four legs, head, dorsal capacitor ribs and tail shaft retained. Original 37-joint skeleton/rest/binds and all weights, UVs and textures preserved; no remesh or rerig.','intact_pre_remesh_available':False}
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['changed_row_ids','removed_face_ids']},indent=2))
