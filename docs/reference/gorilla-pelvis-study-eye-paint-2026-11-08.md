# Gorilla pelvis rollback and painted eyes

User correction: the buttock/pelvis proportions were already correct. The problem is stretching and one-sided lean in animation. Preserve the approved shape. Eyes must be painted solid green on the existing surface, with no pupils or added eye pieces; remove bright brow markings.

Current review candidate: `art/model_catalog/workspaces/gorilla_restored_pelvis_painted_eyes_v12.blend` and `.glb`, clip `Gorilla_CombatLoco_v12`. Source is v9, not the rejected v10 reshaping pass. The isolated industry review scene now loads v12. Production assets/controllers were not promoted.

## Rollback

Discarded v10 mirroring, central guard shortening, separated pelvis shell, and added eye lens/socket geometry. The experimental v11 reweighting trial is also not promoted. v12 retains every original non-brow face position, UV, and skin influence exactly, including all pelvis geometry and weights. Skeleton is unchanged. Blender validation compared per-face corner positions, UVs, and named skin weights against v9; all mesh objects passed after excluding the removed brow inserts. Evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v12/validation.json`.

## Study findings — not a completed pelvis repair

Measured all 73 authored poses. The central rear guard on `Gorilla_Body_Shell` is mixed between Chest, Hips, and both independent thighs. Across the sampled central region, summed influences were RightUpLeg 297.25, LeftUpLeg 184.70, Hips 292.93, Chest 168.94. These are sums over 944 selected vertices, not normalized percentages for a single vertex. There are also small stray lower-leg/foot influences.

Central-region mesh edges shrink to 0.091 times and stretch to 9.715 times their rest lengths. The upper side fragments still in the body mesh reach 4.015 times. These explain why the rear guard distorts and drags asymmetrically even though the original rest proportions are acceptable. Independently rigid thigh shells stay within roughly 0.0041% of their resting edge lengths in this regional audit.

Evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v11/pelvis-diagnosis.json`; reproducible script `study_pelvis_v11.py` in the same scratch root. Before/rest and cycle views are in scratch `v10/before-*.png` and show the source v9, not the rejected correction.

Next repair must identify the complete native armor plate boundaries and attach them consistently to their intended joints. Avoid broad coordinate cuts across cheek plates, re-sculpting, mirroring, shortening, or locking natural whole-body sway. A box-based reweight trial stabilized the central guard but exposed boundary fragments; it was rejected rather than promoted. Review every cycle phase and sharp turns before accepting a binding repair. The active v12 deliberately retains the original pelvis motion while this is studied.

## Eyes

Removed 24 faces belonging to the previous `eye_glow` brow inserts. Painted two narrow green eye regions directly into a copy of the existing 4096px base-color atlas; cleaned old lime flecks around those regions. No new meshes, pupils, decals, lenses, or socket overlays. The modified atlas is packed in the Blender source and embedded in GLB. Front and quarter renders were inspected after reopening the saved source, including checking that the packed image really contains the paint.

Front preview: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v12/eyes-painted-front.png`; quarter preview in the same directory. Generation script: `paint_eyes_v12.py`.

## Runtime validation and limits

Godot 4.7.2 headless industry-scene check loaded `Gorilla_CombatLoco_v12` at 3.5m/s. Log: scratch `industry-painted-eyes-v12/import-check.log`. The headless run also reports a system certificate-store error and exit-time object/resource leaks; it is not a clean runtime-log claim. No new gameplay recording was made for this eye-only rollback. Front/quarter visual verification is from Blender. Pelvis deformation is still unresolved; no artistic approval is implied for v12 eye paint.
