"""Adapted set B native finishing: whole generated drawings and direct pixel ink.
Idempotent: starts from underpaint. Approved stills used only for exact endpoints.
"""
from finish import *
C=[tuple(map(int,c))+(255,) for c in PAL]
LOG=[];TAIL=[]

def save(im,name,v,i,note):
 im=clean(im);bb=im.getbbox()
 if bb[3]!=161:
  grounded=Image.new('RGBA',(192,192));grounded.alpha_composite(im,(0,161-bb[3]));im=grounded
 im.save(R/name/'frames'/f'{v}_f{i}.png')
 LOG.append(dict(move=name,view=v,frame=i,note=note))

# The complete old tail is covered by the native repaint, with the same axis.
# No cut-out still parts, no copied texels, no cropped head/limb patches.
# Root centres tagged against six-times native coordinate inspection boards.
ROOT={
 'hamstring':{'se':[(83,124),(83,126),(83,126),(83,123)],'ne':[(94,126),(94,128),(94,129),(94,125)]},
 'howl':{'se':[(83,124),(83,123),(83,123),(83,123)],'ne':[(94,127),(94,125),(94,125),(94,125)]},
 'death':{'se':[(84,124),(84,129),(84,139),(84,140),(84,148)],'ne':[(94,126),(94,131),(94,141),(94,143),(94,149)]}}
# Manual reference axes include one endpoint pixel: SE (84,122)->(54,152),
# NE (94,126)->(58,158). Root widths 10 and 12px respectively.
AXIS={'se':np.sqrt(30**2+30**2),'ne':np.sqrt(36**2+32**2)}

def tail(im,name,v,i):
 # A continuous inverse coordinate map of the complete generated drawing retains
 # its original plate contours and paint. The former geometric redraw looked
 # too rectangular against the still and is not used in the final frames.
 root=np.array(ROOT[name][v][i-1],float)
 # Measured visible generated tip centres, not assumed reference endpoints.
 tips={'hamstring':{'se':[(55,150)]*4,'ne':[(58,158),(55,158),(55,158),(57,157)]},
       'howl':{'se':[(54,150),(54,151),(54,150),(54,150)],'ne':[(58,159),(58,158),(57,159),(58,158)]},
       'death':{'se':[(56,147),(56,150),(55,153),(52,152),(55,155)],'ne':[(58,158),(58,157),(57,157),(56,156),(55,157)]}}
 oldtip=np.array(tips[name][v][i-1],float);axis=oldtip-root;oldL=np.linalg.norm(axis)
 unit=axis/oldL;normal=np.array([-unit[1],unit[0]])
 # Reference measurements carry partly hidden socket length. Match the visible
 # tail, rather than adding that hidden distance outside the body as a new part.
 wanted={'se':39.,'ne':47.5}[v]
 factor=max(1.,wanted/oldL)
 if oldtip[1]>root[1]:factor=max(1.,min(factor,(158-root[1])/(oldtip[1]-root[1])))
 yy,xx=np.indices((192,192));dx=xx-root[0];dy=yy-root[1]
 u=dx*unit[0]+dy*unit[1];z=dx*normal[0]+dy*normal[1]
 # Smoothly taper to identity on the whole drawing around the socket and sides.
 strength=np.clip(u/10,0,1)*np.clip((10-np.abs(z))/3,0,1)
 su=u*(1-strength)+u/factor*strength
 sz=z
 sx=np.rint(root[0]+su*unit[0]+sz*normal[0]).astype(int)
 sy=np.rint(root[1]+su*unit[1]+sz*normal[1]).astype(int)
 a=np.array(im);b=np.zeros_like(a);valid=(sx>=0)&(sx<192)&(sy>=0)&(sy<192)
 b[valid]=a[sy[valid],sx[valid]]
 if name=='death' and ((v=='ne' and i>=2) or v=='se'):
  # In collapsed rear drawings the sheet foreshortened the exposed tail.
  # Extend its existing straight plate line horizontally, holding tip height.
  vr=np.array(({'ne':{2:(84,135),3:(84,143),4:(84,145),5:(84,150)},'se':{1:(78,124),2:(78,130),3:(78,141),4:(78,142),5:(78,150)}})[v][i],float)
  vt=np.array(({'ne':{2:(57,158),3:(54,158),4:(50,158),5:(50,159)},'se':{1:(54,151),2:(53,153),3:(49,155),4:(48,153),5:(46,157)}})[v][i],float)
  target_axis=41.23 if v=='ne' else 38.6
  target_dx=np.sqrt(max(1.,target_axis**2-(vt[1]-vr[1])**2))
  stretch=max(1.,target_dx/(vr[0]-vt[0]))
  desttip=np.array([vr[0]-target_dx,vt[1]])
  slope=(desttip[1]-vr[1])/(desttip[0]-vr[0])
  distance=np.abs(yy-(vr[1]+(xx-vr[0])*slope))/np.sqrt(1+slope*slope)
  wt=np.clip((11-distance)/3,0,1)*(xx<vr[0])
  xm=np.rint(xx+(vr[0]+(xx-vr[0])/stretch-xx)*wt).astype(int)
  ym=yy
  if v=='se' and i==4:
   # The rolled SE tail lost thickness in the raw sheet. Expand its existing
   # complete plate section around the straight centreline, not by pasting.
   centre=vr[1]+(xx-vr[0])*slope
   ym=np.rint(yy+(centre+(yy-centre)/1.42-yy)*wt).astype(int)
  b=b[np.clip(ym,0,191),np.clip(xm,0,191)]
 TAIL.append(dict(move=name,view=v,frame=i,root=root.tolist(),raw_tip=oldtip.tolist(),tail_visible_axis_px=float(oldL*factor+1),source_visible_axis_px=float(oldL+1),scale_length=float(factor),scale_width=1.0,grey_plates=3,red_tips=1,method='continuous whole-drawing inverse-map of original integrated tail; plate paint retained, no reference pixels'))
 return Image.fromarray(b)

def anchor_paws(im,v):
 # Adapted from set A gait_finish: continuous inverse coordinates to each
 # reference contact. No reference image colours or opaque patches are used.
 zones={'se':[(65,82),(85,96)],'ne':[(70,82),(82,105)]}[v]
 ref=np.array(Image.open(REF[v]));a=np.array(im);yy,xx=np.indices((192,192))
 for lo,hi in zones:
  src=(a[:,:,3]>0)&(xx>=lo)&(xx<hi)&(yy>=148)
  dst=(ref[:,:,3]>0)&(xx>=lo)&(xx<hi)&(yy>=148)
  sy0,sx0=np.where(src);ry,rx=np.where(dst)
  sb=int(sy0.max());db=int(ry.max())
  sf=np.where(src[sb])[0];df=np.where(dst[db])[0]
  wx=np.interp(xx,[lo,lo+2,hi-3,hi-1],[0,1,1,0])
  wy=np.clip((yy-137)/(db-137),0,1)
  xmap=np.interp(xx,[lo,df.min(),df.max(),hi-1],[lo,sf.min(),sf.max(),hi-1])
  sy=yy+(sb-db)*np.clip((yy-137)/(db-137),0,1)*wx
  sx=xx+(xmap-xx)*wy
  region=(xx>=lo)&(xx<hi)&(yy>=137)
  sx=np.rint(np.where(region,sx,xx)).astype(int);sy=np.rint(np.where(region,sy,yy)).astype(int)
  b=np.zeros_like(a);valid=(sx>=0)&(sx<192)&(sy>=0)&(sy<192);b[valid]=a[sy[valid],sx[valid]];a=b
 return Image.fromarray(a)

for name,ts in TIMES.items():
 for v in V:
  for i in range(1,len(ts)-(0 if name=='death' else 1)):
   if name=='death' and i==6:continue
   im=Image.open(R/name/'underpaint'/f'{v}_f{i}.png').convert('RGBA')
   a=np.array(im)
   # Back view retains occluded eye sockets, including during the raised howl.
   if v=='ne':
    cyan=np.all(a[:,:,:3]==PAL[8],2)&(a[:,:,3]>0);a[cyan,:3]=PAL[4]
   im=Image.fromarray(a)
   if name=='howl' and i in (2,3,4):
    # Keep the haunch-settle from f1 during the raising/open/release beats.
    # Continuous whole-drawing map bends the existing shanks forward at the
    # knee and back to their original ground contact; no limb is pasted.
    yy,xx=np.indices((192,192))
    nodes=[0,67,75,89,98,191] if v=='se' else [0,81,90,101,110,191]
    wx=np.interp(xx,nodes,[0,0,1,1,0,0])
    bend=np.interp(yy,[0,135,146,158,191],[0,0,8,0,0])
    sx=np.rint(xx-wx*bend).astype(int)
    a=np.array(im);im=Image.fromarray(a[yy,np.clip(sx,0,191)])
   if name=='hamstring':im=anchor_paws(im,v)
   im=tail(im,name,v,i);d=ImageDraw.Draw(im)
   if name=='hamstring' and v=='se' and i==2:
    # Open bite at lower-leg height: short projected jaw attached at the hinge.
    # Re-ink existing mouth, two joined sabres, no detached pasted patches.
    d.polygon([(125,145),(133,145),(133,151),(130,155),(124,152),(122,148)],fill=C[0])
    d.line([(123,149),(126,153),(131,155),(134,151)],fill=C[4],width=2)
    d.line([(125,145),(125,151)],fill=C[10],width=2)
    d.line([(126,145),(126,151)],fill=C[11])
    d.line([(132,146),(131,151)],fill=C[10])
   if name=='hamstring' and v=='se' and i==3:
    # Closed hit jaw, same two long teeth remaining outside the mouth.
    d.line([(125,146),(132,147)],fill=C[0],width=1)
    d.line([(125,147),(125,153)],fill=C[10],width=2)
    d.line([(132,147),(131,152)],fill=C[11],width=1)
   if name=='death' and v=='se' and i==5:
    # Two native pixels of ear-tip ink restore the sheet's short prone ears.
    d.polygon([(114,131),(117,134),(120,141),(118,142),(115,136)],fill=C[0])
    d.line([(115,133),(117,136),(118,140)],fill=C[4],width=2)
    d.point((115,132),fill=C[6])
    d.polygon([(125,131),(128,134),(129,142),(126,142)],fill=C[0])
    d.line([(126,133),(127,139)],fill=C[4],width=2)
    d.point((126,132),fill=C[6])
    # Preserve the prone camera and full legs: extend the generated folded near
    # hind leg continuously to a red paw rather than flattening the body.
    d.polygon([(77,151),(81,151),(87,156),(92,158),(91,160),(85,160),(80,157),(77,155)],fill=C[0])
    d.polygon([(78,151),(81,152),(87,156),(91,158),(89,159),(85,159),(80,156)],fill=C[3])
    d.line([(79,152),(85,156),(89,157)],fill=C[5],width=2)
    d.line([(86,158),(86,159)],fill=C[7])
    # Draw the existing near foreleg out beyond its tucked elbow, with a
    # connected armoured joint, red shank and splayed mechanical paw.
    d.polygon([(93,151),(98,150),(106,153),(115,155),(119,158),(118,160),(110,160),(101,157),(94,155)],fill=C[0])
    d.polygon([(95,152),(98,151),(106,154),(115,156),(118,158),(116,159),(110,159),(102,156),(95,154)],fill=C[3])
    d.line([(97,152),(106,155),(114,157)],fill=C[5],width=2)
    d.line([(114,157),(114,159)],fill=C[7])
    d.line([(116,158),(116,159)],fill=C[2])
   if name=='death' and v=='ne' and i==5:
    # Rear three-quarter near foreleg extends out on the ground, its shoulder
    # remains under the front armour; preserve away-facing head and fins.
    d.polygon([(121,148),(126,148),(134,152),(142,155),(146,158),(145,160),(137,160),(129,156),(122,153)],fill=C[0])
    d.polygon([(122,149),(126,149),(134,153),(142,156),(145,158),(143,159),(138,159),(130,155),(123,152)],fill=C[3])
    d.line([(124,150),(133,154),(141,157)],fill=C[5],width=2)
    d.line([(141,157),(141,159)],fill=C[7])
    d.line([(143,158),(143,159)],fill=C[2])
   save(im,name,v,i,'whole generated native drawing; direct mouth/tail/eye ink and connected contour cleanup')
  if name=='death':
   a=np.array(Image.open(R/name/'frames'/f'{v}_f5.png'));cyan=np.all(a[:,:,:3]==PAL[8],2)&(a[:,:,3]>0);a[cyan,:3]=PAL[4]
   # Exact same body and alpha as f5; only visible SE cyan eye changes.
   Image.fromarray(a).save(R/name/'frames'/f'{v}_f6.png')
   LOG.append(dict(move=name,view=v,frame=6,note='f5 body byte-identical RGBA except cyan eye colour to dark grey; rear eye already occluded'))

(R/'pixel_edits.json').write_text(json.dumps(LOG,indent=2))
(R/'tail_landmarks.json').write_text(json.dumps(TAIL,indent=2))
print('Native finishing:',len(LOG),'frames; tails',len(TAIL))
