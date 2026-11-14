from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
P=Path(__file__).resolve().parent
a=np.array(Image.open(P/'sheet_finished.png')); rgb=a[:,:,:3]; vis=a[:,:,3]>0; lum=rgb@[.2126,.7152,.0722]
for limit in [65,75,85]:
 dark=vis&(lum<limit); narrow=dark&~ndi.binary_opening(dark,structure=np.ones((3,3))); seam=narrow&(ndi.maximum_filter(lum,size=5)-lum>48)&ndi.binary_erosion(vis)
 ink=np.all(rgb==(20,18,24),axis=2)
 print('limit',limit)
 for d,r,c in [('s',2,1),('se',2,0),('e',1,0),('ne',0,0),('n',0,1)]:
  sl=np.s_[r*a.shape[0]//3:(r+1)*a.shape[0]//3,c*a.shape[1]//3:(c+1)*a.shape[1]//3]
  print(d,int((seam&~ink)[sl].sum()),round((ink|seam)[sl].sum()/vis[sl].sum()*100,2))
