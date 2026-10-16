#!/bin/bash
# One creature-factory round (Claude, 2026-10-12): build the machine in Blender, render the eight sprite views in its
# walk stance, pixelize with its palette, measure against the Legacy bands, and make a contact sheet.
#   bash tools/art/creature_round.sh <machine_id> <version> [ortho, default 5.6]
# Needs tools/blender/build_<id>.py (writes docs/art/3d/<id>.blend and, if rigged, <id>.stance) and
# tools/art/palettes/<id>.json. Output: docs/art/2d/<id>/<version>/ and docs/art/2d/<id>/compare_<version>.png.
# Install into the game with: python tools/art/import_views.py <id> docs/art/2d/<id>/<version> <map.json>
# then, with no editor open, let Godot write the .import sidecars the loader needs:
#   Godot --headless --path . --import   (and run tools/debug/view_art_check.gd)
set -e
cd "$(dirname "$0")/../.."
ID=$1; V=$2; ORTHO=${3:-5.6}
if [ -f "art/machines/$ID/CODEX_IN_PROGRESS" ] && [ "$LIVE_GUARD_FORCE" != "1" ]; then echo "STOP: $ID is marked CODEX_IN_PROGRESS: Codex is finishing it; this round would overwrite its renders and part maps (tools/art/live_guard.py)."; exit 1; fi
eval "$(python tools/art/legacy_env.py $ID)"   # the Legacy-look render settings (2026-10-14)
B="${BLENDER:-C:/Program Files/Blender Foundation/Blender 5.2/blender.exe}"; O=docs/art/2d/$ID
timeout 590 "$B" -b --factory-startup -P tools/blender/build_$ID.py 2>&1 | grep -E '_DONE|Error|Traceback|line [0-9]+' | head -8
STANCE=""; [ -f docs/art/3d/$ID.stance ] && STANCE="$(cat docs/art/3d/$ID.stance)"
SPRITE_STANCE="$STANCE" SPRITE_ORTHO=$ORTHO SPRITE_OUT="$(pwd)/$O/renders" timeout 500 "$B" -b docs/art/3d/$ID.blend -P tools/blender/render_sprite_views.py 2>&1 | grep -E 'Error|Traceback' | head -3
mkdir -p $O/$V
for v in e ne n nw w sw s se; do PIXEL_PALETTE=tools/art/palettes/$ID.json python tools/art/pixelize_render.py $O/renders/$v.png $O/$V/$v.png x4.4 >/dev/null; done
python tools/art/sprite_quality.py $O/$V/e.png $O/$V/se.png $O/$V/s.png $O/$V/n.png
python tools/art/creature_sheet.py $ID $V
