"""Adapted take-B audit: palette, size, roles, lenses, depth, edge and pitched-camera tests."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from collections import Counter
P=Path(__file__).resolve().parent; V=P.parent/'views_cam35'; names=['s','se','e','ne','n']
pal=json.loads((P/'palette.json').read_text()); roles={tuple(bytes.fromhex(p['hex'])):p['role'] for p in pal}; lenscols=[tuple(bytes.fromhex(p['hex'])) for p in pal if p['role']=='eye']; lightcols=[tuple(bytes.fromhex(c)) for c in ['9ff5e6','d6d6dc']]
apW=dict(zip(names,[49,65,84,65,47])); apH=dict(zip(names,[65,62,59,62,63])); target=dict(zip(names,[(49,81),(65,76),(84,62),(65,78),(47,79)])); acc=dict(zip(names,[7.3,6,8.2,6,7.1]))
metrics={}; shape=[]; depths=[]; heights=[]; bad={}; edges={}
for label,folder in [('approved',P.parent/'views'),('new',V)]:
 metrics[label]={}
 for d in names:
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); m=a[:,:,3]>0; y,x=np.where(m); pix=a[m,:3]; n=len(pix); cs,ct=np.unique(pix,axis=0,return_counts=True)
  shares={r:sum(int(c) for rgb,c in zip(cs,ct) if roles.get(tuple(rgb))==r)/n for r in ['turquoise','gold','steel','charcoal','eye','accent']}
  light=sum(int(c) for rgb,c in zip(cs,ct) if tuple(rgb) in lightcols)/n
  lm=m&np.any(np.stack([np.all(a[:,:,:3]==c,axis=2) for c in lenscols]),axis=0); labs,k=ndi.label(lm,np.ones((3,3))); groups=sorted([int((labs==i).sum()) for i in range(1,k+1)],reverse=True)
  lum=pix@[.2126,.7152,.0722]; dom=int(ct.max())/n
  mt={'W':int(np.ptp(x)+1),'H':int(np.ptp(y)+1),'top':int(y.min()),'area':n,'role_shares':shares,'lightest_share':light,'lens_count':int(lm.sum()),'lens_groups':groups,'p05':float(np.percentile(lum,5)),'p95':float(np.percentile(lum,95)),'dominant_share':dom,'border':bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())}
  metrics[label][d]=mt
  shape.append(f'{label} {d}: roles '+', '.join(f'{r} {s:.2%}' for r,s in shares.items())+f'; lightest top shades {light:.2%}; lens total {lm.sum()}, groups {groups}')
  if label=='new':
   bad[d]=['#'+bytes(c).hex() for c in cs if tuple(c) not in roles]
   heights.append(f"{d}: {mt['W']}x{mt['H']}; W/approved {mt['W']/apW[d]:.4f}; H/approved {mt['H']/apH[d]:.4f}; H/W {mt['H']/mt['W']:.4f} vs target {target[d][1]/target[d][0]:.4f} ({target[d][0]}x{target[d][1]}); top row {mt['top']}; border {mt['border']}")
   depths.append(f"{d}: p05 {mt['p05']:.2f}; p95 {mt['p95']:.2f}; dominant {dom:.2%}")
   edge=m&~ndi.binary_erosion(m); ed={}
   for rgb in roles:
    count=int((edge&np.all(a[:,:,:3]==rgb,axis=2)).sum()); allcount=int(np.all(pix==rgb,axis=1).sum()); ed['#'+bytes(rgb).hex()]={'edge_count':count,'share_of_edge':count/int(edge.sum()),'share_of_colour_on_edge':count/allcount if allcount else 0}
   edges[d]=ed
M=metrics['new']; growth=[M[d]['H']/apH[d] for d in names]
heights += [f'H/approved H range {min(growth):.4f}..{max(growth):.4f}; spread max-min {np.ptp(growth):.4f}; max/min {max(growth)/min(growth):.4f}',f"se/ne height {M['se']['H']}/{M['ne']['H']} = {M['se']['H']/M['ne']['H']:.4f}, target 1.00",f"east length/south width {M['e']['W']/M['s']['W']:.4f}; reference 1.71",next(s for s in (P/'guide_sizes.txt').read_text().splitlines() if '35 deg' in s)]
(P/'heights.txt').write_text('\n'.join(heights)+'\n')
(P/'palette-check.txt').write_text('Fixed palette: '+str(len(roles))+' allowed colours.\n'+'\n'.join(f'{d}: '+('PASS; no colours outside palette' if not bad[d] else str(bad[d])) for d in names)+'\n')
for d in names:
 shape.append(f"{d}: accent {M[d]['role_shares']['accent']:.2%} vs approved target {acc[d]:.1f}%; lightest new/approved {M[d]['lightest_share']:.2%}/{metrics['approved'][d]['lightest_share']:.2%}")
shape += ['Lens reference groups: s 40+39, se 53, e 43; expected 35deg s about 32 each, se42,e34; minima s28,se37,e30.']
for d,minimum in [('s',28),('se',37),('e',30)]:
 groups=M[d]['lens_groups']; passed=(len(groups)==(2 if d=='s' else 1) and min(groups)>=minimum)
 shape.append(f'{d} lens minimum: '+('PASS' if passed else 'MISS')+f'; groups {groups}; minimum {minimum}')
shape.append('Rear lenses: '+('PASS zero' if M['ne']['lens_count']==M['n']['lens_count']==0 else 'MISS'))
# Human-selected identifiable feet: canvas rows (bottommost opaque foot pixel).
feet={'s':{'near':140,'far':107},'se':{'near':140,'far':123},'e':{'near':140,'far':None},'ne':{'near':140,'far':118},'n':{'near':140,'far':108}}
shape.append('Approved feet: s/n far pair occluded, not reliably separable; se near row 140 / identifiable far 138; e near 140 / identifiable far 138; ne near 139 / identifiable far 137. Low-camera rises only 2 rows.')
shape.append('Foot bottoms (canvas rows; visual landmarks): '+json.dumps(feet)+'. East has only two distinguishable clamp feet; far pair cannot be established.')
(P/'shape.txt').write_text('\n'.join(shape)+'\n'); (P/'depth.txt').write_text('\n'.join(depths)+'\n')
(P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
# East body: between coil and head, columns chosen from the generated side only.
a=np.array(Image.open(V/'e.png').convert('RGBA')); m=a[:,:,3]>0; ys,xs=np.where(m); x0=int(xs.min()); y0=int(ys.min()); data=[]
hi=np.all(a[:,:,:3]==tuple(bytes.fromhex('9ff5e6')),axis=2)
for x in range(x0+35,x0+59):
 yy=np.where(m[:,x])[0]; top=int(yy.min()); candidates=np.where(hi[:,x]&(np.arange(160)>=top)&(np.arange(160)<=top+20))[0]
 end=int(candidates.max()+1) if len(candidates) else top
 data.append({'column':x,'outline_top':top,'lit_band_end_side_start_proxy':end,'band_depth':end-top})
median=float(np.median([v['band_depth'] for v in data])); metrics['side']={'columns':data,'median_band_depth':median,'near_foot_bottom':140,'far_foot_bottom':None,'far_foot_rise':None}
lines=['East body columns between coil and head. Lit-band boundary uses the end of the turquoise-highlight region as a shade-based proxy; no continuous seam establishes a separate top/side plane.','column | top outline | lit band end / side start proxy | depth']+[f"{d['column']} | {d['outline_top']} | {d['lit_band_end_side_start_proxy']} | {d['band_depth']}" for d in data]
lines += [f'Median lit band depth {median:.1f} rows (nonzero; broad highlight is visible, exact top/side geometry is not certified).','Near feet lowest row 140; far feet not distinguishable. Far-foot rise cannot be measured; required >=6 rows: MISS.']
(P/'side.txt').write_text('\n'.join(lines)+'\n'); (P/'metrics.json').write_text(json.dumps(metrics,indent=2)); print('\n'.join(heights)); print('\n'.join(shape[-12:])); print('\n'.join(depths)); print('Side band median',median)
