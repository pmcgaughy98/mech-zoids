"""Five-view audit, adapted from cam30; reads only approved views and this job."""
from pathlib import Path
import json,sys,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
sys.dont_write_bytecode=True
sys.path.insert(0,'tools/art')
import sprite_director as sd
P=Path(__file__).resolve().parent; T=P.parent; V=T/'views_cam35'
V.mkdir(exist_ok=True)
DS=['s','se','e','ne','n']; GUIDE={'s':(69,64),'se':(64,67),'e':(59,70),'ne':(64,67),'n':(69,64)}
for d in DS: shutil.copyfile(P/'slices'/f'{d}.png',V/f'{d}.png')
roles={tuple(bytes.fromhex(x['hex'].lstrip('#'))):x['role'] for x in json.loads((T/'palette.json').read_text())}
metrics={}; shape=[]; depth=[]; palette=[]; sizes=[]; heights=[]; edges={}; allpixels=[]
for label,base in [('approved',T/'views'),('new',V)]:
 for d in DS:
  a=np.array(Image.open(base/f'{d}.png').convert('RGBA')); m=a[...,3]>0
  yy,xx=np.where(m); pix=a[m,:3]; cs,counts=np.unique(pix,axis=0,return_counts=True)
  w,h=int(np.ptp(xx)+1),int(np.ptp(yy)+1); area=int(m.sum())
  border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
  shares={r:sum(int(n) for c,n in zip(cs,counts) if roles.get(tuple(c))==r)/area for r in ['team','glow','steel','charcoal','accent']}
  glow=np.zeros(m.shape,bool)
  for c,r in roles.items():
   if r=='glow': glow|=m & np.all(a[...,:3]==c,axis=2)
  lab,n=ndimage.label(glow,np.ones((3,3),int)); lens=int(np.bincount(lab.ravel())[1:].max()) if n else 0
  item={'width':w,'height':h,'area':area,'roles':shares,'glow_count':int(glow.sum()),'lens':lens,'border':border}
  metrics[label+'_'+d]=item
  sizes.append(f'{label} {d}: {w}x{h}, area {area}, border contact {border}')
  shape.append(f'{label} {d}: '+ '; '.join(f'{r} {v:.2%}' for r,v in shares.items())+f'; glow pixels {glow.sum()}; largest glow component (8-connected) {lens}')
  if label=='new':
   allpixels.append(pix); gw,gh=GUIDE[d]; item.update(height_ratio=h/gh,width_ratio=w/gw)
   heights.append(f'{d}: {w}x{h}; guide {gw}x{gh}; height/guide {h/gh:.5f}; width/guide {w/gw:.5f}; '+('MISS' if h/gh<.85 or h/gh>1.08 else 'PASS'))
   invalid=['#'+bytes(c).hex() for c in cs if tuple(c) not in roles]
   palette.append(f'{d}: {len(cs)} opaque colours; outside fixed palette: {invalid or "NONE"}; alpha {np.unique(a[...,3]).tolist()}')
   lum=pix@[.2126,.7152,.0722]; lo,hi=np.percentile(lum,[5,95]); k=counts.argmax()
   item.update(p05=float(lo),p95=float(hi),dominant_share=float(counts[k]/area),lone=float(sd.lone_share(a.astype(np.int16))))
   depth.append(f'{d}: p05 {lo:.2f}; p95 {hi:.2f}; range {hi-lo:.2f}; most common #{bytes(cs[k]).hex()} {counts[k]/area:.2%}')
   edge=m & ~ndimage.binary_erosion(m); ec,ct=np.unique(a[edge,:3],axis=0,return_counts=True)
   edges[d]={'#'+bytes(c).hex():{'count':int(n),'share':float(n/edge.sum())} for c,n in zip(ec,ct)}
spread=max(metrics['new_'+d]['height_ratio'] for d in DS)-min(metrics['new_'+d]['height_ratio'] for d in DS)
metrics['height_spread']=spread
heights.append(f'Height ratio spread {spread:.5f}: '+('MISS' if spread>.08 else 'PASS')+'; heights measured, never normalized.')
for d,approved in [('s',153),('se',137)]:
 expected=approved*.83; actual=metrics['new_'+d]['lens']; verdict='MISS' if actual<.85*expected else 'PASS'
 shape.append(f'LENS {d}: approved measured {metrics["approved_"+d]["lens"]}; specified approved {approved}; expected {expected:.2f}; actual {actual}; actual/expected {actual/expected:.5f}; {verdict}')
for d in ['ne','n']: shape.append(f'Rear glow {d}: {metrics["new_"+d]["glow_count"]}; '+('PASS' if metrics['new_'+d]['glow_count']==0 else 'MISS'))
for name,lines in [('sizes',sizes),('heights',heights),('shape',shape),('depth',depth),('palette-check',palette)]: (P/(name+'.txt')).write_text('\n'.join(lines)+'\n')
(P/'edge-audit.json').write_text(json.dumps(edges,indent=2))
cs,counts=np.unique(np.concatenate(allpixels),axis=0,return_counts=True)
metrics['colours']=len(cs); metrics['top_five_share']=float(np.sort(counts)[-5:].sum()/counts.sum())
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
review=Image.new('RGB',(96*5,110*2),(128,128,128)); draw=ImageDraw.Draw(review)
for row,(label,base) in enumerate([('approved',T/'views'),('new',V)]):
 for col,d in enumerate(DS):
  im=Image.open(base/f'{d}.png').convert('RGBA');review.paste(im,(96*col,110*row+14),im);draw.text((96*col+5,110*row+2),label+' '+d,fill=(245,245,245))
review.resize((review.width*4,review.height*4),Image.Resampling.NEAREST).save(P/'review.png')
for script in ['view_check','sheet_judge']:
 result=subprocess.run([sys.executable,'-B',f'tools/art/{script}.py',str(P/'slices')],capture_output=True,text=True)
 (P/(script+'.txt')).write_text(result.stdout+result.stderr)
 print(script,result.returncode,result.stdout,result.stderr)
print('\n'.join(heights));print('\n'.join(shape[-4:]));print('\n'.join(depth))
print('accent new/approved',[(d,metrics['new_'+d]['roles']['accent'],metrics['approved_'+d]['roles']['accent']) for d in DS])
print('lone',[(d,metrics['new_'+d]['lone']) for d in DS]);print('top five',metrics['top_five_share'])
