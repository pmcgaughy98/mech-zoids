# Native pixel helpers reused verbatim from ape_l/run1/build.py.
from pathlib import Path
import ast
from collections import deque
import numpy as np
from PIL import Image, ImageDraw
B=Path(r"D:/dev/new-mech-rpg/docs/art/moba")
def fill_holes(op):
 seen=op.copy();queue=deque()
 for x in range(192):
  for y in (0,191):
   if not seen[y,x]:seen[y,x]=True;queue.append((y,x))
 for y in range(192):
  for x in (0,191):
   if not seen[y,x]:seen[y,x]=True;queue.append((y,x))
 while queue:
  y,x=queue.popleft()
  for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=yy<192 and 0<=xx<192 and not seen[yy,xx]:seen[yy,xx]=True;queue.append((yy,xx))
 return ~seen|op

def mask(poly):
 im=Image.new('1',(192,192));ImageDraw.Draw(im).polygon(poly,fill=1);return np.array(im)

def shift(a,dx=0,dy=0):
 b=np.zeros_like(a);ys,xs=np.where(a[:,:,3]>0);xx=xs+int(dx);yy=ys+int(dy);ok=(xx>=0)&(xx<192)&(yy>=0)&(yy<192);b[yy[ok],xx[ok]]=a[ys[ok],xs[ok]];return b

def comp(a,b):
 m=b[:,:,3]>0;a[m]=b[m]

def piece(a,m):
 b=a.copy();b[~m]=0;return b

def support(a):
 yy,xx=np.where(a[:,:,3]>0);row=int(yy.max());xs=np.where(a[row-1:row+1,:,3].any(axis=0))[0];return np.array([(xs.min()+xs.max())/2,row],float)

def load_selout():
 # touchup_machine imports this exact function; no module top-level code is run.
 sp=B/'rhino_l/take-a/anim/selout_rhino.py'
 tree=ast.parse(sp.read_text());ns={'np':np,'OUTLINE':np.array([20,26,22],np.uint8)}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),str(sp),'exec'),ns)
 return ns['selout']

def pieces(op):
 seen=np.zeros_like(op);out=[]
 for y,x in zip(*np.where(op)):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;pts=[]
  while todo:
   yy,xx=todo.pop();pts.append((yy,xx))
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<192 and 0<=nx<192 and op[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  out.append(pts)
 return sorted(out,key=len,reverse=True)

def locate(a,src):
 # Search the complete native six-row sole stamp, never the target coordinates.
 sole=b.support(src);ys,xs=np.where((src[:,:,3]>0)&(b.Y>=sole[1]-5));cols=src[ys,xs]
 best=None
 for dy in range(-12,13):
  for dx in range(-14,15):
   score=float(np.all(a[ys+dy,xs+dx]==cols,axis=1).mean())
   key=(score,-abs(dx)-abs(dy))
   if best is None or key>best[0]:best=(key,dx,dy)
 (_,score_unused),dx,dy=best
 score=best[0][0]
 # Both support-band endpoints must still exist, with their actual source colours.
 sy=int(sole[1]);by,bx=np.where((src[:,:,3]>0)&(b.Y>=sy-1));left,right=int(bx.min()),int(bx.max())
 ends=[]
 for x in [left,right]:
  ends.append(any(np.array_equal(a[y+dy,x+dx],src[y,x]) for y in [sy-1,sy] if src[y,x,3]>0))
 return sole+[dx,dy],score,[dx,dy],all(ends)

