import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
import verify as a
R=a.R;b=a.b;load=a.load
Z=json.loads((R/'verification.json').read_text());rig=json.loads((R/'rig.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
extra={}
for v in ['e','se','ne']:
 ref=load(R/f'stills/{v}.png');box={'e':(67,130,145,162),'se':(48,98,103,156),'ne':(101,99,151,147)}[v];w=(box[2]-box[0])*5;h=(box[3]-box[1])*5
 board=Image.new('RGB',(w*9,h+28),(66,74,70));dr=ImageDraw.Draw(board)
 for j in range(9):
  im=ref.copy() if j==0 else load(R/f'walk/frames/{v}_f{j-1}.png')
  if j:
   for x,y in Z[v]['structure'][j-1]['seams']:im[y,x]=(255,60,70,255)
  tile=Image.fromarray(im).crop(box).resize((w,h),Image.Resampling.NEAREST);base=Image.new('RGBA',tile.size,(66,74,70));base.alpha_composite(tile);board.paste(base.convert('RGB'),(j*w,28));dr.text((j*w+4,3),v+' '+('still' if not j else f'f{j-1}'),font=font,fill='white')
 board.save(R/f'{v}_seams_review.png')
 for j in range(3):board.crop((j*3*w,0,(j+1)*3*w,h+28)).save(R/f'{v}_seams_part{j}.png')
 old=Image.open(R/f'{v}_footprints.png').convert('RGB');pic=Image.new('RGB',(2020,old.height),(60,70,65));pic.paste(old);d=ImageDraw.Draw(pic)
 for j,n in enumerate(['R3','R2','R1','L3','L2','L1']):
  src=load(R/f'source/{v}_{n}_foot.png');ys,xs=np.where(src[:,:,3]>0);sy=ys.max();keep=ys>=sy-1;ys=ys[keep];xs=xs[keep];track=Z[v]['feet'][n];step=np.array(a.T['views'][v]['planted_step_px']);anchor=np.array(next(q for q in rig[v] if q['foot']==n)['source_sole']);order=track['planted_order'];origin=anchor+np.array(track['frames'][order[0]]['delta']);oy=j*230
  d.text((1605,oy+4),'Ground-corrected sole pixels, 8x',font=font,fill='white')
  for k,f in enumerate(order):
   delta=np.array(track['frames'][f]['delta']);points=np.stack([xs,ys],1)+delta-k*step-origin;colour=['#ffb575','#75e5cf','#e99fe2','#c9e978'][k]
   for x,y in points:
    px=int(round(1790+x*8));py=int(round(oy+100+y*8));d.rectangle((px,py,px+7,py+7),outline=colour,width=2)
   d.text((1605+k%2*190,oy+157+k//2*24),f'f{f}: {colour}',fill=colour,font=font)
 pic.save(R/f'{v}_footprints.png')
 extra[v]={'claw_diff':[],'tail_diff':[],'foot_below_source_row':{},'near_projected_length_change':{}}
 for f in range(8):
  fr=load(R/f'walk/frames/{v}_f{f}.png');dip=int(f in [0,4])
  for p in ['claws','tail']:
   source=b.shift(load(R/f'source/{v}_{p}.png'),0,dip);mm=source[:,:,3]>0;extra[v]['claw_diff' if p=='claws' else 'tail_diff'].append(int(np.any(fr[mm]!=source[mm],axis=1).sum()))
 for n in ['R3','R2','R1']:
  extra[v]['foot_below_source_row'][n]=[int(q['delta'][1]) for q in rig[v] if q['foot']==n]
  extra[v]['near_projected_length_change'][n]=[round(q['projected_length_change'],3) for q in rig[v] if q['foot']==n]
(R/'additional_checks.json').write_text(json.dumps(extra,indent=2));print(json.dumps(extra,indent=1))
