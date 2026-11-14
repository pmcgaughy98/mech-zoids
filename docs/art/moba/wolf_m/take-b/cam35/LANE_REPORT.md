# Wolf (wolf_m/take-b) at 35 degrees: lane report (fleet redraw lane, 2026-11-04)

**Preston's go:** "Go, start the wolf" (2026-11-04), after gorilla take 2 was accepted.
**Result:** one Codex image, **61,049 tokens**. Fleet total now **243,777** (of 0.9M to 1.5M).
**ACCEPTED (2026-11-04):** Preston chose "Turn test, then fix", the turn test passed, and the ne ear pixel is fixed. See "Ruling" at the end.
**Verdict by eye: near pass, not clean.** All five read from above, but the side view came back short and a little
low, the front view is steeper than the rest, and one eye pixel sits on an ear tip in ne. The turn test is the final word.

- Board: `board_cam35.png`. Checks: `verify.txt`, Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- Views: `../views_cam35/` (s, se, e, ne, n). `../fixed/` was not touched.

## What was sent
- Template: gorilla take 2 (`ape_l/take-a/cam35/take2/`), with its four changes kept: width held at the approved with
  plain per-view proportions, "FLAT TOP FACES THAT FACE UP", the one-row 35 degree guide, and the scale anchored on the
  mean of s width, n width and e length. The part-count line is kept (four legs, two ears, two fangs, two fins, one tail).
- Heights were written from the wolf's own hull guide at 35 degrees, not "every view grows":
  s 33x71, se 84x64, e 108x63, ne 78x86, n 33x96. The wolf is long and low with tall ears at the front, so the front
  views stay about the same height and the rear views grow (the head and ears are far away and rise up the page).
- Canvas 192, feet row 160, kept: the tallest guide view (n, 96) tops out at row 64, leaving 64 rows of headroom.
- Palette: the 12 colours the approved views use (no eye glint; the approved stills have none). Eye glow protected in
  the finish step, which kept the eyes this time.

## Numbers (new against approved)
| view | W x H | W ratio | H ratio | H/W new / guide | top row | eye px |
|---|---|---|---|---|---|---|
| s | 35x85 | 1.06 | 1.18 | 2.43 / 2.15 | 76 | 6 (two eyes of 3) |
| se | 85x72 | 1.02 | 1.03 | 0.85 / 0.76 | 89 | 6 |
| e | 100x58 | 0.91 | 0.88 | 0.58 / 0.58 | 103 | 4 |
| ne | 71x91 | 0.91 | 1.30 | 1.28 / 1.10 | 70 | **1 (miss)** |
| n | 36x96 | 1.03 | 1.33 | 2.67 / 2.91 | 65 | 0 |

- Scale anchor: s 1.061, n 1.029, e 0.909, mean 1.00.
- Palette PASS (12 fixed colours, nothing extra). Accent share matches approved in all five (7.4, 6.4, 4.7, 5.3, 4.8%).
- Lit tops: the lightest gunmetal share rose from 6 to 12% to 12 to 19%, so the wolf reads lighter grey than the dark
  approved stills.
- Lowest row 160 in all five, no border contact. view_check lone 0.079, no despeckle. sheet_judge: height flags only,
  which the camera change explains.
- Height per view around the turn: s 85, se 72, e 58, ne 91, n 96. The e to ne step is **33 px** (the guide predicted
  23), and it happens twice per circle (e/ne and w/nw).

## The eye checklist
- Top shows in every view: **yes.** s and n show the back as a long lit band running up the page; e shows it as a band
  with both fins; se and ne too.
- Far feet higher in e, se, ne: **yes.**
- Five views agree on how much top shows: **no, roughly.** s and se are steeper than the guide (taller), e is a little
  flatter and 9% short. Codex's own eye said the same.
- Same machine, no new parts: **yes.** Costs: the fangs are smaller; the ears in s lie back and barely read; the red
  fins in s look like two long red flaps beside the head.
- Plates hard, seams at the approved share: **yes.**
- Eyes full size: **yes** in s, se, e. **Miss in ne:** one cyan pixel on the far ear tip (row 71). Removing it is a
  one-pixel fix, not applied without Preston's word.

## Options for Preston
1. **Turn test first (free).** If the game feel lane finds no pop, accept with the one-pixel ear fix.
2. **Second image (about 60k tokens, fleet total about 305k, inside budget):** ask for the side view as long as the
   approved (110) and a little taller, and the front view less steep. Only on his yes.

## Not done
- No pixel fixes applied (ne eye pixel). No frames redrawn. Nothing installed in the game. Not committed.

## Ruling (Preston, 2026-11-04): "Turn test, then fix"
- **Turn test (game feel lane): PASSES, no pop.** The feet stay on the shadow at all eight swaps. The e/ne step (58 to 91)
  is the biggest change in the circle and shows on the swap frame, but it reads as the body turning into depth, not a jump.
  Their rigid-box estimate for ne is about 93; it came back at 91. It is the same front-to-back growth he accepted on the fennec.
- **Soft spot, not blocking:** se (72) is about 8 to 20 px short of the box estimate, which is why the step gathers at e/ne.
  For a smoother turn later, raise se; don't lower ne.
- **Bar:** the HUD's tilted bar clears the art. Install in 192 cells, feet row 160.
- **Fix applied:** `fix_ne_ear_pixel.py` set ne (119, 71) from eye glow 6ff0dc to gunmetal base 6e6e7e. Codex's original
  is kept as `ne_codex_original.png`. ne is now 0 eye pixels, still 71x91. The board and `verify.txt` are rebuilt.
- Game feel files: `match/cam_angle_test/wolf35_board_2026-11-04.png`, `wolf35_swaps_2026-11-04.png`,
  `wolf35_turn_2026-11-04.mp4`; notes in `match/MATCH_NOTES.md`, "Wolf take B at 35, turn test".
