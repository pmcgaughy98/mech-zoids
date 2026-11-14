from finish import *

def piece(im,mask):
 a=np.array(im).copy();a[~mask]=0;return Image.fromarray(a)

def shift(im,dx,dy):
 out=Image.new('RGBA',im.size);out.paste(im,(dx,dy));return out

def compose(parts):
 out=Image.new('RGBA',(192,192))
 for im,dx,dy in parts:out.alpha_composite(shift(im,dx,dy))
 return out

# Finish the small cyclic motions with the approved native texels. Generated
# pose sheets supply the action plan; no whole-frame translations or resizing.
for name in ['idle','walk']:
 (ROOT/name/'frames').mkdir(parents=True,exist_ok=True)
for n in NAMES:
 ref=approved(n);a=np.array(ref);yy,xx=np.indices((192,192));sx=xx-16;sy=yy-30
 upper=(sy<100)
 if n=='se':upper &= ~(((sx<84)|(sx>=105))&(sy>=91))
 else:upper &= ~(((sx<49)|(sx>=98))&(sy>=94))
 body=piece(ref,upper);fixed=piece(ref,~upper)
 for c,d in enumerate([0,1,2,1,0]):
  fr=compose([(ref,0,0),(body,0,-d),(fixed,0,0)])
  fr.save(ROOT/'idle'/'frames'/f'{n}_f{c}.png')
 if n=='se':
  arms=[(sx>=50)&(sx<84)&(sy>=91),(sx>=105)&(sy>=91)]
  legs=[(sx>=84)&(sx<100)&(sy>=111),(sx<52)&(sy>=106)]
 else:
  arms=[(sx>=98)&(sy>=94),(sx<49)&(sy>=94)]
  legs=[(sx>=45)&(sx<68)&(sy>=110),(sx>=74)&(sx<98)&(sy>=110)]
 used=np.zeros((192,192),bool);layers=[]
 for mask in arms+legs:
  mask &= ~used;used |= mask;layers.append(piece(ref,mask))
 torso=piece(ref,~used)
 liftsA=[0,0,0,0,0,-2,-3,-1];liftsB=[0,-2,-3,-1,0,0,0,0];bob=[0,-1,0,1,0,-1,0,1]
 for c in range(8):
  da,db=liftsA[c],liftsB[c];xa=[0,0,0,0,0,-2,0,2][c];xb=[0,-2,0,2,0,0,0,0][c]
  ta=np.array(torso);ground=ta.copy();ground[:159]=0;ta[159:]=0;moving=Image.fromarray(ta)
  fr=compose([(moving,0,0),(moving,0,bob[c]),(Image.fromarray(ground),0,0),(layers[2],xa,da),(layers[3],xb,db),(layers[0],xa,da),(layers[1],xb,(2 if n=='se' and c>=4 else db))])
  fr.save(ROOT/'walk'/'frames'/f'{n}_f{c}.png')
# Native idle has no generated sheet. Retain an explicitly labelled native contact sheet.
contact=Image.new('RGBA',(192*5,192*2))
cells=[]
for row,n in enumerate(NAMES):
 for c,d in enumerate([0,1,2,1,0]):
  contact.paste(Image.open(ROOT/'idle'/'frames'/f'{n}_f{c}.png'),(c*192,row*192))
  cells.append(dict(view=n,frame=c,source_box=[0,0,160,160],placement=[16,30],upper_lift=d,scale=1,touches_cut=False))
contact.save(ROOT/'idle'/'sheet_raw.png')
(ROOT/'idle'/'grid.json').write_text(json.dumps(dict(source='native approved parts; NO image generation',raw_size=list(contact.size),columns=5,rows=NAMES,x_edges=[i*192 for i in range(6)],y_edges=[0,192,384],row_scale={n:1 for n in NAMES},cells=cells),indent=2))
# Restore native face plates/eyes and back gem, fitting a translated template
# inside the generated head area. Pose silhouettes elsewhere remain generated.
boxes={'se':(87,81,106,95),'ne':(60,61,84,85)}
log=[]
for name in ['chest_beat','hex_shield']:
 for n in NAMES:
  patch=REFS[n].crop(boxes[n]);pa=np.array(patch);pg=(pa[:,:,1]>185)&(pa[:,:,0]<110)&(pa[:,:,3]>0);py,px=np.where(pg)
  for c in range(1,COUNTS[name]-1):
   path=ROOT/name/'frames'/f'{n}_f{c}.png';fr=Image.open(path).convert('RGBA');a=np.array(fr);bb=fr.getbbox();g=(a[:,:,1]>185)&(a[:,:,0]<110)&(a[:,:,3]>0);lab,k=ndi.label(g);candidates=[]
   for j in range(1,k+1):
    y,x=np.where(lab==j);cx,cy=x.mean(),y.mean()
    ok=(len(x)<30 and cx>90 and cy<bb[1]+.55*(bb[3]-bb[1])) if n=='se' else (len(x)>30 and cy<bb[1]+.35*(bb[3]-bb[1]))
    if ok:candidates.append((cx,cy,len(x)))
   if not candidates:log.append(f'{name}/{n}_f{c}: detail occluded, no stamp');continue
   cx,cy,_=min(candidates,key=lambda v:v[1]);x,y=round(cx-px.mean()),round(cy-py.mean());original=a[:,:,3]>0
   fr.alpha_composite(patch,(x,y));a=np.array(fr);a[~original]=0;Image.fromarray(a).save(path);log.append(f'{name}/{n}_f{c}: native face/back gem at {x},{y}')
(ROOT/'native_finish_log.txt').write_text('\n'.join(log)+'\n')
for name in COUNTS:board(name)
print('Native cycles and face/back-gem finish complete')
