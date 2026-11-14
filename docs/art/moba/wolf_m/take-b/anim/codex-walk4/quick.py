from pathlib import Path
import json,numpy as np
from PIL import Image
from scipy import ndimage as ndi
R=Path(__file__).parent
r=json.loads((R/'rig.json').read_text());t=json.loads((R/'targets.json').read_text())
for view in ['se','ne']:
 print(view)
 for name in t['views'][view]['paws']:
  pts=[];errors=[];length=[]
  for rr in [z for z in r[view] if z['name']==name]:
   a=np.array(Image.open(R/'walk/layers'/f"{view}_{name}_f{rr['frame']}.png"));yy,xx=np.where(a[:,:,3]>0);y=yy.max();xs=np.where(a[y,:,3]>0)[0];p=np.array([(xs.min()+xs.max())/2,y]);errors.append(np.abs(p-rr['target']).tolist());length.append(np.abs(np.array(rr['lengths'])-rr['length_reference']).tolist())
   if rr['lift']==0:pts.append(p+rr['frame']*np.array(t['views'][view]['screen_step_5']))
  print(name,'error',np.max(errors,axis=0),'lock',np.ptp(pts,axis=0),'length',np.max(length,axis=0))
 for f in range(8):
  a=np.array(Image.open(R/'walk/frames'/f'{view}_f{f}.png'));mask=a[:,:,3]>0;lab,n=ndi.label(mask,np.ones((3,3)));print(f,'components',n,'sizes',np.bincount(lab.ravel())[1:])
