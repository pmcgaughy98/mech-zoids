"""Foot-lock test: plays a walk the way the game does and stamps footprints (Claude, animation lane, 2026-11-04).

Preston: "Is there a way you could play during reveal thatd show you whats wrong. Not how a wolf gait would look".
The camera follows the wolf like the game's chase camera while the ground scrolls under it at the move speed. Every
frame, each paw pixel touching the ground (row 160) leaves a footprint at its place on the ground. A paw that is
really planted stays on one spot, so its footprints pile up into a dot. A paw that is not moving back under the body
slides along the ground, so its footprints smear into a streak. Grid lines are 10 px (0.18 m at size M) apart.
Run: python foot_lock_test.py <frames dir> <view> [speed m/s, default 1.0] [out name] [out dir, default anim/review]
Writes <out>.mp4 (8 s) and <out>.png (the last frame, with every footprint). Frame dirs are relative to anim/.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ANIM = Path(__file__).resolve().parent
M_PER_TX, FPS_ANIM, FPS_VID, K, SECONDS = 0.018, 10, 50, 3, 8
VIEW_W, TOP, BOTTOM = 432, 64, 176           # native px shown; rows of the 192 canvas kept: TOP to BOTTOM
RED = [(0xe8, 0x25, 0x1f), (0xa8, 0x14, 0x1a), (0x5c, 0x0a, 0x10), (0xff, 0x6a, 0x55)]


def load(d, view):
    fs = sorted(Path(d).glob(f"{view}_f*.png"), key=lambda p: int(p.stem.split("_f")[1]))
    return [np.asarray(Image.open(p).convert("RGBA")) for p in fs]


def contacts(a):
    """Opaque pixels on the ground row (the paws' bottom edge is the dark outline, so colour is not checked)."""
    return [x for x in range(a.shape[1]) if a[160, x, 3] > 0]


def main():
    d, view = sys.argv[1], sys.argv[2]
    speed = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    name = sys.argv[4] if len(sys.argv) > 4 else f"footlock_{view}"
    frames = load(ANIM / d if not Path(d).is_absolute() else d, view)
    px_per_s = speed / M_PER_TX
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    H = (BOTTOM - TOP) * K + 40
    out = Path(sys.argv[5]) if len(sys.argv) > 5 else ANIM / "review"
    out.mkdir(exist_ok=True)
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                             f"{VIEW_W * K}x{H}", "-r", str(FPS_VID), "-i", "-", "-c:v", "libx264", "-pix_fmt",
                             "yuv420p", "-crf", "16", str(out / f"{name}.mp4")], stdin=subprocess.PIPE)
    prints = []  # world x of each ground-contact pixel, with the frame count it was stamped on
    last_i, img = -1, None
    for f in range(SECONDS * FPS_VID):
        t = f / FPS_VID
        cam = t * px_per_s                         # world x of the wolf's canvas left edge
        i = int(t * FPS_ANIM) % len(frames)
        a = frames[i]
        if int(t * FPS_ANIM) != last_i:
            last_i = int(t * FPS_ANIM)
            prints += [cam + x for x in contacts(a)]
        left = cam - (VIEW_W - 192) / 2            # world x at the view's left edge
        img = Image.new("RGB", (VIEW_W * K, H), (78, 86, 82))
        dr = ImageDraw.Draw(img)
        g0 = (BOTTOM - TOP - 16) * K + 40
        dr.rectangle([0, g0 + (160 - (BOTTOM - 16)) * K, VIEW_W * K, H], fill=(96, 92, 80))
        ground_y = 40 + (161 - TOP) * K
        for gx in np.arange(np.floor(left / 10) * 10, left + VIEW_W + 10, 10):
            sx = (gx - left) * K
            dr.line([(sx, ground_y), (sx, H)], fill=(120, 116, 100))
        for wx in prints:
            sx = (wx - left) * K
            if -K <= sx <= VIEW_W * K:
                dr.rectangle([sx, ground_y + 4, sx + K - 1, ground_y + 4 + 3 * K], fill=(255, 220, 90))
        spr = Image.fromarray(a[TOP:BOTTOM]).resize((192 * K, (BOTTOM - TOP) * K), Image.NEAREST)
        img.paste(spr, (int((VIEW_W - 192) / 2 * K), 40), spr)
        dr.text((10, 8), f"{d} {view}: moving at {speed:.2f} m/s, camera follows. Yellow = where a paw touched the ground.",
                fill=(240, 240, 240), font=font)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    img.save(out / f"{name}.png")
    print("wrote", out / f"{name}.mp4", "and .png;", len(prints), "contact pixels stamped")


if __name__ == "__main__":
    main()
