# Gorilla v71 finish, 2026-10-15

Completed the gorilla slice of CODEX_TASKS_2026-10-15.md: generated a new v71 illustration, then finished all 51 battle frames and eight views on their current installed shapes. The main visual change is stronger separation of the upper-arm and forearm guards, using lit upper rims and shaded undersides. Original black hubs, knuckle rollers and visor remain intact. Ready for Preston's review before continuing to the wolf.

## What changed and what can move into the pipeline

| Kind of fix | Classification | Treatment |
|---|---|---|
| Upper-arm / lower-arm guard separation | repeatable | Bone-category masks follow the actual posed surfaces. Lit top row and darker underside make the green plates distinct; no new transparent armpit. The rig weights lower-arm guards mainly to hand groups, so use actual weighted surfaces, not group names alone. |
| Material-colored silhouette edges | repeatable | Green/orange edges use their own darker material shades, with a lit top rim. Lift near-black outer rings only where nearby material supports it. Deep internal seams and grey hubs remain exact. |
| Gentle plate cleanup | repeatable | Collapse only one-rank local noise within the same source part/material, preserving strong bevel transitions and tiny details. |
| Grey hardware upper edges | repeatable | One-step highlight on existing mid-light grey top pixels; original dark-grey hub/roller/muzzle pixels are protected byte-for-byte. |
| Per-facing and per-pose read | hand only | Reviewed all eight views, all seven frame sheets, looping clips and actual battle captures. Visual placement/strength still needs artist judgment; the generated illustration cannot supply masks or correct occlusion. |

26,063 opaque pixels changed: 22,312 across 51 battle frames and 3,751 across eight views. Fix-operation counts overlap and are recorded separately: 14,789 selective-edge operations, 7,434 grey-edge operations, 1,837 gentle-cleanup operations, 1,594 upper-arm and 546 lower-arm operations.

## Preserved contract and must-match items

- Three orange-capped back blocks stay in the native arrangement. Right-shoulder gatling and left-shoulder launcher stay where the model exposes them. No hidden parts painted in.
- All 59 alpha channels, dimensions, transparent RGBA pixels and positions are exact. Views remain 202x111, anchor [101,108]. Animation remains 149x148, feet_y 146.
- Every teal pixel is unchanged, with no new teal. Existing darkest three grey swatches are unchanged exactly, protecting black knuckle rollers, shoulder/fist hubs and dark weapon mouths.
- All final opaque colors come from the original live views.json palette plus the allowed teal ramp. Violet ground-line pixels are unchanged.
- views.json, anim.json and both .installed_hashes.json files remain byte-for-byte unchanged. Frame order, per-frame duration, loops and strike markers are exact. No importer, exporter or round script ran.
- Each live PNG equaled Claude's SHA1 install record before work. All 59 now equal the preserved finish copies; their deliberate mismatch with the unchanged install records allows live_guard.py to detect this finish on a future rebuild.

## Inputs, backups and output

- Original animation backup: docs/art/2d/ape_l/anim_v71_pre_codex/.
- Original view backup: docs/art/2d/ape_l/v71_pre_codex/.
- Finished battle copies: docs/art/2d/ape_l/anim_v71_codex/.
- Finished view copies and review helpers: docs/art/2d/ape_l/v71_codex/.
- Eight-view sheet at exact nearest 4x: v71_codex/before-after-4x.png. Focused front/quarter sheet: four-view-focus.png.
- Seven frame sheets at exact nearest 4x: anim_v71_codex/<clip>-before-after-4x.png. Fixed-palette before/after loops: <clip>-comparison.gif. Finished loops at nearest 2x: <clip>-finished.gif.
- Generated illustration: v71_codex/gorilla-v71-generated-reference.png. Built-in imagegen mode, not CLI; reference-only, never sampled or installed into the sprite slots. Prompt and inputs: v71_codex/generation-prompt.txt. The native model's back-block arrangement remains authoritative.
- Browser review: http://127.0.0.1:8871/v71_codex/review.html, with a narrow-panel layout showing the finished loops at 2x. Local saved page: v71_codex/review.html.
- Actual combat recording: anim_v71_codex/review/combat.mp4 (60fps, 4 seconds), combat.gif (20fps preview) and combat-contact.png. This is a real Piston Knuckles action against the hippo, with damage flash/number and recovery, not a posed animation mockup.

## Source-map evidence and tools

All eight native view renders and all 51 native animation renders were pixelized into review-only files using the current Legacy settings. Each result exactly matches the untouched installed pixels after reproducing the original alignment/crop for verification only. map-audit.json records source render, ID and pixel hashes. No live alignment/export was rerun.

The native part maps bound material edits. Extra flat bone-category maps were made in background Blender using the project's Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md) to distinguish moving upper-arm and lower-arm surfaces. Only review maps were written. The source .blend hash was checked throughout and at completion; the .blend was never saved. Semantic replay provenance: semantic-source.json.

Pillow/NumPy/SciPy supplied deterministic grid/palette edits and audits; built-in imagegen supplied the separate illustration; Godot supplied actual runtime captures/checks; the in-app browser displayed all seven looping previews. Existing measured sprite technique and the 2026-10-14 Legacy gap were reused for synthesis. No reference pixels copied, no paid mesh/sprite connector needed, no protected pipeline/game scripts changed, no commits.

## Verification and limits of the checks

- Original live hashes matched: 8 views and 51 battle frames. Backups preserved before editing; CODEX_IN_PROGRESS protected the machine during work and was removed at handover.
- Godot headless import: exit 0. view_art_check.gd, views_check.gd and battle_check.gd: PASS. battle_check is a combat-rule regression; it does not certify art composition.
- All 51 installed frames captured in both actual battle slots, before and after, with loaded dimensions and durations checked: PASS. Evidence: anim_v71_codex/review/battle/{before,after}/ and <clip>-installed.png.
- Actual view_lab.tscn rotated through all eight gorilla facings: PASS; captures lab_000.png through lab_315.png and view-lab-eight-cameras.png. The lab still crowds overlapping machines and crops their upper edges.
- Required standard battle captures were preserved immediately in v71_codex/battle_before/ and battle_after/.
- Seven fixed-palette GIF loops reviewed with frame sheets and browser playback samples. Three groups of identical source poses yield identical finished pixels. No per-frame palette generation or histogram changes. temporal-audit.json records changes at otherwise unchanged source pixels; pose-context changes remain possible, so this is not a mathematical proof of zero shimmer. GIF durations have 10ms precision; live metadata preserves 165ms gait timing exactly.
- final-audit.json confirms 59 final live PNGs, original alpha/transparency, palette, metadata/guard records and source .blend hash. finish-audit.json holds per-frame changes and quality measurements.
- Quality numbers are records, not targets: animation dark-edge share fell from 12.4-23.4% to 3.9-11.0%; average-cluster range went from 11.3-14.5 to 9.0-11.3 pixels; measured stray share increased from 1.0-2.1% to 2.4-3.7% as selective rims introduced smaller clusters. This pass does not claim every noise metric improved. Preston's visual judgment decides the result.
- Existing engine certificate-store warnings remain; sandboxed import cannot save external editor settings. Imports and checks completed successfully.

## Existing camera/export issues for Claude

These are present in the untouched inputs and before captures. Color changes cannot repair them while preserving silhouettes, canvas and metadata.

1. Animation feet_y is 146 although idle/0's lowest body pixel is row 130; the detached ground line supplies the metadata feet. The player canvas is therefore translated up 26 pixels, enemy up 46. Several attacks and the enemy gorilla's head clip at the viewport top; the body appears raised relative to its line. The exact affected frames/pixel counts are in final-audit.json.
2. The raw camera already cuts geometry in punch/5-7, slam/1-4, throw/3 and 5-7, and death/4-5. Some are visible as cut limbs/fists even though the exported PNG has transparent padding. Raw camera-edge counts are recorded separately from installed-canvas edge counts.
3. Death still tips and lifts the model rather than settling on the floor. Compare source frame sheets and actual death-installed.png before approving the animation foundation.

Please fix the rig/camera/framing or feet derivation on Claude's side and carry the repeatable color treatments to the resulting new frames. Do not restore old silhouettes over a rebuilt set. The other five machines remain untouched by this finish pass, pending Preston's gorilla review.
