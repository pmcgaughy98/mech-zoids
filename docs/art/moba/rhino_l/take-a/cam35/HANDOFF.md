# Rhino cam35 redo: handoff from the sprite factory lane (2026-11-04)

Preston approved this redo at 65k to 100k Codex tokens for ONE image ("go rhino full redo option b", relayed by
Mech-Zoids). Then he moved it to a new session ("go and make a new session for it now"). Nothing for the rhino cam35
has been run. Everything below was prepared free.

## Required reading (in this order)
1. This file.
2. `brief.txt` and `prompt-sheet.txt` in this folder. These are drafts, ready to run as they are.
3. `../cam30/REPORT.txt`, the first try.

## Ready in this folder
- `refs/approved_views.png`: the five approved views on magenta at 4x (s, se, e, ne, n). It is the same as cam30's.
- `refs/angle_guide.png` and `guide_sizes.txt`: the angle guide at 35 degrees.
- `prompt-sheet.txt`: the image prompt.
  - It has two attachments.
  - The e view is worded "SIDE VIEW ... seen from 35 degrees above", never "profile".
  - It holds s back from going overhead.
  - It asks for se at full width, and for hard plate edges and seams.
- `brief.txt`: the Codex job. It has a fixed 12-colour palette, scales e to 103 px, slices at canvas 192 with the lowest foot on row 160, and adds the angle, width and accent checks.
- Launch it as the playbook says, from `C:/Users/pmcga/dev/hollowtide`:
  `codex exec --sandbox workspace-write --add-dir "D:\dev\new-mech-rpg\docs\art\moba" --skip-git-repo-check < brief.txt > codex-log.txt 2>&1`
  Use the full path to brief.txt, and run it in the background.

## The angle guide
- **Script:** `minion_s/take-a/cam35/angle_guide.py L W H out.png pitch`.
  - It draws a plain solid with an elliptic footprint and a flat top, in the five views.
  - The front is tinted green.
  - It prints each view's width and height in texels.
- **The rhino's numbers:** L 103, W 72, H 60 texels.
  - L is the approved e length and W the approved s width.
  - H is set so the guide reproduces the approved views at 6 degrees, the pitch the 3D lane's build used.
  - At 6 degrees the guide gives s 72x70, se 89x69 and e 103x67. The approved views are s 72x70, se 89x70 and e 103x67, so the calibration holds.
  - The rear views are narrower than the guide (approved ne 77, n 66, against 89 and 72).
- **Guide at 35 degrees (W x H):** s 72x108, se 89x100, e 103x90, ne 89x100, n 72x108.
- **Why elliptic and not a box:** a box's corners make the diagonal views far too wide. On the drone, a box gives se 91 px against 62 drawn; the ellipse gives 64. For the rhino, the ellipse gives se 89, exactly the approved width.

## Expected heights, and how far to trust the check
- **Preston's rule** (as relayed): height / guide height between 0.85 and 1.08, and the five ratios within 0.08 of each other.
- **The first try's ratios against this guide:** s 0.81, se 0.87, e 0.79, ne 1.04, n 0.99.
- **The ratio is a weak absolute measure.** The guide has a flat top at full height all the way round, so it overstates any view whose far end is low.
  - On the rhino, the low head in front and the lower rear deck do this.
  - That is why the first try's s scores 0.81 against this guide, while the 3D lane measured it as too steep (about 48 degrees).
  - The 3D lane's `../../3d_test/rhino_cam30.json` now gives pitches of s 50, se 50, e 46, ne 48 and n 40. Its scan's "explained" score barely moves with pitch (0.885 to 0.887 from 6 to 20 degrees), so I would not use those numbers as targets either.
- **Read the ratios mostly for agreement between views,** and next to the first try. Judge the angle by eye on the board and in game feel's in-game test.
- **Report the rule's PASS or MISS as it falls,** but say this when a MISS comes from a view's shape rather than its angle.

## Lessons from the drone cam35 (minion_s/take-a/cam35: one image, 56,967 Codex tokens)
- **Worked:**
  - The lens and seams are fixed, both from the prompt wording.
  - Lens: s 132 against 127 expected, se 111 against 114.
  - Accent share is back at or above the approved views in all five (s 10.5%, n 9.6%).
  - Every view reads as seen from above.
  - The e view's shell top shows as a wide band. Wording e as "SIDE VIEW ... seen from 35 degrees above" with "a WIDE BAND" worked where "profile" failed.
  - No lens pixel in the rear views; only the 14 colours; lone 0.08.
- **The angle check still reads MISS on four of five.**
  - Height / guide: s 0.875, se 0.81, e 0.76, ne 0.73, n 0.75, a spread of 0.14.
  - By eye, the five views agree with each other.
  - The low ratios sit where the drone's ends are low: the pods and barrels hang below the shell. The flat-topped guide counts them at full height.
  - So the absolute window is mis-calibrated for machines that aren't tub-shaped. The rhino will show the same, more strongly in s and n.
- **Finishing:** the accent-keeping step in the brief ("map dark seam pixels to accent 141218 rather than charcoal") did its job. It's in `brief.txt` here too.
- **The board script:** `minion_s/take-a/cam35/cam35_board.py`.
  - Adapt it for the rhino: five views, the 192 canvas, and sel-out from `rhino_l/take-a/anim/selout_rhino.py`.
  - The rhino needs no red row.
  - Game size is 1.55 px per texel; the cam30 rhino board script `../cam30/cam30_board.py` already uses it and is the closer starting point.
  - Note: palette.json hex values may carry a "#", so strip it.

## After the run
- If the seams come back thin, run the free capped-ink pass. It uses the same rule as `hippo_l/take-b/remaster-pilot/capped_ink.py`, and the multi-machine version is `docs/art/moba/capped_ink_trial.py`.
- Send the board to Mech-Zoids Game and to the game feel lane ("Run the mech MOBA game feel lane").
- Leave `../views/`, `../views_cam30/` and `../anim/` untouched.
- If the image fails, stop and report. A second image needs a new yes from Preston, about 45k to 70k.

## Update: the drone cam35 views in game (game feel lane, 2026-11-04)
- The five drone views read as one angle on screen. They turn a full circle around a tilted drone with no pops, all
  views and mirrors keep the dome top, and the heights (56 down to 48 px) step gently.
- The guide check's low ratios (0.73 to 0.88) don't show on screen. This confirms that the ratio over-reads
  machines whose ends sit low, so judge the angle by eye and by the in-game test.
- The only problem was the tilted quad leaning back into walls behind it, which is game feel's to fix, not the drawing's.
- Board and clip: `docs/art/moba/match/cam_angle_test/drone35_board_2026-11-04.png` and `drone35_camera_turn_2026-11-04.mp4`.
