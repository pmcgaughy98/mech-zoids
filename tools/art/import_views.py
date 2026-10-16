"""Import eight machine views into the game's view slots, all on one canvas with the feet in the same place.

The pipeline (docs/team/CODEX_START_HERE.md): one master drawing per machine -> Retro Diffusion's rotate makes
the eight views from it (a 3x3 sheet, paid, Preston approves) -> Codex or Claude fixes any view by hand -> this
script lines them up and writes the slots -> tools/debug/view_art_check.gd checks them in Godot.

Usage (from the project root):
    python tools/art/import_views.py <machine_id> <folder_with_cells> <map.json>

map.json says which cell file is which facing, e.g. {"e": "fixed_cell1.png", "s": "fixed_cell2.png", ...}.
Facings are relative to the camera: e = facing screen right, s = toward the camera, n = away.
A facing left out is filled in the game by mirroring its opposite (se from sw, w from e...), so leave out
only views whose opposite is drawn.

Writes art/machines/<id>/views/<dir>.png, views.json (canvas size, feet point, palette, source) and
views_contact.png (every view at 4x with its label and the feet point), and prints a consistency report.
"""
import json, os, sys
from collections import Counter
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import live_guard   # backs up hand-finished live views before they are replaced (2026-10-15)

DIRS = ["e", "ne", "n", "nw", "w", "sw", "s", "se"]
MIRROR = {"w": "e", "nw": "ne", "sw": "se", "e": "w", "ne": "nw", "se": "sw"}
MARGIN = 2


def feet(img):
    """The feet point: the bottom row with any pixels, and the middle of what touches the ground there
    (the opaque pixels in the lowest 4 rows), so every view stands on the same spot."""
    a = img.getchannel("A")
    w, h = img.size
    rows = [y for y in range(h) if any(a.getpixel((x, y)) for x in range(w))]
    bottom = rows[-1]
    xs = [x for y in range(bottom - 3, bottom + 1) for x in range(w) if a.getpixel((x, y))]
    return (min(xs) + max(xs)) / 2.0, bottom


def main(mid, folder, map_path):
    mapping = json.load(open(map_path))
    views = {d: Image.open(os.path.join(folder, f)).convert("RGBA") for d, f in mapping.items()}
    missing = [d for d in DIRS if d not in views and MIRROR.get(d) not in views]
    if missing:
        sys.exit(f"no art and no mirror for: {missing}")
    # every view cropped to its pixels, then placed so its feet land on one shared point
    crops, feet_pts = {}, {}
    for d, im in views.items():
        bb = im.getchannel("A").getbbox()
        c = im.crop(bb)
        crops[d] = c
        feet_pts[d] = feet(c)
    above = max(fy for fx, fy in feet_pts.values())                     # tallest part above the feet
    half = max(max(fx, c.width - fx) for (fx, fy), c in zip(feet_pts.values(), crops.values()))
    W = int(2 * (half + MARGIN)) + (int(2 * (half + MARGIN)) % 2)      # even width so mirrors line up
    H = int(above + 1 + MARGIN * 2)
    anchor = (W // 2, int(above + MARGIN))
    out_dir = os.path.join("art", "machines", mid, "views")
    live_guard.guard(out_dir, mid, "views")
    os.makedirs(out_dir, exist_ok=True)
    palette = Counter()
    for d, c in crops.items():
        fx, fy = feet_pts[d]
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        canvas.alpha_composite(c, (int(round(anchor[0] - fx)), int(anchor[1] - fy)))
        canvas.save(os.path.join(out_dir, f"{d}.png"))
        palette.update(p[:3] for p in canvas.getdata() if p[3])
    # the palette is every colour used by at least 4 pixels across all views (stray one-offs are flagged)
    pal = sorted("%02x%02x%02x" % c for c, n in palette.items() if n >= 4)
    meta = {"size": [W, H], "anchor": list(anchor), "palette": pal, "source": os.path.abspath(folder),
            "map": mapping, "mirrored": [d for d in DIRS if d not in views]}
    json.dump(meta, open(os.path.join(out_dir, "views.json"), "w"), indent=1)
    live_guard.record(out_dir, [f"{d}.png" for d in crops])
    # report: what an artist should look at
    heights = {d: feet_pts[d][1] + 1 for d in crops}
    med = sorted(heights.values())[len(heights) // 2]
    print(f"{mid}: canvas {W}x{H}, feet at {anchor}, {len(pal)} colours, mirrored in game: {meta['mirrored']}")
    for d in DIRS:
        if d not in crops:
            print(f"  {d:2}  (mirror of {MIRROR[d]})")
            continue
        im = Image.open(os.path.join(out_dir, f"{d}.png"))
        px = [p[:3] for p in im.getdata() if p[3]]
        off = sum(1 for p in px if "%02x%02x%02x" % p not in pal)
        flag = []
        if abs(heights[d] - med) > med * 0.15: flag.append("height differs from the others")
        if off: flag.append(f"{off} off-palette px")
        print(f"  {d:2}  height {heights[d]:3}  {', '.join(flag) or 'ok'}")
    # contact sheet for eyes: each view at 4x, label, yellow feet point
    S, pad = 4, 6
    sheet = Image.new("RGBA", (4 * (W * S + pad) + pad, 2 * (H * S + pad + 12) + pad), (225, 225, 225, 255))
    dr = ImageDraw.Draw(sheet)
    for k, d in enumerate(DIRS):
        src = d if d in crops else MIRROR[d]
        im = Image.open(os.path.join(out_dir, f"{src}.png"))
        if d not in crops:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        x, y = pad + (k % 4) * (W * S + pad), pad + (k // 4) * (H * S + pad + 12)
        sheet.alpha_composite(im.resize((W * S, H * S), Image.NEAREST), (x, y + 12))
        dr.text((x, y), d + ("  (mirror)" if d not in crops else ""), fill=(0, 0, 0, 255))
        ax, ay = x + anchor[0] * S, y + 12 + anchor[1] * S
        dr.rectangle([ax - 2, ay - 2, ax + 2, ay + 2], fill=(255, 212, 0, 255))
    sheet.save(os.path.join(out_dir, "views_contact.png"))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
