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
scale = 66/raw_east_height
small=Image.fromarray(a).resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
b=np.array(small); vis=b[:,:,3]>127
# Prompt's shared thirteen-colour palette, preserving four gunmetal and four red shades.
colours = ['bcbcc8','6e6e7e','444452','22222b','ff6a55','e8251f','a8141a','5c0a10','f0ece4','c9c2b8','6ff0dc','e8fffb','141418']
triples = [tuple(bytes.fromhex(c)) for c in colours]
pal = Image.new('P',(1,1))
pal.putpalette([v for c in triples for v in c] + list(triples[-1]) * (256-len(triples)))
# Match the complete sheet to one palette in Lab; preserve neutral gunmetal
# and saturated red as separate four-tone material ramps.
source_lab = np.array(small.convert('RGB').convert('LAB')).astype(float)
palette_rgb = Image.fromarray(np.array([triples], dtype=np.uint8))
choices_lab = np.array(palette_rgb.convert('LAB')).astype(float)[0]
source_lab[...,1:] = (source_lab[...,1:] + 128) % 256 - 128
choices_lab[...,1:] = (choices_lab[...,1:] + 128) % 256 - 128
distance = (source_lab[:,:,None,:] - choices_lab[None,None,:,:]) ** 2
nearest = (distance * [1, 3, 3]).sum(axis=3).argmin(axis=2)
rgb = Image.fromarray(np.array(triples, dtype=np.uint8)[nearest])
out=np.array(rgb.convert('RGBA')); out[:,:,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
(ROOT/'preparation.json').write_text(json.dumps({'raw_heights':heights,'raw_extents':extents,'raw_east_area':raw_east_area,'raw_east_height':raw_east_height,'target_east_height':66,'shared_scale':scale,'finished_sheet_size':small.size,'visible_colours':len(np.unique(out[vis,:3],axis=0))},indent=2))
print((ROOT/'preparation.json').read_text())


