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
 tile_w, tile_h = (max(v[0] for v in sizes.values())+8,max(v[1] for v in sizes.values())+8) if not game else (max(round(v[0]*40/v[1]) for v in sizes.values())+8,48)
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






# Shade islands are counted with eight-connectivity to avoid calling a diagonal band speckles.
ramps={'crimson':['ff8a98','e0203e','9c1030','520a1e'],'steel':['e2e5ec','a6abb6','60646f']}
mottling={}; cyan={}
for d in [x for x in names if x]:
 a=np.array(Image.open(P/'views'/f'{d}.png').convert('RGBA'))
 result={}
 for material,cols in ramps.items():
  masks=[np.all(a[:,:,:3]==tuple(bytes.fromhex(c)),axis=2)&(a[:,:,3]>0) for c in cols]
  mat=np.any(masks,axis=0); small=[]
  for hexcol,m in zip(cols,masks):
   labels,num=ndimage.label(m,np.ones((3,3)))
   for i in range(1,num+1):
    mask=labels==i; count=int(mask.sum())
    if count>3: continue
    ring=ndimage.binary_dilation(mask,structure=np.ones((3,3)))&~mask
    if np.all(mat[ring]):
     y,x=np.where(mask)
     small.append({'colour':hexcol,'pixels':count,'xy':[int(x.min()),int(y.min())]})
  result[material]={'islands':len(small),'details':small}
 result['total']=sum(result[m]['islands'] for m in ramps)
 mottling[d]=result
 cyan[d]=int(((a[:,:,3]>0)&(np.all(a[:,:,:3]==(82,242,255),axis=2)|np.all(a[:,:,:3]==(236,255,255),axis=2))).sum())
(P/'mottling.json').write_text(json.dumps({'definition':'8-connected shade islands of 1-3 pixels wholly enclosed within crimson or steel, including diagonal surroundings; seam, material-edge and silhouette contacts excluded. Conservative candidates; visual inspection also checks all big plates.','views':mottling},indent=2))
# Semantic counts below are by-eye observations, not inferred by a pixel classifier.
contacts={'ne':4,'n':4,'nw':4,'e':3,'w':3,'se':2,'s':2,'sw':2}
shape=['Every view W x H: '+', '.join(f'{d} {v[0]}x{v[1]}' for d,v in sizes.items()),
 'South width comparison: '+', '.join(f's/{d}={sizes["s"][0]/v[0]:.4f}' for d,v in sizes.items() if d!='s'),
 f'East/south height: {sizes["e"][1]}/{sizes["s"][1]}={sizes["e"][1]/sizes["s"][1]:.4f}; exact matching FAIL.',
 f'North/south height: {sizes["n"][1]}/{sizes["s"][1]}={sizes["n"][1]/sizes["s"][1]:.4f}; no-taller FAIL; heights drift.',
 f'NE/NW cyan eye pixels: {cyan["ne"]}/{cyan["nw"]} (including pale eye-glint colour).',
 'Claw pixels above the eye-socket bottom: 0 apparent by eye in all views; claws in front of eyes: 0 apparent by eye. No semantic pixel segmentation, so these are visual counts.',
 'Leg-tip contacts planted/clearly visible by eye: '+', '.join(f'{d} {v}/{v}' for d,v in contacts.items())+'. Far feet may sit higher in projection; no clearly visible foot is lifted. Six distinct legs are not verifiable when hidden.',
 'Both claws appear resting in all views; SE/SW both eyes visible, far lens partially occluded. Rear views show no face or lens; camera broadly consistent, though north is too tall.',
 'Remaining enclosed 1-3px shade islands by view: '+', '.join(f'{d} {v["total"]} (crimson {v["crimson"]["islands"]},steel {v["steel"]["islands"]})' for d,v in mottling.items())+'. Claw interiors retain mottling; not clean throughout.']
(P/'shape.txt').write_text('\n'.join(shape))
print(shape[-1])
