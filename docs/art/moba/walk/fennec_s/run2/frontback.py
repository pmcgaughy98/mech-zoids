"""Front/back extension of run1 native knee/lower translation and gorilla run2 depth layering."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'run1'))
import build as old
b=old.b;X,Y=old.X,old.Y;load=old.load;P=old.P
T=json.loads((R/'targets.json').read_text())
D={
's':{
'RF':dict(knee=[(83,130),(87,130),(88,133),(87,139),(83,139),(82,136),(82,132)],lower=[(85,140),(90,140),(93,146),(93,153),(94,155),(94,159),(93,160),(84,160),(84,154),(85,150)],root=(86,129),k=(85,135),join=(89,143)),
'LF':dict(knee=[(104,130),(108,130),(109,132),(109,136),(108,139),(104,139),(103,133)],lower=[(101,140),(106,140),(106,153),(107,154),(107,160),(98,160),(97,159),(97,155),(99,153),(99,146)],root=(105,129),k=(106,135),join=(102,143)),
'RH':dict(root=(84,129),k=(84,131),join=(82,139)),
'LH':dict(root=(107,129),k=(107,131),join=(109,139))},
'n':{
'LH':dict(knee=[(84,133),(88,133),(88,144),(84,145),(83,142),(83,136)],lower=[(84,145),(89,145),(91,150),(91,153),(92,154),(92,160),(83,160),(83,154),(84,151)],root=(86,129),k=(86,139),join=(87,146)),
'RH':dict(knee=[(103,133),(107,133),(108,136),(108,142),(107,145),(103,144)],lower=[(102,145),(107,145),(107,151),(108,154),(108,160),(99,160),(99,154),(100,153),(100,150)],root=(105,129),k=(105,139),join=(104,146)),
'LF':dict(knee=[(82,122),(85,122),(85,128),(82,128)],lower=[(80,129),(83,129),(83,140),(80,140)],root=(83,121),k=(83,125),join=(82,131)),
'RF':dict(knee=[(106,122),(109,122),(109,128),(106,128)],lower=[(108,129),(111,129),(111,140),(108,140)],root=(108,121),k=(108,125),join=(109,131))}}

def save(a,p):Image.fromarray(a).save(R/p)
def rect(x0,y0,x1,y1):return (X>=x0)&(X<=x1)&(Y>=y0)&(Y<=y1)
def sources(v):
 ref=load(R/f'stills/{v}.png');parts={};used=np.zeros((192,192),bool);tail=np.zeros_like(ref)
 if v=='n':
  # Straight native tail assembly: complete steel plates, violet bands, gold tip.
  tm=rect(89,129,102,149)|rect(92,150,99,150)|rect(94,151,97,151)
  tail=b.piece(ref,tm);used|=tm
 for n,q in D[v].items():
  if 'lower' not in q:continue
  parts[n]={}
  for p in ['knee','lower']:
   m=b.mask(q[p])&~used&(ref[:,:,3]>0)
   # Chest and tail paint belongs to the pinned chest or whole tail, never a leg.
   m &= ~np.logical_or.reduce([np.all(ref[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['fff4d6','f0d27a','b8923a']])
   parts[n][p]=b.piece(ref,m);used|=m
 if v=='s':
  # Hidden hind shins/feet completed from native five-column steel toe blocks.
  # Crop/translate only: the still exposes just the lateral half of each rear foot.
  for n,srcn,x0,x1,dx in [('RH','RF',84,88,-4),('LH','LF',103,107,4)]:
   lower=b.piece(ref,rect(x0,147,x1,160));lower=old.dark(b.shift(lower,dx,-11))
   knee=b.piece(ref,rect(82 if n=='RH' else 104,132,87 if n=='RH' else 109,138));knee=old.dark(b.shift(knee,-1 if n=='RH' else 1,-4))
   parts[n]={'lower':lower,'knee':knee}
  used |= rect(80,140,84,149)|rect(107,140,111,149)
 body=b.piece(ref,~used)
 if v=='s':
  # Keep the native full chest, all shading and seams, including its taper.
  body[Y>=147]=0
  body[rect(80,140,89,146)&~np.logical_or.reduce([np.all(ref[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['fff4d6','f0d27a','b8923a']])]=0
  body[rect(102,140,111,146)&~np.logical_or.reduce([np.all(ref[:,:,:3]==list(bytes.fromhex(h)),axis=2) for h in ['fff4d6','f0d27a','b8923a']])]=0
 else:
  body[Y>=129]=0
 for n,pp in parts.items():
  q=D[v][n];q['sole']=b.support(pp['lower']).tolist()
  for p,a in pp.items():save(a,f'source/{v}_{n}_{p}.png')
 save(body,f'source/{v}_body.png');save(tail,f'source/{v}_tail.png')
 return ref,parts,body,tail

def band(a,p0,p1,width=5,far=False):
 old.band(a,p0,p1,width,far)

def make(v):
 ref,parts,body,tail=sources(v);frames=[];rig=[]
 for f in range(8):
  dip=int(f in [0,4]);ll={}
  for n,pp in parts.items():
   q=D[v][n];sole=np.array(q['sole']);target=np.array(T['views'][v]['visible_feet'][n]['frames'][f]['sole_centre'])
   delta=np.floor(target-sole+.5).astype(int);dx,dy=map(int,delta);kx=int(np.floor(dx*.5+.5));ky=int(np.floor((dy+dip)*.5+.5))
   root=np.array(q['root'])+[0,dip];kn=np.array(q['k'])+[kx,ky];jn=np.array(q['join'])+delta
   a=np.zeros_like(ref);far=n.endswith('H') if v=='s' else n.endswith('F')
   band(a,root,kn,width=5 if far else 6,far=far);band(a,kn,jn,width=4 if far else 6,far=far)
   raw=b.shift(pp['lower'],dx,dy);b.comp(a,raw);b.comp(a,b.shift(pp['knee'],kx,ky))
   bottom=int(sole[1]+dy);a[Y>bottom]=0;a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
   ll[n]=a;save(a,f'walk/layers/{v}_{n}_f{f}.png')
   rig.append(dict(foot=n,frame=f,delta=[dx,dy],knee_delta=[kx,ky],source_sole=sole.tolist(),target=target.tolist(),lift=T['paths'][n][f][1],hidden_in_still=False))
  a=np.zeros_like(ref);far=['RH','LH'] if v=='s' else ['LF','RF'];near=['RF','LF'] if v=='s' else ['LH','RH']
  for n in far:b.comp(a,ll[n])
  b.comp(a,b.shift(body,0,dip))
  for n in near:b.comp(a,ll[n])
  if v=='n':b.comp(a,b.shift(tail,0,int(f in [1,5])))
  cut={'s':130,'n':122}[v]+dip
  a[:cut]=b.shift(ref,0,dip)[:cut]
  # Fill only enclosed sockets, then one body-band slit pass; open leg gaps stay open.
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);st=b.shift(ref,0,dip)
  for y,x in zip(*np.where(holes)):
   a[y,x]=st[y,x] if st[y,x,3] else P['2e1a6e']
  sl=old.find_slits(a,ref,dip);done=set();filled=[]
  for x,y in sorted(sl,key=lambda p:(p[1],p[0])):
   # Only native pinned chest/rump sockets, never the gap between limbs.
   if (v=='s' and y<=146+dip and 89<=x<=102) or (v=='n' and y<=129+dip and 84<=x<=107):
    c=old.fill_colour(a,ref,dip,x,y,done,{P[h][:3] for h in ['e0c8ff','a46bff','6a3cc8','2e1a6e']});a[y,x]=tuple(c)+(255,);done.add((x,y));filled.append([x,y])
  save(a,f'walk/frames/{v}_f{f}.png');frames.append(a)
 rigfile=R/'rig.json';allrig=json.loads(rigfile.read_text()) if rigfile.exists() else json.loads((R.parent/'run1/rig.json').read_text());allrig[v]=rig;rigfile.write_text(json.dumps(allrig,indent=2))
 report=R/'REPORT.txt';report.write_text(report.read_text()+f'Part {3 if v=="s" else 4} {v}: eight native-pixel frames drawn; knee/lower rigid translations, vertical depth travel, diagonal pairs. Audit pending.\n')
 print(v,'source soles',{n:q['sole'] for n,q in D[v].items()})
if __name__=='__main__':make(sys.argv[1])
