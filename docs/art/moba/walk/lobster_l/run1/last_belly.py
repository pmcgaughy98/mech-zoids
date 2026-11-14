from pathlib import Path
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent
body=np.array(Image.open(R/'source/se_body.png').convert('RGBA'));fill=np.array(Image.open(R/'source/se_body_reconstruction_area.png'))[:,:,3]>0
for x in range(58,77):
 yy=np.where(body[:,x,3]>0)[0]
 if len(yy):
  y=yy.max();z=y-np.interp(x,[57,77],[86,119])
  if z>1:print(x,y,z,fill[y,x],bytes(body[y,x,:3]).hex())
