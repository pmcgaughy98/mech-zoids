"""lobster-walk35-run1. Native part/row-band method reused from hippo/fennec.
Read-only originals; every write is beneath this script. Run python -B.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,ast
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import native as b
R=Path(__file__).resolve().parent
T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192))
load=lambda p:np.array(Image.open(p).convert('RGBA'))
save=lambda a,p:Image.fromarray(a).save(R/p)
P={h:tuple(bytes.fromhex(h))+(255,) for h in '141218 26262e 34343e 555562 7e7e8e 9a9aa6 b8b8c2 eeeef2 6a0a10 c41216 ee2c26 f85a4a 86e8f8 d4fcff'.split()}
def rect(x0,y0,x1,y1):return (X>=x0)&(X<=x1)&(Y>=y0)&(Y<=y1)
# Traced contours exclude each fixed ball and all claw-arm pixels.
D={
'e':{
'R3':dict(poly=[(73,138),(84,138),(87,141),(86,148),(88,152),(86,156),(83,158),(74,158),(71,154),(71,150),(73,148)],top=138,band=(139,144),ft=150,root=(79,136)),
'R2':dict(poly=[(94,140),(104,140),(106,142),(106,151),(108,155),(107,158),(104,160),(96,160),(92,156),(92,152),(94,150)],top=140,band=(141,146),ft=153,root=(100,138)),
'R1':dict(poly=[(112,140),(123,138),(126,141),(127,147),(129,150),(130,154),(127,158),(115,158),(111,155),(111,151),(113,148)],top=140,band=(140,145),ft=151,root=(119,137))},
'se':{
'R3':dict(poly=[(57,103),(65,105),(68,108),(66,113),(63,118),(61,122),(54,122),(51,119),(51,115),(54,112),(55,108)],top=103,band=(104,109),ft=114,root=(63,101)),
'R2':dict(poly=[(64,119),(73,120),(76,124),(74,130),(74,135),(72,139),(68,141),(60,141),(57,138),(57,132),(60,129),(61,124)],top=119,band=(120,126),ft=132,root=(71,117)),
'R1':dict(poly=[(78,130),(87,130),(91,134),(91,141),(92,147),(90,150),(86,153),(78,153),(74,150),(73,147),(76,143),(76,136)],top=130,band=(131,137),ft=146,root=(84,128))},
'ne':{
'R3':dict(poly=[(108,124),(118,122),(122,126),(122,134),(124,139),(122,143),(118,144),(110,144),(106,140),(106,136),(108,132)],top=124,band=(124,130),ft=137,root=(113,121)),
'R2':dict(poly=[(123,113),(132,111),(137,114),(137,123),(139,129),(137,133),(133,134),(126,134),(121,131),(122,126),(123,119)],top=113,band=(113,119),ft=127,root=(129,111)),
'R1':dict(poly=[(136,104),(143,103),(146,106),(148,112),(149,118),(147,121),(144,122),(138,122),(134,119),(135,113),(135,109)],top=104,band=(104,110),ft=116,root=(138,102))}
}
# Foreground claw/arm contour follows the exact still, including the arm over R1.
CLAW={
'e':[(123,129),(129,127),(136,134),(143,129),(151,133),(160,145),(161,153),(154,158),(143,158),(134,155),(131,150),(130,145),(124,141),(122,136)],
'se':[(89,121),(95,120),(101,124),(102,129),(107,134),(111,136),(123,133),(128,126),(130,119),(132,114),(137,112),(141,116),(144,122),(144,128),(148,133),(149,144),(145,152),(138,155),(130,152),(123,151),(118,157),(112,161),(101,161),(94,158),(91,151),(93,143),(92,139),(90,135)],
'ne':[(130,88),(140,90),(147,94),(150,99),(151,105),(147,111),(143,110),(144,106),(144,101),(139,98),(133,99),(130,95)]}
# Torso outline behind moving limb masks. No fill outside this contour.
TORSO={
'e':[(69,117),(91,104),(116,109),(132,127),(135,143),(127,146),(113,146),(102,147),(90,147),(78,146),(68,143)],
'se':[(60,83),(74,80),(100,91),(126,109),(133,129),(123,141),(104,147),(91,143),(80,135),(73,124),(68,115),(63,106),(59,96)],
'ne':[(83,90),(107,80),(133,94),(141,111),(135,120),(123,130),(112,138),(102,140),(91,138),(79,125),(75,108)]}
# Entire far set lies under the shell; offsets estimated from the still's body depth.
FAR={'e':(0,-20),'se':(24,-17),'ne':(-22,-19)}
# Exact complete native feet, including toe recesses and outside shadow edges.
FOOT_ROWS={
'e':{
'R3':[(150,72,85),(151,71,85),(152,71,86),(153,70,87),(154,70,87),(155,71,86),(156,71,85),(157,73,84),(158,73,83)],
'R2':[(152,92,107),(153,92,108),(154,91,107),(155,91,108),(156,91,108),(157,92,108),(158,92,107),(159,94,106),(160,95,105)],
'R1':[(151,112,129),(152,112,130),(153,112,130),(154,112,130),(155,112,129),(156,113,129),(157,113,128),(158,115,128)]},
'se':{
'R3':[(114,53,63),(115,52,63),(116,52,63),(117,52,63),(118,52,63),(119,52,62),(120,53,62),(121,54,62),(122,56,62),(123,58,58)],
'R2':[(132,59,74),(133,58,74),(134,58,76),(135,58,76),(136,58,76),(137,58,76),(138,58,74),(139,59,73),(140,63,71),(141,63,70)],
'R1':[(145,74,91),(146,73,91),(147,73,91),(148,73,91),(149,73,91),(150,73,91),(151,74,89),(152,75,88),(153,77,86)]},
'ne':{
'R3':[(137,107,122),(138,105,122),(139,106,123),(140,106,123),(141,106,123),(142,107,123),(143,108,122),(144,109,121)],
'R2':[(127,122,138),(128,122,139),(129,122,139),(130,122,139),(131,122,139),(132,124,138),(133,125,137),(134,127,133)],
'R1':[(116,136,145),(117,135,145),(118,135,145),(119,135,145),(120,135,145),(121,136,144),(122,137,142)]}}
REMOVE={
'e':{'R3':(70,138,89,158),'R2':(90,140,110,160),'R1':(110,139,131,158)},
'se':{'R3':(51,103,68,123),'R2':(57,119,77,141),'R1':(72,130,94,153)},
'ne':{'R3':(105,123,124,144),'R2':(121,112,140,134),'R1':(134,103,149,122)}}
BALL={
'e':{'R3':[(75,133),(81,131),(85,134),(86,138),(84,141),(76,141),(73,138)],'R2':[(96,135),(101,134),(104,136),(105,141),(102,143),(95,142),(93,139)],'R1':[(114,135),(120,133),(123,136),(124,140),(121,142),(114,142),(111,139)]},
'se':{'R3':[(61,98),(65,97),(67,100),(66,104),(64,106),(59,104),(59,101)],'R2':[(67,113),(72,112),(75,115),(75,119),(73,123),(68,122),(64,119),(64,116)],'R1':[(81,124),(86,123),(90,126),(91,131),(87,134),(81,133),(77,130),(78,126)]},
'ne':{'R3':[(110,117),(115,116),(118,119),(119,123),(116,126),(110,126),(107,123),(107,120)],'R2':[(126,109),(131,108),(134,110),(135,114),(132,117),(126,116),(123,114),(123,111)],'R1':[(136,100),(140,99),(143,101),(143,104),(141,107),(136,106),(134,103)]}}
def sources(v):
 ref=load(R/f'stills/{v}.png');parts={};used=np.zeros((192,192),bool)
 cm=b.mask(CLAW[v])&(ref[:,:,3]>0)
 bm=np.logical_or.reduce([b.mask(p) for p in BALL[v].values()])
 grey=np.logical_or.reduce([np.all(ref==P[h],axis=2) for h in ['34343e','555562','7e7e8e','9a9aa6','b8b8c2','eeeef2','26262e','141218']]);bm &= grey
 if v=='se':bm &= ~rect(63,120,68,123)
 # Do not assign near red foot/band pixels to a large claw bounding polygon.
 if v=='e':cm &= ~rect(110,145,130,161)
 if v=='se':cm &= ~rect(72,141,91,154)
 fg=b.piece(ref,cm)
 for n,q in D[v].items():
  m=b.mask(q['poly'])&~cm&~used&(ref[:,:,3]>0)
  fm=np.zeros((192,192),bool)
  for yy,l,r in FOOT_ROWS[v][n]:fm[yy,l:r+1]=True
  fm &= (ref[:,:,3]>0)&~cm
  q['ft']=min(row[0] for row in FOOT_ROWS[v][n])
  m=((m&(Y<q['ft']))|fm)&~bm
  # Native complete outer dark/red contour at the soles.
  part=b.piece(ref,m);foot=b.piece(part,Y>=q['ft']);parts[n]={'native':part,'foot':foot}
  used|=rect(*REMOVE[v][n])&~cm;q['pixel_support']=b.support(foot).tolist()
  label=T['views'][v]['visible_feet'][n]['still_sole'];q['label_sole']=[(label[0]+label[1])/2,label[2]];q['sole']=b.support(foot).tolist()
  xx=np.where(m)[1];q['span']=[int(xx.min()),int(xx.max())]
 # Remove static leg shadows below each source part as well.
 body=b.piece(ref,~used&~cm&~bm)
 torso=b.mask(TORSO[v]);gun=[P[h] for h in ['26262e','34343e','555562','7e7e8e']]
 fill=used&torso&(Y<({'e':150,'se':143,'ne':138}[v]))
 for yy,xx in zip(*np.where(fill)):
  # Continue the native row's nearest unobscured body shade, with darkest
  # body recess used immediately under ball joints; never extend the belly.
  choices=[(abs(x-xx),x) for x in range(max(0,xx-20),min(192,xx+21)) if body[yy,x,3] and tuple(body[yy,x]) in gun and torso[yy,x]]
  body[yy,xx]=body[yy,min(choices)[1]] if choices else P['26262e']
 for n,pp in parts.items():
  for p,a in pp.items():save(a,f'source/{v}_{n}_{p}.png')
 # Clone native far legs, darker ramp, as in hippo/fennec. The shell occludes them.
 dx,dy=FAR[v]
 for r in ['R3','R2','R1']:
  n='L'+r[1];parts[n]={p:b.shift(a,dx,dy) for p,a in parts[r].items()}
  for p,a in parts[n].items():
   old=a.copy()
   for h,j in [('eeeef2','b8b8c2'),('b8b8c2','9a9aa6'),('9a9aa6','7e7e8e'),('7e7e8e','555562'),('f85a4a','ee2c26'),('ee2c26','c41216'),('c41216','6a0a10')]:a[np.all(old==P[h],axis=2)]=P[j]
  q=dict(D[v][r]);q['root']=(np.array(q['root'])+[dx,dy]).tolist();q['sole']=(np.array(q['sole'])+[dx,dy]).tolist();q['top']+=dy;q['band']=tuple(y+dy for y in q['band']);q['ft']+=dy;D[v][n]=q
  for p,a in parts[n].items():save(a,f'source/{v}_{n}_{p}.png')
 sockets=b.piece(ref,bm)
 # Native fixed socket backs, including the original dark rim above each
 # moving band, belong to the joint, not to the trunk underside.
 jointbacks={'e':[(73,131,86,137),(93,133,106,139),(111,132,124,138)],'se':[(57,96,68,102),(63,112,77,118),(77,122,91,129)],'ne':[(106,115,120,122),(122,107,135,112),(133,98,144,103)]}
 for box in jointbacks[v]:
  mm=rect(*box)&(ref[:,:,3]>0)&~cm
  b.comp(sockets,b.piece(ref,mm));body[mm]=0
 # The complete segmented tail is a separate pinned source; its shape is not
 # part of the body's belly-line test. It follows the same dip, never a lag.
 tailmask={'e':b.mask([(32,128),(46,120),(60,119),(66,113),(73,113),(73,132),(71,140),(75,146),(70,149),(38,149),(31,141)]),
 'se':b.mask([(46,69),(58,65),(67,68),(72,74),(80,79),(85,88),(80,96),(72,99),(64,95),(60,87),(54,84),(49,78)]),
 'ne':b.mask([(42,141),(54,132),(64,128),(74,124),(79,116),(88,112),(96,116),(103,127),(105,140),(103,151),(95,160),(59,162),(43,156)])}[v]
 if v=='e':tailmask &= X<71
 if v=='ne':tailmask &= ~((X>=103)&(Y>=135))
 tail=b.piece(body,tailmask);body[tailmask]=0;save(tail,f'source/{v}_tail.png')
 # Remove only reconstruction below the two specifically reviewed belly
 # corners (not native plate paint). Preserve the native join foreground.
 if v in ['e','se','ne']:
  spans=[tuple(D[v][n]['span']) for n in ['R3','R2','R1']]
  for pass_no in range(4):
   for l,r in spans:
    ly=np.where(body[:,l-1,3]>0)[0];ry=np.where(body[:,r+1,3]>0)[0]
    if len(ly) and len(ry):
     for xx in range(l,r+1):
      limit=np.interp(xx,[l-1,r+1],[ly.max(),ry.max()])+1
      body[(Y[:,xx]>limit)&fill[:,xx],xx]=0
 save(sockets,f'source/{v}_sockets.png')
 
 if v=='e':body[146,73:79]=0
 save(body,f'source/{v}_body.png');save(fg,f'source/{v}_claws.png');save(b.piece(ref,fill),f'source/{v}_body_reconstruction_area.png')
 return ref,parts,body,fg,sockets,tail

def rowband(dst,src,ya,yb,na,nb,xa,xb):
 # Re-draw native bevel/shade row profiles on an integer staircase. No pixel
 # rotation, filtering or resampling; the native foot is handled separately.
 for yy in range(int(na),int(nb)+1):
  t=(yy-na)/max(1,nb-na);sy=int(np.floor(ya+(yb-ya)*t+.5));dx=int(np.floor(xa+(xb-xa)*t+.5))
  xs=np.where(src[sy,:,3]>0)[0];xs=xs[(xs+dx>=0)&(xs+dx<192)]
  if 0<=yy<192:dst[yy,xs+dx]=src[sy,xs]

def limb(pp,q,delta,dip):
 dx,dy=map(int,delta);a=np.zeros_like(pp['native']);top=q['top'];ba,bb=q['band'];ft=q['ft'];kdy=int(np.floor((dy+dip)*.48+.5));kdx=int(np.floor(dx*.5+.5))
 # A fixed ball covers the uppermost join. Knee band and lit edge remain native.
 rowband(a,pp['native'],top,ba-1,top+dip,ba+kdy-1,0,kdx)
 rowband(a,pp['native'],ba,bb,ba+kdy,bb+kdy,kdx,kdx)
 rowband(a,pp['native'],bb+1,ft-1,bb+kdy+1,ft+dy-1,kdx,dx)
 b.comp(a,b.shift(pp['foot'],dx,dy))
 # Measure projected two-link reach between ball, knee and ankle; retained in rig.
 root=np.array(q['root'])+[0,dip];k0=np.array([q['sole'][0],(ba+bb)/2]);ank0=np.array([q['sole'][0],ft]);kn=k0+[kdx,kdy];ank=ank0+[dx,dy]
 length0=np.linalg.norm(k0-np.array(q['root']))+np.linalg.norm(ank0-k0);length=np.linalg.norm(kn-root)+np.linalg.norm(ank-kn)
 return a,[kdx,kdy],float(length-length0)

def tidy_connectors(a,ll,parts,rig,pinned,cut,limit):
 from scipy.ndimage import label
 def pieces(im):
  out=[]
  for c in set(map(tuple,im[im[:,:,3]>0])):
   labs,num=label(np.all(im==c,axis=2)&(Y>=100)&(Y<=164),np.ones((3,3)));sizes=np.bincount(labs.ravel())
   for i in np.where((sizes>0)&(sizes<=2))[0]:
    if i:out.append((c,list(zip(*np.where(labs==i)))))
  return out
 immutable=(pinned[:,:,3]>0)&np.all(a==pinned,axis=2);immutable[:cut]=True
 for rr in rig:
  raw=b.shift(parts[rr['foot']]['foot'],*rr['delta']);immutable|=raw[:,:,3]>0
 mutable=(a[:,:,3]>0)&~immutable
 owner=np.full((192,192),'',dtype='<U2')
 for n in ['L3','L2','L1','R3','R2','R1']:owner[(ll[n][:,:,3]>0)&np.all(a==ll[n],axis=2)]=n
 mutable&=owner!=''
 ramps=[set(P[h] for h in ['141218','26262e','34343e','555562','7e7e8e','9a9aa6','b8b8c2','eeeef2']),set(P[h] for h in ['6a0a10','c41216','ee2c26','f85a4a'])]
 def count_colour(c):
  labs,num=label(np.all(a[100:165]==c,axis=2),np.ones((3,3)));sz=np.bincount(labs.ravel())[1:]
  return int(((sz>0)&(sz<=2)).sum())
 edits=[]
 for _ in range(100):
  old=pieces(a)
  if len(old)<=limit:break
  best=None
  for c,pts in old:
   if not all(mutable[y,x] for y,x in pts):continue
   ramp=next((r for r in ramps if c in r),{c});options=set()
   for y,x in pts:
    for yy in range(max(0,y-1),min(192,y+2)):
     for xx in range(max(0,x-1),min(192,x+2)):
      nc=tuple(a[yy,xx])
      if nc in ramp and nc!=c:options.add(nc)
   for nc in options:
    before=count_colour(c)+count_colour(nc)
    for y,x in pts:a[y,x]=nc
    gain=before-count_colour(c)-count_colour(nc)
    for y,x in pts:a[y,x]=c
    if gain>0:
     key=(gain,-sum(abs(int(c[k])-int(nc[k])) for k in range(3)))
     if best is None or key>best[0]:best=(key,c,pts,nc)
  if best is None:break
  _,c,pts,nc=best
  for y,x in pts:a[y,x]=nc;ll[owner[y,x]][y,x]=nc
  edits.append(dict(pixels=[[int(x),int(y)] for y,x in pts],old=bytes(c[:3]).hex(),new=bytes(nc[:3]).hex()))
 return edits

def boards(v,ref,frames):
 sel=b.load_selout();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);bg=(62,71,67,255)
 board=Image.new('RGBA',(768*9,798),bg)
 box={'e':(64,123,162,164),'se':(46,94,151,164),'ne':(88,95,153,148)}[v];w=(box[2]-box[0])*5;h=(box[3]-box[1])*5
 zoom=Image.new('RGBA',(w*9,h+30),bg)
 for j,a in enumerate([ref]+frames):
  tile=Image.fromarray(sel(a)[0]);board.alpha_composite(tile.resize((768,768),Image.Resampling.NEAREST),(j*768,30));ImageDraw.Draw(board).text((j*768+8,5),v+' '+('STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
  zoom.alpha_composite(tile.crop(box).resize((w,h),Image.Resampling.NEAREST),(j*w,30));ImageDraw.Draw(zoom).text((j*w+8,5),v+' '+('STILL' if j==0 else f'f{j-1}'),font=font,fill='white')
 board.convert('RGB').save(R/f'{v}_board.png');zoom.convert('RGB').save(R/f'{v}_legs_zoom.png')
 for j in range(3):zoom.crop((j*3*w,0,(j+1)*3*w,h+30)).convert('RGB').save(R/f'{v}_legs_part{j}.png')
 pics=[]
 for a in frames:
  im=Image.new('RGBA',(768,768),bg);im.alpha_composite(Image.fromarray(sel(a)[0]).resize((768,768),Image.Resampling.NEAREST));pics.append(im.convert('RGB'))
 # GIF ticks are 10ms, so alternating120/130ms expresses the requested 1s cycle.
 pics[0].save(R/f'{v}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
 rgba=[Image.fromarray(a) for a in frames];rgba[0].save(R/f'{v}_preview.png',save_all=True,append_images=rgba[1:],duration=125,loop=0,disposal=0,blend=0)
 for suffix in ['board.png','legs_zoom.png']:
  ims=[Image.open(R/f'{vv}_{suffix}').convert('RGB') for vv in ['e','se','ne'] if (R/f'{vv}_{suffix}').exists()];out=Image.new('RGB',(max(i.width for i in ims),sum(i.height for i in ims)),bg[:3]);yy=0
  for im in ims:out.paste(im,(0,yy));yy+=im.height
  out.save(R/suffix)

def make(v):
 for d in ['source','walk/frames','walk/layers']:(R/d).mkdir(parents=True,exist_ok=True)
 ref,parts,body,fg,sockets,tail=sources(v);frames=[];rig=[];vt=T['views'][v]
 for f in range(8):
  dip=int(f in [0,4]);ll={}
  for n,pp in parts.items():
   q=D[v][n];sole=np.array(q['sole']);off,lift=T['paths'][n][f];target=sole+off*np.array(vt['u'])*vt['f']-[0,lift]
   # Native source sole may be half a pixel from supplied guide centre.
   if n in vt['visible_feet']:target=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre'])
   delta=np.floor(target+[0,lift]-sole+.5).astype(int)-[0,lift]
   a,kd,le=limb(pp,q,delta,dip);ll[n]=a;save(a,f'walk/layers/{v}_{n}_f{f}.png')
   rig.append(dict(foot=n,frame=f,delta=delta.tolist(),knee_delta=kd,source_sole=sole.tolist(),target=target.tolist(),lift=lift,projected_length_change=le,hidden_in_still=n.startswith('L')))
  a=np.zeros_like(ref)
  for n in ['L3','L2','L1']:b.comp(a,ll[n])
  pin=b.shift(body,0,dip);front=b.shift(fg,0,dip);b.comp(a,b.shift(tail,0,dip));b.comp(a,pin);b.comp(a,b.shift(sockets,0,dip))
  for n in ['R3','R2','R1']:b.comp(a,ll[n])
  b.comp(a,front)
  # Full canvas above the first moving row is the approved image, including alpha.
  cut=min(q['top'] for n,q in D[v].items() if n.startswith('R'))+dip;a[:cut]=b.shift(ref,0,dip)[:cut]
  # Fill only enclosed join holes, preserving open interleg negative space.
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)
  for yy,xx in zip(*np.where(holes)):a[yy,xx]=pin[yy,xx] if pin[yy,xx,3] else P['26262e']
  protected=pin.copy();b.comp(protected,b.shift(tail,0,dip));b.comp(protected,b.shift(sockets,0,dip));b.comp(protected,front)
  from verify import specks
  edits=tidy_connectors(a,ll,parts,[rr for rr in rig if rr['frame']==f],protected,cut,specks(ref)+2)
  for n,layer in ll.items():save(layer,f'walk/layers/{v}_{n}_f{f}.png')
  (R/f'walk/layers/{v}_join_edits_f{f}.json').write_text(json.dumps(edits))
  save(a,f'walk/frames/{v}_f{f}.png');save(pin,f'walk/layers/{v}_body_f{f}.png');save(b.shift(tail,0,dip),f'walk/layers/{v}_tail_f{f}.png');save(b.shift(sockets,0,dip),f'walk/layers/{v}_sockets_f{f}.png');save(front,f'walk/layers/{v}_claws_f{f}.png');frames.append(a)
 path=R/'rig.json';old=json.loads(path.read_text()) if path.exists() else {};old[v]=rig;path.write_text(json.dumps(old,indent=2))
 path=R/'REPORT.txt';lines=path.read_text().splitlines() if path.exists() else ['lobster-walk35-run1; tokens unavailable.','Native hippo/fennec method reused; R1/front, R2/middle, R3/rear near right. Labels retained.','Tripod A L1/R2/L3 planted f0-3; B R1/L2/R3 planted f4-7; body/claws/tail dip f0/f4.']
 lines=[s for s in lines if not s.startswith(v+':')];lines.append(v+': eight native frames and source/layers drawn; pixel audit/visual review pending.');path.write_text('\n'.join(lines)+'\n')
 boards(v,ref,frames);print(v,'drawn', {n:q['sole'] for n,q in D[v].items()})
if __name__=='__main__':
 for v in sys.argv[1:] or ['e','se','ne']:make(v)
