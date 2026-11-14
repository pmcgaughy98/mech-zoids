"""Finish the fennec's Retro Diffusion frames into the game's format (Claude, animation lane, 2026-11-04).

Modelled on rhino_l/take-a/anim/retro-walk/finish_retro.py. Per Retro sheet (raw/<name>_sheet.png, 128 cells):
  1. snap every colour to the nearest of the fennec's 15 colours, binary alpha;
  2. drop specks: opaque islands under 6 px that do not touch the body;
  3. ground: the lowest row with 4+ opaque pixels goes back on the input's foot row (Retro drifts up and down);
  4. map back into the 192 canvas with the offset prep_retro.py cut the input with (offsets.json), feet on row 160.
  5. kick_*: frame 0 and the last frame are replaced by the approved still exactly (the pack check needs that).
No sel-out here: the packer adds it, as for every other fennec frame.
Writes frames/<name>_f<i>.png and board-<name>.png (input still/frame left, sel-out on, 3x) beside this script.
Usage: python finish_retro.py walk_n [walk_ne kick_n kick_ne]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).parent
TAKE = HERE.parents[1]
sys.path.insert(0, str(TAKE.parents[1] / "rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402

selout_rhino.OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
PAL = [0x141218, 0x211E27, 0x2E1A6E, 0x3D3A44, 0x6A3CC8, 0x9D9BA2, 0xA46BFF, 0xB8923A, 0xD6D6DC, 0xE0C8FF,
       0xF0D27A, 0x3FE8B0, 0xC8FFF0, 0xFFF4D6, 0xF6FFFB]
PAL = np.array([[c >> 16, c >> 8 & 255, c & 255] for c in PAL], np.int32)
CELL = 128


def unback(a):
    """custom_action returned frames 1-5 on a white background: clear what is joined to the border and near its colour."""
    edge = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    if (edge[:, 3] > 127).mean() < 0.5:
        return a, 0
    bg = np.median(edge[edge[:, 3] > 127][:, :3], 0)
    near = (np.abs(a[..., :3].astype(int) - bg).sum(-1) < 60) & (a[..., 3] > 127)
    lab, _ = ndimage.label(near)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    m = np.isin(lab, list(border))
    out = a.copy()
    out[m, 3] = 0
    return out, int(m.sum())


def snap(a):
    out = np.zeros_like(a)
    op = a[..., 3] > 127
    px = a[op][:, :3].astype(np.int32)
    out[op, :3] = PAL[((px[:, None, :] - PAL[None]) ** 2).sum(-1).argmin(1)]
    out[op, 3] = 255
    return out


def despeck(a):
    lab, n = ndimage.label(a[..., 3] > 0)
    if n <= 1:
        return a, 0
    sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= 6
    keep[1 + int(np.argmax(sizes))] = True
    out = a.copy()
    out[~keep[lab]] = 0
    return out, int((~keep[lab] & (lab > 0)).sum())


def floor(a):
    return int(np.where((a[..., 3] > 0).sum(1) >= 4)[0].max())


def still(v):
    c = np.zeros((192, 192, 4), np.uint8)
    c[20:180, 16:176] = np.asarray(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA"))
    return c


def finish(name):
    off = json.loads((HERE / "offsets.json").read_text())[name]
    sheet = np.asarray(Image.open(HERE / "raw" / f"{name}_sheet.png").convert("RGBA"))
    cells = [sheet[r * CELL:(r + 1) * CELL, c * CELL:(c + 1) * CELL]
             for r in range(sheet.shape[0] // CELL) for c in range(sheet.shape[1] // CELL)]
    cells = [c for c in cells if (c[..., 3] > 127).sum() > 200]
    inp = np.asarray(Image.open(HERE / "input" / f"{name}_128.png").convert("RGBA"))
    want = floor(inp)
    (HERE / "frames").mkdir(exist_ok=True)
    out = []
    for i, c in enumerate(cells):
        c, cleared = unback(c)
        f, specks = despeck(snap(c))
        shift = want - floor(f)
        f = np.roll(f, shift, axis=0)
        big = np.zeros((192, 192, 4), np.uint8)
        ys, xs = np.nonzero(f[..., 3] > 0)
        ys2, xs2 = ys - off["dy"], xs - off["dx"]
        ok = (ys2 >= 0) & (ys2 < 192) & (xs2 >= 0) & (xs2 < 192)
        big[ys2[ok], xs2[ok]] = f[ys[ok], xs[ok]]
        big[161:] = 0
        out.append(big)
        print(f"{name}_f{i}: background px {cleared}, grounded {shift:+d}, specks {specks}, bottom {ys2.max()}, "
              f"bbox x {xs2.min()}-{xs2.max()} y {ys2.min()}-{ys2.max()}")
    if name.startswith("kick_"):
        v = name.split("_")[1]
        out[0] = still(v)
        out[-1] = still(v)
    for i, f in enumerate(out):
        Image.fromarray(f).save(HERE / "frames" / f"{name}_f{i}.png")
    ref = still(name.split("_")[1]) if name.startswith("kick_") else np.asarray(
        Image.open(HERE / "input" / f"{name}_128.png").convert("RGBA"))
    if not name.startswith("kick_"):  # the input frame, back in the 192 canvas
        r = np.zeros((192, 192, 4), np.uint8)
        ys, xs = np.nonzero(ref[..., 3] > 0)
        r[ys - off["dy"], xs - off["dx"]] = ref[ys, xs]
        ref = r
    box, z = (32, 56, 160, 164), 3
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    board = Image.new("RGBA", ((len(out) + 1) * w, h), (0x3D, 0x43, 0x50, 255))
    tiles = [Image.fromarray(selout_rhino.selout(a)[0]).crop(box).resize((w, h), Image.NEAREST) for a in [ref] + out]
    for c, t in enumerate(tiles):
        board.alpha_composite(t, (c * w, 0))
    board.save(HERE / f"board-{name}.png")
    tiles[1].save(HERE / f"preview-{name}.gif", save_all=True, append_images=tiles[2:], duration=100, loop=0,
                  disposal=2)
    print(f"{name}: {len(out)} frames, board-{name}.png")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        finish(n)
