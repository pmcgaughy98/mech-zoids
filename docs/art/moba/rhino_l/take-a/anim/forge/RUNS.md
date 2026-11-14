# Attack forge runs, rhino ground pound (2026-11-03)

Upload method that works: a file input added to the top page, filled with the exact local PNG by Claude in Chrome's file_upload, then handed to the forge's own file input when "Upload from Device" is clicked. No hand-typed base64.

| Run | View | Result | Blob | Kept |
|---|---|---|---|---|
| 1 | front | side and three-quarter views, glossy generic rhino | 14d4c231 | no |
| 2 | side | right poses, rhino redesigned (long legs, rounded armour) | 15ded930 | no |
| 3 | side | keeps the design; Preston: "looked great" | 9745ea77 | `ground-pound-attack-forge-v3.jpg` |
| 4 | back | rear three-quarter views, 3x3 grid | f4d6c06d | no |
| 5 | front | Opal error, no output | none | no |
| 6 | back (camera spelled out) | true back view, keeps the design, but 3x3 instead of 3x2 and the rear-up barely reads | ad92084c | not downloaded, waiting on his yes |
| 7 | front (camera spelled out) | glossy three-quarter rhino again, cells cropped from a 3x3 | 695c9f4e | no |

## Codex, one sheet for all three views (2026-11-03)

`../codex-ground-pound/`: one image of 3 rows (front, side, back) by 6 frames, from the three approved sprites only. 58,520 tokens.
- Works: the same rhino in all three rows, the rows match frame for frame, and the front legs really lift (side 18 and 24 px in F2 and F3, front 26 and 30).
- Problems: the front and back rows are drawn about 15 to 20% bigger than the sprites (front 86x80 against 72x70, back 77x89 against 66x77); the red eyes are gone; the red that is left is fringe on the outline; side F1, F2 and F5 float 1 px.
- All fixable without a new image. Waiting on his yes for the cleanup pass.

## Cleanup and effect composite (2026-11-03)
Codex sheet cleaned in codex-ground-pound/clean/: sizes re-matched per row, no red fringe, eyes restored in Aseprite, floating side frames grounded. Effect sheet v1 cut into 8 frames and played from contact. Preview: clean/ground-pound-preview.mp4. Details: clean/REPORT.txt. Back rear rebuilt from back_f0 on his note (hind legs planted, body tips up). Waiting on his look.

## Rhino sheets A and B finished (Claude, 2026-11-03)
- Codex set A (idle, walk, horn jab, horn toss) and set B (brace, stampede, death, six effects) delivered; reports in codex-set-a/REPORT.txt and codex-set-b/REPORT.txt.
- fix_set.py: eyes restored on every front and side frame by template match against the cleaned ground-pound eyes, then head tracking for posed frames. Codex frames kept in each sheet's frames_codex/. Log in each set's FIXES.txt, check board eye-check-all.png.
- Horn toss front_f4 and back_f4 (twisted three-quarter peak) swapped for ground-pound f1. Stampede side_f5 moved down 4 px. Every frame's lowest pixel now on y=160.
- Death f5 and f6 keep no eyes on purpose (eye out).
- Known gaps: horn toss side_f2 (scoop) has no eye; horn toss front f1-f2 eyes sit on a lowered head and may read odd; walk front row barely moves; rear legs shorten in some brace and death frames (Codex flagged).
- reel/rhino-reel.mp4 (21 s, all seven moves, three views, effects placed) and reel/rhino-contact.png. Ground pound keeps its own video.

## Walk redone and eyes moved to Codex's own eye (Claude, 2026-11-04)
- Preston: "walking needs redone, also some of the frames the red eye dot is not where it should be".
- Codex walk B (codex-walk-b) failed its own check: side reach frames float 6-7 px, diagonal pairs mismatch, back legs shorten. Not used.
- Walk now: side row from walk A (reads as a walk, all feet grounded) with front and back rows built by walk_frontback.py from the approved ground-pound f0 sprites: body bob from the side row's top edge, whole-leg lifts (legs keep length) in diagonal pairs timed to the side row's foot lifts. Codex's front/back walk frames stay in walk/frames_codex. Review: codex-set-a/walk/review-walk-v2.png, preview-walk-v2.gif.
- Eyes v2 (fix_set.py): every eye Codex drew red is mapped through the exact finishing shrink and frame offset, so it sits in the eye socket like the approved sprite. 45 frames moved (eye-moves-all.png). Guessed eyes remain only where Codex drew none: horn toss front right eye (5 frames), brace front f0, stampede front f5, horn toss side f1; horn toss side f2 still has none.
- Reel rebuilt: reel/rhino-reel.mp4.
- 2026-11-04, his picks from the eye board: horn toss front f3, horn toss side f1 and stampede side f4 take the previous eye placement (the left tile). Copied pixel for pixel into eye_overrides.json by recover_eyes.py; fix_set.py applies them and never re-places those three. Board: eye-picks.png. Reel rebuilt.
- 2026-11-04, his second note: horn toss front f3 right eye moved into the black hole right of the horn; horn toss side f1 eye moved off the forehead into the black hole (socket); stampede side f4 kept its place and got the dark socket the other side eyes have. All hand-set in eye_overrides.json. Board: eye-picks-2.png. Reel rebuilt.
- 2026-11-04, his third note: horn toss side f1 eye was still too high; the head is lowered in that frame. Eye moved down into the socket on the lowered head (x123-126, y140-142). Board: eye-picks-3.png. Reel rebuilt.

## Sel-out for the MOBA style (Claude, 2026-11-04)
- Preston: "ok now sel out for our moba style using what we've collected". The MOBA creatures follow the Hollowtide canon, whose outline comes from its sel_out shader; this game has none, so selout_rhino.py bakes the shader's creature rules into every rhino frame: one dark texel outside wherever the edge is a light or material colour, dark edge pixels darkened to the outline colour (#141218, the rhino palette's darkest). Speck cleanup is a no-op on this palette; detail ink stays off as in the shader.
- Output: frames_selout/ beside every sheet's frames/ (150 frames, ground pound included); frames/ untouched, so rerun selout_rhino.py after any frame fix. Board: selout-board.png. Reel: reel/rhino-reel-selout.mp4 (python rhino_reel.py frames_selout). Feet stay on y=160; the outline under a light foot edge sits on y=161.

## Retro Diffusion walk test (2026-11-04)

Preston: "now try walking animations in retro". Approved 3 runs at $0.14 = $0.42; balance $2.59 to $2.17.
- Tool: rd_advanced_animation__walking, 128x128, 8 frames, spritesheet. Input per view: sel-out ground pound f0,
  centred in 128 with the feet on row 110 (retro-walk/input/). Jobs: side ae1c6c6a, front 6f4e221b, back 99a51ce5.
  The first front try was refused as a corrupted image (base64 copy error); resent as an indexed PNG, fine.
- Raw results: all three kept the colours within one step of the palette (FECF1F for FFCF1F etc.) plus a little
  black and white, and all three painted over the red eyes. Front and back drift up to 3 px off the ground.
- retro-walk/finish_retro.py: snap to the rhino palette, ground each frame on its foot row, put the eyes back by
  head tracking, rerun sel-out, map back into the 192 canvas (retro-walk/frames/, frames128/).
- Verdict, from review-retro.png:
  - side: best walk the rhino has had. Real strides, feet tilt on the lift and plant flat, legs keep length,
    body and head hold the design. Candidate to replace the walk side row.
  - front: moves, but the front legs read longer as they step (raw height up to +3 px). Not clearly better
    than the script-built front row.
  - back: fails. The tail grows into a long yellow spike and the hind legs turn brown in f5-f7.
- Not done: wiring the Retro side row into codex-set-a/walk (8 frames vs the current 6 per cycle), any reroll.
- Preston: "front and back look like galloping rather than the walking gait for side view". Retro moved each
  visible pair together. retro-walk/frontback_8.py rebuilds front and back from GP f0 with walk_frontback.build
  as a four-beat walk timed to the Retro side (front: LF up f1-f3, RF up f5-f7; back: LH up f3-f5, RH up
  f7-f1; lifts 2/4/2 px; body down 1 px when both visible feet are down). Output retro-walk/walk8/ with the
  Retro side copied in. Not yet swapped into codex-set-a/walk. Side loop f7 to f0 is the biggest jump in the
  row (leg overlap 0.74 vs 0.81-0.93 between other frames).
- Preston: "redo with retro as side view is too fluid it wouldnt look right". Front and back rerun on Retro
  ($0.28, balance $1.89; jobs front 5637abee, back 520b0923) with a four-beat walk prompt and prompt expansion
  off. First tries kept as front_sheet_v1.png / back_sheet_v1.png. retro-walk/gait_check.py compares leg-pixel
  change left vs right per frame (high correlation = both legs move together): first try front +1.00, back +0.98;
  redo front +0.51, back +0.97; the script-built walk8 rows -0.95 and -1.00.
  Redo verdict: front alternates a little but the viewer-left foot turns into a black block in f3-f4; back is the
  same bound as before with the tail spike and dark legs. Retro walking does not hold front or back for this rhino.
- Also asked about nw, ne etc.: the approved rhino has 8 views (views/), the west three about 96-98% mirrors of
  the east three, but every animation is front, side and back only. se and ne are missing for all 8 animations.
  retro-walk/input/se_128.png and ne_128.png are prepared (approved views, sel-out, feet on row 110), not run.
- Preston: "do both". (1) retro-walk/frontback_fluid.py: front and back from GP f0 with the four-beat timing
  plus a foot arc (1, 3, 5, 2 px), a 1 px weight shift toward the planted foot, a 1 px shoulder roll over a
  foot lifted 3+ px (outer columns only), 1 px bob on double support; enclosed 1 px holes from the shift filled.
  Gait check front -0.72, back -0.81 (walk). Output walk8f/. (2) Retro walking on se and ne ($0.28, balance
  $1.61; jobs se 2177fb2d, ne 10f39f87), inputs = approved views/se.png and ne.png, sel-out, feet on row 110.
  Both held the design and step like the side; se drifted 1 px, ne up to 4 px (grounded by finish_retro.py,
  which now also takes se and ne). gait_check does not apply to three-quarter or side views (its halves split
  front legs from hind legs there, not left from right).
  retro-walk/walk5.py assembles the proposed set in walk5/: front and back from walk8f, se, side and ne from
  Retro; w, sw, nw to be mirrored in the engine (the drawn west stills are 96-98% mirrors). Not yet swapped
  into codex-set-a/walk.
- Preston: "only 2 that have matching gaits like id want are se and side view", then "can codex generate all to
  way to fill in retro quality? or any of our tools". PixelLab animate_image tried on the front view (free daily
  bonus, 2 generations, job 0a27df9f; PixelLab trial allows one job at a time). Fail: the rhino grows ~9 px
  taller and 13 px wider mid-cycle and sprouts blue and white claws like arms (frames in retro-walk/pixellab/,
  strip front-strip.png). Back and ne not sent. Tally for front and back walks: Codex 2 fails, Retro 2 fails,
  PixelLab animate_image 1 fail. Retro se and side are the only matching walks.
- Preston: "try 1 on front first". PixelLab animate_with_skeleton_v3 (job fac07fb6, 3 free bonus generations,
  15 left today): direction south, template bear, low top-down. Skeleton hand-measured from input/front_128.png
  (front legs on the arm chains, hind legs on the leg chains, head on nose/eyes/ears/neck), 8 poses from the
  Retro side timing (retro-walk/pixellab/front_skeleton.py -> front_keypoints.json). Result: design held
  (alpha IoU 0.93-0.98 with the input, only rhino palette colours, red eyes kept, no new parts), body fixed in
  place, legs alternate (gait check -0.71). The forward foot dips up to 4 px below the ground line (perspective
  of a step toward the camera); left as is, not grounded. Finished by pixellab/finish_pixellab.py into
  pixellab/frames/. Comparison: pixellab/preview-front-se-side.gif.

## 2026-11-04: PixelLab posed back and ne, full five-direction walk

Preston: "yes run back and ne that looks great though."
- back: animate_with_skeleton_v3, job f4c14adb, template bear, low top-down, 3 free generations. Gait check -0.72 (walk).
  IoU vs still 0.91-0.99. Feet dip 1-2 px below the line on some frames (bottom 161-163, still 161).
- ne: job a2d148e9, same settings, direction north-east, 3 free generations. IoU vs still 0.87-0.91, bottom 160-163.
  The gait check does not apply to three-quarter views (its halves split front from hind legs); judged on the board.
- finish_pixellab.py now takes the 192 offset from the outlined views/{v}.png when there are no ground-pound frames.
- Assembled by retro-walk/walk_final.py into retro-walk/walk-final/: front, ne, back from PixelLab posed, se and side
  from Retro. Board has the approved still in column 1. West views are mirrored in the engine.
- PixelLab free generations used today: 11 of 20. Retro balance unchanged at $1.61.
- Not swapped into codex-set-a/walk; waiting on Preston.

## 2026-11-04: walk swapped in, shoulders fixed, detail ink
- **Front shoulders, geometry:** `retro-walk/pixellab/fix_front_shoulders.py` restores the approved still's
  shoulder plates (PixelLab had stretched them into the knee). It changed about 500 px per frame; the legs are
  untouched.
- **Detail ink:** `detail_ink.py` uses the contour part of the Hollowtide shader's detail-ink rule, only on views
  below the se and side walks' interior ink share (5.8%).
  - Front: 1.6% before, 5.2% after. Back: 5.7% before, 10.0% after.
  - The full shader rule (22% and 28%) was rejected.
- **Swap:** `walk-final` was swapped into `codex-set-a/walk/frames` and `selout_rhino.py` was rerun. The old
  frames are kept in `frames_pre_retro/`. `rhino_reel.py` now plays 8 walk frames.
- **Ground check:** it lists front and back frames with the forward foot 1 to 5 px below the line. Left as is.
- **Proposal:** `docs/plan/moba-perspective-remaster-synthesis-2026-11-04.md`.

## 2026-11-04 (later): Codex frames in, shoulder line, kit, reveal, brace walk
- **Swap:** the Codex consistency frames are the live walk. The old walk is kept in `codex-set-a/walk/frames_pre_codex/`.
- **Front shoulder line:** a domed dark arc over each knee-disc plate, with the texel under it lifted to the
  highlight. `front_shoulder_ink.py` did all 8 walk frames (0.0% mismatch). Codex (`codex-shoulder/`) did 38 more
  front frames and skipped 5 rearing or falling ones. The originals are in each `frames/pre_shoulder/`.
- **Kit in 3D:** `rhino_kit.gd` (keys 1-4), `fx3d.gd`, `training_dummy.gd`, packed by `tools/art/pack_rhino_3d.py`.
  Lengths and sizes are presentation placeholders.
- **Reveal:** `rhino-reveal.mp4`, 50.7 s at 1280x720, recorded with Movie Maker off-screen. There is also a 14 MB
  `rhino-reveal-phone.mp4` and a `rhino-reveal-contact.png`. Silent. The structure comes from general knowledge, no
  real reveal was studied.
- **Brace walk:** braced and moving now plays the walk at brace speed (0.35), and stopping plants frame 3 again.
  The check tests both. A drawn braced shuffle is still the proper fix.
- **Check:** `rhino3d_check.gd`, 0 failures, including 4 new brace tests.
- **Still open:** abilities have only front, side and back (se and ne show the side view).

## 2026-11-04: se and ne for every action, braced shuffle (animation lane)
- **Codex:** `make_codex_diag.py` built two jobs that reuse each move's original column text word for word, with a
  2-row layout (se, ne) and the approved se/ne views as refs. Set C (stampede, horn toss, ground pound, horn jab)
  used 104,506 tokens. Set D (brace, death, idle, plus the braced shuffle in front/side/back from brace f3) used 71,728.
  All grids were clean, every row faced the right way (exact share well above the mirrored ref), and the feet are on y=160.
- **By eye:** the se rows hold the design. The ne rows drift on the rump plate and hip discs, the same tier as the
  earlier Codex sets. The stampede gallop is weak in f0, f1 and f6, as in set B. Codex flags the se head turning toward
  side-on at the peaks of horn toss, horn jab and ground pound.
- **Fixes:**
  - `diag_idle.py`: the se/ne idle comes from the approved stills (1 px breath, feet fixed); Codex's idle is in
    `codex-set-d/idle/frames_codex`.
  - `fix_set.py brace-shuffle`: put back Codex's own eyes. It got a shim that reads set C/D grid edges, used only
    for sheets outside FACTORS.
  - `shoulder_transfer.py`: copied the shoulder line from brace front_f3 onto the 6 shuffle front frames
    (`front_shoulder_ink.py` could not fit the braced pose).
  - `se_eyes.py`: tracked the red eye into stampede se f2 and f3 and ground pound se f3 and f4 (board
    `se-eye-board.png`). It skipped, as a poor fit, horn toss se f1 and f4 and horn jab se f1, f3 and f4. Those
    frames still have no eye and are for Preston's picks.
- **Pack:** `pack_rhino_3d.py` now packs se/ne rows where they exist (DIAG) and brace_shuffle; 43 animations.
  Board: `rhino-diag-shuffle-board.png`.
- **Brace shuffle stride:** the planted feet slide 2 px a frame, so the feet stay put at 0.40 m/s at 10 fps. Braced
  movement is 1.225 m/s, so either the braced speed comes down or the feet slide. That is for Preston.
- **Check:** `rhino3d_check.gd` gave 2 failures, both from the game feel lane's fallback test, which used
  ground_pound_se as an undrawn action. Reported to that lane.

## 2026-11-04: idle rebuilt from the approved stills (animation lane, on the sprite factory's note)
- **Why:** the sprite factory found that the Codex idle (set A) carried half the approved stills' interior ink and
  plain knee discs (back 5.0% against 10.1%; front 3.2% against 6.8%; side 3.6% against 10.0%), and its frame 0
  matched the still on only 42-62% of pixels. The rhino gained texture the moment it walked.
- **Fix:** `diag_idle.py --set-a` builds front, side and back idle from views/s, e and n with the 1 px breath (feet
  fixed, f0 = the still). Codex's idle, with its eye fixes and shoulder line, is kept in
  `codex-set-a/idle/frames_pre_still`.
  - Do not rerun `fix_set.py` on idle: it would rebuild from Codex's frames.
  - `pack_rhino_3d.py` `still()` now takes the approved views for every facing, so the ground pound's f0 is no
    longer used.
- **Results:** ink matches the stills (front 6.9%, side 10.2%, back 10.1%), `rhino3d_check` gives 0 failures.
  Board: `idle-from-stills-board.png`.
- **Open:**
  - The idle front has no shoulder line, because the approved s.png has none; `front_shoulder_ink.py` misses by
    26-31% on it.
  - The live walk (Codex consistency frames) itself drifts from the approved stills (front face, back tail plate),
    so the pop when walking starts now comes from the walk, not the idle.

## 2026-11-04: walk upper body back to the stills (animation lane)
Preston: "fix em up with our tools as well".
- **Found first:** the live walk (Codex consistency pass) took the pose-guided PixelLab front, back and ne frames as
  input, kept their pose and foot rows (alpha IoU 0.97 or more) and only restyled them toward the Retro se/side
  look. So the gait is the pose-guided one Preston credits ("that ended up fixing the gallop to a consistent walk"),
  but the restyle matched the stills on only 59-66% of pixels: front chin plate smaller, back tail plate a round knob.
- **Fix:** `walk_to_still.py` puts the still's upper body (head, horn, chin plate, shoulder blocks, rump, tail plate)
  over each frame, moved by its bob (front dx 0-2, dy 1; back dx 1-2, dy 2-3), and keeps the pose-guided legs from
  each knee-disc top down (rows 133-139) and the middle band below row 150. Side, se and ne untouched.
- The shoulder line now comes from sel-out over the still's shoulder blocks, which are silhouette in its geometry.
  The idle-to-walk switch no longer changes the upper body.
- **Kept:** the originals, with `pre_shoulder/`, in `codex-set-a/walk/frames_pre_still_body/` (moved out, so
  `front_shoulder_ink.py` can't restore the drifted frames).
- **Results:** `selout_rhino.py` rerun, `pack_rhino_3d.pack()` (43 animations), `rhino3d_check` 0 failures. Board
  `walk-to-still-board.png`.
- The lessons from every run here are distilled in `docs/art/moba/ANIMATION_PLAYBOOK.md`.
