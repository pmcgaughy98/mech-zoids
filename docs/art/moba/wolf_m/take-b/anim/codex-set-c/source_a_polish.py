"""Native whole-cell corrections and direct pixel contours. Never crops/pastes approved parts."""
from finish import *
C=[tuple(map(int,c))+(255,) for c in PAL]
class Pen:
 def __init__(self,im):self.d=ImageDraw.Draw(im)
 def p(self,pts,c):self.d.polygon([(round(x),round(y)) for x,y in pts],fill=C[c])
 def l(self,pts,c,w=1):self.d.line([(round(x),round(y)) for x,y in pts],fill=C[c],width=w)
 def r(self,b,c):self.d.rectangle(tuple(map(round,b)),fill=C[c])

def remap(im,xscale=1,ypairs=None,xcentre=96):
 a=np.array(im);yy,xx=np.indices((192,192));sx=np.rint((xx-xcentre)/xscale+xcentre).astype(int)
 sy=yy if ypairs is None else np.rint(np.interp(yy,[p[1] for p in ypairs],[p[0] for p in ypairs])).astype(int)
 valid=(sx>=0)&(sx<192)&(sy>=0)&(sy<192);b=np.zeros_like(a);b[valid]=a[sy[valid],sx[valid]];return Image.fromarray(b)

def walk_finish(v,i):
 # Start from each whole underdrawing, retaining its integrated contours.
 im=Image.open(R/'walk/underpaint'/f'{v}_f{i}.png').convert('RGBA')
 if v=='front':
  # Generator repeated the B swing at f5. Mirror that complete drawing to the A half-cycle.
  if i==5:
   a=np.array(im);yy,xx=np.indices((192,192));sx=191-xx;im=Image.fromarray(a[yy,sx])
  offset=2 if i==5 else 0
  im=remap(im,33/36,[(0,0),(95+offset,89),(114+offset,109),(129,125),(141,137),(160,160),(191,191)])
 elif v=='back':
  if i==5:
   a=np.array(im);yy,xx=np.indices((192,192));im=Image.fromarray(a[yy,191-xx])
  im=remap(im,35/36,[(0,0),(91,89),(110,108),(131,129),(143,140),(160,160),(191,191)])
 else:
  im=remap(im,1,[(0,0),(97,95),(112,111),(126,124),(140,138),(160,160),(191,191)])
  # Whole drawing x-map lengthens the existing rigid tail without replacing it.
  a=np.array(im);yy,xx=np.indices((192,192));sx=np.rint(np.interp(xx,[0,34,70,191],[0,40,70,191])).astype(int);im=Image.fromarray(a[yy,sx])
 return clean(im)

def generic_finish(n,v,i):
 im=Image.open(R/n/'underpaint'/f'{v}_f{i}.png').convert('RGBA')
 sx={'sprint':{'front':.825,'back':.875,'side':1},'lunge':{'front':.92,'back':.97,'side':1},'bite':{'front':1,'back':1,'side':1}}[n][v]
 im=remap(im,sx)
 if n=='bite':
  a=np.array(im);yy,xx=np.indices((192,192));weight=np.clip((yy-128)/22,0,1)
  if v=='front':
   src={1:[0,83,92,101,110,191],2:[0,84,94,102,111,191],3:[0,81,90,98,107,191]}[i];dst=[0,83,92,100,109,191]
  elif v=='side':
   src={1:[0,69,78,111,123,191],2:[0,64,74,107,118,191],3:[0,68,78,111,122,191]}[i];dst=[0,63,73,108,119,191]
  else:
   src={1:[0,78,87,95,103,112,191],2:[0,78,87,95,103,112,191],3:[0,78,88,96,103,113,191]}[i];dst=[0,78,87,95,103,112,191]
  target=np.interp(xx,dst,src);sxmap=np.rint(xx*(1-weight)+target*weight).astype(int);im=Image.fromarray(a[yy,sxmap])
 if n=='lunge' and v=='side' and i==3:
  p=Pen(im)
  # Repaint the generated shut profile as an articulated open jaw, joined continuously at the hinge.
  p.p([(133,97),(145,99),(147,102),(145,111),(138,109),(132,103)],0)
  p.p([(132,99),(136,103),(140,107),(146,110),(145,113),(140,112),(136,108),(132,104)],1)
  p.l([(133,100),(137,105),(141,109),(145,111)],6,2)
  p.l([(138,108),(141,111),(144,112)],4)
  p.p([(141,99),(144,100),(143,108),(142,110),(141,108)],10)
  p.l([(141,100),(141,107)],11)
  p.p([(146,100),(148,100),(147,106),(146,107)],10)
 return clean(im)
if __name__=='__main__':
 import sys
 for n in sys.argv[1:] or TIMES:
  if not (R/n/'underpaint').exists():continue
  for v in VIEWS:
   for i in range(len(TIMES[n])):
    if exact(n,i):continue
    im=walk_finish(v,i) if n=='walk' else generic_finish(n,v,i)
    im.save(R/n/'frames'/f'{v}_f{i}.png')
  finalize(n)
