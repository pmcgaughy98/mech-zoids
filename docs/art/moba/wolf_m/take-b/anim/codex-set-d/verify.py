"""Set B verification adapted to two diagonal views; every check reads final PNGs."""
from finish import *
import re
allchecks={};support={};palcount=np.zeros(12,int)
for name,ts in TIMES.items():
 checks=finalize(name);allchecks[name]=checks
 grid=json.loads((R/name/'grid.json').read_text())
 for c in checks:
  p=R/name/'frames'/f"{c['frame']}.png";a=np.array(Image.open(p));m=a[:,:,3]>0
  assert a.shape==(192,192,4) and c['bottom_row']==160 and c['palette_ok'] and c['binary_alpha'] and c['below160']==0 and not c['edge'] and c['components']==1,c
  if c['exact_still']:assert c['file_byte_identical'] and c['silhouette_IoU']==c['colour_IoU']==1
  else:assert c['holes']==0,c
  for j,col in enumerate(PAL):palcount[j]+=(np.all(a[:,:,:3]==col,2)&m).sum()
  v,fi=c['frame'].split('_f');entry=next(e for e in grid['cells'] if e['view']==v and e['frame']==int(fi))
  entry.update(final_path=str(p.relative_to(R/name)),final_bbox=c['bbox'],final_canvas=[192,192],ground_row=160,final_canvas_offset=[0,0],final_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
  c['overall_proportion_gate_pass']=False
 grid.update(preview_ms=ts,finishing='Whole generated drawings and direct native pixel ink. No approved parts pasted; see ../polish.py and ../pixel_edits.json.',empty_gutter_cuts=not any(c['touches_cut'] for c in grid['cells']))
 assert grid['empty_gutter_cuts'],grid
 (R/name/'grid.json').write_text(json.dumps(grid,indent=2))
 for v in V:
  gif=Image.open(R/name/f'preview_{v}.gif');dur=[]
  for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info['duration']);gif.convert('RGB').load()
  assert gif.n_frames==len(ts) and dur==ts
 # Verify f0... column sentences were not changed when adapting layout.
 old=(R.parent/'codex-set-b/prompts'/f'{name}.txt').read_text()
 new=(R/'prompts'/f'{name}.txt').read_text()
 for i in range(len(ts)):
  sentence=re.search(rf'\bf{i} .*?\.',old).group(0)
  assert sentence in new,(name,sentence)
 (R/name/'checks.txt').write_text('Structural checks PASS. Exact stills preserve source holes (SE9, NE11). Strict 2px part gate NOT CERTIFIED; see ../proportions.json.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')

# Report both projected hind-paw contacts, including the exact reference.
for v,zones in {'se':[(65,82),(85,96)],'ne':[(70,82),(82,105)]}.items():
 support[v]={}
 for i in range(-1,6):
  a=np.array(Image.open(REF[v] if i<0 else R/'hamstring/frames'/f'{v}_f{i}.png'));contacts=[]
  for lo,hi in zones:
   yy,xx=np.where((a[148:161,lo:hi,3]>0));bot=int(yy.max()+148);xx=np.where(a[bot,lo:hi,3]>0)[0]+lo
   contacts.append(dict(bottom=bot,sole_x=xx.tolist(),sole_centre=float(xx.mean())))
  support[v]['reference' if i<0 else f'f{i}']=contacts

for v in V:
 a=np.array(Image.open(R/'death/frames'/f'{v}_f5.png'));b=np.array(Image.open(R/'death/frames'/f'{v}_f6.png'))
 cyan=np.all(a[:,:,:3]==PAL[8],2)&(a[:,:,3]>0);changed=np.any(a!=b,2)
 assert np.array_equal(changed,cyan) and np.array_equal(a[:,:,3],b[:,:,3])
 assert not (np.all(b[:,:,:3]==PAL[8],2)&(b[:,:,3]>0)).any()
 # Away-facing approved view has no visible eye: f5/f6 properly match exactly.
 if v=='ne':assert not changed.any()

# Check reference enlargement's original opaque texels against fixed/.
for v in V:
 a=np.array(Image.open(REF[v]).convert('RGBA'));bb=Image.fromarray(a).getbbox()
 ref=Image.open(R/'refs'/f'{v}_6x.png').convert('RGB')
 crop=Image.fromarray(a).crop(bb);m=np.array(crop)[:,:,3]>0
 # Enlargements include an 8px native magenta margin.
 b=np.array(ref)[::6,::6]
 found=False
 for y in range(max(1,b.shape[0]-crop.height+1)):
  for x in range(max(1,b.shape[1]-crop.width+1)):
   if np.array_equal(b[y:y+crop.height,x:x+crop.width][m],np.array(crop)[:,:,:3][m]):found=True
 assert found,(v,'reference enlargement mismatch')
(R/'verification.json').write_text(json.dumps(allchecks,indent=2))
(R/'support_checks.json').write_text(json.dumps(support,indent=2))
(R/'palette.txt').write_text('\n'.join(f'#{bytes(c).hex()} opaque_pixels={int(n)}' for c,n in zip(PAL,palcount)))
print('PASS: 38 PNGs; 10 byte-identical still endpoints IoU1; 28 clean posed frames; 6 GIFs exact timing; empty cuts; prompt column text unchanged; f6 eye-only. Proportion gate remains separate.')
print('Hamstring contacts:',json.dumps(support))
