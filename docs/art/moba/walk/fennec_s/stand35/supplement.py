from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage
P=Path('D:/dev/new-mech-rpg/docs/art/moba/walk/fennec_s/stand35'); T=Path('D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b')
N=['s','se','e','ne','n']
old=[T/'anim/codex-set-a/walk/frames/front_f0.png',T/'anim/codex-set-c/walk/frames/se_f0.png',T/'anim/codex-set-a/walk/frames/side_f0.png',T/'anim/codex-set-c/walk/frames/ne_f0.png',T/'anim/codex-set-a/walk/frames/back_f0.png']
board=Image.new('RGB',(1200,900),(128,128,128)); d=ImageDraw.Draw(board)
for row,(tag,paths) in enumerate([('seated 35',[T/'views_cam35_touchup'/f'{n}.png' for n in N]),('standing 35',[P/'slices'/f'{n}.png' for n in N]),('old trot low camera',old)]):
 for col,(n,path) in enumerate(zip(N,paths)):
  im=Image.open(path).convert('RGBA'); im=im.crop(im.getbbox()); im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST)
  board.paste(im,(col*240+(240-im.width)//2,row*300+290-im.height),im); d.text((col*240+6,row*300+5),f'{tag} {n} (3x)',fill='white')
board.save(P/'review.png')
board=Image.new('RGB',(1200,430),(128,128,128)); d=ImageDraw.Draw(board)
for col,n in enumerate(['n','ne','e']):
 im=Image.open(P/'slices'/f'{n}.png').convert('RGBA'); box=im.getbbox(); x0,y0,x1,y1=box; y0=(y0+y1)//2
 crop=im.crop((x0,y0,x1,y1)); crop=crop.resize((crop.width*5,crop.height*5),Image.Resampling.NEAREST); board.paste(crop,(col*400+20,40),crop); d.text((col*400+20,10),f'{n}: lower half, 5x nearest; rows {y0}-{y1-1}',fill='white')
board.save(P/'tail_legs_zoom.png')
board=Image.new('RGB',(1600,640),(128,128,128)); d=ImageDraw.Draw(board)
for col,n in enumerate(N):
 im=Image.open(P/'slices'/f'{n}.png').convert('RGBA'); crop=im.crop((40,100,120,145)); crop=crop.resize((320,180),Image.Resampling.NEAREST); board.paste(crop,(col*320,40),crop)
 for x in range(40,120,5):
  d.line((col*320+(x-40)*4,40,col*320+(x-40)*4,220),fill=(90,90,90)); d.text((col*320+(x-40)*4,225),str(x),fill='white')
 for y in range(100,145,5):
  d.line((col*320,40+(y-100)*4,col*320+320,40+(y-100)*4),fill=(90,90,90)); d.text((col*320,40+(y-100)*4),str(y),fill='white')
 d.text((col*320,10),n,fill='white')
 a=np.array(im); steel=(a[...,3]>0)&((a[...,:3]==(214,214,220)).all(2)|(a[...,:3]==(157,155,162)).all(2)); steel[:120]=False
 lab,k=ndimage.label(steel,np.ones((3,3)))
 print(n,'steel components below y120:')
 for k1 in range(1,k+1):
  yy,xx=np.where(lab==k1)
  if len(xx)>=3: print((int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())),len(xx))
board.save(P/'measurement.png')
