from finish import *
summary={};palette=set()
for name,N in COUNTS.items():
 checks=board(name)
 seams=json.loads((ROOT/'seam_log.json').read_text())
 for c in checks:c.update(seams.get(name+'/'+c['frame'],{}))
 (ROOT/name/'checks.txt').write_text('Native 15-colour palette; exact still offset (+16,+30); lift is 160 minus lowest row.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 grid=json.loads((ROOT/name/'grid.json').read_text())
 print(name,'cut contacts',[(c['view'],c['frame']) for c in grid['cells'] if c['touches_cut']])
 for n in NAMES:
  assert len(list((ROOT/name/'frames').glob(f'{n}_f*.png')))==N
  assert np.array_equal(np.array(Image.open(ROOT/name/'frames'/f'{n}_f0.png')),np.array(approved(n)))
  if name in ['chest_beat','hex_shield']:assert np.array_equal(np.array(Image.open(ROOT/name/'frames'/f'{n}_f{N-1}.png')),np.array(approved(n)))
  for c in range(N):
   im=Image.open(ROOT/name/'frames'/f'{n}_f{c}.png');assert im.size==(192,192)
   a=np.array(im);palette.update(map(tuple,a[a[:,:,3]>0,:3]))
 for c in checks:
  endpoint=c['frame'].endswith('_f0') or (name in ['chest_beat','hex_shield'] and c['frame'].endswith(f'_f{N-1}')) or (name=='idle' and c['frame'].endswith('_f4'))
  assert c['bottom_row']==160 and (not c['enclosed_hole_pixels'] or endpoint) and not c['pixels_below_160'] and not c['canvas_edge'] and not c['stray_components'] and c['palette_ok'] and c['binary_alpha'],c
 summary[name]={'frames':N*2,'bottom_rows':sorted(set(c['bottom_row'] for c in checks)),'below_ground_pixels':0,'edge_contacts':0,'stray_components':0,'frame0_iou':{c['frame']:c['frame0_IoU'] for c in checks if c['frame0_IoU'] is not None},'raw_sha256':hashlib.sha256((ROOT/name/'sheet_raw.png').read_bytes()).hexdigest(),'raw_size':grid['raw_size']}
 grid.update(clean=not any(c['touches_cut'] for c in grid['cells']),final_canvas=[192,192],approved_offset=[16,30],ground_row=160,finishing=['finish.py','polish.py','gems.py','final_pose.py','seam_fill.py','verify.py'])
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
print('Frames',sum(v['frames'] for v in summary.values()),'palette',len(palette))
(ROOT/'verification.json').write_text(json.dumps({'animations':summary,'palette_opaque_colours':len(palette),'total_frames':54},indent=2)+'\n')

# Record final bounds and approved offset, not just original generated placement.
for name,N in COUNTS.items():
 p=ROOT/name/'grid.json';g=json.loads(p.read_text())
 for c in g['cells']:
  c['final_bbox']=list(Image.open(ROOT/name/'frames'/f"{c['view']}_f{c['frame']}.png").getbbox())
  c['final_source']='native approved pixel parts' if name in ['idle','walk'] or c['frame']==0 or c['frame']==N-1 else 'generated silhouette + native detail patches'
 g['finishing']=['finish.py','polish.py','gems.py','final_pose.py','seam_fill.py','gem_cleanup.py','verify.py'];p.write_text(json.dumps(g,indent=2)+'\n')

# Source grid audit uses pre-opening masks, so cleanup cannot hide raw cut contacts.
for name,N in COUNTS.items():
 p=ROOT/name/'grid.json';g=json.loads(p.read_text());raw=np.array(Image.open(ROOT/name/'sheet_raw.png').convert('RGBA'))
 for c in g['cells']:
  if name=='idle':continue
  x0,y0,x1,y1=c['source_box'];aa=raw[y0:y1,x0:x1];rgb=aa[:,:,:3].astype(int)
  mask=(aa[:,:,3]>220)&~((rgb.min(2)>195)&(np.ptp(rgb,axis=2)<24))
  mask &= ~((rgb[:,:,0]>200)&(rgb[:,:,1]<70));mask &= ~((rgb[:,:,1]>245)&(rgb[:,:,0]<130));mask &= ~((rgb[:,:,0]>180)&(rgb[:,:,1]>190)&(rgb[:,:,2]<90))
  labs,k=ndi.label(mask);sz=np.bincount(labs.ravel());sz[0]=0;mask=labs==sz.argmax()
  c['raw_cut_border_pixels']=int(mask[0].sum()+mask[-1].sum()+mask[:,0].sum()+mask[:,-1].sum())
  c['touches_raw_cut']=bool(c['raw_cut_border_pixels'])
 g['clean_after_isolation']=not any(c['touches_cut'] for c in g['cells'])
 g['clean']=name=='idle' # Generated sources contain saturated fringe debris even when gutters separate.
 g['raw_grid_note']='native contact sheet; no generation' if name=='idle' else 'Two rows and requested column count; raw saturated fringe debris, tight gutters. Largest-component isolation, fringe rejection and one-native-texel outline used. No redo.'
 g['walk_support_note']='SE far support gauntlet extends two pixels down in f4-f7; support endpoint fixed throughout that phase, near support fixed f0-f3. No whole-frame translations.' if name=='walk' else None
 if name=='walk':
  for c in g['cells']:
   f=c['frame'];c['native_torso_bob']=[0,-1,0,1,0,-1,0,1][f];c['diagonal_A_lift']=[0,0,0,0,0,2,3,1][f];c['diagonal_B_lift']=[0,2,3,1,0,0,0,0][f]
 p.write_text(json.dumps(g,indent=2)+'\n')
 for n in NAMES:
  gif=Image.open(ROOT/name/f'preview_{n}.gif');actual=[]
  for i in range(gif.n_frames):gif.seek(i);actual.append(gif.info['duration'])
  assert actual==TIMINGS[name],(name,n,actual)
 print(name,'GIF timing exact; raw-cut contacts',[(c['view'],c['frame']) for c in g['cells'] if c.get('touches_raw_cut')])
# Recheck the copied prompt columns byte-for-byte as text.
for name in ['walk','chest_beat','hex_shield']:
 old=(ROOT.parent/'codex-set-a'/'prompts'/f'{name}.txt').read_text();new=(ROOT/'prompts'/f'{name}.txt').read_text()
 assert next(x for x in old.splitlines() if x.startswith('Columns numbered'))==next(x for x in new.splitlines() if x.startswith('Columns numbered'))
print('Prompt columns unchanged; all endpoint exact-colour and silhouette IoU = 1.0')
