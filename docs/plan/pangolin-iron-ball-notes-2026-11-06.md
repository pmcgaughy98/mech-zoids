# Pangolin iron ball: feel notes from the game feel lane (2026-11-06)

Sent by the game feel lane to the Pangolin session after Preston asked for the iron ball to feel like Rammus's
Powerball (League of Legends) and ruled "Stop on first hit". Structure and feel only: no names, art or numbers from
that game. The lane's knowledge of Powerball is general memory, not checked against the live game. Every number
here is our own suggestion. Kept as the lane wrote it, lightly condensed; the kit proposal lives in the Pangolin
section of `docs/plan/moba-kits.md`.

## How a momentum roll feels (structure)
1. **Windup:** almost none. It tucks and is already moving; the tension comes from the speed building, not a windup.
2. **Ramp:** speed builds steadily over a few seconds from modest to very fast, read through a growing dust trail and
   a rising rumble. The ramp is the decision: hit early and soft, or wait and hit hard while they watch you come.
3. **Steering:** ordinary move input. Unsure whether the reference has a turn-rate limit or drift.
4. **Impact:** the target is bumped up and back briefly, with a slow around the impact. The roller pops out right
   beside the target, ready for its next button. That follow-up is half the satisfaction.
5. **Sound:** a rolling rumble that rises with speed, then a heavy blunt crunch. For ours: an iron clank under a low thud.
6. **What makes it good:** the threat visibly and audibly grows; you're committed but can get out (recast stops it);
   the crash pays off (hitstop, shake, target leaves the ground); you can follow up at once; the enemy could have
   dodged, so a hit feels earned.

## Notes against our match code
- **Curl:** don't root it. Start rolling slowly on frame one while the tuck plays; a rooted pause reads as input lag.
- **Steering:** set `player.move_override` every frame to a roll direction that turns toward `move_dir()` at a capped
  rate, tighter as speed rises. With no keys held it keeps rolling straight.
- **Speed ramp:** `move_override` alone can't ramp (the move code caps direction length at 1). Refresh
  `boost(mult, t, &"iron_ball")` each frame. `speed_factor` multiplies all boosts with the 0.6 slow, so decide
  whether an enemy slow cuts the ball's speed; other boosts would stack on top.
- **Locking other moves:** set `kit.current = "iron_ball"` while rolling (blocks Tab and the bot's `_use_kit`). The
  director's Space basic doesn't check `current`: either `basic_attack` returns false while rolling, or Space ends the roll.
- **Uncurl after the hit:** short, and claw rake (slot 1) can fire straight away.
- **Walls:** `move_and_slide` would scrape along a wall at full speed. Decide: a wall ends the roll (small bump, no
  knock-up) or bounces it.
- **Minions:** if minions are physics bodies, `move_and_slide` stops on them. Either a collision exception while
  rolling, or minions count as a hit. Towers should probably stop it without a knock-up.
- **Knock-up:** `machine_test_player` has `stun(t)` and `knock_aside(offset, time)` but no vertical knock-up. Ours
  would be stun plus a sprite hop scaled by speed, and a farther `knock_aside` for the ring around it. Guard with
  `has_method` for minions and dummies. The game feel lane offers to add a shared `knock_up(height, time)` like `heal()`.
- **Damage taken while rolling:** reduce it in the kit's `take_hit(pos)`, the path plating and shields already use.
- **Shake:** `impact(strength)` from about 0.5 at starting speed to 1.0 at top speed (ladder: rhino catch 0.5, slam
  0.7, finale 1.0; gorilla dome 0.8). **Hitstop:** 0.06 to 0.12 s scaled with speed (rhino flick holds 0.08 s).
- **As a 40 s ultimate** it is used far less often than the reference's, so each hit has to feel bigger.
- **Art saving:** a ball looks the same from every view, so one spin loop serves all eight; scale the spin rate with
  speed (sprite `speed_scale`).
- **Camera (camera lane):** at 2x speed the chase camera may lag. Flag it once it rolls.
- **Bots:** `_use_kit` needs a PLAN row, and the bot must steer `move_override` at its target each frame. Simplest
  rule: start the roll when an enemy machine is in clear line within a set range, and steer straight at it.
