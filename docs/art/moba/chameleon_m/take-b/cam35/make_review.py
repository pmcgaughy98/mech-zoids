from pathlib import Path
from PIL import Image,ImageDraw
import shutil
P=Path(__file__).resolve().parent; V=P.parent/'views_cam35'; V.mkdir(exist_ok=True)
names=['s','se','e','ne','n']; sheet=Image.new('RGB',(5*160*4,2*180*4),(128,128,128)); draw=ImageDraw.Draw(sheet)
for row,folder in enumerate([P.parent/'views',P/'slices']):
 for col,d in enumerate(names):
  im=Image.open(folder/f'{d}.png').convert('RGBA'); sheet.paste(im.resize((640,640),Image.Resampling.NEAREST),(col*640,row*720+50),im.resize((640,640),Image.Resampling.NEAREST)); draw.text((col*640+20,row*720+15),('approved ' if row==0 else 'cam35 ')+d,fill='white',font_size=24)
  if row: shutil.copyfile(folder/f'{d}.png',V/f'{d}.png')
sheet.save(P/'review.png')
e=Image.open(P/'slices/e.png'); e.crop(e.getbbox()).resize((850,510),Image.Resampling.NEAREST).save(P/'east-inspect.png')
