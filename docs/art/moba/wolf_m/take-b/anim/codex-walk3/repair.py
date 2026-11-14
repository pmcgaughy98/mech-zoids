"""Native-pixel repair. Reads approved e and walk2; writes only alongside this script.
Segments are traced from e.png. Nearest sampling rotates plate paint, with
native contour/joint/ankle drawing applied after fitting the existing walk2 rig.
"""
from pathlib import Path
import ast,json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
OLD=R.parent/'codex-walk2'; FIX=R.parents[1]/'fixed/e.png'
P=[tuple(bytes.fromhex(c))+(255,) for c in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()]
ref=np.array(Image.open(FIX).convert('RGBA')); records=json.loads((OLD/'articulation.json').read_text()); targets=json.loads((OLD/'targets.json').read_text())
# Read only the old body/tail functions, without executing its frame-writing module.
tree=ast.parse((OLD/'finish.py').read_text());env=dict(np=np,Image=Image,ImageDraw=ImageDraw,R=OLD,P=P)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['polygon','line','tail','body']],type_ignores=[]),str(OLD/'finish.py'),'exec'),env)
def poly(im,pts,c):ImageDraw.Draw(im).polygon([(round(x),round(y)) for x,y in pts],fill=P[c])
def ln(im,pts,c,w=1):ImageDraw.Draw(im).line([(round(x),round(y)) for x,y in pts],fill=P[c],width=w)
def traced(points):
 mask=Image.new('1',(192,192));ImageDraw.Draw(mask).polygon(points,fill=1);a=ref.copy();a[~np.array(mask)]=0;return a
# Hand-traced shoulder and thigh silhouettes. Interior pixels are the approved plates.
upper={
 'fore':traced([(112,115),(116,115),(119,118),(121,122),(121,126),(118,130),(114,132),(113,136),(112,139),(109,141),(106,140),(105,136),(105,132),(107,128),(105,124),(106,120),(109,118)]),
 'hind':traced([(76,117),(81,117),(85,120),(86,125),(84,129),(81,132),(76,134),(73,138),(69,141),(66,141),(65,138),(68,134),(70,131),(72,128),(70,124),(70,120)])}
# Shank mask includes the raised knee guards, colour bands and taper of the reference.
lower={
 'fore':traced([(104,136),(105,137),(108,139),(110,140),(111,145),(111,150),(112,153),(111,155),(108,155),(108,151),(106,147),(105,144),(104,140)]),
 'hind':traced([(64,136),(65,136),(66,138),(68,140),(69,143),(68,146),(67,149),(67,153),(68,154),(66,155),(63,155),(63,151),(64,147),(63,145),(62,144),(63,141)])}
feet={
 'fore':traced([(108,153),(112,153),(112,155),(114,156),(116,156),(118,157),(119,158),(119,160),(108,160),(107,159),(107,158),(108,156)]),
 'hind':traced([(63,153),(67,153),(67,155),(70,156),(71,156),(72,158),(73,159),(73,160),(62,160),(62,157),(63,156)])}
source={'fore':dict(root=(115,123),joint=(108,140),ankle=(110,154),sole=(114,160)), 'hind':dict(root=(80,122),joint=(67,141),ankle=(65,154),sole=(68,160))}
# The far limbs use their own visible approved shapes, rather than thick near-leg copies.
upper['far_fore']=traced([(120,122),(124,124),(124,128),(121,132),(120,137),(119,141),(115,141),(114,138),(115,134),(117,131),(118,127)])
upper['far_hind']=traced([(82,123),(86,124),(85,129),(82,133),(80,137),(78,140),(74,142),(73,139),(75,134),(77,131),(79,127)])
lower['far_fore']=traced([(113,138),(118,138),(119,141),(118,145),(117,147),(118,148),(118,152),(119,154),(115,154),(115,148),(114,147),(113,144)])
lower['far_hind']=traced([(73,139),(76,139),(79,140),(79,144),(78,147),(78,151),(78,154),(75,155),(73,153),(74,150),(73,146),(72,144)])
feet['far_fore']=traced([(117,152),(120,153),(121,154),(123,154),(124,155),(125,157),(114,157),(114,155),(116,155)])
feet['far_hind']=traced([(74,153),(78,153),(79,154),(81,154),(83,155),(84,157),(74,157)])
source['far_fore']=dict(root=(120,123),joint=(117,141),ankle=(118,153),sole=(120,157))
source['far_hind']=dict(root=(85,122),joint=(76,141),ankle=(76,153),sole=(79,157))
Y,X=np.indices((192,192));GRID=np.stack([X,Y],2)
def fit(a,s0,s1,t0,t1):
 s0=np.array(s0,float);s1=np.array(s1,float);t0=np.array(t0,float);t1=np.array(t1,float)
 sv=s1-s0;tv=t1-t0;sl=np.linalg.norm(sv);tl=np.linalg.norm(tv);su=sv/sl;tu=tv/tl;sn=np.array([-su[1],su[0]]);tn=np.array([-tu[1],tu[0]])
 v=GRID-t0;along=v@tu;across=v@tn;src=s0+along[...,None]*(sl/tl)*su+across[...,None]*sn
 ix=np.rint(src).astype(int);valid=(ix[:,:,0]>=0)&(ix[:,:,0]<192)&(ix[:,:,1]>=0)&(ix[:,:,1]<192);out=np.zeros_like(a);out[valid]=a[ix[:,:,1][valid],ix[:,:,0][valid]]
 return Image.fromarray(out)
def foot(a,s,rec):
 cx,by=rec['target'];wx,wy=rec['wrist'];sx,sy=s['sole'];ax,ay=s['ankle']
 # Inverse native row sampling avoids the raster gaps of forward stamping.
 t=np.clip((by-Y)/max(1,by-wy),0,1)
 srcy=ay+(Y-wy)*(sy-ay)/max(1,by-wy)
 dx=(cx-sx)*(1-t)+(wx-ax)*t
 ix=np.floor(X-dx+.5).astype(int);iy=np.floor(srcy+.5).astype(int)
 valid=(ix>=0)&(ix<192)&(iy>=0)&(iy<192)&(Y<=by)
 out=np.zeros_like(a);out[valid]=a[iy[valid],ix[valid]]
 return Image.fromarray(out)
def paint_leg(rec):
 name=rec['name'];typ='fore' if name.endswith('fore') else 'hind';near=name.startswith('near');key=typ if near else name;s=source[key];root=rec['root'];joint=rec['joint'];wrist=rec['wrist'];cx,by=rec['target']
 im=Image.new('RGBA',(192,192))
 im.alpha_composite(fit(upper[key],s['root'],s['joint'],root,joint))
 im.alpha_composite(fit(lower[key],s['joint'],s['ankle'],joint,wrist))
 # Native shoulder/hip join: stepped plate rim is repainted over the body overlap.
 rx,ry=root
 if near:
  if typ=='fore':
   ln(im,[(rx-2,ry-6),(rx,ry-5),(rx+1,ry-3)],6)
   ln(im,[(rx+5,ry-1),(rx+5,ry+1),(rx+4,ry+3)],4)
  else:
   ln(im,[(rx-3,ry-4),(rx,ry-4),(rx+2,ry-2)],6)
   ln(im,[(rx+4,ry),(rx+4,ry+2)],4)
 else:
  ln(im,[(rx+1,ry+1),(rx+2,ry+3)],1)
 # Joint bridge follows the red guard's stepped rim. It overlaps both transformed ends.
 j=np.array(joint,float);v=np.array(wrist)-j;u=v/np.linalg.norm(v);n=np.array([-u[1],u[0]])
 def q(a,b):return tuple(j+u*a+n*b)
 poly(im,[q(-2,-2),q(-3,0),q(-1,2),q(2,2),q(3,1),q(2,-2)],3 if near else 2)
 poly(im,[q(-2,-2),q(-2,0),q(1,1),q(2,0),q(1,-1)],5 if near else 3)
 ln(im,[q(-2,-2),q(-1,-1)],7 if near else 5)
 ln(im,[q(2,2),q(3,1)],2)
 # Ankle collar is drawn around the bend, not a cut edge of a transformed shank.
 wx,wy=wrist
 poly(im,[(wx-2,wy-2),(wx+1,wy-2),(wx+2,wy),(wx+2,wy+2),(wx,wy+3),(wx-2,wy+1)],3 if near else 2)
 ln(im,[(wx-2,wy),(wx,wy+1),(wx+1,wy+1)],2)
 im.alpha_composite(foot(feet[key],s,rec))
 # Explicit pixel joins, toe separations and claw tips, all at native resolution.
 # Restore each toe's native ramp instead of the previous flat red pad.
 if typ=='fore':
  ln(im,[(cx-1,by-3),(cx,by-2)],2);ln(im,[(cx+2,by-2),(cx+3,by-1)],2)
  ln(im,[(cx+1,by-1),(cx+2,by-1)],7);ln(im,[(cx+4,by-1),(cx+5,by-1)],3)
 else:
  ln(im,[(cx-1,by-3),(cx,by-2)],2);ln(im,[(cx+2,by-2),(cx+2,by-1)],2)
 # Ground footprint span is fixed, retaining the reference's uneven claw bottoms.
 a=np.array(im);a[by+1:]=0
 # Native sole endpoints; replace no intermediate sole pixels with a flat bar.
 for x in [cx-5,cx+5]:
  a[by,x]=P[0];a[by-1,x]=P[2]
 # Ensure traced body root joins stay whole; no transverse cut line is added.
 if False:
  # Same armour and toes in the still's far-side shadow colour bands.
  for old,new in [(9,6),(6,4),(7,5),(5,3),(3,2)]:
   mask=np.all(a[:,:,:3]==P[old][:3],2)&(a[:,:,3]>0)
   # use original colour comparisons simultaneously below instead of cascading
  b=a.copy();mapping={9:6,6:4,7:5,5:3,3:2}
  for old,new in mapping.items():b[np.all(a==P[old],2)]=P[new]
  a=b
 return Image.fromarray(a)
(R/'walk/frames').mkdir(parents=True,exist_ok=True);(R/'walk/layers').mkdir(parents=True,exist_ok=True)
alllegs={};frames=[]
for f in range(8):
 layers={rec['name']:paint_leg(rec) for rec in records if rec['frame']==f};alllegs[f]=layers
 can=Image.new('RGBA',(192,192))
 for name in ['far_hind','far_fore']:can.alpha_composite(layers[name])
 can.alpha_composite(env['tail'](f));can.alpha_composite(env['body'](f))
 for name in ['near_hind','near_fore']:can.alpha_composite(layers[name])
 a=np.array(can);m=a[:,:,3]>0;holes=ndi.binary_fill_holes(m)&~m
 # Resolve enclosed one-pixel raster joins with local material, never growing the silhouette.
 ids=ndi.distance_transform_edt(~m,return_distances=False,return_indices=True);a[holes]=a[ids[0][holes],ids[1][holes]]
 a[161:]=0
 # The original composite is authoritative outside the old and replacement limbs.
 oldframe=np.array(Image.open(OLD/'walk/frames'/f'side_f{f}.png').convert('RGBA'))
 limbmask=np.zeros((192,192),bool)
 for name in layers:
  limbmask|=np.array(layers[name])[:,:,3]>0
  limbmask|=np.array(Image.open(OLD/'walk/layers'/f'{name}_f{f}.png'))[:,:,3]>0
 a[~limbmask]=oldframe[~limbmask]
 frames.append(a);Image.fromarray(a).save(R/'walk/frames'/f'side_f{f}.png')
 for name,im in layers.items():im.save(R/'walk/layers'/f'{name}_f{f}.png')
# Use the supplied game's exact selout function, no module execution/writes.
sp=R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py';st=ast.parse(sp.read_text());se=dict(np=np,OUTLINE=np.array(P[0][:3],np.uint8));exec(compile(ast.Module(body=[n for n in st.body if isinstance(n,ast.FunctionDef) and n.name=='selout'],type_ignores=[]),str(sp),'exec'),se)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);bg=(78,86,82,255);cw=512;ch=352
board=Image.new('RGBA',(cw*8,ch*3),bg);d=ImageDraw.Draw(board)
def tile(a):return Image.fromarray(se['selout'](a)[0]).crop((32,88,160,169)).resize((512,324),Image.Resampling.NEAREST)
board.alpha_composite(tile(ref),(0,28));d.text((8,4),'APPROVED fixed/e.png / 4x sel-out',font=font,fill='white')
for row,seq,label in [(1,[np.array(Image.open(OLD/'walk/frames'/f'side_f{f}.png').convert('RGBA')) for f in range(8)],'WALK2'),(2,frames,'WALK3')]:
 for f,a in enumerate(seq):board.alpha_composite(tile(a),(cw*f,ch*row+28));d.text((cw*f+8,ch*row+4),f'{label} f{f} / 100 ms',font=font,fill='white')
board.convert('RGB').save(R/'board.png')
board.resize((2048,528),Image.Resampling.NEAREST).convert('RGB').save(R/'board_small.png')
pics=[]
for a in frames:
 im=Image.new('RGBA',(512,324),bg);im.alpha_composite(tile(a));pics.append(im.convert('RGB'))
pics[0].save(R/'preview.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2,optimize=False)
# Upright detailed review tile and source segments, for native contour inspection.
detail=Image.new('RGBA',(4*512,2*352),bg)
for f in range(8):detail.alpha_composite(tile(frames[f]),((f%4)*512,(f//4)*352+20))
detail.convert('RGB').save(R/'details.png')
print('Built 8 frames, board and preview. Output:',R)
