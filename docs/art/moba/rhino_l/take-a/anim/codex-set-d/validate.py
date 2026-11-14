from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
out=Path(__file__).resolve().parent
pal=set()
for p in (out/'refs').glob('*.png'):
    if '_6x' in p.stem: continue
    ar=np.array(Image.open(p).convert('RGBA')); pal.update(map(tuple,ar[ar[:,:,3]>0,:3]))
meta=json.loads((out/'generation.json').read_text()); total=0; warnings=[]
for name,n,rows in [('brace',5,['se','ne']),('death',7,['se','ne']),('idle',5,['se','ne']),('brace-shuffle',6,['front','side','back'])]:
    p=out/name; raw=p/'sheet_raw.png'; assert hashlib.sha256(raw.read_bytes()).hexdigest()==meta[name]['sha256']
    grid=json.loads((p/'grid.json').read_text()); assert len(grid['cells'])==n*len(rows); assert len(grid['placements'])==n*len(rows)
    for r in rows:
        with Image.open(p/f'preview_{r}.gif') as gif:
            times=[]
            for i in range(gif.n_frames): gif.seek(i); times.append(gif.info['duration'])
            expected={'brace':1080,'death':1720,'idle':1000,'brace-shuffle':900}[name]
            assert sum(times)==expected,(name,r,times)
            assert (gif.info.get('loop')==0)==(name in ('idle','brace-shuffle'))
        for c in range(n):
            f=p/'frames'/f'{r}_f{c}.png'; im=Image.open(f).convert('RGBA'); ar=np.array(im); m=ar[:,:,3]>0
            assert im.size==(192,192); assert set(np.unique(ar[:,:,3]))<={0,255}
            assert set(map(tuple,ar[m,:3]))<=pal
            assert not(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
            assert not ar[~m].any()
            eyes=(np.all(ar[:,:,:3]==[255,58,42],2)|np.all(ar[:,:,:3]==[255,230,216],2))&m
            assert not (eyes&~ndi.binary_erosion(m,np.ones((3,3)))).any()
            if im.getbbox()[3]!=161: warnings.append(f'{name}/{r}_f{c}: bottom {im.getbbox()[3]-1}')
            total+=1
    assert (p/'review.png').exists()
print(f'{total} frames verified: 192x192; binary alpha; union palette; eye rim zero; no border contact; GIF total durations and looping; raw hashes; grid placements.')
print('Ground warnings: '+('; '.join(warnings) if warnings else 'none'))
