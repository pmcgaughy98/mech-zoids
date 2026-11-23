import io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10');from diagnose import *
r=Path(__file__).parent;c=json.loads((r/'input-audit.json').read_text());d,b=read_glb(c['source']);pr=d['meshes'][0]['primitives'][0];p=accessor(d,b,pr['attributes']['POSITION']);n=accessor(d,b,pr['attributes']['NORMAL']);uv=accessor(d,b,pr['attributes']['TEXCOORD_0']);t=accessor(d,b,pr['indices']).reshape(-1,3)
mat=d['materials'][pr.get('material',0)];ii=d['textures'][mat['pbrMetallicRoughness']['baseColorTexture']['index']]['source'];view=d['bufferViews'][d['images'][ii]['bufferView']];im=np.array(Image.open(io.BytesIO(b[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']])).convert('RGB'));u=uv[t].mean(1);col=im[np.clip((u[:,1]*im.shape[0]).astype(int),0,im.shape[0]-1),np.clip((u[:,0]*im.shape[1]).astype(int),0,im.shape[1]-1)].astype(float);pts=p[t].mean(1);nn=n[t].mean(1)
cyan=(col[:,1]>160)&(col[:,2]>150)&(col[:,1]>col[:,0]*1.25)&(col[:,2]>col[:,0]*1.25)
results=[]
for sign in [-1,1]:
 sel=cyan&(pts[:,0]*sign>.15)&(pts[:,2]<-2.4)&(nn[:,2]<-.5);points=pts[sel];ev,vec=np.linalg.eigh(np.cov(points.T));axis=vec[:,-1];axis*=np.sign(axis[0]);print(sign,len(points),points.round(4).tolist(),'axis',axis,'angle',np.degrees(np.arctan2(axis[1],axis[0])))
 results.append({'side':sign,'face_ids':np.where(sel)[0].tolist(),'original_panel_axis':axis.tolist(),'original_panel_angle_xy_degrees':float(np.degrees(np.arctan2(axis[1],axis[0])))})
(r/'panel-measurements.json').write_text(json.dumps(results,indent=2)+'\n')
