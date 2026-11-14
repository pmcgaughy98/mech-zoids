import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'run1'))
import build as old
b=old.b
for d in ['walk/frames','walk/layers','source']:(R/d).mkdir(parents=True,exist_ok=True)
(R/'REPORT.txt').write_text('fennec-trot35-run2. Tokens: unavailable.\nPart 1 ne repair underway; run1 layers and native translation method reused.\n')
for v in ['s','n','e','ne']:
 a=old.load(R/f'stills/{v}.png')
 Image.fromarray(a).crop((55,105,130,167)).resize((750,620),Image.Resampling.NEAREST).save(R/f'{v}_inspect.png')
 if v in ['e','ne']:
  ref,parts,body,tail=old.sources(v)
  for name,im in [('body',body),('tail',tail)]:Image.fromarray(im).save(R/f'source/{v}_{name}.png')
  for n,pp in parts.items():
   for name,im in pp.items():Image.fromarray(im).save(R/f'source/{v}_{n}_{name}.png')
  gold=np.logical_or.reduce([np.all(a[:,:,:3]==bytes.fromhex(h),axis=2) for h in []]) if False else None
  if v=='e':
   for f in range(-1,8):
    im=a if f<0 else old.load(R.parent/f'run1/walk/frames/e_f{f}.png')
    mask=np.logical_or.reduce([np.all(im[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['fff4d6','f0d27a','b8923a']])
    print(f,[(len(c),(min(x for y,x in c),min(y for y,x in c),max(x for y,x in c),max(y for y,x in c))) for c in b.pieces(mask)])
