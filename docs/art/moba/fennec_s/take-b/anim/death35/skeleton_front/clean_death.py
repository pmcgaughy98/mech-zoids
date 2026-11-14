"""Fennec death front, from PixelLab animate_with_skeleton_v3 (job 76809977, hand-posed skeletons in keypoints.py).

Raw frames (raw/f0-f5): recoil, sag, buckle, topple, down, flat. Death35 layout:
f0 = the approved still exactly; f1-f4 = raw f0-f3; f5 = raw f5 (flat, head on the ground; raw f4 kept as the alt);
f6 = f5 with the eye lights out (#2E1A6E), same as build_death.py.
Cleanup (no pose change): nearest of the still's 15 colours, lift to the ground line (lowest row 140), 1 px specks,
spurs and notches, enclosed holes filled, loose bits under 13 px dropped. Then the death35 rules from check_death.py.
"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label

TAKE = Path(r"D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b")
LIVE = TAKE / "anim/death35/frames"
HERE = Path(__file__).parent
OUT = HERE / "frames"
N4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]
EIGHT = np.ones((3, 3), int)
MS = [300, 100, 130, 140, 160, 180, 1400]
VS = (0x2E, 0x1A, 0x6E)
sys.path.insert(0, str(TAKE.parent.parent / "rhino_l/take-a/anim"))
from selout_rhino import selout  # noqa: E402

still = np.asarray(Image.open(HERE / "still_s.png").convert("RGBA"))
sm = still[..., 3] > 0
PAL = np.unique(still[sm][:, :3], axis=0).astype(int)
EYES = {(63, 232, 176), (200, 255, 240), (246, 255, 251)}
PALSET = {tuple(c) for c in PAL}


def snap(a):
    b = a.copy()
    m = a[..., 3] > 0
    d = ((a[m][:, None, :3].astype(int) - PAL[None]) ** 2).sum(-1)
    b[m, :3] = PAL[d.argmin(1)]
    b[~m] = 0
    return b


def clean(a, log):
    H, W = a.shape[:2]
    ys = np.nonzero(a[..., 3] > 0)[0]
    dy = min(0, 140 - int(ys.max()))
    if dy:
        a = np.roll(a, dy, 0)
        log["lifted"] = -dy
    for _ in range(4):
        ch = 0
        m = a[..., 3] > 0
        for y, x in zip(*np.nonzero(m)):
            c = tuple(a[y, x, :3])
            on = [(y + j, x + i) for j, i in N4 if m[y + j, x + i]]
            if len(on) <= 1:
                a[y, x] = 0
                log["spurs"] += 1
                ch += 1
                continue
            if c in EYES:
                continue
            cols = Counter(tuple(a[p][:3]) for p in on)
            top, n = cols.most_common(1)[0]
            near8 = {tuple(a[y + j, x + i, :3]) for j in (-1, 0, 1) for i in (-1, 0, 1) if (j or i) and m[y + j, x + i]}
            if top != c and (n == 4 or (n >= 3 and c not in near8)):
                a[y, x, :3] = top
                log["specks"] += 1
                ch += 1
        m = a[..., 3] > 0
        for y, x in zip(*np.nonzero(~m)):
            if 0 < y < 140 and 0 < x < W - 1:
                on = [(y + j, x + i) for j, i in N4 if m[y + j, x + i]]
                if len(on) >= 3:
                    a[y, x, :3] = Counter(tuple(a[p][:3]) for p in on).most_common(1)[0][0]
                    a[y, x, 3] = 255
                    log["notches"] += 1
                    ch += 1
        if not ch:
            break
    hl, hn = label(binary_fill_holes(a[..., 3] > 0) & (a[..., 3] == 0))
    for k in range(1, hn + 1):
        pts = list(zip(*np.nonzero(hl == k)))
        for y, x in pts:
            on = [(y + j, x + i) for j, i in N4 if a[y + j, x + i, 3] > 0]
            a[y, x, :3] = Counter(tuple(a[p][:3]) for p in on).most_common(1)[0][0] if len(pts) <= 4 and on else VS
            a[y, x, 3] = 255
        log["holes_filled_px"] += len(pts)
    lab, n = label(a[..., 3] > 0, EIGHT)
    if n > 1:
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        main = int(sizes.argmax())
        for k in range(1, n + 1):
            if k != main and sizes[k] < 13:
                a[lab == k] = 0
                log["loose_px_dropped"] += int(sizes[k])
    return a


def rules(fr):
    out = {}
    for i, a in enumerate(fr):
        m = a[..., 3] > 0
        ys, xs = np.nonzero(m)
        out[f"f{i}"] = {
            "binary_alpha": set(np.unique(a[..., 3]).tolist()) <= {0, 255},
            "off_palette": int(sum(1 for c in a[m][:, :3] if tuple(c) not in PALSET)),
            "edge": bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any()),
            "holes": int((binary_fill_holes(m) & ~m).sum()),
            "pieces8": int(label(m, EIGHT)[1]),
            "lowest": int(ys.max()), "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]}
    ok = all(r["binary_alpha"] and not r["off_palette"] and not r["edge"] and not r["holes"] and r["pieces8"] == 1
             and r["lowest"] <= 140 for r in out.values())
    f56 = np.array_equal(fr[5][..., 3], fr[6][..., 3])
    diff = np.any(fr[5] != fr[6], -1)
    only_eyes = all(tuple(fr[5][y, x, :3]) in EYES for y, x in zip(*np.nonzero(diff)))
    return out, ok and np.array_equal(fr[0], still) and f56 and only_eyes, {"f0_is_still": bool(np.array_equal(fr[0], still)),
                                                                              "f5_f6_alpha_same": bool(f56), "f6_differs_only_at_eyes": bool(only_eyes)}


def build(f5_raw):
    raw = [np.asarray(Image.open(HERE / f"raw/f{i}.png").convert("RGBA")) for i in range(6)]
    fr, logs = [still.copy()], {}
    for i, r in enumerate([raw[0], raw[1], raw[2], raw[3], raw[f5_raw]], start=1):
        log = Counter()
        snapped = snap(r)
        a = clean(snapped.copy(), log)
        log["changed_by_cleanup"] = int(np.any(a != snapped, -1).sum())
        fr.append(a)
        logs[f"f{i}"] = dict(log)
    f6 = fr[5].copy()
    eye = np.array([tuple(c) in EYES for c in f6[..., :3].reshape(-1, 3)]).reshape(f6.shape[:2]) & (f6[..., 3] > 0)
    f6[eye, :3] = VS
    fr.append(f6)
    return fr, logs


def strip(fr, box, k, outline):
    cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    S = Image.new("RGBA", (len(fr) * (cw + 4), ch), (0, 0, 0, 0))
    for i, a in enumerate(fr):
        img = selout(a)[0] if outline else a
        c = Image.fromarray(img).crop(box).resize((cw, ch), Image.NEAREST)
        S.alpha_composite(c, (i * (cw + 4), 0))
    return S


def main():
    OUT.mkdir(exist_ok=True)
    live = [np.asarray(Image.open(LIVE / f"front_f{i}.png").convert("RGBA")) for i in range(7)]
    report = {}
    sets = {}
    for name, f5r in (("main", 5), ("alt", 4)):
        fr, logs = build(f5r)
        per, ok, extra = rules(fr)
        report[name] = {"cleanup": logs, "rules": per, "all_pass": bool(ok), **extra}
        print(name, "ALL RULES", ok, extra, "| cleanup", logs)
        sets[name] = fr
    for i, a in enumerate(sets["main"]):
        Image.fromarray(a).save(OUT / f"front_f{i}.png")
    Image.fromarray(sets["alt"][5]).save(OUT / "front_f5_alt.png")
    (HERE / "report.json").write_text(json.dumps(report, indent=1))
    al = np.zeros((160, 160), bool)
    for a in live + sets["main"] + sets["alt"]:
        al |= a[..., 3] > 0
    ys, xs = np.nonzero(al)
    box = (int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, 143)
    grey = (0x5A, 0x60, 0x58, 255)
    rows = [("live (rejected ears)", live, 3), ("new: PixelLab skeleton", sets["main"], 3), ("new at game size 1x", sets["main"], 1)]
    W = 230 + 7 * ((box[2] - box[0]) * 3 + 8)
    Hh = sum((box[3] - box[1]) * k + 26 for *_, k in rows) + 20
    B = Image.new("RGBA", (W, Hh), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 22
    for lab, fr, k in rows:
        d.text((8, y + 6), lab, fill=(235, 235, 230, 255))
        S = strip(fr, box, k, True)
        cw = (box[2] - box[0]) * k
        for i in range(7):
            x = 230 + i * (cw + (8 if k == 3 else 4))
            d.rectangle([x, y, x + cw, y + (box[3] - box[1]) * k], fill=grey)
            B.alpha_composite(S.crop((i * (cw + 4), 0, i * (cw + 4) + cw, S.height)), (x, y))
            if k == 3 and lab.startswith("live"):
                d.text((x + 4, y - 16), f"f{i}  {MS[i]} ms", fill=(235, 235, 230, 255))
        y += (box[3] - box[1]) * k + 26
    B.save(HERE / "board_death_front.png")
    gif = []
    k = 3
    bw = (box[2] - box[0]) * k
    for a, b in zip(live, sets["main"]):
        F = Image.new("RGBA", (2 * bw + 30, (box[3] - box[1]) * k + 20), grey)
        for n, (lab, arr) in enumerate((("live", a), ("new", b))):
            c = Image.fromarray(selout(arr)[0]).crop(box)
            F.alpha_composite(c.resize((bw, (box[3] - box[1]) * k), Image.NEAREST), (5 + n * (bw + 20), 15))
            ImageDraw.Draw(F).text((8 + n * (bw + 20), 2), lab, fill=(255, 255, 255, 255))
        gif.append(F.convert("RGB"))
    gif[0].save(HERE / "front_death_live_vs_new.gif", save_all=True, append_images=gif[1:], duration=MS, loop=0)
    # PixelLab score strip: the 7 new frames, cropped, 1x, no outline
    s = strip(sets["main"], (box[0], box[1], box[2], 143), 1, False)
    s.save(HERE / "score_strip.png")
    print("box", box, "strip", s.size)


if __name__ == "__main__":
    main()
