# Wolf capped-ink trial (sprite factory lane, 2026-11-04)

Preston: "Build all five". Still-only trial: the approved `../fixed` were never written.
- Rule: the one Preston kept for the hippo (`hippo_l/take-b/remaster-pilot/RUN.md`).
- Script: `docs/art/moba/capped_ink_trial.py`. Board: `board.png`. Numbers: `metrics.json`.
- Overview of all five: `docs/art/moba/CAPPED_INK_BOARD_2026-11-04.png`.

| View | Before | Capped | Pixels added | Full rule, for comparison |
|---|---|---|---|---|
| s | 8.9% | not gated | 0 | not gated |
| se | 7.9% | not gated | 0 | not gated |
| e | 5.6% | not gated | 0 | not gated |
| ne | 6.3% | not gated | 0 | not gated |
| n | 2.6% | 5.6% | 43 of 139 candidates | 12.2%, +161 px |

- Target (the lower of se and e): 5.6%.
- Added pixels with no inked neighbour: 0.
- `views_capped_trial/` holds the trial stills; `views_capped_trial_selout/` shows them as the game would.
- Neither folder is packer-ready. `../fixed` stays as drawn until Preston rules.
- The by-eye review is in `docs/art/moba/STILLS_STOCKTAKE_2026-11-04.md`, "Capped ink, five more".

## Ruling (Preston, 2026-11-04): "Keep all five"
- The capped n is now the approved still in `../fixed/`. His originals are in `../fixed_pre_ink/`; copy them back to undo.
- `n.png`: his original sha1 a51d001a8fbe, installed 59c83f00cbc3 (byte-identical to `views_capped_trial/n.png`), +43 px.
- Checked before install: the trial's other views match the approved folder pixel for pixel, and each installed view differs from his original by exactly the counted ink pixels.
- `fixed/` is this machine's approved folder (ROSTER). `../views/` is the take before the hand fix and was not changed.
- The engine mirrors ne into the nw slot, so the game shows that ink there too. Packed sheets need a repack by the animation lane to pick this up.
