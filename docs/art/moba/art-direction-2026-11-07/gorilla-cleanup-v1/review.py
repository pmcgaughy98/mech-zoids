from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
p=Path(__file__).parent
variants=['source-4k','selected-100k-2k','connected-100k-2k']
rows=[]
for variant in variants:
 for shot in ['y0-d0','y45-d0','y135-d0','y180-d0','y135-d8']:
  a=np.asarray(Image.open(p/f'source-4k-{shot}-mask.png').convert('L'))>127
  b=np.asarray(Image.open(p/f'{variant}-{shot}-mask.png').convert('L'))>127
  common=a&b
  rgb=np.asarray(Image.open(p/f'{variant}-{shot}.png').convert('RGB'),dtype=np.float32)
  ref=np.asarray(Image.open(p/f'source-4k-{shot}.png').convert('RGB'),dtype=np.float32)
  rows.append({'variant':variant,'shot':shot,'silhouette_iou':float(common.sum()/(a|b).sum()),'mean_absolute_rgb_difference_inside_common_silhouette_255':float(np.abs(rgb-ref)[common].mean())})
report={'per_shot':rows,'summary':[{'variant':v,'min_silhouette_iou':min(r['silhouette_iou'] for r in rows if r['variant']==v),'mean_silhouette_iou':float(np.mean([r['silhouette_iou'] for r in rows if r['variant']==v]))} for v in variants]}
(p/'screen-space-report.json').write_text(json.dumps(report,indent=2))
board=Image.new('RGB',(1536,810),'#171c22');d=ImageDraw.Draw(board)
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
d.text((16,12),'GORILLA CLEANUP | same 100k / 2K target | fixed geometry seams, preserved finish',font=f,fill='white')
for i,(v,label) in enumerate(zip(variants,['Source reference: 499k / 4K','Selected reduction: 100k / 2K','Connected cleanup: 100k / 2K'])):
 x=i*512
 d.text((x+12,50),label,font=sm,fill='white')
 im=Image.open(p/f'{v}-y45-d0.png');board.paste(im.crop((384,200,896,560)),(x,82))
 im=Image.open(p/f'{v}-y180-d0.png');board.paste(im.crop((384,240,896,540)),(x,480))
d.text((16,451),'Native-resolution crops, same pose/camera/material/light. Changes are mainly structural.',font=sm,fill='#d5dce5')
d.text((16,785),'Closed surface verified after export/re-import. Still one fused shell: no rig or joint separation yet.',font=sm,fill='#d5dce5')
board.save(p/'cleanup-comparison.png')
print(json.dumps(report['summary'],indent=2))
print('Near three-quarter shading difference:',[(r['variant'],round(r['mean_absolute_rgb_difference_inside_common_silhouette_255'],3)) for r in rows if r['shot']=='y45-d0'])
