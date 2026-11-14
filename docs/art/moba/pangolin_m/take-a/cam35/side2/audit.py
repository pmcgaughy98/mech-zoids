"""Side-only camera audit adapted from RUN1; all writes confined to side2."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
P=Path(__file__).resolve().parent
TAKE=P.parent.parent
pal=json.loads((P/'palette.json').read_text()); roles={tuple(bytes.fromhex(c['hex'])):c['role'] for c in pal}
records={}; edges={}; shape=[]; depth=[]
for tag,path in [('new',P/'e.png'),('approved',TAKE/'views/e.png'),('first run',TAKE/'views_cam35/e.png')]:
 a=np.array(Image.open(path).convert('RGBA')); m=a[...,3]>0; yy,xx=np.where(m); pix=a[m,:3]
 cs,ct=np.unique(pix,axis=0,return_counts=True); lum=pix@[.2126,.7152,.0722]
 shares={r:sum(int(n) for c,n in zip(cs,ct) if roles.get(tuple(c))==r)/len(pix) for r in ['yellow','steel','charcoal frame','eye','dark accent']}
 eye=np.zeros(m.shape,bool)
 for c,r in roles.items():
  if r=='eye': eye|=m & np.all(a[...,:3]==c,axis=2)
 lab,n=ndimage.label(eye,np.ones((3,3))); groups=sorted([int((lab==i).sum()) for i in range(1,n+1)],reverse=True)
 light=float((m & np.all(a[...,:3]==(255,240,154),axis=2)).sum()/m.sum())
 k=ct.argmax(); border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
 rec=dict(width=int(np.ptp(xx)+1),height=int(np.ptp(yy)+1),area=int(m.sum()),top_row=int(yy.min()),bottom_row=int(yy.max()),role_shares=shares,lightest_yellow_share=light,eye_groups=groups,eye_pixels=int(eye.sum()),elsewhere_eye_pixels=int(eye.sum())-(groups[0] if groups else 0),p05=float(np.percentile(lum,5)),p95=float(np.percentile(lum,95)),dominant_colour=bytes(cs[k]).hex(),dominant_share=float(ct[k]/ct.sum()),border_contact=border,invalid_colours=[bytes(c).hex() for c in cs if tuple(c) not in roles])
 records[tag]=rec
 shape.append(tag+': '+'; '.join(f'{r} {s:.4%}' for r,s in shares.items())+f'; lightest yellow {light:.4%}; accent target 1.8%; eye groups {groups}, elsewhere {rec["elsewhere_eye_pixels"]}; top outline {yy.min()}; bottom {yy.max()}')
 depth.append(f'{tag}: p05 {rec["p05"]:.4f}; p95 {rec["p95"]:.4f}; range {rec["p95"]-rec["p05"]:.4f}; most common #{rec["dominant_colour"]} {rec["dominant_share"]:.4%}')
 edge=m & ~ndimage.binary_erosion(m); ec,et=np.unique(a[edge,:3],axis=0,return_counts=True)
 edges[tag]={bytes(c).hex():{'edge_count':int(sum(n for cc,n in zip(ec,et) if np.array_equal(cc,c))),'body_count':int(n)} for c,n in zip(cs,ct)}
 a_eye=np.argwhere(eye); rec['eye_bounds_xyxy']=[int(a_eye[:,1].min()),int(a_eye[:,0].min()),int(a_eye[:,1].max()),int(a_eye[:,0].max())] if len(a_eye) else None
r=records['new']; e=np.array(Image.open(P/'e.png')); w=np.array(Image.open(P/'w.png')); flip=e[:,::-1]; em=flip[...,3]>0; wm=w[...,3]>0
mirror=dict(rgba_different_pixels=int(np.any(flip!=w,axis=2).sum()),silhouette_different_pixels=int((em!=wm).sum()),silhouette_iou=float((em&wm).sum()/(em|wm).sum()))
prep=json.loads((P/'preparation.json').read_text())
heights=[f'e: {r["width"]} x {r["height"]}; W/82 {r["width"]/82:.5f} target 1.00; H/43 {r["height"]/43:.5f}; H/W {r["height"]/r["width"]:.5f} target 0.66 (~54 tall)',f'H {r["height"]} vs first-run se 61 and ne 60; target 54-60: '+('PASS' if 54<=r['height']<=60 else 'MISS'),f'Top row {r["top_row"]}; lowest row {r["bottom_row"]}; border contact {r["border_contact"]}; canvas 192 x 192, slice_grid bottom-centred with feet=160.',f'West vs horizontal east mirror: {mirror}',f'Whole-sheet nearest scale {prep["shared_scale"]:.12f}; RUN1 {prep["run1_shared_scale"]:.12f}; raw east width {prep["raw_east_width"]}. No per-view resizing.']
(P/'heights.txt').write_text('\n'.join(heights)+'\n')
(P/'shape.txt').write_text('\n'.join(shape)+'\nRows zero-based. Eye expected about 9; approved 11; under 8 is a miss.\n')
(P/'depth.txt').write_text('\n'.join(depth)+'\nLuminance = .2126 R + .7152 G + .0722 B; opaque pixels only.\n')
(P/'palette-check.txt').write_text('Fixed palette: '+', '.join(c['hex'] for c in pal)+'\nNew east '+('PASS; no invalid colours' if not r['invalid_colours'] else 'FAIL '+str(r['invalid_colours']))+'\nOpaque colours: '+str(len(edges['new']))+'; alpha values '+str(np.unique(e[...,3]).tolist())+'\n')
records['mirror']=mirror
(P/'metrics.json').write_text(json.dumps(records,indent=2)); (P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
board=Image.new('RGB',(5*576,576),(128,128,128)); draw=ImageDraw.Draw(board)
for i,(label,path) in enumerate([('approved e',TAKE/'views/e.png'),('first run e',TAKE/'views_cam35/e.png'),('new e',P/'e.png'),('first run se',TAKE/'views_cam35/se.png'),('first run ne',TAKE/'views_cam35/ne.png')]):
 im=Image.open(path).convert('RGBA').resize((576,576),Image.Resampling.NEAREST); board.paste(im,(i*576,0),im); draw.text((i*576+12,12),label+' - 3x',fill='white')
board.save(P/'review.png')
print('\n'.join(heights));print('\n'.join(shape));print('\n'.join(depth))
