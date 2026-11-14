"""Five-view lobster camera audit, adapted from EX audit.py; no sprite drawing."""
from pathlib import Path
import json, subprocess, os, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
P=Path(__file__).resolve().parent; TAKE=P.parent; V=TAKE/'views_cam35'; V.mkdir(exist_ok=True)
NAMES=['s','se','e','ne','n']; ALL=NAMES+['nw','w','sw']
AW=dict(zip(NAMES,[89,114,124,112,81])); AH=dict(zip(NAMES,[66,63,55,65,66]))
TW=dict(zip(NAMES,[89,115,124,112,89])); TH=dict(zip(NAMES,[74,63,71,80,90]))
ACC=dict(zip(NAMES,[5.9,7.9,10.6,8.2,5.5]))
pal=json.loads((P/'palette.json').read_text()); roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in pal}; valid=set(roles)
for d in NAMES: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
metrics={'approved':{},'new':{}}; edges={}; shape=[]; depth=[]; invalid={}; border={}; allpix=[]
for tag,folder in [('approved',TAKE/'views'),('new',P/'slices')]:
 for d in (NAMES if tag=='approved' else ALL):
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
  cs,counts=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/len(pix) for r in ['gunmetal','red','steel','eye','accent']}
  eye=np.zeros(m.shape,bool)
  for rgb,role in roles.items():
   if role=='eye': eye |= m & np.all(a[...,:3]==rgb,axis=2)
  labels,n=ndimage.label(eye,structure=np.ones((3,3)))
  groups=sorted([int((labels==i).sum()) for i in range(1,n+1)],reverse=True)
  lights={c:float((m&np.all(a[...,:3]==tuple(bytes.fromhex(c)),axis=2)).sum()/m.sum()) for c in ['7e7e8e','f85a4a','eeeef2']}
  rec={'width':int(np.ptp(xx)+1),'height':int(np.ptp(yy)+1),'area':int(m.sum()),'role_shares':shares,'eye_pixels':int(eye.sum()),'eye_groups':groups,'light_shares':lights,'p05':float(np.percentile(lum,5)),'p95':float(np.percentile(lum,95)),'dominant_share':float(counts[k]/len(pix)),'dominant_colour':bytes(cs[k]).hex(),'lowest_row':int(yy.max()),'top_row':int(yy.min())}
  metrics[tag][d]=rec
  if d in NAMES:
   shape.append(f"{tag} {d}: "+'; '.join(f'{r} {v:.4%}' for r,v in shares.items())+f"; accent target {ACC[d]:.1f}%; light gunmetal {lights['7e7e8e']:.3%}, red {lights['f85a4a']:.3%}, steel {lights['eeeef2']:.3%}; eyes {int(eye.sum())}, 8-connected groups {groups}; top/bottom {yy.min()}/{yy.max()}")
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
 heights.append(f"{d}: {r['width']}x{r['height']}; W/approved W {r['width']/AW[d]:.4f}; H/approved H {r['height']/AH[d]:.4f}; H/W {r['height']/r['width']:.4f} vs target {TH[d]/TW[d]:.4f}; top row {r['top_row']}; border {border[d]}")
spread=max(metrics['new'][d]['height']/AH[d] for d in NAMES)-min(metrics['new'][d]['height']/AH[d] for d in NAMES)
se_ne=metrics['new']['se']['height']/metrics['new']['ne']['height']
heights.append(f'H/approved H spread max-min {spread:.4f}; se/ne height {se_ne:.4f} ({metrics["new"]["se"]["height"]}/{metrics["new"]["ne"]["height"]}); Rows zero-based; heights informational, no height repair.')
heights.append(f"east/south width {metrics['new']['e']['width']/metrics['new']['s']['width']:.4f} vs approved {124/89:.4f}; se/s height {metrics['new']['se']['height']/metrics['new']['s']['height']:.4f}; se/e height {metrics['new']['se']['height']/metrics['new']['e']['height']:.4f}")
(P/'heights.txt').write_text('\n'.join(heights))
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = .2126 R + .7152 G + .0722 B, opaque pixels only.\n')
(P/'shape.txt').write_text('\n'.join(shape)+'\nEye misses: south each below 30; se near below 30; east below 21; any eye in ne/n. Expected s 36+34, se 35+20, e 25. Approved s 44+41, se 43+24, e 30.\n')
(P/'palette-check.txt').write_text('Allowed fixed palette: '+', '.join(c['hex'] for c in pal)+'\n'+ '\n'.join(f'{d}: '+('PASS, no colours outside palette' if not invalid[d] else 'FAIL '+str(invalid[d])) for d in NAMES)+'\nAll eight border contacts: '+str(border))
cs,ct=np.unique(np.concatenate(allpix),axis=0,return_counts=True)
metrics.update(border_contact=border,top_five_share=float(np.sort(ct)[-5:].sum()/ct.sum()),colours=len(cs),height_spread=spread,se_ne=se_ne)
(P/'metrics.json').write_text(json.dumps(metrics,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
board=Image.new('RGB',(5*576,2*576),(128,128,128)); draw=ImageDraw.Draw(board)
for row,(tag,folder) in enumerate([('approved',TAKE/'views'),('new',V)]):
 for col,d in enumerate(NAMES):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); board.paste(im.resize((576,576),Image.Resampling.NEAREST),(col*576,row*576),im.resize((576,576),Image.Resampling.NEAREST)); draw.text((col*576+12,row*576+12),f'{tag} {d} - 3x',fill='white')
board.save(P/'review.png')
env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
for name in ['view_check','sheet_judge']:
 args=['python','-B',f'C:/Users/pmcga/dev/hollowtide/tools/art/{name}.py',str(P/'slices')]
 if name=='sheet_judge': args+=['--json',str(P/'sheet-judge.json')]
 result=subprocess.run(args,capture_output=True,text=True,env=env)
 txt=result.stdout+result.stderr
 (P/f'{name}.txt').write_text(txt+f'\nExit code: {result.returncode}\nHeights informational for elevated camera; no height repairs.\n')
 print(txt)
print('\n'.join(heights)); print('\n'.join(shape)); print('\n'.join(depth)); print('top5',metrics['top_five_share'])
