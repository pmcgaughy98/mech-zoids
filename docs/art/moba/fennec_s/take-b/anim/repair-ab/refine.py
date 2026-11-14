from repair import *
exec((OUT/'apply_repairs.py').read_text().split('# Idle')[0].split('from repair import *')[1])
oldlog=json.loads((OUT/'edits.json').read_text());LOG=[]
for i in range(8):
 p,a=load('walk','back',i)
 clear(a,78,129,87,129);clear(a,106,129,116,129)
 # Rebuild a single contour at the shoulder instead of a horizontal bar.
 a[129,88]=COL[0];a[129,105]=COL[0]
 save(p,a,'trimmed remaining shoulder tabs to one contour texel')
 p,a=load('walk','side',i)
 # Clean the back edge nib at the shoulder cap, keeping connected silhouette.
 lab,k=ndi.label(a[:,:,3]>0,np.ones((3,3)));sz=np.bincount(lab.ravel());sz[0]=0
 for j in range(1,k+1):
  if sz[j]<=2:a[lab==j]=0
 if i in [2,5,6]:
  poly(a,[(89,155),(92,155),(93,156),(95,157),(95,159),(94,160),(88,160),(87,159),(87,157)],0)
  poly(a,[(89,156),(92,156),(92,157),(94,157),(94,158),(88,158),(88,157)],5)
  a[159,88:95]=COL[3];a[157,89:92]=COL[8]
 save(p,a,'finished clipped hind-foot pad; cleaned isolated shoulder nib')
# Blend caps into the adjoining spine rather than leaving roof-shaped paste blocks.
for m,i,x0,x1,y in [('sand_kick',1,86,108,136),('sand_kick',4,83,105,137)]:
 p,a=load(m,'side',i)
 # Curved contour rises gradually toward the neck on the right.
 poly(a,[(x0,y+2),(x0+1,y-1),(x0+4,y-3),(x1-5,y-3),(x1,y-1),(x1,y+2)],0)
 poly(a,[(x0+1,y+2),(x0+2,y),(x0+5,y-2),(x1-5,y-2),(x1-1,y),(x1-1,y+2)],6)
 a[y-1,x0+6:x1-5]=COL[9]
 save(p,a,'finished rounded hip plate instead of long flat paste edge')
p,a=load('ear_burst','side',2)
poly(a,[(99,131),(103,128),(108,127),(112,130),(110,133),(103,134),(99,133)],0)
poly(a,[(101,131),(104,129),(108,128),(110,130),(109,132),(103,133)],4)
poly(a,[(101,131),(105,129),(107,129),(106,131),(103,132)],6)
save(p,a,'shaded sloping neck joint to match adjoining back plate')
p,a=load('dig','side',2);clear(a,63,141,80,149)
# Complete only small join holes, using the neighbouring dark armour ramp.
for x,y,c in [(109,140,2),(110,141,2),(111,141,2),(98,144,4),(98,145,4),(99,145,4),(100,145,2)]:a[y,x]=COL[c]
save(p,a,'removed generated tail wedge and closed body join pinholes')
for m,v,i,c in [('idle','side',1,2),('idle','side',2,2),('idle','side',3,2),('sand_kick','side',3,4),('dig','front',2,7),('dig','back',2,4)]:
 p,a=load(m,v,i);op=a[:,:,3]>0;holes=ndi.binary_fill_holes(op)&~op;a[holes]=COL[c];save(p,a,'closed enclosed paste-join pinholes with neighbouring material')
(OUT/'edits.json').write_text(json.dumps(oldlog+LOG,indent=2))
boards()
