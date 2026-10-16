# Wolf v52 finish, installed

Task 1 wolf is finished and installed after Preston requested the next machine. All six machines now have preserved finish records, but four earlier live builds have since been replaced. Current roster status is in CODEX_FINISH_STATUS_2026-10-13.md; their finishes need carrying forward before the battle review. Task 2 has not started.

## Must match, checked on all eight facings

- Exact original 214x108 canvases, every alpha byte, transparent pixel and foot anchor (107,105).
- Both ground rows and every cyan eye/throat-emitter pixel unchanged exactly, with no new cyan or halo.
- Four articulated legs, the native planted foreleg, three claw hooks per paw, red fangs/forearm blades, short angular muzzle, charcoal armor and segmented spiked tail remain in their v52 positions.
- Two ears and two parallel antennas behind the head retain their actual source placement. Occlusion is retained; no third central mast is added.
- Right-back rail gun, two haunch 2x2 pods, throat emitter, paired exhausts, vents and cables retain native placement and visible apertures.
- Deep interior grey/ red mouths, hubs and seams are protected. Seven isolated rank-one grey checks in the east plate are separately identified by strict same-part/four-neighbor guards; real lines and black apertures are excluded.
- Final colors use only the 21 approved palette swatches. Body stays charcoal, accents stay blood-red.

## Finish

Reduced fine shading variations inside existing grey/red parts and removed unambiguous interior specks. Restrained material-colored edges replace some darkest exterior pixels with lit charcoal tops and darker sides/undersides. Selected rail/pod housings and existing joints receive small grey highlights; deep apertures stay dark. Grey highlights explicitly avoid stepping into the approved extra-top swatch when it is slightly darker than the base top.

The finish changes 74-323 pixels per view, 1,640 total. It is deliberately restrained on the black body. Small mechanical detail and some charcoal checker texture remain where smoothing could merge real structure.

Native v52 crops matched the installed input exactly after placement. Render dimensions agreed; hashed snapshots of the 16 render/part-ID files are preserved under source-renders so another rebuild cannot silently replace these guides.

## Artifacts and checks

- Untouched full installed folder: docs/art/2d/wolf_m/v52_pre_codex/.
- Final copies, helpers, notes, audit, input hashes, measurements and logs: docs/art/2d/wolf_m/v52_codex/.
- Eight-view nearest-neighbor 4x comparison: v52_codex/before-after-eight-4x.png. Rows alternate before and after; individual pairs also saved.
- Actual Godot camera evidence: v52_codex/view-lab-eight-cameras.png and lab_000.png through lab_315.png.
- Measurements: v52_codex/statistics.md and audit.json.

Guarded installation checked every live PNG and metadata file against the untouched backup before replacing them. Final live PNGs equal their preserved finished copies. views.json retains size, anchor, map and mirror state; palette lists all approved swatches and source points to the finished folder. The alignment importer was not rerun.

Godot import exits 0. view_art_check.gd passes for six machines with wolf feet at (107,105). views_check.gd passes. The actual view lab walkthrough passes through e, se, s, sw, w, nw, n, ne, resolving installed wolf art. All eight before/after pairs and the final runtime camera grid were inspected.

The shipping lab excludes wolf. The review helper temporarily adds the actual ViewSprite actor, hides the other machines and shifts the review stage down. Its HUD is moved to the top of the viewport so it does not cover the ears/antennas. Shipping scene and scripts remain unchanged. This isolated review is not approval of battle composition.

Godot reports inability to read the system certificate store; import also reports inability to save external editor settings. These environment diagnostics did not prevent import, rendering or the checks passing.

## Measurement limits

Dark-edge share falls in every facing, from 56.9-68.4% to 48.5-56.5%. This remains substantially above the historical 20% reference ceiling. The charcoal design and tiny dark mechanical parts need an explicit battle-contrast review; this pass does not claim target compliance or equivalence to the reference sprites.

Upper-light scores are 61.6-100.7. Clusters are 3.85-5.42 pixels, generally increasing slightly, with ne decreasing. Stray share is 9.3-16.4%, improving some views and remaining similar or slightly higher in others. Detailed per-view values are recorded. Runtime previews expose all facings, but the front/back dark body still reads more weakly than the steel legs and red hardware.

Technique reused from docs/reference/sprite-rules-legacy-2026-10-12.md: material ramps, selective outlines and upper-left light. Project wolf_m.png informs hardware readability only; Preston's no-glow correction takes priority. Native parts supply geometry/placement, Pillow/NumPy provide audited color changes, and Godot supplies runtime evidence. No copied game art, paid generation, protected model/pipeline/script edits or commits.

## Carry forward

Preserve v52_codex as the review record. Future rebuilds need the finish transferred onto new silhouettes or affected views flagged; do not install older PNGs over newer geometry.

At handoff, gorilla v66_codex and wolf v52_codex match live art in all eight views. Hippo p24, kangaroo p45, pangolin p20 and shoebill p67 differ from their earlier finished records in all eight views. Those four are explicitly flagged for finish transfer; their records remain intact. Refresh them before calling Task 1 current across the roster, then review the actual battle slots.
