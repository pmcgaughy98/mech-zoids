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


def fit_whole(im,scale=1,xscale=1,ground=160):
 b=im.getbbox();crop=im.crop(b);crop=crop.resize((round(crop.width*scale*xscale),round(crop.height*scale)),Image.Resampling.NEAREST)
 out=Image.new('RGBA',(192,192));x=round((b[0]+b[2]-crop.width)/2);out.paste(crop,(x,ground+1-crop.height));return clean(out)

def native_finish(n,v,i):
 im=Image.open(R/n/'underpaint'/f'{v}_f{i}.png').convert('RGBA')
 if n=='sprint':im=fit_whole(im,{'se':.88,'ne':.94}[v],ground=bottom(n,i))
 if n=='lunge' and v=='se':im=fit_whole(im,xscale=.96,ground=bottom(n,i))
 return clean(im)

if __name__=='__main__':
 for n in TIMES:
  for v in VIEWS:
   for i in range(len(TIMES[n])):
    if exact(n,i):continue
    native_finish(n,v,i).save(R/n/'frames'/f'{v}_f{i}.png')
  finalize(n)
