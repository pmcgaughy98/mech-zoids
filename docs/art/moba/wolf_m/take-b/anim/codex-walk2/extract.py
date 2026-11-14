from pathlib import Path
import numpy as np,json
from PIL import Image,ImageDraw
from scipy import ndimage as ndi
R=Path(r'D:/dev/new-mech-rpg/docs/art/moba/wolf_m/take-b/anim/codex-walk2');raw=np.array(Image.open(R/'sheet_raw.png').convert('RGBA'));m=raw[:,:,3]>127
lab,n=ndi.label(m,np.ones((3,3)));sizes=np.bincount(lab.ravel());sizes[0]=0;m=sizes[lab]>500
pal=np.array([tuple(bytes.fromhex(x)) for x in '141418 22222b 5c0a10 a8141a 444452 e8251f 6e6e7e ff6a55 6ff0dc bcbcc8 c9c2b8 f0ece4'.split()],np.uint8)
(R/'walk/underpaint').mkdir(parents=True,exist_ok=True);(R/'walk/frames').mkdir(exist_ok=True)
xs=[0,284,550,818,1086,1354,1626,1894,2172];cells=[]
for i in range(8):
 a=raw[:,xs[i]:xs[i+1]].copy();mm=m[:,xs[i]:xs[i+1]];a[~mm]=0;a[:,:,3]=mm*255
 im=Image.fromarray(a);bb=im.getbbox();crop=im.crop(bb);crop=crop.resize((round(crop.width*.447),round(crop.height*.447)),Image.Resampling.NEAREST)
 # muzzle stays x150; sole baseline initially160.
 pos=(151-crop.width,161-crop.height);can=Image.new('RGBA',(192,192));can.paste(crop,pos);b=np.array(can);mask=b[:,:,3]>0;idx=((b[:,:,:3].astype(int)[:,:,None]-pal.astype(int))**2).sum(3).argmin(2);b[:,:,:3]=pal[idx];b[~mask]=0
 Image.fromarray(b).save(R/'walk/underpaint'/f'side_f{i}.png');cells.append(dict(frame=i,source_box=[xs[i],0,xs[i+1],724],source_opaque_box=list(bb),scale=.447,placement=pos))
board=Image.new('RGBA',(8*512,360),(80,88,84,255))
for i in range(8):board.alpha_composite(Image.open(R/'walk/underpaint'/f'side_f{i}.png').crop((32,88,160,178)).resize((512,360),Image.Resampling.NEAREST),(i*512,0))
board.convert('RGB').save(R/'underpaint_board.png')
json.dump(dict(columns=8,rows=1,raw_size=[2172,724],cells=cells,canvas=[192,192],frame_ms=100,loop=True),open(R/'grid.json','w'),indent=2)
