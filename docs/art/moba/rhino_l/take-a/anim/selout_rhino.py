"""Sel-out for the MOBA style, baked into the rhino's frames (Claude, 2026-11-04). Preston: "ok now sel out for
our moba style using what we've collected".

The MOBA creatures follow the Hollowtide sprite canon, where the outline comes from the sel-out shader
(hollowtide docs/art/crew-dungeon-selout-2026-10-10/candidate/scripts/arena/sel_out.gdshaderinc) instead of being
painted. This game has no such shader, so its creature rules are applied here per pixel, exactly:
  1. a transparent pixel whose up, down, left or right neighbour is a light or material colour (luma 0.23 or more)
     becomes the outline colour: one texel of outline outside the silhouette;
  2. a silhouette edge pixel (a transparent pixel up, down, left or right of it) darker than luma 0.23 is darkened
     to the outline colour (per channel minimum), so existing dark edges get no extra thickness;
  3. the shader's speck cleanup only merges colours closer than 0.12 with luma over 0.16; no two rhino colours
     are that close, so it changes nothing here and is left out; its detail-ink mode is off for creatures.
Outline colour: the rhino palette's darkest, #141218 (the shader's #0B0E11 would add a 13th colour; they differ by
under 10 per channel). The feet still stand on y=160; under a light foot edge the outline sits on y=161.
Reads every sheet's frames/ and writes frames_selout/ beside it, so rerun after any fix to the frames.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ANIM = Path(__file__).parent
OUTLINE = np.array([0x14, 0x12, 0x18], np.uint8)
SHEETS = [ANIM / "codex-set-a" / s for s in ("idle", "walk", "horn-jab", "horn-toss")] + \
         [ANIM / "codex-set-b" / s for s in ("brace", "stampede", "death")] + [ANIM / "codex-ground-pound/clean"] + \
         [ANIM / "codex-set-c" / s for s in ("stampede", "horn-toss", "ground-pound", "horn-jab")] + \
         [ANIM / "codex-set-d" / s for s in ("brace", "death", "idle", "brace-shuffle")]  # se/ne rows, shuffle


def selout(a):
    op = a[..., 3] > 127
    luma = (a[..., :3].astype(float) / 255) @ np.array([0.2126, 0.7152, 0.0722])
    light = op & (luma >= 0.23)

    def nb(m, fill):
        p = np.pad(m, 1, constant_values=fill)
        return p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]

    repair = ~op & np.logical_or.reduce(nb(light, False))
    edge = op & np.logical_or.reduce([~x for x in nb(op, False)])
    dark_edge = edge & (luma < 0.23)
    out = a.copy()
    out[dark_edge, :3] = np.minimum(a[dark_edge, :3], OUTLINE)
    out[repair, :3] = OUTLINE
    out[repair, 3] = 255
    return out, int(repair.sum()), int(dark_edge.sum())


def main():
    total, pairs = [], []
    for d in SHEETS:
        src, dst = d / "frames", d / "frames_selout"
        dst.mkdir(exist_ok=True)
        for p in sorted(src.glob("*_f[0-9].png")):
            a = np.asarray(Image.open(p).convert("RGBA"))
            b, added, darkened = selout(a)
            Image.fromarray(b).save(dst / p.name)
            total.append((d.name, p.stem, added, darkened))
            if p.stem in ("front_f0", "side_f0", "back_f0") and d.name == "idle" or \
               (d.name, p.stem) in {("horn-jab", "side_f3"), ("stampede", "front_f3"), ("death", "side_f4")}:
                pairs.append((f"{d.name} {p.stem}", a, b))
    added = [t[2] for t in total]
    print(f"{len(total)} frames; outline pixels added per frame {min(added)}-{max(added)}; "
          f"dark edge pixels darkened {sum(t[3] for t in total)} in all")
    # before | after at 4x on the MOBA map grey
    k, box = 4, (24, 72, 168, 166)
    w, h = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    board = Image.new("RGBA", (2 * w + 8, len(pairs) * (h + 16)), (0x5A, 0x60, 0x58, 255))
    dr = ImageDraw.Draw(board)
    for j, (lab, a, b) in enumerate(pairs):
        y = j * (h + 16)
        dr.text((4, y + 2), f"{lab}   left: before   right: sel-out", fill=(240, 240, 240, 255))
        for i, im in enumerate((a, b)):
            board.alpha_composite(Image.fromarray(im).crop(box).resize((w, h), Image.NEAREST), (i * (w + 8), y + 16))
    board.save(ANIM / "selout-board.png")
    print("board", board.size)


if __name__ == "__main__":
    main()
