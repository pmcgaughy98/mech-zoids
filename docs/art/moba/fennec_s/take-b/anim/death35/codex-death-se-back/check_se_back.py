"""Check Codex's se and back death candidates (death35 rules, my own measure) and draw the review boards.
board_se_back.png: per view live then new f0-f6 (sel-out, 3x), then the installed front for the same fall.
compare_se_back_7x.png: per view the still, live f3, new f3, live f5, new f5 (raw, 7x)."""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, label
sys.path.insert(0, r"D:/dev/_scratch/touchup-lane/death-relight")
from relight import codes, light_angle
sys.path.insert(0, r"D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim")
from selout_rhino import selout
D35 = Path(r"D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b/anim/death35"); J = D35 / "codex-death-se-back"
ST = Path(r"D:/dev/new-mech-rpg/docs/art/moba/fennec_s/take-b/views_cam35_touchup")
EYES = [(0x3F, 0xE8, 0xB0), (0xC8, 0xFF, 0xF0), (0xF6, 0xFF, 0xFB)]
A = lambda p: np.asarray(Image.open(p).convert("RGBA"))
HERE = Path(__file__).parent
rep = {}; allok = True
data = {}
for name, sv in (("se", "se"), ("back", "n")):
    still = A(ST / f"{sv}.png"); pal = {tuple(c) for c in A(ST / "s.png")[A(ST / "s.png")[..., 3] > 0][:, :3]}
    live = [A(D35 / f"frames/{name}_f{i}.png") for i in range(7)]; new = [A(J / f"frames/{name}_f{i}.png") for i in range(7)]
    data[name] = (still, live, new)
    rows = []
    for i, b in enumerate(new):
        m = b[..., 3] > 0; ys, xs = np.nonzero(m); h = codes(b)
        r = {"alpha_binary": bool(set(np.unique(b[..., 3])) <= {0, 255}), "palette_ok": {tuple(c) for c in b[m][:, :3]} <= pal,
             "pieces": int(label(m, np.ones((3, 3), int))[1]), "holes": int((binary_fill_holes(m) & ~m).sum()),
             "edge": bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any()), "lowest": int(ys.max()),
             "ink": round(100 * (h == "141218").sum() / m.sum(), 2), "light": light_angle(h)["violet"],
             "eyes": sum(int(((b[..., :3] == e).all(-1) & m).sum()) for e in EYES), "px": int(m.sum()),
             "centre_x": round(float(xs.mean()), 1)}
        r["ok"] = r["alpha_binary"] and r["palette_ok"] and r["pieces"] == 1 and r["holes"] == 0 and not r["edge"] and r["lowest"] <= 140
        allok &= r["ok"]; rows.append(r)
    f6 = new[5].copy(); e = np.zeros((160, 160), bool)
    for c in EYES: e |= (f6[..., :3] == c).all(-1) & (f6[..., 3] > 0)
    f6[e, :3] = (0x2E, 0x1A, 0x6E)
    rep[name] = {"f0_is_still": bool(np.array_equal(new[0], still)), "f6_is_f5_eyes_out": bool(np.array_equal(f6, new[6])),
                 "still_ink": round(100 * (codes(still) == "141218").sum() / (still[..., 3] > 0).sum(), 2),
                 "still_light": light_angle(codes(still))["violet"], "still_px": int((still[..., 3] > 0).sum()), "frames": rows}
    allok &= rep[name]["f0_is_still"] and rep[name]["f6_is_f5_eyes_out"]
    print(name, "f0=still", rep[name]["f0_is_still"], "f6=f5 eyes out", rep[name]["f6_is_f5_eyes_out"],
          "still ink", rep[name]["still_ink"], "light", rep[name]["still_light"], "px", rep[name]["still_px"])
    for i, r in enumerate(rows):
        print("  f%d ok %s pieces %d lowest %d ink %.2f light %s eyes %d px %d cx %.1f" % (i, r["ok"], r["pieces"], r["lowest"], r["ink"], r["light"], r["eyes"], r["px"], r["centre_x"]))
rep["all_rules"] = bool(allok); print("ALL RULES", allok)
(HERE / "check_se_back.json").write_text(json.dumps(rep, indent=1))
front = [A(D35 / f"frames/front_f{i}.png") for i in range(7)]
al = np.zeros((160, 160), bool)
for nm in data:
    for a in data[nm][1] + data[nm][2]: al |= a[..., 3] > 0
for a in front: al |= a[..., 3] > 0
ys, xs = np.nonzero(al); box = (int(xs.min()) - 3, int(ys.min()) - 3, int(xs.max()) + 4, int(ys.max()) + 4)
k = 3; cw, ch = (box[2] - box[0]) * k, (box[3] - box[1]) * k; grey = (0x5A, 0x60, 0x58, 255)
rowsB = [("se live", data["se"][1]), ("se new", data["se"][2]), ("back live", data["back"][1]), ("back new", data["back"][2]), ("front", front)]
B = Image.new("RGBA", (90 + 7 * (cw + 6), len(rowsB) * (ch + 8) + 26), (34, 37, 41, 255)); d = ImageDraw.Draw(B); y = 20
for lab, fr in rowsB:
    d.text((6, y + 6), lab, fill=(235, 235, 230, 255))
    for i, a in enumerate(fr):
        x = 90 + i * (cw + 6); d.rectangle([x, y, x + cw, y + ch], fill=grey)
        B.alpha_composite(Image.fromarray(selout(a)[0]).crop(box).resize((cw, ch), Image.NEAREST), (x, y))
        if y == 20: d.text((x + 4, 4), f"f{i}", fill=(235, 235, 230, 255))
    y += ch + 8
B.save(HERE / "board_se_back.png")
def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0); return Image.fromarray(a).crop((int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 2, int(ys.max()) + 2))
k = 6; lines = []
for nm in ("se", "back"):
    still, live, new = data[nm]
    lines.append([(f"{nm} still", crop(still))] + [(f"{nm} {t} f{i}", crop(fr[i])) for i in (3, 5) for t, fr in (("live", live), ("new", new))])
W = max(sum(c.width * k + 10 for _, c in ln) for ln in lines) + 10
H = sum(max(c.height for _, c in ln) * k + 30 for ln in lines) + 10
C = Image.new("RGBA", (W, H), (34, 37, 41, 255)); dc = ImageDraw.Draw(C); y = 4
for ln in lines:
    x = 10; hh = max(c.height for _, c in ln) * k
    for lab, c in ln:
        dc.rectangle([x, y + 20, x + c.width * k, y + 20 + c.height * k], fill=grey)
        C.alpha_composite(c.resize((c.width * k, c.height * k), Image.NEAREST), (x, y + 20)); dc.text((x, y + 4), lab, fill=(235, 235, 230, 255))
        x += c.width * k + 10
    y += hh + 30
C.save(HERE / "compare_se_back_6x.png"); print(B.size, C.size)
