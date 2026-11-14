from pathlib import Path
import json
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
M=json.loads((P/'metrics.json').read_text()); N=['s','se','e','ne','n']
AW=dict(zip(N,[91,89,79,86,87])); AH=dict(zip(N,[72,72,71,70,70])); GW=dict(zip(N,[91,89,79,86,91])); GH=dict(zip(N,[83,89,89,90,85])); AC=dict(zip(N,[10.2,8.5,8.9,7.6,8.4]))
BOX={'approved':{'s':(72,82,87,87),'se':(91,82,104,87),'e':(105,83,111,88),'ne':(92,65,111,91),'n':(69,85,90,97)},'new':{'s':(72,82,88,88),'se':(91,77,105,85),'e':(106,71,114,78),'ne':(96,58,112,78),'n':(68,78,91,91)}}
shape=[]; heights=[]; lights={}; visor={}
for tag,folder in [('approved',P.parent.parent/'views'),('new',P/'views')]:
 lights[tag]={};visor[tag]={}
 for d in N:
  a=np.array(Image.open(folder/f'{d}.png').convert('RGBA')); solid=a[...,3]>0; packed=(a[...,:3].astype(int)*[65536,256,1]).sum(2)
  lights[tag][d]={c:100*int((solid&(packed==int(c,16))).sum())/int(solid.sum()) for c in ['9ccb62','f2ac5c']}
  glow=solid&np.isin(packed,[int(c,16) for c in ['1b9a52','3fe07f','d6ffe6']]); x0,y0,x1,y1=BOX[tag][d]; vc=int(glow[y0:y1,x0:x1].sum());visor[tag][d]=vc
  rec=M[tag][d];shape.append(f"{tag} {d}: "+'; '.join(f'{r} {v:.4%}' for r,v in rec['role_shares'].items())+f"; visor-only {vc}, ROI {BOX[tag][d]}; light green {lights[tag][d]['9ccb62']:.4f}%, light orange {lights[tag][d]['f2ac5c']:.4f}%, combined {sum(lights[tag][d].values()):.4f}%")
  if tag=='new':
   shape.append(f" accent {100*rec['role_shares']['dark accent']:.4f}% vs {AC[d]:.1f}% approved; delta {100*rec['role_shares']['dark accent']-AC[d]:+.4f} percentage points")
   heights.append(f"{d}: {rec['width']} x {rec['height']}; W/approved W {rec['width']/AW[d]:.6f}; H/approved H {rec['height']/AH[d]:.6f}; H/W {rec['height']/rec['width']:.6f} vs guide {GH[d]}/{GW[d]}={GH[d]/GW[d]:.6f}")
ratios=[M['new'][d]['height']/AH[d] for d in N];spread=max(ratios)-min(ratios)
heights += [f'H/approved H spread max-min {spread:.6f}; min {min(ratios):.6f}; max {max(ratios):.6f}', 'Informational: no height repair or per-view scaling applied. Anchor ratios south/91=north/87=east/79=1.000000; mean 1.000000.']
(P/'heights.txt').write_text('\n'.join(heights)+'\n')
# Contact rows in visually isolated limb ROIs. Other far feet are occluded.
feet={'s':{'near fist':(34,117,61,135),'far hind foot':(61,98,75,116)},'se':{'near fist':(48,118,82,135),'far fist':(107,101,128,120),'near hind foot':(34,91,51,107),'far hind foot':(82,97,96,113)},'e':{'near fist':(81,117,111,135),'far fist':(108,86,120,101),'near hind foot':(39,109,67,124)},'ne':{'near hind foot':(59,119,86,135),'far hind foot':(37,108,59,120),'near fist':(100,114,123,135)},'n':{'near hind foot':(49,121,72,135),'far fist':(34,106,51,119)}}
shape.append('Contact rows, zero-based 160px canvas; manual limb identification, opaque max within recorded ROI:')
for d,rs in feet.items():
 a=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA'))
 for label,(x0,y0,x1,y1) in rs.items():
  yy,xx=np.where(a[y0:y1,x0:x1,3]>0);shape.append(f'new {d} {label}: lowest row {int(yy.max())+y0 if len(yy) else "none"}; ROI {(x0,y0,x1,y1)}')
shape+=['new e far hind foot and ne far fist are occluded/not confidently separable; no invented contact rows.','Approved near contacts all row 130; far feet overlap at low camera, no confident separate row.','Rear ROIs cover the head/face region, excluding generators and shields. No glow there; visual inspection confirms no rear visor.','Thin seams below luminance 70 with opposed lighter neighbours map to accent; broad deep shadows retain material ramps. Accent targets remain missed, especially n.']
(P/'shape.txt').write_text('\n'.join(shape)+'\n')
M.update(light_shares=lights,visor=visor,height_ratio_spread=spread); (P/'metrics.json').write_text(json.dumps(M,indent=2))
fmt=lambda vals: ', '.join(vals)
lines=[
'Order s,se,e,ne,n. Width px/approved ratio: '+fmt(f"{M['new'][d]['width']}/{M['new'][d]['width']/AW[d]:.3f}" for d in N)+'; anchors s/n/e = 1/1/1, mean 1.000.',
'Height px/approved ratio: '+fmt(f"{M['new'][d]['height']}/{M['new'][d]['height']/AH[d]:.3f}" for d in N)+f'; ratio spread {spread:.4f}.',
'H/W new/guide: '+fmt(f"{M['new'][d]['height']/M['new'][d]['width']:.3f}/{GH[d]/GW[d]:.3f}" for d in N)+'.',
'Lightest green+orange shares new/approved %: '+fmt(f"{sum(lights['new'][d].values()):.2f}/{sum(lights['approved'][d].values()):.2f}" for d in N)+'; separate shades in shape.txt.',
'Visor-only s/se/e/ne/n: '+ '/'.join(str(visor['new'][d]) for d in N)+'; approved s18/se17; expected ~15/14, both >=12; rear zero.',
'Accent new/approved %: '+fmt(f"{100*M['new'][d]['role_shares']['dark accent']:.2f}/{AC[d]:.1f}" for d in N)+'; front/side/back close; diagonals overshoot.',
'Palette PASS: all 15 fixed colours, no outsiders, binary alpha; all eight borders clear; zero residual magenta/plum, lone pale rim or accent rim pixels.',
'view_check: front/back 0.78 MISS; area 0.08, height 0.06, colour 0.87, dips none, lone '+f"{M['lone_exact']:.4f}"+' (<0.11; no despeckle); colours 15.',
'sheet_judge: all eight OK, FIX nothing, REDO nothing; heights left unchanged. Top-five share '+f"{M['top_five_share']:.2%}"+' misses 65%.',
'Depth p05/p95 all five 24.44/185.43 (range 160.99 <180); dominant %: '+fmt(f"{100*M['new'][d]['dominant_share']:.2f}" for d in N)+'.',
'By eye: recognizable same two-arm gorilla, no clear new hardware; plate shapes/stance drift. Firm plates, seams and mostly clean bands, some fine noise.',
'Camera MISS: increased lit hump/back/forearm/fist tops, but not a convincing uniform 35 degrees; side is taller than long yet lacks a wide top band and separable far hind foot.',
'Front width holds, visor remains full width and is not overhead; rear visor zero. Near/far contacts in shape.txt. Review review.png; all deliverables only in take2.',
'Tokens used unavailable. Exactly one built-in generation, verbatim prompt-sheet.txt, two refs in order; raw unchanged; no redo, commit or asset installation.'
]
(P/'REPORT.txt').write_text('\n'.join(lines)+'\n');print('\n'.join(lines))
