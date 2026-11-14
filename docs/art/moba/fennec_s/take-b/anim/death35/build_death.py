"""Native-pixel death construction. All coordinates refer to 160px approved stills.
No rotations, filtering, image synthesis, or writes outside this directory.
"""
from pathlib import Path
import importlib.util, sys, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, GifImagePlugin
ROOT=Path(r'D:\dev\new-mech-rpg\docs\art\moba')
HERE=Path(__file__).parent
(HERE/'frames').mkdir(exist_ok=True)
D=(20,18,24,255); INK=(33,30,39,255); VS=(46,26,110,255); M=(61,58,68,255)
V=(106,60,200,255); G=(157,155,162,255); L=(164,107,255,255); GO=(184,146,58,255)
S=(214,214,220,255); H=(224,200,255,255); Y=(240,210,122,255); W=(255,244,214,255)
VIEWS=['s','se','e','ne','n']; NAMES=['front','se','side','ne','back']; MS=[300,100,130,140,160,180,1400]
def poly(im,pts,c): ImageDraw.Draw(im).polygon(pts,fill=c)
def line(im,pts,c,w=1): ImageDraw.Draw(im).line(pts,fill=c,width=w)
def maskpoly(pts):
 m=Image.new('1',(160,160));ImageDraw.Draw(m).polygon(pts,fill=1);return np.array(m)
# Hand traced boundaries: source fragments never undergo resampling.
SPECS={
's':dict(ears=[[(60,78),(72,81),(79,91),(76,96),(70,100),(67,107),(60,103),(56,97),(56,87)],[(98,78),(102,88),(102,98),(96,104),(92,107),(88,100),(82,94),(83,88),(89,82)]],head=[(73,93),(85,93),(91,98),(93,105),(90,111),(86,114),(84,116),(75,116),(70,112),(67,107),(68,100)],tail=[],legs=[[(68,122),(77,122),(79,130),(79,140),(68,140)],[(81,122),(91,122),(93,140),(81,140)],[(60,119),(68,119),(70,134),(60,134)],[(91,119),(98,119),(99,134),(91,134)]],hip=(80,123),headcenter=(80,104),cut=116),
'se':dict(ears=[[(76,84),(83,85),(90,91),(91,99),(88,105),(83,111),(77,110),(72,103),(71,96)],[(101,73),(105,76),(106,87),(106,99),(100,100),(94,97),(91,90),(94,81)]],head=[(95,99),(102,99),(106,104),(106,110),(109,112),(108,118),(100,120),(92,117),(87,113),(87,106)],tail=[(51,113),(62,113),(68,116),(73,117),(75,125),(71,131),(64,129),(57,126),(54,121),(51,118)],legs=[[(77,125),(88,125),(90,139),(82,140),(76,134)],[(91,122),(99,122),(99,136),(102,138),(100,140),(91,140)],[(99,120),(104,120),(105,132),(102,136),(99,136)]],hip=(80,127),headcenter=(98,109),cut=119),
'e':dict(ears=[[(90,81),(94,83),(98,91),(100,99),(96,107),(90,113),(86,111),(83,104),(83,96),(85,88)],[(91,73),(94,78),(92,85),(88,92),(86,101),(81,99),(80,92),(83,84)]],head=[(99,94),(105,96),(108,101),(109,105),(115,106),(117,110),(114,113),(106,115),(99,114),(95,111),(95,105)],tail=[(43,136),(47,131),(54,127),(63,123),(68,118),(75,118),(80,125),(79,134),(74,139),(53,140)],legs=[[(78,123),(89,123),(96,128),(95,135),(99,137),(99,140),(81,140)],[(99,119),(104,119),(106,136),(109,137),(109,140),(99,140)],[(106,117),(110,117),(111,128),(109,133),(105,133)]],hip=(84,128),headcenter=(105,105),cut=115),
'ne':dict(ears=[[(81,65),(86,71),(90,77),(92,85),(87,90),(81,92),(75,86),(73,78),(76,72)],[(104,72),(107,77),(107,90),(105,96),(100,100),(94,99),(90,93),(91,83),(97,77)]],head=[(86,83),(91,84),(94,89),(100,91),(107,91),(109,94),(106,98),(100,101),(91,101),(84,98),(79,93),(80,88)],tail=[(51,137),(57,129),(64,123),(68,119),(75,118),(80,122),(79,129),(75,135),(65,139),(55,140)],legs=[[(88,114),(96,114),(100,119),(100,125),(98,129),(88,130),(85,123)],[(100,111),(104,112),(104,119),(107,120),(108,124),(105,127),(101,125)]],hip=(86,121),headcenter=(94,94),cut=102),
'n':dict(ears=[[(62,59),(70,63),(76,70),(79,78),(77,85),(73,91),(66,91),(61,85),(59,77),(59,67)],[(97,59),(100,67),(100,79),(97,86),(91,92),(85,89),(81,82),(83,73),(90,65)]],head=[(76,81),(83,81),(88,87),(91,94),(87,99),(82,102),(75,101),(70,97),(68,92),(72,86)],tail=[(76,119),(84,119),(87,125),(88,134),(84,140),(78,140),(73,135),(72,127)],legs=[[(64,109),(70,109),(71,119),(70,130),(66,133),(61,132),(62,124)],[(89,110),(96,110),(99,121),(99,131),(94,133),(89,129)]],hip=(80,118),headcenter=(80,92),cut=103)
}

def extract(a,sp):
 remain=a[:,:,3]>0; parts={}
 # Head in front of the ears, retaining the exact approved face and eyes.
 for key,pts in [('head',sp['head'])]+[(f'ear{i}',p) for i,p in enumerate(sp['ears'])]+([('tail',sp['tail'])] if sp['tail'] else [])+[(f'leg{i}',p) for i,p in enumerate(sp['legs'])]:
  m=maskpoly(pts)&remain;b=np.zeros_like(a);b[m]=a[m];parts[key]=b;remain &= ~m
 # Assign the fine boundary texels left outside the hand traces to the same
 # anatomical piece, so no old ear contour can survive in the torso.
 headbounds={116:(67,93,97),119:(87,109,102),115:(95,118,100),102:(79,110,88),103:(68,92,88)}
 lo,hi,top=headbounds[sp['cut']]
 floor={116:128,119:132,115:133,102:126,103:128}[sp['cut']]
 ec=[np.argwhere(parts[f'ear{i}'][:,:,3]>0).mean(axis=0) for i in range(2)]
 lc=[np.array(sp['legs'][i])[:,::-1].mean(axis=0) for i in range(len(sp['legs']))]
 for y,x in zip(*np.where(remain)):
  if y<sp['cut']:
   if (sp['cut']==115 and y>=110 and x<=94) or (sp['cut']==119 and y>=112 and x<=88) or (sp['cut']==102 and y>=100) or (sp['cut']==116 and y>=112):continue
   if y>=top and lo<=x<=hi:key='head'
   else:key=f'ear{min(range(2),key=lambda i:abs(x-ec[i][1])+abs(y-ec[i][0]))}'
  elif y>=floor:
   key=f'leg{min(range(len(lc)),key=lambda i:abs(x-lc[i][1]))}'
  else:continue
  parts[key][y,x]=a[y,x];remain[y,x]=False
 b=np.zeros_like(a);b[remain]=a[remain];parts['body']=b
 if sp['cut']==119:
  yy,xx=np.indices((160,160));m=(yy>=118)&(xx<100)&(parts['head'][:,:,3]>0)
  parts['body'][m]=parts['head'][m];parts['head'][m]=0
 return parts

def paste(im,a,dx=0,dy=0,shear=0,pivot=100):
 # Integer row stepping (never a rotation or interpolation).
 dst=np.array(im); ys,xs=np.where(a[:,:,3]>0)
 for y,x in zip(ys,xs):
  xx=int(x+dx+round((int(y)-pivot)*shear));yy=int(y+dy)
  if 0<=xx<160 and 0<=yy<160:dst[yy,xx]=a[y,x]
 im.paste(Image.fromarray(dst))

def leaf(im,base,kind,back=False,scale=1,semi=False):
 # Hand drawn ear silhouettes for successive hinge positions. Local coordinates.
 shapes={
 'left':[(1,2),(-5,2),(-13,-3),(-21,-6),(-25,-4),(-22,-10),(-17,-13),(-10,-11),(-3,-6)],
 'right':[(-1,2),(5,2),(14,-2),(23,-3),(25,0),(22,-7),(17,-11),(9,-10),(2,-5)],
 'leftlow':[(1,1),(-4,4),(-12,5),(-22,3),(-26,5),(-23,0),(-18,-5),(-10,-6),(-3,-4)],
 'rightlow':[(-1,1),(4,5),(13,7),(24,6),(28,7),(25,2),(20,-3),(11,-5),(3,-3)],
 'leftflat':[(1,2),(-5,4),(-14,4),(-25,1),(-29,2),(-25,-3),(-17,-6),(-9,-6),(-2,-3)],
 'rightflat':[(-1,2),(5,4),(14,5),(25,3),(29,4),(25,-2),(17,-5),(9,-5),(2,-2)]}
 pts=shapes[kind];bx,by=base
 def p(q):return [(bx+int(round(x*scale)),by+int(round((y-(max(0,abs(x)-4)//2 if semi else 0))*scale))) for x,y in q]
 poly(im,p(pts),VS)
 # Faceted top cap and lower band follow the silhouette, not a rectangular crop.
 poly(im,p([(0,-1),(-3,-4),(-10,-9),(-17,-11),(-22,-8),(-20,-5),(-12,-3),(-5,0)] if kind=='left' else
             [(0,-1),(3,-4),(9,-8),(17,-9),(22,-5),(20,-2),(13,-1),(5,1)] if kind=='right' else
             [(0,0),(-4,-3),(-10,-5),(-18,-4),(-23,-1),(-20,1),(-12,2),(-5,2)] if kind in ['leftlow','leftflat'] else
             [(0,0),(4,-2),(11,-4),(18,-2),(24,1),(22,3),(14,3),(5,2)]),L)
 if back:
  poly(im,p([(-3,-3),(-10,-8),(-17,-10),(-22,-7),(-17,-6),(-10,-5)] if kind=='left' else
                [(3,-3),(10,-7),(17,-8),(22,-5),(17,-4),(10,-4)] if kind=='right' else
                [(-4,-3),(-11,-5),(-18,-4),(-23,-1),(-17,-1),(-11,-2)] if kind in ['leftlow','leftflat'] else
                [(4,-2),(11,-4),(18,-2),(23,0),(18,0),(11,-1)]),H)
  line(im,p([(-22,-2),(-14,2),(-6,2),(0,0)] if kind.startswith('left') else [(0,0),(6,3),(15,5),(23,3)]),V,2)
 else:
  poly(im,p([(-3,-2),(-10,-5),(-18,-8),(-22,-6),(-17,-3),(-9,0),(-4,1)] if kind=='left' else
                [(3,-2),(10,-5),(18,-7),(22,-3),(16,-2),(9,0),(4,1)] if kind=='right' else
                [(-3,0),(-10,-2),(-18,-2),(-24,0),(-18,2),(-11,3),(-5,2)] if kind.startswith('left') else
                [(3,0),(10,-1),(18,0),(24,3),(18,4),(11,4),(5,2)]),Y)
  line(im,p([(-4,1),(-11,3),(-18,2)] if kind.startswith('left') else [(4,2),(11,4),(18,4)]),GO)
  line(im,p([(-17,-8),(-21,-7)] if kind=='left' else [(16,-8),(20,-5)] if kind=='right' else [(-18,-4),(-23,-1)] if kind.startswith('left') else [(17,-3),(22,0)]),H)

def belly(im,cx,cy,view,phase):
 # Newly exposed ventral plates: hand drawn stepped outline and shaded bands.
 w=14 if view in ['s','n'] else 18;h=10
 poly(im,[(cx-w,cy-3),(cx-w+3,cy-8),(cx-4,cy-11),(cx+8,cy-8),(cx+w,cy-2),(cx+w-1,cy+7),(cx+9,cy+10),(cx-6,cy+9),(cx-w,cy+4)],INK)
 poly(im,[(cx-w+2,cy-3),(cx-w+5,cy-7),(cx-3,cy-8),(cx+8,cy-6),(cx+w-2,cy),(cx+w-3,cy+5),(cx+7,cy+7),(cx-6,cy+6),(cx-w+2,cy+2)],VS)
 poly(im,[(cx-w+4,cy-4),(cx-3,cy-7),(cx+7,cy-5),(cx+12,cy-1),(cx+8,cy+2),(cx-4,cy+1)],V)
 poly(im,[(cx-w+6,cy-5),(cx-3,cy-7),(cx+6,cy-5),(cx+7,cy-3),(cx-5,cy-2)],L)
 line(im,[(cx-4,cy+2),(cx+1,cy+6),(cx+8,cy+7)],INK)
 line(im,[(cx+7,cy-3),(cx+11,cy),(cx+11,cy+3)],M,2)

def joint(im,x,y):
 poly(im,[(x-4,y-3),(x,y-5),(x+4,y-3),(x+5,y+2),(x+2,y+5),(x-3,y+4),(x-5,y)],VS)
 poly(im,[(x-3,y-2),(x,y-3),(x+3,y-2),(x+3,y+2),(x,y+3),(x-3,y+1)],G)
 line(im,[(x-2,y-2),(x+1,y-2),(x+2,y-1)],S)
 line(im,[(x-4,y+2),(x-2,y+4),(x+2,y+4)],INK)

def limb(im,a,b,near=True):
 # Folded limb, redesigned joint transition, no abrupt source-part cuts.
 x,y=a;u,v=b
 poly(im,[(x-3,y-3),(x+3,y-3),(u+3,v-2),(u+4,v+2),(u+1,v+4),(u-4,v+3),(x-4,y+2)],VS)
 line(im,[(x,y-2),(u,v)],L if near else V,3)
 poly(im,[(u-4,v),(u+2,v-1),(u+5,v+2),(u+5,v+4),(u-3,v+4),(u-5,v+2)],M)
 line(im,[(u-3,v),(u+1,v),(u+3,v+1)],G,2)
 line(im,[(u-3,v+4),(u+4,v+4)],INK)

# Translation paths. Head drop, front buckle, rear sag, then right-side roll.
HEAD={
's':[(0,0),(0,-2),(0,4),(-2,10),(-7,18),(-20,24),(-20,24)],
'se':[(0,0),(-1,-1),(0,4),(0,9),(-3,16),(-6,20),(-6,20)],
'e':[(0,0),(-2,-1),(-1,4),(0,10),(1,17),(1,23),(1,23)],
'ne':[(0,0),(-1,1),(0,4),(2,9),(5,16),(10,23),(10,23)],
'n':[(0,0),(0,2),(0,5),(2,10),(11,20),(22,27),(22,27)]}
BODY={
's':[(0,0),(0,-1),(0,1),(-1,4),(-4,7),(-6,10),(-6,10)],
'se':[(0,0),(-1,0),(0,1),(0,3),(-2,6),(-3,8),(-3,8)],
'e':[(0,0),(-1,0),(0,1),(0,3),(0,6),(0,8),(0,8)],
'ne':[(0,0),(-1,0),(0,1),(1,3),(3,6),(5,9),(5,9)],
'n':[(0,0),(0,1),(0,2),(1,4),(4,8),(7,11),(7,11)]}

def pose(view,f,parts,src):
 if f==0:return Image.fromarray(src)
 if f==1:
  # One rigid native-pixel recoil; the ear tips flick at the hinge in 1px steps.
  # No joints are cut in the hit pose.
  dx,dy={'s':(0,-2),'se':(-1,-1),'e':(-2,0),'ne':(-1,1),'n':(0,1)}[view]
  threshold={'s':93,'se':96,'e':96,'ne':85,'n':82}[view]
  a=np.zeros_like(src)
  for y,x in zip(*np.where(src[:,:,3]>0)):
   flick=round(max(0,threshold-int(y))*.065)
   sign=(-1 if x<80 else 1) if view in ['s','n'] else -1
   a[y+(0 if (view=='n' and y>=130) or (view=='ne' and y>=138) else dy),x+dx+sign*flick]=src[y,x]
  return Image.fromarray(a)
 sp=SPECS[view];im=Image.new('RGBA',(160,160));hdx,hdy=HEAD[view][f];bdx,bdy=BODY[view][f]
 hc=sp['headcenter'];hx,hy=hc[0]+hdx,hc[1]+hdy
 # Neck connector must be a continuous shaped bridge under head and torso.
 if f<=3:
  x0,y0=sp['headcenter']; nc=(x0+bdx,y0+(13 if view in ['s','se','e'] else 11)+bdy)
 else:nc=(sp['hip'][0]+bdx,sp['hip'][1]+min(bdy,7)-3)
 poly(im,[(nc[0]-5,nc[1]-4),(nc[0]+5,nc[1]-3),(hx+5,hy+7),(hx+2,hy+(12 if f<4 else 10)),(hx-5,hy+10),(nc[0]-6,nc[1]+3)],VS)
 line(im,[(nc[0]-3,nc[1]-3),(hx-2,hy+7)],V,4)
 # Tail first; its base stays close to the original support polygon.
 if 'tail' in parts:
  if f<=3:paste(im,parts['tail'],0,0)
  elif view=='n':
   paste(im,parts['tail'],5 if f==4 else 8,-1, .25 if f>=5 else .1,128)
  elif view=='se':paste(im,parts['tail'],-1,3 if f==4 else 6,-.12,125)
  elif view=='ne':paste(im,parts['tail'],2,-2 if f==4 else -4,.18,128)
  else:paste(im,parts['tail'],0,-1)
 if f<=2:
  paste(im,parts['body'],bdx,bdy)
  for k in parts:
   if k.startswith('leg'):paste(im,parts[k])
 elif f==3:
  # Underpainting at the chest-to-upper-leg hinge, then original plates.
  cx,cy=sp['hip']
  paste(im,parts['body'],bdx,bdy)
  for i,k in enumerate(k for k in parts if k.startswith('leg')):
   a=parts[k].copy();y,x=np.where(a[:,:,3]>0)
   # Crouched leg translated intact; original foot remains the planted contact.
   paste(im,a,(-1 if view=='s' else 1) if i==1 else 0,0)
  if view in ['se','e','ne']:
   limb(im,(102+bdx,123),(106,135 if view!='ne' else 126))
 else:
  cx,cy=sp['hip'];cx+=bdx;cy=min(130,cy+min(bdy,7))
  # Far limbs are drawn before the flank, visible only at their folded ends.
  if view=='s':
   limb(im,(cx+3,cy-2),(cx+19,cy+1),False);limb(im,(cx+4,cy+4),(cx+17,136),False)
  elif view=='n':
   limb(im,(cx-2,cy),(cx-18,cy+3),False);limb(im,(cx-1,cy+6),(cx-15,136),False)
  else:
   limb(im,(cx+7,cy-4),(cx+20,cy-1),False);limb(im,(cx-2,cy+2),(cx+5,cy+5),False)
  belly(im,cx,cy,view,f)
  # Transfer the dorsal/haunch armour, with hand traced narrow crop masks.
  body=parts['body'].copy()
  yy,xx=np.indices((160,160))
  if view=='s':keep=(yy>=116)&(yy<=124)&(xx<76)
  elif view=='n':keep=(yy>=104)&(yy<=119)&(xx>=70)&(xx<=89)
  elif view=='se':keep=(yy>=113)&(yy<=127)&(xx<87)
  elif view=='e':keep=(yy>=110)&(yy<=126)&(xx<96)
  else:keep=(yy>=102)&(yy<=117)&(xx<96)
  body[~keep]=0
  paste(im,body,bdx, min(bdy,7),(.14 if view=='n' else -.12 if view=='s' else .15),sp['hip'][1])
  # Hand-redrawn seams run around, and into, those native plates.
  if view=='s':
   joint(im,cx+5,cy+1);limb(im,(cx+6,cy+3),(cx+15,136))
   if f>=5:
    # Tail newly revealed behind the rolled seated body.
    poly(im,[(cx+7,cy-5),(cx+16,cy-10),(cx+21,cy-9),(cx+19,cy-4),(cx+12,cy)],VS)
    poly(im,[(cx+9,cy-6),(cx+16,cy-9),(cx+19,cy-8),(cx+16,cy-5)],L)
    poly(im,[(cx+19,cy-9),(cx+25,cy-11),(cx+23,cy-6),(cx+19,cy-4)],Y)
    line(im,[(cx+20,cy-9),(cx+24,cy-10)],W)
  elif view=='n':joint(im,cx-6,cy+2);limb(im,(cx-8,cy+4),(cx-18,cy+7))
  else:
   joint(im,cx-1,cy+1);limb(im,(cx+7,cy+1),(cx+17,cy+5))
  # Native joint rings and the surrounding violet armour, translated intact.
  disc_trace={
   's':[(63,116),(67,114),(70,117),(71,122),(68,126),(64,125),(62,122)],
   'se':[(78,123),(83,122),(87,125),(89,130),(86,134),(81,135),(77,131)],
   'e':[(81,122),(87,121),(93,124),(96,128),(93,133),(87,135),(81,132),(78,127)],
   'ne':[(90,114),(94,114),(98,117),(99,121),(96,125),(90,126),(86,122),(87,118)],
   'n':[(64,111),(67,110),(70,113),(71,118),(68,122),(64,121),(62,117)]}
  disc=np.zeros_like(src);dm=maskpoly(disc_trace[view])&(src[:,:,3]>0);disc[dm]=src[dm]
  dd={'s':(5,9),'se':(-1,3),'e':(0,2),'ne':(4,5),'n':(5,8)}[view]
  paste(im,disc,dd[0],dd[1])
  # Gold chest peeks around the folded front shoulder, using original colours.
  if view in ['s','se','e'] and f==4:
   poly(im,[(hx-3,hy+6),(hx+4,hy+4),(hx+7,min(138,hy+8)),(hx+5,min(139,hy+14)),(hx-1,min(140,hy+13)),(hx-5,min(139,hy+9))],GO)
   poly(im,[(hx-3,hy+6),(hx+3,hy+5),(hx+5,hy+8),(hx+2,min(139,hy+11)),(hx-2,min(139,hy+10))],Y)
 # Hit-frame repair: keep native shoulder-to-tail transitions continuous.
 if f==1 and view in ['se','e','s']:
  a=np.array(im);yy,xx=np.indices((160,160))
  zone=((yy>=112)&(xx<=88)&(yy<=134) if view=='se' else
        (yy>=110)&(xx<=95)&(yy<=134) if view=='e' else (yy>=116)&(yy<=134))
  a[zone]=src[zone];im=Image.fromarray(a)
 # Ears behind the transferred face, manually posed from f2 onwards.
 if f==1:
  for i in range(2):paste(im,parts[f'ear{i}'],hdx+(-1 if i==0 else 1),hdy-1,(-.08 if i==0 else .08),100)
 else:
  back=view in ['ne','n'];drop=f>=4
  if view=='s':
   leaf(im,(hx-8 if f<5 else hx-6,hy-6 if f<5 else hy+1), 'left' if f==2 else 'leftlow' if f<5 else 'leftflat',False,1.05,semi=f==2)
   leaf(im,(hx+7 if f<5 else hx+5,hy-7 if f<5 else hy-10),'right' if f<=3 else 'rightlow' if f==4 else 'rightflat',False,1.05,semi=f==2)
  elif view=='n':
   leaf(im,(hx-6,hy-6 if f<4 else hy-9),'left' if f<=3 else 'leftlow' if f==4 else 'leftflat',True,1.05,semi=f==2)
   leaf(im,(hx+7 if f<5 else hx+5,hy-4 if f<4 else hy+1 if f==4 else hy+6),'right' if f==2 else 'rightlow' if f<5 else 'rightflat',True,1.05,semi=f==2)
  elif view=='e':
   leaf(im,(hx-7,hy-9),'left' if f<=3 else 'leftlow' if f==4 else 'leftflat',True,1.05,semi=f==2)
   leaf(im,(hx-10,hy-4),'left' if f==2 else 'leftlow' if f<5 else 'leftflat',False,1.1,semi=f==2)
  elif view=='se':
   leaf(im,(hx+1,hy-9),'right' if f<=3 else 'rightlow' if f==4 else 'rightflat',False,.95,semi=f==2)
   leaf(im,(hx-9,hy-4),'left' if f==2 else 'leftlow' if f<5 else 'leftflat',False,1.05,semi=f==2)
  else:
   leaf(im,(hx-7,hy-9),'left' if f<=3 else 'leftlow' if f==4 else 'leftflat',True,1.05,semi=f==2)
   leaf(im,(hx+4,hy-4),'right' if f==2 else 'rightlow' if f<5 else 'rightflat',True,1.05,semi=f==2)
 # Integer stepped head lean during the roll. Every source face pixel stays whole.
 sh=0 if f<=2 else (.12 if view=='s' else -.12 if view=='n' else .08) if f==3 else (.4 if view=='s' else -.4 if view=='n' else .12)
 paste(im,parts['head'],hdx,hdy,sh,sp['headcenter'][1])
 if f>=2:
  # Draw the cheek/ear hinge over the native fragment edge.
  line(im,[(hx-7,hy-3),(hx-5,hy-5),(hx-3,hy-5)],V)
 if f==6:
  a=np.array(im);eye=np.isin(a[:,:,0],[63,200,246]) & ((a[:,:,1]==232)|(a[:,:,1]==255)) & (a[:,:,3]>0)
  a[eye]=VS
  im=Image.fromarray(a)
 return im

def clean(im,src,f):
 a=np.array(im);op=a[:,:,3]>0
 # Fill enclosed pinholes with their local, existing material colour.
 from scipy.ndimage import binary_fill_holes,label
 holes=binary_fill_holes(op)&~op
 for y,x in zip(*np.where(holes)):
  ns=[tuple(a[yy,xx]) for yy,xx in [(y-1,x),(y,x-1),(y+1,x),(y,x+1)] if a[yy,xx,3]]
  a[y,x]=max(set(ns),key=ns.count) if ns else VS
 if f:
  lab,n=label(a[:,:,3]>0,structure=np.ones((3,3)))
  sizes=np.bincount(lab.ravel());sizes[0]=0
  for i in range(1,n+1):
   if sizes[i]<5:a[lab==i]=0
 return Image.fromarray(a)

spec=importlib.util.spec_from_file_location('game_selout',ROOT/'rhino_l/take-a/anim/selout_rhino.py');sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel);sel.OUTLINE=np.array([20,18,24],np.uint8)
allframes={}
for v,n in zip(VIEWS,NAMES):
 src=np.array(Image.open(ROOT/'fennec_s/take-b/views_cam35_touchup'/f'{v}.png').convert('RGBA'))
 parts=extract(src,SPECS[v]);frames=[]
 for f in range(7):
  im=pose(v,f,parts,src)
  if f:im=clean(im,src,f)
  im.save(HERE/'frames'/f'{n}_f{f}.png');frames.append(im)
 allframes[v]=frames
# Review, full-canvas, 4x nearest with requested exact game sel-out.
board=Image.new('RGB',(8*640,5*668),(86,93,84));dr=ImageDraw.Draw(board)
for j,(v,n) in enumerate(zip(VIEWS,NAMES)):
 still=Image.open(ROOT/'fennec_s/take-b/views_cam35_touchup'/f'{v}.png').convert('RGBA')
 for col,im in enumerate([still]+allframes[v]):
  b=Image.fromarray(sel.selout(np.array(im))[0]).resize((640,640),Image.Resampling.NEAREST)
  x=col*640;y=j*668;board.paste(b,(x,y+28),b);dr.text((x+8,y+7),f'{n}: '+('approved still' if col==0 else f'f{col-1} {MS[col-1]}ms'),fill=(244,244,234))
 board.crop((0,j*668,5120,(j+1)*668)).save(HERE/f'board_{n}.png')
board.save(HERE/'board.png')
# GIF palette is shared across all frames; omit NETSCAPE loop extension (one play).
for v,n in zip(VIEWS,NAMES):
 gifs=[]
 for im in allframes[v]:
  b=Image.new('RGB',(640,640),(86,93,84));o=Image.fromarray(sel.selout(np.array(im))[0]).resize((640,640),Image.Resampling.NEAREST);b.paste(o,(0,0),o);gifs.append(b)
 palette=gifs[0].quantize(colors=64)
 gifs=[b.quantize(palette=palette,dither=Image.Dither.NONE) for b in gifs]
 with (HERE/f'preview_{n}.gif').open('wb') as fp:
  for chunk in GifImagePlugin._get_global_header(gifs[0],{'duration':MS[0]}):fp.write(chunk)
  for gif,ms in zip(gifs,MS):GifImagePlugin._write_frame_data(fp,gif,(0,0),{'duration':ms,'disposal':2})
  fp.write(b';')
print('Built 35 raw frames and review artifacts.')

