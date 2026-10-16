"""Contact sheets and GIFs from tools/debug/vfx_capture.gd's frames (Claude, 2026-10-15).

python tools/art/vfx_sheets.py <frames folder> [out folder]

For each captured attack: a sheet of 8 frames around the impact (0.4 s before to 0.6 s after, the stage only, at half
size so each art pixel of the 0.75-scale field is 1.5 sheet pixels) and a GIF of the whole step at half size.
Also writes all_impacts.png: one frame per attack, just after the impact, for an overview.
"""
import json
import os
import sys

from PIL import Image, ImageDraw

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src
os.makedirs(dst, exist_ok=True)
index = json.load(open(os.path.join(src, "index.json"), encoding="utf-8"))
STAGE_H = 496  # the stage above the panel, in 1280x720 window pixels (124 screen rows)


def frame(tag, k):
    return Image.open(os.path.join(src, tag, "%03d.png" % k)).convert("RGB")


def nearest(times, t):
    return min(range(len(times)), key=lambda k: abs(times[k] - t))


overview = []
for tag, info in index.items():
    times = info["times"]
    impact = info["impact"] if info["impact"] >= 0 else info["hold"] * 0.4
    picks = []
    for i in range(8):
        k = nearest(times, impact - 0.4 + i * (1.0 / 7.0))
        if k not in picks:
            picks.append(k)
    w, h = 640, STAGE_H // 2
    sheet = Image.new("RGB", (w * 4, (h + 12) * 2), (12, 14, 20))
    d = ImageDraw.Draw(sheet)
    for i, k in enumerate(picks):
        im = frame(tag, k).crop((0, 0, 1280, STAGE_H)).resize((w, h), Image.NEAREST)
        x, y = (i % 4) * w, (i // 4) * (h + 12)
        sheet.paste(im, (x, y + 12))
        d.text((x + 4, y), "%+.2f s" % (times[k] - impact), fill=(255, 220, 0))
    sheet.save(os.path.join(dst, "%s_sheet.png" % tag))
    gif = [frame(tag, k).resize((640, 360), Image.NEAREST) for k in range(len(times))]
    gif[0].save(os.path.join(dst, "%s.gif" % tag), save_all=True, append_images=gif[1:],
                duration=int(1000 / info["fps"]), loop=0)
    overview.append((tag, frame(tag, nearest(times, impact + 0.07)).crop((0, 0, 1280, STAGE_H)).resize((427, 165), Image.NEAREST)))
    print(tag, len(times), "frames, impact %.2f s" % impact)

showcase = os.environ.get("VFX_SHOWCASE", "")   # "tag1,tag2,...": one GIF playing those attacks in a row
if showcase:
    reel = []
    for tag in showcase.split(","):
        if tag not in index:
            continue
        n = len(index[tag]["times"])
        for k in range(n):
            im = frame(tag, k).resize((640, 360), Image.NEAREST)
            ImageDraw.Draw(im).text((6, 4), index[tag]["weapon"], fill=(255, 255, 255))
            reel.append(im)
    fps = next(iter(index.values()))["fps"]
    reel[0].save(os.path.join(dst, "showcase.gif"), save_all=True, append_images=reel[1:], duration=int(1000 / fps), loop=0)
    print("showcase", len(reel), "frames")

if overview:
    cols = 3
    rows = (len(overview) + cols - 1) // cols
    ov = Image.new("RGB", (427 * cols, 177 * rows), (12, 14, 20))
    d = ImageDraw.Draw(ov)
    for i, (tag, im) in enumerate(overview):
        x, y = (i % cols) * 427, (i // cols) * 177
        ov.paste(im, (x, y + 12))
        d.text((x + 4, y), tag, fill=(255, 220, 0))
    ov.save(os.path.join(dst, "all_impacts.png"))
