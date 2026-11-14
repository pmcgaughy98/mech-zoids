"""Angle guide for drawing a machine from the game camera (sprite factory lane, Claude, 2026-11-04).

A plain solid with an elliptic footprint (length x width) and a flat top at height H, drawn at PITCH degrees above level in
the five drawn views (s, se, e, ne, n), on magenta, at 4x. The green-tinted side is the machine's front.
It shows Codex how much top shows and how far the sides foreshorten; it is not a design and must not be copied.
An elliptic footprint fits the approved diagonal widths far better than a box (drone se: box 91 px, ellipse 64, drawn 62).
Prints each view's guide width and height in texels, used for the height check.
Usage: python angle_guide.py L W H out.png [pitch]
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw

L, W, H = (float(x) for x in sys.argv[1:4])
OUT = sys.argv[4]
PITCH = float(sys.argv[5]) if len(sys.argv) > 5 else 35.0
HEAD = {"s": 180, "se": 135, "e": 90, "ne": 45, "n": 0}  # compass heading the machine faces; camera is south
K, PAD, GAP, N = 4, 24, 48, 96
pr = math.radians(PITCH)
tocam = np.array([0.0, -math.cos(pr), math.sin(pr)])  # (east, north, up)


def frame(h):
    hr = math.radians(h)
    return np.array([math.sin(hr), math.cos(hr), 0.0]), np.array([-math.cos(hr), math.sin(hr), 0.0])


def screen(p):  # world (east, north, up) -> (sx, sy up)
    return np.array([p[0], p[2] * math.cos(pr) + p[1] * math.sin(pr)])


panels, sizes = [], {}
for v, h in HEAD.items():
    F, Lv = frame(h)
    t = np.linspace(0, 2 * math.pi, N, endpoint=False)
    ring = [(L / 2 * math.cos(a)) * F + (W / 2 * math.sin(a)) * Lv for a in t]
    bot = [screen(p) for p in ring]
    top = [screen(p + np.array([0, 0, H])) for p in ring]
    pts = np.array(bot + top)
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    w, hh = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
    sizes[v] = (round(w), round(hh))
    img = Image.new("RGB", (int(math.ceil(w * K)) + 2 * PAD, int(math.ceil(hh * K)) + 2 * PAD), (255, 0, 255))
    d = ImageDraw.Draw(img)
    px = lambda s: ((s[0] - x0) * K + PAD, (hh - (s[1] - y0)) * K + PAD)
    for i, a in enumerate(t):  # side quads that face the camera
        j = (i + 1) % N
        am = a + math.pi / N
        nrm = (math.cos(am) / (L / 2)) * F + (math.sin(am) / (W / 2)) * Lv
        nrm /= np.linalg.norm(nrm)
        facing = float(nrm @ tocam)
        if facing <= 0:
            continue
        front = math.cos(am) > math.cos(math.radians(40))
        g = int(110 + 70 * facing)
        col = (g - 30, g + 25, g - 40) if front else (g, g, g + 6)
        d.polygon([px(bot[i]), px(bot[j]), px(top[j]), px(top[i])], fill=col)
    d.polygon([px(s) for s in top], fill=(224, 224, 230), outline=(40, 40, 48), width=3)
    panels.append(img)

Wt = sum(i.width for i in panels) + GAP * (len(panels) - 1) + 2 * PAD
Ht = max(i.height for i in panels) + 2 * PAD
sheet = Image.new("RGB", (Wt, Ht), (255, 0, 255))
x = PAD
for i in panels:
    sheet.paste(i, (x, Ht - PAD - i.height))
    x += i.width + GAP
sheet.save(OUT)
print("guide at", PITCH, "deg, L W H", L, W, H, "(W x H texels):", sizes)
