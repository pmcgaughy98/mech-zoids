# Hippo p18 finish, installed

Task 1 hippo is finished and installed after Preston approved the gorilla and requested the next machine. Kangaroo is next, followed by pangolin, shoebill and wolf. Task 2 battle review is unlocked by the gorilla approval but has not started. The accidental wolf attachment was disregarded.

## Must match, checked on all eight facings

- Exact original 202x74 canvas, every alpha byte and foot anchor (101,71). No move, scale, crop, mirror or silhouette change.
- Original transparent pixels, both flat ground rows, cyan eyes/indicators and all cream tusks/toes/pressure-valve ends remain byte-for-byte unchanged.
- Purple barrel body, four short legs, broad muzzle/jaw, salmon flank panels, charcoal frame and original joint positions retained.
- Twin cannon, two torpedo tubes, paired flank jets, pressure valves and bow ram retain native p18 placement. Visible mouths stay dark; occluded pieces are not invented.
- All colors are from the 32 approved palette swatches. The input already conformed; no material remapping was necessary.

## Finish

Reduced fine checker shading within native purple/salmon plates, retaining actual part boundaries and deep recesses. Added restrained upper edge highlights, darker plate-colored side/underside edges, targeted cannon/jet housing highlights and a few existing grey joint highlights. Removed unambiguous interior singletons. The cream detail and cyan masks are protected throughout.

The helper uses existing p18 part-ID renders and checks their correspondence to the installed sprites before changing colors. The final pass changes 172-415 pixels per view, 2,094 total. Some texture remains around small overlapping plates and rear recesses; broad smoothing there would lose authored detail. No geometry or equipment placements were redrawn from the concept reference.

## Evidence and artifacts

- Original full installed views folder: docs/art/2d/hippo_m/p18_pre_codex/.
- Finished copies, review helpers, audit, notes, logs and comparisons: docs/art/2d/hippo_m/p18_codex/.
- Eight-view before/after at exact nearest-neighbor 4x: p18_codex/before-after-eight-4x.png. Rows alternate before and after. Individual pairs are also saved.
- Native game camera captures: p18_codex/view-lab-eight-cameras.png and lab_000.png through lab_315.png.
- Color/change metrics and input hashes: p18_codex/audit.json and statistics.md.

All eight live PNGs match the preserved final copies. views.json retains size, anchor, map, mirror state and the same approved palette; its source now points to the finished copies. The alignment importer was not rerun. Installation refused any live input differing from the untouched backup.

## Verification

- Godot headless import: exit 0.
- view_art_check.gd: PASS, six installed machines; hippo feet at (101,71).
- views_check.gd: PASS.
- Actual scenes/view_lab.tscn camera walkthrough: PASS; hippo actor loads installed art in se, s, sw, w, nw, n, ne, e across eight 45-degree camera steps.
- Inspected all eight before/after pairs and the actual camera grid. The existing lab crowds its enlarged sprites, obscuring parts of the hippo in several angles. The separate contact sheet exposes every facing fully. This task does not approve battle composition.

The engine reports inability to read the system certificate store; the import also reports inability to save its external editor settings. These environment diagnostics did not prevent import, rendering or the checks passing.

## Measurement limits and carry-forward

Color-cluster size increases in every view, to 4.57-5.97 pixels. Stray share falls in every view, from 11.7-16.7% to 9.8-12.0%. Dark edge share is 2.2-12.9%, increasing in several views as undersides darken. Upper-light scores rise to 97.1-214.3. These metrics do not establish battle readability or complete removal of texture. Hardware apertures remain constrained by their native pixel footprints.

Technique reused from docs/reference/sprite-rules-legacy-2026-10-12.md: material ramps, selective outlines and upper-left light. Project reference docs/art/reference/starters/hippo_m.png informs finish feel only. Native renders supply plate ownership, Pillow/NumPy perform audited color edits, and Godot supplies runtime evidence. No copied game art, paid generation, protected pipeline/model/script edits or commits.

Preserve p18_codex as the review record. When Claude rebuilds the hippo, carry this finish to its new silhouettes or flag the views needing another pass. Do not install these older PNGs over a newer model render; the part-ID and input guards are p18-specific.
