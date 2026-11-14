import sys
sys.dont_write_bytecode=True
import build as m
from pathlib import Path
import numpy as np
R=m.R
for v in ['e','ne']:
 t=m.load(R/f'source/{v}_tail.png')
 for f in [0,7]:
  s=m.b.shift(t,0,int(f in [0,4]));a=m.load(R/f'walk/frames/{v}_f{f}.png');yy,xx=np.where((s[:,:,3]>0)&np.any(a!=s,axis=2));print(v,f,[(int(x),int(y),bytes(s[y,x,:3]).hex(),bytes(a[y,x,:3]).hex()) for y,x in zip(yy,xx)])
