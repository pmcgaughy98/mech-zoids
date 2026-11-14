from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
OUT=Path(__file__).resolve().parent
spec={'stampede':[80]*6,'horn-toss':[200,100,100,100,200,100,100],'ground-pound':[100,200,100,300,300,300],'horn-jab':[200,200,100,200,100,100]}
pal=set()
for n in ['se','ne']:
    a=np.array(Image.open(OUT/'refs'/f'{n}.png').convert('RGBA')); pal.update(map(tuple,a[a[:,:,3]>0,:3]))
checks=[]
for name,times in spec.items():
    gen=json.loads((OUT/'generation.json').read_text())[name]; raw=OUT/name/'sheet_raw.png'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==gen['sha256']
    assert list(Image.open(raw).size)==gen['size']
    grid=json.loads((OUT/name/'grid.json').read_text())
    for n in ['se','ne']:
        for entry in grid['rows'][n]['frames']:
            c=entry['frame']; f=Image.open(OUT/name/'frames'/f'{n}_f{c}.png').convert('RGBA'); a=np.array(f); m=a[:,:,3]>0
            assert f.size==(192,192) and set(np.unique(a[:,:,3]))<={0,255}
            assert set(map(tuple,a[m,:3]))<=pal and not a[~m].any()
            assert f.getbbox()[3]-1==160
            assert not(m[0].any() or m[-1].any() or m[:,0].any() or m[:,-1].any())
            eye=(np.all(a[:,:,:3]==[255,58,42],2)|np.all(a[:,:,:3]==[255,230,216],2))&m
            assert not (eye&~ndi.binary_erosion(m,structure=np.ones((3,3)))).any()
            # Recreate the frame exclusively from saved finished sheet and offsets.
            row=Image.open(OUT/name/f'row_{n}_finished.png').convert('RGBA'); cell=row.crop(entry['scaled_cell_box'])
            rebuilt=Image.new('RGBA',(192,192)); rebuilt.paste(cell,tuple(entry['final_cell_offset']))
            assert np.array_equal(a,np.array(rebuilt))
        gif=Image.open(OUT/name/f'preview_{n}.gif'); durations=[]
        for i in range(gif.n_frames): gif.seek(i); durations.append(gif.info['duration'])
        assert durations==times,(name,n,durations)
        assert gif.size==(576,576)
        assert (gif.info.get('loop')==0) if name=='stampede' else ('loop' not in gif.info)
    checks.append(f'{name}: PASS raw hash/size, all frames alpha/palette/eye-rim/feet/border, grid transform reconstruction, GIF dimensions/order durations/loop; clean={grid["clean"]}')
(OUT/'validation.txt').write_text('\n'.join(checks)+'\n')
print('\n'.join(checks)); print('palette',len(pal),'frames',52)
