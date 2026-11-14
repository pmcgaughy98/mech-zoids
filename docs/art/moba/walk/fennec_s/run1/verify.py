"""Independent pixel-stamp/contact audit, adapted from ape_l/run1/verify.py."""
import sys;sys.dont_write_bytecode=True
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import build as m
b=m.b;R=m.R;T=m.T;load=m.load;Y,X=m.Y,m.X
b.b=b
lines=['fennec-trot35-run1: native pixel audit.','Contact measurement: exhaustive colour-stamp search dx[-14,14], dy[-12,12], copied from ape_l/run1/verify.py.','Targets/rig are not used by the pixel search. When a composite stamp is occluded or its sole endpoints are covered, use the saved leg layer.','Contact = midpoint of the outermost painted pixels in the lowest TWO native rows; y = lowest row.','The foot and lower leg are one translated native block; round steel knee housing is another. Both retain their native dimensions; the top four shin rows enter the redrawn knee joint. Entire knee housing and shin below that joint are pixel-checked.','Upper canvas checked against the still after body dip, with the extracted tail translated one frame later.','Sel-out is the exact selout_rhino.py function imported by touchup_machine.py, AST-loaded without executing tool top-level code.']
res={};fails=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for v in ['e','se','ne']:
 ref=load(R/f'stills/{v}.png');tail=load(R/f'source/{v}_tail.png');body=load(R/f'source/{v}_body.png');frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)];allowed=set(map(tuple,ref[ref[:,:,3]>0]));vr={'structure':[],'feet':{}};res[v]=vr
 rig=json.loads((R/'rig.json').read_text())[v]
 for f,a in enumerate(frames):
  op=a[:,:,3]>0;cc=b.pieces(op);holes=b.fill_holes(op)&~op;dip=int(f in [0,4]);pinned=b.shift(ref,0,dip);tt=b.shift(tail,0,dip);pinned[tt[:,:,3]>0]=0;b.comp(pinned,b.shift(tail,0,int(f in [1,5])))
  cut={'e':131,'se':127,'ne':124}[v]+dip;diff=np.any(a[:cut]!=pinned[:cut],axis=2);uppct=100*diff.sum()/(cut*192);paintmask=pinned[:cut,:,3]>0;paintdiff=np.any(a[:cut]!=pinned[:cut],axis=2)&paintmask
  bp=b.shift(body,0,dip);bm=bp[:,:,3]>0;bodydiff=np.any(a[bm]!=bp[bm],axis=1)
  st=dict(frame=f,canvas=list(a.shape[:2]),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),off_palette_pixels=sum(tuple(c) not in allowed for c in a[op]),colours=len(set(map(tuple,a[op]))),components=len(cc),stray_pixels=sum(map(len,cc[1:])),holes=int(holes.sum()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),lowest_row=int(np.where(op)[0].max()),upper_paint_diff_pixels=int(paintdiff.sum()),upper_paint_diff_percent=float(100*paintdiff.sum()/max(1,paintmask.sum())),upper_canvas_diff_pixels=int(diff.sum()),upper_canvas_diff_percent=float(uppct),body_mask_diff_including_leg_occlusion=int(bodydiff.sum()))
  vr['structure'].append(st);lines.append('STRUCT '+v+' '+json.dumps(st))
  if st['off_palette_pixels'] or st['stray_pixels'] or st['holes'] or st['edge'] or not st['binary_alpha'] or st['upper_paint_diff_pixels']:fails.append(f'{v} f{f} structure/body')
 footpic=Image.new('RGB',(1480,4*270),(58,66,62));dr=ImageDraw.Draw(footpic)
 for j,n in enumerate(['RF','LH','LF','RH']):
  src=load(R/f'source/{v}_{n}_lower.png');source_sole=b.support(src);tracks=[];pp=[]
  for f,a in enumerate(frames):
   layer=load(R/f'walk/layers/{v}_{n}_f{f}.png');p,score,d,ends=b.locate(a,src);where='composite'
   if score<1 or not ends:p,score,d,ends=b.locate(layer,src);where='leg layer (occluded)'
   rr=next(q for q in rig if q['foot']==n and q['frame']==f);target=np.array(rr['target']);err=np.abs(p-target);lift=rr['lift'];actual_lift=int(np.floor(target[1]+lift+.5))-p[1]
   sy,sx=np.where(src[:,:,3]>0);dx,dy=d;native=float(np.all(layer[sy+dy,sx+dx]==src[sy,sx],axis=1).mean())
   jointfree=sy>=sy.min()+4
   lower_core=float(np.all(layer[sy[jointfree]+dy,sx[jointfree]+dx]==src[sy[jointfree],sx[jointfree]],axis=1).mean())
   knee=load(R/f'source/{v}_{n}_knee.png');ky,kx=np.where(knee[:,:,3]>0);kd=rr['knee_delta'];kneematch=float(np.all(layer[ky+kd[1],kx+kd[0]]==knee[ky,kx],axis=1).mean())
   tr=dict(frame=f,sole=p.tolist(),measured_from=where,stamp_match=score,ends=ends,delta=d,target=target.tolist(),target_error_xy=err.tolist(),lift_expected=lift,lift_measured=float(actual_lift),lower_native_match=native,lower_below_joint_match=lower_core,knee_native_match=kneematch)
   tracks.append(tr);pp.append(p);lines.append('CONTACT '+v+' '+n+' '+json.dumps(tr))
   if err.max()>1 or actual_lift!=lift or score!=1 or not ends or lower_core!=1 or kneematch!=1:fails.append(f'{v} {n} f{f} contact/native')
  planted=[T['paths'][n][f][1]==0 for f in range(8)];start=next(f for f in range(8) if planted[f] and not planted[(f-1)%8]);order=[(start+k)%8 for k in range(5)];step=np.array(T['views'][v]['planted_step_px']);locked=np.array([pp[f]-k*step for k,f in enumerate(order)]);spread=np.ptp(locked,axis=0)
  vr['feet'][n]=dict(planted_order=order,spread_xy=spread.tolist(),max_target_error=float(max(max(t['target_error_xy']) for t in tracks)),frames=tracks)
  if spread.max()>2:fails.append(f'{v} {n} lock')
  oy=j*270;dr.text((10,oy+4),f'{v} {n} planted {order}: measured lock spread {spread[0]:.3f}, {spread[1]:.3f} px',fill='white',font=font)
  colors=['#ffb575','#75e5cf','#e99fe2','#c9e978','#aab8ff'];orig=locked.mean(0)
  for k,f in enumerate(order):
   dr.text((10,oy+26+k*20),f'f{f} sole {pp[f][0]:.1f},{pp[f][1]:.1f}  locked {locked[k][0]:.3f},{locked[k][1]:.3f}  {tracks[f]["measured_from"]}',fill=colors[k],font=font)
   dy,dx=tracks[f]['delta'][1],tracks[f]['delta'][0];yy,xx=np.where((src[:,:,3]>0)&(Y>=source_sole[1]-1))
   for y,x in zip(yy,xx):
    pt=np.array([x+dx,y+dy])-k*step;px,py=np.floor((pt-orig)*7+[1200,oy+65]).astype(int);dr.rectangle((px,py,px+6,py+6),fill=colors[k])
  for f in range(8):
   dr.text((10+f*180,oy+139),f'f{f} '+('layer' if 'layer' in tracks[f]['measured_from'] else 'frame'),font=font,fill='white');cx,cy=source_sole;box=(int(cx)-17,int(cy)-19,int(cx)+19,int(cy)+9)
   tile=Image.new('RGBA',(144,112),(73,79,75,255));where=load(R/f'walk/layers/{v}_{n}_f{f}.png') if 'layer' in tracks[f]['measured_from'] else frames[f];tile.alpha_composite(Image.fromarray(where).crop(box).resize((144,112),Image.Resampling.NEAREST));footpic.paste(tile.convert('RGB'),(10+f*180,oy+158))
 footpic.save(R/f'{v}_footprints.png')
 lines.append('SUMMARY '+v+' '+json.dumps({n:{k:vv for k,vv in q.items() if k!='frames'} for n,q in vr['feet'].items()}))
res['failures']=fails;(R/'verification.json').write_text(json.dumps(res,indent=2));lines.append('FINAL_FAILURES '+json.dumps(fails));(R/'checks.txt').write_text('\n'.join(lines)+'\n')
for v in ['e','se','ne']:
 print(v,'spreads',{n: q['spread_xy'] for n,q in res[v]['feet'].items()},'errors',{n:q['max_target_error'] for n,q in res[v]['feet'].items()})
print('FAILURES',fails)
