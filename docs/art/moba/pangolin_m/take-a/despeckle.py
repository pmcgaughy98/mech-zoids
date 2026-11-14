from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
import json
P=Path(__file__).resolve().parent
LENS={(0x5e,0xf2,0xe6),(0xe8,0xff,0xfb)}
def despeckle(a):
    h, w = a.shape[:2]
    out = a.copy()
    fixed = 0
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] == 0 or tuple(a[y, x, :3]) in LENS:
                continue
            nbrs = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3] > 0]
            if not nbrs:
                continue
            here = a[y, x, :3].astype(int)
            if any(np.abs(here - np.array(n[:3], int)).sum() < 30 for n in nbrs):
                continue
            out[y, x] = Counter(nbrs).most_common(1)[0][0]
            fixed += 1
    return out, fixed



a=np.array(Image.open(P/'sheet_finished.png').convert('RGBA'))
a,n=despeckle(a)
Image.fromarray(a).save(P/'sheet_finished.png')
(P/'despeckle.json').write_text(json.dumps({'passes':1,'pixels_changed':n,'eye_colours_preserved':True},indent=2))
print('despeckle pixels',n)
