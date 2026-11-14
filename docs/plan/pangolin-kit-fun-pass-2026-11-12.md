# Pangolin kit, fun pass (proposal, 2026-11-12)

**Approved by Preston, 2026-11-12: "Approved"** (scrap comet as the ultimate, not tether swing). Drafted by the
pangolin effects lane.

**His words:** "let's make a fun feeling kit. The rolling ball will need some thinking about how we could make it
fun. I dont like rail dive as its too similar to kangaroo, also defeats the ball purpose as u can just tp to enemies."

## What informed it (structure only, general knowledge, not checked live)
- **Rammus (League), Powerball:** the ball is his everyday move on a short cooldown, not a once-a-fight ultimate.
  The whole character is built around rolling in.
- **Wrecking Ball (Overwatch):** a roll is fun when speed is earned and kept. He swings on a tether to build speed,
  then lets go. Speed is the reward for good steering.
- **Pinball, Rocket League:** bouncing off walls without losing speed. A bank shot off a wall feels clever.
- **Katamari:** a ball that gets bigger as it picks things up.

The lesson from all four: **the ball is fun when it is the main way you move, and when skill keeps your speed up.**
Today it is a long-cooldown ultimate that ends on the first hit, and rail dive does its job (getting to a target)
instantly. So the ball gets used once a fight and rail dive makes it pointless.

## Proposed kit
| Slot | What it does | Cooldown |
|---|---|---|
| Basic | Claw swipes (unchanged). | none |
| Passive, sharp scales | Melee attackers take a little damage back (unchanged). | none |
| 1, salvage | Unchanged: tears armour off enemies in a cone, it wears the plates, each enemy hit is magnetised. | short |
| 2, iron ball | **Moved here from the ultimate, short cooldown (about 9 s).** Curls and rolls where steered, building speed. **Bounces off walls and keeps its speed.** **Minions are bowled aside** and do not stop it. **Magnetised enemies pull its path toward them.** The first enemy machine it hits ends the roll and is knocked into the air, harder the faster it was going. | short |
| 3, scale flare | Unchanged, plus: **flared while rolling**, the ball is spiked, and the hit that ends the roll also does the flare's damage around the target. | medium |
| 4, scrap comet (new ultimate) | Pulls every plate it has stolen, and scrap off nearby wrecks, onto its shell and rolls as a **ball twice the size**. It does not stop on hits: it runs over enemies, knocking each one into the air, and still bounces off walls. It grows a little with each enemy it flattens. After about 4 s it bursts and throws the plates outward. | long |

**Rail dive is cut.** Its magnetism job moves into the ball: magnetised enemies bend the roll toward them, so you
still reach the carry, but you have to roll there and steer, and they can see you coming.

## How it plays
Salvage the front line (magnetising them), roll in and let the magnet pull you onto one, bank off a wall to keep
speed, flare before contact for the spiked hit, claw swipes after. Scrap comet is the team-fight move: plough
through the whole fight.

## Alternatives named
- **Tether swing instead of scrap comet:** while rolling, press again near a magnetised enemy to latch on and swing
  around them, then let go to fling off faster. Most skill-heavy and the most "fun to master", but harder to build
  and to read.
- **Keep the ball as the ultimate** and give slot 2 a short roll-free move. Safer, but the ball stays a
  once-a-fight move, which is the problem.

## What it changes for other lanes
- **Game feel lane** owns the kit script: slot 2 becomes the roll, wall bounce, minion bowling, magnet curve.
- **Pangolin 3D lane:** the Rail_Launch, Rail_Streak and Rail_Arrive clips are no longer needed (keep them parked).
  The roll loop becomes the most used clip. Scrap comet needs a bigger ball shape, maybe the same roll scaled up
  with plates attached.
- **Effects lane (this one):** the rail dive effect is parked, not deleted
  (`shaders/pangolin_rail.gdshader`, the rail functions in `scripts/moba3d/pangolin_fx.gd`). The iron ball effects
  are reused for slot 2. New: wall-bounce spark, minion bowl hit, spiked-ball flare, scrap comet.

## First slice if approved
The game feel lane moves the ball to slot 2 with wall bounce and minion bowling, and it gets played. Headless check:
roll into a wall at an angle, measure speed before and after the bounce (should stay within 10 percent), and roll
through a minion and check the roll did not end.
