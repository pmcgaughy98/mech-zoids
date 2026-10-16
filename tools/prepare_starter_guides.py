from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'docs/art/starter-sources-2026-10-11/guides'
out.mkdir(parents=True, exist_ok=True)
dirs = ['e','ne','n','nw','w','sw','s','se']
for machine in ['ape_l','shoebill_m','pangolin_m','hippo_m']:
    sheet = Image.open(ROOT / f'docs/team/view-guides/{machine}.png')
    for i,direction in enumerate(dirs):
        x, y = (i % 4) * 96, (i // 4) * 82 + 10
        crop = sheet.crop((x,y,x+96,y+72))
        crop.resize((768,576), Image.Resampling.NEAREST).save(out / f'{machine}-{direction}.png')

retired = ROOT / 'docs/art/retired-2026-10-11'
retired.mkdir(parents=True, exist_ok=True)
records = []
for name in ['lion_m.png','raptor_s.png']:
    source = ROOT / 'art/machines' / name
    destination = retired / name
    if source.exists():
        if destination.exists():
            raise FileExistsError(destination)
        records.append({'from':str(source), 'to':str(destination), 'size':Image.open(source).size})
        source.rename(destination)
if records:
    (retired / 'manifest.json').write_text(json.dumps(records, indent=2))
