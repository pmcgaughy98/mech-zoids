#!/bin/bash
# Render and pixelize a machine's battle frames without installing them (Claude, 2026-10-16, creature factory pass).
# The same steps as tools/art/anim_round.sh up to the pixelized frames, into a folder of your choosing, so
# tools/art/patch_frames.py can compare them with the frames the live set came from and install only what changed.
#   bash tools/art/anim_render_only.sh <id> <out_dir> [ortho]
# PIXELIZER=pixelize_detail (2026-10-16) renders the piece and normal passes too and pixelizes with the detail pixelizer.
set -e
cd "$(dirname "$0")/../.."
ID=$1; OUT=$2; ORTHO=${3:-5.6}
eval "$(python tools/art/legacy_env.py $ID)"
B="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
rm -rf "$OUT"; mkdir -p "$OUT"
python - "$ID" "$OUT/jobs.txt" <<'PY'
import json, sys
mid, jobs = sys.argv[1], sys.argv[2]
plan = json.load(open("tools/art/anim/%s_plan.json" % mid))
with open(jobs, "w") as f:
    for name, c in plan.items():
        for k, fr in enumerate(c["frames"]):
            f.write("%s %d %s %d\n" % (name, k, c.get("source", name), fr))
PY
PX=${PIXELIZER:-pixelize_render}
if [ "$PX" = pixelize_detail ]; then export SPRITE_PIECES=1 SPRITE_NORMALS=1; fi
SPRITE_ORTHO=$ORTHO timeout 3600 "$B" -b -P tools/blender/render_jobs.py -- "docs/art/3d/$ID.blend" "$OUT/jobs.txt" "$OUT" 2>&1 | grep -E "RENDER_JOBS_DONE|Error|Traceback" | head -3
for f in "$OUT"/*/*/e.png; do
  PIXEL_NO_CROP=1 PIXEL_PALETTE=tools/art/palettes/$ID.json python tools/art/$PX.py "$f" "$(dirname "$f")/e_px.png" x4.4 >/dev/null
done
echo "ANIM_RENDER_ONLY_DONE $OUT"
