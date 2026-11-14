from finish import *

def piece(im,mask):
 a=np.array(im).copy();a[~mask]=0;return Image.fromarray(a)

def shift(im,dx,dy):
 out=Image.new('RGBA',im.size);out.paste(im,(dx,dy));return out

def compose(parts):
 out=Image.new('RGBA',(192,192))
 for im,dx,dy in parts:out.alpha_composite(shift(im,dx,dy))
 return out

# Restore native face plates/eyes and back gem, fitting a translated template
# inside the generated head area. Pose silhouettes elsewhere remain generated.
boxes={'front':(69,80,90,95),'side':(104,82,116,97),'back':(65,61,94,86)}
log=[]
for name in ['bound','hex_dome','death']:
 for n in NAMES:
  ref=REFS[n];box=boxes[n];patch=ref.crop(box);pa=np.array(patch);pm=pa[:,:,3]>0
  base=approved(n);bb0=base.getbbox()
  for c in range(1,COUNTS[name]-(0 if name=='death' else 1)):
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);bb=fr.getbbox()
   if n=='side' and name=='chest_beat' and c in [3,4]:
    log.append(f'{name}/{n}_f{c}: chest fist occludes face; no stamp')
    continue
   # Locate actual generated eye/gem pixels before stamping. Body-top offsets
   # are unreliable when the gorilla rears or the throwing arm is raised.
   green=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,2]>70)&(a[:,:,3]>0)
   labels,k=ndi.label(green);candidates=[]
   for j in range(1,k+1):
    gy,gx=np.where(labels==j);cx,cy=gx.mean(),gy.mean()
    if n=='back': ok=len(gx)>20 and cy<bb[1]+(bb[3]-bb[1])*.45
    elif n=='front':ok=len(gx)<30 and abs(cx-96)<17 and cy<bb[1]+(bb[3]-bb[1])*.58
    else:ok=len(gx)<24 and cx>bb[0]+(bb[2]-bb[0])*.70 and cy<bb[1]+(bb[3]-bb[1])*.49
    if ok:candidates.append((cx,cy,len(gx)))
   if not candidates:
    log.append(f'{name}/{n}_f{c}: face occluded; no stamp')
    continue
   if n=='front':cx=np.mean([v[0] for v in candidates]);cy=np.mean([v[1] for v in candidates])
   elif n=='side':cx,cy,_=max(candidates,key=lambda v:v[0])
   else:cx,cy,_=min(candidates,key=lambda v:(v[0]-96)**2+(v[1]-bb[1]-12)**2)
   pg=(pa[:,:,1]>185)&(pa[:,:,0]<110)&(pa[:,:,2]>70)&pm
   py,px=np.where(pg)
   ex=round(cx-px.mean());ey=round(cy-py.mean());best=None
   for dy in range(-1,2):
    for dx in range(-1,2):
     x,y=ex+dx,ey+dy;t=a[y:y+patch.height,x:x+patch.width]
     if t.shape!=pa.shape:continue
     score=((t[:,:,:3].astype(float)-pa[:,:,:3])**2).mean(2)[pm].mean()+80*(dx*dx+dy*dy)
     if best is None or score<best[0]:best=(score,x,y)
   _,x,y=best;original=a[:,:,3]>0;fr.alpha_composite(patch,(x,y));a=np.array(fr);a[~original]=0;Image.fromarray(a).save(path)
   log.append(f'{name}/{n}_f{c}: native {"back gem" if n=="back" else "head/face/eyes"} at {x},{y}')
(ROOT/'native_finish_log.txt').write_text('\n'.join(log)+'\n')
for name in COUNTS:board(name)
print('Native detail and cycle finish complete')
