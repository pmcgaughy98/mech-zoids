"""ape-walk35-run1. Only integer translations and hand drawn stepped sockets.
All output paths resolve under this script's directory. Inputs are read-only.
"""
from pathlib import Path
import ast, json, hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from collections import deque

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
R=Path(__file__).resolve().parent
B=R.parents[2]
T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192))
P={h:tuple(bytes.fromhex(h))+(255,) for h in '141a16 22301d 47693a 6c9b4a 9ccb62 4a4950 8a8a93 dfe2e9 55331a 9c5e28 d4853b f2ac5c 1b9a52 3fe07f d6ffe6'.split()}
# Native contours. Shoulders, head, back plate and rump are on the pinned body.
# The full elbow, forearm, hex bezel, gem and all three knuckles belong together.
D={
'e':{
 'RF':dict(poly=[(94,108),(101,106),(106,108),(109,112),(108,117),(113,117),(118,121),(123,129),(125,138),(126,145),(129,151),(128,158),(125,161),(100,161),(96,155),(94,145),(90,138),(89,128),(90,117),(92,112)],root=(100,104),joint=(99,117),w=7,kind='arm'),
 'RH':dict(poly=[(61,121),(65,119),(71,119),(77,121),(80,125),(81,131),(79,137),(83,139),(83,147),(79,151),(60,151),(57,147),(57,139),(60,133),(60,127)],root=(68,114),joint=(69,126),w=7,kind='leg'),
 'LF':dict(poly=[(118,113),(122,112),(126,115),(129,116),(133,119),(135,124),(134,130),(130,133),(124,132),(122,128),(121,125),(117,124),(114,121),(114,116)],root=(122,109),joint=(121,117),w=4,kind='arm')},
'se':{
 'RF':dict(poly=[(68,107),(74,104),(80,105),(84,109),(86,115),(83,118),(89,120),(94,124),(97,129),(97,143),(101,147),(102,155),(99,161),(72,161),(69,154),(68,145),(65,139),(62,134),(63,128),(64,120),(67,117)],root=(75,103),joint=(75,117),w=8,kind='arm'),
 'LF':dict(poly=[(116,100),(121,101),(125,104),(128,110),(131,112),(136,117),(139,123),(138,130),(141,135),(141,143),(134,148),(130,150),(120,149),(116,144),(113,141),(112,129),(111,124),(111,119),(112,113),(113,107)],root=(117,98),joint=(119,111),w=6,kind='arm'),
 'RH':dict(poly=[(56,104),(60,104),(64,108),(65,113),(64,118),(61,122),(64,125),(69,125),(73,127),(73,132),(68,135),(56,135),(50,131),(48,126),(49,120),(51,117),(51,110)],root=(61,99),joint=(57,112),w=5,kind='leg'),
 'LH':dict(poly=[(96,119),(101,118),(105,120),(108,124),(109,128),(111,131),(111,135),(107,139),(101,139),(97,136),(96,131),(92,129),(92,125)],root=(98,114),joint=(100,125),w=5,kind='leg')},
'ne':{
 'RF':dict(poly=[(110,111),(115,110),(120,114),(123,116),(127,115),(131,118),(133,123),(136,126),(136,143),(140,146),(140,153),(136,157),(128,159),(119,160),(114,156),(111,153),(110,147),(107,141),(104,134),(104,126),(106,120)],root=(113,106),joint=(115,121),w=7,kind='arm'),
 'RH':dict(poly=[(83,133),(88,130),(92,132),(95,135),(97,140),(96,146),(100,149),(101,154),(98,158),(93,161),(82,161),(78,157),(77,152),(78,146),(77,141),(79,137)],root=(86,128),joint=(86,141),w=6,kind='leg'),
 'LH':dict(poly=[(57,129),(60,128),(63,131),(65,136),(68,139),(73,140),(77,142),(78,146),(74,149),(59,150),(55,147),(54,143),(54,136)],root=(64,123),joint=(59,136),w=5,kind='leg'),
 'LF':dict(poly=[(54,100),(58,98),(62,98),(63,104),(62,109),(60,114),(59,119),(57,125),(53,128),(49,126),(48,121),(48,111),(50,105)],root=(64,95),joint=(57,108),w=4,kind='arm')}
}

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
def poly(a,points,c):
 im=Image.fromarray(a);ImageDraw.Draw(im).polygon([tuple(map(int,p)) for p in points],fill=P[c]);a[:]=im

def socket(q,dx,dy,dip):
 # Short green articulated link behind the intact native hinge. Horizontal
 # colour bands follow a one-pixel staircase, with round stepped end caps.
 a=np.zeros((192,192,4),np.uint8)
 x0,y0=q['root'];x1,y1=q['joint'];y0+=dip;x1+=dx;y1+=dy
 w=q['w'];height=max(1,y1-y0)
 for y in range(y0,y1+3):
  t=np.clip((y-y0)/height,0,1);cx=int(np.floor(x0+(x1-x0)*t+.5))
  inset=2 if y in (y0,y1+2) else 1 if y in (y0+1,y1+1) else 0
  l,r=cx-w+inset,cx+w-inset
  a[y,l:r+1]=P['22301d'];a[y,l+1:r]=P['47693a'];a[y,l+1:cx+1]=P['6c9b4a']
  if y<y0+3:a[y,l+2:min(cx,l+4)]=P['9ccb62']
 return a

def load_selout():
 # touchup_machine imports this exact function; no module top-level code is run.
 sp=B/'rhino_l/take-a/anim/selout_rhino.py'
 tree=ast.parse(sp.read_text());ns={'np':np,'OUTLINE':np.array([20,26,22],np.uint8)}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),str(sp),'exec'),ns)
 return ns['selout']

def sources(view,ref):
 src={};used=np.zeros((192,192),bool)
 # Forearm overlaps own hind limb. All source texels get a single owner.
 for name in ['RF','LF','RH','LH']:
  if name not in D[view]:continue
  m=mask(D[view][name]['poly'])&~used&(ref[:,:,3]>0)
  src[name]=piece(ref,m);used|=m
 body=piece(ref,~used)
 if view=='e':
  # Left hind is fully behind the right thigh/rump. Same native limb, depth lane.
  src['LH']=shift(src['RH'],0,-14)
  D[view]['LH']=dict(D[view]['RH']);D[view]['LH']['root']=(68,100);D[view]['LH']['joint']=(69,112)
 if view=='se':
  # Finish the unseen sole behind the forearm using the still's own orange
  # shin/ankle paint. Only the existing visible trace can protrude from the torso.
  foot=piece(src['RH'],(Y>=126)&(Y<=134)&(X>=51)&(X<=68))
  comp(src['RH'],shift(foot,9,6))
  foot=piece(src['LH'],Y>=130)
  comp(src['LH'],shift(foot,-5,5))
 if view=='ne':
  # The far fist is occluded by the flank; native far bezel is already visible.
  # Add only a translated native knuckle support block behind the pinned flank.
  kn=piece(src['RF'],Y>=149)
  comp(src['LF'],shift(kn,-59,-20))
 return src,body

def build():
 (R/'walk/frames').mkdir(parents=True,exist_ok=True);(R/'walk/layers').mkdir(exist_ok=True)
 (R/'source').mkdir(exist_ok=True)
 protected={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/'targets.json',*sorted((R/'stills').glob('*.png'))]}
 (R/'protected_hashes.json').write_text(json.dumps(protected,indent=2))
 rig={};allframes={}
 for view in ['e','se','ne']:
  ref=np.array(Image.open(R/'stills'/f'{view}.png').convert('RGBA'));src,body=sources(view,ref)
  Image.fromarray(body).save(R/f'source/{view}_body.png')
  for n,a in src.items():Image.fromarray(a).save(R/f'source/{view}_{n}.png')
  frames=[];rig[view]=[]
  for f in range(8):
   dip=int(f in (0,4));layers={}
   for n,s in src.items():
    sole=support(s);off,lift=T['paths'][n][f];vt=T['views'][view]
    if n in vt['visible_feet']:ideal=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre'])
    else:ideal=sole+off*np.array(vt['u'])*vt['f']-[0,lift]
    delta=np.floor(ideal-sole+.5).astype(int);dx,dy=map(int,delta)
    a=socket(D[view][n],dx,dy,dip);comp(a,shift(s,dx,dy))
    # The source foot is the only silhouette at the ground, including lifted frames.
    raw=shift(s,dx,dy);bottom=int(sole[1])+dy
    a[Y>bottom]=0;a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
    layers[n]=a;Image.fromarray(a).save(R/f'walk/layers/{view}_{n}_f{f}.png')
    rig[view].append(dict(foot=n,frame=f,delta=[dx,dy],source_sole=sole.tolist(),target=ideal.tolist(),lift=lift,ground_row=bottom+lift,hidden_in_still=n not in vt['visible_feet']))
   a=np.zeros_like(ref)
   for n in ['LF','LH','RH','RF']:comp(a,layers[n])
   comp(a,shift(body,0,dip))
   # Mechanical socket recesses: enclosed wedges are metal-shadow, never holes.
   holes=fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);a[holes]=P['22301d']
   frames.append(a);Image.fromarray(a).save(R/f'walk/frames/{view}_f{f}.png')
  allframes[view]=frames
 (R/'rig.json').write_text(json.dumps(rig,indent=2))
 boards(allframes)
 print('Built 24 native frames')

def boards(allframes):
 selout=load_selout();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
 # Full 192 canvases, exact nearest-neighbour 4x, still then eight frames.
 cw,ch=768,800;bg=(73,88,77,255)
 board=Image.new('RGBA',(cw*9,ch*3),bg);d=ImageDraw.Draw(board)
 for vi,(v,frames) in enumerate(allframes.items()):
  ref=np.array(Image.open(R/'stills'/f'{v}.png').convert('RGBA'));pics=[]
  for j,a in enumerate([ref]+frames):
   tile=Image.fromarray(selout(a)[0]).resize((768,768),Image.Resampling.NEAREST)
   board.alpha_composite(tile,(j*cw,vi*ch+28));d.text((j*cw+12,vi*ch+5),v+' '+('APPROVED STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
   if j:
    im=Image.new('RGBA',tile.size,bg);im.alpha_composite(tile);pics.append(im.convert('RGB'))
  board.crop((0,vi*ch,cw*9,(vi+1)*ch)).convert('RGB').save(R/f'{v}_board.png')
  pics[0].save(R/f'{v}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
  raw=[Image.fromarray(a) for a in frames];raw[0].save(R/f'{v}_preview.apng',save_all=True,append_images=raw[1:],duration=125,loop=0,disposal=0,blend=0)
  # Legible compact board for inspection; still, 4 frames on row one, 4 on row two.
  box=(40,70,148,165);w,h=432,380;small=Image.new('RGBA',(w*5,(h+25)*2),bg);dd=ImageDraw.Draw(small)
  for j,a in enumerate([ref]+frames):
   col,row=(0,0) if j==0 else ((j-1)%4+1,(j-1)//4)
   small.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((w,h),Image.Resampling.NEAREST),(col*w,row*(h+25)+25));dd.text((col*w+6,row*(h+25)+3),v+' '+('STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
  small.convert('RGB').save(R/f'{v}_review.png')
 board.convert('RGB').save(R/'board.png')

if __name__=='__main__':build()
