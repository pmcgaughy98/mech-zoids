from pathlib import Path
import json
P=Path('D:/dev/new-mech-rpg/docs/art/moba/walk/fennec_s/stand35')
m=json.loads((P/'metrics.json').read_text()); N=['s','se','e','ne','n']; targets=[5,6.1,5.8,6.2,6.2]
notes='''Visual identification on the zero-based 160x160 canvases; near/far refers to camera distance, not left/right.
s: near front soles 140/140; far hind soles about 130/130, partly merged into near-leg silhouette.
se: near front 140, near hind 133; far front 136, far hind about 129 (partly occluded).
e: near hind 140, near front 139; far hind 133, far front 132.
ne: near hind 140, near front 129; far hind 136, far front about 126 (partly occluded).
n: near hind 140/140; far front about 121/121 (small side stubs, blending into hind-leg silhouette).
Belly e: central body columns 80-87 end at row 123; near soles 139/140, giving 15/16 intermediate rows (124-138/139). Near foot upper edges 133/134 leave 9/10 rows to the foot tops. Legs excluded from the body measurement.
Visible parts by eye (s,se,e,ne,n): four foot endpoints each; two full near legs plus partly hidden far legs in s/e/n; three clearer legs plus an occluded far leg in se/ne. No apparent fifth leg, third ear or second tail. Whole independently drawn far legs FAIL.
Same design family, ears, joint discs, chest and segmented tail retained; no obvious new part. Standing and mostly straight legs, but not every leg is whole or fully distinct; side fore/hind soles differ by 1px.
Tops visible and far feet higher throughout; common 35-degree pitch uncertain, especially the low-looking east view. Front ear width 43 vs seated 47 FAIL; front eye pixels 24 vs 28 and se 15 vs 18 meet floors but do not preserve full size. Firm plates/seams and clean bands; rear eye count zero.
'''
with (P/'shape.txt').open('a') as f:
 f.write('\nAccent comparisons (new/target): '+', '.join(f"{n} {100*m['new'][n]['role_shares']['dark accent']:.2f}/{t:.1f}%" for n,t in zip(N,targets))+'\n')
 f.write('Eye floors: s 24>=24 PASS; se 15>=15 PASS; rear ne/n 0/0 PASS. Seated s/se/e 28/18/12.\n'+notes)
(P/'tail.txt').write_text('Visual pixel inspection, including the hip joint/upper leg as part of the leg; gap means intervening clear background pixels in screen projection. Masks cannot distinguish hidden anatomy.\nn: minimum clear gap 0 px at upper hind-leg/hip boundaries; cream tip sits between shins, but no positive tail/leg clearance.\nne: minimum clear gap 0 px; tail base/segments adjoin near hip and overlap/obscure the far hind upper leg.\ne: minimum clear gap 0 px at the tail-root/upper hind-hip junction; distal horizontal tail clears lower legs.\nTail-clear-of-every-leg requirement FAIL. Tail straight in all three. See tail_legs_zoom.png, lower halves at 5x nearest on mid grey.\n')
with (P/'REPORT.txt').open('a') as f:f.write('\nStep 4 complete: shape, heights, palette, depth, tail, view_check and sheet_judge written. Visual misses recorded.\nStep 5 complete: review.png contains seated35, standing35 and old low-camera trot rows at 3x nearest; tail_legs_zoom.png at 5x nearest.\n')
# Supplemental audit metadata is separate from numeric metrics so copied script remains reviewable.
(P/'visual-notes.txt').write_text(notes)
report='''fennec-stand35: exactly one built-in image; verbatim prompt + two ordered refs; raw unchanged. Tokens unknown.
Scale: whole sheet 1254->267 nearest (0.212919); east 75 px PASS; south ears 43 vs seated 47, delta -4, MISS (tolerance 3).
Sizes s/se/e/ne/n: 43x57 / 54x61 / 75x60 / 55x69 / 36x68.
H/seated: .905/.897/.882/.908/.829; H/old trot: .792/.847/.811/.920/.883; informational, unchanged.
Eyes s/se/e/ne/n: 24/15/8/0/0 vs seated 28/18/12/0/0; floors PASS; full-size retention MISS.
Accent new/seated target (%): s 5.03/5.0; se 6.11/6.1; e 5.80/5.8; ne 6.19/6.2; n 6.20/6.2.
Palette PASS: fixed 15 only; no outsiders, magenta/plum, lone pale edge or accent rim; all eight borders clear.
view_check: front/back .62 MISS; lone .105738 PASS, no despeckle; top-five 78.30%; 15 colours.
sheet_judge: FIX none; REDO ne/n/nw solely height (exempt); mirrors e/w .898, ne/nw .895, se/sw .993.
Feet near/far rows: s 140/approximately130; se 140,133/136,approximately129; e 140,139/133,132; ne 140,129/136,approximately126; n 140/approximately121.
East belly bottom 123; near soles 139/140: 15/16 intermediate rows; to foot tops 9/10 rows.
Tail gaps n/ne/e: 0/0/0 px including upper hip contacts; ne also obscures far hind leg; clearance MISS.
Depth p05/p95; dominant: s 25.07/214.43,19.47%; se 18.86/214.43,20.80%; e 18.86/214.43,19.63%; ne 18.86/214.43,21.68%; n 18.86/214.43,23.71%.
By eye: same fennec parts, two ears/one straight tail, four foot endpoints each; no apparent extra parts. Full far legs obscured: MISS.
Standing, mostly straight legs, far feet higher; tops visible, common 35deg uncertain/east low-looking. Ear width and front eye size reduced: MISS.
Firm plates/seams, clean bands, no rear eyes PASS. Overall does not meet every requirement; no redo generated.
Saved five views_stand35 PNGs, checks, three-row review.png and tail_legs_zoom.png; writes confined to OUT/VIEWS.
'''
(P/'REPORT.txt').write_text(report)
print(report)
