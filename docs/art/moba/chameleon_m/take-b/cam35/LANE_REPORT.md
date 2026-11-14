# Chameleon take B at 35 degrees: lane report (Chameleon session, 2026-11-06)

**Run:** one Codex image, **63,803 tokens** (cap 80k), 08:15 to 08:25, on Preston's "Yes, queue it" and the hub's slot.
Fleet total by the pangolin's count: 569,068 + 63,803 = 632,871. The hub keeps the true total.
Board: `board_cam35.png`. Views: `../views_cam35/` (s, se, e, ne, n on a 160 canvas, feet row 140). `views/` is untouched.

## Verdict by eye: near pass. Four views pass; the side view is a soft pass and the lenses come back small.
| view | new W x H | approved | target | by eye |
|---|---|---|---|---|
| s | 48x78 | 49x65 | 49x81 | Pass. The back runs up the page behind the head, both lenses show, the gold jaw is clear, not overhead. The coil peeks at the top centre, not to one side. |
| se | 63x76 | 65x62 | 65x76 | Pass. Lit back and head top, near lens, far lens hidden, the coil past the body. As tall as ne. |
| e | 85x51 | 84x59 | 84x62 | **Soft pass.** Unlike the pangolin, the back shows as a lit band (median 9 rows, `side.txt`), and the head and turret tops are lit. But it came back 14% shorter than approved: the legs are shorter, so the machine looks crouched. Only two clamp feet read clearly, and the far feet aren't measurably higher. |
| ne | 68x76 | 65x62 | 65x78 | Pass. The coil near the viewer, the back running up to the head, no lens. |
| n | 47x79 | 47x63 | 47x79 | Pass. The back runs away up the page and the tail comes down the middle, no lens. |

- **Turn steps** (neighbour heights s 78, se 76, e 51, ne 76, n 79): se to e 25 px, e to ne 25 px. The lobster's 25 and
  26 px, the hippo's 28 and the wolf's 33 all passed the game feel turn test. The turn test is the gate.
- **Lenses come back small** (the fleet's known pattern): s 28 + 26 px (approved 40 + 39), se 38 (53), e 29 (43).
  None in ne or n. The free fix is the gorilla lane's glow repaint (`ape_l/take-a/cam35/fix_se_visor.py`), which needs
  Preston's word per machine.
- **Pass:**
  - Palette: all 16 fixed colours, none added.
  - Accent within 0.3 points of approved in all five.
  - No border contact; feet on row 140 in all five.
  - Widths 0.97 to 1.05.
  - Raw e/s 1.77 against the reference's 1.71, so the side view did not shrink.
- **Lit tops doubled:** the turquoise-highlight and steel-light share rose from 10 to 14% to 20 to 22% in every view.
- **Codex's own flags:** view_check lone 0.07, so no despeckle was needed. sheet_judge flagged only e and w heights
  (information).

## Lens fix (Preston: "Lens fix, then turn test", 2026-11-06). Free.
- **Script:** `fix_lenses.py`. It paints each lens back from the approved view of the same direction.
  - The approved pattern is shrunk top to bottom by cos 35 and placed where Codex drew the lens, cores aligned.
  - Old lens pixels it doesn't cover take their neighbour's colour; a stray pixel or two is cleared.
- **Output:** `fixed/` (all five views; ne and n unchanged). `../views_cam35/` stays as Codex delivered it.
- **Lens sizes:** s 26 and 28 became 30 and 33; se 37 became 40; e 29 became 35. All are now above the miss lines
  (28, 37, 30), close to the expected 32, 42 and 34. The pale glint is back in all three.
- **Pass:** the outline is unchanged in all five, palette 0 off, accent 5.9 to 8.1%, no other pixels touched.
- **Before and after:** `lens_fix_board.png`.
- **Turn test:** asked of the game feel lane on `fixed/`.

## Turn test on `fixed/` (game feel lane, 2026-11-06)
- **Run:** windowed at 30 fps, exit 0, no script errors.
  - The test now has chameleon rows: approved take-b as the upright set, canvas 160, feet edge 141, size M.
  - The bar is at 1.71 m. The body radius of 0.6 m is their guess until a kit exists.
- **Feet** sit on row 140 in all five views of both sets. Heights: s 78, se 76, e 51, ne 76, n 79. The steps are 25 px
  each way around e, the same as the lobster's, which passed.
- **HP bar at 1.71 m:** the tilted art needs 1.70 m at the game camera, so it clears, but only just. Over the drone's
  whole range it needs 2.25 m.
  - Turn clips: the smallest gap is 55.3 px on the floor and at the tower.
  - At the wall spot the gap is -11.4 px, which every machine shows there (the rhino was -14 to -20).
- **View swaps:** not measurable by frame difference (the clip changes a median of 29,707 px a frame).
- **By eye** (`turn_contact.png`, every 8th frame of the open-floor tilted clip): the turn doesn't break, and every
  view reads as the same machine from above. But at e and w the chameleon visibly ducks: it looks lower and smaller
  than se and ne on either side. It's the 14% short side view.
- Files: `D:\dev\_scratch\game_feel\chameleon35\` (their board, the 2x2 clip, log) and the MATCH_NOTES entry.

## Accepted (Preston, 2026-11-06: "Accept them")
**`fixed/` is the chameleon's final 35-degree set** (`fixed/APPROVED.txt`). Install it in 160 cells, feet row 140.
The short side view is known and accepted. Chameleon total: one image, 63,803 tokens.

## Options for Preston (as offered after the run)
1. **Free fixes first (recommended):** repaint the lens glow to approved size in s, se and e. Then ask the game feel lane
   for the turn test.
2. **Accept as it is**, then the turn test.
3. **Second image, side view only** (paid, about 55k to 65k, needs his yes). Not recommended yet: the pangolin's
   side-only retry missed the same way, and this side view already shows its back. Only worth it if the turn test pops
   at e or he wants the legs taller.
