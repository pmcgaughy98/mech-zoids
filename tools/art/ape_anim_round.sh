#!/bin/bash
# Re-render the gorilla's battle animation from the current blend (docs/art/3d/ape_l_v2.blend) and pack it into
# art/machines/ape_l/anim/ (Claude, 2026-10-13). Run after every gorilla build that is installed: the battle draws
# the gorilla from these frames, not from its views, so they go stale when the model changes.
#   bash tools/art/ape_anim_round.sh
# The frame picks and durations (tools/art/ape_l_anim_plan.json, one render job per line in ape_l_anim_jobs.txt) come
# from animation pass 3 (reports/Gorilla mech animation foundation.md). Frames are pixelized uncropped
# (PIXEL_NO_CROP=1) so all share one canvas; export_anim.py asserts that.
set -e
cd "$(dirname "$0")/../.."
if [ -f "art/machines/ape_l/CODEX_IN_PROGRESS" ] && [ "$LIVE_GUARD_FORCE" != "1" ]; then echo "STOP: ape_l is marked CODEX_IN_PROGRESS: Codex is finishing it; this round would overwrite its renders and part maps (tools/art/live_guard.py)."; exit 1; fi
eval "$(python tools/art/legacy_env.py ape_l)"   # the Legacy-look render settings (2026-10-14)
export SPRITE_ORTHO="${SPRITE_ORTHO:-5.61}"   # 2026-10-15: 20 sprite px more frame each side (816 px, still 4.4 px per sprite px); the
# haymaker punch's fist left the 4.4 frame, and Codex found slam/throw/death cut by it too. export_anim crops to the union.
B="${BLENDER:-C:/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
OUT="$(cygpath -m "$(realpath -m "${ANIM_OUT:-docs/art/2d/ape_l/anim_frames}")")"   # absolute: Blender put a relative path under C:\ (2026-10-14)
rm -rf "$OUT"; mkdir -p "$OUT"
while read clip k frame; do
  d="$OUT/$clip/$k"; mkdir -p "$d"
  SPRITE_CLIP="$clip" SPRITE_FRAME="$frame" SPRITE_VIEWS="e" SPRITE_OUT="$d" timeout 200 "$B" -b docs/art/3d/ape_l_v2.blend -P tools/blender/render_sprite_views.py 2>&1 | grep -E "Error|Traceback" | head -1 || true
  PIXEL_NO_CROP=1 PIXEL_EYE_FLAT=1 PIXEL_HIGHLIGHT_RANK=0.84,0.94 python tools/art/pixelize_render.py "$d/e.png" "$d/e_px.png" x4.4 >/dev/null
done < tools/art/ape_l_anim_jobs.txt
python tools/art/export_anim.py ape_l "$OUT" tools/art/ape_l_anim_plan.json
