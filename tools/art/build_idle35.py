"""35-degree idles for machines whose 35-degree views are final (Claude, animation lane, 2026-11-05).

Hub, relaying Preston's "get every session going": build the idles by script, board them, do not install or pack.
Method: the rhino's cam35-idle/build_cam35_idle.py (the playbook's diag_idle.py), approved with the rhino idle. The body
rises 0, 1, 1, 1, 0 px above a cut row (f0-f4 at 200 ms), the row just over the cut is repeated to close the gap, and
everything from the cut down never moves. Frame 0 is the still.

The cut is set per view by eye on a marked strip of the lower body, as for the rhino: from 35 degrees the far feet sit
higher on the page, so the cut goes above every foot (a foot above the cut would stretch and lift). The board's third
column marks in red every pixel that changes on the raised frames, which is how a lifted foot would show.

Writes, per machine, <take>/anim/idle35/: frames/ (raw), frames_selout/ (the game's sel-out, the machine's darkest
colour), board.png, idle.gif (3x, the breath at 200 ms), build_check.txt. Names follow the packers: front, se, side,
ne, back. Reads the newest approved views (source()). Run: python tools/art/build_idle35.py [machine ...]
(default: all ready)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MOBA = ROOT / "docs/art/moba"
sys.path.insert(0, str(MOBA / "rhino_l/take-a/anim"))
import selout_rhino  # noqa: E402

NAMES = [("s", "front"), ("se", "se"), ("e", "side"), ("ne", "ne"), ("n", "back")]
LIFT = [0, 1, 1, 1, 0]
MS = 200
# take folder, feet row (the lowest still row), cut row per view (rows from the cut down never move).
MACHINES = {
    "fennec": ("fennec_s/take-b", 140, {"s": 126, "se": 118, "e": 120, "ne": 114, "n": 120}),
    "gorilla": ("ape_l/take-a", 130, {"s": 100, "se": 100, "e": 104, "ne": 104, "n": 104}),
    # wolf ne: the far front paw hangs at rows 117-126 and the near one starts at 116, so the cut sits at 116 (128 lifted
    # the far paw and split the near one; seen on the zoom, 2026-11-05).
    "wolf": ("wolf_m/take-b", 160, {"s": 144, "se": 133, "e": 140, "ne": 116, "n": 132}),
    # hippo: final after its turn test (hub, 2026-11-05: "Turn test, then accept"). Far feet sit at about rows 125-140
    # in se, ne and n, so those cut higher.
    "hippo": ("hippo_l/take-b", 160, {"s": 138, "se": 122, "e": 136, "ne": 122, "n": 122}),
}
READY = ["fennec", "gorilla", "wolf", "hippo"]


# Newest first. A folder counts only when Preston kept it (it has an APPROVED.txt). shade1 is the touch-up plus a 1 px
# shade pass (hippo, kept 2026-11-05 "Keep 1 px version", docs/art/moba/touchup/LOG.md section 9); it supersedes the
# plain touch-up. A new pass gets a line here, at the front.
SOURCES = ["views_cam35_touchup_shade1", "views_cam35_touchup"]


def source(take):
    """The newest approved 35-degree views (SOURCES), else views_cam35. The first build (2026-11-05 morning) used
    views_cam35 for all; each idle is rebuilt when a newer set is kept. Touch-ups and shade passes are recolours that
    keep the alpha, so the cuts still hold (build() checks the alpha against views_cam35)."""
    for name in SOURCES:
        if (MOBA / take / name / "APPROVED.txt").exists():
            return MOBA / take / name
    return MOBA / take / "views_cam35"


def breath(a, k, cut):
    if k == 0:
        return a.copy()
    out = a.copy()
    out[:cut - k] = a[k:cut]
    out[cut - k:cut] = a[cut - 1]
    return out


def darkest(a):
    cols = np.unique(a[a[..., 3] > 0][:, :3], axis=0)
    return cols[int(np.argmin(cols.astype(float) @ [0.2126, 0.7152, 0.0722]))].astype(np.uint8)


def build(machine):
    take, feet, cut = MACHINES[machine]
    views = source(take)
    # Its own folder. Until 2026-11-05 this wrote anim/cam35-idle/, which is where the install scripts (the fleet redraw
    # lane's build_cam35_idle.py, 192 cells for the packers) write; a rebuild here overwrote the fennec's packed source.
    out = MOBA / take / "anim/idle35"
    for sub in ("frames", "frames_selout"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    selout_rhino.OUTLINE = darkest(np.asarray(Image.open(views / "s.png").convert("RGBA")))
    lines, rows = [], []
    for v, name in NAMES:
        still = np.asarray(Image.open(views / f"{v}.png").convert("RGBA")).copy()
        base = np.asarray(Image.open(MOBA / take / "views_cam35" / f"{v}.png").convert("RGBA"))
        assert (still[..., 3] == base[..., 3]).all(), f"{machine} {v}: {views.name} alpha differs from views_cam35"
        ys = np.nonzero(still[..., 3] > 0)[0]
        assert ys.max() == feet, f"{machine} {v}: lowest row {ys.max()}, want {feet}"
        frames = [breath(still, k, cut[v]) for k in LIFT]
        sel = []
        for i, f in enumerate(frames):
            assert (f[cut[v]:] == still[cut[v]:]).all()
            Image.fromarray(f).save(out / "frames" / f"{name}_f{i}.png")
            s = selout_rhino.selout(f.copy())[0]
            Image.fromarray(s).save(out / "frames_selout" / f"{name}_f{i}.png")
            sel.append(s)
        moved = int(((frames[2] != frames[0]).any(2)).sum())
        lines.append(f"{name} ({v}): cut row {cut[v]} ({feet - cut[v]} rows over the feet row), top row {ys.min()}, "
                     f"f0 = still {(frames[0] == still).all()}, {moved} px change on the raised frames")
        rows.append((v, name, still, frames, sel, cut[v]))
    (out / "build_check.txt").write_text(f"source {views.name}; outline #{bytes(selout_rhino.OUTLINE).hex()}\n"
                                         + "\n".join(lines) + "\n")
    board(machine, out, rows, feet)
    gif(out, rows, feet)
    print(machine, "source", views.name, "outline", bytes(selout_rhino.OUTLINE).hex(), *lines, sep="\n  ")


def crop_box(rows, feet):
    top = min(int(np.nonzero(r[2][..., 3] > 0)[0].min()) for r in rows) - 3
    return top, feet + 3


def board(machine, out, rows, feet):
    k = 3
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 16)
    top, bot = crop_box(rows, feet)
    w = rows[0][2].shape[1]
    cw, ch = w * k, (bot - top) * k
    img = Image.new("RGB", (3 * (cw + 8), 26 + len(rows) * (ch + 26)), (60, 66, 62))
    d = ImageDraw.Draw(img)
    for c, t in enumerate(("still, cut row in cyan", "raised frame (f2)", "red: pixels that change")):
        d.text((c * (cw + 8) + 6, 4), t, fill=(240, 220, 120), font=font)
    for r, (v, name, still, frames, sel, cut) in enumerate(rows):
        y0 = 26 + r * (ch + 26)
        d.text((4, y0 + 4), f"{r + 1}  {machine} {v}  (cut {cut})", fill=(255, 255, 255), font=font)
        diff = np.zeros_like(still)
        op = still[..., 3] > 0
        diff[op] = (110, 116, 112, 255)
        ch_ = (frames[2] != frames[0]).any(2)
        diff[ch_] = (230, 40, 40, 255)
        for c, a in enumerate((sel[0], sel[2], diff)):
            im = Image.fromarray(a).crop((0, top, w, bot)).resize((cw, ch), Image.NEAREST)
            x0 = c * (cw + 8)
            img.paste(im, (x0, y0 + 24), im)
            if c == 0:
                yy = y0 + 24 + (cut - top) * k
                d.line([(x0, yy), (x0 + cw, yy)], fill=(80, 230, 255), width=2)
    img.save(out / "board.png")


def gif(out, rows, feet):
    k = 3
    top, bot = crop_box(rows, feet)
    w = rows[0][2].shape[1]
    frames = []
    for i in range(len(LIFT)):
        img = Image.new("RGB", (len(rows) * w * k, (bot - top) * k), (78, 92, 84))
        for c, row in enumerate(rows):
            im = Image.fromarray(row[4][i]).crop((0, top, w, bot)).resize((w * k, (bot - top) * k), Image.NEAREST)
            img.paste(im, (c * w * k, 0), im)
        frames.append(img)
    frames[0].save(out / "idle.gif", save_all=True, append_images=frames[1:], duration=MS, loop=0)


if __name__ == "__main__":
    for m in sys.argv[1:] or READY:
        build(m)
