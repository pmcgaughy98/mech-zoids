from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent
out=Image.new('RGBA',(3*768,768),(65,73,70))
for j,v in enumerate(['e','se','ne']):
 im=Image.open(R/f'source/{v}_body.png');out.alpha_composite(im.resize((768,768),Image.Resampling.NEAREST),(j*768,0))
out.convert('RGB').save(R/'body_review.png')
