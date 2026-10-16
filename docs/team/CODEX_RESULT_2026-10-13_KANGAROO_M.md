# Kangaroo p42 finish, installed

Task 1 kangaroo is finished and installed after Preston requested the next machine. Pangolin is next, followed by shoebill and wolf. Check live metadata before starting each; Claude is continuing to rebuild machines. Task 2 battle review has not started.

## Must match, checked on all eight facings

- Original 170x116 canvas, every alpha byte, transparent pixel and foot anchor (85,113) exactly.
- Both ground rows and all cyan eye pixels unchanged; no new cyan or halo.
- Two upright ears with dark cores, angular muzzle, segmented neck, two boxing gloves, closed pouch hatch, bent hind legs, long feet and tapered segmented tail retain their native shapes and placement.
- Right-shoulder 3x2 rocket pod, left-shoulder rotary gun and paired hip boosters remain in their p42 positions. Visible apertures and dark mechanical hubs are retained; occluded hardware is not invented.
- The two darkest grey shades are unchanged pixel for pixel, protecting frame recesses and muzzle mouths.
- Only the 19 approved swatches in tools/art/palettes/kangaroo_m.json. Input already conformed; no material remapping.

## Finish and source ownership

Reduced checker texture inside red torso, pouch, hip and tail plates while retaining real seams and small detail. Added restrained upper-edge highlights, selective outlines, weapon housing highlights and existing grey joint highlights. The final underside revision respects the palette's edge floor, avoiding newly near-black edges.

The factory notes say p44 restores retained p42. All eight p44 source RGBA images were verified identical to p42 before using the current native renders. The p42 crops also matched the installed sprites exactly after placement. A hashed snapshot of the 16 render/part-ID files is saved under p42_codex/source-renders so another rebuild cannot silently replace these guides.

The pass changes 121-296 pixels per view, 1,512 total. Small tail, charcoal and hardware textures remain where smoothing could erase mechanical detail. Hardware aperture readability remains limited by the native pixel footprint.

## Artifacts and verification

- Full untouched installed folder: docs/art/2d/kangaroo_m/p42_pre_codex/.
- Final copies, comparisons, input hashes, measurements, helpers and logs: docs/art/2d/kangaroo_m/p42_codex/.
- Eight-view nearest-neighbor 4x comparison: p42_codex/before-after-eight-4x.png. Rows alternate before and after; individual pairs also saved.
- Actual Godot camera evidence: p42_codex/view-lab-eight-cameras.png and lab_000.png through lab_315.png.
- Detailed metrics: p42_codex/statistics.md and audit.json. The first darker draft is retained separately under revision1.

Guarded installation accepted only the original backup or the recorded first draft, refusing unrelated live changes. Final installed PNGs match the preserved final copies. views.json retains canvas, anchor, map, mirror state and palette; only its source changes. The alignment importer was not rerun.

Final Godot import exits 0. view_art_check.gd passes for six machines with kangaroo feet at (85,113). views_check.gd passes. The final actual view lab camera run passes and resolves installed kangaroo art in e, se, s, sw, w, nw, n, ne. All eight comparison pairs and the final runtime grid were inspected.

The shipping lab's cast does not contain kangaroo. The review helper temporarily adds the actual ViewSprite actor to that scene, hides its other actors and shifts the review stage down to keep the ears fully visible. It exercises the real camera/view resolution without changing the shipping scene or script. These captures are an isolated review setup, not a battle composition approval.

The engine reports inability to read its system certificate store, and import reports inability to save external editor settings. Neither prevents import, rendering or the checks passing.

## Measurements and carry-forward

Clusters increase in all eight views, to 3.87-5.77 pixels. Stray share is 9.0-15.5%, improving most in the side views; the rear three-quarter change is small. Dark edge share falls or stays equal in every view, to 9.2-23.8%. Upper-light scores are 66.7-142.2. Remaining dark frame edges exceed the historical 20% reference ceiling in two views; the task's real-frame details are preserved rather than recolored solely to satisfy the metric.

Technique reused from docs/reference/sprite-rules-legacy-2026-10-12.md: material ramps, selective outlines and upper-left light. Project concept kangaroo_m.png informs finish feel only; native parts determine placement. Pillow/NumPy supply audited color changes, and Godot supplies runtime evidence. No copied game art, paid generation, model/pipeline edits or commits.

Preserve p42_codex as the review record. On a rebuild, carry the color finish to the new silhouettes or flag the affected views; do not install these older sprites over new geometry.
