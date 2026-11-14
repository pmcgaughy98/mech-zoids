from repair import *
import shutil,hashlib
LOG=[]
def load(m,v,i):
 p=files(m,v)[i];return p,np.array(Image.open(p).convert('RGBA'))
def save(p,a,note):
 old=np.array(Image.open(p).convert('RGBA'))
 if np.array_equal(old,a):return
 n=int(p.stem.split('_f')[1]);m=p.parent.parent.name;assert not ((n==0 and m not in ['walk','pop_out']) or (n==len(files(m,p.stem.split('_f')[0]))-1 and m in ['idle','sand_kick','ear_burst','sonic_boom','pop_out']))
 dest=p.parent.parent/'frames_pre_repair'/p.name;dest.parent.mkdir(exist_ok=True)
 if not dest.exists():shutil.copy2(p,dest)
 Image.fromarray(a).save(p);LOG.append([m,p.stem,note,int(np.any(old!=a,axis=2).sum())])
def cap(a,x0,x1,y,c=6):
 # Individually chosen cut: two stepped rows complete its rounded cap.
 w=x1-x0+1
 if w<5:return
 a[y-2,x0+2:x1-1]=COL[0]
 a[y-1,x0+1:x1]=COL[c];a[y-1,x0+1]=COL[0];a[y-1,x1-1]=COL[0]
 a[y,x0+1:x1]=COL[c]
 a[y,x0]=COL[0];a[y,x1]=COL[0]
def poly(a,pts,c):
 im=Image.fromarray(a);ImageDraw.Draw(im).polygon(pts,fill=COL[c]);a[:]=np.array(im)
def clear(a,x0,y0,x1,y1):a[y0:y1+1,x0:x1+1]=0
# Idle's translated upper half left an ink line through an unbroken plate.
for v in ['front','back']:
 for i in [1,2,3]:
  p,a=load('idle',v,i)
  if v=='front':
   # The row spans cream and joint; preserve both materials across the join.
   for x in range(87,106):
    if tuple(a[138,x])==COL[0]:a[138,x]=a[137,x] if a[137,x,3] else a[139,x]
  else:
   for x in range(87,106):
    if tuple(a[138,x])==COL[0]:a[138,x]=a[137,x]
  save(p,a,'joined the horizontal paste cut through chest/waist plate')
# Walking side back caps and back-view shoulder tabs: each pose has the same source seam.
for i in range(8):
 p,a=load('walk','side',i)
 x0={0:96,1:96,2:94,3:96,4:95,5:94,6:95,7:94}[i];cap(a,x0,103,130,6)
 # Small isolated horizontal silhouette tab at left of the back.
 clear(a,85,136,86,136)
 save(p,a,'finished stepped upper haunch cap and removed back-edge tab')
 p,a=load('walk','back',i)
 # Restore smoothly sloping shoulder margins across the duplicated one-row tabs.
 for y in [129]:
  for x in list(range(78,88))+list(range(106,116)):
   if a[y,x,3] and not a[y-1,x,3] and not a[y+1,x,3]:a[y,x]=0
 save(p,a,'removed horizontal shoulder paste tabs; continuous sloped margins retained')
# The kick's shoulder/hip parts had flat guillotine tops.
for i,segs in {1:[(82,90,134,5),(105,109,134,5)],2:[(79,90,140,5)],3:[(81,85,131,5),(105,113,131,5)],4:[(101,110,138,5)]}.items():
 p,a=load('sand_kick','front',i)
 for x0,x1,y,c in segs:cap(a,x0,x1,y,c)
 save(p,a,'rounded and shaded clipped shoulder/joint caps')
for i,segs in {1:[(86,108,136,6)],2:[(92,99,131,6)],3:[(102,113,130,6),(130,134,130,5)],4:[(83,105,137,6)]}.items():
 p,a=load('sand_kick','side',i)
 for x0,x1,y,c in segs:cap(a,x0,x1,y,c)
 save(p,a,'completed upper hip/shoulder contour across straight paste edge')
for i,segs in {1:[(79,84,134),(107,111,134)],2:[(78,84,138),(107,112,138)],4:[(80,84,135)]}.items():
 p,a=load('sand_kick','back',i)
 for x0,x1,y in segs:cap(a,x0,x1,y,6)
 save(p,a,'completed clipped haunch tops')
p,a=load('sand_kick','back',3)
clear(a,79,130,84,132);clear(a,108,130,112,132)
save(p,a,'removed long leftover horizontal shoulder bars')
# Ear burst upright has a neck/spine notch and duplicate back tabs.
p,a=load('ear_burst','side',2)
clear(a,103,129,108,129)
poly(a,[(99,131),(103,128),(108,128),(112,130),(112,133),(103,134),(99,133)],0)
poly(a,[(101,131),(104,129),(108,129),(110,130),(110,132),(103,133)],6)
save(p,a,'redrew continuous sloping neck-to-back join, replacing flat cut and tab')
p,a=load('ear_burst','back',2)
for y in [129,131]:
 for x in list(range(79,89))+list(range(103,113)):
  if a[y,x,3] and not a[y-1,x,3] and not a[y+1,x,3]:a[y,x]=0
# Explicit shoulder slope bridges the cut instead of leaving a square step.
poly(a,[(85,131),(89,128),(90,131),(87,134),(85,133)],0)
poly(a,[(87,131),(89,130),(89,132),(87,133)],6)
poly(a,[(103,130),(106,131),(108,133),(106,134),(103,132)],0)
poly(a,[(104,131),(106,132),(106,133),(104,132)],4)
save(p,a,'removed duplicated shoulder tabs and completed tapered shoulder joins')
# Dig crouch: rounded paw/haunch tops and a continuous crouched torso.
p,a=load('dig','front',2)
cap(a,79,89,150,5);cap(a,102,114,150,5)
# Cream throat bridges into the bent forelimbs, retaining the crouch height.
poly(a,[(92,151),(99,151),(101,153),(99,155),(94,155),(92,153)],0)
poly(a,[(93,151),(98,151),(100,153),(98,154),(95,154),(93,153)],10)
save(p,a,'finished square-cut forepaws and short throat/body join')
p,a=load('dig','side',1);cap(a,92,102,131,6);save(p,a,'rounded clipped upper haunch')
p,a=load('dig','side',2)
# Remove a spurious straight one-pixel bridge and rebuild the actual neck/body connection.
clear(a,98,145,111,145)
poly(a,[(97,135),(101,137),(106,139),(111,142),(115,144),(115,147),(109,149),(104,147),(99,144),(97,141)],0)
poly(a,[(98,137),(101,139),(105,141),(110,143),(113,144),(113,146),(109,147),(105,145),(101,143),(98,141)],4)
poly(a,[(98,137),(101,139),(105,141),(109,143),(107,144),(103,142),(99,141)],6)
# Tail/haunch pasted seam is a straight remnant, outside the intended diagonal tail.
clear(a,63,147,78,147)
save(p,a,'redrew crouched torso/neck bridge; removed straight body bar and tail sliver')
p,a=load('dig','back',2)
cap(a,78,88,143,6);cap(a,103,112,143,6)
save(p,a,'rounded square-cut hip tops into crouched back')
# Death front has a truncated ear well above ground and a leftover chin tab.
p,a=load('death','front',1)
clear(a,102,126,105,126)
save(p,a,'removed projecting chin paste remnant')
p,a=load('death','front',4)
# Ear edge had been sliced horizontally at y151. Finish its tapered lower rim.
poly(a,[(115,150),(126,150),(128,151),(125,153),(121,153),(117,152)],0)
poly(a,[(117,150),(125,150),(126,151),(123,152),(121,152)],7)
poly(a,[(118,150),(124,150),(124,151),(121,151)],10)
save(p,a,'finished the chopped lower ear rim above ground')
(OUT/'edits.json').write_text(json.dumps(LOG,indent=2))
print(len(LOG),'frame edits')
boards()
