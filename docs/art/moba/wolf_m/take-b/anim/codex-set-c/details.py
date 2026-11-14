"""Native whole-cell fields adapted from A's bite paw and tail finishing."""
from polish import *
records=[]
# Source/destination inclusive contact spans, read at native scale.
K={
'se':{
1:([0,55,59,68,78,81,92,97,109,112,124,191],[0,54,58,67,77,81,91,98,110,114,125,191]),
2:([0,54,58,67,77,80,90,96,108,111,123,191],[0,54,58,67,77,81,91,98,110,114,125,191]),
3:([0,56,60,69,79,82,92,97,109,112,124,191],[0,54,58,67,77,81,91,98,110,114,125,191])},
'ne':{
1:([0,60,71,72,83,86,98,99,107,114,125,191],[0,57,72,73,83,87,99,100,108,116,127,191]),
2:([0,57,69,70,80,83,95,96,105,112,123,191],[0,57,72,73,83,87,99,100,108,116,127,191]),
3:([0,60,71,72,83,86,98,99,107,114,126,191],[0,57,72,73,83,87,99,100,108,116,127,191])}}
for v in VIEWS:
 for i in [1,2,3]:
  im=native_finish('bite',v,i);a=np.array(im);yy,xx=np.indices((192,192));source,dest=K[v][i]
  weight=np.clip((yy-125)/25,0,1);sx=np.rint(xx*(1-weight)+np.interp(xx,dest,source)*weight).astype(int);b=a[yy,np.clip(sx,0,191)]
  clean(Image.fromarray(b)).save(R/'bite/frames'/f'{v}_f{i}.png')
  records.append(dict(move='bite',view=v,frame=i,source_x_knots=source,destination_x_knots=dest,method='whole lower-drawing coordinate field for fixed paw spans; no parts pasted'))
(R/'detail_edits.json').write_text(json.dumps(records,indent=2)+'\n')
finalize('bite')

# Remove off-material ivory speckles from metal, retaining ivory only on the two fangs.
for n in TIMES:
 for v in VIEWS:
  for i in range(len(TIMES[n])):
   if exact(n,i):continue
   path=R/n/'frames'/f'{v}_f{i}.png';a=np.array(Image.open(path));yy,xx=np.indices((192,192))
   # Metal can use silver but never the tusk ivory. Fangs are always at the far-right head silhouette.
   ivory=np.all(a[:,:,:3]==PAL[10],2)|np.all(a[:,:,:3]==PAL[11],2)
   allowed=(xx>=120) if v=='se' else (xx>=122)
   edited=ivory&~allowed&(a[:,:,3]>0);a[edited,:3]=PAL[9]
   Image.fromarray(a).save(path)
   records.append(dict(move=n,view=v,frame=i,material_speckles_recoloured=int(edited.sum())))
(R/'detail_edits.json').write_text(json.dumps(records,indent=2)+'\n')
for n in TIMES:finalize(n)
