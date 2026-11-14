# Lobster (lobster_l/take-g) at 35 degrees: lane report (lobster session, 2026-11-05)

**Preston's go:** "35-degree redraw", then "Yes, run it" (2026-11-05).
**Result:** one Codex image, **70,525 tokens**, under the 100k cap. It started at 20:42 and ended at 20:56.
**Verdict by eye: near pass.** It's the same lobster, seen from above, with every part kept and no tail spikes. The side view is the best view. The front views (s, se) and the back view (n) look down more steeply than the side view does, so the five views don't fully agree on the angle. The turn test is the final word.

- **Board:** `board_cam35.png`.
- **Checks:** `verify.txt`, Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- **Views:** `../views_cam35/` (s, se, e, ne, n). `../views/` was not touched.

## What was sent
- The hippo's brief, with the lobster's parts, palette (14 colours) and numbers.
- The guide was a one-row hull guide at 35 degrees. Its heights: s 89x74, se 115x63, e 124x71, ne 112x80, n 89x90.
- **New for the long-body side-view shrink:** the prompt said the side view is 1.4 times as long as the front is wide. The brief had Codex measure that before the shrink.
- The canvas stayed at 192 and the feet row at 160. The finishing scripts were the hippo's.

## Numbers (new against approved)
| view | W x H | W ratio | H ratio | H/W new / guide | top row | eyes |
|---|---|---|---|---|---|---|
| s | 83x105 | 0.93 | 1.59 | 1.27 / 0.83 | 56 | 38 + 37 |
| se | 100x95 | 0.88 | 1.51 | 0.95 / 0.55 | 66 | 59 + far 16 |
| e | 129x70 | 1.04 | 1.27 | 0.54 / 0.57 | 91 | 38 |
| ne | 107x96 | 0.96 | 1.48 | 0.90 / 0.71 | 65 | 0 |
| n | 83x106 | 1.02 | 1.61 | 1.28 / 1.01 | 55 | 0 |

- **The side-view fix worked.** e came back at 1.04 of the approved length (wolf 0.91, hippo 0.89), and its height matches the guide (70 against 71).
- **The front and back went the other way.** s, se and n came back much taller than the guide (105, 95 and 106, against 74, 63 and 90). s and se also lost width (0.93 and 0.88).
- **Heights around the turn:** s 105, se 95, e 70, ne 96, n 106. The steps are se to e 25 px and e to ne 26 px. The wolf's 33 px and the hippo's 28 px both passed.
- **Eyes PASS:** s 38 + 37 against the expected 36 + 34; se 59; e 38. None in ne or n. The se far eye is 16, against about 20 expected.
- **Palette PASS:** 14 fixed colours. The accent share matches the approved in all five (e 10.2 against 10.6).
- **Clean-up:** view_check lone went from 0.13 to 0.05 after one despeckle pass. sheet_judge flagged heights only.
- **Lit tops:** the lightest-gunmetal share rose from 9 to 18% to 16 to 26%.

## The eye checklist
- **Top shows in every view:** yes. The carapace's red plate is lit everywhere, and the tail segments show as lit bands.
- **Far feet higher in e, se and ne:** yes.
- **The five views agree:** no.
  - s, se and n look from about 55 to 65 degrees, judged by their height over width.
  - e looks from about 30 degrees.
  - In s, the tail rises as a column behind the head to the fan at the top.
- **Same machine, no new parts:** yes. Two claws, two eyes, two red-tipped antenna rods (short and laid back in s and se, which is right from above), one straight banded tail with its fan, and no spikes. The fan reads a little bulkier.
- **Plates and seams:** yes. They are hard, at the approved accent share.
- **Eyes:** yes. They are full size, with none in the rear views.

## Options for Preston
1. **Turn test, then accept (free).** If nothing pops at e, it's accepted as is.
2. **Second image (about 70k tokens, cap 100k, worst case about 175k).**
   - It would ask for less height in s, se and n: the tail drawn flatter and shorter on the page, and s and se kept at full width.
   - Only on his yes and the hub's slot.

## Not done
- No pixel fixes.
- Nothing installed in the game.
- Not committed.

## Turn test (game feel lane, 2026-11-05)
- **Result:** ran windowed at 30 fps with no script errors. Feet are on row 160 in all five views.
- **Swaps: no measured result.** The game feel lane withdrew its swap numbers (10.9 to 12.3), because they were read from composite frames. A frame difference can't single out the swaps anyway, since the walk cycle and the camera move the whole frame.
- **By eye instead (lobster session):** I made a contact sheet of the tilted-floor panel, every fourth frame of the 240-frame turn clip (`D:/dev/_scratch/lobster/turn_contact.png`).
  - The lobster stays centred on its shadow at every swap, and head and tail stay on the same side across each one.
  - No pop is visible. The side views read smaller than the front and back, as the heights say.
  - The thumbnails are about 0.4x, so this is a coarse check. The clip itself is `D:/dev/_scratch/game_feel/lobster35/clip/` (c0000 to c0239).
- **In-game board:** all five read from above and sit on their shadow, against open floor, a tower and a wall. Front and back look clearly bigger than the side view. See `D:/dev/_scratch/game_feel/lobster35/board_lobster35.png`.
- **HP bar:** the tilted art leans back 1.06 m at its tallest view. The bar needs to sit at 2.3 m at least (the test used 2.9 m to clear at every distance). Use this when installing.
- **Not checked:** the west views.

## Ruling (Preston, 2026-11-06): "Accept them"
- **ACCEPTED as drawn.** No pixel fixes.
- **Known cost:** the front and back views look bigger than the side view.
- **Install:** 192 cells, feet row 160, HP bar at least 2.3 m.
- **Approval marker:** `../views_cam35/APPROVED.txt`.
