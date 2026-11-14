from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
R=Path(r'D:/dev/new-mech-rpg/docs/art/moba/wolf_m/take-b/anim/codex-walk2')
a=Image.open(R.parent.parent/'fixed/e.png').convert('RGBA')
# Contact registration at center of sole silhouette; far soles end at y158 in the still.
paws={'near_fore':{'x':114,'y':160,'span':[108,119],'pair':'A'},'far_hind':{'x':79,'y':158,'span':[74,84],'pair':'A'},'far_fore':{'x':120,'y':158,'span':[114,125],'pair':'B'},'near_hind':{'x':68,'y':160,'span':[62,73],'pair':'B'}}
paths={'A':[(8,0),(3,0),(-2,0),(-7,0),(-4,2),(-1,4),(2,4),(5,2)],'B':[(-4,2),(-1,4),(2,4),(5,2),(8,0),(3,0),(-2,0),(-7,0)]}
cols={'near_fore':'#4effd2','far_hind':'#34a5ff','far_fore':'#ffbd43','near_hind':'#ff57cd'}
k=4;cw=512;ch=410
board=Image.new('RGB',(cw*8,ch),(40,44,49));d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
for f in range(8):
 faded=Image.new('RGBA',(192,192),(40,44,49,255));tmp=a.copy();tmp.putalpha(tmp.getchannel('A').point(lambda x:int(x*.32)));faded.alpha_composite(tmp)
 im=faded.crop((32,88,160,169)).resize((512,324),Image.Resampling.NEAREST);board.paste(im,(f*cw,48))
 d.text((f*cw+8,4),f'f{f} A {paths["A"][f]}  B {paths["B"][f]}',font=font,fill='white')
 d.line((f*cw,48+(160-88)*k,f*cw+511,48+(160-88)*k),fill=(90,100,104))
 for name,p in paws.items():
  off,lift=paths[p['pair']][f];x=f*cw+(p['x']+off-32)*k;y=48+(160-lift-88)*k
  if name.startswith('far'):d.rectangle((x-5,y-5,x+5,y+5),outline=cols[name],width=2)
  else:d.ellipse((x-5,y-5,x+5,y+5),outline=cols[name],width=2)
  d.line((x-7,y,x+7,y),fill=cols[name],width=1);d.line((x,y-7,x,y+7),fill=cols[name],width=1)
 d.text((f*cw+7,380),'A cyan fore / blue hind; B gold fore / pink hind',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12),fill='white')
board.save(R/'pose_guide.png')
json.dump({'still_paws':paws,'paths':paths,'ground':160,'duration_ms':100,'note':'Far soles normalized from perspective row158 to shared gameplay ground160; x remains measured still contact center.'},open(R/'targets.json','w'),indent=2)
# Annotated native pixel inspection.
im=a.crop((38,92,154,164)).resize((928,576),Image.Resampling.NEAREST);bg=Image.new('RGBA',im.size,(75,80,80,255));bg.alpha_composite(im);dr=ImageDraw.Draw(bg)
for x in range(40,154,5):dr.text(((x-38)*8,0),str(x),fill='yellow')
for y in range(95,164,5):dr.text((0,(y-92)*8),str(y),fill='yellow')
bg.save(R/'still_measure.png')
