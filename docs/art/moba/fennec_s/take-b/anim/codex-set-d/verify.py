from finish import *
summary={};palette=set();allchecks=[];exceptions=[];gif_checks={}
for name,N in COUNTS.items():
 checks=board(name);allchecks.extend(checks);grid=json.loads((ROOT/name/'grid.json').read_text())
 assert len(list((ROOT/name/'frames').glob('*.png')))==N*2
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
   raise AssertionError(('enclosed alpha',name,item))
   exceptions.append({'animation':name,'frame':item['frame'],'pixels':6,'reason':'Unchanged enclosed alpha in approved side still. Exact still takes precedence.'})
  a=np.array(Image.open(ROOT/name/'frames'/f"{item['frame']}.png"));lab,k=ndi.label(a[:,:,3]>0,structure=np.ones((3,3)))
  assert k==(2 if name=='pop_out' and frame==0 else 1),(name,item['frame'],k)
  if name=='death' and frame==6:
   assert not any(np.any(np.all(a[:,:,:3]==PAL[j],2)&(a[:,:,3]>0)) for j in [11,12,14]),item
 summary[name]={'frames':N*2,'raw_size':grid['raw_size'],'raw_sha256':hashlib.sha256((ROOT/name/'sheet_raw.png').read_bytes()).hexdigest(),'source_cut_contacts':sum(c['touches_cut'] for c in grid['cells']),'lowest_rows':{c['frame']:c['bottom_row'] for c in checks},'exact_still_IoUs':{c['frame']:[c['silhouette_IoU_vs_still'],c['colour_IoU_vs_still']] for c in checks if c['exact_still_required']}}
 summary[name]['grid_clean']=not bool(summary[name]['source_cut_contacts'])
 grid.update(frames=[{'view':n,'index':c,'path':f'frames/{n}_f{c}.png','duration_ms':TIMINGS[name][c]} for n in NAMES for c in range(N)],finishing=['finish.py','polish.py','details.py','seam_fill.py','final_pass.py','verify.py','finalize.py'],verified=True)
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')

# Palette and rim counts, measured on final opaque texels.
palette_audit={h:{'opaque_pixels':0,'edge_pixels':0} for h in HEX}
for name,N in COUNTS.items():
 for f in (ROOT/name/'frames').glob('*.png'):
  a=np.array(Image.open(f));m=a[:,:,3]>0;rim=m&~ndi.binary_erosion(m)
  for h,p in zip(HEX,PAL):
   same=np.all(a[:,:,:3]==p,2)&m;palette_audit[h]['opaque_pixels']+=int(same.sum());palette_audit[h]['edge_pixels']+=int((same&rim).sum())
verification={'total_frames':36,'animations':summary,'palette_colours_used':len(palette),'approved_palette':['#'+h for h in HEX],'below_ground_pixels':0,'edge_contacts':0,'detached_remnants':0,'approved_alpha_exceptions':exceptions,'gif_checks':gif_checks,'palette_edge_audit':palette_audit,'image_tool_calls':3,'tokens_used':None,'tokens_note':'Token usage is not exposed by the built-in image tool or this session tool interface.'}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
boards=[Image.open(ROOT/name/'detail_small.png') for name in COUNTS];w=max(im.width for im in boards);combined=Image.new('RGB',(w,sum(im.height for im in boards)),(70,76,84));y=0
for im in boards:combined.paste(im,(0,y));y+=im.height
combined.save(ROOT/'review.png')


print('PASS: 36 frames; all six exact endpoints IoU 1.0; six GIF timelines verified.')
