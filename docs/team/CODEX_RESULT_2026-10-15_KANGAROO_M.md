# Kangaroo p68 finish, 2026-10-15

Finished and installed all 40 battle frames in six clips and all eight views. The orange thigh plate reads smaller within a grey steel surround, with clearer hip/knee hardware. Both visible foot caps have dark distal tips. Tail surfaces have a compact orange ramp with narrow seams between visible links. Forearm/glove and shoulder-gun upper edges are easier to distinguish. Native ears, head, eye, shoulder gun and hip boosters remain in their original arrangement.

31,384 opaque pixels changed: 26,035 across battle frames and 5,349 across views. This is a color-only finish; all original alpha, dimensions, feet positions, timing and metadata are exact. No reference/generated pixels were copied into game art.

## Fixes for Claude

| Fix | Classification | Carry-forward rule |
|---|---|---|
| Steel around the orange thigh plate | repeatable | Follow visible thigh surfaces, excluding real dark hardware. Shade roughly the outer 30% in the existing grey ramp and retain a restrained lit orange lip. Choose a consistent border width for a whole plate; for thin foreshortened plates use hip/knee end caps instead of a border that consumes the orange face. Main battle idle treatment is about 31%; pixel quantization/occlusion puts exposed plates across the set at roughly 26–41%. |
| Hip and knee discs | repeatable | Use the real joint pieces, keeping dark hubs exact. Convert exposed orange disc trim to mid-grey and light the existing upper edge. Do not recolor calf plates or shin rods as joints. |
| Dark toe/foot-cap tips | repeatable | The native toe meshes are mostly covered by the orange foot cap. Tint the distal two pixels of the visible cap itself, oriented away from the visible shin. Keep the existing footprint and occlusion; do not draw a hidden toe or a second hidden foot. |
| Tail bands and joints | repeatable | Keep the nine native tail links. Simplify their face fill into the existing orange ramp, light the continuous upper tail contour, and use a one-pixel seam at each exposed link boundary. Keep real inter-link hardware dark. Apparent band widths vary with foreshortening; do not force a fixed-width pattern across all facings. |
| Arm/gun separation | repeatable | Light the existing steel upper edges of the forearms/gloves and gun housing. Keep native black hubs, pistons and gun mouths exact. Do not change the native gun or booster design to match the older generated reference. |
| Eyes, head and ground-line protection | repeatable | Protect the complete native head/ear category, every teal pixel, dark hardware categories and both violet ground-line swatches. View part maps can extend beneath a foot into the generated line, so semantic masks alone are insufficient. |
| Per-facing/pose strength and acceptance | hand only | Review every sheet and all six loops. The first tail-lighting pass produced a false checker pattern on overlapping links; continuous-surface lighting plus a narrow link seam replaced it. Anatomical thresholds and final art judgment remain build-specific. |

## Preserved contract and source verification

- All 48 initial live PNGs matched their SHA1 install records. Original folders were copied before any edit. CODEX_IN_PROGRESS protected work and was removed at handover.
- All final alpha bytes, canvases, transparent RGBA pixels and alignment are exact. Views stay 172x123 with anchor [86,120]; battle frames stay 124x132 with feet_y 129.
- views.json, anim.json and both .installed_hashes.json files are byte-for-byte unchanged. Frame order, durations, loops and strike markers remain original. Their deliberate live PNG hash mismatch allows the guard to detect this finish on a future rebuild.
- Final colors use the current live views.json palette plus the allowed teal ramp. Every teal pixel and violet ground-line pixel is exact. The finish protects mapped dark hardware and head/ear pixels exactly.
- Every native color view/frame re-pixelized exactly to the untouched installed crop/alignment before its part map was used: eight views and 40 frames. Native render/ID hashes are still unchanged at handover.
- Extra flat piece maps came from a read-only background Blender replay of kangaroo_m.blend using the previously applied project Blender Scripting skill. Each replayed color image matched the corresponding native source before its piece mask was trusted. Records carry dominant material, weighted bone and rest-space bounds. The model hash is unchanged and the blend was never saved.
- No installer/exporter/round script ran. No protected pipeline/game/model source file was edited. No commit or paid generator was used. Existing Legacy studies and the new reference supplied technique only.

The final ground-line audit caught 73 edited line pixels in the eight view previews. The complete original violet ramp is now protected. Excluding the line from foot-cap orientation also refined the view foot masks. All 40 battle PNGs remained byte-identical to the already captured battle pass, verified by hash; only view files changed in that correction.

## Originals, finished copies and review

- Originals: docs/art/2d/kangaroo_m/anim_p68_pre_codex/ and p68_pre_codex/.
- Finished copies: docs/art/2d/kangaroo_m/anim_p68_codex/ and p68_codex/.
- Eight views at exact nearest 4x: p68_codex/before-after-4x.png. Focused S/SE/E/SW sheet: four-view-focus.png.
- Every clip at exact nearest 4x: anim_p68_codex/<clip>-before-after-4x.png.
- Six fixed-palette before/after loops: <clip>-comparison.gif. Finished loops at 2x: <clip>-finished.gif. Pingpong order includes reversed interior frames; preview timing rounds to 10 ms, while live timing is exact.
- Complete finished frame contacts: p68_codex/finished-frames-1-2x.png and finished-frames-2-2x.png.
- Browser review: http://127.0.0.1:8873/p68_codex/review.html; local saved page: p68_codex/review.html. Local-only preview server PID at launch: 32504.
- Real Impact Boxing Gloves attack against the hippo: anim_p68_codex/review/combat.mp4 (60fps, four seconds), combat.gif (20fps), and combat-contact.png. The attack, 21-damage response, recovery and following enemy action were captured through the actual combat queue.
- Native required before/after battle captures: p68_codex/battle_before/ and battle_after/.
- All 40 installed frames in both battle slots, with loaded canvas/duration checks: anim_p68_codex/review/battle/{before,after}/, manifests and <clip>-installed.png contacts.
- Eight actual view-lab directions: p68_codex/lab_000.png through lab_315.png and view-lab-eight-cameras.png. The review helper substitutes a single kangaroo in the actual lab cast, since the default cast does not include it; game source stayed unchanged.

## Checks and measurement limits

Final Godot import exits 0. view_art_check, views_check and battle_check PASS. All 40 loaded frames pass dimension/duration checks in both battle slots; all eight lab facings load installed art. The real boxing recording completed. Final live files equal their finished copies, with exact alpha/transparent pixels, eyes, ground lines and metadata; original native maps and model hash remain intact.

All six loops and full frame sheets were reviewed. Identical source starts shared by jab/0, flak/0, kick/0 and death/0 finish identically. temporal-audit.json records remaining color changes at otherwise unchanged screen pixels as parts move; this is not a zero-shimmer claim.

Measurements are records, not acceptance targets. Animation mean cluster size changes from 10.41–12.43 to 7.39–8.66 pixels, while stray-color share rises from 1.51–2.92% to 3.90–6.03%. View cluster size changes from 10.46–13.47 to 7.90–9.41; stray share rises from 1.66–2.30% to 3.59–5.02%. Structural plate/tail separation improved; the finish does not reduce every measure of pixel noise. Full measurements and operation counts: finish-audit.json, final-audit.json and legacy-gap-record.json. Input/map evidence: input-audit.json, map-audit.json and piece-source.json.

## Existing issues for Claude

- No raw animation camera edge cuts were found. Existing battle staging still crops ears/head at the top during some actions: player kick/3–7 clips 4–34 pixels; the higher enemy slot clips several jab/flak/hit frames and more of kick/1–8, up to 466 pixels. The loaded frame checks pass, but do not certify composition. Per-frame counts and captures are preserved in final-audit.json and review/battle/.
- Original body bottoms move from the feet row to 13 pixels above it through action poses. No alignment or animation edits were made.
- Default view-lab framing clips ear tips/overlaps its HUD in some facings, visible in the saved actual lab captures. Fixing scene staging belongs on Claude's side.
- In NE and N the far foot exposes only one and three native pixels respectively. It was not expanded or redrawn. The visible foot caps elsewhere carry the new dark tips.

Next: shoebill p84, then hippo p40 and pangolin p40. Re-read the latest handoff and verify live install hashes before starting each. Historical p42 finishes and every generated concept remain untouched.
