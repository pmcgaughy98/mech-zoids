"""Additional delivery checks: planted contact positions, native idle lower pixels, prompt identity."""
from finish import *
checks={}
# Actual rendered ground contacts stay fixed through each support interval.
supports={'se':[(range(0,4),(105,115)),(range(4,8),(89,105)),(range(4,8),(116,123))],
          'ne':[(range(0,4),(103,115)),(range(4,8),(115,121))]}
for n,groups in supports.items():
 for frames,(x0,x1) in groups:
  samples=[np.array(Image.open(ROOT/'walk'/'frames'/f'{n}_f{c}.png'))[160,x0:x1,3]>0 for c in frames]
  assert all(np.array_equal(s,samples[0]) for s in samples) and samples[0].any(),(n,list(frames),x0,x1)
  checks[f'{n}:{list(frames)}:{x0}-{x1}']={'ground_row':160,'actual_fixed_x':(np.where(samples[0])[0]+x0).tolist(),'passed':True}
for n in NAMES:
 ref=np.array(approved(n))
 for c in range(5):
  a=np.array(Image.open(ROOT/'idle'/'frames'/f'{n}_f{c}.png'));assert np.array_equal(a[140:],ref[140:]),(n,c,'idle fixed lower parts')
for name,N in COUNTS.items():
 for n in NAMES:
  gif=Image.open(ROOT/name/f'preview_{n}.gif');assert ('loop' in gif.info)==(name in ['idle','walk'])
  assert gif.n_frames==N
  times=[]
  for c in range(N):gif.seek(c);times.append(gif.info['duration'])
  assert times==TIMINGS[name]
 if name=='idle':continue
 source=(ROOT.parent/'codex-set-a'/'prompts'/f'{name}.txt').read_text()
 prompt=(ROOT/'prompts'/f'{name}.txt').read_text()
 marker='Exactly EIGHT columns' if N==8 else 'Exactly SIX columns'
 assert source[source.index(marker):]==prompt[prompt.index(marker):],name
 grid=json.loads((ROOT/name/'grid.json').read_text())
 for cell in grid['cells']:
  fr=Image.open(ROOT/name/'frames'/f"{cell['view']}_f{cell['frame']}.png")
  cell['final_opaque_box']=list(fr.getbbox());cell['final_path']=f"frames/{cell['view']}_f{cell['frame']}.png"
 grid['native_placements']='../native_finish_log.txt and ../detail_finish_log.txt; tails in ../final_pass_log.txt'
 grid['source_grid_clean']=not any(c.get('raw_nominal_overlap',False) for c in grid['cells'])
 grid['extraction_clean']=not any(c['touches_cut'] for c in grid['cells'])
 (ROOT/name/'grid.json').write_text(json.dumps(grid,indent=2)+'\n')
(ROOT/'support_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
# Full two-angle overview, preserving the approved still at the left of each row.
boards=[Image.open(ROOT/name/'review_small.png') for name in COUNTS]
w=max(b.width for b in boards);out=Image.new('RGB',(w,sum(b.height for b in boards)),(70,76,84));y=0
for b in boards:out.paste(b,(0,y));y+=b.height
out.save(ROOT/'review.png')
print('PASS: rendered planted contacts fixed, native idle lower body fixed, all GIF looping/count/timing correct, move columns unchanged, source cut contacts recorded per grid.')
