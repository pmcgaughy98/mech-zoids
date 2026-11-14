import sys,json,shutil,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parent;BASE=Path('D:/dev/new-mech-rpg');OUT=BASE/'docs/art/moba/shoebill_m/backplate-repair-v1-2026-11-13'
r=json.loads((OUT/'repair-verification.json').read_text());audit=json.loads((OUT/'independent-export-audit.json').read_text());poses=json.loads((OUT/'visual-deformation-check.json').read_text());assert audit['passed'] and r['output_sha256']==poses['tested_sha256']==audit['tested_sha256'];assert len(poses['poses'])==14 and max(p['coincident_surface_gap_m'] for p in poses['poses'])<1e-6
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def res(p):return 'res://'+p.relative_to(BASE).as_posix()
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
source=Path(r['source']);archive=BASE/'art/model_catalog/sources'/source.name;assert sha(source)==r['source_sha256']
if archive.exists():assert sha(archive)==r['source_sha256']
else:shutil.copy2(source,archive)
catpath=BASE/'art/model_catalog/catalog.json';cat=json.loads(catpath.read_text(encoding='utf-8'));entry=next(e for e in cat['entries'] if e['id']=='shoebill');original_entry=json.loads(json.dumps(entry));views={}
for key in ['front','left','back','right']:
 im=Image.new('RGB',(2100,865),'#14212c');draw=ImageDraw.Draw(im);draw.text((20,12),'Shoebill / '+key.upper()+' / body quality and fitted moon-plate repair',font=font(28),fill='white')
 labels=['INTACT BODY ARCHIVE\nOriginal backplate','RIGGED DOWNLOAD\nDonor feather overlap','BACKPLATE REPAIR\nSame 38-joint skeleton']
 for i,(version,label) in enumerate(zip(['intact','before','after'],labels)):
  draw.multiline_text((i*700+18,51),label,font=font(24),fill=['#c5d7ee','#f5c583','#95eaba'][i],spacing=3);im.paste(Image.open(OUT/f'{version}-{key}.png').convert('RGB').resize((700,700)),(700*i,115))
 draw.text((20,826),'The intact archive shows the body before the fitted moon plate. Original files and four source reference PNGs are preserved.',font=font(22),fill='#cedde9');path=OUT/f'review-{key}.png';im.save(path);views[key]={'path':res(path),'kind':'Intact body archive with original backplate / rigged fitted moon plate / local repair; source designs explicitly labeled'}
def pair(view,title,dest):
 im=Image.new('RGB',(1600,950),'#14212c');draw=ImageDraw.Draw(im);draw.text((20,12),title,font=font(30),fill='white')
 for i,(v,label) in enumerate([('before','BEFORE / DONOR FEATHER OVERLAP'),('after','AFTER / MOON FACE CLEARED')]):
  draw.text((800*i+18,56),label,font=font(25),fill='#f4c58e' if i==0 else '#95eaba');im.paste(Image.open(OUT/f'{v}-{view}.png').convert('RGB'),(i*800,100))
 draw.text((20,914),'Original body, wings and 38-joint skeleton retained. Matching camera and lighting.',font=font(25),fill='#cedde9');im.save(OUT/dest)
pair('plate-three-quarter','Shoebill / fitted backplate correction','backplate-before-after.png')
pair('plate-back','Shoebill / moon-plate face and rim','backplate-face-comparison.png')
files=[OUT/f'pose-{p["label"]}.png' for p in poses['poses']];cols=4;cell=280;im=Image.new('RGB',(cols*cell,math.ceil(len(files)/cols)*(cell+30)+50),'#14212c');draw=ImageDraw.Draw(im);draw.text((12,10),'Shoebill / 14 native-joint diagnostic poses',font=font(24),fill='white')
for i,p in enumerate(files):
 x=i%cols*cell;y=50+i//cols*(cell+30);im.paste(Image.open(p).convert('RGB').resize((cell,cell)),(x,y));draw.text((x+8,y+cell+3),p.stem,font=font(16),fill='white')
im.save(OUT/'pose-proof.png')
entry['display_model']=res(Path(r['output']));entry['artist_workspace']=res(Path(r['output']).with_suffix('.blend'));entry['status']='Donor feather overlap removed from moon plate; local gaps/flaps repaired. Original 38-joint rig and weights retained.'
original_height=1.101505994796753
entry['review_models']=[{'label':'INTACT BODY ARCHIVE\nOriginal backplate','path':entry['source_model']['path'],'display_scale':2.6/original_height},{'label':'RIGGED DOWNLOAD\nFitted plate / overlap','path':res(archive),'display_scale':2.6/1.7},{'label':'BACKPLATE REPAIR\nSame 38-joint skeleton','path':res(Path(r['output'])),'display_scale':2.6/1.7}]
entry['review_views']=views;entry['review_provenance']={'date':'2026-11-13','report':res(OUT/'repair-verification.json'),'independent_audit':res(OUT/'independent-export-audit.json'),'joint_count':38,'rigged_input_sha256':r['source_sha256'],'repaired_sha256':r['output_sha256'],'intact_pre_remesh_body_available':True,'exact_composite_pre_remesh_source_available':False,'body_archive_scope':'Original generated body archive with its earlier backplate; not verified as the exact historical upload of the fitted composite. Current approved moon plate retained.','scope':r['scope']+' Original position/normal/UV/skin rows retained. New rear-shell vertices copy corresponding source skin weights; original skeleton/rest/binds/materials/textures unchanged. Hidden mount closures and one small head gap repaired. No gameplay installation.'}
(OUT/'catalog-entry.json').write_text(json.dumps(entry,indent=2)+'\n');(OUT/'previous-catalog-entry.json').write_text(json.dumps(original_entry,indent=2)+'\n') if not (OUT/'previous-catalog-entry.json').exists() else None
for file in ['diagnose_shoebill.py','rebuild_plate_shell.py','review_rig_and_source.py','audit_export.py','package_shoebill.py','face-components.json','mesh-analysis.npz']:shutil.copy2(ROOT/file,OUT/file)
shutil.copy2(Path('D:/dev/_scratch/mech-art-direction/roster-repair-2026-11-10/diagnose.py'),OUT/'diagnose.py')
if '--publish' in sys.argv:catpath.write_text(json.dumps(cat,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('Shoebill Workshop entry and sheets published.')
print('Final SHA256',r['output_sha256'])
