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
  gif=Image.open(ROOT/name/f'preview_{n}.gif');durations=[]
  for gi in range(gif.n_frames):gif.seek(gi);durations.append(gif.info['duration'])
  assert durations==TIMINGS[name],(name,n,durations)
  if name in ['bound','hex_dome']:assert np.array_equal(np.array(Image.open(ROOT/name/'frames'/f'{n}_f{N-1}.png')),np.array(approved(n)))
  for c in range(N):
   im=Image.open(ROOT/name/'frames'/f'{n}_f{c}.png');assert im.size==(192,192)
   a=np.array(im);palette.update(map(tuple,a[a[:,:,3]>0,:3]))
 for c in checks:
  assert c['bottom_row']==(160-LIFTS.get(int(c['frame'].split('_f')[1]),0) if name=='bound' else 160) and (not c['enclosed_hole_pixels'] or c['frame'].endswith('_f0') or (name=='bound' and c['frame'].endswith('_f8')) or (name=='hex_dome' and c['frame'].endswith('_f7'))) and not c['pixels_below_160'] and not c['canvas_edge'] and not c['stray_components'] and c['palette_ok'] and c['binary_alpha'],c
 summary[name]={'frames':N*2,'bottom_rows':sorted(set(c['bottom_row'] for c in checks)),'below_ground_pixels':0,'edge_contacts':0,'stray_components':0,'frame0_iou':{c['frame']:c['frame0_IoU'] for c in checks if c['frame0_IoU'] is not None},'raw_sha256':hashlib.sha256((ROOT/name/'sheet_raw.png').read_bytes()).hexdigest(),'raw_size':grid['raw_size']}
 for cell in grid['cells']:
  n,j=cell['view'],cell['frame'];fr=Image.open(ROOT/name/'frames'/f'{n}_f{j}.png')
  cell['final_opaque_box']=list(fr.getbbox());cell['lift']=LIFTS.get(j,0) if name=='bound' else 0
  cell['exact_approved_still']=j==0 or (name in ['bound','hex_dome'] and j==N-1)
  if cell['exact_approved_still']:cell['placement']=[16,30]
  cell['finishing_coordinates']='Native face/gem patches and local pose changes recorded in finishing scripts and logs.'
 grid.update(clean=not any(c['touches_cut'] for c in grid['cells']),final_canvas=[192,192],approved_offset=[16,30],ground_row=160,finishing=['finish.py','polish.py','gems.py','final_pose.py','seam_fill.py','verify.py'])
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
print('Frames',sum(v['frames'] for v in summary.values()),'palette',len(palette))
(ROOT/'verification.json').write_text(json.dumps({'animations':summary,'palette_opaque_colours':len(palette),'total_frames':50},indent=2)+'\n')
# Compact board for visual motion review, every frame at 2x native pixels.
for name,N in COUNTS.items():
 im=Image.new('RGB',(N*260,2*230+32),'#636A70');d=ImageDraw.Draw(im)
 for r,n in enumerate(NAMES):
  for c in range(N):
   f=Image.open(ROOT/name/'frames'/f'{n}_f{c}.png').crop((25,55,155,170)).resize((260,230),Image.Resampling.NEAREST)
   im.paste(f,(c*260,32+r*230),f);d.text((c*260+4,32+r*230),f'{n} {c}',fill='white')
 im.save(ROOT/name/'detail_board.png')
# Root board uses representative key poses, labelled with their frame IDs.
im=Image.new('RGB',(5*320,3*300),'#555B61');d=ImageDraw.Draw(im)
for r,(name,N) in enumerate(COUNTS.items()):
 ids={'bound':[0,3,4,6,8],'hex_dome':[0,2,3,5,7],'death':[0,2,4,6,7]}[name]
 for c,j in enumerate(ids):
  f=Image.open(ROOT/name/'frames'/f'se_f{j}.png').crop((20,35,180,175)).resize((320,280),Image.Resampling.NEAREST);im.paste(f,(c*320,r*300+20),f);d.text((c*320+5,r*300+5),f'{name} se F{j}',fill='white')
im.save(ROOT/'review.png')
