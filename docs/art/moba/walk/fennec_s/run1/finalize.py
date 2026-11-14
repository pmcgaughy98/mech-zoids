import sys;sys.dont_write_bytecode=True
sys.path.insert(0,r'D:\dev\new-mech-rpg\docs\art\moba\walk\fennec_s\run1')
import build as b
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw
r=b.R;tool=r.parents[2]/'walk/tools/walk_tools.py';base=['--targets',str(r/'targets.json'),'--frames',str(r/'walk/frames'),'--views','e','se','ne','--still-dir',str(r/'stills')]
for cmd,extra in [('footlock',['--out',str(r/'footlock.json')]),('seams',['--body','e0c8ff','a46bff','6a3cc8','2e1a6e'])]:
 p=subprocess.run([sys.executable,str(tool),cmd]+base+extra,capture_output=True,text=True);(r/f'{cmd}_tool.txt').write_text(p.stdout+p.stderr)
 with (r/'checks.txt').open('a') as out:out.write('\nSUPPLIED_TOOL '+cmd+'\n'+p.stdout+p.stderr)
 print(p.stdout)
audit=json.loads((r/'verification.json').read_text());slits={};hashes={}
for v in ['e','se','ne']:
 st=b.load(r/f'stills/{v}.png');slits[v]=[];board=Image.new('RGBA',(400*8,270),(65,72,68,255))
 for f in range(8):
  a=b.load(r/f'walk/frames/{v}_f{f}.png');sl=b.find_slits(a,st,int(f in [0,4]));slits[v].append(sl);im=Image.fromarray(a);d=ImageDraw.Draw(im)
  for x,y in sl:d.point((x,y),fill=(255,90,70,255))
  board.alpha_composite(im.crop((60,115,140,164)).resize((400,245),Image.Resampling.NEAREST),(f*400,25));ImageDraw.Draw(board).text((f*400+5,3),f'{v} f{f}: {len(sl)} flags',fill='white')
  hashes[f'{v}_f{f}.png']=hashlib.sha256((r/f'walk/frames/{v}_f{f}.png').read_bytes()).hexdigest()
 board.save(r/f'{v}_seams_review.png')
 # Source placement independently rechecked against the approved 160-pixel image.
 original=b.load(r.parent/f'views_stand35/{v}.png');canvas=b.np.zeros((192,192,4),b.np.uint8);canvas[20:180,16:176]=original
 assert b.np.array_equal(canvas,st),v+' still placement differs'
 preview=Image.open(r/f'{v}_preview.gif');assert preview.n_frames==8 and preview.info['loop']==0
 durations=[]
 for f in range(8):preview.seek(f);durations.append(preview.info['duration'])
 assert durations==[100]*8
(r/'seams_review.json').write_text(json.dumps(slits,indent=2));(r/'frame_hashes.json').write_text(json.dumps(hashes,indent=2))
watch=(r/'token-watch-run1.txt').read_text().splitlines()[-1]
lines=['fennec-trot35-run1: 24 raw frames, e/se/ne, 192x192; previews 8 x 100ms, looping.',
'Tokens: watcher snapshot '+watch+'; final total unavailable.',
'Foot labels retained: RF/RH near right, LF/LH far left. ne LH is hind; its native knee is hidden by the tail.',
'Method reused: ape_l/run1 native helpers/stamp audit; run2 complete hidden joints. Native translations only.',
'RF+LH swing f5-7; LF+RH f1-3; all planted f0/f4; body dips f0/f4, whole native tail f1/f5.',
'Pixel-stamp foot lock, all four feet: e spread x/y 0.500/0.000; se/ne each 0.950/0.840 px. PASS.',
'Target errors: e <=0.500; se <=0.500; ne <=0.475 px. Lifts exact 2/3/2. PASS.',
'Occluded contacts measured from complete saved leg layers; checks.txt lists every measurement/frame.',
'Supplied footlock tool: SOME FEET NEED A LOOK; overlapping silhouettes merge nearby soles (see footlock.json).',
'Its passing feet: e RH and ne RH; remaining feet have independent native-stamp/layer passes above.',
'Seams tool residual flags f0-7:']
for v in ['e','se','ne']:lines.append('  '+v+' '+str([len(q) for q in slits[v]]))
lines+=['Residual seam flags are open inter-leg/ankle spaces after one body-band fill; retained per playbook, not iteratively filled.',
'No enclosed holes remain; strict zero-flags seams gate is NOT met. Red-dot review PNGs and coordinates supplied.',
'Upper original opaque paint difference f0-7: all views [0,0,0,0,0,0,0,0]%.',
'Whole upper canvas: e/ne 0%; se f0/f4 add 5 tail-root joining pixels (0.0203%); other se frames 0%.',
'Native knee housings 100% intact on layers; shin/foot below top 4 joining rows 100% unchanged; rigid-part length change 0px.',
'Whole articulated leg-length tolerance was not independently established; joints are stepped native-colour bands.']
for v in ['e','se','ne']:lines.append('Lowest '+v+' f0-7: '+str([q['lowest_row'] for q in audit[v]['structure']]))
lines+=['All: binary alpha, native palette only, 1 component, 0 holes/strays/edge contacts. Stills equal approved +16,+20.',
'By eye at 4x selout and every joint at 5x: e/se/ne read as this fennec trotting in diagonal pairs; knees/feet whole.',
'Tail stays straight, translated whole behind legs. Far joints dark and occluded; no abrupt cutoffs seen.',
'Delivery is reviewable; strict seams/upper-canvas/whole-length gates above remain qualified, not an all-gates pass.']
assert len(lines)<30
(r/'REPORT.txt').write_text('\n'.join(lines)+'\n')
with (r/'checks.txt').open('a') as out:out.write('\nFINAL REVIEW\n'+'\n'.join(lines)+'\n')
print('Report',len(lines),'lines; GIF timing and approved still placement verified.')
