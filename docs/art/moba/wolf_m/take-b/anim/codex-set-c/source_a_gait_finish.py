"""Whole-drawing coordinate corrections for walk support. No pasted reference parts."""
from polish import *
records=[]
for v in ['front','back']:
 for i in range(8):
  source=i if i<4 else i-4
  im=walk_finish(v,source);a=np.array(im)
  if i>=4:a=a[:,::-1].copy()
  yy,xx=np.indices((192,192));sy=yy.astype(float);sx=xx.astype(float)
  lifts=([0,0,0,0,3,4,5,0][i],[3,4,5,0,0,0,0,0][i])
  zones=[(0,96,83,92),(96,192,100,109)] if v=='front' else [(0,91,78,87),(101,192,103,112)]
  rec=[]
  for side,(lo,hi,tx0,tx1) in enumerate(zones):
   m=a[:,:,3]>0;my,mx=np.where(m[:,lo:hi]&(np.indices(m[:,lo:hi].shape)[0]>=130));source_bottom=int(my.max());dest_bottom=160-lifts[side]
   region=(xx>=lo)&(xx<hi)&(yy>=128)
   ymap=128+(yy-128)*(source_bottom-128)/(dest_bottom-128)
   sy[region]=ymap[region]
   foot=(m)&(yy>=source_bottom-3)&(xx>=lo)&(xx<hi);fy,fx=np.where(foot);fx0=int(fx.min());fx1=int(fx.max())
   w=np.clip((yy-128)/26,0,1);xmap=(xx-tx0)*(fx1-fx0)/(tx1-tx0)+fx0;sx[region]=(xx*(1-w)+xmap*w)[region]
   rec.append(dict(source_foot_bottom=source_bottom,final_foot_bottom=dest_bottom,clearance=lifts[side],source_foot_span=[fx0,fx1],final_foot_span=[tx0,tx1]))
  sy=np.rint(sy).astype(int);sx=np.rint(sx).astype(int);valid=(sy>=0)&(sy<192)&(sx>=0)&(sx<192);b=np.zeros_like(a);b[valid]=a[sy[valid],sx[valid]];m=b[:,:,3]>0
  # Warp only the leg zones. Pixels below each lifted paw are cleared, rather than sampling empty gutters ambiguously.
  for side,(lo,hi,_,_) in enumerate(zones):b[161-lifts[side]:,lo:hi]=0
  clean(Image.fromarray(b)).save(R/'walk/frames'/f'{v}_f{i}.png')
  records.append(dict(view=v,frame=i,whole_generated_source_frame=source,mirror_whole_drawing=i>=4,legs=rec))
(R/'support_edits.json').write_text(json.dumps(records,indent=2)+'\n')
finalize('walk')
