"""Lays the arena style frames out side by side with their names. Map design lane, 2026-11-04.
  python tools/map/style_sheet.py
Reads docs/plan/moba-style-<theme>-2026-11-04.png (from tools/map/style_frames.gd) and writes
docs/plan/moba-style-frames-2026-11-04.png: 2 across, each frame at half size, with a caption bar under each.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(__file__)
PLAN = os.path.join(HERE, "..", "..", "docs", "plan")
FRAMES = [
    ("nature", "Stage 1 (for comparison): nature"),
    ("circuit", "A  Circuit: clean daylight tech, light steel, cyan traces"),
    ("neon", "B  Neon: night, dark plates, glowing grid, violet and cyan"),
    ("foundry", "C  Foundry: industrial dusk, diamond plate, hazard stripes, amber"),
]
W, H, BAR = 640, 360, 26


def main():
    sheet = Image.new("RGB", (W * 2, (H + BAR) * 2), (20, 18, 24))
    draw = ImageDraw.Draw(sheet)
    for i, (name, caption) in enumerate(FRAMES):
        img = Image.open(os.path.join(PLAN, "moba-style-%s-2026-11-04.png" % name)).convert("RGB")
        img = img.resize((W, H), Image.NEAREST)
        x, y = (i % 2) * W, (i // 2) * (H + BAR)
        sheet.paste(img, (x, y))
        draw.text((x + 8, y + H + 7), caption, fill=(235, 235, 240))
    out = os.path.join(PLAN, "moba-style-frames-2026-11-04.png")
    sheet.save(out)
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main()
