from pathlib import Path
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent
a=np.array(Image.open(P/'sheet_raw.png').convert('RGBA')); h,w=a.shape[:2]
m=~((a[:,:,0]>190)&(a[:,:,1]<85)&(a[:,:,2]>185))
for d,r,c in [('s',2,1),('n',0,1),('e',1,0)]:
 y,x=np.where(m[r*h//3:(r+1)*h//3,c*w//3:(c+1)*w//3]); print(d, int(x.ptp()+1) if hasattr(x,'ptp') else int(np.ptp(x)+1),int(np.ptp(y)+1))
s=m[2*h//3:,w//3:2*w//3]; e=m[h//3:2*h//3,:w//3]
ratio=(np.where(e)[1].max()-np.where(e)[1].min()+1)/(np.where(s)[1].max()-np.where(s)[1].min()+1)
text=f'Raw east length / south width = {ratio:.4f}; reference 1.71; '+('MISS under 1.60' if ratio<1.60 else 'not under 1.60')
(P/'raw-ratio.txt').write_text(text); print(text)
