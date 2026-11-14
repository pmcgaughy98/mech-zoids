# Rhino cam35: lane report (rhino camera-angle lane, 2026-11-04)

One Codex image, 59,027 tokens (budget 65k to 100k). One generated image confirmed in Codex's output folder; `sheet_raw.png` is that image unchanged (same SHA256). No redo.

Board: `board_cam35.png` (approved, cam30, cam35 rows at 3x with sel-out, plus game size at 1.55 px per texel).
Views: `../views_cam35/` (s, se, e, ne, n). `../views/`, `../views_cam30/` and `../anim/` were not touched (no file in them changed during the run).

## What I changed in the sprite factory's draft (drafts kept as `*.draft.txt`)
- Codex may no longer open `views_cam30` or any cam30 image, and no longer reads cam30's REPORT. It gets the first try's numbers in the brief. The job rule is that Codex never sees the cam30 try.
- The accent target is stated in the finishing step: the approved share, 6 to 9%.
- The prompt adds one line: draw the top only as the reference implies it, with nothing new added up there.

## Angle check (re-measured by `verify.py`; Codex's numbers agree)
Rule: height / guide height between 0.85 and 1.08; the five within 0.08.

| view | W x H | H / guide | rule | first try | new H / approved H |
|---|---|---|---|---|---|
| s | 67x84 | 0.778 | MISS | 0.81 | 1.20 |
| se | 85x83 | 0.830 | MISS | 0.87 | 1.19 |
| e | 103x75 | 0.833 | MISS | 0.79 | 1.12 |
| ne | 83x103 | 1.030 | PASS | 1.04 | 1.39 |
| n | 65x106 | 0.981 | PASS | 0.99 | 1.38 |

Spread 0.252, MISS (first try 0.251).

**What the numbers say:**
- **Same angles as cam30.** Every view's height is within 4 px of cam30's (s 84 vs 87, se 83 vs 87, e 75 vs 71, ne 103 vs 104, n 106 vs 107). The angle guide did not move the drawing. Only e rose a little (0.79 to 0.83) and se widened.
- **Shape or angle?** A shape like the rhino's (high hump in front, lower rear deck) can make the back views read taller than the front views at one camera angle. So this check alone cannot split the spread into shape and angle.
  - By eye, the ne and n views still look steeper than s and e, and e still looks low.
  - The front views s and se also read MISS against the guide. That fits the guide over-counting the low head, as the sprite factory warned.
- **The 3D lane's angles are of cam30, not cam35.** Its readings (se, ne and n about 38 degrees, s about 48, e far lower) are in `../../3d_test/NOTES.md`. No file in 3d_test postdates this image. They likely still roughly apply, since the heights barely changed (inference, not measured).
  - The 3D model allows for the hump and reads s as the steepest view. My by-eye reading puts ne and n steepest. Both agree e is low.
  - The 3D lane flagged its own pitch scan as unreliable on the rhino, so game feel's turn test decides.

## Widths
- s 0.93, se 0.955, e 1.00, ne 0.93 and n 0.90 of the guide width.
- **se is 85 px:** that clears the 84 floor but is 4 px short of the 89 target (the first try was 78).

## Seams
**Accent share, new against approved:**

| view | new | approved |
|---|---|---|
| s | 6.4% | 6.3% |
| se | 7.4% | 7.8% |
| e | 7.7% | 9.2% |
| ne | 7.5% | 7.4% |
| n | 9.8% | 9.4% |

All five are back in the approved range (the first try was 1.7 to 3.9%).

**Caveat:** the charcoal frame share fell from 14 to 19% to 4 to 8%.
- Frame plus seams together: 10.6 to 15.7% now, against 20 to 28% approved and 11.7 to 19.0% in the first try.
- So most of the seam gain is the finishing step re-labelling dark pixels from charcoal to accent. Codex did not draw more lines.
- **Capped-ink pass: not run.** The playbook only inks a view whose share is under about 0.75 of target, and the lowest view here is e at 0.84. It is free if Preston wants the plate lines heavier.

## Other checks
- Palette PASS (the fixed 12 colours).
- Eye pixels: s 8, se 5, e 5; ne and n 0.
- Lowest row 160 in all five; no border contact; alpha is fully on or off.
- view_check: lone 0.076, so no despeckle was needed.
- sheet_judge: flags only heights, which the brief waives.

## Drift against the approved views
- Plates are still rounded and blobby, with fewer straight-cut facets. Codex says the same.
- The charcoal frame and the dark gaps between plates have mostly gone (see Seams), so the knee discs and joints read weaker.
- The far feet are not clearly higher on the page in e; Codex marked them as obscured.
- The head and hump proportions drift as in cam30. Same rhino, no new parts seen.

## Not verified
- **No shape-aware angle measure on cam35.** The 3D lane's model-height method was not run, so no per-view pitch in degrees.
- **No in-game camera turn.** That is game feel's test, and the final check.
- **The mirrored views (sw, w, nw)** were checked only by Codex's sheet_judge.
- **The board was judged at reduced size.**

## Later results (2026-11-04)
- **Installed in game** as the idle in all five views, tilted toward the camera while idling only (game feel's per-animation tilt). Godot import, then rhino3d_check: 64 PASS, 0 failures. ROSTER.md has the entry.
- **Game feel's turn test on the installed set:**
  - The idle turns a full circle with no pops, even though the views grew unevenly against the approved ones (s 1.20, se 1.19, e 1.12, ne 1.39, n 1.38).
  - It pops hard on every walk start and stop, because the walk is still upright at the old angle; the tilted back idle stands about 1.6 times the walk frames. This was accepted and is not fixed.
  - The camera-angles lane reports that the pivot on the near foot makes the body float about 0.35 m behind its ground point. A per-view ground-row meta may be asked for in pack_rhino_3d.py.
- **For any second rhino image (needs Preston's yes):** the gorilla lane got even growth across its five views (8 to 10%, spread 0.02). It did that with a guide built from the machine's own solid at 6 and 35 degrees, plus the line "every view, the side view included, grows by about the same amount". See `ape_l/take-a/cam35/LANE_REPORT.md`.
- **Gorilla's second image (54,566 tokens) lifted its low side view from about 9 to 25 to 33 degrees.** Four changes, in `ape_l/take-a/cam35/take2/prompt-sheet.txt` and `brief.txt`:
  1. "WIDTH STAYS, HEIGHT GROWS", with per-view proportions in plain words from the machine's own 35-degree solid ("the side view becomes TALLER THAN IT IS LONG").
  2. "FLAT TOP FACES THAT FACE UP": lit tops on the hump, back and limbs; front faces shorter, top faces longer.
  3. A one-row guide at 35 degrees only (`cam35_fleet/hull_guide.py`).
  4. Scale anchored on the mean of s width, n width and e length, not e alone.
  The gorilla's turn test is still to come.
- **Gorilla take 2 passed in game** (game feel: no pops, side view reads from above; Preston accepted it). Its heights run 83 to 89 px with steps of 1 to 5 px between neighbouring views.
  - The rhino's cam35 steps are larger: s 84, se 83, e 75, ne 103, n 106. That is 28 px from e to ne.
  - Game feel still saw no pops on the rhino's idle turn.
  - For a rhino redo, use the gorilla's take-2 recipe and aim for small steps between neighbouring views.
