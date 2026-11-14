"""Read saved PNGs: contacts are recovered by native foot-pixel matching, not rig targets."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
import build as b
R=Path(__file__).resolve().parent;T=json.loads((R/'targets.json').read_text());rig=json.loads((R/'rig.json').read_text())
lines=['RHINO L WALK35 RUN 1 / SAVED FRAME AUDIT',
 'Contact measurement: exhaustive source foot-block pixel search in saved composite PNGs; targets never enter search.',
 'Visible source-foot sole: midpoint of outermost opaque pixels on its lowest row. Search matches the lower six rows; natural body occlusion can hide side paint.',
 'Lock: five planted frames, chronological from landing, wrapping beyond f7; measured contact minus k*planted_step.',
 'Pinned body: all original opaque pixels outside explicitly traced limb regions; compared after requested f0/f4 dip.',
 '11 opaque source colours plus transparent = 12 palette entries. Raw frames have no additional colours.',
 'GIF format rounds to 10ms; alternating120/130ms preserves1000ms cycle. APNG125ms exact.']
result={};fail=[];summary={};font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
def check(ok,msg):
 if not ok:fail.append(msg)
def measure(frame,foot):
 # Source-region limited search, independent of both pose records and target locations.
 src,span=b.fp(foot);ys,xs=np.where(foot[:,:,3]>0);use=ys>=max(ys.min()+2,src[1]-5);ys=ys[use];xs=xs[use];cols=foot[ys,xs]
 candidates=[]
 for dx in range(-12,13):
  for dy in range(-10,11):
   xx=xs+dx;yy=ys+dy;score=float(np.all(frame[yy,xx]==cols,axis=1).mean())
   candidates.append((score,-abs(dx)-abs(dy),dx,dy))
 score,_,dx,dy=max(candidates)
 # Measure the actually visible source-sole endpoints in the final image.
 y=int(src[1])+dy;row=np.where(foot[int(src[1]),:,3]>0)[0]
 good=[int(x+dx) for x in row if np.array_equal(frame[y,x+dx],foot[int(src[1]),x])]
 if not good:return None,score,[dx,dy],0
 return np.array([(min(good)+max(good))/2,y]),score,[dx,dy],len(good)

for view,legs in b.D.items():
 ref=np.array(Image.open(b.B/'views_cam35'/f'{view}.png').convert('RGBA'));frames=[np.array(Image.open(R/'walk/frames'/f'{view}_f{f}.png').convert('RGBA')) for f in range(8)]
 body=np.array(Image.open(R/'walk/layers'/f'{view}_body.png'));pinned=body[:,:,3]>0
 vr={'structure':[],'feet':{},'upper_body_difference_percent':[]};result[view]=vr;rows=[];upp=[]
 for f,a in enumerate(frames):
  op=a[:,:,3]>0;holes=ndi.binary_fill_holes(op)&~op;labs,n=ndi.label(holes);hs=np.bincount(labs.ravel())[1:].tolist();_,components=ndi.label(op,np.ones((3,3)));colors=set(map(tuple,a[op]));allowed=set(b.P);edge=bool(op[[0,-1]].any() or op[:,[0,-1]].any())
  dip=int(f in (0,4));pr=b.shift(body,0,dip);pm=pr[:,:,3]>0;diff=int(np.any(a[pm]!=pr[pm],axis=1).sum());pct=100*diff/int(pm.sum());upp.append(pct);rows.append(int(np.where(op)[0].max()))
  st={'frame':f,'size':list(a.shape[:2]),'binary_alpha':bool(np.isin(a[:,:,3],[0,255]).all()),'opaque_colours':len(colors),'palette_ok':colors<=allowed,'components':components,'holes_sizes':hs,'canvas_edge':edge,'lowest_row':rows[-1],'upper_diff_pixels':diff,'upper_diff_percent':pct}
  vr['structure'].append(st);lines.append(f'STRUCT {view} '+json.dumps(st));check(st['size']==[192,192] and st['binary_alpha'] and st['palette_ok'] and components==1 and not edge and not hs,f'{view} f{f} structure');check(diff==0,f'{view} f{f} pinned body')
 vr['upper_body_difference_percent']=upp
 board=Image.new('RGB',(1400,400*4),(60,68,65));dr=ImageDraw.Draw(board)
 for pi,(name,q) in enumerate(legs.items()):
  foot=ref.copy();foot[~b.limb_mask(view,name,q)]=0;foot[b.Y<q[4]]=0;src,_=b.fp(foot);rr=[];meas=[]
  for f,a in enumerate(frames):
   p,score,dxy,vis=measure(a,foot);target=np.array(T['views'][view]['visible_feet'][name]['frames'][f]['sole_centre']);lift=T['paths'][name][f][1]
   err=np.abs(p-target) if p is not None else np.array([999,999]);ground=int(np.floor(target[1]+lift+.5));actual_lift=ground-p[1] if p is not None else -999
   row={'frame':f,'measured_sole':None if p is None else p.tolist(),'source_pixel_match':score,'translation_recovered':dxy,'visible_matching_sole_pixels':vis,'target':target.tolist(),'error_xy':err.tolist(),'lift_expected':lift,'lift_measured':actual_lift}
   rr.append(row);meas.append(p);lines.append(f'CONTACT {view} {name} '+json.dumps(row));check(p is not None and score>=.8 and vis==int((foot[int(src[1]),:,3]>0).sum()) and err.max()<=1 and actual_lift==lift,f'{view} {name} f{f} contact')
  # Land three frames after first swing. The following five samples are all planted.
  land=(T['gait'][name]+3)%8;idx=[(land+k)%8 for k in range(5)];step=np.array(T['views'][view]['planted_step_px']);locked=np.array([meas[f]-k*step for k,f in enumerate(idx)]);spread=np.ptp(locked,axis=0);check(spread.max()<=2,f'{view} {name} footlock')
  maxerr=np.max([r['error_xy'] for r in rr],axis=0);vr['feet'][name]={'frames':rr,'planted_order':idx,'lock_points':locked.tolist(),'spread_xy':spread.tolist(),'max_error_xy':maxerr.tolist()}
  lines.append(f'FOOTLOCK {view} {name} order={idx} spread_xy={spread.tolist()} max_target_error_xy={maxerr.tolist()}')
  oy=400*pi;dr.text((12,oy+8),f'{view} {name} / planted f{idx} / spread {spread[0]:.3f}, {spread[1]:.3f}px',font=font,fill='white')
  # Each saved sole stamp, advanced into world coordinates, uses a distinct colour.
  colour=[(255,180,70),(90,225,225),(235,110,180),(170,215,95),(200,180,255)]
  orig=locked.mean(0)-[50,35]
  for k,f in enumerate(idx):
   p=meas[f]-k*step;xy=(p-orig)*4+[600,oy+60];c=colour[k];dr.ellipse((xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4),outline=c,width=2)
   dr.text((14,oy+40+k*28),f'f{f} measured {meas[f][0]:.2f},{meas[f][1]:.2f} -> locked {p[0]:.3f},{p[1]:.3f}',font=font,fill=c)
   # Actual lowest foot-row pixels, overlaid at4x after subtracting k*step.
   srcrow=np.where(foot[int(src[1]),:,3]>0)[0];dx,dy=rr[f]['translation_recovered'];yy=int(src[1])+dy
   for sx in srcrow:
    xx=sx+dx
    if np.array_equal(frames[f][yy,xx],foot[int(src[1]),sx]):
     xworld=xx-k*step[0];yworld=yy-k*step[1];x,y=(np.array([xworld,yworld])-orig)*4+[600,oy+60];dr.rectangle((x,y,x+3,y+3),fill=c)
  # Full final-pixel contact strip for all eight poses at3x.
  for f,a in enumerate(frames):
   cx,cy=src;crop=Image.fromarray(a).crop((int(cx)-22,int(cy)-25,int(cx)+22,int(cy)+10)).resize((132,105),Image.Resampling.NEAREST);tile=Image.new('RGBA',crop.size,(78,86,82,255));tile.alpha_composite(crop);board.paste(tile.convert('RGB'),(12+f*170,oy+275));dr.text((12+f*170,oy+252),f'f{f}',font=font,fill='white')
 # An occluded sole cannot be read from a complete composite. Audit its saved
 # native limb PNG instead, explicitly separating that evidence from visible soles.
 vr['hidden_limb_tracks']={}
 for hidden_index,name in enumerate(sorted({x['name'] for x in rig[view] if x['hidden_in_still']})):
  records=[x for x in rig[view] if x['name']==name];pp=[];visible=[]
  for rr in records:
   f=rr['frame'];a=np.array(Image.open(R/f'walk/layers/{view}_{name}_f{f}.png'));p,span=b.fp(a);pp.append(p);xs=np.where(a[int(p[1]),:,3]>0)[0];nvis=sum(np.array_equal(frames[f][int(p[1]),x],a[int(p[1]),x]) for x in xs);visible.append(int(nvis))
   check(abs(rr['ground_row']-p[1]-rr['lift'])<.001,f'{view} hidden {name} f{f} lift')
  land=(T['gait'][name]+3)%8;idx=[(land+k)%8 for k in range(5)];step=np.array(T['views'][view]['planted_step_px']);locked=np.array([pp[f]-k*step for k,f in enumerate(idx)]);spread=np.ptp(locked,axis=0);check(spread.max()<=2,f'{view} hidden {name} lock')
  vr['hidden_limb_tracks'][name]={'measured_from':'saved isolated native limb PNGs; occluded in complete frame','contacts':np.array(pp).tolist(),'planted_order':idx,'spread_xy':spread.tolist(),'matching_composite_sole_pixel_counts':visible}
  lines.append(f'HIDDEN TRACK {view} {name} '+json.dumps(vr['hidden_limb_tracks'][name]))
  oy=400*(len(legs)+hidden_index);dr.text((12,oy+8),f'{view} {name} / HIDDEN IN STILL: isolated limb-pixel evidence / spread {spread[0]:.3f}, {spread[1]:.3f}px',font=font,fill='white');orig=locked.mean(0)-[50,35]
  for k,f in enumerate(idx):
   p=pp[f]-k*step;xy=(p-orig)*4+[600,oy+60];c=colour[k];dr.text((14,oy+40+k*28),f'f{f} {pp[f][0]:.2f},{pp[f][1]:.2f} -> locked {p[0]:.3f},{p[1]:.3f}; composite matching sole pixels {visible[f]}',font=font,fill=c);dr.ellipse((xy[0]-4,xy[1]-4,xy[0]+4,xy[1]+4),outline=c,width=2)
   limb=np.array(Image.open(R/f'walk/layers/{view}_{name}_f{f}.png'));sp,span=b.fp(limb);xs=np.where(limb[int(sp[1]),:,3]>0)[0]
   for xx in xs:
    x,y=(np.array([xx,sp[1]])-k*step-orig)*4+[600,oy+60];dr.rectangle((x,y,x+3,y+3),fill=c)
  for f in range(8):
   limb=Image.open(R/f'walk/layers/{view}_{name}_f{f}.png');cx,cy=np.mean(pp,axis=0);crop=limb.crop((int(cx)-22,int(cy)-25,int(cx)+22,int(cy)+10)).resize((132,105),Image.Resampling.NEAREST);tile=Image.new('RGBA',crop.size,(78,86,82,255));tile.alpha_composite(crop);board.paste(tile.convert('RGB'),(12+f*170,oy+275));dr.text((12+f*170,oy+252),f'f{f} limb',font=font,fill='white')
 board.save(R/f'{view}_footprints.png')
 length=max(np.max(np.abs(np.array(x['lengths'])-x['source_lengths'])) for x in rig[view]);check(length<=1,f'{view} lengths');vr['max_bone_length_error']=float(length)
 gif=Image.open(R/f'{view}_preview.gif');dur=[]
 for f in range(gif.n_frames):gif.seek(f);dur.append(gif.info['duration'])
 check(dur==[120,130]*4 and gif.info['loop']==0,f'{view} gif');apng=Image.open(R/f'{view}_preview.apng');ad=[]
 for f in range(apng.n_frames):
  apng.seek(f);ad.append(apng.info['duration']);check(np.array_equal(np.array(apng.convert('RGBA')),frames[f]),f'{view} APNG f{f} pixels')
 check(ad==[125]*8 and apng.info['loop']==0,f'{view} apng');lines.append(f'TIMING {view} GIF={dur} APNG={ad} loop=0')
 summary[view]={'lowest_rows':rows,'upper_diff':upp,'length_error':float(length),'lock':{n:q['spread_xy'] for n,q in vr['feet'].items()},'target_error':np.max([q['max_error_xy'] for q in vr['feet'].values()],axis=0).tolist()}
result['failures']=fail
air={f:[n for n,path in T['paths'].items() if path[f][1]>0] for f in range(8)}
lines.append('GAIT supplied path feet in air per frame: '+json.dumps(air))
lines.append('GAIT single-foot airborne criterion is incompatible with paths: f1/f3/f5/f7 each lift two feet; paths preserved exactly.')
lines.append('HIDDEN placements: e left limbs16px higher at same side x (concealed lateral lane); se LF=RF+(-24,-17), ne LF=RF+(-24,-10), read from visible hind depth spacing.')
lines.append('SOURCE source se RF broad bounding-box centre120.5 differs from native lowest-row centre123.5; native foot translated to meet requested centre rather than redefining the measured sole.')
lines.append('BODY all pinned source paint exact; stepped dark socket wedges close newly exposed gaps. No added holes after articulation.')
(R/'verification.json').write_text(json.dumps(result,indent=2)+'\n');lines.append('FAILURES '+repr(fail));(R/'checks.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,indent=2));print('FAILURES',fail)
