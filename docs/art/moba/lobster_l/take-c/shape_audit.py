from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
P=Path(__file__).resolve().parent
metrics=json.loads((P/'metrics.json').read_text()); sizes=metrics['sizes']; eyes={}
for d in ['s','se','sw','e','w']:
 a=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA')); m=a[:,:,3]>0
 lens=m & (np.all(a[:,:,:3]==(95,240,255),axis=2)|np.all(a[:,:,:3]==(232,255,255),axis=2))
 lab,num=ndimage.label(lens,np.ones((3,3))); components=[]
 for i in range(1,num+1):
  yy,xx=np.where(lab==i)
  components.append({'pixels':len(yy),'centre_xy':[float(xx.mean()),float(yy.mean())],'bottom_y':int(yy.max()),'height_share':float((160-yy.mean())/sizes[d][1])})
 eyes[d]=components
(P/'eye-metrics.json').write_text(json.dumps(eyes,indent=2))
shares=[c['height_share'] for cs in eyes.values() for c in cs]
lines=['Every view W x H: '+', '.join(f'{d} {v[0]}x{v[1]}' for d,v in sizes.items()),f'East/south height {sizes["e"][1]}/{sizes["s"][1]}={sizes["e"][1]/sizes["s"][1]:.4f}; north/south {sizes["n"][1]/sizes["s"][1]:.4f}.','Eye centres above foot baseline y160 / view height: '+', '.join(d+': '+str([round(c['height_share'],4) for c in cs]) for d,cs in eyes.items()),f'Eye height spread {(max(shares)/min(shares)-1):.2%}; within 10%: {max(shares)/min(shares)<=1.1}.', 'Rear cyan/glint pixels: '+(P/'cyan-counts.json').read_text()]
(P/'shape-numbers.txt').write_text('\n'.join(lines)); print('\n'.join(lines))
