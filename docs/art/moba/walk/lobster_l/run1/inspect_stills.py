from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
R=Path(__file__).resolve().parent
out=Image.new('RGB',(3*768,768),(60,70,65))
for i,v in enumerate(['e','se','ne']):
 a=Image.open(R/f'stills/{v}.png').convert('RGBA'); t=Image.new('RGBA',a.size,(60,70,65,255));t.alpha_composite(a);t=t.resize((768,768),Image.Resampling.NEAREST)
 d=ImageDraw.Draw(t)
 for x in range(32,168,10):d.line((x*4,340,x*4,680),fill=(90,100,95));d.text((x*4,320),str(x),fill='white')
 for y in range(90,171,10):d.line((120,y*4,680,y*4),fill=(90,100,95));d.text((100,y*4),str(y),fill='white')
 out.paste(t,(i*768,0))
out.save(R/'inspect_stills.png')
a=np.array(a);print('palette', sorted(set(tuple(c[:3]) for c in a[a[:,:,3]>0])))
T=json.loads((R/'targets.json').read_text());print(json.dumps(T['views']['e'],indent=1)[:3500])
