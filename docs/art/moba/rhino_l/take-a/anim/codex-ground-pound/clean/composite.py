"""Ground pound preview: cleaned rhino frames (front, side, back) with the cleaned effect at contact.

Effect rows above its anchor (the ring centre) draw behind the rhino, rows below draw in front.
Timeline in 100 ms ticks: F0 x4, F1 x2, F2, F3 x3, F4+E1..E3, F5+E4..E6, F0+E7 (85%), F0+E8 (60%), F0 x3.
"""
import json, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CG = Path("D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/codex-ground-pound")
CL = CG / "clean"
FF = "C:/Users/pmcga/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe"
TMP = Path("C:/Users/pmcga/AppData/Local/Temp/claude/6130f382513777ab/f2cf3d90-f1be-4e8b-8fb2-5520f92ba654/scratchpad/gp_frames")
VIEWS = ["front", "side", "back"]
BG = (0x3D, 0x43, 0x50, 255)
TOP, SW, SH, LAB = 64, 256, 136, 16
fr = {(v, c): Image.open(CL / "frames" / f"{v}_f{c}.png").convert("RGBA") for v in VIEWS for c in range(6)}
meta = json.loads((CL / "effect/anchor.json").read_text())
ax, ay = meta["anchor"]
eff = [Image.open(CL / "effect" / f"e{k}.png").convert("RGBA") for k in range(1, 9)]

g = np.asarray(fr[("side", 4)])[156:161, :, 3].max(0) > 0
runs, cur = [], None
for x, v in enumerate(list(g) + [False]):
    if v and cur is None: cur = x
    if not v and cur is not None: runs.append((cur, x - 1)); cur = None
sx = round((runs[-1][0] + runs[-1][1]) / 2)
ANCH = {"front": (96, 159), "side": (sx, 158), "back": (96, 151)}
print("side f4 ground runs", runs, "-> anchors", ANCH)

def stage(v, c, k=None, op=1.0):
    st = Image.new("RGBA", (SW, SH), BG)
    rh = fr[(v, c)].crop((0, TOP, 192, 192))
    if k is None:
        st.alpha_composite(rh, (32, 0)); return st
    e = np.asarray(eff[k - 1]).copy(); e[..., 3] = (e[..., 3] * op).astype(np.uint8)
    behind, front = e.copy(), e.copy(); behind[ay:, :, 3] = 0; front[:ay, :, 3] = 0
    X, Y = 32 + ANCH[v][0] - ax, ANCH[v][1] - TOP - ay
    st.alpha_composite(Image.fromarray(behind), (X, Y))
    st.alpha_composite(rh, (32, 0))
    st.alpha_composite(Image.fromarray(front), (X, Y))
    return st

font = ImageFont.load_default()
def tick(c, k, op, note):
    im = Image.new("RGBA", (SW * 3, SH + LAB), BG)
    d = ImageDraw.Draw(im)
    for i, v in enumerate(VIEWS):
        im.alpha_composite(stage(v, c, k, op), (i * SW, LAB))
        d.text((i * SW + 6, 3), v, fill=(220, 224, 232, 255), font=font)
    d.text((SW * 3 - 6 - d.textlength(note, font=font), 3), note, fill=(150, 156, 170, 255), font=font)
    return im.convert("RGB")

SEQ = [(0, None, 1)] * 4 + [(1, None, 1)] * 2 + [(2, None, 1)] + [(3, None, 1)] * 3 + \
      [(4, 1, 1), (4, 2, 1), (4, 3, 1), (5, 4, 1), (5, 5, 1), (5, 6, 1), (0, 7, .85), (0, 8, .6)] + [(0, None, 1)] * 3
normal = [tick(c, k, op, "100 ms per frame") for c, k, op in SEQ]
slow = [tick(c, k, op, "half speed") for c, k, op in SEQ]
shutil.rmtree(TMP, ignore_errors=True); TMP.mkdir(parents=True)
seq = normal * 3 + [im for im in slow for _ in range(2)] * 2
for i, im in enumerate(seq): im.save(TMP / f"{i:04d}.png")
mp4 = CL / "ground-pound-preview.mp4"
r = subprocess.run([FF, "-y", "-loglevel", "error", "-framerate", "10", "-i", str(TMP / "%04d.png"),
                    "-vf", "scale=iw*3:ih*3:flags=neighbor", "-r", "30", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "14", "-movflags", "+faststart", str(mp4)], capture_output=True, text=True)
print("ffmpeg rc", r.returncode, r.stderr[-400:], "mp4", mp4.stat().st_size if mp4.exists() else None, "bytes,", len(seq) / 10, "s")
gif = CL / "ground-pound-preview.gif"
gf = [im.resize((im.width * 2, im.height * 2), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=255) for im in normal]
gf[0].save(gif, save_all=True, append_images=gf[1:], duration=100, loop=0)
print("gif", gif.stat().st_size, "bytes")

pick = [10, 12, 14, 16]
cs = Image.new("RGB", (SW * 3 * 2, (SH + LAB) * 2 * len(pick)))
for j, t in enumerate(pick):
    cs.paste(normal[t].resize((SW * 6, (SH + LAB) * 2), Image.NEAREST), (0, j * (SH + LAB) * 2))
cs.save(CL / "composite-contact.png")

# before (Codex finish) vs after (clean) board
rows = []
for v in VIEWS:
    for tag, src in (("codex", CG / "frames"), ("clean", CL / "frames")):
        rows.append((f"{v} {tag}", [Image.open(src / f"{v}_f{c}.png").convert("RGBA") for c in range(6)]))
bbs = [im.getbbox() for _, ims in rows for im in ims]
bx = (min(b[0] for b in bbs) - 2, min(b[1] for b in bbs) - 2, max(b[2] for b in bbs) + 2, max(b[3] for b in bbs) + 2)
S, cw, chh, lw = 2, (bx[2] - bx[0]) * 2, (bx[3] - bx[1]) * 2, 84
bd = Image.new("RGBA", (lw + 6 * cw, len(rows) * chh), BG)
dd = ImageDraw.Draw(bd)
for r_, (name, ims) in enumerate(rows):
    dd.text((6, r_ * chh + chh // 2 - 6), name, fill=(220, 224, 232, 255), font=font)
    for c, im in enumerate(ims):
        bd.alpha_composite(im.crop(bx).resize((cw, chh), Image.NEAREST), (lw + c * cw, r_ * chh))
    if r_ % 2 == 1:
        dd.line([(0, (r_ + 1) * chh - 1), (bd.width, (r_ + 1) * chh - 1)], fill=(90, 98, 114, 255))
bd.save(CL / "review-before-after.png")

lines = []
for v in VIEWS:
    for c in range(6):
        a = np.asarray(fr[(v, c)]); m = a[..., 3] > 0; ys, xs = np.where(m)
        cols = {tuple(p) for p in a[m][:, :3]}
        red = int((m & np.all(a[..., :3] == (0xFF, 0x3A, 0x2A), -1)).sum())
        glint = int((m & np.all(a[..., :3] == (0xFF, 0xE6, 0xD8), -1)).sum())
        edge = bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any())
        lines.append(f"{v}_f{c}: {xs.max()-xs.min()+1}x{ys.max()-ys.min()+1}, bottom y {ys.max()}, {len(cols)} colours, red {red}, glint {glint}, border contact {edge}")
(CL / "checks.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
