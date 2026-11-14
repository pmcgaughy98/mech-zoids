# Walk lane log

The method and rules are in `WALK_PLAYBOOK.md`. Newest entry first.

## 2026-11-09: sprite walks stopped
- Preston, via the hub: "2D sprites are scrapped btw". Machines are 3D now. Walk lane stopped: the lobster touch-up fix cancelled with the touch-up lane (no frames had been written to touchup/lobster_l_walk), lobster run 2 and the wolf runs dropped. No paid run was in flight; the codex.exe processes running today are the Codex desktop app, not this lane. Packed walks (rhino, hippo, gorilla, fennec, minion) stay as they are until the 3D models replace them.

## 2026-11-06: lobster run 1 sent to touch-up (free)
- Preston: "Touch up free". Handed to the touch-up lane: se R3 and ne R1 shredded legs, plus his note "on the back view ne view you have the left legs dont move": the far left legs (red feet peeking at the body's left edge) get the tripod motion. Labels walk/lobster_l/feet_far_ne.json, targets plan_far_ne/targets.json. Output expected in touchup/lobster_l_walk/frames.
- Brief lesson for run 2: far legs that peek out move too, with their own labels; partly hidden legs move whole.

## 2026-11-06: lobster run 1 done, 170,761 tokens
- Started 08:27 on the hub's slot, stopped by the watcher at the 170k cap at 09:02 (worst case quoted 245k). 24 frames delivered.
- Review (lobster_l/run1/REVIEW.txt): e good; se R3 and ne R1 shredded (partly hidden legs broken into shards). Checks pass otherwise. My brief's "no foot below its still row" contradicted the targets; drop it from run 2.
- Lesson for briefs: a leg partly hidden behind another leg or a claw still gets moved whole as the still's pixels; say so, and gate it (whole leg pixel count per frame within a few px of the still's).

## 2026-11-06: lobster run 1 approved, queued for the paid slot
- Preston: "Lobster run 1". Cap 170k, worst about 245k. Queued with the hub after the rhino jab sheet 3 (running) and the chameleon redraw. Starts only on the hub's word. Command in walk/lobster_l/run1/RUN.txt.

## 2026-11-06: lobster walk, free prep done (nothing launched)
- Preston: "Tripod, 3 legs at once". walk_tools gait tripod6 added (A = L1 R2 L3 planted f0-f3, B = R1 L2 R3; lifts 2,3,3,2; dips f0 f4; shift +0.5); hippo and wolf targets rebuild unchanged; mirror +4 passes. Backup of the old script: session scratchpad walk_tools_pre_tripod.py.
- walk/lobster_l: feet.json (near legs only; s front pair, n rear pair), plan_walk (P 3, 8 fps, 0.48 m/s), run1 brief (e, se, ne; cap 170k), run2 draft (s, n; cap 110k). Likely 250k-320k, worst about 430k. Waiting on Preston's yes; frames go to the Lobster session to pack.

## 2026-11-06: walk queue audited (QUEUE.md)
- Preston: "Start working on walk animations for mechs and angles that dont have one or need fixed".
- Real 35 walks in game: rhino, hippo, gorilla, fennec (and the minion). Stand-ins that glide: lobster, kangaroo. Wolf prep ready, paid run parked. No approved 35 stills yet: pangolin, shoebill, falcon, squirrel, chameleon. Hummingbird hovers.
- Proposed order: wolf run 1 (ready), lobster (stills approved today; tripod gait proposal), kangaroo (hop call first). Nothing paid started.

## 2026-11-05: rhino s and n walk rebuild packed (all five views now the rebuild)
- Preston, via the Rhino session: "Yes, pack it" (shown review/walk_sn_rebuild_2026-11-05.png and the s and n GIFs).
- Checks before packing: footlock ALL FEET LOCKED (s RF, LF and n LH, RH spreads 0.00 x, 0.88 y; max off target 0.50 px), one piece every frame, 0 off-palette against views_cam35_touchup, binary alpha, lowest rows 160-163.
- walk35_touchup/selout_rebuild.py now writes s and n as front and back too; pack_rhino_3d.py WALK_BY_VIEW points all five views at walk35_touchup/frames_selout. Ran pack() only.
- Against the backup: rows front 1,413 px and back 2,250 px changed; se, side, ne and the idle stills 0; rhino_frames.tres, the kit sheet and both .import files byte-identical. TILT_ANIMS and FEET untouched. Godot not run (the Rhino session does that).
- Backup: rhino_l/take-a/anim/walk35_touchup/backup_pre_pack_sn (art_machines_rhino/*, pack_rhino_3d.py, selout_rebuild.py, README with restore steps).

## 2026-11-05: hippo walk packed into the game
- Preston, in the Hippo session: "Approve, pack it" (touch-up's cleaned walk with 1 px sway).
- Copied touchup/hippo_l_walk/frames to hippo_l/take-b/anim/walk35/frames (APPROVED.txt); sel-out by walk35/selout_walk.py with the idle's outline (#141218, darkest of views_cam35_touchup_shade1).
- tools/art/pack_hippo_3d.py now packs walk_<view> for s, se, e, ne, n: 8 frames, speed 8, looping, sheet rows 5-9 (sheet 1536x1920); tilt_anims ["idle", "walk"]; sel-out checked against a fresh one. FEET unchanged.
- Checked: idle rows and the five idle animations byte-identical to before; walk rows equal frames_selout; 65 frames in hippo_frames.tres. Godot not run (the Hippo session does that; the sheet .import reimports on the next Godot run).
- Backup: hippo_l/take-b/anim/walk35/backup_pre_pack (art_machines_hippo/*, pack_hippo_3d.py, README with restore steps). The kit still needs full_speed_walk_rate = walk_speed / 0.48.

## 2026-11-05: hummingbird out of the walk queue
- Preston took hover for hummingbird_s (via the Hummingbird session): it flies low all the time and never walks. No walk cycle; playbook section 3 row updated. Kit: docs/plan/moba-kits.md.

## 2026-11-05: wolf 35 trot parked
- Preston said "Not now" to the paid run (via the Wolf session). The prep in walk/wolf_m stays as it is; README marked PARKED. Launch only on his own yes, relayed in his words.

## 2026-11-05: wolf 35 trot, free prep done (nothing launched)
- Preston, via the Wolf session: "Free prep only". No Codex run, no spend.
- walk/wolf_m/feet.json: labels from views_cam35_touchup (RF/LF in s; all four in se, e, ne; LH/RH in n at row 151). The tail tip, not a foot, is the lowest point in ne and n.
- walk_tools.py: new gait trot4 (RF+LH start 4, LF+RH start 0, lifts 2,4,4,2, dips f1 f5, shift +0.5). foot_path now takes any swing length; the hippo targets rebuild byte-identical and the mirror +4 check still passes. Backup of the old script: session scratchpad walk_tools_pre_trot4.py.
- plan_walk: P 5 at 10 fps = the old approved side table exactly, 0.9 m/s drawn, stride 40 side px (0.72 m) per 0.8 s cycle. WolfKit STRIDE 0.9 sent to the Wolf session.
- run1/brief.txt (e, se, ne; cap 150k) ready; run2/brief.txt is a draft to finish from run 1. Both folders hold stills, targets and guides. Waiting on Preston's own yes.

## 2026-11-05: wolf 35 walk quoted (price only, nothing started)
- Asked by the Wolf session (Preston: "Yes, ask them"). Quote: run 1 e, se, ne cap 150k; run 2 s, n cap 110k; likely 230k-270k; worst case about 410k (each cap plus one step of about 75k).
- Stills: wolf_m/take-b/views_cam35_touchup (APPROVED, "Keep it", recolour of views_cam35 with identical alpha), not views_cam35. Asked the Wolf session to check idle35 was built from the touch-up set.
- Gait: keep the approved old-angle trot (pair A planted f0-f3, pair B f4-f7, lifts 2, 4, 4, 2, 10 fps; playbook section 3) and the tail rule (common.txt: straight plates, moved whole). Needs a new walk_tools gait entry (free). Reuse codex-walk2 to 4 for motion only.
- Drawing need not wait for the idle install; pack after it, with the wolf kit full_speed_walk_rate set. Waiting on Preston's own yes via the Wolf session.

## 2026-11-05: gorilla tilt stopgap (Gorilla session)
- art/machines/ape/ape_frames.tres has tilt_anims = idle, walk, chest_beat, hex_shield, bound, hex_dome, death (stopgap Preston approved, per the Gorilla session). pack_ape_3d.py still has TILT_ANIMS = ["idle", "walk"] (line 54) and writes the .tres from it, so a repack would undo the stopgap. FEET_CAM35 already matches the .tres. Told the Gorilla session; fixed the same day (pack_ape_3d.py TILT_ANIMS now lists all seven, citing "Yes, tilt now"). Still tell the Gorilla session before any gorilla repack.

## 2026-11-05: rhino walk rebuild packed (se, e, ne)
- Preston, via the Rhino session, shown review/walk_rebuild_2026-11-05.gif and the choice "Add sway, then pack" or "Pack as is": "Pack as is".
- Backup: rhino_l/take-a/anim/walk35_touchup/backup_pre_pack (art/machines/rhino files and pack_rhino_3d.py, README with restore).
- Checks first: footlock ALL FEET LOCKED (se/ne 0.48-1.24 px, e 0.00); 0 off-palette colours against views_cam35_touchup in the rebuild and the packed s/n; no semi-alpha.
- Sel-out by walk35_touchup/selout_rebuild.py into walk35_touchup/frames_selout (se, side, ne). pack_rhino_3d.py: WALK_BY_VIEW sends se/side/ne to the rebuild; TILT_ANIMS and FEET untouched. Ran pack() only.
- Result: rhino_sheet rows se, e, ne changed (3,106 / 3,555 / 3,559 px); s, n and idle 0; kit sheet and .tres byte-identical. Godot import and rhino3d_check left to the Rhino session (one Godot at a time). Nothing committed.

## 2026-11-05: rhino walk rebuild, packing agreed with the Rhino session
- The Rhino session (owns rhino refinement) asked the walk lane to pack touch-up's leg rebuild (rhino_l/take-a/anim/walk35_touchup/frames: se, e, ne, raw, from views_cam35_touchup) once Preston approves it; s and n stay from walk35/walk/frames_selout.
- Found: the in-game idle is built from views_cam35_touchup (cam35-idle/build_cam35_idle.py); views_cam35 and views_cam35_touchup differ by about 700 px a view; walk35/walk has frames_pre_touchup, so the packed walk looks already recoloured. Rebuild vs packed raw: 235-508 px a frame (the legs).
- Plan on his yes: back up; sel-out se/e/ne with selout_rhino.selout into walk35_touchup/frames_selout (se, side, ne); per-view walk source in pack_rhino_3d.py; keep TILT_ANIMS and FEET; footlock and palette checks first. Offered sway as an option.

## 2026-11-05: touch-up sealed the hippo ne slot
- Touch-up filled the ne f1/f2 row 146 slot between the belly and the LH pad with the still's own colours (5 px and 3 px; the still is solid there). It kept s f1/f5 (jaw gap), se f3 (101,149) and n f2 (105,147) open as real background gaps after an 8x look. First seal only patched part of it; touch-up reran seal.py on fresh sway output (row 146 takes the still belly row one up, x 57-66 f1, x 55-63 f2; the still notch at 72,145 kept). Rechecked here after the fix: footlock ALL FEET LOCKED in all five views; ne seams 0 px on every frame (the walk final had 1 px on f1). Waiting on Preston's verdict before packing.

## 2026-11-05: touch-up hippo revision rechecked
- Touch-up made each foot's lowest 10 rows rigid (its first pin locked only the sole rows, and 4-30 px of the ne pads moved). Rechecked: walk_tools footlock ALL FEET LOCKED in all five views; planted pad boxes identical to the final except 1 px (se RH f4); 0 off-palette px; no alpha holes.
- walk_tools seams shows a few new 1-3 px slit flags (se f3, ne f1, ne f2, n f2) and s f1/f5 at 13 px by the jaw. Sent to touch-up to look at 8x. Still waiting on Preston's verdict on touch-up's version before packing.

## 2026-11-05: touch-up hippo version checked; one correction
- Touch-up finished cleanup and 1 px sway in touchup/hippo_l_walk/frames (40 frames; compare gif hippo_walk_compare.gif). Waiting on Preston's verdict, which touch-up relays; not packed.
- My independent check: walk_tools footlock passes in s, se, e and n; ne LH (2.24 px) and RF (2.38 px) flag CHECK. The ne RF pad box is pixel-identical to the walk final on every planted frame (the flag is the moving head next to it); the ne LH box changes 14-21 px on f0, f6, f7, where touch-up cleared the hanging fill beside the foot. Seams: only the s jaw gaps (real). Palette: 0 off-palette px.
- Correction: I listed a dark vertical line in the ne LH foot pad as a defect. It is in the approved still (accent 141218 at x 58 between the grey pad and the lilac toe, rows 149-151). Touch-up kept it, rightly. README fixed.

## 2026-11-05: hippo walk approved, to touch-up
- Preston: "Approve, to touch-up". Final in hippo_l/final: 40 frames (e, se, ne from run 1; s, n from run 2), stills, targets.json, README.txt with the se/ne defect boxes and the agreed sway, walk_5views_3x.gif.
- Touch-up messaged with the folder, defects and sway numbers. Hub told. Next for this lane: pack touch-up's version with pack_hippo_3d.py and a backup once Preston approves it; check the hippo kit's full_speed_walk_rate first.
- Also today: WALK_PLAYBOOK.md section 13 (lessons from the gorilla, fennec and hippo) and actual costs under section 12.

## 2026-11-05: hippo run 2 done (s, n); all five views drawn; se and ne cleanup not done
- Run 2: 100,320 tokens against a 100,000 cap (stopped on time, during its own audit). Hippo total 325,033 (run 1 224,713 + run 2 100,320), past the 300k line on Preston's "Yes, start run 2".
- Its verify.py (I ran it): no failures; belly gate passes (nothing hangs below the belly), feet locked within 0.9 px, specks within the still +2. walk_tools footlock: all feet pass. Seams: s has 11 px enclosed gaps on f0, f1, f4, f5, where a front foot steps out below the jaw (real gaps, left open). Lowest rows 160-163.
- By eye at 3x: s and n read as the hippo stepping toward and away from the camera, legs whole, body and jaw unchanged.
- se and ne cleanup: my free script (hippo_l/clean1, NOTE.txt) mislocated the defects and was not applied. The defects stay for the touch-up pass: fill below the belly by se RH and right of ne LH, the split ne LH foot, specks by the se RH knee.
- Review gif of all five views: D:/dev/_scratch/walk/hippo_walk_5views_3x.gif. Waiting on Preston: approve the motion, then it goes to touch-up for the cleanup and the sway.

## 2026-11-05: hippo run 2 started (s, n)
- Preston: "Yes, start run 2". Cap 100,000; estimate 90k-110k; worst case about 175k if one step overshoots. Hippo total likely 315k-335k. Command and start time in hippo_l/run2/RUN.txt.
- s and n only, plain (no sway: touch-up adds it free in its pass). New gates from run 1: the body stops at the belly (no fill hanging below it), and every foot pad stays whole.
- e, se, ne: the walk lane cleans se and ne itself, free (fix source/se_body.png and ne_body.png, recomposite).

## 2026-11-05: fennec sway kept; hippo sway goes to touch-up
- Touch-up relayed Preston on the fennec sway: "Keep, do all views". Installed in touchup/fennec_s_walk (old set in pre_sway/; script touchup/fennec_s_walk/sway.py: 2 px lean over the planted front leg, bob 0 2 1 0 0 2 1 0 on top of the 1 px dip, feet rows fixed, legs bend below a hip line).
- Lesson for every walk: a body pinned to the still reads stiff ("isnt fluid"). Sway and bob can be added after Codex, free, by per-row offsets that fade to zero at the feet.
- Hippo plan (proposal, Preston judges): touch-up adds sway in its pass, 1 px each side. Lean away from the swinging side for the four-beat walk: R = -1 0 +1 +1 +1 0 -1 -1 (f0-f7). Bob 0 1 1 0 0 1 1 0. Lock each planted foot by its own box, because se RH (row 135) and ne RF (row 136) are far above the bottom rows.
- So run 2 (s, n) does not need to wait for sway. Next free step either way: clean se and ne by fixing source/se_body.png and ne_body.png (the fill hangs below the belly there), then recomposite with the leg layers.

## 2026-11-05: hippo run 1 done (e, se, ne), over its cap, two views need cleanup
- Cost 224,713 tokens against a 160,000 cap. The watcher read 149,939 at 17:43:19 and 224,713 at 17:43:40: one Codex step counted about 75k (likely its whole context re-read uncached), so the cap stopped it one step late. Lesson: the cap can overshoot by one step, up to about one context (75k here). Quote Preston the worst case as cap + 75k. (Corrected the same day: an earlier version said to set caps 75k under the quoted price, but that leaves run 2 a 35k cap, too low to finish s and n.)
- Stopped during its own audit, so REPORT.txt still says audit pending. I ran its verify.py: no failures (foot lock within 0.9 px, targets within 0.5, discs identical, no slits, specks within still +2).
- walk_tools footlock: e and ne pass; se RH CHECK (4.4 px), a tool limit: RH sole at row 135 merges with the body underside; the stamp measure (0.9 px) decides. Seams: one 1 px slit, ne f1.
- By eye at 3x and 8x: e reads well. se and ne have defects the checks missed: dark body fill hanging below the belly with straight edges where a leg moved (se RH area, ne LH area), the ne LH foot split by a dark vertical line on f1-f3, and loose dark specks by the se RH knee (f0, f1). Free script cleanup can fix these (Codex leg layers are in walk/layers).
- Hippo total so far 224,713. Run 2 (s, n) at about 90k-110k would take it to about 315k-335k, past the 300k line: asking Preston.

## 2026-11-05: hippo run 1 started (e, se, ne)
- Preston: "Yes, start run 1". Cap 160,000; estimate 120k-160k. Command and start time in hippo_l/run1/RUN.txt.
- C: had 34 GB free at launch.

## 2026-11-05: hippo walk, prep done (free), waiting on Preston's go
- Asked through the old hub, Preston's words: "what about hippo. If not its next."
- Still: hippo_l/take-b/views_cam35_touchup_shade1 (APPROVED.txt, "Keep 1 px version"; touch-up confirmed). Already standing, 192 canvas, feet row 160, so no step A.
- Feet labelled in hippo_l/feet.json (soles, lowest-row dump, 5x look). Hidden: s hind pair, se LH, e far pair, ne LF, n front pair; se LF peeks under the jaw.
- Plan: hippo_l/plan_walk (lateral4 like the rhino, size L, P 3, 8 fps, lifts 2,3,2, dips f0 and f4, 0.48 m/s).
- Run 1 staged in hippo_l/run1 (brief, stills, targets, guides for e, se, ne). Run 2 would do s and n plus repairs.
- Price: about 220k-290k Codex tokens over two runs (rhino 275k, gorilla 243k, fennec 241k). Caps: run 1 160k, run 2 140k. Nothing runs before his yes.

## 2026-11-05: fennec front view legs widened

Preston on the result: "looks great" (2 px each side kept).

Preston: "Widen front view front legs a bit as it looks like its still walking in the sitting position". In s, the front
legs only separated over rows 147-160 with a 4 px gap. `fennec_s/widen_s/widen_s.py 2` (free, no Codex): below row 140
the halves move apart 1 px (rows 141-144), then 2 px each side, and the gold chest plate stays exactly in place. The first
version stretched the centre column and blunted the plate's point; it was rejected after a look. The gap is now 8 px.
Checks: feet locked (spreads 0.5 px or less), seams 0 (were 3-5 px), 15 colours, one piece. Also updated:
views_stand35/s.png, feet.json s labels, plan_trot targets, `final/stills/`. Originals are in `widen_s/before/`. The
touch-up lane was told before it reached the fennec trot. Playbook note: in s and n, check the stance width against the
standing still before a run, since a seated-derived still keeps its legs tucked.

## 2026-11-05: fennec trot done, to touch-up

Run 2 took 13:34 to 13:46 and used 106,214 tokens (cap 140k), so step B totals 240,928 against the 180k-280k quoted. Both
repair gates pass and the lane's re-measure agrees: ne tail light px 68-77 in every frame, e gold 4 solid pieces in every
frame. s and n are new: the silhouette footlock passes, spreads 0.5 px or less. By eye at 3x, the ne tail is whole, the e
chest is whole, and s and n read as trotting toward and away from the camera. Seams flags left are gaps between legs, open.
`fennec_s/final/`: 40 frames (se from run 1; e, ne, s, n from run 2), README.txt, walk_5views.gif with a plain 1 px outline.
Sent to the touch-up lane; the animation lane packs after it. Lesson for the playbook: give each view a draw order
(far legs, tail, body, near legs) and a number gate for each part that can break (light px in the tail box, gold piece
count). Run 2 hit both on the first try.

## 2026-11-05: gorilla walk to touch-up; fennec run 2 started (repairs, s, n)

Preston: "also handoff gorilla walk to touch up ... the 2 fold fixed a lot of it just needs touched up". The touch-up
lane got `ape_l/final/frames` (read only), with the rules to keep: foot lock, upper body equal to the idle, 15 colours.
Then the animation lane packs it. Preston: "yes to the fold two repairs into run 2 front and back views". Measured before
the brief: the ne tail box (x 58-91, y 128-149) holds 70 light violet px in the still and 11-34 in run 1's frames.
se's gold pieces equal its still's in every frame, so se needs no repair. The run 2 brief gives draw orders (ne: far legs,
tail, body, near legs) and two number gates: ne tail light px at least 63, and e gold pieces equal to the still's 4 with
none of 4 px or fewer. Started 13:34, cap 140k; step B total at most about 275k.

## 2026-11-05: fennec trot run 1 done (e, se, ne), two defects

The run took 10:17 to 10:35 and used 134,714 tokens (cap 140k). It finished on its own; Preston's usage limit stopped the
sessions afterwards, not the run. Codex's checks pass: feet locked by its stamp measure, upper body identical, palette and
structure clean. The lane's silhouette footlock flags most feet at 2-4 px: the fennec's feet stand close, and the soles
merge in that measure (a tool limit here; by eye the feet are planted). By eye, e and se trot cleanly. Defects
(`fennec_s/run1/LANE_REVIEW.txt`, `lane_defects_zoom.png`):
- ne, every frame: the far hind leg's dark upper band covers the tail, which breaks the tail's light top band into dark
  blocks and specks.
- e f3-f6: the gold chest plate breaks into loose fragments at the moving front shoulder.
Waiting on Preston: how to repair.

## 2026-11-05: fennec step B, trot run 1 started (e, se, ne)

Preston: "Start step B". Foot labels: `fennec_s/feet.json`, from `soles` plus a 6x look. Near feet are the lowest in every
view; partly hidden: s RH and LH, se LH, n LF and RF; hidden: e LH and LF, ne LF. One stray mint eye pixel on the e far
front foot (192 canvas 120,149) was set to the steel around it, in views_stand35/e.png and run1/stills/e.png. Plan:
`fennec_s/plan_trot/` (walk_tools gait: diagonal pairs, P 3.5 px, 10 fps, lifts 2,3,2, dip f0 and f4, drawn 0.56 m/s =
the kit's STRIDE, so no game change). `walk_tools.py gait` now takes a fractional --P (it was whole px only). The run 1
brief is the gorilla's with the fennec's legs (hip, upper leg, knee disc, lower leg, foot; the upper leg redrawn as a
leaning band), the tail dipping one frame after the body and kept off the legs, the seams check with violet body colours,
and REPORT.txt kept current from the first view on. Started 10:17, cap 140k, estimate 90k-140k. Run 2 (s, n) follows the
check, cap 140k.

## 2026-11-05: fennec step A done (standing 35 views)

The run took 10:04 to 10:10 and used 54,066 tokens (estimate 60k-100k): one image, finished, sliced and checked. Palette,
alpha, accent shares and lone pixels pass. Codex scaled the sheet so e was 75 px long, and that left the head 8% small (s
ear span 43 against the seated 47, eyes 24/15/8 against 28/18/12). The fix: a standing fox is longer than a sitting one, so
body length is the wrong scale key, and the head is the right one. The lane re-finished the same raw image with Codex's
finish.py at e 83 (`stand35/refinish/`, free). That gives s 48x64 and eyes 29/19/17, and the ne/nw mirror improves 0.895 to
0.989. The five views are in `fennec_s/views_stand35/` (Codex's e 75 finish is in codex_e75/). By eye: the same fennec,
standing square on four legs, far feet higher, seen from above. Open points: in n the cream tail tip sits between the hind
legs, touching their inner edges (drawn over them, correct for a tail nearer the camera); in ne the far hind leg is mostly
hidden. Lesson for the playbook: scale a re-posed still by the head, not by body length. Board:
`stand35/standing_vs_seated.png`. Step B (trot runs) waits for Preston.

## 2026-11-05: fennec step A started (standing 35 still)

Preston: "Yes, start step A". The fennec's 35 views are seated, so the gorilla method has no standing pose to move.
Step A makes one: a single Codex image sheet, the seated cam35 recipe, with two refs. The first is the approved seated 35
views, for the look and the camera. The second is the old trot f0 frames at the low camera, for leg length and body height
only. The pose is standing square on four straight legs, with the tail straight, raised and clear of every leg. That
targets the two glitches the touch-up lane patched (n: gold tail pixels on the inner hind leg; ne/nw: the tail over the
near hind leg). Scale: e is 75 px long, cross-checked by the ear span in s against the seated 47 px. Checks are those of
the seated run plus tail.txt (the gap between tail and legs) and a feet-rows and belly-gap line. Folder:
`fennec_s/stand35/` (brief, prompt, refs, the hollowtide check tools copied into tools/). Views go to
`fennec_s/views_stand35/`. Started 10:04, cap 110k, estimate 60k-100k. C: had 15 GB free.

## 2026-11-05: gorilla seam fix, final frames

Preston: "Fix it first". The ne f3-f4 hip seam was a transparent slit 2-4 px wide: the leg slid back as planned and
nobody drew the body behind it. The same defect sat at the near forearm in e f3-f5 and at the forearm and head in se
f0, f1, f4 and f5 (missed at 2x, found with a slit detector). New check, `walk_tools.py seams`: one --fix pass filled
them with the body bands (e 94 px, se 130, ne 170 over 8 frames each; s and n untouched). The fill reproduces exactly
from the tool. Remaining flagged pixels are open space beside the far arm at the silhouette edge, left open. All 40
frames are in `ape_l/final/frames` (README.txt there gives the sources): all feet locked, one piece each, palette and
alpha clean. Codex's run1 and run2 folders stay as delivered. Not packed or tested in the game.

## 2026-11-05: gorilla run 2 done (ne repair, s, n)

Preston: "Fold into run 2". 9:29 to 9:44, 100,614 tokens (cap 160k), finished on its own with its REPORT.txt written
first, as briefed. The lane fixed the se f0 loose pixel by hand beforehand (run2/walk/frames/se_f0.png). Codex kept the
ne label LH (left hind; the shield above belongs to the far forearm). Lane checks: foot lock passes in ne, s and n (n far
fists 2.00 px on the silhouette measure, 0.0 on Codex's limb layers: partly hidden); one piece per frame; lowest rows
up to 163. By eye (run2/ape_run2_board2x.png): s and n are clean and read as walking toward and away from the camera;
the ne knee, foot and joins are whole now, but f3 and f4 show a dark jagged seam at the far-left hip join. The full walk
is 5 views x 8 frames: e, se (se f0 fixed) from run 1, ne, s, n from run 2. Not packed or tested in the game.

## 2026-11-05: gorilla run 1 done (e, se, ne)

Preston: "Run it now". 8:57 to 9:24, stopped by the cap at 143,043 tokens (estimate 95k-115k) while finalizing; all
24 frames and checks were written, Codex's REPORT.txt was not (the lane wrote `ape_l/run1/REPORT.txt`). Foot lock passes
in all three views. e and se read clean at 2x. ne's far-left limb breaks up (cut-off orange parts, a broken knee disc,
loose specks), and se f0 has one loose pixel. Lesson: the token estimate for a machine with big forearm blocks runs
about 30% over the rhino's, and finalizing came last, so the next cap goes to 160k, or the brief asks for REPORT.txt
before the boards. The C: temp cleanup at about 9:15 did not touch the run (all its output is on D:).

## 2026-11-05: gait chosen, run 1 ready (not started)

Preston: "A, diagonal pairs" (recorded in `ape_l/plan_a_diagonal/CHOSEN.txt`). `ape_l/run1/` holds the Codex brief
(the rhino's run 1 brief adapted: the gorilla's 15 colours, forearms moved as whole blocks with their hex shields, gems
never redrawn), targets.json and guides from plan A, the stills placed on the 192 canvas (lowest row 160 in every view),
and RUN.txt with the capped command (cap 140k tokens, estimate 95k-115k). It waits for his go and his choice of when,
since C: has about 1 GB free and Codex writes its session logs there.

## 2026-11-05: tools, rhino check, gorilla plans (all free)

**Interruptions.** C: filled up mid-session, then a PC restart (around 8:40) and an app crash (8:44). Nothing paid had
started. On disk afterwards: the playbook (copied into the main checkout, identical to the worktree copy), `work/`
(an earlier stills board and an inspection dump). `tools/walk_tools.py` was written after the restart. Scratch goes
to `D:\dev\_scratch\walk\` (hub, Preston's call).

**walk_tools.py, checked against the approved rhino walk** (`rhino_l/take-a/anim/walk35/`):
- `foot_path` reproduces the rhino's four foot paths exactly, and `build_targets` reproduces every sole target in
  its targets.json (0.0 px max difference). Dip frames come out as f0 and f4, as approved.
- `footlock` on the installed frames (`walk/frames`): every visible foot locked. Spread: e 0.00, s and n 0.88,
  se and ne 0.48-1.74 px (gate 2 px). Max distance from target 1.74 px (ne LH). One piece per frame, no strays,
  no semi-alpha, no canvas edge, no off-palette pixels against the touch-up stills. Lowest rows match the rhino
  report (s and n reach 163, se and ne 162). Output: `D:\dev\_scratch\walk\rhino_footlock.json`.
- `mirror`: for both the four-beat walk and diagonal pairs, playing sw, w and nw at frame (i + 4) mod 8 keeps the
  same physical foot up on every frame. Today a turn from s to sw swaps the up foot within one frame. That is a
  proposal for whoever owns the engine's walk player; nothing was changed in the game.

**Gorilla foot labels** (`ape_l/feet.json`), from `soles` plus a look at the approved touch-up stills (feet row 130,
placed at +16, +30, so row 160): fists are the shielded forearms. Visible per view: s RF, LF, RH, LH; se RF, LF;
e RH, RF; ne LH, RH, RF; n LF, LH, RH, RF. The ne LH label is the least certain (10 px from where the body's
proportions put it).

**Two free plans, P 3 px a frame, 8 fps, lifts 2, 3, 2, dip on f0 and f4, drawn speed 0.48 m/s (the rhino's):**
- `ape_l/plan_a_diagonal/`: knuckle walk in diagonal pairs (RF + LH swing f5-f7, LF + RH swing f1-f3), as the
  approved set A walk at the old angle.
- `ape_l/plan_b_fourbeat/`: four-beat walk, the rhino's order (LF 1, LH 3, RF 5, RH 7).
- Each has targets.json (for the Codex brief and `footlock`), guide_<view>.png (8 frames, filled bar = planted,
  outline = swinging with its lift) and plan.gif (all five views at 8 fps).

**Speed (stride, Froude; a proposal, general knowledge).** Gorilla leg 45-60 px = 0.9-1.2 m. A comfortable walk
(Fr 0.25) is 1.5-1.7 m/s; the drawn 0.48 m/s is a slow amble (Fr 0.02-0.03). The game's placeholder move_speed of
3.5 m/s is Fr 1.0-1.4, a run. Planting at 3.5 m/s needs P 21.9 px a frame at 8 fps, or playing the walk 7.3 times
fast. Preston and game feel pick; this lane does not.

**Waiting on Preston:** which gait (A or B), then a go for the paid Codex run. Estimate from the rhino with its
lessons built in: run 1 (e, se, ne) 95k-115k tokens, run 2 (s, n) 85k-105k, so 180k-220k, plus 60k-80k only if a
leg cleanup is needed. Codex writes its logs to C:, which has about 1 GB free, so he picks when it runs.
