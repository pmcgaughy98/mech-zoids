# Walk playbook (walk lane)

How to make a machine's walk at 35 degrees, check it, and price it. Started 2026-11-05 by the walk lane ("Build mech
walk animations", Preston: "Get a walking animations session going that is skilled up from everything we learned").
Update this file when a lesson changes. The run log is `LOG.md` in this folder.

**Sources.** Read this session: `ANIMATION_PLAYBOOK.md` (all), `cam35_fleet/HANDOFF.md`, the rhino 35-degree walk
(`rhino_l/take-a/anim/walk35/`: REPORT.txt, clean/REPORT.txt, brief_run1.txt), the wolf walk4 run
(`wolf_m/take-b/anim/codex-walk4/REPORT.txt`, brief.txt, `common.txt`), the gorilla's set A walk report, the kits
(`docs/plan/moba-kits.md`), and the game feel lane's answers on speed (2026-11-05). General knowledge, not read
this session: the four key poses (Richard Williams, *The Animator's Survival Kit*), animal gait sequences
(Muybridge's plates, Hildebrand's gait studies), and the walk-to-run Froude rule (R. McNeill Alexander). Those
parts are marked as craft proposals. Nothing here is canon until Preston says so.

## 1. Rules that bind every walk
- **Build from the newest views.** Before any frames, look for `<take>/views_cam35_touchup/` and its APPROVED.txt.
  The rhino walk was drawn from `views_cam35` after Preston kept the touch-up, and needed `walk35_touchup.py` to
  recolour 40 frames afterwards.
- **The walk and the stills share one angle.** A machine's walk is drawn at 35 degrees only once its 35-degree stills
  are approved. Mixed angles pop at every start and stop.
- **Above the legs, every frame is the still**, moved only by the bob. Then idle to walk cannot pop. The rhino's
  35-degree walk matched its still on 0% differing pixels above the legs.
- **Legs are the still's own pixels, translated, never rotated or resampled.** Rotation left specks that cost a
  78,180-token cleanup on the rhino. Where a leg leans, step its parts 1 px a row.
- **Joints are redrawn, not pasted.** Pasted parts that did not join caused the cutoffs Preston rejected ("Too many
  cutoff etc."). Every joint and every join with the body is drawn in the still's colours and bands.
- **Feet stay planted** (section 7), and the drawn stride is checked against the game's speed (section 8).
- **No curled tails.** Tails lift and swing but stay straight, with the still's thickness and plate count.
- **Palette, canvas, offsets and feet row are the machine's own.** Keep its `palette.json`; place stills on the 192
  canvas at (+16, 160 - feet row).
- **Judge at 4x with the game's sel-out, the approved still in column 1.** He rejects "barely acceptable".
- **Never write into another lane's folders or the approved views.** This lane writes to `walk/<machine>/` only.
- **The session worktree has no `docs/art/moba`.** Write files in the worktree and copy them over with Bash (the
  fleet lane's method). C: was full on 2026-11-05, so the scratchpad was not usable.

## 2. Key poses (craft, proposal)
A walk is a controlled fall caught by each landing foot. Per foot, four poses:

| Pose | What happens | What the body does |
|---|---|---|
| Contact | The swinging foot lands ahead; the other foot of that pair is at the back of its stance | Hold the still's height |
| Down | Weight drops onto the landing foot | The dip: the body sinks 1 px (L can take 2); the shoulders or hips over that foot lead |
| Passing | The swinging foot passes the planted one, at its highest lift | The body returns to still height |
| Up | The planted foot pushes off | Body at still height (rising over it would lift the head off the still; not used yet) |

- On our machines the body only translates by whole pixels; armour does not squash. The rhino's approved bob is a
  1 px dip on f0 and f4 (the frames a fore foot lands).
- Head and tail lag the body by one frame (section 5). The rhino's pose-guided front walk leaned the head toward the
  planted foot, and Preston liked that walk.

## 3. Gaits by body (proposals unless marked approved)
| Machine | Gait | Phase per 8 frames | Status |
|---|---|---|---|
| rhino (L) | four-beat lateral walk | LF swings f1-f3, LH f3-f5, RF f5-f7, RH f7-f1; one foot up on even frames, two on odd; lifts 2, 3, 2 | approved, installed at 35 |
| gorilla (L) | knuckle walk, diagonal pairs | right fist + left foot planted f0-f3, the other pair f4-f7; the fists swing as whole forearms | the set A walk (old angle) used diagonal pairs; the kit says "knuckle walking". Real gorillas use a four-beat walk: both are on the guide for Preston |
| wolf (M) | trot, diagonal pairs | pair A (near fore + far hind) planted f0-f3, pair B f4-f7; lifts 2, 4, 4, 2; P 5 at 10 fps, dips f1 and f5 (walk_tools gait trot4) | approved at the old angle |
| fennec (S) | trot | 10 fps, STRIDE 0.56 m/s in `fennec_kit.gd` | approved at the old angle; the walk is exempt from f0 = still (seated still) |
| hippo (L), pangolin (M) | four-beat walk, like the rhino | as rhino | proposal |
| chameleon (M) | slow diagonal-pair walk with a side-to-side rock | as wolf, longer holds | proposal |
| kangaroo (M) | hop: both hind feet together, tail and gloves trail | take-off f0-f1, air f2-f5, land f6-f7 | proposal; kit: "big hops" |
| squirrel (S) | hop or bound | as kangaroo, shorter air | proposal; kit: "hops and sudden changes of direction" |
| shoebill (M) | two legs: L planted f0-f3, R f4-f7, a body sway toward the planted leg | 8 frames | proposal |
| hummingbird (S) | no walk: hover drift (wing cycle plus a lean into the move) | wing cycle | confirmed: Preston took hover (2026-11-05, via the Hummingbird session); not in the walk queue. Kit: docs/plan/moba-kits.md |
| falcon (M) | check the kit and game feel (walk on talons, or a low glide) | | open |

## 4. Weight and timing by size (proposal; the rhino, wolf and fennec numbers are real)
| Size | Frames | ms a frame | Cycle | Dip | Lifts |
|---|---|---|---|---|---|
| L | 8 | 125 (8 fps), rhino | 1.0 s | 1 px (2 px on a heavy landing, such as the gorilla dropping onto its fists) | 2-3 px |
| M | 8 | 100 (10 fps), wolf | 0.8 s | 1 px | 2-4 px |
| S | 8 | 100 (10 fps), fennec | 0.8 s | 0-1 px | 3-4 px |

Heavier means longer holds on the planted feet, a lower down pose and smaller lifts. Lighter means more air and a
quicker cycle. A cycle length is a placeholder until game feel and Preston set the speed (section 8).

## 5. Overlap and secondary motion
- **Tails:** straight. They trail the body bob by one frame and swing 1-2 px sideways, opposite the hips.
- **Ears, fins, antennae and cables:** trail by one frame, 1 px. Rigid armour plates move with their body part and
  never flex.
- **Gems, lenses and eyes:** carried with their part by translation, never redrawn smaller. Check them on every frame
  (the gorilla's hex gems broke in its hex_shield ne frames).
- **Arms that are legs** (gorilla fists, kangaroo gloves): the whole forearm block moves, and the shoulder join is
  redrawn.

## 6. Loops, frames and views
- **Seamless loop:** f7 to f0 is a normal step. Each foot does exactly one swing per cycle, the planted step is the
  same across the wrap, and the dip pattern repeats. Check it with an onion skin of f7 under f0.
- **Frames:** 8 a cycle, equal timing. Walks are retimed only with Preston's word (the wolf front and back were
  retimed into pairs on f0 and f4).
- **Views:** draw s, se, e, ne and n. The engine mirrors sw, w and nw, and a turn keeps the frame index.
- **Mirror phase (in the game since 2026-11-05, Preston: "Yes, fix it"):** a mirror swaps left and right, so in sw,
  w and nw the foot that is up is the other one. `show_facing()` in `scripts/moba3d/directional_sprite_3d.gd` now
  moves a walking machine's frame to (i + 4) mod 8 (minions (i + 2) mod 4) when it flips into or out of a mirrored
  view, the e-to-w snap included; idle and actions are untouched. Proof: `tools/debug/walk_turn_check.gd`, gorilla
  foot swaps 3 to 0. So every alternating walk (four-beat, diagonal, biped) must keep its two halves symmetric: the
  foot that swings on f(i) swings on its partner's side on f(i + 4), and the dip lands on f0 and f4. A hop has no
  left-right half, so check how a hop looks across that half-loop jump before drawing one. `walk_tools.py mirror`
  checks a gait.

## 7. Foot lock at 35 degrees
- A ground step of d texels along the body shows on screen as d x f x u. At pitch p and view yaw a (e 0, se 45,
  s 90), the screen vector is (cos a, sin a x sin p). At 35: e u (1, 0), f 1.000; se u (0.867, 0.497), f 0.815;
  s u (0, 1), f 0.574; ne and n the same with y negated.
- **Planted step a frame on the canvas = -P x f x u**, where P is the side-view step in px a frame. At P = 3:
  e (-3, 0); se (-2.12, -1.22); ne (-2.12, +1.22); s (0, -1.72); n (0, +1.72).
- **Lock rule:** the k-th planted frame's sole centre minus k planted steps stays within 2 px of the first. The rhino
  passed with e 0.00, se and ne 0.88, s and n 0.88 px.
- **Depth travel shows now.** At 35, a fore-and-back step in s and n shows at 0.574 of its length (0.16 at the old
  angle), so front and back walks need real foot travel, not reordered frames.
- **Toes toward the camera** may draw 2-3 px under the feet row (rhino s and n 163, se and ne 162). The floor hides
  none of it, and walk and idle both end on row 161 with sel-out.
- **The game camera is 30 degrees and the art is drawn at 35** (game feel, 2026-11-05). An s or n planted step drawn
  for 35 plays about 13% long in game: 0.22 px a frame at P = 3. That is under the 2 px lock gate; logged for game
  feel.

## 8. Stride against speed
- Drawn ground speed = P x fps x texel (m). Texel: L 0.020, M 0.018, S 0.016 m.
- Rhino: 3 x 8 x 0.020 = 0.48 m/s, kept by Preston ("Keep 0.48 m/s").
- The game: `move_speed = 3.5` m/s for every machine, a placeholder (`machine_test_player.gd:7`). `stride_speed`
  is one export for all machines (0.48), and `full_speed_walk_rate` is still 1.0, so the feet slide today.
- To plant at 3.5 m/s, a walk drawn at 0.48 m/s plays 7.3 times fast, or the side step must be 21.9 px a frame at
  L and 8 fps (24.3 at M, 27.3 at S). That is a run, not a walk: the gorilla's whole side view is 79 px long.
- **Natural walk speed (Froude, proposal):** v = sqrt(Fr x 9.81 x leg height in m). A comfortable walk is about
  Fr 0.25; animals switch to a run near Fr 0.5. `walk_tools.py stride` prints this per machine from its leg height.
- **Preston picks**, per game feel: lower move_speed, play the walk fast, draw longer strides, or add a run cycle.
  This lane never picks a speed. `stride_speed` needs a per-machine value once a second machine walks.

## 9. The checks on every walk (`walk_tools.py footlock`, plus the eye)
| Check | Pass |
|---|---|
| Foot lock per visible foot, from the frame pixels | spread 2 px or under in x and y |
| Swing feet | lift matches the gait sheet within 1 px; the swing goes forward along u |
| Above the legs | 0% differing pixels against the still after the dip |
| Lowest row per frame | the feet row, or 2-3 rows under it for toes toward the camera, listed |
| Palette, alpha, holes, strays, canvas edge | the still's colours only, binary alpha, one connected machine, no edge contact |
| Seams (`walk_tools.py seams`) | no slit where a limb slid back from the pinned body (solid in the idle, now an enclosed hole). Codex left them on the gorilla in e, se and ne; one `--fix` pass filled them with the body bands. Look first: open space beside a far limb at the silhouette edge is real and stays open, so never run a second pass |
| Loop | f7 to f0 is a normal step (planted step within 1 px of the others) |
| Mirror phase | the same physical foot up across s/sw and n/nw at each frame, or the offset noted |
| Stride | drawn m/s, and the playback rate needed at the current move_speed, reported |
| Eye | board at 4x with sel-out, still in column 1; a dot-grid review video (`make_walk35_review.py`) |
| Game | packed by the animation lane, then game feel's turn and speed test |

The foot-lock tool finds feet by the bottom of each column, so a foot hidden behind the body cannot be measured from a
composite. Codex's own verify measured those from its limb layers; ask for them in the brief.

## 10. Tools (stock-take 2026-11-05)
| Tool | Free or paid | Use here |
|---|---|---|
| `walk/tools/walk_tools.py` (this lane) | free | `stride`, `gait` (sheet, targets, guides, plan video), `footlock`, `mirror` |
| Animation lane scripts (`rhino_l/take-a/anim/`: make_walk35_rhino.py, make_walk35_review.py, walk35_selout.py, walk35_touchup.py; `wolf_m/take-b/anim/foot_lock_test.py`) | free | brief and target builder, review video, sel-out, recolour |
| Codex token cap (`rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped_d.sh`, codex_tokens.py; same arguments as the old `run_codex_capped.sh`, but runs Codex from `D:/dev/_scratch/codex-cwd`, since hollowtide is moving to D:; animation lane, 2026-11-05) | free | kills a Codex run at a token cap; the watcher checks every 20 s, so a run can end about 3k over its cap |
| Aseprite MCP: render_onion_skin, compare_frames, audit_animation, tweens, Lua | free (local) | onion skins for the loop and the passing pose, frame diffs; needs an .aseprite file |
| PixelLab pixelart_workbench (lint, motion, inspect, repair) | free for subscribers (its own note) | lint for orphan pixels and outline gaps on finished frames |
| Godot 4.7.2 headless check and Movie Maker | free | the in-game check and phone video, run by the lanes that own the game |
| Codex walk run (5 views) | paid: Codex tokens on Preston's plan | redraws the joints; the rhino took 274,960 tokens |
| PixelLab animate_with_skeleton_v3 | paid (inside the free daily quota of 20 generations, 3 a view) | fallback for straight s and n walks; held the rhino, lost the fennec |
| Retro Diffusion walking | paid, $0.14 a run | its side and se walks read as walks; ask before each run |
| SpriteCook animate | paid credits | not tried on a machine yet |

## 11. A walk, step by step
1. Confirm the 35-degree stills are approved, and find the newest folder (touch-up first).
2. `walk_tools.py stride` with the machine's leg height and size; agree P and fps with game feel.
3. `walk_tools.py gait` writes `targets.json`, the guides and the plan video for Preston. Free.
4. Price the Codex run (section 12) and wait for Preston's yes in his own words.
5. Codex run 1 (e, se, ne), then run 2 (s, n), each under a token cap, with the rhino's brief_run1 rules: translate,
   never rotate; joints by hand; body pinned.
6. `walk_tools.py footlock` and `seams` on every view, then the board at 4x with sel-out and a 5x zoom of each
   moving joint. The gorilla's cut-off ne limb passed every number and showed only in the zoom. Add to every brief:
   "where a limb slides back, draw the body behind it; no slit may show the background inside the body".
7. Send the frames to the touch-up lane for cleanup and sway. Once Preston approves its version, the walk lane packs
   them itself with pack_<machine>_3d.py and a backup (the animation lane was closed 2026-11-05). Game feel gets the
   turn and speed test. Message the hub at each handoff.

## 12. Pricing a walk
| Run | Rhino tokens | Expected with the lessons built in |
|---|---|---|
| Run 1: e, se, ne | 102,921 | 95k-115k |
| Leg cleanup | 78,180 (caused by rotation) | 0 if run 1 translates; 60k-80k if not |
| Run 2: s, n | 93,859 | 85k-105k |
| Repair pass for cutoffs (fennec) | 45k-190k for two sets | only if the board shows cutoffs |

Actual totals (Codex tokens, from each run's token-watch file):
| Machine | Run 1 (e, se, ne) | Run 2 (s, n, repairs) | Total |
|---|---|---|---|
| Gorilla (L, knuckle walk) | about 142k | 100,614 (with ne repair) | about 243k |
| Fennec (S, trot) | 134,714 | 106,214 (with two repairs) | 240,928, plus step A |
| Hippo (L, four-beat) | 224,713 (cap 160k, overshot one step) | 100,320 (cap 100k) | 325,033 |

## 13. Lessons from the gorilla, fennec and hippo (2026-11-05)
Body and look
- A body pinned to the still reads stiff. Preston on the fennec trot (0 px sway, 1 px dip): "isnt fluid". The fix,
  kept for all views ("Keep, do all views"), is touch-up's sway.py (touchup/fennec_s_walk/sway.py). It adds lean and
  bob after Codex, for free, by per-row offsets that fade to zero at the feet. Lean over the planted side: in a trot,
  over the landing front leg, 2 px; in a four-beat walk, away from the swinging side, 1 px for an L machine. Bob 1-2 px
  just after each landing, on top of the dip. Lock each planted foot by its own box, not the bottom rows: in the
  diagonals some feet stand 25 rows up (hippo se RH on row 135, ne RF on row 136).
- A new body pose (sit to stand, rear up) is a redraw, not a puppet. Preston rejected cut-and-reposition parts on the
  fennec death. Route: one image-tool sheet from the approved 35 still plus a pose reference (fennec step A,
  fennec_s/stand35), finished to the fixed palette. Scale a re-posed sheet by the head (ear span), not body length:
  scaled by length, the fennec's head came out 8% small.
- Front view (s): set the near legs wide enough apart, or the stance reads as sitting. Preston on the fennec: "Widen
  front view front legs a bit". Fixed by moving each leg out 2 px with the chest plate fixed (fennec_s/widen_s/).
Briefs
- Give a draw order per view: far legs, tail, body, near legs; in s, the jaw over the front legs as the still has it.
  Without one, the fennec's ne far hind leg covered its tail.
- Plates and discs belong to the body: where a limb uncovers one, draw it whole. Gate it with numbers: the piece count
  of the plate's colours equals the still's, with none of 4 px or fewer.
- The body stops at the belly: fill behind a moved leg only inside the body's outline. Hippo run 1 filled the still's
  leg area below the belly, which hung dark blocks under it and split a far foot. Run 2's belly gate fixed it: in each
  leg's column span, the body's lowest row stays within 1 px of the line between the columns on either side.
- Number gates work where "make it clean" does not (fennec: tail light px at least 63 in a box; gold pieces = 4).
  Add a speck gate: 1-2 px single-colour pieces in the leg rows, no more than the still plus 2.
- Have REPORT.txt updated after each view. Both hippo runs hit the cap during their own audits, so the walk lane ran
  their verify.py afterwards.
Checks
- walk_tools footlock's silhouette measure merges a sole with whatever touches it (close feet, the belly, the jaw).
  When that happens, Codex's stamp measure decides.
- The seams check finds holes, not extra fill. The hippo's hanging belly fill passed every number and showed only at
  8x, so always look at an 8x zoom of each leg area.
- A script fix needs the exact defect boxes. A straight belly-line guess removed the wrong pixels on the hippo
  (hippo_l/clean1/NOTE.txt). Hand cleanup in touch-up is the fallback.
Cost
- The capped runner reads tokens every 20 s, and one Codex step can add a whole context at once (hippo run 1 went
  from 149,939 to 224,713 in one tick). Quote Preston the worst case as the cap plus 75k.
In game
- Foot slide = speed / (stride_speed * speed_scale) (scripts/moba3d/machine_test_player.gd). A kit must set
  full_speed_walk_rate = walk_speed / STRIDE. The fennec kit does. ape_kit does not, so the gorilla slides 7.3x at
  move_speed 3.5. Check each machine's kit when packing.
