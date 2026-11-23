# Pangolin magnetism: showing it without tossing machines (decided 2026-11-18: near-field snap)

**Decided:** Preston, 2026-11-18: "Near-field snap". B and C are not being built. The lore line has gone to the
moba-lore session.

Kit design lane. Preston, 2026-11-18: "with magnetic powers I wonder are we doing enough to showcase that? ... being
around metal mechs irl it would be op right? obviously I wouldn't want it to be able to levitate and just toss all the
mechs ... its more the ball mechanics so idk how we can make that work."

## The short answer
- **Real magnetism wouldn't be OP at range.** This is general physics, not checked for this doc. A magnet's pull drops
  off very steeply with distance: the field falls roughly with the cube of the distance. That's why a scrapyard lifting
  magnet has to almost touch the steel it lifts. A realistic magnet is strong at contact and weak a few metres away.
- **So the kit can follow the physics.** The field grips what it touches and what's loose, and fades within metres. It
  never lifts or throws a machine.
- **It's already in every slot:** Salvage, the ball's curve, Scale Flare, Scrap Comet, and now the pry. It's already
  drawn too (`pangolin_fx.gd`):
  - a mark on magnetised enemies;
  - the Salvage field cone, with plates ripping off and snapping on;
  - a pull line while the ball bends;
  - the field lines on Scrap Comet.
- **What's missing:** the ball's curve is flat. Today the pull is the same 1.6 rad/s anywhere inside 10 m, so it doesn't
  feel like a magnet.

## Pick: near-field snap (ball only)
The pull keeps today's strength at range, then gets much stronger as the ball closes in, ending in a snap.

| Distance to the magnetised enemy | Today | Pick |
|---|---|---|
| 10 m (edge of the pull) | 1.6 rad/s | 1.6 rad/s (unchanged) |
| 4 m (Salvage's reach) | 1.6 rad/s | 1.6 rad/s (unchanged) |
| 3 m | 1.6 rad/s | about 2.8 rad/s |
| about 2.3 m and closer | 1.6 rad/s | 4.8 rad/s, a lock ("the snap") |

- **Rule:** the bend is `mag_turn × (4 m / distance)²`, never below 1× and capped at 3×. Everything else stays as
  today: the 10 m range, and only enemies ahead of the roll.
- **The trade:** it's stronger only up close. At range nothing changes, so the long-range curve the ball took over from
  rail dive (fun pass) keeps its job. Inside about 2.3 m a magnetised enemy is very hard to sidestep. But the ball
  usually hits from there anyway, so the change is mostly feel.
- **The showcase:**
  - The pull line follows the same curve: faint and slack at 10 m, taut and bright at the snap.
  - At the snap there's a clang and a spark ring.
  - The magnetised enemy's loose bolts and plate edges lean toward the incoming ball as it closes.
  - Nothing on the enemy moves except those small parts.
- **Builds:** the game feel lane changes the curve (two exports). The effects lane adds the line, the snap and the
  bolts. Both were sent on 2026-11-18, the effects work through the hub.
- **Godot has the curve (game feel lane, 2026-11-18):**
  - Exports `mag_snap_ref` 4.0 m and `mag_snap_cap` 3.0.
  - The probe measured 1.60 rad/s from 9.5 m in to 4 m, 2.84 at 3 m, and 4.80 at 2.31 m and closer. It also checks that
    nothing moves the enemy.
  - **Hooks for `pangolin_fx`:**
    - The cue `mag_snap` fires once when the bend first reaches the cap. `kit.mag_snapped` is that target. It re-arms
      only after the bend drops below the cap.
    - `kit.mag_mult` is this frame's multiplier, 1.0 to 3.0, for the pull line's tautness.
    - All of these reset at `ball_start`.
  - Not watched in a game window yet.

## Alternatives
- **B, full falloff:** also weaker at range, about 0.5 rad/s at 10 m. That's closer to the physics, and easier to dodge
  from far. It takes back part of the long-range job the ball inherited from rail dive.
- **C, the ball gathers scrap as it rolls:** bowled minions and wrecks it rolls over add bits to the ball, visual only.
  It shows the magnet constantly. Making it grow or hit harder would overlap Scrap Comet, which already owns "pull
  scrap and grow".
- **Not proposed:** lifting, throwing or pulling machines; a new passive or resource. Tether swing (lost to Scrap
  Comet) and rail dive (cut) stay closed.

## Lore line (proposed, goes to the moba-lore session after a pick)
"Its field is a scrapyard lifting magnet's: it grips what it touches and what's loose, and it fades within a few metres.
It can tear the plates off a machine and steer itself onto one. It can't lift one."

## Not checked
- I haven't seen today's magnet visuals in motion.
- The curve numbers are a starting point and haven't been played.
