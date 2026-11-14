# Pangolin roll feel: options (proposal, 2026-11-14)

**Picked by Preston, 2026-11-14: "A, bank-shot charge"** (with the recast pop). B and C stay parked.

Drafted by the pangolin effects lane for Preston to pick from. The game feel lane builds whichever one he picks.

**His words:** "Is there a basic ability that lets it turn into ball? whether its a mode it can switch too or a
attack roll that stops at first god or minion or overwatch hamster guy. Lets make our own kit though that people will
enjoy but those felt great so we can make our mechanics that might feel even better."

## How it plays today (as built, `scripts/moba3d/pangolin_kit.gd`)
- **Slot 2, iron ball, is an attack roll, not a mode.** About 9 s cooldown (medium tier).
  - It curls and rolls for up to 3 s, starting at 4 m/s and building to 12 m/s, steered with the move keys.
  - Off a wall it bounces and keeps 95 percent of its speed.
  - Minions are bowled aside (20 damage, thrown 1.8 m) and do not stop it.
  - Magnetised enemies within 10 m bend its path toward them.
  - The first enemy machine it reaches ends the roll: a kit hit plus up to 40 bonus damage, and the machine is tossed
    0.6 to 2.2 m and stunned 0.4 to 1.0 s. Both scale with speed.
- **Slot 3, flare used mid-roll,** spikes the ball, and the ending hit also bursts flare damage around the target.
- **Slot 4, scrap comet:** a ball twice the size that runs over everyone and does not stop. It grows on each hit and
  bursts after about 4 s.
- **Not built yet:** claw-swipe basic attack and the sharp-scales passive.

## What the references do (structure only, general knowledge, not checked live)
| Game | How the ball works | What feels great |
|---|---|---|
| Rammus (League), Powerball | An attack roll that speeds up and stops at the first enemy champion or monster, knocking it back. | One clear goal: build speed, then hit someone hard. |
| Wrecking Ball (Overwatch) | A mode you switch into and out of. Rolling is how he moves, and a grapple lets him swing for speed. | Movement itself is fun; skill keeps speed up. |
| Rocket League, pinball | Bounces keep speed. | Bank shots off walls feel clever. |

Today our roll is closest to Rammus, plus wall bounces and the magnet curve.

## Options for the roll (our own mechanics)
**A. Bank-shot charge (recommended, smallest change).** Keep the attack roll, but every wall bounce **charges** the
ball. It gains a little speed and damage and throws a brighter spark ring, up to 3 charges. A three-bank hit is the
big payoff moment. This mechanic is ours: no reference rewards bouncing as the main skill.
- Pairs with **recast to pop:** press 2 again mid-roll to uncurl early with a small knock-up around the pangolin, so a
  roll that misses still does something.

**B. Roll stance (Wrecking Ball style mode).** Slot 2 switches between walking and ball. In ball form it moves fast
and bowls minions, but cannot basic attack. Hitting an enemy machine at full speed does the crash, after which it
stays in ball form at low speed. A short cooldown starts on leaving.
- **Most freedom, and the hardest to balance.** In a lane-based MOBA a permanent fast form is strong for escaping and
  ganking.

**C. Magnet slingshot.** Keep the attack roll. While rolling, press 2 near a magnetised enemy to orbit them once and
fling off in the aimed direction at full speed. This was the tether-swing alternative from the fun pass.
- **The most skill-heavy and fun to master, but the hardest to read and to build.**

## First slice if A is picked
The game feel lane adds a `charges` count, 0 to 3, to the roll:
- Each bounce adds +1.5 m/s over the max speed and +15 bonus damage.
- Recast on 2 pops: a 1.5 m knock-up, 30 damage.

The effects lane draws the charge rings (one copper band per charge on the ball) and a bigger crash at three
charges. Headless check: two bounces, then a hit, and confirm `charges == 2` and that the damage rose by 30.
