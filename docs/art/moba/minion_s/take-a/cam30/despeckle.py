"""One simultaneous four-neighbour despeckle pass, from shoebill take C; green and white lens colours kept."""
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
import json
P=Path(__file__).resolve().parent
LENS={tuple(bytes.fromhex(c)) for c in ['5fd8ff','d0f4ff','f6fdff']}
def role(c):
    h=bytes(c).hex()
    return 'team' if h in ['9ad0ff','3a8cff','2258c8','14306e'] else 'glow' if h in ['5fd8ff','d0f4ff','f6fdff'] else 'steel' if h in ['e2e4ea','b8bcc6','8a8f9c','5c6170'] else 'accent' if h == '141218' else 'charcoal'

def despeckle(a):
    h, w = a.shape[:2]
    out = a.copy()
    fixed = 0
    for y in range(h):
        for x in range(w):
            if a[y, x, 3] == 0 or tuple(a[y, x, :3]) in LENS:
                continue
            nbrs = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                    if 0 <= yy < h and 0 <= xx < w and a[yy, xx, 3] > 0 and tuple(a[yy,xx,:3]) not in LENS]
            nbrs = [n for n in nbrs if role(n[:3]) == role(a[y,x,:3])]
            if not nbrs:
                continue
            here = a[y, x, :3].astype(int)
            if any(np.abs(here - np.array(n[:3], int)).sum() < 30 for n in nbrs):
                continue
            out[y, x] = Counter(nbrs).most_common(1)[0][0]
            fixed += 1
    return out, fixed


a,n=despeckle(np.array(Image.open(P/'sheet_finished.png').convert('RGBA')))
Image.fromarray(a).save(P/'sheet_finished.png')
(P/'despeckle.json').write_text(json.dumps({'passes':1,'pixels_changed':n,'lens_colours_preserved':['5fd8ff','d0f4ff','f6fdff']},indent=2))
print('despeckle pixels changed',n)
