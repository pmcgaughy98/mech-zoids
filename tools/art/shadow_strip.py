# The pixelizer draws a flat ground-shadow line (two rows, one colour each) under a sprite's feet. It is not part of
# the creature, and under spread legs it runs wide enough to skew outline scores (found 2026-10-13 on the wolf).
# strip(im): the sprite cropped to its alpha box, with that shadow line removed.
import numpy as np
from PIL import Image


def strip(im):
    im = im.crop(im.getchannel("A").getbbox())
    a = np.array(im)
    for _ in range(3):
        row = a[-1]
        on = row[:, 3] > 128
        if on.sum() < 10:
            break
        idx = np.flatnonzero(on)
        if idx[-1] - idx[0] + 1 != len(idx):   # not one unbroken run
            break
        cols = {tuple(c) for c in row[on][:, :3]}
        if len(cols) > 1:
            break
        a = a[:-1]
    out = Image.fromarray(a, "RGBA")
    return out.crop(out.getchannel("A").getbbox())
