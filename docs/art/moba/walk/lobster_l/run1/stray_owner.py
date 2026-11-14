from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
for p in (R/'walk/layers').glob('se_*_f0.png'):
 a=np.array(Image.open(p).convert('RGBA'));pts=[(122,67),(123,68)]
 hits=[(y,x,bytes(a[y,x,:3]).hex()) for y,x in pts if a[y,x,3]]
 if hits:print(p.name,hits)
