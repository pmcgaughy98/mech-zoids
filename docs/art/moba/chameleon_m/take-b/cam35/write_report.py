from pathlib import Path
import json
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parent; V=P.parent/'views_cam35'
report='''One built-in image, supplied prompt verbatim, exactly two references; tokens unavailable. Raw e/s 1.7653 vs 1.71 (clears 1.60); overall MISSES remain.
Order s/se/e/ne/n: sizes 48x78 / 63x76 / 85x51 / 68x76 / 47x79; W/approved 0.9796 / 0.9692 / 1.0119 / 1.0462 / 1.0000.
H/approved: 1.2000 / 1.2258 / 0.8644 / 1.2258 / 1.2540.
H/W (target): 1.6250(1.6531) / 1.2063(1.1692) / 0.6000(0.7381) / 1.1176(1.2000) / 1.6809(1.6809).
Growth spread max-min 0.3896 (max/min 1.4507); se/ne 76/76=1.00; final e/s 1.7708; top rows 63/65/90/65/62; anchor mean 0.9972, rounding to 1.00.
Side: median lit-band depth 9 rows, measured by highlight boundary proxy; a firm separate top/side seam is not established. Near feet bottom 140; far feet unresolved, >=6-row rise test MISS.
Lightest turquoise+steel shares new/approved (%): 22.29/12.56 / 20.76/13.70 / 20.63/10.45 / 19.85/12.27 / 22.06/11.40.
Lens totals 54/38/29/0/0; groups s28+26 (one below28 MISS), se38 (>=37), e29 (<30 MISS); expected about s32+32/se42/e34; rear zero PASS.
Accent new/approved (%): 7.13/7.3 / 6.09/6.0 / 8.13/8.2 / 6.24/6.0 / 7.00/7.1.
Palette PASS: every opaque pixel in the fixed 16; no off-palette colours, magenta/plum fringe, lone pale rim pixels or accent rim pixels; no canvas border contact.
view_check all eight: front/back0.74 (<0.80), area0.16(s>se), height0.33(w>sw), colour0.89(n>nw), dips none, lone0.07, max15 colours/view; no despeckle required or run.
sheet_judge all eight: FIX nothing; REDO e,w for height51 vs median76 (information only; no same-height correction). Mirrors e/w0.941, ne/nw0.988, se/sw0.894.
Depth p05/p95 all five 18.86/225.63; dominant shares (%) 16.73/16.99/19.18/21.93/20.15.
By eye: recognizable same chameleon, one spiral tail, no obvious new parts; front has both turret lenses, clear jaw/clamps, back above head and coil on one side, not straight overhead; diagonal heights agree; broad lit head/back/turret/coil/joint tops, firm plates/seams and clean bands improve pitch. Side length holds but profile is shallow and only two clamp feet resolve: exactly four legs, two toe blocks per foot and a common35-degree angle cannot be certified. Rear lenses absent. Review: review.png; all detailed checks saved alongside it; five delivered views in ../views_cam35.
'''
assert len(report.splitlines())<15
(P/'REPORT.txt').write_text(report)
for name in ['sheet_raw.png','sheet_finished.png','review.png','view_check.txt','sheet_judge.txt','heights.txt','palette-check.txt','shape.txt','side.txt','depth.txt','REPORT.txt']:
 assert (P/name).is_file(),name
assert sorted(x.name for x in V.iterdir())==['e.png','n.png','ne.png','s.png','se.png']
for d in ['s','se','e','ne','n']:
 im=Image.open(V/f'{d}.png'); assert im.size==(160,160)
 assert np.array_equal(np.array(im),np.array(Image.open(P/'slices'/f'{d}.png')))
print('Verified required artifacts; VIEWS contains exactly five 160px copies; REPORT has',len(report.splitlines()),'lines.')
