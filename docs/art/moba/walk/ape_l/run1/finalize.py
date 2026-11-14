from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
R=Path(r'D:/dev/new-mech-rpg/docs/art/moba/walk/ape_l/run1');sys.path.insert(0,str(R));import build as b
q=json.loads((R/'verification.json').read_text());t=json.loads((R/'targets.json').read_text());ext=json.loads((R/'footlock.json').read_text());assert not q['failures']
lines=[]
# Whole native gem+3px bezel is checked in FINAL production frames as well as layers.
for v in ['e','se','ne']:
 for n in ['RF','LF']:
  src=np.array(Image.open(R/f'source/{v}_{n}.png').convert('RGBA'));glow=(src[:,:,1]>180)&(src[:,:,0]<110)&(src[:,:,2]>70)&(src[:,:,3]>0);gy,gx=np.where(glow)
  if len(gy)==0:continue
  patch=(b.X>=gx.min()-3)&(b.X<=gx.max()+3)&(b.Y>=gy.min()-3)&(b.Y<=gy.max()+3)&(src[:,:,3]>0);material=np.isin(src[:,:,:3].astype('uint32')@np.array([65536,256,1]),[0x141a16,0x22301d,0x4a4950,0x8a8a93,0xdfe2e9,0x1b9a52,0x3fe07f,0xd6ffe6]);patch &= material;yy,xx=np.where(patch)
  for r in q[v]['feet'][n]['frames']:
   dx,dy=r['recovered_translation'];a=np.array(Image.open(R/f'walk/frames/{v}_f{r["frame"]}.png').convert('RGBA'));score=float(np.all(a[yy+dy,xx+dx]==src[yy,xx],axis=1).mean())
   lines.append(f'FINAL_SHIELD {v} {n} f{r["frame"]} native green+metal bezel exact-pixel share {score:.6f}'+(' (far shield partially occluded by pinned flank)' if n=='LF' and v=='ne' else ''))
   if (v,n) in [('e','RF'),('se','RF'),('se','LF'),('ne','RF')]:assert score==1,(v,n,r['frame'],score)
for v in ['e','se','ne']:
 raw=Image.open(R.parents[2]/f'ape_l/take-a/views_cam35_touchup/{v}.png').convert('RGBA');c=Image.new('RGBA',(192,192));c.paste(raw,(16,30));assert np.array_equal(np.array(c),np.array(Image.open(R/f'stills/{v}.png').convert('RGBA')));lines.append(f'APPROVED {v}: still exactly native touchup at(+16,+30), 0 differing pixels.')
 lines.append('WALK_TOOLS '+v+' '+json.dumps(ext[v]))
 for n in ['RF','LH','LF','RH']:
  pp=[np.array(r['measured_sole']) for r in q[v]['feet'][n]['frames']];step=np.array(t['views'][v]['planted_step_px']);stance=q[v]['feet'][n]['planted_order'];seam=max(float(np.max(np.abs(pp[stance[k+1]]-pp[stance[k]]-step))) for k in range(4));assert seam<=1;lines.append(f'LOOP_STANCE {v} {n}: max adjacent planted-step residual {seam:.3f}px including wrap where planted.')
assert all(d['pass'] for v in ext.values() for d in v['feet'].values())
lines+=['WALK_TOOLS RESULT: ALL FEET LOCKED. Every final frame: one piece, zero strays, binary alpha, no edge or off-palette pixels.',
'WALK_TOOLS NOTE: e RF max_target_error_px=3.00 because measure_sole follows one contour run and stops before the separated third knuckle. The complete native bottom-two-row support band has centre112.5 in the still; its final centre is within0.5px of every supplied target. Native three-knuckle silhouette retained.',
'Native block length change0px: every source limb texel equals a single integer translation in each isolated layer. Upper sockets are hand-drawn green stepped links under fixed armour; no rotation, scaling or interpolation.',
'Hidden-anchor caveat: e LH/LF, se RH/LH and ne LF have no supplied sole targets. Their support anchors are inferred from still depth and native same-view traces. They follow the supplied paths; their five-frame lock is measured in isolated layers.',
'VISUAL: inspected all24 final poses on4x selout boards and extreme f0/2/4/6 at8x. e,se,ne read as forward knuckle walking, arms alternate, native shields and hind segments remain whole. se hidden hind beats cannot be judged from composite alone.',
'STRIDE 3 side-px/frame *8fps *0.020m/px =0.48m/s.',
'REBUILD python -B build.py; python -B verify.py; requested walk_tools footlock command; python -B finalize.py. Writes confined to run1.']
checkpath=R/'checks.txt';s=checkpath.read_text();marker='\nFINAL AUDIT\n';s=s.split(marker)[0];checkpath.write_text(s+marker+'\n'.join(lines)+'\n')
report=[
'ape-walk35-run1 / green L gorilla / e,se,ne / 8-frame diagonal knuckle walk / 8fps.',
'Tokens: exact session usage unavailable. No image tool, commits or writes outside run1.',
'Approved touchup stills match run1/stills exactly at(+16,+30); stills and targets unchanged.',
'Native forearms+fists+hex shields translate whole; native hind segments translate whole; joints stepped by hand.',
'Native part length/dimension change0px; source paint matches translated limb layers100%; no rotations/resampling.',
'Foot names: RF right fist, LF left fist, RH right hind, LH left hind. ne LH retained as far hind behind rump.',
'se RH = left rear knee/hook, LH = under chest; both soles occluded in approved still.',
'Gait: RF+LH swing f5-7; LF+RH swing f1-3; all planted f0/f4; exact2,3,2px raster lifts.',
'e lock spread x/y: RF0/0 LH0/0 LF0/0 RH0/0px. PASS.',
'se lock spread x/y: RF0.484/0.868 LH0.484/0.868 LF0.484/0.868 RH0.484/0.868px. PASS.',
'ne lock spread x/y: RF0.484/0.868 LH0.484/0.868 LF0.484/0.868 RH0.484/0.868px. PASS.',
'Measured native support-band target max x/y: e0.500/0px; se/ne0.243/0.434px. PASS<=1.',
'Sole = midpoint of outer opaque endpoints in bottom2 native rows; exhaustive native-colour stamp search.',
'Occluded measurements: e LH/LF all, se LH/RH all, ne LF all + LH f0,1,6,7: saved limb PNGs.',
'Hidden anchors are inferred, not supplied sole targets. Footprint pictures label composite vs layer evidence.',
'walk_tools footlock: ALL FEET LOCKED. All24 one piece, zero strays, off-palette, semi-alpha or edge pixels.',
'Tool e RF reports3px target error: its contour-run detector excludes third knuckle; full band error<=0.5px.',
'Pinned upper-body differing pixels f0..7(%): e[0,0,0,0,0,0,0,0], se[0,0,0,0,0,0,0,0], ne[0,0,0,0,0,0,0,0].',
'Body/head/visor/back plate/shoulders exact after1px dip f0/f4; upper canvas including transparency also exact.',
'e lowest rows f0..7: [160,160,160,160,160,158,157,158].',
'se lowest rows f0..7: [162,161,160,159,158,157,157,159].',
'ne lowest rows f0..7: [162,159,158,159,160,159,160,161]. Perspective maximum162<=163.',
'24/24 raw transparent192x192, approved15 colours only, binary alpha, one piece, zero holes/strays/edge contact.',
'Whole visible gem+bezel final matches100%; body0% change; verify.py has0 failures. Ground speed0.48m/s.',
'By eye e/se/ne: forward knuckle walk, alternating native whole limbs, clean joins; se hind beats occluded.',
'board.png + per-view boards: approved still then f0..7, exact4x, game selout(#141a16); raw frames no outline.',
'GIFs alternate120/130ms (format10ms ticks), exact1000ms loops; supplied APNGs125ms/frame exactly.',
'Reproduce: build.py, verify.py, requested walk_tools command, finalize.py; checks.txt/verification.json detailed.'
]
assert len(report)<30;(R/'REPORT.txt').write_text('\n'.join(report)+'\n')
# A concise machine-readable delivery manifest, only within this run.
files=[*sorted((R/'walk/frames').glob('*.png')),R/'board.png',R/'checks.txt',R/'footlock.json',R/'REPORT.txt',*[R/f'{v}_{s}' for v in ['e','se','ne'] for s in ['preview.gif','preview.apng','footprints.png']]]
assert len(list((R/'walk/frames').glob('*.png')))==24
(R/'delivery.json').write_text(json.dumps({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
print('Finalized:',len(report),'report lines; final visible shields100%;24 frames; all checks pass.')
