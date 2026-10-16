# Gorilla v66 finish, ready for review

Task 1's gorilla is installed. Remaining Task 1 machines: hippo, kangaroo, pangolin, shoebill and wolf. Task 2's battle pass has not started; the task file places that after Preston reviews the gorilla. The accidentally attached wolf sheet was disregarded.

## Must match, verified on all eight views

- Original 196x100 canvases, exact alpha bytes and foot anchor (98,97). No movement, crop, scale, mirror or silhouette change.
- Cyan visor pixels are byte-for-byte unchanged, and there are no added cyan pixels elsewhere.
- Three back blocks, cap placement, green dome/brow/jaw, orange chest/fists/toes and actual joint/weapon positions remain the source v66 geometry.
- Rotary gun and 2x3 shoulder launcher retain their original visible apertures; no hardware was added in occluded views. Dark internal muzzle/hub/seam detail is retained.
- Final colors are entirely from `tools/art/palettes/ape_l.json` (27 available swatches including its teal ramp).

## Result

Softer micro-grid shading inside the existing green/orange plates; broad fist highlight areas with original curled fingers and dark mechanical divisions retained. Light-following outer edges, small upper housing/barrel highlights in all eight directions, selective pale grey highlights on existing circular joint regions, and isolated interior color specks cleaned where their ownership is unambiguous.

The cleanup uses the existing v66 part-ID renders to keep color adjustments inside actual parts. It does not invent rectangular fists or overwrite the original part silhouettes. The existing v66 sprite positions are preserved even where the view's body looks off-center relative to its feet.

The source sprites already contained colors outside the current palette JSON. Those were mapped within their own material families, including old violet ground-line shades to approved grey shades and the unsupported pale grey to the palette's pale grey. No transparent pixels or eye pixels changed. `views.json` keeps size, anchor, map and mirror state; only source and palette were updated. Importer alignment was not re-run.

## Artifacts

- Eight-view before/after contact at exact 4x: `docs/art/2d/ape_l/v66_codex/before-after-eight-4x.png`. Rows alternate before and after.
- Per-view comparisons: `<direction>-before-after-4x.png` in that same folder.
- Full original installed views folder: `docs/art/2d/ape_l/v66_pre_codex/`.
- Finished installed views and preserved final copy: `art/machines/ape_l/views/` and `docs/art/2d/ape_l/v66_codex/`.
- Input hashes and exact-alpha/eye/palette audit: `v66_codex/audit.json`.
- Actual game lab camera evidence: `v66_codex/view-lab-eight-cameras.png`, plus `lab_000.png` through `lab_315.png`.
- Reproducible review helpers live inside the artwork folder; no `.py`, `.gd` or `.json` under `tools/`, `scripts/` or `docs/art/3d/` was changed for this task.

## Per-view focus

| View | Finish focus |
|---|---|
| e | Visible forearm and side fist planes; rotary barrel top, launcher casing, shoulder rim. |
| ne | Rump/side plates and hind-leg ramps; rear-facing launcher casing and rotary barrel top. |
| n | Back/rump plates and hind legs; existing rear housings; three cap positions preserved. |
| nw | Shoulder, rump and near hind-leg planes; oblique barrel/casing edges and ear/shoulder rims. |
| w | Side torso/forearm/near fist planes; rear barrel housing, side launcher casing and shoulder disc. |
| sw | Near fist and forearm shading; rotary/casing top edges, visible shoulder/ear rim. |
| s | Both fist shells and upper arms; launcher and front rotary housing highlights; original fingers and mouths retained. |
| se | Near/far fist shells and chest/arm planes; launcher top, visible gun housing and ear/shoulder highlights. |

## Checks

- Guarded install verified every live input PNG and metadata file still equalled its backup before replacement.
- Post-install all eight live PNGs equal the finished copies, and every alpha channel equals the untouched original.
- Godot headless import: exit 0.
- `view_art_check.gd`: PASS, six machines, zero gorilla off-palette pixels, exact canvas/feet and height consistency.
- `views_check.gd`: PASS.
- Actual `scenes/view_lab.tscn` camera run: PASS, gorilla resolves to installed art through e, se, s, sw, w, nw, n, ne. Captured and inspected the before/after pairs and game camera sheets.

The existing view lab crowds the enlarged sprites together and crops some other machines at its upper edge. This pass does not change that scene layout. Its successful wiring checks should not be read as approval of battle composition; that belongs to Task 2.

## Measurement limits

Dark-edge share is about 6-15%, down from 16-25%. Color clusters remain about 5.0-6.5 pixels; measured stray share is about 6.9-10.1%. Upper-light score is 159-236; v66 was already 123-185, above the historical v31 reference band's 49-107. Some upper-edge work raises this further. Not every historical target is met, and fewer isolated pixels is not claimed across all views. Visual review is the remaining gate. The strict 27-swatch palette also supersedes the older request for 30-40 colors.

Technique references reused: `docs/reference/sprite-rules-legacy-2026-10-12.md` for ramps and selective outlines; `docs/art/reference/starters/ape_l.png` for finish feel only. No game art was copied, no paid generator used, no commits made.

## Carry forward

Keep `v66_codex` immutable as the approved/rejected review record. If the model is rebuilt, these PNGs must not be installed over the newer silhouettes. Carry the plate shading, hardware upper-edge, joint-rim and selective-outline edits to the new views, or flag them for another finish pass. The part-ID correspondence is v66-specific and checked; the helper deliberately refuses a mismatched source.

Detailed pixel-change counts and sprite_quality measurements: `docs/art/2d/ape_l/v66_codex/statistics.md`.
