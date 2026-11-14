# Wolf (wolf_m) mech status

Written 2026-11-05 by the wolf mech session (it was the fleet lane's kangaroo session; the hub moved it to the wolf).
This session owns the wolf's VFX, kit script and art touch-ups. Walks, attacks, packing, sound and camera fit stay
with their lanes (roster: `docs/team/mech-sessions-2026-11-05.md` in the hub's worktree).

**Role and kit** (`docs/plan/moba-kits.md`): assassin, ode to Thanatos. Passive scent (senses low-health enemies, runs
faster toward them), 1 lunge, 2 hamstring, 3 howl, 4 run down. Art the plan asks for: lunge, bite, howl, sprint loop.

## What exists
| Thing | Where | State |
|---|---|---|
| Approved stills, drawn low | `take-b/fixed/` (8 views, 192 canvas, feet row 160, 12 colours) | approved; n has capped ink |
| Stills at 35 degrees | `take-b/views_cam35/` (s, se, e, ne, n) | accepted: Preston "Turn test, then fix"; ne ear-tip eye pixel removed; turn test PASS (`match/MATCH_NOTES.md`, 2026-11-04). 61,049 Codex tokens |
| Touched-up stills at 35 | `take-b/views_cam35_touchup/` (recolour, same alpha) | kept: Preston "Keep it", 2026-11-05 (`APPROVED.txt`); the kit and idle35 use these. `cam35_touchup/views_selout_light/` is a pack-time sel-out preview, not a source |
| Idle at 35 | `take-b/anim/idle35/` (frames, frames_selout, idle.gif, board) | built from the touch-up views; not installed |
| Walks and moves, drawn low | `take-b/anim/codex-set-a` to `d`, `codex-walk2` to `4`, `codex-tailfix`, `review/` (wolf_walk.mp4, wolf_all.mp4) | made for the low camera; which set is final is not checked here |
| Older battle-game art | `art/machines/wolf_m/views/` (8 views, 2026-10-20) and `anim/` (dash, death, hit, howl, idle, lunge) | from the earlier battle game, not take B and not 35 degrees |
| Battle VFX recipes | `scripts/battle/vfx_recipes.gd`: `wolf_m/lunge`, `howl`, `dash` | battle game only |

**Not there yet:**
- No MOBA game frames installed. MATCH_NOTES lists "install its frames, then rerun the test with
  `--drone-views=installed`". The hub says the wolf's pack is on hold.

## Done: lunge slice (2026-11-05, Preston: "Lunge in the match")
- `scripts/moba3d/wolf_kit.gd` (WolfKit), slot 1 only. It leaps at the enemy nearest the aim (within 6 m and 40 degrees
  of the mouse aim), lands 0.9 m short and bites after a 0.07 s hitstop. A wounded match target (at or under half
  health) cuts the lunge cooldown in half. With no enemy there, it leaps 3.5 m along the aim and bites the first enemy
  it meets, or the air. Camera shake through KitFeel. Sound cues `lunge_cast`, `lunge_bite`, `lunge_miss`, with
  sounds from the sound lane (Preston: "All A", 2026-11-05; `audio/sfx/wolf/`, wired through KitAudio). Every number is a placeholder to see it, not balance.
- Frames: no installed frames, so `WolfKit.install()` builds idle and walk from `take-b/views_cam35_touchup` at run time (one
  still per view, tilted). No lunge frames: the leap is a hop of the still.
- Press play: `scenes/moba3d/wolf_test.tscn` (the field slice, the wolf, one extra dummy 4 m ahead). Mouse aims, 1 lunges.
- Check: `tools/debug/check_wolf_kit.gd`, 21 of 21 pass (frames, aim cone, landing distance, facing, bite, air bite,
  wounded refund). The scene loads clean headless.
- In the match: the game feel lane added the wolf to `arena_play`'s Tab rotation (rhino, gorilla, fennec, wolf),
  2026-11-05; their probe found it installed, tilted, size M. Not yet checked: the lunge against bots and minions in a
  full match, and how the wolf looks on screen.

- Cooldowns: the game feel lane added the wolf row to MatchRules.TIERS from the doc (2026-11-05): 1 short 5 s,
  2 medium 9 s, 3 medium-long 12 s, 4 long 40 s.

## Done: basic attack, melee bite (2026-11-05, Preston: "Yes, melee bite")
- `WolfKit.basic_attack(target)`, the game feel lane's hook: Space or left click (target null, aimed with the mouse),
  or a bot with its target. The director keeps the gates and the cooldown. Built the same way as the hippo's bite.
- A short snap at the nearest hittable enemy within 1.8 m edge to edge and 50 degrees of the aim: 0.08 s wind-up,
  40 damage (`hit(player, 40 / kit_hit_damage)`), hit spark, 0.05 s hitstop, shake 0.2, cue `basic_bite`. With nothing
  in reach it snaps the air (a puff, cue `basic_whiff`), so the key always answers. Every 0.8 s. A bot's target more
  than 0.3 m past reach is refused; no bite fires during the lunge.
- No bite frames: the body holds still and the hit shows as the spark. The attack lane can draw a real bite later.
- All placeholders to see it, not balance.
- Sounds: Preston picked "All C" (sound lane, 2026-11-06): `basic_bite` "Snap trap" (latch, dry snap, crunch, 250 ms),
  `basic_whiff` "Click" (light snap, thin swish, 200 ms). Made for the basic attack, wired through KitAudio;
  `check_kit_audio.gd` PASS.
- Check: `tools/debug/check_wolf_kit.gd`, now 25 cases (the 5 new ones: player bite hits at 40/60, whiff, bot out of
  reach refused, bot in reach hits, no bite mid-lunge), 25 of 25 pass under --fixed-fps 60. `kit_api_check` 0 failures.

## Open
- Pack on hold: the 35-degree idle exists but is not installed in 192 cells.
- A paid 35-degree death: undecided. Hits and deaths have no owning lane yet; Preston is being asked.
- Not checked here: which low-camera walk set is final (the 35-degree walk would reuse only its timing).
- When a real walk is packed, WolfKit must set full_speed_walk_rate = walk speed / stride (as the fennec kit does),
  or the feet slide (walk lane, 2026-11-05).
- 35-degree walk quote (walk lane, 2026-11-05): two Codex runs, e/se/ne capped 150k and s/n capped 110k; likely
  230k to 270k, worst case about 410k. Preston: "Free prep only" (2026-11-05): the walk lane does the free steps
  (feet labels, plan, guides, gait entry, brief) and stops; the paid runs are not approved.
  Free prep DONE (walk lane, 2026-11-05) in `docs/art/moba/walk/wolf_m/`: feet.json, plan_walk/ (targets, guides,
  plan.gif), run1/ (brief for e, se, ne), run2/ (draft for s, n), README.txt. New gait trot4 in walk_tools: the old
  approved side trot's timing exactly, mirror check passes. Stride for WolfKit: STRIDE 0.9, so
  full_speed_walk_rate = walk_speed / 0.9 (set it when the walk is packed, not before: the walk is one still now).
  Paid runs: Preston "Not now" (2026-11-05). Parked; the prep stays as it is.

## Next slices (Preston picks one)
1. **Lunge in the match (free). DONE, see above.** Write `scripts/moba3d/wolf_kit.gd` with slot 1 only: leap at a target and bite,
   part of the cooldown back if the target is wounded. It uses the views it has (a slide and a short hop, no new frames)
   and one simple bite flash. Press play in the match test. One session. The kits for the rhino, gorilla and fennec are
   the pattern. It asks the game feel lane first, since that lane owns the shared match code.
2. **Wolf on the floor with its own frames (free, needs another lane).** Lift the pack hold: the animation lane packs
   the 35-degree idle already built, then the game feel lane reruns the turn test with installed frames. One short
   session for each lane. This is what MATCH_NOTES lists as open.
3. **A 35-degree death (paid).** One Codex image set, about 55k to 80k tokens going by the fleet's single images
   (54,566 to 78,028). Worst case about 155k if it runs under a capped script, since caps overshoot by about 75k.
   Only one paid job may run across the team at a time, and it needs Preston's own yes.

My pick: 1. It is free, it is the wolf's own work, and it puts something on screen to press play on.
