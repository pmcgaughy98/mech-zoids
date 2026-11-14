import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,shutil,importlib.util
import numpy as np
from scipy import ndimage as ndi
from PIL import Image,ImageDraw,GifImagePlugin
R=Path(__file__).resolve().parent
PAL=np.array([tuple(bytes.fromhex(s)) for s in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()],np.uint8)
V=['front','side','back'];REF={v:R.parent.parent/'fixed'/f'{n}.png' for v,n in zip(V,['s','e','n'])}
TIMES={'hamstring':[120,120,80,100,160,200],'howl':[160,160,200,500,250,220],'death':[300,100,130,140,160,180,1400]}
spec=importlib.util.spec_from_file_location('sel',str(R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py'));sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel);sel.OUTLINE=PAL[0]
def clean(im):
 a=np.array(im).copy();m=a[:,:,3]>127
 idx=((a[:,:,:3].astype(int)[:,:,None,:]-PAL.astype(int)[None,None,:,:])**2).sum(3).argmin(2);a[:,:,:3]=PAL[idx]
 lab,k=ndi.label(m,np.ones((3,3)));sz=np.bincount(lab.ravel());sz[0]=0
 if k:m=lab==sz.argmax()
 holes=ndi.binary_fill_holes(m)&~m;a[holes,:3]=PAL[0];m|=holes
 a[:,:,3]=m*255;a[~m]=0
 return Image.fromarray(a)
def extract(name):
 out=R/name;raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);H,W=a.shape[:2];N=len(TIMES[name]);(out/'frames').mkdir(exist_ok=True);(out/'slices').mkdir(exist_ok=True)
 m=(a[:,:,3]>127)&~((a[:,:,0]>150)&(a[:,:,2]>150)&(a[:,:,1]<150))
 m &= ~((a[:,:,:3].min(2)>235)&(np.ptp(a[:,:,:3],axis=2)<15))
 lab,k=ndi.label(m);sz=np.bincount(lab.ravel());m &= sz[lab]>15
 bands=[s[0] for s in ndi.find_objects(ndi.label(m.any(1))[0]) if s[0].stop-s[0].start>H*.09]
 if len(bands)!=3:raise ValueError(('bands',name,bands))
 ys=[0]+[(bands[j].stop+bands[j+1].start)//2 for j in range(2)]+[H];xs=np.rint(np.linspace(0,W,N+1)).astype(int)
 for j in range(1,N):
  choices=[x for x in range(max(2,xs[j]-W//(N*4)),min(W-2,xs[j]+W//(N*4))) if not m[:,x-1:x+2].any()]
  if choices:xs[j]=min(choices,key=lambda x:abs(x-xs[j]))
 cells=[];scales={}
 for r,v in enumerate(V):
  rb=Image.open(REF[v]).getbbox();cm=m[ys[r]:ys[r+1],xs[0]:xs[1]];yy,xx=np.where(cm)
  # Separate X/Y calibration of the entire drawing once per view; no native parts pasted.
  sx=(rb[2]-rb[0])/(xx.max()-xx.min()+1);sy=(rb[3]-rb[1])/(yy.max()-yy.min()+1);scales[v]=[sx,sy]
  for c in range(N):
   box=[int(xs[c]),int(ys[r]),int(xs[c+1]),int(ys[r+1])];ca=a[box[1]:box[3],box[0]:box[2]].copy();cm=m[box[1]:box[3],box[0]:box[2]];ca[:,:,3]=cm*255;ca[~cm]=0;im=Image.fromarray(ca);bb=im.getbbox();sprite=im.crop(bb);sprite.save(out/'slices'/f'{v}_f{c}.png')
   scaled=sprite.resize((round(sprite.width*sx),round(sprite.height*sy)),Image.Resampling.NEAREST)
   x=round((rb[0]+rb[2]-1-scaled.width+1)/2);y=161-scaled.height
   frame=Image.new('RGBA',(192,192));frame.paste(scaled,(x,y));clean(frame).save(out/'frames'/f'{v}_f{c}.png')
   exact=c==0 or (name!='death' and c==N-1)
   if exact:shutil.copyfile(REF[v],out/'frames'/f'{v}_f{c}.png')
   cells.append(dict(view=v,frame=c,source_box=box,source_opaque_box=list(bb),scale=[sx,sy],placement=[x,y],duration_ms=TIMES[name][c],touches_cut=bb[0]==0 or bb[1]==0 or bb[2]==im.width or bb[3]==im.height,exact_still=exact))
 grid=dict(raw_size=[W,H],raw_sha256=hashlib.sha256((out/'sheet_raw.png').read_bytes()).hexdigest(),rows=V,columns=N,x_edges=xs.tolist(),y_edges=ys,row_scale=scales,cells=cells)
 (out/'grid.json').write_text(json.dumps(grid,indent=2))
 print(name,raw.size,scales)
def finalize(name):
 out=R/name;N=len(TIMES[name]);checks=[];cw=640;ch=480
 board=Image.new('RGB',((N+1)*cw,3*ch),'#596159');d=ImageDraw.Draw(board)
 for r,v in enumerate(V):
  pics=[];ref=np.array(Image.open(REF[v]).convert('RGBA'));rm=ref[:,:,3]>0
  for i in range(-1,N):
   im=Image.open(REF[v] if i<0 else out/'frames'/f'{v}_f{i}.png').convert('RGBA');a=np.array(im);m=a[:,:,3]>0
   disp=Image.fromarray(sel.selout(a)[0]);bg=Image.new('RGBA',(192,192),'#596159');bg.alpha_composite(disp);tile=bg.crop((16,48,176,166)).resize((640,472),Image.Resampling.NEAREST).convert('RGB');board.paste(tile,((i+1)*cw,r*ch+8));d.text(((i+1)*cw+4,r*ch+8),v+' '+('STILL' if i<0 else f'f{i} {TIMES[name][i]}ms'),fill='white')
   if i<0:continue
   pics.append(tile.quantize(colors=32,method=Image.Quantize.MAXCOVERAGE));yy,xx=np.where(m);_,k=ndi.label(m,np.ones((3,3)));exact=i==0 or (name!='death' and i==N-1)
   check=dict(frame=f'{v}_f{i}',bottom_row=int(yy.max()),bbox=list(im.getbbox()),colours=len(np.unique(a[m,:3],axis=0)),palette_ok=all(tuple(c) in set(map(tuple,PAL)) for c in np.unique(a[m,:3],axis=0)),binary_alpha=bool(np.isin(a[:,:,3],[0,255]).all()),below160=int(m[161:].sum()),edge=bool(m[[0,-1]].any() or m[:,[0,-1]].any()),components=k,holes=int((ndi.binary_fill_holes(m)&~m).sum()),exact_still=exact)
   if exact:check.update(file_byte_identical=(out/'frames'/f'{v}_f{i}.png').read_bytes()==REF[v].read_bytes(),silhouette_IoU=float((m&rm).sum()/(m|rm).sum()),colour_IoU=float((np.all(a==ref,2)&(m|rm)).sum()/(m|rm).sum()))
   checks.append(check)
  with (out/f'preview_{v}.gif').open('wb') as f:
   header,_=GifImagePlugin.getheader(pics[0],info={'loop':0})
   for block in header:f.write(block)
   for pic,ms in zip(pics,TIMES[name]):
    for block in GifImagePlugin.getdata(pic,duration=ms,disposal=2,include_color_table=True):f.write(block)
   f.write(b';')
  gif=Image.open(out/f'preview_{v}.gif');assert gif.n_frames==N
  durations=[]
  for i in range(N):gif.seek(i);durations.append(gif.info['duration'])
  assert durations==TIMES[name]
  board.crop((0,r*ch,board.width,(r+1)*ch)).save(out/f'review_{v}.png')
 board.save(out/'review.png');board.resize((board.width//2,board.height//2),Image.Resampling.NEAREST).save(out/'overview.png')
 (out/'checks.txt').write_text('Native checks before sel-out. Exact endpoints preserve source holes.\n'+'\n'.join(json.dumps(c) for c in checks)+'\n');return checks
if __name__=='__main__':
 import sys
 for name in sys.argv[2:] or TIMES:
  if sys.argv[1]=='extract':extract(name)
  else:print(name,finalize(name))
