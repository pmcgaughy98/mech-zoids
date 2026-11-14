# Falcon capped-ink trial (sprite factory lane, 2026-11-04)

Preston: "Build all five". Still-only trial: the approved `../views` were never written.
- Rule: the one Preston kept for the hippo (`hippo_l/take-b/remaster-pilot/RUN.md`).
- Script: `docs/art/moba/capped_ink_trial.py`. Board: `board.png`. Numbers: `metrics.json`.
- Overview of all five: `docs/art/moba/CAPPED_INK_BOARD_2026-11-04.png`.

| View | Before | Capped | Pixels added | Full rule, for comparison |
|---|---|---|---|---|
| s | 5.8% | not gated | 0 | not gated |
| se | 4.2% | not gated | 0 | not gated |
| e | 4.5% | not gated | 0 | not gated |
| ne | 2.7% | 4.2% | 32 of 190 candidates | 11.9%, +223 px |
| n | 3.3% | not gated | 0 | not gated |

- Target (the lower of se and e): 4.2%.
- Added pixels with no inked neighbour: 0.
- `views_capped_trial/` holds the trial stills; `views_capped_trial_selout/` shows them as the game would.
- Neither folder is packer-ready. `../views` stays as drawn until Preston rules.
- The by-eye review is in `docs/art/moba/STILLS_STOCKTAKE_2026-11-04.md`, "Capped ink, five more".

## Ruling (Preston, 2026-11-04): "Keep all five"
- The capped ne is now the approved still in `../views/`. His originals are in `../views_pre_ink/`; copy them back to undo.
- `ne.png`: his original sha1 4f9071891310, installed c6aedd7d68b8 (byte-identical to `views_capped_trial/ne.png`), +32 px.
- Checked before install: the trial's other views match the approved folder pixel for pixel, and each installed view differs from his original by exactly the counted ink pixels.
- The engine mirrors ne into the nw slot, so the game shows that ink there too. Packed sheets need a repack by the animation lane to pick this up.
