from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent
for label,folder in [('approved',P.parent/'views'),('new',P/'slices')]:
 for d in ['s','se','e','ne','n']:
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); m=a[:,:,3]>0; yy,xx=np.where(m); low=yy.min()+np.ptp(yy)*.55
  steel=m&np.any(np.stack([np.all(a[:,:,:3]==tuple(bytes.fromhex(c)),axis=2) for c in ['d6d6dc','9d9ba2','58555e']]),axis=0)
  l,k=ndi.label(steel,np.ones((3,3))); groups=[]
  for i in range(1,k+1):
   y,x=np.where(l==i)
   if len(x)>=5 and y.max()>low: groups.append((len(x),[int(x.min()),int(y.min()),int(x.max()),int(y.max())]))
  print(label,d,groups)
# Context: reject disconnected warm jaw pixels accidentally within a lens bounding box.
p=P/'finish.py'; s=p.read_text(); key='lens_regions=[]\ncolours='
s=s.replace(key,"""labs,num=ndi.label(lens,np.ones((3,3)))
for k in range(1,num+1):
 if (labs==k).sum()==1:
  lens[labs==k]=False
lens_regions=[]
colours=""")
p.write_text(s)
