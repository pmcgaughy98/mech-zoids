"""Run sprite_director's between-view checks on any folder of eight stills, without touching the tool or its worklist."""
import sys
from pathlib import Path
sys.path.insert(0, "tools/art")
import numpy as np
import sprite_director as sd

for folder in sys.argv[1:]:
    p = Path(folder)
    views = [sd.load(p / f"{f}.png") for f in sd.FACINGS]
    w = sd.view_jumps(views)
    dips = [sd.FACINGS[i] for i in sd.view_dips(views)]
    lone = max(sd.lone_share(v) for v in views)
    colours = max(len(np.unique(v[sd.mask(v)][:, :3], axis=0)) for v in views)
    pair = lambda k: f"{sd.FACINGS[w[k][1]]}>{sd.FACINGS[(w[k][1] + 1) % 8]}"
    fit = sd.front_back(views)
    print(f"{p.parent.name + '/' + p.name:38s} front/back {fit:.2f} ({'ok' if fit >= sd.FRONT_BACK_NEW else f'under {sd.FRONT_BACK_NEW}'})  "
          f"area {w['area'][0]:.2f} ({pair('area')})  height {w['height'][0]:.2f} ({pair('height')})  "
          f"colour {w['colour'][0]:.2f} ({pair('colour')})  dips {dips or 'none'}  lone {lone:.2f}  colours {colours}")
