"""Fennec death front, finish 2. Preston on finish 1: "Needs more ink" and "kind of looks flat towards end animations".

Starts from frames/ (cleaned PixelLab skeleton frames). Recolour only: alpha never changes, so the pose and the
death rules hold. Per frame f1-f5, in order:
1. touchup_machine.py passes (fennec settings): specks, capped-ink seams, bevel rims, charcoal gaps.
2. Volume, measured against the approved s still (light top-left-front, as the fleet):
   a. highlight caps: each base-shade plate (violet, gold, steel; 20+ px) gets its highlight shade on a band
      along its top edge (and one less on its left edge); band depth 1-3 picked per frame so the highlight share
      lands closest to the still's without passing it.
   b. shade_pass.py: shadow plates sink to the deepest shade (d1) and base plates get a dark bevel on their bottom
      and right edges (d2), each picked so the share lands closest to the still's without passing it.
3. Ink, more than finish 1 (capped at INK_X x the still's ink share), darkest raw PixelLab pixel first:
   A. 1 px dark lines between lit pixels, B. the shadow-side pixel of 2 px dark bands,
   C. part edges (violet / gold / steel / charcoal meeting, inside the shape): the shadow-side pixel (below or
   right). Never on the silhouette edge (the game's sel-out owns it), never within 2 px of an eye, no blobs.
f0 stays the still; f6 = f5 with the eye lights out. Writes finished2/, finish2_report.json, board_finish2.png,
front_death_finished2.gif.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import finish_death as F  # noqa: E402  (loads touchup_machine as F.M, clean_death as F.C)

M, C = F.M, F.C
sys.argv = ["shade_pass.py", "fennec_s/take-b"]
_s = importlib.util.spec_from_file_location("shade", r"D:/dev/new-mech-rpg/docs/art/moba/touchup/shade_pass.py")
SP = importlib.util.module_from_spec(_s)
_s.loader.exec_module(SP)

INK_X = 1.5
OUT = HERE / "finished2"
FAM = {h: r for r, hs in M.ROLES.items() for h in hs}
PLATES = [sorted(hs, key=M._luma) for r, hs in M.ROLES.items() if r in ("violet", "cream-gold", "steel")]


def hi_share(h):
    return float(np.isin(h, M.HILITE).sum()) / float((h != "").sum())


def caps(h, guard, depth, rp):
    out = h.copy()
    base, hi = rp[-2], rp[-1]
    plate = (h == base) | (h == hi)
    lab, sizes = SP.comps(plate)
    big = SP.big_mask(lab, sizes, plate, 20)
    dt, dl = SP.edge_dist(plate, (-1, 0)), SP.edge_dist(plate, (0, -1))
    out[big & (h == base) & ((dt < depth) | (dl < depth - 1)) & ~guard] = hi
    return out


def volume(h, guard, ref):
    log = {"cap_depth": {}}
    nref, n = float((ref != "").sum()), float((h != "").sum())
    for rp in PLATES:     # per family: exactly the cap pixels needed to reach the still's highlight share
        base, hi = rp[-2], rp[-1]
        need = int(round(float((ref == hi).sum()) / nref * n)) - int((h == hi).sum())
        if need <= 0:
            log["cap_depth"][FAM[hi]] = 0
            continue
        plate = (h == base) | (h == hi)
        lab, sizes = SP.comps(plate)
        dt, dl = SP.edge_dist(plate, (-1, 0)), SP.edge_dist(plate, (0, -1))
        cand = [(min(dt[y, x], dl[y, x] + 1), -sizes[lab[y, x]], y, x)          # top edges first, big plates first
                for y, x in zip(*np.nonzero((h == base) & ~guard & ((dt < 2) | (dl < 1))))
                if sizes[lab[y, x]] >= 20]
        cand.sort()
        h = h.copy()
        for _, _, y, x in cand[:need]:
            h[y, x] = hi
        log["cap_depth"][FAM[hi]] = min(need, len(cand))
    sa, s0 = SP.shares(ref), SP.shares(h)
    d1 = None
    if s0["deep"] < sa["deep"]:
        for d in (4, 3, 2, 1):
            hh = SP.sink_shadow(h, guard, d)
            if SP.shares(hh)["deep"] <= sa["deep"] + 0.5:
                d1, h1 = d, hh
        if d1:
            h = h1
    log["sink_d1"] = d1
    d2 = 0
    for d in range(1, SP.A.d2_max + 1):
        hh = SP.bevel_base(h, guard, d)
        if SP.shares(hh)["shadow"] <= sa["shadow"] + 0.5:
            d2 = d
    if d2:
        h = SP.bevel_base(h, guard, d2)
    log["bevel_d2"] = d2
    return h, log


def ink(h, lum, guard, target_px):
    op = h != ""
    H, W = h.shape
    inner = op.copy()
    for dy, dx in M.N4:
        inner &= np.roll(np.roll(op, -dy, 0), -dx, 1)
    dark = F.LINE_DARK
    lit = lambda c: c and c not in dark + [M.SEAM] and FAM.get(c) != "eye"
    stages = {"A": [], "B": [], "C": []}
    for y, x in zip(*np.nonzero(inner & ~guard)):
        c = h[y, x]
        if c == M.SEAM or FAM.get(c) == "eye":
            continue
        if c in dark:
            for d1, d2 in M.OPP:
                c1, c2 = M.nb(h, y, x, d1), M.nb(h, y, x, d2)
                if lit(c1) and lit(c2):
                    stages["A"].append((lum[y, x], y, x))
                    break
                # 2 px band, this pixel on its shadow side (below or right of the other dark pixel)
                if d1 in ((-1, 0), (0, -1)) and c1 in dark and lit(c2) and lit(M.nb(h, y, x, (2 * d1[0], 2 * d1[1]))):
                    stages["B"].append((lum[y, x], y, x))
                    break
        for d in ((-1, 0), (0, -1)):        # part edge: the neighbour above or left is another part
            q = M.nb(h, y, x, d)
            if q and q != M.SEAM and FAM.get(q) not in ("eye", None) and FAM.get(q) != FAM.get(c):
                stages["C"].append((lum[y, x], y, x))
                break
    have = int((h == M.SEAM).sum())
    added = {}
    for k in ("A", "B", "C"):
        n = 0
        for _, y, x in sorted(stages[k]):
            if have >= target_px:
                break
            if h[y, x] == M.SEAM:
                continue
            blob = sum(h[y + j, x + i] == M.SEAM for j in (-1, 0, 1) for i in (-1, 0, 1) if (j or i))
            if blob >= 4:
                continue
            h[y, x] = M.SEAM
            have += 1
            n += 1
        added[k] = n
    return added, {k: len(v) for k, v in stages.items()}


def main():
    OUT.mkdir(exist_ok=True)
    still = C.still
    hs = M.codes(still)
    gap_t = M.CAP * M.dark_share(hs)
    frames = [np.asarray(Image.open(HERE / f"frames/front_f{i}.png").convert("RGBA")) for i in range(6)]
    rep = {"still": {**F.shares(hs), **{"v_" + k: v for k, v in SP.shares(hs).items()}}, "ink_x": INK_X}
    new = [still.copy()]
    for i in range(1, 6):
        a = frames[i]
        h = M.codes(a)
        before = {**F.shares(h), **{"v_" + k: v for k, v in SP.shares(h).items()}}
        guard = M.eye_guard(h)
        M.specks(h, guard)
        M.seams(h, guard)
        M.rims(h, guard, M.RIM, 40)
        M.gaps(h, guard, gap_t)
        h, vlog = volume(h, guard, hs)
        added, cands = ink(h, F.raw_luma(i), guard, int(round(INK_X * F.INK_SHARE * (h != "").sum())))
        b = M.paint(a, h)
        assert np.array_equal(b[..., 3], a[..., 3])
        rep[f"f{i}"] = {"before": before, "after": {**F.shares(h), **{"v_" + k: v for k, v in SP.shares(h).items()}}, "volume": vlog,
                        "ink_added": added, "ink_candidates": cands, "changed_px": int(np.any(a != b, -1).sum())}
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
    (HERE / "finish2_report.json").write_text(json.dumps(rep, indent=1, default=float))
    print("still", rep["still"])
    for i in range(1, 6):
        r = rep[f"f{i}"]
        print(f"f{i}", "after", r["after"], r["volume"], "ink", r["ink_added"], "changed", r["changed_px"])
    print("RULES", ok, extra)
    board(new)


def board(new):
    prev = [np.asarray(Image.open(HERE / f"finished/front_f{i}.png").convert("RGBA")) for i in range(7)]
    al = np.zeros((160, 160), bool)
    for a in new:
        al |= a[..., 3] > 0
    ys, xs = np.nonzero(al)
    box = (int(xs.min()) - 2, int(ys.min()) - 2, int(xs.max()) + 3, 143)
    k = 4
    cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    grey = (0x5A, 0x60, 0x58, 255)
    rows = [("finish 1 (last look)", prev, True), ("finish 2: volume + more ink", new, True),
            ("finish 2, raw (no game sel-out)", new, False)]
    B = Image.new("RGBA", (220 + 7 * (cw + 6), len(rows) * (ch + 24) + (box[3] - box[1]) + 40), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 22
    for lab, fr, out in rows:
        d.text((8, y + 6), lab, fill=(235, 235, 230, 255))
        for i, a in enumerate(fr):
            img = C.selout(a)[0] if out else a
            c = Image.fromarray(img).crop(box).resize((cw, ch), Image.NEAREST)
            x = 220 + i * (cw + 6)
            d.rectangle([x, y, x + cw, y + ch], fill=grey)
            B.alpha_composite(c, (x, y))
            if y == 22:
                d.text((x + 4, y - 16), f"f{i}  {C.MS[i]} ms", fill=(235, 235, 230, 255))
        y += ch + 24
    d.text((8, y), "finish 2 at 1x, game sel-out", fill=(235, 235, 230, 255))
    for i, a in enumerate(new):
        c = Image.fromarray(C.selout(a)[0]).crop(box)
        x = 220 + i * (c.width + 6)
        d.rectangle([x, y, x + c.width, y + c.height], fill=grey)
        B.alpha_composite(c, (x, y))
    B.save(HERE / "board_finish2.png")
    gif = []
    k2 = 3
    bw, bh = (box[2] - box[0]) * k2, (box[3] - box[1]) * k2
    for a in new:
        G = Image.new("RGBA", (bw + 10, bh + 10), grey)
        G.alpha_composite(Image.fromarray(C.selout(a)[0]).crop(box).resize((bw, bh), Image.NEAREST), (5, 5))
        gif.append(G.convert("RGB"))
    gif[0].save(HERE / "front_death_finished2.gif", save_all=True, append_images=gif[1:], duration=C.MS, loop=0)


if __name__ == "__main__":
    main()
