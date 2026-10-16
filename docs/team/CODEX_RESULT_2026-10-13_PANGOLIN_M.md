# Pangolin p16 finish, installed

Task 1 pangolin is finished and installed after Preston requested the next machine. Shoebill is next, followed by wolf. Read live metadata before starting them because Claude is rebuilding those machines. Task 2 battle review has not started.

## Must match, checked on all eight facings

- Exact original 250x80 canvases, every alpha byte, transparent pixel and foot anchor (125,77).
- Both ground rows and every cyan eye pixel unchanged. No new cyan or halo.
- Four Delft-blue spine studs and all existing blue snout/hardware pixels unchanged pixel for pixel.
- Layered gold scales, arched body, four short legs, pointed snout, red claws and long segmented tail retain native shapes and placement.
- Shoulder racks, under-snout rotary gun and rump 2x3 launcher stay in their p16 positions. Visible apertures and dark joint/muzzle hubs remain; occluded pieces are not invented.
- The two darkest base grey shades and any extra-bottom grey shades are protected exactly.
- All output colors come from the 37 approved palette swatches, including its extra top/bottom shades and teal ramp.

## Finish and inputs

Reduced fine gold/red shading variations inside individual native parts, retaining the real seams between overlapping scales. Added restrained upper-edge highlights, selective outlines, targeted grey housing highlights and selective existing joint highlights. This is a modest finish on an already detailed sprite, changing 51-226 pixels per view, 1,179 total.

The current renders belong to restored p18, which the factory records as identical to retained p16. All eight p18 source RGBA images were checked against p16, and each p16 crop matched its installed sprite exactly after placement. A hashed snapshot of the 16 render/part-ID files is saved in p16_codex/source-renders; future builds cannot silently replace the guides.

The singleton cleanup found no unambiguous four-neighbor interior candidates. No isolated-detail removal is claimed. Some small-scale and rear texture remains where smoothing could merge scales or lose hardware detail. Apertures stay limited by their original pixel footprint.

## Artifacts and checks

- Untouched full installed folder: docs/art/2d/pangolin_m/p16_pre_codex/.
- Final copies, helpers, notes, input hashes, audit, measurements and logs: docs/art/2d/pangolin_m/p16_codex/.
- All eight before/after at exact nearest-neighbor 4x: p16_codex/before-after-eight-4x.png. Rows alternate before and after; individual facing pairs also saved.
- Actual Godot camera evidence: p16_codex/view-lab-eight-cameras.png and lab_000.png through lab_315.png.
- Per-view pixel changes and metrics: p16_codex/audit.json and statistics.md.

Guarded installation verified every live PNG and metadata file still matched the untouched backup before replacement. The installed PNGs match their preserved final copies. views.json retains canvas, anchor, map and mirror state; source points to the final folder and palette lists the complete approved swatches. The alignment importer was not rerun.

Godot import exits 0. view_art_check.gd passes for six machines, including pangolin feet at (125,77). views_check.gd passes. The actual view lab camera walkthrough passes, resolving installed pangolin art through e, se, s, sw, w, nw, n, ne. All eight comparison pairs and the final runtime grid were inspected.

The review helper temporarily isolates a pangolin ViewSprite at the center of the actual lab and shifts the review stage down, so every part is visible. It exercises the real camera/view resolution without modifying the shipping scene or scripts. These captures are an isolated art review, not approval of battle composition.

Godot reports inability to read the system certificate store; import also reports inability to save external editor settings. These environment diagnostics did not prevent import, rendering or the checks passing.

## Measurement limits and carry-forward

Dark edge share falls in every facing, to 15.5-20.8%. Upper-light scores rise to 111.6-164.4. Clusters are 4.02-5.04 pixels, increasing in six facings and decreasing slightly in the rear three-quarter views. Stray share is 9.5-13.2%; it improves in most facings but rises slightly in ne/nw. These metrics do not establish battle readability or complete texture removal. Two facings remain slightly above the historical 20% dark-edge ceiling.

Technique reused from docs/reference/sprite-rules-legacy-2026-10-12.md: material ramps, selective outlines and upper-left light. The project concept pangolin_m.png informs finish feel only; native parts determine geometry and placement. Pillow/NumPy provide audited color edits and Godot supplies runtime evidence. No copied game art, paid generation, protected model/pipeline/script edits or commits.

Preserve p16_codex as the review record. On a rebuild, carry this finish to the new silhouettes or flag affected views. Do not install these older PNGs over new geometry.
