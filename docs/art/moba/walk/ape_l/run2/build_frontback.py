from pathlib import Path
import json,hashlib,sys
import numpy as np
from PIL import Image
import build as b
R=b.R;Y,X=b.Y,b.X
load=lambda p:np.array(Image.open(p).convert('RGBA'))
# Explicit native contours; whole shields travel with forearms.
b.D['s']={
'RF':dict(poly=[(61,113),(67,115),(72,119),(76,124),(79,130),(80,145),(82,153),(80,161),(50,161),(49,144),(49,128),(53,119),(57,115)],root=(65,108),joint=(65,119),w=6,kind='arm'),
'LF':dict(poly=[(129,113),(123,115),(118,119),(114,124),(111,130),(110,145),(108,153),(110,161),(140,161),(141,144),(141,128),(137,119),(133,115)],root=(125,108),joint=(125,119),w=6,kind='arm'),
'RH':dict(poly=[(79,133),(91,133),(92,138),(91,144),(78,144)],root=(85,129),joint=(85,136),w=5,kind='leg'),
'LH':dict(poly=[(99,133),(111,133),(112,138),(111,144),(98,144)],root=(105,129),joint=(105,136),w=5,kind='leg')}
b.D['n']={
'LF':dict(poly=[(62,103),(64,104),(64,115),(67,119),(74,121),(77,128),(75,134),(71,137),(71,145),(55,145),(51,132),(51,111),(56,107)],root=(64,103),joint=(61,112),w=4,kind='arm'),
'RF':dict(poly=[(128,103),(126,104),(126,115),(123,119),(116,121),(113,128),(115,134),(119,137),(119,145),(135,145),(139,132),(139,111),(134,107)],root=(126,103),joint=(129,112),w=4,kind='arm'),
'LH':dict(poly=[(74,127),(80,127),(85,132),(88,140),(91,150),(92,158),(87,161),(67,161),(64,156),(65,150),(70,146),(69,137),(70,131)],root=(77,125),joint=(77,135),w=7,kind='leg'),
'RH':dict(poly=[(116,127),(110,127),(105,132),(102,140),(99,150),(98,158),(103,161),(123,161),(126,156),(125,150),(120,146),(121,137),(120,131)],root=(113,125),joint=(113,135),w=7,kind='leg')}

def make(v):
 ref=load(R/f'stills/{v}.png');used=np.zeros((192,192),bool);src={}
 for n in ['RF','LF','RH','LH']:
  m=b.mask(b.D[v][n]['poly'])&~used&(ref[:,:,3]>0)
  if v=='n' and n in ('LF','RF'):m &= Y<=144
  src[n]=b.piece(ref,m);used|=m
 body=b.piece(ref,~used);Image.fromarray(body).save(R/f'source/{v}_body.png')
 for n,a in src.items():Image.fromarray(a).save(R/f'source/{v}_{n}.png')
 rig=json.loads((R/'rig.json').read_text());rig[v]=[];frames=[]
 for f in range(8):
  dip=int(f in [0,4]);layers={}
  for n,s in src.items():
   sole=b.contact(s,v,n);target=np.array(b.T['views'][v]['visible_feet'][n]['frames'][f]['sole_centre']);dx,dy=np.floor(target-sole+.5).astype(int)
   a=b.socket(b.D[v][n],dx,dy,dip);raw=b.shift(s,dx,dy);b.comp(a,raw);bottom=int(sole[1]+dy);a[Y>bottom]=0;a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
   layers[n]=a;Image.fromarray(a).save(R/f'walk/layers/{v}_{n}_f{f}.png')
   off,lift=b.T['paths'][n][f];rig[v].append(dict(foot=n,frame=f,delta=[int(dx),int(dy)],source_sole=sole.tolist(),target=target.tolist(),lift=lift,ground_row=bottom+lift,hidden_in_still=False))
  a=np.zeros_like(ref)
  # Socket contours sit behind pinned body paint, as in run1.
  for n in layers:
   q=next(q for q in rig[v] if q['frame']==f and q['foot']==n);b.comp(a,b.socket(b.D[v][n],*q['delta'],dip))
  if v=='s':
   for n in ['RH','LH']:
    q=next(q for q in rig[v] if q['frame']==f and q['foot']==n);b.comp(a,b.shift(src[n],*q['delta']))
   b.comp(a,b.shift(body,0,dip))
   for n in ['RF','LF']:
    q=next(q for q in rig[v] if q['frame']==f and q['foot']==n);b.comp(a,b.shift(src[n],*q['delta']))
  else:
   for n in ['RF','LF']:
    q=next(q for q in rig[v] if q['frame']==f and q['foot']==n);b.comp(a,b.shift(src[n],*q['delta']))
   b.comp(a,b.shift(body,0,dip))
   for n in ['RH','LH']:
    q=next(q for q in rig[v] if q['frame']==f and q['foot']==n);b.comp(a,b.shift(src[n],*q['delta']))
  cut={'s':108,'n':104}[v]+dip;a[:cut]=b.shift(ref,0,dip)[:cut]
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);a[holes]=b.P['22301d']
  frames.append(a);Image.fromarray(a).save(R/f'walk/frames/{v}_f{f}.png')
 (R/'rig.json').write_text(json.dumps(rig,indent=2));return frames
if __name__=='__main__':
 v=sys.argv[1];fr=make(v);existing={vv:[load(R/f'walk/frames/{vv}_f{f}.png') for f in range(8)] for vv in ['ne','s','n'] if (R/f'walk/frames/{vv}_f0.png').exists()};b.boards(existing)
 p=R/'REPORT.txt';p.write_text(p.read_text()+f'Part {2 if v=="s" else 3}: {v} native frames and preview built; checks underway.\n')
 print(v, {n:b.support(load(R/f'source/{v}_{n}.png')).tolist() for n in b.D[v]})
