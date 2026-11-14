"""Local pixel corrections following the first review, without regeneration."""
from finish import *
for n in NAMES:
 # Crouch has exactly a four-native-pixel torso drop and fixed contacts.
 ref=approved(n);a=np.array(ref);yy,xx=np.indices(a.shape[:2]);sx=xx-16;sy=yy-30
 upper=sy<100
 if n=='se':upper &= ~(((sx<80)|(sx>=106))&(sy>=91))
 else:upper &= ~(((sx<55)|(sx>=98))&(sy>=91))
 fixed=a.copy();fixed[upper]=0;moving=a.copy();moving[~upper]=0
 fr=Image.fromarray(fixed);layer=Image.new('RGBA',(192,192));layer.paste(Image.fromarray(moving),(0,4));fr.alpha_composite(layer)
 fr.save(ROOT/'bound'/'frames'/f'{n}_f1.png')
 # Both fists are overhead already in column 2; column 3 rises four pixels.
 a=np.array(Image.open(ROOT/'hex_dome'/'frames'/f'{n}_f3.png'));m=a[:,:,3]>0;yy,xx=np.indices(m.shape);bb=Image.fromarray(a).getbbox()
 arm=(yy<bb[1]+42)
 fixed=a.copy();fixed[arm]=0;moving=a.copy();moving[~arm]=0
 fr=Image.fromarray(fixed);layer=Image.new('RGBA',(192,192));layer.paste(Image.fromarray(moving),(0,4));fr.alpha_composite(layer)
 fr.save(ROOT/'hex_dome'/'frames'/f'{n}_f2.png')
 # The prone body settles one pixel; ground contact texels remain planted.
 p=ROOT/'death'/'frames'/f'{n}_f6.png';fr=Image.open(p).convert('RGBA');a=np.array(fr);bb=fr.getbbox()
 if n!='ne':
  green=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,2]>70)&(a[:,:,3]>0);lab,k=ndi.label(green)
  for j in range(1,k+1):
   y,x=np.where(lab==j)
   # Eyes are small islands inside the head. The large gem islands stay green.
   if len(x)<28 and (100<x.mean()<120 and y.mean()<bb[1]+(bb[3]-bb[1])*.75):
    a[lab==j,:3]=(71,71,79)
  # Use the faceplate's darkest actual grey from approved palette.
  grey=PAL[(np.ptp(PAL.astype(int),axis=1)<18)&(PAL[:,0]>35)]
  mask=np.all(a[:,:,:3]==(71,71,79),axis=2)&(a[:,:,3]>0);a[mask,:3]=grey[np.sum(grey.astype(int),axis=1).argmin()]
 fr=Image.fromarray(a);fr.save(p);settle=Image.new('RGBA',(192,192));settle.paste(fr,(0,1));sa=np.array(settle);sa[159:]=np.array(fr)[159:];settle=Image.fromarray(sa);settle.save(ROOT/'death'/'frames'/f'{n}_f7.png')
print('Crouch, overhead lead-in and prone settle corrected')
