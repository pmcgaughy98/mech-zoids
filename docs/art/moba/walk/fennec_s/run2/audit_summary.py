import json
from pathlib import Path
R=Path('.')
a=json.loads((R/'verification.json').read_text())
for v in ['ne','e','s','n']:
 print(v)
 for q in a[v]['structure']:
  print(q['frame'],{k:q[k] for k in ['off_palette_pixels','stray_pixels','holes','upper_paint_diff_pixels','upper_canvas_diff_pixels']})
 for n,d in a[v]['feet'].items():
  for q in d['frames']:
   if q['lower_below_joint_match']<1 or q['knee_native_match']<1 or q['stamp_match']<1:print(n,q['frame'],{k:q[k] for k in ['stamp_match','ends','lower_below_joint_match','knee_native_match']})
