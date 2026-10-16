# Shoebill p62 finish, installed

Task 1 shoebill is finished and installed after Preston requested the next machine. Wolf is next. Read its live metadata before starting: Claude has continued rebuilding the machines. Task 2 battle review has not started.

## Must match, checked on all eight facings

- Exact original p62 122x123 canvases, every alpha byte, transparent pixel and foot anchor (61,120).
- Both ground rows and all cyan eye pixels unchanged; no new cyan or halo.
- Gold hooked bill, nostrils, mouth, clamp teeth, blue crest, long plated neck, pale-blue body armor, wing plates and dark feather plates retain native shapes and placement.
- Two grey articulated legs in the p62 stance, gold cuffs and splayed feet remain exactly positioned.
- Head-mounted Stillwater Lance, including the attached p62 skull pylon, and two shortened breast guns remain in their native positions. Visible dark mouths and hubs are retained; occluded parts are not invented.
- Darkest grey frame shades and the deepest interior blue/gold mouth/seam pixels are unchanged exactly.
- All output colors are from the 26 approved palette swatches, including its teal ramp.

## Finish

Reduced checker shading within individual blue/gold parts, including the navy wing planes, while preserving deep seams and feather divisions. Even checker ties collapse to one palette shade rather than retaining alternating pixels. Added restrained upper edges, selective outlines and targeted grey gun-housing/pylon and joint highlights. The pass changes 162-421 pixels per view, 2,242 total.

Small wing/hardware textures remain where part ownership is uncertain. The separate singleton cleanup found no remaining unambiguous candidates; reduced stray share comes from plate cleanup. Existing detached pixels near the legs remain under the exact-alpha requirement. Their removal or repositioning would require a native model/render correction by Claude.

## Current build and records

The initial p58 draft was not installed. Live sprites changed during the pass; the installation guard refused to replace them. Work was carried to p62, including its corrected head-gun attachment and shorter breast guns. The preserved p58 folder is labeled draft only; its camera logs observed newer live art and are not evidence of a p58 installation.

Native p62 crops match the installed input exactly after placement. Native render dimensions agree, and hashed copies of the 16 render/part-ID files are saved under p62_codex/source-renders, protecting the guides from future rebuilds.

- Full untouched installed p62 folder: docs/art/2d/shoebill_m/p62_pre_codex/.
- Final copies, helpers, notes, audit, measurements, hashes and logs: docs/art/2d/shoebill_m/p62_codex/.
- Eight-view nearest-neighbor 4x comparison: p62_codex/before-after-eight-4x.png. Rows alternate before and after; individual pairs are also saved.
- Actual Godot evidence: p62_codex/view-lab-eight-cameras.png and lab_000.png through lab_315.png.
- Detailed changes and scores: p62_codex/audit.json and statistics.md.

## Verification

Guarded p62 installation verified every live PNG and metadata file still matched the untouched backup before replacement. Final live PNGs equal their preserved finished copies. views.json retains size, anchor, map, mirror state and palette; source points to the final folder. The alignment importer was not rerun.

Godot import exits 0. view_art_check.gd passes for six machines with shoebill feet at (61,120). views_check.gd passes. The actual view lab camera walkthrough passes through e, se, s, sw, w, nw, n, ne, loading installed shoebill art. All eight comparison pairs and the final runtime grid were inspected.

The review helper temporarily isolates a shoebill ViewSprite in the real lab and shifts the review stage down to expose the full bill, gun and feet. Shipping scene/scripts are unchanged. This is an isolated art review, not approval of battle composition.

Godot reports inability to read the system certificate store; import also reports inability to save external editor settings. Neither prevents import, rendering or checks passing.

## Measurements and carry-forward

Cluster size increases in all facings, to 4.32-5.72 pixels. Stray share falls in all facings, from 9.8-15.3% to 8.7-12.9%. Dark edge share falls in all facings, to 10.6-21.4%; ne remains slightly above the historical 20% reference ceiling. Upper-light scores rise to 124.4-197.9. These metrics do not establish battle readability or complete removal of texture.

Technique reused from docs/reference/sprite-rules-legacy-2026-10-12.md: material ramps, selective outlines and upper-left light. Project concept shoebill_m.png informs finish feel only; p62 supplies the pose and placement. Pillow/NumPy provide audited color edits and Godot supplies runtime evidence. No copied game art, paid generation, protected model/pipeline/script edits or commits.

Preserve p62_codex as the review record. Future rebuilds need this finish carried onto their new silhouettes or affected views flagged; do not install older PNGs over newer geometry. The live hippo is now p19, superseding the earlier approved p18 finish; its p18_codex record remains preserved and p19 needs the finish carried forward separately.
