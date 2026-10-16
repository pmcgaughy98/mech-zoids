# Shoebill p85 Wing Buffet finish, 2026-10-16

Finished and installed the seven replacement frames, art/machines/shoebill_m/anim/buffet/1-7.png, after Claude fixed the far wing's bindings. 3,541 opaque pixels changed. The other 33 animation PNGs, including Buffet endpoints 0 and 8, all eight views and the extra view contact remain byte-for-byte unchanged. No old wing silhouette was restored.

The 110x120 canvas, feet_y 117, all timing/loop/strike metadata and both installation records are exact. Full Buffet durations remain [150,150,180,250,50,50,120,130,200], strike 5. Colors stay within the live views palette plus the allowed teal ramp.

## Carry-forward rules

| Fix | Classification | Rule |
|---|---|---|
| Mid-blue torso | repeatable | Compress the existing main/pale body surfaces toward the middle blue ramp while retaining small upper catchlights. Protect head, eyes, original gold, hardware and wing steps. Torso luminance falls 20.34-24.13% across these seven frames, matching the p84 treatment. |
| Torso plate separation | repeatable | Place one-sided navy seams at actual dorsal, breast and upper/lower flank interfaces; darken native chest vents. Do not add an outside black ring. |
| Shoulder and hip gold | repeatable | Add a narrow gold upper edge only on exposed native upper-arm and hip-cap surfaces. Preserve all original gold, including hooked bill, muzzle, joint rings and toe tips. |
| Forward head gun | repeatable | Follow visible native piece-map coverage, including thin barrel pixels, using the darkest existing steel shade. Preserve gold muzzle pixels and the original footprint. |
| Mask and pose review | hand only | Require exact original render-to-live correspondence and exact piece color replay before using semantic masks. Inspect the complete loop including the already-finished endpoints. Do not thicken a thin barrel onto the bill/background or invent hidden pieces. |

## Preservation and sources

Seven raw input PNGs matched their current SHA1 install records. The other 33 matched the saved anim_p84_codex finish, and all eight views matched p84_codex. Full current inputs were backed up to docs/art/2d/shoebill_m/anim_p85_buffet_pre_codex/. The complete current 40-frame finished archive is anim_p85_buffet_codex/. Historical p84 files remain untouched.

The seven original color/ID/pixel sources were copied from the current anim_frames cache into p85_buffet_codex/installed-sources/buffet/1-7/. Each native color render independently re-pixelized exactly to the installed RGBA crop [46,23,156,143], using native x4.4/palette settings, before map use.

The Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md) supplied the read-only replay workflow. Per-piece maps were rendered from the current model and native poses without saving the blend. Every replayed color image matched its original render exactly. Native part identity, materials and rest-space surfaces therefore follow the corrected p85 bindings. The model SHA256 is unchanged from the start of this slice.

Every alpha byte, transparent RGBA pixel, position, eye pixel, original gold pixel and protected head/hardware/stepped-wing pixel is exact. Protection masks are preserved in masks/. Source, metadata, model and output hashes are recorded in input-audit.json, map-audit.json, piece-source.json, finish-audit.json and final-audit.json. Only the seven named live PNGs changed. No protected pipeline/game/model source was edited; no installer/exporter/round script, paid generator or commit ran. CODEX_IN_PROGRESS was removed at handover.

## Checks and review

- Godot import exits 0. view_art_check, views_check, battle_check and battle_fit_check PASS.
- All 40 loaded frames captured before and after in both actual battle slots at 1280x720, with canvas/duration assertions and current Stage placement. Captures: anim_p85_buffet_codex/review/battle/{before,after}/. Full nine-frame Buffet contact: review/buffet-battle-contact.png.
- Required native battle captures preserved immediately in p85_buffet_codex/battle_before/ and battle_after/.
- Six seconds of real Wing Buffet combat recorded at 60fps. The fixture provides enough EP to fire the original weapon, which deals 40 damage. All nine animation indices were observed through actual playback; result queue and observed frames are saved in review/combat_buffet/audit.json. MP4: review/combat_buffet.mp4; contact: review/buffet-combat-contact.png.
- All eight unchanged views checked in the actual view lab's new solo-focus mode, using its own positions and camera rotation. No scene modifications. Default cast and eight solo captures preserved; view-lab-eight-cameras.png collects them.
- Full nine-frame before/after contact at nearest 4x; comparison GIF at exact 4x and finished GIF at exact 3x. Fixed palette and all durations are exact at GIF's 10ms precision. Identical source poses finish identically; moving screen-pixel color changes are recorded without a zero-shimmer claim. Contacts, native battle/lab captures and the browser loop were visually inspected.
- Quality measurements are records, not targets: mean cluster size 7.50-8.54 before, 6.81-7.79 after; stray share 3.31-4.81% before, 4.16-5.53% after. Plate seams and small highlights add small clusters. Full quality and Legacy metrics are saved.

Review: http://127.0.0.1:8879/p85_buffet_codex/review.html. Local server PID 33840 at launch.

No raw render touches the camera edge in these seven frames. Current battle captures show the complete Buffet poses in both slots. The previously reported narrow gun sections remain native and preserved. No new source issue was introduced or painted around.

Next handoff slice: pangolin p41, sixteen battle frames plus seven views on the new 200x87 view canvas. After that: six gorilla death frames on the new 173x148 animation canvas. Their raw replacements were not altered in this shoebill slice; re-read current handoff and verify exact inputs before continuing.
