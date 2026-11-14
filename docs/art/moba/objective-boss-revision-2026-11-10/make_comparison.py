"""Compose previews without modifying original generated concepts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json,zipfile

root=Path(__file__).resolve().parent
items=[('coin_beetle','GOLD: COIN BEETLE REVISION'),('power_wyvern','POWER A: WYVERN PROPOSAL'),('power_ankylosaur','POWER B: ANKYLOSAUR PROPOSAL')]
board=Image.new('RGB',(2400,760),'white')
draw=ImageDraw.Draw(board)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
manifest={}
for col,(key,title) in enumerate(items):
    p=root/key/'concept_raw.png'
    im=Image.open(p).convert('RGB')
    im.thumbnail((776,650),Image.Resampling.NEAREST)
    board.paste(im,(col*800+(800-im.width)//2,65+(650-im.height)//2))
    draw.text((col*800+20,22),title,font=font,fill='#20242b')
    manifest[key]={'file':f'{key}/concept_raw.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size),'prompt':f'{key}/prompt.txt'}
board.save(root/'concept_comparison.png')
(root/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(root/'boss_concept_comparison.zip','w',zipfile.ZIP_DEFLATED) as z:
    for key,_ in items:
        for name in ['concept_raw.png','prompt.txt']:
            z.write(root/key/name,arcname=f'{key}/{name}')
    for name in ['concept_comparison.png','manifest.json','REPORT.md']:
        if (root/name).exists(): z.write(root/name,arcname=name)
print(json.dumps(manifest,indent=2))
