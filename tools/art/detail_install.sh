#!/bin/bash
# Install a machine's detail-pixelized views and battle frames (Claude, 2026-10-16; Preston: "better versions and more
# enhanced and detailed than zoids sprites"; docs/reference/sprite-detail-2026-10-16.md).
#   bash tools/art/detail_install.sh <id> <build>
# Needs docs/art/2d/<id>/renders_detail/ (the eight views with _piece and _n passes, render_sprite_views.py
# SPRITE_PIECES=1 SPRITE_NORMALS=1) and docs/art/2d/<id>/anim_frames_detail/ (the battle frames, the same passes).
# Pixelizes both with tools/art/pixelize_detail.py into docs/art/2d/<id>/<build>_detail/ and the frames' e_px.png,
# then installs: import_views.py and export_anim.py (each backs up a hand-finished live folder first: live_guard.py).
set -e
cd "$(dirname "$0")/../.."
ID=$1; BUILD=$2
if [ -f "art/machines/$ID/CODEX_IN_PROGRESS" ] && [ "$LIVE_GUARD_FORCE" != "1" ]; then echo "STOP: $ID is marked CODEX_IN_PROGRESS"; exit 1; fi
eval "$(python tools/art/legacy_env.py $ID)"
if [ "$ID" = ape_l ]; then export PIXEL_EYE_FLAT=1 PIXEL_HIGHLIGHT_RANK=0.84,0.94; PLAN=tools/art/ape_l_anim_plan.json
else export PIXEL_PALETTE=tools/art/palettes/$ID.json; PLAN=tools/art/anim/${ID}_plan.json; fi
R=docs/art/2d/$ID/renders_detail; V=docs/art/2d/$ID/${BUILD}_detail; mkdir -p $V
for v in e ne n nw w sw s se; do python tools/art/pixelize_detail.py $R/$v.png $V/$v.png x4.4 >/dev/null; done
cp docs/art/2d/$ID/$BUILD/map.json $V/map.json
python tools/art/import_views.py $ID $V $V/map.json | tail -3
F=docs/art/2d/$ID/anim_frames_detail
for f in $F/*/*/e.png; do PIXEL_NO_CROP=1 python tools/art/pixelize_detail.py "$f" "$(dirname "$f")/e_px.png" x4.4 >/dev/null; done
python tools/art/export_anim.py $ID $F $PLAN | tail -3
echo "DETAIL_INSTALL_DONE $ID"
