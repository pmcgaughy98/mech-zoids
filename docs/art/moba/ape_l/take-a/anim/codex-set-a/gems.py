from finish import *

def template(n,box):
 a=np.array(REFS[n].crop(box));g=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,2]>70)&(a[:,:,3]>0)
 lab,k=ndi.label(g);sz=np.bincount(lab.ravel());sz[0]=0;g=lab==sz.argmax()
 mask=ndi.binary_dilation(g,iterations=4)&(a[:,:,3]>0)
 # Keep gem and its grey bezel; orange gauntlet corners belong to the pose.
 orange=(a[:,:,0]>a[:,:,1]*1.1)&(a[:,:,1]>a[:,:,2]*1.3)
 mask &= ~orange;a[~mask]=0;yy,xx=np.where(g)
 return Image.fromarray(a),(xx.mean(),yy.mean())
tiles={'flat':template('side',(77,95,105,122)),'left':template('front',(33,94,51,120)),'right':template('front',(109,94,126,120))}
log=[]
for name in ['chest_beat','hex_shield']:
 for n in NAMES:
  for c in range(1,COUNTS[name]-1):
   p=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(p).convert('RGBA');a=np.array(fr);bb=fr.getbbox()
   g=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,2]>70)&(a[:,:,3]>0);lab,k=ndi.label(g)
   for j in range(1,k+1):
    y,x=np.where(lab==j)
    if len(x)<35:continue
    cx,cy=x.mean(),y.mean();w=x.max()-x.min()+1;h=y.max()-y.min()+1
    if n=='back' and cy<bb[1]+28:continue
    key=('left' if cx<96 else 'right') if w/h<.72 else 'flat'
    patch,center=tiles[key];dx,dy=round(cx-center[0]),round(cy-center[1]);fr.alpha_composite(patch,(dx,dy));log.append(f'{name}/{n}_f{c}: {key} native gem/bezel at {dx},{dy}')
   # Remove any detached single-pixel debris after all compositing.
   original_mask=a[:,:,3]>0
   a=np.array(fr);a[~original_mask]=0;m=a[:,:,3]>0;labs,k=ndi.label(m,structure=np.ones((3,3)));sz=np.bincount(labs.ravel());drop=(sz[labs]<3)&m;a[drop]=0
   # A projected gem stays inside the generated gauntlet silhouette.
   rim=m&~ndi.binary_erosion(m);a[rim,:3]=PAL[0];Image.fromarray(a).save(p)
for n in NAMES:
 # Penultimate beat frame is the final one-pixel settle onto planted knuckles.
 Image.open(ROOT/'idle'/'frames'/f'{n}_f1.png').save(ROOT/'chest_beat'/'frames'/f'{n}_f6.png')
for name in COUNTS:board(name)
(ROOT/'gem_finish_log.txt').write_text('\n'.join(log)+'\n')
print('Native gem finishing done')
