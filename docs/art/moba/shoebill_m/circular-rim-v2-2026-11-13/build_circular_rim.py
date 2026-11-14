"""Add a continuous circular housing over the fitted plate's exposed gray backing."""
import sys,json,copy,hashlib,struct,math
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
ROOT=Path(__file__).parent;OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13');OUT.mkdir(exist_ok=True)
SOURCE=Path('D:/dev/new-mech-rpg/docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13/shoebill-backplate-repaired-v1.glb');d,blob=read_glb(SOURCE);original=copy.deepcopy(d)
raw,rb=read_glb('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_shoebill_single_material_25k_20261111_character.glb');rp=raw['meshes'][0]['primitives'][0];p=accessor(raw,rb,rp['attributes']['POSITION']);tri=accessor(raw,rb,rp['indices']).reshape(-1,3);rgb=np.load(ROOT/'mesh-analysis.npz')['triangle_rgb'];comps=json.loads((ROOT/'face-components.json').read_text());plate=np.array(next(c['faces'] for c in comps if c['count']==4410));sleeve=np.array(next(c['faces'] for c in comps if c['count']==120))
center=np.array([-.0001698,1.1668026]);_,edges,groups,_=topology(p,tri[sleeve]);back=next(g for g in groups if g['max'][2]>-.30);points=p[back['vertices']];angle=np.mod(np.arctan2(points[:,1]-center[1],points[:,0]-center[0]),2*np.pi);order=np.argsort(angle);theta=angle[order];zback=points[order,2]
gold=plate[(rgb[plate,0]>.4)&(rgb[plate,0]>rgb[plate,1]*1.03)&(rgb[plate,1]>rgb[plate,2]*1.02)];gold_points=p[np.unique(tri[gold])];gold_tree=cKDTree(gold_points);names=[d['nodes'][n]['name'] for n in d['skins'][0]['joints']];anchor=names.index('Bone_003')
parents=np.arange(len(gold_points))
def find(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
 return i
for a,b in gold_tree.query_pairs(.04):parents[find(b)]=find(a)
clusters={}
for i in range(len(gold_points)):clusters.setdefault(find(i),[]).append(i)
notches=[]
for ids in clusters.values():
 if len(ids)<15:continue
 pts=gold_points[ids];xy=pts[:,:2]-center;angles=np.arctan2(xy[:,1],xy[:,0]);middle=float(np.arctan2(xy[:,1].mean(),xy[:,0].mean()));delta=np.angle(np.exp(1j*(angles-middle)));width=float(abs(delta).max())+.01
 notches.append((middle,width,-.432))
assert len(notches) in [4,5],notches
segments=192
# Inner opening / rolled silver lip / blue perimeter / fitted rear casing.
profile=[(.230,-.434),(.235,-.457),(.245,-.488),(.260,-.490),(.273,-.474),(.285,-.451),(.290,-.431),(.290,None),(.278,None),(.236,None),(.230,-.400)]
vertices=[];nprofile=len(profile)
for i in range(segments):
 a=2*np.pi*i/segments;c,s=np.cos(a),np.sin(a);rear=float(np.interp(a,np.r_[theta[-1]-2*np.pi,theta,theta[0]+2*np.pi],np.r_[zback[-1],zback,zback[0]]))+.006
 for k,(r,z) in enumerate(profile):
  xy=center+np.array([c,s])*r
  if z is None:z=rear+(.002 if k in [8,9] else 0)
  if k<5:
   # Smooth, constant-depth hardware pockets avoid noisy per-vertex notches.
   for middle,width,target in notches:
    delta=abs(float(np.angle(np.exp(1j*(a-middle)))))
    fade=1.0 if delta<=width else .5+.5*np.cos(np.pi*(delta-width)/.10) if delta<width+.10 else 0.0
    z=z+max(0,target-z)*fade
  vertices.append([xy[0],xy[1],z])
v=np.asarray(vertices,dtype=np.float32);silver=[];blue=[]
for i in range(segments):
 for k in range(nprofile):
  a=i*nprofile+k;b=((i+1)%segments)*nprofile+k;c=((i+1)%segments)*nprofile+(k+1)%nprofile;dd=i*nprofile+(k+1)%nprofile
  target=silver if k<4 else blue
  target.extend([[a,b,c],[a,c,dd]])
t=np.asarray(silver+blue,dtype=np.int64)
# Make the closed annular surface point outward consistently.
volume=float(np.einsum('ij,ij->i',v[t[:,0]],np.cross(v[t[:,1]],v[t[:,2]])).sum()/6)
if volume<0:
 silver=[ft[::-1] for ft in silver];blue=[ft[::-1] for ft in blue];t=t[:,::-1];volume=-volume
normal=np.zeros_like(v)
for ft in t:
 n=np.cross(v[ft[1]]-v[ft[0]],v[ft[2]]-v[ft[0]])
 for vi in ft:normal[vi]+=n
normal/=np.linalg.norm(normal,axis=1)[:,None]
m,e,g,deg=topology(v,t);assert not g and not deg and all(len(fs)==2 for fs in e.values())
weights=np.zeros((len(v),4),dtype='<f4');weights[:,0]=1;joints=np.zeros((len(v),4),dtype='<u2');joints[:,0]=anchor
uv=np.zeros((len(v),2),dtype='<f4')
for i in range(segments):
 for k in range(nprofile):uv[i*nprofile+k]=[i/segments,k/nprofile]
outblob=blob+b'\0'*((-len(blob))%4)
def append(array,component,kind,target,position=False):
 global outblob
 outblob+=b'\0'*((-len(outblob))%4);offset=len(outblob);data=array.tobytes();outblob+=data;vi=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(data),'target':target});ai=len(d['accessors']);a={'bufferView':vi,'componentType':component,'count':len(array),'type':kind}
 if position:a['min']=array.min(0).tolist();a['max']=array.max(0).tolist()
 d['accessors'].append(a);return ai
attrs={'POSITION':append(v,5126,'VEC3',34962,True),'NORMAL':append(normal,5126,'VEC3',34962),'TEXCOORD_0':append(uv,5126,'VEC2',34962),'JOINTS_0':append(joints,5123,'VEC4',34962),'WEIGHTS_0':append(weights,5126,'VEC4',34962)}
for label,faces,color,metal,rough in [('Continuous silver moon rim',silver,[.20,.22,.30,1],.5,.34),('Circular blue backplate casing',blue,[.045,.06,.36,1],.2,.48)]:
 mat=len(d['materials']);d['materials'].append({'name':label,'pbrMetallicRoughness':{'baseColorFactor':color,'metallicFactor':metal,'roughnessFactor':rough}});d['meshes'][0]['primitives'].append({'attributes':attrs.copy(),'indices':append(np.asarray(faces,dtype='<u2').reshape(-1,1),5123,'SCALAR',34963),'material':mat,'mode':4})
d['buffers'][0]['byteLength']=len(outblob)
for k in ['nodes','skins','images','textures','samplers','scene','scenes','animations']:assert d.get(k)==original.get(k),k
assert d['materials'][:len(original['materials'])]==original['materials'];assert d['meshes'][0]['primitives'][:len(original['meshes'][0]['primitives'])]==original['meshes'][0]['primitives']
js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);outblob+=b'\0'*((-len(outblob))%4);dest=OUT/'shoebill-circular-moon-rim-v2.glb';dest.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(outblob))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(outblob),0x004e4942)+outblob)
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'joint_count':38,'before_triangles':25962,'final_triangles':25962+len(t),'new_frame_triangles':len(t),'frame_segments':segments,'circular_outer_radius_m':.290,'moon_window_radius_m':.230,'plate_center_gltf_xy':center.tolist(),'frame_positive_volume_m3':volume,'new_frame_rigid_attachment':'Bone_003, existing plate/body control','all_prior_primitives_attributes_weights_and_source_binary_preserved':True,'skeleton_hierarchy_rest_binds_unchanged':True,'original_moon_face_rim_brass_mounts_body_and_wings_geometry_unchanged':True,'added_materials':['Continuous silver moon rim','Circular blue backplate casing'],'scope':'User confirmed a circular rim with moon design visible. Added a smooth circular silver rim and fitted blue outer casing over exposed gray backing. Original brass mounts remain visible in fitted recesses; original rig and weights unchanged.'}
(OUT/'repair-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
