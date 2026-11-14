import sys
sys.dont_write_bytecode=True
import frontback as m
from PIL import Image,ImageDraw
import json
R=m.R;np=m.np;b=m.b
allflags={}
for v in ['ne','e','s','n']:
 st=m.load(R/f'stills/{v}.png');allflags[v]=[]
 board=Image.new('RGBA',(8*350,300),(75,80,84,255))
 for f in range(8):
  a=m.load(R/f'walk/frames/{v}_f{f}.png');sl=m.old.find_slits(a,st,int(f in [0,4]));holes=np.argwhere(b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0))
  allflags[v].append(sl);print(v,f,'slits',sl,'holes',holes.tolist())
  im=Image.fromarray(a);dr=ImageDraw.Draw(im)
  for x,y in sl:dr.point((x,y),fill='red')
  for y,x in holes:dr.point((int(x),int(y)),fill='cyan')
  board.alpha_composite(im.crop((57,117,127,170)).resize((350,265),Image.Resampling.NEAREST),(350*f,25));ImageDraw.Draw(board).text((350*f,0),f'{v} f{f}',fill='white')
 board.convert('RGB').save(R/f'{v}_seams_review.png')
(R/'seams_review.json').write_text(json.dumps(allflags,indent=2))
