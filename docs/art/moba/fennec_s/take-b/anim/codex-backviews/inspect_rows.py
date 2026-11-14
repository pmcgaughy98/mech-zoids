from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import importlib.util
R=Path(r'D:\dev\new-mech-rpg\docs\art\moba\fennec_s\take-b\anim\codex-backviews')
spec=importlib.util.spec_from_file_location('sel',r'D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py');sel=importlib.util.module_from_spec(spec);spec.loader.exec_module(sel)
b=Image.new('RGBA',(9*272,4*424),(85,91,83,255));d=ImageDraw.Draw(b)
for j,(move,v,N) in enumerate([('walk','back',8),('walk','ne',8),('sand_kick','back',6),('sand_kick','ne',6)]):
 ref=Image.new('RGBA',(192,192));ref.paste(Image.open(R.parent.parent/'views'/('n.png' if v=='back' else 'ne.png')),(16,20))
 ims=[ref]+[Image.open(R.parent/('codex-set-a' if v=='back' else 'codex-set-c')/move/'frames'/f'{v}_f{i}.png').convert('RGBA') for i in range(N)]
 d.text((4,j*424+3),move+' '+v+' / approved then live f0...',fill='white')
 for i,im in enumerate(ims):
  a=sel.selout(np.array(im))[0];b.alpha_composite(Image.fromarray(a).crop((62,80,130,180)).resize((272,400),Image.Resampling.NEAREST),(i*272,j*424+24))
b.convert('RGB').save(R/'before_board.png')

