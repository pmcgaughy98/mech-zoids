#!/bin/bash
# Gorilla round (moved from the session scratchpad 2026-10-13). Ref-4 part pass (2026-10-13): stance base 19 to 22, R_leg 16 to 22, L_leg 3 to 34, L_arm 27 to 21 (SE whole 0.799 to 0.816, far fist 0.785 to 0.871, hind 0.738 to 0.788). Battle stance: walk frame 19; near (right) hind leg 16 and far (left) hind leg 3 (7 caught its swing, lifted in the w view) so the hind legs splay as in his reference; far (left) arm 27 so both fists show planted.
# One head round: patch (optional), build, sprite renders, pixelize into docs/art/2d/ape_l/$1, head close-ups + sprites sheet.
set -e
cd /d/dev/new-mech-rpg
V=$1; PATCH=$2
if [ -f "art/machines/ape_l/CODEX_IN_PROGRESS" ] && [ "$LIVE_GUARD_FORCE" != "1" ]; then echo "STOP: ape_l is marked CODEX_IN_PROGRESS: Codex is finishing it; this round would overwrite its renders and part maps (tools/art/live_guard.py)."; exit 1; fi
eval "$(python tools/art/legacy_env.py ape_l)"   # the Legacy-look render settings (2026-10-14)
SP="C:/Users/pmcga/AppData/Local/Temp/claude/C--Program-Files-Git/4953b3ea-a6b8-40db-8a77-2bac0e47ab36/scratchpad"
[ -n "$PATCH" ] && python "$SP/$PATCH"
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
timeout 590 "$B" -b --factory-startup -P tools/blender/build_ape_l_v2.py 2>&1 | grep -E 'APE_L_V2_DONE|Error|Traceback|line [0-9]+' | head -4
SPRITE_STANCE="base=22;R_leg=22;L_leg=34;L_arm=21" timeout 500 "$B" -b docs/art/3d/ape_l_v2.blend -P tools/blender/render_sprite_views.py 2>&1 | grep -E 'SPRITE glow|Error' | head -3
O=docs/art/2d/ape_l; mkdir -p $O/$V
for v in e ne n nw w sw s se; do PIXEL_EYE_FLAT=1 PIXEL_HIGHLIGHT_RANK=0.84,0.94 python tools/art/pixelize_render.py $O/renders/$v.png $O/$V/$v.png x4.4 >/dev/null; done
python - "$V" <<'PYEOF'
import sys
from PIL import Image
V = sys.argv[1]; O = "docs/art/2d/ape_l"
heads = []
for v in ("s", "e", "se"):
    r = Image.open(f"{O}/renders/{v}.png").convert("RGBA"); bb = r.getchannel("A").getbbox(); w = bb[2] - bb[0]
    if v == "s":
        box = (bb[0] + w // 2 - 120, bb[1] - 5, bb[0] + w // 2 + 120, bb[1] + 165)
    else:
        box = (bb[2] - 220, bb[1] - 5, bb[2] + 5, bb[1] + 165)
    heads.append(r.crop(box))
S = 3
def crop(p):
    im = Image.open(p).convert("RGBA"); return im.crop(im.getchannel("A").getbbox())
sprites = [crop(f"{O}/{V}/{v}.png") for v in ("s", "e", "se", "n")]
Hh = max(h.height for h in heads) * 2
W = max(sum(h.width * 2 + 20 for h in heads), sum(t.width * S + 16 for t in sprites)) + 20
sheet = Image.new("RGBA", (W, Hh + max(t.height for t in sprites) * S + 40), (226, 226, 226, 255))
x = 10
for h in heads:
    sheet.alpha_composite(h.resize((h.width * 2, h.height * 2), Image.NEAREST), (x, 5)); x += h.width * 2 + 20
x = 10
for t in sprites:
    sheet.alpha_composite(t.resize((t.width * S, t.height * S), Image.NEAREST), (x, Hh + 20)); x += t.width * S + 16
sheet.save(f"{O}/compare_head_{V}.png"); print("sheet", f"{O}/compare_head_{V}.png")
PYEOF
