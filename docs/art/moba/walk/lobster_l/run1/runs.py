from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
for v,x0,x1,lo in [('e',68,133,147),('se',48,94,109),('ne',104,151,118)]:
 a=np.array(Image.open(R/f'stills/{v}.png').convert('RGBA'));print(v)
 for y in range(lo,162):
  xs=np.where(a[y,x0:x1,3]>0)[0]+x0
  groups=np.split(xs,np.where(np.diff(xs)>1)[0]+1)
  print(y,[(int(g.min()),int(g.max())) for g in groups if len(g)])
