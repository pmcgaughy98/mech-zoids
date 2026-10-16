# Gorilla wider death finish, 2026-10-16

Finished and installed all six replacement death frames. 2,012 opaque pixels changed using the established green/orange finish. The other 45 animation PNGs and all eight views plus the extra live view contact remain byte-for-byte unchanged from this slice's input. No earlier clipped death silhouette was restored.

The new 173x148 canvas, feet_y 130, durations [80,100,130,180,250,1000], once playback and strike -1 remain exact. Every other clip's timing and all four metadata/install-record files are byte-for-byte unchanged.

## Carry-forward rules

| Fix | Classification | Rule |
|---|---|---|
| Gentle plate cleanup | repeatable | Collapse only one-rank internal fluctuations in sufficiently broad regions of the same native part and material. Preserve real dark seams. |
| Selective outer edges | repeatable | Use the same native part's green/orange ramp to lift exposed upper edges and shade side/underside edges. Do not add a near-black silhouette ring. |
| Green plate separation | repeatable | Light exposed upper edges and shade lower edges of broad visible green surfaces. Keep deep native seams and cap already strong highlights. |
| Steel catchlights | repeatable | Lift existing mid/light grey upper edges only; preserve 181f1c, 272d38 and 2a2c31 hardware, rollers, hubs and muzzles exactly. |
| Source and pose review | hand only | Require exact original color-render correspondence before native ID-map use. Review the whole clip and loaded battle poses; retain the recovered fist silhouette and do not paste back old frames. |

## Inputs, sources and preservation

All six raw death PNGs matched their current SHA1 install records. The other 45 frames matched anim_rebuilt_clips_codex in columns 0-168, with only four transparent columns on the right. All eight views matched v71_codex. Full current input backup: docs/art/2d/ape_l/anim_death_wide_pre_codex/. Full current finished 51-frame archive: anim_death_wide_codex/. Helpers, sources and preview: death_wide_codex/. Historical finish archives remain untouched.

The exact wide source artifacts were recovered from Claude's scratchpad/ape_death/death/0-5/ and preserved in death_wide_codex/installed-sources/death/. Every original 992x992 color render independently re-pixelized exactly to its installed 173x148 RGBA crop [40,40,213,188], using native x4.4 settings. Only those paired native ID maps informed the finish. There was no model rerender or bone-label transfer. Source paths and hashes are in recovered-sources.json and map-audit.json.

Every alpha byte, transparent RGBA pixel, canvas, position, teal eye pixel and protected dark hardware pixel is exact. Final colors stay in the current views palette plus the permitted teal ramp. The model SHA256 remains unchanged, and no model was opened/saved for this slice. Only the six named live PNGs were replaced. No installer/exporter/round script ran; no protected pipeline/game/model source changed. No generated/reference pixels, paid tool or commit was used. CODEX_IN_PROGRESS was removed at handover.

## Verification and review

- Godot import exits 0. view_art_check, views_check, battle_check and battle_fit_check PASS.
- All 51 current loaded frames captured before and after in both actual battle slots at 1280x720 with canvas/duration assertions and current Stage placement. Captures/manifests: anim_death_wide_codex/review/battle/{before,after}/. New death poses collected in review/death-battle-contact.png.
- Required native battle_capture runs preserved immediately in death_wide_codex/battle_before/ and battle_after/.
- Six seconds of controlled defeat playback recorded at 60fps through the actual damage/destruction queue. All six death indices observed, including the final settled pose. The fixture applies 190 fatal damage; it is a controlled defeat test, not a full player-driven loss run. Queue and frame-index audit: review/combat_death/audit.json. Recording: review/combat_death.mp4; contact: review/death-combat-contact.png.
- All eight unchanged views load in the actual lab's solo-focus mode, using its own placement and rotation. Default cast, eight captures and view-lab-eight-cameras.png preserved; no scene edits.
- Fixed-palette loop before/after at exact 3x and finished at exact 2x, with original durations represented exactly at GIF's 10ms precision. All six frame comparisons at nearest 4x; compact 2x contact in death_wide_codex/. Identical source poses finish identically; temporal-audit.json records moving screen-pixel color changes without a zero-shimmer claim.
- Full frame contacts, loop, actual defeat playback and lab captures were visually inspected.
- Measurements are records, not targets: mean cluster size 12.53-13.34 before, 9.33-9.88 after; stray share 1.25-1.76% before, 3.21-3.94% after. Small edge highlights add small clusters. Full quality and Legacy records are saved in finish-audit.json, final-audit.json and legacy-gap-record.json.
- Closing roster check: all 299 live animation/view PNGs across all six machines match their current saved finished copies. Evidence: finished-roster-audit.json and check_finished_roster.py. Shoebill uses anim_p85_buffet_codex; pangolin uses anim_p41_codex/p41_codex; gorilla now uses anim_death_wide_codex with v71_codex views. Wolf, kangaroo and hippo retain their previous finished archives.

Review: http://127.0.0.1:8881/death_wide_codex/review.html. Local server PID 7016 at launch.

## Source issue resolved and queue status

Claude's wider renders resolve the reported far-fist camera cut: all six original native images have zero opaque pixels on every camera edge, including death/3-5, which previously had 29/68/68 at the right edge. The wider installed fist silhouette remains exact through the finish. This closes the gorilla source-edge follow-up.

The October 16 creature-factory finish queue is complete: shoebill Wing Buffet, pangolin tail frames/views and gorilla wider death frames. Remaining source/design notes stay in their reports: west-view pangolin tail-tip cut, hidden claws, wolf edge pixels and narrow shoebill barrel sections. Lighting/texture work remains on Claude's side until a new handoff; no such work was started here.
