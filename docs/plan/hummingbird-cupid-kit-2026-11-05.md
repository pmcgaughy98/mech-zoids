# Hummingbird kit rework: ode to Cupid (draft, 2026-11-05)

Hummingbird session. Preston picked slice A ("kit rework (free)").
**Taken 2026-11-05: version 1 (bonds) and hover** ("Bonds + hover"); now the kit section in `docs/plan/moba-kits.md`.
Names and numbers are still proposals for him to edit. Version 2 and the other hover choices stay below for the record.

## Why
The kit rule of 2026-11-04 (`docs/plan/moba-kits.md`): the animal gives the body and at most one trait; the rest
comes from a power theme (the god's domain, an element, or a machine system). The 11-03 hummingbird kit takes
everything from the animal: nectar, wing hum, flutter, and a flower field.

## What stays in every version
- Role: healer support. Charm stays on the ultimate (the roster's only charm). The ultimate stays a placed zone that
  holds a spot, because the map's plaza and side pits are sized for it.
- **The one animal trait: flutter** (darts in any direction, even backward). It is the most hummingbird thing and the
  kit's escape. Alternative: keep the hum instead, and the kit needs a new escape.
- Nothing held. Every power comes from the body: the ruby throat plate, the steel needle beak, the cyan lenses.
- The heart-shaped throat plate stays as drawn; in version 1 it becomes the emitter for the link beams.

## What was used (general knowledge, nothing read this session)
- **Tether healers** (Dota 2's Io): a line to one ally that shares healing; enemies who cross the line are slowed.
  Structure taken: a visible line between two units that does the work.
- **Beam healers** (Overwatch's Mercy): one chosen ally at a time, easy to read from a distance.
- **Speed-aura healers** (Overwatch's Lucio): team speed as both a chase and an escape tool.
- **Bounce heals** (Dota 2's Dazzle): one cast reaches two targets.
- **Cupid himself:** his arrows bind two people together. Only the idea of binding is taken; no bow, arrows or hearts.
- **Real hummingbirds** cannot walk or hop; their feet only grip a perch. They hover, and fly backward.

No names, numbers or art from any of these.

## The numbers' scale
Nothing in the game sets health yet. Numbers below assume **1000 health per machine** as a placeholder, with lengths in
metres and times in seconds, like the rhino kit's placeholders (`scripts/moba3d/rhino_kit.gd`: stun 1.6 s, pound
radius 4.0 m). Machines move at 3.5 m/s.

## Version 1, recommended: bonds (Cupid's domain as a machine system)
Love as link beams from the throat plate. It gives the roster a mechanic no other machine has.

| Slot | Proposed name | What it does | Starting numbers |
|---|---|---|---|
| Passive | Kindred link | The last ally it healed stays linked by a beam from its throat plate and slowly heals. A new heal moves the link. | ally heals 10/s; breaks past 9 m or behind a wall |
| 1 | Link needle | A needle of light from the beak. Ally hit: healed and linked. Enemy hit: damaged. | 10 m line; heal 100; damage 60; cooldown 5 s |
| 2 | Surge line | The link pulses: the linked ally runs faster, and enemies who cross the beam are slowed. With no link, the speed goes to itself. | 3 s; +30% speed; crossing slow 30% for 1 s; cooldown 12 s |
| 3 | Flutter | Darts in any direction, even backward, without turning. | 4 m in 0.2 s; cooldown 8 s |
| 4 | Kindred ring | A ring of beams at its feet. Every ally inside is linked at once and heals; the first time each enemy enters, it is charmed: it walks toward the centre and cannot act. | 3.5 m radius; 5 s; heal 30/s; charm 1.0 s; cooldown 90 s |

**How it plays:** needle the carry to link it, poke enemies with the needle between heals, surge the line to chase or
to wall off a diver, flutter out. Kindred ring wins a fight over a spot.
**Cost to build:** the link and the line-crossing check are new code for the game feel lane.

## Version 2: light (an element)
The throat plate as a prism. It has the same shape as the 11-03 kit, so it is the smallest change and the cheapest
code.

| Slot | Proposed name | What it does | Starting numbers |
|---|---|---|---|
| Passive | Prism charge | Hitting enemies charges the throat plate; its next heal is stronger per charge. (Nectar's job, from light.) | up to 3 charges, +15% each; fade after 8 s |
| 1 | Light needle | Heals an ally or damages an enemy, then bends to one more target of the same side nearby for half. | 10 m line; heal 100; damage 60; bend 4 m; cooldown 5 s |
| 2 | Glow | A light aura: nearby allies move faster. (The hum's job, from light.) | 5 m; 4 s; +25% speed; cooldown 14 s |
| 3 | Flutter | Same as version 1. | 4 m in 0.2 s; cooldown 8 s |
| 4 | Lantern | Drops a bright lens core. Allies inside heal; each enemy's first entry draws it toward the light like a moth (the charm). | 3.5 m radius; 5 s; heal 30/s; charm 1.0 s; cooldown 90 s |

## What changes for the art (either version)
- **Goes:** nectar drops, the hum ripple, the flower field.
- **Body moves:** one cast pose (beak and throat plate glow) for slots 1, 2 and 4, then flutter (a lean). Casts and
  holds can be script-built from the 35-degree stills for free (`docs/art/moba/kit-anims-35-plan.md`); flutter's lean
  may need one drawn frame.
- **Effects:** version 1 needs the needle, the link beam, the ring of beams and a charm mark. Version 2 needs the
  needle with a bend flash, the glow aura, the lantern core with rays and a charm mark. All of these are effects, not
  body poses, so the free effect tools can make them.

## The hover call (his to make)
The kit says it hovers; the approved still stands on folded wings, by his rule for birds ("every pose resting on
feet"). This decides the pose of the 35-degree redraw.

| Choice | What it means | Art cost |
|---|---|---|
| **Hover (recommended)** | Flies low all the time, a small gap above its shadow. The drone minion already does this (a 9-row gap above its feet row). | No walk cycle, and no feet to slide at 3.5 m/s. The 35-degree redraw becomes a hover pose (a new pose, the same one paid redraw as planned). Hover bob is free by script; the wing beat is 2 or 3 drawn wing frames or a blur effect. |
| Stand, as approved | Walks on its feet like the approved still. | A walk cycle drawn at 35 degrees (100k to 280k Codex tokens for 5 views) and the open foot-slide question. A walking hummingbird may also read odd, since real ones cannot walk. |
| Both | Stands when still, lifts off to move. | The most art: stand idle, take-off, hover move and landing, with pops between them. |

Hover breaks his feet rule for this one bird. The falcon keeps the rule, and its take-off still reads as its own
power: it climbs high, while the hummingbird stays low.

## First slice, if he picks version 1
**Kindred link and link needle only**, in a new `scripts/moba3d/hummingbird_kit.gd` beside `rhino_kit.gd`, using the
approved front still on a billboard as a stand-in (no new art). The game feel lane hooks it into the match.
- A needle that hits an ally heals it by 100 and links it.
- A linked ally heals 10 per second while it stays inside 9 m.
- The link breaks past 9 m, and a new heal moves it to the new ally.
- A needle that hits an enemy damages it by 60 and makes no link.

**Headless check:** a `tools/debug/` script that spawns the hummingbird, two allies and an enemy, fires the needle at
each, then measures the healing over 3 s, walks the ally to 9.5 m and checks the link is gone. `--check-only` first.
