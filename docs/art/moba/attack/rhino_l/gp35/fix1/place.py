"""Adapted run1 placement: whole-frame translations; no part edits."""
import json
import numpy as np
from PIL import Image
from finish import P,regions,NAMES,note
H={'e':[(27,96,49,106),(26,96,48,106),(27,96,49,106)],'se':[(26,83,50,94),(26,86,50,100),(26,86,50,100)]}
F={'e':[[(62,96,84,106)],[(68,83,91,94)],[(73,65,96,74)]],'se':[[(47,98,70,110),(76,96,103,105)],[(62,81,85,91),(81,70,100,81)],[(62,62,84,73),(82,53,100,65)]]}
def sole(a,box):
 x0,y0,x1,y1=box;m=a[y0:y1,x0:x1,3]>0;yy,xx=np.where(m);y=int(yy.max());xs=np.where(m[y])[0];return [float((xs.min()+xs.max())/2+x0),int(y+y0)]
if __name__=='__main__':
 im=Image.open(P/'sheet_finished.png');targets=json.loads((P/'targets.json').read_text());rec={};moves=[];(P/'frames').mkdir(exist_ok=True)
 for k,box in enumerate(regions(*im.size)):
  v=NAMES[k//3];col=k%3;a=np.array(im.crop(box));hs=sole(a,H[v][col]);fs=[sole(a,b) for b in F[v][col]];t=next(s for s in targets['views'][v]['soles'] if s['leg']=='hind');trans=np.rint(np.array([t['x'],t['y']])-hs).astype(int)
  canvas=Image.new('RGBA',(192,192));canvas.paste(Image.fromarray(a),tuple(trans));name=f'{v}_f{col+1}'
  entry={'column':col+1,'translation':trans.tolist(),'hind':(np.array(hs)+trans).tolist(),'front':(np.array(fs)+trans).tolist(),'foot_boxes':{'hind':H[v][col],'front':F[v][col]},'method':'Visually traced steel foot pads; lowest opaque dark sole row midpoint within boxes; E only near front is visible.'}
  rec[name]=entry
  if col:
   canvas.save(P/'frames'/f'{name}.png');moves.append(f'{name} ({trans[0]:+d},{trans[1]:+d})')
 (P/'placement.json').write_text(json.dumps({'frames':rec,'moves':moves},indent=2));note('Step 3 complete: four 192x192 frames, whole-frame translations '+', '.join(moves)+'; column 1 not saved as a frame.');print(json.dumps(rec,indent=2))
