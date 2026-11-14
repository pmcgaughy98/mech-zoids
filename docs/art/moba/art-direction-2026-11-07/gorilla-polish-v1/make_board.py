from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
p=Path(__file__).parent
im=Image.new('RGB',(1536,810),'#161b22')
d=ImageDraw.Draw(im)
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
d.text((18,12),'CURRENT GORILLA | original, first graphic pass, refined finish | identical arena lighting',font=f,fill='white')
for i,(v,label) in enumerate([('A-original','Original export'),('C-graphic','Earlier graphic treatment'),('D-refined','Refined: softer edges, selective metal')]):
 x=i*512
 d.text((x+12,52),label,font=sm,fill='white')
 src=Image.open(p/f'{v}-1280x720-y45-d0.png')
 im.paste(src.crop((384,200,896,560)),(x,82))
 rear=Image.open(p/f'{v}-1280x720-y180-d0.png')
 im.paste(rear.crop((384,240,896,540)),(x,480))
d.text((18,452),'Three-quarter view above; back view below. Identical native-resolution crops, no added lighting.',font=sm,fill='#d6dce4')
d.text((18,785),'Static 2 m test scale. Original geometry and textures preserved; this pass changes material response only.',font=sm,fill='#d6dce4')
im.save(p/'gorilla-polish-comparison.png')
