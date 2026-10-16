# Gorilla rebuilt slam, throw and death finish, 2026-10-15

Finished and installed all 26 replacement frames: ten slam, ten throw and six death. The finish carries the current v71 green/orange treatment onto Claude's new silhouettes. 8,321 opaque pixels changed: slam 3,181, throw 3,176, death 1,964. The completed nine-frame punch and the other sixteen idle/gait/hit frames remain byte-for-byte unchanged from this slice's input. All eight views and the extra live view contact are exact.

Canvas 169x148, feet_y 130 and all metadata/hash records remain unchanged. Slam durations [250,250,250,300,50,50,200,80,160,250], strike 5; throw [200,200,200,260,90,50,120,120,150,150], strike 5; death [80,100,130,180,250,1000]. No old animation silhouette was restored.

## Carry-forward rules

| Fix | Classification | Rule |
|---|---|---|
| Gentle plate cleanup | repeatable | Collapse only one-rank internal color fluctuations inside broad regions of the same native part and material. Retain real dark seams. |
| Selective outer edges | repeatable | Use the same part's own green/orange ramp: lift exposed top edges, shade sides and undersides. Never add a near-black silhouette ring. |
| Green plate separation | repeatable | On broad visible native green regions, lift the upper edge one step and shade the lower edge one step. Preserve deep seams and cap already strong highlights. |
| Steel catchlights | repeatable | Lift only existing mid/light grey upper edges of native parts. Keep 181f1c, 272d38 and 2a2c31 hubs, rollers and muzzles exact. |
| Source and pose review | hand only | Independently re-pixelize the original color render and prove exact installed correspondence before using its ID map. Inspect contacts, loops and actual combat; do not invent hidden parts or change alignment to conceal a source problem. |

## Input verification and exact sources

Sixteen replacement PNG files matched current SHA1 installation records. The ten slam file hashes differed because the slam was installed at width 166, then padded to 169 by a later clip installation. Each recorded hash matches live_backup_anim_4; every live pixel in columns 0-165 is exact, with only three transparent columns added. This explains the difference without guessing. The other 25 frames match anim_punch_haymaker_codex in columns 0-162, with six transparent right columns. Eight live views match v71_codex.

The old anim_frames cache predates the rebuild. Exact original artifacts were recovered from Claude's scratchpad/clips/final/slam, final/death and w10/throw, then copied to rebuilt_clips_codex/installed-sources/. Every one of the 26 original native color renders was independently re-pixelized using the native x4.4 settings and matched the installed RGBA crop [20,20,189,168] exactly. Only those accompanying native part-ID maps were used. No model rerender or uncertain bone-label transfer was needed. Source paths and hashes are recorded in recovered-sources.json and map-audit.json.

All original alpha bytes, transparent RGBA pixels, canvas sizes, positions, teal pixels and protected dark hardware colors are exact. Final colors stay within the live views palette and permitted teal ramp. All four metadata/install-record files are byte-for-byte unchanged. Only the 26 named live PNGs were replaced. No install/export/round script, paid generation or commit ran; no protected pipeline, game or model source file was edited.

Full current input backup: docs/art/2d/ape_l/anim_rebuilt_clips_pre_codex/.
Full current finished 51-frame archive: docs/art/2d/ape_l/anim_rebuilt_clips_codex/.
Helpers, audits and browser review: docs/art/2d/ape_l/rebuilt_clips_codex/.
Historical v71 and punch finish archives remain untouched.

## Verification and previews

- Godot import exits 0. view_art_check, views_check, battle_check and battle_fit_check PASS. The latter includes the current field zoom and staging; its existing unrelated kangaroo/pangolin allowances remain Claude's work.
- All 51 loaded frames captured before and after in both actual battle slots at 1280x720, with canvas/duration assertions. The fixture uses current Stage.clip_y placement; battle_fit_check separately models the live easing. Captures: anim_rebuilt_clips_codex/review/battle/{before,after}/. All 26 new poses are collected in review/{slam,throw,death}-battle-contact.png.
- Native battle_capture runs preserved immediately in rebuilt_clips_codex/battle_before/ and battle_after/.
- All eight unchanged view-lab facings load installed art. Fixture only isolates the existing gorilla and hides HUD; no scene edits. Captures and view-lab-eight-cameras.png preserved.
- Real Quake Slam and Ballast Throw actions each recorded for six seconds at 60fps. The review fixture tops up energy for Quake Slam so it fires; this recorded attempt misses while playing all ten frames. Ballast Throw deals 41 damage and plays all ten frames. No weapon stats changed. Recordings retain the current effects and later combat events.
- Defeat recorded for six seconds through controlled fatal damage and the actual damage/destruction playback queue; all six death frames observed, ending in the settled pose. It is a controlled defeat fixture, not a claim about a full player-driven defeat run.
- Clips, observed frame indices and combat result queues saved in review/combat_<clip>/audit.json. MP4s, posters and contact sheets are in review/.
- Fixed-palette before/after GIFs at exact 3x and finished GIFs at exact 2x preserve all three clips' durations exactly (10ms GIF precision). Every source-identical pose finishes identically, including across clip boundaries. Moving screen-pixel color changes are recorded in temporal-audit.json; this is not a zero-shimmer claim.
- Full frame comparisons: anim_rebuilt_clips_codex/<clip>-before-after-4x.png. Compact comparisons are in rebuilt_clips_codex/<clip>-comparison-2x.png. Contacts and browser loops were visually inspected, along with actual combat and lab captures.
- Measurements are records only: mean cluster 11.41-13.59 before and 8.19-10.90 after; stray share 1.21-1.73% before and 2.81-4.22% after. The small rim/steel highlights create small clusters. Full quality and Legacy gap measurements are preserved without a target band.

Review: http://127.0.0.1:8878/rebuilt_clips_codex/review.html. Local server PID 3612 at launch.

## Remaining source issue for Claude

The verified original raw color renders still reach the right camera edge on the far fist in death/3, death/4 and death/5: 29, 68 and 68 opaque native edge pixels respectively (816x816 sources). This is visible in the source before the finish and cannot be repaired by recoloring within an unchanged alpha mask. Slam and throw have no raw camera-edge contacts. This source issue is separate from the battle top-framing check, which passes. Correcting it needs a matching render handoff; do not restore old death frames. Final death's lowest opaque row is 127 versus feet_y 130, unchanged by the finish.

The 26-frame finishing task is complete and live. CODEX_IN_PROGRESS is removed at handover. Later source repairs and lighting/texture work remain Claude's handoff items.
