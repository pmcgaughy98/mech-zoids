# Machine animation playbook

## Gemini research review, 2026-11-09

The first authorized Meshy Prime Text to Motion trial is recorded in `docs/reference/gemini-animation-research-2026-11-09/MESHY_TRIAL_RESULT.md`. It cost 10 credits and missed the shield action/support intent. An isolated arm-only fit was rendered against the authored cast and rejected. Keep the authored cast; no production animation or event timing changed. Inspect actual donor rigs: this FBX contained 52 bones at 30 fps, not the report's assumed 24 joints.

Read `docs/reference/gemini-animation-research-2026-11-09/REVIEW.md` before using the external report in that folder. It contains useful action-phase structure but unsupported measurements, gait numbers and some incorrect engine guidance. Raw report and original Word export are preserved for comparison. Video-only reviews cannot certify millimeter clearances or invent contact frames without a stated time base. Source event clocks and approved timing take precedence; generated motion and third-party research still require local visual and technical checks.

## Current 3D animation research, 2026-11-09

For skeletal mech work, first read `docs/reference/animation-skillup-2026-11-09/REPORT.md`
and `ACTION_CARDS.md` in the same folder. They add sourced animal-action definitions,
rigid-body adaptation, contact/transition methods and a screened repository shortlist.
Read `docs/team/ANIMATION_LANE_EXCHANGE_2026-11-08.md` for the gorilla/rhino corrections.
Use both visible motion review and technical validation. A clean loop or clearance test
does not establish that an action reads as the intended punch, chest beat or gait.
The sprite pipeline below remains historical guidance; do not apply its sheet-generation
rules or counts automatically to the current skeletal-model workflow.

How to make a MOBA machine animation, or fix one, without relearning the rhino walk. This is what worked and
what failed from 2026-11-03 to 2026-11-04. The full logs are `rhino_l/take-a/anim/forge/RUNS.md` and each Codex
set's `REPORT.txt`.

Written by the hub session (Mech-Zoids Game) and the animation lane, 2026-11-04. Update this file whenever a lesson
changes.

## 1. Preston's rules
- **The approved stills are the truth.** They are each machine's `<machine>/take-*/views/` (rhino `rhino_l/take-a`,
  gorilla `ape_l/take-a`, fennec `fennec_s/take-b`). Frame 0 of every idle and every ability is the still itself.
  Every frame is judged side by side against the still.
- **He rejects "barely acceptable".** Show a board with the approved still in column 1, and let him pick.
- **Feet stay planted.** Feet sit on the foot row in every frame, and a planted foot must not slide in the game.
- **Paid runs need a cost estimate and his yes first.** This covers Retro Diffusion, ElevenLabs, and any credits.
  PixelLab's free daily generations (20) are fine to use. Codex runs on his plan: quote the token estimate
  (section 3) when you ask.
- **His picks are permanent.** Eyes he chose are in `eye_overrides.json`, and no script re-places them.
- **Numbers are his to set.** Lengths, speeds and sizes are placeholders until he sets them.
- **Sel-out only, unless he says otherwise.** The packer adds sel-out to the stills as drawn. Detail ink is a
  per-view fix for a view that is clearly flat (the rhino front), never a blanket pass. The gorilla is sel-out only
  ("sel out only").
- **No curled tails** ("no curved tails as they are hard to rotate"). Tails lift and swing but stay straight.

## 2. Canvas, feet and views
- **Every machine animates on a 192x192 canvas with the feet on y=160.** Place a still at
  (+16, 160 - its foot row):

  | Machine | Still | Foot row | Offset in 192 |
  |---|---|---|---|
  | Rhino (L) | 192x192 | 160 (outline under a light foot edge on 161, so `feet_edge_row` = 161) | 0, 0 |
  | Gorilla (L) | 160x160 | 130 | +16, +30 |
  | Fennec (S) | 160x160 | 140 | +16, +20 |

  Most other stills are 160x160 with a foot row of 140 (`STILLS_STOCKTAKE_2026-11-04.md`). Measure; don't assume.
- **Views:**
  - Five are drawn: s, se, e, ne and n. The engine mirrors sw, w and nw, so a fix in ne also fixes nw.
  - An action drawn only in s, e and n shows its e frames in se and ne.
  - An action that has its own se and ne frames plays them (the own-view rule in `directional_sprite_3d.gd`).
- **Size classes:** L is 0.020 m a texel, M 0.018, S 0.016. The world stays at 50 texels a metre.
  `size_scale()` sizes the ring, the shadow and shields against the L rhino.
- **Seated stills (fennec):** the walk cannot start on the still, so the walk is the one animation exempt from
  "frame 0 = still". Every ability still starts and ends on it.

## 3. The generators: what each is good and bad at (measured)
| Tool | Good | Bad | Cost |
|---|---|---|---|
| Codex, 3-row sheet (front, side, back) | Same machine in every row, rows match frame for frame, legs really lift | Drifts from the stills (front face, back tail plate), a Codex idle carries only half the stills' interior ink, eyes land in the wrong place | ~58k-105k tokens a sheet |
| Codex, 2-row se/ne job | Reuses the move's original column text word for word, with the approved se/ne views as refs; grids clean, every row faced the right way | ne drifts on rump plates and hip discs; se head turns side-on at attack peaks; parts on the far side break (the gorilla's back hex plate in hex_shield ne f1-f4) | rhino set C 104,506 tokens, set D 71,728; gorilla set D 80,664 |
| PixelLab `animate_with_skeleton_v3`, pose-guided from keypoints copied off an approved side walk | **The only tool that made a straight front or back walk** (section 9): design held (alpha IoU 0.87-0.99 against the still), one leg at a time | Stretched the front shoulder plates into the knee; the forward foot dips 1-5 px. **Lost the design on the fennec** (2026-11-04, job 6555b2ae, template bear, front): legs alternate, but it drew a generic fox with long thin legs, a grey ruff and no chest plate, alpha IoU 0.63 with the input (fennec_s/take-b/anim/pose-walk/). It holds a bulky machine, not a small big-headed one. Before redoing a Codex front or back walk, measure its foot lift per leg band first: the fennec's Codex trot already lifted 2-4 px | 3 free generations a view, ~4 min each |
| PixelLab, text-prompted walk | | Grew ~9 px taller mid-step and sprouted claw arms | free generations |
| Retro Diffusion walking style | Side and se walks that read as walks | Paid per run | $0.14 a run |
| Build from the still with a script | Exact design, exact ink | Limited motion | free |

- **Codex walk B failed its own check:** the side reach frames floated 6-7 px, the diagonal pairs mismatched, and
  the back legs shortened. Run the checks in section 5 before trusting any generator.
- **Codex briefs that worked** (`ape_l/take-a/anim/codex-set-a/brief.txt`, `fennec_s/take-b/anim/common.txt`):
  - Name the still files, the canvas offset, the exact colour list and what must never change (parts, limb length,
    head size, the outline).
  - Point Codex at the previous machine's set folder as the method (finish, polish, gems, seam_fill, verify).
  - **One image-tool call per animation, no redo.** Weak sheets are fixed in finishing, not regenerated.
  - **No generated idle.** Ask for the idle to be built from the still (section 4, step 6).
  - Give each move its frame plan with the key frames (release, blast, landing) agreed with the game feel lane.
  - Ask for preview durations in ms, `grid.json`, `checks.txt`, gifs, a board with the still leftmost, and tokens.
  - Effects are never in the body frames.
- **se/ne after the fact:** `make_codex_diag.py` (rhino) and `make_codex_diag_ape.py` (gorilla) build 2-row jobs from
  the original column text and the se/ne stills on a flat key colour at 6x with a 48 px margin.
- **Codex launch** (from `C:/Users/pmcga/dev/hollowtide`, in the background; one set per folder, two sets can run at
  once):
  `codex exec --sandbox workspace-write --add-dir "D:\dev\new-mech-rpg\docs\art\moba" --skip-git-repo-check < "$A/brief.txt" > "$A/codex-log.txt" 2>&1`
- **Uploading to a web forge:**
  1. Add a file input to the top page.
  2. Fill it with the exact local PNG using Claude in Chrome's `file_upload`.
  3. Hand it to the forge's own input when "Upload from Device" is clicked.
  Never type base64 by hand.

## 4. Finishing, in this order
Most scripts are in `rhino_l/take-a/anim/`. Exceptions are named.
1. **Eyes:** `fix_set.py`.
   - It template-matches the cleaned eyes, then tracks the head on posed frames.
   - It maps Codex's own red eye through the exact finishing shrink and offset.
   - `se_eyes.py` tracks eyes into se frames from the nearest frame that has one (min score 0.55), and skips any
     frame where the fit is poor.
   - List every frame left without an eye for Preston. **Open:** rhino horn toss se f1 and f4, horn jab se f1, f3
     and f4.
2. **Broken parts (plates, gems, faces):** `ape_l/take-a/anim/back_plate.py`.
   - Cut the part from the still (its colours plus the ring they enclose), find it in each frame by matching the
     still's gem mask within 10 px, paste it there, then clear the box above it and dark texels stranded next to
     it.
   - Frames whose part already matches the still at 0.9 or better are left alone. Broken frames measured 0.76-0.80.
   - Cut with a square dilation (7 px) so corners such as the bezel's cap are included; a diamond cut them off.
3. **Shoulder line (rhino front):**
   - Geometry first: `retro-walk/pixellab/fix_front_shoulders.py` restores the still's shoulder plates.
   - `front_shoulder_ink.py` draws a domed dark arc over each knee-disc plate and lifts the texel under it to the
     highlight.
   - Where that can't fit the pose (braced, rearing), `shoulder_transfer.py` copies the line from the nearest frame
     that has it (match 0.76-0.87 on the braced shuffle).
4. **Detail ink:** `detail_ink.py` uses only the contour part of the Hollowtide detail-ink rule, in the machine's own
   darkest colour (`darkest()`). It brings a view up to the liked views' interior ink share and no further. The full
   rule (22-28%) was rejected.
   - **Gate with a margin:** ink a view only when its share is clearly below the target (under about 0.75 times).
     A view a point under the target doubled its ink and grew hard rings (the gorilla's n and ne trial).
5. **Seams:** each Codex set's `seam_fill.py` fills runs of 4+ transparent texels with ink on both sides. The
   originals go in `frames_pre_seam/`.
6. **Walk upper body (front, back):** `walk_to_still.py` puts the still's upper body, moved by each frame's bob,
   over the walk's own legs (section 9, step 7). Use it on any walk whose body drifts from the still.
7. **Idle:** `diag_idle.py` builds the idle from the approved still: the body above a cut row 13 px over the feet
   rises 0, 1, 1, 1, 0 px, the cut row is repeated to close the gap, and the feet never move.
   - Never rerun `fix_set.py` on an idle: it rebuilds from Codex's frames.
   - **Views drawn from the game camera (35 degrees):** set the cut per view. Far feet sit up to about 30 rows above
     the feet row there, so a fixed 13-row cut lifts them. The rhino's cam35 idle cuts at s 152, se 131, e 141,
     ne 131 and n 142, chosen on a marked strip of the lower bodies. A gap search by run count mistook the horn,
     jaw and tail for leg gaps. (`rhino_l/take-a/anim/cam35-idle/build_cam35_idle.py`, 2026-11-04.)
8. **Sel-out:** last, at pack time. `selout_rhino.selout()` with `selout_rhino.OUTLINE` set to the machine's darkest
   colour (rhino #141218, gorilla #141a16, fennec #141218). The rhino also keeps `frames_selout/`. Rerun after any
   frame fix.

**Last finishing step: a Codex repair pass (fennec, 2026-11-04).** Codex's finishing pastes native parts from the stills (face, ears, discs, tail pieces) onto generated bodies, and where they do not line up it leaves cutoffs: straight cut edges, a second chin under the pasted head, chopped haunches, gaps and spurs. Preston: "Too many cutoff etc." Deleting pixels (diag-touchup/touchup.py) only removes the leftovers; the cut areas need redrawing. What worked: a Codex job per two sets with no image calls, starting from the current frames (never rebuilding from raw sheets), keeping originals in frames_pre_repair/, judging boards with sel-out at 4x. Fennec: sets A+B 45 of 153 frames, 147,657 tokens; sets C+D 43 of 102 frames, 189,814 tokens (fennec_s/take-b/anim/make_codex_repair_fennec.py, repair-ab/, repair-cd/). Budget it with every new machine's sets.

Retro Diffusion custom_action on the fennec (sand kick, n and ne, $0.25 each) failed both views: from frame 2 it
stood the fox on its hind legs with clawed arms. Retro walking held the fennec's back and ne. Check a style's
price with estimate_inference_cost for each style, not only the first. (`fennec_s/take-b/anim/retro/RUN.md`)

## 5. Checks, with the numbers that passed
| Check | Pass |
|---|---|
| Feet on the foot row, every frame | bottom row 160 (161 under a light edge); list any dip |
| Air and underground frames | named in the packer; the gorilla bound's air frames bottom at 132-148, the fennec pop-out at 140-150; dug-in frames never below 160 |
| Frame 0 (and the end frame of moves that end on the still) | identical to the still (IoU 1.0); the old Codex idle matched only 42-62% of pixels, which caused the pop |
| Gait (a walk alternates) | about -0.7; not valid for three-quarter views, judge those on the board |
| Alpha IoU against the still | 0.87 or higher |
| Interior ink share against the still | rhino front 6.8-6.9%, side 10.0-10.2%, back 10.1%; gorilla s 10.9, se 9.1, e 9.5, ne 8.3, n 9.0% |
| Part match (plates, gems) against the still | 0.9 or better; broken frames read 0.76-0.80 |
| Colours | the machine's palette only, eyes kept, no new parts |
| Facing | exact share well above the mirrored ref |
| Pack check | each packer's `check()`: frame counts match the timings, f0 = still, feet rows; prints `check: OK` |
| Engine | `rhino3d_check.gd` / `ape3d_check.gd` with `--headless --fixed-fps 60`, 0 failures |

## 6. Speed: the drawn stride has to match the movement
- **Measure the stride:** `tools/debug/walk_stride_measure.py <frames dir> side --fps N` gives the speed a planted
  foot moves at the drawn frame rate.
- **The rhino walk:** planted feet move at 0.48 m/s, while the placeholder movement speed is 3.5 m/s. Unless the
  two match, the feet slide. Settled 2026-11-04, Preston: "Keep 0.48 m/s"; game feel plays the walk at
  `full_speed_walk_rate = move_speed / 0.48`.
- **The braced shuffle:** drawn by Codex from brace f3 (set D). The planted feet slide 2 px a frame, which is
  0.40 m/s at 10 fps; braced movement is 1.225 m/s, so the feet slide about 3x. Open as of 2026-11-04: slow the
  brace to 0.4 m/s or accept the slide. Preston picks.
- **The fix options:**
  - slow the move;
  - raise the playback rate (`speed_scale`, `full_speed_walk_rate`);
  - draw a longer stride or a faster gait.
- **Engine rules that hide seams:**
  - Turning mid-step keeps the step: the new view picks up at the same frame.
  - A held action (brace) plays its `<action>_shuffle_<view>` while moving, and plants the held frame again on stop.

### 6b. Walks drawn at 35 degrees (rhino, 2026-11-04, installed)
- **Scripts** (`rhino_l/take-a/anim/`): `make_walk35_rhino.py` (refs, `walk35/targets.json`, guides, the two Codex
  briefs), `make_walk35_clean_rhino.py` (leg cleanup brief), `make_walk35_review.py` (review video),
  `walk35_selout.py`, `walk35_touchup.py`. Frames: `walk35/walk/frames`, with every earlier stage kept beside them.
- **Gait (four-beat walk):** LF swings f1-f3, LH f3-f5, RF f5-f7, RH f7-f1. One foot is up on even frames, two on
  odd frames (not "one at a time"; Codex caught that wording). Stance offsets +2P, +P, 0, -P, -2P; swing -P, 0, +P
  with lifts 2, 3, 2 px. P = 3 px a frame in the side view at 8 fps = 0.48 m/s at 0.020 m a texel.
- **Camera axis per view:** a ground step d shows on screen as d x f x u. e: u (1, 0), f 1; se: (0.867, 0.497),
  0.815; ne: (0.867, -0.497), 0.815; s: (0, 1), 0.574; n: (0, -1), 0.574. Planted step per frame on screen = -P x f x u
  (e -3, 0; se -2.12, -1.22; ne -2.12, +1.22; s 0, -1.72; n 0, +1.72).
- **Foot lock in the brief:** the k-th planted frame sits at the plant position minus k times the planted step.
- **Legs:** taken from the still's own pixels and TRANSLATED, never rotated. Rotation left speck noise and needed a
  cleanup pass. Joints hand-drawn; the body pixel for pixel with a 1 px dip on f0 and f4.
- **Cost:** run 1 (e, se, ne) 102,921 tokens, leg cleanup 78,180, run 2 (s, n) 93,859: 274,960 in all. Runs were
  capped by a token watcher (Codex rollouts in `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`; tokens = input -
  cached + output, which matches Codex's "tokens used"; kill the tree at the cap). Tools: `walk35/codex_cap/`
  (`run_codex_capped.sh`, `codex_tokens.py`, and `run_rhino_walk35.sh` as the worked example).
- **Result:** foot lock e 0 px, se/ne under 0.9 px, s/n 0.88 px in y; front and back steps are small (about 3 px
  lift, 3.4 px travel). Body equals the still.
- **Review:** `make_walk35_review.py` plays 8 fps over a dot grid that scrolls at the planted step along each view's
  axis, the still beside it; a locked foot moves with the dots, a sliding one drifts.
- **Build from the newest approved views.** The walk was drawn from `views_cam35` after Preston kept the touch-up
  (`views_cam35_touchup`), so walk and idle differed in colour and the back flickered at n. `walk35_touchup.py`
  recoloured it by source position (Preston: "Looks right"). Look for a `*_touchup` folder before writing a brief.
- **In game:** `tilt_anims` includes `walk`. Toes reaching toward the camera draw 2-3 px under the foot row (raw s/n
  163, se/ne 162; one more with sel-out); the floor hides 0 rows (game feel). Walk and idle both end on row 161 with
  sel-out, so the walk needs no lift. Walk-to-idle plant gap 0.000 m in all views (camera lane).
- **Wolf:** the se/ne trot (`wolf_m/take-b/anim/make_codex_walk4_wolf.py`, 116,093 tokens) and the retimed
  front/back (`retime_walk.py`, pairs on f0/f4) are at the old angle. No 35-degree wolf walk yet.

## 7. Packing and the engine
- **Packers** (`tools/art/`), one per machine: `pack_rhino_3d.py`, `pack_ape_3d.py`, `pack_fennec_3d.py`.
  - Each has `STILL_AT` (the offset), a `KIT` list of (name, ms per frame, loop), `SET_OF` (which Codex set folder),
    and `DIAG_SET` for se/ne. A frame lasts ms/100 ticks at speed 10.
  - The ape and fennec packers pick up se/ne rows by themselves once `<view>_f0.png` exists in the set named in
    `DIAG_SET`; until then the walk plays the side walk and the idle the still.
  - `still()` takes the approved views for every facing.
  - **Rhino:** run only `pack()` (`cd tools/art && python -c "import pack_rhino_3d as p; p.pack()"`). Its main block
    also runs `fx()` and `kit_art()`, which write other lanes' folders.
- **New PNGs:** they need `Godot --headless --path . --import` before a check or a recording sees them.
- **Recording:**
  - Movie Maker: `--resolution 1280x720 --fixed-fps 30 --position 20000,20000`.
  - Then ffmpeg libx264 at crf 20, plus a phone copy at crf 27 with `-preset slow` and `+faststart`.

## 8. Safety: keep every stage
- Every batch edit first moves the originals into a sibling folder. Names used so far:
  - `frames_codex/`
  - `frames_pre_codex/`
  - `frames_pre_retro/`
  - `frames_pre_seam/`
  - `frames_pre_still/`
  - `frames_pre_eyes/`
  - `frames_pre_plate/`
  - `frames_pre_still_body/`
  - `pre_shoulder/` (`front_shoulder_ink.py` restores from it first, so remove it before rerunning on purpose)
- Ink or style trials run on copies, never on `art/machines/*/` views or the approved stills.
- **Before a repack, check the stills' timestamps against the packed sheet.** On 2026-11-04 a rejected ink trial
  overwrote the gorilla's n and ne stills. Frame 0 of every Codex set equals the still, so the exact originals were
  recovered from the frames (561 and 518 px differed, every one of them ink).
- After any restore, prove it is pixel-identical to the backup (0 px differ).
- **When a still changes under drawn frames** (the sprite factory's capped ink on the fennec n +49 px and ne +50 px,
  2026-11-04): `fennec_s/take-b/anim/ink-carry/carry_ink.py`. Frames equal to the old still become the new still;
  in every other frame each ink cluster is carried with its part (the old still's pixels around it matched within
  6 px, 85% or more), only onto opaque texels. Built-from-still idles take all of it; redrawn Codex parts take what
  matches. Originals in `<move>/frames_pre_ink/`, log in `carry-log.json`.
- Don't rerun `tools/art/pack_ape_fx.py`: it overwrites the `ape_still_*` backups.

## 9. The rhino walk, start to finish
**The rule to carry forward:** for a straight front or back walk on a four-legged machine, take the gait from an
approved side walk and pose it frame by frame. Don't prompt for it. Then put the still's upper body back over the
posed legs (step 8).

1. **Side and se were the easy part.** Retro Diffusion's walking style gave side and se walks that read as walks; the
   legs are spread apart from those angles.
2. **Straight front and back failed five times:** Codex twice (walk A weak, walk B floating 6-7 px with mismatched
   pairs and shortening legs), Retro twice, and text-prompted PixelLab once (it grew about 9 px taller mid-step and
   sprouted blue claws like arms). From straight in front or behind the legs stack, so every tool moved both legs
   together, stretched them, or invented parts. `walk_frontback.py` (a bob from the side row, whole-leg lifts in
   diagonal pairs) was a stopgap.
3. **The fix: PixelLab pose-guided** (`animate_with_skeleton_v3`, beta, built around a human skeleton). Preston:
   "that ended up fixing the gallop to a consistent walk".
   - Give it the leg position for every frame instead of describing the walk. Copy the positions from the approved
     side walk, so the gait matches by construction: `front_skeleton.py` built `front_keypoints.json` (8 frames) from
     the side walk's timing.
   - Map the front legs to the skeleton's arms and the back legs to its legs.
   - Cost: 3 free generations per view, about 4 minutes each. Run one view at a time.
   - Result: the first front walk from any tool that kept the rhino intact and stepped one leg at a time. Same size
     and shape as the still, rhino colours only, red eyes kept, nothing grown, gait check read it as a walk (back
     -0.72); the body stayed put and the head leaned slightly toward the planted foot. Alpha IoU against the still
     0.87-0.99.
   - `finish_pixellab.py`: colour snap, eyes and outline, no grounding. The forward foot dips up to 4 px below the
     line as perspective; grounding every frame would make the body bounce.
   - Preston: "yes run back and ne that looks great though". The same method made back and ne.
     `retro-walk/walk_final.py` assembled all five (PixelLab front, back, ne; Retro se, side).
4. Swapped in. `fix_front_shoulders.py` restored the still's shoulder plates (PixelLab had stretched them into the
   knee), and detail ink went on front and back.
5. **Codex consistency pass:** Codex took the pose-guided front, back and ne frames as its input and the Retro se and
   side as the look to match, with the same pose, the same foot rows and alpha IoU 0.97 or more against each input.
   So the live walk's gait is the pose-guided one; Codex only restyled shading and ink. The front shoulder line went
   on after (`front_shoulder_ink.py`, 8 frames, 0.0% mismatch). The pre-Codex walk is in
   `codex-set-a/walk/frames_pre_codex/`.
6. The idle was rebuilt from the approved stills (`diag_idle.py --set-a`): ink matches (front 6.9%, side 10.2%, back
   10.1%) and f0 is the still. That moved the pop to the moment the walk started, because the restyled walk matched
   the stills on only 59-66% of pixels (front chin plate smaller, back tail plate a round knob).
7. **Upper body back to the still** (Preston: "fix em up with our tools as well"): `walk_to_still.py` takes the
   still's head, horn, chin plate, shoulder blocks, rump and tail plate, moved by each frame's bob (front dx 0-2,
   dy 1; back dx 1-2, dy 2-3), and keeps the pose-guided legs from each knee-disc top down (rows 133-139) and the
   middle band below row 150. The idle-to-walk switch no longer changes the upper body. The shoulder line now comes
   from sel-out over the still's shoulder blocks, which are silhouette in its geometry. `rhino3d_check` 0 failures.
   Originals, with `pre_shoulder/`, are in `codex-set-a/walk/frames_pre_still_body/`. Board:
   `walk-to-still-board.png`.

## 10. A new machine, step by step
1. Approved stills for s, se, e, ne and n. Record the canvas, the foot row and the offset to y=160 (section 2).
2. Agree the animation names and key frames with the game feel lane, which owns the mechanics.
3. Generate motion. Walks: the side and se from a walk tool, then front, back and ne pose-guided from the side
   walk's keypoints (section 9). Abilities: Codex sheets in front, side and back first (sets A and B), se and ne later (sets C and D) from the
   same column text. PixelLab posed for walks that hold the design. A script for idles. Quote the cost first.
4. Finish in the order of section 4.
5. Run the checks in section 5, plus the stride against the movement speed in section 6.
6. Make a board with the still in column 1, and Preston picks.
7. Write the machine's packer from the closest one, pack, import, run the engine check, and record if asked.
8. Log the run in the machine's `RUNS.md` or the set's `REPORT.txt`, and update this playbook if anything new was
   learned.

## 11. Effects next to a tilted machine (fennec small gate, 2026-11-05)
- Draw an effect at its machine's texel (S 0.016 m), not the 0.02 m fx grid, so it reads as the same pixel art beside
  the body. Use only the machine's palette, with its darkest colour as the outside ink.
- Stand upright effects on `tilted_fx_3d.gdshader` (the machines' tilt vertex with blended alpha). It faces the camera
  from every side and sorts like the machine. A see-through middle (alpha 0.7-0.95) lets the body show when the effect
  stands between it and the camera, which is how the gate makes the cast read from the n view.
- Spawn on the action's key frame through `_at_frame`. It lands one game frame (33 ms at 30 fps) after the sprite
  reaches that frame, because the helper polls each frame.
- A scripted run turns the machine to the mouse on keys 1 to 5. Call the kit function directly, or set
  `aim_screen_override` (see `tools/debug/aim_check.gd`).
- Two `--import` runs at once crawled for 10+ minutes on this machine. Run one, and wait for a gap when other lanes
  are using Godot.
- (Fennec bolt, 2026-11-05.) A new `class_name` is unknown to Godot until the editor or an import refreshes the class
  cache. Naming the new class in another script, or using it as a value in its own (`FennecBolt.new()`), fails to
  compile, and that takes down every script that depends on it: `arena_play` would not load for any lane until it was
  fixed. Refer to a new script by path (`const Bolt := preload(...)`, `load(path).new()`) until the cache knows it.
- A projectile at the game camera needs about 10 texels of body. The first bolt was 7 texels wide and read as a line,
  and its dark violet (`VIO_D`) tail disappeared on the arena floor's blue. What worked: a wider head, a 1-texel mint
  glow at alpha 0.4 outside the ink, a mid violet tail with a lilac centre line, and a white pulse that moves along the
  tail each frame, so the frames differ.
- Draw a flying sprite at 16 screen angles from its shape, not by rotating pixels, and show the one nearest its flight
  as projected on screen (`unproject_position` of its position and one metre ahead). It then points the way it flies
  from every view, toward the camera included.
- The chase camera keeps the machine above the middle, so only about 3 m of floor show toward the camera. A target
  there either stands under the screen's edge or hides the strike behind itself. Test the shot toward the camera with
  no target, and check that it flies its full reach.
- Blended effects sort by distance. A bolt leaving the gate's far side is drawn under the swirl for the first metre;
  that is right for an exit through the far face, but it hides the bolt for a few frames from the view behind the gate.
- (Fennec blink flash, 2026-11-05.) For a flash of the machine itself, draw its current frame in light rather than a
  drawn shape. `BlinkFlash` puts the sprite's atlas frame on a quad with `tilted_fx_3d.gdshader` (tint, rim, fade,
  scan; mirrored by flipping the cell's UVs), so the light has the machine's outline in every view and pose. A drawn
  column of light in its place read as a pill.
- When the body appears out of light, keep it hidden until the light covers it at full width. Showing it under a
  narrower ghost let its ears and tail stick out past the white.
- Two siblings added with the same name: Godot renames the second (`@MeshInstance3D@n`), so a test that finds nodes by
  name misses it. Give effect nodes distinct names (`BlinkGhostOut`, `BlinkGhostIn`).
- Adding settings to a shared effect shader: keep the defaults identical, then compare frames from before and after
  pixel by pixel. The bolt and gate frames came out identical (0 differing pixels).

## 12. Moves at 35 degrees after the idle and walk (animation lane, 2026-11-05)
- **Order.** `docs/art/moba/kit-anims-35-plan.md`. Idle, walk and death can go now. Kit moves wait until that
  machine's kit is redone to the power-theme rule in `docs/plan/moba-kits.md`, or they get drawn twice. Only the
  fennec's kit is redone (portals).
- **Free before paid.** Breath, ear stretch, glow and charge loops come from the approved views by script
  (`tools/art/build_idle35.py`, `tools/art/build_cast35.py`). Codex is for new poses: 100k-280k tokens for one move in
  5 views at 35 degrees, each run on Preston's direct yes.
- **Codex runs** go through `rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped.sh`, which runs from
  `D:/dev/_scratch/codex-cwd` (not a repo). An app restart kills the token watcher: find the codex PID by start time
  and watch it again before the run passes the cap. The cap can overshoot by about one full context (~75k): the
  walk lane's hippo run 1, capped at 160k, ended at 224,713, because one Codex step counted ~75k between two
  watcher reads 20 s apart. Faster polling can't stop a single step, so set the cap about 75k under the number
  quoted to Preston, or quote him cap + 75k as the worst case.
- **Count pieces with 4-connectivity.** 8-connected, a Codex death looked like one piece a frame; 4-connected it was
  up to 11, joined only at corners. Preston called it "a mess". The fix that passed: a free cleanup, then a PixelLab
  `animate_with_skeleton_v3` redraw of the worst view (the front) by the touch-up lane.
- **Which still f0 must equal.** Moves drawn at 35 degrees start on the 35-degree still (the touch-up views); the
  old-angle kit still starts on `views/`. The packers keep both (`STILLS`, `OLD_STILLS`) and check each against its own.
- **160 canvas frames** (the fennec's stills and death35) are placed at `STILL_AT` (16,20) in the 192 cell; touched-up
  walks are already 192 and go in with no offset.
- **Tilt.** A move drawn at 35 degrees goes in `metadata/tilt_anims` (matched by the name before the last "_"); an
  old-angle move must stay out of it.
- **Ground rows.** Packed 35-degree walks plant their stepping near foot up to 4 rows below 160 (157-164); the camera
  lane measured this as correct (the foot steps toward the camera), so walk checks allow it. A death's hit jolt may
  lift 1 px.

**Arrival shield (fennec effect 4, 2026-11-05):**
- An effect worn by any machine is drawn in texels and laid on at the wearer's texel (`sprite.pixel_size`). One sheet
  can then serve every class whose bodies are about the same size in texels. Measure the bodies over every frame of
  their sheets first: the fennec (S) reached 83 texels up, the rhino (L) 107, so there are two shell sizes, not one
  shell scaled.
- To draw over the body it surrounds, move the quad toward the camera along its own sight line (0.15 m). It stays in
  the same place on screen, and the body's depth no longer cuts it.
- Afterimages: start each one behind the body on the camera's sight line (0.25 m), so it shows only once the machine
  walks on, with no flash of mint over the body. At a slow walk, 0.1 s apart and 0.25 s long they hid behind the body;
  0.065 s apart and 0.4 s long read.
- A parse error in a script that the clip test preloads breaks `arena_play` for every lane, because arena_play makes
  the test by its class. Run `--check-only --script` on new scripts before the first game run.
- Saving whole 1280x720 frames costs about 0.7 s each. A 650-frame test ran past its 500 s limit and lost its log. Save
  the screen region the clip needs.
