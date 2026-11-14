from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage as ndi
import ast,json
BASE=Path(r'D:\dev\new-mech-rpg\docs\art\moba\fennec_s\take-b')
OUT=BASE/'anim/repair-ab'
MOVES={m:BASE/'anim'/s/m for s,ms in [('codex-set-a',['idle','walk','sand_kick','ear_burst','sonic_boom']),('codex-set-b',['dig','pop_out','death'])] for m in ms}
VIEWS={'front':'s','side':'e','back':'n'}
PAL=['141218','211e27','2e1a6e','3d3a44','6a3cc8','9d9ba2','a46bff','b8923a','d6d6dc','e0c8ff','f0d27a','3fe8b0','c8fff0','fff4d6','f6fffb']
COL=[tuple(bytes.fromhex(h))+(255,) for h in PAL]
OUTLINE=np.array([20,18,24],np.uint8)
source=Path(r'D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py').read_text()
node=next(x for x in ast.parse(source).body if isinstance(x,ast.FunctionDef) and x.name=='selout')
exec(compile(ast.Module(body=[node],type_ignores=[]),'selout','exec'))
def still(v):
 im=Image.new('RGBA',(192,192));im.alpha_composite(Image.open(BASE/'views'/f'{VIEWS[v]}.png').convert('RGBA'),(16,20));return im
def files(m,v):return sorted((MOVES[m]/'frames').glob(v+'_f*.png'),key=lambda p:int(p.stem.split('_f')[1]))
def tile(im):
 im=Image.fromarray(selout(np.array(im.convert('RGBA')))[0]);bg=Image.new('RGBA',im.size,'#737980');bg.alpha_composite(im);return bg.crop((24,24,176,164)).resize((608,560),Image.Resampling.NEAREST).convert('RGB')
def boards():
 for m,d in MOVES.items():
  n=len(files(m,'front'));b=Image.new('RGB',((n+1)*608,6*584),'#737980');dr=ImageDraw.Draw(b)
  for vi,v in enumerate(VIEWS):
   for row in range(2):
    y=(vi*2+row)*584
    ims=[still(v)]+[Image.open((d/'frames_pre_repair'/p.name) if row==0 and (d/'frames_pre_repair'/p.name).exists() else p) for p in files(m,v)]
    for j,im in enumerate(ims):
     b.paste(tile(im),(j*608,y+24));dr.text((j*608+8,y+5),f'{m} {v} '+('BEFORE' if row==0 else 'AFTER')+(' STILL' if j==0 else f' f{j-1}'),fill='white')
   # inspection strip keeps 4x source pixels
   b.crop((0,vi*1168,b.width,vi*1168+584)).save(OUT/f'inspect-{m}-{v}.png')
  b.save(OUT/f'repair-board-{m}.png')
if __name__=='__main__':boards()
