import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path('D:/dev/new-mech-rpg/docs/art/moba/falcon_m/local-repair-v1-2026-11-13');marks=json.loads((OUT/'foot-label-pixels.json').read_text());im=Image.new('RGB',(720,845),'#14212c');im.paste(Image.open(OUT/'before-feet.png').convert('RGB'),(0,65));d=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n);d.text((15,15),'Falcon / five-toe foot, underside',font=font(28),fill='white');x,y=marks['outer_rear'];y+=65
d.line([(630,690),(x,y)],fill='black',width=8);d.line([(630,690),(x,y)],fill='#ffbf59',width=4);d.ellipse((605,665,655,715),fill='#ffbf59',outline='black',width=3);d.text((622,674),'1',font=font(27),fill='black');d.text((15,794),'1 extra outer rear toe / recommend removing both sides',font=font(24),fill='white');im.save(OUT/'foot-extra-toe-labeled.png');print(marks)
