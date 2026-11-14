"""Inputs for the fennec's Retro Diffusion back-view walk and sand kick (Claude, animation lane, 2026-11-04).

Preston: "Do walks in retro and sand kick there too as too many cutoffs and misproportions. mainly backviews."
Same cut as the rhino's retro-walk/input: the sprite centred in a 128 canvas with the feet on row 110, padded away from
the edges (Retro animates badly when pixels touch the edge). offsets.json keeps the shift so finish_retro.py can put
each Retro frame back into the 192 canvas with the feet on row 160.
  walk_n, walk_ne   the current standing trot frame 0 (codex-set-a back_f0, codex-set-c ne_f0)
  kick_n, kick_ne   the approved seated stills n.png and ne.png (sand_kick starts and ends on them)
"""
import base64
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
ANIM = HERE.parent
TAKE = ANIM.parent


def still(v):
    c = Image.new("RGBA", (192, 192))
    c.alpha_composite(Image.open(TAKE / "views" / f"{v}.png").convert("RGBA"), (16, 20))
    return c


SRC = {"walk_n": Image.open(ANIM / "codex-set-a/walk/frames/back_f0.png").convert("RGBA"),
       "walk_ne": Image.open(ANIM / "codex-set-c/walk/frames/ne_f0.png").convert("RGBA"),
       "kick_n": still("n"), "kick_ne": still("ne")}


def main():
    offsets = {}
    for name, im in SRC.items():
        a = np.asarray(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        dx = 64 - (int(xs.min()) + int(xs.max()) + 1) // 2
        dy = 110 - 160
        out = np.zeros((128, 128, 4), np.uint8)
        out[ys + dy, xs + dx] = a[ys, xs]
        Image.fromarray(out).save(HERE / "input" / f"{name}_128.png")
        (HERE / "input" / f"{name}_128.b64").write_text(base64.b64encode((HERE / "input" / f"{name}_128.png").read_bytes()).decode())
        offsets[name] = {"dx": dx, "dy": dy}
        print(name, "bbox x", xs.min() + dx, xs.max() + dx, "y", ys.min() + dy, ys.max() + dy)
    (HERE / "offsets.json").write_text(json.dumps(offsets, indent=1))


if __name__ == "__main__":
    main()
