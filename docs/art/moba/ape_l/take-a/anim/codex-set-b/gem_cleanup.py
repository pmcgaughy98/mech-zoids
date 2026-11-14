"""Remove dark pinholes inside gem faces, preserving bezel and native highlights."""
from finish import *
from scipy.spatial import ConvexHull
log=[]
for name,N in COUNTS.items():
 for n in NAMES:
  for c in range(1,N-(1 if name in ['bound','hex_dome'] else 0)):
   p=ROOT/name/'frames'/f'{n}_f{c}.png';a=np.array(Image.open(p));g=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,2]>70)&(a[:,:,3]>0);lab,k=ndi.label(g)
   fixed=0
   for j in range(1,k+1):
    y,x=np.where(lab==j)
    if len(x)<35:continue
    pts=np.column_stack([x,y]);hull=ConvexHull(pts);mask=Image.new('1',(192,192));ImageDraw.Draw(mask).polygon([tuple(map(int,p)) for p in pts[hull.vertices]],fill=1)
    inside=np.array(mask,dtype=bool)&(a[:,:,3]>0)
    # The still's gem face has green facets and pale highlights, no ink flecks.
    dark=inside&(a[:,:,:3].max(2)<160)&~g
    fixed+=int(dark.sum());a[dark,:3]=(63,224,127)
   Image.fromarray(a).save(p);log.append(f'{name}/{n}_f{c}: {fixed} internal gem ink flecks repaired')
(ROOT/'gem_cleanup_log.txt').write_text('\n'.join(log)+'\n')
print('Gem face pinholes repaired')
