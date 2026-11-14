from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent;B=R.parents[1];T=json.loads((R/'targets.json').read_text());L=R/'run2/layers'
P={tuple(bytes.fromhex(c)) for c in '141218 211e27 3d3a44 58555e 7a4a06 9d9ba2 d18a0a d6d6dc ff3a2a ffcf1f fff4a8'.split()}
rig=json.loads((R/'run2/rig.json').read_text());lines=['RHINO L WALK35 RUN2 / saved frame pixel audit'];results={};font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for path,digest in json.loads((R/'run2/protected_hashes.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest,path
for f in range(8):
 lifted=[n for n,path in T['paths'].items() if path[f][1]>0];assert len(lifted)==(1 if f%2==0 else 2);lines.append(f'GAIT f{f}: approved four-beat lifted={lifted}; '+('one' if f%2==0 else 'two')+' swing feet; hidden pair remains occluded in s/n.')
lines.append('PROTECTED: all approved e/se/ne frame hashes, all five stills, targets.json unchanged.')
for view in ['s','n']:
 seq=[np.array(Image.open(R/'walk/frames'/f'{view}_f{f}.png').convert('RGBA')) for f in range(8)];body=np.array(Image.open(L/f'{view}_body.png').convert('RGBA'));footresults={};rows=[];uppers=[]
 for f,a in enumerate(seq):
  op=a[:,:,3]>0;colors=set(map(tuple,a[op,:3]));alpha=bool(np.isin(a[:,:,3],[0,255]).all());lab,n=ndi.label(op,np.ones((3,3)));holes=int((ndi.binary_fill_holes(op)&~op).sum());edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any());lowest=int(np.where(op)[0].max());rows.append(lowest)
  dip=int(f in (0,4));ys,xs=np.where(body[:,:,3]>0);diff=int(np.any(a[ys+dip,xs]!=body[ys,xs],axis=1).sum());pct=100*diff/len(xs);uppers.append(pct)
  lines.append(f'STRUCT {view} f{f} 192x192 colors={len(colors)} palette={colors<=P} binary_alpha={alpha} components={n} holes={holes} edge={edge} lowest={lowest} pinned_diff={diff}/{len(xs)} ({pct:.6f}%)')
  assert a.shape==(192,192,4) and colors<=P and alpha and n==1 and holes==0 and not edge and diff==0
 board=Image.new('RGB',(1200,900),(66,91,80));d=ImageDraw.Draw(board);d.text((12,8),view+' ground contacts: measured on final frame soles; stance unwrapped across f7',font=font,fill='white')
 for pi,(name,foot) in enumerate(T['views'][view]['visible_feet'].items()):
  cx=(foot['still_sole'][0]+foot['still_sole'][1])/2; measured=[];errs=[];lifts=[];src=np.array(Image.open(L/f'{view}_{name}_source.png'));sy,sx=np.where(src[:,:,3]>0);height=int(sy.max()-sy.min()+1)
  for f,a in enumerate(seq):
   # Sole is the bottom occupied raster row in the original foot's narrow x band,
   # observed directly in final PNG, with no reliance on layer coordinates/targets.
   x0,x1=map(int,foot['still_sole'][:2]);search=a[148:172,x0:x1+1,3]>0;yy,xx=np.where(search);y=int(yy.max()+148);sole=np.where(a[y,x0:x1+1,3]>0)[0]+x0;p=np.array([(sole.min()+sole.max())/2,y]);target=np.array(foot['frames'][f]['sole_centre']);lift=foot['frames'][f]['lift'];ground=int(np.floor(target[1]+lift+.5));err=np.abs(p-target);errs.append(err.tolist());measured.append(p.tolist());lifts.append(ground-p[1]);assert err.max()<=1 and ground-p[1]==lift
   layer=np.array(Image.open(L/f'{view}_{name}_f{f}.png'));dy=next(z['translation_y'] for z in rig[view] if z['name']==name and z['frame']==f)
   # Disc/cuff/foot paint is an unscaled, untranslated-in-x rigid native component.
   shifted=src[sy,sx];dx=next(z['translation_x'] for z in rig[view] if z['name']==name and z['frame']==f);native=layer[sy+dy,sx+dx];changed=int(np.any(native!=shifted,axis=1).sum())
   # Joint bearing may overlap top two dark rows; the visible disc/cuff/sole core must match.
   core=sy>=140 if view=='s' else sy>=138
   corechanged=int(np.any(native[core]!=shifted[core],axis=1).sum());assert changed==0
   lines.append(f'FOOT {view} {name} f{f}: final_pixel_sole={p.tolist()} ideal={target.tolist()} error_xy={err.tolist()} lift={ground-p[1]}/{lift} native_core_diff={corechanged} rigid_disc_to_sole_length_delta=0')
  # Landing is first zero-lift after swing; stance is five consecutive frames.
  path=T['paths'][name];start=next(f for f in range(8) if path[f][1]==0 and path[(f-1)%8][1]>0);indices=[(start+k)%8 for k in range(5)];step=np.array(T['views'][view]['planted_step_px']);world=np.array([np.array(measured[f])-k*step for k,f in enumerate(indices)]);spread=np.ptp(world,axis=0);assert spread.max()<=2
  res={'contacts':measured,'error_xy':errs,'lift_measured':lifts,'stance_indices':indices,'world_contacts':world.tolist(),'spread_xy':spread.tolist(),'max_error':float(np.max(errs)),'native_disc_to_sole_length_delta':0};footresults[name]=res
  lines.append(f'LOCK {view} {name}: order={indices} final_pixels_minus_k_step={world.tolist()} spread_xy={spread.tolist()} PASS<=2px')
  ox=pi*600;d.text((ox+16,48),f'{name}: x/y spread {spread[0]:.3f}/{spread[1]:.3f}px',font=font,fill='white');cols=['#ffc340','#60e5e5','#eb8cbb','#9cde78','#d9bbff']
  for k,f in enumerate(indices):
   p=np.array(measured[f]);w=world[k];d.text((ox+16,82+28*k),f'f{f}: screen {p[0]:.2f}, {p[1]:.2f}  world {w[0]:.3f}, {w[1]:.3f}',font=font,fill=cols[k]);xx=ox+300+(w[0]-cx)*70;yy=390+(w[1]-world[0,1])*70;d.ellipse((xx-8-k,yy-8-k,xx+8+k,yy+8+k),outline=cols[k],width=2);d.line((xx-18,yy,xx+18,yy),fill=cols[k]);d.line((xx,yy-18,xx,yy+18),fill=cols[k])
  d.text((ox+16,570),'70x contact scatter (rings); no target dots used',font=font,fill='white')
  d.text((ox+16,630),'8x final sole-pixel footprints, ground compensated',font=font,fill='white')
  for k,f in enumerate(indices):
   a=seq[f];p=np.array(measured[f]);y=int(p[1]);xx=np.where(a[y,x0:x1+1,3]>0)[0]+x0;shift_y=-k*step[1];yy=720+(y+shift_y-world[0,1])*8
   for x in xx:
    px=ox+300+(x-cx)*8;d.rectangle((px,yy,px+7,yy+3),fill=cols[k])
   d.text((ox+16,760+k*22),f'f{f}: {len(xx)} saved sole pixels',font=font,fill=cols[k])
 board.save(R/f'{view}_footprints.png');results[view]={'feet':footresults,'lowest_rows':rows,'upper_body_diff_percent':uppers}
 gif=Image.open(R/f'{view}_preview.gif');dur=[]
 for f in range(gif.n_frames):gif.seek(f);dur.append(gif.info['duration'])
 assert gif.n_frames==8 and dur==[120,130]*4 and gif.info['loop']==0
 apng=Image.open(R/f'{view}_preview.apng');ad=[]
 for f in range(apng.n_frames):apng.seek(f);ad.append(apng.info['duration'])
 assert ad==[125]*8
 lines.append(f'TIMING {view}: GIF {dur}, loop=0, 1000ms cycle; APNG 8 x125ms exact.')
lines+=['Far feet have no supplied targets in s/n; no invented exposed far-foot contacts are claimed.','Upper-body percentage denominator: every opaque pinned source texel, including entire head/horn/shell/tail and fixed shoulder plates.','Native component lengths: original knee/cuff/sole pixels translate rigidly, 0px length/width change; joint recess opens/closes under fixed armour.','Palette: 11 opaque still RGB colors plus transparency = 12 entries. No new colors.','No generated images, rotations, scaling, interpolation, new palette colors, commits, or edits outside walk35.']
(R/'checks.txt').write_text('\n'.join(lines)+'\n');(R/'run2/verification.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS: 16 frames,32 visible contacts,4 stance tracks,upper-body 0%,palette/alpha/components/holes/edge/protected hashes/timing.')
