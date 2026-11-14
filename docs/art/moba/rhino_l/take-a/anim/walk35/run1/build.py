"""Run 1: native rhino traces, articulated at their existing joints. Writes here only."""
from pathlib import Path
import ast, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
B=R.parents[1]
T=json.loads((R/'targets.json').read_text())
Y,X=np.indices((192,192)); GRID=np.stack((X,Y),axis=2)
P=[tuple(bytes.fromhex(c))+(255,) for c in '141218 211e27 3d3a44 58555e 7a4a06 9d9ba2 d18a0a d6d6dc ff3a2a ffcf1f fff4a8'.split()]
# Root, knee, ankle; traced articulated region, foot boundary row.
# Shoulder armour, tail and head remain on the pinned body layer.
D={
 'e':{
  'RH':[(64,132),(64,141),(63,150),[(55,133),(61,135),(67,135),(71,139),(73,146),(76,151),(76,160),(51,160),(51,149),(54,142)],152],
  'RF':[(102,133),(102,142),(102,150),[(97,135),(104,135),(109,138),(111,144),(115,152),(115,160),(91,160),(91,149),(94,143)],152]},
 'se':{
  'LH':[(65,114),(61,123),(63,132),[(57,116),(62,116),(66,119),(68,125),(70,128),(75,129),(78,133),(76,139),(72,143),(56,143),(53,137),(54,129),(56,125)],134],
  'RH':[(92,127),(85,141),(87,150),[(81,134),(87,136),(92,139),(94,144),(96,150),(100,154),(101,160),(77,160),(77,150),(79,144)],152],
  'RF':[(114,132),(114,141),(120,148),[(109,145),(114,146),(117,148),(129,148),(134,150),(134,155),(108,155),(106,150),(107,147)],148]},
 'ne':{
  'LH':[(60,123),(60,132),(63,140),[(56,125),(61,125),(64,128),(64,136),(69,138),(74,138),(77,141),(77,148),(72,150),(59,150),(53,144),(54,137),(55,133)],141],
  'RH':[(84,126),(94,139),(88,149),[(87,131),(95,129),(100,132),(102,137),(101,142),(97,147),(99,152),(98,157),(94,160),(84,160),(77,155),(76,149),(79,144),(80,139),(84,134)],152],
  'RF':[(126,112),(117,121),(116,130),[(115,114),(120,113),(124,117),(124,125),(127,128),(130,131),(130,136),(123,139),(112,139),(105,135),(103,130),(108,125),(111,121)],131]}}
K={
 'e':{'RH':[(60,136),(65,135),(69,137),(71,140),(71,144),(68,147),(62,148),(58,145),(57,141),(58,138)],'RF':[(98,137),(104,136),(108,138),(110,141),(109,145),(106,148),(99,148),(96,145),(95,141),(96,139)]},
 'se':{'LH':[(58,117),(62,116),(65,118),(67,121),(67,125),(65,128),(61,129),(57,126),(56,122)],'RH':[(83,136),(87,136),(90,139),(91,143),(89,146),(85,147),(81,145),(80,142),(81,139)],'RF':[]},
 'ne':{'LH':[(57,125),(61,125),(63,128),(64,133),(62,137),(58,137),(55,134),(55,129)],'RH':[(94,131),(98,131),(101,134),(102,139),(100,143),(97,146),(93,145),(90,143),(89,139),(90,135)],'RF':[(116,114),(120,114),(123,117),(123,122),(120,126),(115,127),(112,124),(112,120)]}}

def mask(poly):
 im=Image.new('1',(192,192));ImageDraw.Draw(im).polygon(poly,fill=1);return np.array(im)
def limb_mask(view,name,q):
 m=mask(q[3])
 extras={('e','RF'):[(113,147),(114,148),(114,149)],('se','LH'):[(77,138),(77,139)],('ne','RF'):[(105,136),(106,136),(108,137),(109,138)],('ne','LH'):[(54,146),(55,147)]}
 for x,y in extras.get((view,name),[]):m[y,x]=True
 if (view,name)==('ne','RH'):m[146:161,76:103]=True
 return m
def shift(a,dx=0,dy=0):
 b=np.zeros_like(a); ys,xs=np.where(a[:,:,3]>0);xx=xs+int(dx);yy=ys+int(dy);ok=(xx>=0)&(xx<192)&(yy>=0)&(yy<192);b[yy[ok],xx[ok]]=a[ys[ok],xs[ok]];return b
def comp(a,b):
 m=b[:,:,3]>0;a[m]=b[m]
def fp(a):
 yy,xx=np.where(a[:,:,3]>0);y=int(yy.max());xs=np.where(a[y,:,3]>0)[0];return np.array([(xs[0]+xs[-1])/2,y]),[int(xs[0]),int(xs[-1])]
def fit(a,s0,s1,t0,t1):
 s0,s1,t0,t1=map(lambda z:np.array(z,float),(s0,s1,t0,t1));sv=s1-s0;tv=t1-t0
 su=sv/np.linalg.norm(sv);tu=tv/np.linalg.norm(tv);sn=np.array([-su[1],su[0]]);tn=np.array([-tu[1],tu[0]])
 v=GRID-t0;src=s0+(v@tu)[...,None]*su+(v@tn)[...,None]*sn
 ix=np.floor(src+.5).astype(int);ok=(ix[:,:,0]>=0)&(ix[:,:,0]<192)&(ix[:,:,1]>=0)&(ix[:,:,1]<192)
 b=np.zeros_like(a);b[ok]=a[ix[:,:,1][ok],ix[:,:,0][ok]];return b
def joint(root,ankle,l1,l2,hint):
 v=ankle-root;dist=np.linalg.norm(v);u=v/dist;along=(l1*l1-l2*l2+dist*dist)/(2*dist);h=math.sqrt(max(0,l1*l1-along*along));n=np.array([-u[1],u[0]])
 opts=[root+u*along+n*h,root+u*along-n*h];p=min(opts,key=lambda q:np.linalg.norm(q-hint))
 # Choose a native knee pivot while keeping both bones within one pixel.
 opts=[]
 for dx in range(-2,3):
  for dy in range(-2,3):
   jj=np.floor(p+.5)+[dx,dy];err=np.abs([np.linalg.norm(jj-root)-l1,np.linalg.norm(ankle-jj)-l2])
   opts.append((max(err)>1,float(err@err)+.005*np.linalg.norm(jj-hint)**2,jj))
 return min(opts,key=lambda q:(q[0],q[1]))[2]
def smallholes(a):
 m=a[:,:,3]>0;holes=ndi.binary_fill_holes(m)&~m;labs,n=ndi.label(holes);sizes=np.bincount(labs.ravel());fix=holes&np.isin(labs,np.where(sizes<=12)[0]);idx=ndi.distance_transform_edt(~m,return_distances=False,return_indices=True);a[fix]=a[idx[0][fix],idx[1][fix]];return a
def poly(im,pts,c):ImageDraw.Draw(im).polygon([tuple(np.floor(np.array(p)+.5).astype(int)) for p in pts],fill=P[c])
def line(im,pts,c,w=1):ImageDraw.Draw(im).line([tuple(np.floor(np.array(p)+.5).astype(int)) for p in pts],fill=P[c],width=w)

def build():
 (R/'walk/frames').mkdir(parents=True,exist_ok=True);(R/'walk/layers').mkdir(exist_ok=True)
 recs={}; allframes={}
 for view,legs in D.items():
  ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'));body=ref.copy();segs={};masks={}
  for name,q in legs.items():
   root,knee,ankle,outline,cut=q;mm=limb_mask(view,name,q)&(ref[:,:,3]>0);masks[name]=mm
   a=ref.copy();a[~mm]=0
   # Native foot block translates intact. Knee disc and gold shank rotate separately.
   foot=a.copy();foot[Y<cut]=0
   km=mask(K[view][name]) if K[view][name] else np.zeros((192,192),bool)
   disc=a.copy();disc[~km]=0
   upper=a.copy();upper[(Y>knee[1])|km]=0
   shank=a.copy();shank[(Y<knee[1])|(Y>=cut+1)|km]=0
   segs[name]=(upper,shank,foot,disc);body[mm]=0
  # Hidden limbs use the still's homologous paint, behind the entire pinned body.
  # Diagonal lateral separation is read from the visible hind soles, not invented width.
  hidden={'LH':('RH',(0,-16)),'LF':('RF',(0,-16))} if view=='e' else {'LF':('RF',(-24,-17 if view=='se' else -10))}
  for name,(donor,delta) in hidden.items():
   segs[name]=tuple(shift(a,*delta) for a in segs[donor]);src=D[view][donor]
   # Full source homologous shapes are kept; depth is provided by compositing.
   Image.fromarray(segs[name][2]).save(R/'walk/layers'/f'{view}_{name}_source_foot.png')
  Image.fromarray(body).save(R/'walk/layers'/f'{view}_body.png')
  Image.fromarray((~np.logical_or.reduce(list(masks.values()))).astype('uint8')*255).save(R/'walk/layers'/f'{view}_pinned_mask.png')
  recs[view]=[];frames=[]
  for f in range(8):
   dip=int(f in (0,4));layers={}
   active=dict(legs)
   for name,(donor,delta) in hidden.items():
    active[name]=[(np.array(p)+delta).tolist() for p in legs[donor][:3]]+legs[donor][3:]
   for name,q in active.items():
    root,knee,ankle=map(lambda z:np.array(z,float),q[:3]);up,sh,foot,disc=segs[name]
    sole,span=fp(foot);off,lift=T['paths'][name][f]
    if name in legs:
     t=T['views'][view]['visible_feet'][name]['frames'][f];ideal=np.array(t['sole_centre'])
    else:
     vv=T['views'][view];ideal=sole+off*np.array(vv['u'])*vv['f']-[0,lift]
    # Preserve the original foot's half-pixel centre and exact integer lift.
    dx=int(np.floor(ideal[0]-sole[0]+.5));ground=int(np.floor(ideal[1]+lift+.5));dy=ground-lift-int(sole[1]);delta=np.array([dx,dy]);ank=ankle+delta;rt=root+[0,dip]
    l1=np.linalg.norm(knee-root);l2=np.linalg.norm(ankle-knee);j=joint(rt,ank,l1,l2,knee+delta*.35)
    u=fit(up,root,knee,rt,j);s=fit(sh,knee,ankle,j,ank)
    im=Image.fromarray(np.zeros_like(ref))
    # Tapered socket behind the unchanged native disc; torso paint hides its top.
    vv=j-rt;vv/=np.linalg.norm(vv);nv=np.array([-vv[1],vv[0]])
    poly(im,[rt-nv*5,rt+nv*5,j+nv*5,j+vv*3,j-nv*5],1)
    im.alpha_composite(Image.fromarray(u));im.alpha_composite(Image.fromarray(s))
    # Small stepped collar behind the original knee disc conceals raster joins.
    vec=ank-j;vec/=np.linalg.norm(vec);nn=np.array([-vec[1],vec[0]])
    def p(a,b):return j+vec*a+nn*b
    poly(im,[p(0,-5),p(0,5),p(6,5),p(7,3),p(7,-4)],1)
    poly(im,[p(2,-4),p(2,4),p(6,4),p(6,-4)],6)
    poly(im,[p(2,-3),p(2,0),p(6,1),p(6,-3)],9)
    im.alpha_composite(Image.fromarray(shift(disc,int(np.floor(j[0]-knee[0]+.5)),int(np.floor(j[1]-knee[1]+.5)))))
    # The source gold cuff overlaps the source foot, covering rotated shank ends.
    footpaint=shift(foot,dx,dy)
    im.alpha_composite(Image.fromarray(footpaint))
    a=smallholes(np.array(im));a[ground-lift+1:]=0
    # A folded knee must never manufacture a second sole alongside the foot.
    a[(Y>=ground-lift-2)&(footpaint[:,:,3]==0)]=0
    layers[name]=a;Image.fromarray(a).save(R/'walk/layers'/f'{view}_{name}_f{f}.png')
    recs[view].append({'name':name,'frame':f,'hidden_in_still':name not in legs,'root':rt.tolist(),'knee':j.tolist(),'ankle':ank.tolist(),'source_lengths':[l1,l2],'lengths':[float(np.linalg.norm(j-rt)),float(np.linalg.norm(ank-j))],'target':ideal.tolist(),'lift':lift,'ground_row':ground,'sole_source':sole.tolist()})
   # Far limbs first. Pinned shoulder and face paint occlude the joints naturally.
   a=np.zeros_like(ref)
   for name in ['LF','LH','RF','RH']:
    if name in layers:comp(a,layers[name])
   comp(a,shift(body,0,dip))
   a=smallholes(a)
   # Close the remaining exposed socket wedges by hand-colour: these are joins,
   # not open space between independent legs. Preserve every pinned opaque pixel.
   holes=ndi.binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)
   a[holes]=P[1]
   # Only disconnected sampling fragments may be removed, never a connected plate.
   labs,n=ndi.label(a[:,:,3]>0,np.ones((3,3)));sz=np.bincount(labs.ravel());sz[0]=0
   for label in range(1,n+1):
    if sz[label]<=3:a[labs==label]=0
   frames.append(a);Image.fromarray(a).save(R/'walk/frames'/f'{view}_f{f}.png')
  allframes[view]=frames
 (R/'rig.json').write_text(json.dumps(recs,indent=2))
 make_boards(allframes)

def make_boards(allframes):
 sp=B/'anim/selout_rhino.py';tree=ast.parse(sp.read_text());env={'np':np,'OUTLINE':np.array(P[0][:3],np.uint8)}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),str(sp),'exec'),env);selout=env['selout']
 bg=(78,86,82,255);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);box=(28,54,154,170);cw,ch=504,488
 board=Image.new('RGBA',(cw*9,ch*3),bg);dr=ImageDraw.Draw(board)
 for vi,(view,frames) in enumerate(allframes.items()):
  ref=np.array(Image.open(B/'views_cam35'/f'{view}.png').convert('RGBA'));pics=[]
  for fi,a in enumerate([ref]+frames):
   tile=Image.fromarray(selout(a)[0]).crop(box).resize((504,464),Image.Resampling.NEAREST);board.alpha_composite(tile,(cw*fi,ch*vi+24));dr.text((cw*fi+8,ch*vi+2),f'{view} '+('STILL' if fi==0 else f'f{fi-1}'),font=font,fill='white')
   if fi:
    im=Image.new('RGBA',tile.size,bg);im.alpha_composite(tile);pics.append(im.convert('RGB'))
  pics[0].save(R/f'{view}_preview.gif',save_all=True,append_images=pics[1:],duration=[120,130]*4,loop=0,disposal=2,optimize=False)
  raw=[Image.fromarray(a) for a in frames]
  raw[0].save(R/f'{view}_preview.apng',save_all=True,append_images=raw[1:],duration=125,loop=0,disposal=0,blend=0)
  board.crop((0,vi*ch,cw*9,(vi+1)*ch)).convert('RGB').save(R/f'{view}_board.png')
 board.convert('RGB').save(R/'board.png');board.resize((2268,732),Image.Resampling.NEAREST).convert('RGB').save(R/'board_small.png')

if __name__=='__main__':build()
