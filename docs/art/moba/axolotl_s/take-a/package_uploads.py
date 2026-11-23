from pathlib import Path
from PIL import Image
import numpy as np
import json,zipfile
root=Path(__file__).resolve().parent
prep=json.loads((root/'white_views/prep.json').read_text())
out=root/'tight_white_views'
out.mkdir(exist_ok=True)
checks={}
for view in ['front','left','back','right']:
    name=f'axolotl_{view}.png'
    im=Image.open(root/'white_views'/name)
    assert im.mode=='RGB' and im.size==(1024,1024)
    x0,y0,x1,y1=prep['views'][view]['output_box']
    tight=im.crop((x0-4,y0-4,x1+4,y1+4))
    tight.save(out/name)
    a=np.array(tight)
    assert min(tight.size)>=128
    assert np.all(a[:4]==255) and np.all(a[-4:]==255)
    assert np.all(a[:,:4]==255) and np.all(a[:,-4:]==255)
    checks[view]={'dimensions':list(tight.size),'local_nonwhite_fraction':float(np.any(a<245,axis=2).mean())}
(out/'prep.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'axolotl_four_white_sheets.zip','w',zipfile.ZIP_DEFLATED) as z:
    for folder in ['white_views','tight_white_views']:
        for view in ['front','left','back','right']:
            name=f'axolotl_{view}.png'
            z.write(root/folder/name,arcname=f'{folder}/{name}')
        z.write(root/folder/'prep.json',arcname=f'{folder}/prep.json')
    for name in ['prompt.txt','REPORT.md']:
        if (root/name).exists():z.write(root/name,arcname=name)
    z.write(root/'white_views/review.png',arcname='review.png')
with zipfile.ZipFile(root/'axolotl_four_white_sheets.zip') as z:assert z.testzip() is None
print(json.dumps(checks,indent=2))

