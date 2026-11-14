"""Non-drawing sheet preparation: key, one shared shrink, one shared palette."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
C = ROOT.parent / 'take-c'
normal = ROOT / 'sheet_size_matched.png'
im = Image.open(normal if normal.exists() else ROOT / 'sheet_raw.png').convert('RGBA')
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
east = a[im.height//3:2*im.height//3, :im.width//3]  # East measurements; south sets the single shared scale.
raw_east_area = int((east[:,:,3] > 0).sum())
sy, sx = np.where(east[:,:,3] > 0)
raw_east_height = int(sy.max()-sy.min()+1)
south = a[2*im.height//3:, im.width//3:2*im.width//3]
sy_s, sx_s = np.where(south[:,:,3] > 0)
raw_south_height = int(sy_s.max()-sy_s.min()+1)
raw_east_width = int(sx.max()-sx.min()+1)
scale = json.loads((C/'preparation.json').read_text())['shared_scale']  # Exact take C scale, never remeasured.
smooth=np.array(Image.fromarray(a[:,:,:3]).filter(ImageFilter.MedianFilter(9)))
a[:,:,:3]=smooth
small=Image.fromarray(a).resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
b=np.array(small); vis=b[:,:,3]>127
# Approved crimson mech-lobster palette: distinct material ramps and reserved lens colours.
colours = ['7e7e8e','555562','34343e','26262e','f85a4a','ee2c26','c41216','6a0a10','eeeef2','b8b8c2','9a9aa6','5ff0ff','e8ffff','141218']
triples = [tuple(bytes.fromhex(c)) for c in colours]
locked = np.array(Image.open(C/'sheet_finished.png').convert('RGBA'))
exact = set(map(tuple, np.unique(locked[locked[:,:,3]>0,:3],axis=0)))
assert set(triples) == exact, 'C palette differs; stop rather than invent colours'
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
# Protect cyan lenses and pale glints, separating them from neutral steel.
rgb_src=np.array(small)[:,:,:3].astype(int)
lens=(rgb_src[:,:,1]-rgb_src[:,:,0]>30)&(rgb_src[:,:,2]-rgb_src[:,:,0]>30)&(rgb_src[:,:,1]>100)
# Glints are nearly white and enclosed by cyan on this sheet.
from scipy import ndimage
near_lens=ndimage.binary_dilation(lens,iterations=2)
lens |= near_lens & (rgb_src.min(axis=2)>225)
cost[:,:,11:13]=np.where(lens[:,:,None],cost[:,:,11:13],1e12)
for k in list(range(11))+[13]: cost[:,:,k]=np.where(lens,1e12,cost[:,:,k])
nearest=cost.argmin(axis=2)
rgb = Image.fromarray(np.array(triples, dtype=np.uint8)[nearest])
out=np.array(rgb.convert('RGBA')); out[:,:,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_edit_finished.png')
(ROOT/'preparation.json').write_text(json.dumps({'raw_heights':heights,'raw_extents':extents,'raw_east_area':raw_east_area,'raw_east_height':raw_east_height,'raw_south_height':raw_south_height,'raw_east_width':raw_east_width,'target_south_height':66,'shared_scale':scale,'finished_sheet_size':small.size,'visible_colours':len(np.unique(out[vis,:3],axis=0))},indent=2))
print((ROOT/'preparation.json').read_text())


