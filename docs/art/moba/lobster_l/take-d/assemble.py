from pathlib import Path
from PIL import Image
import numpy as np, shutil
P=Path(__file__).resolve().parent; C=P.parent/'take-c'
shutil.copyfile(C/'sheet_finished.png',P/'sheet_finished.png')
a=Image.open(P/'sheet_finished.png').convert('RGBA'); b=Image.open(P/'sheet_edit_finished.png').convert('RGBA')
assert a.size==b.size
a.paste(b.crop((0,0,b.width,b.height//3)),(0,0))
a.save(P/'sheet_finished.png')
assert np.array_equal(np.array(a)[a.height//3:],np.array(Image.open(C/'sheet_finished.png').convert('RGBA'))[a.height//3:])
print('Only top row replaced; lower two rows pixel-identical to C.')
