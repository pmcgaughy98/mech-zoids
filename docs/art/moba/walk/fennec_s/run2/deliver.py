import sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'run1'));import build as old
b=old.b;load=old.load;sel=b.load_selout();bg=(84,88,91,255);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
def view(v):
 frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)];ims=[load(R/f'stills/{v}.png')]+frames
 board=Image.new('RGBA',(768*9,800),bg);zoom=Image.new('RGBA',(300*9,300),bg);gif=[]
 for j,a in enumerate(ims):
  s=Image.fromarray(sel(a)[0]);board.alpha_composite(s.resize((768,768),Image.Resampling.NEAREST),(j*768,28));ImageDraw.Draw(board).text((j*768+8,3),v+' '+('still' if j==0 else f'f{j-1}'),font=font,fill='white')
  z=s.crop((73,113,121,167)).resize((240,270),Image.Resampling.NEAREST);zoom.alpha_composite(z,(j*300,28));ImageDraw.Draw(zoom).text((j*300+5,3),v+' '+('still' if j==0 else f'f{j-1}'),font=font,fill='white')
  if j:
   g=Image.new('RGBA',(576,576),bg);g.alpha_composite(s.resize((576,576),Image.Resampling.NEAREST));gif.append(g.convert('RGB'))
 board.convert('RGB').save(R/f'{v}_board.png');zoom.convert('RGB').save(R/f'{v}_legs_zoom.png')
 for k in [0,1]:zoom.crop((300*(1+4*k),0,300*(5+4*k),300)).convert('RGB').save(R/f'{v}_legs_half{k}.png')
 gif[0].save(R/f'{v}_preview.gif',save_all=True,append_images=gif[1:],duration=100,loop=0,disposal=2,optimize=False)
 # A compact whole-character review that keeps each source pixel at 3x.
 review=Image.new('RGBA',(350*5,450*2),bg)
 for j,a in enumerate(ims):
  col,row=(0,0) if not j else ((j-1)%4+1,(j-1)//4)
  s=Image.fromarray(sel(a)[0]).crop((45,23,145,169)).resize((300,438),Image.Resampling.NEAREST)
  review.alpha_composite(s,(col*350,row*450+12));ImageDraw.Draw(review).text((col*350,row*450),v+' '+('still' if j==0 else f'f{j-1}'),fill='white')
 review.convert('RGB').save(R/f'{v}_review.png')
def allboards():
 views=[v for v in ['ne','e','s','n'] if (R/f'walk/frames/{v}_f0.png').exists()]
 for v in views:view(v)
 out=Image.new('RGB',(768*9,800*len(views)),bg[:3])
 for i,v in enumerate(views):out.paste(Image.open(R/f'{v}_board.png'),(0,800*i))
 out.save(R/'board.png')
 views=[v for v in ['s','n'] if (R/f'{v}_legs_zoom.png').exists()];out=Image.new('RGB',(2700,300*len(views)),bg[:3])
 for i,v in enumerate(views):out.paste(Image.open(R/f'{v}_legs_zoom.png'),(0,300*i))
 out.save(R/'legs_zoom.png')
if __name__=='__main__':
 if len(sys.argv)>1:view(sys.argv[1])
 else:allboards()
