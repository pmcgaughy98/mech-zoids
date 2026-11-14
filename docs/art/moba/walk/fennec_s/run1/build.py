"""fennec-trot35-run1: hand-traced native parts; gorilla integer-translation method.
No generated imagery, rotations, resampling, or writes outside this directory.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,ast
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import ape_native as b
R=Path(__file__).resolve().parent
# Reuse the walk lane's single-pass seam detector and body-band colour choice.
_seamfile=R.parents[2]/'walk/tools/walk_tools.py'
_tree=ast.parse(_seamfile.read_text());_ns={'np':np}
exec(compile(ast.Module(body=[n for n in _tree.body if isinstance(n,ast.FunctionDef) and n.name in ['find_slits','fill_colour']],type_ignores=[]),str(_seamfile),'exec'),_ns)
find_slits,fill_colour=_ns['find_slits'],_ns['fill_colour']
T=json.loads((R/'targets.json').read_text());Y,X=np.indices((192,192));b.Y,b.X=Y,X;b.b=b
P={h:tuple(bytes.fromhex(h))+(255,) for h in '141218 211e27 2e1a6e 3d3a44 6a3cc8 9d9ba2 a46bff d6d6dc e0c8ff f0d27a fff4d6'.split()}
load=lambda p:np.array(Image.open(p).convert('RGBA'))
# Each knee housing includes its complete steel disc. Each lower block includes
# the unchanged native shin, ankle and steel foot, with sole contact endpoints.
D={
'e':{
 'RH':dict(knee=[(84,133),(89,133),(96,136),(98,139),(97,144),(93,146),(81,146),(80,140),(81,137)],lower=[(81,147),(90,147),(91,153),(94,154),(94,158),(92,160),(81,160)],root=(87,131),k=(88,140),join=(86,147),sole=(86.5,160)),
 'RF':dict(knee=[(110,131),(114,131),(117,134),(117,139),(115,143),(108,143),(108,135)],lower=[(107,144),(116,144),(116,152),(119,154),(119,159),(107,159),(107,153)],root=(112,129),k=(112,137),join=(112,144),sole=(112.5,159)),
 },
'se':{
 'RH':dict(knee=[(81,127),(85,127),(90,130),(92,134),(91,137),(88,140),(80,141),(79,136),(79,131)],lower=[(80,141),(87,141),(87,146),(91,147),(91,151),(88,153),(80,153),(79,151),(79,147)],root=(84,125),k=(84,133),join=(84,141),sole=(84,153)),
 'RF':dict(knee=[(99,133),(103,133),(108,136),(110,139),(108,143),(104,145),(98,144),(96,140),(97,136)],lower=[(97,145),(106,145),(106,153),(109,154),(109,159),(107,160),(98,160),(97,157)],root=(102,132),k=(102,139),join=(102,145),sole=(103,160)),
 'LF':dict(knee=[(112,139),(116,139),(119,142),(119,147),(111,148),(110,144)],lower=[(111,148),(118,148),(118,150),(121,151),(121,154),(118,156),(109,156),(109,151)],root=(114,137),k=(114,143),join=(114,148),sole=(114,156)),
 },
'ne':{
 'RH':dict(knee=[(91,135),(96,135),(102,137),(103,140),(102,143),(100,146),(96,148),(90,147),(89,141),(89,137)],lower=[(90,148),(97,148),(97,152),(101,154),(101,158),(98,160),(90,160)],root=(94,133),k=(95,141),join=(94,148),sole=(94.5,160)),
 'RF':dict(knee=[(108,124),(112,124),(115,127),(115,131),(112,133),(107,132),(106,128)],lower=[(107,133),(113,133),(113,140),(116,142),(116,146),(114,148),(105,148),(103,145),(103,142),(107,140)],root=(110,122),k=(110,128),join=(110,133),sole=(109.5,148)),
 'LH':dict(knee=[(80,137),(85,137),(87,141),(87,146),(78,147),(78,141)],lower=[(78,147),(85,147),(85,149),(89,149),(89,152),(86,155),(78,155),(77,152),(77,149)],root=(83,135),k=(82,141),join=(82,147),sole=(82,155)),
}}
TAIL={
'e':[(50,120),(82,120),(82,133),(80,139),(50,141)],
'se':[(60,110),(84,110),(84,122),(78,128),(60,128)],
'ne':[(60,120),(84,120),(84,127),(90,126),(94,129),(92,132),(86,138),(76,150),(60,150)]}
# Remove all visible far-leg peeks from the pinned body, in addition to near parts.
PEEKS={
'e':[(91,147,98,154),(117,145,122,154)],
'se':[(91,139,97,149)],
'ne':[]}

def rects(boxes):
 m=np.zeros((192,192),bool)
 for x0,y0,x1,y1 in boxes:m[y0:y1+1,x0:x1+1]=True
 return m

def dark(a):
 a=a.copy()
 # simultaneous palette mapping
 old=a.copy()
 for c,d in [('e0c8ff','a46bff'),('a46bff','6a3cc8'),('6a3cc8','2e1a6e'),('d6d6dc','9d9ba2'),('9d9ba2','3d3a44')]:a[np.all(old==P[c],axis=2)]=P[d]
 return a

def sources(v):
 ref=load(R/f'stills/{v}.png');used=np.zeros((192,192),bool);parts={}
 chest=np.zeros((192,192),bool)
 # Preserve the entire cream chest plate, including its steel highlights and rim.
 if v=='se':
  for yy,lo,hi in [(133,106,117),(134,105,117),(135,105,117),(136,105,117),(137,105,117),(138,106,116),(139,106,116),(140,106,115),(141,107,114),(142,106,113),(143,106,112),(144,107,110),(145,108,110)]:chest[yy,lo:hi+1]=True
 yellow=np.logical_or.reduce([np.all(ref==P[h],axis=2) for h in ['f0d27a','fff4d6']]);chest|=yellow&(X>100)
 native_tail=b.mask(TAIL[v])&(ref[:,:,3]>0)
 used|=native_tail

 for n in ['RF','RH','LF','LH']:
  if n not in D[v]:continue
  q=D[v][n];km=b.mask(q['knee'])&~used&~chest&(ref[:,:,3]>0);lm=b.mask(q['lower'])&~used&~km&~chest&(ref[:,:,3]>0)
  parts[n]={'knee':b.piece(ref,km),'lower':b.piece(ref,lm)};used|=km|lm
 # Hidden legs reconstructed with the same translated native parts, one ramp darker.
 # Their still peeks set depth/foot position. No pasted fragment can become detached.
 hidden={'e':[('LH','RH',6,-7),('LF','RF',8,-6)],'se':[('LH','RH',10,-5)],'ne':[('LF','RF',-12,-5)]}[v]
 for n,fromn,dx,dy in hidden:
  q=dict(D[v][fromn]);q['root']=tuple(np.array(q['root'])+[dx,dy]);q['k']=tuple(np.array(q['k'])+[dx,dy]);q['join']=tuple(np.array(q['join'])+[dx,dy]);q['sole']=tuple(np.array(q['sole'])+[dx,dy]);q['hidden']=True;D[v][n]=q
  parts[n]={p:dark(b.shift(a,dx,dy)) for p,a in parts[fromn].items()}
 if v=='ne':
  # The far hind knee is occluded by the tail in the still, not a tail plate.
  parts['LH']['knee']=dark(b.shift(parts['RH']['knee'],-12,-5))
  D[v]['LH']['k']=(83,136);D[v]['LH']['root']=(83,132)
 # Use the actual visible far sole where there is enough source to recover it.
 if v=='se':
  p=b.piece(ref,rects([(91,142,96,148)]));parts['LH']['lower']=p;D[v]['LH']['sole']=(94,148);D[v]['LH']['join']=(94,142)
 tail=b.piece(ref,native_tail)
 used|=tail[:,:,3]>0;used|=rects(PEEKS[v])&(ref[:,:,3]>0)
 body=b.piece(ref,~used);b.comp(body,b.piece(ref,chest))
 # Remaining native shank outlines are limb paint, not pinned trunk paint.
 # Removing them here prevents the old stationary vertical slivers seen on ape.
 if v=='e':body[(Y>=143)&(X>=100)&(X<=123)]=0
 if v=='se':body[(Y>=146)&(X>=90)&(X<=123)]=0
 if v=='ne':
  body[Y>=147]=0;body[(Y>=133)&(X>=103)&(X<=118)]=0;body[(Y>=139)&(X>=89)&(X<=102)]=0

 # Finish the flank behind the native hip housings. Only body above the leg
 # attachment is filled; the space between shin/foot pairs remains background.
 # Nearest native body band copied by row, as in the gorilla's seam repair.
 fills={'e':[(82,132,96,136),(108,131,117,142)],'se':[(81,127,89,130),(98,133,105,136)],'ne':[(90,135,99,138),(107,124,113,132)]}[v]
 for x0,y0,x1,y1 in fills:
  for y in range(y0,y1+1):
   for x in range(x0,x1+1):
    if body[y,x,3]==0 and ref[y,x,3]:body[y,x]=P['2e1a6e']
 return ref,parts,body,tail

def band(a,p0,p1,width=6,far=False):
 # Native palette bands, stepped by <=1px per row wherever room permits.
 x0,y0=p0;x1,y1=p1;y0,y1=int(y0),int(y1)
 if y1<y0:x0,y0,x1,y1=x1,y1,x0,y0
 for y in range(y0,y1+1):
  t=(y-y0)/max(1,y1-y0);cx=int(np.floor(x0+(x1-x0)*t+.5));l=cx-width//2;r=l+width
  a[y,l:r]=P['2e1a6e'];a[y,l+1:r-1]=P['6a3cc8' if not far else '2e1a6e']
  a[y,l+1:l+3]=P['a46bff' if not far else '6a3cc8'];a[y,r-1]=P['141218']

def make(v):
 for d in ['walk/frames','walk/layers','source']:(R/d).mkdir(parents=True,exist_ok=True)
 ref,parts,body,tail=sources(v)
 for label,a in [('body',body),('tail',tail)]:Image.fromarray(a).save(R/f'source/{v}_{label}.png')
 for n,pr in parts.items():
  for p,a in pr.items():Image.fromarray(a).save(R/f'source/{v}_{n}_{p}.png')
 frames=[];rig=[]
 for f in range(8):
  dip=int(f in (0,4));layers={}
  for n,pr in parts.items():
   q=D[v][n];sole=np.array(q['sole'],float);off,lift=T['paths'][n][f];vt=T['views'][v]
   ideal=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre']) if n in vt['visible_feet'] else sole+off*np.array(vt['u'])*vt['f']-[0,lift]
   dx,dy=np.floor(ideal-sole+.5).astype(int);kx=int(np.floor(dx*.5+.5));ky=int(np.floor((dy+dip)*.5+.5))
   a=np.zeros_like(ref);root=np.array(q['root'])+[0,dip];knee=np.array(q['k'])+[kx,ky];join=np.array(q['join'])+[dx,dy]
   band(a,root,knee,width=7 if n.endswith('H') else 6,far=n.startswith('L'))
   # The shin and foot remain one rigid native translation. Draw the small
   # articulated connection UNDER both translated pieces so no butt seam shows.
   band(a,knee,join,width=6,far=n.startswith('L'))
   b.comp(a,b.shift(pr['lower'],dx,dy));b.comp(a,b.shift(pr['knee'],kx,ky))
   bottom=int(sole[1]+dy);a[Y>bottom]=0
   raw=b.shift(pr['lower'],dx,dy);a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
   layers[n]=a;Image.fromarray(a).save(R/f'walk/layers/{v}_{n}_f{f}.png')
   rig.append(dict(foot=n,frame=f,delta=[int(dx),int(dy)],knee_delta=[kx,ky],source_sole=sole.tolist(),target=ideal.tolist(),lift=lift,hidden_in_still=n not in vt['visible_feet']))
  Image.fromarray(b.shift(tail,0,int(f in (1,5)))).save(R/f'walk/layers/{v}_tail_f{f}.png')
  a=np.zeros_like(ref)
  # Tail always behind legs. Pinned trunk hides far legs only where it really exists.
  b.comp(a,b.shift(tail,0,int(f in (1,5))))
  for n in ['LF','LH']:b.comp(a,layers[n])
  b.comp(a,b.shift(body,0,dip))
  for n in ['RF','RH']:b.comp(a,layers[n])
  if v=='se':
   chestmask=b.mask([(106,133),(117,133),(117,137),(115,141),(110,145),(107,143),(105,138)])
   b.comp(a,b.shift(b.piece(ref,chestmask),0,dip))
  # Above the attachments, pin both paint and transparent background exactly.
  cut={'e':131,'se':127,'ne':124}[v]+dip
  pinned=b.shift(ref,0,dip);tt=b.shift(tail,0,dip);pinned[tt[:,:,3]>0]=0;b.comp(pinned,b.shift(tail,0,int(f in (1,5))))
  a[:cut]=pinned[:cut]
  # Fill only actual enclosed holes: translated native body paint where available,
  # deepest violet in mechanical socket recesses. No blanket silhouette expansion.
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)
  st=b.shift(ref,0,dip)
  for yy,xx in zip(*np.where(holes)):
   c=tuple(st[yy,xx]);a[yy,xx]=c if c in [P[h] for h in ['e0c8ff','a46bff','6a3cc8','2e1a6e']] else P['2e1a6e']
  # One pass only, as required by WALK_PLAYBOOK section 9. All filled
  # pixels are saved for review; no iterative expansion toward an idle silhouette.
  sl=find_slits(a,ref,dip);done=set();pre=a.copy()
  for xx,yy in sorted(sl,key=lambda p:(p[1],p[0])):
   c=fill_colour(a,ref,dip,xx,yy,done,{P[h][:3] for h in ['e0c8ff','a46bff','6a3cc8','2e1a6e']})
   a[yy,xx]=tuple(c)+(255,) if tuple(c) in {P[h][:3] for h in ['e0c8ff','a46bff','6a3cc8','2e1a6e']} else P['2e1a6e'];done.add((xx,yy))
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);a[holes]=P['2e1a6e']
  Image.fromarray(pre).save(R/f'walk/layers/{v}_before_seams_f{f}.png')
  Image.fromarray(a).save(R/f'walk/frames/{v}_f{f}.png');frames.append(a)
 old=json.loads((R/'rig.json').read_text()) if (R/'rig.json').exists() else {};old[v]=rig;(R/'rig.json').write_text(json.dumps(old,indent=2))
 boards(v,ref,frames)
 report=R/'REPORT.txt';s=report.read_text() if report.exists() else 'fennec-trot35-run1. Tokens: final total unavailable.\nRF/RH near right; LF/LH far left; supplied labels retained.\n'
 s+=f'{v}: eight native frames drawn; measurements and visual review pending.\n';report.write_text(s)
 print(v,'drawn')

def boards(v,ref,frames):
 sel=b.load_selout();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);bg=(74,80,76,255)
 board=Image.new('RGBA',(768*9,800),bg);zoom=Image.new('RGBA',(420*9,250),bg);review=Image.new('RGBA',(360*5,400*2),bg)
 for j,a in enumerate([ref]+frames):
  tile=Image.fromarray(sel(a)[0]);board.alpha_composite(tile.resize((768,768),Image.Resampling.NEAREST),(j*768,30));ImageDraw.Draw(board).text((j*768+8,5),v+' '+('STILL' if not j else f'f{j-1}'),font=font,fill='white')
  zoom.alpha_composite(tile.crop((60,118,144,162)).resize((420,220),Image.Resampling.NEAREST),(j*420,25));ImageDraw.Draw(zoom).text((j*420+8,3),v+' '+('STILL' if not j else f'f{j-1}'),font=font,fill='white')
  col,row=(0,0) if j==0 else ((j-1)%4+1,(j-1)//4)
  review.alpha_composite(tile.crop((50,85,140,180)).resize((360,380),Image.Resampling.NEAREST),(col*360,row*400+20));ImageDraw.Draw(review).text((col*360+5,row*400+1),v+' '+('STILL' if not j else f'f{j-1}'),font=font,fill='white')
 board.convert('RGB').save(R/f'{v}_board.png');zoom.convert('RGB').save(R/f'{v}_legs_zoom.png');review.convert('RGB').save(R/f'{v}_review.png')
 for half in range(2):zoom.crop((420*(1+half*4),0,420*(5+half*4),250)).convert('RGB').save(R/f'{v}_legs_half{half}.png')
 pics=[]
 for a in frames:
  tile=Image.new('RGBA',(768,768),bg);tile.alpha_composite(Image.fromarray(sel(a)[0]).resize((768,768),Image.Resampling.NEAREST));pics.append(tile.convert('RGB'))
 pics[0].save(R/f'{v}_preview.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2,optimize=False)
 views=[vv for vv in ['e','se','ne'] if (R/f'{vv}_board.png').exists()]
 out=Image.new('RGB',(768*9,800*len(views)),bg[:3]);zz=Image.new('RGB',(420*9,250*len(views)),bg[:3])
 for i,vv in enumerate(views):out.paste(Image.open(R/f'{vv}_board.png'),(0,800*i));zz.paste(Image.open(R/f'{vv}_legs_zoom.png'),(0,250*i))
 out.save(R/'board.png');zz.save(R/'legs_zoom.png')

if __name__=='__main__':
 for v in sys.argv[1:] or ['e','se','ne']:make(v)
