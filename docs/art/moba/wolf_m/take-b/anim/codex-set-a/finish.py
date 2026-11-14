"""Slice whole generated cells. No reference parts are pasted into posed drawings."""
from pathlib import Path
import json,hashlib,shutil,importlib.util
from PIL import Image,ImageDraw,GifImagePlugin
import numpy as np
from scipy import ndimage as ndi
R=Path(__file__).resolve().parent
VIEWS=['front','side','back']; REF={'front':'s','side':'e','back':'n'}
TIMES={'walk':[100]*8,'sprint':[70]*6,'lunge':[120,180,80,120,90,160,200],'bite':[100,120,80,140,160]}
PAL=np.array([tuple(bytes.fromhex(c)) for c in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()],np.uint8)
spec=importlib.util.spec_from_file_location('sel',str(R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py'));sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel);sel.OUTLINE=PAL[0]
def refpath(v):return R.parent.parent/'fixed'/f'{REF[v]}.png'
def approved(v):return Image.open(refpath(v)).convert('RGBA')
def exact(n,i):return n in ['lunge','bite'] and i in [0,len(TIMES[n])-1]
def bottom(n,i):return 152 if n=='sprint' and i==2 else 140 if n=='lunge' and i==3 else 160

def clean(im):
 a=np.array(im).copy();m=a[:,:,3]>127
 lab,k=ndi.label(m,np.ones((3,3)));sz=np.bincount(lab.ravel());sz[0]=0
 if k:m=lab==sz.argmax()
 idx=((a[:,:,:3].astype(int)[:,:,None,:]-PAL.astype(int))**2).sum(3).argmin(2);a[:,:,:3]=PAL[idx]
 holes=ndi.binary_fill_holes(m)&~m
 # Fill transparent pinholes with nearest adjacent material, retaining dark part divisions.
 if holes.any():
  inds=ndi.distance_transform_edt(~m,return_distances=False,return_indices=True);a[holes,:3]=a[inds[0][holes],inds[1][holes],:3]
 m|=holes;a[:,:,3]=m*255;a[~m]=0
 return Image.fromarray(a)
def source_mask(a):
 rgb=a[:,:,:3].astype(int);m=(a[:,:,3]>127)&~((rgb[:,:,0]>150)&(rgb[:,:,2]>130)&(rgb[:,:,1]<145)&((rgb[:,:,0]+rgb[:,:,2]-2*rgb[:,:,1])>140))
 lab,k=ndi.label(m,np.ones((3,3)));sz=np.bincount(lab.ravel());sz[0]=0;m &= sz[lab]>30
 return m

def extract(n):
 out=R/n;N=len(TIMES[n]);raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);m=source_mask(a);W,H=raw.size
 bands=[s[0] for s in ndi.find_objects(ndi.label(m.any(1))[0]) if s[0].stop-s[0].start>H*.08]
 assert len(bands)==3,(n,bands)
 ys=[0]+[(bands[i].stop+bands[i+1].start)//2 for i in range(2)]+[H];xs=np.rint(np.linspace(0,W,N+1)).astype(int)
 for i in range(1,N):
  cand=[x for x in range(max(2,xs[i]-W//(N*4)),min(W-2,xs[i]+W//(N*4))) if not m[:,x-1:x+2].any()]
  if cand:xs[i]=min(cand,key=lambda x:abs(x-xs[i]))
 (out/'frames').mkdir(exist_ok=True);(out/'slices').mkdir(exist_ok=True);(out/'underpaint').mkdir(exist_ok=True)
 cells=[];factors={}
 for r,v in enumerate(VIEWS):
  samples=[]
  for i in range(N):
   mm=m[ys[r]:ys[r+1],xs[i]:xs[i+1]];yy,xx=np.where(mm);samples.append([xx.max()-xx.min()+1,yy.max()-yy.min()+1])
  target=approved(v).getbbox();tw=target[2]-target[0];th=target[3]-target[1]
  # A single fixed row scale. The neutral/gathered cell supplies the shared native calibration.
  scale=(tw/samples[0][0]*th/samples[0][1])**.5;factors[v]=scale
  for i in range(N):
   box=[int(xs[i]),ys[r],int(xs[i+1]),ys[r+1]];ca=a[box[1]:box[3],box[0]:box[2]].copy();cm=m[box[1]:box[3],box[0]:box[2]];ca[:,:,3]=cm*255;ca[~cm]=0
   cell=Image.fromarray(ca);bb=cell.getbbox();sprite=cell.crop(bb);sprite.save(out/'slices'/f'{v}_f{i}.png')
   sprite=sprite.resize((round(sprite.width*scale),round(sprite.height*scale)),Image.Resampling.NEAREST)
   x=round((target[0]+target[2]-1)/2-(sprite.width-1)/2);y=bottom(n,i)+1-sprite.height
   fr=Image.new('RGBA',(192,192));fr.paste(sprite,(x,y));fr=clean(fr);fr.save(out/'underpaint'/f'{v}_f{i}.png');fr.save(out/'frames'/f'{v}_f{i}.png')
   if exact(n,i):shutil.copyfile(refpath(v),out/'frames'/f'{v}_f{i}.png')
   cells.append(dict(view=v,frame=i,source_box=box,source_opaque_box=list(bb),scale=scale,placement=[x,y],duration_ms=TIMES[n][i],touches_cut=bool(bb[0]==0 or bb[1]==0 or bb[2]==cell.width or bb[3]==cell.height)))
 grid=dict(raw_size=[W,H],raw_sha256=hashlib.sha256((out/'sheet_raw.png').read_bytes()).hexdigest(),columns=N,rows=VIEWS,x_edges=xs.tolist(),y_edges=ys,row_scale=factors,cells=cells,final_canvas=[192,192],duration_ms=TIMES[n],loop=n in ['walk','sprint'])
 (out/'grid.json').write_text(json.dumps(grid,indent=2)+'\n');print(n,raw.size,factors)

def finalize(n):
 N=len(TIMES[n]);out=R/n;grid=json.loads((out/'grid.json').read_text());checks=[]
 cw,ch=512,432;board=Image.new('RGBA',((N+1)*cw,3*ch),(84,92,88,255));d=ImageDraw.Draw(board)
 for row,v in enumerate(VIEWS):
  pics=[]
  for i in range(-1,N):
   im=approved(v) if i<0 else Image.open(out/'frames'/f'{v}_f{i}.png').convert('RGBA');a=np.array(im);b=sel.selout(a)[0]
   tile=Image.fromarray(b).crop((32,65,160,168)).resize((512,412),Image.Resampling.NEAREST)
   board.alpha_composite(tile,((i+1)*cw,row*ch+20));d.text(((i+1)*cw+6,row*ch+4),f'{n} {v} '+('APPROVED' if i<0 else f'f{i} {TIMES[n][i]}ms'),fill='white')
   if i<0:continue
   bg=Image.new('RGBA',(192,192),(84,92,88,255));bg.alpha_composite(Image.fromarray(b));pic=bg.crop((32,65,160,168)).resize((512,412),Image.Resampling.NEAREST).convert('RGB').quantize(colors=32,method=Image.Quantize.MAXCOVERAGE);pics.append(pic)
   m=a[:,:,3]>0;yy,xx=np.where(m);r=np.array(approved(v));rm=r[:,:,3]>0;u=m|rm;colors=np.unique(a[m,:3],axis=0);holes=int((ndi.binary_fill_holes(m)&~m).sum());components=ndi.label(m,np.ones((3,3)))[1]
   c=dict(frame=f'{v}_f{i}',duration_ms=TIMES[n][i],size=list(im.size),bounds=list(im.getbbox()),bottom_row=int(yy.max()),colour_count=len(colors),palette_ok=all(tuple(x) in set(map(tuple,PAL)) for x in colors),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),pixels_below_160=int(m[161:].sum()),canvas_edge=bool(m[[0,-1]].any() or m[:,[0,-1]].any()),components=components,enclosed_holes=holes,required_exact_still=exact(n,i))
   if exact(n,i):c.update(rgba_equal=bool(np.array_equal(a,r)),png_bytes_identical=(out/'frames'/f'{v}_f{i}.png').read_bytes()==refpath(v).read_bytes(),silhouette_IoU=float((m&rm).sum()/u.sum()),colour_IoU=float((np.all(a==r,2)&u).sum()/u.sum()))
   c['structural_pass']=c['size']==[192,192] and c['palette_ok'] and c['binary_alpha'] and not c['pixels_below_160'] and not c['canvas_edge'] and components==1 and (holes==0 or exact(n,i)) and c['bottom_row']==bottom(n,i)
   checks.append(c);cell=next(c for c in grid['cells'] if c['view']==v and c['frame']==i);cell['final_opaque_box']=list(im.getbbox());cell['final_path']=f'frames/{v}_f{i}.png';cell['exact_endpoint']=exact(n,i)
  with (out/f'preview_{v}.gif').open('wb') as fp:
   header,_=GifImagePlugin.getheader(pics[0],info={'loop':0} if grid['loop'] else {})
   for block in header:fp.write(block)
   for pic,ms in zip(pics,TIMES[n]):
    for block in GifImagePlugin.getdata(pic,duration=ms,disposal=2,include_color_table=True):fp.write(block)
   fp.write(b';')
  g=Image.open(out/f'preview_{v}.gif');dur=[]
  for i in range(g.n_frames):g.seek(i);dur.append(g.info['duration'])
  assert g.n_frames==N and dur==TIMES[n],(n,v,dur)
 board.convert('RGB').save(out/'review.png')
 for row,v in enumerate(VIEWS):board.crop((0,row*ch,board.width,(row+1)*ch)).convert('RGB').save(out/f'review_{v}.png')
 board.resize((min(2048,board.width),round(board.height*min(2048,board.width)/board.width)),Image.Resampling.NEAREST).convert('RGB').save(out/'review_small.png')
 (out/'grid.json').write_text(json.dumps(grid,indent=2)+'\n');(out/'checks.txt').write_text('Before sel-out. Approved exact endpoints retain original enclosed holes.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n')
 print(n,'checks',len(checks),'faults',[c for c in checks if not c['structural_pass']]);return checks
if __name__=='__main__':
 import sys
 mode=sys.argv[1]
 allc={}
 for n in sys.argv[2:] or TIMES:
  if mode=='extract':extract(n)
  allc[n]=finalize(n)
 (R/'verification.json').write_text(json.dumps(allc,indent=2)+'\n')
