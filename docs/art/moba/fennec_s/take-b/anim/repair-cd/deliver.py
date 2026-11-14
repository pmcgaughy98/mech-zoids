from repair import *
import hashlib
manifest=[]
for m in MOVES:
 grid=json.loads((directory(m)/'grid.json').read_text())
 for v in ['se','ne']:
  fs=files(m,v); durations=grid['durations_ms']
  oldgif=Image.open(directory(m)/f'preview_{v}.gif')
  # Keep existing preview canvas dimensions, durations and looping behavior.
  oldsize=oldgif.size
  raw=[];review=[]
  for p in fs:
   im=Image.open(p).convert('RGBA');old=p.parent.parent/'frames_pre_repair'/p.name
   pre=Image.open(old).convert('RGBA') if old.exists() else im
   bg=Image.new('RGBA',(192,192),'#454953');bg.alpha_composite(im);raw.append(bg.resize(oldsize,Image.Resampling.NEAREST).convert('RGB'))
   panel=Image.new('RGBA',(3*384,392),'#454953');d=ImageDraw.Draw(panel)
   for j,(lab,q) in enumerate([('approved',still(v)),('before',pre),('after',im)]):
    panel.alpha_composite(tile(q),(j*384,24));d.text((j*384+4,4),f'{m} {v} {lab} {p.stem}',fill='white')
   review.append(panel.convert('RGB'))
   a=np.array(im);b=np.array(pre)
   manifest.append(dict(move=m,view=v,frame=p.stem,changed_pixels=int(np.any(a!=b,axis=2).sum()),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_sha256=hashlib.sha256(old.read_bytes()).hexdigest() if old.exists() else hashlib.sha256(p.read_bytes()).hexdigest()))
  opts=dict(save_all=True,duration=durations,disposal=2,optimize=False)
  if 'loop' in oldgif.info:opts['loop']=oldgif.info['loop']
  # Preserve prior preview once, in the permitted repair output folder.
  dest=OUT/f'original-preview-{m}-{v}.gif'
  if not dest.exists():shutil.copy2(directory(m)/f'preview_{v}.gif',dest)
  raw[0].save(directory(m)/f'preview_{v}.gif',append_images=raw[1:],**opts)
  review[0].save(OUT/f'preview-{m}-{v}.gif',append_images=review[1:],save_all=True,duration=durations,loop=0,disposal=2,optimize=False)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
for m in MOVES:
 links=' '.join(f'<a href="play-{q}.html">{q}</a>' for q in MOVES)
 (OUT/f'play-{m}.html').write_text(f'<html><meta charset="utf-8"><style>body{{background:#454953;color:white;font:16px sans-serif;margin:8px}}a{{color:#f0d27a;margin-right:10px}}img{{display:block;width:1152px;height:392px;image-rendering:pixelated}}</style>{links}<div>{m}: approved | before | after. SE then NE. 4x with sel-out #141218.</div><img src="preview-{m}-se.gif"><img src="preview-{m}-ne.gif"></html>')
print('changed',sum(r['changed_pixels']>0 for r in manifest),'pixels',sum(r['changed_pixels'] for r in manifest))

