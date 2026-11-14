from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
codes={'141218':'0','26262e':'1','34343e':'2','555562':'3','7e7e8e':'4','9a9aa6':'5','b8b8c2':'6','eeeef2':'7','6a0a10':'a','c41216':'b','ee2c26':'c','f85a4a':'d'}
for v,box in [('e',(68,136,135,162)),('se',(48,103,95,155)),('ne',(104,103,151,146))]:
 a=np.array(Image.open(R/f'stills/{v}.png').convert('RGBA'));x0,y0,x1,y1=box
 print(v, 'tens', ''.join(str(x//10%10) for x in range(x0,x1)));print('      '+''.join(str(x%10) for x in range(x0,x1)))
 for y in range(y0,y1):print(f'{y:3}   '+''.join(codes.get(bytes(a[y,x,:3]).hex(),'?') if a[y,x,3] else '.' for x in range(x0,x1)))
