from pathlib import Path
import json,hashlib,struct
import numpy as np
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).parent
variants=['source-4k','source-2k','100k-4k','40k-4k','100k-2k','40k-2k']
shots=['y0-d0','y45-d0','y135-d0','y180-d0','y135-d8']
metrics=[]
for v in variants:
 for shot in shots:
  ref=np.asarray(Image.open(p/f'source-4k-{shot}-mask.png').convert('L'))>127
  mask=np.asarray(Image.open(p/f'{v}-{shot}-mask.png').convert('L'))>127
  inter=ref&mask;union=ref|mask
  a=np.asarray(Image.open(p/f'source-4k-{shot}.png').convert('RGB'),dtype=np.float32)
  b=np.asarray(Image.open(p/f'{v}-{shot}.png').convert('RGB'),dtype=np.float32)
  delta=np.abs(a-b).mean(axis=2)
  metrics.append({'variant':v,'shot':shot,'silhouette_iou':float(inter.sum()/union.sum()),'source_pixels':int(ref.sum()),'variant_pixels':int(mask.sum()),'mean_abs_rgb_difference_inside_common_silhouette_255':float(delta[inter].mean()),'fraction_common_pixels_with_mean_rgb_difference_above_12':float((delta[inter]>12).mean())})
files={'source-4k':p.parent/'gorilla-polish-v1/gorilla-source.glb','source-2k':p/'gorilla-source-2k.glb','100k-4k':p/'gorilla-100k-4k.glb','40k-4k':p/'gorilla-40k-4k.glb','100k-2k':p/'gorilla-100k-2k.glb','40k-2k':p/'gorilla-40k-2k.glb'}
summaries=[]
texhashes={}
for name,file in files.items():
 with file.open('rb') as f:
  f.read(12);n,t=struct.unpack('<II',f.read(8));d=json.loads(f.read(n));n,t=struct.unpack('<II',f.read(8));b=f.read(n)
 hs=[]
 for im in d['images']:
  bv=d['bufferViews'][im['bufferView']];o=bv.get('byteOffset',0);hs.append(hashlib.sha256(b[o:o+bv['byteLength']]).hexdigest())
 texhashes[name]=hs
 tris=sum(d['accessors'][pr['indices']]['count']//3 for m in d['meshes'] for pr in m['primitives'])
 rows=[r for r in metrics if r['variant']==name]
 summaries.append({'variant':name,'triangles':tris,'file_mb_decimal':file.stat().st_size/1e6,'min_silhouette_iou':min(r['silhouette_iou'] for r in rows),'mean_silhouette_iou':sum(r['silhouette_iou'] for r in rows)/len(rows)})
report={'camera':'1280x720, 60 degree FOV, 6.5 m, 30 degree pitch, 2 m test height; 4 near angles + 8 m farther case','metrics_caveat':'Screen-space masks measure static projection overlap, not topology, deformation or perceived quality. Color differences include normal/shading/UV changes. No frame-time or GPU-memory benchmark.','source_textures_exactly_retained_in_4k_reductions':texhashes['source-4k']==texhashes['100k-4k']==texhashes['40k-4k'],'summaries':summaries,'per_shot':metrics}
(p/'screen-space-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps(summaries,indent=2))
board=Image.new('RGB',(1536,830),'#171c22');dr=ImageDraw.Draw(board)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
dr.text((18,12),'GORILLA OPTIMIZATION | same refined material, camera, pose and arena lighting',font=font,fill='white')
for col,(v,label) in enumerate([('source-4k','Source: 499k / 4K / 50.0 MB'),('100k-2k','Candidate: 100k / 2K / 13.4 MB'),('40k-2k','Lighter test: 40k / 2K / 10.7 MB')]):
 x=col*512
 dr.text((x+12,50),label,font=small,fill='white')
 im=Image.open(p/f'{v}-y45-d0.png');board.paste(im.crop((384,200,896,560)),(x,82))
 back=Image.open(p/f'{v}-y180-d0.png');board.paste(back.crop((384,240,896,540)),(x,480))
dr.text((18,451),'Native-resolution crops: three-quarter above, rear below. Static comparison, not a frame-rate test.',font=small,fill='#d4dce4')
dr.text((18,790),'100k candidate removes 80% of source triangles. Original downloads and the animation lane are untouched.',font=small,fill='#d4dce4')
board.save(p/'optimization-comparison.png')
# Full-frame distance comparison preserves the small on-screen size.
far=Image.new('RGB',(1536,355),'#171c22');df=ImageDraw.Draw(far)
for col,v in enumerate(['source-4k','100k-2k','40k-2k']):
 df.text((col*512+12,12),v+' | 8 metres farther',font=small,fill='white')
 far.paste(Image.open(p/f'{v}-y135-d8.png').resize((512,288),Image.Resampling.LANCZOS),(col*512,44))
df.text((12,334),'Full frames reduced equally. No close-up zoom used here.',font=small,fill='white')
far.save(p/'distance-comparison.png')
