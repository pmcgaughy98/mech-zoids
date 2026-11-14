# Fennec capped-ink trial (sprite factory lane, 2026-11-04)

Preston: "Build all five". Still-only trial: the approved `../views` were never written.
- Rule: the one Preston kept for the hippo (`hippo_l/take-b/remaster-pilot/RUN.md`).
- Script: `docs/art/moba/capped_ink_trial.py`. Board: `board.png`. Numbers: `metrics.json`.
- Overview of all five: `docs/art/moba/CAPPED_INK_BOARD_2026-11-04.png`.

| View | Before | Capped | Pixels added | Full rule, for comparison |
|---|---|---|---|---|
| s | 5.6% | not gated | 0 | not gated |
| se | 6.7% | not gated | 0 | not gated |
| e | 6.7% | not gated | 0 | not gated |
| ne | 4.0% | 6.7% | 50 of 250 candidates | 17.3%, +302 px |
| n | 3.9% | 6.7% | 49 of 180 candidates | 14.0%, +243 px |

- Target (the lower of se and e): 6.7%.
- Added pixels with no inked neighbour: 0.
- `views_capped_trial/` holds the trial stills; `views_capped_trial_selout/` shows them as the game would.
- Neither folder is packer-ready. `../views` stays as drawn until Preston rules.
- The by-eye review is in `docs/art/moba/STILLS_STOCKTAKE_2026-11-04.md`, "Capped ink, five more".

## Ruling (Preston, 2026-11-04): "Keep all five"
- The capped ne and n are now the approved stills in `../views/`. His originals are in `../views_pre_ink/`; copy them back to undo.
- `ne.png`: his original sha1 578be269b8ab, installed b6d02fd54163 (byte-identical to `views_capped_trial/ne.png`), +50 px.
- `n.png`: his original sha1 7ad7f16f94e8, installed 28bbbb1a7914 (byte-identical to `views_capped_trial/n.png`), +49 px.
- Checked before install: the trial's other views match the approved folder pixel for pixel, and each installed view differs from his original by exactly the counted ink pixels.
- The engine mirrors ne into the nw slot, so the game shows that ink there too. Packed sheets need a repack by the animation lane to pick this up.
