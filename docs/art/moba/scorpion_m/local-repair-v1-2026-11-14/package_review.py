import hashlib, json, shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).parent
BASE = Path('D:/dev/new-mech-rpg')
OUT = BASE/'docs/art/moba/scorpion_m/local-repair-v1-2026-11-14'
r = json.loads((OUT/'repair-verification.json').read_text())
a = json.loads((OUT/'independent-export-audit.json').read_text())
poses = json.loads((OUT/'visual-deformation-check.json').read_text())
assert a['passed'] and a['tested_sha256']==r['output_sha256']==poses['tested_sha256']
assert len(poses['poses'])+len(poses['no_surface_motion'])==52 and len(poses['poses'])>=40
res = lambda p: 'res://'+p.relative_to(BASE).as_posix()
font = lambda n: ImageFont.truetype('C:/Windows/Fonts/arial.ttf', n)
src = Path(r['source'])
archive = BASE/'art/model_catalog/sources'/src.name
if archive.exists():
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==r['source_sha256']
else:
    shutil.copy2(src, archive)
catpath = BASE/'art/model_catalog/catalog.json'
cat = json.loads(catpath.read_text(encoding='utf-8'))
e = next(e for e in cat['entries'] if e['id']=='scorpion')
review = {}
versions = [('intact','INTACT GENERATED QUALITY ARCHIVE','#c5d8ed'),('before','DOWNLOADED RIG / BEFORE REPAIR','#f4c48b'),('after','LOCAL REPAIR / SAME RIG AND WEIGHTS','#97e8b8')]
for key in ['front','left','back','right']:
    im = Image.new('RGB',(2160,865),'#14212c')
    d = ImageDraw.Draw(im)
    d.text((18,12),'Scorpion / '+key.upper()+' / quality and local repair',font=font(28),fill='white')
    for i,(v,label,color) in enumerate(versions):
        d.text((i*720+15,58),label,font=font(22),fill=color)
        im.paste(Image.open(OUT/f'{v}-{key}.png').convert('RGB'),(i*720,100))
    d.text((18,830),'Eight walking legs, both pincers and raised tail retained. Original rig, skin and textures preserved.',font=font(22),fill='#c5d8ed')
    dest = OUT/f'review-{key}.png'
    im.save(dest)
    review[key] = {'path':res(dest),'kind':'Intact generated quality archive / downloaded rig / local repair; matched view and scale'}
im = Image.new('RGB',(1440,1570),'#14212c')
d = ImageDraw.Draw(im)
d.text((18,12),'Scorpion / 23 malformed triangles removed; original surface retained',font=font(29),fill='white')
for row,part in enumerate(['head','tail']):
    for col,(v,label) in enumerate([('before','BEFORE'),('after','AFTER')]):
        y = 60+row*755
        d.text((col*720+18,y),label+' / '+part.upper(),font=font(25),fill='#f4c48b' if col==0 else '#97e8b8')
        im.paste(Image.open(OUT/f'{v}-{part}.png').convert('RGB'),(col*720,y+35))
im.save(OUT/'before-after.png')
im = Image.new('RGB',(1200,1980),'#14212c')
d = ImageDraw.Draw(im)
d.text((14,10),'Scorpion / 21 views from native joint diagnostics',font=font(29),fill='white')
for i,label in enumerate(poses['rendered_poses']):
    x = i%4*300
    y = 55+i//4*320
    im.paste(Image.open(OUT/f'pose-{label}.png').convert('RGB').resize((300,290)),(x,y))
    d.text((x+7,y+292),label,font=font(20),fill='white')
im.save(OUT/'pose-proof.png')
cfg = json.loads((ROOT/'input-audit.json').read_text())
meta = json.loads((OUT/'intact-render-metadata.json').read_text())
fit = min(2.9/max(cfg['bounds'][1][i]-cfg['bounds'][0][i] for i in [0,2]),2.6/1.7)
e['display_model'] = res(Path(r['output']))
e['artist_workspace'] = res(Path(r['output']).with_suffix('.blend'))
e['status'] = '23 malformed triangles removed. Eight walking legs, both pincers and raised tail retained. New supplied 52-joint rig, all skin weights and textures preserved.'
e['review_models'] = [
    {'label':'INTACT QUALITY ARCHIVE\nOriginal generated geometry','path':e['source_model']['path'],'display_scale':fit*meta['height_scale']},
    {'label':'DOWNLOADED RIG\nBefore local triangle cleanup','path':res(archive),'display_scale':fit},
    {'label':'LOCAL REPAIR\nSame 52-joint rig and skin','path':res(Path(r['output'])),'display_scale':fit}
]
e['review_views'] = review
e['review_provenance'] = {'date':'2026-11-14','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':52,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_available':True,'source_archive_scope':'Intact generated quality archive; exact historical Meshy upload not independently verified.','scope':r['scope']+' All 23,970 healthy source faces retained. No gameplay replacement.'}
(OUT/'catalog-entry.json').write_text(json.dumps(e,indent=2)+'\n')
for name in ['diagnose_model.py','render_model.py','repair_model.py','audit_export.py','detail_pose_review.py','package_review.py','input-audit.json','face-components.json']:
    shutil.copy2(ROOT/name, OUT/name)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:
    latest = json.loads(catpath.read_text(encoding='utf-8'))
    other = [x for x in latest['entries'] if x['id']!='scorpion']
    latest['entries'] = [e if x['id']=='scorpion' else x for x in latest['entries']]
    assert [x for x in latest['entries'] if x['id']!='scorpion']==other
    catpath.write_text(json.dumps(latest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Scorpion package ready:', r['output_sha256'])
