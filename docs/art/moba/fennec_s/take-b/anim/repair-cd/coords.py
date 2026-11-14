import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).parent))
from repair import *
for m,v,i in [('walk','se',0),('walk','ne',0),('sand_kick','ne',1),('sand_kick','se',2),('ear_burst','ne',3),('dig','se',1),('dig','ne',1),('dig','ne',2),('pop_out','ne',1),('death','se',1),('sonic_boom','ne',2),('sonic_boom','se',1)]:
 im=Image.open(files(m,v)[i]).convert('RGBA'); k=10;box=(65,105,145,162)
 t=im.crop(box).resize((800,570),Image.Resampling.NEAREST);bg=Image.new('RGBA',(850,620),'#454953');bg.alpha_composite(t,(40,30));d=ImageDraw.Draw(bg)
 for x in range(65,146,5):
  xx=40+(x-65)*k;d.line((xx,30,xx,600),fill='#626671');d.text((xx,10),str(x),fill='white')
 for y in range(105,163,5):
  yy=30+(y-105)*k;d.line((40,yy,840,yy),fill='#626671');d.text((2,yy),str(y),fill='white')
 bg.save(OUT/f'coords-{m}-{v}-{i}.png')
