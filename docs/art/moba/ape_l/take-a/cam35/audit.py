"""Approved audit adapted for camera comparison, fixed palette, roles and five-view review."""
from pathlib import Path
import json, subprocess, os, shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
P=Path(__file__).resolve().parent; TAKE=P.parent; V=TAKE/'views_cam35'; V.mkdir(exist_ok=True)
NAMES=['s','se','e','ne','n']; ALL=['s','se','e','ne','n','nw','w','sw']
pal=json.loads((P/'palette.json').read_text()); roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in pal}; valid=set(roles)
for d in NAMES: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
metrics={}; edges={}; sizes=[]; shape=[]; depth=[]; invalid={}; border={}; allpix=[]
for tag,folder in [('approved',TAKE/'views'),('new',P/'slices')]:
 metrics[tag]={}
 for d in (NAMES if tag=='approved' else ALL):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); a=np.array(im); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
  cs,counts=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/len(pix) for r in ['armour green','orange','steel','shield and visor glow','dark accent']}
  eye=sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))=='shield and visor glow')
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
(P/'sizes.txt').write_text('\n'.join(sizes)+'\nAll eight canvas borders: '+str(border)+'\nEast width 79: '+str(metrics['new']['e']['width']==79))
(P/'shape.txt').write_text('\n'.join(shape)+'\nRows are zero-based on 160x160 canvases. Feet must be identified visually; opaque bottom alone does not identify a far foot.\n')
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = 0.2126 R + 0.7152 G + 0.0722 B; opaque pixels only.\n')
(P/'palette-check.txt').write_text('Allowed palette: '+', '.join(c['hex'] for c in pal)+'\n'+ '\n'.join(f'{d}: '+('PASS, no colours outside palette' if not invalid[d] else 'FAIL '+str(invalid[d])) for d in NAMES)+'\nEvery opaque colour in VIEWS is allowed: '+str(all(not invalid[d] for d in NAMES)))
cs,ct=np.unique(np.concatenate(allpix),axis=0,return_counts=True)
metrics['border_contact']=border; metrics['top_five_share']=float(np.sort(ct)[-5:].sum()/ct.sum()); metrics['colours']=len(cs)
(P/'metrics.json').write_text(json.dumps(metrics,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
# Both rows use identical scale and baseline. No per-view resizing.
board=Image.new('RGB',(5*384,2*384),(128,128,128)); draw=ImageDraw.Draw(board)
for row,(tag,folder) in enumerate([('approved',TAKE/'views'),('new',V)]):
 for col,d in enumerate(NAMES):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); im=im.crop(im.getbbox()); im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
  board.paste(im,(col*384+(384-im.width)//2,row*384+365-im.height),im); draw.text((col*384+12,row*384+10),f'{tag} {d} - 3x',fill='white')
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

# Gorilla-specific camera measurements; no pixels are redrawn here.
AH={'s':72,'se':72,'e':71,'ne':70,'n':70}
GH={'s':83,'se':89,'e':89,'ne':90,'n':85}
EH={'s':98,'se':101,'e':105,'ne':101,'n':98}
TARGET={'s':10.2,'se':8.5,'e':8.9,'ne':7.6,'n':8.4}
height=[]; shape=[]; visor={}
# Boxes are exclusive upper bounds, zero-based on 160px canvases. Visually
# identified slit only, excluding the generator, shields and all other glow.
BOX={'approved':{'s':(72,82,87,87),'se':(91,82,104,87),'e':(105,83,111,88)},
     'new':{'s':(72,86,88,93),'se':(94,84,105,90),'e':(106,78,114,84)}}
for tag,folder in [('approved',TAKE/'views'),('new',P/'slices')]:
 visor[tag]={}
 for d in NAMES:
  rec=metrics[tag][d]
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA'))
  glow=(a[...,3]>0)&np.isin((a[...,:3].astype(int)*[65536,256,1]).sum(2),[int(c,16) for c in ['1b9a52','3fe07f','d6ffe6']])
  if d in BOX[tag]:
   x0,y0,x1,y1=BOX[tag][d]; vc=int(glow[y0:y1,x0:x1].sum())
  else: vc=0 # Rear views inspected: glow belongs to generator/shields, no visor/face.
  visor[tag][d]=vc
  rec['visor_pixels']=vc
  shape.append(f"{tag} {d}: "+'; '.join(f'{r} {v:.4%}' for r,v in rec['role_shares'].items())+f"; visor ONLY {vc}; slit ROI {BOX[tag].get(d,'none: rear, visual exclusion of generator/shields')}")
  if tag=='new':
   share=100*rec['role_shares']['dark accent']; shape.append(f"  accent {share:.3f}% vs approved target {TARGET[d]:.1f}%: {share-TARGET[d]:+.3f} percentage points")
   height.append(f"{d}: {rec['width']} x {rec['height']}; H/approved H {rec['height']/AH[d]:.6f}; H/shape-guide H {rec['height']/GH[d]:.6f}; H/elliptic-guide H {rec['height']/EH[d]:.6f}")
ratios=[metrics['new'][d]['height']/AH[d] for d in NAMES]; spread=max(ratios)-min(ratios)
height+= [f'H/approved spread max-min: {spread:.6f}; min {min(ratios):.6f}; max {max(ratios):.6f}', 'Informational only: no height normalization, stretching or repairs applied.']
(P/'heights.txt').write_text('\n'.join(height)+'\n')
shape+=['Foot rows (zero-based 160px canvas; visually identified contacts, measured within isolated foot regions):',
'new s: near fists 130; far hind feet 116.',
'new se: near fist 130; far fist 115; visible hind foot 105; other hind foot not separately discernible.',
'new e: near fist 130; far fist 108; near hind foot 124; far hind foot occluded/not separately discernible.',
'new ne: near hind foot 130; far hind foot 119; near fist 124; far fist not confidently separable.',
'new n: near hind feet 130; far fists 114.',
'approved s: near fists 130; far hind feet approximately 126 (low camera overlap).',
'approved se/e/ne/n: lowest near contacts 130; far contacts overlap body/near limbs at low camera and are not confidently separable; no invented far-foot rows.',
'Visor thresholds: approved s18/se17; expected cam35 about s15/se14; new se is a MISS (<12); rear visor zero.',
'Accent seams are retained by luminance and local thin-line contrast; broad shadows retain material ramp; no quota-based recolouring.',
'All eight canvas borders: '+str(border)]
(P/'shape.txt').write_text('\n'.join(shape)+'\n')
metrics['visor']=visor;metrics['height_ratio_spread']=spread
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
# Edge audit is per palette colour per view: body count and silhouette-edge count.
(P/'edge-audit.txt').write_text('\n'.join(f"{d} #{c}: body {r['body_count']}; edge {r['count']}; share of colour on edge {r['count']/max(1,r['body_count']):.4%}" for d,cs in edges.items() for c,r in cs['colours'].items())+'\n')
lines=[
'Heights H/approved (s,se,e,ne,n): '+', '.join(f"{metrics['new'][d]['height']}/{AH[d]}={metrics['new'][d]['height']/AH[d]:.3f}" for d in NAMES)+f'; spread {spread:.4f}.',
'Tokens used: unavailable. Built-in tool: exactly one image, exact prompt-sheet.txt, two refs in specified order; raw saved unchanged.',
'Visor s/se/e/ne/n: '+ '/'.join(str(visor['new'][d]) for d in NAMES)+'; approved s18/se17; expected s15/se14; se MISS (<12); rear zero.',
'Accent new/approved % (s,se,e,ne,n): '+', '.join(f"{100*metrics['new'][d]['role_shares']['dark accent']:.2f}/{TARGET[d]:.1f}" for d in NAMES)+'.',
'Palette: PASS, all 15 fixed colours, no outsiders; alpha binary; all eight borders clear; no magenta/plum, lone pale rim or accent rim pixels remain.',
'view_check: front/back 0.76 MISS (<0.80), area 0.14, height 0.01, colour 0.89, dips none, lone 0.083 (no despeckle required), colours 15.',
'sheet_judge: all eight OK; FIX nothing; REDO nothing. Height comparisons informational, unchanged. Top-five colour share 55.5% misses 65% canon.',
'Depth p05/p95: all five 24.44/185.43 (range 160.99, below canon 180); dominant shares s14.20%, se15.37%, e18.55%, ne19.28%, n21.53%.',
'By eye: recognizably the same gorilla and parts; plates/segmentation and proportions drift, especially narrower se; no clear new hardware.',
'Camera: all show more top, but 35 degrees is not convincingly met consistently; e shows a top/back band and raised far fist, far hind foot remains hidden.',
'Front visor is visible but narrower/weaker than approved; front is not overhead. Firm plates/seams and mostly clean bands, some small clusters; no rear visor.',
'Pilot is a MISS for fleet rollout: heights only +8-10%, below shape guide; se visor too small. Review: review.png; details in heights/shape/depth/check files.'
]
(P/'REPORT.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
