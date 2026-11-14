from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage
P=Path(__file__).resolve().parent
names=['ne','n','nw','e',None,'w','se','s','sw']
sizes={}; depths={}; edges={}; pixels=[]; border={}
for d in [x for x in names if x]:
 im=Image.open(P/'views'/f'{d}.png').convert('RGBA'); a=np.array(im); m=a[...,3]>0
 yy,xx=np.where(m); sizes[d]=[int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1),int(m.sum())]
 border[d]=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
 pix=a[m,:3]; pixels.append(pix); cs,counts=np.unique(pix,axis=0,return_counts=True)
 lum=pix@[.2126,.7152,.0722]; k=counts.argmax()
 depths[d]={'p05':float(np.percentile(lum,5)),'p95':float(np.percentile(lum,95)),'dominant_colour':'#'+bytes(cs[k]).hex(),'dominant_share':float(counts[k]/len(pix)),'height':sizes[d][1]}
 edge=m & ~ndimage.binary_erosion(m); ec,ct=np.unique(a[edge,:3],axis=0,return_counts=True)
 edges[d]={'edge_pixels':int(edge.sum()),'colours':{'#'+bytes(c).hex():{'count':int(n),'share':float(n/edge.sum()),'share_of_colour_on_edge':float(n/np.all(pix==c,axis=1).sum())} for c,n in zip(ec,ct)}}
# Both per-view and combined audits include every palette colour, including zero edge counts.
allpix=np.concatenate(pixels); cs,counts=np.unique(allpix,axis=0,return_counts=True)
combined={}
for c,n in zip(cs,counts):
 key='#'+bytes(c).hex(); count=sum(v['colours'].get(key,{}).get('count',0) for v in edges.values())
 combined[key]={'count':count,'share':count/sum(v['edge_pixels'] for v in edges.values()),'body_count':int(n),'share_of_colour_on_edge':count/int(n)}
 for v in edges.values(): v['colours'].setdefault(key,{'count':0,'share':0,'share_of_colour_on_edge':0})
(P/'edge-audit.json').write_text(json.dumps({'edge_definition':'opaque pixel adjacent to transparency in four-neighbourhood','combined':combined,'views':edges},indent=2))
(P/'sizes.txt').write_text('\n'.join(f'{d}: {sizes[d][0]}x{sizes[d][1]}, opaque area {sizes[d][2]}' for d in ['s','se','e','ne','n'])+'\nBorder contact: '+str(border))
(P/'depth.txt').write_text('\n'.join(f"{d}: p05 {depths[d]['p05']:.2f}; p95 {depths[d]['p95']:.2f}; range {depths[d]['p95']-depths[d]['p05']:.2f}; most common {depths[d]['dominant_colour']} {depths[d]['dominant_share']:.2%}; height {depths[d]['height']}px" for d in ['e','se','s','n']))
(P/'metrics.json').write_text(json.dumps({'sizes':sizes,'depth':depths,'border_contact':border,'colours':len(cs),'top_five_share':float(np.sort(counts)[-5:].sum()/counts.sum())},indent=2))
for game,filename in [(False,'review.png'),(True,'review-game-size.png')]:
 tile_w, tile_h = (max(s[0] for s in sizes.values())+12,max(s[1] for s in sizes.values())+10) if not game else (52,36)
 sheet=Image.new('RGB',(tile_w*3,tile_h*3),(128,128,128))
 for k,d in enumerate(names):
  if d is None: continue
  im=Image.open(P/'views'/f'{d}.png').convert('RGBA')
  im=im.crop(im.getbbox())
  if game:
   im=im.crop(im.getbbox()); im=im.resize((round(im.width*26/im.height),26),Image.Resampling.NEAREST)
  sheet.paste(im,((k%3)*tile_w+(tile_w-im.width)//2,(k//3)*tile_h+tile_h-4-im.height),im)
 sheet.resize((sheet.width*4,sheet.height*4),Image.Resampling.NEAREST).save(P/filename)
print((P/'sizes.txt').read_text()); print((P/'depth.txt').read_text()); print('colours',len(cs),'top five',np.sort(counts)[-5:].sum()/counts.sum())






roles={c:r for r,cc in {'team':['9ad0ff','3a8cff','2258c8','14306e'],'glow':['5fd8ff','d0f4ff','f6fdff'],'steel':['e2e4ea','b8bcc6','8a8f9c','5c6170'],'charcoal':['3d3a44','211e27'],'accent':['141218']}.items() for c in cc}
(P/'palette.json').write_text(json.dumps([{'hex':'#'+bytes(c).hex(),'role':roles[bytes(c).hex()],'count':int(n)} for c,n in zip(cs,counts)],indent=2))
lines=[f"east height / south height: {sizes['e'][1]}/{sizes['s'][1]} = {sizes['e'][1]/sizes['s'][1]:.4f}", f"south width / height: {sizes['s'][0]}/{sizes['s'][1]} = {sizes['s'][0]/sizes['s'][1]:.4f}"]
for d in [x for x in names if x]:
 a=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA')); m=a[...,3]>0
 code=a[...,:3].astype(int)@np.array([65536,256,1]); team=np.isin(code,[int(c,16) for c,r in roles.items() if r=='team']) & m; glow=np.isin(code,[int(c,16) for c,r in roles.items() if r=='glow']) & m
 yy,xx=np.where(m)
 # Nozzle mouths occupy the bottom of the drone. Count upper glow as lens,
 # separately from the intentionally visible rear-facing nozzle glow.
 lens=glow & (np.indices(m.shape)[0] < yy.min()+.72*(yy.max()-yy.min()+1))
 lines.append(f"{d}: team {team.sum()/m.sum():.2%}; glow {glow.sum()/m.sum():.2%}; combined {(team|glow).sum()/m.sum():.2%}; lens pixels {lens.sum()}; bottom row {yy.max()}")
(P/'shape.txt').write_text('\n'.join(lines)+'\nLens definition: glow above bottom 28% of opaque height; lower thruster glow excluded, verified visually.\n')
print((P/'shape.txt').read_text())
