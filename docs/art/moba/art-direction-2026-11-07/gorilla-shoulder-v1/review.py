from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
p=Path(__file__).parent
metrics=[]
for shot in ['y0-d0','y-45-d0','y-90-d0','y180-d0','y-45-d8']:
 a=np.asarray(Image.open(p/f'reference-{shot}-mask.png').convert('L'))>127
 b=np.asarray(Image.open(p/f'rest-{shot}-mask.png').convert('L'))>127
 common=a&b
 rgb=np.asarray(Image.open(p/f'rest-{shot}.png').convert('RGB'),dtype=np.float32)
 ref=np.asarray(Image.open(p/f'reference-{shot}.png').convert('RGB'),dtype=np.float32)
 metrics.append({'shot':shot,'rest_silhouette_iou':float(common.sum()/(a|b).sum()),'rest_mean_absolute_rgb_difference_255':float(np.abs(rgb-ref)[common].mean())})
(p/'rest-comparison-report.json').write_text(json.dumps(metrics,indent=2))
im=Image.new('RGB',(1536,820),'#171c22');d=ImageDraw.Draw(im)
f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);sm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
d.text((16,12),'GORILLA SHOULDER TEST | original rest, separated rest, 12-degree rigid movement',font=f,fill='white')
for col,(v,title) in enumerate([('reference','Connected reference'),('rest','Separated and capped, at rest'),('reach','12-degree shoulder reach')]):
 x=col*512
 d.text((x+12,50),title,font=sm,fill='white')
 src=Image.open(p/f'{v}-y-45-d0.png');im.paste(src.crop((384,200,896,560)),(x,82))
 side=Image.open(p/f'{v}-y-90-d0.png');im.paste(side.crop((384,230,896,550)),(x,480))
d.text((16,451),'Same camera/material/light. One arm transforms rigidly; body and opposite arm remain static.',font=sm,fill='#d5dce5')
d.text((16,802),'Geometry probe only. No skeleton, weights, production clip, collision-free range or full rig claim.',font=sm,fill='#d5dce5')
im.save(p/'shoulder-comparison.png')
print(json.dumps(metrics,indent=2))
