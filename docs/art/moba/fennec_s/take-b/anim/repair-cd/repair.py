from pathlib import Path
import json, importlib.util, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
ROOT=Path(r'D:\dev\new-mech-rpg\docs\art\moba\fennec_s\take-b')
OUT=ROOT/'anim/repair-cd'
spec=importlib.util.spec_from_file_location('sel',ROOT.parents[1]/'rhino_l/take-a/anim/selout_rhino.py')
# actual sibling species under moba
spec=importlib.util.spec_from_file_location('sel',ROOT.parents[1]/'rhino_l/take-a/anim/selout_rhino.py')
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
MOVES={**{m:'c' for m in ['idle','walk','sand_kick','ear_burst','sonic_boom']},**{m:'d' for m in ['dig','pop_out','death']}}
def directory(m): return ROOT/f'anim/codex-set-{MOVES[m]}/{m}'
def files(m,v): return sorted((directory(m)/'frames').glob(f'{v}_f*.png'),key=lambda p:int(p.stem.split('_f')[1]))
def still(v):
    im=Image.new('RGBA',(192,192)); im.paste(Image.open(ROOT/f'views/{v}.png').convert('RGBA'),(16,20)); return im

def outlined(im): return Image.fromarray(mod.selout(np.array(im.convert('RGBA')))[0])
def tile(im,k=4):
    im=outlined(im).crop((48,72,144,164)).resize((96*k,92*k),Image.Resampling.NEAREST)
    bg=Image.new('RGBA',im.size,'#454953');bg.alpha_composite(im);return bg

def boards():
 for m in MOVES:
  for v in ['se','ne']:
   fs=files(m,v); ims=[still(v)]+[Image.open(p).convert('RGBA') for p in fs]
   board=Image.new('RGBA',(4*384,((len(ims)+3)//4)*392),'#454953');dr=ImageDraw.Draw(board)
   for j,im in enumerate(ims):
    x=(j%4)*384;y=(j//4)*392; board.alpha_composite(tile(im),(x,y+24));dr.text((x+4,y+5),'STILL' if j==0 else fs[j-1].stem,fill='white')
   board.save(OUT/f'inspect-{m}-{v}.png')
  fs=files(m,'se');n=len(fs)+1
  board=Image.new('RGBA',(n*288,4*302),'#454953');dr=ImageDraw.Draw(board)
  for row,(v,when) in enumerate([('se','before'),('se','after'),('ne','before'),('ne','after')]):
   ims=[still(v)]
   for p in files(m,v):
    old=p.parent.parent/'frames_pre_repair'/p.name
    ims.append(Image.open(old if when=='before' and old.exists() else p).convert('RGBA'))
   for j,im in enumerate(ims):
    board.alpha_composite(tile(im,3),(j*288,row*302+26));dr.text((j*288+4,row*302+5),f'{v} {when} '+('STILL' if j==0 else f'f{j-1}'),fill='white')
  board.save(OUT/f'repair-board-{m}.png')

def audit():
 palette={tuple(bytes.fromhex(x)) for x in ['141218','211e27','2e1a6e','3d3a44','6a3cc8','9d9ba2','a46bff','b8923a','d6d6dc','e0c8ff','f0d27a','3fe8b0','c8fff0','fff4d6','f6fffb']}
 result=[]
 for m in MOVES:
  for v in ['se','ne']:
   fs=files(m,v)
   for i,p in enumerate(fs):
    a=np.array(Image.open(p).convert('RGBA'));mask=a[:,:,3]>0
    labs,n=ndi.label(mask,np.ones((3,3)));sizes=np.bincount(labs.ravel())[1:]
    holes=ndi.binary_fill_holes(mask)&~mask
    lock=(i==0 and m not in ['walk','pop_out']) or (i==len(fs)-1 and m in ['idle','sand_kick','ear_burst','sonic_boom','pop_out'])
    r=dict(move=m,view=v,frame=i,bottom=int(np.where(mask)[0].max()),holes=int(holes.sum()),components=sizes.tolist(),palette=all(tuple(c) in palette for c in a[mask,:3]),alpha=set(np.unique(a[:,:,3]).tolist())<={0,255},edge=bool(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any()),locked=lock,still_equal=bool(np.array_equal(a,np.array(still(v)))) if lock else None)
    result.append(r)
 (OUT/'checks.json').write_text(json.dumps(result,indent=2))
 print('frames',len(result));print(json.dumps([r for r in result if r['holes'] or len(r['components'])>1 or r['bottom']!=160 or (r['locked'] and not r['still_equal']) or not r['palette'] or not r['alpha'] or r['edge']],indent=1))
if __name__=='__main__': boards();audit()
