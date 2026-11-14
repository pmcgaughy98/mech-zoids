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
south = a[2*im.height//3:, im.width//3:2*im.width//3]
sy_s, sx_s = np.where(south[:,:,3]>0)
raw_south_width = int(sx_s.max()-sx_s.min()+1)
raw_south_height = int(sy_s.max()-sy_s.min()+1)
# Choose integer sheet dimensions by predicting Pillow NEAREST sample centres.
# Perform only one resize, shared by both views.
ideal = im.width * 69 / raw_south_width
for target in sorted(range(round(ideal)-8,round(ideal)+9),key=lambda n:abs(n-ideal)):
    ix = np.minimum(((np.arange(target)+.5)*im.width/target).astype(int),im.width-1)
    iy = np.minimum(((np.arange(target)+.5)*im.height/target).astype(int),im.height-1)
    sampled = a[iy[:,None],ix[None,:],3] > 0
    cell = sampled[2*target//3:, target//3:2*target//3]
    yy,xx = np.where(cell)
    if xx.max()-xx.min()+1 == 69: break
else: raise ValueError('Cannot meet exact 69px width with a whole-sheet shrink')
scale = target/im.width
# Light raw-resolution smoothing of colour only before the single nearest shrink.
filtered=np.array(Image.fromarray(a[:,:,:3]).filter(ImageFilter.MedianFilter(3)))
interior=ndimage.binary_erosion(a[:,:,3]>0,iterations=2)
a[interior,:3]=filtered[interior]
small=Image.fromarray(a).resize((target,round(im.height*scale)),Image.Resampling.NEAREST)
b=np.array(small); vis=b[:,:,3]>127
# Approved chameleon palette: distinct material ramps and reserved lens colours.
colours = ['9ad0ff','3a8cff','2258c8','14306e','5fd8ff','d0f4ff','f6fdff','e2e4ea','b8bcc6','8a8f9c','5c6170','3d3a44','211e27','141218']
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
# Material masks keep the shared palette's ramps separate. Cyan glow and
# blue plates are distinguished by hue; pale glow follows only nearby cyan.
rgb_src=np.array(small)[:,:,:3].astype(int)
r,g,bl=rgb_src.transpose(2,0,1)
cyan=vis & (g>r+35) & (bl>r+35) & ((g-r) > .72*(bl-r))
lens=cyan | (ndimage.binary_dilation(cyan,iterations=1) & vis & (rgb_src.min(axis=2)>175) & (bl-r>5))
team=vis & ~lens & (bl-r>35) & (bl-g>25)
for k in range(len(triples)):
    allowed=lens if 4<=k<=6 else team if k<4 else ~(lens|team)
    cost[:,:,k]=np.where(allowed,cost[:,:,k],1e12)
nearest=cost.argmin(axis=2)
rgb = Image.fromarray(np.array(triples, dtype=np.uint8)[nearest])
out=np.array(rgb.convert('RGBA')); out[:,:,3]=np.where(vis,255,0); out[~vis]=0
Image.fromarray(out).save(ROOT/'sheet_finished.png')
(ROOT/'preparation.json').write_text(json.dumps({'raw_south_width':raw_south_width,'raw_south_height':raw_south_height,'target_south_width':69,'pre_palette_smoothing':'3x3 median on raw RGB interior only','shared_scale':scale,'finished_sheet_size':small.size,'visible_colours':len(np.unique(out[vis,:3],axis=0))},indent=2))
print((ROOT/'preparation.json').read_text())
