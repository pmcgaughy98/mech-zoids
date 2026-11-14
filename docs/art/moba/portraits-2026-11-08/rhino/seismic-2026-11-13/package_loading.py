# Packaging only. Reuses mode_down verbatim from the existing Claude legend_card.py.
# Does not load the old retired sprite palette or run its plate-cleaning rules.
from pathlib import Path
from PIL import Image
import collections
def mode_down(img, tw, th):
    W, H = img.size; px = img.load(); out = Image.new("RGB", (tw, th)); op = out.load()
    for ty in range(th):
        ya = int(ty * H / th); yb = max(int((ty + 1) * H / th), ya + 1)
        for tx in range(tw):
            xa = int(tx * W / tw); xb = max(int((tx + 1) * W / tw), xa + 1)
            op[tx, ty] = collections.Counter(px[x, y] for y in range(ya, yb) for x in range(xa, xb)).most_common(1)[0][0]
    return out
if __name__ == '__main__':
    base=Path(__file__).parent
    raw=Image.open(base/'rhino-seismic-release-master.png').convert('RGB')
    # Contain the full downloaded frame; extend background only, never crop another body part.
    h=round(raw.width*373/205)
    canvas=Image.new('RGB',(raw.width,h),raw.getpixel((0,0)))
    canvas.paste(raw,(0,0))
    art=mode_down(canvas,205,373)
    art.save(base/'rhino_loading_205x373_candidate.png')
    art.resize((410,746),Image.Resampling.NEAREST).save(base/'rhino_loading_review_2x.png')
