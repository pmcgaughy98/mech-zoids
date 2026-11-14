from finish import *
for name in TIMES:
 for v in V:
  b=Image.new('RGB',(520,len(TIMES[name])*392),'#596159');d=ImageDraw.Draw(b)
  for i in range(len(TIMES[name])):
   im=Image.open(R/name/'frames'/f'{v}_f{i}.png');bg=Image.new('RGBA',(192,192),'#596159');bg.alpha_composite(im)
   tile=bg.crop((30,68,160,166)).resize((520,392),Image.Resampling.NEAREST);b.paste(tile,(0,i*392));d.text((4,i*392+12),f'{name} {v} f{i}',fill='white')
   for x in range(40,160,5):d.line(((x-30)*4,i*392,(x-30)*4,i*392+391),fill='#777c77');d.text(((x-30)*4,i*392+2),str(x),fill='white')
   for y in range(75,165,5):d.line((0,i*392+(y-68)*4,520,i*392+(y-68)*4),fill='#777c77');d.text((0,i*392+(y-68)*4),str(y),fill='white')
  b.save(R/name/f'measurement_{v}.png')
