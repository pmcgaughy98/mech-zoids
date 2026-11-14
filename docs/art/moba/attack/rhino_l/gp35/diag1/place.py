"""Whole-frame placement only, based on visually labelled foot-pad boxes."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from finish import regions,NAMES,P,TAKE,note
# Boxes include the complete steel pad and dark sole, excluding jaw and joints.
H={
'se':[[(18,69,42,83)],[(18,71,40,83)],[(18,69,43,83)],[(18,70,41,83)],[(18,72,41,84)],[(18,70,42,83)]],
'ne':[[(39,94,63,104),(18,83,38,96)],[(39,96,63,104),(18,83,38,96)],[(39,94,63,104),(18,81,38,94)],[(38,91,61,103),(18,81,38,94)],[(39,95,63,105),(18,84,38,96)],[(39,93,63,103),(18,81,38,94)]]}
F={
'se':[[(41,86,63,98),(71,85,94,94)],[(40,86,63,98),(73,87,95,95)],[(46,84,69,95),(77,77,97,84)],[(54,60,76,77),(77,50,101,65)],[(40,87,63,99),(73,89,95,98)],[(41,86,64,98),(76,81,97,90)]],
'ne':[[(73,77,89,87)],[(73,79,89,88)],[(74,69,90,80)],[(77,47,94,60)],[(72,83,89,91)],[(73,72,90,83)]]}

def sole(a,box):
 x0,y0,x1,y1=box; m=a[y0:y1,x0:x1,3]>0; yy,xx=np.where(m)
 y=int(yy.max()); xs=np.where(m[y])[0]
 # Outermost row midpoint, explicitly including the dark pad sole.
 return [float((xs.min()+xs.max())/2+x0),int(y+y0)]
def shifted(p,t):return [float(p[0]+t[0]),int(p[1]+t[1])]
if __name__=='__main__':
 im=Image.open(P/f'sheet_finished_{NAMES[0]}.png'); targets=json.loads((P/'targets.json').read_text()); dest=P/'frames';dest.mkdir(exist_ok=True)
 rec={}; moves=[]; dbg=Image.new('RGB',(6*384,400),(100,100,100));draw=ImageDraw.Draw(dbg)
 for k,box in enumerate(regions(*im.size)):
  v=NAMES[k//6];i=k%6;a=np.array(im.crop(box)); 
  hs=[sole(a,b) for b in H[v][i]]; fs=[sole(a,b) for b in F[v][i]]; ts=[[s['x'],s['y']] for s in targets['views'][v]['soles'] if s['leg']=='hind']
  # Row offset from column 1; subsequent correction uses only whole-frame translation.
  if i==0:
   rowoff=np.rint(np.median(np.subtract(ts,hs),axis=0)).astype(int);base=rowoff.copy()
  err=np.subtract(ts,np.add(hs,base)); correction=np.rint(np.median(err,axis=0)).astype(int)
  if np.max(np.abs(err))<=1:correction[:]=0
  trans=base+correction
  if np.any(correction):moves.append(f'{v}_f{i} ({correction[0]:+d},{correction[1]:+d})')
  canvas=Image.new('RGBA',(192,192));canvas.paste(Image.fromarray(a),tuple(trans));canvas.save(dest/f'{v}_f{i}.png')
  rec[f'{v}_f{i}']={'cell_box':box,'row_offset':base.tolist(),'correction':correction.tolist(),'translation':trans.tolist(),'hind_cell':hs,'front_cell':fs,'hind':[shifted(s,trans) for s in hs],'front':[shifted(s,trans) for s in fs],'foot_boxes':{'hind':H[v][i],'front':F[v][i]},'method':'Visually identified steel foot pads; dark sole outermost row in labelled box; midpoint of occupied sole row. SE far pad partly overlaps jaw: position uncertain.'}
  z=canvas.resize((384,384),Image.Resampling.NEAREST);dbg.paste(z,(i*384,(k//6)*400+16),z);draw.text((i*384+4,(k//6)*400),f'{v} f{i}',fill='white')
  for tag,ps in [('H',rec[f'{v}_f{i}']['hind']),('F',rec[f'{v}_f{i}']['front'])]:
   for x,y in ps:
    x=i*384+x*2;y=(k//6)*400+16+y*2;draw.line((x-5,y,x+5,y),fill='cyan' if tag=='H' else 'red',width=1);draw.text((x,y+2),tag,fill='white')
 for v in NAMES:
  shutil.copyfile(TAKE/'views_cam35_touchup'/f'{v}.png',dest/f'{v}_f0.png')
  rec[f'{v}_f0']['hind']=[[s['x'],s['y']] for s in targets['views'][v]['soles'] if s['leg']=='hind'];rec[f'{v}_f0']['front']=[[s['x'],s['y']] for s in targets['views'][v]['soles'] if s['leg'].startswith('front')];rec[f'{v}_f0']['method']='Exact approved still; foot labels from supplied targets.json.'
 (P/f'placement_{NAMES[0]}.json').write_text(json.dumps({'frames':rec,'moves':moves},indent=2));dbg.save(P/f'feet_measured_{NAMES[0]}.png');note('Step 3 complete: 6 frames per row on 192 canvases, exact still f0; whole-frame corrections '+', '.join(moves));print('moves',moves)
 for key,r in rec.items():print(key,'hind',r['hind'],'front',r['front'],'offset',r['translation'])
