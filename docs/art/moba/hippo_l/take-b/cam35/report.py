from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
P=Path('D:/dev/new-mech-rpg/docs/art/moba/hippo_l/take-b/cam35');m=json.loads((P/'metrics.json').read_text());prep=json.loads((P/'preparation.json').read_text());names=['s','se','e','ne','n'];a=m['approved'];b=m['new'];aw=[77,113,123,105,73];ah=[70,70,62,77,76];tw=[77,113,123,106,77];th=[90,89,82,98,98]
feet='Feet, zero-based rows; identities judged visually, rows measured in isolated foot regions. Approved: s front L/R 160/160, far occluded; se near hind/front 156/160, far front 158, far hind occluded; e near hind/front 160/160, far stubs not independently certain; ne near hind/front 160/157, far hind 158, far front occluded; n hind heels 160/160, forefeet occluded. New: s front L/R 160/160, far occluded; se near hind/front 135/160, far front 157, far hind occluded; e near hind/front 158/160, far feet overlap and cannot be assigned reliable separate bottom rows; ne near hind/front 160/136, far hind 154, far forefoot occluded; n hind heels 160/160, forefeet occluded. Four legs cannot be certified independently in each view.'
with (P/'shape.txt').open('a') as f:f.write('\n'+feet+'\n')
checks=(P/'view_check.txt').read_text().splitlines()[0]
ratios=[b[d]['width']/w for d,w in zip(names,aw)]
anchor=np.mean([ratios[0],ratios[4],ratios[2]])
# Verify delivery identity and palette against the final slices, not an earlier processing stage.
valid={tuple(bytes.fromhex(c['hex'])) for c in json.loads((P/'palette.json').read_text())}
for d in names:
 view=P.parent/'views_cam35'/(d+'.png'); assert view.read_bytes()==(P/'slices'/(d+'.png')).read_bytes()
 im=np.array(Image.open(view).convert('RGBA')); assert all(tuple(c) in valid for c in np.unique(im[im[...,3]>0,:3],axis=0))
assert hashlib.sha256((P/'sheet_raw.png').read_bytes()).hexdigest()==prep['raw_sha256']
lines=[
'Order s,se,e,ne,n. W (W/approved): '+', '.join(f"{b[d]['width']} ({b[d]['width']/w:.3f})" for d,w in zip(names,aw))+f'; anchor s/n/e 1.013/1.082/0.894, mean {anchor:.4f} (1.00 rounded). Tokens unavailable; one image, no redo.',
'H (H/approved): '+', '.join(f"{b[d]['height']} ({b[d]['height']/h:.3f})" for d,h in zip(names,ah))+f"; growth spread {m['height_spread']:.4f}.",
'H/W new/35-degree target: '+', '.join(f"{b[d]['height']/b[d]['width']:.3f}/{h/w:.3f}" for d,h,w in zip(names,th,tw))+f"; se/ne {b['se']['height']}/{b['ne']['height']}={m['se_ne']:.3f} (se 11.1% shorter).",
'Top rows: '+','.join(str(b[d]['top_row']) for d in names)+'; all eight 192 canvases clear of borders; feet and full metrics in shape.txt/heights.txt.',
'Lightest purple% new/approved: '+', '.join(f"{100*b[d]['light_shares']['a990e0']:.2f}/{100*a[d]['light_shares']['a990e0']:.2f}" for d in names)+'.',
'Lightest steel% new/approved: '+', '.join(f"{100*b[d]['light_shares']['e4e4ea']:.2f}/{100*a[d]['light_shares']['e4e4ea']:.2f}" for d in names)+'.',
'Eyes total[groups] new: '+', '.join(f"{b[d]['eye_pixels']}{b[d]['eye_groups']}" for d in names)+'; approved 39[20,19],20[18,2],21[21],0[],0[]. Minimums PASS; rear zero.',
'Accent% new/approved target: '+', '.join(f"{100*b[d]['role_shares']['dark accent']:.2f}/{v:.1f}" for d,v in zip(names,[6.1,6.1,5.9,6,5.9]))+'; all role shares and palette rim counts saved.',
'Palette PASS: 14 fixed colours, no extras; eyes protected; no detected magenta/plum fringe, lone pale rim pixels or accent rim. Raw SHA256 unchanged; five delivered copies verified.',
'view_check: '+'front/back'+checks.split('front/back',1)[-1]+f"; top5 {m['top_five_share']:.3f}. Lone .10 <= .11; no despeckle needed.",
'sheet_judge: FIX none; REDO e,ne,nw,w for height only (camera exception; no height fixes). Mirrors e/w .960, ne/nw .981, se/sw .971; palette 1.0 throughout.',
'Depth p05/p95/dominant%: '+', '.join(f"{b[d]['p05']:.1f}/{b[d]['p95']:.1f}/{100*b[d]['dominant_share']:.1f}" for d in names)+'; luminance span below canon 180.',
'By eye: recognizable same hippo, two ears/tusks, one jaw and tail plate where exposed; no obvious extra appendage; four legs cannot be certified through occlusion. Firm plates, seams and clean bands; no rear eyes.',
'Camera/width FAIL: lit head/back tops increase; front stays wide with deck above head and clear eyes/muzzle/jaw, not overhead. Side is 10.6% short and reads lower, its deck band and far-leg separation insufficient; joint-top lighting weak. One consistent 35-degree angle not achieved. Review: review.png; full evidence in OUT.'
]
assert len(lines)==14
(P/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
