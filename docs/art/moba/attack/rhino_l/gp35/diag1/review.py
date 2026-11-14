import sys,importlib.util
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
from pathlib import Path
P=Path(__file__).resolve().parent
TAKE=Path('D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a')
NAMES=['se','ne']
def arr(p):return np.array(Image.open(p).convert('RGBA'))
def note(s):
 with (P/'REPORT.txt').open('a') as f:f.write(s+'\n')
def main():
 frames={v:[arr(P/'frames'/f'{v}_f{i}.png') for i in range(6)] for v in NAMES}
 still={v:arr(TAKE/'views_cam35_touchup'/f'{v}.png') for v in NAMES}
 # Exact import without executing source main or touching its directory.
 spec=importlib.util.spec_from_file_location('rhino_selout',TAKE/'anim/selout_rhino.py'); module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 assert module.OUTLINE.tolist()==[20,18,24]
 sd=P/'frames_selout';sd.mkdir(exist_ok=True);sel={};stsel={}
 for v in NAMES:
  sel[v]=[]; stsel[v]=Image.fromarray(module.selout(still[v])[0])
  for i,a in enumerate(frames[v]):
   z=Image.fromarray(module.selout(a)[0]);z.save(sd/f'{v}_f{i}.png');sel[v].append(z)
 def board(scale,path):
  cw=192*scale;ch=192*scale+20;b=Image.new('RGB',(7*cw,2*ch),(128,128,128));d=ImageDraw.Draw(b)
  for r,v in enumerate(NAMES):
   for c,z in enumerate([stsel[v]]+sel[v]):
    z=z.resize((cw,cw),Image.Resampling.NEAREST);b.paste(z,(c*cw,r*ch+20),z);d.text((c*cw+4,r*ch+4),v+' '+('still' if c==0 else 'f'+str(c-1)),fill='white')
  b.save(P/path)
 board(4,'review.png');board(1,'strip_1x.png')
 b=Image.new('RGB',(4*350,2*420),(128,128,128));d=ImageDraw.Draw(b)
 for r,v in enumerate(NAMES):
  for c,(label,z) in enumerate([('still',stsel[v])]+[(f'f{i}',sel[v][i]) for i in [2,3,4]]):
   z=z.crop((45,85,115,165)).resize((350,400),Image.Resampling.NEAREST);b.paste(z,(c*350,r*420+20),z);d.text((c*350+5,r*420+4),v+' '+label,fill='white')
 b.save(P/'legs_5x.png')
 for v in NAMES:
  gifs=[]
  for z in sel[v]:
   bg=Image.new('RGB',(768,768),(128,128,128));z=z.resize((768,768),Image.Resampling.NEAREST);bg.paste(z,(0,0),z);gifs.append(bg)
  gifs[0].save(P/f'preview_{v}.gif',save_all=True,append_images=gifs[1:],duration=[100,100,100,200,300,300],loop=0,disposal=2,optimize=False)
 note('Step 5 complete: sel-out copies, labelled review 4x / strip 1x / joints 5x and three timed GIFs saved.');print('review assets complete')

if __name__=='__main__':main()
