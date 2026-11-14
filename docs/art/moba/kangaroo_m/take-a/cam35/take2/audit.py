"""Five-view kangaroo camera audit, adapted from EX audit.py; no sprite drawing."""
from pathlib import Path
import json, subprocess, os, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
P=Path(__file__).resolve().parent; TAKE=P.parent.parent; V=P/'views'; V.mkdir(exist_ok=True)
NAMES=['s','se','e','ne','n']; ALL=NAMES+['nw','w','sw']
AW=dict(zip(NAMES,[55,64,69,65,49])); AH=dict(zip(NAMES,[80,79,78,77,79]))
TW=dict(zip(NAMES,[55,64,69,65,49])); TH=dict(zip(NAMES,[73,80,83,89,90]))
ACC=dict(zip(NAMES,[7.8,7.7,7.5,6.0,5.8]))
pal=json.loads((P/'palette.json').read_text()); roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in pal}; valid=set(roles)
for d in NAMES: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
metrics={'approved':{},'new':{}}; edges={}; shape=[]; depth=[]; invalid={}; border={}; allpix=[]
for tag,folder in [('approved',TAKE/'fixed'),('new',P/'slices')]:
 for d in (NAMES if tag=='approved' else ALL):
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
  cs,counts=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/len(pix) for r in ['orange-red','steel','charcoal frame','eye','dark accent']}
  eye=np.zeros(m.shape,bool)
  for rgb,role in roles.items():
   if role=='eye': eye |= m & np.all(a[...,:3]==rgb,axis=2)
  labels,n=ndimage.label(eye,structure=np.ones((3,3)))
  groups=sorted([int((labels==i).sum()) for i in range(1,n+1)],reverse=True)
  lights={c:float((m&np.all(a[...,:3]==tuple(bytes.fromhex(c)),axis=2)).sum()/m.sum()) for c in ['ff8a4a','d6d6dc']}
  rec={'width':int(np.ptp(xx)+1),'height':int(np.ptp(yy)+1),'area':int(m.sum()),'role_shares':shares,'eye_pixels':int(eye.sum()),'eye_groups':groups,'light_shares':lights,'p05':float(np.percentile(lum,5)),'p95':float(np.percentile(lum,95)),'dominant_share':float(counts[k]/len(pix)),'dominant_colour':bytes(cs[k]).hex(),'lowest_row':int(yy.max()),'top_row':int(yy.min())}
  metrics[tag][d]=rec
  if d in NAMES:
   shape.append(f"{tag} {d}: "+'; '.join(f'{r} {v:.4%}' for r,v in shares.items())+f"; accent target {ACC[d]:.1f}%; light orange-red {lights['ff8a4a']:.3%}, steel {lights['d6d6dc']:.3%}; eyes {int(eye.sum())}, 8-connected groups {groups}; top/bottom {yy.min()}/{yy.max()}")
  if tag=='new':
   border[d]=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
   invalid[d]=[bytes(c).hex() for c in cs if tuple(c) not in valid]
   edge=m&~ndimage.binary_erosion(m); ec,ct=np.unique(a[edge,:3],axis=0,return_counts=True)
   edges[d]={'edge_pixels':int(edge.sum()),'colours':{c['hex']:{'edge_count':int(sum(n for rgb,n in zip(ec,ct) if bytes(rgb).hex()==c['hex'])),'body_count':int(sum(n for rgb,n in zip(cs,counts) if bytes(rgb).hex()==c['hex']))} for c in pal}}
   allpix.append(pix)
   if d in NAMES: depth.append(f"{d}: p05 {rec['p05']:.2f}; p95 {rec['p95']:.2f}; most common #{rec['dominant_colour']} {rec['dominant_share']:.2%}")
heights=[]
for d in NAMES:
 r=metrics['new'][d]
 heights.append(f"{d}: {r['width']}x{r['height']}; W/approved W {r['width']/AW[d]:.4f}; H/approved H {r['height']/AH[d]:.4f}; H/target {r['height']}/{TH[d]} = {r['height']/TH[d]:.4f}; top row {r['top_row']}; border {border[d]}")
spread=max(metrics['new'][d]['height']/AH[d] for d in NAMES)-min(metrics['new'][d]['height']/AH[d] for d in NAMES)
se_ne=metrics['new']['se']['height']/metrics['new']['ne']['height']
heights.append(f'H/approved H spread max-min {spread:.4f}; se/ne height {se_ne:.4f} ({metrics["new"]["se"]["height"]}/{metrics["new"]["ne"]["height"]}); target se a little less than ne. Rows zero-based; heights informational, no height repair.')
(P/'heights.txt').write_text('\n'.join(heights))
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = .2126 R + .7152 G + .0722 B, opaque pixels only.\n')
(P/'shape.txt').write_text('\n'.join(shape)+'\nEye misses: south each of two eyes below 2; se below 4; east below 3; any eye in ne/n. Approved s [2,2], se [6], east [4]. Observed rear eye pixels are a miss; preserved, not recoloured.\n')
(P/'palette-check.txt').write_text('Allowed fixed palette: '+', '.join(c['hex'] for c in pal)+'\n'+ '\n'.join(f'{d}: '+('PASS, no colours outside palette' if not invalid[d] else 'FAIL '+str(invalid[d])) for d in NAMES)+'\nAll eight border contacts: '+str(border))
cs,ct=np.unique(np.concatenate(allpix),axis=0,return_counts=True)
metrics.update(border_contact=border,top_five_share=float(np.sort(ct)[-5:].sum()/ct.sum()),colours=len(cs),height_spread=spread,se_ne=se_ne)
(P/'metrics.json').write_text(json.dumps(metrics,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
board=Image.new('RGB',(5*640,2*640),(128,128,128)); draw=ImageDraw.Draw(board)
for row,(tag,folder) in enumerate([('approved',TAKE/'fixed'),('new',V)]):
 for col,d in enumerate(NAMES):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); board.paste(im.resize((640,640),Image.Resampling.NEAREST),(col*640,row*640),im.resize((640,640),Image.Resampling.NEAREST)); draw.text((col*640+12,row*640+12),f'{tag} {d} - 4x',fill='white')
board.save(P/'review.png')
env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
for name in ['view_check','sheet_judge']:
 args=['python','-B',f'tools/art/{name}.py',str(P/'slices')]
 if name=='sheet_judge': args+=['--json',str(P/'sheet-judge.json')]
 result=subprocess.run(args,capture_output=True,text=True,env=env)
 txt=result.stdout+result.stderr
 (P/f'{name}.txt').write_text(txt+f'\nExit code: {result.returncode}\nHeights informational for elevated camera; no height repairs.\n')
 print(txt)
print('\n'.join(heights)); print('\n'.join(shape)); print('\n'.join(depth)); print('top5',metrics['top_five_share'])

(P/'shape.txt').write_text((P/'shape.txt').read_text()+'\n'+(P/'visual-audit.txt').read_text())
