"""Non-drawing sheet preparation: key, one shared shrink, one shared palette."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

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
scale = 72/raw_south_height
# Light raw-resolution smoothing of colour only before the single nearest shrink.
filtered=np.array(Image.fromarray(a[:,:,:3]).filter(ImageFilter.MedianFilter(3)))
interior=ndimage.binary_erosion(a[:,:,3]>0,iterations=2)
a[interior,:3]=filtered[interior]
small=Image.fromarray(a).resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
b=np.array(small); vis=b[:,:,3]>127
# Approved chameleon palette: distinct material ramps and reserved lens colours.
colours = ['e0c8ff','a46bff','6a3cc8','2e1a6e','fff4d6','f0d27a','b8923a','d6d6dc','9d9ba2','3d3a44','211e27','3fe8b0','c8fff0','f6fffb','141218']
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
# Reserve mint and its two light shades only for lens pixels, keeping all three apart.
rgb_src=np.array(small)[:,:,:3].astype(int)
green=vis & (rgb_src[:,:,1]>rgb_src[:,:,0]+25) & (rgb_src[:,:,1]>rgb_src[:,:,2]+5)
near_eye=ndimage.binary_dilation(green,iterations=1)
lens=green | (near_eye & vis & (rgb_src.min(axis=2)>180) & (rgb_src[:,:,1]>=rgb_src[:,:,0]))
cost[:,:,11:14]=np.where(lens[:,:,None],cost[:,:,11:14],1e12)
for k in list(range(11))+[14]: cost[:,:,k]=np.where(lens,1e12,cost[:,:,k])
nearest=cost.argmin(axis=2)
rgb = Image.fromarray(np.array(triples, dtype=np.uint8)[nearest])
out=np.array(rgb.convert('RGBA')); out[:,:,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
(ROOT/'preparation.json').write_text(json.dumps({'raw_heights':heights,'raw_extents':extents,'raw_east_area':raw_east_area,'raw_east_height':raw_east_height,'raw_south_height':raw_south_height,'raw_east_width':raw_east_width,'target_south_height':72,'pre_palette_smoothing':'3x3 median on raw RGB interior only','shared_scale':scale,'finished_sheet_size':small.size,'visible_colours':len(np.unique(out[vis,:3],axis=0))},indent=2))
print((ROOT/'preparation.json').read_text())


