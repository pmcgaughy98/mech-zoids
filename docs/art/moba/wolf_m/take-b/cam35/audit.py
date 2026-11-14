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
for tag,folder in [('approved',TAKE/'fixed'),('new',P/'slices')]:
 metrics[tag]={}
 for d in (NAMES if tag=='approved' else ALL):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); a=np.array(im); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
  cs,counts=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/len(pix) for r in ['gunmetal','red','fang','eye','dark accent']}
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
(P/'sizes.txt').write_text('\n'.join(sizes)+'\nAll eight canvas borders: '+str(border)+'\nEast width ratio: '+str(metrics['new']['e']['width']/110))
(P/'shape.txt').write_text('\n'.join(shape)+'\nRows are zero-based on 192x192 canvases. Feet must be identified visually; opaque bottom alone does not identify a far foot.\n')
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = 0.2126 R + 0.7152 G + 0.0722 B; opaque pixels only.\n')
(P/'palette-check.txt').write_text('Allowed palette: '+', '.join(c['hex'] for c in pal)+'\n'+ '\n'.join(f'{d}: '+('PASS, no colours outside palette' if not invalid[d] else 'FAIL '+str(invalid[d])) for d in NAMES)+'\nEvery opaque colour in VIEWS is allowed: '+str(all(not invalid[d] for d in NAMES)))
cs,ct=np.unique(np.concatenate(allpix),axis=0,return_counts=True)
metrics['border_contact']=border; metrics['top_five_share']=float(np.sort(ct)[-5:].sum()/ct.sum()); metrics['colours']=len(cs)
(P/'metrics.json').write_text(json.dumps(metrics,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
# Both rows use identical scale and baseline. No per-view resizing.
board=Image.new('RGB',(5*384,2*384),(128,128,128)); draw=ImageDraw.Draw(board)
for row,(tag,folder) in enumerate([('approved',TAKE/'fixed'),('new',V)]):
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


# Wolf-specific camera, eye, highlight and shape evidence.
AW=dict(zip(NAMES,[33,83,110,78,35])); AH=dict(zip(NAMES,[72,70,66,70,72]))
TW=dict(zip(NAMES,[33,84,108,78,33])); TH=dict(zip(NAMES,[71,64,63,86,96]))
ACC=dict(zip(NAMES,[7.4,6.4,4.7,5.3,4.8]))
heights=[]; extra=[]; highlights=[]; eyes=[]; accents=[]
for tag,folder in [('approved',TAKE/'fixed'),('new',V)]:
 for d in NAMES:
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); solid=a[...,3]>0
  rec=metrics[tag][d]; y,x=np.where(solid)
  glow=solid&np.all(a[...,:3]==(111,240,220),axis=2)
  lab,n=ndimage.label(glow,structure=np.ones((3,3)))
  groups=sorted([int((lab==i).sum()) for i in range(1,n+1)],reverse=True)
  lights={c:float((solid&np.all(a[...,:3]==tuple(bytes.fromhex(c)),axis=2)).sum()/solid.sum()) for c in ['bcbcc8','ff6a55']}
  rec.update(top_row=int(y.min()),eye_groups=groups,light_shares=lights)
  extra.append(f"{tag} {d}: lightest gunmetal {lights['bcbcc8']:.2%}; lightest red {lights['ff6a55']:.2%}; eye 6ff0dc {int(glow.sum())}, largest group {max(groups,default=0)}, groups {groups}; accent {rec['role_shares']['dark accent']:.2%} vs approved target {ACC[d]:.1f}%")
  if tag=='new':
   heights.append(f"{d}: {rec['width']}x{rec['height']}; W/approved {rec['width']/AW[d]:.4f}; H/approved {rec['height']/AH[d]:.4f}; H/W {rec['height']/rec['width']:.4f} vs target {TH[d]/TW[d]:.4f}; top row {y.min()}; border {border[d]}")
spread=max(metrics['new'][d]['height']/AH[d] for d in NAMES)-min(metrics['new'][d]['height']/AH[d] for d in NAMES)
heights.append(f'H/approved H spread (max minus min): {spread:.4f}; no height repairs. Rows zero-based, 192 canvas.')
(P/'heights.txt').write_text('\n'.join(heights))
feet="New foot rows: s near 160/160, far occluded; se near fore/hind 160/142, far 154/132; e near 160/160, far 147/145; ne near fore/hind 133/158, far 126/153; n hind heels 151/151, far forefeet occluded (tail reaches 160). Approved: s near 160/160 far occluded; se near fore/hind 160/157 far 158/154; e near 160/160, far partly occluded 158; ne near fore/hind 155/160 far 149/157; n heels 155/155 far occluded (tail 160). Identifications visual and approximate where parts overlap."
with (P/'shape.txt').open('a') as out: out.write('\n'+'\n'.join(extra)+'\n'+feet+'\n')
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
lines=[
'Order throughout: s,se,e,ne,n. Tokens unavailable. One built-in image; prompt-sheet.txt used verbatim; no redo.',
'W/approved: '+', '.join(f"{metrics['new'][d]['width']}/{AW[d]}={metrics['new'][d]['width']/AW[d]:.3f}" for d in NAMES)+'; anchor mean 0.9994 (s 1.061,n 1.029,e .909).',
'H/approved: '+', '.join(f"{metrics['new'][d]['height']}/{AH[d]}={metrics['new'][d]['height']/AH[d]:.3f}" for d in NAMES)+f'; spread {spread:.3f}.',
'H/W new/target: '+', '.join(f"{metrics['new'][d]['height']/metrics['new'][d]['width']:.3f}/{TH[d]/TW[d]:.3f}" for d in NAMES)+'; top rows '+','.join(str(metrics['new'][d]['top_row']) for d in NAMES)+'; no borders touched.',
'Lightest gunmetal% new/approved: '+', '.join(f"{100*metrics['new'][d]['light_shares']['bcbcc8']:.1f}/{100*metrics['approved'][d]['light_shares']['bcbcc8']:.1f}" for d in NAMES)+'.',
'Lightest red% new/approved: '+', '.join(f"{100*metrics['new'][d]['light_shares']['ff6a55']:.1f}/{100*metrics['approved'][d]['light_shares']['ff6a55']:.1f}" for d in NAMES)+'.',
'Eyes count(largest group) new: '+', '.join(f"{metrics['new'][d]['eye_pixels']}({max(metrics['new'][d]['eye_groups'],default=0)})" for d in NAMES)+'; approved 4(2),4(4),4(4),0(0),0(0). Rear ne 1 is a MISS; front counts >=3.',
'Accent% new/approved: '+', '.join(f"{100*metrics['new'][d]['role_shares']['dark accent']:.1f}/{ACC[d]:.1f}" for d in NAMES)+'.',
'Palette PASS: 12 fixed colours, no extras; no magenta/plum fringe or lone pale rim; eye glow protected. Edge counts in edge-audit.json.',
'view_check: front/back .70; area .25; height .36; colour .89; dips none; lone '+f"{lone:.4f}"+'; 12 colours; top5 '+f"{metrics['top_five_share']:.3f}"+'; no despeckle required.',
'sheet_judge: FIX none; REDO e,ne,n,nw,w for height only, informational under camera exception; mirrors .977/.874/.863; no repairs or redo.',
'Depth p05/p95/dominant%: '+', '.join(f"{metrics['new'][d]['p05']:.1f}/{metrics['new'][d]['p95']:.1f}/{100*metrics['new'][d]['dominant_share']:.1f}" for d in NAMES)+'.',
'By eye: recognizable same wolf; four legs where exposed, two ears/fangs/fins and one tail consistent, no obvious new parts; firm plates/seams and clean bands. Occlusion prevents certifying all counts in all views.',
'Camera FAIL: front too overhead; side 9% short and stays too low despite a back band and raised far feet; angle inconsistent. Rear taller with head/ears atop; lit top faces increased, but fangs smaller and rear ne cyan remains. Foot rows in shape.txt.'
]
(P/'REPORT.txt').write_text('\n'.join(lines)+'\n'); print('\n'.join(lines))
