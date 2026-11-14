"""Native traced-pixel 2D rig; all outputs confined to this directory."""
from pathlib import Path
import numpy as np, json, math, ast
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
B=R.parents[1]; M=B.parents[1]
P=[tuple(bytes.fromhex(c))+(255,) for c in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()]
SIDE_SPACING=float(np.linalg.norm(np.array([117.,159.5])-np.array([73.25,159.])))
SIDE=json.loads((R.parent/'codex-walk2/articulation.json').read_text())
PATH=json.loads((R.parent/'codex-walk2/targets.json').read_text())['paths']
Y,X=np.indices((192,192)); GRID=np.stack([X,Y],2)
# Each outline is traced in the approved fixed still at native resolution.
# root, knee, ankle, sole; upper contour, lower contour, paw contour.
D={
'se':{
'near_fore':[(102,123),(101,138),(102,154),(105,160),[(99,115),(105,115),(108,118),(110,123),(109,127),(105,131),(104,138),(101,140),(98,135),(97,131),(94,127),(94,122),(96,118)],[(97,132),(100,134),(104,137),(105,141),(104,146),(105,151),(105,155),(101,156),(100,150),(99,145),(97,140)],[(100,152),(104,152),(104,154),(108,155),(109,156),(110,158),(110,160),(99,160),(98,157),(99,155)]],
'far_fore':[(116,125),(115,139),(116,152),(120.5,158),[(114,121),(118,122),(119,127),(119,132),(117,137),(117,140),(113,139),(111,135),(111,130)],[(111,134),(113,135),(116,138),(118,141),(117,147),(118,151),(118,154),(114,154),(114,149),(113,144)],[(114,151),(118,151),(119,153),(121,153),(123,154),(125,156),(125,158),(114,158),(113,155)]],
'near_hind':[(82,121),(72,137),(69,151),(71.5,157),[(78,114),(83,113),(87,116),(88,122),(85,127),(80,131),(76,135),(73,138),(68,139),(67,134),(70,129),(73,126),(74,120)],[(68,133),(72,135),(74,138),(72,144),(71,149),(72,152),(71,154),(67,154),(67,148),(68,143),(67,139)],[(67,150),(71,150),(72,152),(75,153),(76,154),(77,156),(77,157),(67,157),(66,154)]],
'far_hind':[(87,126),(84,139),(84,150),(86.5,154),[(85,123),(89,124),(90,129),(88,133),(86,138),(85,141),(82,142),(80,138),(81,133),(83,130)],[(80,133),(84,134),(86,138),(86,144),(85,149),(86,151),(85,153),(82,153),(82,148),(81,143)],[(82,149),(86,149),(87,150),(89,151),(91,152),(91,154),(81,154),(81,152)]]},
'ne':{
'near_fore':[(119,121),(117,138),(120,150),(119.5,155),[(116,113),(122,113),(124,117),(124,124),(122,127),(120,128),(120,133),(119,138),(116,139),(114,134),(114,129),(112,124),(113,118)],[(114,133),(118,135),(120,138),(120,143),(121,147),(121,151),(117,152),(117,147),(115,142),(113,138)],[(117,149),(121,149),(122,150),(125,151),(126,152),(127,153),(127,155),(116,155),(115,152)]],
'far_fore':[(107,124),(103,138),(102,149),(103,153),[(104,120),(109,121),(110,126),(108,131),(106,135),(106,139),(102,140),(100,137),(101,131)],[(100,134),(104,135),(106,139),(105,143),(105,149),(106,151),(102,152),(100,149),(100,144),(99,139)],[(99,148),(103,148),(105,149),(107,150),(108,151),(108,153),(98,153),(97,151)]],
'near_hind':[(99,125),(91,142),(90,155),(92,160),[(94,118),(100,117),(105,120),(105,126),(103,131),(99,135),(96,139),(93,144),(88,145),(87,141),(88,137),(91,133),(91,126)],[(87,137),(91,139),(94,142),(94,147),(92,152),(93,156),(89,158),(87,155),(88,149),(87,145)],[(88,154),(92,154),(93,156),(96,156),(98,157),(99,159),(99,160),(87,160),(86,157)]],
'far_hind':[(82,131),(77,144),(76,154),(77,157),[(80,127),(85,126),(86,131),(82,136),(80,140),(80,145),(76,147),(73,144),(74,139),(77,135)],[(74,140),(78,140),(80,143),(79,148),(78,153),(79,155),(75,156),(73,153),(74,148),(73,145)],[(74,153),(78,153),(79,154),(82,154),(83,156),(83,157),(73,157),(72,155)]]}}
TAIL={
'se':[(75,119),(79,122),(74,128),(68,133),(63,140),(57,144),(55,151),(54,149),(54,140),(57,135),(62,129),(68,124)],
'ne':[(84,124),(88,128),(83,134),(77,140),(70,148),(64,153),(58,159),(57,157),(57,149),(60,142),(66,136),(72,131),(78,127)]}
def mask(poly):
 im=Image.new('1',(192,192));ImageDraw.Draw(im).polygon(poly,fill=1);return np.array(im)
def trace(ref,poly):
 a=ref.copy();a[~mask(poly)]=0;return a
def shift(a,dx=0,dy=0):
 out=np.zeros_like(a);dx=int(dx);dy=int(dy);ys,xs=np.where(a[:,:,3]>0);xx=xs+dx;yy=ys+dy;ok=(xx>=0)&(xx<192)&(yy>=0)&(yy<192);out[yy[ok],xx[ok]]=a[ys[ok],xs[ok]];return out
def composite(a,b):
 z=b[:,:,3]>0;a[z]=b[z]
def fit(a,s0,s1,t0,t1,phase=(0,0)):
 s0=np.array(s0,float);s1=np.array(s1,float);t0=np.array(t0,float);t1=np.array(t1,float)
 sv=s1-s0;tv=t1-t0;sl=np.linalg.norm(sv);tl=np.linalg.norm(tv);su=sv/sl;tu=tv/tl;sn=np.array([-su[1],su[0]]);tn=np.array([-tu[1],tu[0]])
 v=GRID-t0+phase;src=s0+(v@tu)[...,None]*sl/tl*su+(v@tn)[...,None]*sn;ix=np.floor(src+.5).astype(int);valid=(ix[:,:,0]>=0)&(ix[:,:,0]<192)&(ix[:,:,1]>=0)&(ix[:,:,1]<192);out=np.zeros_like(a);out[valid]=a[ix[:,:,1][valid],ix[:,:,0][valid]];return out

def native_widths(a,start,end):
 m=a[:,:,3]>0;s=np.array(start,float);v=np.array(end,float)-s;u=v/np.linalg.norm(v);n=np.array([-u[1],u[0]]);ds=np.arange(-20,20.001,.02);out=[]
 for frac in [.25,.5,.75]:
  p=np.floor(s+v*frac+ds[:,None]*n+.5).astype(int);on=m[p[:,1],p[:,0]];lab,k=ndi.label(on);out.append(round(max([(lab==j).sum()*.02 for j in range(1,k+1)],default=0)))
 return np.array(out)
def fitted(a,s0,s1,t0,t1):
 ref=native_widths(a,s0,s1);best=None
 for px,py in [(0,0)]+[(x,y) for x in [-.4,-.2,0,.2,.4] for y in [-.4,-.2,0,.2,.4]]:
  b=fit(a,s0,s1,t0,t1,(px,py));delta=np.abs(native_widths(b,t0,t1)-ref);score=(int(delta.max()),int(delta.sum()),px*px+py*py)
  if best is None or score<best[0]:best=(score,b)
  if delta.max()<=1:return b
 return best[1]

def ik(root,end,l1,l2,hint):
 v=end-root;dist=np.linalg.norm(v);u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);h=math.sqrt(max(0,l1*l1-along*along));p=np.array([-u[1],u[0]]);opts=[root+u*along+p*h,root+u*along-p*h];return min(opts,key=lambda x:np.linalg.norm(x-hint))
def repair_holes(a):
 op=a[:,:,3]>0;holes=ndi.binary_fill_holes(op)&~op
 labs,n=ndi.label(holes);sizes=np.bincount(labs.ravel());holes &= np.isin(labs,[i for i in range(1,n+1) if sizes[i]<=24]);idx=ndi.distance_transform_edt(~op,return_distances=False,return_indices=True);a[holes]=a[idx[0][holes],idx[1][holes]];return a

def stroke(im,pts,c,w=1):ImageDraw.Draw(im).line([tuple(np.floor(np.array(p)+.5).astype(int)) for p in pts],fill=P[c],width=w)
def poly(im,pts,c):ImageDraw.Draw(im).polygon([tuple(np.floor(np.array(p)+.5).astype(int)) for p in pts],fill=P[c])
def footprint(a):
 ys,xs=np.where(a[:,:,3]>0);y=int(ys.max());xx=np.where(a[y,:,3]>0)[0];return np.array([(xx.min()+xx.max())/2,y]),[int(xx.min()),int(xx.max())]

(R/'walk/frames').mkdir(parents=True,exist_ok=True);(R/'walk/layers').mkdir(parents=True,exist_ok=True)
allframes={};rigs={};outtargets={'duration_ms':100,'paths':PATH,'side_paw_spacing':SIDE_SPACING,'side_still_paws':{'near_fore':[113.5,160],'far_fore':[120.5,159],'near_hind':[68,160],'far_hind':[78.5,158]},'views':{},'raster_note':'Nearest native pixel targets. Sole rows limited to160 before subtracting lift; se near_fore f0 and ne near_hind f7 ideal rows exceed160 by less than1px; raster sole is160. Both remain within1px. No body-space vertical rescaling.'}
for view,legs in D.items():
 ref=np.array(Image.open(B/'fixed'/f'{view}.png').convert('RGBA'))
 fore=(np.array(legs['near_fore'][3])+legs['far_fore'][3])/2;hind=(np.array(legs['near_hind'][3])+legs['far_hind'][3])/2;axis=fore-hind;spacing=np.linalg.norm(axis);u=axis/spacing;foreshorten=spacing/SIDE_SPACING;v=axis/SIDE_SPACING
 # Divide still paint into pinned torso, four articulated limbs, and a rigid straight tail.
 segs={name:[trace(ref,p) for p in q[4:]] for name,q in legs.items()}
 body=ref.copy()
 for name,q in legs.items():
  for a in segs[name]:body[a[:,:,3]>0]=0
 tail=trace(ref,TAIL[view]);body[tail[:,:,3]>0]=0
 # Old limb remnants outside a trace must never hang from a stationary torso.
 limits={'se':[(65,128),(77,126),(85,130),(96,130),(107,129),(113,126),(123,126)],'ne':[(70,134),(83,132),(91,135),(102,131),(110,128),(117,128),(125,125)]}[view]
 cutoff=np.interp(X,[p[0] for p in limits],[p[1] for p in limits]);body[Y>cutoff]=0
 # Under shoulder and hip plates, extend only the torso that can actually be exposed.
 torso={'se':[(78,117),(89,114),(103,115),(111,122),(106,126),(98,130),(88,132),(80,128)],'ne':[(82,128),(94,117),(105,115),(116,116),(121,121),(116,126),(108,129),(101,135),(91,136)]}[view]
 under=np.zeros_like(ref);tm=mask(torso);under[tm]=P[1];under[tm&(ref[:,:,3]>0)]=ref[tm&(ref[:,:,3]>0)];composite(under,body);body=under
 frames=[];recs=[];targets={}
 for name,q in legs.items():
  targets[name]={'pair':'A' if name in ['near_fore','far_hind'] else 'B','still_sole':list(q[3]),'frames':[]}
 for f in range(8):
  dip=int(f in [1,5]);layers={}
  for name,q in legs.items():
   root,joint,ankle,sole=map(lambda z:np.array(z,float),q[:4]);pair=targets[name]['pair'];off,lift=PATH[pair][f];ideal=sole+off*v-np.array([0,lift]);ground=sole+off*v;tx=sole[0]+int(math.floor(off*v[0]+.5));gy=min(160,int(math.floor(ground[1]+.5)));target=np.array([tx,gy-lift],float)
   sr=next(r for r in SIDE if r['name']==name and r['frame']==f)
   sroot=np.array((115,123) if name=='near_fore' else (120,123) if name=='far_fore' else (80,122) if name=='near_hind' else (85,122))
   sjoint=np.array((108,140) if name=='near_fore' else (117,141) if name=='far_fore' else (67,141) if name=='near_hind' else (76,141))
   rt=root+[0,dip]
   # The side wrist bends forward on the two lift-four foreleg frames.
   wrist=ankle+(target-sole)
   if name.endswith('fore') and lift==4:wrist+=4*v+np.array([0,-1])
   jdelta=np.array(sr['joint'])-sjoint;hint=joint+jdelta[0]*v+np.array([0,jdelta[1]])
   l1=np.linalg.norm(joint-root);l2=np.linalg.norm(ankle-joint)
   j=ik(rt,wrist,l1,l2,hint)
   # Native joint choice preserves both segment lengths to within two pixels.
   candidates=[]
   for dx in range(-2,3):
    for dy in range(-2,3):
     jj=np.floor(j+.5)+[dx,dy];err=np.array([np.linalg.norm(jj-rt)-l1,np.linalg.norm(wrist-jj)-l2]);candidates.append((np.max(np.abs(err))>2,float(err@err)+.02*np.linalg.norm(jj-hint)**2,jj))
   j=min(candidates,key=lambda z:(z[0],z[1]))[2]
   up=fitted(segs[name][0],root,joint,rt,j);lo=fitted(segs[name][1],joint,ankle,j,wrist)
   # The clawed foot itself translates without stretching or changing its toe pixels.
   rawfoot=segs[name][2];measured,_=footprint(rawfoot);ft=shift(rawfoot,int(math.floor(tx-measured[0]+.5)),int(target[1]-measured[1]))
   # Half-pixel sole centres retain the original span and get nearest whole-pixel translation.
   actual,_=footprint(ft)
   im=Image.fromarray(np.zeros_like(ref));im.alpha_composite(Image.fromarray(up));im.alpha_composite(Image.fromarray(lo))
   # Hand-shaped stepped joint and ankle collars conceal sampling seams.
   near=name.startswith('near');c=3 if near else 2
   vv=wrist-j;vv=vv/np.linalg.norm(vv);nn=np.array([-vv[1],vv[0]])
   def pt(a,b):return j+vv*a+nn*b
   poly(im,[pt(-2,-2),pt(-2,1),pt(0,2),pt(2,1),pt(2,-1),pt(0,-2)],c)
   stroke(im,[pt(-2,-1),pt(0,-1),pt(1,0)],5 if near else 3)
   stroke(im,[pt(1,2),pt(2,1)],2)
   wa=wrist
   poly(im,[wa+[-2,-2],wa+[1,-2],wa+[2,0],wa+[1,2],wa+[-2,1]],c)
   stroke(im,[wa+[-2,0],wa+[0,1]],2)
   im.alpha_composite(Image.fromarray(ft));a=repair_holes(np.array(im));a[int(target[1])+1:]=0
   layers[name]=a
   rec={'view':view,'name':name,'frame':f,'root':rt.tolist(),'joint':j.tolist(),'ankle':wrist.tolist(),'target':ideal.tolist(),'raster_target':target.tolist(),'ground_row':gy,'lift':lift,'length_reference':[l1,l2],'lengths':[float(np.linalg.norm(j-rt)),float(np.linalg.norm(wrist-j))]}
   recs.append(rec);targets[name]['frames'].append({'frame':f,'offset':off,'lift':lift,'ideal':ideal.tolist(),'raster':target.tolist()})
   Image.fromarray(a).save(R/'walk/layers'/f'{view}_{name}_f{f}.png')
   for tag,piece in [('upper',up),('shank',lo),('paw',ft)]:Image.fromarray(piece).save(R/'walk/layers'/f'{view}_{name}_{tag}_f{f}.png')
  can=np.zeros_like(ref)
  for name in ['far_hind','far_fore']:composite(can,layers[name])
  sway=[0,1,1,0,0,-1,-1,0][f]
  composite(can,shift(tail,sway,dip));composite(can,shift(body,0,dip))
  for name in ['near_hind','near_fore']:composite(can,layers[name])
  can=repair_holes(can);can[161:]=0
  # Remove disconnected raster flecks only, preserving the whole connected creature.
  labs,n=ndi.label(can[:,:,3]>0,np.ones((3,3)));sizes=np.bincount(labs.ravel());sizes[0]=0
  for label in range(1,n+1):
   if label!=int(np.argmax(sizes)):can[labs==label]=0
  frames.append(can);Image.fromarray(can).save(R/'walk/frames'/f'{view}_f{f}.png')
 allframes[view]=frames;rigs[view]=recs
 outtargets['views'][view]={'fore_midpoint':fore.tolist(),'hind_midpoint':hind.tolist(),'spacing':spacing,'u':u.tolist(),'f':foreshorten,'screen_step_5':(5*v).tolist(),'paws':targets}
(R/'targets.json').write_text(json.dumps(outtargets,indent=2)+'\n');(R/'rig.json').write_text(json.dumps(rigs,indent=2)+'\n')
# Load the game's sel-out function without executing its file or writing beside it.
sp=M/'rhino_l/take-a/anim/selout_rhino.py';tree=ast.parse(sp.read_text());env={'np':np,'OUTLINE':np.array(P[0][:3],np.uint8)};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),str(sp),'exec'),env)
selout=env['selout'];bg=(78,86,82,255);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
CW,CH=512,344
board=Image.new('RGBA',(CW*8,CH*7),bg);draw=ImageDraw.Draw(board)
def tile(a):return Image.fromarray(selout(a)[0]).crop((32,86,160,166)).resize((512,320),Image.Resampling.NEAREST)
def row(seq,yy,label):
 for f,a in enumerate(seq):board.alpha_composite(tile(a),(CW*f,CH*yy+24));draw.text((CW*f+5,CH*yy+2),f'{label} f{f}',font=font,fill='white')
row([np.array(Image.open(R.parent/'codex-set-a/walk/frames'/f'side_f{f}.png').convert('RGBA')) for f in range(8)],0,'APPROVED SIDE timing')
for vi,view in enumerate(['se','ne']):
 yy=1+vi*3;ref=np.array(Image.open(B/'fixed'/f'{view}.png').convert('RGBA'));row([ref],yy,f'{view} APPROVED fixed')
 row([np.array(Image.open(R.parent/'codex-set-c/walk/frames'/f'{view}_f{f}.png').convert('RGBA')) for f in range(8)],yy+1,f'{view} SET C')
 row(allframes[view],yy+2,f'{view} WALK4')
 pics=[]
 for a in allframes[view]:
  pic=Image.new('RGBA',(512,320),bg);pic.alpha_composite(tile(a));pics.append(pic.convert('RGB'))
 pics[0].save(R/f'{view}_preview.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2,optimize=False)
board.convert('RGB').save(R/'board.png');board.resize((2048,1204),Image.Resampling.NEAREST).convert('RGB').save(R/'board_small.png')
# Separate native 4x new rows for visual inspection.
for view in allframes:
 b=Image.new('RGBA',(2048,688),bg);d=ImageDraw.Draw(b)
 for f,a in enumerate(allframes[view]):b.alpha_composite(tile(a),((f%4)*512,(f//4)*344+24));d.text(((f%4)*512+8,(f//4)*344+3),f'{view} f{f}',font=font,fill='white')
 b.convert('RGB').save(R/f'{view}_review4x.png')
print('Built frames, layers, targets, board and GIFs.')
for view,r in outtargets['views'].items():print(view,'u',r['u'],'f',r['f'])
