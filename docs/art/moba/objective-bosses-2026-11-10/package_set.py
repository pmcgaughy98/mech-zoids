"""Package generated references; raw files are never changed."""
from pathlib import Path
import json, zipfile, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
roles = ['gold_stag_beetle', 'power_elephant']
views = ['front', 'left', 'back', 'right']
summary = {}
board = Image.new('RGB', (1440, 800), 'white')
draw = ImageDraw.Draw(board)
for row, role in enumerate(roles):
    folder = root / role
    subprocess.run([sys.executable, str(folder/'prep_white_views.py')], check=True, capture_output=True)
    report = json.loads((folder/'white_views/prep.json').read_text())
    uploads = folder/'tight_white_views'
    uploads.mkdir(exist_ok=True)
    summary[role] = {'source_sha256': report['source_sha256'], 'height_spread': report['source_height_spread_fraction'], 'views': {}}
    for col, view in enumerate(views):
        name = f'boss_{role}_{view}.png'
        source = Image.open(folder/'white_views'/name)
        x0,y0,x1,y1 = report['views'][view]['output_box']
        tight = source.crop((x0-4,y0-4,x1+4,y1+4))
        tight.save(uploads/name)
        pixels = np.array(tight)
        # Local color mask is an upload framing diagnostic, not provider validation.
        coverage = float(np.any(pixels < 245, axis=2).mean())
        summary[role]['views'][view] = {'size': list(tight.size), 'local_nonwhite_fraction': round(coverage,4)}
        assert tight.mode == 'RGB' and min(tight.size) >= 128
        assert np.all(pixels[:4] == 255) and np.all(pixels[-4:] == 255)
        assert np.all(pixels[:,:4] == 255) and np.all(pixels[:,-4:] == 255)
        thumb = tight.copy()
        thumb.thumbnail((330,335), Image.Resampling.NEAREST)
        x,y = col*360+(360-thumb.width)//2, row*400+35+(345-thumb.height)//2
        board.paste(thumb,(x,y))
        draw.text((col*360+15,row*400+12),f'{role.upper()} / {view.upper()}',fill='black')
    (uploads/'prep.json').write_text(json.dumps(summary[role],indent=2),encoding='utf-8')
    with zipfile.ZipFile(folder/f'boss_{role}_four_white_views.zip','w',zipfile.ZIP_DEFLATED) as z:
        for view in views:
            name=f'boss_{role}_{view}.png'
            z.write(folder/'white_views'/name,arcname='square_white_views/'+name)
            z.write(uploads/name,arcname='tight_white_views/'+name)
        z.write(uploads/'prep.json',arcname='tight_white_views/prep.json')
board.save(root/'review_all.png')
(root/'packaging_checks.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'bosses_eight_white_sheets.zip','w',zipfile.ZIP_DEFLATED) as z:
    for role in roles:
        for kind in ['white_views','tight_white_views']:
            for view in views:
                p=root/role/kind/f'boss_{role}_{view}.png'
                z.write(p,arcname=f'{role}/{kind}/{p.name}')
            z.write(root/role/kind/'prep.json',arcname=f'{role}/{kind}/prep.json')
        z.write(root/role/'prompt.txt',arcname=f'{role}/prompt.txt')
    for name in ['review_all.png','packaging_checks.json','REPORT.md']:
        if (root/name).exists(): z.write(root/name,arcname=name)
print(json.dumps(summary,indent=2))

