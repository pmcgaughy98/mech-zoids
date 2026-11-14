"""Finish the PixelLab death front like the approved stills (Preston: "Looks good just needs sell out cap ink etc.").

Runs the lane's own touchup_machine.py passes, with the fennec's run settings (defaults: --cap 0.80 --rim 3), on
f1-f5 of frames/ (cleaned PixelLab skeleton frames): specks, capped ink seams, bevel rims, charcoal gaps (capped at
0.80 x the approved s still's dark share). Recolour only: alpha never changes, so the pose and the death rules hold.
Eyes and the ring around them are never touched. f0 stays the still; f6 is rebuilt from f5 with the eyes out.
Sel-out is the game's: the packer adds it (rhino ruling "Keep, game sel-out"); boards show it.
Writes finished/front_f0-6.png, finish_report.json, board_finish.png, front_death_finished.gif.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
MACH = Path(r"D:/dev/new-mech-rpg/docs/art/moba/touchup/touchup_machine.py")
sys.argv = ["touchup_machine.py", "fennec_s/take-b"]
spec = importlib.util.spec_from_file_location("machine", MACH)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
sys.path.insert(0, str(HERE))
import clean_death as C  # noqa: E402

OUT = HERE / "finished"
LIVE = C.LIVE


INK_SHARE = float((M.codes(C.still) == M.SEAM).sum()) / float((C.still[..., 3] > 0).sum())   # 5.0%, the still's
LINE_DARK = ["2e1a6e", "211e27", "3d3a44"]
CLEANUP = json.loads((HERE / "report.json").read_text())["main"]["cleanup"]
RAW_OF = {1: 0, 2: 1, 3: 2, 4: 3, 5: 5}


def raw_luma(i):
    """Luma of PixelLab's own raw pixel under each frame pixel (before the snap to 15 colours), lift applied."""
    r = np.asarray(Image.open(HERE / f"raw/f{RAW_OF[i]}.png").convert("RGBA")).astype(float)
    r = np.roll(r, -CLEANUP[f"f{i}"].get("lifted", 0), 0)
    lum = 0.2126 * r[..., 0] + 0.7152 * r[..., 1] + 0.0722 * r[..., 2]
    lum[r[..., 3] == 0] = 999
    return lum


def ink_lines(h, lum, guard, target_px):
    """Capped ink, part lines: the still's #141218 is all inside the shape (0% on the silhouette edge): eye ring,
    ear joins, plate and leg splits. PixelLab drew those lines one shade light. A dark pixel inside the shape that
    is a 1 px line between lit pixels (both neighbours across it opaque and not dark) becomes ink, darkest raw pixel
    first, up to the still's ink share. The outer edge is left to the game's sel-out."""
    have = int((h == M.SEAM).sum())
    need = max(0, target_px - have)
    op = h != ""
    cand = []
    for y, x in zip(*np.nonzero(np.isin(h, LINE_DARK) & ~guard)):
        if not all(op[y + dy, x + dx] for dy, dx in M.N4):
            continue
        pairs = 0
        for d1, d2 in M.OPP:
            c1, c2 = M.nb(h, y, x, d1), M.nb(h, y, x, d2)
            if c1 and c2 and c1 not in LINE_DARK + [M.SEAM] and c2 not in LINE_DARK + [M.SEAM]:
                pairs += 1
        if pairs:
            cand.append((lum[y, x] - 8 * pairs, y, x))
    cand.sort()
    for _, y, x in cand[:need]:
        h[y, x] = M.SEAM
    return min(need, len(cand)), len(cand)


def shares(h):
    op = (h != "").sum()
    return {"ink_141218": round(100 * float((h == M.SEAM).sum()) / op, 1),
            "frame_plus_seam": round(100 * M.dark_share(h), 1),
            "highlight": round(100 * float(np.isin(h, M.HILITE).sum()) / op, 1)}


def main():
    OUT.mkdir(exist_ok=True)
    still = C.still
    hs = M.codes(still)
    target = M.CAP * M.dark_share(hs)
    fr = [np.asarray(Image.open(HERE / f"frames/front_f{i}.png").convert("RGBA")) for i in range(6)]
    rep = {"still": shares(hs), "gap_target_pct": round(100 * target, 1)}
    new = [still.copy()]
    for i in range(1, 6):
        a = fr[i]
        h = M.codes(a)
        before = shares(h)
        guard = M.eye_guard(h)
        sp = M.specks(h, guard)
        sm, valleys = M.seams(h, guard)
        rm = M.rims(h, guard, M.RIM, 40)
        gp, cand = M.gaps(h, guard, target)
        ik, ic = ink_lines(h, raw_luma(i), guard, int(round(INK_SHARE * (h != "").sum())))
        b = M.paint(a, h)
        assert np.array_equal(b[..., 3], a[..., 3])
        rep[f"f{i}"] = {"before": before, "after": shares(h), "specks": sp, "seam_ink_px": sm, "valleys": valleys,
                        "rim_px": rm, "gap_px": gp, "gap_candidates": cand, "ink_line_px": ik, "ink_candidates": ic,
                        "changed_px": int(np.any(a != b, -1).sum())}
        new.append(b)
    f6 = new[5].copy()
    eye = np.array([tuple(c) in C.EYES for c in f6[..., :3].reshape(-1, 3)]).reshape(f6.shape[:2]) & (f6[..., 3] > 0)
    f6[eye, :3] = C.VS
    new.append(f6)
    per, ok, extra = C.rules(new)
    rep["rules_all_pass"] = bool(ok)
    rep.update(extra)
    for i, a in enumerate(new):
        Image.fromarray(a).save(OUT / f"front_f{i}.png")
    (HERE / "finish_report.json").write_text(json.dumps(rep, indent=1))
    print("still", rep["still"], "gap target", rep["gap_target_pct"])
    for i in range(1, 6):
        r = rep[f"f{i}"]
        print(f"f{i}", "before", r["before"], "after", r["after"], "| specks", r["specks"], "ink", r["seam_ink_px"],
              "rim", r["rim_px"], "gaps", r["gap_px"], "ink lines", r["ink_line_px"], "of", r["ink_candidates"],
              "changed", r["changed_px"])
    print("RULES", ok, extra)
    board(fr + [None], new)


def board(old, new):
    live = [np.asarray(Image.open(LIVE / f"front_f{i}.png").convert("RGBA")) for i in range(7)]
    prev = [np.asarray(Image.open(HERE / f"frames/front_f{i}.png").convert("RGBA")) for i in range(7)]
    al = np.zeros((160, 160), bool)
    for a in new + prev:
        al |= a[..., 3] > 0
    ys, xs = np.nonzero(al)
    box = (int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, 143)
    k = 4
    cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    grey = (0x5A, 0x60, 0x58, 255)
    rows = [("PixelLab, cleaned (last look)", prev, True), ("finished: capped ink, rims, gaps", new, True),
            ("finished, raw (no game sel-out)", new, False)]
    B = Image.new("RGBA", (200 + 7 * (cw + 6), len(rows) * (ch + 24) + (box[3] - box[1]) + 40), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 22
    for lab, fr, out in rows:
        d.text((8, y + 6), lab, fill=(235, 235, 230, 255))
        for i, a in enumerate(fr):
            img = C.selout(a)[0] if out else a
            c = Image.fromarray(img).crop(box).resize((cw, ch), Image.NEAREST)
            x = 200 + i * (cw + 6)
            d.rectangle([x, y, x + cw, y + ch], fill=grey)
            B.alpha_composite(c, (x, y))
            if y == 22:
                d.text((x + 4, y - 16), f"f{i}  {C.MS[i]} ms", fill=(235, 235, 230, 255))
        y += ch + 24
    d.text((8, y), "1x, game sel-out", fill=(235, 235, 230, 255))
    for i, a in enumerate(new):
        c = Image.fromarray(C.selout(a)[0]).crop(box)
        x = 200 + i * (c.width + 6)
        d.rectangle([x, y, x + c.width, y + c.height], fill=grey)
        B.alpha_composite(c, (x, y))
    B.save(HERE / "board_finish.png")
    gif = []
    k2 = 3
    bw, bh = (box[2] - box[0]) * k2, (box[3] - box[1]) * k2
    for a in new:
        F = Image.new("RGBA", (bw + 10, bh + 10), grey)
        F.alpha_composite(Image.fromarray(C.selout(a)[0]).crop(box).resize((bw, bh), Image.NEAREST), (5, 5))
        gif.append(F.convert("RGB"))
    gif[0].save(HERE / "front_death_finished.gif", save_all=True, append_images=gif[1:], duration=C.MS, loop=0)


if __name__ == "__main__":
    main()
