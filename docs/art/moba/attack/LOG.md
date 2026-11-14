# Attack lane log

Newest first. The method is `ATTACK_PLAYBOOK.md`.

## 2026-11-06 Rhino horn_jab at 35, sheet 1 of 3 (se, e)

- Preston: "Yes, run the jab" in this session (first via the Rhino session), for: three draw-only sheets, first pass
  50k-95k, 80k-150k with fixes, cap 40k per sheet, worst 345k. Keep 6 frames and the hit on F2 (JAB_HIT_FRAME).
  The hub kept the slot straight on from the gorilla; jab sheet 1 is the checkpoint.
- Refs: the approved stills only (rhino_l/take-a/views_cam35_touchup); no old-angle jab frames went to Codex.
- Sheet 1: 08:04 to 08:06, **27,796 tokens**. Finished free with `attack_finish.py` (the gorilla script generalised:
  canvas, feet row and seam ink read from the stills; the red lens eye restored from the raw cell's red).
- e: clean. F1 head drops, F2 lunge with the horn +10 px past the still's front, F3 toss with the horn highest, F4 and
  F5 settle. Feet band IoU 0.85-0.91 against the still. se: body facing holds, F2 reaches +20 px, but the head swings
  toward the side on the toss (F3, F4). Not a miss; sheet 3 carries a second se take with a firmer facing line.
- Board `rhino_l/jab35/s1/board_jab_3x.png`, video `s1/rhino_jab_s1_phone.mp4` (the kit's holds 2,2,1,2,1,1 at 2x).
  Sent to Preston and the Rhino session. Jab total: 27,796.

## 2026-11-06 Gorilla strike, sheets 2 and 3, and the five-view set

- Preston: "Yes, run 2 and 3" after seeing sheet 1. The hub held the slot through both.
- Sheet 2 (ne, n): 07:5x to 07:59, **27,103 tokens**. Both rows kept their facing, no eyes. Finish: ne planted foot and
  fist on the still's exact pixels after a 1 px nudge (ne f1-f5 -1 x); n row +1 y. The n punch angles up and to the
  right past the shoulder instead of straight away (Codex's drawing; readable from behind).
- Sheet 3 (s, second take of e): to 08:03, **22,600 tokens**. The new e take matches the still far better (column 1
  IoU 0.979 against the first take's 0.807; hind foot within 1 px), so it replaces the sheet 1 e row; row +1 y.
  s: the right foot stays on the still's pixels (84-122, row 130); the s contact fist reads small, foreshortened
  toward the camera, low in front of the body.
- **Gorilla strike total: 65,993 tokens** (16,290 + 27,103 + 22,600), under the 75k-105k first-pass quote.
- Set: `ape_l/strike35/final/strike/<view>_F0..F4.png` (F2 contact), README, board `final/board_strike_4x.png`, video
  `final/gorilla_strike_phone.mp4`. Waiting on Preston; the Gorilla Session packs only after his yes.
- The rhino jab started straight after (sheet 1 at 08:0x), slot held per the hub.
- Queue, lobster (Lobster session): basic is a melee claw snap (Preston: "Melee claw snap"), 2 m reach, 1.1 s cycle,
  0.1 s wind-up, 0.05 s contact hold; the still lunges 0.25 m for now. Wanted: a 35-degree snap with the BIG claw
  (the small claw is the slot 2 pinch), five views. Stills: lobster_l/take-g/views_cam35 (approved), canvas 192,
  feet row 160. The Lobster session packs lobster_frames.tres via pack_lobster_3d.py; never write into
  art/machines/lobster without telling it. Not priced or asked yet. Queue now: rhino jab (running), then hippo,
  lobster, fennec (falcon blocked on stills); order is Preston's call.

## 2026-11-06 Gorilla strike, sheet 1 of 3 (se, e)

- Preston: "Yes, gorilla strike" (quote: 75k-105k first pass over three sheets, 120k-180k with fixes, cap 40k per
  sheet, worst 345k). The hub gave the slot (the pangolin ended 21:02 the day before). Start 07:2x, end 07:36,
  **16,290 tokens** (draw-only, one image). Slot released while Preston looks; ask the hub again before sheet 2.
- Refs: the approved stills only (ape_l/take-a/views_cam35_touchup se, e at 6x). No pose ref: the ape's kit
  animations are still old-angle drawings, so none were given to Codex.
- Gorilla canvas is 160x160 with feet on row 130 (the packer places it at +16,+30 in the 192 canvas).
- Finish (free, `ape_l/strike35/s1/ape_finish.py`): magenta out; each cell mapped to the still's 15 colours at full
  size, then each output pixel takes its block's most common colour (clean clusters); thin seams inked darkest first
  up to the still's ink share. Scale per row from column 1 against the still (se 0.311, e 0.302).
- Placement lesson: pinning each frame's lowest pixel to row 130 is wrong for attacks. A fist driven toward the camera
  sits below the feet on the page (se contact reaches row 135), and pinning lifted the feet 5 px. Codex kept each
  row's ground line, so each frame keeps its own place relative to column 1. Check: the se far fist sits on the
  still's exact pixels (99-123, bottom 118) in every frame where it shows. The e row is drawn a little more turned
  than the still (column 1 IoU 0.81 against se 0.97), so the whole row moved (-6,-2) to put the hind foot on the
  still's (41-65, bottom 120).
- Gates: facing kept in both rows; ink se 0.102-0.110 against 0.107, e 0.090-0.094 against 0.092; 15 colours,
  palette only; no clipping. Reach at contact: e +8 px past the still's front; se fist out toward the camera.
- Short: the e row's body differs a little from the still, so idle to F0 and F4 back to idle will pop slightly in e.
- Frames: sheet columns 2 to 6 are strike F0 to F4 (files `frames/<view>_f1..f5`), contact F2. Board:
  `s1/board_strike_4x.png`; video `s1/gorilla_strike_s1_phone.mp4` (4 loops at 1.1x, then one at quarter speed).

## 2026-11-05: diag4 (Codex edit of the se rear) started; slot clash

Preston: "Yes, try the edit" (estimate 20k-30k, cap 30k, worst case about 105k). Started without asking the hub
whether the paid slot was free; the pangolin's redraw had held it since 20:30. My miss. The hub told Preston and said
not to stop diag4. Rule added to the playbook: ask the hub before every paid run, even after Preston's yes.
- Result: Codex 20:3x to 20:35, **20,727 tokens**. The near front leg did fold up and the facing held, but the edit
  redrew the whole rhino: the second hind foot is gone (one foot on the ground), an extra yellow underside shape, the
  body sits level instead of tipping up, so it reads as a crouch, not a rear. Not usable (`diag4/compare_3x.png`:
  still, diag1 before, the edit, the approved e rear). Sixth se rear miss.
- Ground pound spend so far: 330,419 tokens. Usable now: e F0-F4 (F5 to redraw from F4), se F2 and ne F2, F3 (free
  finish), plus diag1's se F1, F4, F5 and ne F1, F4, F5 if their scale is matched.
- Asked Preston how to get the se rear; no paid run until he answers and the hub says the slot is free.
- Game feel lane, same evening: Preston wants basic attacks for every mech ("Rhino, gorilla will be melee"). All 13
  mech sessions have been told to message this lane for frames. A short swing with one contact frame held for hitstop.
  Plan: a queue, one priced paid run at a time, each with Preston's yes plus the hub's slot check. The rhino already
  has horn_jab; the gorilla needs strike frames, coordinated with the Gorilla Session.
- Queue, falcon (Falcon session): wing dart basic is built in falcon_kit.gd (range 7 m, cooldown 0.9 s, placeholders).
  It needs a wing-fire set: a 2 to 3 frame wind-up, a contact frame with the wing snapping open, a short recovery,
  alternating right and left wings, kept short. The dart leaves at wing height, about row 100, and the falcon canvas
  has its feet on row 140, not 160. **Blocked** until the falcon has 35-degree stills (a paid Codex redraw, not queued
  yet). Nothing to do until then.
  Falcon session's answer on wings: one set per drawn view, mirrored by the engine. In side and three-quarter views
  the near wing fires; in s and n the right wing. The kit handles left and right with a 0.3 m spawn offset, so that
  needs no art. Per-wing sets are an add-on to price only if Preston wants true alternation.
- Rhino basic attack: the Rhino session plays the old-angle horn_jab and asked which frame is the hit. Measured on
  all five drawn views: F2 is the lunge (the horn furthest forward: side x 153 against 147 at rest, se 151 against 140,
  ne 147 against 137; head lowest). F3 is the toss (the horn highest in every view). Answer sent: JAB_HIT_FRAME 2, so
  the hit lands at 0.20 s at 2x; 3 only if Preston wants the hit on the toss. Strip: D:/dev/_scratch/attack/horn_jab_frames.png.
- Queue, gorilla (Gorilla Session): a strike_<view> basic in 5 views at 35 degrees, contact about 0.2 s, done by about
  0.45 s, reach 2.2 m. Not blocked (stills approved in ape_l/take-a/views_cam35_touchup). Quoted to the Gorilla Session:
  three draw-only sheets (e+se, ne+n, s), cap 40k each; first pass about 75k to 105k tokens, with one or two fixes
  about 120k to 180k; worst case 115k per sheet. Proposed a one-arm forward fist, F0 to F4, contact F2. Frames go to
  attack/ape_l/strike35/; the Gorilla Session packs ape_frames.tres. Next in line if Preston puts basics first.
  Gorilla Session agreed (STRIKE_HIT_FRAME already 2; it packs via tools/art/pack_ape_3d.py, adds "strike" to
  TILT_ANIMS, keeps the feet meta, tells touch-up first) and is quoting Preston 75k-105k / 120k-180k / worst 345k.
  Told it that Preston's yes has to come to this session directly, not relayed.
- Queue, hippo (Hippo session, heads-up only): the basic is a melee bite (Preston: "Melee bite"), in hippo_kit.gd,
  playing on the idle for now with a 0.05 s contact hold and a hit spark. Wanted later: a short jaw snap, about a
  0.1 s wind-up then contact; the Hippo session wires a contact-frame constant. Not blocked: the final 35-degree
  stills are hippo_l/take-b/views_cam35_touchup_shade1 (it supersedes views_cam35_touchup). Not priced or asked yet.
- Queue, fennec (Fennec session): its ranged dart basic works on a cast stand-in (cast F2, then CAST_FRAME 4) and reads
  OK. It offered a dedicated `basic`: 3 to 4 frames, a quick ear-flash flick (wind 1, release 1, recover 1 to 2),
  5 views, canvas 192 with feet row 161, the dart keyed on the release frame. Answer: worth drawing, third in the
  queue after the gorilla and hippo; rough price two draw-only sheets, 50k-70k first pass, 80k-120k with fixes,
  worst 230k. Hands off fennec death35 se_f0-6 (touch-up candidate waiting on Preston).

## 2026-11-05: free finish of the good diag2 cells; se rear retry (23,442 tokens) turns side-on again

Preston: "Yes, do that" (finish the good cells free, retry only the se rear: estimate 25k-35k, cap 35k).
**Free finish** (`rhino_l/gp35/diag2_fin/`; Codex fix1's finish.py run by the attack lane, one copy per row in
`diag2_fin_se/`, `diag2_fin_ne/`; placement and checks `D:/dev/_scratch/attack/diag2_place.py`):
- Scale per row from column 1 (standing) against the still: se 0.284 (86x83 against 85x83), ne 0.325 (height
  matched; the ne stand is 20% wider, a slight turn, and is not used).
- se F2 (rise): hind sole on row 143 after one whole-frame move (0, -2); eye 5 px; ink 8.95% against 7.79% (just
  over 15%); 1 piece; specks 364 (limit 497); palette clean.
- ne F2, F3: hind soles on 160 and 150 (1 px or under); no eye; ne F3's top 26 px over the still, the same as the
  approved e rear; ink 6.6% and 6.9% against 8.25% (under the 15% band: seams thinner, for the finish pass); 1 piece;
  specks under the limit.
- Board `diag2_fin/board_4x.png`.
**se rear retry** (`diag3/`, draw-only, se only, 1 row by 3, the se still and the side pose ref, a harder facing line,
"the near hind leg ... never a dark block"): Codex 20:25 to 20:27, **23,442 tokens**. Rise and rear turned side-on
again (preview `diag3/preview_3x.png`). Fifth se rear miss.
- All se rears side by side: `diag3/se_rear_candidates_3x.png`. Only diag1's keeps the se facing (chest to the
  viewer, head lower right); its fault is the near front leg left planted, and a low rear.
- Ground pound spend so far: 309,692 tokens.
- Proposed (waiting on Preston): a Codex EDIT of diag1's se rear (attach that frame, change only the near front leg,
  folded up, and lift the chest a little; keep the facing), draw-only, estimate 20k-30k, cap 30k, worst about 105k.

## 2026-11-05: diag2 draw-only with the pose ref (31,831 tokens): ne works, se rear still turns

Preston: "Try with pose ref" (estimate 25k-40k, cap 40k, worst case about 115k). Codex ran 20:18 to 20:22, exit 0,
**31,831 tokens**. One image, 2 rows (se, ne) by 3 (stand, rise, rear), attaching the se/ne stills and
`diag2/refs/pose_side.png` (the e still and the approved e F2 and F3, labelled pose only). New prompt line: in the rise
and rear exactly two feet touch the ground, both front legs folded under the chest. No finishing.
- Free preview (`diag2/preview_3x.png`, `preview_1x.png`; script `D:/dev/_scratch/attack/diag2_preview.py`: magenta out,
  column 1 height matched to the still, nearest palette snap; not the finishing).
- ne rise and rear: right for the first time on a diagonal. Back to the camera, no eye, hips at standing height,
  short hind legs, no thigh, the body tips away. The far folded foreleg is hidden or missing. ne stand is wider than
  the still (turned a little toward the side), which matters only if its stand is used.
- se rise: keeps the lower-right facing, front just off the ground.
- se rear: drifts side-on again and the near hind leg has an odd dark block at the joint. Not usable.
- Ground pound spend so far: 286,250 tokens.

## 2026-11-05: diag1 result (85,656 tokens): the diagonal rear fails again

Preston: "Yes, start it" (diag1, cap 100k). Codex ran 20:02 to 20:10, exit 0, **85,656 tokens** (estimate 70k-100k).
One image, 2 rows (se, ne) by 6, the two diagonal stills only, each row finished at its own head scale.
- **F3 fails in both views** (5x: `rhino_l/gp35/diag1/legs_5x.png`): se F3 brings the near front leg down as a third
  planted leg and turns toward the viewer and side; ne F3 stacks extra joint discs and a thigh block under the rump
  (11 rows of charcoal above the disc against the still's 2).
- se F2 barely rises (front 5 px up against e's approved 15). ne F2 rises 4 px from its own sole.
- Both rows come out 7-12% smaller than the still in body size at the head scale (se 79x74 against 85x83, ne 78x90
  against 83x103), so F0 to F1 would shrink visibly.
- F4 against F5 9.5 and 11.4 px (limit 3), the same split-pose problem as run 1.
- Passes: F0, eyes (se 5 every frame, ne none), ink, palette, pieces, specks, F3 IoU.
- Frames worth keeping if the rear gets solved: se F1, F4, F5 and ne F1, F2, F4, F5 read correctly at 1x and keep
  their facing.
- Ground pound spend so far: 106,953 + 61,810 + 85,656 = 254,419 tokens; finished: the e view.
- The pattern: three Codex runs drew the diagonal rear wrong three different ways (run 1 ne turned with thighs, fix1 se
  turned, diag1 extra leg and stacked joints). Wording alone does not fix it. Asked Preston how to go on.
- Board `diag1/review.png`, `diag1/strip_1x.png`, video `diag1/ground_pound_diag1_phone.mp4`.

## 2026-11-05: e rear approved

Preston, asked "Does the new side-view rear look right?": "Yes, looks right". Approved: e F2 and F3 from
`rhino_l/gp35/fix1_e/frames/` (note `fix1_e/APPROVED_e_rear.txt`). The approved rear: hips at standing height, the
body tips like a seesaw on the hips, front feet 15 px up at F2 and 35 px at F3, the sprite top about 15 px over the
still. That is the height for every view. e F5 still has to be drawn from F4. Nothing packed.
- Prepared `rhino_l/gp35/diag1/` (free): one Codex image, 2 rows (se, ne) by 6 frames, the se and ne stills only.
  Wording: run 1's columns, fix1's rise and rear lines and hind-leg rule (the approved wording), plus "THE FACING
  NEVER CHANGES" for both diagonals. Finish per row at its own head scale; new gates for facing (head size, eye, box
  ratio) and rear height against the approved e frames. Estimate 70k-100k, cap 100k, worst case about 175k. Waiting
  on Preston. Run 2 (s, n) and the F5 pass come after.

## 2026-11-05: fix1 result (61,810 tokens): thighs gone; e good, se turned

Preston: "Yes, start it" (fix1, cap 75k). Codex fix1 ran 19:13 to 19:19, exit 0, **61,810 tokens** (estimate 45k-75k).
One image (2 rows e, se by 3 columns), only the two stills attached, no redo.
- **Thighs gone** in both views (5x: `rhino_l/gp35/fix1_e/legs_5x.png`): the joint disc sits right under the body
  again. Hips at the still's height (e 134/133 against 134; se 117/116 against 117). Hind feet drift 0 px.
- **e was drawn about 9% small** against se (head -8.9% e, +10.8% se in column 1), so the one median shrink fitted
  neither. Re-finished the e row free at its own head scale (`rhino_l/gp35/fix1_e/`: fix1's own scripts, factor
  0.2711 instead of 0.2470, foot boxes rescaled; no new drawing). e heads now -2.1% (F2), +2.7% (F3); size 101x72
  against 103x75. Ink, eye, palette, pieces, specks, seams all pass. fix1_e's leg-length lines are not valid: the
  audit's disc rows are fixed numbers from the old scale; the 5x look is the check.
- **e front feet** still go 15 px (F2) and 35 px (F3) up: the body now tips like a seesaw on the hips, so the height
  comes from the tilt, not from legs. The sprite's top is about 15 px over the still's, against 22 px in run 1.
- **se turned toward the side view** in F2 and F3 (Codex's own look says the same), so its head is 10-11% big
  against the still. Not usable; needs another draw. Second time a diagonal view drifted toward the side view (run 1's ne).
- Board `fix1/review.png`; e set at 1x `fix1_e/e_compare_1x.png` (new on top, run 1 below); phone video
  `fix1_e/ground_pound_e_fix1_phone.mp4`.
- Next: Preston looks at the new e rear. Then the se and ne redraw and run 2 (s, n), priced first.
- Gorilla session (local_a78f516e-924c-4b93-8ae4-a6c4882a60a1) asked for a per-ability cost for its 35 redraws (its
  moves are tilted as a stopgap; pop 19-23%). Told it the method is not proven yet: 168,763 tokens so far for one
  finished view; rough projection 250k-350k per ability in 5 views; real numbers after the rhino passes. Keep
  ape_frames.tres tilt_anims and feet meta if ever packed.

## 2026-11-05: F3 too high, the fix prepared (free so far)

Preston on run 1: "F3 ares too high, its like they added another segment to the knees making it higher. fix", then
"not to the knee joints but they added thighs essentially". Confirmed at 5x (`D:/dev/_scratch/attack/f3_legs.png`):
a charcoal thigh between the body and the hind joint disc. Top of the hind-leg band against the still: e F2 4 px
higher, F3 20 px; se F2 15 px, F3 28 px.
- Prepared `rhino_l/gp35/fix1/`: one Codex image, 2 rows (e, se) by 3 columns (standing, rise, rear) from the two
  stills only (no pose guide, no run 1 frame attached). Run 1's wording plus a hind-leg rule (disc against the body,
  no thigh, hips at standing height, seesaw at the hips, front feet no higher than a hind leg is tall). New gates: leg
  length, disc-to-body gap, hip height. Estimate 45k-75k, cap 75k, worst case about 150k. Waiting on Preston's yes.
- Walk lane (2026-11-05): extra fill needs a number gate; the seams check finds holes only. Added to the playbook.
- Hub (2026-11-05): one session per mech now does overall refinement; attack animations stay with this lane. The rhino
  session (local_0d636c38-8177-4132-8862-4c9253c141e6) owns the rhino and rhino_kit.gd; sent it run 1, the fix, run 2
  and the timing change (slam 0.7 s to 0.5 s). Roster: admiring-bell worktree docs/team/mech-sessions-2026-11-05.md.
- Rhino session's answer: the kit waits on POUND_SLAM_FRAME (line 171), so holds 1,1,1,2,3,3 are safe; the 0.12 s rise
  flash and hitstop are fixed times; impact.emit(0.7) is shake strength. Pack by adding "ground_pound" to TILT_ANIMS in
  pack_rhino_3d.py, not the .tres. Both prices are in rhino_l/MECH_STATUS.md as slice C, waiting on Preston.
- Game feel: the rock pop goes to the rhino session, not game feel (it has told the rhino session the plan). Game
  feel keeps the shared code. Playbook section 1 routing updated.

## 2026-11-05: ground pound run 1 result (106,953 tokens)

Codex run 1 ended 18:00, exit 0, **106,953 tokens** (cap 110,000; estimate 60k-100k). One image call, no redo, no old
frame opened. Board `rhino_l/gp35/run1/review.png` (still in column 1), game size `strip_1x.png`, phone video
`rhino_l/gp35/run1/ground_pound_run1_phone.mp4` (e, se, ne stacked at 4x; holds 1, 1, 1, 2, 3, 3, then 4 tremor
stomps of F5 0.12 s; approximate game timing).

**By view** (my look at 1x and 4x; Codex's own look agrees):
- e: a clear rear and slam. Hind feet hold (1 px or under). F3 rears far higher than the plan: front feet 34 px up
  against the 16 px target, closer to 45 degrees than 30. It reads stronger at 1x. F4 lands 3.5 px off the still soles.
- se: the rear reads; hind feet hold. Front feet 23-34 px up at F3 (target 16). Head 5.7% over the still (limit 3%).
  F2 and F3: the far front foot meets the jaw, which can read as a second chin.
- ne: fails. From F1 the body turns toward the side view (face showing, rump not to the camera), 87 px tall against
  the still's 103, hind feet drift 4 px. Not usable.

**Gates.** Pass: F0 equals the still (0 px), eyes in every frame (e, se 5 px; ne 0 like its still), ink share
7.3-9.2% against 7.8-8.3%, palette, binary alpha, one piece, specks under the limit, no seam slits, F3 telegraph IoU
e 0.40, se 0.36. Miss: front lift sizes (all views), F4 against F5 (e 7.1, se 7.8, ne 13.0 px; limit 3), F5 against
the still (7.8 to 15.8 px), head size se and ne, ne size and hind feet.
- F4 and F5 came out as two separate poses, so the tremor's F5 flash would jump 7-8 px. F5 has to be drawn from F4.
- The lowest-row gate does not fit se (near hind sole on row 143). Rewritten as "every planted sole on its still row".
- Lessons added to the playbook, section 5.

**Proposed next (waiting on Preston, nothing started):** run 2 = s, n and a new ne in one sheet, run 1's column wording
word for word, plus a line for the back views ("the rump faces the camera, the face is hidden"). Then one finish pass
that draws F5 from F4 in every view and fixes the se jaw join and head scale. Run 2 price: about 105k like run 1,
cap 110k, worst case about 185k. The rear height (16 px planned, 34 px drawn) is Preston's call.

## 2026-11-05: rhino ground pound at 35, prep (free) and Codex run 1

Preston: "Yes, start it" (free prep, then run 1 capped at 110k).

**Feet labelled** at 4x (`D:\dev\_scratch\attack\label_feet.png`): e near hind 53-72 and near front 93-112 on row 160
(40 texels apart, matching the packer's feet: front +7, rear -33, half width 20); far legs hidden in e. se near front
79-98 r160, near hind 60-70 r143, far front under the jaw 113-133 r155. ne near hind 83-95 r160, far hind 60-70 r150,
near front 109-122 r139. s and n: the near pair on row 160 (s 64-83 and 107-126; n 64-85 and 107-128); 88-102 r153
in s is the steel jaw, 88-104 r141 in n is the tail plate gap.

**Prep** (`attack/tools/gp35_prep.py`, output `attack/rhino_l/gp35/prep/`): `targets.json` (hip pivot 34 texels up,
pitch 0/0/15/30/0/0, front feet shift F2 e (-1.4, -8.5), se (-1.0, -9.0), ne (-1.0, -7.9); F3 e (-5.4, -16.4),
se (-3.8, -18.6), ne (-3.8, -14.2)), `still_metrics.json` (ink share e 8.1%, se 7.8%, ne 8.3%; eye px 5, 5, 0; one
4-connected piece; specks 322, 414, 346), guide strips, `refs/look_35.png`, `refs/pose_guide.png` (flat silhouettes,
holes closed, loose bits under 40 px dropped) and `blocking.gif` (labelled "blocking, not the art").
- Look: e reads as a rear-up on planted hind feet; se and ne read mostly as the body getting taller, which is what
  the camera shows. The rough rotation left holes and loose bits; fixed for the pose guide only.
- The whole-sprite speck count of a finished still is in the hundreds (pixel detail), so the speck gate is 1.2 times
  the still's count, not "the still plus 2" (that walk gate was for leg rows).

**Run 1** (`attack/rhino_l/gp35/run1/`, brief.txt, prompt-sheet.txt, RUN.txt): one image of 3 rows (e, se, ne) by 6
frames from the touch-up stills and the pose guide only (no old frame may be opened), finished by head scale, hind
feet placed on the still's soles by whole-frame moves only, f0 replaced by the still, checks, sel-out board, 1x strip,
joint zooms, previews. Cap 110,000, estimate 60k-100k. Started 2026-11-05 17:48.
- Hub, after the start: a capped run can overshoot by about 75k, so run 1's worst case is about 185k. Told Preston;
  playbook and plan now quote cap plus 75k.
- Preston, after seeing the blocking GIF: "do it like how we made the other attack animations not the way you do
  with walking animations". Run 1 is already a Codex image sheet drawing new poses; asked, he chose "Let run 1
  finish". From here: sheet 2 (s, n) reuses run 1's column wording word for word, with no pixel-moved blocking or
  pose silhouettes, and the frames get the attack finishing order. Playbook section 1 and step 6 updated.

## 2026-11-05: lane started, playbook written, pilot waiting on the lanes (all free)

Preston: "make a session for attack animation". The old animation lane session was deleted; its files are on disk.

**Read:** the animation playbook, the walk playbook and the kits (all three in full), the ground pound's clean
report and the forge run log, both rhino APPROVED notes, the walk lane's token lines, the packer's KIT lines and
`rhino_kit.gd`'s slam frame. Wrote `ATTACK_PLAYBOOK.md`.

**Current rhino stills:** `rhino_l/take-a/views_cam35_touchup/` (touch-up lane, 2026-11-05: "is current ... nothing
newer and no rhino touch-up in progress"). Measured (scratch: `D:\dev\_scratch\attack\measure_rhino.py`):
| View | Bounding box (x0, y0, x1, y1) | Size | Colours |
|---|---|---|---|
| s | 62, 77, 128, 160 | 67x84 | 11 |
| se | 54, 78, 138, 160 | 85x83 | 11 |
| e | 44, 86, 146, 160 | 103x75 | 11 |
| ne | 54, 58, 136, 160 | 83x103 | 10 |
| n | 64, 55, 128, 160 | 65x106 | 10 |
- The touch-up differs from `views_cam35` by 671 to 760 px per view (colour only; alpha identical per its APPROVED).
- The installed 35 idle (`cam35-idle/frames`) equals the touch-up stills on f0 (se and ne checked: 0 px differ).
- Sole segments on the stills (`walk_tools.py soles`), not yet labelled front or hind: s 64-83 r160, 88-102 r153,
  107-126 r160; se 60-70 r143, 79-98 r160, 101-107 r142, 113-133 r155; e 53-72 r160, 76-91 r141, 93-112 r160,
  128-136 r137 (may be the jaw); ne 60-70 r150, 83-95 r160, 109-122 r139; n 64-85 r160, 88-104 r141, 107-128 r160.
  The animation playbook warns that a gap search mistook horn, jaw and tail for legs: label at 6x by eye first.

**In the game today:** the ground pound is old-angle frames (`codex-ground-pound/clean` front, side, back;
`codex-set-c/ground-pound` se, ne), 6 frames held 1, 2, 1, 3, 3, 3 ticks of 100 ms, slam on frame 4 at 0.7 s. The
old frames were measured once for history; per Preston ("You are using old map old animations not at 35 degree
look") none of their numbers go into the 35 plan.

**Asked (Preston: "communicate with other sessions", "Game feel is the one that lots of moba knowledge too"):**
- the animation lane fork: what is current at 35, any 35 attack work started, the current map, lessons since the
  playbook;
- the walk lane: final walks and their packed folders, lessons for a planted rear-and-slam, its test map;
- game feel: the current map, what still plays old-angle frames, the ground pound's key frames and holds, the
  telegraph length, the ring effect;
- the hub: one-line status, the current map.

**Hub's answer (2026-11-05):** map `scenes/moba3d/arena_play.tscn` (instances `arena_blockout.tscn`); old scenes not
to use: field_test, ape_field_test, rhino_walk_test, the `*_reveal` scenes. At 35 in the game = each machine's
`metadata/tilt_anims` (`art/machines/<m>/<m>_frames.tres`): rhino idle and walk only, so all five rhino moves
(ground_pound, horn_jab, horn_toss, stampede, brace with brace_shuffle) are old-angle and this lane's to redraw;
gorilla bound, chest_beat, hex_dome, hex_shield likewise; fennec moves held for the kit redraft. Deaths and hits have
no owner. Headless runs: `--check-only` first and a timeout (a parse error hung match_check 33 minutes today).
Playbook updated with all of it.

**Walk lane's answer:** rearing is a new pose, so the key frames need a redraw route (Preston rejected
cut-and-reposition on the fennec death ears); scale by the head; a draw order per view; number gates; REPORT after
each part; a feet-planted attack must not move the machine. The rhino walk in the game was drawn from `views_cam35`,
not the touch-up.

**Game feel's answer:** keep 6 frames, slam on F4; F5 a small lift close to F4 (the tremor toggles F5 for 0.12 s, then
F4, 4 stomps 0.4 s apart: checked in `rhino_kit.gd`, Preston's change today); wind-up about 0.5 s (F0 x1, F1 x1,
F2 x1, F3 x2); `gp_ring` stays; new ask: a rock pop effect, 4-6 frames, about 1 m, bottom-centre anchor; optional
cracks for an 8 m circle. Tests: arena_play is the match, field_test the simple one-kit scene.

**Animation lane fork's answer:** live rhino set = touch-up stills, `cam35-idle/frames_selout`,
`walk35/walk/frames_selout`; `walk35_touchup/frames` exists but is not packed. No 35 attack work was started.
`kit-anims-35-plan.md` says rhino kit moves wait for a rhino kit redo; asked Preston. Playbook section 12 added there.

**Plan written:** `rhino_l/PLAN.md` (frame table, screen targets, route, draw orders, gates, effects, price).
Playbook updated with every lesson above.

**Next (superseded by the plan):** the plan for the rhino ground pound at 35 (frame table, targets, guides, a blocking previz), from the lanes'
answers, then the Codex price for Preston. Playbook estimate: 150k to 225k tokens over two runs, plus 45k to 80k only
if a repair pass is needed. Nothing paid has run.

## 2026-11-06 Rhino horn_jab, sheets 2 and 3, and the five-view set
- Sheet 2 (ne, n): 22,730 tokens. Column 1 fits 0.955 and 0.964. Both jabs read; n is subtle because the horn goes away from the camera.
- Sheet 3 (s, second take of se): 27,873 tokens. s fits 0.998; its horn reaches rows 161-172 on F1-F4, below the feet row, toward the camera (kept).
  The se second take holds its facing on the toss (s1's head turned side-on), so it replaces s1's se. Its reach is shorter: F2 to x 146 against s1's 158.
- Jab total: 27,796 + 22,730 + 27,873 = 78,399 against the 345k worst case. Hub told.
- Final: rhino_l/jab35/final/ (jab/<view>_F0..F5, README, board_jab_3x.png, rhino_jab_phone.mp4). Not packed; Preston liked the jab ("Also rhino jab works"). Packing waits for his yes on this set.
- Timing check against the kits: the jab runs 0.45 s inside the rhino's basic_cooldown 0.9; the gorilla strike runs about 0.45 s inside the ape's 1.0. A held attack won't cut either off.

## 2026-11-06 Gorilla strike: mirror and alternation
- Preston: "Can you mirror the gorilla animation so the other first punches too. The melee attack will be like mobas where holding basic attack keeps attacking. Give it moba feel, Then i want it to bunch with both hands one at a time".
- s and n mirror cleanly (shift -1 x): final/strike_b/s_F0..F4 and n_F0..F4. About 13-16% of pixels change shading side, because the light now comes from the other side.
- se, e and ne cannot be mirrored: a mirror turns them into sw, w and nw. A left-fist set for them needs a drawn far-arm punch (2 draw-only sheets, priced and asked).
- Demo: final/gorilla_strike_alternating_phone.mp4 (s and n, right then left).
- Game feel: hold-to-attack is already in for every machine (arena_play._process plus director attack_cd). Alternating strike and strike_b is the Gorilla kit's side.

## 2026-11-06 Rhino horn_jab packed (35 degrees, five views)
- Preston: "Yes, pack it" (in the Rhino session, shown jab35/final/board_jab_3x.png and rhino_jab_phone.mp4, with the 78,399 total and the s F2 tip at row 172).
- Backup first: jab35/backup_pre_pack/ (pack_rhino_3d.py, rhino_frames.tres, rhino_kit_sheet.png, rhino_sheet.png). Walk lane told before the edit and after.
- Sel-out: jab35/final/frames_selout/{front,se,side,ne,back}_f0..f5 via selout_rhino.selout.
- tools/art/pack_rhino_3d.py: JAB35 path; KIT and DIAG horn_jab point to it; "horn_jab" added to TILT_ANIMS. Holds unchanged. Ran pack() only.
- Compared against the backup: the tres changed one line (tilt_anims); the kit sheet changed only rows 5-9 (horn_jab); the walk sheet changed 0 px.
- Slip, fixed: my edit first wrote the packer with CRLF endings; restored LF before handing back. Write repo files as bytes, or with newline='\n'.
- Next is the Rhino session's: import, rhino3d_check, rhino_basic_check, match_check, and the camera lane's floor check on the s horn tip. Nothing committed.
- Gorilla left-fist set: Preston "Yes, run it". Hub queue: chameleon redraw, then the lobster walk run 1, then this. Sheet 1 prompt ready in ape_l/strike35/left_s1.

## 2026-11-06 Gorilla strike feel: measured, test sheet proposed
- Preston via game feel: "It just feels like it extends its arm forward and you cant really feel when you are using it". The code side (lunge, shove, spark, camera kick) is in.
- Measured against the stills, contact F2 reaches: e +6 px past the still's front (body 78 px), se +0 across and +5 down, s inside the still, ne +5, n 8 px up.
  The knuckle stance already has the fist forward on the ground, so the punch ends where the arm started. F1 is a wind-up, but mild (fist beside the head).
- Free: holds proposal F0 0.5, F1 1.5, F2 1, F3 1, F4 1 ticks at 1.1x (contact 0.18 s, end 0.45 s) sent to the Gorilla session.
- Proposed to Preston: a one-sheet test (se, e) with a deep wind-up (fist behind the shoulder, chest twisted away) and a locked-straight contact
  about a quarter of a body length past the still, clear of the ground. Cap 40k, worst 115k. The left-fist set is on hold so the left fist isn't drawn in the soft poses.

## 2026-11-06 Ground pound "diag1" request relayed by the Rhino session: not run
- The Rhino session relayed Preston's "Yes, run it" to "Run the ground pound diagonals next (70k to 100k, worst case about 175k)?", citing PLAN.md's diag1.
- diag1 already ran on 2026-11-05 (85,656 tokens, F3 failed in both views). diag2, diag3 and diag4 followed. The se rear has missed six times; the ground pound has spent 330,419 tokens.
- Not started: rerunning diag1 as written repeats a known miss, and a relayed yes is not this lane's approval. Told the Rhino session and put the state to Preston here.
- Preston (via the Rhino session): "Leave it" on the jab's s F2 horn clip. No touch.
- Preston, here: "Yes, after the test". A fresh plan for the ground pound se rear comes after the gorilla snap-punch test. Free to write; any paid run in it gets priced and asked here first.

## 2026-11-06 Gorilla snap-punch test (se, e): 21,962 tokens
- Preston: "Yes, test first" (cap 40k, worst 115k). The hub gave the slot at 09:02; Codex ran 09:05 to 09:08, 21,962 tokens. Slot handed back while he looks.
- Measured against the stills:
  - Contact reach: e +20 px past the still's front (old +6; the target was about 20). se +3 px across, with the fist up at chest height at the lower right (old: on the ground, +5 px down).
  - Wind-up: the fist goes behind the back edge, 7 px (se) and 9 px (e). Before, it sat beside the head.
  - Hind feet planted (lowest rows match the still within 1-2 px). The lowest row drops to 120-121 in F1-F4 only because the near fist leaves the ground.
- Codex's own look: e wind-up "turns toward viewer" (the twist asked for); se wind-up eyes enlarged; the far fist hidden behind the body at contact (three contacts unconfirmed).
- Ink 0.082-0.110 against the stills' 0.092-0.105; 15 colours.
- Board snap_s1/board_4x.png, comparison snap_s1/old_vs_snap_2x.png, video snap_s1/gorilla_snap_test_phone.mp4.
- Proposed for the rest (waiting on Preston):
  - right fist ne+n, and s with a second se take;
  - left fist se+e, and ne plus a spare;
  - 4 sheets, likely 80k-110k, cap 40k each, worst 460k, with a checkpoint after each sheet.

## 2026-11-06 Gorilla snap strike, sheet A of 4 (right fist ne, n): 25,940 tokens, partial miss
- Preston: "Yes, draw the rest" (4 sheets, likely 80k-110k, cap 40k each, worst 460k). The hub held the slot across A-D; Codex ran 09:12 to 09:15.
- ne: contact reach +16 px past the still (old +5), the arm straight out to the upper right. Wind-up FAILS: the fist is raised at the shoulder, not pulled back (Codex's own look agrees).
- n: contact goes up and to the right, 6 px above the still (old: 8 px). No stronger than the old one. Wind-up fails the same way.
- Feet planted (lowest row 130 in every frame; n band IoU 0.90-0.96). Ink 0.084-0.092; 14-15 colours.
- Stopped per the hub's condition and asked Preston. Proposal: go on with B (s, se second take) and C (left fist se, e), and retry n in sheet D's spare row with new wording.
  The back-view punch goes away from the camera, so it reads as the arm rising, like the rhino's n jab.
- Board snapA/old_vs_snap_2x.png, video snapA/gorilla_snapA_phone.mp4. Slot free while he looks.

## 2026-11-09 Lane stopped: 2D sprites scrapped
- The hub relayed Preston's decision, in his words: "2D sprites are scrapped btw". Machines are now 3D models, rigged and animated; the gorilla-3d and rhino-3d sessions lead.
- Dropped: gorilla snap sheets B, C and D (prompts written in ape_l/strike35/snapB, snapC; never run). The left-fist set and the ground pound se-rear plan are dropped too.
- Nothing was mid-flight: no paid run, no half-written shared file. Sheet A ended 2026-11-06 09:15.
- Spend on record:
  - rhino jab 78,399 (packed into the sprite pack 2026-11-06);
  - gorilla strike sheets s1-s3 (see the strike entries);
  - snap test 21,962;
  - snap sheet A 25,940;
  - ground pound 330,419.
- Left in place: the jab35 change in tools/art/pack_rhino_3d.py (backup in rhino_l/jab35/backup_pre_pack/) and all attack folders. Nothing deleted; nothing committed.
