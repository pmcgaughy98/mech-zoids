from finish import *
for name in TIMES:
 b=Image.new('RGB',(1200,len(TIMES[name])*340),'#596159');d=ImageDraw.Draw(b)
 for i in range(len(TIMES[name])):
  im=Image.open(R/name/'frames'/f'side_f{i}.png');bg=Image.new('RGBA',(192,192),'#596159');bg.alpha_composite(im);tile=bg.crop((30,80,160,165)).resize((780,510),Image.Resampling.NEAREST)
  # 4x native display, grid every 5 native pixels.
  tile=bg.crop((30,80,160,165)).resize((520,340),Image.Resampling.NEAREST);b.paste(tile,(0,i*340));d.text((530,i*340+10),f'{name} side f{i}',fill='white')
  for x in range(40,160,10):d.line(((x-30)*4,i*340,(x-30)*4,i*340+339),fill='#777c77');d.text(((x-30)*4,i*340+2),str(x),fill='white')
  for y in range(90,165,10):d.line((0,i*340+(y-80)*4,520,i*340+(y-80)*4),fill='#777c77');d.text((0,i*340+(y-80)*4),str(y),fill='white')
 b.crop((0,0,670,b.height)).save(R/name/'measurement_side.png')
