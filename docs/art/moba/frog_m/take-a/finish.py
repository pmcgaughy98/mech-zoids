"""Non-drawing sheet preparation: key, one shared shrink, one shared palette."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
im = Image.open(ROOT / 'sheet_raw.png').convert('RGBA')
a = np.array(im)
bg = (a[:,:,0] > 190) & (a[:,:,1] < 85) & (a[:,:,2] > 185)
a[bg] = (0,0,0,0)
heights=[]
extents=[]
for row,col in [(0,0),(0,1),(0,2),(1,0),(1,2),(2,0),(2,1),(2,2)]:
    cell=a[row*im.height//3:(row+1)*im.height//3,col*im.width//3:(col+1)*im.width//3]
    yy,xx=np.where(cell[:,:,3]>0)
    heights.append(int(yy.max()-yy.min()+1))
    extents.append(int(max(yy.max()-yy.min()+1,xx.max()-xx.min()+1)))
east = a[im.height//3:2*im.height//3, :im.width//3]  # East sets the single shared scale.
raw_east_area = int((east[:,:,3] > 0).sum())
sy, sx = np.where(east[:,:,3] > 0)
raw_east_height = int(sy.max()-sy.min()+1)
south = a[2*im.height//3:, im.width//3:2*im.width//3]
sy_s, sx_s = np.where(south[:,:,3] > 0)
raw_south_height = int(sy_s.max()-sy_s.min()+1)
raw_east_width = int(sx.max()-sx.min()+1)
scale = 60/raw_south_height
small=Image.fromarray(a).resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
b=np.array(small); vis=b[:,:,3]>127
# Approved chameleon palette: distinct material ramps and reserved lens colours.
colours = ['eaff8a','a8e81e','5f9a0e','2c4a08','d6d6dc','9d9ba2','58555e','3d3a44','211e27','4a1fa8','9a6bff','f2ecff','141218']
triples = [tuple(bytes.fromhex(c)) for c in colours]
pal = Image.new('P',(1,1))
pal.putpalette([v for c in triples for v in c] + list(triples[-1]) * (256-len(triples)))
# Match the complete sheet to one palette in Lab; preserve the prompt material ramps.
source_lab = np.array(small.convert('RGB').convert('LAB')).astype(float)
palette_rgb = Image.fromarray(np.array([triples], dtype=np.uint8))
choices_lab = np.array(palette_rgb.convert('LAB')).astype(float)[0]
source_lab[...,1:] = (source_lab[...,1:] + 128) % 256 - 128
choices_lab[...,1:] = (choices_lab[...,1:] + 128) % 256 - 128
distance = (source_lab[:,:,None,:] - choices_lab[None,None,:,:]) ** 2
cost = (distance * [1, 3, 3]).sum(axis=3)
# Reserve violet lenses by source hue and bounded glint positions on this raw sheet.
rgb_src=np.array(small)[:,:,:3].astype(int)
r,g,b=rgb_src[...,0],rgb_src[...,1],rgb_src[...,2]
lens=(b>r+20)&(b>g+25)&vis
u,v=np.meshgrid(np.arange(small.width)/small.width,np.arange(small.height)/small.height)
zone=np.zeros(vis.shape,bool)
for x0,y0,x1,y1 in [(251,492,308,550),(945,492,1003,550),(215,911,268,963),(547,912,607,965),(649,912,706,965),(985,911,1040,965)]:
    zone|=(u>=x0/1254)&(u<=x1/1254)&(v>=y0/1254)&(v<=y1/1254)
lens |= zone & (r>220)&(g>200)&(b>220)&vis
cost[:,:,9:12]=np.where(lens[:,:,None],cost[:,:,9:12],1e12)
for k in list(range(9))+[12]: cost[:,:,k]=np.where(lens,1e12,cost[:,:,k])
nearest=cost.argmin(axis=2)
rgb = Image.fromarray(np.array(triples, dtype=np.uint8)[nearest])
out=np.array(rgb.convert('RGBA')); out[:,:,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
(ROOT/'preparation.json').write_text(json.dumps({'raw_heights':heights,'raw_extents':extents,'raw_east_area':raw_east_area,'raw_east_height':raw_east_height,'raw_south_height':raw_south_height,'raw_east_width':raw_east_width,'target_south_height':60,'shared_scale':scale,'finished_sheet_size':small.size,'visible_colours':len(np.unique(out[vis,:3],axis=0))},indent=2))
print((ROOT/'preparation.json').read_text())


