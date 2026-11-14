"""Check Codex's front death candidate against the death35 rules and the still, my own measure (not Codex's).
Rules: 160x160, binary alpha, the still's 15 colours, one 8-connected piece, no enclosed holes, no edge contact, lowest
row <= 140, f0 == still byte for byte, f6 == f5 with the eyes set to #2E1A6E. Measures (relight.py's light_angle, the
same one in refs/measure.json): ink and cap shares, violet and gold light angle, luma spread, pixels changed vs live.
Writes compare_7x.png (still | live | new for f2, f3, f5, no outline) and board_compare.png (sel-out 4x, three rows).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label

sys.path.insert(0, r"D:/dev/_scratch/touchup-lane/death-relight")
from relight import codes, light_angle  # noqa: E402
sys.path.insert(0, r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
from selout_rhino import selout  # noqa: E402

HERE = Path(__file__).parent
D35 = Path(r"D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b/anim/death35")
J = D35 / "codex-death"
STILL = Path(r"D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b/views_cam35_touchup/s.png")
EYES = [(0x3F, 0xE8, 0xB0), (0xC8, 0xFF, 0xF0), (0xF6, 0xFF, 0xFB)]
MS = [300, 100, 130, 140, 160, 180, 1400]
A = lambda p: np.asarray(Image.open(p).convert("RGBA"))


def stats(a):
    h = codes(a)
    m = h != ""
    op = int(m.sum())
    L = (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2])[m]
    return {"ink%": round(100 * int((h == "141218").sum()) / op, 2), "cap%": round(100 * int((h == "e0c8ff").sum()) / op, 2),
            "light": {k: v for k, v in light_angle(h).items() if k != "steel"}, "luma_sd": round(float(L.std()), 1)}


def main():
    still = A(STILL)
    pal = {tuple(c) for c in still[still[..., 3] > 0][:, :3]}
    live = [A(D35 / f"frames/front_f{i}.png") for i in range(7)]
    new = [A(J / f"frames/front_f{i}.png") for i in range(7)]
    rep = {"still": stats(still)}
    ok = True
    for i, (a, b) in enumerate(zip(live, new)):
        m = b[..., 3] > 0
        ys, xs = np.nonzero(m)
        r = {"size_ok": b.shape == (160, 160, 4), "alpha_binary": bool(set(np.unique(b[..., 3])) <= {0, 255}),
             "palette_ok": {tuple(c) for c in b[m][:, :3]} <= pal,
             "pieces": int(label(m, np.ones((3, 3), int))[1]), "holes": int((binary_fill_holes(m) & ~m).sum()),
             "edge": bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any()), "lowest": int(ys.max()),
             "alpha_same_as_live": bool(np.array_equal(m, a[..., 3] > 0)),
             "px_repainted": int(np.any(a != b, -1).sum()),
             "eye_px": sum(int(((b[..., :3] == e).all(-1) & m).sum()) for e in EYES), **stats(b)}
        r["rules"] = (r["size_ok"] and r["alpha_binary"] and r["palette_ok"] and r["pieces"] == 1 and r["holes"] == 0
                      and not r["edge"] and r["lowest"] <= 140)
        ok &= r["rules"]
        rep[f"f{i}"] = r
    f6 = new[5].copy()
    e = np.zeros(f6.shape[:2], bool)
    for c in EYES:
        e |= (f6[..., :3] == c).all(-1) & (f6[..., 3] > 0)
    f6[e, :3] = (0x2E, 0x1A, 0x6E)
    rep["f0_is_still"] = bool(np.array_equal(new[0], still))
    rep["f6_is_f5_eyes_out"] = bool(np.array_equal(f6, new[6]))
    rep["all_rules"] = ok and rep["f0_is_still"] and rep["f6_is_f5_eyes_out"]
    (HERE / "check_report.json").write_text(json.dumps(rep, indent=1))
    print("still", rep["still"])
    for i in range(7):
        r = rep[f"f{i}"]
        print(f"f{i}", "rules", r["rules"], "alpha same", r["alpha_same_as_live"], "repainted", r["px_repainted"],
              "ink", r["ink%"], "cap", r["cap%"], "light", r["light"], "luma_sd", r["luma_sd"], "eyes", r["eye_px"])
        print("    live", stats(live[i]))
    print("f0 is still", rep["f0_is_still"], "| f6 = f5 eyes out", rep["f6_is_f5_eyes_out"], "| ALL", rep["all_rules"])
    pictures(still, live, new)


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return Image.fromarray(a).crop((int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2))


def pictures(still, live, new):
    grey = (0x5A, 0x60, 0x58, 255)
    k = 7
    picks = [("the still", still)] + [(f"{t} f{i}", fr[i]) for i in (2, 3, 5) for t, fr in (("live", live), ("new", new))]
    cs = [(lab, crop(a)) for lab, a in picks]
    W = sum(c.width * k + 10 for _, c in cs) + 10
    H = max(c.height for _, c in cs) * k + 34
    C = Image.new("RGBA", (W, H), (34, 37, 41, 255))
    d = ImageDraw.Draw(C)
    x = 10
    for lab, c in cs:
        d.rectangle([x, 26, x + c.width * k, 26 + c.height * k], fill=grey)
        C.alpha_composite(c.resize((c.width * k, c.height * k), Image.NEAREST), (x, 26))
        d.text((x, 8), lab, fill=(235, 235, 230, 255))
        x += c.width * k + 10
    C.save(HERE / "compare_7x.png")
    al = np.zeros((160, 160), bool)
    for a in live + new:
        al |= a[..., 3] > 0
    ys, xs = np.nonzero(al)
    box = (int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4)
    k = 4
    cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k
    B = Image.new("RGBA", (110 + 7 * (cw + 6), 2 * (ch + 22) + 26), (34, 37, 41, 255))
    d = ImageDraw.Draw(B)
    y = 20
    for lab, fr in (("live", live), ("Codex", new)):
        d.text((8, y + 6), lab, fill=(235, 235, 230, 255))
        for i, a in enumerate(fr):
            x = 110 + i * (cw + 6)
            d.rectangle([x, y, x + cw, y + ch], fill=grey)
            B.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((cw, ch), Image.NEAREST), (x, y))
            if y == 20:
                d.text((x + 4, y - 16), f"f{i}  {MS[i]} ms", fill=(235, 235, 230, 255))
        y += ch + 22
    B.save(HERE / "board_compare.png")


if __name__ == "__main__":
    main()
