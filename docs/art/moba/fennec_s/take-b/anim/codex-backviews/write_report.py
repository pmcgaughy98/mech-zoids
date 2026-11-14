from finish import *
P=json.loads((R/'proportions.json').read_text());V=json.loads((R/'verification.json').read_text());S=json.loads((R/'support_checks.json').read_text())
lines=['FENNEC TAKE B / BACK VIEW REDRAW / 2026-11-04',
 'Cost: exactly TWO built-in image-generation calls, one per move; no redo/variation. Token usage unavailable. Prompts in prompts/.',
 'Method: generated whole-cell underdrawing, fixed 0.285 scale per row, 15-colour snap, extensive direct native-pixel contour/colour repaint. No approved still parts pasted; stills used only at kick f0/f5.']
for name in COUNTS:
 g=json.loads((R/name/'grid.json').read_text());lines.append(f"{name}: sheet {g['raw_size'][0]}x{g['raw_size'][1]}, SHA256 {g['raw_sha256']}; clean empty source gutters: {g['source_grid_clean']}.")
lines += ['Checks: 28/28 transparent 192x192, binary alpha, approved palette only, lowest opaque row160, none below160/at canvas edges, one connected body, zero holes or stray components.',
 'Kick back/ne f0 and f5: RGBA bytes identical to approved still at (+16,+20), silhouette IoU=1.0 and colour IoU=1.0; paired PNG files also byte-identical.',
 'Walk: diagonal A planted f0-f3, B planted f3-f7; swing clearance 2,3,4px, landing f3/f7. Actual planted RGBA ground spans fixed; NE swing advances 0,1,2px. Side trot f0-f7 inspected.',
 'Kick: hind ground spans identical f1-f4; forepads removed at f3, release paws forward/up where visible. Stills have pads above grounded tail tip; exact endpoints preserve that.',
 'Four GIFs reopened: 8 walk frames at 100ms looping; 6 kick frames at 260,130,130,90,160,280ms once. Boards use provided selout() at native resolution then 4x nearest-neighbour.',
 'Measurement key: E=left/right ear WxH, H=head width, B=body width, L=visible hind-leg width x length, t=shank thickness, F=foreleg length/thickness, T=straight tail axial pixels/visible violet plates (+one cream tip).',
 'Parts overlap: manual masks/landmarks in proportions.json; ear/head/body/leg extents measured from occupied pixels. Shank edges, tail axes/counts and NE foreleg joint chain manually tagged. N forelegs occluded; full length not independently measurable.']
def fmt(m):
 es='/'.join(f'{w}x{h}' for w,h in m['ears_wh']);leg='x'.join(map(str,m['hind_leg_wh']));fore='occluded' if m['foreleg_length'] is None else f"{m['foreleg_length']}/{m['foreleg_thickness']}"
 return f"E{es} H{m['head_width']} B{m['body_width']} L{leg} t{m['shank_thickness']} F{fore} T{m['tail_axis_pixels']}/{m['visible_violet_tail_plates']}"
for v in ['back','ne']:lines.append(f"Approved {v}: {fmt(P['reference_measurements'][v])}.")
for name,N in COUNTS.items():
 for v in ['back','ne']:
  for start in range(0,N,2):
   entries=[next(f for f in P['frames'] if f['move']==name and f['view']==v and f['frame']==i) for i in [start,start+1]]
   lines.append(f'{name}/{v} '+ '; '.join(f"f{e['frame']} [{fmt(e['measurements'])}]" for e in entries)+'.')
lines += ['Proportions: tagged extents vary by at most 1px vs still (N left ear +1px width; NE left ear -1px width); every frame within requested 2px. Limb/tail dimensions and plate counts held. Body heights drawn 19px in both views.',
 'By eye walk/N: whole connected parts, no visible cutoffs/seams; upright full-size ears, broad torso, short standing legs; back angle held in all 8; diagonal lift/landing beats read, forelegs partly hidden.',
 'By eye walk/NE: whole parts, no visible cutoffs; fixed head, short legs, straight short segmented tail; up-right rear angle held in all 8; lifted paws advance, planted paws hold, side timing matched.',
 'By eye kick/N: whole parts, no visible cutoffs; proportions held through dip/release; straight rear angle in all 6; shoulders/head convey mostly occluded front-paw dig/fling; hind feet planted.',
 'By eye kick/NE: whole parts, no visible cutoffs; proportions held, rear angle in all 6; crouch/dig, up-forward paw release and settle read; f0/f5 exact seated recovery. Both final boards inspected after fixes.',
 'Files: per move sheet_raw.png, slices/, frames/, grid.json, checks.txt, two preview GIFs, board.png (still + live row + new row for each view). Root proportions.json, verification.json, support_checks.json and pixel_edits.json.',
 'Rebuild: python -B finish.py walk sand_kick; python -B redraw.py; python -B finalize.py. Scripts and deliverables written only here; image tool automatically retained originals in its managed .codex/generated_images cache. No assets/tools changed; no commit.']
assert len(lines)<40,len(lines)
assert all(f['within_two_px'] for f in P['frames'])
for v in ['back','ne']:
 assert (R/'sand_kick/frames'/f'{v}_f0.png').read_bytes()==(R/'sand_kick/frames'/f'{v}_f5.png').read_bytes()
 # Updated reference copies attached to the generator match the approved source RGBA.
 assert np.array_equal(np.array(Image.open(R/'refs'/('n.png' if v=='back' else 'ne.png')).convert('RGBA')),np.array(Image.open(R.parent.parent/'views'/('n.png' if v=='back' else 'ne.png')).convert('RGBA')))
# Actual visible hind-foot clearance, sampled along each pad centre after forward swing.
clearance={}
for v,centres in [('back',[83,107]),('ne',[111,100])]:
 values=[]
 for i in range(8):
  a=np.array(Image.open(R/'walk/frames'/f'{v}_f{i}.png'));e=next(e for e in P['frames'] if e['move']=='walk' and e['view']==v and e['frame']==i)['annotation'];sh=e.get('hind_x_shift',[0,0]);m=a[:,:,3]>0
  pair=[160-int(np.where(m[:,x+dx])[0].max()) for x,dx in zip(centres,sh)]
  assert pair==e['hind_lifts'],(v,i,pair,e['hind_lifts']);values.append(pair)
 clearance[v]=values
(R/'lift_checks.json').write_text(json.dumps(clearance,indent=2)+'\n')
(R/'REPORT.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(f'Final report: {len(lines)} lines. Endpoints byte-identical; updated references verified; rendered lifts correct; all tagged extents within 2px.')
