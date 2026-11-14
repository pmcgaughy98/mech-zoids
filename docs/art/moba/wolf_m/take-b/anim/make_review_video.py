"""Numbered review video of every wolf animation (Claude, animation lane, 2026-11-04).

Preston: "When you are done making animations show me a video with all animations. Also number them so I can tell you
what models are wrong or have issues."
Numbers run 1-40: move order idle, walk, sprint, lunge, bite, hamstring, howl, death; view order s (front), se,
e (side), ne, n (back). Number = move index x 5 + view index + 1, so 12 is sprint e. Each move gets a 4 s segment with
its five views at 3x in a 3-over-2 grid (cropped to x 20-164, y 60-166, which holds every drawn frame), sel-out applied as in the game, playing at their own frame times (one-shot moves
hold their last frame 600 ms, then replay). Writes review/wolf_all.mp4 and review/wolf_index.png.
Run: python make_review_video.py [move ...]  (moves given: only those, written as review/wolf_<moves>.mp4)
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ANIM = Path(__file__).resolve().parent
OUT = ANIM / "review"
SELOUT = Path(r"D:\dev\new-mech-rpg\docs\art\moba\rhino_l\take-a\anim\selout_rhino.py")
FFMPEG = "ffmpeg"
VIEWS = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
MOVES = [  # name, ms per frame, loops
    ("idle", [220] * 5, True),
    ("walk", [100] * 8, True),
    ("sprint", [70] * 6, True),
    ("lunge", [120, 180, 80, 120, 90, 160, 200], False),
    ("bite", [100, 120, 80, 140, 160], False),
    ("hamstring", [120, 120, 80, 100, 160, 200], False),
    ("howl", [160, 160, 200, 500, 250, 220], False),
    ("death", [300, 100, 130, 140, 160, 180, 1400], False),
]
SOURCE = {"walk": ("codex-set-a", "codex-set-c"), "sprint": ("codex-set-a", "codex-set-c"),
          "lunge": ("codex-set-a", "codex-set-c"), "bite": ("codex-set-a", "codex-set-c"),
          "hamstring": ("codex-set-b", "codex-set-d"), "howl": ("codex-set-b", "codex-set-d"),
          "death": ("codex-set-b", "codex-set-d")}
K, FPS, SEG_S, HOLD = 3, 50, 4.0, 600
if len(sys.argv) > 1:
    SEG_S = 8.0  # a single-move clip plays longer
CROP = (20, 60, 164, 166)
CW, CH, LABEL = (CROP[2] - CROP[0]) * K, (CROP[3] - CROP[1]) * K, 44
W, H = CW * 3, (CH + LABEL) * 2
BG = (78, 86, 82)


def load_selout():
    spec = importlib.util.spec_from_file_location("selout_rhino", SELOUT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUTLINE = np.array([0x14, 0x14, 0x18], np.uint8)  # the wolf's darkest colour
    return mod.selout


def frame_path(move, view, file_view, i):
    if move == "idle":
        return ANIM / "idle" / "frames" / f"{file_view}_f{i}.png"
    main, diag = SOURCE[move]
    folder = diag if view in ("se", "ne") else main
    return ANIM / folder / move / "frames" / f"{file_view}_f{i}.png"


def frames_for(move, view, file_view, n, selout):
    out = []
    for i in range(n):
        p = frame_path(move, view, file_view, i)
        if not p.exists():
            return None
        a = np.asarray(Image.open(p).convert("RGBA")).copy()
        a = selout(a)[0]
        out.append(Image.fromarray(a, "RGBA").crop(CROP).resize((CW, CH), Image.NEAREST))
    return out


def index_at(ms_list, loops, t_ms):
    total = sum(ms_list) + (0 if loops else HOLD)
    t = t_ms % total
    acc = 0
    for i, ms in enumerate(ms_list):
        acc += ms
        if t < acc:
            return i
    return len(ms_list) - 1


def main():
    selout = load_selout()
    OUT.mkdir(exist_ok=True)
    big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 30)
    small = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    only = sys.argv[1:]
    name = "wolf_all" if not only else "wolf_" + "_".join(only)
    segments, missing = [], []
    for mi, (move, ms, loops) in enumerate(MOVES):
        if only and move not in only:
            continue
        cells = []
        for vi, (view, file_view) in enumerate(VIEWS):
            num = mi * 5 + vi + 1
            fr = frames_for(move, view, file_view, len(ms), selout)
            if fr is None:
                missing.append(f"{num} {move} {file_view}")
            cells.append((num, file_view, fr))
        segments.append((move, ms, loops, cells))
    proc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                             f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                             "-crf", "16", str(OUT / f"{name}.mp4")], stdin=subprocess.PIPE)
    index = Image.new("RGB", (W, H * len(segments)), BG)
    for si, (move, ms, loops, cells) in enumerate(segments):
        for f in range(int(SEG_S * FPS)):
            t = f * 1000 / FPS
            img = Image.new("RGB", (W, H), BG)
            d = ImageDraw.Draw(img)
            for ci, (num, file_view, fr) in enumerate(cells):
                x, y = (ci % 3) * CW + (CW // 2 if ci >= 3 else 0), (ci // 3) * (CH + LABEL)
                d.text((x + 14, y + 8), f"{num}", fill=(255, 230, 120), font=big)
                d.text((x + 70, y + 14), f"{move} {file_view}", fill=(235, 235, 235), font=small)
                if fr is None:
                    d.text((x + 140, y + LABEL + CH // 2), "not drawn yet", fill=(200, 120, 120), font=small)
                    continue
                im = fr[index_at(ms, loops, t)]
                img.paste(im, (x, y + LABEL), im)
            if f == 0:
                index.paste(img, (0, si * H))
            proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    index.save(OUT / f"{name}_index.png")
    print("wrote", OUT / f"{name}.mp4", f"{len(segments) * SEG_S:.0f} s;", "missing:", missing or "none")


if __name__ == "__main__":
    main()
