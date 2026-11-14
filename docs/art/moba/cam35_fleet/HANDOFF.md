# Fleet redraw at 35 degrees: handoff from the sprite factory lane (2026-11-04)

Preston (relayed by Mech-Zoids Game): "go redraw the rest of the machines at 35 thats perfect". He said it after the
drone cam35 set turned a full circle in game with no pops. The sprite factory session that built the recipe had grown
long, so it is handing the fleet to a fresh session. Nothing in this fleet has been run yet.

## Required reading (2 files)
1. This file.
2. `docs/art/moba/rhino_l/take-a/cam35/HANDOFF.md`: the method, the angle guide, and the drone's lessons, including
   the in-game result at the end.

Then open the drone's run as the worked example (`minion_s/take-a/cam35/`: `prompt-sheet.txt`, `brief.txt`,
`finish.py`, `cam35_board.py`, `REPORT.txt`). Use the rhino's `rhino_l/take-a/cam35/prompt-sheet.txt` as the
four-legged example. Its own session ran it; read its REPORT.txt if it's there.

## Scope, budget, order
- **Scope:** 11 machines.
  - gorilla (ape_l), fennec, wolf, hippo, kangaroo, pangolin;
  - shoebill, chameleon, falcon, hummingbird, squirrel.
  - Not the rhino (its own session) or the drone (done).
- **Budget:** one image per machine, at about 60k to 100k Codex tokens each.
  - A second image where the first misses is allowed, inside the fleet total of about 0.9M to 1.5M.
  - A third image on any machine, or going past 1.5M overall, needs Preston's new yes through Mech-Zoids.
- **Order, one at a time** (so the Codex usage limit can't stall a batch):
  1. gorilla, fennec, wolf;
  2. hippo, kangaroo, pangolin, shoebill (they have frames);
  3. chameleon, falcon, hummingbird, squirrel.
- **Never touch:** the approved views, `anim/`, `art/machines/`, `views_cam30/`.

## Per machine: what to build
- **Working folder:** `<machine>/<take>/cam35/`. Put `refs/approved_views.png` and `refs/angle_guide.png` in it.
- **Output:** the five views (s, se, e, ne, n) in `<machine>/<take>/views_cam35/`.
- **Team colours:** none of these 11 is expected to have team-coloured parts; only the drone has them. Check each
  prompt-sheet's palette line. Make a `_red` folder only where there are team colours.
1. **Reference sheet:** the five approved views on magenta at 4x, sharing a baseline. Copy the snippet from the drone or
   the rhino run. Use the approved folder in the table below: some machines use `fixed/`, not `views/`.
2. **palette.json:** only the rhino and the drone have one. For the rest, write it free from the approved views, with
   roles and shades taken from the palette line in that take's `prompt-sheet.txt`. The palette is fixed in the finish
   step.
3. **Angle guide:** `python minion_s/take-a/cam35/angle_guide.py L W H refs/angle_guide.png 35 > guide_sizes.txt`,
   with L, W and H from the table.
   - L is the e view's length and W is the s view's width.
   - H is set so the guide reproduces the approved s height at 6 degrees.
   - Flyers (falcon, hummingbird) include their wings in L and W, so their guide is coarse.
4. **prompt-sheet.txt:** start from the machine's own take `prompt-sheet.txt` and keep its parts, colours,
   signature and palette lines. Replace its VIEWS paragraph and its 3x3 layout with the camera wording from the drone
   and rhino cam35 prompts:
   - two attachments (approved views first, then the guide);
   - "ONLY THE CAMERA MOVES UP";
   - the top showing in every view;
   - e worded as "SIDE VIEW ... seen from 35 degrees above, the top showing as a WIDE BAND", never "profile";
   - the far feet higher on the page;
   - the hard plate edges and seams paragraph;
   - eyes or lens kept full size.
5. **brief.txt:** copy the drone's or rhino's and change the paths, canvas, feet row, scale anchor (scale once so the
   e view is L px long) and the number of palette colours. Keep the accent-keeping finish step.
6. **Run Codex** from `C:/Users/pmcga/dev/hollowtide`, in the background:
   `codex exec --sandbox workspace-write --add-dir "D:\dev\new-mech-rpg\docs\art\moba" --skip-git-repo-check < <full path>/brief.txt > <full path>/codex-log.txt 2>&1`
7. **Afterwards:**
   - Read REPORT.txt and the token count (the last "tokens used" line in codex-log.txt).
   - Build the board by adapting `minion_s/take-a/cam35/cam35_board.py`:
     - one row of approved views and one of new views, at 3x for 192 canvases or 4x for 160;
     - a game-size row;
     - sel-out from `rhino_l/take-a/anim/selout_rhino.py`, applied for review only;
     - strip the "#" from palette.json hex values.
   - Look at the board yourself before sending it.
8. **If the seams come back thin,** run the free capped-ink pass (`docs/art/moba/capped_ink_trial.py`, the same rule
   as `hippo_l/take-b/remaster-pilot/capped_ink.py`) on the new views.
9. **Report after each machine** to Mech-Zoids Game: the board path, the tokens, pass or miss, and the running fleet
   total. Send the board to the game feel lane ("Run the mech MOBA game feel lane") too.

## The checks, revised (Mech-Zoids asked for the height window to be fixed)
- **The height-over-guide ratio is retired as a gate.** It can't tell angle from shape:
  - The drone's five views scored 0.73 to 0.88 and passed in game with no pops.
  - The rhino's first try scored s 0.81 and e 0.79, yet one was too steep and the other too flat.
  - The flat-topped guide overstates any view whose ends hang low.
- **Report the ratios, and each view's height gain over the approved view, as information only.**
- **The gate is the eye, on the board:**
  - The top shows in every view, including e, where it should show as a wide band.
  - The far feet sit higher than the near feet in e, se and ne.
  - The five views agree on how much top shows.
  - It is the same machine, with no new parts.
  - The plates are hard and the seams are at about the approved accent share.
  - The eyes or lens are full size, and there is no eye pixel in ne or n.
  - The game feel turn test is the final word.
- **Eyes or lens at the tilt-expected size:** the largest connected group of eye colours in the approved s and se,
  times about 0.82 (cos 35 / cos 6). Under 85% of that is a miss. Count only the eye. On the drone, the 222 total
  included nozzle glows hidden from above, and the lens alone was 153.
- **Keep these:**
  - the palette check (only the fixed colours);
  - the canvas border check;
  - the lowest foot on the feet row;
  - view_check and sheet_judge on all eight slices (the canon's same-height rule does not apply).

## Per-machine data (approved views measured 2026-11-04)
Sizes are W x H in texels. The guide is at 35 degrees. "Sheet tokens" is what the original 8-view sheet cost.

| Take | Approved folder | Canvas | Feet row | Approved s, se, e, ne, n | Colours | Guide L W H | Guide at 35 | Sheet tokens |
|---|---|---|---|---|---|---|---|---|
| ape_l/take-a (gorilla) | `views/` | 160 | 130 | s 91x72, se 89x72, e 79x71, ne 86x70, n 87x70 | 15 | 79 91 64 | s 91x98, se 85x101, e 79x105, ne 85x101, n 91x98 | 49,222 |
| fennec_s/take-b | `views/` | 160 | 140 | s 49x72, se 63x72, e 74x74, ne 58x75, n 44x77 | 15 | 74 49 65 | s 49x95, se 63x89, e 74x81, ne 63x89, n 49x95 | 56,063 |
| wolf_m/take-b | `fixed/` | 192 | 160 | s 33x72, se 83x70, e 110x66, ne 78x70, n 35x72 | 12 | 110 33 61 | s 33x113, se 81x96, e 110x69, ne 81x96, n 33x113 | 59,383 |
| hippo_l/take-b | `views/` | 192 | 160 | s 77x70, se 113x70, e 123x62, ne 105x77, n 73x76 | 14 | 123 77 57 | s 77x118, se 103x106, e 123x91, ne 103x106, n 77x118 | 57,627 |
| kangaroo_m/take-a | `fixed/` | 160 | 140 | s 55x80, se 64x79, e 69x78, ne 65x77, n 49x79 | 13 | 69 55 73 | s 55x100, se 62x96, e 69x91, ne 62x96, n 55x100 | 54,082 |
| pangolin_m/take-a | `views/` | 192 | 160 | s 45x56, se 70x54, e 82x43, ne 67x52, n 45x59 | 13 | 82 45 48 | s 45x86, se 66x77, e 82x65, ne 66x77, n 45x86 | 58,660 |
| shoebill_m/take-e | `views/` | 160 | 140 | s 66x80, se 84x81, e 96x78, ne 66x81, n 58x82 | 16 | 96 66 70 | s 66x113, se 82x105, e 96x95, ne 82x105, n 66x113 | 72,216 |
| chameleon_m/take-b | `views/` | 160 | 140 | s 49x65, se 65x62, e 84x59, ne 65x62, n 47x63 | 16 | 84 49 57 | s 49x94, se 69x86, e 84x74, ne 69x86, n 49x94 | 91,991 |
| falcon_m/take-b | `views/` | 160 | 140 | s 50x72, se 60x71, e 71x69, ne 57x71, n 48x71 | 16 | 71 50 65 | s 50x94, se 61x88, e 71x82, ne 61x88, n 50x94 | 66,852 |
| hummingbird_s/take-a | `views/` | 160 | 140 | s 46x72, se 75x70, e 92x69, ne 69x73, n 44x73 | 15 | 92 46 63 | s 46x104, se 73x93, e 92x78, ne 73x93, n 46x104 | 52,085 |
| squirrel_s/take-b | `fixed/` | 160 | 140 | s 56x72, se 69x71, e 75x71, ne 63x72, n 52x72 | 16 | 75 56 65 | s 56x96, se 66x91, e 75x85, ne 66x91, n 56x96 | 59,507 |

Notes:
- **The approved views already carry Preston's rulings.**
  - Capped ink is installed on wolf `fixed/n`, fennec `views/ne` and `n`, falcon `views/ne`, squirrel `fixed/ne`,
    hummingbird `views/n` and hippo `views/ne` and `n`.
  - The gorilla is sel-out only.
  - Codex sees these as they are.
- **Shoebill has two approved takes.** take-e ("Keep E") is the later ruling, so use it, not take-c.
- **The wolf's front and back views are very narrow** (33 to 35 px). The 35-degree s and n will mostly show its back,
  which is expected.
- **Before each machine,** check the ROSTER and that take's RUN.md files for a newer "Ruling" or "Decided" section.
  A click can be corrected in another session, as happened with the gorilla.

## Progress (fleet redraw lane, 2026-11-04)
**Running Codex total: 450,532 tokens** (of 0.9M to 1.5M). Seven images: gorilla 2 (57,314 + 54,566 = 111,880), fennec 1 (70,848), wolf 1 (61,049), hippo 1 (71,498), kangaroo 2 (78,028 + 57,229 = 135,257).

| machine | images | tokens | result | board |
|---|---|---|---|---|
| gorilla (ape_l/take-a), pilot | 2 | 111,880 (take 1 57,314; take 2 54,566) | take 2 is final: "Reads from above" (Preston); the turn test found no pops (heights 83 to 89, steps of 5 px at most), so his "Yes, accept then" applies. Take 1 had passed the turn test but read "taller" | `ape_l/take-a/cam35/board_cam35.png` |
| fennec (fennec_s/take-b) | 1 | 70,848 | reads from above in all five; eyes fixed with tools (s 22 to 28, se 10 to 18); turn test: no break, but it grows 19 px from s to n (e to ne +8, the tail flips), Preston kept it ("Looks fine, keep it", 2026-11-04). DONE | `fennec_s/take-b/cam35/board_cam35.png` |
| wolf (wolf_m/take-b) | 1 | 61,049 | reads from above in all five; eyes s 6, se 6, e 4; side view short and low (100x58 against 110x66). Turn test: PASS, no pop; the e/ne step 58 to 91 reads as turning into depth (se is the soft spot: raise se, not lower ne, if ever smoothed). Preston: "Turn test, then fix"; ne ear-tip eye pixel removed (`fix_ne_ear_pixel.py`). DONE, install in 192 cells | `wolf_m/take-b/cam35/board_cam35.png` |
| hippo (hippo_l/take-b) | 1 | 71,498 | reads from above in all five; eyes PASS (s 18+18, se 21, e 16), none in the rear; no fixes. e short and low again (110x71 against 123x62; guide 82). Turn test: PASS, no pop; e/ne step 71 to 99 reads as turning into depth; se 88 held (wolf lesson worked). Preston: "Turn test, then accept" (2026-11-05). DONE, install in 192 cells | `hippo_l/take-b/cam35/board_cam35.png` |
| kangaroo (kangaroo_m/take-a) | 2 | 135,257 (take 1 78,028; take 2 57,229) | take 2 is final (PARTIAL from Codex); Preston: "Free fixes first". Done in `take2/fixed/`: s eyes 1+1 to 2+2, one despeckle pass on all five (lone share 0.05-0.09 to 0.02-0.03). Turn test: PASS, no pop; e reads as turning into depth (swaps 14.8 to 16.5, se/e 15.4, e/ne 15.3), feet row holds. Preston: "Yes, accept it" (2026-11-05). DONE, install `take2/fixed/` in 160 cells. Fixed: ne shows the back of the head, no eye (0 px in ne and n); se, ne and n read from above (lit tops, se far foot 132 against 140). Still short: e near-level (77 against guide 83), s eyes 1+1 px (approved 2+2), light speckle on ne and n. Widths 0.97 to 1.02, side over front 1.30 (approved 1.25). Detail: `kangaroo_m/take-a/cam35/take2/LANE_REPORT.md` | `kangaroo_m/take-a/cam35/take2/board_cam35_fixed.png` |

- **Stopped after the pilot for Preston's look,** as planned. The other ten wait for his go.
- **The gorilla now has its own session,** "Redraw the gorilla from the camera angle" (Preston, 2026-11-04). It reports any new tokens here.
- **Recipe change for limbed machines:**
  - The guide is now `cam35_fleet/hull_guide.py guide <views> refs/angle_guide.png 6 35`. It is a solid cut from the machine's own approved outlines, in two rows (6 and 35 degrees), and it replaces `angle_guide.py`.
  - `hull_guide.py measure` gives a shape-aware angle per view.
  - Detail and the drone and rhino comparison: `ape_l/take-a/cam35/LANE_REPORT.md`.
- **Hub:** reports go to "Run the mech MOBA hub", which replaced "Mech-Zoids Game".

## Next session: start here (fleet redraw lane, written 2026-11-04 after the fennec)
This session grew long, so the rest of the fleet goes to a fresh session.
- **Preston's go:** "Go, fennec first" (2026-11-04), after the gorilla pilot.
- **Preston (2026-11-04): the wolf starts "After gorilla take 2".** Read the gorilla take-2 result (`ape_l/take-a/cam35/take2/`, its lane report and turn test) and use whatever brief changes it proves. Then confirm with Preston before spending.
- **Wait for Preston's go, in his own words, before the wolf.** He flagged the gorilla's front view as "a taller front view version", so the method may change first; see the gorilla lane's take 2 below.
- **Next machine:** the wolf (`wolf_m/take-b`, approved folder `fixed/`, canvas 192, feet row 160). After it come hippo, kangaroo, pangolin and shoebill, then chameleon, falcon, hummingbird and squirrel.
- **Required reading (3 files):**
  1. This file.
  2. `fennec_s/take-b/cam35/LANE_REPORT.md`, the latest run.
  3. `ape_l/take-a/cam35/LANE_REPORT.md`, the drone and rhino comparison and why the guide changed.
- **The recipe per machine (about 6 tool calls):**
  1. `python cam35_fleet/prep_machine.py <take> <approved subdir> "<hex:role:shade,...>" <eye hexes> <accent hex>`, run from `docs/art/moba`. It writes the refs, `palette.json`, the shape guide and `guide_sizes.txt`, and prints the approved sizes, accent shares and eye pixels.
     - Take the palette line from the take's own `prompt-sheet.txt`.
     - Look at the guide once.
  2. Copy `fennec_s/take-b/cam35/prompt-sheet.txt` and `brief.txt` and change the machine's parts, colours, palette, layout lines and numbers.
     - **Write the HOW MUCH line from that machine's guide heights.** Don't write "every view grows the same": a tall-eared or long-tailed machine gets shorter in some views.
     - Keep the part-count line.
  3. Run Codex in the background (step 6 above).
  4. `python cam35_fleet/fleet_board.py <take> <approved subdir> "<Title>" <eye hexes> <accent hex> <outline hex>` builds `board_cam35.png` and `verify.txt`. Look at the board.
  5. Write `LANE_REPORT.md` in the machine's cam35 folder, add a row and the total here, and report:
     - to Preston: board, tokens, pass or miss;
     - to "Run the mech MOBA game feel lane": the turn test;
     - to "Run the mech MOBA hub": one line.
- **Lessons so far:**
  - The shape measure's angle by height over width is information only. Ears, horns or wings drawn shorter read as a "steeper" camera.
  - The game feel turn test is the gate. The gorilla passed with an uneven measure.
  - **From the gorilla lane:** a front view that loses width and only gains height reads "taller", not "from above" (Preston on the gorilla's s). So ask to hold each view's width at the approved, and ask for lit top faces on the shoulders, limbs and back.
  - **Eyes come back small** (gorilla se 8 px, fennec s 22 and se 10). The free fix is the gorilla lane's `ape_l/take-a/cam35/fix_se_visor.py`: paint the glow along the dark slit Codex drew. It needs Preston's word per machine.
  - **Check the canvas holds the taller views.** Game feel: the gorilla take 2 must be packed into 192 cells, or the bar ends up on its head. Pick the canvas from the guide's tallest view plus headroom, not from the approved canvas.
  - **After Preston approves a machine,** message "Touch up mech sprites in Aseprite" that its views_cam35 are final, quoting his words. That lane recolours only, into `views_cam35_touchup/`, and never writes to our folders. It was told on 2026-11-04 that the gorilla (take 2) and the fennec are final.
  - **Long-bodied machines: keep se as tall as the guide says** (game feel, wolf turn test, 2026-11-04). At 35 degrees part of the body length turns into screen height in the three-quarter views, about length x 0.707 x sin 35.
    - If se is drawn flatter than that, the whole height change bunches up at the e to ne swap. The wolf's se came back about 8 to 20 px short, and its biggest jump is at e to ne. It passed with no pop, but a smoother turn needs se and ne close.
    - In the prompt-sheet, give se its guide height in plain words, as tall as ne or nearly, for the hippo, kangaroo, pangolin and the other long bodies.
    - Detail: `match/MATCH_NOTES.md`, "Wolf take B at 35, turn test".
  - **Codex draws the side view about 10% small on long machines** (wolf e 0.91, hippo e 0.89; s and n 1.01 to 1.08). Its own height over length matched the guide (wolf 0.58 / 0.58, hippo 0.65 / 0.67), so "low" is the same shrink, not a flatter angle. The fennec (e/s 1.04 of approved) and gorilla take 2 (1.00), whose side views are not much longer than the front, did not do it. Proposed brief fix (free, fleet redraw lane, 2026-11-05, sent to the hub): say in the prompt how many times longer the side view is than the front view is wide (from the approved), size the sheet from the side view (about 70% of the cell width, the tallest view at most 55% of the cell height) instead of the 80% cap, and have the brief report e length over s width against the approved ratio before slicing. Matters most for the pangolin, shoebill, chameleon and hummingbird.
  - **Watch for extra limbs.** The gorilla's ne grew an extra forearm by the head, removed with `ape_l/take-a/cam35/fix_ne_extra_arm.py`. Make sure you remove the right part: the first try took a leg.
- **The gorilla** has its own session, "Redraw the gorilla from the camera angle" (local_a78f516e-924c-4b93-8ae4-a6c4882a60a1). Take 2 is done on Preston's "Yes, second image": **54,566 tokens**, gorilla total 111,880 (two images).
  - Result by measure: widths 0.99 to 1.01 of approved; all five read 15 to 25 degrees by outline and 25 to 33 by height,
    the side view included (take 1: 8 to 9 and 9 to 13); H/W matches the hull guide. Visor PASS, palette PASS.
  - Costs: height spread 0.10 (take 1: 0.02), accent heavy in the diagonals (se 10.3%, ne 9.1%), plates still round.
  - The one-row guide: `python cam35_fleet/hull_guide.py guide <approved views> out.png 35 35`, keep the top row.
  - **Preston on take 2's front view (2026-11-04): "Reads from above".** That is his verdict on the look, not a go for
    the wolf.
  - **Turn test on take 2: PASS, no pops** (neighbour height steps 1 to 5 px). Preston had said "Yes, accept then" on
    that condition, so **gorilla take 2 is accepted** (2026-11-04). Install in 192 cells, not 160. Take 2 is in `views_cam35/`,
    take 1 in `cam35/take1_views/`. Details: `ape_l/take-a/cam35/HANDOFF.md`, section "Take 2".
- **The worktree has no copy of `docs/art/moba`.** Write in the scratchpad and copy files over with Bash.
- **The gorilla lane's take-2 brief changes (2026-11-04).** Use them on the remaining nine. They are in `ape_l/take-a/cam35/take2/brief.txt` and `prompt-sheet.txt`.
  - A "WIDTH STAYS, HEIGHT GROWS" line, with plain per-view proportions.
  - A "FLAT TOP FACES THAT FACE UP" line: lit tops on the back, limbs and so on.
  - A one-row guide at 35 degrees only.
  - Scale anchor: the average of the s width, n width and e length over the approved, since all three stay the same with pitch. This replaces the e length alone.
  - Check whether take 2 passed the turn test before relying on it.

