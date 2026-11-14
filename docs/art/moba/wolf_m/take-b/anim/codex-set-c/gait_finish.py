"""Adapted A whole-drawing field correction. No mirrored camera or pasted still parts."""
from polish import *
records=[]
# Small foot field corrections retain the generated paw contour; stronger field and
# contour trials were rejected on visual review because they pinched the feet.
XK={'se':[[72,84,102,125],[75,90,103,119],[77,84,107,120],[78,88,109,120],[72,88,109,121],[79,83,101,121],[75,91,107,123],[77,91,109,122]],
'ne':[[78,94,104,124],[78,92,104,121],[84,89,111,121],[85,91,110,120],[77,89,106,121],[81,87,99,120],[77,89,106,120],[77,90,103,121]]}
TARGET={'se':[72,86,104,120],'ne':[78,93,103,122]}
for v in VIEWS:
 for i in range(8):
  im=native_finish('walk',v,i);a=np.array(im);yy,xx=np.indices((192,192));w=np.clip((yy-132)/22,0,1)
  # Limit corrections to two texels: retain each complete source drawing's limbs.
  sxnodes=XK[v][i];dxnodes=[x+int(np.clip(t-x,-2,2)) for x,t in zip(sxnodes,TARGET[v])]
  xs=[0,64 if v=='se' else 73]+dxnodes+[191];ss=[0,64 if v=='se' else 73]+sxnodes+[191]
  sx=np.rint(xx*(1-w)+np.interp(xx,xs,ss)*w).astype(int)
  b=a[yy,np.clip(sx,0,191)];clean(Image.fromarray(b)).save(R/'walk/frames'/f'{v}_f{i}.png')
  records.append(dict(view=v,frame=i,source_centres=sxnodes,corrected_centres=dxnodes,maximum_coordinate_correction=2,mirrored=False,support_gate='NOT PASSED: generated support phases and clearances remain inconsistent; correction intentionally limited to avoid pinched anatomy'))
(R/'support_edits.json').write_text(json.dumps(records,indent=2)+'\n')
finalize('walk')
