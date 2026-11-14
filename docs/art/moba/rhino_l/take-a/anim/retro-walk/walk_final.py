"""The rhino's 8-direction walk from five drawn directions (Claude, 2026-11-04).

Preston kept the Retro Diffusion side and se walks ("only 2 that have matching gaits like id want are se and
side view") and liked the PixelLab pose-guided front ("yes run back and ne that looks great though"). So:
- front, ne, back: PixelLab animate_with_skeleton_v3, posed with the same four-beat step order as the Retro
  side (pixellab/front_skeleton.py, pixellab/skeleton_views.py), finished by pixellab/finish_pixellab.py;
- se, side: Retro Diffusion walking, finished by finish_retro.py.
West-facing directions (w, sw, nw) are the east ones mirrored in the engine.
Writes walk-final/{view}_f0..f7.png (192 canvas), board-walk-final.png (first column is the approved still,
then the 8 frames, with the IoU of each frame against that still) and preview-walk-final.gif, compass order
s, se, e, ne, n.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ANIM = HERE.parent
sys.path.insert(0, str(ANIM))
from selout_rhino import selout  # noqa: E402

OUT = HERE / "walk-final"
PL, RD = HERE / "pixellab" / "frames", HERE / "frames"
SRC = {"front": PL, "se": RD, "side": RD, "ne": PL, "back": PL}
MAKER = {"front": "PixelLab posed", "se": "Retro", "side": "Retro", "ne": "PixelLab posed", "back": "PixelLab posed"}
ORDER = ("front", "se", "side", "ne", "back")
GP = ANIM / "codex-ground-pound/clean/frames_selout"
BG = (0x3D, 0x43, 0x50, 255)


def still(v):
    p = GP / f"{v}_f0.png"
    if p.exists():
        return np.asarray(Image.open(p).convert("RGBA"))
    return selout(np.asarray(Image.open(ANIM.parent / "views" / f"{v}.png").convert("RGBA")))[0]


def main():
    OUT.mkdir(exist_ok=True)
    for v in ORDER:  # fresh copies first, then the detail-ink pass (detail_ink.py) on the flat views
        for i in range(8):
            shutil.copy(SRC[v] / f"{v}_f{i}.png", OUT / f"{v}_f{i}.png")
    shutil.rmtree(OUT / "pre_ink", ignore_errors=True)
    import detail_ink
    detail_ink.run(OUT)
    rows, ref, report = {}, {}, []
    for v in ORDER:
        ref[v] = still(v)
        m0 = ref[v][..., 3] > 0
        rows[v] = []
        ious, bots = [], []
        for i in range(8):
            a = np.asarray(Image.open(OUT / f"{v}_f{i}.png").convert("RGBA"))
            rows[v].append(a)
            m = a[..., 3] > 0
            ious.append((m & m0).sum() / (m | m0).sum())
            bots.append(int(np.where(m)[0].max()))
        report.append(f"{v} ({MAKER[v]}): IoU vs still {min(ious):.2f}-{max(ious):.2f}, "
                      f"bottom row {min(bots)}-{max(bots)} (still {int(np.where(m0)[0].max())})")
        rows[v] = list(zip(rows[v], ious))
    k, crop = 3, (16, 66, 176, 168)
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    board = Image.new("RGBA", (9 * w, len(ORDER) * h), BG)
    dr = ImageDraw.Draw(board)
    for j, v in enumerate(ORDER):
        board.alpha_composite(Image.fromarray(ref[v]).crop(crop).resize((w, h), Image.NEAREST), (0, j * h))
        dr.text((4, j * h + 2), f"{v} still", fill=(255, 220, 120, 255))
        for i, (a, iou) in enumerate(rows[v]):
            board.alpha_composite(Image.fromarray(a).crop(crop).resize((w, h), Image.NEAREST), ((i + 1) * w, j * h))
            dr.text(((i + 1) * w + 4, j * h + 2), f"{v} f{i}  IoU {iou:.2f}", fill=(235, 235, 240, 255))
        gy = j * h + (161 - crop[1]) * k
        dr.line((0, gy, 9 * w, gy), fill=(120, 126, 140, 255))
    board.save(OUT / "board-walk-final.png")
    gifs = []
    for i in list(range(8)) * 3:
        g = Image.new("RGBA", (len(ORDER) * w, h), BG)
        for j, v in enumerate(ORDER):
            g.alpha_composite(Image.fromarray(rows[v][i][0]).crop(crop).resize((w, h), Image.NEAREST), (j * w, 0))
        gifs.append(g.convert("RGB"))
    gifs[0].save(OUT / "preview-walk-final.gif", save_all=True, append_images=gifs[1:], duration=125, loop=0)
    (OUT / "REPORT.txt").write_text("\n".join(report) + "\n", encoding="utf8")
    print("\n".join(report))
    print("saved walk-final/")


if __name__ == "__main__":
    main()
