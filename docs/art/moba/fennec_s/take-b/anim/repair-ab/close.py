from repair import *
for m,d in MOVES.items():
 for v in VIEWS:
  fs=files(m,v);b=Image.new('RGB',(1200,((len(fs)+2)//3)*520),'#737980');dr=ImageDraw.Draw(b)
  for i,p in enumerate(fs):
   a=Image.fromarray(selout(np.array(Image.open(p).convert('RGBA')))[0]);bg=Image.new('RGBA',(192,192),'#737980');bg.alpha_composite(a)
   box=(48,62,148,162) if v!='side' else (32,62,152,162)
   im=bg.crop(box).resize((400 if v!='side' else 480,400),Image.Resampling.NEAREST)
   # side uses 3x scale to fit; all detail boards use 4x minimum elsewhere
   if v=='side':im=bg.crop((32,62,152,162)).resize((400,400),Image.Resampling.NEAREST)
   x=i%3*400;y=i//3*520;b.paste(im.convert('RGB'),(x,y+24));dr.text((x+4,y+4),f'{m} {v} f{i}',fill='white')
  b.save(OUT/f'close-{m}-{v}.png')
