# Kangaroo (kangaroo_m/take-a) at 35 degrees, take 2: lane report (fleet redraw lane, 2026-11-05)

**Preston's go:** "Yes, second image", then "Yes, run it" and "Run it now" (2026-11-05), with C: almost full.
**Result:** one Codex image, **57,229 tokens**. Kangaroo total 135,257 (two images). Fleet total now **450,532** (of 0.9M to 1.5M).
**Verdict by eye: PARTIAL.** Better than take 1, not clean. Codex's own report says "partial miss".
- Fixed: ne shows the back of the head and both ears, muzzle pointing away, no eye (0 eye px in ne and n).
- Fixed: se, ne and n now read from above: lit tops on the shoulders, thighs and tail; se's far foot is higher (132 against 140).
- Still short: e is close to level (77 tall against the guide's 83, angle fit 11 degrees, take 1 was 12).
- Miss: the front (s) eyes are 1 + 1 px (approved 2 + 2, take 1 was 2 + 1).
- Light speckle on the big orange areas of ne and n (lone 0.10, just under the 0.11 despeckle trigger, so no pass ran).

- Board: `board_cam35.png` (approved, take 1, take 2, and a game-size row). Checks: `verify.txt`, Codex's `REPORT.txt`,
  `heights.txt`, `shape.txt`, `visual-audit.txt`. Script: `cam35_board.py`.
- Views: `views/` here (s, se, e, ne, n). `../../fixed/` and `../../views_cam35/` (take 1) were not touched.

## What changed from take 1
- The prompt named take 1's failures and asked for the view "from a high ledge": far foot and tail end higher on the page.
- The angle guide was attached second, with its colour key (pale = tops, green = fronts, grey = sides).
- The rear views: the head seen from behind, no eye pixel. This worked.

## Numbers (take 2 against approved)
| view | W x H | W ratio | H against guide | top row | angle fit (take 1) | eyes |
|---|---|---|---|---|---|---|
| s | 54x73 | 0.98 | 73 / 73 | 68 | 1 deg (5) | **1 + 1 (miss)** |
| se | 62x77 | 0.97 | 77 / 80 | 64 | 33 deg (24) | 6 + 1 |
| e | 70x77 | 1.01 | 77 / 83 | 64 | 11 deg (12) | 4 |
| ne | 66x82 | 1.02 | 82 / 89 | 59 | 11 deg (8) | 0 (pass) |
| n | 50x84 | 1.02 | 84 / 90 | 57 | 12 deg (8) | 0 |

- Widths 0.97 to 1.02. Side over front 1.30 (approved 1.25, take 1 1.25).
- Palette PASS (13 fixed colours, 0 off-palette). Accent matches the approved share in all five. No third arm or fist.
- Heights s 73, se 77, e 77, ne 82, n 84: steps of 5 px at most, so a turn test would likely find no pop.
- view_check front/back 0.64 (below 0.80, take 1 0.69). sheet_judge: all eight OK.
- The angle fit is the fleet's shape-aware measure. It reads low for upright bodies (the kangaroo's ears and tail),
  so it is a comparison with take 1, not a gate.

## The eye checklist
- Top shows in every view: **yes in s, se, ne, n; weakly in e.**
- Far feet higher: **yes** in se (132); e and ne far feet are hidden behind the near leg and tail.
- Same machine, no new parts: **yes.** Some drift: rounder fists and thighs, softer back plates.
- Plates hard, seams at the approved share: **yes**, with light speckle on ne and n.
- Eyes: **miss** in s (too small); **pass** in se, e, ne, n.

## Options for Preston
1. **Fix with tools, then turn test (recommended, free).** Repaint the front eyes to 2 + 2 px on the eye ramp, run one
   despeckle pass on ne and n, then send the five views to the game feel lane for the turn test. e stays a little
   level; the wolf's and hippo's side views were short too and passed the turn test as "turning into depth".
2. **Third image (about 60k tokens, fleet total about 510k, inside budget).** Only for the side view and the front eyes.
   Take 2 already fixed the rear head, so a third try risks losing that.

## Free fixes (Preston: "Free fixes first", 2026-11-05, relayed by the hub)
- `fix_take2.py` reads `views/` (left as Codex made it) and writes `fixed/`. Board: `board_cam35_fixed.png`
  (approved, take 2 as Codex made it, take 2 fixed). Checks: `fix-report.txt`, `verify_fixed.txt`.
- **Front eyes:** each eye was 1 px with the dark socket pixel directly above it. That socket pixel became eye glow,
  so each eye is 2 px tall in one column, the approved shape. Eyes 1 + 1 to 2 + 2. The socket keeps its upper row.
- **Despeckle:** one pass on all five (so they stay alike through a turn), the four-neighbour rule copied from
  `despeckle.py`, eye and accent colours kept. Pixels changed: s 158, se 166, e 136, ne 161, n 92. Lone-pixel share:
  s 0.091 to 0.029, se 0.092 to 0.028, e 0.079 to 0.022, ne 0.079 to 0.020, n 0.050 to 0.018.
- Unchanged by the fixes: every size, top row and feet row, palette (0 off-palette), accent 7.7 / 7.5 / 6.0 / 5.8%
  (s 7.8 to 7.7 from the two socket pixels).
- By eye: the backs of ne and n are now flat bands; the front eyes read at game size.
- **Still short after the fixes:** e is still close to level (77 against the guide's 83). That needs a redraw, not a
  tool fix. The turn test decides whether it matters.

## Turn test (game feel lane, 2026-11-05): PASS
- e reads as the body turning into depth, not a pop. The 8 swaps in a full turn change the picture by about the same
  amount (mean pixel difference 14.8 to 16.5; se to e 15.4, e to ne 15.3). The feet row holds at every swap.
- Test sizes: radius 0.45 m (long side, as for the wolf), look 0.8 m, bar 1.71 m. The tilted bar needs 1.70 m from the
  player's spot outward; the HUD's M bar (2.07 m) clears it. At the wall spot it sits on the art (-20.6 px), the same
  wall-spot issue as the other machines.
- No soft spots. The lane first said "e shows no eye" from a downscaled strip; at full size every e frame shows the eye
  (9 glow px tilted, 8 upright), matching `fixed/e.png` (4 px, as the approved e). The lane corrected it.
- Files in `docs/art/moba/match/cam_angle_test/`: `kangaroo35_board_2026-11-05.png`, `kangaroo35_turn_2026-11-05.mp4`
  (240 frames), `kangaroo35_swaps_2026-11-05.png`. Notes: `docs/art/moba/match/MATCH_NOTES.md`.

## Accepted
- Preston: "Yes, accept it" (2026-11-05). The views to install are `fixed/` (s, se, e, ne, n), in 160 cells with the feet on row 140.

## Not done
- Nothing installed (install is outside this lane). Not committed.
