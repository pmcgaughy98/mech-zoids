"""Whole generated-drawing corrections and direct native-pixel ink. No still part compositing."""
from finish import *
LOG=[]
def save(a,name,v,i,note):
 p=R/name/'frames'/f'{v}_f{i}.png';im=clean(Image.fromarray(a) if isinstance(a,np.ndarray) else a);bb=im.getbbox();grounded=Image.new('RGBA',(192,192));grounded.alpha_composite(im,(0,161-bb[3]));grounded.save(p);LOG.append(dict(move=name,view=v,frame=i,note=note))
def rowwarp(name,v,i,src,dst,start):
 p=R/name/'frames'/f'{v}_f{i}.png';a=np.array(Image.open(p));b=np.zeros_like(a)
 for y in range(192):
  blend=np.clip((y-start)/(157-start),0,1);nodes=np.array(src)*(1-blend)+np.array(dst)*blend
  xx=np.rint(np.interp(np.arange(192),nodes,src)).astype(int);b[y]=a[y,np.clip(xx,0,191)]
 save(b,name,v,i,'continuous whole-drawing lower-body inverse-map; anchors hind support, no part cut/paste')
# Crouch splay is reduced with a continuous warp, preserving every connected limb.
for i in range(1,5):
 rowwarp('hamstring','front',i,[0,71,84,112,124,191],[0,80,93,100,112,191],138)
 rowwarp('hamstring','back',i,[0,72,86,105,120,191],[0,76,90,100,115,191],142)
 # Rear pads align in place rather than translating with the reaching shoulder.
 old=[0,60,80,95,105,140,191];new=[0,57,77,95,105,140,191]
 rowwarp('hamstring','side',i,old,new,144)
# Explicit tiny ink repairs: no sampled native patches.
p=R/'hamstring/frames/side_f2.png';im=Image.open(p).convert('RGBA');d=ImageDraw.Draw(im)
# Low open jaw: black mouth interior, attached lower rim, two sabre teeth.
d.polygon([(135,143),(149,142),(148,149),(144,151),(137,148)],fill=tuple(PAL[0])+(255,))
d.line([(136,147),(140,150),(146,151),(149,148)],fill=tuple(PAL[4])+(255,),width=2)
d.line([(137,143),(137,149)],fill=tuple(PAL[10])+(255,),width=2)
d.line([(146,143),(145,148)],fill=tuple(PAL[11])+(255,),width=1)
save(im,'hamstring','side',2,'hand-pixel open mouth and two joined pale sabre teeth')
# Front f2: joined teeth and small lower jaw; preserve generated open-mouth silhouette.
p=R/'hamstring/frames/front_f2.png';im=Image.open(p).convert('RGBA');d=ImageDraw.Draw(im)
d.line([(93,149),(93,154)],fill=tuple(PAL[10])+(255,),width=1);d.line([(100,149),(100,154)],fill=tuple(PAL[11])+(255,),width=1)
save(im,'hamstring','front',2,'hand-pixel pale fangs')
# Direct native-pixel tail repaint. Three grey armour plates and one red tip.
# A single straight axis, constant native length and substantial plate width.
TAILS={'hamstring':[(73,129),(73,131),(74,131),(74,128)],'howl':[(74,131),(75,131),(75,131),(75,130)],'death':[(75,129),(74,133),(75,142),(75,146)]}
TAIL_LOG=[]
for name,roots in TAILS.items():
 for i,root in enumerate(roots,1):
  path=R/name/'frames'/f'side_f{i}.png';a=np.array(Image.open(path));oldtip=np.array(([42,153] if name=='hamstring' else [44,154]) if name!='death' else [(45,153),(42,155),(42,155),(45,156)][i-1],float);root=np.array(root,float)
  # Sweep the old complete tail out of the drawing; leave no duplicate generated edge.
  old=oldtip-root;yy,xx=np.indices((192,192));t=np.clip(((xx-root[0])*old[0]+(yy-root[1])*old[1])/(old@old),0,1)
  dist=np.hypot(xx-(root[0]+t*old[0]),yy-(root[1]+t*old[1]));erase=(xx<=np.minimum(root[0]+1,root[0]+(yy-root[1])*old[0]/old[1]+8))&(yy>=root[1]-14+.5*(root[0]-xx))
  a[erase]=0;im=Image.fromarray(a);d=ImageDraw.Draw(im)
  # Broad straight tail may swing outward when the hips lower; tip never below ground.
  vy=min(25.,156-root[1]);vx=-float(np.sqrt(42.5**2-vy**2));axis=np.array([vx,vy]);normal=np.array([-axis[1],axis[0]])/42.5
  def xy(t,w):return tuple(np.rint(root+axis*t+normal*w).astype(int))
  C=[tuple(c)+(255,) for c in PAL]
  # The grey plates overlap on one axis, no separate pieces or cut-edge joins.
  d.polygon([xy(0,-5.5),xy(.28,-5.2),xy(.52,-4.7),xy(.78,-3.8),xy(1,0),xy(.78,3.8),xy(.52,4.7),xy(.28,5.2),xy(0,5.5)],fill=C[0])
  for j,(t0,t1,w) in enumerate([(0,.28,5),(.28,.53,4.7),(.53,.78,4.2)]):
   d.polygon([xy(t0+.01,-w+1),xy(t1,-w+.7),xy(t1,w-1),xy(t0+.01,w-.5)],fill=C[4])
   d.polygon([xy(t0+.01,1.2),xy(t1-.02,1.2),xy(t1-.02,w-1),xy(t0+.01,w-.5)],fill=C[6])
   d.line([xy(t0+.025,w-.7),xy(t1-.035,w-.9)],fill=C[9],width=1)
   if j:d.line([xy(t0,-w),xy(t0,w)],fill=C[1],width=1)
  d.polygon([xy(.79,-3.2),xy(.79,3.2),xy(1,0)],fill=C[3]);d.polygon([xy(.80,.6),xy(.80,3.0),xy(.98,.2)],fill=C[5]);d.line([xy(.81,2.6),xy(.91,1.2)],fill=C[7],width=1)
  # Armour socket flows into the haunch, covering the exposed root cap continuously.
  rx,ry=map(int,root)
  d.polygon([(rx-5,ry-5),(rx-1,ry-10),(rx+7,ry-9),(rx+11,ry-3),(rx+6,ry+5),(rx,ry+5)],fill=C[4])
  d.polygon([(rx-4,ry-5),(rx,ry-9),(rx+6,ry-8),(rx+3,ry-4)],fill=C[6])
  d.line([(rx-4,ry-5),(rx,ry-9),(rx+4,ry-8)],fill=C[9],width=1)
  # Rejoin the back-fin edge over the cleared tail root with an uninterrupted taper.
  fy={'hamstring':[110,114,114,110],'howl':[116,113,113,112],'death':[108,112,126,131]}[name][i-1]
  d.polygon([(57,fy+11),(65,fy+5),(76,fy+2),(96,fy),(105,fy+3),(109,fy+9),(89,fy+7),(72,fy+7)],fill=C[0])
  d.polygon([(59,fy+10),(66,fy+5),(77,fy+2),(96,fy+1),(104,fy+4),(107,fy+8),(89,fy+6),(72,fy+6)],fill=C[3])
  d.polygon([(60,fy+9),(68,fy+5),(78,fy+3),(96,fy+1),(103,fy+4),(106,fy+7),(91,fy+5),(73,fy+5)],fill=C[5])
  d.line([(64,fy+7),(73,fy+4),(80,fy+3),(95,fy+2),(100,fy+4)],fill=C[7],width=1)
  d.line([(89,fy-1),(100,fy-1),(102,fy)],fill=C[2],width=1)
  save(im,name,'side',i,'direct native-pixel full tail repaint: straight 43.5px axis, broad 10-11px root, three grey plates plus red tip; old tail cleared, tapered fin edge joined')
  TAIL_LOG.append(dict(move=name,view='side',frame=i,root=root.tolist(),tip=(root+axis).tolist(),axis_length_inclusive=43.5,grey_plates=3,red_tips=1))
(R/'tail_landmarks.json').write_text(json.dumps(TAIL_LOG,indent=2))

# Weak raw death f5/f6 switched camera and flattened anatomy. Finish from the sheet's
# complete f4 drawing using a rigid whole-body roll, which retains actual part lengths.
for v,angle in [('front',-20),('side',5),('back',40)]:
 im=Image.open(R/'death/frames'/f'{v}_f4.png').convert('RGBA');bb=im.getbbox();sp=im.crop(bb).rotate(angle,resample=Image.Resampling.NEAREST,expand=True);sp=sp.crop(sp.getbbox());rb=Image.open(REF[v]).getbbox();x=round((rb[0]+rb[2]-sp.width)/2);y=161-sp.height
 out=Image.new('RGBA',(192,192));out.alpha_composite(sp,(x,y));save(out,'death',v,5,f'whole generated f4 rigid roll {angle}deg; replaces flattened wrong-camera f5; no still pixels')
 a=np.array(Image.open(R/'death/frames'/f'{v}_f5.png'));cyan=np.all(a[:,:,:3]==PAL[8],2)&(a[:,:,3]>0);a[cyan,:3]=PAL[4];save(a,'death',v,6,'identical prone f5 body, cyan eye pixels repainted dark grey')
(R/'pixel_edits.json').write_text(json.dumps(LOG,indent=2))
print('Finished',len(LOG),'whole drawings')
