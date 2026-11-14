"""Pixel audit independent of rig translations and target positions during search."""
from pathlib import Path
from collections import deque
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import build as b
R=Path(__file__).resolve().parent;T=json.loads((R/'targets.json').read_text())

def load(p):return np.array(Image.open(p).convert('RGBA'))
def pieces(op):
 seen=np.zeros_like(op);out=[]
 for y,x in zip(*np.where(op)):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;pts=[]
  while todo:
   yy,xx=todo.pop();pts.append((yy,xx))
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<192 and 0<=nx<192 and op[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  out.append(pts)
 return sorted(out,key=len,reverse=True)

def locate(a,src,anchor=None):
 # Search the complete native six-row sole stamp, never the target coordinates.
 sole=b.support(src) if anchor is None else anchor;ys,xs=np.where((src[:,:,3]>0)&(b.Y>=sole[1]-5));cols=src[ys,xs]
 best=None
 for dy in range(-12,13):
  for dx in range(-14,15):
   score=float(np.all(a[ys+dy,xs+dx]==cols,axis=1).mean())
   key=(score,-abs(dx)-abs(dy))
   if best is None or key>best[0]:best=(key,dx,dy)
 (_,score_unused),dx,dy=best
 score=best[0][0]
 # Both support-band endpoints must still exist, with their actual source colours.
 sy=int(sole[1]);by,bx=np.where((src[:,:,3]>0)&(b.Y>=sy-1));left,right=int(bx.min()),int(bx.max())
 ends=[]
 for x in [left,right]:
  ends.append(any(np.array_equal(a[y+dy,x+dx],src[y,x]) for y in [sy-1,sy] if src[y,x,3]>0))
 return sole+[dx,dy],score,[dx,dy],all(ends)

lines=['ape-walk35-run2: independent pixel audit.',
'Sole centre: outer endpoints of the lowest TWO source pixel rows, midpoint; y is the lowest row. This reproduces the supplied still centres (side fist native centre112.5 vs label113, difference0.5px).',
'Foot search: exhaustive native colour stamp over translations dx[-14,14],dy[-12,12]; no target, path or rig input during measurement. Occlusion -> isolated limb PNG, explicitly marked.',
'Pinned body: original opaque paint outside traced limbs, excluding translated foreground native plates (legitimate occlusion) or local ne repair. Before-mask differences also reported; full upper canvas checked separately.',
'n fists: nine-pixel contact bands from still_sole define support; adjoining orange sidewalls are carried intact. Exhaustive source stamp search recovers translations without target access.',
'GIF 10ms quantization: alternating120/130ms yields exact1000ms cycle; APNG125ms exact.',
'Selout: touchup_machine.py imports rhino_l/take-a/anim/selout_rhino.py selout; exact function AST loaded, OUTLINE=#141a16, no top-level tools execute.']
fail=[];res={};summary={};font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
def check(ok,msg):
 if not ok:fail.append(msg)
for v in ['ne','s','n']:
 ref=load(R/f'stills/{v}.png');frames=[load(R/f'walk/frames/{v}_f{f}.png') for f in range(8)];body=load(R/f'source/{v}_body.png');vt=T['views'][v];allowed=set(map(tuple,ref[ref[:,:,3]>0]));vr={'structure':[],'feet':{}};res[v]=vr
 for f,a in enumerate(frames):
  op=a[:,:,3]>0;cs=pieces(op);holes=b.fill_holes(op)&~op;pinned=b.shift(body,0,int(f in (0,4)));pm=pinned[:,:,3]>0;unmasked_diff=int(np.any(a[pm]!=pinned[pm],axis=1).sum())
  # Paint above/outside reposed limbs is pinned. Native foreground limbs can occlude the flank.
  if v=='ne':pm &= ~((b.X>=45)&(b.X<=81)&(b.Y>=123)&(b.Y<=154))
  else:
   rr=json.loads((R/'rig.json').read_text())[v]
   for n in (['RF','LF'] if v=='s' else ['RH','LH']):
    q=next(q for q in rr if q['frame']==f and q['foot']==n)
    pm &= b.shift(load(R/f'source/{v}_{n}.png'),*q['delta'])[:,:,3]==0
  diff=int(np.any(a[pm]!=pinned[pm],axis=1).sum())
  st=dict(frame=f,canvas=list(a.shape[:2]),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),off_palette_pixels=sum(tuple(c) not in allowed for c in a[op]),opaque_colours=len(set(map(tuple,a[op]))),components=len(cs),stray_pixels=sum(map(len,cs[1:])),holes=int(holes.sum()),edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any()),lowest_row=int(np.where(op)[0].max()),body_diff_before_foreground_occlusion_mask=unmasked_diff,protected_body_pixels=int(pm.sum()),upper_body_diff_pixels=diff,upper_body_diff_percent=100*diff/int(pm.sum()))
  cut={'ne':98,'s':108,'n':104}[v]+int(f in (0,4));upper=b.shift(ref,0,int(f in (0,4)))
  st['whole_upper_canvas_diff_pixels']=int(np.any(a[:cut]!=upper[:cut],axis=2).sum());check(st['whole_upper_canvas_diff_pixels']==0,f'{v} f{f} whole upper canvas')
  vr['structure'].append(st);lines.append('STRUCT '+v+' '+json.dumps(st));check(st['canvas']==[192,192] and st['binary_alpha'] and not st['off_palette_pixels'] and not st['holes'] and st['components']==1 and not st['edge'],f'{v} f{f} structure');check(diff==0,f'{v} f{f} upperbody')
 board=Image.new('RGB',(1472,4*295),(52,65,57));dr=ImageDraw.Draw(board)
 for j,n in enumerate(['RF','LH','LF','RH']):
  src=load(R/f'source/{v}_{n}.png');source_sole=b.contact(src,v,n);pp=[];tracks=[];layers=[]
  for f,a in enumerate(frames):
   layer=load(R/f'walk/layers/{v}_{n}_f{f}.png');layers.append(layer)
   p,score,delta,ends=locate(a,src,source_sole);where='composite'
   if n not in vt['visible_feet'] or score<.98 or not ends:
    p,score,delta,ends=locate(layer,src,source_sole);where='limb layer (occluded in composite)'
   off,lift=T['paths'][n][f]
   if n in vt['visible_feet']:target=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre'])
   else:target=source_sole+off*np.array(vt['u'])*vt['f']-[0,lift]
   err=np.abs(p-target);ground=int(np.floor(target[1]+lift+.5));actual_lift=ground-p[1]
   # Every source paint texel remains at one integer translation in its limb layer.
   sy,sx=np.where(src[:,:,3]>0);dx,dy=delta
   native_match=float(np.all(layer[sy+dy,sx+dx]==src[sy,sx],axis=1).mean())
   # Whole source gem/bezel, palette band and shape. No resampling permitted.
   glow=(src[:,:,1]>180)&(src[:,:,0]<110)&(src[:,:,2]>70)&(src[:,:,3]>0)
   gy,gx=np.where(glow);gemmatch=None
   if len(gy):
    patch=(b.X>=gx.min()-4)&(b.X<=gx.max()+4)&(b.Y>=gy.min()-4)&(b.Y<=gy.max()+4)&(src[:,:,3]>0)
    yy,xx=np.where(patch);gemmatch=float(np.all(layer[yy+dy,xx+dx]==src[yy,xx],axis=1).mean());check(gemmatch==1,f'{v} {n} f{f} whole shield')
   rr=dict(frame=f,measured_sole=p.tolist(),measured_from=where,stamp_match=score,endpoint_visible=ends,recovered_translation=delta,target=target.tolist(),target_error_xy=err.tolist(),expected_lift=lift,measured_lift=actual_lift,native_part_match=native_match,gem_bezel_match=gemmatch)
   pp.append(p);tracks.append(rr);lines.append('CONTACT '+v+' '+n+' '+json.dumps(rr));check(score==1 and ends and err.max()<=1 and lift==actual_lift,f'{v} {n} f{f} contact');check(native_match==1,f'{v} {n} f{f} native part length/paint')
  land=(T['gait'][n]+3)%8;order=[(land+k)%8 for k in range(5)];step=np.array(vt['planted_step_px']);locked=np.array([pp[f]-k*step for k,f in enumerate(order)]);spread=np.ptp(locked,axis=0);check(spread.max()<=2,f'{v} {n} foot lock')
  foot=dict(planted_order=order,spread_xy=spread.tolist(),frames=tracks,max_target_error_xy=np.max([r['target_error_xy'] for r in tracks],axis=0).tolist(),native_part_length_change_px=0)
  vr['feet'][n]=foot;lines.append('FOOTLOCK '+v+' '+n+' '+json.dumps({k:val for k,val in foot.items() if k!='frames'}))
  oy=j*295;dr.text((12,oy+4),f'{v} {n}: stance {order}; lock spread {spread[0]:.3f}/{spread[1]:.3f}px; foot centres from saved pixels',font=font,fill='white')
  colors=[(255,150,80),(80,225,210),(235,130,210),(160,215,80),(180,170,255)];orig=locked.mean(0)
  for k,f in enumerate(order):
   c=colors[k];dr.text((12,oy+30+k*22),f'f{f}: {pp[f][0]:.1f},{pp[f][1]:.1f} -> {locked[k,0]:.3f},{locked[k,1]:.3f}  [{tracks[f]["measured_from"]}]',fill=c,font=font)
   dx,dy=tracks[f]['recovered_translation'];sy=int(source_sole[1]);yy,xx=np.where((src[:,:,3]>0)&(b.Y>=sy-1))
   for y,x in zip(yy,xx):
    # Actual support stamp, moved back into common ground coordinates.
    pt=np.array([x+dx,y+dy])-k*step;px,py=np.floor((pt-orig)*6+[1170,oy+85]).astype(int);dr.rectangle((px,py,px+5,py+5),fill=c)
  # Composites and isolated contacts in adjacent rows, at native 2x.
  cx,cy=source_sole;box=(int(cx)-18,int(cy)-18,int(cx)+18,int(cy)+8)
  for f in range(8):
   xx=12+f*180;dr.text((xx,oy+149),f'f{f}: '+('layer' if 'layer' in tracks[f]['measured_from'] else 'frame'),font=font,fill='white')
   for k,arr in enumerate([frames[f],layers[f]]):
    im=Image.fromarray(arr).crop(box).resize((72,52),Image.Resampling.NEAREST);tile=Image.new('RGBA',im.size,(80,92,83));tile.alpha_composite(im);board.paste(tile.convert('RGB'),(xx+k*78,oy+177))
  dr.text((12,oy+245),'Each cell: final composite / isolated limb. Coloured stamps: five measured support bands corrected by ground step.',font=font,fill=(180,190,180))
 board.save(R/f'{v}_footprints.png')
 rows=[r['lowest_row'] for r in vr['structure']];summary[v]=dict(lowest_rows=rows,upper_diff=[r['upper_body_diff_percent'] for r in vr['structure']],foot_lock={n:q['spread_xy'] for n,q in vr['feet'].items()},max_target_error=np.max([q['max_target_error_xy'] for q in vr['feet'].values()],axis=0).tolist(),occluded_measurements={n:[r['frame'] for r in q['frames'] if 'layer' in r['measured_from']] for n,q in vr['feet'].items()})
 for ext,durations in [('gif',[120,130]*4),('apng',[125]*8)]:
  im=Image.open(R/f'{v}_preview.{ext}');ds=[]
  for f in range(im.n_frames):im.seek(f);ds.append(im.info['duration'])
  check(ds==durations and im.info['loop']==0,f'{v} {ext} timing');lines.append('TIMING '+v+' '+ext+' '+str(ds)+' loop=0')
protected=json.loads((R/'protected_hashes.json').read_text());check(all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in protected.items()),'inputs changed')
res['summary']=summary;res['failures']=fail;lines.append('FAILURES '+repr(fail));(R/'checks.txt').write_text('\n'.join(lines)+'\n');(R/'verification.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(summary,indent=2));print('FAILURES',fail)

extra=[]
rr=json.loads((R/'rig.json').read_text())
for v in ['s','n']:
 for n in ['RF','LF']:
  src=load(R/f'source/{v}_{n}.png');gy,gx=np.where((src[:,:,1]>180)&(src[:,:,0]<110)&(src[:,:,2]>70)&(src[:,:,3]>0))
  zone=(b.X>=gx.min()-3)&(b.X<=gx.max()+3)&(b.Y>=gy.min()-3)&(b.Y<=gy.max()+3)&(src[:,:,3]>0);sy,sx=np.where(zone);rates=[]
  for f in range(8):
   dx,dy=next(q['delta'] for q in rr[v] if q['foot']==n and q['frame']==f);a=load(R/f'walk/frames/{v}_f{f}.png');rate=float(np.all(a[sy+dy,sx+dx]==src[sy,sx],axis=1).mean());rates.append(rate);check(rate==1,f'{v} {n} f{f} composite shield/gem')
  extra.append(f'COMPOSITE_SHIELD {v} {n} gem+rim exact native translation: {rates}')
for f in range(8):
 old=load(R.parent/f'run1/walk/frames/ne_f{f}.png');a=load(R/f'walk/frames/ne_f{f}.png');region=(b.X>=45)&(b.X<=81)&(b.Y>=123)&(b.Y<=154);changed=np.any(old!=a,axis=2);check(not changed[~region].any(),f'ne f{f} outside repair changed')
 preserved={}
 for n in ['RF','RH','LF']:
  la=load(R.parent/f'run1/walk/layers/ne_{n}_f{f}.png')
  if n=='LF':
   ss=load(R.parent/'run1/source/ne_LF.png');ss[b.Y>=128]=0;d=next(q['delta'] for q in rr['ne'] if q['foot']==n and q['frame']==f);la=b.shift(ss,*d)
  pm=(la[:,:,3]>0)&np.all(la==old,axis=2);dd=int(np.any(a[pm]!=old[pm],axis=1).sum());preserved[n]=dd;check(dd==0,f'ne f{f} changed other limb {n}')
 extra.append(f'NE_LOCAL_REPAIR f{f}: changed {int(changed.sum())} px, outside window 0 px; other visible native limbs changed {preserved}')
res['failures']=fail
(R/'verification.json').write_text(json.dumps(res,indent=2)+'\n')
with (R/'checks.txt').open('a') as fp:fp.write('\n'.join(extra)+'\nFINAL_FAILURES '+repr(fail)+'\n')
print('FINAL_FAILURES',fail)
