from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as ndi
import json,hashlib,importlib.util
R=Path(__file__).resolve().parent
PAL=np.array([tuple(bytes.fromhex(h)) for h in '141218 211e27 2e1a6e 3d3a44 6a3cc8 9d9ba2 a46bff b8923a d6d6dc e0c8ff f0d27a 3fe8b0 c8fff0 fff4d6 f6fffb'.split()],dtype=np.uint8)
COUNTS={'walk':8,'sand_kick':6}
TIMES={'walk':[100]*8,'sand_kick':[260,130,130,90,160,280]}
spec=importlib.util.spec_from_file_location('sel',str(R.parents[3]/'rhino_l/take-a/anim/selout_rhino.py'));sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel)
def approved(v):
 im=Image.new('RGBA',(192,192));im.paste(Image.open(R.parent.parent/'views'/('n.png' if v=='back' else 'ne.png')).convert('RGBA'),(16,20));return im

def clean(a):
 a=np.array(a).copy();m=a[:,:,3]>127
 idx=((a[:,:,:3].astype(int)[:,:,None,:]-PAL.astype(int)[None,None,:,:])**2).sum(3).argmin(2);a[:,:,:3]=PAL[idx]
 lab,k=ndi.label(m,structure=np.ones((3,3)));sizes=np.bincount(lab.ravel());sizes[0]=0
 if k:m=lab==sizes.argmax()
 holes=ndi.binary_fill_holes(m)&~m;a[holes]=[*PAL[0],255];m|=holes
 a[:,:,3]=m*255;a[~m]=0
 return a

def board(name):
 N=COUNTS[name];cw,ch=304,376
 b=Image.new('RGBA',((N+1)*cw,4*ch),(82,89,81,255));d=ImageDraw.Draw(b)
 for row,(v,status) in enumerate([('back','live'),('back','new'),('ne','live'),('ne','new')]):
  d.text((4,row*ch+2),f'{name} {v} {status} | STILL | f0...',fill='white')
  for c in range(-1,N):
   if c==-1:im=approved(v)
   else:
    p=(R.parent/('codex-set-a' if v=='back' else 'codex-set-c')/name/'frames'/f'{v}_f{c}.png') if status=='live' else R/name/'frames'/f'{v}_f{c}.png'
    im=Image.open(p).convert('RGBA')
   out=sel.selout(np.array(im))[0];tile=Image.fromarray(out).crop((60,78,136,166)).resize((304,352),Image.Resampling.NEAREST)
   b.alpha_composite(tile,((c+1)*cw,row*ch+24))
 b.convert('RGB').save(R/name/'board.png')
 # Full-scale crop panels retained, no resampling below 4x.
 for v,j in [('back',0),('ne',2)]:b.crop((0,j*ch,b.width,(j+2)*ch)).convert('RGB').save(R/name/f'board_{v}.png')

def extract(name):
 N=COUNTS[name];out=R/name;(out/'frames').mkdir(exist_ok=True);(out/'slices').mkdir(exist_ok=True)
 raw=Image.open(out/'sheet_raw.png').convert('RGBA');a=np.array(raw);H,W=a.shape[:2]
 m=(a[:,:,3]>127)&~((a[:,:,0]>170)&(a[:,:,2]>170)&(a[:,:,1]<130))
 lab,k=ndi.label(m);sizes=np.bincount(lab.ravel());m&=sizes[lab]>20
 bands=[s[0] for s in ndi.find_objects(ndi.label(m.any(1))[0]) if s[0].stop-s[0].start>H*.1];assert len(bands)==2,bands
 ys=[0,(bands[0].stop+bands[1].start)//2,H];xs=np.rint(np.linspace(0,W,N+1)).astype(int)
 for i in range(1,N):
  choices=[x for x in range(max(2,xs[i]-W//(N*4)),min(W-2,xs[i]+W//(N*4))) if not m[:,x-1:x+2].any()]
  if choices:xs[i]=min(choices,key=lambda x:abs(x-xs[i]))
 cells=[]
 factors={'back':.285,'ne':.285} if name=='walk' else {'back':.285,'ne':.285}
 for r,v in enumerate(['back','ne']):
  factor=factors[v];ref=approved(v).getbbox()
  for c in range(N):
   box=[int(xs[c]),int(ys[r]),int(xs[c+1]),int(ys[r+1])];ca=a[box[1]:box[3],box[0]:box[2]].copy();cm=m[box[1]:box[3],box[0]:box[2]];ca[:,:,3]=cm*255;ca[~cm]=0
   im=Image.fromarray(ca);bb=im.getbbox();im=im.crop(bb);im.save(out/'slices'/f'{v}_f{c}.png')
   scaled=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.NEAREST)
   # Ear midpoint is stable across these rear projections; bottom set provisionally at ground.
   x=round((ref[0]+ref[2]-1)/2-(scaled.width-1)/2);y=161-scaled.height
   fr=Image.new('RGBA',(192,192));fr.paste(scaled,(x,y));fr=Image.fromarray(clean(fr));fr.save(out/'frames'/f'{v}_f{c}.png')
   if name=='sand_kick' and c in (0,N-1):approved(v).save(out/'frames'/f'{v}_f{c}.png')
   cells.append(dict(view=v,frame=c,source_box=box,source_opaque_box=list(bb),scale=factor,placement=[x,y],duration_ms=TIMES[name][c],touches_cut=bb[0]==0 or bb[1]==0 or bb[2]==box[2]-box[0] or bb[3]==box[3]-box[1]))
 (out/'grid.json').write_text(json.dumps(dict(raw_size=[W,H],raw_sha256=hashlib.sha256((out/'sheet_raw.png').read_bytes()).hexdigest(),columns=N,rows=['back','ne'],x_edges=xs.tolist(),y_edges=ys,row_scale=factors,cells=cells,approved_offset=[16,20],ground_row=160),indent=2))
 board(name)
 print(name,raw.size,[(v,Image.open(out/'frames'/f'{v}_f0.png').getbbox()) for v in ['back','ne']])
if __name__=='__main__':
 import sys
 for n in sys.argv[1:]:extract(n)
