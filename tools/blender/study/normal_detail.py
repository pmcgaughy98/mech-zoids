# Surface-detail strength of a normal map at three scales: the mean gradient of its red and green channels (x10)
# after resizing to 1024, 512 and 256 px. Pixel speckle only shows at 1024; panel seams, rivets and plate edges
# survive to 256. A finished map holds its number as the scale drops; a noisy one collapses.
import sys
import numpy as np
from PIL import Image
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    out = []
    for n in (1024, 512, 256):
        a = np.asarray(im.resize((n, n), Image.LANCZOS), dtype=np.float32)[:, :, :2] / 255.0
        out.append((np.abs(np.diff(a, axis=0)).mean() + np.abs(np.diff(a, axis=1)).mean()) * 10)
    print("DETAIL 1024 %.3f  512 %.3f  256 %.3f  %s" % (out[0], out[1], out[2], p.split("/")[-1]))
