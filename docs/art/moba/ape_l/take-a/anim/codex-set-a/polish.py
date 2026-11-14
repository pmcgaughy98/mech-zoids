from finish import *

def piece(im,mask):
 a=np.array(im).copy();a[~mask]=0;return Image.fromarray(a)

def shift(im,dx,dy):
 out=Image.new('RGBA',im.size);out.paste(im,(dx,dy));return out

def compose(parts):
 out=Image.new('RGBA',(192,192))
 for im,dx,dy in parts:out.alpha_composite(shift(im,dx,dy))
 return out

# Finish the small cyclic motions with the approved native texels. Generated
# pose sheets supply the action plan; no whole-frame translations or resizing.
for n in NAMES:
 ref=approved(n);a=np.array(ref);yy,xx=np.indices((192,192));sx=xx-16;sy=yy-30
 # Forearms/feet stay fixed during breathing. Chest, head and shoulders lift.
 upper=(sy<100)
 if n=='front': upper &= ~(((sx<61)|(sx>=99))&(sy>=90))
 elif n=='side':upper &= ~((sx>=73)&(sy>=92))
 else:upper &= ~(((sx<55)|(sx>=104))&(sy>=90))
 body=piece(ref,upper);fixed=piece(ref,~upper)
 for c,d in enumerate([0,1,2,1,0]):
  fr=compose([(ref,0,0),(body,0,-d),(fixed,0,0)])
  fr.save(ROOT/'idle'/'frames'/f'{n}_f{c}.png')

 # Anatomical right forearm + left hind foot form diagonal A.
 if n=='front':
  arms=[(sx<61)&(sy>=89),(sx>=99)&(sy>=89)]
  legs=[(sx>=84)&(sx<99)&(sy>=105),(sx>=61)&(sx<76)&(sy>=105)]
 elif n=='back':
  arms=[(sx>=104)&(sy>=90),(sx<55)&(sy>=90)]
  legs=[(sx>=48)&(sx<73)&(sy>=108),(sx>=87)&(sx<111)&(sy>=108)]
 else:
  arms=[(sx>=72)&(sx<108)&(sy>=92),(sx>=108)&(sy>=95)]
  legs=[(sx>=100)&(sy>=116),(sx<67)&(sy>=109)]
 # Give each texel exactly one owner, including overlaps hidden by forearms.
 used=np.zeros((192,192),bool);layers=[]
 for mask in arms+legs:
  mask &= ~used;used |= mask;layers.append(piece(ref,mask))
 torso=piece(ref,~used)
 liftsA=[0,0,0,0,0,-2,-3,-1];liftsB=[0,-2,-3,-1,0,0,0,0]
 bob=[0,-1,0,1,0,-1,0,1]
 for c in range(8):
  # Contact coordinates are constant. The swing pair lifts and returns to
  # those coordinates; there is no lateral drift of a planted endpoint.
  da,db=liftsA[c],liftsB[c]
  xa=([0,0,0,0,0,-3,0,3][c] if n=='side' else [0,0,0,0,0,-1,0,1][c])
  xb=([0,-3,0,3,0,0,0,0][c] if n=='side' else [0,-1,0,1,0,0,0,0][c])
  # Keep every ground texel out of the bobbing torso, including the small
  # outside corners which sit beyond the hind-foot masks in the rear still.
  torso_a=np.array(torso);ground=torso_a.copy();ground[:159]=0;torso_a[159:]=0
  moving=Image.fromarray(torso_a)
  fr=compose([(moving,0,0),(moving,0,bob[c]),(Image.fromarray(ground),0,0),(layers[2],xa,da),(layers[3],xb,db),(layers[0],xa,da),(layers[1],xb,db)])
  # Back view uses the same anatomical pair, reversed on screen.
  fr.save(ROOT/'walk'/'frames'/f'{n}_f{c}.png')

# Restore native face plates/eyes and back gem, fitting a translated template
# inside the generated head area. Pose silhouettes elsewhere remain generated.
boxes={'front':(69,80,90,95),'side':(104,82,116,97),'back':(65,61,94,86)}
log=[]
for name in ['chest_beat','hex_shield']:
 for n in NAMES:
  ref=REFS[n];box=boxes[n];patch=ref.crop(box);pa=np.array(patch);pm=pa[:,:,3]>0
  base=approved(n);bb0=base.getbbox()
  for c in range(1,COUNTS[name]-1):
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
    else:ok=len(gx)<24 and cx>100 and cy<bb[1]+(bb[3]-bb[1])*.55
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
   _,x,y=best;fr.alpha_composite(patch,(x,y));fr.save(path)
   log.append(f'{name}/{n}_f{c}: native {"back gem" if n=="back" else "head/face/eyes"} at {x},{y}')
(ROOT/'native_finish_log.txt').write_text('\n'.join(log)+'\n')
for name in COUNTS:board(name)
print('Native detail and cycle finish complete')
