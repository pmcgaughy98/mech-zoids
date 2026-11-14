from repair import *
COL={k:'#'+c for c,k in [('141218','#'),('211e27','d'),('2e1a6e','v'),('3d3a44','g'),('6a3cc8','P'),('9d9ba2','s'),('a46bff','L'),('b8923a','b'),('d6d6dc','w'),('e0c8ff','h'),('f0d27a','Y'),('3fe8b0','t'),('c8fff0','T'),('fff4d6','C'),('f6fffb','W')]}
changes=[]
def edit(m,v,i,fn,note):
 p=files(m,v)[i];old=p.parent.parent/'frames_pre_repair'/p.name
 im=Image.open(old if old.exists() else p).convert('RGBA');before=np.array(im).copy();fn(im)
 if np.array_equal(before,np.array(im)):return
 old.parent.mkdir(exist_ok=True)
 if not old.exists():shutil.copy2(p,old)
 im.save(p);changes.append(dict(move=m,view=v,frame=i,pixels=int(np.any(before!=np.array(im),axis=2).sum()),repair=note))
def rect(im,box,c):ImageDraw.Draw(im).rectangle(box,fill=(0,0,0,0) if c=='.' else COL[c])
def poly(im,pts,c):ImageDraw.Draw(im).polygon(pts,fill=COL[c])
def line(im,pts,c):ImageDraw.Draw(im).line(pts,fill=COL[c])
def walkse(im):
 # Exact empty side of native ear contour. Preserve native ear and face.
 for y,left in [(122,96),(123,97),(124,99),(125,101),(126,102),(127,102),(128,102)]:rect(im,(88,y,left-1,y),'.')
 for y in range(129,135):rect(im,(115,y,128,y),'.')
 # Close the jaw underside at its actual termination, leaving the throat behind it.
 line(im,[(115,128),(121,128),(122,127)],'v')
 line(im,[(114,129),(114,132),(113,134)],'d')
 # Remove the generated foot/leg spikes on the right of the far shin.
 for y in range(140,154):
  a=np.array(im)
  # native shin occupies <=117; scraps project 1-3 px to its right
  if y in [142,143,149,150]:rect(im,(118,y,122,y),'.')
for i in range(8): edit('walk','se',i,walkse,'Removed old ear wedge, second muzzle, throat scrap and shin spurs; closed jaw/throat outline.')
def walkne(im):
 for y,left in [(122,96),(123,98),(124,100),(125,100),(126,100)]:rect(im,(92,y,left-1,y),'.')
 line(im,[(100,124),(100,126)],'d')
for i in range(8):edit('walk','ne',i,walkne,'Removed rectangular left neck/head stub; joined rear skull to neck.')
# Rounded local bridge from clipped haunch lip to the existing tail root.
def bridge(im,x,y):
 # A tapered continuation of the existing flank into the tail root.
 for dy,left in [(-2,1),(-1,0),(0,0),(1,0),(2,1),(3,2)]:
  rect(im,(x-4 if dy<=0 else x-1,y+dy,x+left-1,y+dy),'.')
  rect(im,(x+left,y+dy,x+6,y+dy),'P')
  rect(im,(x+left,y+dy,x+left,y+dy),'v')
 # Upper light belongs to the back plane, lower purple to the flank plane.
 line(im,[(x+2,y-2),(x+5,y-2)],'L')
# These coordinates concern only the cut lip, not the joint disc.
for i,x,y in [(1,83,144),(2,83,145),(3,83,142),(4,83,145)]:
 edit('sand_kick','ne',i,lambda im,x=x,y=y:bridge(im,x,y),'Rounded chopped rear armour lip and shaded its connection into tail root.')
for i,x,y in [(1,82,144),(2,81,145),(4,82,145)]:
 edit('sand_kick','se',i,lambda im,x=x,y=y:bridge(im,x,y),'Closed haunch-to-tail notch and rebuilt cut rear armour edge.')
# Duplicate muzzle below the pasted native snout in the deep sand-kick crouch.
def sandse2(im):
 # Reapply bridge because edits always begin from original.
 bridge(im,81,145)
 for y in range(140,147):rect(im,(117,y,130,y),'.')
 line(im,[(115,139),(116,140),(116,143)],'v')
edit('sand_kick','se',2,sandse2,'Closed rear notch; removed second muzzle below native snout and finished throat.')
# Crouch backs clipped into sharp rectangular rear lips.
for v,items in [('se',[(1,82,143),(2,82,146),(3,82,146),(4,82,145),(5,82,144)]),('ne',[(1,83,144),(2,84,145),(3,84,145),(4,83,144),(5,83,145),(6,83,145)])]:
 for i,x,y in items:edit('sonic_boom',v,i,lambda im,x=x,y=y:bridge(im,x,y),'Rounded severed rear lip and connected haunch shading to tail root; retained previous touchup.')
def earne3(im):
 rect(im,(96,123,99,125),'.');line(im,[(100,124),(101,125),(103,125)],'d')
edit('ear_burst','ne',3,earne3,'Removed straight neck stub below raised head; tapered neck join.')
# Hand-drawn short back arches replacing the horizontal clipping boundary.
def back(im,pts):
 poly(im,pts,'P');line(im,pts[:-1],'L')
for v in ['se','ne']:
 edit('dig',v,1,lambda im:back(im,[(84,136),(87,134),(92,133),(97,133),(101,134),(105,136),(105,138),(85,138)]),'Rebuilt clipped upper back with shallow stepped armour arch into neck.')
 edit('dig',v,2,lambda im:back(im,[(79,147),(83,145),(89,144),(96,144),(102,145),(108,147),(108,149),(80,149)]),'Redrew straight-cut back above grounded legs as continuous stepped armour.')
def popne1(im):
 # Old generated neck bar hung above a missing left shoulder.
 rect(im,(86,148,99,153),'.')
 poly(im,[(86,154),(89,152),(92,151),(96,151),(100,152),(103,154),(102,157),(86,157)],'P')
 poly(im,[(87,154),(90,152),(96,152),(100,153),(101,155),(89,155)],'L')
 line(im,[(86,154),(89,152),(92,151),(96,151),(99,152)],'v')
edit('pop_out','ne',1,popne1,'Removed floating rectangular neck/back bar; completed partially emerged shoulder contour.')
for v in ['se','ne']:
 edit('pop_out',v,3,lambda im:back(im,[(83,140),(87,138),(92,137),(98,137),(103,138),(107,140),(106,142),(84,142)]),'Rebuilt flat-clipped landing back contour into neck.')
def deathse1(im):
 rect(im,(94,127,98,129),'.')
 line(im,[(99,127),(101,128),(103,129)],'d')
edit('death','se',1,deathse1,'Removed horizontal rear-neck spur and closed neck contour.')
# The deeper crouches have wider old lips, outside the small root patch.
for m,v,i,x,y in [('sand_kick','se',2,76,144),('sand_kick','ne',2,78,144),('sonic_boom','se',2,76,144),('sonic_boom','se',3,76,145)]:
 p=files(m,v)[i];im=Image.open(p).convert('RGBA')
 rect(im,(x-4,y-1,x+2,y+1),'.')
 poly(im,[(x+3,y-3),(x+8,y-4),(x+12,y-1),(x+11,y+5),(x+7,y+7),(x+3,y+4),(x+1,y)],'v')
 poly(im,[(x+4,y-3),(x+8,y-3),(x+11,y-1),(x+10,y+4),(x+7,y+5),(x+4,y+3),(x+2,y)],'P')
 line(im,[(x+4,y-3),(x+7,y-3),(x+9,y-2)],'L')
 im.save(p)
# Explicit texels closing gaps revealed only by the runtime outline.
for m,v,i,pts in [('walk','se',2,[(118,142,'v')]),('sand_kick','se',4,[(82,143,'P'),(82,147,'v'),(82,148,'v'),(83,148,'v')]),('sonic_boom','se',1,[(83,146,'v')]),('sonic_boom','se',4,[(82,143,'P'),(82,147,'v'),(82,148,'v'),(83,148,'v')]),('dig','ne',1,[(99,132,'P'),(99,133,'P')])]:
 p=files(m,v)[i];im=Image.open(p).convert('RGBA')
 for x,y,c in pts:im.putpixel((x,y),tuple(bytes.fromhex(COL[c][1:]))+(255,))
 im.save(p)
# Remove three specifically inspected disconnected remnants of the old horizontal lips.
for m,v,i,pts in [('sand_kick','ne',3,[(78,143),(79,143),(80,143),(81,143),(82,143),(77,144),(78,144),(79,144),(80,144),(81,144),(82,144)]),('sonic_boom','se',1,[(78,144),(79,144),(80,144),(81,144)]),('sonic_boom','ne',4,[(78,143),(78,144)])]:
 p=files(m,v)[i]; im=Image.open(p).convert('RGBA')
 for xy in pts: im.putpixel(xy,(0,0,0,0))
 im.save(p)
(OUT/'edits.json').write_text(json.dumps(changes,indent=2));print(len(changes),'repair entries',sum(x['pixels'] for x in changes),'pixels')
boards();audit()
