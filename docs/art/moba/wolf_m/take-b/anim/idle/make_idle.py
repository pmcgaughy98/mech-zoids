"""The wolf's idle in five views, built from the approved stills (Claude, animation lane, 2026-11-04).

Preston: "let's go to wolf kit and animations". The approved stills are take-b/fixed/ (192x192, feet on row 160,
standing; Preston 2026-11-03: "do the back view fix looks good though"; the n still carries today's capped ink).
Same method as the fennec's idle: native approved pixels only; everything above the legs (above CUT, the top row
where the legs show as separate columns, counted from 4 rows above the ground) lifts 0, 1, 1, 1, 0 px, the row at CUT repeats under it, the feet never move.
Frame 0 and frame 4 are the still exactly. Preview 220 ms a frame, looping.
Writes frames/<front|se|side|ne|back>_f0-4.png, board.png and preview.gif.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
TAKE = HERE.parents[1]
VIEWS = {"front": "s", "se": "se", "side": "e", "ne": "ne", "back": "n"}
LIFT = [0, 1, 1, 1, 0]
sys.path.insert(0, str(TAKE.parents[1] / "rhino_l/take-a/anim"))


def runs(row):
    return int((np.diff(np.concatenate([[0], row.astype(int), [0]])) == 1).sum())


def cut_row(op):
    ys = np.nonzero(op.any(1))[0]
    y = ys.max() - 4  # a few rows up: one foot or the tail tip alone can touch the ground row
    while y > ys.min() and runs(op[y]) >= 2:
        y -= 1
    return y + 1  # first row (from the top) of the leg zone


def main():
    import selout_rhino
    a0 = np.asarray(Image.open(TAKE / "fixed" / "s.png").convert("RGBA"))
    cols = np.unique(a0[a0[..., 3] > 0][:, :3], axis=0)
    selout_rhino.OUTLINE = cols[int(np.argmin(cols.astype(float) @ [0.2126, 0.7152, 0.0722]))].astype(np.uint8)
    rows, cuts = [], {}
    for name, v in VIEWS.items():
        st = np.asarray(Image.open(TAKE / "fixed" / f"{v}.png").convert("RGBA"))
        # the back view's tail runs down between the legs and joins them, so it takes the front's cut (same heights
        # since fix_backs.py)
        cut = cuts["front"] if name == "back" else cut_row(st[..., 3] > 0)
        cuts[name] = cut
        fr = []
        for k in LIFT:
            f = st.copy()
            if k:
                f[:cut - k] = st[k:cut]
                f[cut - k:cut] = st[cut - 1]
            fr.append(f)
        for i, f in enumerate(fr):
            Image.fromarray(f).save(HERE / "frames" / f"{name}_f{i}.png")
        print(f"{name} ({v}): cut row {cut}, legs {160 - cut + 1} px")
        rows.append(fr)
    z, box = 3, (24, 70, 168, 166)
    w, h = (box[2] - box[0]) * z, (box[3] - box[1]) * z
    board = Image.new("RGBA", (5 * w, 5 * h), (0x3D, 0x43, 0x50, 255))
    tiles = [[Image.fromarray(selout_rhino.selout(f)[0]).crop(box).resize((w, h), Image.NEAREST) for f in r] for r in rows]
    for r, row in enumerate(tiles):
        for c, t in enumerate(row):
            board.alpha_composite(t, (c * w, r * h))
    board.save(HERE / "board.png")
    gif = []
    for i in range(5):
        f = Image.new("RGBA", (5 * w, h), (0x3D, 0x43, 0x50, 255))
        for c in range(5):
            f.alpha_composite(tiles[c][i], (c * w, 0))
        gif.append(f.convert("RGB"))
    gif[0].save(HERE / "preview.gif", save_all=True, append_images=gif[1:], duration=220, loop=0)
    print("outline", bytes(selout_rhino.OUTLINE).hex())


if __name__ == "__main__":
    main()
