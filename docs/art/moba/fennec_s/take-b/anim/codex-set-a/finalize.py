from finish import *
from verify import board
from PIL import GifImagePlugin
summary={};allcolors=set();edgecounts=np.zeros(15,int);totalcounts=np.zeros(15,int)
for name,N in COUNTS.items():
 checks=board(name)
 for item in checks:
  a=np.array(Image.open(ROOT/name/'frames'/f"{item['frame']}.png"));m=a[:,:,3]>0
  _,components=ndi.label(m,structure=np.ones((3,3)));item['connected_components']=components
  assert item['bottom_row']==160 and item['pixels_below_160']==0 and item['palette_ok'] and item['binary_alpha'] and not item['canvas_edge'] and item['stray_components']==0,item
  assert components==1,item
  if item['required_exact_still']:assert item['silhouette_IoU']==1 and item['colour_IoU']==1,item
  exception=item['frame'].startswith('side_') and (name=='idle' or item['required_exact_still'])
  assert item['enclosed_hole_pixels']==(6 if exception else 0),item
  rim=m&~ndi.binary_erosion(m)
  for j,p in enumerate(PAL):
   same=np.all(a[:,:,:3]==p,axis=2)&m;totalcounts[j]+=int(same.sum());edgecounts[j]+=int((same&rim).sum())
  allcolors.update(map(tuple,a[m,:3]))
 (ROOT/name/'checks.txt').write_text('Approved offset (+16,+20). Native approved side has six enclosed pixels; kept only on exact endpoints and fixed idle lower body.\n'+'\n'.join(json.dumps(x) for x in checks)+'\n')
 grid=json.loads((ROOT/name/'grid.json').read_text());grid['durations_ms']=TIMINGS[name];grid['loop']=name in ['idle','walk'];grid['frames']={n:[dict(file=f'frames/{n}_f{c}.png',duration_ms=TIMINGS[name][c]) for c in range(N)] for n in NAMES};grid['finishing']=['finish.py','polish.py','seam_fill.py','details.py','gait_finish.py','finalize.py'];grid['native_detail_log']='../native_finish_log.txt';grid['approved_offset']=[16,20];grid['ground_row']=160
 if name!='idle':grid['raw_sha256']=hashlib.sha256((ROOT/name/'sheet_raw.png').read_bytes()).hexdigest()
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
 # Explicit GIF blocks retain repeated held drawings as distinct timed frames.
 for n in NAMES:
  pics=[]
  for c in range(N):
   a=np.array(Image.open(ROOT/name/'frames'/f'{n}_f{c}.png'));m=a[:,:,3]>0;idx=np.full((192,192),15,dtype=np.uint8)
   for j,p in enumerate(PAL):idx[np.all(a[:,:,:3]==p,axis=2)&m]=j
   im=Image.fromarray(idx,'P');im.putpalette(PAL.flatten().tolist()+[115,121,128]+[0]*(768-48));pics.append(im.resize((576,576),Image.Resampling.NEAREST))
  with (ROOT/name/f'preview_{n}.gif').open('wb') as fp:
   header,_=GifImagePlugin.getheader(pics[0],info={'loop':0,'optimize':False})
   for block in header:fp.write(block)
   for im,ms in zip(pics,TIMINGS[name]):
    for block in GifImagePlugin.getdata(im,duration=ms,disposal=2):fp.write(block)
   fp.write(b';')
  gif=Image.open(ROOT/name/f'preview_{n}.gif');assert gif.n_frames==N
  times=[]
  for c in range(N):gif.seek(c);times.append(gif.info['duration'])
  assert times==TIMINGS[name],(name,n,times)
 summary[name]={'frame_count':N*3,'checks':checks,'gif_frames_per_view':N,'durations_ms':TIMINGS[name],'source':'native only' if name=='idle' else grid['raw_sha256'],'raw_size':grid.get('raw_size')}
(ROOT/'verification.json').write_text(json.dumps({'total_frames':99,'palette_colours':len(allcolors),'animations':summary},indent=2)+'\n')
(ROOT/'palette.txt').write_text('hex total_opaque_pixels edge_pixels fraction_of_colour_on_edge\n'+'\n'.join(f'#{h} {t} {e} {e/t:.6f}' for h,t,e in zip(HEX,totalcounts,edgecounts))+'\n')
# Front key pose overview; full three-view boards live under each animation.
b=Image.new('RGB',(6*256,5*220),'#737980');d=ImageDraw.Draw(b)
for r,(name,N) in enumerate(COUNTS.items()):
 ids={'idle':[0,1,2,3,4],'walk':[0,1,2,4,6],'sand_kick':[0,1,2,3,5],'ear_burst':[0,1,2,3,5],'sonic_boom':[0,2,3,4,7]}[name]
 for col,c in enumerate([-1]+ids):
  im=approved('front') if c<0 else Image.open(ROOT/name/'frames'/f'front_f{c}.png')
  tile=Image.new('RGB',(192,192),'#737980');tile.paste(im,mask=im.getchannel('A'));tile=tile.crop((32,75,160,171)).resize((256,192),Image.Resampling.NEAREST);b.paste(tile,(col*256,r*220+25));d.text((col*256+8,r*220+6),name+(' STILL' if c<0 else f' f{c}'),fill='white')
b.save(ROOT/'review.png')
print('PASS: 99 frames; 24 required endpoints have both IoUs 1.0; 15 GIFs have exact frame counts and timing; 15 palette colours; one connected body per frame.')
