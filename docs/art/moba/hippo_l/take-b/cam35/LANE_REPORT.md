# Hippo (hippo_l/take-b) at 35 degrees: lane report (fleet redraw lane, 2026-11-05)

**Preston's go:** "Go, start the hippo" (2026-11-05), after the wolf was accepted.
**Result:** one Codex image, **71,498 tokens**. Fleet total now **315,275** (of 0.9M to 1.5M).
**ACCEPTED (2026-11-05):** Preston said "Turn test, then accept", and the turn test passed. No fixes.
**Verdict by eye: near pass, the same pattern as the wolf.** All five read from above, the eyes are full size and
nothing is extra. The side view is again the weak one: short and low. The turn test is the final word.

- Board: `board_cam35.png`. Checks: `verify.txt`, Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- Views: `../views_cam35/` (s, se, e, ne, n). `../views/` was not touched.

## What was sent
- The wolf's brief with the hippo's parts, palette (14 colours) and numbers. The four take-2 changes and the part-count
  line are kept (four legs, two ears, two tusks, one steel jaw, one tail plate).
- Heights from the hippo's own hull guide at 35 degrees: s 77x90, se 113x89, e 123x82, ne 106x98, n 77x98. Unlike the
  wolf, every view grows by about the same amount (19 to 22 px), so the prompt says so.
- **New from the wolf turn test:** se is asked to be "NEARLY AS TALL as the rear three-quarter view, never flatter".
- Canvas 192, feet row 160, kept. Finishing scripts from the wolf's cam35 (same canvas).

## Numbers (new against approved)
| view | W x H | W ratio | H ratio | H/W new / guide | top row | eyes |
|---|---|---|---|---|---|---|
| s | 78x90 | 1.01 | 1.29 | 1.15 / 1.17 | 71 | 18 + 18 |
| se | 101x88 | 0.89 | 1.26 | 0.87 / 0.79 | 73 | 21 + far 4 |
| e | 110x71 | 0.89 | 1.15 | 0.65 / 0.67 | 90 | 16 |
| ne | 98x99 | 0.93 | 1.29 | 1.01 / 0.93 | 62 | 0 |
| n | 79x94 | 1.08 | 1.24 | 1.19 / 1.27 | 67 | 0 |

- Scale anchor: s 1.013, n 1.082, e 0.894, mean 1.00.
- Eyes PASS (minimums s 14, se 13, e 15; e is 16). No eye pixel in ne or n.
- Palette PASS (14 fixed colours). Accent matches the approved share in all five.
- view_check lone 0.10, no despeckle. sheet_judge: height flags only.
- Lit tops: the lightest purple share rose from 4 to 14% to 18 to 27%, so the hippo reads a lighter purple.
- Height per view around the turn: s 90, se 88, e 71, ne 99, n 94. se against ne: 88 against 99, much closer than the
  wolf (72 against 91). The big step is now e to ne, **28 px**, because e came back low (71 against the guide's 82).

## The eye checklist
- Top shows in every view: **yes**, the back deck as a broad lit surface everywhere, and as a band in e.
- Far feet higher in e, se, ne: **yes**, though weakest in e.
- Five views agree: **mostly.** s, se, ne and n agree; e is flatter and short (110 long against 123).
- Same machine, no new parts: **yes.** The ears in s are hard to see on the head top.
- Plates hard, seams at the approved share: **yes.**
- Eyes full size, none in the rear: **yes.**

## A pattern across two machines
Codex draws the side view about 10% short against the front and back: wolf e 0.91, hippo e 0.89, while s and n come
back at 1.01 to 1.08. The mean anchor then splits the error. For the rest of the fleet, one option is to state the
side view's length as a share of its cell in the prompt (the longest view, about 75% of the cell), or to anchor on e
alone. Not changed without a decision.

## Options for Preston
1. **Turn test first (free).** If no pop, accept as is. No pixel fix is needed.
2. **Second image (about 70k tokens, fleet total about 385k, inside budget):** ask for a longer and taller side view.
   Only on his yes.

## Not done
- No pixel fixes. No frames redrawn. Nothing installed in the game. Not committed.

## Ruling (Preston, 2026-11-05): "Turn test, then accept"
- Accepted on condition that the game feel turn test passes. No pixel fix is needed.
- **Turn test (game feel lane, 2026-11-05): PASSES, no pop. The hippo is ACCEPTED.** The feet stay on the shadow at all
  eight swaps, and the head and rump stay on their sides. The e/ne step (71 to 99, 28 px) reads as the body turning into depth,
  the same as the wolf's 33 px step, which passed. se at 88 holds well, so the wolf lesson worked.
- **Soft spot, not blocking:** e is 89% of the approved length and 71 tall against the guide's 82, so the hippo looks a
  little smaller side-on. e at its guide size would cut the e/ne step to about 17 px.
- **Bar:** the HUD's tilted bar (2.3 m for L) clears the art; 2.15 m is needed. Install in 192 cells, feet row 160.
- Game feel files: `match/cam_angle_test/hippo35_board_2026-11-05.png`, `hippo35_swaps_2026-11-05.png`,
  `hippo35_turn_2026-11-05.mp4`.
