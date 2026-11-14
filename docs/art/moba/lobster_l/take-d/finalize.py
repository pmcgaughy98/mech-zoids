from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, json, hashlib
P=Path(__file__).resolve().parent; C=P.parent/'take-c'
M=json.loads((P/'metrics.json').read_text()); cyan=json.loads((P/'cyan-counts.json').read_text()); mo=json.loads((P/'mottling.json').read_text())['views']; judge=json.loads((P/'sheet_judge.json').read_text())
ident={}
for d in ['s','se','sw','e','w']:
    x=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA')); y=np.array(Image.open(C/'views'/f'{d}.png').convert('RGBA'))
    ident[d]={'pixel_identical':bool(np.array_equal(x,y)),'changed_pixels':int(np.any(x!=y,axis=2).sum())}
assert all(x['pixel_identical'] for x in ident.values())
assert not any(M['border_contact'].values())
a=np.array(Image.open(P/'sheet_finished.png').convert('RGBA')); c=np.array(Image.open(C/'sheet_finished.png').convert('RGBA'))
palette=lambda v:set(map(tuple,np.unique(v[v[:,:,3]>0,:3],axis=0)))
assert palette(a)==palette(c)
assert np.array_equal(a[a.shape[0]//3:],c[c.shape[0]//3:])
(P/'identity.txt').write_text('\n'.join(f'{d}: pixel-identical={v["pixel_identical"]}; changed pixels={v["changed_pixels"]}' for d,v in ident.items())+'\nLower two sheet rows pixel-identical; exact C palette; binary alpha; no border contact.\n')
(P/'identity.json').write_text(json.dumps(ident,indent=2))
# Same close-cropped layout and scale in both comparison rows; no drawing changes.
ims={(take,d):Image.open(root/'views'/f'{d}.png').convert('RGBA') for take,root in [('C',C),('D',P)] for d in ['nw','n','ne']}
ims={key:im.crop(im.getbbox()) for key,im in ims.items()}
tw=max(im.width for im in ims.values())+8; th=max(im.height for im in ims.values())+12
review=Image.new('RGB',(tw*3+16,th*2),(128,128,128)); draw=ImageDraw.Draw(review)
for row,take in enumerate(['C','D']):
    draw.text((2,row*th+3),take,fill=(255,255,255))
    for col,d in enumerate(['nw','n','ne']):
        im=ims[take,d]; review.paste(im,(16+col*tw+(tw-im.width)//2,row*th+th-4-im.height),im)
review.resize((review.width*4,review.height*4),Image.Resampling.NEAREST).save(P/'review-back.png')
s=M['sizes']['s'][1]; shape=[]
for d in ['n','ne','nw']:
    h=M['sizes'][d][1]; shape.append(f'{d}: {h}px / s {s}px = {h/s:.5f}; no taller than south: {h<=s}; within 10 percent: {abs(h/s-1)<=.10}')
shape += [f'ne/nw mirrored silhouette similarity: {judge["notes"]["mirror ne/nw"]:.3f}',
'Visual assessment uses the single raw edit returned inline by image_gen; no extra source images opened.',
'Same machine: YES, gunmetal plates, inset red panels, red ring joints, steel legs/red feet, antenna rods and spined straight tail retained; no red tail/fan.',
'Camera: FAIL; still looking down at broad tail tops, not along the tail at ground level.',
'Fan: six apparent separate gunmetal plates in n, dark seams and brighter bevels; improved, but still a broad flat fan top.',
'Tail: no curl or sideways bend; elevated root/downward slope remains, flat-on-ground requirement FAIL.',
'Visible planted feet: n 6/6, ne 3/3, nw 3/3 by raw-image inspection; no claim about fully occluded feet.',
f'Cyan/lens pixels ne/n/nw: {cyan["ne"]}/{cyan["n"]}/{cyan["nw"]}; no rear face seen.',
'Size through turns: FAIL, backs taller than front; retained e/w remain shorter as in C.',
'Final review files generated as requested; visual judgments above refer to the raw returned edit, not reopened output PNGs.']
(P/'shape.txt').write_text('\n'.join(shape)+'\n')
n=M['depth']['n']; c_line=next(line for line in (C/'depth.txt').read_text().splitlines() if line.startswith('n:'))
lines=['Luminance = 0.2126R + 0.7152G + 0.0722B over all opaque n pixels.', 'Take C '+c_line, f'Take D n: p05 {n["p05"]:.2f}; p95 {n["p95"]:.2f}; range {n["p95"]-n["p05"]:.2f}; most common {n["dominant_colour"]} {n["dominant_share"]:.2%}; height {n["height"]}px.',
'Mottling candidates: enclosed 8-connected 1-3px same-material shade islands; excludes seams/material and silhouette contacts; mechanical details may count.']
lines += [f'{d}: {mo[d]["total"]} candidate islands; '+', '.join(f'{mat} {mo[d][mat]["islands"]}' for mat in ['gunmetal','red','steel']) for d in ['n','ne','nw']]
(P/'depth.txt').write_text('\n'.join(lines)+'\n'); (P/'mottling.txt').write_text('\n'.join(lines[3:])+'\n')
report=[
'By eye FIRST: same machine YES; gunmetal plates, red panels/rings, pale legs/red feet, antenna rods, straight spined tail; no red tail/fan.',
'Camera FAIL: rear still looks down on tail; root remains raised. Fan has six apparent bevelled plates/seams, but retains a broad flat top.',
'Visible feet planted n6/6 ne3/3 nw3/3; no curl/bend or rear face; cyan ne/n/nw 0/0/0. Turn-size consistency FAIL.',
'Kept s,se,sw,e,w are pixel-identical to C: zero changed pixels; lower two sheet rows unchanged.',
'Sizes W x H/area: n83x75/3925; ne114x74/4157; nw113x74/4166; s89x66/3444.',
'Height/s: n1.1364 ne1.1212 nw1.1212; all FAIL no-taller/within10%; ne/nw mirror0.992.',
'view_check: front/back0.82 PASS; area0.16 height0.26 colour0.82 dips none lone0.09; sheet_judge FAIL height e,ne,n,nw,w; FIX nothing.',
'Depth n C -> D: p05 18.86->30.84; p95 127.16->154.87; dominant24.02%->25.15%; height77->75; range124.02 still under180.',
'Mottling n/ne/nw: 44/40/37 enclosed 1-3px shade-island candidates; some small mechanical details may count; not clean enough.',
'ONE built-in edit; exact prompt; raw1254x1254 same as C, saved unchanged/hash in generation.json; tokens/cost unknown; no redo.',
'Exact C scale66/223 and all14 palette colours retained; median9 before palette; no post-palette despeckle; plum/magenta/lone-pale/ink rim0 after cleanup.',
'All eight192px views, no border contact, binary alpha; reviews/checks/scripts saved only in take-d; no install/commit/revert. Candidate fails requested back-view fix.'
]
assert len(report)<15
(P/'REPORT.txt').write_text('\n'.join(report)+'\n')
(P/'verification.json').write_text(json.dumps({'identity':ident,'exact_palette':True,'unchanged_lower_rows':True,'no_border_contact':True,'report_lines':len(report),'review_files':{f:Image.open(P/f).size for f in ['review.png','review-back.png','review-game-size.png']}},indent=2))
print((P/'REPORT.txt').read_text())
