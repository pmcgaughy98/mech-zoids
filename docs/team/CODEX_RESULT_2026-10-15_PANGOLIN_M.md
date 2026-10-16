# Pangolin p40 finish, 2026-10-15

Finished and installed all 40 battle frames in six clips and all eight views. Gold scales now use a restrained face ramp, brighter dorsal scale edges and dark-grey seams between their native rows. Visible claws have a stronger red body, brighter hooked tips and narrow root valleys separating adjacent claws where space permits. Blue back spikes, cyan eyes, the native head/snout, weapons and red tail tip are preserved.

49,795 opaque pixels changed: 42,226 across animation frames and 7,569 across views. This is a color-only finish. Original alpha, canvas, alignment, feet metadata, frame timing and geometry remain exact. No reference or generated pixels were copied into the game.

## Carry-forward rules for Claude

| Fix | Classification | Rule |
|---|---|---|
| Scale face grouping | repeatable | Follow the native body scale meshes and gold tail-scale meshes. Group attached main-material details with their nearest real scale in rest space. Compress each surface into a few existing gold swatches; the upper body tier gets a lighter face than the lower flank. Keep native grey hardware and non-gold detail pixels exact. |
| Lit top tier | repeatable | Light the exposed upper edge of dorsal body scales and central upper tail scales. Keep side-scale highlights restrained. The first preview lit every leaf edge and looked like a bright lattice; restricting extra rims to the dorsal tier replaced it. |
| Grey row seams | repeatable | Identify the eight native body bands and the gold tail bands from their rest-space longitudinal positions. Apply a one-sided 3f3e43 seam only where gold surfaces from different rows touch. Keep the outermost silhouette and tiny foreshortened scale fragments out of the seam mask. No near-black silhouette ring. |
| Claw recovery and tips | repeatable | Use actual raw claw coverage, including thin hooks lost by dominant part IDs. Follow the three native knuckle/hook pairs on each foot. Use a02010 on visible claw bodies, c0402a on visible hooks and a small d86a4f tip catchlight. Do not spread red onto a hidden claw or unrelated foot hardware. |
| Claw separation | repeatable | Where two sufficiently large native claw groups touch, put a narrow 3f3e43 valley at their root interface. Preserve the distal red points and exterior alpha. Do not consume a one-pixel claw with a seam. |
| Occlusion and final art strength | hand only | Check every pose/facing. Some feet or hooks have no visible source pixels, and no 2D recolor can reveal them within this contract. Claw coverage and tip counts are recorded per foot in finish-audit.json. Review row highlight density after pixel quantization rather than lighting every scale contour. |

## Preservation and source correspondence

All 48 initial live PNGs matched their SHA1 install records. Original folders were backed up before edits. CODEX_IN_PROGRESS protected work and was removed at handover.

Views remain 206x87 with anchor [103,84]. Battle frames remain 155x132 with feet_y 127. Every alpha byte and transparent RGBA pixel is unchanged. Both live metadata files and both .installed_hashes.json records are byte-for-byte exact. Frame order, durations, loops and strike markers are preserved. Live PNGs equal the final review copies; the deliberate PNG hash mismatch lets the next install guard detect the finish.

Colors use the live views.json palette, the allowed teal ramp and c9cbd2, explicitly allowed by the current task because it is already present in the live art. Every original blue, eye and violet ground-line pixel is exact. Mapped head and weapon regions are exact. Only mapped gold-scale and actual visible claw pixels can change; all other source pixels are asserted exact. The complete native red tail is unchanged.

Every native color view/frame re-pixelized exactly to the installed crop and alignment before map use. Extra per-piece maps came from the same read-only background Blender workflow as the preceding machines, using the project Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md). View replay used the native mixed walk stance and 14-degree camera, with the side views at 18 degrees and turned 35 degrees. Every replayed color image matched its native source. The model was never saved; its hash and all native render/ID hashes remain unchanged.

No installer, exporter or round script ran. No protected pipeline, game or model source changed. No commit or paid generator was used. Local helpers and new review assets live only in the finished-record folders.

## Originals and review artifacts

- Originals: docs/art/2d/pangolin_m/anim_p40_pre_codex/ and p40_pre_codex/.
- Finished copies: docs/art/2d/pangolin_m/anim_p40_codex/ and p40_codex/.
- Before/after sheets at exact nearest 4x: p40_codex/before-after-4x.png and anim_p40_codex/<clip>-before-after-4x.png. Focused four-view sheet: four-view-focus.png.
- Six fixed-palette before/after loops at 4x, browser versions at 3x, finished loops at 2x. GIF duration precision is 10ms; live timings remain exact. Complete finished contacts: finished-frames-1-2x.png and finished-frames-2-2x.png.
- Browser review: http://127.0.0.1:8876/p40_codex/review.html. Local-only review server PID at launch: 1256.
- A real Scale Rake attack against hippo: anim_p40_codex/review/combat.mp4 (240 frames, 60fps), combat.gif and combat-contact.png. It records the attack, 17 damage, recovery and the following enemy action through the actual combat queue.
- Required battle snapshots were immediately preserved in p40_codex/battle_before/ and battle_after/.
- All 40 loaded frames, both actual battle slots, before and after: anim_p40_codex/review/battle/{before,after}/, manifests and per-clip installed contacts.
- Eight actual view-lab facings: p40_codex/lab_000.png through lab_315.png and view-lab-eight-cameras.png. The fixture uses the existing pangolin alone with facing zero and the HUD hidden; no scene shift or native game change. The default cast is preserved as lab_default_cast.png.

## Checks and measurement limits

Godot import exits 0. view_art_check, views_check and battle_check PASS. All 40 loaded frames pass canvas/duration checks in both battle slots; all eight lab facings load installed art. The combat recording completed. Final asset audits verify exact alpha/transparent pixels, palette, protected colors, metadata, live-copy hashes, native maps and model hash.

All 40 frames and six loop previews were inspected. Identical source starts finish identically. temporal-audit.json records color changes at otherwise unchanged screen pixels as surfaces move; this is not a zero-shimmer claim.

Measurements are records, not targets. Animation mean cluster size changes from 9.37-10.98 to 5.98-6.75 pixels, and stray-color share from 1.86-3.05% to 4.57-6.72%. View cluster size changes from 10.43-14.17 to 6.24-7.13 pixels, and stray share from 1.50-2.76% to 4.38-5.97%. The seams and hooks add small clusters; this is not a reduction in every measure of noise. Full records: finish-audit.json, final-audit.json and legacy-gap-record.json. Provenance: input-audit.json, map-audit.json and piece-source.json.

## Existing limits for Claude

- Three claw groups are visible on each of the three exposed feet in battle idle; the fourth foot is hidden. In the E view the near front and rear feet expose all three, the far front exposes two, and the far rear none. N exposes no claw hooks, and NE exposes only one front claw group. Other facings and action poses vary; per-foot source coverage/tip counts are recorded. Hidden claws were not invented.
- The original roll animation separates the red/gold tail surface from the grey tail core, visibly forking the tail. It is present before this finish. source-roll-tail-comparison.png records original and finished roll/5 side by side. Piece records show some scale meshes bound to tail.0 or tail.1 away from their corresponding core segment. Fixing binding/animation requires Claude's model work and fresh source frames; no geometry was changed here.
- No raw animation camera-edge cuts were found. Existing battle staging clips the raised tail in roll: enemy roll/3-6 loses 67, 72, 328 and 386 opaque pixels; player roll/5-6 loses 15 and 22. The loaded-frame checks pass but do not certify composition. The original body bottom ranges from two pixels below the feet row to 15 pixels above it. Details/captures are in final-audit.json and review/battle/.

The six-machine finishing pass has reached pangolin. The outstanding follow-up is Claude's newly replaced nine-frame gorilla punch. Preserve its new 163x148 canvas, timings and the other 42 padded finished frames; do not restore the old punch.
