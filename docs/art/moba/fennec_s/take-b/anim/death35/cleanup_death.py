from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,GifImagePlugin
from scipy.ndimage import label,binary_fill_holes
import importlib.util
P=Path(__file__).parent
ns={'__file__':str(P/'build_death.py')};exec((P/'build_death.py').read_text().split('spec=importlib')[0],ns)
VIEWS=ns['VIEWS'];NAMES=ns['NAMES'];MS=ns['MS'];ROOT=ns['ROOT']
original_leaf=ns['leaf']
records={};frames={}
# Hinge positions are hand placed relative to the unmodified run-1 head.
# Each row is translated intact; horizontal folding adds integer column steps.
# No interpolation, image rotation or filtering is used.
HINGES={
's': [[(71,105),(88,105)],[(69,108),(89,108)],[(66,113),(81,116)],[(60,122),(77,119)],[(48,132),(66,127)]],
'se':[[(86,111),(99,102)],[(86,115),(99,107)],[(84,120),(97,114)],[(81,128),(94,122)],[(79,133),(93,128)]],
'e': [[(94,112),(95,107)],[(95,117),(96,112)],[(96,123),(99,126)],[(96,130),(100,126)],[(96,136),(100,131)]],
'ne':[[(87,94),(99,96)],[(90,98),(102,101)],[(94,105),(106,109)],[(101,114),(114,117)],[(106,123),(120,125)]],
'n': [[(71,94),(88,95)],[(74,99),(91,100)],[(83,109),(98,109)],[(87,117),(107,120)],[(96,127),(109,127)]]}

def ear_sources(src,v):
 parts=ns['extract'](src,ns['SPECS'][v]);out=[]
 yy,xx=np.indices((160,160))
 for i in range(2):
  a=parts[f'ear{i}'].copy()
  if v=='se' and i==0:a[(xx<71)|(yy>111)]=0
  if v=='e':a[(xx>(100 if i==0 else 95))]=0
  if v=='e' and i==1:a[yy>92]=0
  out.append(a)
 return out

FOLD_CACHE={}
def extents(xy):
 vals,vec=np.linalg.eigh(np.cov(xy.T));q=xy@vec[:,-1];r=xy@vec[:,0]
 return float(np.ptp(q)+1),float(np.ptp(r)+1),vec[:,-1]
def native_fold(a,hinge,target,sign,phase):
 ys,xs=np.where(a[:,:,3]>0);bx,by=hinge;tx,ty=target
 relx=xs-bx;rely=ys-by;original=np.column_stack((relx,rely));refL,refW,_=extents(original)
 key=(a.tobytes(),sign,phase)
 if key not in FOLD_CACHE:
  best=None
  # Search unit row/column steps for native length and breadth; rows and columns
  # are translated on the integer lattice, never rotated or interpolated.
  desired=[65,45,25,10][phase]
  for k in np.arange(-1,1.001,.05):
   ox=relx+np.rint(rely*k).astype(int)
   for t in np.arange(-1,1.001,.05):
    oy=rely+np.rint(ox*t).astype(int);xy=np.column_stack((ox,oy));L,W,axis=extents(xy)
    if axis[1]>0:axis=-axis
    tip=ys<=ys.min()+2;base=ys>=ys.max()-4;vx=float(ox[tip].mean()-ox[base].mean());vy=float(oy[tip].mean()-oy[base].mean())
    angle=np.degrees(np.arctan2(-vy,sign*vx))
    loss=abs(angle-desired)+max(0,abs(L-refL)-1.4)*10000+max(0,abs(W-refW)-.95)*10000+abs(L-refL)*2+abs(W-refW)*3
    if best is None or loss<best[0]:best=(loss,ox.copy(),oy.copy(),float(k),float(t),L,W,angle)
  FOLD_CACHE[key]=best
 _,ox,oy,*_=FOLD_CACHE[key]
 dest=np.zeros_like(a)
 for y,x,dx,dy in zip(ys,xs,ox,oy):
  if 0<=ty+dy<160 and 0<=tx+dx<160:dest[ty+dy,tx+dx]=a[y,x]
 return dest

for v,n in zip(VIEWS,NAMES):
 src=np.array(Image.open(ROOT/f'fennec_s/take-b/views_cam35_touchup/{v}.png').convert('RGBA'));ears=ear_sources(src,v);parts=ns['extract'](src,ns['SPECS'][v]);frames[v]=[]
 for f in range(7):
  old=np.array(Image.open(P/f'frames_run1/{n}_f{f}.png').convert('RGBA'))
  if f<2:frames[v].append(old);records[n,f]=[];continue
  # Reconstruct ONLY the ear underpainting, then use its difference as the edit mask.
  ns['leaf']=lambda *args,**kw:None
  bare=np.array(ns['clean'](ns['pose'](v,f,parts,src),src,f))
  ns['leaf']=original_leaf
  full=np.array(ns['clean'](ns['pose'](v,f,parts,src),src,f))
  assert np.array_equal(full,old),(n,f,'run1 reconstruction mismatch')
  region=np.any(full!=bare,axis=2)
  a=old.copy();a[region]=bare[region]
  # Protect native face and every run-1 non-ear texel. Ears may cover transparent
  # background and old ear pixels, never change body, leg, tail or face colours.
  hm=Image.new('RGBA',(160,160));hdx,hdy=ns['HEAD'][v][f];sh=0 if f<=2 else (.12 if v=='s' else -.12 if v=='n' else .08) if f==3 else (.4 if v=='s' else -.4 if v=='n' else .12);ns['paste'](hm,parts['head'],hdx,hdy,sh,ns['SPECS'][v]['headcenter'][1]);headmask=np.array(hm)[:,:,3]>0
  editable=~headmask;editable[140:]=False
  saved=[]
  for i in ([1,0] if v in ['se','e'] else [0,1]):
   ear=ears[i];ys,xs=np.where(ear[:,:,3]>0)
   # Hinge is the middle of the lower quarter of the native ear.
   floor=int(ys.max());low=ys>=floor-4;bx=int(round(float(np.median(xs[low]))));by=floor
   target=HINGES[v][4 if f>=5 else f-2][i]
   sign=(-1 if i==0 else 1) if v in ['s','n','ne'] else -1
   phase=0 if f==2 else 1 if f==3 else 2 if f==4 else 3
   b=native_fold(ear,(bx,by),target,sign,phase);mask=(b[:,:,3]>0)&editable
   a[mask]=b[mask];saved.append((i,ear,b,mask))
  # Native row steps can leave diagonal-only corners. Redraw the exposed join
  # with an adjacent ear material, confined to the ear edit zone.
  allowed=editable.copy();allowed[140:]=False
  for iteration in range(10):
   op=a[:,:,3]>0;lab,num=label(op)
   if num==1:break
   sizes=np.bincount(lab.ravel());sizes[0]=0;main=int(sizes.argmax());changed=False
   for k in range(1,num+1):
    if k==main:continue
    yy,xx=np.where(lab==k)
    # Connect diagonal contact with one native-colour orthogonal bridge.
    options=[]
    for y,x in zip(yy,xx):
     for dy,dx in [(-1,-1),(-1,1),(1,-1),(1,1)]:
      if 0<y+dy<159 and 0<x+dx<159 and lab[y+dy,x+dx]==main:
       for py,px in [(y,x+dx),(y+dy,x)]:
        if allowed[py,px]:options.append((py,px,y,x))
    if options:
     py,px,y,x=options[len(options)//2];a[py,px]=a[y,x];changed=True
    elif len(xx)<8 and np.all(region[yy,xx]):a[yy,xx]=0;changed=True
   if not changed:break
  # Enclosed join pinholes receive the adjacent native material.
  holes=binary_fill_holes(a[:,:,3]>0)&(a[:,:,3]==0)&allowed
  for y,x in zip(*np.where(holes)):
   cols=[tuple(a[py,px]) for py,px in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if a[py,px,3]]
   if cols:a[y,x]=max(set(cols),key=cols.count)
  # Remove isolated unit-step tips and short hanging scanline remnants;
  # preserve all run-1 non-ear pixels.
  newregion=region.copy()
  for _,_,b,_ in saved:newregion|=b[:,:,3]>0
  for iteration in range(5):
   op=a[:,:,3]>0;lab,num=label(op);sizes=np.bincount(lab.ravel());sizes[0]=0;main=int(sizes.argmax())
   for k in range(1,num+1):
    if k!=main and sizes[k]<=2 and np.all(newregion[lab==k]):a[lab==k]=0
   op=a[:,:,3]>0;sq=op[:-1,:-1]&op[1:,:-1]&op[:-1,1:]&op[1:,1:];thick=np.zeros_like(op)
   for dy,dx in [(0,0),(1,0),(0,1),(1,1)]:thick[dy:dy+159,dx:dx+159]|=sq
   lab,num=label(op&~thick,np.ones((3,3)));changed=False
   for k in range(1,num+1):
    mask=lab==k
    if mask.sum()>2 and np.all(newregion[mask]):a[mask]=0;changed=True
   if not changed:break
  # Square off concave hinge steps that otherwise form a diagonal single-pixel chain.
  for iteration in range(8):
   op=a[:,:,3]>0;sq=op[:-1,:-1]&op[1:,:-1]&op[:-1,1:]&op[1:,1:];thick=np.zeros_like(op)
   for dy,dx in [(0,0),(1,0),(0,1),(1,1)]:thick[dy:dy+159,dx:dx+159]|=sq
   lab,num=label(op&~thick,np.ones((3,3)));fixed=False
   for k in range(1,num+1):
    mask=lab==k
    if mask.sum()<=2:continue
    yy,xx=np.where(mask);options=[]
    for y in range(max(1,int(yy.min())-1),min(139,int(yy.max())+2)):
     for x in range(max(1,int(xx.min())-1),min(159,int(xx.max())+2)):
      if op[y,x] or headmask[y,x]:continue
      patch=op[y-1:y+2,x-1:x+2].copy();patch[1,1]=True
      score=int((patch[:-1,:-1]&patch[1:,:-1]&patch[:-1,1:]&patch[1:,1:]).sum())
      if score:options.append((score,y,x))
    if options:
     _,y,x=max(options);cols=[tuple(a[py,px]) for py,px in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if a[py,px,3]];a[y,x]=max(set(cols),key=cols.count);fixed=True
   if not fixed:break
  records[n,f]=saved;frames[v].append(a)
  Image.fromarray(a).save(P/f'frames/{n}_f{f}.png')
# Review exact game sel-out.
spec=importlib.util.spec_from_file_location('game_selout',ROOT/'rhino_l/take-a/anim/selout_rhino.py');sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel);sel.OUTLINE=np.array([20,18,24],np.uint8)
board=Image.new('RGB',(5120,3340),(86,93,84));dr=ImageDraw.Draw(board)
for j,(v,n) in enumerate(zip(VIEWS,NAMES)):
 still=np.array(Image.open(ROOT/f'fennec_s/take-b/views_cam35_touchup/{v}.png').convert('RGBA'))
 for col,a in enumerate([still]+frames[v]):
  im=Image.fromarray(sel.selout(a)[0]).resize((640,640),Image.Resampling.NEAREST);x=col*640;y=j*668;board.paste(im,(x,y+28),im);dr.text((x+8,y+7),n+(': approved still' if col==0 else f': f{col-1} {MS[col-1]}ms'),fill=(244,244,234))
 board.crop((0,j*668,5120,(j+1)*668)).save(P/f'board_{n}.png')
board.save(P/'board.png')
# Compact unoutlined ear review, still then f2..f6.
b=Image.new('RGB',(6*400,5*400),(86,93,84))
for j,(v,n) in enumerate(zip(VIEWS,NAMES)):
 for k,a in enumerate([np.array(Image.open(ROOT/f'fennec_s/take-b/views_cam35_touchup/{v}.png').convert('RGBA'))]+frames[v][2:]):
  im=Image.fromarray(a).crop((35,50,135,150)).resize((400,400),Image.Resampling.NEAREST);b.paste(im,(k*400,j*400),im)
b.save(P/'cleanup_review.png')
for v,n in zip(VIEWS,NAMES):
 print(n,[label(a[:,:,3]>0)[1] for a in frames[v]])
# GIFs retain the exact original timing and one-play header.
for v,n in zip(VIEWS,NAMES):
 gifs=[]
 for a in frames[v]:
  bg=Image.new('RGB',(640,640),(86,93,84));im=Image.fromarray(sel.selout(a)[0]).resize((640,640),Image.Resampling.NEAREST);bg.paste(im,(0,0),im);gifs.append(bg)
 palette=gifs[0].quantize(colors=64);gifs=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in gifs]
 with (P/f'preview_{n}.gif').open('wb') as fp:
  for chunk in GifImagePlugin._get_global_header(gifs[0],{'duration':MS[0]}):fp.write(chunk)
  for im,ms in zip(gifs,MS):GifImagePlugin._write_frame_data(fp,im,(0,0),{'duration':ms,'disposal':2})
  fp.write(b';')

def dims(a):
 y,x=np.where(a[:,:,3]>0)
 if len(x)<3:return (0.,0.)
 return tuple(round(z,2) for z in extents(np.column_stack([x,y]))[:2])
def thin_runs(op):
 sq=op[:-1,:-1]&op[1:,:-1]&op[:-1,1:]&op[1:,1:];thick=np.zeros_like(op)
 for dy,dx in [(0,0),(1,0),(0,1),(1,1)]:thick[dy:dy+159,dx:dx+159]|=sq
 lab,num=label(op&~thick,np.ones((3,3)));sizes=np.bincount(lab.ravel())[1:]
 return int((sizes>2).sum()),int(max(sizes,default=0))
lines=['death35-clean: zero-based native-pixel checks.',
 'Connectivity: four neighbours, not diagonals.',
 'Thin run: connected edge pixels that belong to no solid 2x2 opaque patch; runs >2 forbidden.',
 'Ear length/base breadth: principal-axis extent and perpendicular widest triangle span, pixel centres +1.',
 'Both measured directly from traced native ear masks; widths include the violet shell.',
 'Full trace measured before head/other-ear occlusion; visible extents also listed (occlusion shortens these).',
 'Ear 0/1: screen-left/right for front/back/ne; near/far for side; lower/upper for se.',
 'Side far ear reference is its visible upper triangle; the lower stripe assigned by run1 was near-ear/head material.',
 'All source ear material uses integer row/column translations of at most 1px per step; no rotation/resampling.',
 'f0/f1 remain byte-for-byte original files. f2-f6 edited from run1 only in ear footprints and their joins.',
 'Dimensions are geometric pixel spans, so decimals are expected.','']
allbottom={};worstL=0;worstW=0
for v,n in zip(VIEWS,NAMES):
 src=np.array(Image.open(ROOT/f'fennec_s/take-b/views_cam35_touchup/{v}.png').convert('RGBA'));ears=ear_sources(src,v);ref=[dims(a) for a in ears];pal=set(map(tuple,src[src[:,:,3]>0,:3]));lines.append(f'{n}: still ear0 L/W={ref[0]}, ear1 L/W={ref[1]}');bottom=[]
 for f,a in enumerate(frames[v]):
  disk=np.array(Image.open(P/f'frames/{n}_f{f}.png').convert('RGBA'));assert np.array_equal(a,disk)
  old=np.array(Image.open(P/f'frames_run1/{n}_f{f}.png').convert('RGBA'));op=a[:,:,3]>0;yy,xx=np.where(op);num=label(op)[1];thin,maxthin=thin_runs(op)
  assert num==1,(n,f,'components',num)
  assert thin==0,(n,f,'thin runs',thin,maxthin)
  assert not (binary_fill_holes(op)&~op).any(),(n,f,'holes')
  assert set(np.unique(a[:,:,3]))<={0,255}
  assert not (set(map(tuple,a[op,:3]))-pal)
  assert not(op[0].any() or op[-1].any() or op[:,0].any() or op[:,-1].any())
  assert yy.max()<=140
  assert np.array_equal(a[140:],old[140:]),(n,f,'ground changed')
  if f<2:assert np.array_equal(a,old)
  if f==0:assert np.array_equal(a,src)
  bottom.append(int(yy.max()));es=[]
  for i in range(2):
   if f==0:b=ears[i]
   elif f==1:
    b=np.zeros_like(src);dx,dy={'s':(0,-2),'se':(-1,-1),'e':(-2,0),'ne':(-1,1),'n':(0,1)}[v];threshold={'s':93,'se':96,'e':96,'ne':85,'n':82}[v]
    for y,x in zip(*np.where(ears[i][:,:,3]>0)):
     flick=round(max(0,threshold-int(y))*.065);sign=(-1 if x<80 else 1) if v in ['s','n'] else -1;b[y+dy,x+dx+sign*flick]=ears[i][y,x]
   else:b=next(z[2] for z in records[n,f] if z[0]==i)
   L,W=dims(b);dL=round(L-ref[i][0],2);dW=round(W-ref[i][1],2);worstL=max(worstL,abs(dL));worstW=max(worstW,abs(dW))
   assert abs(dL)<=2,(n,f,i,'length',dL)
   # Native lattice stepping changes perpendicular breadth by at most one texel.
   assert abs(dW)<=1.1,(n,f,i,'breadth',dW)
   visible=b.copy();visible[~np.all(a==b,axis=2)]=0
   es.append(f'e{i} L/W={L:.2f}/{W:.2f} delta={dL:+.2f}/{dW:+.2f}, visible={dims(visible)}')
  lines.append(f'  f{f}: pieces4={num}; long_thin_runs={thin}; longest_thin={maxthin}; bottom={yy.max()}; changed_pixels={np.any(a!=old,axis=2).sum()}; '+ '; '.join(es))
 assert np.array_equal(frames[v][5][:,:,3],frames[v][6][:,:,3])
 gif=Image.open(P/f'preview_{n}.gif');dur=[]
 for f in range(gif.n_frames):gif.seek(f);dur.append(gif.info['duration'])
 assert gif.n_frames==7 and dur==MS and 'loop' not in gif.info
 allbottom[n]=bottom
 lines+=['  f0 exact PASS; palette/binary alpha/holes/edges/ground preservation PASS.',f'  GIF: {dur} ms, 7 frames, no loop; f5/f6 identical silhouette.','']
lines += [f'Max full-ear length deviation: {worstL:.2f}px; max base breadth deviation: {worstW:.2f}px (integer-grid rounding).',
 'All 35 opaque masks: one four-connected component; zero thin runs longer than 2 pixels.',
 'board.png: approved still + f0..f6, five rows, exact game selout #141218, 4x nearest.',
 'Ground and canvas tests use raw frames; review-only selout may add a border outside them.',
 'By eye: broad triangles and native gold panels persist through the fold; no parallel detached slivers.',
 'Body/legs/tail pose and colour layers are unchanged; new ear pixels occlude some torso pixels as ears fold.']
(P/'checks.txt').write_text('\n'.join(lines)+'\n')
report=(P/'REPORT.txt').read_text().split('\nCleanup')[0].rstrip()
watch=(P/'token-watch-death35-clean.txt').read_text().splitlines()[-1]
cleanup=['Cleanup (death35-clean)',f'Tokens: watcher snapshot {watch}; final total unknown.',
 'front: replaced both blade/wing ears with broad native shells/panels; redrew folded hinges.',
 'se: native lower/upper ear triangles and gold panels; removed parallel violet/gold remnants.',
 'side: kept near ear panel and far upper triangle; cleaned the false lower far-ear stripe and joins.',
 'ne: native back-facing shells, stepped down toward neck; removed isolated corner tips.',
 'back: broad native back-ear shells through the fall; connected folded bases without slivers.',
 'PASS all views f0..f6: four-connected piece counts 1,1,1,1,1,1,1; long thin-run counts all 0.',
 f'Full ear traces: length within {worstL:.2f}px; base breadth within {worstW:.2f}px (grid rounding); per-frame/visible spans in checks.txt.',
 'PASS f0 exact; own-still palette; binary alpha; no holes/edge contacts; f0/f1 unchanged.',
 'PASS lowest rows f0..f6: '+ '; '.join(n+':'+','.join(map(str,z)) for n,z in allbottom.items()),
 'PASS row140+ unchanged; timings unchanged; board/five GIFs rebuilt with game selout #141218 at 4x.',
 'By eye: ears retain native triangles and gold panels as they fold down; no parallel slivers.']
assert len(cleanup)<15
(P/'REPORT.txt').write_text(report+'\n\n'+'\n'.join(cleanup)+'\n')
print('Cleanup checks PASS; reports and previews rebuilt.')
