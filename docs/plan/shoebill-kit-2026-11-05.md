# Shoebill kit: two versions to pick from (draft, 2026-11-05)

**Status, 2026-11-05:** Preston picked **Version B, Thoth's moon** ("Version B, moon"). The section ready to go into
`docs/plan/moba-kits.md` is at the end of this file. The numbers are still proposals until he sets them.

**Nothing here is canon.** Every name and number below is a proposal for Preston to edit. Once he picks, the
Shoebill session writes the result into the shoebill section of `docs/plan/moba-kits.md`.

**Where this file lives:** copied to the main folder on 2026-11-05 on Preston's okay. This is now the main copy.

## What was used
- **Read this session:**
  - **The SMITE wiki's Thoth page, structure only:**
    - The ult reaches about twice as far as his line skill.
    - His cooldowns run roughly 10 s, 14 s, 5 s and 90 s.
    - His ult charges in three steps over 3 s and can be fired early for less.
    - His dash's follow-up roots one target and slows the rest.
  - **This project's numbers:**
    - Every machine has 600 HP, and one kit hit is 60.
    - The stand-in basic attack is 30 damage at 6 m.
    - Machines move at 3.5 m/s.
    - Towers shoot 12 m.
    - The arena is 84 x 156 m, and its lanes are 14 m wide.
    - The fennec's bolt goes 7 m at 12 m/s.
    - A slow cuts speed to 0.6.
  - **The roster checks in `moba-kits.md`:**
    - The lobster owns the pull.
    - The lobster (pinch) and the shoebill (marsh) own roots.
    - Silence has had no owner since the fennec dropped it today.
- **General knowledge, not read:**
  - Long-range MOBA mages that trade movement for reach: skills that charge longer while held, ults that plant
    the caster in place for very long shots, and long channelled snipes. The structure taken: **standing still
    is the price of range**, and a visible line on the ground warns the target during the wind-up.
- **Thoth himself:** the moon, time-keeping, writing, and weighing the hearts of the dead.
- **Copied from these:** nothing. No names, no numbers, no text, and no glyphs or books.

## Shared by both versions
- **Animal trait kept: patience** (the shoebill's real habit of standing dead still, then striking).
  - After **1 s** standing still it gains a charge every **1 s**, up to **3**.
  - Each charge adds **+15% damage and +1 m range** to the next slot 1 or 2.
  - Charges survive **3 s** of walking, so a small dodge doesn't throw them away. A cast spends them all.
  - The ult winds up standing still anyway, so it doesn't use charges.
- **Body numbers:** unchanged from the match, the same for every machine until Preston sets them: 600 HP and
  3.5 m/s.
- **Why the scale:**
  - The bolt at 10 m (13 m charged) outranges the 6 m basic attack and the fennec's 7 m bolt.
  - The ult at 24 m is twice a tower's reach, so it can finish a target under a tower from outside it. That is the
    point of a long-range mage, but it needs a playtest.

## Version A: the animal kit, made concrete
The kit as written today, with names and numbers. All five parts come from the bird, which is what the
2026-11-04 rule moves away from.

| Slot | Proposed name | What it does | Numbers | Cooldown |
|---|---|---|---|---|
| Passive | **Still Water** | Patience, as above. The eye lenses brighten with each charge. | 3 charges, see above | none |
| 1 | **Bill Clatter** | Clatters its bill and fires a sound wave down a line. It passes through every enemy it meets. | 10 m (13 m charged), 14 m/s, 60 damage (87 charged), 1.2 m wide | 6 s |
| 2 | **Mire** | Throws a marsh patch on the ground. It hides from enemies after 1 s. The first enemy to step in is rooted and damaged. | Up to 8 m away, 1.6 m across, root 1.2 s, 50 damage, lasts 20 s, 2 at once | 12 s |
| 3 | **Updraft** | A wing-beat hop backward. The gust where it took off slows enemies. | 5 m back in 0.35 s, gust 2.5 m across, slow 1.5 s | 14 s |
| 4 | **Long Strike** | Winds up standing still, then stabs its bill forward. The body lunges 2 m and a shock line runs on down the lane. | 24 m line, 1.6 m wide; three wind-up steps of 0.8 s; 120 / 180 / 240 damage; fire after step 1 or wait | 80 s |

**Art it needs:**
- **Body moves:** clatter (bill open and shut), the hop, and the wind-up and lunge.
- **Effects:** the sound wave, the marsh patch and the shock line.
- That is 3 body moves and 3 effects.

## Version B: Thoth's moon (the power theme)
The bird gives the body and patience. The rest is **moonlight from its eye lenses**, the one glowing part the
approved take E already has. The charges become moon phases: crescent, half, full.

| Slot | Proposed name | What it does | Numbers | Cooldown |
|---|---|---|---|---|
| Passive | **Moon Phases** | Patience, shown as a moon disc over its back that fills crescent, half, full. | 3 charges, see above | none |
| 1 | **Moonbeam** | A thin beam of light from the eye lens. A 0.3 s line on the ground warns the target, then the beam hits everything in the line. | 10 m (13 m charged), 60 damage (87 charged), 1 m wide | 6 s |
| 2 | **Moon Pool** | Sets a pale disc of light on the ground that only its team can see. The first enemy to step in is pinned by the light. | Up to 8 m away, 1.6 m across, root 1.2 s, 50 damage, lasts 20 s, 2 at once | 12 s |
| 3 | **Wane** | The same wing hop backward. The takeoff spot flares bright and dazzles: a slow. | 5 m back in 0.35 s, flare 2.5 m across, slow 1.5 s | 14 s |
| 4 | **Moonlance** | The moon disc fills in three steps over its head, then a lance of light fires down the lane. | 24 m line, 1.6 m wide; steps 0.8 s; 120 / 180 / 240 damage; fire after step 1 or wait | 80 s |

**Art it needs:**
- **Body moves:** one cast pose (head forward, lenses lit) for slots 1, 2 and 4, and the hop.
- **Effects:** the beam, the pool, the flare, the moon disc and the lance.
- That is 2 body moves and 5 effects. Effects are the cheaper half: the PixelLab effect tool and Godot shaders
  are free.

## Alternatives (swap any in)
- **B with one wetland touch:** keep Mire instead of Moon Pool.
- **Silence is free on the roster.** Thoth is the god of words. Moonbeam at full charge could also silence for
  0.8 s. That would make the shoebill the roster's only silence, on top of a root. It is strong, so it is
  optional.
- **Lunge as the animal trait instead of patience:** then the passive becomes moon phases charging over time
  (not standing still). This drops the shoebill's most distinct habit, so it isn't recommended.
- **Not proposed:** a blink in place of the hop, because blinking is the fennec's thing now.

## Roster checks
- **No pull** (the lobster's).
- **The root stays one of two** (lobster and shoebill), as the roster expects.
- **Nothing held in hand:** sound from the bill in A, light from the eye lenses in B.
- **Range:** the only machine past 12 m. One open risk: whether 24 m feels unfair against a tower diver. That is a
  playtest question, not a drawing one.

## First slice, once he picks
- **Build:** patience and slot 1 only, on a stand-in body. The shoebill has no 35-degree stills yet.
- **Where:** in its own `shoebill_kit.gd`, with the game feel lane, which owns the shared kit and director code.
- **Headless check:**
  - stand still 4 s and read 3 charges;
  - fire and measure the reach, 13 m, and the damage, 87;
  - walk 3.5 s and read that the charges are gone.

---

## Ready to paste into `docs/plan/moba-kits.md` (Version B, picked 2026-11-05)

**1. Replace the whole shoebill section (from its `###` line down to its "Art it needs" line) with:**

### Shoebill (`shoebill_m`), ode to Thoth
**Role:** long-range mage. Waits, then hits from very far away.
**Took:** long-range spell damage, a trap on the ground, a hop back to escape, a very long line ultimate, and the
moon as the power theme (Preston picked Version B, 2026-11-05; draft `docs/plan/shoebill-kit-2026-11-05.md`).
**Left:** the scribe and glyph theme, and the books.
**From the animal (the one trait):** standing perfectly still, as patience. The wing hop stays as its body move.
**Power theme:** moonlight from its eye lenses. Patience charges show as moon phases: crescent, half, full.

| Slot | What it does | Cooldown |
|---|---|---|
| Passive, moon phases | Standing still fills a moon disc over its back, crescent, half, full; each phase adds damage and range to the next slot 1 or 2. Charges survive a short walk. | none |
| 1, moonbeam | A thin beam of light from the eye lens down a long line, after a short warning line on the ground. Hits everything in the line. | short |
| 2, moon pool | Sets a disc of light on the ground that only its team can see; the first enemy to step in is rooted and damaged. | medium |
| 3, wane | A wing hop backward; the takeoff spot flares and slows enemies. | medium |
| 4, moonlance | The moon disc fills in three steps over its head, then a huge lance of light fires down the lane. Can fire after the first step for less. | long |

**Proposed numbers (Preston sets them):** patience 1 s to start, a charge a second up to 3, +15% damage and +1 m
each, kept 3 s while walking; moonbeam 10 m (13 m charged), 60 damage, 1 m wide, 6 s; moon pool up to 8 m away,
1.6 m across, root 1.2 s, 50 damage, 20 s, two at once, 12 s; wane 5 m back, slow 1.5 s, 14 s; moonlance 24 m,
1.6 m wide, steps 0.8 s, 120 / 180 / 240 damage, 80 s.
**How it plays:** stand still at the back to fill the moon, moonbeam from range, moon pools to guard its flank, wane
when someone dives it. Moonlance to finish a fleeing target or open a fight from twice a tower's reach.
**Art it needs:** one cast pose (head forward, lenses lit), the wing hop; effects: beam and warning line, moon pool,
takeoff flare, moon disc phases, lance.

**2. Role map row:** change the shoebill's signature from "patience, lunge strike" to "patience, moonbeam,
moonlance".

**3. Roster checks line:** "roots on the lobster (pinch) and the shoebill (marsh)" becomes "... and the shoebill
(moon pool)".

---

## Built: first slice (2026-11-05, Preston "Yes, build it")
- **Files:**
  - `scripts/moba3d/shoebill_kit.gd`: moon phases, moonbeam and the basic attack.
  - `scripts/moba3d/shoebill_field.gd` and `scenes/moba3d/shoebill_field_test.tscn`: the field to press play on.
  - `tools/debug/shoebill_kit_check.gd`: the headless check.
- **Basic attack, lens flick (proposal, added for the game feel lane's basic-attack hook):** a short flick of
  light from the eye lens that hits the first enemy in line. 7 m, 28 damage, every 1.0 s. The stand-in it replaces
  did 30 at 6 m every 0.9 s, so it trades a little damage for reach.
- **Body:** a stand-in (the field's player keeps its frames) until the shoebill has 35-degree frames.
- **Effects:** placeholders drawn in code (moon disc, ground line, beam box), until the VFX pass.
- **Not built:** moon pool, wane, moonlance; the shoebill is not in the match yet (the game feel lane adds machines).
