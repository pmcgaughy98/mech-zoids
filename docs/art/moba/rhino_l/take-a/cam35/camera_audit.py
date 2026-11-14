from pathlib import Path
import json
P=Path('D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/cam35')
m=json.loads((P/'metrics.json').read_text()); names=['s','se','e','ne','n']; new=m['new']; guide=dict(zip(names,[(72,108),(89,100),(103,90),(89,100),(72,108)])); first=[.81,.87,.79,1.04,.99]; targets=[6.3,7.8,9.2,7.4,9.4]
hr={d:new[d]['height']/guide[d][1] for d in names}; wr={d:new[d]['width']/guide[d][0] for d in names}; spread=max(hr.values())-min(hr.values())
lines=[f"{d}: {new[d]['width']}x{new[d]['height']}; height/guide {hr[d]:.4f} {'PASS' if .85<=hr[d]<=1.08 else 'MISS'}; width/guide {wr[d]:.4f} {'PASS' if .85<=wr[d]<=1.08 else 'MISS'}; first try height/guide {old:.2f}" for d,old in zip(names,first)]
lines.append(f'Height ratio spread {spread:.4f}: MISS (limit 0.08); first try spread 0.25. Overall MISS. No height correction applied.')
(P/'heights.txt').write_text('\n'.join(lines)+'\n')
(P/'widths.txt').write_text('se: 85 px vs approved 89; minimum 84: PASS.\n'+'\n'.join(f'{d}: width/guide {wr[d]:.4f}' for d in names)+'\n')
feet='''Feet, visually identified with measured silhouette rows; zero-based on 192px canvas:
approved s: near front pair 160; farther pads partly exposed at 158, assignment uncertain.
approved se: near hind 160, near front 159; farther visible hind pad 158.
approved e: near hind/front 160; farther exposed pads 159.
approved ne: near hind 160, other hind 158; farther/front visible pad 157.
approved n: near hind pair 160; farther pads occluded, no reliable row.
new s: near front pair 160; farther pads occluded, no reliable row.
new se: near hind 160, near front 155; farther visible hind pad 143.
new e: near hind/front 160; far feet occluded/not separable, no evidence of raised far pads.
new ne: near hind 160, other hind 150; farther/front visible pad 139.
new n: near hind pair 160; farther pads occluded, no reliable row.
'''
shape=(P/'shape.txt').read_text().split('Feet, visually identified')[0]
shape+=feet+'\nAccent new/approved target (%):\n'+'\n'.join(f"{d}: {new[d]['role_shares']['accent']*100:.2f}/{target:.1f}" for d,target in zip(names,targets))+'\n'
(P/'shape.txt').write_text(shape)
report=[
'Angle height/guide (new vs first): '+', '.join(f'{d} {hr[d]:.3f}/{old:.2f}' for d,old in zip(names,first))+f'; spread {spread:.3f} vs 0.250: MISS.',
'Angle width/guide: '+', '.join(f'{d} {wr[d]:.3f}' for d in names)+'; all width ratios PASS.',
'SE width 85 px vs approved 89; minimum 84: PASS. East 103 px; one shared nearest shrink.',
'Accent new/approved (%): '+', '.join(f"{d} {new[d]['role_shares']['accent']*100:.2f}/{v:.1f}" for d,v in zip(names,targets))+'.',
'Palette PASS: all 12 fixed colours, no extras; no magenta/plum, lone pale rim pixels or rim accent; all eight borders clear.',
f"view_check: front/back 0.85; area 0.07; height 0.27; colour 0.93; dips none; lone 0.08 (exact {m['lone_exact']:.5f}); 12 colours. No despeckle needed.",
'sheet_judge: FIX nothing; REDO e/ne/n/nw/w solely for height; informational here, no height repair or new generation. Mirror 0.950/0.950/0.953.',
'Depth p05/p95, dominant share: '+', '.join(f"{d} {new[d]['p05']:.2f}/{new[d]['p95']:.2f}, {new[d]['dominant_share']:.2%}" for d in names)+'.',
'By eye: recognizable same rhino, no obvious new parts; consistent 35-degree camera NO. Side top band inadequate; far feet not separately visible.',
'By eye: front face/horn clear and full-size; plates remain rounder than approved; interior seams retained, clean bands. Rear eye pixels ne=0, n=0.',
'Built-in image tool: exactly ONE image, verbatim prompt-sheet.txt, approved_views then angle_guide; raw saved unchanged. Tokens used unavailable.',
'Files: cam35/sheet_raw.png, sheet_finished.png, review.png and audit .txt/.json; views_cam35 contains only s/se/e/ne/n.png. Overall angle MISS; stopped without redo.'
]
(P/'REPORT.txt').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
assert len(report)<15
assert sorted(x.name for x in (P.parent/'views_cam35').iterdir())==['e.png','n.png','ne.png','s.png','se.png']
