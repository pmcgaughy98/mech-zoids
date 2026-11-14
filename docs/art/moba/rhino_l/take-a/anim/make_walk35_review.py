"""Review video for the rhino walk at 35 degrees (Claude, animation lane, 2026-11-04).

Plays each view the way the game does: the frames change at 8 fps while the ground (a dot grid) scrolls under the
rhino at the planted pace, along that view's camera axis (walk35/targets.json "planted_step_px", 0.48 m/s). A planted
foot that is really locked moves with the dots; one that slides drifts across them. Numbered views, the still on the
left of each tile for comparison. Sel-out on, 3x.
Run: python make_walk35_review.py [view ...]   (default: every view that has frames). Writes walk35/review_<views>.mp4.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ANIM = Path(__file__).resolve().parent
W35 = ANIM / "walk35"
STILLS = ANIM.parent / "views_cam35"
ORDER = ("s", "se", "e", "ne", "n")
FPS_ANIM, FPS_VID, SECONDS, K = 8, 30, 8, 3
BOX = (36, 56, 156, 168)          # canvas area shown
GRID = 12                          # dot spacing, canvas px


def load_selout():
    spec = importlib.util.spec_from_file_location("selout_rhino", ANIM / "selout_rhino.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.selout


def main():
    views = sys.argv[1:] or [v for v in ORDER if (W35 / "walk" / "frames" / f"{v}_f0.png").exists()]
    t = json.load(open(W35 / "targets.json", encoding="utf8"))
    selout = load_selout()
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
    bw, bh = (BOX[2] - BOX[0]) * K, (BOX[3] - BOX[1]) * K
    tile_w, tile_h = bw * 2 + 8, bh + 36
    cols = min(3, len(views))
    nrows = (len(views) + cols - 1) // cols
    W, H = tile_w * cols + 12 * (cols - 1), tile_h * nrows + 12 * (nrows - 1)
    W += W % 2
    H += H % 2
    sprites = {}
    for v in views:
        fr = [selout(np.asarray(Image.open(W35 / "walk" / "frames" / f"{v}_f{i}.png").convert("RGBA")).copy())[0]
              for i in range(8)]
        still = selout(np.asarray(Image.open(STILLS / f"{v}.png").convert("RGBA")).copy())[0]
        cut = lambda a: Image.fromarray(a).crop(BOX).resize((bw, bh), Image.NEAREST)
        sprites[v] = ([cut(a) for a in fr], cut(still))
    out = W35 / f"review_{'_'.join(views)}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                             f"{W}x{H}", "-r", str(FPS_VID), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                             "-crf", "16", str(out)], stdin=subprocess.PIPE)
    for f in range(SECONDS * FPS_VID):
        sec = f / FPS_VID
        i = int(sec * FPS_ANIM) % 8
        img = Image.new("RGB", (W, H), (52, 56, 54))
        dr = ImageDraw.Draw(img)
        for n, v in enumerate(views):
            x0 = (n % cols) * (tile_w + 12)
            y0 = (n // cols) * (tile_h + 12)
            num = ORDER.index(v) + 1
            dr.text((x0 + 4, y0 + 6), f"{num}  rhino walk {v}   (left: approved still)", fill=(240, 220, 120), font=font)
            sx, sy = t["views"][v]["planted_step_px"]
            ox, oy = sec * FPS_ANIM * sx, sec * FPS_ANIM * sy     # ground moves with a planted foot
            for side in (0, 1):
                tx = x0 + side * (bw + 8)
                dr.rectangle([tx, y0 + 36, tx + bw - 1, y0 + 36 + bh - 1], fill=(78, 92, 84))
                if side:
                    for gx in np.arange(-GRID, BOX[2] - BOX[0] + GRID, GRID):
                        for gy in np.arange(-GRID, BOX[3] - BOX[1] + GRID, GRID):
                            px = (gx + ox) % (BOX[2] - BOX[0] + GRID) - GRID / 2
                            py = (gy + oy) % (BOX[3] - BOX[1] + GRID) - GRID / 2
                            if 0 <= px < BOX[2] - BOX[0] and 0 <= py < BOX[3] - BOX[1]:
                                dr.rectangle([tx + px * K, y0 + 36 + py * K, tx + px * K + 3, y0 + 36 + py * K + 3],
                                             fill=(150, 170, 140))
            frames, still = sprites[v]
            img.paste(still, (x0, y0 + 36), still)
            img.paste(frames[i], (x0 + bw + 8, y0 + 36), frames[i])
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    print("wrote", out)


if __name__ == "__main__":
    main()
