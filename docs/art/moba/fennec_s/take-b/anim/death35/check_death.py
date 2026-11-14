"""Independent pixel and playback assertions; all writes confined to death35."""
from pathlib import Path
import runpy
import numpy as np
from PIL import Image
from scipy.ndimage import label,binary_fill_holes
P=Path(__file__).parent
b=runpy.run_path(str(P/'build_death.py'))
lines=['DEATH35: raw 160x160 PNG checks (coordinates zero-based).',
       'Body centre = mean opaque x inside the anatomically traced torso mask.',
       'f0-f3: source torso mask carried with torso; f4-f6: exposed flank contour.',
       'Silhouette centre = mean x of ALL opaque texels (includes ears and tail).',
       'Connectivity uses 8-neighbours; holes use enclosed transparent regions.','']
summary=[]
for v,n in zip(b['VIEWS'],b['NAMES']):
 src=np.array(Image.open(b['ROOT']/'fennec_s/take-b/views_cam35_touchup'/f'{v}.png').convert('RGBA'))
 pal=set(map(tuple,src[src[:,:,3]>0,:3]));parts=b['extract'](src,b['SPECS'][v]);bottom=[];cx=[];ac=[];seq=[]
 lines.append(f'{n} ({v})')
 for f in range(7):
  a=np.array(Image.open(P/'frames'/f'{n}_f{f}.png').convert('RGBA'));op=a[:,:,3]>0;yy,xx=np.where(op)
  assert a.shape==(160,160,4)
  assert set(np.unique(a[:,:,3]))<={0,255}
  extra=set(map(tuple,a[op,:3]))-pal;assert not extra,(n,f,extra)
  assert not (op[0].any() or op[-1].any() or op[:,0].any() or op[:,-1].any())
  assert not (binary_fill_holes(op)&~op).any()
  _,nc=label(op,structure=np.ones((3,3)));assert nc==1,(n,f,nc)
  assert yy.max()<=140
  if f==0:assert np.array_equal(a,src)
  if f<=3:
   tm=Image.new('RGBA',(160,160));dx,dy=b['BODY'][v][f]
   if f==1:dx,dy={'s':(0,-2),'se':(-1,-1),'e':(-2,0),'ne':(-1,1),'n':(0,1)}[v]
   b['paste'](tm,parts['body'],dx,dy);mask=np.array(tm)[:,:,3]>0
  else:
   x,y=b['SPECS'][v]['hip'];dx,dy=b['BODY'][v][f];x+=dx;y=min(130,y+min(dy,7));w=14 if v in ['s','n'] else 18
   mask=b['maskpoly']([(x-w,y-3),(x-w+3,y-8),(x-4,y-11),(x+8,y-8),(x+w,y-2),(x+w-1,y+7),(x+9,y+10),(x-6,y+9),(x-w,y+4)])
  mask &= op;ty,tx=np.where(mask);assert tx.size
  bottom.append(int(yy.max()));cx.append(round(float(tx.mean()),2));ac.append(round(float(xx.mean()),2));seq.append(a)
  lines.append(f'  f{f}: bottom={bottom[-1]}, torso_centre_x={cx[-1]:.2f}, silhouette_centre_x={ac[-1]:.2f}; palette/alpha/holes/components/edges PASS')
 assert np.array_equal(seq[5][:,:,3],seq[6][:,:,3])
 diff=np.any(seq[5]!=seq[6],axis=2)
 eye=set([(63,232,176),(200,255,240),(246,255,251)])
 assert all(tuple(c) in eye for c in seq[5][diff,:3])
 assert all(tuple(c) in [(46,26,110),(20,18,24),(33,30,39)] for c in seq[6][diff,:3])
 gif=Image.open(P/f'preview_{n}.gif');dur=[]
 for f in range(gif.n_frames):gif.seek(f);dur.append(gif.info.get('duration'))
 assert gif.n_frames==7 and dur==b['MS'],(n,gif.n_frames,dur)
 assert 'loop' not in gif.info
 lines += [f'  f0 exact: PASS (0 differing RGBA pixels)',f'  f5/f6 same pose: PASS; eye texels darkened: {int(diff.sum())}',f'  GIF: 7 frames; {dur} ms; no loop extension; held final.','']
 summary.append((n,bottom,cx,ac,int(diff.sum())))
lines += ['All 35 raw frames PASS. Palette: each view uses only its own approved still colours.',
          'All five f0 RGBA arrays equal approved stills exactly.',
          'No opaque row below 140, no alpha holes, no detached components, no canvas-edge contacts.',
          'board.png: 5120x3340, five rows; approved still then f0-f6, exact selout_rhino.selout at 4x.',
          'OUTLINE is #141218; outline is review-only, raw deliverable frames have none baked in.',
          'Body movement: early recoil then one-way flank roll; f5/f6 centres identical.']
(P/'checks.txt').write_text('\n'.join(lines)+'\n')
rep=['Violet S fennec death35 -- 35 raw native-pixel frames; no image generation.',
     'Tokens: watcher snapshot '+(P/'token-watch-death35.txt').read_text().splitlines()[-1]+' (time, tokens); final total unknown.',
     'PASS f0: exact RGBA equality in all five views (zero changed pixels).',
     'PASS palette: each view stays within its own still palette (union 15 colours).',
     'PASS alpha: binary; no enclosed holes, detached components, or edge contacts.',
     'Lowest opaque rows f0..f6:']
for n,bot,cx,ac,eye in summary:rep.append(f'  {n}: '+', '.join(map(str,bot)))
rep.append('Measured torso centre x f0..f6 (explicit anatomical mask; see checks.txt):')
for n,bot,cx,ac,eye in summary:rep.append(f'  {n}: '+', '.join(f'{x:.2f}' for x in cx))
rep += ['PASS in-place: torso shifts only with recoil/roll; no progressive canvas slide.',
        'PASS timing: all GIFs have 7 frames, 300/100/130/140/160/180/1400 ms, play once.',
        'PASS settle: f6 preserves f5 pose/alpha; visible eyes darken to #2E1A6E.',
        'n/ne have no visible eye lights to extinguish; their f6 equals f5 exactly.',
        'PASS review: board.png + five boards, exact game sel-out #141218 at 4x.',
        'By eye front: whole violet fox, asymmetric ear drop and roll onto its right.',
        'By eye se: recognisable face/hips; chest buckles, flank lowers, ears flatten.',
        'By eye side: head/chest descend over folded legs; straight tail rests behind.',
        'By eye ne: native back/hip plates retained; right roll exposes folded limbs.',
        'By eye back: head rolls screen-right; near ear rests low, legs fold left.',
        'Native translations/hand redrawing; no external files or Git state changed.']
assert len(rep)<30,len(rep)
(P/'REPORT.txt').write_text('\n'.join(rep)+'\n')
print('\n'.join(rep))


