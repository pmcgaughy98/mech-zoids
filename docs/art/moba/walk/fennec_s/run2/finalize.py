import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image
import frontback as m
import repair
R=m.R;b=m.b;load=m.load
base=['--targets',str(R/'targets.json'),'--frames',str(R/'walk/frames'),'--views','e','ne','s','n','--still-dir',str(R/'stills')]
tool=R.parents[2]/'tools/walk_tools.py'
# R.parents[2] is walk, so use walk/tools.
tool=R.parent.parent/'tools/walk_tools.py'
outputs={}
for name,extra in [('footlock',['--out',str(R/'footlock.json')]),('seams',['--body','e0c8ff','a46bff','6a3cc8','2e1a6e'])]:
 q=subprocess.run([sys.executable,'-B',str(tool),name]+base+extra,capture_output=True,text=True)
 assert q.returncode==0,q.stderr
 outputs[name]=q.stdout;(R/f'{name}_tool.txt').write_text(q.stdout+q.stderr)
 print(q.stdout)
 with (R/'checks.txt').open('a') as out:out.write('\nSUPPLIED_TOOL '+name+'\n'+q.stdout+q.stderr)
audit=json.loads((R/'verification.json').read_text());assert audit['failures']==[]
slits=json.loads((R/'seams_review.json').read_text());hashes={};extra=[]
for v in ['ne','e','s','n']:
 st=load(R/f'stills/{v}.png');orig=load(R.parent/f'views_stand35/{v}.png');can=np.zeros((192,192,4),np.uint8);can[20:180,16:176]=orig;assert np.array_equal(st,can)
 gif=Image.open(R/f'{v}_preview.gif');assert gif.n_frames==8 and gif.info['loop']==0
 for f in range(8):
  gif.seek(f);assert gif.info['duration']==100
  p=R/f'walk/frames/{v}_f{f}.png';hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 # Every source sole is supported by exact six-row colour stamps; audit measures
 # source layers only when occlusion makes the composite stamp incomplete.
 extra.append(v+' occluded stamps: '+str({n:[q['frame'] for q in d['frames'] if 'layer' in q['measured_from']] for n,d in audit[v]['feet'].items()}))
# Tail source is exactly the still's native extraction; check visible n tail whole.
for f in range(8):
 a=load(R/f'walk/frames/n_f{f}.png');t=b.shift(load(R/'source/n_tail.png'),0,int(f in [1,5]));mask=t[:,:,3]>0
 assert np.array_equal(a[mask],t[mask]),('n tail',f)
 for n in ['LH','RH']:
  src=load(R/f'source/n_{n}_lower.png');assert not repair.gold(src).any()
extra+=['n: whole translated tail paint matches 100% in every composite; all hind-leg source parts contain zero gold.', 's/n rigid knee and lower blocks retain source dimensions; translated, never rotated/resampled.','e knee steel/native non-gold paint matches 100%; five mis-extracted gold shadow pixels per RF/LF source knee are intentionally recoloured deepest violet.','Whole articulated leg-length tolerance was not independently established; only rigid native-block lengths were pixel-checked.']
# Independent repair gates.
light=[];gold=[]
for f in range(8):
 a=load(R/f'walk/frames/ne_f{f}.png');mask=np.logical_or.reduce([np.all(a[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['e0c8ff','a46bff']]);light.append(int(mask[128:150,58:92].sum()))
 a=load(R/f'walk/frames/e_f{f}.png');sizes=[len(c) for c in b.pieces(repair.gold(a))];gold.append(sizes)
assert min(light)>=63 and all(len(s)==4 and min(s)>4 for s in gold)
extra+=['REPAIR_NE_LIGHT_COUNTS '+str(light),'REPAIR_E_GOLD_COMPONENT_SIZES '+str(gold)]
watch=(R/'token-watch-run2.txt').read_text().splitlines();snapshot=watch[-1] if watch else 'unavailable'
lines=[
'fennec-trot35-run2: completed Part 1 ne, Part 2 e, Part 3 s, Part 4 n; 32 raw 192x192 frames.',
'Tokens: watcher snapshot '+snapshot+'; final total unavailable.',
'Reused run1 native-part rig/stamp method and gorilla run2 front/back layering; no image generation or resampling.',
'ne repair: far LH/LF -> whole native tail -> body -> near RH/RF; original foot layers/deltas retained.',
'ne light pixels x58-91/y128-149 f0-7: '+str(light)+'; >=63 PASS.',
'e repair: pinned plate bands, highlight and seam behind RF; removed chest-shadow gold from moving RF/LF knees.',
'e gold pieces: [4,4,4,4,4,4,4,4], minimum size '+str(min(min(s) for s in gold))+'px (>4); PASS. Still has 4.',
's/n: front feet near in s, hind feet near in n; real vertical depth travel; RF+LH swing f5-7, LF+RH f1-3.',
'All planted f0/f4; body dips f0/f4; whole native tail dips f1/f5; lifts exact 2/3/2.',
'Deciding native-stamp lock spreads x/y: ne all 0.950/0.840; e all 0.500/0.000; s/n all 0.000/0.032px; PASS.',
'Max target errors: ne 0.475px; e 0.500px; s/n 0.020px. Occluded contacts measured on saved leg layers (checks.txt).',
'Silhouette footlock: SOME FEET NEED A LOOK (e RF, ne LH/RF merge neighbouring soles); s/n all pass.',
'Seams tool remaining flags f0-7 (open inter-leg/ankle or tail-to-leg gaps, retained after visual review):',
]
for v in ['e','ne','s','n']:lines.append('  '+v+' '+str([len(q) for q in slits[v]]))
lines += [
'No enclosed holes or interior pinned-body slits remain; residual tool flags are not filled between legs.',
'Upper paint/canvas difference above attachments: every frame 0% in all four views, after body/tail dip.',
'Native knee steel and lower blocks preserved on layers; rigid-part length change 0px. Full articulated length not independently established.',
]
for v in ['e','ne','s','n']:lines.append('Lowest '+v+' f0-7: '+str([q['lowest_row'] for q in audit[v]['structure']]))
lines += [
'All frames: binary alpha, native palette only, one component, no holes/strays/edge contacts; s/n within allowed row164.',
'By eye: ne tail whole/clean, cream tip intact, far LH below it; e chest whole with clean leg overlap, no loose gold.',
'By eye: s/n read as this fennec trotting toward/away in diagonal pairs; native knees/feet, legs separate; tail straight/clean.',
'n tail matches its complete translated native source 100% in every frame; no gold in hind-leg sources.',
'4x selout board, 100ms looping GIFs, 5x repairs/legs, s/n footprints and full checks supplied. Writes only run2; no commit.'
]
# Keep report under 30 lines by consolidating lowest rows.
lines[20:24]=['Lowest f0-7: e '+str([q['lowest_row'] for q in audit['e']['structure']])+'; ne '+str([q['lowest_row'] for q in audit['ne']['structure']]),'Lowest f0-7: s '+str([q['lowest_row'] for q in audit['s']['structure']])+'; n '+str([q['lowest_row'] for q in audit['n']['structure']])]
assert len(lines)<30,len(lines)
(R/'REPORT.txt').write_text('\n'.join(lines)+'\n');(R/'frame_hashes.json').write_text(json.dumps(hashes,indent=2))
with (R/'checks.txt').open('a') as out:out.write('\nADDITIONAL_AUDIT\n'+'\n'.join(extra)+'\nFINAL REVIEW\n'+'\n'.join(lines)+'\n')
print('Report lines',len(lines),'all required GIF timing, still placement, native-stamp and repair gates pass.')
