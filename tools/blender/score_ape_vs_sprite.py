"""Score the gorilla against Preston's sprite (Claude, 2026-10-11). The build writes two renders from the sprite's rear
three-quarter angle (docs/art/3d/silhouette/rear34.png and rear34_color.png); this compares them with the sprite
(docs/art/ape-rd-2026-10-11/source_preston_pick.webp):
  - outline overlap (intersection over union) after both are cropped and scaled to the same height
  - colour split: share of green, grey/black and orange pixels, against the sprite's
  python tools/blender/score_ape_vs_sprite.py
Writes docs/art/3d/silhouette/rear34_compare.png (blue = sprite only, orange = model only, dark = both).
"""
import colorsys, os
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPRITE = os.path.join(ROOT, "docs", "art", "ape-rd-2026-10-11", "source_preston_pick.webp")
SIL = os.path.join(ROOT, "docs", "art", "3d", "silhouette")


def crop(mask):
    ys, xs = np.where(mask)
    return mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def fit(mask, h):
    w = max(1, int(mask.shape[1] * h / mask.shape[0]))
    return np.asarray(Image.fromarray(mask.astype("uint8") * 255).resize((w, h))) > 128


def colour_split(rgb, mask, ink=0.12):
    px = rgb[mask].reshape(-1, 3) / 255.0
    px = px[px.max(1) > ink]   # leave out ink lines darker than this
    hsv = np.array([colorsys.rgb_to_hsv(*p) for p in px[:: max(1, len(px) // 20000)]])
    h, s, v = hsv[:, 0] * 360, hsv[:, 1], hsv[:, 2]
    green = ((h > 60) & (h < 160) & (s > 0.2)).mean()
    orange = ((h > 10) & (h < 50) & (s > 0.35)).mean()
    grey = 1.0 - green - orange
    return green, grey, orange


def main():
    sprite = np.asarray(Image.open(SPRITE).convert("RGBA"))
    s_mask = sprite[:, :, 3] > 128
    model = np.asarray(Image.open(os.path.join(SIL, "rear34.png")).convert("L")) < 128
    H = 300
    a, b = fit(crop(model), H), fit(crop(s_mask), H)
    W = max(a.shape[1], b.shape[1])
    A = np.zeros((H, W), bool)
    B = np.zeros((H, W), bool)
    A[:, (W - a.shape[1]) // 2:(W - a.shape[1]) // 2 + a.shape[1]] = a
    B[:, (W - b.shape[1]) // 2:(W - b.shape[1]) // 2 + b.shape[1]] = b
    iou = (A & B).sum() / (A | B).sum()
    viz = np.full((H, W, 3), 255, "uint8")
    viz[B] = (80, 160, 255)
    viz[A] = (255, 140, 60)
    viz[A & B] = (40, 40, 40)
    Image.fromarray(viz).save(os.path.join(SIL, "rear34_compare.png"))
    colour = np.asarray(Image.open(os.path.join(SIL, "rear34_color.png")).convert("RGB"))
    m_split = colour_split(colour, model)
    s_split = colour_split(sprite[:, :, :3], s_mask)
    print("outline overlap %.3f | width/height model %.2f sprite %.2f" % (iou, a.shape[1] / H, b.shape[1] / H))
    print("colour split  green / grey+black / orange")
    print("  sprite      %.0f%% / %.0f%% / %.0f%%" % tuple(x * 100 for x in s_split))
    print("  model       %.0f%% / %.0f%% / %.0f%%" % tuple(x * 100 for x in m_split))
    # The sprite draws near-black ink between every plate; the flat render has none (the game adds it with its
    # outline shader). Paint to paint, both with everything darker than 0.2 left out:
    s2, m2 = colour_split(sprite[:, :, :3], s_mask, 0.2), colour_split(colour, model, 0.2)
    print("  paint only: sprite %.0f%% / %.0f%% / %.0f%%   model %.0f%% / %.0f%% / %.0f%%" % tuple(x * 100 for x in s2 + m2))


if __name__ == "__main__":
    main()
