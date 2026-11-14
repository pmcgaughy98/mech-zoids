"""One synchronous pass adapted from shoebill take C; preserve all amber lens tones."""
from pathlib import Path
from collections import Counter
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
LENS={(196,106,14),(255,176,46),(255,241,196)}
a=np.array(Image.open(P/'sheet_finished.png').convert('RGBA')); out=a.copy()
fixed=0
for y,x in zip(*np.where(a[...,3]>0)):
 if tuple(a[y,x,:3]) in LENS: continue
 nbrs=[tuple(a[yy,xx]) for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)) if 0<=yy<a.shape[0] and 0<=xx<a.shape[1] and a[yy,xx,3]>0]
 if not nbrs: continue
 if any(np.abs(a[y,x,:3].astype(int)-np.array(n[:3],int)).sum()<30 for n in nbrs): continue
 c=Counter(nbrs).most_common(1)[0][0]
 if c!=tuple(a[y,x]): out[y,x]=c; fixed+=1
Image.fromarray(out).save(P/'sheet_finished.png')
(P/'despeckle.json').write_text(json.dumps({'passes':1,'pixels_changed':fixed,'lens_colours_kept':list(map(list,LENS))},indent=2))
print('despeckle pixels changed',fixed)
