"""Preston's picks from eye-moves-all.png (2026-11-04): "horn toss side f1 left, horn toss front f3 left, stampede
side f4 left need fixed". Left in each pair is the last version's eye, so those eyes are copied pixel for pixel
from the board's left tiles into eye_overrides.json, which fix_set.py applies instead of placing eyes itself.
Each tile's crop position is checked first by matching the right tile against the current frame.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ANIM = Path(__file__).parent
sys.path.insert(0, str(ANIM))
from fix_set import R, G, red_centres  # noqa: E402

BOARD = np.asarray(Image.open(ANIM / "eye-moves-all.png").convert("RGBA"))
PICKS = [(18, "codex-set-a", "horn-toss", "front", 3), (20, "codex-set-a", "horn-toss", "side", 1),
         (36, "codex-set-b", "stampede", "side", 4)]
TW, TH, LABEL, PITCH_X, PITCH_Y = 192, 120, 220, 610, 124

out = json.loads((ANIM / "eye_overrides.json").read_text()) if (ANIM / "eye_overrides.json").exists() else {}
for idx, sdir, sheet, view, c in PICKS:
    x0, y0 = (idx % 3) * PITCH_X, (idx // 3) * PITCH_Y
    a = np.asarray(Image.open(ANIM / sdir / sheet / "frames" / f"{view}_f{c}.png").convert("RGBA"))
    cen = red_centres(a)
    cx, cy = int(np.mean([p[0] for p in cen])), int(np.mean([p[1] for p in cen]))
    crop = a[cy - 15:cy + 15, cx - 24:cx + 24]
    new_tile = BOARD[y0:y0 + TH, x0 + LABEL + TW:x0 + LABEL + 2 * TW]
    old_tile = BOARD[y0:y0 + TH, x0 + LABEL:x0 + LABEL + TW]
    sample_new, sample_old = new_tile[1::4, 1::4], old_tile[1::4, 1::4]
    op = crop[..., 3] > 0
    agree = np.all(sample_new[..., :3] == crop[..., :3], -1)[op].mean()
    assert agree > 0.99, (sheet, view, c, agree)
    pix = []
    backup = np.asarray(Image.open(ANIM / sdir / sheet / "frames_codex" / f"{view}_f{c}.png").convert("RGBA"))
    for j in range(30):
        for i in range(48):
            col = tuple(int(v) for v in sample_old[j, i, :3])
            if col in (R, G):
                x, y = cx - 24 + i, cy - 15 + j
                assert backup[y, x, 3], (sheet, view, c, x, y)
                pix.append([x, y, "%02X%02X%02X" % col])
    out[f"{sheet}/{view}/{c}"] = pix
    print(f"{sheet} {view}_f{c}: tile check {agree:.3f}, {len(pix)} eye px from the left tile")
(ANIM / "eye_overrides.json").write_text(json.dumps(out, indent=1), encoding="utf8")
