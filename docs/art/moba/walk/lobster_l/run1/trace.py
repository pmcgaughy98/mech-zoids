from PIL import Image,ImageDraw
from pathlib import Path
R=Path(__file__).resolve().parent
for v in ['e','se','ne']:
 im=Image.open(R/f'stills/{v}.png').convert('RGBA');box={'e':(65,125,141,162),'se':(45,94,145,157),'ne':(85,89,155,149)}[v]
 cr=im.crop(box);o=Image.new('RGBA',(cr.width*10+40,cr.height*10+40),(65,73,70));o.alpha_composite(cr.resize((cr.width*10,cr.height*10),Image.Resampling.NEAREST),(40,40));d=ImageDraw.Draw(o)
 for x in range(box[0],box[2]):
  if x%5==0:d.text(((x-box[0])*10+40,20),str(x),fill='white')
 for y in range(box[1],box[3]):
  if y%5==0:d.text((4,(y-box[1])*10+40),str(y),fill='white')
 o.save(R/f'{v}_trace.png')
