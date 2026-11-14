from finish import *
b=Image.new('RGBA',(3200,420),(82,89,81,255));d=ImageDraw.Draw(b)
for i in range(8):
 im=Image.open(R.parent/'codex-set-a/walk/frames'/f'side_f{i}.png').convert('RGBA');out=Image.fromarray(sel.selout(np.array(im))[0]);b.alpha_composite(out.crop((48,78,148,176)).resize((400,392),Image.Resampling.NEAREST),(i*400,24));d.text((i*400+4,4),f'SIDE trot f{i}',fill='white')
b.convert('RGB').save(R/'side_beats.png')
for i in range(2):b.crop((i*1600,0,(i+1)*1600,420)).convert('RGB').save(R/f'side_beats_{i}.png')
# Focus crops preserve 4x texels on a display-sized image.
for name in COUNTS:
 b=Image.open(R/name/'board.png');cw=304;ch=376
 out=Image.new('RGB',(4*cw,4*ch),(82,89,81))
 for j in range(4):
  for k,c in enumerate([0,1,3,4]):out.paste(b.crop((c*cw,j*ch,(c+1)*cw,(j+1)*ch)),(k*cw,j*ch))
 out.save(R/name/'focus.png')
