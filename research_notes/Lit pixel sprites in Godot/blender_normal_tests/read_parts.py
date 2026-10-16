import os, sys, json
import numpy as np
import OpenImageIO as oiio
d = sys.argv[sys.argv.index("--") + 1]
res = {}
for f in sorted(os.listdir(d)):
    if not f.endswith(".exr"):
        continue
    p = os.path.join(d, f)
    inp = oiio.ImageInput.open(p)
    parts = []
    i = 0
    while inp.seek_subimage(i, 0):
        spec = inp.spec()
        names = list(spec.channelnames)
        entry = {"part": spec.getattribute("name"), "channels": names}
        nidx = [k for k, n in enumerate(names) if "Normal" in n or n in ("X", "Y", "Z") and "Normal" in str(spec.getattribute("name"))]
        if nidx:
            px = np.array(inp.read_image(i, 0, 0, spec.nchannels, "float")).reshape(spec.height, spec.width, spec.nchannels)
            H = spec.height
            pick = lambda r, c: [round(float(px[r, c, k]), 3) for k in nidx]
            entry.update({"center": pick(H // 2, H // 2), "top(screen up)": pick(int(H * 0.19), H // 2), "right(screen right)": pick(H // 2, int(H * 0.81))})
        parts.append(entry)
        i += 1
    inp.close()
    res[f] = parts
print("RESULT_JSON " + json.dumps(res))
