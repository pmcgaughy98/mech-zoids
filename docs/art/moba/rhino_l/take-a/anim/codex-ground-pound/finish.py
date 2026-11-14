from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as ndi

OUT = Path(__file__).resolve().parent
NAMES = ['front', 'side', 'back']
refs = [Image.open(OUT/'refs'/f'{n}.png').convert('RGBA') for n in NAMES]
pal = np.unique(np.concatenate([np.array(im)[np.array(im)[:,:,3]>0,:3] for im in refs]),axis=0)
raw = Image.open(OUT/'sheet_raw.png').convert('RGBA')
a = np.array(raw); rgb = a[:,:,:3].astype(float)
meta = dict(size=list(raw.size),sha256=hashlib.sha256((OUT/'sheet_raw.png').read_bytes()).hexdigest(),palette=pal.tolist())
(OUT/'generation.json').write_text(json.dumps(meta,indent=2)+'\n')
# Key saturated pink, including dark plum contamination. Grey and yellow remain.
pink = (rgb[:,:,0]-rgb[:,:,1]>28)&(rgb[:,:,2]-rgb[:,:,1]>24)&(rgb[:,:,2]>rgb[:,:,0]*.64)
mask = (a[:,:,3]>127)&~pink
labels,count=ndi.label(mask)
sizes=np.bincount(labels.ravel()); keep=np.flatnonzero(sizes>max(20,mask.sum()*.0003)); keep=keep[keep!=0]
# Tiny disconnected generator debris is discarded at source resolution, before smoothing/palette.
mask=np.isin(labels,keep)
W,H=raw.size; xs=np.rint(np.linspace(0,W,7)).astype(int)
# Detect the two actual empty row gutters. Equal thirds would cut the rear-view horns.
occupied=mask.any(axis=1); bands=ndi.find_objects(ndi.label(occupied)[0])
bands=[b[0] for b in bands if b[0].stop-b[0].start>H*.12]
ys=np.array([0]+[(bands[i].stop+bands[i+1].start)//2 for i in range(2)]+[H]) if len(bands)==3 else np.rint(np.linspace(0,H,4)).astype(int)
found=[]; clean=True
for r in range(3):
 for c in range(6):
  m=mask[ys[r]:ys[r+1],xs[c]:xs[c+1]]; yy,xx=np.where(m)
  lab,num=ndi.label(m); sz=np.bincount(lab.ravel())[1:]; major=int((sz>max(30,m.sum()*.025)).sum())
  box=None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
  okay=box is not None and min(box[0],box[1],m.shape[1]-box[2],m.shape[0]-box[3])>=2 and major==1
  clean &= okay
  found.append(dict(row=NAMES[r],column=c+1,box=box,major_components=major,clean=bool(okay)))
(OUT/'grid.json').write_text(json.dumps(dict(clean=bool(clean),cells=found),indent=2)+'\n')
if not clean:
 (OUT/'checks.txt').write_text('FAIL: no clean 3x6 grid. See grid.json. Stopped before finishing.\n')
 print(json.dumps(dict(status='grid_failed',metadata=meta,cells=found))); raise SystemExit(2)
side=found[6]['box']; factor=103/(side[2]-side[0]); nw,nh=round(W*factor),round(H*factor)
# Fill exterior RGB from nearest foreground, then smooth very lightly before reduction.
indices=ndi.distance_transform_edt(~mask,return_distances=False,return_indices=True)
filled=a[:,:,:3][tuple(indices)]
filled=Image.fromarray(filled).filter(ImageFilter.MedianFilter(3))
small=np.array(filled.resize((nw,nh),Image.Resampling.LANCZOS))
alpha=np.array(Image.fromarray(mask.astype('uint8')*255).resize((nw,nh),Image.Resampling.BOX))>=128
# Smooth in continuous colour before exact palette mapping, never despeckle quantized pixels.
small=np.array(Image.fromarray(small).filter(ImageFilter.MedianFilter(3)))
# Suppress isolated bright rim samples in continuous RGB before the palette step.
rim=alpha&~ndi.binary_erosion(alpha)
for iteration in range(4):
 previous=small.copy()
 for y,x in zip(*np.where(rim&(small.mean(2)>170))):
  y0,y1=max(0,y-1),min(nh,y+2); x0,x1=max(0,x-1),min(nw,x+2)
  near=previous[y0:y1,x0:x1][alpha[y0:y1,x0:x1]].astype(float)
  if len(near)>1 and (np.linalg.norm(near-previous[y,x],axis=1)<70).sum()<3:
   small[y,x]=np.median(near,axis=0).astype('uint8')
palette=pal.astype(np.int32)
# Quantizer-aware smoothing still modifies continuous RGB only, before final mapping.
# This prevents isolated highlight samples at Voronoi colour boundaries.
for iteration in range(12):
 trial=((small[:,:,None,:].astype(np.int32)-palette[None,None,:,:])**2).sum(3).argmin(2)
 changes=[]
 for y,x in zip(*np.where(rim&(pal[trial].mean(2)>180))):
  y0,y1=max(0,y-1),min(nh,y+2); x0,x1=max(0,x-1),min(nw,x+2)
  localmask=alpha[y0:y1,x0:x1].copy(); localmask[y-y0,x-x0]=False
  nearby=trial[y0:y1,x0:x1][localmask]
  if len(nearby) and not (nearby==trial[y,x]).any():
   continuous=small[y0:y1,x0:x1][localmask]
   changes.append((y,x,np.median(continuous,axis=0).astype('uint8')))
 if not changes: break
 for y,x,value in changes: small[y,x]=value
flat=small.reshape(-1,3).astype(np.int32)
dist=((flat[:,None,:]-palette[None,:,:])**2).sum(2)
quant=pal[dist.argmin(1)].reshape(nh,nw,3)
finished=np.dstack([quant,alpha.astype('uint8')*255]); finished[~alpha]=0
sheet=Image.fromarray(finished,'RGBA'); sheet.save(OUT/'sheet_finished.png')
(OUT/'frames').mkdir(exist_ok=True)
frames=[]; checks=[f'Clean 3x6 grid: YES; uniform shrink factor {factor:.10f}; finished sheet {nw}x{nh}.',f'Exact reference union palette: {len(pal)} colours. Alpha binary.']
sx=np.rint(xs*factor).astype(int); sy=np.rint(ys*factor).astype(int)
for r,n in enumerate(NAMES):
 cell0=sheet.crop((sx[0],sy[r],sx[1],sy[r+1])); b=cell0.getbbox()
 dx=round(96-(b[0]+b[2]-1)/2); dy=160-(b[3]-1)
 row=[]
 for c in range(6):
  cell=sheet.crop((sx[c],sy[r],sx[c+1],sy[r+1])); f=Image.new('RGBA',(192,192)); f.paste(cell,(dx,dy))
  # Fixed column-1 anchor for all six cells. No per-frame recentering or vertical correction.
  f.save(OUT/'frames'/f'{n}_f{c}.png'); row.append(f)
  ar=np.array(f); m=ar[:,:,3]>0; yy,xx=np.where(m); colors=np.unique(ar[m,:3],axis=0)
  border=bool(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
  checks.append(f'{n}_f{c}: width={xx.max()-xx.min()+1}, height={yy.max()-yy.min()+1}, colours={len(colors)}, in_ref_palette={all(any(np.array_equal(v,p) for p in pal) for v in colors)}, bottom_y={yy.max()}, border_touch={border}')
 frames.append(row)
for r,n in enumerate(NAMES):
 f=frames[r][0]; ref=refs[r]; b=f.getbbox(); rb=ref.getbbox()
 aligned=Image.new('RGBA',(192,192)); aligned.paste(ref,(round((b[0]+b[2]-rb[0]-rb[2])/2),b[3]-rb[3]))
 fa,ra=np.array(f),np.array(aligned); union=(fa[:,:,3]>0)|(ra[:,:,3]>0)
 similarity=(np.all(fa==ra,axis=2)&union).sum()/union.sum()
 checks.append(f'{n} column1 vs ref: {b[2]-b[0]}x{b[3]-b[1]} vs {rb[2]-rb[0]}x{rb[3]-rb[1]}; exact colour match over opaque union after feet alignment={similarity:.4f}')
 if n!='side':
  vals=[]
  for f in frames[r]:
   b=f.getbbox(); ar=np.array(f.crop(b)); m=ar[:,:,3]>0; flip=ar[:,::-1]; union=m|(flip[:,:,3]>0)
   vals.append(float((np.all(ar==flip,axis=2)&union).sum()/union.sum()))
  checks.append(f'{n} mirror exact-colour similarities F0..F5: '+', '.join(f'{v:.3f}' for v in vals))
# Feet are grey, low-chroma clusters. Save all candidates for honest manual/semantic interpretation.
footdata=[]
for r,n in enumerate(NAMES):
 for c,f in enumerate(frames[r]):
  ar=np.array(f); rgb=ar[:,:,:3].astype(int); grey=(rgb.max(2)-rgb.min(2)<22)&(rgb.mean(2)>52)&(ar[:,:,3]>0)
  grey[:100]=False
  lab,num=ndi.label(grey); candidates=[]
  for k in range(1,num+1):
   yy,xx=np.where(lab==k)
   if len(xx)>=6 and xx.max()-xx.min()>=3:
    candidates.append(dict(box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],area=len(xx),clearance=int(160-yy.max())))
  footdata.append(dict(frame=f'{n}_f{c}',candidates=candidates))
(OUT/'foot-candidates.json').write_text(json.dumps(footdata,indent=2)+'\n')
# Labelled review at exact requested nearest-neighbour scales.
review=Image.new('RGB',(70+6*576,32+3*600),(128,128,128)); d=ImageDraw.Draw(review)
for c in range(6): d.text((70+c*576+270,8),f'F{c}',fill='white')
for r,n in enumerate(NAMES):
 d.text((5,32+r*600+260),n,fill='white')
 for c,f in enumerate(frames[r]):
  z=f.resize((576,576),Image.Resampling.NEAREST); review.paste(z,(70+c*576,32+r*600),z)
review.save(OUT/'review.png')
comparison=Image.new('RGB',(2*768+100,3*800),(128,128,128)); d=ImageDraw.Draw(comparison)
for r,n in enumerate(NAMES):
 d.text((4,r*800+4),f'{n}: generated F0 / approved ref',fill='white')
 for c,f in enumerate([frames[r][0],refs[r]]):
  z=f.resize((768,768),Image.Resampling.NEAREST); comparison.paste(z,(50+c*768,r*800+24),z)
comparison.save(OUT/'review-vs-ref.png')
for r,n in enumerate(NAMES):
 gif=[]
 for f in frames[r]:
  bg=Image.new('RGB',(192,192),(128,128,128)); bg.paste(f,mask=f.getchannel('A')); gif.append(bg.resize((576,576),Image.Resampling.NEAREST))
 gif[0].save(OUT/f'preview_{n}.gif',save_all=True,append_images=gif[1:],duration=[400,120,120,120,120,120],loop=0,disposal=2)
# Palette edge audit includes per-colour rim share and top-five concentration.
allcol=[]; edgecounts=np.zeros(len(pal),int); totalcounts=np.zeros(len(pal),int)
for row in frames:
 for f in row:
  ar=np.array(f); m=ar[:,:,3]>0; rim=m&~ndi.binary_erosion(m)
  for i,p in enumerate(pal):
   hit=np.all(ar[:,:,:3]==p,axis=2)&m; totalcounts[i]+=hit.sum(); edgecounts[i]+=(hit&rim).sum()
checks.append('Palette edge audit (hex: total_px, rim_px, rim_share):')
for p,t,e in zip(pal,totalcounts,edgecounts): checks.append(f'#{p[0]:02X}{p[1]:02X}{p[2]:02X}: {t}, {e}, {e/max(1,t):.4f}')
checks.append(f'Top-5 colour share={np.sort(totalcounts)[-5:].sum()/totalcounts.sum():.4f}; no magenta/plum exists in the reference palette.')
(OUT/'checks.txt').write_text('\n'.join(checks)+'\n')
meta.update(shrink_factor=factor,grid_clean=True,finished_size=[nw,nh]); (OUT/'generation.json').write_text(json.dumps(meta,indent=2)+'\n')
print('\n'.join(checks[:26])); print('FOOT CANDIDATES'); print(json.dumps(footdata))
