"""One simultaneous four-neighbour despeckle pass, from shoebill take C; green and white lens colours kept."""
from pathlib import Path
from collections import Counter
import numpy as np
from PIL import Image
import json
P=Path(__file__).resolve().parent
LENS={(94,242,230),(232,255,251),(20,18,24)}
ROLES={tuple(bytes.fromhex(c['hex'])):c['role'] for c in json.loads((P/'palette.json').read_text())}
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
            nbrs=[n for n in nbrs if ROLES.get(tuple(n[:3]))==ROLES.get(tuple(a[y,x,:3]))]
            if not nbrs:
                continue
            here = a[y, x, :3].astype(int)
            if any(np.abs(here - np.array(n[:3], int)).sum() < 30 for n in nbrs):
                continue
            out[y, x] = Counter(nbrs).most_common(1)[0][0]
            fixed += 1
    return out, fixed


def lone_count(a):
    solid=a[...,3]>0
    count=0
    for c in np.unique(a[solid,:3],axis=0):
        mask=solid & np.all(a[...,:3]==c,axis=2)
        from scipy import ndimage
        neighbours=ndimage.convolve(mask.astype(int),np.ones((3,3),int),mode='constant')-mask
        count+=int((mask & (neighbours==0)).sum())
    return count

src=np.array(Image.open(P/'sheet_finished.png').convert('RGBA'))
before=lone_count(src)
a,n=despeckle(src) if before else (src,0)
Image.fromarray(a).save(P/'sheet_finished.png')
result={'passes':int(before>0),'pixels_changed':n,'lone_8neighbour_before':before,'lone_8neighbour_after':lone_count(a),'lens_colours_preserved':['5ef2e6','e8fffb','141218']}
(P/'despeckle.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
