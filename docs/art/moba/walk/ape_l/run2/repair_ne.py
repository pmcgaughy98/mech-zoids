from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
import build as b
R=Path(__file__).resolve().parent;R1=R.parent/'run1';Y,X=b.Y,b.X
load=lambda p:np.array(Image.open(p).convert('RGBA'))
for d in ['source','walk/layers']:(R/d).mkdir(parents=True,exist_ok=True)
ref=load(R/'stills/ne.png')
# Knee, cuff, shin and complete orange foot are a single native translation.
m=b.mask([(60,122),(65,124),(66,128),(66,135),(70,137),(77,140),(78,145),(72,148),(60,149),(54,145),(54,136),(55,129),(57,126)])
src=b.piece(ref,m)
# Explicit hip contour, not the still's large flank plate.
b.D['ne']['LH'].update(root=(64,122),joint=(61,129),w=4)
body=load(R1/'source/ne_body.png');body[m]=0
Image.fromarray(body).save(R/'source/ne_body.png');Image.fromarray(src).save(R/'source/ne_LH.png')
for n in ['RF','RH','LF']:Image.open(R1/f'source/ne_{n}.png').save(R/f'source/ne_{n}.png')
rig=json.loads((R/'rig.json').read_text()) if (R/'rig.json').exists() else {};rig['ne']=[];frames=[]
for f in range(8):
 dip=int(f in [0,4]);orig=load(R1/f'walk/frames/ne_f{f}.png');scene=np.zeros_like(orig)
 layers={n:load(R1/f'walk/layers/ne_{n}_f{f}.png') for n in ['RF','RH','LF']}
 # The LF's invented support was pasted through the hind knee; retain its real shield/arm only.
 lf=layers['LF'].copy(); lf[Y>=128+int(json.loads((R1/'rig.json').read_text())['ne'][4*f+1]['delta'][1])]=0
 sole=b.support(src);target=np.array(b.T['views']['ne']['visible_feet']['LH']['frames'][f]['sole_centre']);dx,dy=np.floor(target-sole+.5).astype(int)
 limb=b.socket(b.D['ne']['LH'],int(dx),int(dy),dip);b.comp(limb,b.shift(src,dx,dy));raw=b.shift(src,dx,dy);bottom=int(sole[1]+dy);limb[Y>bottom]=0;limb[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
 b.comp(scene,lf);b.comp(scene,b.shift(body,0,dip));b.comp(scene,limb);b.comp(scene,layers['RH']);b.comp(scene,layers['RF'])
 # Local repair only. All pixels outside the repair window remain byte-exact.
 region=(X>=45)&(X<=81)&(Y>=123)&(Y<=154)
 out=orig.copy();out[region]=scene[region]
 holes=b.fill_holes(out[:,:,3]>0)&(out[:,:,3]==0)&region;out[holes]=b.P['22301d']
 # Old far-fist support left one isolated orange texel inside this repair.
 from collections import deque
 op=out[:,:,3]>0; seen=np.zeros_like(op); comps=[]
 for y,x in zip(*np.where(op)):
  if seen[y,x]:continue
  todo=[(y,x)];seen[y,x]=True;pts=[]
  while todo:
   yy,xx=todo.pop();pts.append((yy,xx))
   for ay in [-1,0,1]:
    for ax in [-1,0,1]:
     ny,nx=yy+ay,xx+ax
     if 0<=ny<192 and 0<=nx<192 and op[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  comps.append(pts)
 for cc in sorted(comps,key=len,reverse=True)[1:]:
  assert all(region[y,x] for y,x in cc)
  for y,x in cc:out[y,x]=0
 # Preserve every already-visible texel of the other native limbs.
 for name in ['RH','RF','LF']:
  other=layers[name].copy()
  if name=='LF':
   oldsrc=load(R1/'source/ne_LF.png');oldsrc[Y>=128]=0
   q=next(q for q in json.loads((R1/'rig.json').read_text())['ne'] if q['frame']==f and q['foot']=='LF');other=b.shift(oldsrc,*q['delta'])
  preserve=(other[:,:,3]>0)&np.all(other==orig,axis=2)
  out[preserve]=orig[preserve]
 Image.fromarray(out).save(R/f'walk/frames/ne_f{f}.png');frames.append(out)
 for n,la in {**layers,'LH':limb}.items():Image.fromarray(la).save(R/f'walk/layers/ne_{n}_f{f}.png')
 for rr in json.loads((R1/'rig.json').read_text())['ne'][4*f:4*f+4]:
  if rr['foot']=='LH':rr.update(delta=[int(dx),int(dy)],source_sole=sole.tolist())
  rig['ne'].append(rr)
# Same nine-cell arrangement as supplied defect sheet.
zoom=Image.new('RGB',(1466,544),(23,24,31));d=ImageDraw.Draw(zoom)
for j,a in enumerate([ref]+frames):
 col,row=(j%5,j//5);im=Image.fromarray(a).crop((38,112,96,166)).resize((290,270),Image.Resampling.NEAREST);tile=Image.new('RGBA',im.size,(58,63,72));tile.alpha_composite(im);zoom.paste(tile.convert('RGB'),(col*294,row*274));d.text((col*294+2,row*274+2),'still' if j==0 else str(j-1),fill='white')
zoom.save(R/'ne_repaired.png')
(R/'rig.json').write_text(json.dumps(rig,indent=2))
b.boards({'ne':frames})
(R/'REPORT.txt').write_text('ape-walk35-run2\nTokens: not available.\nPart 1: repaired ne; label LH retained (left hind knee/foot, separate from far forearm).\nNative grey knee and orange foot translated whole; hip join hand drawn.\nEvery pixel outside x45-81/y123-154 is identical to run1. Foot translations retained.\nPart 1 final pixel checks underway. Parts 2/3 outputs also present; full audit pending.\n')
print('ne built',b.support(src))
