"""hippo-walk35-run1. Native-part method reused from fennec/ape walks.
Only output beside this script. All input scripts/stills are read-only.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json, ast, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import native as b
R=Path(__file__).resolve().parent
T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192))
P={h:tuple(bytes.fromhex(h))+(255,) for h in '141218 211e27 26183f 3d3a44 4a347e 4e4b55 7258b4 8a8892 a990e0 c0bfc6 c4720e e4e4ea ffc23c fff1c4'.split()}
load=lambda p:np.array(Image.open(p).convert('RGBA'))
save=lambda a,p:Image.fromarray(a).save(R/p)
def rect(x0,y0,x1,y1):return (X>=x0)&(X<=x1)&(Y>=y0)&(Y<=y1)
# Contours are traced in the approved still. Discs never enter these masks.
D={
 'e':{
  'RH':dict(knee=[(58,142),(63,142),(66,144),(66,146),(58,146)],lower=[(57,146),(66,146),(70,148),(73,149),(76,151),(77,155),(74,158),(50,158),(49,152),(51,149),(53,148),(53,146)],root=(60,140),k=(61,144),join=(61,147),w=6),
  'RF':dict(knee=[(100,143),(105,143),(108,145),(108,147),(100,148)],lower=[(100,148),(108,148),(108,151),(113,152),(117,154),(116,158),(112,160),(99,160),(94,157),(94,151),(96,149)],root=(102,142),k=(104,146),join=(104,149),w=6)},
 'se':{
  'RH':dict(knee=[(50,118),(56,118),(56,122),(50,122)],lower=[(50,122),(56,122),(60,125),(61,127),(63,128),(63,134),(60,135),(49,135),(46,132),(46,127),(48,124)],root=(52,116),k=(53,120),join=(54,123),w=5),
  'RF':dict(knee=[(79,139),(84,138),(89,140),(90,143),(88,145),(80,145)],lower=[(79,145),(88,144),(91,146),(91,150),(96,152),(98,157),(95,160),(78,160),(74,157),(72,152),(73,149),(76,149)],root=(82,137),k=(84,142),join=(85,146),w=6)},
 'ne':{
  'RH':dict(knee=[(95,139),(100,139),(104,141),(105,145),(103,148),(95,148)],lower=[(95,148),(103,148),(106,150),(108,152),(107,156),(104,158),(101,160),(86,160),(83,157),(83,153),(89,151),(94,151)],root=(98,138),k=(100,144),join=(100,149),w=6),
  'RF':dict(knee=[(124,119),(129,119),(131,122),(131,124),(125,125),(122,123)],lower=[(123,124),(130,124),(133,126),(135,128),(136,132),(132,135),(130,136),(118,136),(116,133),(116,130),(121,128)],root=(126,118),k=(127,122),join=(127,125),w=5),
  'LH':dict(knee=[(52,134),(56,134),(58,137),(58,140),(52,140)],lower=[(51,140),(57,140),(59,142),(59,145),(66,146),(69,148),(70,152),(66,154),(50,154),(47,151),(47,147),(49,144)],root=(55,133),k=(55,137),join=(55,141),w=5)}
}
# Full pinned disc masks, also used to prevent steel joins entering violet housings.
DISCS={
 'e':[[(52,130),(57,128),(63,128),(67,130),(69,134),(68,138),(65,141),(58,142),(53,139),(51,135)],[(94,128),(99,126),(104,127),(109,130),(111,136),(108,141),(104,144),(98,143),(93,140),(91,134)]],
 'se':[[(47,105),(51,104),(55,108),(56,113),(53,117),(48,118),(46,114)],[(76,122),(80,120),(86,122),(89,126),(89,134),(85,139),(80,140),(75,136),(73,129)]],
 'ne':[[(90,133),(96,130),(102,132),(106,137),(106,143),(103,147),(96,149),(91,146),(88,140)],[(122,109),(127,107),(131,110),(133,114),(131,119),(127,122),(122,120),(120,115)],[(53,119),(60,117),(67,119),(72,122),(73,126),(69,130),(60,133),(53,130),(50,125)]]}

def dark(a):
 out=a.copy()
 for h,j in [('a990e0','7258b4'),('7258b4','4a347e'),('4a347e','26183f'),('e4e4ea','c0bfc6'),('c0bfc6','8a8892'),('8a8892','4e4b55'),('4e4b55','3d3a44')]:out[np.all(a==P[h],axis=2)]=P[j]
 return out

def sources(v):
 ref=load(R/f'stills/{v}.png');parts={};used=np.zeros((192,192),bool)
 discs=np.logical_or.reduce([b.mask(q) for q in DISCS[v]])&(ref[:,:,3]>0)
 for n,q in D[v].items():
  parts[n]={}
  for part in ['knee','lower']:
   mask=b.mask(q[part])&~discs&~used&(ref[:,:,3]>0)
   parts[n][part]=b.piece(ref,mask);used|=mask
 # Remove stationary fragments around the native foot contours, assigning them
 # to the complete lower block. Above the sole this includes its violet heel.
 extent={'e':{'RH':rect(47,148,78,161),'RF':rect(93,149,118,162)},
         'se':{'RH':rect(45,125,64,136),'RF':rect(71,149,101,162)},
         'ne':{'RH':rect(82,151,110,162),'RF':rect(116,128,138,138),'LH':rect(46,145,73,156)}}[v]
 for n,m in extent.items():
  extra=m&~used&~discs&(ref[:,:,3]>0);b.comp(parts[n]['lower'],b.piece(ref,extra));used|=extra
 # At the silhouettes the native heel meets the trunk without an alpha edge.
 # These row contours give the adjoining trunk pixels back to the pinned body.
 keepbody=np.zeros_like(used)
 if v=='se':
  keepbody|=rect(61,122,64,135)|rect(59,122,60,126)
 if v=='ne':
  keepbody|=rect(68,138,73,152)|rect(60,138,67,145)
  keepbody|=rect(116,124,120,130)
 for pp in parts.values():
  for part in pp:pp[part][keepbody]=0
 used[keepbody]=False
 if v=='se':
  # Full native front shin casing: the dark left rim moves with the shin.
  rim=rect(73,141,78,148)&~discs&(ref[:,:,3]>0)&~used
  b.comp(parts['RF']['lower'],b.piece(ref,rim));used|=rim
 if v=='e':
  rim=rect(51,144,57,147)&~discs&~used&(ref[:,:,3]>0)
  b.comp(parts['RH']['lower'],b.piece(ref,rim));used|=rim
 if v=='ne':
  for n,m in [('RF',rect(130,124,137,127)),('RH',rect(104,147,111,150))]:
   rim=m&~discs&~used&(ref[:,:,3]>0);b.comp(parts[n]['lower'],b.piece(ref,rim));used|=rim
 body=b.piece(ref,~used)
 # Hidden limbs are complete dark-ramp native joints, never cut-off peeks.
 hidden={'e':[('LH','RH',7,-7),('LF','RF',7,-8)],'se':[('LH','RH',44,-3),('LF','RH',76,22)],'ne':[('LF','RF',-36,-6)]}[v]
 for n,src,dx,dy in hidden:
  q=dict(D[v][src]);q.update({key:tuple(np.array(q[key])+[dx,dy]) for key in ['root','k','join']});q['hidden']=True;D[v][n]=q
  parts[n]={p:dark(b.shift(a,dx,dy)) for p,a in parts[src].items()}
 if v=='se':
  # Trace the native exposed LF heel/sole, excluding the steel jaw above it.
  peek=rect(134,150,141,150)|rect(130,151,141,151)|rect(128,152,141,152)|rect(125,153,141,153)|rect(122,154,141,158)
  body[peek]=0
  # The whole jaw remains a foreground occluder of LF in every pose.
  jaw=b.piece(ref,b.mask([(101,134),(106,129),(111,130),(113,140),(118,142),(140,137),(146,133),(145,143),(139,149),(129,153),(116,155),(105,149),(100,143)]))
  jaw[peek]=0
  b.comp(body,jaw)
 # Paint the trunk behind each socket before any limb moves. These small patches
 # continue existing purple shade bands and cannot create an inter-leg bridge.
 patches={'e':[(55,140,68,145),(96,141,111,146)],'se':[(49,116,57,120),(76,137,90,143)],'ne':[(92,141,104,148),(122,119,132,125),(51,133,59,140)]}[v]
 for x0,y0,x1,y1 in patches:
  for y in range(y0,y1+1):
   for x in range(x0,x1+1):
    if not body[y,x,3]:body[y,x]=P['26183f']
 # Keep every complete native disc/armour pixel on the pinned layer.
 b.comp(body,b.piece(ref,discs))
 for n,pp in parts.items():
  q=D[v][n];q['sole']=b.support(pp['lower']).tolist()
  for p,a in pp.items():save(a,f'source/{v}_{n}_{p}.png')
 save(body,f'source/{v}_body.png');save(b.piece(ref,discs),f'source/{v}_discs.png')
 return ref,parts,body,discs

def band(a,p0,p1,width,far=False):
 # Hand-defined steel profile: lit left bevel, middle steel, dark right seam.
 # The centre follows integer stair steps; no rotation, interpolation or scaling.
 x0,y0=map(int,p0);x1,y1=map(int,p1)
 if y1<y0:x0,y0,x1,y1=x1,y1,x0,y0
 for y in range(y0,y1+1):
  t=(y-y0)/max(1,y1-y0);cx=int(np.floor(x0+(x1-x0)*t+.5));l=cx-width//2;r=l+width
  a[y,l:r+1]=P['211e27'];a[y,l+1:r]=P['4e4b55' if far else '8a8892'];a[y,l+1:l+3]=P['8a8892' if far else 'c0bfc6'];a[y,r-1:r]=P['3d3a44']

def casing(a,p0,p1,width,far=False):
 x0,y0=map(int,p0);x1,y1=map(int,p1)
 if y1<y0:x0,y0,x1,y1=x1,y1,x0,y0
 for y in range(y0,y1+1):
  cx=int(np.floor(x0+(x1-x0)*(y-y0)/max(1,y1-y0)+.5));l=cx-width//2;r=l+width
  a[y,l:r+1]=P['211e27'];a[y,l+1:r]=P['26183f'];a[y,l+1:l+3]=P['26183f' if far else '4a347e']

def articulation(q,delta,dip,body,far):
 # The socket can pivot under its fixed round housing. Choose integer knee and
 # hidden attachment points that retain the two native link lengths, rather
 # than shortening a lifted leg into a straight telescoping rod.
 r0=np.array(q['root']);k0=np.array(q['k']);j0=np.array(q['join']);j=j0+delta
 l1=np.linalg.norm(k0-r0);l2=np.linalg.norm(j0-k0);half=np.floor((delta+[0,dip])*.5+.5).astype(int)
 best=None
 for rx in range(-3,4):
  for ry in range(-3,4):
   root=r0+[rx,ry+dip]
   if not far and not body[tuple((root-[0,dip])[::-1])][3]:continue
   for kx in range(-3,4):
    for ky in range(-2,3):
     kd=half+[kx,ky];kn=k0+kd;u=np.linalg.norm(kn-root);lo=np.linalg.norm(j-kn);err=abs(u+lo-l1-l2)
     if abs(u-l1)>1 or abs(lo-l2)>1 or err>1:continue
     score=(kx*kx+ky*ky)*4+rx*rx+ry*ry+err*.1
     if best is None or score<best[0]:best=(score,root,kn,kd,float(err),float(u-l1),float(lo-l2))
 if best is None:
  root=r0+[0,dip];kn=k0+half;return root,kn,half,float(abs(np.linalg.norm(kn-root)+np.linalg.norm(j-kn)-l1-l2)),None,None
 return best[1:]

def joint_cleanup(a,ref,body,parts,rig,dip):
 # Finish only the small shading/seam fragments at redrawn moving joins.
 # Approved body/discs, alpha, knee cores and the complete foot pads are locked.
 from collections import Counter
 from scipy.ndimage import label
 structure=np.ones((3,3),np.uint8)
 def colour_count(im,c):
  lab,num=label(np.all(im[120:165]==c,axis=2),structure);sizes=np.bincount(lab.ravel())[1:];return int(((sizes>0)&(sizes<=2)).sum())
 def bits(im):
  out=[]
  for c in set(map(tuple,im[im[:,:,3]>0])):
   lab,num=label(np.all(im[120:165]==c,axis=2),structure);sizes=np.bincount(lab.ravel())
   for i in np.where((sizes>0)&(sizes<=2))[0]:
    if i:
     yy,xx=np.where(lab==i);out.append((c,list(zip((yy+120).tolist(),xx.tolist()))))
  return out
 mutable=np.zeros((192,192),bool);kcore=np.zeros_like(mutable)
 for rr in rig:
  n=rr['foot'];dx,dy=rr['delta'];src=parts[n]['lower'];ys,xs=np.where(src[:,:,3]>0)
  mutable|=(X>=xs.min()+dx-2)&(X<=xs.max()+dx+2)&(Y>=ys.min()+dy-4)&(Y<rr['source_sole'][1]+dy-8)
  kn=b.shift(parts[n]['knee'],*rr['knee_delta']);kcore|=np.logical_or.reduce([np.all(kn==P[h],axis=2) for h in ['e4e4ea','c0bfc6','8a8892']])
 pinned=b.shift(body,0,dip);mutable&=~((pinned[:,:,3]>0)&np.all(a==pinned,axis=2));mutable&=(a[:,:,3]>0)&~kcore
 limit=len(bits(ref))+2;edits=[]
 ramps=[set(P[h] for h in ['141218','211e27','26183f','3d3a44','4e4b55']),set(P[h] for h in ['4e4b55','8a8892','c0bfc6','e4e4ea']),set(P[h] for h in ['26183f','4a347e','7258b4','a990e0'])]
 for _ in range(80):
  pcs=bits(a);count=len(pcs)
  if count<=limit:break
  best=None
  for c,cc in pcs:
   if not all(mutable[y,x] for y,x in cc):continue
   ramp=set().union(*(r for r in ramps if c in r));near=Counter(tuple(a[yy,xx]) for y,x in cc for yy in range(y-1,y+2) for xx in range(x-1,x+2) if (yy,xx) not in cc and a[yy,xx,3])
   for colour,num in near.most_common(3):
    if colour==c or colour not in ramp:continue
    trial=a.copy()
    for y,x in cc:trial[y,x]=colour
    score=colour_count(a,c)+colour_count(a,colour)-colour_count(trial,c)-colour_count(trial,colour)
    key=(score,-len(cc),num)
    if score>0 and (best is None or key>best[0]):best=(key,cc,colour)
  if best is None:break
  _,cc,colour=best
  for y,x in cc:a[y,x]=colour;edits.append([x,y,bytes(colour[:3]).hex()])
 return edits

def make(v):
 for d in ['source','walk/frames','walk/layers']:(R/d).mkdir(parents=True,exist_ok=True)
 ref,parts,body,discs=sources(v);frames=[];rig=[]
 for f in range(8):
  dip=int(f in [0,4]);layers={}
  for n,pp in parts.items():
   q=D[v][n];sole=np.array(q['sole']);off,lift=T['paths'][n][f];vt=T['views'][v]
   target=np.array(vt['visible_feet'][n]['frames'][f]['sole_centre']) if n in vt['visible_feet'] else sole+off*np.array(vt['u'])*vt['f']-[0,lift]
   # Round the ground position once, then subtract the integer lift.
   delta=np.floor(target+[0,lift]-sole+.5).astype(int)-[0,lift];dx,dy=map(int,delta)
   root,kn,kd,length_error,upper_error,lower_error=articulation(q,delta,dip,body,n.startswith('L'));jn=np.array(q['join'])+delta
   a=np.zeros_like(ref)
   casing(a,root,kn,q['w']+4,n.startswith('L'));casing(a,kn,jn,q['w']+3,n.startswith('L'))
   band(a,root,kn,q['w'],n.startswith('L'));band(a,kn,jn,q['w']-1,n.startswith('L'))
   raw=b.shift(pp['lower'],dx,dy);b.comp(a,raw);b.comp(a,b.shift(pp['knee'],*kd))
   bottom=int(sole[1]+dy);a[Y>bottom]=0;a[(Y>=bottom-1)&(raw[:,:,3]==0)]=0
   # Save the complete joint even where its fixed housing occludes it.
   layers[n]=a;save(a,f'walk/layers/{v}_{n}_f{f}.png')
   rig.append(dict(foot=n,frame=f,delta=[dx,dy],knee_delta=kd.tolist(),source_sole=sole.tolist(),target=target.tolist(),lift=lift,hidden_in_still=n not in vt['visible_feet'],root=root.tolist(),knee=kn.tolist(),ankle=jn.tolist(),leg_length_error=length_error,upper_link_error=upper_error,lower_link_error=lower_error))
  a=np.zeros_like(ref)
  for n in (['LF','LH'] if v=='ne' else ['LH','LF']):b.comp(a,layers[n])
  b.comp(a,b.shift(body,0,dip))
  for n in ['RH','RF']:b.comp(a,layers[n])
  b.comp(a,b.shift(b.piece(ref,discs),0,dip))
  # Continue the flank behind a receding far-hind socket. These are only the
  # missing interior socket pixels, never the open space between the four feet.
  if v in ['se','ne']:
   sf=R.parents[2]/'walk/tools/walk_tools.py';tr=ast.parse(sf.read_text());ns={'np':np}
   exec(compile(ast.Module(body=[n for n in tr.body if isinstance(n,ast.FunctionDef) and n.name=='find_slits'],type_ignores=[]),str(sf),'exec'),ns)
   for x,y in ns['find_slits'](a,ref,dip):
    if (v=='ne' and 50<=x<=63 and 138+dip<=y<=145+dip) or (v=='se' and 53<=x<=57 and 119+dip<=y<=124+dip):a[y,x]=P['26183f']
  # Only enclosed metal sockets are filled. Real spaces between legs stay open.
  holes=b.fill_holes(a[:,:,3]>0)&(a[:,:,3]==0);st=b.shift(ref,0,dip)
  for y,x in zip(*np.where(holes)):a[y,x]=st[y,x] if st[y,x,3] else P['26183f']
  cut={'e':140,'se':116,'ne':119}[v]+dip;a[:cut]=st[:cut]
  edits=joint_cleanup(a,ref,body,parts,[q for q in rig if q['frame']==f],dip)
  # Any tiny disconnected trace is a contour remnant, never a new floating part.
  for cc in b.pieces(a[:,:,3]>0)[1:]:
   if len(cc)<=2:
    for y,x in cc:a[y,x]=0
  (R/f'walk/layers/{v}_join_edits_f{f}.json').write_text(json.dumps(edits))
  frames.append(a);save(a,f'walk/frames/{v}_f{f}.png')
 rigfile=R/'rig.json';allrig=json.loads(rigfile.read_text()) if rigfile.exists() else {};allrig[v]=rig;rigfile.write_text(json.dumps(allrig,indent=2))
 report=R/'REPORT.txt';lines=report.read_text().splitlines() if report.exists() else ['hippo-walk35-run1; tokens: unavailable.','RF/RH = near right; LF/LH = far left. Labels checked against stills; retained.']
 lines=[s for s in lines if not s.startswith(v+':')];lines.append(v+': 8 raw frames drawn; native steel joints/feet, fixed discs/body; audit pending.');report.write_text('\n'.join(lines)+'\n')
 print(v,'source soles',{n:q['sole'] for n,q in D[v].items()});boards(v,ref,frames)
 return frames

def boards(v,ref,frames):
 selout=b.load_selout();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17);bg=(65,73,80,255)
 board=Image.new('RGBA',(768*9,800),bg);dr=ImageDraw.Draw(board);pics=[]
 box=(35,95,151,165);zoom=Image.new('RGBA',(580*9,380),bg);dz=ImageDraw.Draw(zoom)
 review=Image.new('RGBA',(464*5,610),bg);dv=ImageDraw.Draw(review)
 for j,a in enumerate([ref]+frames):
  outlined=Image.fromarray(selout(a)[0]);tile=outlined.resize((768,768),Image.Resampling.NEAREST);board.alpha_composite(tile,(j*768,28));label=v+' '+('STILL' if j==0 else f'f{j-1}');dr.text((j*768+10,4),label,font=font,fill='white')
  zoom.alpha_composite(outlined.crop(box).resize((580,350),Image.Resampling.NEAREST),(j*580,27));dz.text((j*580+8,4),label,font=font,fill='white')
  c,row=(0,0) if j==0 else ((j-1)%4+1,(j-1)//4);review.alpha_composite(outlined.crop(box).resize((464,280),Image.Resampling.NEAREST),(c*464,row*305+25));dv.text((c*464+8,row*305+3),label,font=font,fill='white')
  if j:
   im=Image.new('RGBA',tile.size,bg);im.alpha_composite(tile);pics.append(im.convert('RGB'))
 board.convert('RGB').save(R/f'{v}_board.png');zoom.convert('RGB').save(R/f'{v}_legs_zoom.png');review.convert('RGB').save(R/f'{v}_review.png')
 # GIF timing is stored in 10 ms units: alternating120/130 gives a 1s cycle.
 pics[0].save(R/f'{v}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,optimize=False,disposal=2)
 raw=[Image.fromarray(a) for a in frames];raw[0].save(R/f'{v}_preview.apng',save_all=True,append_images=raw[1:],duration=125,loop=0)

def combine():
 for suffix,out in [('board.png','board.png'),('legs_zoom.png','legs_zoom.png')]:
  ims=[Image.open(R/f'{v}_{suffix}').convert('RGB') for v in ['e','se','ne']];im=Image.new('RGB',(ims[0].width,sum(x.height for x in ims)))
  y=0
  for a in ims:im.paste(a,(0,y));y+=a.height
  im.save(R/out)

if __name__=='__main__':
 for v in (sys.argv[1:] or ['e','se','ne']):make(v)
 if all((R/f'{v}_board.png').exists() for v in ['e','se','ne']):combine()
