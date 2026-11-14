"""Native-resolution repaint over the two generated underdrawings.
No reference image is cropped, sampled, masked or composited into a posed frame.
The approved still is read only by approved() for the four required endpoints.
All contours below are explicitly drawn in native pixels; only the generated torso
interior survives where it fits the corrected contour. No transformed part patches.
"""
from finish import *
C=[tuple(c)+(255,) for c in PAL.tolist()]
class Pen:
 def __init__(self,im,dx=0,dy=0):self.d=ImageDraw.Draw(im);self.dx=16+dx;self.dy=20+dy
 def p(self,pts,c):self.d.polygon([(x+self.dx,y+self.dy) for x,y in pts],fill=C[c])
 def l(self,pts,c,w=1):self.d.line([(x+self.dx,y+self.dy) for x,y in pts],fill=C[c],width=w)
 def r(self,box,c):x,y,z,t=box;self.d.rectangle((x+self.dx,y+self.dy,z+self.dx,t+self.dy),fill=C[c])

def back_head(im,dy):
 p=Pen(im,0,dy)
 # Ear backs: full taper, dark underside, stepped bright rim.
 p.p([(63,64),(65,64),(65,66),(68,69),(68,70),(71,73),(71,74),(74,77),(75,80),(76,84),(76,89),(74,94),(71,98),(70,101),(67,100),(64,97),(62,94),(60,91),(59,88),(58,85),(58,78),(59,73),(61,70),(61,67),(62,67)],1)
 p.p([(63,67),(65,67),(69,71),(69,73),(73,77),(74,81),(75,86),(74,91),(71,96),(68,96),(64,92),(61,88),(59,84),(59,77),(61,72)],4)
 p.p([(63,67),(66,69),(71,75),(73,79),(74,84),(74,86),(71,85),(67,84),(63,82),(61,79),(61,73)],6)
 p.p([(63,64),(64,64),(64,67),(67,70),(68,70),(68,72),(71,74),(71,76),(73,78),(73,80),(70,78),(67,76),(66,73),(64,72),(63,69)],9)
 p.p([(95,64),(97,67),(98,71),(100,74),(101,78),(101,86),(100,91),(98,94),(96,98),(93,101),(90,101),(87,96),(84,91),(83,86),(84,80),(86,76),(88,73),(91,69),(93,66)],1)
 p.p([(95,67),(97,71),(99,76),(100,81),(100,86),(98,91),(95,96),(92,97),(88,93),(85,88),(84,84),(86,78),(88,75),(91,72)],4)
 p.p([(95,68),(97,73),(98,78),(99,82),(98,84),(95,84),(91,86),(86,87),(85,84),(87,78),(90,75),(93,72)],6)
 p.p([(95,64),(95,67),(93,68),(93,70),(91,71),(91,73),(89,74),(89,76),(87,78),(86,80),(89,79),(91,77),(92,75),(95,73),(96,70)],9)
 # Low rear head plate and uninterrupted collar.
 p.p([(75,88),(84,88),(86,91),(88,94),(90,98),(91,101),(88,103),(70,103),(68,101),(70,96),(72,93)],1)
 p.p([(75,89),(83,89),(86,93),(88,97),(88,99),(71,99),(72,95)],6)
 p.p([(71,99),(88,99),(87,101),(72,102),(70,101)],4)
 p.r((76,91,76,92),9);p.r((77,92,78,92),9)
 p.p([(74,104),(85,104),(87,107),(73,107)],3);p.r((75,104,84,104),1)

def ne_head(im,dy):
 p=Pen(im,0,dy)
 p.p([(79,67),(81,67),(83,70),(85,73),(87,76),(89,79),(90,84),(90,90),(89,93),(87,97),(84,98),(80,95),(77,92),(75,89),(73,85),(74,79),(74,75),(76,71)],1)
 p.p([(79,70),(82,71),(85,75),(87,79),(89,84),(88,90),(86,94),(83,94),(78,90),(75,86),(75,79),(76,74)],4)
 p.p([(79,69),(82,72),(86,76),(88,81),(89,85),(86,85),(83,84),(78,82),(76,79),(77,73)],6)
 p.p([(79,67),(80,67),(80,69),(83,71),(83,73),(85,73),(85,75),(87,76),(87,78),(84,77),(82,75),(81,72),(79,71)],9)
 p.p([(106,66),(107,69),(108,73),(108,87),(107,92),(105,96),(103,99),(101,102),(97,102),(94,99),(92,94),(90,89),(91,85),(93,80),(96,76),(98,73),(102,69)],1)
 p.p([(105,69),(107,74),(107,86),(106,91),(103,97),(100,100),(97,98),(94,94),(92,89),(93,84),(96,79),(100,75)],4)
 p.p([(104,71),(106,75),(106,81),(103,83),(101,85),(97,86),(93,87),(93,84),(96,79),(100,76)],6)
 p.p([(106,66),(106,69),(103,71),(103,73),(101,74),(100,77),(97,79),(96,81),(93,84),(94,80),(97,76),(99,73),(103,69)],9)
 p.p([(106,80),(107,79),(107,87),(106,92),(104,96),(103,96),(104,90),(105,85)],7)
 p.p([(106,80),(107,80),(107,85),(106,87),(106,90),(105,91),(105,85)],10)
 # Occluded near face: the reference has a cream muzzle rim, no exposed teal eye.
 p.p([(84,89),(89,89),(93,92),(96,95),(99,98),(101,102),(104,101),(106,102),(107,104),(104,105),(84,105),(81,103),(79,99),(80,96)],1)
 p.p([(85,90),(89,90),(92,94),(95,96),(98,99),(96,101),(82,100),(81,98)],6)
 p.p([(82,100),(97,100),(99,102),(97,103),(85,103),(82,102)],4)
 p.r((85,92,85,93),9);p.r((86,93,87,93),9)
 p.p([(103,101),(105,101),(105,102),(107,103),(106,104),(103,104),(102,103)],10)
 p.r((103,104,105,104),7)
 p.p([(85,106),(95,106),(97,108),(96,111),(92,111),(90,108),(84,108)],3)
 p.l([(85,106),(95,106),(97,108)],1)

def torso(im,source,v,dy,pose):
 # Constrain/repaint the generated torso contour, retaining its interior texels.
 if v=='back':pts=[(75,106),(84,106),(88,108),(91,112),(91,117),(89,121),(86,124),(72,124),(69,122),(68,118),(68,112),(71,109)]
 else:pts=[(87,107),(94,107),(98,110),(100,113),(100,119),(96,123),(92,125),(79,125),(74,124),(69,122),(70,119),(74,116),(77,113),(81,110)]
 mask=Image.new('L',(192,192));d=ImageDraw.Draw(mask);d.polygon([(x+16,y+20+dy) for x,y in pts],fill=255);m=np.array(mask)>0
 a=np.array(im);src=np.array(source);good=m&(src[:,:,3]>0)&np.isin(src[:,:,0],PAL[[0,1,2,3,4,5,6,8,9],0]);a[m]=C[4];a[good]=src[good];im.paste(Image.fromarray(a))
 p=Pen(im,0,dy)
 p.l(pts+[pts[0]],1)
 if v=='back':
  p.p([(75,107),(83,107),(87,110),(88,114),(86,119),(72,119),(70,115),(71,111)],6)
  p.p([(72,119),(86,119),(87,122),(84,123),(74,123)],2)
  p.l([(72,109),(70,113),(70,116)],5);p.l([(88,110),(90,113),(90,116)],5)
  p.l([(74,120),(84,120)],4)
 else:
  p.p([(87,108),(92,108),(96,110),(97,114),(94,118),(89,122),(78,123),(72,122),(75,118),(80,114)],6)
  p.p([(72,122),(78,124),(90,123),(92,125),(78,125),(70,123)],2)
  p.l([(72,119),(75,117)],4);p.l([(76,116),(79,113)],4)
  # Shoulder disc is drawn, not stamped.
  p.p([(98,110),(100,111),(101,114),(100,117),(97,118),(95,116),(95,112)],3)
  p.p([(97,111),(99,111),(100,114),(99,116),(96,115),(96,112)],5)
 return im

def back_leg(p,x,y,lift,far=False):
 # Nineteen-pixel hind leg; planting translates neither joint nor pad horizontally.
 y-=lift
 p.p([(x+2,y),(x+7,y),(x+9,y+3),(x+9,y+8),(x+7,y+12),(x+7,y+15),(x+10,y+16),(x+10,y+18),(x,y+18),(x,y+16),(x+2,y+14),(x+1,y+8),(x,y+5)],1)
 p.p([(x+2,y+2),(x+6,y+1),(x+8,y+4),(x+7,y+8),(x+2,y+8),(x+1,y+5)],4)
 p.p([(x+2,y+2),(x+6,y+1),(x+7,y+4),(x+2,y+5)],6)
 p.p([(x+2,y+8),(x+7,y+9),(x+6,y+14),(x+3,y+15)],2)
 p.r((x+1,y+16,x+8,y+17),3);p.r((x+2,y+16,x+6,y+17),5)

def ne_leg(p,x,y,lift):
 y-=lift
 p.p([(x+3,y),(x+9,y),(x+11,y+3),(x+11,y+7),(x+8,y+10),(x+8,y+12),(x+12,y+13),(x+12,y+15),(x,y+15),(x,y+13),(x+2,y+11),(x,y+7),(x,y+3)],1)
 p.p([(x+3,y+1),(x+8,y+1),(x+10,y+3),(x+9,y+7),(x+5,y+9),(x+1,y+7),(x+1,y+4)],4)
 p.p([(x+3,y+1),(x+7,y+1),(x+7,y+3),(x+2,y+5)],6)
 p.p([(x+7,y+4),(x+9,y+4),(x+9,y+7),(x+6,y+8),(x+5,y+7)],5)
 p.p([(x+3,y+10),(x+7,y+9),(x+7,y+12),(x+9,y+13),(x+2,y+13)],2)
 p.r((x+1,y+14,x+10,y+14),5)

def back_tail(p,dy=0,sway=0):
 # Twenty-pixel straight projection; three violet plates then the cream tip.
 x=72+sway;y=121+dy
 p.p([(x+5,y),(x+9,y),(x+12,y+2),(x+14,y+8),(x+14,y+13),(x+11,y+17),(x+8,y+19),(x+5,y+19),(x+2,y+17),(x,y+13),(x,y+8),(x+2,y+3)],1)
 p.p([(x+5,y+1),(x+9,y+1),(x+12,y+3),(x+11,y+5),(x+2,y+5),(x+3,y+3)],4)
 p.p([(x+5,y+1),(x+9,y+1),(x+10,y+2),(x+4,y+2)],9)
 p.p([(x+2,y+6),(x+11,y+6),(x+13,y+9),(x+12,y+11),(x+1,y+11)],4)
 p.p([(x+5,y+6),(x+9,y+6),(x+11,y+8),(x+3,y+8)],6)
 p.l([(x+2,y+10),(x+11,y+10)],2)
 p.p([(x+1,y+12),(x+4,y+11),(x+7,y+12),(x+10,y+11),(x+13,y+12),(x+12,y+15),(x+9,y+18),(x+5,y+18),(x+2,y+16)],7)
 p.p([(x+2,y+12),(x+5,y+11),(x+7,y+12),(x+10,y+11),(x+12,y+12),(x+11,y+15),(x+8,y+17),(x+5,y+16)],10)
 p.p([(x+5,y+11),(x+7,y+12),(x+7,y+14),(x+10,y+14),(x+9,y+15),(x+6,y+14),(x+5,y+13)],13)

def ne_tail(p,lift=0):
 # Straight axis (82,128) -> (52,137), with constant projected length.
 p.p([(82,123-lift),(85,126-lift),(84,132-lift),(80,136-lift),(72,138-lift),(64,140-lift),(54,140-lift),(51,138-lift),(52,135-lift),(57,131-lift),(62,129-lift),(66,128-lift),(73,126-lift),(78,124-lift)],1)
 p.p([(79,125-lift),(82,125-lift),(83,128-lift),(82,133-lift),(78,135-lift),(75,129-lift)],4)
 p.p([(79,125-lift),(82,125-lift),(82,127-lift),(77,129-lift)],6)
 p.p([(74,127-lift),(77,129-lift),(78,135-lift),(72,137-lift),(70,133-lift),(69,129-lift)],4)
 p.p([(70,129-lift),(74,128-lift),(76,130-lift),(72,131-lift)],6)
 p.p([(67,129-lift),(69,130-lift),(71,137-lift),(65,139-lift),(63,135-lift),(62,131-lift)],4)
 p.p([(63,131-lift),(66,130-lift),(69,132-lift),(64,133-lift)],6)
 p.p([(61,131-lift),(63,134-lift),(64,139-lift),(54,139-lift),(52,138-lift),(54,135-lift),(58,132-lift)],7)
 p.p([(60,131-lift),(61,133-lift),(62,135-lift),(55,137-lift),(53,138-lift),(55,135-lift),(58,133-lift)],10)
 p.l([(54,136-lift),(57,133-lift),(60,131-lift)],13)
 # Joint cuts follow one shared rigid axis, never a chain bending upward.
 p.l([(74,128-lift),(76,131-lift),(77,135-lift)],2)
 p.l([(67,130-lift),(69,133-lift),(70,137-lift)],2)

def redraw(name,v,i):
 source=Image.open(R/name/'frames'/f'{v}_f{i}.png').convert('RGBA')
 nearshift=([0,0,0,0,0,1,2,0][i] if name=='walk' and v=='ne' else 0)
 farshift=([0,1,2,0,0,0,0,0][i] if name=='walk' and v=='ne' else 0)
 im=Image.new('RGBA',(192,192));p=Pen(im)
 if name=='walk':
  head_dy=0;body_dy=[0,0,1,0,0,0,1,0][i]
  lh=[0,0,0,0,2,3,4,0][i];rh=[2,3,4,0,0,0,0,0][i]
 else:
  head_dy=[0,1,7,-2,3,0][i];body_dy=[0,1,6,-1,3,0][i];lh=rh=0
 if v=='back':
  # Far front legs remain short and mostly occluded by rear torso/tail.
  for x,lift in ([] if name=='sand_kick' and i==3 else [(70,rh),(84,lh)]):
   yy=120-lift;p.p([(x,yy),(x+4,yy),(x+4,yy+18),(x+5,yy+20),(x-1,yy+20),(x-1,yy+18)],1)
   p.r((x+1,yy+3,x+3,yy+16),2);p.r((x,yy+19,x+4,yy+20),3)
  back_leg(p,62,122,lh);back_leg(p,86,122,rh)
  torso(im,source,v,body_dy,name)
  # Hind shoulders are continuous with the torso: no orphan discs or horizontal joins.
  if name=='sand_kick' and i==3:
   p.p([(68,112),(71,115),(70,120),(67,121),(65,119),(65,115)],1)
   p.p([(67,114),(69,115),(69,118),(66,118)],4)
   p.p([(89,112),(92,113),(94,117),(93,120),(90,120),(88,116)],1)
   p.p([(90,114),(92,115),(92,118),(90,118)],4)
  back_tail(p,-4 if name=='walk' else 0,[-1,0,1,0,-1,0,1,0][i] if name=='walk' else 0)
  back_head(im,head_dy)
 else:
  # Far rear leg and far foreleg; alternating opposite diagonal supports.
  ne_leg(p,78+farshift,125,rh)
  fy=119-lh
  p=Pen(im,nearshift,0)
  if name=='sand_kick' and i==3:
   p.p([(98,112),(101,111),(106,106),(111,101),(113,99),(116,100),(117,102),(114,104),(109,109),(103,116),(100,117)],1)
   p.p([(100,113),(102,112),(107,107),(112,102),(114,102),(109,108),(103,115)],4)
   p.p([(113,100),(115,100),(116,102),(113,103),(112,102)],5)
  else:
   p.p([(98,fy),(102,fy),(102,fy+15),(105,fy+18),(105,fy+21),(97,fy+21),(97,fy+19),(99,fy+17)],1)
   p.r((99,fy+2,101,fy+16),2);p.r((98,fy+20,104,fy+20),5)
  p=Pen(im)
  torso(im,source,v,body_dy,name)
  ne_leg(p,88+nearshift,125,lh)
  ne_tail(p,3 if name=='walk' else 0)
  ne_head(im,head_dy)
 a=clean(im)
 # Repaint only isolated one-pixel palette impurities left from the underdrawing.
 Image.fromarray(a).save(R/name/'frames'/f'{v}_f{i}.png')
 return {'view':v,'frame':i,'head_translation':[0,head_dy],'body_bob':body_dy,'hind_lifts':[lh,rh],'hind_x_shift':[nearshift,farshift],'method':'direct native-pixel contour/colour repaint; no still part compositing'}

if __name__=='__main__':
 log=[]
 for name,N in COUNTS.items():
  for v in ['back','ne']:
   for i in range(N):
    if name=='sand_kick' and i in (0,5):approved(v).save(R/name/'frames'/f'{v}_f{i}.png');continue
    log.append(dict(move=name,**redraw(name,v,i)))
  board(name)
 (R/'pixel_edits.json').write_text(json.dumps(log,indent=2))
 print('Repainted 24 posed drawings; four untouched exact still endpoints.')


