import sys
sys.dont_write_bytecode=True
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import verify as a
R=a.R;b=a.b;load=a.load
Z=json.loads((R/'verification.json').read_text());rig=json.loads((R/'rig.json').read_text());extra={};strict=[]
for v in ['e','se','ne']:
 extra[v]={'occlusions':{},'foot_low_rows':{},'leg_length_changes':{},'claw_diff':[],'tail_diff':[]}
 for f in range(8):
  fr=load(R/f'walk/frames/{v}_f{f}.png');dip=int(f in [0,4])
  for p,key in [('claws','claw_diff'),('tail','tail_diff')]:
   src=b.shift(load(R/f'source/{v}_{p}.png'),0,dip);op=src[:,:,3]>0;extra[v][key].append(int(np.any(fr[op]!=src[op],axis=1).sum()))
 for n in ['R3','R2','R1']:
  src=load(R/f'source/{v}_{n}_foot.png');sole=b.support(src);oc=[];rows=[];lc=[]
  for f in range(8):
   q=Z[v]['feet'][n]['frames'][f];rr=next(r for r in rig[v] if r['frame']==f and r['foot']==n);raw=b.shift(src,*q['delta']);fr=load(R/f'walk/frames/{v}_f{f}.png');claw=b.shift(load(R/f'source/{v}_claws.png'),0,int(f in [0,4]));mm=(raw[:,:,3]>0)&np.any(raw!=fr,axis=2);allowed=(claw[:,:,3]>0)&np.all(claw==fr,axis=2);bad=mm&~allowed;ys,xs=np.where(bad)
   oc.append(dict(frame=f,match=q['whole_foot_match_composite'],claw_covered=int((mm&allowed).sum()),other_covered=int(bad.sum()),other_pixels=[[int(x),int(y)] for y,x in zip(ys,xs)]));rows.append(int(np.where(raw[:,:,3]>0)[0].max()));lc.append(round(rr['projected_length_change'],3))
   if bad.any():strict.append(f'{v} {n} f{f}: foot covered by other leg ({bad.sum()}px)')
   if abs(lc[-1])>1:strict.append(f'{v} {n} f{f}: projected length change {lc[-1]:.3f}px')
   if rows[-1]>sole[1]:strict.append(f'{v} {n} f{f}: below own still row by {rows[-1]-sole[1]:.0f}px (supplied target)')
  extra[v]['occlusions'][n]=oc;extra[v]['foot_low_rows'][n]=rows;extra[v]['leg_length_changes'][n]=lc
(R/'strict_checks.json').write_text(json.dumps(dict(views=extra,unmet_requirements=strict),indent=2))
with (R/'checks.txt').open('a') as out:
 out.write('\nADDITIONAL: '+json.dumps(extra)+'\nSTRICT UNMET REQUIREMENTS: '+json.dumps(strict)+'\n')
last=(R/'token-watch-run1.txt').read_text().splitlines()[-1]
lines=[f'lobster-walk35-run1: 24 raw review frames e/se/ne; tokens watcher snapshot {last}; final total unknown.',
'Native hippo/fennec part, pinned-shell, integer-band, stamp-audit method; no image tool/rotation/filtering.',
'Names retained: R1 front/R2 middle/R3 rear = near right; L1/L2/L3 far left, behind shell/tail.',
'Guide differences: se R3 painted support (59,123), guide (56,122); se R2 support (67,141), guide (64.5,141).',
'Actual bottom-two-row sole stamps are translated to supplied targets; targets.json/stills unchanged.',
'Tripod A L1/R2/L3 planted f0-3; B R1/L2/R3 planted f4-7; lifts2/3/3/2 exact; body/claws/tail dip f0/f4.',
'Deciding pixel stamp lock x/y spread: e all0/0; se/ne max0.879/0.783px; PASS. Hidden feet measured on layers.',
'Max pixel-measured target error e0.500, se0.490, ne0.490px; all foot layer stamps100% in all8 frames.',
'Upper canvas above moving joins: e/se/ne f0-7 all[0,0,0,0,0,0,0,0]% differing after dip.']
for v in ['e','se','ne']:
 q=Z[v];lines.append(f"{v} underside true native leg spans: "+str([(s['span'],round(s['max_below_line'],3),s['pass']) for s in q['underside']]))
lines.append('Body excludes separately pinned sockets/tail/claws; absent exterior column uses conservative trunk bound (checks.txt).')
for v in ['e','se','ne']:lines.append(f"{v} specks still{Z[v]['still_specks']} -> f0-7 "+str([s['specks'] for s in Z[v]['structure']])+'.')
for v in ['e','se','ne']:lines.append(f"{v} lowest f0-7 "+str([s['lowest_row'] for s in Z[v]['structure']])+'.')
lines.append('All192x192; binary alpha; native palette only; one component;0 holes/strays/edge pixels. Only dipped claws reach161.')
lines.append('Footlock tool SOME FEET NEED A LOOK: se R3, ne R2/R1 merge soles; e R1 can merge claw; stamps decide.')
lines.append('Seams tool open-gap flags e/se/ne: '+str([[len(s['seams']) for s in Z[v]['structure']] for v in ['e','se','ne']])+'.')
lines.append('No flags inside pinned trunk and0 enclosed holes; red-dot seam boards retain open spaces between legs/ankles.')
lines.append('Whole feet100% on every leg layer; composite occlusion counts per foot/frame in strict_checks.json; touching soles FAIL separation gate.')
maxlength=max(abs(t) for v in extra.values() for n,z in v['leg_length_changes'].items() for t in z)
lines.append(f'Projected articulated length change max{maxlength:.3f}px: 1px length gate NOT MET; native-width bands retained.')
lines.append('Own-still-row gate NOT MET in diagonal planted poses (up to2px lower, prescribed targets); global foot row<=160.')
lines.append('By eye at4x selout/5x joints: heavy near-front+rear versus middle rhythm; claws intact, no stepping; tail plates intact, shell underside clear.')
lines.append('Review delivery, NOT an all-gates pass: underside/overlap/length exceptions above remain. GIF120/130ms alternates (10ms format limit); APNG exact125ms.')
(R/'REPORT.txt').write_text('\n'.join(lines)+'\n');assert len(lines)<30
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (R/'walk/frames').glob('*.png')};(R/'frame_hashes.json').write_text(json.dumps(manifest,indent=2));(R/'timing.json').write_text(json.dumps(dict(run='lobster-walk35-run1',frame_ms=[125]*8,gif_ms=[120,130]*4,loop=0),indent=2))
print('report lines',len(lines),'strict exceptions',len(strict));print({v:{k:z for k,z in e.items() if k in ['claw_diff','tail_diff']} for v,e in extra.items()})
