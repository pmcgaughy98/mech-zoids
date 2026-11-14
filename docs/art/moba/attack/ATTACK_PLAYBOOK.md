# Attack playbook (attack lane)

How to make a machine's attack animation at 35 degrees, check it, price it and pack it. Started 2026-11-05 by the
attack lane (Preston: "make a session for attack animation"). The run log is `LOG.md` in this folder. Update this
file whenever a lesson changes.

**Sources.** Read this session: `../ANIMATION_PLAYBOOK.md` (all), `../walk/WALK_PLAYBOOK.md` (all),
`docs/plan/moba-kits.md` (all), the rhino ground pound history (`rhino_l/take-a/anim/codex-ground-pound/clean/REPORT.txt`,
the first sections of `rhino_l/take-a/anim/forge/RUNS.md`), `rhino_l/take-a/views_cam35_touchup/APPROVED.txt`,
`rhino_l/take-a/cam35/APPROVED.txt`, the walk lane's token lines in `../walk/LOG.md`, `pack_rhino_3d.py` (KIT lines) and
`scripts/moba3d/rhino_kit.gd` (slam frame). General knowledge, not read this session: the animation principles
(Thomas and Johnston, *The Illusion of Life*), Richard Williams, *The Animator's Survival Kit* (anticipation, contact,
holds, follow-through), the rush, hit and return frame markers in Explorers of Sky's sprite animation data (structure
only), fighting-game frame data (startup, active, recovery), and MOBA telegraph practice. Those parts are marked as
proposals. Nothing here is canon until Preston says so.

## 1. Rules that bind every attack
- **Attacks are made the attack way, not the walk way** (Preston, 2026-11-05: "do it like how we made the other attack
  animations not the way you do with walking animations"). That means Codex draws the move's new poses in one image
  per sheet from the approved stills and the move in words, column by column, then the finishing steps of
  `ANIMATION_PLAYBOOK.md` section 4 (eyes, broken parts, ink, seams, a repair pass). The second sheet reuses the first
  sheet's column wording word for word. Pixel-moved blocking, walk-style foot targets and pose silhouettes are not the
  method; numbers are checked on the finished frames.
- **Build on the newest approved 35-degree stills**, and match them exactly above the moving parts. The idle uses those
  stills, so any difference pops on the switch. Look for `<take>/views_cam35_touchup/APPROVED.txt` and ask the touch-up
  lane ("Touch up mech sprites in Aseprite") which set is current. Rhino: `views_cam35_touchup`, confirmed by the
  touch-up lane 2026-11-05 (raw, no outline; the packer adds sel-out).
- **Old-angle frames are history, never a base.** `codex-ground-pound/`, `codex-set-a` to `-d` and the forge sheets
  say what a move does and what Preston said about it. Their frames and their pixel numbers are at the old angle and
  are not used for frames or targets. (Preston, 2026-11-05: "You are using old map old animations not at 35 degree
  look".) Check with the lanes which map and which animations are current before planning.
- **The current map is `scenes/moba3d/arena_play.tscn`** (it instances `arena_blockout.tscn`; layout
  `docs/plan/moba-arena-layout-2026-11-04.md`, owned by the map lane). Videos and in-game looks for Preston are taken
  there, never in `ape_field_test`, `rhino_walk_test` or the `*_reveal` scenes (hub, 2026-11-05). The headless
  `rhino3d_check.gd` and `rhino_feel_check.gd` load `field_test.tscn`, the simple place game feel uses to test one kit.
- **What is at 35 in the game** is the `metadata/tilt_anims` list in `art/machines/<m>/<m>_frames.tres`; everything not
  in it is still at the old low angle. On 2026-11-05: rhino idle, walk (old: ground_pound, horn_jab, horn_toss,
  stampede, brace, brace_shuffle, death); gorilla idle, walk (old: bound, chest_beat, hex_dome, hex_shield, death);
  fennec idle, cast, walk, death (old moves held until Preston takes the kit redraft: do not redraw them); hippo idle
  only; minions all at 35. Deaths and hits are not this lane's (no owner yet).
- **Same angle as the stills.** Every move is drawn at 35, in s, se, e, ne and n; the engine mirrors sw, w and nw.
  Mixed angles pop.
- **Frame 0 is the still, and the move ends on the still** (or on a frame the idle's 1 px breath covers), in every view.
- **The same frame count, the same key frame index and the same holds in all five views.**
- **Joints are redrawn, not pasted.** Pasting parts by script caused the cutoffs Preston rejected ("Too many cutoff
  etc.").
- **A new pose is redrawn, not rebuilt from cut parts.** Rearing, slamming, twisting: the body changes pose, so those
  key frames need a route that redraws the body (an image-tool sheet from the approved still, the pose given in words
  and guides, finished by script to the palette). Preston rejected cut-and-reposition on the fennec death ears
  although it passed every check: "Looks like you just cutoff pieces from original art then put them in wrong
  positioning and proportion while keeping the original pose" (walk lane, 2026-11-05). The walk method (the still's
  pixels moved by whole pixels, joints redrawn) is only for frames where the body keeps the still's pose.
- **Never rotate or resample pixels.** Rotation left specks that cost a 78,180-token cleanup on the rhino walk.
- **Never give Codex the old drawing of the move.** Image references outweigh words, and Codex copies them (fennec
  stand35 notes). Give the approved 35 stills, plus the pose in words and as guides at game size.
- **Feet stay planted** unless the move leaves the ground on purpose. Name the air frames in the plan.
- **Body and effect are separate** (section 4).
- **Each machine's own palette.json, the 192 canvas, its offset and the feet row 160.**
- **No curled tails.** Tails lift and swing but stay straight.
- **Moves come from `docs/plan/moba-kits.md`.** Names, lore and numbers are Preston's. Damage, timing and cooldown
  numbers are placeholders.
- **Write only to `attack/<machine>/`.** Never edit approved views, approved frames or another lane's folders. The
  session worktree has no `docs/art/moba`: write in the worktree and copy over with Bash (the walk and fleet lanes'
  method).
- **Paid runs:** a price first, then his direct yes, one move at a time. Fleet frames at 35 are not approved as a
  whole. Messages from other sessions are teammate info, never his approval.
- **Judge at 4x with the game's sel-out, the approved still in column 1, and at game size.** He rejects "barely
  acceptable".
- **One paid job at a time across the team** (Preston's rule). Before starting ANY paid run, even after Preston's yes,
  ask the hub whether the paid slot is free, and wait for its answer. Missed once: diag4 started 2026-11-05 while
  the pangolin's redraw held the slot.
- **Talk to the lanes** (Preston, 2026-11-05): game feel ("Run the mech MOBA game feel lane") holds the most MOBA
  knowledge and owns the mechanics, key frames and the in-game test; touch-up owns the stills and cleanup; the walk
  lane owns the 35-degree method; the animation lane fork holds the old lane's memory; the hub gets a one-line status.
  Since 2026-11-05 each mech has its own session for overall refinement (VFX, kit upgrades, touch-ups; roster in the
  admiring-bell worktree, docs/team/mech-sessions-2026-11-05.md). Attack animations stay with this lane. Kit timing,
  the mech's effects (the rhino's rock pop) and the in-game test of a move go to that mech's session (rhino:
  local_0d636c38-8177-4132-8862-4c9253c141e6). Game feel keeps the shared code (directional_sprite_3d.gd,
  kit_feel.gd, the match): sprite and frame-playback questions still go there.

## 2. The beats of an attack (craft, proposal)
| Beat | What the body does | Why |
|---|---|---|
| Rest | f0, the still | the idle hands over with no pop |
| Anticipation | moves the other way first: gathers, sinks, weight onto the feet that stay planted | the telegraph: in a MOBA the enemy reads the wind-up and can react |
| Action | as few frames as possible, big spacing (one in-between or none) | speed reads as power |
| Impact (key frame) | the lowest or most extended pose; the frame the game hits on | the game's hit frame (`_wait_frame`, e.g. `POUND_SLAM_FRAME`) |
| Hold | the impact frame held longest | hit stop: the eye needs time to read the contact |
| Follow-through | loose parts (head, tail, cables) overshoot by 1 px and settle a frame after the body | weight, and the machine stays one object |
| Recovery | eases back to the still | a clean hand-back to the idle |

- **Frame data view** (fighting games): startup = rest plus anticipation plus action, active = impact plus hold,
  recovery = follow-through plus recovery. Explorers of Sky marks the same points in its sprite data as a rush frame,
  a hit frame and a return frame. Agree those three frame indices with game feel before drawing.
- **Spacing:** slow out of the anticipation, fast into the impact, slow into the still.
- **Silhouette:** the anticipation and impact poses must read as a different shape from the still at game size. Check
  a black silhouette strip at 1x.
- **Arcs:** the head or horn tip travels on an arc. Trace one point per frame and look for kinks.
- **Weight by size:** L lifts less, lands harder (a body drop on impact) and holds longer; S is quicker with more air.
  Armour never squashes; the drop comes from the legs bending, and those knees are redrawn.
- **Overlap:** the head lags the body by one frame, the tail by one frame, 1 to 2 px.

## 3. Geometry at 35 degrees
- **Ground moves** show on screen as d x f x u (walk playbook section 7): e u (1, 0), f 1.000; se (0.867, 0.497),
  0.815; s (0, 1), 0.574; ne and n the same with y negated.
- **Vertical moves show the same in every view:** a lift of h texels shows as h x cos 35 = 0.819 h px straight up in
  s, se, e, ne and n. So a front-foot lift or a body rise must measure the same on screen in all five views (gate in
  section 5).
- **A rear-up about the hind hips** (pitch t): a point L texels ahead of the hips rises L sin t (0.819 of that on
  screen) and pulls back L (1 - cos t) along the body (x f x u on screen).
- **In s and n the pull-back shows as vertical motion.** In s the front end pulls back away from the camera, which is
  up on screen, so it adds to the rise (0.574 x the pull-back); in n it pulls toward the camera, down on screen, so it
  takes away from it. Put the per-view numbers in targets.json; the redraw follows them.
- **Toes toward the camera** may draw 2 to 3 px under the feet row (rhino s and n 163, se and ne 162); list them.
- **The game camera is 30 degrees and the art is 35** (game feel, 2026-11-05). Check the move in the game view.

## 4. Body and effect
- Body frames hold no effect pixels. The body moves its approved pixels; the effect is its own sprite or a Godot
  particle.
- **Ground effects** (rings, cracks, dust patches) are laid flat by the engine (`Fx3D.spawn_flat`), so they do not
  depend on the art angle. **Upright effects** stand on `tilted_fx_3d.gdshader` and are drawn at the machine's texel,
  in its palette, with its darkest colour as the outside ink (animation playbook section 11).
- Spawn on the key frame through `_at_frame` (it lands one game frame late at 30 fps).
- A flash of the machine itself uses its own frame in light (the BlinkFlash method), not a drawn shape.
- Effect tools: Aseprite, PixelLab vfx_workbench (check its own free note), Godot particles with game feel, the Opal
  Effect forge (shuts down 2026-11-17). Grok is not for these.

## 5. Gates for every attack
| Check | How | Pass |
|---|---|---|
| Start and end | diff against the still | f0 0 px differ; the last frame 0 px, or a whole-body shift of 1 px the idle covers |
| Above the moving parts | undo the planned move (translation or the named band steps) and diff | 0 px differ |
| Planted feet | `walk_tools.py footlock` with a targets.json of the planted soles | drift 1 px or under across the whole move |
| Lifted feet | sole centre per frame | lift within 1 px of the plan; lands back on its still sole within 1 px on the impact frame |
| Lowest row | per frame | 160 (161 with sel-out); toes toward the camera listed |
| Air frames | named in the plan and the packer | only those leave the row |
| Cross-view | frame count, key frame index, holds; screen lift / 0.819 | identical; the same world lift within 1 px in all five views |
| Parts (eye, horn, plates, gems) | match against the still part | 0.9 or better wherever the part shows; the eye in every frame the still shows it |
| Palette and pieces | colour set, alpha, connected pieces, canvas edge | the machine's palette.json only, binary alpha, one piece, no edge contact |
| Seams | `walk_tools.py seams` | no slit inside the body; look before any `--fix`, one pass only |
| Readability (proposal) | silhouette IoU against the still at 1x | anticipation and peak 0.90 or under; impact body drop 2 px or more on L |
| Hand-back | onion skin of the last frame over the still, and over idle f0 | no jump |
| Eye | board at 4x with sel-out, still in column 1; a 1x strip; a 5x zoom of every joint; a phone video | Preston picks |
| Game | packer `check()`, `--import`, `rhino3d_check.gd --headless --fixed-fps 60`, then game feel's in-game test | `check: OK`, 0 failures |

Run `--check-only` on any new GDScript before a headless run, and give every long headless run a timeout: a parse
error hung match_check for 33 minutes on 2026-11-05 and blocked every lane's Godot. In-game tests run in
`arena_play.tscn`.

### Lessons from the other lanes (2026-11-05)
- **The kit fixes the frame indexes.** The code holds named frames (`POUND_SLAM_FRAME`, `POUND_RISE_FRAME`,
  `hold_frame`), so the frame count and the key indexes are game feel's contract, the same in every view. Example: the
  rhino tremor toggles F5 (0.12 s) and F4 for each stomp, so F5 must sit close to F4.
- **Scale a re-posed sheet by the head, not the body length.** The fennec scaled by length came out with its head 8%
  small.
- **Put a draw order per view in the brief** (far limbs, tail, body, near limbs). Without one the fennec's ne far hind
  leg was drawn over its tail.
- **Plates and discs belong to the body.** Where a limb uncovers one, draw it whole with its bands.
- **Number gates work; "make it clean" does not.** Give Codex counts (pieces per plate, light pixels in a box, specks
  no more than the still plus 2).
- **Count pieces 4-connected.** 8-connected hid corner-only joins in the fennec death that Preston called "a mess".
- **Codex updates REPORT.txt after each part**, so a run stopped by its cap still leaves a report. Run it through the
  capped runner from `D:/dev/_scratch/codex-cwd`; an app restart kills the token watcher.
- **Generated frames come back light on ink**, with no highlight caps and grey eyes: finish to the still's ink shares.
- **A feet-planted attack must not move the machine**, or the feet slide in the game (slide = speed /
  (stride_speed x speed_scale), `machine_test_player.gd`).
- **Match the 35 idle's size and feet.** Game feel measured an idle-to-action pop of 13-22 on the fennec, strongest
  from n (`docs/art/moba/match/cam_angle_test/fennec35_action_idle_switch_2026-11-05.png`).
- **Scratch goes on D:** (`D:\dev\_scratch\attack\`); C: is nearly full.

### Lessons from ground pound run 1 (2026-11-05)
- **Back views drift toward the side view** when they share a sheet with e and se: run 1's ne row turned from F1 on
  (face showing, rump no longer to the camera, 87 px tall against 103). Give ne and n their own rows with a line
  that names what the still shows: "the rump faces the camera, the face is hidden, the horn shows over the back".
- **A hold-and-flash pair is drawn as one pose.** F4 and F5 drawn as separate poses differed by 7 to 13 px, so the
  tremor's 0.12 s F5 flash would jump. F5 is drawn from the finished F4 (same pose, one foot 2-3 px up).
- **The lowest-row gate is per sole, not per frame.** In se the near hind sole is on row 143, so a frame with the front
  feet up has 143 as its lowest row. The gate is: every planted sole on its own still row.
- **A rear target from geometry can be too timid.** 30 degrees about the hips gave 16 px; the model drew about 34 px
  in e and it reads better at 1x. Treat the lift numbers as a floor for the telegraph and let Preston set the height.
- A 3-row sheet with finishing and checks cost 106,953 tokens, at the top of the 60k-100k estimate.
- **Added parts pass the hole checks.** Run 1's F3 grew a charcoal thigh between the body and the hind joint disc,
  lifting the hips 20 px (e) and 28 px (se); Preston: "they added thighs essentially". Seam checks only find holes,
  not extra fill (the walk lane found the same with "the body stops at the belly"). Every rear gets number gates
  against the still: hind leg length from sole to disc centre (2 px), anything between disc and body (2 px), hip
  height (3 px). The prompt names the leg's parts in order and says "no thigh, no extra segment".
- **The fix worked** (fix1, 61,810 tokens): naming the leg's parts, "the hips stay at standing height", "a seesaw
  at the hips" and attaching the stills only removed the thighs.
- **Diagonal views drift to the side view on a rear**, twice now (run 1 ne, fix1 se). The prompt must pin the
  diagonal in every column: "the head and horn point to the lower right, toward the camera, as in column 1; the body
  never turns side-on". Do not put a diagonal in the same sheet as the e row.
- **The approved side view works as a pose reference for a diagonal** (diag2, 31,831 tokens draw-only): ne's rise and
  rear came out right the first time it was attached, labelled "pose only, never its facing". A draw-only run (image
  plus a by-eye report, finishing by script afterwards) costs about a third of a full run, so try a hard pose that way.
- **The image model pulls a rear toward the side view.** The se rear missed five times (run 1, fix1, diag1, diag2,
  diag3), turning side-on even when drawn alone with a pinned facing. When a generated frame already has the right
  facing and one wrong part, edit that frame (attach it, change only the part) rather than draw the pose again.
- **Rows can come out at different scales.** When the rows' column 1 heads differ by more than 6%, finish each row at
  its own head scale (the same nearest shrink, one factor per row) instead of the median. Fixed-number landmarks in an
  audit script go stale when the scale changes; re-trace them or check by eye at 5x.

### Lessons from the gorilla strike, sheet 1 (2026-11-06)

- **Don't pin the lowest pixel to the feet row on an attack.** A limb driven toward the camera sits below the feet on
  the page (the gorilla's se contact reaches row 135, feet row 130). Pinning lifted the feet. Keep each frame's own
  place in the sheet relative to column 1, then check the planted parts against the still per part.
- **If a row is drawn a little off the still** (column 1 IoU well under 0.95), move the whole row so a planted foot
  sits on the still's foot; never move single frames, which makes planted parts slide.
- **Majority-vote shrink keeps seams:** map the raw to the still's colours at full size, then each output pixel takes
  its block's most common colour, and ink is added darkest first up to the still's ink share. Area averaging lost
  two thirds of the seams. Script: `ape_l/strike35/s1/ape_finish.py`.
- Draw-only with the stills alone was enough for a punch (16,290 tokens for two rows of six).

## 6. Tools (stock-take 2026-11-05)
| Tool | Free or paid | Use here |
|---|---|---|
| This lane's scripts (`attack/tools/`, Python with PIL and numpy) | free | plan, targets, guides, blocking previz, gates, boards, videos |
| `walk/tools/walk_tools.py` | free | `soles` to label feet, `footlock` for planted feet, `seams`, `mirror` |
| Animation lane scripts in `rhino_l/take-a/anim/` (`selout_rhino.py`, `make_walk35_review.py`, `build_cam35_idle.py`, `walk35_touchup.py`) | free | sel-out, review video, idle cut rows, recolour by source; run on copies, never write into those folders |
| Codex token cap (`rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped_d.sh`, `codex_tokens.py`) | free | kills a Codex run at its cap (checks every 20 s, so a run can end about 3k over) |
| Aseprite MCP | free (local) | onion skins, frame diffs, `audit_animation`, hand-drawn joints and eyes |
| PixelLab `pixelart_workbench` | free for subscribers (its own note) | lint orphan pixels and outline gaps, inspect, repair |
| PixelLab `vfx_workbench` | check its own free note before each use | effect sprites |
| Godot 4.7.2 headless, Movie Maker, ffmpeg | free | engine check, recordings, phone video (crf 27, `-preset slow`, `+faststart`); one Godot at a time |
| Blender MCP (live link) | free (local) | possible: a blocking rig of a pose rendered from the five 35-degree cameras as guides; not tried here yet |
| Opal Effect forge (Chrome) | free | made the ground pound ring v1; shuts down 2026-11-17 |
| watch skill | free | study attacks in gameplay videos (synthesis) |
| Game feel lane | free | mechanics, key frames, particles, the in-game test |
| Codex | paid: tokens on Preston's plan | redraws the moving parts and joints at 35 (section 8) |
| PixelLab generation (`animate_with_skeleton_v3`, `animate_image`) | paid beyond the 20 free daily generations | not planned; it lost the fennec's design |
| Retro Diffusion advanced animation (attack, custom_action) | paid per run; `estimate_inference_cost` is free | not planned; custom_action stood the fennec on its hind legs with claws ($0.25 a view) |
| SpriteCook `animate_game_art` | paid credits | untried on a machine |
| Autosprite `generate_attack_moves` | price unknown | untried; price it before any use |
| Gemini API | paid | its MCP failed to connect on 2026-11-05 |
| Grok | | not for these (Preston's rule) |

## 7. An attack, step by step
1. Read the move's row in `moba-kits.md`: what it does, nothing invented.
2. Confirm the newest approved 35-degree stills with the touch-up lane.
3. Ask game feel for the key frames (rush, hit, return), the holds, the telegraph length and the effect plan. Keep
   the kit's key frame index unless game feel changes it. Ask the hub and game feel which map is current.
4. Plan, free: the frame table in words (beat, pose, holds, key frames) and the numbers the finished frames are
   checked against. Show Preston.
5. Price the Codex run (section 8: cap plus 75k worst case) and wait for his direct yes.
6. Codex sheet 1 and sheet 2, each under a token cap, one image per sheet, no redo: the stills as the look, the move
   in words column by column, the draw order per view, no effect pixels, never the old drawing of the move. Sheet 2
   reuses sheet 1's column wording word for word (and may take sheet 1's finished frames as the pose reference).
   Then the finishing order of `ANIMATION_PLAYBOOK.md` section 4, with a Codex repair pass last if the board shows
   cutoffs.
7. The gates in section 5, then the board, the 1x strip, the joint zooms and a phone video.
8. Preston picks. Then pack (backup first), import, engine check; send to game feel for the in-game test and to the
   touch-up lane for cleanup; one line to the hub.
9. Log in `LOG.md`; update this playbook if a lesson changed.

## 8. Pricing a move
Known Codex numbers:
| Run | Tokens |
|---|---|
| Ground pound, old angle, one 3-row sheet (6 frames a row) | 58,520 |
| se/ne 2-row sets at the old angle | 71,728 to 104,506 |
| 35-degree walks, 5 views x 8 frames, two runs | rhino 274,960 (with a 78,180 leg cleanup), gorilla 240,928, fennec about 241k |
| Repair pass for cutoffs (fennec, two sets) | 147,657 and 189,814 |

**The cap can overshoot by about one full context, roughly 75k tokens** (hub and walk lane, 2026-11-05: the hippo
run 1, capped at 160k, ended at 224,713; the watcher saw 149,939, then one Codex step counted about 75k, likely its
whole context re-read uncached). So quote Preston the worst case as the cap plus 75k, and set the cap about 75k under
the most he has agreed to.

One image job plus its finishing measured 54,066 (fennec stand35) and 58,520 (the old ground pound sheet); the
fennec notes put a fresh `codex exec` at 60k to 110k a sheet. Estimate for one move at 35, 5 views x 6 frames with f0
the still (proposal until the pilot measures it): run 1 (e, se, ne) 60k to 100k, cap 110k; run 2 (s, n) 55k to 90k,
cap 100k; a finish pass 60k to 110k, cap 120k, if the gates miss (every generated set so far needed one). So 115k to
190k without the finish pass and 175k to 300k with it.

## 9. Packing
- This lane packs its own moves once Preston approves them. The rhino packer is `tools/art/pack_rhino_3d.py`: its KIT
  row for `ground_pound` reads the old-angle `codex-ground-pound/clean` (front, side, back) and `DIAG` points se and
  ne at `codex-set-c/ground-pound`.
- A move drawn at 35 is packed tilted: add its name to `metadata/tilt_anims` in `art/machines/<m>/<m>_frames.tres`
  (as the walk was). A move left out of that list plays upright, at the old angle's setup.
  Where the machine's packer writes that list (rhino: `TILT_ANIMS` in `tools/art/pack_rhino_3d.py`, line 93, with
  its FEET constants, kept by the rhino session), add the name there, never in the .tres, or the next pack drops it.
  The rhino session checked (2026-11-05): `rhino_kit.gd` waits on the slam frame, not on seconds, so new holds only move
  when the slam lands. Tell the mech's session before packing.
- Before a swap: copy every file the packer will overwrite into `attack/<machine>/backup_pre_<move>35/`, and check the
  stills' timestamps against the packed sheet. Run only `pack()`; its main block also writes other lanes' folders.
  Then `--import`, the engine check, and prove a restore would be pixel-identical.
- The wolf's packing stays on hold.

## 10. The pilot: rhino ground pound
Kit: "Rears on its hind legs and slams down." Changed by Preston on 2026-11-05 to a tremor (`rhino_kit.gd`: "a bigger
circle like cabrakan"): the first slam on F4, then 4 stomps 0.4 s apart, each F5 for 0.12 s then F4. In the game
today: 6 frames drawn at the old angle, held 1, 2, 1, 3, 3, 3 ticks of 100 ms. Preston's notes on the old version
that still apply to the move: the back view must rear up on the hind legs, not lift the whole body, and the shoulders
rise with the top part. Plan and price: `rhino_l/PLAN.md`.
