from PIL import Image,ImageDraw
from pathlib import Path
R=Path(r'D:/dev/new-mech-rpg/docs/art/moba/wolf_m/take-b/anim/codex-walk2')
board=Image.new('RGBA',(9*320,336),(75,80,80,255));d=ImageDraw.Draw(board)
for f in range(-1,8):
 im=Image.open(R.parent.parent/'fixed/e.png' if f<0 else R/'walk/frames'/f'side_f{f}.png').convert('RGBA');board.alpha_composite(im.crop((112,92,152,132)).resize((320,320),Image.Resampling.NEAREST),((f+1)*320,16));d.text(((f+1)*320+3,2),'STILL' if f<0 else str(f),fill='white')
board.convert('RGB').save(R/'head_details.png')
