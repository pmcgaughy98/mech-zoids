# Gorilla v77 finish

Finished the installed v77 battle set first, then its eight views, on `cloud/model-pass-2026-10-16`. Kept the approved longitudinal spine rack, right back cannon, five-knuckle fists, extended rear and thicker hind legs.

## Changes

- Hand only: drew a dark bore within the visible cannon cap, framed by a light upper steel lip and darker lower rim. The model cap is solid; a pixel-level opening makes it read hollow. Hidden/back-facing caps were left alone.
- Repeatable: separated the ankle wheels into a grey outer rim, lighter inner ring, dark hub and one central highlight. Confined the treatment to the existing layered wheel pieces, never adding a hidden wheel or touching surrounding green armor.

51 battle frames: 5,455 RGB pixels changed. Eight views: 732. Total: 6,187 pixels across 59 named PNGs; 620 bore/lip pixels and 5,567 ankle-wheel pixels. Only existing palette swatches used. Exact alpha, canvas, feet, ground lines, clip timings and silhouettes preserved.

## Inputs and saved copies

All 59 raw live PNGs matched their installed SHA-1 records before work. Replayed every native color/piece/normal render through the current detail pixelizer and verified exact equality to the installed crop before accepting its part map. `v77_codex/map-audit.json` records placement and source hashes. No generator or model edits.

- Raw backups: `docs/art/2d/ape_l/anim_v77_pre_codex/`, `v77_pre_codex/`.
- Finished copies: `docs/art/2d/ape_l/anim_v77_codex/`, `v77_codex/`.
- Comparisons: `v77_codex/before-after-4x.png`, `hardware-detail-12x.png`, and each clip's `*-before-after-4x.png` and looping `*-before-after.gif` under `anim_v77_codex/`.
- Review: `http://127.0.0.1:8882/v77_codex/review.html`.
- Actual battle recording: `v77_codex/punch-combat.mp4`.

Viewed all seven clip comparisons for temporal consistency. Captured all 51 installed frames before and after through both actual battle slots; inspected the actual view lab at all eight angles. The combat recording drives the real attack queue and observes all nine punch frames.

## Checks

PASS: import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check, vfx_check.

The sandbox blocked the foundation check's temporary `user://` save. Foundation, systems and start-chain were run from exact source copies with only their disposable save-path literals redirected into this job folder. An inverse replacement verifies their logic is unchanged; original test source hashes are recorded. These three workspace-path runs passed. No production script changed. The first VFX run hit a 180-second timeout; the complete original check passed at fixed 60 FPS, 288 attacks across all three window sizes. Results and logs are in `v77_codex/checks.json` and `save-check-results.json`.

`v77_codex/final-audit.json`: all 59 live files equal the finished copies; exact alpha/canvas preserved; edits restricted to the verified cannon-cap and layered ankle-wheel IDs. All other pre-existing files under `art/machines/` remain byte-identical, including metadata, installed hash files, other machines and model assets. Kept the allowed punch/3 top overhang. No commit.

## Source issue for Claude

The raw v77 death frames already contain a loose grey disc below the falling rear leg, visible in the before/after comparisons. It remains at exactly the source position; do not hide or move it with a silhouette edit. Relevant outer ankle wheel pieces are body-bound in the native part list (119/121, 216/218), while their inner layers are foot-bound. Please check those weights in the source before the next patch. This finish does not repair model binding.

Gorilla lock removed at handover. Next machine is wolf v94; gorilla review remains the approval point from the inherited Task 1 method.
