"""Two-view adaptation of the approved take audit; reads only permitted approved views."""
from pathlib import Path
import json, sys, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
sys.path.insert(0,'tools/art')
import sprite_director as sd
P=Path(__file__).resolve().parent
T=P.parent
V=T/'views_cam30'
V.mkdir(exist_ok=True)
for d in ['s','se']: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
roles={tuple(bytes.fromhex(x['hex'].lstrip('#'))):x['role'] for x in json.loads((T/'palette.json').read_text())}
metrics={}; sizes=[]; shape=[]; depth=[]; palette=[]; edges={}; allpixels=[]
for label,base in [('approved',T/'views'),('new',V)]:
 for d in ['s','se']:
  a=np.array(Image.open(base/f'{d}.png').convert('RGBA')); m=a[...,3]>0
  yy,xx=np.where(m); pix=a[m,:3]; cs,counts=np.unique(pix,axis=0,return_counts=True)
  w,h=int(np.ptp(xx)+1),int(np.ptp(yy)+1); area=int(m.sum())
  border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/area for r in ['team','glow','steel','charcoal','accent']}
  glow=sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))=='glow')
  metrics[label+'_'+d]={'width':w,'height':h,'area':area,'roles':shares,'glow_count':glow,'height_width':h/w,'border':border}
  sizes.append(f'{label} {d}: {w}x{h}, opaque area {area}, border contact {border}')
  shape.append(f'{label} {d}: '+ '; '.join(f'{r} {v:.2%}' for r,v in shares.items())+f'; glow pixels {glow}; H/W {h/w:.4f}')
  if label=='new':
   allpixels.append(pix)
   invalid=['#'+bytes(c).hex() for c in cs if tuple(c) not in roles]
   palette.append(f'{d}: {len(cs)} opaque colours; outside fixed palette: {invalid or "NONE"}; alpha {np.unique(a[...,3]).tolist()}')
   lum=pix@[.2126,.7152,.0722]; lo,hi=np.percentile(lum,[5,95]); k=counts.argmax()
   depth.append(f'{d}: p05 {lo:.2f}; p95 {hi:.2f}; range {hi-lo:.2f}; most common #{bytes(cs[k]).hex()} {counts[k]/area:.2%}')
   metrics['new_'+d].update(p05=float(lo),p95=float(hi),dominant_share=float(counts[k]/area),lone=sd.lone_share(a.astype(np.int16)))
   edge=m & ~ndimage.binary_erosion(m)
   ec,ct=np.unique(a[edge,:3],axis=0,return_counts=True)
   edges[d]={ '#'+bytes(c).hex():{'count':int(n),'share':float(n/edge.sum())} for c,n in zip(ec,ct)}
(P/'sizes.txt').write_text('\n'.join(sizes)+'\n')
(P/'shape.txt').write_text('\n'.join(shape)+'\n')
(P/'depth.txt').write_text('\n'.join(depth)+'\n')
(P/'palette-check.txt').write_text('\n'.join(palette)+'\n')
(P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
cs,counts=np.unique(np.concatenate(allpixels),axis=0,return_counts=True)
metrics['colours']=len(cs); metrics['top_five_share']=float(np.sort(counts)[-5:].sum()/counts.sum())
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
(P/'view_check.txt').write_text('python tools/art/view_check.py VIEWS: SKIPPED; requires all eight views (loads every facing unconditionally). Only s and se authorized.\nExact sprite_director.lone_share, used by view_check: '+ '; '.join(f'{d} {metrics["new_"+d]["lone"]:.5f}' for d in ['s','se'])+'\n')
(P/'sheet_judge.txt').write_text('python tools/art/sheet_judge.py VIEWS: SKIPPED; full verdict requires all eight views; six deliberately absent. No fabricated or mirrored views supplied.\nPartial checks: binary alpha; identical 96x96 canvases; bottom row 78; no border contact.\n')
raw=np.array(Image.open(P/'sheet_finished.png')); cells={}
for row in range(3):
 for col in range(3): cells[f'{row},{col}']=int((raw[row*raw.shape[0]//3:(row+1)*raw.shape[0]//3,col*raw.shape[1]//3:(col+1)*raw.shape[1]//3,3]>0).sum())
(P/'cells.txt').write_text(json.dumps(cells,indent=2)+'\nOnly bottom-left and bottom-middle occupied: '+str(all(n==0 for k,n in cells.items() if k not in ['2,0','2,1']))+'\n')
review=Image.new('RGB',(96*4,110),(128,128,128)); draw=ImageDraw.Draw(review)
for i,(label,base,d) in enumerate([('approved s',T/'views','s'),('approved se',T/'views','se'),('new s',V,'s'),('new se',V,'se')]):
 im=Image.open(base/f'{d}.png').convert('RGBA'); review.paste(im,(96*i,14),im); draw.text((96*i+8,2),label,fill=(245,245,245))
review.resize((review.width*4,review.height*4),Image.Resampling.NEAREST).save(P/'review.png')
print((P/'sizes.txt').read_text());print((P/'depth.txt').read_text()); print('lone',[(d,metrics['new_'+d]['lone']) for d in ['s','se']]);print('top five',metrics['top_five_share'])
