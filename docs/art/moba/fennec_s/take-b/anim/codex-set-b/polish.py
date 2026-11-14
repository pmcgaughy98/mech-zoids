"""Restore native still texels on generated poses, then close compositing seams."""
from finish import *

LOG=[]
def eye(a):
 g=(a[:,:,1]>180)&(a[:,:,0]<150)&(a[:,:,2]>110)&(a[:,:,3]>0)
 y,x=np.where(g)
 return (float(x.mean()),float(y.mean())) if len(x) else None

def crop_alpha(im,box):
 a=np.array(im).copy();y,x=np.indices(a.shape[:2]);keep=(x>=box[0])&(x<box[2])&(y>=box[1])&(y<box[3]);a[~keep]=0
 return Image.fromarray(a)

HEAD_BOTTOM={'front':109,'side':109,'back':104}
FACE={'front':(68,95,95,109),'side':(94,92,117,109)}
EAR_BOXES={'front':[(56,69,78,101),(84,69,105,102)],'side':[(80,67,102,105)]}

for name,N in COUNTS.items():
 for n in NAMES:
  ref=approved(n);ra=np.array(ref);re=eye(ra)
  for c in range(N):
   if (name in ['dig','death'] and c==0) or (name=='pop_out' and c in [0,4]) or (name=='dig' and c>=3):continue
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);ge=eye(a);bb=fr.getbbox()
   fullhead=name!='death' or c==1
   if fullhead:
    if n!='back':dx,dy=round(ge[0]-re[0]),round(ge[1]-re[1])
    else:
     # Head and ear rigid pieces are retained at native scale in rear views.
     dx=0;dy=bb[1]-ref.getbbox()[1]
    bottom=HEAD_BOTTOM[n]+20+dy
    # Replace generated head silhouette, not merely paint another head on top.
    if n=='side':a[:bottom,max(0,93+dx):]=0
    else:a[:bottom]=0
    fr=Image.fromarray(a)
    h=np.array(ref).copy();h[HEAD_BOTTOM[n]+20:]=0
    fr.alpha_composite(shifted(Image.fromarray(h),dx,dy));LOG.append(f'{name}/{n}_f{c}: native complete head, ears, face translated {dx},{dy}')
   elif n in FACE:
    # Native half-closed eye/muzzle plate. Final eyes go dark only after restoration.
    if c==6:
     # Same settled face centre as the preceding collapsed pose.
     prev=np.array(Image.open(ROOT/name/'frames'/f'{n}_f5.png'));ge=eye(prev)
    patch=REFS[n].crop(FACE[n]);pa=np.array(patch);pe=eye(pa)
    if ge and pe:
     dx,dy=round(ge[0]-pe[0]),round(ge[1]-pe[1]);original=np.array(fr)[:,:,3]>0
     fr.alpha_composite(patch,(dx,dy));fa=np.array(fr);fa[~original]=0;fr=Image.fromarray(fa)
     LOG.append(f'{name}/{n}_f{c}: native face/half-closed eyes/muzzle at {dx},{dy}, clipped to posed head')
    # Restore cream inner-ear material from native rigid plates, rotated without resizing.
    a=np.array(fr);cream=(np.isin(a[:,:,0],[240,255]))&(a[:,:,1]>=200)&(a[:,:,2]<230)&(a[:,:,3]>0)
    # Ears sit above the eye line, chest and muzzle are excluded.
    if ge:
     yy,xx=np.indices(cream.shape);cream &= yy<ge[1]-4
     labs,k=ndi.label(cream);regions=[]
     for j in range(1,k+1):
      y,x=np.where(labs==j)
      if len(x)>10:regions.append((float(x.mean()),float(y.mean()),len(x)))
     regions=sorted(regions,key=lambda v:v[0])
     for j,reg in enumerate(regions):
      if n=='front':idx=0 if reg[0]<ge[0] else 1
      else:idx=0
      box=EAR_BOXES[n][idx];ea=np.array(REFS[n].crop(box));em=(ea[:,:,0]>=220)&(ea[:,:,1]>=180)&(ea[:,:,2]<230)&(ea[:,:,3]>0);ea[~em]=0
      ang=(55 if idx==0 else -55) if n=='front' else 55
      patch=Image.fromarray(ea).rotate(ang,resample=Image.Resampling.NEAREST,expand=True);p=np.array(patch);y,x=np.where(p[:,:,3]>0)
      if not len(x):continue
      dx,dy=round(reg[0]-x.mean()),round(reg[1]-y.mean());orig=np.array(fr);fr.alpha_composite(patch,(dx,dy));a=np.array(fr)
      # Copy only inside the corresponding generated cream ear region, preserving its outline.
      mask=ndi.binary_dilation(labs==int(labs[round(reg[1]),round(reg[0])]),iterations=1) if labs[round(reg[1]),round(reg[0])]>0 else cream
      keep=mask&(orig[:,:,3]>0);a[~keep]=orig[~keep];fr=Image.fromarray(a)
      LOG.append(f'{name}/{n}_f{c}: native cream ear texels rigid-rotated {ang} degrees')
   a=np.array(fr)
   if name=='death' and c==6:
    g=(a[:,:,1]>180)&(a[:,:,0]<210)&(a[:,:,3]>0);a[g,:3]=PAL[2]
   a[161:]=0
   # Fill enclosed holes and remove detached source debris, with a clean dark rim.
   fr=clean(Image.fromarray(a));fr.save(path)

# Native circular hip disc and shoulder disc, where the posed grey centres expose them.
for name,N in COUNTS.items():
 for n in NAMES:
  if n=='side':boxes=[(84,124,91,132),(91,111,100,120)]
  elif n=='front':boxes=[(68,111,73,119),(88,111,93,119)]
  else:continue  # Back discs are mostly occluded; do not invent visible frontal joints.
  templates=[]
  for box in boxes:
   patch=REFS[n].crop(box);pa=np.array(patch);g=np.all(pa[:,:,:3]==PAL[5],2)&(pa[:,:,3]>0)
   # Only the joint's native greys belong to the template, never neighboring chest cream.
   keep=np.zeros(pa.shape[:2],bool)
   for index in [3,5,8]:keep |= np.all(pa[:,:,:3]==PAL[index],2)&(pa[:,:,3]>0)
   pa[~keep]=0;patch=Image.fromarray(pa)
   if g.sum():
    y,x=np.where(g);templates.append((patch,x.mean(),y.mean(),g.sum()))
  for c in range(1,N):
   if (name=='dig' and c>=3) or (name=='pop_out' and c in [0,4]):continue
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);m=a[:,:,3]>0
   g=np.all(a[:,:,:3]==PAL[5],2)&m;g[154:]=False;lab,k=ndi.label(g)
   for j in range(1,k+1):
    y,x=np.where(lab==j)
    if len(x)<5 or len(x)>45 or y.max()-y.min()>10:continue
    patch,cx,cy,size=min(templates,key=lambda t:abs(t[3]-len(x)));dx,dy=round(x.mean()-cx),round(y.mean()-cy)
    fr.alpha_composite(patch,(dx,dy));a=np.array(fr);a[~m]=0;fr=Image.fromarray(a)
    LOG.append(f'{name}/{n}_f{c}: native grey joint disc at {dx},{dy}')
   fr=clean(clipped(fr));fr.save(path)

# Late dig is an actual clipped descent, not a standing rump at ground level.
# Frame 3 retains rump and hind limbs; frame 4 exposes the final rump edge and tail.
for n in NAMES:
 for c in [3,4]:
  path=ROOT/'dig'/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);m=a[:,:,3]>0
  # Keep a native one-texel cut edge where the body crosses underground.
  a[160,m[160],:3]=PAL[0];fr=clean(Image.fromarray(a));fr.save(path)

for name in COUNTS:board(name)
(ROOT/'native_finish_log.txt').write_text('\n'.join(LOG)+'\n')
print('Native head/eye/muzzle/ear/disc restoration complete:',len(LOG),'placements')
