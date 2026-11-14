from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
for v in ['e','se','ne']:
 body=np.array(Image.open(R/f'source/{v}_body.png').convert('RGBA'));print(v)
 for n in ['R3','R2','R1']:
  part=np.array(Image.open(R/f'source/{v}_{n}_native.png').convert('RGBA'));yy,xx=np.where(part[:,:,3]>0);l,r=int(xx.min()),int(xx.max());row=[]
  for x in [l-1,r+1]:
   yy=np.where(body[:,x,3]>0)[0];row.append(int(yy.max()) if len(yy) else None)
  err=[]
  if all(y is not None for y in row):
   for x in range(l,r+1):
    yy=np.where(body[:,x,3]>0)[0]
    if len(yy):err.append(float(yy.max()-np.interp(x,[l-1,r+1],row)))
  print(n,l,r,row,max(err,default=None))
