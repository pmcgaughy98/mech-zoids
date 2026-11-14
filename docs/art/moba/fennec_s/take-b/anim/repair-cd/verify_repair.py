from repair import *
from PIL import ImageSequence
checks=json.loads((OUT/'checks.json').read_text());assert all(r['palette'] and r['alpha'] and not r['edge'] and not r['holes'] and r['bottom']==(145 if r['move']=='pop_out' and r['frame']==2 else 160) and (not r['locked'] or r['still_equal']) and (len(r['components'])==1 or r['move']=='pop_out' and r['frame']==0) for r in checks)
outline=[]
for m in MOVES:
 for v in ['se','ne']:
  for p in files(m,v):
   mask=np.array(outlined(Image.open(p)))[:,:,3]>0;ys,xs=np.where(ndi.binary_fill_holes(mask)&~mask)
   if len(xs):outline.append(dict(move=m,frame=p.stem,holes=list(zip(xs.tolist(),ys.tolist()))))
(OUT/'outline-checks.json').write_text(json.dumps(outline,indent=2));print('outline holes:',outline)
results=[]
for m in MOVES:
 g=json.loads((directory(m)/'grid.json').read_text())
 for v in ['se','ne']:
  gif=Image.open(directory(m)/f'preview_{v}.gif');intervals=[];t=0
  for f in ImageSequence.Iterator(gif):
   d=f.info.get('duration',0);intervals.append((t,t+d,f.convert('RGB').copy()));t+=d
  assert t==sum(g['durations_ms'])
  start=0
  for p,d in zip(files(m,v),g['durations_ms']):
   im=Image.open(p).convert('RGBA');bg=Image.new('RGBA',(192,192),'#454953');bg.alpha_composite(im);expected=np.array(bg.resize(gif.size,Image.Resampling.NEAREST).convert('RGB'))
   assert all(np.array_equal(expected,np.array(r[2])) for r in intervals if r[0]<start+d and r[1]>start)
   start+=d
  results.append(dict(move=m,view=v,total_ms=t,pixel_exact=True,durations=g['durations_ms']))
(OUT/'gif-checks.json').write_text(json.dumps(results,indent=2));print('102 frame checks, 22 still locks, 16 GIF timeline/pixel checks: PASS')
