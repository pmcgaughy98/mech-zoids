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
 tile_w, tile_h = (max(v[0] for v in sizes.values())+12,max(v[1] for v in sizes.values())+10) if not game else (max(round(v[0]*40/v[1]) for v in sizes.values())+12,48)
 sheet=Image.new('RGB',(tile_w*3,tile_h*3),(128,128,128))
 for k,d in enumerate(names):
  if d is None: continue
  im=Image.open(P/'views'/f'{d}.png').convert('RGBA')
  im=im.crop(im.getbbox())
  if game:
   im=im.crop(im.getbbox()); im=im.resize((round(im.width*40/im.height),40),Image.Resampling.NEAREST)
  sheet.paste(im,((k%3)*tile_w+(tile_w-im.width)//2,(k//3)*tile_h+tile_h-4-im.height),im)
 sheet.resize((sheet.width*4,sheet.height*4),Image.Resampling.NEAREST).save(P/filename)
print((P/'sizes.txt').read_text()); print((P/'depth.txt').read_text()); print('colours',len(cs),'top five',np.sort(counts)[-5:].sum()/counts.sum())





