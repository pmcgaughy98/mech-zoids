"""EX finish adapted: fixed ramps, one head-scaled whole-sheet nearest shrink."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from defringe import clean
P=Path(__file__).resolve().parent
TAKE=Path('D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a')
NAMES=['e','se','ne']; CROSS=nd.generate_binary_structure(2,1)
def specks(a):
 m=a[:,:,3]>0; total=0
 for c in np.unique(a[m,:3],axis=0):
  lab,n=nd.label(m&np.all(a[:,:,:3]==c,axis=2),CROSS)
  sz=np.bincount(lab.ravel())[1:]; total+=int(((sz>=1)&(sz<=2)).sum())
 return total
def regions(w,h):
 return [(round(c*w/6),round(r*h/3),round((c+1)*w/6),round((r+1)*h/3)) for r in range(3) for c in range(6)]
def note(s):
 with (P/'REPORT.txt').open('a') as f: f.write(s+'\n')
if __name__=='__main__':
 from despeckle import despeckle
 im=Image.open(P/'sheet_raw.png').convert('RGBA'); a=np.array(im); rgb=a[:,:,:3].astype(float)
 r,g,b=rgb.transpose(2,0,1); bg=(r>180)&(g<110)&(b>150); a[bg]=0; solid=~bg
 bad=solid&(r-g>25)&(b-g>25)&(b>r*.65); good=solid&~bad
 ix=nd.distance_transform_edt(~good,return_distances=False,return_indices=True); a[bad,:3]=a[ix[0][bad],ix[1][bad],:3]
 smooth=nd.median_filter(a[:,:,:3],size=(3,3,1),mode='nearest'); interior=nd.binary_erosion(solid,iterations=2)&((a[:,:,:3]@[.2126,.7152,.0722])>=40); a[interior,:3]=smooth[interior]
 # Visually identified first-column landmarks: E/SE horn tip -> primary eye; NE horn tip -> back/lower head edge.
 heads={'e':{'raw':[[261,109],[229.5,168]],'still':[[139,98],[127.2,123.4]]},'se':{'raw':[[236,130],[197.5,181]],'still':[[128,112],[113.5,132.75]]},'ne':{'raw':[[233,46],[215,138]],'still':[[127,58],[116,99]]}}
 for v,z in heads.items():
  z['raw_length']=float(np.linalg.norm(np.subtract(*z['raw']))); z['still_length']=float(np.linalg.norm(np.subtract(*z['still']))); z['factor']=z['still_length']/z['raw_length']
 factor=float(np.median([z['factor'] for z in heads.values()])); w=round(im.width*factor); h=round(im.height*factor)
 small=Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST); src=np.array(small); vis=src[:,:,3]>127
 rgb=src[:,:,:3].astype(float); r,g,b=rgb.transpose(2,0,1); lum=rgb@[.2126,.7152,.0722]
 pal=json.loads((TAKE/'palette.json').read_text()); colours=np.array([list(bytes.fromhex(c['hex'])) for c in pal],np.uint8)
 yellow=vis&(r>g*1.02)&(g>b*1.18)&(g>35); role=np.full(vis.shape,2); role[yellow]=0; role[vis&~yellow&(lum>=68)]=1
 dark=vis&~yellow&(lum<70); thin=dark&(nd.distance_transform_edt(dark)<=1.5)&nd.binary_erosion(vis)&nd.binary_dilation(vis&(lum>85),iterations=2); role[thin]=4
 cost=((rgb[:,:,None]-colours[None,None].astype(float))**2).sum(3)
 for k,c in enumerate(pal): cost[:,:,k]=np.where(role==['yellow','steel','charcoal','eye','accent'].index(c['role']),cost[:,:,k],1e12)
 nearest=cost.argmin(2); nearest[yellow]=np.select([lum[yellow]>215,lum[yellow]>163,lum[yellow]>105],[0,1,2],default=3)
 out=np.zeros_like(src); out[:,:,:3]=colours[nearest]; out[:,:,3]=np.where(vis,255,0); out[~vis]=0
 meta={'raw_sha256':hashlib.sha256((P/'sheet_raw.png').read_bytes()).hexdigest(),'raw_size':list(im.size),'heads':heads,'median_factor':factor,'actual_xy_scale':[w/im.width,h/im.height],'finished_size':[w,h],'rows':{},'eye_restored':[],'discarded_tiny_alpha':{},'despeckle':{},'ink':{},'closed_pinholes':{}}
 metrics=json.loads((P/'still_metrics.json').read_text())
 for k,box in enumerate(regions(w,h)):
  v=NAMES[k//6]; col=k%6; x0,y0,x1,y1=box; cell=out[y0:y1,x0:x1].copy(); m=cell[:,:,3]>0
  lab,n=nd.label(m,CROSS); counts=np.bincount(lab.ravel()); counts[0]=0; tiny=(counts<=2)&(counts>0); tiny[0]=False
  # One isolated 10-pixel pale fleck well below SE f3 is background debris, not anatomy.
  if v=='se' and col==3:
   for label in range(1,n+1):
    yy0,xx0=np.where(lab==label)
    if counts[label]<=10 and yy0.min()>110 and (cell[lab==label,:3]@[.2126,.7152,.0722]).mean()>145: tiny[label]=True
  remove=tiny[lab]; meta['discarded_tiny_alpha'][f'{v}{col}']=int(remove.sum()); cell[remove]=0
  rr,gg,bb=rgb[y0:y1,x0:x1].transpose(2,0,1); red=(rr>180)&(gg<115)&(bb<100)&(rr>gg*2)&nd.binary_erosion(cell[:,:,3]>0)
  lab,n=nd.label(red); counts=np.bincount(lab.ravel()); counts[0]=0
  if v!='ne' and counts.max()>0:
   yy,xx=np.where(lab==counts.argmax()); cx=int(round(xx.mean())); cy=int(round(yy.mean()))
   for dx,dy in [(-1,0),(0,0),(1,0),(0,1),(1,1)]:
    if cell[cy+dy,cx+dx,3]: cell[cy+dy,cx+dx,:3]=[255,58,42]
   meta['eye_restored'].append(f'{v}_f{col} @({cx},{cy}) local cell')
  before=specks(cell); applied=before>1.2*metrics[v]['specks_1_2px']
  if applied: cell,_=despeckle(cell)
  after=specks(cell); meta['despeckle'][f'{v}{col}']={'before':before,'after':after,'passes':int(applied)}
  # Close only enclosed 1-2-pixel pinholes, using their existing neighbouring palette colour.
  holes=nd.binary_fill_holes(cell[:,:,3]>0)&~(cell[:,:,3]>0); labh,nh=nd.label(holes); fixed=0
  for hi in range(1,nh+1):
   hm=labh==hi
   if hm.sum()<=2:
    ring=nd.binary_dilation(hm)&(cell[:,:,3]>0); cs,ct=np.unique(cell[ring,:3],axis=0,return_counts=True)
    cell[hm,:3]=cs[ct.argmax()];cell[hm,3]=255;fixed+=int(hm.sum())
  meta['closed_pinholes'][f'{v}{col}']=fixed
  cell,plum,pale,rim=clean(cell); m=cell[:,:,3]>0; ink=np.all(cell[:,:,:3]==[20,18,24],axis=2)&m
  goal=round(metrics[v]['ink_share']*m.sum()); current=int(ink.sum())
  # Keep two-pixel-wide dark shadow junctions on the charcoal shadow ramp when ink exceeds the allowed band.
  cap=int(np.floor(metrics[v]['ink_share']*1.15*m.sum()))
  if current>cap:
   broadish=ink&(nd.distance_transform_edt(dark[y0:y1,x0:x1])>1.0)
   by,bx=np.where(broadish); order=np.argsort(-lum[y0:y1,x0:x1][by,bx]); remove=order[:current-cap]
   cell[by[remove],bx[remove],:3]=[33,30,39]; ink=np.all(cell[:,:,:3]==[20,18,24],axis=2)&m; current=int(ink.sum())
  cand=thin[y0:y1,x0:x1]&nd.binary_erosion(m)&~ink&~np.all(cell[:,:,:3]==[255,58,42],axis=2)
  yy,xx=np.where(cand); order=np.argsort(lum[y0:y1,x0:x1][yy,xx]); take=order[:max(0,goal-current)]; cell[yy[take],xx[take],:3]=[20,18,24]
  meta['ink'][f'{v}{col}']={'eligible':int(cand.sum()),'added':len(take),'share':float((np.all(cell[:,:,:3]==[20,18,24],axis=2)&m).sum()/m.sum())}; out[y0:y1,x0:x1]=cell
  if col==0:
   yy,xx=np.where(m); meta['rows'][v]={'width':int(np.ptp(xx)+1),'height':int(np.ptp(yy)+1),'still_wh':[{'e':103,'se':85,'ne':83}[v],{'e':75,'se':83,'ne':103}[v]],'head_length_scaled':heads[v]['raw_length']*factor,'head_error':factor/heads[v]['factor']-1}
 Image.fromarray(out).save(P/'sheet_finished.png'); (P/'preparation.json').write_text(json.dumps(meta,indent=2)); note('Step 2 complete: one nearest shrink; fixed palette, seam mapping, eyes, conditional despeckle. preparation.json has measurements.'); print(json.dumps(meta,indent=2))
