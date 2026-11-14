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
 tile=192 if not game else 100
 sheet=Image.new('RGB',(tile*3,tile*3),(128,128,128))
 for k,d in enumerate(names):
  if d is None: continue
  im=Image.open(P/'views'/f'{d}.png').convert('RGBA')
  if game:
   im=im.crop(im.getbbox()); im=im.resize((round(im.width*40/im.height),40),Image.Resampling.NEAREST)
  sheet.paste(im,((k%3)*tile+(tile-im.width)//2,(k//3)*tile+tile-12-im.height),im)
 sheet.resize((sheet.width*4,sheet.height*4),Image.Resampling.NEAREST).save(P/filename)
print((P/'sizes.txt').read_text()); print((P/'depth.txt').read_text()); print('colours',len(cs),'top five',np.sort(counts)[-5:].sum()/counts.sum())

# Landmarks selected by eye on the measured native crops, excluding ears/fins/tail.
# Inclusive pixel spans; measurement images label crop-local x/y coordinates.
e = np.array(Image.open(P/'views/e.png').convert('RGBA'))
e = e[95:161,41:151]
assert e[9,73,3] and e[35,60,3] and not e[36:66,60,3].any()
s = np.array(Image.open(P/'views/s.png').convert('RGBA'))[89:161,80:113]
assert s[15,5,3] and s[15,27,3] and s[32,0,3] and s[32,32,3]
shape = {'east_shoulder_height':57,'east_chest_gap':30,'east_body_chest_to_rump':57,'south_chest_width':33,'south_head_width':23}
(P/'shape.txt').write_text(
 'Native finished-pixel measurements; anatomical landmarks chosen by eye, approximate to 1-2 px.\n'
 'Coordinates below are crop-local; measure-e.png and measure-s.png show the grid.\n'
 'east: shoulder height 57 px (shoulder x73 y9, ground y65 inclusive).\n'
 'east: clear gap under chest 30 px (x60, empty rows y36..65); gap/shoulder 0.526.\n'
 'east: body chest-to-rump length 57 px (rump x29 to chest x85 inclusive, excluding neck/tail); length/shoulder 1.000, target about 1.5 FAIL.\n'
 'south: chest width 33 px (x0..32 at y32), head width 23 px (hood x5..27 at y15, excluding ears/fins); chest/head 1.435, too wide for barely wider.\n')
metrics=json.loads((P/'metrics.json').read_text()); metrics['shape']=shape
(P/'metrics.json').write_text(json.dumps(metrics,indent=2))
print((P/'shape.txt').read_text())
