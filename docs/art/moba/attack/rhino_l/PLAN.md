# Rhino ground pound at 35 degrees: plan (proposal, nothing here is canon)

Attack lane, 2026-11-05. Method: `../ATTACK_PLAYBOOK.md`. Numbers are placeholders for Preston to set.

## What the move is
- Kit (`docs/plan/moba-kits.md`, slot 2): "Rears on its hind legs and slams down. The ring deals damage and slows."
- The code since Preston's change on 2026-11-05 (`scripts/moba3d/rhino_kit.gd`): a tremor over a 4 m circle. The
  first slam is on F4 (`POUND_SLAM_FRAME`), then 4 stomps 0.4 s apart, each showing F5 (`POUND_RISE_FRAME`) for
  0.12 s and then F4 again. The stampede finale plays one slam with the F4 and F5 holds.
- Game feel's asks (2026-11-05): keep 6 frames with the slam on F4; F5 a small lift close to F4; the wind-up about
  0.5 s (F0 x1, F1 x1, F2 x1, F3 x2); a new rock pop effect.

## The base
- Stills: `rhino_l/take-a/views_cam35_touchup/` (touch-up lane: current). The installed idle's f0 equals them.
- The walk in the game (`walk35/walk/frames_selout`) was drawn from `views_cam35`: same alpha, 671-760 px of colour
  differ. `walk35_touchup/frames` recolours it but is not packed. That is the touch-up lane's or Preston's call; the
  ground pound starts and ends on the touch-up still, like the idle.
- No old-angle ground pound frame goes into the brief or the targets.

## Frames (indexes fixed by the kit, the same in all five views)
| F | Beat | Body | Feet | Hold (100 ms ticks) |
|---|---|---|---|---|
| 0 | rest | the still | all planted | 1 |
| 1 | anticipation | weight back onto the hind legs: the body 2 px back along its axis and 1 px down; the head 1 px lower (lag) | all four planted | 1 |
| 2 | rise | pitched up 15 degrees about the hind hips; head up; front knees start to fold | hind planted; front up 10 texels (8 px on screen) | 1 |
| 3 | peak, the telegraph | pitched up 30 degrees, horn high, front legs tucked | hind planted; front up 20 texels (16 px on screen) | 2 |
| 4 | slam, the hit frame | front feet back on their still soles; body 2 px under the still (knees bent), head 3 px under (lag) | all four planted | 3 |
| 5 | small lift | chest 1 px under the still; the near front foot up 3 texels (2-3 px) | three planted | 3 |

The slam lands at 0.5 s (today 0.7 s). The packer row becomes (0, 1), (1, 1), (2, 1), (3, 2), (4, 3), (5, 3).
F5 hands back to the idle through `stop_action`, so F5 stays within 3 px of the still in every part.

## Screen targets per view (35-degree geometry, playbook section 3)
- Lifts are vertical, so they show the same in every view: F2 8 px, F3 16 px, F5 2-3 px.
- The pull-back at the peak: hind and front soles sit 40 texels apart in e (measured), so the front end pulls back
  40 x (1 - cos 30) = 5.4 texels. On screen: e 5 px toward the tail; se (-3.5, -2.0); ne (-3.5, +2.0); s 3 px up
  (adds to the rise: about 19 px); n 3 px down (takes from it: about 13 px).
- Per-foot targets go in `targets.json` after the feet are labelled at 6x (free step 1).

## Route
- F2 to F5 are new poses, so they are redrawn (walk lane lesson, Preston on the fennec death). F1 keeps the still's
  pose and moves it by whole pixels, with the knees redrawn.
- Codex, one image-tool call per run, from the touch-up stills only. The pose is given in words and as guide strips
  at game size (markers on the still: planted-foot boxes, front-foot targets, the horn tip's path). Finished by
  script: snap to the palette, scale by the head (horn base to eye), hind legs below the hips pinned to the still's
  pixels, eyes, ink shares to the still's. Then the gates.
- Run 1: e, se, ne. Run 2: s, n, after Preston has looked at run 1. A finish pass only if the gates miss.
- Draw order in the brief: e and se: far legs, tail, body, near legs. ne: far front leg, head and horn, body, near
  legs. s: hind legs and rump, body, head and horn, front legs. n: head and horn, front legs, body, rump plates and
  tail, hind legs.

## Gates (the playbook's section 5, plus these numbers)
| Check | Pass |
|---|---|
| F0 | 0 px differ from the touch-up still |
| Hind feet | sole drift 1 px or under over F0 to F5 |
| Front feet | F1 drift 1 px or under; F2 lift 8 +-1 px, F3 16 +-1; F4 on the still soles +-1; F5 near front 2-3 px |
| F4 against F5 | every part within 3 px (the 0.12 s toggle) |
| F5 against the still | every part within 3 px (the hand-back) |
| Eye | in every frame where the still shows one |
| Head and horn | head size within 3% of the still's; horn part match 0.9 or better |
| Plates | pieces per plate colour equal to the still's, 4-connected; specks (1-2 px single-colour pieces) no more than the still plus 2 |
| Ink | interior ink share within 15% of the still's, per view |
| Palette and pieces | the still's colours only, binary alpha, one 4-connected piece, no edge contact |
| Telegraph | F3 silhouette IoU against the still 0.85 or under at 1x |
| Lowest row | 160; toes toward the camera up to 163, listed |

## Effects (separate, free)
- `gp_ring` stays as the burst at the feet on the first slam; `KitFeel.ground_wave` draws the 4 m edge in code (game
  feel).
- New, asked by game feel: a rock pop, 4 to 6 frames, about 1 m, anchored at the bottom centre (50 texels at the
  rhino's 0.020 m). The rhino's palette, its darkest colour as the ink. Free: Aseprite or PixelLab vfx_workbench.
- Optional: `cracks.png` drawn for an 8 m circle (stretched to 6.8 m now).

## Free steps before run 1
1. Label the feet at 6x (`walk_tools.py soles` plus a look).
2. `targets.json`, guide strips per view, and a blocking previz GIF labelled "blocking, not the art".
3. The brief: the stills, the frame table, the draw orders, the gates above, REPORT.txt after each part.

## Price (Codex tokens on Preston's plan)
The math: one image job plus finishing measured 54,066 (fennec stand35) and 58,520 (the old 3-row ground pound); the
fennec notes put a fresh `codex exec` at 60k to 110k a sheet; the 35 walks' runs were 94k to 143k with hand-drawn
joints; repair passes 45k to 190k.
| Run | Views | Estimate | Cap |
|---|---|---|---|
| 1 | e, se, ne | 60k-100k | 110k |
| 2 | s, n | 55k-90k | 100k |
| Finish pass, only if the gates miss | all five | 60k-110k | 120k |
Total 115k to 190k without the finish pass, 175k to 300k with it. Every generated set so far needed one, so expect it.
Worst case per run (learned after run 1 started, hub 2026-11-05): a run that reaches its cap can overshoot by about
75k, so run 1's worst case is about 185k. Later caps will be set 75k under what Preston agrees to.

## Open for Preston
- The go for run 1.
- `docs/art/moba/kit-anims-35-plan.md` says rhino kit moves wait for a rhino kit redo. He reworked the ground pound
  himself on 2026-11-05, so this plan reads it as staying.
