from pathlib import Path
import json,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10';ROOT=Path(__file__).parent;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
canvas=Image.new('RGB',(1440,1540),'#17202a');draw=ImageDraw.Draw(canvas)
for r,view in enumerate(['needle-side','needle-top']):
 for c,version in enumerate(['before','after']):
  canvas.paste(Image.open(OUT/f'{version}-{view}.png').convert('RGB'),(c*720,r*770+40));draw.text((c*720+15,r*770+8),version.upper()+' / '+view+' / same length',font=font,fill='white')
canvas.save(OUT/'needle-before-after.png')
for view in ['front','side','right','back','underside','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');draw=ImageDraw.Draw(canvas)
 for i,(version,label) in enumerate([('intact','INTACT PRE-REMESH'),('before','REMESHED + RIGGED INPUT'),('after','STRAIGHT NEEDLE v1 / existing rig')]):
  canvas.paste(Image.open(OUT/f'{version}-{view}.png').convert('RGB'),(i*720,65));draw.text((i*720+15,15),label,font=font,fill='white')
 draw.text((15,790),'HUMMINGBIRD / '+view.upper()+' / model comparisons; original sheets preserved',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
v=json.loads((OUT/'verification.json').read_text());check=json.loads((OUT/'visual-deformation-check.json').read_text());assert v['output_sha256']==check['tested_sha256']
archive=OUT/'hummingbird-remeshed-rigged-input.glb'
if not archive.exists():shutil.copy2(v['source'],archive)
assert hashlib.sha256(archive.read_bytes()).hexdigest()==v['source_sha256']
catalog=BASE/'art/model_catalog/catalog.json';data=json.loads(catalog.read_text());entry=next(e for e in data['entries'] if e['id']=='hummingbird');prefix='res://docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10/';fit=2.9/3.9312416
entry.update(display_model=prefix+'hummingbird-rigged-straight-needle-v1.glb',status='Needle v1: straightened shaft and taper; length retained. Existing 21-bone rig/weights preserved. Other remesh defects pending.')
entry['review_models']=[{'label':'INTACT PRE-REMESH\nOriginal source','path':entry['source_model']['path'],'display_scale':fit*check['intact_alignment']['uniform_scale']},{'label':'REMESHED + RIGGED\nDownloaded input','path':prefix+'hummingbird-remeshed-rigged-input.glb','display_scale':fit},{'label':'STRAIGHT NEEDLE v1\nLength + rig retained','path':entry['display_model'],'display_scale':fit}]
entry['review_views']={key:{'path':prefix+f'review-{view}.png','kind':'Rendered version comparison, not generation input'} for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]}
entry['review_provenance']={'date':'2026-11-10','report':prefix+'verification.json','rigged_input_sha256':v['source_sha256'],'repaired_sha256':v['output_sha256'],'scope':'Needle shape only. Existing rig and weights untouched; no length change; other topology/finish defects not approved.'}
catalog.write_text(json.dumps(data,indent=2)+'\n')
for filename in ['repair.py','review.py','package.py']:shutil.copy2(ROOT/filename,OUT/filename)
shutil.copy2('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py',OUT/'diagnose.py')
print('Hummingbird needle comparison packaged and Workshop entry updated.')
