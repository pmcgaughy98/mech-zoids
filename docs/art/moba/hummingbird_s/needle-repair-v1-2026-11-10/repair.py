import sys,json,copy,hashlib,struct
from pathlib import Path
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import *
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10');OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path('D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_hummingbird_remeshed_25k_20261111_character.glb');d,b=read_glb(SOURCE);old=copy.deepcopy(d);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);norm=accessor(d,b,pr['attributes']['NORMAL']);tri=accessor(d,b,pr['indices']).reshape(-1,3)
z0=.30;z1=float(p[:,2].max());mask=p[:,2]>z0;pts=p[mask];bins=[]
for z in np.arange(.25,z1+.025,.04):
 q=p[abs(p[:,2]-z)<.035]
 if len(q):bins.append([z,*((q.min(0)+q.max(0))*.5)[:2]])
bins=np.array(bins);new=p.copy()
for i in np.where(mask)[0]:
 x,y,z=p[i];ox=np.interp(z,bins[:,0],bins[:,1]);oy=np.interp(z,bins[:,0],bins[:,2]);t=(z-z0)/(z1-z0)
 dx=x-ox;dy=y-oy;r=max(abs(dx)+abs(dy),1e-7);rx=.040*(1-t)+.001*t;ry=.046*(1-t)+.001*t;axis_y=1.260+(1.075-1.260)*t;axis_x=-.003
 target=np.array([axis_x+dx/r*rx,axis_y+dy/r*ry,z]);blend=min(1,max(0,(z-z0)/.09));blend=blend*blend*(3-2*blend);new[i]=p[i]*(1-blend)+target*blend
delta=np.linalg.norm(new-p,axis=1);moved=delta>1e-7
# Area-weighted local normals; unchanged vertices keep their exact source data.
cross=np.cross(new[tri[:,1]]-new[tri[:,0]],new[tri[:,2]]-new[tri[:,0]]);acc=np.zeros_like(new)
for col in range(3):np.add.at(acc,tri[:,col],cross)
nn=norm.copy();length=np.linalg.norm(acc,axis=1);valid=moved&(length>1e-10);nn[valid]=acc[valid]/length[valid,None]
payload=b
def append(values,name):
 global payload
 payload+=b'\0'*((-len(payload))%4);off=len(payload);raw=values.astype('<f4').tobytes();payload+=raw;view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(raw),'target':34962});a={'bufferView':view,'componentType':5126,'count':len(values),'type':'VEC3'}
 if name=='POSITION':a.update(min=values.min(0).tolist(),max=values.max(0).tolist())
 ai=len(d['accessors']);d['accessors'].append(a);pr['attributes'][name]=ai
append(new,'POSITION');append(nn,'NORMAL');d['buffers'][0]['byteLength']=len(payload);encoded=json.dumps(d,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);payload+=b'\0'*((-len(payload))%4);target=OUT/'hummingbird-rigged-straight-needle-v1.glb';target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(encoded)+len(payload))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(payload),0x004e4942)+payload)
for k in ['nodes','skins','materials','textures','images','samplers','animations']:assert d.get(k)==old.get(k)
check,cb=read_glb(target);assert cb[:len(b)]==b
for name in ['JOINTS_0','WEIGHTS_0','TEXCOORD_0']:assert np.array_equal(accessor(check,cb,pr['attributes'][name]),accessor(old,b,old['meshes'][0]['primitives'][0]['attributes'][name]))
beforetop=topology(p,tri);aftertop=topology(new,tri)
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'joints':len(d['skins'][0]['joints']),'triangles':len(tri),'vertices_changed':int(moved.sum()),'max_displacement_m':float(delta.max()),'protected_body_max_error':float(np.linalg.norm(new[~mask]-p[~mask],axis=1).max()),'needle_forward_extent_preserved':float(new[:,2].max())==z1,'axis_gltf_y_up':{'shaft_start_z':z0,'tip_z':z1,'base_xy':[-.003,1.26],'tip_xy':[-.003,1.075]},'weights_uvs_skeleton_binds_materials_textures_byte_preserved':True,'before_topology':{'boundaries':sum(len(v)==1 for v in beforetop[1].values()),'over_shared':sum(len(v)>2 for v in beforetop[1].values())},'after_topology':{'boundaries':sum(len(v)==1 for v in aftertop[1].values()),'over_shared':sum(len(v)>2 for v in aftertop[1].values())},'scope':'Needle straightening only; keep length and slight downward aim. Collar and body protected. Existing unrelated remesh topology remains unapproved.'}
(OUT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
