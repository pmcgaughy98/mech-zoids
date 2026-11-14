"""Approved audit adapted for camera comparison, fixed palette, roles and five-view review."""
from pathlib import Path
import json, subprocess, os, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
P=Path(__file__).resolve().parent; TAKE=P.parent; V=TAKE/'views_cam30'; V.mkdir(exist_ok=True)
NAMES=['s','se','e','ne','n']; ALL=['s','se','e','ne','n','nw','w','sw']
pal=json.loads((TAKE/'palette.json').read_text()); roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in pal}; valid=set(roles)
for d in NAMES: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
metrics={}; edges={}; sizes=[]; shape=[]; depth=[]; invalid={}; border={}; allpix=[]
for tag,folder in [('approved',TAKE/'views'),('new',P/'slices')]:
 metrics[tag]={}
 for d in (NAMES if tag=='approved' else ALL):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); a=np.array(im); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
  cs,counts=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/len(pix) for r in ['yellow','steel','charcoal','eye','accent']}
  eye=sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))=='eye')
  rec={'width':int(np.ptp(xx)+1),'height':int(np.ptp(yy)+1),'area':int(m.sum()),'role_shares':shares,'eye_pixels':eye,'p05':float(np.percentile(lum,5)),'p95':float(np.percentile(lum,95)),'dominant_share':float(counts[k]/len(pix)),'dominant_colour':bytes(cs[k]).hex(),'lowest_row':int(yy.max())}
  metrics[tag][d]=rec
  if d in NAMES:
   shape.append(f"{tag} {d}: "+'; '.join(f'{r} {v:.4%}' for r,v in shares.items())+f"; eye pixels {eye}; height/width {rec['height']/rec['width']:.4f}; lowest opaque row {yy.max()}; foot rows: see visual notes below")
  if tag=='new':
   border[d]=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
   invalid[d]=[bytes(c).hex() for c in cs if tuple(c) not in valid]
   edge=m&~ndimage.binary_erosion(m); ec,ct=np.unique(a[edge,:3],axis=0,return_counts=True)
   edges[d]={'edge_pixels':int(edge.sum()),'colours':{c['hex']:{'count':int(sum(n for rgb,n in zip(ec,ct) if bytes(rgb).hex()==c['hex'])),'body_count':int(sum(n for rgb,n in zip(cs,counts) if bytes(rgb).hex()==c['hex']))} for c in pal}}
   allpix.append(pix)
   if d in NAMES: depth.append(f"{d}: p05 {rec['p05']:.2f}; p95 {rec['p95']:.2f}; dominant #{rec['dominant_colour']} {rec['dominant_share']:.2%}")
for d in NAMES:
 a=metrics['approved'][d]; b=metrics['new'][d]
 sizes.append(f"{d}: new {b['width']}x{b['height']}/{b['area']}; approved {a['width']}x{a['height']}/{a['area']} (width x height / opaque area)")
(P/'sizes.txt').write_text('\n'.join(sizes)+'\nAll eight canvas borders: '+str(border)+'\nEast width 103: '+str(metrics['new']['e']['width']==103))
(P/'shape.txt').write_text('\n'.join(shape)+'\nRows are zero-based on 192x192 canvases. Feet must be identified visually; opaque bottom alone does not identify a far foot.\n')
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = 0.2126 R + 0.7152 G + 0.0722 B; opaque pixels only.\n')
(P/'palette-check.txt').write_text('Allowed palette: '+', '.join(c['hex'] for c in pal)+'\n'+ '\n'.join(f'{d}: '+('PASS, no colours outside palette' if not invalid[d] else 'FAIL '+str(invalid[d])) for d in NAMES)+'\nEvery opaque colour in VIEWS is allowed: '+str(all(not invalid[d] for d in NAMES)))
cs,ct=np.unique(np.concatenate(allpix),axis=0,return_counts=True)
metrics['border_contact']=border; metrics['top_five_share']=float(np.sort(ct)[-5:].sum()/ct.sum()); metrics['colours']=len(cs)
(P/'metrics.json').write_text(json.dumps(metrics,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
# Both rows use identical scale and baseline. No per-view resizing.
board=Image.new('RGB',(5*384,2*336),(128,128,128)); draw=ImageDraw.Draw(board)
for row,(tag,folder) in enumerate([('approved',TAKE/'views'),('new',V)]):
 for col,d in enumerate(NAMES):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); im=im.crop(im.getbbox()); im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
  board.paste(im,(col*384+(384-im.width)//2,row*336+310-im.height),im); draw.text((col*384+12,row*336+10),f'{tag} {d} - 3x',fill='white')
board.save(P/'review.png')
env=os.environ.copy(); env['PYTHONDONTWRITEBYTECODE']='1'
for name in ['view_check','sheet_judge']:
 args=['python','-B',f'tools/art/{name}.py',str(P/'slices')]
 if name=='sheet_judge': args+=['--json',str(P/'sheet-judge.json')]
 result=subprocess.run(args,capture_output=True,text=True,env=env)
 text=result.stdout+result.stderr
 (P/f'{name}.txt').write_text(text+f'\nExit code: {result.returncode}\nHeight comparison is informational for this elevated camera; no height repairs applied.\n')
 print(text)
# Exact lone value, using same implementation as view_check.
import sys
sys.dont_write_bytecode=True; sys.path.insert(0,'tools/art'); import sprite_director as sd
lone=max(sd.lone_share(sd.load(P/'slices'/f'{d}.png')) for d in ALL)
metrics['lone_exact']=lone; (P/'metrics.json').write_text(json.dumps(metrics,indent=2))
print('\n'.join(sizes)); print('\n'.join(depth)); print('lone exact',lone,'top five',metrics['top_five_share']); print('borders',border)
