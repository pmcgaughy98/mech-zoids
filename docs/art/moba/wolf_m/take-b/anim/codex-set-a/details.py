"""Direct native-pixel flattened sprint ear correction; no reference image sampling."""
from polish import *
records=[]
# True profile sprint ears, same intrinsic lengths but folded to trail backwards.
for i in range(6):
 path=R/'sprint/frames'/f'side_f{i}.png';im=Image.open(path).convert('RGBA');a=np.array(im);g=(a[:,:,3]>0)&np.all(a[:,:,:3]==PAL[8],2);ey,ex=np.where(g);x=round(ex.mean());y=round(ey.mean());yy,xx=np.indices((192,192))
 # Original upright ear tips are completely removed, retaining the sloping hood below.
 erase=(xx>=x-21)&(xx<=x+1)&(yy<y-6);a[erase]=0;im=Image.fromarray(a);p=Pen(im)
 p.p([(x-20,y-7),(x-14,y-10),(x-5,y-6),(x+1,y-3),(x-8,y-3)],4)
 p.p([(x-11,y-7),(x-25,y-12),(x-23,y-8),(x-18,y-4),(x-12,y-2),(x-8,y-3)],0)
 p.p([(x-12,y-7),(x-23,y-11),(x-21,y-8),(x-16,y-5),(x-10,y-3)],4)
 p.l([(x-23,y-11),(x-17,y-8),(x-11,y-6)],6)
 p.p([(x-5,y-6),(x-20,y-14),(x-19,y-10),(x-14,y-6),(x-7,y-3),(x-3,y-3)],0)
 p.p([(x-6,y-6),(x-18,y-12),(x-17,y-9),(x-12,y-6),(x-6,y-4)],4)
 p.l([(x-19,y-13),(x-13,y-10),(x-6,y-6)],9)
 clean(im).save(path)
 records.append({'move':'sprint','view':'side','frame':i,'ear_axis_landmarks':[[[x-25,y-12],[x-12,y-3]],[[x-20,y-14],[x-5,y-5]]],'method':'complete removal of upright tips and direct native-pixel folded contour repaint, joined to hood'})
(R/'detail_edits.json').write_text(json.dumps(records,indent=2)+'\n')
finalize('sprint')
