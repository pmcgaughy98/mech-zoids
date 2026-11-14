from pathlib import Path
import numpy as np
from scipy.ndimage import label
from PIL import Image
R=Path(__file__).resolve().parent
for v,span in [('e',(73,84)),('se',(58,71))]:
 a=np.array(Image.open(R/f'source/{v}_body.png').convert('RGBA'));l,r=span;rows=[np.where(a[:,x,3]>0)[0].max() for x in [l-1,r+1]];fill=np.array(Image.open(R/f'source/{v}_body_reconstruction_area.png').convert('RGBA'))[:,:,3]>0
 print(v,'belly')
 for x in range(l,r+1):
  yy=np.where(a[:,x,3]>0)[0]
  if len(yy):
   y=yy.max();limit=np.interp(x,[l-1,r+1],rows);print(x,y,round(limit,2),'fill',fill[y,x],bytes(a[y,x,:3]).hex())
for f in [0,1,7]:
 a=np.array(Image.open(R/f'walk/frames/se_f{f}.png').convert('RGBA'));labs,n=label(a[:,:,3]>0,np.ones((3,3)));sz=np.bincount(labs.ravel());big=sz[1:].argmax()+1
 for j in range(1,n+1):
  if j!=big:print('se',f,'stray',list(zip(*np.where(labs==j))))
