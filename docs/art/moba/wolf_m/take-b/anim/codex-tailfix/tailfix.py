"""Tail-only native RGBA edit. Reads approved side and immutable set A; all writes local."""
from pathlib import Path
import math,json,hashlib,importlib.util
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
SRC=R.parent/'codex-set-a'; STILL=R.parent.parent/'fixed/e.png'
PAL=[tuple(bytes.fromhex(c)) for c in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()]
spec=importlib.util.spec_from_file_location('sel',str(R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py'));sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel);sel.OUTLINE=np.array(PAL[0],np.uint8)
ref=np.array(Image.open(STILL).convert('RGBA')); yy,xx=np.indices((192,192))
# Entire three metal plates and terminal red plate, up to the root under the fin.
mask=(yy>=119)&(yy<=156)&(xx<=69)&(ref[:,:,3]>0)
for y in range(129,157):
 # Separation from the hindleg uses the approved transparent gutter.
 mask[y, [68,67,66,65,64,63,61,61,60,60,59,58,56,56,55,55,54,53,51,49,48,47,46,45,45,44,43,43][y-129]+1:]=False
T=np.zeros_like(ref);T[mask]=ref[mask]
Image.fromarray(T).save(R/'reference_tail.png')
# angle is rigid rotation from the still. Root here is attachment (68,122),
# while measured reference tail axis remains (62,125) to (42,154).
W=[(75,122,0),(75,122,-1.5),(75,121,-2),(75,122,-1),(75,122,0),(75,122,1.5),(75,121,2),(75,122,1)]
S=[(74,125,49),(74,127,50),(73,121,51),(75,122,50),(76,125,49),(76,123,50)]

def transformed(root,angle):
 a=math.radians(angle);c,s=math.cos(a),math.sin(a)
 dx=xx-root[0];dy=yy-root[1]
 sx=np.rint(c*dx+s*dy+68).astype(int);sy=np.rint(-s*dx+c*dy+122).astype(int)
 ok=(sx>=0)&(sx<192)&(sy>=0)&(sy<192);b=np.zeros_like(T);b[ok]=T[sy[ok],sx[ok]]
 return b

def clean_sprint(t):
 # Hand-directed native contour pass: remove single-pixel rotation teeth,
 # restore continuous highlight/shadow bands without rescaling any plate.
 b=t.copy();m=b[:,:,3]>0;xs=np.where(m.any(0))[0]
 tops=np.array([np.where(m[:,x])[0].min() for x in xs]);bots=np.array([np.where(m[:,x])[0].max() for x in xs])
 top=ndi.median_filter(tops,size=3,mode='nearest');bot=ndi.median_filter(bots,size=3,mode='nearest')
 for j,x in enumerate(xs):
  lo,hi=int(top[j]),int(bot[j]);b[:lo,x]=0;b[hi+1:,x]=0
  for y in range(lo,hi+1):
   if b[y,x,3]==0:
    ys=np.where(m[:,x])[0];b[y,x]=t[ys[np.argmin(abs(ys-y))],x]
  # Keep terminal red shading intact. The metal crown and underside get
  # a clean two-tone bevel, like the broad bevels in the approved still.
  if tuple(b[lo,x,:3]) in [PAL[k] for k in [1,4,6,9]]:
   b[lo,x]=(*PAL[9],255)
   if hi-lo>5:b[lo+1,x]=(*PAL[6],255)
  if tuple(b[hi,x,:3]) in [PAL[k] for k in [0,1,4,6,9]]:
   b[hi,x]=(*PAL[1],255)
   if hi-lo>5:b[hi-1,x]=(*PAL[1],255)
 return b

def native(p):return np.array(Image.open(p).convert('RGBA'))
def preview(a):return Image.fromarray(sel.selout(a)[0])
records=[]
for move,params in [('walk',W),('sprint',S)]:
 out=R/move;(out/'frames').mkdir(parents=True,exist_ok=True)
 originals=[];new=[]
 for i,(rx,ry,ang) in enumerate(params):
  p=SRC/move/'frames'/f'side_f{i}.png';a=native(p);b=a.copy()
  old=np.zeros((192,192),bool)
  if move=='walk':old[118:129,:75]=True
  else:
   # Tail-only contour stops where each haunch begins, retaining the leg unchanged.
   top,bot,cut=[(121,130,76),(123,132,75),(119,128,73),(118,127,76),(120,130,76),(119,129,76)][i]
   old[top:bot+1,:cut]=True
   if i==2:old[127:129,64:]=False
   if i==1:old[133,:64]=True
  old &= a[:,:,3]>0
  b[old]=0
  t=transformed((rx,ry),ang)
  if move=='sprint':t=clean_sprint(t)
  tm=t[:,:,3]>0
  b[tm]=t[tm]
  # Root-local hand pixels integrate the plate crown with the rump.
  join=np.zeros((192,192),bool)
  offsets=[(0,-2,6),(1,-2,4),(1,-1,4),(1,0,1),(0,1,4),(1,1,1),(1,2,1)] if move=='walk' else [(1,-2,6),(2,-1,4),(2,0,4),(2,1,1),(1,2,1)]
  for dx,dy,k in offsets:
   x,y=rx+dx,ry+dy
   if a[y,x,3] or tm[y,x]:
    b[y,x]=(*PAL[k],255);join[y,x]=True
  bdiff=np.any(a!=b,2);outside=bdiff&~(old|tm)
  assert not (outside&~join).any()
  Image.fromarray(b).save(out/'frames'/f'side_f{i}.png')
  Image.fromarray((old.astype('uint8')*255)).save(out/f'old_tail_mask_f{i}.png')
  Image.fromarray((tm.astype('uint8')*255)).save(out/f'new_tail_mask_f{i}.png')
  Image.fromarray((join.astype('uint8')*255)).save(out/f'join_mask_f{i}.png')
  originals.append(a);new.append(b)
  records.append(dict(move=move,frame=i,root=[rx,ry],rotation_deg=ang,changed=int(bdiff.sum()),outside_tail=int(outside.sum()),rump_join_changes=int((bdiff&join&~(old|tm)).sum()),old_tail_pixels=int(old.sum()),new_tail_pixels=int(tm.sum()),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),length_axis_inclusive=36.23,plates=4))
 # 4x boards, approved leftmost, old row above repaired row.
 cw,ch=512,420;board=Image.new('RGBA',((len(params)+1)*cw,ch*2),(85,92,88,255));d=ImageDraw.Draw(board)
 for row,frames in enumerate([originals,new]):
  for col,a in enumerate([ref]+frames):
   im=preview(a).crop((28,85,156,183)).resize((512,392),Image.Resampling.NEAREST)
   board.alpha_composite(im,(col*cw,row*ch+24));d.text((col*cw+6,row*ch+5),('APPROVED STILL' if col==0 else f'{move} f{col-1} '+('SET A' if row==0 else 'TAIL FIX')),fill='white')
 board.convert('RGB').save(out/'board.png')
 pics=[]
 for a in new:
  im=Image.new('RGBA',(192,192),(85,92,88,255));im.alpha_composite(preview(a));pics.append(im.crop((28,85,156,169)).resize((512,336),Image.Resampling.NEAREST).convert('RGB'))
 pics[0].save(out/'preview.gif',save_all=True,append_images=pics[1:],duration=100 if move=='walk' else 70,loop=0,disposal=2,optimize=False)
(R/'measurements.json').write_text(json.dumps(records,indent=2)+'\n')
print('Wrote 14 frames, two boards and GIFs')
