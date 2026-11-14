# Hippo capped-ink trial (sprite factory lane, 2026-11-04)

Preston: "Try the hippo". Still-only work: the approved `../views` were never written.
Script: `capped_ink.py`. Board: `board.png`. Numbers: `metrics.json`.

**Ruling (Preston, 2026-11-04): "Keep capped ink".** The capped ne and n are now the approved views in `../views`.
His originals are kept in `../views_pre_ink/`. See Files.

## Why capped
The ink measure (`../../../STILLS_STOCKTAKE_2026-11-04.md`, "Ink measure") showed that the rhino walk's contour rule
overshoots on every machine: wherever it fires, a view lands at 1.5 to 2.8 times its target. On the gorilla, Preston
chose sel-out only over that look.

## The rule
- **Candidates:** the same as the contour rule in `rhino_l/take-a/anim/detail_ink.py`. That means an interior pixel
  that is already near-black (luma under 0.3) next to a clearly brighter one.
- **Gate:** only views under 0.75 times the target. The target is the lower of se and e: 6.4%.
- **Order:** strongest contrast first, with a bonus for touching existing ink, so new ink extends lines.
- **Stop:** when the view reaches the target.
- **Ink colour:** the hippo's own darkest (`detail_ink.darkest`). The palette is unchanged.

## Result
| View | Before | Capped | Pixels added | Full rule, for comparison |
|---|---|---|---|---|
| s | 6.6% | not gated | 0 | not gated |
| se | 6.5% | sets the target | 0 | not gated |
| e | 6.4% | sets the target | 0 | not gated |
| ne | 4.3% | 6.4% | 110 of 353 candidates | 10.8%, +410 px |
| n | 3.6% | 6.4% | 113 of 275 candidates | 10.3%, +303 px |

- No added pixel stands alone: 0 have no inked neighbour. The gorilla's ne had broken single pixels; this doesn't.

## What it looks like (Claude, by eye on the 4x board, rows 1 to 5)
- **ne:** the new ink goes to the seams around the head and neck, the leg joints and the feet.
- **n:** it rings the two rear hip discs and the tops of the feet, and adds two short lines at the hull's upper
  corners.
- **The big back plates get almost nothing.** Their seams are mid-purple, not near-black, so the rule can't pick them.
- **Effect:** the legs separate from the body a little more. It is subtle at 4x and slight at game size. The back
  plates still read flat.
- **Not checked:** I did not zoom in on the game-size row (row 6).

## Files
- `views_capped_trial/`: s, se and e equal `../views`. ne and n carry the capped ink.
- `views_capped_trial_selout/`: the same with sel-out, as the game shows them.
- `../views/ne.png` and `../views/n.png` are now byte-identical to `views_capped_trial/`. s, se, e and the drawn
  west views are unchanged. The engine mirrors ne into the nw slot, so the game shows the ink there too.
- `../views_pre_ink/`: his original ne and n. Copy them back to undo.
