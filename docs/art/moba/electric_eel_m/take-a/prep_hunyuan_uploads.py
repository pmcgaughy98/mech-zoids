"""Package tight rectangular uploads; preserve artwork and source pixel scale."""
from pathlib import Path
import hashlib,json,zipfile
import numpy as np
from PIL import Image
from scipy import ndimage

root=Path(__file__).resolve().parent
out=root/'hunyuan_uploads_v1'
out.mkdir(exist_ok=True)
raw=root/'sheet_raw.png'
rgba=np.array(Image.open(raw).convert('RGBA'))
mask=rgba[:,:,3]>=128
labels,_=ndimage.label(mask,structure=np.ones((3,3),dtype=bool))
counts=np.bincount(labels.ravel());counts[0]=0
objects=ndimage.find_objects(labels)
report={'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
        'operation':'Crop each isolated raw silhouette, add 8px white border. No scaling, stretching, repainting or paid API calls.',
        'occupancy_metric':'Local alpha>=128 foreground fraction; not the remote proprietary detector.',
        'views':{}}
for index in np.argsort(counts)[-4:]:
    ys,xs=objects[index-1]
    cy,cx=ndimage.center_of_mass(mask,labels,int(index))
    name=('front' if cx<rgba.shape[1]/2 else 'left') if cy<rgba.shape[0]/2 else ('back' if cx<rgba.shape[1]/2 else 'right')
    crop=rgba[ys,xs].copy()
    selected=labels[ys,xs]==index
    crop[:,:,3]=np.where(selected,crop[:,:,3],0)
    padding=8
    size=(crop.shape[1]+2*padding,crop.shape[0]+2*padding)
    sheet=Image.new('RGBA',size,'white')
    sheet.alpha_composite(Image.fromarray(crop),(padding,padding))
    filename=f'electric_eel_{name}_hunyuan.png'
    sheet.convert('RGB').save(out/filename)
    foreground_fraction=int(selected.sum())/(size[0]*size[1])
    assert min(size)>=128 and max(size)<=5000
    # Tencent does not document its detector's precise ratio calculation.
    # Verify tight bounding-box framing; report foreground separately rather
    # than misrepresenting a local mask as a successful remote validation.
    bbox_fraction=crop.shape[0]*crop.shape[1]/(size[0]*size[1])
    assert bbox_fraction>0.89,(name,bbox_fraction)
    report['views'][name]={'file':filename,'canvas':list(size),'foreground_fraction':round(foreground_fraction,4),
       'bounding_box_fraction':round(crop.shape[0]*crop.shape[1]/(size[0]*size[1]),4),'source_box':[xs.start,ys.start,xs.stop,ys.stop]}
assert set(report['views'])=={'front','left','back','right'}
(out/'prep.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
with zipfile.ZipFile(out/'electric_eel_hunyuan_uploads.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['front','left','back','right']:
        file=out/report['views'][name]['file'];z.write(file,arcname=file.name)
    z.write(out/'prep.json',arcname='prep.json')
print(json.dumps(report,indent=2))
