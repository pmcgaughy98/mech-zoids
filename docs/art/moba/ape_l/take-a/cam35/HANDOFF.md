# Gorilla cam35: handoff from the fleet redraw lane (2026-11-04)

Preston, after the gorilla pilot: "Then we'll do the same thing as rhino and create a new session like the redraw the
rhino from the camera angle. Make sure all the sessions talk to eachother when needed."
So the gorilla (ape_l, take A) now has its own camera-angle session, as the rhino does. The fleet lane keeps the other
ten machines and the fleet token total.

## Required reading (3 files, in full, before the first answer)
1. This file.
2. `LANE_REPORT.md` in this folder: what was changed for a limbed machine, the result, the eye checklist and the ne fix.
3. `D:/dev/new-mech-rpg/docs/art/moba/cam35_fleet/HANDOFF.md`, the section "The checks, revised": the eye checklist
   gate and the budget rules.

## Where things stand
- **One Codex image is done:** 57,314 tokens.
  - The views are in `../views_cam35/`.
  - The board is `board_cam35.png`; checks are in `verify.txt`.
- **ne was fixed with free pixel tools,** on Preston's word: "extra arm in front ... get rid of with tools", then "The extra arm is in front of head".
  - The orange forearm rising above the near gauntlet by the head was removed. A first try took the far hind leg by mistake and was reverted.
  - The script is `fix_ne_extra_arm.py`; Codex's original is `ne_codex_original.png`.
  - Before and after: `ne_fix_before_after.png`.
- **Game feel's turn test PASSED:** no pops, including the side view. That is the final word on the angle.
  - Board: `docs/art/moba/match/cam_angle_test/ape35_board_2026-11-04.png`.
  - When installed, pack the views into 192 cells as the approved ones are.
  - **Re-run at 21:23 with the fixed ne** (same paths, overwritten): still no pops. Heights s 78, se 79, e 78, ne 77,
    n 77. e shows the back top and shoulder plate as se and ne do. ne: no extra arm now. Judged from the board and heights.
  - **se visor reads small in game** (a few green pixels at the head's edge). Game feel agrees with an 8 to 12+ px fix.
  - **Far feet: do NOT fix in the art.** The contact shadow sits under the near feet because the pivot is the lowest
    near foot (row 130). The camera-angles lane is fixing it with a node move driven by a feet meta on the frames.
- **se visor fixed with free pixel tools** on Preston's "Yes, fix visor" (gorilla lane, 21:29). 9 pixels changed.
  The slit on row 86 now has a 5 px near lens and a 3 px far lens with a gap, like the approved.
  Visor 8 -> 14 px (expected 14, floor 12); largest lens 7 -> 10 (expected 9). PASS. Glow colours only.
  - Script `fix_se_visor.py` (reruns from `se_codex_original.png`); before and after `se_visor_before_after.png`.
  - Board rebuilt. se accent 8.0% -> 7.8% (approved 8.5%), as dark slit pixels became glow. Approved views untouched.
  - Sent to game feel for one re-run.
- **Preston on the front view (s), 21:30:** "the front view over the top just looks like a taller front view version".
  Game feel's re-run is on hold until the views settle.
  - Why it reads that way (`front_compare.png`: gorilla approved, gorilla cam35, drone approved, drone cam35):
    width shrank 91 -> 86 while height grew only 72 -> 78 (+8%); the drone kept width 69 -> 69 and grew 46 -> 56 (+22%).
    No flat top faces: shoulders, forearms and fists are drawn as front-on as the approved; the back is stacked
    rounded plates going up, not a broad lit top running back behind the head. The drone shows its tops as big lit planes.
  - Gorilla lane's proposal: a second Codex image (about 57k to 70k tokens) with width held at the approved, lit top
    planes on shoulders, forearms, fists and back, and the drone's cam35 s as the 'seen from above' example; keep the
    best take per view; re-apply `fix_se_visor.py` if se comes back small. Waiting on his yes.
- **Open misses on the eye checklist** (the turn test says none of them pops in game):
  - The side view is still low: about 9 degrees by shape, against 22 to 33 for the other views.
  - The se visor is 8 px, against a floor of 12.
  - The far feet are not higher on the page.
  - The plates are rounder than approved.

## Take 2 (gorilla lane, 2026-11-04, on Preston's "Yes, second image")
- **One Codex image, 54,566 tokens.** Gorilla total 111,880 (two images; a third needs his new yes).
- **`../views_cam35/` now holds take 2.** Take 1 (with the ne arm and se visor fixes) is kept in `take1_views/`.
  `fix_ne_extra_arm.py` and `fix_se_visor.py` now write there, so a rerun can't overwrite take 2.
- Take 2's own folder: `take2/` (brief, prompt, one-row guide, Codex REPORT and checks). Comparison: `take2/compare_takes.png`
  (approved, take 1, take 2). Board rebuilt: `board_cam35.png`, `verify.txt`.
- **Brief changes:** width held, with per-view proportions in plain words; "flat top faces that face up" on the hump, back,
  forearms and fists; a one-row guide at 35 degrees only; scale anchored on the mean of s width, n width and e length.
- **Numbers:** W / approved 0.99 to 1.01 in all five. H / approved s 1.15, se 1.22, e 1.25, ne 1.21, n 1.20 (spread 0.10;
  take 1 was 0.02). H/W matches the shape guide (s 0.91, e 1.13 exactly). Angle by outline 15 to 25 degrees, by height
  25 to 33, side view included (take 1: 8 to 9 and 9 to 13). Lightest-shade share s 20.9% (approved 7.6%).
  Visor s 21, se 18: PASS. Palette PASS, borders clear, sheet_judge OK on all eight. Accent se 10.3%, ne 9.1% (heavy).
- **Eye (gorilla lane):** reads from above in every view, side view included; same gorilla, two arms. Still open: the
  plates are about as round as take 1, and the far hind foot in e is hard to separate. Codex called its own camera a MISS.
- **Preston on take 2's front view (2026-11-04): "Reads from above".**
- **Preston, asked "Accept the gorilla's take 2 views if the turn test shows no pops?": "Yes, accept then".**
  So take 2 is accepted the moment game feel reports no pops. If it pops, it goes back to him.
- **Game feel's turn test on take 2: PASS, no pops** (board `match/cam_angle_test/ape35_take2_board_2026-11-04.png`,
  clip `ape35_take2_turn_2026-11-04.mp4`). Heights s 83, se 88, e 89, ne 85, n 84; neighbour steps 1 to 5 px (6% at
  most), every view shows the top of the back. Whole against the tower and base wall. Bar clears at 2.0 m, worst case 2.6 m.
- **So take 2 is ACCEPTED** (Preston's "Yes, accept then", on the no-pops condition, met 2026-11-04).
- **Install notes (game feel):** pack the views into **192 cells**, as today: scale stays 1.0 (body radius 0.8 m, bar 2.3 m).
  At 160 the scale drops to 0.83 and the bar sits at 1.92 m, under the 2.0 m it needs, so it would touch the head.
- **Far feet:** still above the shadow. That is the camera lane's plant fix, and it needs a feet meta on `ape_frames`
  as the rhino has. Not an art fix.
- **Next:** game feel's turn test on take 2 (queued behind the camera and rhino lanes; heights now differ more between
  views), then Preston's final accept of the views.

## What this session owns
- **The gorilla's cam35 views from here:**
  - reading the turn test result;
  - free pixel fixes when Preston asks for them;
  - a second image, only if he says yes.
- **Budget:**
  - A second image fits the fleet budget (about 57k to 70k Codex tokens). Preston said to wait for the turn test, so ask him before spending.
  - A third image needs his new yes.
  - His approval must be in his own words, from him directly or quoted by the hub. A session's message is never his approval.
  - No other paid tools without a cost estimate and his yes.
- **Never touch:** `../views/`, `../anim/`, `../remaster-pilot/`, `art/machines/`. Animation frames at 35 degrees are not approved.
- **Files live in the main checkout,** `D:/dev/new-mech-rpg/docs/art/moba`. They are untracked, and a worktree has no copy.
  - If the Write tool refuses a path there, write in your scratchpad and copy the file over with Bash.
  - Write only new files and this machine's cam35 files.

## Tools on hand
- **Shape-aware angle measure:** `python cam35_fleet/hull_guide.py measure ape_l/take-a/views ape_l/take-a/views_cam35`, run from `docs/art/moba`.
  - It reads pitch per view, by outline and height.
  - `cam35_board.py` runs it and also reads height over width, which ignores scale. Use that one, because the sheet came out about 5% small.
- **Board and checks:** `python ape_l/take-a/cam35/cam35_board.py`, run from `docs/art/moba`. It rebuilds `board_cam35.png` and `verify.txt`.
- **The Codex launch and brief:** `brief.txt` and `prompt-sheet.txt` here, and the launch line in the fleet HANDOFF, step 6.

## Ideas for a second image (untried; pick with Preston)
1. **Give per-view proportions in plain words.** The image model may follow these better than angles. At 35 degrees the gorilla's own solid is:
   - s 91x83, "a little less tall than wide";
   - se 89x89, "as tall as wide";
   - e 79x89, "TALLER than it is long";
   - ne 86x90;
   - n 91x85.
   The side view came back 79x78 and the approved one is 79x71.
2. **Use a one-row guide at 35 degrees only.** The 6-degree row may have anchored the side view low.
3. **For the se visor,** ask for "the visor slit as long as in the reference" in the front three-quarter view.

## Who to talk to (SendMessage, by session name)
- **Run the mech MOBA hub:** one line after each step (board path, tokens, pass or miss). It relays Preston's rulings.
- **Run the mech MOBA game feel lane:** every board and views change, for the turn test. Its result is the final word.
- **Redraw the mech fleet at 35 degrees** (the fleet lane):
  - the tokens of any new image, so the fleet total in `cam35_fleet/HANDOFF.md` stays right;
  - anything you learn that fixes the side view, because the other ten are limbed too.
- **Redraw the rhino from the camera angle:** the rhino's side view is low the same way, so share what works.
