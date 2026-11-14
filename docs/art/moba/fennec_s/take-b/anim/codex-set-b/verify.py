from finish import *
summary={};palette=set();allchecks=[];exceptions=[];gif_checks={}
for name,N in COUNTS.items():
 checks=board(name);allchecks.extend(checks);grid=json.loads((ROOT/name/'grid.json').read_text())
 assert len(list((ROOT/name/'frames').glob('*.png')))==N*3
 for n in NAMES:
  for c in range(N):
   im=Image.open(ROOT/name/'frames'/f'{n}_f{c}.png');assert im.size==(192,192)
   a=np.array(im);palette.update(map(tuple,a[a[:,:,3]>0,:3]))
   required=(name in ['dig','death'] and c==0) or (name=='pop_out' and c==4)
   if required:assert np.array_equal(a,np.array(approved(n))),(name,n,c,'exact pixels')
  gif=Image.open(ROOT/name/f'preview_{n}.gif');duration=[]
  for c in range(gif.n_frames):gif.seek(c);duration.append(gif.info['duration'])
  assert duration==TIMINGS[name],(name,n,duration)
  assert 'loop' not in gif.info  # One-shot previews stop on held final frame.
  gif_checks[f'{name}/{n}']={'frames':gif.n_frames,'durations_ms':duration,'loop':False}
 for item in checks:
  frame=int(item['frame'].split('_f')[1]);assert item['palette_ok'] and item['binary_alpha']
  assert not item['pixels_below_160'] and not item['canvas_edge'] and not item['stray_components']
  assert item['bottom_row']==(145 if name=='pop_out' and frame==2 else 160),item
  if item['exact_still_required']:assert item['silhouette_IoU_vs_still']==1 and item['colour_IoU_vs_still']==1
  if item['enclosed_hole_pixels']:
   assert item['exact_still_required'] and item['frame'].startswith('side_') and item['enclosed_hole_pixels']==6,item
   exceptions.append({'animation':name,'frame':item['frame'],'pixels':6,'reason':'Unchanged enclosed alpha in approved side still. Exact still takes precedence.'})
  a=np.array(Image.open(ROOT/name/'frames'/f"{item['frame']}.png"));lab,k=ndi.label(a[:,:,3]>0,structure=np.ones((3,3)))
  assert k==(2 if name=='pop_out' and frame==0 and not item['frame'].startswith('side') else 1),(name,item['frame'],k)
  if name=='death' and frame==6:
   assert not any(np.any(np.all(a[:,:,:3]==PAL[j],2)&(a[:,:,3]>0)) for j in [11,12,14]),item
 summary[name]={'frames':N*3,'raw_size':grid['raw_size'],'raw_sha256':hashlib.sha256((ROOT/name/'sheet_raw.png').read_bytes()).hexdigest(),'source_cut_contacts':sum(c['touches_cut'] for c in grid['cells']),'lowest_rows':{c['frame']:c['bottom_row'] for c in checks},'exact_still_IoUs':{c['frame']:[c['silhouette_IoU_vs_still'],c['colour_IoU_vs_still']] for c in checks if c['exact_still_required']}}
 assert not summary[name]['source_cut_contacts']
 grid.update(frames=[{'view':n,'index':c,'path':f'frames/{n}_f{c}.png','duration_ms':TIMINGS[name][c]} for n in NAMES for c in range(N)],finishing=['finish.py','polish.py','final_pass.py'],verified=True)
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')

# Palette and rim counts, measured on final opaque texels.
palette_audit={h:{'opaque_pixels':0,'edge_pixels':0} for h in HEX}
for name,N in COUNTS.items():
 for f in (ROOT/name/'frames').glob('*.png'):
  a=np.array(Image.open(f));m=a[:,:,3]>0;rim=m&~ndi.binary_erosion(m)
  for h,p in zip(HEX,PAL):
   same=np.all(a[:,:,:3]==p,2)&m;palette_audit[h]['opaque_pixels']+=int(same.sum());palette_audit[h]['edge_pixels']+=int((same&rim).sum())
verification={'total_frames':54,'animations':summary,'palette_colours_used':len(palette),'approved_palette':['#'+h for h in HEX],'below_ground_pixels':0,'edge_contacts':0,'detached_remnants':0,'approved_alpha_exceptions':exceptions,'gif_checks':gif_checks,'palette_edge_audit':palette_audit,'image_tool_calls':3,'tokens_used':None,'tokens_note':'Token usage is not exposed by the built-in image tool or this session tool interface.'}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
boards=[Image.open(ROOT/name/'detail_small.png') for name in COUNTS];w=max(im.width for im in boards);combined=Image.new('RGB',(w,sum(im.height for im in boards)),(70,76,84));y=0
for im in boards:combined.paste(im,(0,y));y+=im.height
combined.save(ROOT/'review.png')

lines=['FENNEC S / TAKE B / CODEX SET B / 2026-11-04','54 transparent native-scale 192x192 PNG frames: dig 18; pop_out 15; death 21.','Built-in image tool: exactly THREE calls, one sheet per animation; no redo or variations.','Tokens used: unavailable. Neither image generation nor the session tools exposes token totals; no estimate is presented as usage.','', 'METHOD','Read both ape_l take-a codex sets, prompts, references, reports, finish/polish/gems/seam_fill/verify scripts. Used the same reference-sheet, slice, native-detail restore, seam cleanup, board and check method.','Approved front/side/back stills and 6x nearest-neighbour copies on magenta are in refs/. Each sheet attached all three approved 6x stills in that order. Exact generation prompts are in prompts/. All raw sheets retained unmodified.','Clean gutters define per-row slice boundaries. grid.json records source boxes, source bounds, one fixed conversion factor per view (from the neutral reference column), placements, durations and frame paths. Generated poses are never independently fit or normalized. Native restored parts are translated or rigid-rotated, never resized.','Native face, half-closed eyes and muzzle, full heads and ears on upright poses, cream inner-ear texels on compatible drooped poses, exposed grey joint discs, straight grounded tail segments and tips are restored from the approved stills. Occluded parts are not invented.','finish.py snaps to the shared 15-colour palette, uses binary alpha and a dark one-texel rim. polish.py restores native parts; final_pass.py restores straight tails, darkens the final eyes, fills enclosed seams through clean(), removes detached old-head remnants and builds detail boards.','', 'VALIDATION','All 54: approved palette only; binary alpha; no pixels below row160; no edge contacts; no detached debris. Source cuts have zero silhouette contacts.','Exact still offset (+16,+20). Dig f0, death f0, pop_out f4 in ALL three views: silhouette IoU 1.000000; exact-colour IoU 1.000000.','pop_out f0 follows its specific ear-tips-only instruction, overriding the generic f0=still rule. It contains native ear tips clipped at row160.','pop_out airborne f2 lowest row: front=145, side=145, back=145. Every other frame has lowest row160, including the clipped dig descent.','Dig f3 front half is underground; f4 exposes reduced rump/hind-limb edge and straight tail; f5 only the native gold-cream tail tip remains. No hole or dirt.','Death staggers, ears hinge outward/down, short legs buckle and body slumps onto its side. Native straight tail is flat. Final f6 teal/mint/white eye pixels take #2e1a6e and the frame is held for 1400ms. All GIFs are one-shot and stop on the final frame.','Exception: the approved SIDE still has SIX enclosed transparent pixels. They are preserved in dig side_f0, death side_f0 and pop_out side_f4 to keep exact IoU 1.0. All newly drawn frames have zero enclosed holes.','Per-frame geometry, colour counts, durations, IoUs and holes: each checks.txt. Full machine-readable results and per-colour edge counts: verification.json.','', 'VISUAL REVIEW','Viewed all three-view review and enlarged detail boards after native finishing. Corrected shrinking rear ears, cut-neighbor tail tips, clipped underground descent, copied chest colours leaking into joint patches, detached old-ear remnants, straight tail segments and remaining bright final-eye highlights.','Generated extreme-pose armour contours still have small drawing differences from the approved stills. Exact endpoints and native visible identity parts are enforced; no claim of pixel identity for changed poses.','', 'DELIVERY']
for name,N in COUNTS.items():
 lines += [f"{name}: {N} moments x 3 views; durations_ms={TIMINGS[name]}; raw_size={summary[name]['raw_size']}; raw_sha256={summary[name]['raw_sha256']}"]
lines += ['Each animation: frames/, sheet_raw.png, slices/, grid.json, checks.txt, three preview GIFs, review.png (approved still leftmost in every row), review_small.png, detail_board.png, detail_small.png.','Root review.png combines the three animations. Prompts, refs, restoration logs, scripts and verification are retained.','Rebuild in order: python finish.py; python polish.py; python final_pass.py; python verify.py.','Only this codex-set-b folder was written by finishing. The built-in tool used its managed default cache; its outputs were copied here. No game installation or commit.']
(ROOT/'REPORT.txt').write_text('\n'.join(lines)+'\n')
print('PASS: 54 frames; 15 colours; exact still IoUs 1.0; pop_out air lowest145; 9 GIFs/timelines verified.')
print('Approved side-still alpha exceptions:',len(exceptions),'x six pixels; no new enclosed holes.')
