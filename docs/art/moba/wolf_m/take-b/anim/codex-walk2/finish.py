"""Native pixel finishing; generated upper drawings, hand-authored joined leg/tail contours. No still pixels copied."""
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,math,importlib.util
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
P=[tuple(bytes.fromhex(x))+(255,) for x in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()]
targets=json.loads((R/'targets.json').read_text());paths=targets['paths'];paws=targets['still_paws']
(R/'walk/layers').mkdir(exist_ok=True)
def polygon(d,pts,c):d.polygon([(round(x),round(y)) for x,y in pts],fill=P[c])
def line(d,pts,c,w=1):d.line([(round(x),round(y)) for x,y in pts],fill=P[c],width=w)
def ik(root,end,l1,l2):
 r=np.array(root,float);e=np.array(end,float);v=e-r;dist=np.linalg.norm(v);u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);h=math.sqrt(max(0,l1*l1-along*along));perp=np.array([-u[1],u[0]]);return tuple(r+u*along+perp*h)
def band(d,a,b,width,c):
 a=np.array(a);b=np.array(b);v=b-a;n=np.array([-v[1],v[0]])/np.linalg.norm(v)*width/2;polygon(d,[a+n,b+n,b-n,a-n],c)
def leg(name,f):
 near=name.startswith('near');fore=name.endswith('fore');pair=paws[name]['pair'];off,lift=paths[pair][f];cx=paws[name]['x']+off;by=160-lift;dip=int(f in [1,5]);root=(115 if near else 120,123+dip) if fore else (80 if near else 85,122+dip)
 # Full polygon redraw from the rotating shoulder/hip to the sole.
 wrist=(cx-3,by-5) if fore else (cx,by-4)
 if fore and lift==4:wrist=(cx+1,by-6)
 lengths=(19.25,16) if fore else (21.5,17.5)
 joint=ik(root,wrist,*lengths)
 # Choose native joint pixels with the complete shoulder-to-sole chain in tolerance.
 j0=np.rint(joint).astype(int);candidates=[]
 for dx in [-1,0,1]:
  for dy in [-1,0,1]:
   j=(int(j0[0]+dx),int(j0[1]+dy));l1=math.dist(root,j);l2=math.dist(j,wrist)
   chain=l1+l2+math.dist(wrist,(cx,by))+1
   segment_ref=(19.235,17.263) if fore else (21.095,17.029)
   if abs(chain-(41.10 if fore else 42.73))<=2 and abs(l1-segment_ref[0])<=2 and abs(l2-segment_ref[1])<=2:
    candidates.append(((l1-lengths[0])**2+(l2-lengths[1])**2,j))
 assert candidates,(name,f)
 joint=min(candidates)[1];jx,jy=joint;rx,ry=root;wx,wy=wrist
 im=Image.new('RGBA',(192,192));d=ImageDraw.Draw(im)
 # upper armour follows both hip and knee, overlaps torso at its root.
 if fore:
  outer=[(rx-5,ry-7),(rx+3,ry-6),(rx+7,ry+2),(rx+6,ry+9),(jx+4,jy-1),(jx+3,jy+3),(jx-4,jy+2),(jx-5,jy-4),(rx-9,ry+5)]
  polygon(d,outer,0)
  polygon(d,[(rx-5,ry-6),(rx+2,ry-5),(rx+5,ry+2),(rx+4,ry+9),(jx+2,jy),(jx+1,jy+2),(jx-3,jy),(jx-3,jy-5),(rx-7,ry+5)],4 if near else 1)
  if near:
   polygon(d,[(rx-5,ry-6),(rx,ry-5),(rx+3,ry+1),(rx+3,ry+7),(jx,jy-4),(jx-3,jy-3),(rx-6,ry+5)],6)
   line(d,[(rx-5,ry-5),(rx-3,ry-5),(rx+1,ry+1)],9)
  else:line(d,[(rx,ry-4),(rx+3,ry+2),(jx+2,jy-2)],4,2)
 else:
  polygon(d,[(rx-5,ry-7),(rx+4,ry-6),(rx+7,ry+2),(rx+4,ry+10),(jx+4,jy),(jx+1,jy+4),(jx-4,jy+2),(jx-5,jy-3),(rx-6,ry+4)],0)
  polygon(d,[(rx-4,ry-6),(rx+3,ry-5),(rx+5,ry+2),(rx+2,ry+10),(jx+2,jy),(jx,jy+2),(jx-3,jy),(jx-3,jy-3),(rx-5,ry+3)],4 if near else 1)
  if near:
   polygon(d,[(rx-4,ry-5),(rx+1,ry-5),(rx+3,ry+1),(rx,ry+8),(jx,jy-2),(jx-3,jy-1),(rx-4,ry+3)],6)
   line(d,[(rx-4,ry-5),(rx,ry-5)],9)
  else:line(d,[(rx+2,ry-4),(rx+3,ry+2),(jx+1,jy-1)],4,2)
 # Long lower red segment, seven pixels near and six far, dark inside edge.
 width=6 if near else 5
 band(d,joint,wrist,width+1,0);band(d,(jx-.5,jy),(wx-.5,wy),width-1,3 if near else 2)
 band(d,(jx-1.2,jy),(wx-1.2,wy),2,5 if near else 3)
 line(d,[(jx-2,jy),(jx-2,jy+4)],7 if near else 5)
 # articulated knee guard, attached to upper and shank.
 polygon(d,[(jx-3,jy-4),(jx-1,jy-5),(jx+3,jy-2),(jx+3,jy+2),(jx,jy+4),(jx-3,jy+1)],3 if near else 2)
 polygon(d,[(jx-3,jy-4),(jx-1,jy-4),(jx+1,jy-1),(jx-1,jy+2),(jx-3,jy+1)],5 if near else 3)
 if near:line(d,[(jx-3,jy-3),(jx-2,jy-1)],7)
 # Sole contact center is cx. Constant sole width gives a true locked footprint.
 # Lift-four frames fold at the wrist; reach frames extend the toe again.
 polygon(d,[(wx-3,wy-1),(wx+2,wy-1),(wx+3,by-4),(cx+3,by-4),(cx+5,by-2),(cx+5,by),(cx-5,by),(cx-6,by-2),(wx-3,by-3)],0)
 polygon(d,[(wx-2,wy),(wx+1,wy),(wx+2,by-3),(cx+2,by-3),(cx+4,by-1),(cx-4,by-1),(cx-4,by-2)],3 if near else 2)
 polygon(d,[(wx-2,wy),(wx,wy),(wx+1,by-2),(cx+1,by-1),(cx-3,by-1)],5 if near else 3)
 if near:
  line(d,[(wx-2,wy+1),(wx-1,wy+2)],7)
  line(d,[(cx+2,by-3),(cx+3,by-2)],5)
 line(d,[(cx,by-2),(cx,by-1)],2)
 # Flat complete dark sole, center fixed irrespective of toe articulation.
 line(d,[(cx-5,by),(cx+5,by)],0)
 return im,dict(name=name,frame=f,offset=off,lift=lift,target=[cx,by],root=list(root),joint=[round(jx,3),round(jy,3)],wrist=list(wrist),lengths=[round(math.dist(root,joint),3),round(math.dist(joint,wrist),3)],sole=[cx-5,cx+5,by])
def tail(f):
 im=Image.new('RGBA',(192,192));d=ImageDraw.Draw(im)
 # Four broad straight plates, explicit native contours rather than a pasted still.
 sway=[0,1,1,0,0,-1,-1,0][f];dip=int(f in [1,5])
 def tp(pts):return [(x+sway,y+dip) for x,y in pts]
 def poly(pts,c):polygon(d,tp(pts),c)
 poly([(68,119),(70,123),(64,130),(61,135),(58,141),(54,146),(47,153),(42,156),(41,152),(42,143),(46,135),(51,128),(57,123),(63,121)],0)
 poly([(67,120),(69,123),(62,130),(56,134),(50,134),(53,129),(58,125),(63,123)],4)
 poly([(63,123),(67,121),(65,124),(59,128),(54,130),(51,133),(52,129),(57,126)],6)
 poly([(62,124),(65,122),(62,125),(57,128),(54,128)],9)
 poly([(62,131),(60,136),(56,142),(49,143),(46,140),(48,135),(52,132),(55,132),(58,131)],4)
 poly([(57,132),(59,132),(55,137),(51,139),(47,140),(49,136),(52,134)],6)
 poly([(51,134),(54,133),(51,136),(48,137)],9)
 poly([(55,143),(52,147),(48,152),(43,152),(42,149),(43,143),(46,140),(49,142)],4)
 poly([(46,141),(49,142),(47,146),(44,148),(43,147),(44,143)],6)
 # Terminal red tip, same broad base and tapered point as the still.
 poly([(44,142),(48,144),(46,149),(43,154),(42,156),(41,152),(42,146)],2)
 poly([(43,143),(46,144),(45,148),(42,153),(42,148)],3)
 poly([(43,144),(45,144),(44,147),(42,150)],5)
 # Native outer-contour correction: retain the still's tapered lower plate width.
 ar=np.array(im)
 limits={140:55,141:55,142:55,143:54,144:54,145:53,146:52,147:50,148:48,149:47,150:46,151:45,152:44,153:44,154:43,155:42,156:42}
 for y,limit in limits.items():
  row=y+dip;edge=limit+sway
  ar[row,edge+1:]=0
  if ar[row,edge,3]:ar[row,edge]=P[0]
 im=Image.fromarray(ar)
 return im

def body(f):
 # Use the complete generated cell4 upper drawing throughout to remove identity flicker.
 # This is generated paint, never the approved still or a pasted reference part.
 a=np.array(Image.open(R/'walk/underpaint/side_f4.png').convert('RGBA'));yy,xx=np.indices((192,192));sy=yy.astype(float)
 # Align generated head landmarks and shorten overlong generated fang tips.
 eyes=np.argwhere(np.all(a[:,:,:3]==P[8][:3],2));ey=eyes[:,0].mean();off=111.5-ey
 fang=np.argwhere((xx>=140)&(yy>=119)&(a[:,:,3]>0));fb=fang[:,0].max()
 headshift=np.where(yy<=112,off,np.where(yy<=119,off*(119-yy)/7,-(yy-119)*(fb-128)/max(1,fb-119)))
 sy=yy-headshift*np.clip((xx-117)/12,0,1)
 # Level back; abdomen contour rises by 2px without moving the top.
 sy+=np.clip((yy-117)/12,0,1)*2*np.clip((120-xx)/12,0,1)
 sy=np.rint(sy).astype(int);valid=(sy>=0)&(sy<192);b=np.zeros_like(a);b[valid]=a[sy[valid],xx[valid]]
 # Remove all generated legs and the generated tail before complete native redraw.
 # Curved lower torso clipping ends inside the fully redrawn joint plates.
 boundary=np.interp(xx,[0,64,70,78,86,91,100,107,115,122,129,135,191],[118,118,125,129,129,126,129,131,132,129,123,130,130])
 keep=(yy<=boundary)&~((xx<70)&(yy>=119));b[~keep]=0
 # One-pixel torso dip, head remains steady via a continuous neck blend.
 dip=int(f in [1,5]);out=np.zeros_like(b)
 for y,x in zip(*np.where(b[:,:,3]>0)):
  dy=round(dip*np.clip((130-x)/12,0,1));out[y+dy,x]=b[y,x]
 return Image.fromarray(out)
records=[]
for f in range(8):
 b=body(f);canvas=Image.new('RGBA',(192,192));layers={}
 for name in paws:
  layers[name],rec=leg(name,f);records.append(rec);layers[name].save(R/'walk/layers'/f'{name}_f{f}.png')
 # Far limbs occluded by torso and near limbs, exactly as a profile drawing.
 for name in ['far_hind','far_fore']:canvas.alpha_composite(layers[name])
 canvas.alpha_composite(tail(f));canvas.alpha_composite(b)
 for name in ['near_hind','near_fore']:canvas.alpha_composite(layers[name])
 a=np.array(canvas);m=a[:,:,3]>0
 # Native closed-contour repair of enclosed pinholes, no growth below ground.
 holes=ndi.binary_fill_holes(m)&~m
 inds=ndi.distance_transform_edt(~m,return_distances=False,return_indices=True);a[holes]=a[inds[0][holes],inds[1][holes]]
 m=a[:,:,3]>0;l,n=ndi.label(m,np.ones((3,3)));sz=np.bincount(l.ravel());sz[0]=0;a[(l>0)&(sz[l]<4)]=0;a[161:]=0
 Image.fromarray(a).save(R/'walk/frames'/f'side_f{f}.png')
json.dump(records,open(R/'articulation.json','w'),indent=2)
# Plain native board for review.
board=Image.new('RGBA',(8*512,360),(80,88,84,255))
for f in range(8):board.alpha_composite(Image.open(R/'walk/frames'/f'side_f{f}.png').crop((32,88,160,178)).resize((512,360),Image.Resampling.NEAREST),(f*512,0))
board.convert('RGB').save(R/'finish_board.png')
