from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path('D:/dev/new-mech-rpg/docs/art/moba/cobra_m/rigged-repair-v1-2026-11-10')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
labels={'intact':'INTACT BEFORE REMESH | single-tail correction','remeshed':'REMESHED + RIGGED | downloaded input','repaired':'LOCAL REPAIR v1 | existing rig preserved'}
for view in ['front','side','back','right','underside','three-quarter']:
 canvas=Image.new('RGB',(2160,820),'#17202a');d=ImageDraw.Draw(canvas)
 for i,version in enumerate(labels):
  canvas.paste(Image.open(ROOT/f'{version}-{view}.png').convert('RGB'),(i*720,65));d.text((i*720+18,15),labels[version],font=small,fill='white')
 d.text((20,790),'COBRA / '+view.upper()+' / matched display scale; original generation sheets remain separate',font=small,fill='white')
 canvas.save(ROOT/f'review-{view}.png')
canvas=Image.new('RGB',(1200,1340),'#17202a');d=ImageDraw.Draw(canvas)
for i in range(4):
 for j,version in enumerate(['remeshed','repaired']):
  image=Image.open(ROOT/f'{version}-patch-{i+1}.png').convert('RGB');image.thumbnail((600,300));canvas.paste(image,(j*600,i*335+30));d.text((j*600+12,i*335+5),f'Patch {i+1} / {version}',font=small,fill='white')
canvas.save(ROOT/'patch-closeups.png')
canvas=Image.new('RGB',(1440,960),'#17202a');d=ImageDraw.Draw(canvas)
for i,name in enumerate(['repaired-three-quarter','pose-tail-left','pose-tail-right','pose-neck']):
 image=Image.open(ROOT/f'{name}.png').convert('RGB');image.thumbnail((720,440));canvas.paste(image,((i%2)*720,(i//2)*480+35));d.text(((i%2)*720+20,(i//2)*480+5),name,font=font,fill='white')
canvas.save(ROOT/'rig-deformation-proof.png')
print('Packaged 5 labeled matched comparison sheets, patch closeups and rig proof')
