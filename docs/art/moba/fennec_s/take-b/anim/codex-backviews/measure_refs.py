from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
R=Path(r'D:\dev\new-mech-rpg\docs\art\moba\fennec_s\take-b\anim\codex-backviews')
for v in ['n','ne']:
 a=np.array(Image.open(R.parent.parent/'views'/f'{v}.png').convert('RGBA')); m=a[:,:,3]>0
 print(v,Image.fromarray(a).getbbox())
 for y in range(64,141,2):
  xs=np.where(m[y])[0];runs=[]
  if len(xs):
   for run in np.split(xs,np.where(np.diff(xs)>1)[0]+1):runs.append((int(run.min()),int(run.max())))
  print(y,runs)
 b=Image.new('RGB',(640,720),(80,86,80)); b.paste(Image.fromarray(a).crop((45,60,115,145)).resize((560,680),Image.Resampling.NEAREST),(40,20));d=ImageDraw.Draw(b)
 for x in range(45,116,5):
  xp=40+(x-45)*8; d.line((xp,20,xp,700),fill=(110,90,90));d.text((xp,704),str(x),fill='white')
 for y in range(60,146,5):
  yp=20+(y-60)*8;d.line((40,yp,600,yp),fill=(110,90,90));d.text((5,yp),str(y),fill='white')
 b.save(R/'refs'/f'{v}_coordinates.png')
