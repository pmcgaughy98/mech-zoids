from pathlib import Path
import json,hashlib,shutil,sys
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10')
from diagnose import read_glb,accessor,topology
import numpy as np
BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/hummingbird_s/needle-length-v3-2026-11-10';OLD=BASE/'docs/art/moba/hummingbird_s/needle-repair-v1-2026-11-10';ROOT=Path(__file__).parent;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
path=OUT/'hummingbird-rigged-needle-length-v3.glb';check=json.loads((OUT/'visual-deformation-check.json').read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==check['tested_sha256']
source=BASE/'docs/art/moba/hummingbird_s/topology-repair-v2-2026-11-10/hummingbird-rigged-needle-topology-v2.glb';a,ab=read_glb(source);d,b=read_glb(path);pr=d['meshes'][0]['primitives'][0];old=a['meshes'][0]['primitives'][0]
for key in ['nodes','skins','materials','images','textures','animations']:assert a.get(key)==d.get(key)
for attr in ['JOINTS_0','WEIGHTS_0','TEXCOORD_0']:assert np.array_equal(accessor(a,ab,old['attributes'][attr]),accessor(d,b,pr['attributes'][attr]))
p=accessor(d,b,pr['attributes']['POSITION']);op=accessor(a,ab,old['attributes']['POSITION']);assert np.array_equal(p[op[:,2]<=.30],op[op[:,2]<=.30]);t=accessor(d,b,pr['indices']).reshape(-1,3);m,e,g,deg=topology(p,t);assert not g and not deg and all(len(fs)==2 for fs in e.values())
(OUT/'verification.json').write_text(json.dumps({'approval':'Preston selected 30% shorter shaft','output_sha256':check['tested_sha256'],'body_collar_positions_weights_uvs_rig_binds_materials_textures_unchanged':True,'shaft_factor':.7,'tip_z_before':float(op[:,2].max()),'tip_z_after':float(p[:,2].max()),'boundaries':0,'over_shared_edges':0,'triangles':len(t)},indent=2))
canvas=Image.new('RGB',(1440,780),'#17202a');dr=ImageDraw.Draw(canvas)
for i,(version,label) in enumerate([('before','PREVIOUS LENGTH'),('after','APPROVED / SHAFT 30% SHORTER')]):canvas.paste(Image.open(OUT/f'{version}-needle-side.png').convert('RGB'),(i*720,50));dr.text((i*720+15,10),label,font=font,fill='white')
canvas.save(OUT/'approved-needle-before-after.png')
for view in ['front','side','right','back','underside','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');dr=ImageDraw.Draw(canvas)
 for i,(image,label) in enumerate([(OLD/f'intact-{view}.png','INTACT PRE-REMESH'),(OLD/f'before-{view}.png','DOWNLOADED RIGGED INPUT'),(OUT/f'after-{view}.png','V3 / APPROVED SHORTER SHAFT')]):canvas.paste(Image.open(image).convert('RGB'),(i*720,65));dr.text((i*720+15,15),label,font=font,fill='white')
 dr.text((15,790),'HUMMINGBIRD / '+view.upper()+' / original generation sheets preserved',font=font,fill='white');canvas.save(OUT/f'review-{view}.png')
cat=BASE/'art/model_catalog/catalog.json';data=json.loads(cat.read_text());entry=next(e for e in data['entries'] if e['id']=='hummingbird');prefix='res://docs/art/moba/hummingbird_s/needle-length-v3-2026-11-10/'
entry['display_model']=prefix+'hummingbird-rigged-needle-length-v3.glb';entry['status']='Hummingbird v3: approved 30% shorter straight shaft; repaired topology retained. Original rig, weights, collar/body and textures preserved.';entry['review_models'][2].update(label='APPROVED LENGTH v3\nShaft 30% shorter',path=entry['display_model'])
for key,view in [('front','front'),('left','side'),('back','back'),('right','right')]:entry['review_views'][key]['path']=prefix+f'review-{view}.png'
entry['review_provenance'].update(report=prefix+'verification.json',repaired_sha256=check['tested_sha256'],scope='Approved 30% shorter shaft, straightening and topology v2 retained. Original rig/weights/body preserved.')
cat.write_text(json.dumps(data,indent=2)+'\n')
for filename in ['review_length_v3.py','package_length_v3.py','length_study.py']:shutil.copy2(ROOT/filename,OUT/filename)
print('Verified approved v3, packaged sheets and updated Workshop.')
