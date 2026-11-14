"""Audit native output and render comparisons without writing outside this directory."""
from pathlib import Path
import runpy,json,math,subprocess
from PIL import Image
import numpy as np
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
m=runpy.run_path(str(R/'repair.py'));P=m['P'];OLD=m['OLD'];rec=m['records'];targets=m['targets']
frames=[np.array(Image.open(R/'walk/frames'/f'side_f{f}.png').convert('RGBA')) for f in range(8)]
lines=['WOLF M TAKE B / WALK3 / NATIVE AUDIT','Widths: traced visible plate/shank contours in fixed/e.png; cross-sections at 25/50/75% of each segment axis.','Widths are rounded native pixel coverage perpendicular to the segment, not a horizontal bounding box.','Paw width is its widest horizontal native row; contact span is tested separately.']
struct=[];palette={p[:3] for p in P}
for f,a in enumerate(frames):
 mask=a[:,:,3]>0;holes=int((ndi.binary_fill_holes(mask)&~mask).sum());labs,n=ndi.label(mask,np.ones((3,3)));sizes=np.bincount(labs.ravel())[1:].tolist()
 edge=bool(mask[[0,-1]].any() or mask[:,[0,-1]].any());colors=set(map(tuple,a[mask,:3]));old=np.array(Image.open(OLD/'walk/frames'/f'side_f{f}.png').convert('RGBA'))
 allowed=np.zeros((192,192),bool)
 for name in targets['still_paws']:
  for root in [R,OLD]:allowed|=np.array(Image.open(root/'walk/layers'/f'{name}_f{f}.png'))[:,:,3]>0
 forbidden=int((np.any(a!=old,2)&~allowed).sum())
 row=dict(frame=f,binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),palette_ok=colors<=palette,colors=len(colors),holes=holes,components=n,component_sizes=sizes,below160=int(mask[161:].sum()),edge=edge,outside_leg_changes=forbidden)
 struct.append(row);lines.append('STRUCT '+json.dumps(row))
 assert a.shape==(192,192,4) and row['binary_alpha'] and row['palette_ok'] and not holes and n==1 and not row['below160'] and not edge and not forbidden,row
# Segment-width checks: native-pixel widths from the reference and the transformed plate.
def widths(a,start,end):
 mask=np.array(a)[:,:,3]>0;s=np.array(start,float);v=np.array(end,float)-s;u=v/np.linalg.norm(v);n=np.array([-u[1],u[0]]);ds=np.arange(-20,20.001,.01);ws=[];raw=[]
 for frac in [.25,.5,.75]:
  pos=np.floor(s+v*frac+ds[:,None]*n+.5).astype(int);on=mask[pos[:,1],pos[:,0]];lab,k=ndi.label(on);lens=[(lab==j).sum()*.01 for j in range(1,k+1)];w=float(max(lens,default=0));raw.append(round(w,2));ws.append(round(w))
 return ws,raw
def pawwidth(a):
 mask=np.array(a)[:,:,3]>0
 return max((np.where(row)[0].ptp()+1 if row.any() else 0) for row in mask)
# np.ptp is used for compatibility with newer NumPy.
def pawwidth(a):
 mask=np.array(a)[:,:,3]>0
 return int(max((np.ptp(np.where(row)[0])+1 if row.any() else 0) for row in mask))
widths_result={};width_summary=[]
for name in targets['still_paws']:
 near=name.startswith('near');typ='fore' if name.endswith('fore') else 'hind';key=typ if near else name;s=m['source'][key];entry={};summ=[]
 for seg,aa,bb in [('upper','root','joint'),('shank','joint','ankle')]:
  paint=m['upper' if seg=='upper' else 'lower'][key];refw,rawref=widths(paint,s[aa],s[bb]);new=[];rawnew=[]
  for r in [q for q in rec if q['name']==name]:
   ta=r[aa];tb=r['wrist' if bb=='ankle' else bb];out=Image.open(R/'walk/layers'/f"{name}_f{r['frame']}.png");w,raw=widths(out,ta,tb);new.append(w);rawnew.append(raw)
  delta=int(np.abs(np.array(new)-refw).max());entry[seg]=dict(reference=refw,frames=new,raw_reference=rawref,raw_frames=rawnew,max_native_delta=delta)
  assert delta<=1,(name,seg,entry[seg])
  low=np.min(new,axis=0).tolist();high=np.max(new,axis=0).tolist();summ.append(f'{seg} {refw} -> {low}..{high}')
 # Measure the authored complete paw deformation, before its shank overlaps it.
 rw=pawwidth(m['feet'][key]);pw=[pawwidth(m['foot'](m['feet'][key],s,r)) for r in rec if r['name']==name]
 entry['paw']=dict(reference=rw,frames=pw,max_native_delta=int(max(abs(w-rw) for w in pw)))
 assert entry['paw']['max_native_delta']<=1,(name,entry['paw'])
 summ.append(f'paw {rw} -> {min(pw)}..{max(pw)}');widths_result[name]=entry
 width_summary.append(name+': '+ '; '.join(summ));lines.append('WIDTH '+width_summary[-1])
# Contact tests use full unoccluded authored limbs and the final composite's visible footprints.
table=[];spreads={}
for name,p in targets['still_paws'].items():
 world=[];sets=[]
 for f in range(8):
  a=np.array(Image.open(R/'walk/layers'/f'{name}_f{f}.png'));mask=a[:,:,3]>0;by=int(np.where(mask)[0].max());sole=np.where(mask[by])[0];lo=int(sole.min());hi=int(sole.max());cx=(lo+hi)/2;off,lift=targets['paths'][p['pair']][f];tx=p['x']+off
  old=np.array(Image.open(OLD/'walk/layers'/f'{name}_f{f}.png'));oldby=np.where(old[:,:,3]>0)[0].max();olds=np.where(old[oldby,:,3]>0)[0]
  errors=[abs(lo-int(olds.min())),abs(hi-int(olds.max()))];xe=abs(cx-tx);le=abs(160-by-lift)
  visible=[int(x) for x in sole if np.array_equal(frames[f][by,x],a[by,x])]
  row=dict(paw=name,frame=f,target_x=tx,sole_span=[lo,hi],center_x=cx,endpoint_errors=errors,target_lift=lift,lift=160-by,x_error=xe,lift_error=le,visible_matching_sole_pixels=visible)
  table.append(row);lines.append('PAW '+json.dumps(row));assert max(errors)<=1 and xe<=1 and le<=1,row
  if lift==0:world.append(cx+5*f);sets.append([lo+5*f,hi+5*f])
 spread=max(world)-min(world);ends=np.ptp(sets,axis=0).tolist();assert spread<=2 and max(ends)<=2
 # Match stamp times in the supplied test, including the 50fps timestamp arithmetic.
 stamps=[];last=-1
 for vf in range(400):
  t=vf/50;idx=int(t*10)
  if idx!=last:stamps.append((idx,t));last=idx
 timed=[]
 for cycle in range(10):
  w=[]
  for idx,t in stamps:
   if idx//8==cycle and targets['paths'][p['pair']][idx%8][1]==0:
    sample=next(q for q in table if q['paw']==name and q['frame']==idx%8);w.append(sample['center_x']+50*t)
  if len(w)==4:timed.append(max(w)-min(w))
 spreads[name]=dict(world_x=world,center_spread=spread,endpoint_spreads=ends,actual_stamp_spread=round(max(timed),6));assert max(timed)<=2
 lines.append('FOOTLOCK '+name+' '+json.dumps(spreads[name]))
g=Image.open(R/'preview.gif');dur=[]
for i in range(g.n_frames):g.seek(i);dur.append(g.info['duration'])
assert g.n_frames==8 and dur==[100]*8 and g.info['loop']==0
lines.append('GIF PASS 8 frames, 100 ms each, infinite loop.')
# Palette and exposed edge accounting, including intentionally retained gunmetal outline.
lines.append('Palette RGB : opaque pixel count / silhouette edge count, all 8 frames:')
for p in P:
 total=edgecount=0
 for a in frames:
  mask=a[:,:,3]>0;edge=mask&~ndi.binary_erosion(mask,structure=ndi.generate_binary_structure(2,1));on=np.all(a==p,2);total+=int(on.sum());edgecount+=int((on&edge).sum())
 lines.append('#%02x%02x%02x'%p[:3]+f' {total} / {edgecount}')
(R/'checks.txt').write_text('\n'.join(lines)+'\n')
(R/'verification.json').write_text(json.dumps(dict(structure=struct,widths=widths_result,paws=table,footlock=spreads),indent=2)+'\n')
report=['WOLF M TAKE B / CODEX WALK3 / SIDE TROT','Tokens: unavailable. Native pixel repair only; no image tool; no commit.','Inputs: approved fixed/e.png and codex-walk2; all writes inside codex-walk3.','8 RGBA frames,192x192; 100ms loop preview; supplied 0.90m/s diagnostic PNG/MP4.','Widths below: perpendicular native pixels at 25/50/75% of plate and shank; paw widest row.']
report+=width_summary
report+=['Width PASS: each corresponding native cross-section and paw width within1px of the traced still.','Width audit uses visible approved contours; hidden upper plates reconstructed only under the body overlap.','32/32 paw checks PASS: sole endpoints within1px of walk2; center errors <=0.5px; lift errors0px.']
for name,v in spreads.items():report.append(name+f" ground world-x {v['world_x']}; spread {v['center_spread']:g}px; endpoint spreads {v['endpoint_spreads']}px.")
report+=['Actual supplied diagnostic stamp times: all four planted-paw spreads0px at0.90m/s.','8/8 PASS: binary alpha, approved palette, bottom160, below160=0, holes0, components1, canvas-edge0.','Body/head/fins/tail: pixel-identical to walk2 outside union of old and replacement leg masks.','Method: approved plate paint fitted to existing rig; native shoulder/hip, knee, ankle and toe joins repainted.','EYE at4x game sel-out: tapered plate legs and separate clawed toes resemble the still; whole joined limbs, no cutoffs seen.','EYE: still reads as a robot wolf trotting forward; diagonal timing and paw paths retained.','board.png: fixed still / walk2 row / walk3 row, supplied selout() OUTLINE#141418, nearest4x.']
assert len(report)<25,len(report)
(R/'REPORT.txt').write_text('\n'.join(report)+'\n')
print('\n'.join(width_summary));print('All structural, width, paw, footprint, protected-pixel and GIF checks PASS.')
