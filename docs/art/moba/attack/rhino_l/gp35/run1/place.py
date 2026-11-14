"""Whole-frame placement only, based on visually labelled foot-pad boxes."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as nd
from finish import regions,NAMES,P,TAKE,note
# Boxes include the complete steel pad and dark sole, excluding jaw and joints.
H={
'e': [[(20,94,46,110)],[(20,94,46,110)],[(20,94,46,110)],[(21,94,47,110)],[(20,94,47,110)],[(20,94,46,110)]],
'se':[[(17,78,39,93)],[(18,78,40,93)],[(19,81,41,96)],[(19,81,42,96)],[(18,78,40,93)],[(17,79,40,94)]],
'ne':[[(38,97,63,109),(18,86,42,99)],[(36,96,62,109),(18,86,44,99)],[(36,94,60,107),(18,86,39,100)],[(34,94,59,108),(18,86,39,99)],[(36,96,62,109),(19,86,43,100)],[(35,94,60,108),(18,86,39,100)]]}
F={
'e':[[(59,95,87,110)],[(58,95,86,110)],[(69,79,93,94)],[(70,59,94,74)],[(59,95,84,110)],[(58,94,83,108)]],
'se':[[(42,93,68,106),(75,87,104,96)],[(42,93,68,106),(74,88,100,97)],[(57,74,82,89),(80,56,103,68)],[(54,56,78,72),(85,45,102,54)],[(43,93,69,106),(76,89,105,98)],[(44,90,70,104),(77,82,104,91)]],
'ne':[[(75,85,98,99)],[(75,86,96,99)],[(74,69,94,81)],[(82,38,98,56)],[(74,86,96,99)],[(74,75,94,87)]]}
def sole(a,box):
 x0,y0,x1,y1=box; m=a[y0:y1,x0:x1,3]>0; yy,xx=np.where(m)
 y=int(yy.max()); xs=np.where(m[y])[0]
 # Outermost row midpoint, explicitly including the dark pad sole.
 return [float((xs.min()+xs.max())/2+x0),int(y+y0)]
def shifted(p,t):return [float(p[0]+t[0]),int(p[1]+t[1])]
if __name__=='__main__':
 im=Image.open(P/'sheet_finished.png'); targets=json.loads((P/'targets.json').read_text()); dest=P/'frames';dest.mkdir(exist_ok=True)
 rec={}; moves=[]; dbg=Image.new('RGB',(6*384,3*400),(100,100,100));draw=ImageDraw.Draw(dbg)
 for k,box in enumerate(regions(*im.size)):
  v=NAMES[k//6];i=k%6;a=np.array(im.crop(box)); 
  if v=='ne': H[v][i][1]=(18,84,37,98)
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
 (P/'placement.json').write_text(json.dumps({'frames':rec,'moves':moves},indent=2));dbg.save(P/'feet_measured.png');note('Step 3 complete: 18 frames on 192 canvases, exact still f0; whole-frame corrections '+', '.join(moves));print('moves',moves)
 for key,r in rec.items():print(key,'hind',r['hind'],'front',r['front'],'offset',r['translation'])
