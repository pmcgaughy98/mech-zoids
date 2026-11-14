# Gorilla cam35: lane report (fleet redraw lane, pilot, 2026-11-04)

One Codex image, **57,314 tokens** (budget 60k to 100k). Fleet total so far: 57,314.
- Board: `board_cam35.png` (approved row, cam35 row, both at 4x with sel-out for review, plus game size at 1.55 px per texel).
- Views: `../views_cam35/` (s, se, e, ne, n). Checks: `verify.txt`, plus Codex's `REPORT.txt`, `heights.txt`, `shape.txt`.
- `../views/` is byte-identical (sha256 checked before and after); no file in `../anim/` or `../remaster-pilot/` changed.

## What I changed for a limbed machine, and why
**Comparing the drone and rhino runs first.** I built a free shape-aware measure, `cam35_fleet/hull_guide.py`.
- It cuts a rough solid from a machine's approved outlines (s, e, se and ne; a "visual hull").
- It reports the camera pitch at which that solid best matches each drawn view.
- Two readings: by outline and absolute height, and by height over width (which ignores overall scale).

| run | s | se | e | ne | n | read by |
|---|---|---|---|---|---|---|
| drone cam35 | 34 | 34 | 31 | 20 | 8 | outline |
| rhino cam30 | 49 | 68 | 7 | 34 | 22 | outline |
| rhino cam35 | 46 | 70 | 14 | 34 | 17 | outline |
| gorilla cam35 | 9 | 8 | 9 | 8 | 9 | outline (scale shrank, see below) |
| gorilla cam35 | 30 | 26 | 9 | 22 | 33 | height over width |

- It agrees with the eye and the 3D lane on the rhino: s too steep (about 47, against the 3D lane's 48 to 50) and e too flat.
- The rhino did not fail to move. Its views moved by different amounts, and its cam30 and cam35 came out the same.
- The elliptic guide's targets are wrong for a limbed shape. For the gorilla it asked for heights of 98 to 105 px. The gorilla's own solid at 35 degrees is 83 to 90 px (s 83, se 89, e 89, ne 90, n 85), only 15 to 29% over the approved views.

**What I changed:**
1. **The guide.**
   - `refs/angle_guide.png` is now the gorilla's own solid, in two rows: the reference camera (6 degrees) and 35 degrees.
   - Codex sees exactly what the camera change does to each view. The front is green, the top pale and the sides grey.
2. **The prompt.**
   - "Every view, the side view included, grows by about the same amount, one fifth to one quarter".
   - Far-feet lines written for a knuckle-walker: hind feet above the fists in s, fists above the hind feet in n.
   - The visor and shields keep their size.
   - The plates paragraph keeps the gorilla's own rounded plates. "Straight cut edges", as for the drone and rhino, would have changed the machine.
3. **The measure** now runs on every machine (`verify.txt`). Information only; the eye and game feel's turn are the gate.

## Result
| view | W x H (approved) | H / approved | angle by height over width | visor px | accent (approved) |
|---|---|---|---|---|---|
| s | 86x78 (91x72) | 1.08 | 30 | 15 (expected 15) | 8.8% (10.2%) |
| se | 81x79 (89x72) | 1.10 | 26 | 8 (expected 14, floor 12) | 8.0% (8.5%) |
| e | 79x78 (79x71) | 1.10 | 9 | n/a | 8.0% (8.9%) |
| ne | 79x77 (86x70) | 1.10 | 22 | 0 | 8.5% (7.6%) |
| n | 82x77 (87x70) | 1.10 | 33 | 0 | 8.4% (8.4%) |

- **Heights:** all five grew by the same 8 to 10% (spread 0.02, the tightest of any run). That is about 0.86 to 0.94 of the shape guide.
- **Widths:** every view except e came out narrower than approved (s 86 vs 91, se 81 vs 89). The sheet is scaled so e is 79 long, so the whole machine reads about 5% smaller. That is why the outline reading says about 9 degrees everywhere.
- **Palette PASS** (15 colours). Lowest row 130 in all five, no border contact, alpha on or off. view_check lone 0.083. sheet_judge OK on all eight.

## Eye checklist (fleet HANDOFF)
- **Top shows in every view:** PASS in s, se, ne and n. The hump and generator are seen from above, and the head sits lower under the hump. e: PARTLY. The hump top and generator face show, but as a rounded dome more than a wide band.
- **Far feet higher in e, se, ne:** MISS. Not clearly higher in any of them; Codex says the far hind foot stays hidden in e.
- **Five views agree:** by height, yes. By shape, e reads flatter than the other four. This is the same pattern as the rhino, milder.
- **Same machine, no new parts:** PASS.
- **Plates and seams:** seams near the approved share (s a little low). Plates are rounder and lumpier than approved, with fewer plate breaks. PARTLY.
- **Visor full size:** s PASS (15). se MISS (8 against a floor of 12).
  - Later (gorilla lane, Preston's yes): se fixed with pixel tools to 14 px, PASS. See `fix_se_visor.py`.
- **No visor in ne or n:** PASS. ne has two stray glow pixels on the far elbow disc, at the silhouette edge, not on the head.
- **Game feel's turn test:** not run yet. It is the final word.

## Honest call
- The angle moved, but only part way.
  - s, se, ne and n read as seen from above, at roughly 22 to 33 degrees by shape.
  - The side view moved least (about 9 to 10 degrees by shape, though its top does show).
- The new guide gave the most even heights of any run, but it did not fix the side view. The side view stayed low on both limbed machines, so I expect it on the rest of the fleet too.
- Against the checklist it is a MISS on three items: far feet, the se visor and the e band. Codex also called it a miss.

## Not verified
- The in-game turn (game feel's).
- The mirrored views (sw, w, nw), checked only by sheet_judge.
- The board was judged at reduced size.
- The game size of 1.55 px per texel is the rhino's figure, assumed to hold for the gorilla.

## Fix: extra arm in ne (Preston, 2026-11-04)
Preston: "79x77 has extra arm in front. needs fixed get rid of with tools", then "you removed the leg ... The extra arm is in front of head".
- **First try was wrong.** It took out the far hind leg at the lower left. That was reverted from Codex's original.
- **What was removed:** the orange forearm with a steel cap and two glow pixels rising above the near gauntlet, in front of where the head is (texels x 101 to 112, rows 72 to 86). The approved ne has nothing there.
- **How:** `fix_ne_extra_arm.py`, free pixel tools, no new image.
  - It works from `ne_codex_original.png`.
  - It fills one-pixel gaps in the shoulder with green shadow.
  - No dark line was left on the new outer edge.
- **Result:** ne is still 79x77, palette PASS, lowest row 130, no glow left by the head. Both hind legs are kept.
- **Before and after:** `ne_fix_before_after.png`. `slices/` keeps Codex's untouched output. `board_cam35.png` was rebuilt.

## Game feel turn test (2026-11-04): no pops, including the side view
- Board and clip: `docs/art/moba/match/cam_angle_test/ape35_board_2026-11-04.png` and `ape35_turn_2026-11-04.mp4`.
- Heights are even on screen. On the tilted quad, e shows the top of the back the way se and ne do, so the low side-view reading by shape does not show as a pop.
- The test ran on the views before the ne fix; the fix does not change the ne size.
- **When installed:** pack the views into 192 cells as the approved ones are. A 160 canvas drops the size scale to 0.83.

## Take 2 (gorilla lane, 2026-11-04)
One more Codex image, 54,566 tokens, on Preston's "Yes, second image" after he said take 1's front view "just looks like
a taller front view version". Full numbers and the brief changes are in HANDOFF.md, "Take 2". In short: the width held and
the side view moved from about 9 to 25 to 33 degrees by shape, by keeping width fixed, giving plain per-view proportions,
asking for lit flat top faces, and showing a 35-degree-only guide. Take 2 is now in `../views_cam35/`; take 1 is in
`take1_views/`.

