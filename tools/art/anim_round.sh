#!/bin/bash
# A machine's battle animation set (Claude, 2026-10-13): render the frames its plan picks from the clips in its blend,
# pixelize them on one canvas, pack them into art/machines/<id>/anim/ for the battle (scripts/ui/machine_anim.gd).
#   bash tools/art/anim_round.sh <id> [ortho]
# Plan: tools/art/anim/<id>_plan.json, {anim: {source, frames, ms, loop, strike}} ("source" is the Blender clip, the
# anim name what the battle plays: idle, hit, death and each weapon's "clip" in scripts/data/machines.gd).
# The gorilla keeps its own round (tools/art/ape_anim_round.sh). Run after installing a new build of the machine.
set -e
cd "$(dirname "$0")/../.."
ID=$1; ORTHO=${2:-5.6}
if [ -f "art/machines/$ID/CODEX_IN_PROGRESS" ] && [ "$LIVE_GUARD_FORCE" != "1" ]; then echo "STOP: $ID is marked CODEX_IN_PROGRESS: Codex is finishing it; this round would overwrite its renders and part maps (tools/art/live_guard.py)."; exit 1; fi
eval "$(python tools/art/legacy_env.py $ID)"   # the Legacy-look render settings (2026-10-14)
B="${BLENDER:-C:/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
OUT="docs/art/2d/$ID/anim_frames"; rm -rf "$OUT"; mkdir -p "$OUT"
python - "$ID" "$OUT/jobs.txt" <<'PY'
import json, sys
mid, jobs = sys.argv[1], sys.argv[2]
plan = json.load(open("tools/art/anim/%s_plan.json" % mid))
with open(jobs, "w") as f:
    for name, c in plan.items():
        for k, fr in enumerate(c["frames"]):
            f.write("%s %d %s %d\n" % (name, k, c.get("source", name), fr))
PY
SPRITE_ORTHO=$ORTHO timeout 1800 "$B" -b -P tools/blender/render_jobs.py -- "docs/art/3d/$ID.blend" "$OUT/jobs.txt" "$OUT" 2>&1 | grep -E "RENDER_JOBS_DONE|Error|Traceback" | head -3
for f in "$OUT"/*/*/e.png; do
  PIXEL_NO_CROP=1 PIXEL_PALETTE=tools/art/palettes/$ID.json python tools/art/pixelize_render.py "$f" "$(dirname "$f")/e_px.png" x4.4 >/dev/null
done
python tools/art/export_anim.py "$ID" "$OUT" "tools/art/anim/${ID}_plan.json"
