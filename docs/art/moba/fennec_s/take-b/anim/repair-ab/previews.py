from repair import *
from PIL import GifImagePlugin
import hashlib
rows=[];locked=[];changed=[]
for m,d in MOVES.items():
 for v in VIEWS:
  fs=files(m,v);grid=json.loads((d/'grid.json').read_text())
  # Read original preview holds; retained independently of differing grid schemas.
  gif=Image.open(d/f'preview_{v}.gif');times=[]
  for i in range(gif.n_frames):gif.seek(i);times.append(gif.info.get('duration',100))
  if len(times)!=len(fs):
   print('TIMING MISMATCH',m,v,len(times),len(fs));raise RuntimeError('timing')
  pics=[]
  for i,p in enumerate(fs):
   a=np.array(Image.open(p).convert('RGBA'));n=len(fs)
   req=(i==0 and m not in ['walk','pop_out']) or (i==n-1 and m in ['idle','sand_kick','ear_burst','sonic_boom','pop_out'])
   if req:
    assert np.array_equal(a,np.array(still(v))),(m,v,i,'not exact');locked.append(f'{m}/{p.name}')
   pre=d/'frames_pre_repair'/p.name
   if pre.exists():changed.append({'frame':f'{m}/{p.name}','before_sha256':hashlib.sha256(pre.read_bytes()).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed_pixels':int(np.any(a!=np.array(Image.open(pre).convert('RGBA')),2).sum())})
   op=a[:,:,3]>0;bottom=np.where(op)[0].max();assert bottom== (bottom if m=='pop_out' and i==2 else 160)
   if m=='pop_out' and i==2:assert 140<=bottom<=150
   assert not op[161:].any()
   b=selout(a)[0];bg=Image.new('RGBA',(192,192),'#737980');bg.alpha_composite(Image.fromarray(b))
   pic=bg.convert('RGB').resize((768,768),Image.Resampling.NEAREST).quantize(colors=32,method=Image.Quantize.FASTOCTREE)
   pics.append(pic)
  # Exact frame blocks prevent repeated holds being merged.
  for dst in [d/f'preview_{v}.gif',OUT/f'preview-{m}-{v}.gif']:
   with dst.open('wb') as fp:
    head,_=GifImagePlugin.getheader(pics[0],info={'loop':0,'optimize':False})
    for block in head:fp.write(block)
    for pic,ms in zip(pics,times):
     for block in GifImagePlugin.getdata(pic,duration=ms,disposal=2,include_color_table=True):fp.write(block)
    fp.write(b';')
   gg=Image.open(dst);assert gg.n_frames==len(fs)
   tt=[]
   for j in range(gg.n_frames):gg.seek(j);tt.append(gg.info['duration'])
   assert tt==times
  rows.append((m,v,times))
(OUT/'validation.json').write_text(json.dumps({'frames':153,'changed':changed,'locked_exact':locked,'gif_timing':rows},indent=2))
html='''<!doctype html><style>body{background:#737980;color:white;font:18px sans-serif;margin:10px}img{width:31vw;image-rendering:pixelated}h2{margin:4px}button{font-size:20px;margin:5px}</style><div id="buttons"></div><h2 id="title"></h2><div id="gifs"></div><script>const moves=MOVES;function show(m){document.querySelector('#title').textContent=m+' / front - side - back / sel-out';document.querySelector('#gifs').innerHTML=['front','side','back'].map(v=>`<img src="preview-${m}-${v}.gif">`).join('')}moves.forEach(m=>{let b=document.createElement('button');b.textContent=m;b.onclick=()=>show(m);document.querySelector('#buttons').append(b)});show(moves[0]);</script>'''.replace('MOVES',json.dumps(list(MOVES)))
(OUT/'play.html').write_text(html)
print('PASS',len(changed),'changed;',len(locked),'exact locked frames; GIF holds retained')
