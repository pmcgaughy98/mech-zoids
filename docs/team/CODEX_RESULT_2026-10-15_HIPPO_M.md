# Hippo p40 finish, 2026-10-15

Finished and installed all 40 battle frames in six clips and all eight views. Shoulder, hip and knee hardware and the visible spine ridge now use 2e2235. A narrow dark contact seam on already opaque pixels separates the front and rear leg masses. Short copper trim strips break up the purple hull, with a restrained lit upper edge. The original cream toes, cyan eyes, snout, twin-cannon turret and back tubes remain intact.

18,431 opaque pixels changed: 15,475 across animation frames and 2,956 across views. This is a color-only finish. Alpha, canvas, alignment, feet metadata, timing and source geometry are unchanged. No reference or generated pixels were copied into game art.

## Carry-forward rules for Claude

| Fix | Classification | Rule |
|---|---|---|
| Dark joints | repeatable | Follow the actual narrow disc pieces on the upper-arm, forearm, thigh and shin bones. Take visible frame/accent/hub faces to the existing 2e2235 swatch. Preserve the surrounding purple armor and complete feet. Do not darken entire leg silhouettes. |
| Spine ridge | repeatable | Shade only the three native trim ridge meshes between the saddle plates to 2e2235. Keep the turret, barrels and tubes exact. Some ridge meshes are hidden by weapons; do not paint them back in. |
| Leg separation | repeatable | Follow the visible contact between projected front/rear leg masks. Within a narrow shared corridor, tint existing underbody and limb-core pixels 2e2235. Exclude armor faces, head, feet, cream colors, eyes, weapons and the outermost silhouette. This is a shaded seam, not a transparent cut. |
| Copper trim | repeatable | Use four upper-flank armor stations and two dorsal stations along the native six hull bands. Place a compact 2-4-pixel strip inside each exposed plate, using c98b6b with dca688 on a two-row strip's upper edge. Do not trace individual upper-contour columns: that produced a false zigzag in the first preview. |
| Per-facing exposure and final strength | hand only | Review all clips and facings after quantization. All battle poses expose four or five trim stations, usually five; views expose three to five (N has three). Occluded strips remain absent. Select the largest compact rectangle that fits each exposed face, instead of adding detached pixels or painting over greebles. |
| Preservation and temporal review | repeatable | Protect the complete mapped head, back weapons and feet; protect all original cream, teal and violet ground-line colors globally. Repeated identical source poses must finish identically. Inspect all frames and fixed-palette loops. |

## Preserved contract and provenance

All 48 initial live PNGs matched their SHA1 install records. CODEX_IN_PROGRESS protected this slice and was removed at handover. Original copies are docs/art/2d/hippo_m/anim_p40_pre_codex/ and p40_pre_codex/. Finished copies are anim_p40_codex/ and p40_codex/.

Views remain 132x83 with anchor [66,80]. Battle frames remain 134x90 with feet_y 84. Every alpha byte and transparent RGBA pixel is exact. Both metadata files and both .installed_hashes.json records are byte-for-byte unchanged. Frame order, durations, loop modes and strike markers are exact. Live PNGs equal the final review copies. The deliberate PNG hash mismatch lets the install guard detect this finish on the next rebuild.

Final colors use the live views.json palette plus the permitted teal ramp. Every original cream pixel, eye pixel and violet ground-line pixel remains exact. The complete mapped head, weapon and foot regions are also exact. The source snout and all four original leg silhouettes are preserved; no hidden toe or limb was drawn.

Every native color view/frame re-pixelized exactly to the installed crop and alignment before its ID map was used. Extra per-piece maps came from a read-only background Blender replay using the project Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md). Every replayed color image matched the native source. The model was never saved; its SHA256 and the native render/ID hashes remain unchanged. Evidence: input-audit.json, map-audit.json, piece-source.json and final-audit.json.

No installer, exporter or round script ran. No protected pipeline, game or model source changed. No commit or paid generator was used. Review helpers and new outputs are confined to the finished-record folders.

## Review and validation

- Godot import exits 0. view_art_check, views_check and battle_check PASS; logs are in p40_codex/.
- All 40 loaded frames were checked and captured in both actual battle slots, before and after, with canvas and duration assertions. Captures/manifests: anim_p40_codex/review/battle/{before,after}/.
- Required native battle captures against wolf were immediately preserved in p40_codex/battle_before/ and battle_after/.
- All eight actual view-lab directions load installed art. The review fixture uses the existing hippo actor alone, facing zero, with the lab HUD hidden. No position shift or native game-source change was needed. The default cast is saved as lab_default_cast.png; eight captures and view-lab-eight-cameras.png show the review fixture.
- A real Gape Crush attack against wolf was recorded through the combat queue: 240 frames at 60fps, including 23 damage and recovery. Video, GIF and contact: anim_p40_codex/review/combat.mp4, combat.gif and combat-contact.png.
- Six fixed-palette before/after loops and all 40 frames were inspected. Preview GIF timing rounds to 10ms; live timing remains exact. Repeated source poses finish identically. temporal-audit.json records remaining screen-pixel color changes as parts move; this is not a zero-shimmer claim.
- Eight-view comparison and six clip contact sheets are exact nearest 4x. Complete finished-frame contacts are finished-frames-1-2x.png and finished-frames-2-2x.png.
- Browser review: http://127.0.0.1:8875/p40_codex/review.html. Local-only review server PID at launch: 36376.

Measurements are records, not targets. Animation mean cluster size changes from 12.50-15.96 to 11.74-15.04 pixels; stray-color share changes from 0.81-2.20% to 1.18-2.61%. Views change from 13.36-15.60 to 12.99-14.35 pixels per cluster, and 0.77-2.12% to 1.08-2.27% stray share. Structural separation adds small trim clusters; the finish does not reduce every noise measure. Full quality and Legacy measurements are in finish-audit.json, final-audit.json and legacy-gap-record.json.

## Composition limits and remaining handoffs

No raw animation camera-edge cuts or top clipping in either battle slot were found. The original body bottom ranges from three pixels below the feet metadata row to one pixel above it through the poses; no alignment was changed.

All eight views and all 40 frames contain existing opaque contact pixels suitable for the leg-separation treatment. The views provide 22-166 eligible pixels depending on the facing. This does not create open background between the legs or reveal hidden legs. Full gap and trim counts are recorded per frame in finish-audit.json.

Next scheduled machine: pangolin p40. Claude's new nine-frame gorilla punch also still needs its finish. Re-read the current handoff and verify live files before starting either. Do not restore the old gorilla punch or overwrite its new 163x148 canvas.
