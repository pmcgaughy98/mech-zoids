"""Gorilla (ape_l) art for the 3D slice (Claude, 2026-11-04).

Writes:
- art/machines/ape/ape_still_<v>.png: the five approved stills (s, se, e, ne, n), 160x160, feet on row 130. A stand-in
  until the Codex animation sets land; DirectionalSprite3D shows them as one-frame idles and walks.
- art/fx/moba3d/hex_gem_arm.png, hex_gem_back.png: copies of the gorilla's hex gems (the gauntlet gem as seen face-on
  in the side still, the back gem from the back still), cut out with a one-texel dark outline. Preston's shield look:
  three shields that look like the three gems float in a round loop around the shielded machine.
- art/fx/moba3d/hex_tile.png: one repeat of a pixel hex grid in the gems' greens, for the hex shield shell and the
  hex dome. 24x14 texels: flat-top hexes whose centres form a near-equilateral lattice (neighbours 13.9 and 14 apart).

Run: python tools/art/pack_ape_fx.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
VIEWS = ROOT / "docs/art/moba/ape_l/take-a/views"
MACH = ROOT / "art/machines/ape"
FX = ROOT / "art/fx/moba3d"

OUTLINE = (0x14, 0x1A, 0x16)
GEM = {(0x3F, 0xE0, 0x7F), (0x1B, 0x9A, 0x52), (0xD6, 0xFF, 0xE6)}
EDGE = (0x3F, 0xE0, 0x7F)
FILL = (0x1B, 0x9A, 0x52)
SHINE = (0xD6, 0xFF, 0xE6)


def stills() -> None:
    MACH.mkdir(parents=True, exist_ok=True)
    for v in ["s", "se", "e", "ne", "n"]:
        im = Image.open(VIEWS / f"{v}.png").convert("RGBA")
        a = np.array(im)
        rows = np.where(a[:, :, 3].any(axis=1))[0]
        assert rows.max() == 130, f"{v}: feet on row {rows.max()}, expected 130"
        im.save(MACH / f"ape_still_{v}.png")


def gem(view: str, box: tuple[int, int, int, int], name: str) -> None:
    """Cuts the largest gem-coloured blob inside box out of a still and rings it with the dark outline."""
    a = np.array(Image.open(VIEWS / f"{view}.png").convert("RGBA"))
    x0, y0, x1, y1 = box
    sub = a[y0:y1 + 1, x0:x1 + 1]
    mask = np.zeros(sub.shape[:2], bool)
    for y in range(sub.shape[0]):
        for x in range(sub.shape[1]):
            mask[y, x] = sub[y, x, 3] > 0 and tuple(sub[y, x, :3]) in GEM
    h, w = mask.shape
    out = np.zeros((h + 2, w + 2, 4), np.uint8)
    out[1:-1, 1:-1][mask] = sub[mask]
    m = np.zeros((h + 2, w + 2), bool)
    m[1:-1, 1:-1] = mask
    ring = np.zeros_like(m)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            ring |= np.roll(np.roll(m, dy, 0), dx, 1)
    ring &= ~m
    out[ring] = (*OUTLINE, 255)
    Image.fromarray(out).save(FX / f"{name}.png")
    print(name, out.shape[1], "x", out.shape[0], int(m.sum()), "gem texels")


def hex_tile() -> None:
    W, H = 24, 14
    centres = [(0.0, 0.0), (12.0, 7.0)]
    pts = [(cx + i * W, cy + j * H) for cx, cy in centres for i in (-1, 0, 1) for j in (-1, 0, 1)]
    out = np.zeros((H, W, 4), np.uint8)
    for y in range(H):
        for x in range(W):
            p = (x + 0.5, y + 0.5)
            d = sorted(((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2, c) for c in pts)
            (d1, c1), (d2, c2) = d[0], d[1]
            gap = (d2 - d1) / (2.0 * ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5)
            if gap < 0.75:
                out[y, x] = (*EDGE, 255)
            else:
                out[y, x] = (*FILL, 64)
    # A glint on the upper-left edge of each hex, the gems' own highlight colour.
    for cx, cy in centres:
        gx, gy = int(cx - 4) % W, int(cy - 6) % H
        if out[gy, gx, 3] == 255:
            out[gy, gx] = (*SHINE, 255)
    Image.fromarray(out).save(FX / "hex_tile.png")


if __name__ == "__main__":
    stills()
    gem("e", (81, 100, 98, 116), "hex_gem_arm")
    gem("n", (70, 67, 88, 80), "hex_gem_back")
    hex_tile()
