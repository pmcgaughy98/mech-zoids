# Updated gorilla punch finish, 2026-10-15

Finished and installed the nine replacement haymaker punch frames. The finish follows the established v71 green/orange palette: restrained plate cleanup, own-color selective outer edges, lit upper green plate edges, darker lower plate edges and small steel catchlights. Cyan eyes and dark hubs/rollers are exact.

2,605 opaque pixels changed across the nine punches. The other 42 animation PNG files, all eight finished views and the extra live view contact are byte-for-byte unchanged from this slice's input. No old punch frame was restored. The wider 163x148 canvas, feet_y 130, strike index 5 and durations [160,240,130,70,50,150,120,200,380] remain exact.

## Carry-forward rules

| Fix | Classification | Rule |
|---|---|---|
| Gentle plate cleanup | repeatable | Within sufficiently broad native part-ID regions, collapse only a one-rank local color fluctuation. Keep real dark material seams. |
| Selective outside edges | repeatable | Sample the same native part and color family. Lift exposed top edges and shade side/underside edges in their own green/orange ramp. Do not add a near-black silhouette ring. |
| Green plate separation | repeatable | Use the installed source's native part IDs to isolate broad visible green surfaces, including the arm plates. Light their exposed upper edge one step and shade the lower edge one step, retaining deep native seams and capping strong highlights. This avoids transferring uncertain bone labels from a later model. |
| Steel catchlights | repeatable | Lift only existing mid/light grey pixels on the upper edge of native parts. Keep original 181f1c, 272d38 and 2a2c31 hardware exact, preserving black hubs, rollers and muzzles. |
| Source selection and final pose review | hand only | Require exact source-to-live pixel correspondence before using a map. Review all nine poses together and through real combat. Do not rerender from a newer model and assume it represents these installed silhouettes. |

## Exact sources and preservation

The nine punch PNGs matched their current SHA1 install records. The other 42 intentionally differ from those records because they retain the prior finish. Each was verified pixel-for-pixel against live_backup_anim_1 in columns 0-148, with only transparent right padding to width 163. All eight views matched the saved v71 finish. These expected pre-existing differences were preserved.

A full current live animation backup is saved as docs/art/2d/ape_l/anim_punch_haymaker_pre_codex/. The complete current finished 51-frame archive, including untouched copies of the other 42 frames, is anim_punch_haymaker_codex/. The new review/helper folder is punch_haymaker_codex/. Historical anim_v71_codex and v71_codex records remain untouched.

The live Blender model and plan had advanced after the installed punch was produced. A read-only replay using the project Blender Scripting skill did not match the installed pixels and was rejected as a source. The exact original renders were recovered from Claude's punch/inst6 scratch artifacts and preserved in punch_haymaker_codex/installed-sources/punch/0-8/. Each was re-pixelized with the native settings and verified exactly against the installed 163x148 crop at [20,20,183,168]. Their accompanying native ID maps are therefore aligned to the actual installed punch.

An attempted bone-label transfer was also excluded from the final finish. The final routine uses only the verified native plate IDs and source colors; it does not use the later model's pose colors, geometry or bone labels. Diagnostic replay/identity artifacts remain in the review folder as evidence of the rejected route. The Blender model was not saved or modified by this work; concurrent model changes remain Claude's work.

Every original alpha byte and transparent RGBA pixel in the punches is exact. Canvases, positions, feet row, timing and strike marker are unchanged. Every teal eye pixel and the three protected dark hardware swatches are exact. Colors remain within the current live palette plus the permitted teal ramp. Both live metadata files and both .installed_hashes.json records are byte-for-byte unchanged. The live guard can detect this new punch finish on a future install.

Only nine live PNG files were replaced. No installer, exporter or round script ran. No protected pipeline/game/model source file changed. No reference/generated pixels were copied, no paid generator ran and no commit was made. CODEX_IN_PROGRESS protected the slice and was removed at handover.

## Validation and review

- Godot import exits 0. view_art_check, views_check and battle_check PASS.
- All 51 current animation frames were checked in both actual battle slots before and after, with loaded canvas and duration assertions: anim_punch_haymaker_codex/review/battle/{before,after}/. The nine new punches are collected in review/punch-contact.png.
- All eight unchanged views load installed art in the actual view lab. The fixture isolates the existing gorilla at facing zero and hides the HUD; no native scene change. The original cast and eight captures are preserved in punch_haymaker_codex/.
- Required native battle captures were immediately preserved in punch_haymaker_codex/battle_before/ and battle_after/.
- Actual Piston Knuckles combat against hippo was recorded for four seconds at 60fps, including 26 damage, recovery and the next enemy action. Files: anim_punch_haymaker_codex/review/combat.mp4, combat.gif and combat-contact.png.
- All nine finished poses, the before/after loop and actual combat contacts were inspected. The fixed-palette loop uses exact 3x comparison or 2x finished scaling. All punch durations are multiples of 10ms and fit GIF timing exactly. Live timings remain unchanged. temporal-audit.json records screen-pixel color changes through movement; it is not a zero-shimmer claim.
- Full comparison at exact nearest 4x: punch_haymaker_codex/before-after-4x.png. Finished contact at 2x: finished-frames-2x.png. Impact comparison: impact-comparison-4x.png.
- Browser review: http://127.0.0.1:8877/punch_haymaker_codex/review.html. Local-only server PID at launch: 35132.

Final auditing verifies the nine live punches, all 42 untouched animation file hashes, all eight views, the extra contact, every metadata/hash record and the preserved native source/ID hashes. Measurements are records, not targets: mean cluster size changes from 11.64-13.09 to 8.94-10.18 pixels; stray share from 1.43-1.87% to 3.09-4.16%. The added plate/steel highlights create small clusters. Full measurements and operation counts are in finish-audit.json, final-audit.json and legacy-gap-record.json.

## Existing composition limits for Claude

The new wide source has no raw camera-edge cuts in any punch frame. All nine fit the player's battle slot without top clipping. The higher enemy slot still clips seven poses: punch/0-5 and 8 lose 25, 625, 704, 730, 160, 17 and 4 opaque pixels respectively. The jump lifts the original body bottom as much as 21 pixels above the feet row; no pose or alignment was altered. Counts and actual captures are preserved in final-audit.json and review/battle/.

Other clips' previously reported camera/death issues were not changed by this nine-frame slice. The six-machine finish pass and this replacement-punch follow-up are complete on the current live sprites. Further geometry/animation repairs need matching source renders and a new finish handoff.
