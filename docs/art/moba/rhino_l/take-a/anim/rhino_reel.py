"""Rhino reel: every finished animation in three views with its effects, as one video plus a contact board.

Frames come from codex-set-a and codex-set-b after fix_set.py; effects from codex-set-b/effects. The part of a
ring effect above its centre row draws behind the rhino and the part below draws in front (same rule as the
ground pound composite). One-shot moves play at normal speed and then at half speed. The ground pound has its
own video (codex-ground-pound/clean) and is not repeated here. Claude, 2026-11-03.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).parent
OUT = ANIM / "reel"
SUB = sys.argv[1] if len(sys.argv) > 1 else "frames"  # frames_selout for the sel-out reel
TAG = "" if SUB == "frames" else "-" + SUB.replace("frames_", "")
FX_DIR = ANIM / "codex-set-b/effects"
FFMPEG = "C:/Users/pmcga/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe"
VIEWS = ("front", "side", "back")
BG = (0x3D, 0x43, 0x50, 255)
CROP = (8, 40, 184, 184)  # x0, y0, x1, y1 of the 192x192 frame shown per view
K = 3

# (title, set, sheet, steps, effects as (start step, effect, placement, loop?), one-shot?)
ANIMS = [
    ("idle", "a", "idle", [1, 1, 2, 2, 3, 3, 4, 4] * 2, [], False),
    ("walk", "a", "walk", [0, 1, 2, 3, 4, 5, 6, 7] * 3, [], False),
    ("horn jab", "a", "horn-jab", [0, 0, 1, 1, 2, 3, 3, 4, 5, 0, 0, 0], [(5, "hit", "horn", False)], True),
    ("horn toss, stun on landing", "a", "horn-toss", [0, 0, 1, 2, 3, 4, 4, 5, 6, 0, 0, 0, 0, 0, 0, 0],
     [(7, "impact", "landing", False), (8, "stun", "landing-stun", True)], True),
    ("brace", "b", "brace", [0, 1, 2, 3, 3, 3, 3, 3, 3, 3, 4, 0, 0],
     [(2, "brace", "feet", False), (5, "deflect", "plate", False)], True),
    ("stampede", "b", "stampede", [1, 2, 3, 4, 5, 6] * 3, [(s, "dust", "rear", False) for s in range(0, 18, 3)], False),
    ("death", "b", "death", [0, 1, 2, 3, 4, 5, 6, 6, 6, 6, 6, 6], [], True),
]


def load_fx():
    fx = {}
    for d in sorted(p for p in FX_DIR.iterdir() if p.is_dir()):
        frames = [np.asarray(Image.open(p).convert("RGBA")) for p in sorted(d.glob("*.png"))]
        if not frames:
            continue
        alpha = np.any([f[..., 3] > 0 for f in frames], axis=0)
        ys, xs = np.where(alpha)
        box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        frames = [f[box[1]:box[3], box[0]:box[2]] for f in frames]
        h, w = frames[0].shape[:2]
        ground = d.name.startswith(("impact", "dust"))
        fx[d.name.split("-")[0]] = dict(frames=frames, anchor=(w // 2, h - 1 if ground else h // 2), name=d.name)
    return fx


def target(a, view, where):
    """Where an effect goes for this rhino frame and view, and whether it draws behind, in front, or split."""
    ys, xs = np.where(a[..., 3] > 0)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    cx, h = (x0 + x1) // 2, y1 - y0
    if where == "horn":
        if view == "side":
            i = np.argmax(xs)
            return (xs[i] + 2, ys[i]), "front"
        mid = (xs > cx - 8) & (xs < cx + 8)
        return (cx, ys[mid].min() + 2), "front" if view == "front" else "behind"
    if where == "landing":
        return {"front": ((cx, 150), "behind"), "side": ((x0 - 16, 160), "front"), "back": ((cx, 178), "front")}[view]
    if where == "landing-stun":
        return {"front": ((cx, 128), "behind"), "side": ((x0 - 16, 140), "front"), "back": ((cx, 158), "front")}[view]
    if where == "feet":
        return (cx, 156), "split"
    if where == "plate":
        if view == "side":
            return (x1 - 10, y0 + int(0.45 * h)), "front"
        return (cx, y0 + int(0.45 * h)), "front" if view == "front" else "behind"
    if where == "rear":
        return {"front": ((cx, 160), "behind"), "side": ((x0 - 2, 160), "behind"), "back": ((cx, 163), "front")}[view]


def paste(dst, src, at):
    x, y = at
    h, w = src.shape[:2]
    X0, Y0, X1, Y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if X0 >= X1 or Y0 >= Y1:
        return
    s = src[Y0 - y:Y1 - y, X0 - x:X1 - x]
    m = s[..., 3] > 0
    dst[Y0:Y1, X0:X1][m] = s[m]


def compose(a, layers):
    """layers: list of (effect frame, top-left, mode, split row in canvas)."""
    out = np.zeros((192, 192, 4), np.uint8)
    out[...] = BG
    for f, at, mode, row in layers:
        if mode == "behind":
            paste(out, f, at)
        elif mode == "split":
            paste(out, f[:max(0, row - at[1])], at)
    paste(out, a, (0, 0))
    for f, at, mode, row in layers:
        if mode == "front":
            paste(out, f, at)
        elif mode == "split":
            cut = max(0, row - at[1])
            paste(out, f[cut:], (at[0], at[1] + cut))
    return out


def clip_frames(fx, setname, sheet, steps, effects):
    frames_dir = ANIM / f"codex-set-{setname}" / sheet / SUB
    imgs = {v: [np.asarray(Image.open(frames_dir / f"{v}_f{i}.png").convert("RGBA")) for i in range(8)
                if (frames_dir / f"{v}_f{i}.png").exists()] for v in VIEWS}
    out = []
    for s, fi in enumerate(steps):
        row = []
        for v in VIEWS:
            a = imgs[v][fi]
            layers = []
            for start, name, where, loop in effects:
                e = fx[name]
                k = s - start
                if k < 0 or (not loop and k >= len(e["frames"])):
                    continue
                f = e["frames"][k % len(e["frames"])]
                (tx, ty), mode = target(a, v, where)
                layers.append((f, (tx - e["anchor"][0], ty - e["anchor"][1]), mode, ty))
            row.append(compose(a, layers))
        out.append(row)
    return out, imgs


def stage(row, title, note):
    tiles = [Image.fromarray(t).crop(CROP) for t in row]
    w, h = CROP[2] - CROP[0], CROP[3] - CROP[1]
    im = Image.new("RGBA", (3 * w, h + 16), BG)
    d = ImageDraw.Draw(im)
    for i, (t, v) in enumerate(zip(tiles, VIEWS)):
        im.alpha_composite(t, (i * w, 16))
        d.text((i * w + 4, 18), v, fill=(200, 204, 214, 255))
    d.rectangle((0, 0, 3 * w, 15), fill=(0x2A, 0x2E, 0x38, 255))
    d.text((4, 2), f"{title}  {note}", fill=(235, 235, 240, 255))
    return im.resize((im.width * K, im.height * K), Image.NEAREST)


def main():
    OUT.mkdir(exist_ok=True)
    fx = load_fx()
    print("effects:", {k: (v["name"], len(v["frames"]), v["frames"][0].shape[1]) for k, v in fx.items()})
    shots, n = OUT / "frames", 0
    shots.mkdir(exist_ok=True)
    for p in shots.glob("*.png"):
        p.unlink()
    board_rows, ground = [], []
    for title, setname, sheet, steps, effects, oneshot in ANIMS:
        seq, imgs = clip_frames(fx, setname, sheet, steps, effects)
        passes = [("", 1), ("(half speed)", 2)] if oneshot else [("", 1)]
        for note, rep in passes:
            for row in seq:
                im = stage(row, title, note)
                for _ in range(rep):
                    im.save(shots / f"{n:04d}.png")
                    n += 1
        for v in VIEWS:
            board_rows.append((f"{title} {v}", [Image.fromarray(compose(a, [])).crop(CROP) for a in imgs[v]]))
            for i, a in enumerate(imgs[v]):
                b = np.where(a[..., 3] > 0)[0].max()
                if b != 160 and not (TAG and b == 161):
                    ground.append(f"{sheet} {v}_f{i} bottom {b}")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", "10", "-i", str(shots / "%04d.png"),
                    "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "14", str(OUT / f"rhino-reel{TAG}.mp4")], check=True)
    w, h = CROP[2] - CROP[0], CROP[3] - CROP[1]
    board = Image.new("RGBA", (7 * w * 2 + 8, len(board_rows) * (h * 2 + 14)), (0x2A, 0x2E, 0x38, 255))
    d = ImageDraw.Draw(board)
    for j, (label, tiles) in enumerate(board_rows):
        y = j * (h * 2 + 14)
        d.text((4, y + 1), label, fill=(235, 235, 240, 255))
        for i, t in enumerate(tiles):
            board.alpha_composite(t.resize((w * 2, h * 2), Image.NEAREST), (i * w * 2, y + 13))
    board.save(OUT / f"rhino-contact{TAG}.png")
    print(f"{n} frames at 10 fps = {n / 10:.1f} s; board {board.size}")
    print("ground:", ground or "every frame's lowest pixel on y=160")


if __name__ == "__main__":
    main()
