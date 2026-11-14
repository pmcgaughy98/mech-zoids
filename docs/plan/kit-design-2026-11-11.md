# Kit design pass: what makes a kit special, applied to the roster (2026-11-11)

Kit design session, started from the hub on Preston's ask. **Everything below is a draft for Preston to edit**,
except the hippo's Pressure kit, which he approved and which is now in `docs/plan/moba-kits.md`. No code was touched.
Names and numbers are his; the ones here are proposals.

His words:
- "we need to make a session that really thinks about this kit phenemona. Because like in games like league of
  legend some abilities are map effecting or create a large head version of the character that sweeps a wide area.
  Idk but we need to step our kit game up"
- On the hippo: "how does the kit use hippos unique abilities? ... what would differiantie it from just uploading
  real hippos right?"
- On the hippo draft: "Pressure, go with it ... this kit sounds good. Also like the bacchus ode by 'filling up the
  wine flask' to upgrade abilites"

Standing rule kept: kits are inspiration only. Only structure is taken from League and SMITE (meters, zones,
projections, camera moves), never a champion's or god's kit.

---

## The short answer
A kit stops being "an animal that attacks" when:
1. **One rule runs through the whole kit** (the identity mechanic), and at least three of the five buttons fill it,
   spend it or change it.
2. **That rule lives on the body** where you can see it: tank windows, pistons, plates, a tail.
3. **The motion is the animal, the effect is the machine.** A real hippo yawns, flops, wallows and bites. Ours does
   the same motions, but what comes out is a pressurised spray, piston legs, a coolant dump and a hydraulic clamp.
   That is the answer to "what would differentiate it from just uploading real hippos".
4. **About half the roster leaves something on the map** (a zone, a wall, a gate, a field), and **a few, on
   purpose, project a giant copy of a body part** across a wide area.
5. **Ultimates change the body, the world or the camera**, not only the numbers.
6. **Everything is built to read from a chase camera**, which sees much less of the field than a top-down MOBA.

---

## Principles

### 1. One identity mechanic per machine
- It is a rule, not a slot: a meter, a stack, a state or a placed object that most of the kit talks to.
- **The test:** remove it and at least three buttons change. If only the passive changes, it is a passive, not an
  identity.
- **No two machines share a verb.** The roster table below gives each machine one verb (fill and spend, absorb and
  release, lend and recall, weigh down...).
- **An enemy can read it and play around it.** A full gauge is a warning: back off, bait it out, or kill it first.
  Power the enemy cannot see is frustration, not depth.
- The house example is already built: the rhino's **Seismic charge**. Hits load the pistons; Brace's release and the
  Tremor charge's finale spend them (`rhino-kit-synthesis-2026-11-10.md`).

### 2. Grown from the body, shown on the body
- The power-body sheets already require that "every body should make its power source and delivery mechanism
  visible while idle" (`power-body-recreations.md`). The identity mechanic should be that power source: the hippo's
  tanks, the rhino's pistons, the gorilla's forearm hex plates, the squirrel's tail lights, the shoebill's moon disc.
- The gauge is a material on the model (fill bands, glow, a plate lighting up), with the HUD as backup, not the
  other way round.

### 3. Abilities that change the map
What they add: the fight becomes about space, not only targets. A pool, a wall or a gate stays after the cast and
makes everyone else decide: go around it, fight in it, or break it.

| Kind | What it does | Roster examples (current or proposed) |
|---|---|---|
| Wall | blocks movement or shots | gorilla hex dome, proposed hex wall |
| Field | lingers, slows, heals or hurts | rhino tremble circle, hippo coolant pool, falcon storm field |
| Trap | hidden until stepped on | shoebill moon pool |
| Route | moves people across the map | fennec gates |
| Arena | locks a fight in place | kangaroo boxing ring, gorilla dome trap |
| Pull point | drags things to a spot or along a flow | lobster gravity well (proposed), shark currents (proposed) |

Rules for them:
- **One lasting object per machine at a time from its basic slots**, plus its ultimate. Otherwise a team fight
  turns to soup.
- **Short lives** (about 3 to 6 s) unless it can be broken, like the dome's wall health.
- **Team colour on the edge**, so a glance says "theirs" or "ours".

### 4. Giant projections of a body part
Preston's "large head version of the character that sweeps a wide area". Later the same day he named the ability he
meant: Ornn's Call of the Forge God in League. It is a giant summoned elemental that charges across the map toward
Ornn, and he can headbutt it to send it back, bigger. That pattern, and where it fits our roster:
`docs/reference/moba-kit-catalog-2026-11-11.md`.
- **It is a hard-light copy of the machine, or of the part it fights with**: the wolf's head, the shrimp's claw. It
  reads as "that machine, huge" and needs no new design.
- **It sweeps or travels along a shape that was shown first**: a cone, a line or a circle. The wind-up is the dodge
  window.
- **It should be cheap to make.** In Godot it is plausibly a scaled copy of the part's mesh with a translucent
  emissive shader, so no new model or clip is needed. Not tested; the look lane should confirm.
- **Rare on purpose: four in the roster**, each from a different body part:
  - ~~a giant charging summon of the whole machine, Ornn-style~~ (dropped by Preston, 2026-11-11);
  - the wolf's head (Run Down);
  - the falcon's wings (Sky Barrage);
  - the pistol shrimp's claw (its ultimate).

  If every ultimate has one, none of them is special.

### 5. Scale and spectacle on ultimates
An ultimate uses at least two of these four:
1. **The body changes shape:** plates open, tanks blaze, the tail flares.
2. **The world changes:** a dome, a well, a field, a gate ring.
3. **A giant projection** (only the four above).
4. **The camera moves:** your own ult pulls the camera back or up one step so you see the whole area, then returns.
   Preston already set this for the falcon ("55 to 60, no new art"); this pass proposes it for every ult that covers
   a wide area.

The ult also **spends the identity mechanic hardest**: the rhino's finale, the hippo's Lockjaw, the gorilla's dome.
Every big ult needs a wind-up the enemy can see. Scale without a dodge window feels unfair.

### 6. Reading it from a 3D chase camera
This is where a chase camera differs most from League's top-down view.
- **Ground shapes flatten.** From a low chase camera, a 4 m circle is a thin oval, and its near half is hidden under
  your own machine. Every zone needs **a rim that stands up**: 0.3 to 1 m of light, mist or panels, or rising
  particles. A flat ground decal alone is not enough.
- **You see forward, not around.** Threats from behind and from off screen need sound and a screen-edge marker.
  Every ult gets a map-wide sound and an edge arrow toward the caster. This also makes "from behind" mechanics (the
  rhino's front plating, the fennec's backward bolt) stronger here than in a top-down game.
- **Your own gauge goes on your back and flanks**, because that is what your camera sees. The shoebill's moon disc
  and the squirrel's tail already do this. Put the hippo's flask on its back pipes and side windows, and the
  gorilla's cells on its forearms.
- **Enemy tells are silhouette changes** that read at 20 m or more: rearing, flaring, opening, a projection rising.
  A glow alone gets lost in a busy fight.
- **Walls block the camera's view.** Tall effects (gate rings, pillars, projections) read over a wall; flat ones do
  not.

---

## The pressure overlap, settled
The hippo lane found three machines using "pressure". This keeps the word on the hippo and gives each machine its
own verb.

| Machine | Verb | What it never does | Colour (to keep the water effects apart) |
|---|---|---|---|
| Hippo | **fill and spend**: a reservoir it fills by fighting and pours into its next skill | burst in one snap; drag enemies | violet (its power-body sheet: "luminous violet belly chamber"), which is also the wine |
| Pistol shrimp | **burst**: it cocks the claw, and one snap sends out a single cavitation shockwave | keep a reservoir; leave a field | white flash, bubble |
| Shark | **currents**: it moves enemies *along* a flow, sideways or along its path | pull to a point (that is the lobster's) | aqua (its sheet: "aqua gill chambers") |

**One change from the hippo lane's suggestion:** the lane suggested "the shark pulls", but the lobster already owns
the pull (roster checks in `moba-kits.md`). So the shark **drags things along a current** instead of reeling them in.
The lobster's open ult option is called "undertow" today. This pass proposes renaming it **gravity well**, which
fits the lobster's gravity body, so that "undertow" belongs only to the shark.

---

## Roster table
**What changes** is measured against `moba-kits.md` as it stands today. Only the hippo row is applied. Every other
change waits on Preston's yes, section by section.

| Machine | Identity mechanic (verb, body source) | Map-changing or giant projection | What changes from moba-kits.md |
|---|---|---|---|
| Rhino | **absorb and release:** Seismic charge in the pistons | tremble circle (field); the Tremor charge carries enemies to the finale | Design: nothing. The section is behind the built slices (Brace and release, Tremor charge, the carry) and should catch up. |
| Gorilla | **lend and recall:** hex cells on the forearm plates, placed as shields and walls, flying back | **hex wall** in the empty slot 2; the dome in the ult | Fill slot 2 with the hex wall; shields, wall and dome all draw on six cells. |
| Hippo | **fill and spend:** Pressure Tanks; full tanks overcharge the next skill | the toxic puddle and the Toxic Flood lake (fields). The giant jaws were dropped (Preston, 2026-11-11) | **Superseded:** see `docs/plan/hippo-kit-pressure-2026-11-11.md`. |
| Lobster | **weigh down:** gravity; its hits make enemies heavy, and at full weight they are grounded | **gravity well** ult (the renamed undertow) | Weight on claw grab and pinch; a new control type, grounded; rename undertow and recommend it as the ult. |
| Kangaroo | **rhythm:** capacitor gauntlets charge per landed hit; the tail discharges the kick | boxing ring as a true duel (option) | Make the stacks visible on the gauntlets; the ring keeps outsiders out (option). Installed kit unchanged. |
| Pangolin | **magnetise and home:** a salvaged target is magnetised, and the iron ball curves toward it | none | **Redone 2026-11-12:** claw rake became salvage (armour theft), dig in became rail dive. See "Pangolin redo". |
| Wolf | **execute:** hunts the wounded | **giant spectral wolf head** on Run Down | The phase chambers show the scent; the projection on the ult. |
| Shoebill | **stillness:** patience fills the moon disc | moon pool (trap); moonlance leaves a lit strip | Small: the lit strip after moonlance. |
| Fennec | **relocate:** gates | the gates themselves (route) | None. Its open items stand. |
| Falcon | **altitude:** take off stores height, stoop spends it | **giant wing shadow** over Sky Barrage; storm field | Height as a resource; the projection and field on the ult. |
| Squirrel | **relay:** shots jump to a second target | Tail Ping relay post (option) | None needed; the relay post is optional. |
| Chameleon | **unseen:** cloak | **refraction field** ult (option) | Option: the ult becomes a fixed ambush zone instead of a moving cloak. |
| Hummingbird | **link:** beams from the throat plate | the surge line beam; kindred ring | None. |
| Shark | **currents:** undertow drags along a flow | current lanes; maelstrom ult | New machine, kit undecided: identity only. |
| Pistol shrimp | **burst:** cock and snap | **giant projected claw** on its ult | New machine, kit undecided: identity only. |
| Bombardier beetle | **mix:** two sprays react when they meet | the reaction puddle | New: identity only. |
| Mantis | **cut lines:** blade slashes linger in the air for a beat | the lingering slashes | New: identity only. |
| Hornet | **stack:** venom builds on one target until a paralysing sting | none | New: identity only. |
| Electric eel | **conduct:** charged ground shares a hit among every enemy standing on it | charged ground | New: identity only. |
| Dragonfly | **paint and volley:** marks several targets, then fires at all of them | none | New: identity only. |
| Scorpion | **plant:** braces its pincers for a siege stance with longer range | none | New: identity only. |
| Jellyfish | **trail:** drifts and leaves a tendril trail that heals allies and stings enemies | the trail | New: identity only. |
| Tortoise | **preserve:** stasis and rewind on an ally | a slow-time field | New: identity only. |
| Cobra | **terrain:** moves along and over walls | uses the map's walls | New: identity only (his wall-slither idea). |
| Spider | **seal:** a thread stores the damage a target takes and deals it again when it snaps | none | New: identity only. |
| Bison | not read this session | | No proposal: its power direction was not in the files read. |

The verbs are all different. The closest pairs are covered under "Overlaps to watch".

---

## Per-machine proposals (drafts for Preston)

### Hippo: Pressure (superseded the same day; kept for the record)
**Superseded.** Preston's later calls on 2026-11-11 are in `docs/plan/hippo-kit-pressure-2026-11-11.md`, which is now
the source of truth:
- passive Pressure Tanks;
- 1 Vent, a toxic purple spray;
- 2 Piston Drop, which stuns about 0.5 s after landing;
- 3 Lockjaw, which drags the target into the lake ("Drag them into the lake"), with no fling away;
- 4 Toxic Flood, which blows all three tanks.

Coolant Dump is dropped as a slot, and the three flask bands, the soak and the aimed fling below no longer apply.
`moba-kits.md` mirrors the new file (updated 2026-11-12).

The original draft follows.
Approved slots: passive Head of Pressure, 1 Vent, 2 Piston Drop, 3 Coolant Dump, 4 Lockjaw. Body: three tanks of
glowing violet fluid with windows (one on each side, one under the throat), pipes from a back pack, and piston legs.

**The flask (the Bacchus ode), folded into Head of Pressure:**
- The tanks fill in three bands as it deals and takes damage.
- **The next skill, ultimate included, drinks the whole flask.** It gets one upgrade step per band, and then the
  tanks are empty.
- That is the decision the flask creates: spend a third now, or keep biting until the flask is full and the big
  version is ready.
- The full flask is also the enemy's warning. The jaw vents hiss and steam, and the back pipes glow.
- Proposed numbers:
  - steady trading fills it in about 8 s;
  - after 5 s out of combat, it drains one band every 4 s.

| Slot | Base (approved) | Each band adds (proposal) | Full flask (proposal) |
|---|---|---|---|
| 1 Vent | Jaws open; the throat tank blasts a cone of pressurised spray. Damage, and soaked enemies deal less for a short time. | +0.8 m cone, +0.5 s soak | A high-pressure blast: the cone also pushes enemies back to its edge, and the soak lasts longer. This replaces the giant head, which Preston dropped: "I don't think it fits with hippo". |
| 2 Piston Drop | The legs fire it into the air; it lands with a shock ring from the feet that stuns. | +1 m range, +0.4 m ring | The ring also soaks everyone it hits. |
| 3 Coolant Dump | Empties the side tanks into a glowing pool: heals the hippo while it stands in it and slows enemies. The windows drain. | +0.5 m radius, +1 s | Allies standing in the pool heal too. |
| 4 Lockjaw | A hydraulic clamp on one enemy, which can't act, then the fling. | +0.3 s hold | Flung farther; the landing splash soaks enemies around it. |

- **Soaked** is the kit's one shared status: the target deals less damage for a short time. Vent applies it, and so
  do Piston Drop and Lockjaw at a full flask. Coolant Dump only slows.
- **Proposal: aim the fling.** Lockjaw throws toward the aim point instead of always behind. This splits it from the
  rhino's horn toss, which always throws behind, and it makes the hippo's combo: Coolant Dump, then Lockjaw a carry
  and fling it into the pool.
- **Reads from the chase camera:**
  - the player sees the flask on the back pipes and the side windows (HUD pips as backup);
  - enemies see the throat tank and the hissing vents;
  - the pool gets a low wall of violet mist as its rim.
- **Clips that fit, unchanged:**
  - Hippo_Yawn (Vent; cone 0.35 to 0.95 s).
  - Hippo_Belly_Flop (Piston Drop; off the floor 0.22 s, lands 0.72 s).
  - Hippo_Wallow (Coolant Dump; sinks 0.22 s).
  - Hippo_Chomp (Lockjaw; clamps 0.24 s, flings 1.12 s).
  - Basic chain unchanged: Hippo_Bite, Hippo_Jaw_Swing, Hippo_Stomp.
- **New clips:** none.
- **New effects:**
  - three-band fill on the window material;
  - the spray cone;
  - the pushback wave at the cone's edge;
  - the shock ring;
  - the pool with its rim;
  - the landing splash;
  - the soaked mark;
  - the full-flask hiss and steam.

### Rhino: absorb and release (built)
- **Identity:** Seismic charge, as built in the rhino slices. Nothing new to design.
- **Map:** the tremble circle; the Tremor charge's carry is its spectacle.
- **Doc gap: closed 2026-11-12.** The `moba-kits.md` rhino section now matches the built slices (Preston: "Yes,
  update them").
- **Clips:** the rhino lane's (only `ground_pound_finale` was named in the files read). The synthesis asks for a
  small horn lift in `ground_pound_finale` if the carry stays.

### Gorilla: lend and recall
- **Identity:** the forearm hex plates hold **six cells**, lit while they are home.
  - A hex shield takes one cell, which flies back when the shield ends (more slowly if it broke).
  - **Slot 2 (empty today), hex wall:** plants a short line of three hex panels. Enemies and shots stop; allies walk
    through (the dome's rules).
  - **The ult's dome takes every cell left on the arms**, and its size or wall health grows with them. The more the
    gorilla has lent out, the smaller its dome: a real decision.
- **Map:** the wall and the dome.
- **Chase camera:** the forearms sit at the sides of its own view, so the dark and lit plates read at a glance;
  cells streak out and back.
- **Clips that fit:** Shield_Self, Shield_Ally, Gorilla_ChestBeat_Ult_Codex_ExitTrial, Swat_Left/Right, Gorilla_Slam.
  The wall could use Gorilla_Slam or the registered Gorilla_ShieldDrive_Brace_Trial.
  - Gorilla_ShieldDrive_Brace, Drive, Hit and Brake trial clips are registered, which suggests the gorilla lane is
    already trying something in a slot. Not read; ask the lane before using the slot.
- **New effects:** cell fly-out and fly-back, wall panels, plate lights.

### Lobster: weigh down (gravity body)
*2026-11-12: superseded by the "Lobster rework draft" at the end.* Grounding now overlaps the bison draft's
Coupling Chain ("can't dash or leap"), so that draft swaps it for a pull toward the lobster.
- **Identity:** claw grab and pinch each add weight, shown as gravity rings at the enemy's feet.
  - Heavy enemies move slower.
  - **At full weight a target is grounded** for a short time: it cannot dash, leap, blink or take a fennec gate.
  - That is a new control type in a roster that lost its only silence.
- **Ult:** keep the choice he already has (`moba-kits.md`, open choice 2), but rename undertow to **gravity well**.
  It slams the crusher claw into the ground, and enemies inside gain weight every half second and are dragged to the
  centre.
  - This pass recommends gravity well: a map-changing ult, and it spends the identity.
  - Shell guard keeps the lobster a purer support.
- **Molt passive:** unchanged.
- **Clips:** none read. Needs the claw shot and cable, pinch, tail flip, and a claw slam for the well.
- **Effects:** gravity rings, grounded mark, the well with a standing rim.

### Kangaroo: rhythm (installed kit stays)
- **Identity:** the rhythm stacks, made visible.
  - Each stack lights a ring on a capacitor gauntlet.
  - The rhythm kick discharges them through the tail, with a small floor flash.
- **Option 1, a timing bonus:** a basic pressed on the beat adds two stacks. This only works if the chain is tapped,
  not held; the game feel lane knows which.
- **Option 2, a true duel:** the boxing ring also keeps other machines out, which makes it a map-changing arena.
  **On since 2026-11-12:** Preston answered "Yes, block them" (area attacks don't hit the pair in the ring).
  With the Ne Zha lock added, nothing can answer the bout while it runs, so its length and cooldown are the
  limits. Game feel has asked him whether the block still holds. See moba-kits.md, "Title bout: bob and weave
  toward Ne Zha".
- **Clips that fit:** the installed ones (Jab_Left, Jab_Right_Quick, Hook_Right, Guard_Counter, Ring_Cast, and the
  hop and tail kick clips, whose names were not read).
- **New clips:** none.
- **New effects:** gauntlet rings, tail discharge, ring posts.

### Pangolin: magnetise and home (magnetic body)
- **Identity:**
  - Claw rake magnetises the target with a blue charge (proposal: 4 s).
  - The iron ball curves toward the nearest magnetised enemy. Steering still works; the curve adds to it.
  - Each hit scale flare blocks magnetises the attacker.
- **Option:** dig in becomes a **rail dive**: it rides the spine rails' field to a magnetised enemy or a spot. That
  trims the kit to one animal trait (the curl), but it costs the dig clips if the pangolin lane has made them. Ask
  that lane first.
- **Map:** none.
- **Chase camera:** magnetised enemies wear a ring that the pangolin's player can see at range.
- **Clips:** the pangolin lane's, not read.

### Pangolin redo: slots 1 and 2 (2026-11-12)
**Why.** Preston, relayed by the pangolin effects lane: "Dig and claw are too much like animal". This is the
problem he named on 2026-11-12: "my mechs have been very linear", only animal, while gods get powers, elements
and weapons. Claw rake and dig in came from the body layer alone. The section above only made dig in an option.

**The pangolin's four layers:**

| Layer | Pangolin |
|---|---|
| Body | the overlapping scale armour, the curl into a ball, the claws |
| Power | magnetism (Codex's body: copper-bronze plates, spine rails, flank field couplers) |
| Rig | a magnetic salvage hauler, built to strip plating off wrecks and haul it along rails (approved 2026-11-12) |
| Ode | Kuzenbo's spiked shell (the sharp scales passive) |

**Why that rig.** Every enemy is a machine, so a magnet is a threat to all of them. A salvager strips armour, and
a diver that eats armour can stay in the back line without hiding underground. That replaces what dig in did.

**The kit, slot by layer:**
- **Basic attack:** claw swipes. The claws stay, as the plain hit, and the Claw_Rake clip gets used.
- **Passive, sharp scales:** ode crossed with body. Unchanged.
- **1, salvage (rig crossed with power, landing on the body):** its field tears plates off enemies in a short
  cone in front. They lose armour; it gains that armour for a few seconds, and the stolen plates sit visibly on
  its shell. Each enemy hit is magnetised (about 4 s). This replaces claw rake's armour shred with theft.
- **2, rail dive (power crossed with rig):** it rides its spine rails' field in a straight line. On a magnetised
  enemy it locks on from long range and streaks to them; without one, it is a short dash to a spot. Arriving on
  a magnetised enemy spends the charge for extra damage. It can be targeted the whole way, unlike dig in.
- **3, scale flare (body crossed with power):** unchanged, plus each blocked hit magnetises the attacker.
- **4, iron ball (body crossed with power):** unchanged, plus it curves toward the nearest magnetised enemy.

**The loop:** salvage magnetises, rail dive and iron ball find magnetised targets, and scale flare magnetises
whoever hits back. Magnetism runs through four slots; it is what ties the kit together. No slot is from one
layer only.

**Colour:** copper with amber sparks, Preston's theme for every pangolin ability (per the effects lane). That
replaces the "blue charge" above. The blue spine rails are body art, not the effect colour.

**Overlap checks:**
- **Rails:** the bison draft also has rails (Lay Track, the Express line). To keep them apart, the pangolin's rail
  dive leaves no track on the ground: it is a streak of amber sparks off its own spine. The bison owns rails on
  the ground.
- **The pull:** the lobster owns pulling enemies. Salvage pulls plates, not machines; rail dive moves the
  pangolin. No overlap.
- **Armour theft:** no other kit steals armour, as far as moba-kits.md shows. Not checked against every draft.
- **Knock-up:** the pangolin keeps it through iron ball. Dig in's erupt knock-up is gone.

**Clips:** Claw_Rake moves to the basic attack. **Dig_In and Dig_Erupt are parked:** ask the pangolin 3D lane
before dropping them. New clips: salvage (field pose, plates flying in), rail dive (launch, streak, arrive).

**Rejected:** a railgun firing its scales. It uses the same power and rails, but it turns a diving fighter into
a ranged poke.

**Approved (Preston, 2026-11-12): "Yes, approve both".** That covers salvage, rail dive and the salvage-hauler
rig. The effects, 3D and game feel lanes were told the same day. Preston to the effects lane: "start with the
magnetised mark".

**Cue for the magnetised mark (settled by the game feel lane, 2026-11-12):** the kit sets `kit.mag_target`
(Node3D) and `kit.mag_time` (seconds), then emits `cue("magnetise")`. It emits once per target, for every source:
salvage hits, scale flare blocks, and refreshes. Observers read both fields inside their cue handler. There is no
direct call into the effects node, so a missing effects file can't break the kit. (The effects lane had also
offered `fx.magnetise(target, seconds)`; game feel chose the cue to match the other lanes.)
**When:** the pangolin kit port comes after the hippo port (Toxic Flood and the tanks still left there). The
effects lane can build against this cue now.

### Wolf: execute (spectral hunter body)
- **Identity:** unchanged (hunts the wounded). The phase chambers on its back glow brighter as the scented target
  weakens, so the player reads the hunt from behind.
- **Run Down (ult):** a **giant spectral wolf head** projects from the chambers and lunges down the line to the marked
  target, ahead of the wolf, showing the path. Then the wolf follows.
- **Clips:** none read. Needs lunge, bite, howl, sprint, and one cast pose for the projection.

### Shoebill: stillness (unchanged)
- **One small add:** moonlance leaves a lit strip down its line for a few seconds, and enemies on it are revealed.
- The moon disc over its back is already where a chase camera looks, so it reads well.

### Fennec: relocate (unchanged)
*2026-11-14: settled; see "Fennec: the pending portal draft, checked" at the end.*
- The gates are its map change.
- From a chase camera the rings need height so they read over walls.
- Its open items in `moba-kits.md` stand.

### Falcon: altitude (storm/ion body)
*2026-11-13: superseded by the "Falcon rework draft" at the end. Take off goes, so the stored height goes with it.*
- **Identity:** take off stores height, shown as charge in the breast window, for a short time. A stoop from height
  dives farther and hits harder. Keen eye unchanged.
- **Sky Barrage:**
  - a **giant projected shadow of its wings** spreads over the area;
  - the darts fall as ion bolts;
  - the area stays a storm field that slows while the barrage lasts.
- **Camera:** the steep ult camera Preston already set.
- **Clips:** none read. Needs take off, land, stoop, and wing dart fire.

### Squirrel: relay (unchanged)
- **Option:** Tail Ping leaves a relay post that keeps revealing for a few seconds. Low priority.

### Chameleon: unseen
*2026-11-13: see the "Chameleon rework draft" at the end. The refraction field below stays an option only.*
- **Option:** the ult becomes a **refraction field**: a fixed area where allies stay hidden while inside, even when
  moving, and enemies outside cannot see in. A planned ambush spot instead of a moving team cloak.

### Hummingbird: link (unchanged)
- The surge line beam already acts as a moving line on the map.

### New animals (identity only; kits undecided)
Each gets one verb, so no two collide when their kits are written.

| Machine | Verb | What it does |
|---|---|---|
| Shark | currents | Its moves lay currents that drag enemies along them and speed allies who go with the flow. The ult is a maelstrom it circles, dragging everything around the ring. |
| Pistol shrimp | burst | It cocks the claw, and the snap sends one bubble that bursts at a point. The ult: a giant projected claw snaps over an area, and the bubble collapses with a blast and a flash. |
| Bombardier beetle | mix | The shoulder nozzles hold two chemicals. A spot hit by both reacts and blasts. |
| Mantis | cut lines | The magnetic blades leave slashes hanging in the air for a beat that cut whoever crosses. |
| Hornet | stack | Venom builds on one target; at full stacks, a paralysing sting. |
| Electric eel | conduct | Charged ground: a hit on one enemy standing on it is shared by every enemy on it. |
| Dragonfly | paint and volley | The compound eyes mark several targets, then one volley hits them all. |
| Scorpion | plant | The pincers brace into a siege stance; the tail cannon gains range while planted. |
| Jellyfish | trail | Drifts and leaves a tendril trail that heals allies and stings enemies. |
| Tortoise | preserve | Stasis and rewind on an ally; a slow-time field. |
| Cobra | terrain | Moves along and over walls (Preston's wall-slither idea). |
| Spider | seal | A thread stores the damage a target takes and deals it again when it snaps. |

---

## Overlaps to watch
- **Rhino and hippo both fill a gauge by fighting.** This is the closest pair. Keep them apart:
  - the rhino fills only from hits taken while braced, and spends on two fixed moves;
  - the hippo fills from all trading, and spends on whichever skill comes next.
- **Grab-and-fling:**
  - the hippo's Lockjaw: now a carry and slam ("Drag them into the lake"), not a fling;
  - the rhino's horn toss: always behind;
  - the rhino's carry: forward, to the finale;
  - the lobster's claw grab: to itself.

  Four directions, four jobs.
- **Lines between things:** the hummingbird's beam (ally to itself), the lobster's cable (enemy to itself) and the
  spider's thread (on one enemy). Give each a different form: beam, cable, thread.
- **Magnetism:** the pangolin's body and the mantis's "magnetic blade forearms". Keep the word on the pangolin and
  give the mantis a different power when its kit is written.
- **Planting:** the rhino's Brace (defence) and the scorpion's siege stance (range). Same pose, opposite jobs; fine
  if the effects look different.
- **Giant projections:** keep them to the four named. A fifth needs a reason.

## Priority if Preston wants more sections rewritten
The kits that score lowest on the principles are the ones built from the animal before the 2026-11-04 rule:
- **lobster** (no power theme in the kit yet);
- **wolf** (all animal); the **pangolin** was redone on 2026-11-12 (see "Pangolin redo");
- **falcon** (all animal);
- **gorilla** (slot 2 empty).

The rhino section only needs to catch up with what is built.

## Four layers: the breadth test, run on the bison (2026-11-11)
Preston: "my mechs have been very linear in terms of when gods and champions they have access to powers and
elements and weapons etc." Then: "Bison will be four layers test".

**What is already broad.** The power-body pass (`docs/plan/power-body-recreations.md`, Codex's lane) gave every
machine a supernatural power: moon, time, fate, gravity, storm, magnetism, phase, signal and more. The narrowness is
in the kits. Most take that one power and make four versions of it, plus the animal's most obvious move.

**The four layers.** A god's kit pulls from several sources at once. Thor has a weapon he throws, lightning he
commands, and the strength of his body. Ours can do the same:

| Layer | The question | The bison's answer |
|---|---|---|
| Body | What does the animal do that nothing else does? | the head-low charge; the hump-powered head sweep bison use to plow snow; pawing before a charge; the herd |
| Power | What supernatural force runs through it? | heat, flame and steam (Preston's pick) |
| Rig | What was the machine built to do? The job hands it weapons and tools for free. | **proposal:** a steam locomotive, with the firebox in the hump, the shoulder exhausts as smokestacks, a cowcatcher plow on the head, a steam whistle, and rails |
| Ode | Which god does it nod to, once? | **Ares** (Preston, 2026-11-12) |

**The rule:** each slot draws from a different layer, and the best slots cross two. A kit where every slot comes
from the power layer is the linear kind.

**Why the bison needed it.** Its proposed kit is in `docs/art/moba/bison_l/take-a/DESIGN.md` (not edited here). It
has four parts, plus a rage mode:
- a heat meter to fill and spend;
- a flame cone;
- a radial steam push;
- a charge.

The meter, the cone and the push are the hippo's Pressure structures done in fire. The charge is the rhino's lane.

**The test draft.** Names and numbers are proposals.

| Slot | Name | What it does | Layers |
|---|---|---|---|
| Passive | Full Steam | Moving in a straight line builds speed and heat; turning sheds it. At full steam, the next hit or ability lands harder. The tell is the smokestack: wisps at rest, a black plume at full steam, tall enough to see over walls. It is not a meter to spend, because the hippo owns fill and spend. | Rig + Power |
| 1 | Plow | A wide head sweep with the cowcatcher. It throws enemies sideways, the way a plow throws snow, and scorches them. Sideways means it is not the hippo's pushback. | Body + Rig |
| 2 | Lay Track | For a few seconds it drops glowing rails behind it. Allies on the rails move faster. On them, the bison hits full steam at once and can't be slowed. Enemies crossing hot rails are scorched. It makes a route, which is a map-changing kind. | Rig + Power |
| 3 | Whistle | A steam-whistle shriek in a ring. Enemies inside are briefly spooked and run away from it: a fear, not a knock. The sound is the tell. | Rig + Power |
| 4 | Express (*dropped 2026-11-12: Preston, no charge for the bison; see the audit at the end*) | **Wind-up:** it paws the ground (the raging bull) while a long straight line of rails lights up ahead, with the whistle heard map-wide. **Charge:** it runs the whole line at full steam, unstoppable, throwing enemies on the line to both sides. **Allies:** any who step on the track before it passes couple on behind it like rail cars and ride to the end. The herd becomes the train. | Body, Power, Rig (Ode open) |
| Basic | | Head sweep, horn hook, stomp. DESIGN.md's alternating head sweep stays. | Body |

**Overlap check:**
- The rails are a line on the ground, like the shark's currents. Currents drag enemies; rails speed allies.
- Express throws enemies aside instead of carrying them, so it is not a drag either.
- The rhino keeps catch-and-throw.

**Art cost.** The current bison concept has no cowcatcher or smokestack. The hump already houses the furnace, and the
paired shoulder exhausts can read as smokestacks. A cowcatcher would be a change to the chin and brow plates. That is
Codex's body lane, so it needs Preston's pick first.

**Open:**
- whether the locomotive rig is right;
- the ode;
- whether Lay Track should also block enemies (a wall) or only scorch them.

## Decisions only Preston can make
1. ~~**The flask**~~ superseded: the newer hippo kit (`hippo-kit-pressure-2026-11-11.md`) uses full tanks to
   overcharge the next skill, then drain. That is per cast, with no bands.
2. **The Ornn-style summon: settled, not needed** (Preston, 2026-11-11: "Doesn't need the Ornn-style"). Ornn was an
   example of the bigger point: gods and champions draw on powers, elements and weapons, and our machines feel
   linear next to them. The breadth question is now the open item. The Ornn notes stay in
   `docs/reference/moba-kit-catalog-2026-11-11.md` as reference.
3. ~~**Lockjaw's fling**~~ settled: Preston picked "Drag them into the lake", with no fling away (see
   `hippo-kit-pressure-2026-11-11.md`).
4. **The lobster's ult:** gravity well (renamed undertow, recommended) or shell guard. And whether "undertow" moves
   to the shark.
5. **Which other sections of `moba-kits.md` to rewrite**, and in what order.
6. **The giant projections:** wolf, falcon, pistol shrimp (the Ornn-style summon is dropped).
7. **All names and numbers.**

## What was read, and what was not checked
- **Read:**
  - `moba-kits.md` (all sections);
  - `power-body-recreations.md`;
  - the hippo lane's Pressure draft;
  - the rhino synthesis (headings plus the Seismic charge and carry lines);
  - the kangaroo kit header;
  - the clip names in `scripts/moba3d` kit code (kangaroo, gorilla).
- **Not checked:**
  - the full clip lists for the rhino and the pangolin;
  - any clips for the other machines;
  - the gorilla's ShieldDrive trial;
  - the bison's power;
  - whether a scaled part mesh with a hard-light shader looks right in the match.

## Too animal: the audit, and the bison's ode (Preston, 2026-11-12)
**His words:** "we don't need an effect that's exactly like orn I was just using that to show how the kits seemed
animal like like a claw attack if i had claws. Or horn if it has horns, or digging if it digs in real life. Like
fennec and pangolin both had digs before I changed manually and fennec has portal powers and pangolin magnetic.
Which we may have to redesign if needed".

**Reading:** the same rule as 2026-11-04 and the four layers above. The animal gives the body and at most one trait.
The other slots come from the power, the rig and the ode. Ornn was an example of that breadth, not a move to copy
(already settled on 2026-11-11: "Doesn't need the Ornn-style").

**The audit, for the machines with a 3D lane plus the bison.** Powers are from `power-body-recreations.md`.

| Machine | Power | Slots that come only from the animal today | Verdict |
|---|---|---|---|
| Rhino | earth and tremor: seismic drive, shoulder transducers, resonant horn | horn toss only (*corrected 2026-11-12:* this row first listed brace and stampede too, which was behind the build. Brace stores and releases Seismic charge, and the stampede is now the Tremor charge, with tremor pulses and the carry) | **one slot.** The charge stays the rhino's one trait now that the bison won't charge. Horn toss moves to the seismic power (draft at the end). |
| Kangaroo | kinetic force: capacitor gauntlets, charged leg assemblies, bracing tail | rhythm, hop and jab, tail kick, guard (the title bout's ring is the exception) | **rework.** Boxing is the one trait, fired through the capacitor gauntlets. The hops and the tail kick move to the kinetic power. The title bout and its Ne Zha weave stay. |
| Gorilla | green shield tech: forearm projectors, chest core, dorsal shield reactor | chest beat (the ult) | **fits; the slot is settled** (Reactor Fault Line, 2026-11-13, at the end). The built kit (`scripts/moba3d/arena_gorilla_kit.gd`, checked 2026-11-12): 1 Hex Shield, 2 Fault Line (a slam that cracks the ground along the aim), 3 Shield Drive (a braced forearm-shield charge that ends in a slam), 4 the chest-beat ult. Chest beat is the trait; Hex Shield and Shield Drive are the power. Fault Line is neither clearly animal nor clearly shield tech. Whether it moves to the reactor or the chest core is Preston's call. *Corrected:* this row first said slot 2 was empty and slot 3 was the leap, which was behind the build. |
| Hippo | pressure: three tanks, pistons | the jaws only (bite, Lockjaw) | **fits.** The template. |
| Pangolin | magnetism; rig: salvage hauler | claws only, as the basic attack | **fits** since today's redo. |
| Bison | heat, flame and steam; rig: steam locomotive (proposal) | the charge (Express) | **rework:** no charge, ode to Ares (below). |

*Since then:* the wolf and the shoebill are checked at the end, and the other six in "The last six, audited".
Basic attacks can stay
animal (a bite, a swat, claws).

**What a kinetic kangaroo rework would touch** (from the kangaroo 3D lane, 2026-11-12; the clip names were
checked in `art/arena_models/kangaroo.glb`):
- Animal-only clips: HopJab, Leap, Flurry (slot 1); TailKick (slot 2, and the title bout's last hit); Guard_Counter,
  Guard_Sweep (slot 3). The basic chain (Jab_Left, Jab_Right_Quick, Hook_Right) stays.
- **Cheap route:** the discharge is an effect on the existing clips. The effects lane already hangs trails on both
  gloves and Tail_Pad. **Costlier route:** new clips with a charge-up pose, one clip round per move.
  **Picked, per the kangaroo 3D lane (2026-11-12):** Preston answered that lane's note with "approve send to effects".
  The lane read it as the cheap route and sent the kangaroo effects lane the brief. This settles only how the
  discharge looks; the kangaroo's slot rework is not drafted yet and is still his to pick.
- Hooks for a charge read already exist: 4 rhythm stacks, then the next basic is the tail kick, with cues at every hit.
- ~~**Open:** if the tail kick becomes a kinetic blast from the charged legs, does the bout's finisher change with it
  or keep the plain kick?~~ **Answered:** "Yes, same blast" (Preston, 2026-11-12, to the kangaroo 3D lane).

**Gorilla body facts for a Fault Line rework** (from the gorilla 3D lane): forearm shield cells front and rear, a
chest core hex, a dorsal reactor hex on the backpack, and 38 bones, including a jaw that opens and sprung shoulder
plates. That lane holds Fault Line's own clip until Preston picks.

**The rhino's, the kangaroo's, the wolf's and the lobster's rework drafts, the shoebill's check and the last six's
audit are at the end**, and Fault Line is settled at the end (Reactor Fault Line). Until
he picks, nothing built is removed, and new clips for the slots in question wait. The kangaroo and gorilla 3D lanes
have confirmed they are holding.

### Bison: no charge, ode to Ares
**His words:** "for the bison I feel like having a charge will make it too much like rhino or having it as such a big
part of kit. I was thinking ode to ares with bison."
- **Dropped:** Express, the charge ult. The rhino keeps the charge.
- **Ares in SMITE 2** (the official site's data, pulled today):
  - Shackles: chains run out; the first god hit is bound to him, can't use movement abilities, and burns. While one
    is bound, he can fire more chains for free.
  - Bolster Defenses: allies around him get more protection and harder basic attacks, growing if they keep hitting
    gods.
  - Searing Flesh: a flame cone from his shield.
  - No Escape (ult): chains to every enemy god around him; he can't be crowd-controlled, takes less damage, and pulls
    them all in.
  - Blessed Presence (passive): auras from his items.
- **What fits a steam bison (proposal, names and numbers his):**
  - **The chains, as red-hot coupling chains from the locomotive.** Ode, rig and power in one slot. A coupled enemy
    can't dash and burns; if it walks off, the chain goes taut and tows it like a rail car. While one is coupled,
    another chain is free.
  - **Bolster Defenses as the herd:** allies near the bison hit harder. It is offence, so it doesn't copy the
    gorilla's passive, which cuts damage taken.
- **Left out of Ares:** the flame cone, because the hippo's Vent is a cone. No Escape's mass pull as is, because the
  lobster's undertow option is a mass pull.
- **Overlaps to watch:** the lobster's claw grab reels one enemy all the way in; the hippo's Lockjaw carries one in its
  jaws. The bison's chain is a leash, not a reel.
- **Open for Preston:** see the draft below.

### Bison kit draft: ode to Ares (2026-11-12, Preston picked "Bison (Ares)")
Names and numbers are proposals; timings are tiers. Ares's kit is from the SMITE 2 site feed (the game files were
not checked for him).

| Layer | The bison's answer |
|---|---|
| Body | **The one trait:** the hump-powered head sweep bison use to plow snow. Basics stay animal too. |
| Power | heat, flame and steam (Preston's pick) |
| Rig | steam locomotive (still a proposal): coupling chains, the whistle, hauling a train |
| Ode | Ares: chains that bind, the war aura, No Escape |

| Slot | Name | What it does | Layers |
|---|---|---|---|
| Basic | | The concept's basic stays: a short, heavy horn hook that alternates sides. | Body |
| Passive | Scorch | Its chains and plow scorch enemies. Its basic attacks hit scorched enemies harder. | Power |
| 1 | Coupling Chain | Fires a red-hot chain from the muzzle. The first enemy hit is coupled for a few seconds: it can't dash or leap, and it burns. The chain has a fixed length. If the enemy walks past it, the chain goes taut and tows them wherever the bison walks. While one enemy is coupled, a second chain fires for free. | Ode (Shackles) + Rig (coupler) + Power |
| 2 | War Whistle | A steam-whistle blast. Allies around it hit harder and attack faster for a few seconds; allies who keep landing hits on enemy machines stretch and grow the buff. The tell is the shriek and a white plume from both shoulder exhausts. | Rig (whistle) + Ode (Bolster Defenses) |
| 3 | Plow | The hump-powered head sweep, far bigger than the basic: a wide arc in front that throws enemies sideways and scorches them. A coupled enemy it hits is thrown to the far end of its chain. | Body + Power |
| 4 (ult) | Freight | Throws chains to every enemy around it (Ares's No Escape) and couples them all. It braces for a beat and can't be stopped, then walks off at a slow, heavy pace, towing the whole line behind it like rail cars: out of position, into its team, or away from their carry. Coupled enemies burn and can't dash, but can still attack. A stun or knock-up landed on the bison while it hauls snaps every chain. | Ode + Rig + Power + Body (its strength) |

**How it plays:** couple the carry, plow to fling them to the chain's far end toward your team, whistle as the team
collapses on them. Freight when the enemy is grouped, to drag them apart or into a choke.

**No charge anywhere.** Freight is a slow haul, not a rush. The rhino keeps the charge; the gorilla's Shield Drive is
the other charge in the roster.

**Overlap check:**
- **Closest: the lobster's claw grab.** Both fire a line at the first enemy hit. The claw reels its target all the way
  in; the chain is a leash that only tows when the bison walks. The look must differ too: a red-hot chain, not a claw
  on a cable.
- **The hippo's Lockjaw** walks with one enemy clamped in its jaws for about 1 s. Freight walks with several on chains
  as an ult: the same "walk while towing" idea at another scale. Preston should look at the two side by side.
- **The gorilla's passive** cuts damage taken for allies near it. War Whistle is offence only (harder, faster hits),
  so it doesn't copy it.
- *Missed at first (2026-11-12):* **the wolf's howl** (designed, not built) also gives nearby allies faster attacks. The wolf rework
  below keeps its call to movement and the hunt, and leaves the fight buff to the whistle.
- **Cut because the hippo owns them:** DESIGN.md's stored pressure (fill and spend, like the hippo's tanks), its
  furnace jet (a cone, like Vent) and its radial steam push (like Toxic Flood's push).
- **New to the roster:** "can't dash or leap" as a soft control, and a mass tow as an ult.

**Dropped from the 2026-11-11 test draft:**
- Full Steam: it rewarded running in straight lines, which is charge play.
- Lay Track: it fed Express. The rails are free for another machine.
- Whistle as a fear: the whistle now rallies.

**Left out of Ares:** Searing Flesh's flame cone, the item auras, and No Escape's pull to himself.

**Art cost:**
- The concept body (`docs/art/moba/bison_l/take-a/DESIGN.md`) has no chain hardware. The chain can fire from the
  muzzle (its `muzzle_purge` socket), so no body change is needed. A coupler hook on the chest would read
  better, but that is a change to Codex's body lane and needs Preston's pick.
- The chains can be an effect, not a mesh.
- Clips: the chain throw (head toss), the plow sweep, the whistle (head up, exhausts venting on `steam_l` and
  `steam_r`), and Freight's brace plus a heavy haul walk loop.

*Settled 2026-11-13: see "Bison: where it stands" at the end (Preston: "Yes, with your picks").*
**Direction:** Preston answered "Is the bison draft the right direction?" with "Yes, rhino next" (2026-11-12), read
as yes. The items below are still his.

**Open for Preston:**
- The role. The roster has 3 tanks; the bison would be a fourth frontliner, a catcher who rallies.
- Whether the locomotive rig stays. The chains and the haul lean on it.
- The ult: Freight (recommended), or Ares's pull-to-self if the lobster keeps shell guard and leaves the mass pull
  free. *The lobster draft at the end recommends gravity well, which takes the mass pull, so Freight.*
- All names and numbers.

### Bison kit draft 2: Ares + Vulcan (2026-11-12, Preston: "Lets do ode to vulcan too", then "build Eruption")
Preston: the bison gets a second ode, Vulcan, because "it has those plume things on top": the four stacks must be a big
part of the kit. Odes are "just inspiration to skill up the creativity", not the god's kit functions. This draft
changes only what the stacks touch; the rest of draft 1 above stands. Written by the bison-3d lane; source copy:
`D:/dev/_scratch/bison-3d/kit-ares-vulcan-draft-2026-11-12.md`.

**The stacks:** four hex stacks on the hump, 2 x 2, two each side of the spine. At 1.70 m they are the highest point of
the machine, so they show from every camera, including the chase camera, where the hump hides the head.

**From Vulcan (themes only):** the forge, molten slag, fire thrown up out of a furnace, a volcano's roar. His SMITE kit
(Backfire, Inferno Cannon, Magma Bomb, Earthshaker, passive Master Craftsman; names checked 2026-11-12) lends no
function: no turret, no backward dash.

| Slot | Name | What it does | Stacks | Layers |
|---|---|---|---|---|
| Basic | Horn hook | Unchanged. | none | Body |
| Passive | Scorch and Slag | Draft 1's Scorch, plus: fire the stacks throw lands as slag, a burning pool that scorches anyone standing in it for a few seconds. | slag comes out of the stacks | Power + Vulcan |
| 1 | Coupling Chain | Unchanged. | none | Ares + Rig |
| 2 | Eruption (replaces War Whistle) | Head up, a roar, and all four stacks erupt in turn, launching four molten bombs that land in a ring around it and leave slag. Allies inside the ring get War Whistle's buff (harder, faster hits; landing hits stretches it). | all four fire | Vulcan + Ares + Rig |
| 3 | Plow | Unchanged; the stacks flare with the sweep (looks only). | flare | Body + Power |
| 4 (ult) | Freight | Draft 1's Freight, plus: while it hauls, the stacks pour fire and drop slag behind it, so the coupled line is dragged through a burning track. | trail of slag | Ares + Vulcan + Rig + Body |

**Optional, looks only:** each stack belongs to one ability and goes dark while it cools down, so anyone can read the
bison's cooldowns off its back.

**How it plays:** couple the carry, plow them to the chain's far end, erupt as the team collapses (the buff ring, and
slag under the fight). Freight drags the coupled line through its own fire.

**Overlap check:**
- **Kept out: a heat gauge on the stacks.** Fill and spend is the hippo's.
- **Slag is a hurting field,** like the hippo's toxic puddle. It differs in coming from thrown bombs (several small
  pools at range, or a trail) and in feeding Scorch. Preston should look at the two side by side.
- **The fight buff stays inside Eruption,** so the note above about the wolf's howl still holds.
- **Still no charge.**

**Built (bison-3d lane, round 4):** `D:/dev/_scratch/bison-3d/game-export-r4/` (13 clips, not registered).
Bison_Eruption, 1.5 s: events gather 0.04, roar 0.32, erupt_fl 0.38, erupt_rr 0.48, erupt_fr 0.58, erupt_rl 0.68,
recover 1.05; one bomb per stack, from sockets `stack_fl`, `stack_rr`, `stack_fr`, `stack_rl` (profile
`sockets_proposal`). Plow gains a `flare` event, Freight_Haul gains `slag` events. Bison_Whistle stays in the GLB, unused.
From the chase camera the eruption reads through the stacks firing, so the bomb effects carry it.

*Settled 2026-11-13: see "Bison: where it stands" at the end (Preston: "Yes, with your picks").*
**Open for Preston:** all names and numbers; whether War Whistle's buff stays inside Eruption or becomes its own thing;
slag next to the hippo's puddle; the cooldown-stack option.

### Rhino rework draft (2026-11-12, Preston: "Yes, rhino next")
**Most of the rhino already crosses layers.** The audit table above was behind the build. Brace stores Seismic
charge in the pistons and lets it go as a blast. The stampede is now the Tremor charge, which sends tremor pulses as it
runs and carries enemies to the finale (`scripts/moba3d/rhino_kit.gd`, checked 2026-11-12). Only slot 1, horn toss,
comes from the animal alone, so the rework is one slot.

| Layer | The rhino's answer |
|---|---|
| Body | **The one trait:** the charge, with enemies carried on the horn (the Tremor charge). Basics stay animal: the horn hook, rip and gore chain. |
| Power | earth and tremor: seismic drive, shoulder transducers, resonant horn |
| Rig | proposal: a **seismic thumper**, the survey machines that press a plate to the ground and shake it to send waves through rock. It explains Brace (plant and store) and the new slot 1 (the thump). No body change. |
| Ode | Cabrakan: the tremble circle |

| Slot | Name | What it does | Layers | Change |
|---|---|---|---|---|
| Basic | Horn chain | hook, rip, gore (built) | Body | none |
| Passive | Front plating | hits on the front arc are blocked, and blocked hits fill Seismic charge (built) | Body (armour) + Power | none |
| 1 | **Heave** (replaces horn toss) | The shoulder transducers thump the ground. A ripple runs a short way ahead, and the first enemy it reaches is heaved up out of the ground and pitched over the rhino's back, landing behind it, stunned briefly. The horn rings and glows as the tell. No dash: the rhino stays planted. | Power + Rig | **new** |
| 2 | Ground pound | the tremble circle (built) | Ode (Cabrakan's Tremors) + Power | none |
| 3 | Brace and release | plants, blocks, stores charge, lets it go as a blast (built) | Rig + Power | none; only the rig reading is new |
| 4 | Tremor charge | the run, the pulses, the carry, the finale (built) | Body (the charge) + Power | none |

**Why Heave:** it keeps the horn toss's job (pull a straggler back to your team) and its direction (always behind), so
the four grab directions above still hold: the hippo carries and slams, the rhino's ult carries forward, the lobster
pulls to itself, and the rhino's slot 1 throws behind. Taking out the dash leaves the Tremor charge as the rhino's only
charge, which is the point of the trait.

**Alternative for slot 1, if Preston wants a set-up instead of a throw: Resonance.** The rhino rings its horn like a
tuning fork. Enemies near it are marked for a few seconds, and the next tremble or release that hits a marked enemy
stuns it. Less spectacle, more combo.

**Overlap check:**
- **The gorilla's Fault Line** (a slam that cracks the ground along the aim) is earth power on the gorilla, and earth
  and tremor are the rhino's. Heave is a single throw, not a crack line, so the slots don't copy each other, but the
  two machines would share a look. That is a second reason to move Fault Line onto the gorilla's shield tech. It is
  still Preston's call.
- **Cabrakan shows up twice.** The tremble circle is the ode. Brace and release also has the shape of his Refraction
  Shield (taking damage charges it, and at the top it stuns). The four-layer rule says one ode. It is built and was
  approved as the house example, so this is a flag, not a change.
- **The hippo's gauge:** unchanged. The overlaps section above still holds.

**Art and build cost:**
- One new clip for Heave: a planted shoulder thump with the horn ringing. The 3D body already has `horn_toss` and
  `toss` clips (`art/arena_models/authored_profiles.json`); they would be retired, not deleted, until Preston picks.
  Clips are the rhino lane's.
- Code: `horn_toss()` in `scripts/moba3d/rhino_kit.gd` would be swapped. That is game feel's lane.
- `moba-kits.md`'s rhino section: brought up to the build on 2026-11-12 (Preston: "Yes, update them").

**Open for Preston:**
- **Picked: Heave** for slot 1 (Preston, 2026-11-12: "Heave"). Resonance is dropped.
- The thumper rig: taken 2026-11-14.
- Fault Line on the gorilla, now with the rhino's earth power as a second reason to move it.
- Names and numbers.

### Cobra: the 3D lane's proposal, checked (2026-11-12)
The cobra 3D lane sent a kit proposal, with Preston's yes to send it:
`D:/dev/_scratch/cobra-3d/cobra-kit-ideas-2026-11-12.md`. Nothing is picked. Its slots, checked against the roster:

| Slot | Their proposal | Check |
|---|---|---|
| Passive | Wall Line: the concept's wall crossing, and the first basic after a wall hits harder | **Fits.** This is the one trait. |
| 1 | Rail Lunge: the front column fires forward and bites the first enemy | **Too animal, and taken.** A cobra's strike is the animal's own move, the "claw attack if I had claws" case. The wolf's slot 1 is already a lunge and bite. |
| 2 | Pin: a hood-plate sweep knocks the target back, and a wall stuns them | **Taken in part.** The gorilla's fling already stuns on a wall (`fling_wall_stun` in `scripts/moba3d/ape_kit.gd`). |
| 3 | Ground Ping: a tail slam reveals enemies, for longer on ones touching a wall | **Taken.** The squirrel's Tail Ping is a ring pulse that shows enemies through walls and fog. Same body part, same name, same job. |
| 4 | Breach (drives through a wall and leaves a gap allies can use) or Overrun (runs along the top of a wall, hitting enemies beside it) | **Both new to the roster.** Breach's team route sits near the fennec's gates, but a gap in a wall is not a portal. Overrun is the cleanest. |

**What's missing is a power and an ode.** The lane's "rig" is the body: the long segments, the upright column, the
tail. In the four layers, the rig is what the machine was built to do, and nothing is set for the cobra. So slots 1 to
3 all come from the animal again.

**A lead already on the cobra's body** (`docs/art/moba/cobra_m/take-a/REPORT.md`): hood phase projectors, a front
neck core, ventral adhesion and phase pads. **Phase** (passing through solid matter) would be a power that makes the
wall crossing tech rather than climbing, and makes Breach its natural ult. It differs from the fennec's portals (no
gate, no exit point) and the chameleon's cloak (it is seen the whole time). Proposal; it needs Preston's pick.
*Corrected 2026-11-12:* "phase" is already the word on the fennec's gate parts (ear phase conductors, tail-base phase
anchor) and the wolf's phase chambers (`power-body-recreations.md`), so the draft below calls the cobra's power
**pass-through** to keep the three apart.

**Ode candidates in SMITE 2:**
- **Medusa** (site data, full text): Lacerate (slithers forward through enemies, stops at the first god and roots it),
  Petrify (removes her mask: enemies looking at her are stunned, the rest are slowed, and she can't be crowd-controlled
  while casting), Acid Spray, Viper Shot, and the passive Sidewinder. Petrify's "only if they are looking at you"
  would be new to the roster, and the hood projectors could carry it, reading the facing the game already tracks (the
  rhino's front plating uses it). The lane left out hood hypnosis on purpose; this is the machine version of it, so it
  is Preston's call.
- **Jormungandr** (Venomous Haze, Consuming Bellow, Submerge, The World Serpent; passive Immovable) and **Serqet**
  (Deathbane, Cobra's Kiss, Ambush, Last Breath; passive Catalyst) are in the game files by name only, with no
  descriptions, and are not on the site feed, so they are likely unreleased in SMITE 2. Their text was not pulled.

**Suggested direction (not a draft):** keep Wall Line as the trait, take Overrun or Breach as the ult, and rebuild
slots 1 to 3 from a power and the ode instead of the strike, the hood and the tail. The lane's basic chain (bite, hood
swipe, head slam) is fine, since basics can stay animal.

**Clips:** hold the new clips for Rail Lunge, Pin, Ground Ping and Breach until Preston picks. Wall_Over at the real
wall height (2.6 m on the 5v5 wall module, 3 m in the 2026-11-04 arena) is safe to build, since the passive stays
either way.

**Open for Preston:**
- Breach or Overrun.
- A power for the cobra: phase (from its own concept parts), or another.
- The ode: Medusa (the only one with checked text), or pull Jormungandr's and Serqet's text first.
- Whether the full cobra draft comes now or after the kangaroo. *Answered:* "Also approve cobra" (below).

### Cobra kit draft (2026-11-12, Preston: "Also approve cobra")
**Confirmed:** Preston, 2026-11-12, asked whether this full draft is what he approved: "Yes, both". It is now in
`moba-kits.md`. Names and numbers are still proposals.

| Layer | The cobra's answer |
|---|---|
| Body | **The one trait:** crossing walls (Wall Line). Basics stay animal: the lane's bite, hood swipe and head slam chain. |
| Power | **pass-through:** it can make solid matter go soft, itself or a wall. The concept's hood projectors, neck core and belly pads carry it. |
| Rig | proposal: a **rescue snake robot**, built to get through rubble and open a way for the people behind it. |
| Ode | Medusa: Petrify's gaze, which only stuns those looking at her |

| Slot | Name | What it does | Layers |
|---|---|---|---|
| Basic | | bite, hood swipe, head slam (the lane's chain) | Body |
| Passive | Wall Line | Moving into a crossable wall slithers it over, on a cooldown, ending on walkable ground. Its first basic after coming out of anything solid (a wall crossing, Ghost Run or Seam) hits harder. | Body (the trait) + Power |
| 1 | Ghost Run | Goes soft for about a second and moves faster: it passes through enemy machines and their shots, but can't attack. No damage on the way through; coming out readies the Wall Line hit. Escape or engage. | Power |
| 2 | Hood Gaze | The hood flares and its projectors fire a cone forward. Enemies in it facing the cobra are stunned; the rest are slowed. It reads the facing the game already tracks. | Ode (Petrify) + Power (hood projectors) |
| 3 | Seam | Sinks into the wall it touches and travels inside it, unseen, for a few seconds, then surfaces anywhere along that wall. The tell is a ripple moving along the wall face. | Body (the trait) + Power |
| 4 (ult) | Breach | Softens a section of wall and drives through it. Enemies on the far side are damaged and knocked back, and for a few seconds allies can walk through the soft section. | Rig + Power |

**How it plays:** Seam along a jungle wall to a lane, surface behind the target, Hood Gaze as they turn to face it,
then the Wall Line hit. Ghost Run out through their team. Breach to open a gank route or steal an objective.

**Over, along and through:** the passive goes over walls, Seam goes along them, and Breach goes through. That covers
Preston's "moves along and over walls" with one slot each. Overrun (along the top) would repeat Seam, so Breach is the
ult.

**Overlap check:**
- **Ghost Run:** no machine passes through bodies or shots (`moba-kits.md` has no such move). It is close to
  Medusa's Lacerate, which slithers through enemies and damages them; Ghost Run does no damage, so the ode stays one.
- **Hood Gaze:** stuns are common, but a stun that depends on facing is new. The gorilla's chest beat is a taunt, not
  a stun.
- **Seam:** the chameleon's camouflage hides anywhere; Seam hides only inside a wall and shows a ripple. The squirrel's
  Tail Ping, which reveals through walls, counters it.
- **Breach:** the fennec's great gate is the team's portal; Breach is a short physical gap in one wall. The gorilla's
  dome makes walls; Breach removes them.
- **Dropped from the lane's proposal:** Rail Lunge (the wolf's lunge), Pin (the gorilla's wall stun), Ground Ping (the
  squirrel's Tail Ping), Overrun (repeats Seam).
- **Checked and avoided:** a delayed root patch (the shoebill's moon pool roots the first enemy that steps in) and an
  armour softening debuff (the pangolin's magnetism steals armour).

**Art and build cost:**
- Clips: Ghost Run (a fast slither; the softness can be an effect), Hood Gaze (hood flare), Seam (into and out of a
  wall face), Breach (a drive into a wall face), and Wall_Over at the real wall height (2.6 m or 3 m). Clips are the
  cobra lane's.
- **Hood rig limit (cobra 3D lane, 2026-11-12):** the auto-rig hood is lopsided. One hood bone moves no part of the mesh
  and another moves only 11 vertices, so a strong flare lifts one side only. Two ways out: (a) re-weight the hood
  plates, which changes the approved model's skin and is Preston's call; (b) keep the rig and sell Hood Gaze with the
  projector cone plus a neck rear-up. Kit side recommended (b). **Decided (a):** Preston first said "Yes, both", which
  included (b), then changed it: "Actually were changing hood weights". The hood plates get re-weighted, so Hood Gaze
  can use a full, even flare.
- Seam breaks the concept's "no parking inside terrain" rule on purpose, for a few seconds, along one wall only.
- Seam and Breach need the map's walls to be known sections. The 5v5 wall module is 6 m long
  (`foundry-5v5-2026-11-10/FOUNDATION.md`), which would make one module a natural Breach size, if the walls stay
  modular. The map is Codex's lane.

**Open for Preston:**
- Whether this reading of "approve cobra" is right. *Answered:* "Yes, both".
- Breach as the ult (Overrun drops, since Seam covers "along").
- The power's name (pass-through). The rescue-robot rig was taken 2026-11-14.
- Seam's few seconds inside a wall.
- Names and numbers.

### Kangaroo rework draft (2026-11-12, corrected the same day)
*Corrected:* the first version was drafted from `moba-kits.md`, which is behind the installed kit
(`scripts/moba3d/kangaroo_kit.gd`, slots 1 to 3 reworked on Preston's ideas of 2026-11-11). It dropped two things he
asked for by name, the leap to an enemy or an ally and the tail kick's wall stun, and it described the old guard. The
kangaroo 3D lane caught it, and the code confirms it. This version starts from the installed kit.

**His words:** "Yse then wolf and shoebill" (yes to drafting the kangaroo, then the wolf and the shoebill).

**The finding:** once the kinetic power shows, every installed slot already crosses two layers. The rework is a look,
not new moves, and nothing he asked for goes.

| Layer | The kangaroo's answer |
|---|---|
| Body | **The one trait:** boxing, fired through the capacitor gauntlets. Basics stay animal: jab, jab, hook. |
| Power | kinetic force: capacitor gauntlets that store hits, charged leg assemblies, a conducting and bracing tail |
| Rig | proposal: a **launch catapult**, like a carrier's, that stores energy and fires it |
| Ode | Ravana: the punch combos and the buff built by landing hits. Ne Zha stays the bout's feel reference. |

| Slot | Installed (`kangaroo_kit.gd`) | Kinetic layer added | Layers |
|---|---|---|---|
| Basic | jab, jab, hook | none | Body |
| Passive, rhythm | Landed hits stack; at full, the next basic is the tail kick. | Each stack lights a ring on the gauntlets; the kick fires as the kinetic blast (Preston: "approve send to effects"). | Body + Power |
| 1, hop and jab | Leaps to an enemy (lands in front, four fast punches) or to an ally (lands beside it, and both take less damage for 2.5 s). With nobody under the aim, a short hop and four punches. His references: Da Ji, Mr Fantastic, The Thing. | The leg assemblies charge and fire the leap; the four punches discharge the gauntlets. | Body + Power + Rig (the launch) |
| 2, tail kick | A double kick off the tail launches the enemy. If a wall or another machine stops it, it takes a burst and a stun, and so does the machine it hit (his Gilgamesh reference). | The kick fires as the kinetic blast through the bracing tail. | Body + Power |
| 3, guard | Up to 2.0 s, blocking and counting every hit. A second press after 0.5 s, or the time out, counters every enemy within 3 m, harder for each blocked hit (up to double), with a 0.6 s stun if anything was blocked. His idea: a multi-target punisher. | The gauntlets store each blocked hit (a ring per hit) and dump them in the counter. | Body + Power |
| 4, title bout | The ring, four beats with the weave and the lock, the finish. | The last kick gets the same blast (decided: "Yes, same blast"). | Body + Ode |

**Dropped from the first version:** Spring Launch as a new move (the installed leap gets the charged-leg look instead)
and Transfer (the tail kick keeps his wall and machine stun).

**Overlap check (built against built):**
- **Guard and the rhino's Brace and release** have the same shape: block and count hits, then pay them out around it
  with a stun. Both are built and both were his. What keeps them apart: the rhino's charge carries over (up to 5,
  draining), spends on control (a push and a slow) and stuns only at full; the kangaroo's resets every cast, spends on
  damage, and stuns if anything was blocked. Keep that line. A flag for Preston, not a change.
- **The tail kick and the gorilla's fling** both stun a thrown enemy that hits a wall; the kick also stuns on hitting
  another machine. Both built; a flag only. (The cobra's Pin was dropped for the same reason.)
- **The leap's landing** throws punches, not a landing stun, so the hippo's Piston Drop keeps that.

**Art and build cost:**
- **No new clips.** Leap already has hop, apex and land events. The rest is effects: the leg charge, the gauntlet
  rings and the blast (the last two already with the effects lane).
- Kit code: by standing practice the kangaroo 3D lane drafts `kangaroo_kit.gd` and game feel installs it. No
  mechanics change here, so code only changes if the effects need new cues.
- `moba-kits.md`'s kangaroo section: brought up to the build on 2026-11-12 (Preston: "Yes, update them").

**Decided:** look-only. Preston, 2026-11-12: "Kangaroo look-only is fine". No slot is replaced.
**Still open:** the guard and brace overlap (a flag). The catapult rig was taken 2026-11-14.

### Wolf rework draft (2026-11-12)
Every slot came from the animal: the scent, the lunge and bite, the hamstring bite, the pack howl, the chase.
**Built so far:** the lunge and the bite basic (`scripts/moba3d/wolf_kit.gd`, header of 2026-11-05; Preston: "Lunge
in the match" and "Yes, melee bite"). The header says scent, hamstring, howl and run down were not built yet.
*Corrected:* this first said the whole kit was built. Shade Step would replace the lunge he asked to see in the
match, so that swap is his call in so many words.

| Layer | The wolf's answer |
|---|---|
| Body | **The one trait:** the scent, tracking the wounded. Basics stay animal: bites. |
| Power | spectral: the red phase chambers and the paw and spine energy hardware on its concept (`wolf_m/take-c-power/`) |
| Rig | proposal: a **pursuit unit** built to catch runners, with a capture launcher in its spine |
| Ode | Thanatos: sensing the dying, the execute that grows with missing health, healing on a kill (unchanged) |

| Slot | Name | What it does | Layers | Change |
|---|---|---|---|---|
| Passive | Scent | Senses enemies below a health threshold through the fog and runs faster toward them (designed). The chambers glow brighter as the target weakens. | Body + Ode | none |
| 1 | **Shade Step** (replaces lunge) | Dissolves into red smoke and reappears beside a target enemy in short range; its next bite lands harder. On a wounded target, part of the cooldown comes back (kept from lunge). | Power | new |
| 2 | **Snare** (replaces hamstring) | The spine launcher fires a weighted cable snare that wraps the first enemy's legs: a strong slow for a few seconds, the hamstring's job. | Rig | new |
| 3 | **Shade Pack** (replaces howl) | The chambers release spectral wolves that run beside each nearby ally for a few seconds. Allies move faster, and the shades lead them toward the scented targets. Movement only, no attack speed. | Power + Body (the scent, shared) | new |
| 4 | Run Down | Marks one enemy and sprints at it; the next bite grows with missing health, and a kill heals (designed). The giant spectral head leads the way (the proposal above). | Ode + Power | none |

**How it plays:** scent the wounded, Shade Step onto them, Snare so they can't run, Run Down to finish. Shade Pack to
start a team chase.

**Overlap check:**
- **Shade Step:** the fennec's gates are placed portals, and the cobra's Ghost Run goes soft. A blink onto an enemy is
  new.
- **Snare** is a thrown wrap, not a line held between two things, so it stays clear of the lobster's cable, the
  bison's chain and the spider's thread.
- **Shade Pack and the bison's War Whistle** both help nearby allies. The old howl gave faster attacks, which the
  whistle also gives. Shade Pack keeps only movement and the hunt, and the whistle keeps the fight.
- **Thanatos twice:** the ode is in the passive and the ult. Built and kept; a flag, like the rhino's Cabrakan.

**Art and build cost:** no wolf 3D model or lane yet, so nothing to retire. Clips it would need: Shade Step (dissolve
and reappear, mostly effect), Snare (a spine launcher recoil), Shade Pack (head up, chambers venting), plus run, bite
and sprint. Code: `wolf_kit.gd`.

**Approved:** Preston, 2026-11-12: "wolf drafts approved". It is now in `moba-kits.md`.
**Still open:** names and numbers. The pursuit rig was taken 2026-11-14.

### Shoebill: checked, no rework (2026-11-12)
- **It already meets the rule.** The one animal trait is standing still: patience fills the moon disc. The wing hop is
  its body move. Moonbeam, moon pool and moonlance are moon power from the eye lenses, and wane crosses the hop with a
  moonlight flare.
- Preston picked this kit (Version B, 2026-11-05). The first slice built the passive, moonbeam and the basic
  (`scripts/moba3d/shoebill_kit.gd` header); the other slots' build state was not checked.
- **The flag runs the other way: it leans on its ode.** Its "Took" line in `moba-kits.md` names one Thoth piece per
  slot: a long line, a ground trap, a hop back, a very long line ult. So the four slots follow Thoth's four, in moon
  power, with no rig. (Thoth's SMITE 2 text is names only in the game files; this comes from the shoebill's own doc.)
- **Recommend leaving it**, since he picked it. If he wants it less Thoth, the slot to change is moonbeam, because
  moonlance is already the long line.
- The small add above (moonlance leaves a lit strip that reveals enemies on it) is parked: "as is" reads as no
  change.
- **Decided: no rework.** Preston, 2026-11-12: "shoebill stays as is".

### The last six, audited (2026-11-12)
**His words:** "shoebill stays as is next". Powers are from `power-body-recreations.md`, build state from each kit
script's header.

| Machine | Power | Slots that come only from the animal today | Built | Verdict |
|---|---|---|---|---|
| Lobster | gravity and attraction: violet emitter strips inside both pincers, field collars, a dorsal attraction core | molt, tail flip, shell guard (the claws are its one trait: snap, grab, pinch) | the basic only | **rework** (below). The power shows in no slot. |
| Falcon | storm/ion: crimson folded emitter wings, breast charge window, dorsal induction chamber | keen eye, stoop; take off and sky barrage are the animal plus Rama | the dart basic and keen eye | **rework, next.** The power shows in no slot either. The "altitude" pass above has an ion layer to start from. |
| Chameleon | optical cloaking and refraction (muted prisms, `take-d`, pending his pick) | swivel eyes, tongue lash. Camouflage and colour flash already cross the animal with the power. | no kit script found | **two slots,** after the falcon. |
| Squirrel | signal relay | none: the hop is its one trait (reworked 2026-11-05) | `squirrel_kit.gd` (slots not checked) | **fits** |
| Hummingbird | bonds | none: flutter is its one trait (reworked 2026-11-05) | `hummingbird_kit.gd` (slots not checked) | **fits** |
| Fennec | gates | the built slice still has big ears and sand kick, but he dropped the sand kick (2026-11-05) and his own portal draft waits on his "Take it" | `fennec_kit.gd` | **his redesign is in flight;** not re-audited |

### Lobster rework draft (2026-11-12)
*Corrected the same day:* the first version gave the claw grab Abduct's damage cut, which is a god's kit function.
Preston restated in the bison lane that odes are "just inspiration to skill up the creativity", not the god's kit
functions (the rule was already in the kit notes). The cut is gone, and Khepri is a theme only.

**Why it is first:** every designed slot except the claws is the animal (shell, tail flip, molt), and the gravity
power shows in none of them.

**Start point:** `moba-kits.md`'s lobster section and the "weigh down" pass above. Built: the claw snap basic only
(`scripts/moba3d/lobster_kit.gd`, "No abilities yet"), so nothing built changes. The body is the gravity
recreation (`lobster_l/take-i-heavy/`, pending his pick).

| Layer | The lobster's answer |
|---|---|
| Body | **The one trait:** the claws. Basics stay animal: the claw snap. The shell, tail flip and molt go as moves; the heavy shell stays as the look. |
| Power | gravity and attraction: violet emitter strips inside both pincers, field collars at the wrists, a dorsal attraction core |
| Rig | proposal: an **anchor-handling tug**, built to tow rigs and set their anchors. It hands the kit a tow line and an anchor. |
| Ode | Khepri as a theme only: the scarab rolling the sun, a heavy body that drags things after it. That is the feel of Weight. |

| Slot | Draft | Was | Layers |
|---|---|---|---|
| Basic, claw snap | Built, unchanged. | same | Body |
| Passive, Weight (*replaces molt*) | Its abilities put gravity rings on enemies, up to 3, fading a few seconds after the last. A ringed enemy is pulled toward the lobster: walking away from it is slower for each ring, walking toward it is not. At 3 rings, a dash or blink away from it goes half as far. The basic adds no rings. | molt: a shell shed at low health, for a shield and speed | Power + Ode (theme) |
| 1, claw grab | Fires the crusher claw on its tow line. The first enemy hit is clamped, ringed and reeled back to the lobster. | the same pull, without the ring | Body + Rig |
| 2, pinch | The other claw clamps the enemy in front: damage and a short root, plus a ring. The root lasts longer on an enemy that already has rings. | the same, without the ring | Body + Power |
| 3, Anchor (*replaces tail flip*) | Drives its tail fan into the ground as a gravity anchor for a few seconds. Inside a ring around it, the lobster and its allies can't be knocked, pulled, carried or thrown, and each enemy inside takes a ring every second. | tail flip: dart backward, knock back | Rig + Power |
| 4, gravity well (*his open choice; recommended*) | Slams the crusher claw into the ground. For a few seconds, enemies inside a wide circle are dragged toward its centre and take a ring every half second. | undertow (the same idea, renamed in the "weigh down" pass), or shell guard | Body + Power |

**If he keeps shell guard for slot 4:** the rules can stay, with the field look: a violet bubble from the attraction
core on the ally in place of a shell. That is a look-only fix, like the kangaroo's.

**How it plays:** plant Anchor in front of the team so their divers can't throw or carry anyone, claw grab the carry
out of position, pinch to hold them. Every ring makes running from the lobster harder. Gravity well pulls a group
into the team's burst.

**Overlap check:**
- **Grounding is dropped.** The "weigh down" pass grounded a full-weight target (no dash, leap, blink or gate). The
  bison draft's Coupling Chain now does that ("can't dash or leap", which that draft calls new to the roster).
  Weight shortens only dashes away from the lobster, so the two read apart. A flag if he wants grounding back on one
  of them.
- **Mass pulls:** gravity well drags enemies to a centre, the bison's Freight tows every coupled enemy behind it, and
  the hummingbird's Kindred ring charms enemies into walking to its centre. That is three ults that move a crowd. If
  he wants fewer, the shell guard choice frees one.
- **The bison's ult:** his draft left Ares's pull-to-self open only if the lobster kept shell guard. Gravity well
  takes the mass pull, so the bison takes Freight, which that draft already recommends.
- **Anchor is new:** nothing in `moba-kits.md` or this doc stops allies being moved (Freight's "can't be stopped" is
  the bison itself). It counters most of the roster's engages: the rhino's carry and Heave, the hippo's Lockjaw, the
  kangaroo's tail kick, the gorilla's fling, the bison's tow. A strong tool; the numbers need watching.
- **Lines between things:** the tow line is the lobster cable already on that list. Nothing new.
- **The escape goes:** tail flip was its only escape. With Anchor it plants instead of running, which suits an L
  support, but it has no way out.
- **Body:** `take-i-heavy` draws both claws huge, so the pinch's "small claw" is just the other claw.

**Art and build cost:**
- No lobster 3D lane exists yet, and machines are rigged 3D models now. Clips a lane would need: the claw shot and
  reel-in, the pinch, the tail-fan plant and lift (Anchor), and the claw slam (well).
- Effects: 1 to 3 gravity rings at the feet, the tow line, the anchor ring, the well and its rim.
- Kit code: only the basic exists, so nothing built is removed.

**Approved:** Preston, 2026-11-13: "Yes, falcon next", his answer to "Does the lobster draft work, with Anchor in place
of the tail flip?". It is now in `moba-kits.md`, with slot 4 read as gravity well, the recommendation.
**Still open:** names and numbers; shell guard in place of the well, if he wants it. The tug rig was taken 2026-11-14.

### Gorilla slot 2: four options (2026-11-12, updated after the pose stills)
**Asked by:** the gorilla 3D lane, which holds slot 2's clip until Preston picks. Everything else on the gorilla is in
the match (kit v36).

**Pose stills:** the lane rendered three cast poses at Preston's request, each from the match camera and the front
quarter: `C:/Users/pmcga/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/side-session-notes/local_b046f4d1-5f44-4d41-a546-0c0b69f8e6fc/gorilla-v27/gorilla-slot2-cast-poses.png`.
The sheet's letters name the source: **sheet A** the back reactor, **sheet B** the chest core, **sheet C** the
forearms. They are built from frames of existing clips, not final animation. (This doc's options are named, not
lettered, so the two sets of letters don't get mixed up. The poses here are described from the lane's note; this
lane did not open the sheet.)

*Corrected:* the first version said the reactor needed a back-to-target pose and fit nothing. The lane's pose A
hunkers down facing the target while the reactor fires up and arcs forward. The reactor is also the only source the
match camera can see, because it faces the camera.

**Today (built, `scripts/moba3d/gorilla_fault_line.gd`, marked a prototype):** it plays the heavy Slam clip. On the
clip's damage event, a crack runs 6 m along the aim at 9 m/s, 1.5 m wide. Each enemy takes 22 damage once, then a
slowing field holds for 1.4 s. No hard control. Preston kept its look in the gorilla effects session (2026-11-12,
per the lane).

**Why it is open:** cracking the ground is earth power, which is the rhino's. The rhino's Heave also sends a ripple
along the ground ahead from a thump. The gorilla's power is the shield tech.

| | Reactor Fault Line (**recommended**) | Forearm Fault Line | Shock Front | Hex Wall |
|---|---|---|---|---|
| Pose | sheet A: hunkers down, fists planted; the back reactor fires up and arcs forward | sheet C: both forearm shields planted side by side; the line runs out along the floor | sheet B: rears up, arms open, jaw open; the chest core fires straight ahead | not on the sheet (closest is C): arms out, palms forward; three panels fly out and plant |
| What it does | as today: the arc comes down along the aim, the crack opens under it, damages, and leaves a slow | as today, from the fists | a cone of hex light shoves enemies back, away from its allies | a short line of three hex panels across the aim. Enemies and shots stop at it; allies walk through (the dome's rules). |
| Shape | a line, 6 m | a line, 6 m | a cone, about 4 m and 60 degrees | a line across the aim, about 4 m wide, a few metres ahead |
| Timing (proposals) | 0.4 s wind-up, fires as the reactor flares, rooted until 0.2 s after | 0.4 s wind-up, fires on the impact, rooted until 0.2 s after | 0.35 s wind-up, fires as the core flares, rooted | 0.3 s wind-up, fires as the arms open, rooted for the cast only |
| Effect | today's crack kept, plus a lime arc from the reactor | today's crack kept, plus the cell flash | new | new, borrowing the dome's panels |
| The match camera sees the source | yes: the reactor faces it | the forearms, at the sides of the view | no: the core faces away, so the pose has to carry it | the panels, ahead |
| Looks like a move it has (the lane's read) | least | the ult's slam frame and the Drive Slam's ending | the chest-beat ult's reared silhouette | the ult's slam frame |
| Layers | Body + Power | Body + Power | Power | Power |
| Against it | one small new effect (the arc); the ground line stays close to the rhino's Heave | reads like two moves it already has | close to Geb's Shock Wave, a god's kit function (odes are inspiration only, Preston, 2026-11-12), and a push like the hippo's and the rhino's brace release | every slot becomes shield tech, the linear kind the four-layer rule warns about, and it is a small copy of the ult's dome |

**Why the reactor version:** it keeps the Fault Line he kept today and puts the source on the shield tech. It is the
only source the chase camera sees, and its pose looks least like the ult or the Drive Slam. *Changed from the first
version,* which recommended the forearm version before the stills showed that pose matches the ult's slam and the
Drive Slam's ending.

**Rooting today** (from the gorilla 3D lane, 2026-11-13, read in code): `ApeKit._begin` (`ape_kit.gd`) sets the player
busy, and `fault_line()` frees it only after the Slam clip's damage event at 0.417 s. So slot 2 roots the gorilla
for 0.417 s, fires on the hit, and lets it move during the backswing. The 0.4 s wind-ups above match that.

**Picked: Reactor Fault Line.** Preston, 2026-11-13, in the gorilla 3D lane: "I choose A", answering that lane's pose
sheet, where A is the back reactor. Confirmed here the same day: "Yes, the reactor".

**Built as kit v37** (the gorilla 3D lane, 2026-11-13): clip `Gorilla_FaultLine`, 1.0 s. It drops onto its fists and
bows to present the reactor (0 to 0.30 s), swells (0.30 to 0.40), fires at 0.40 s with the body kicked down and the
jaw snapping open, is rooted until 0.60 s, and is back at idle by 1.0 s. Feet and fists stay planted. The move is
unchanged in the kit: the same line, damage, slow field and crack, launched on the fire event. The reactor's lime arc
belongs to the effects lane and is not built yet.

**To watch in the match:** Shield Drive (slot 3) starts from a similar brace. Slot 2 keeps the fists flat, the head
tucked and the back raised; the drive holds the forearm shields up in front. Whether an enemy can tell the two
wind-ups apart is a playtest question.

### Falcon rework draft (2026-11-13, Preston: "Yes, falcon next")
**Why it is next:** its storm/ion power shows in no slot, and two slots follow Rama's SMITE kit. Its "Took" line
names them: rising into the air to shoot down, a dodge, a barrage from the sky that reaches far. Odes are inspiration
only (Preston, 2026-11-12).

**Start point:** `moba-kits.md`'s falcon section and the "altitude" pass above. Built: the feather dart basic and keen
eye (`scripts/moba3d/falcon_kit.gd`: 7 m range, 26 damage, up to 50% more near full range). Both stay; keen eye gets
a new look only. The body is the storm/ion recreation (`falcon_m/take-c-power/`, pending his pick).

| Layer | The falcon's answer |
|---|---|
| Body | **The one trait:** the stoop. Basics stay animal: the feather darts from the wings. |
| Power | storm/ion: crimson folded emitter wings, a breast charge window, a dorsal induction chamber |
| Rig | proposal: a **cloud-seeding plane**, built to fly survey runs over a region and fire seeding flares into the clouds. It hands the kit flares and a long run. |
| Ode | Rama as a theme only: the archer prince's long, patient draw. |

| Slot | Draft | Was | Layers |
|---|---|---|---|
| Basic, feather dart | Built, unchanged. | same | Body |
| Passive, keen eye (*look only*) | Built, unchanged: the farther the target, the harder the dart hits. New look: each dart gathers charge from the wing emitters as it flies and glows brighter the farther it goes. | keen sight | Body + Power |
| 1, Ion Lance (*replaces piercing dart*) | Hold to draw the breast window's charge, up to about 1 s, moving slowly, then loose an ion bolt that pierces every enemy on its line. The longer the draw, the longer the line and the harder the hit. | piercing dart: the next dart pierces a line | Power + Ode (theme) |
| 2, Seed Flare (*replaces take off*) | Fires a seeding flare at a spot in range. About 1 s later, lightning strikes there: damage in a small circle. A charged cloud then hangs over the spot for a few seconds and shows enemies under it. | take off: rise, volley down, land | Rig + Power |
| 3, stoop (the one trait) | Dives a short way toward the aim: its dodge. The dive charges the induction chamber, and the first enemy hit takes a talon strike that discharges it: damage and a slow. | the same dive and talon slow, without the charge | Body + Power |
| 4, Seeding Run (*replaces sky barrage*) | Picks a long line anywhere it can see. A giant projection of its emitter wings sweeps along it from end to end, striking enemies beneath with lightning. Struck enemies stay charged for a few seconds, and the falcon's darts hit them as if from full range (keen eye's top bonus). | sky barrage: circles over an area and rains darts | Rig + Power + Body (a giant projection of its wings, principle 4) |

**How it plays:** hold range and draw Ion Lance down a lane. Seed a flare on a bush or a choke to see and hit what is
there. Stoop out when divers reach it. Seeding Run across a fight far away, then shoot the charged enemies for keen
eye's full bonus.

**Overlap check:**
- **Reveals:** the squirrel's Tail Ping, the fennec's big ears, the chameleon's swivel eyes and the wolf's scent
  already show enemies. Seed Flare's cloud is small, on a delay and tied to a strike. A light flag.
- **Long-line ults:** the shoebill's moonlance is a very long line too. Moonlance is a beam from the shoebill; Seeding
  Run is a remote sweep that marks. A flag.
- **Darts that jump:** the squirrel's Hearsay jumps. Ion Lance pierces instead, so they stay apart.
- **A charged shot is new:** nothing in `moba-kits.md` holds to draw a shot.
- **No new hurting field:** the cloud only shows enemies and the run leaves nothing on the ground, so it adds nothing
  to the slag and the hippo's puddle.
- **Slows:** only the stoop's talon slow, which it already had.

**Art and build cost:**
- Nothing built is removed: the dart and keen eye stay, and keen eye's new look is an effect.
- Clips a 3D lane would need: the draw and loose, the flare shot, the stoop and talon strike, the run cast.
- Effects: dart glow by distance, the lance bolt, the flare, the strike and its cloud, the stoop's discharge, the
  giant wing projection.
- Camera: his steep ult camera (55 to 60 degrees, 2026-11-04) was for an ult that lifts the camera. Seeding Run keeps
  the falcon where it is, so whether the camera lifts for it is open.

**Approved:** Preston, 2026-11-13: "Yes, chameleon next", his answer to "Does the falcon draft work?". It is now in
`moba-kits.md`.
**Still open:** the run's camera; names and numbers. The cloud-seeding plane rig was taken 2026-11-14.

### Chameleon rework draft (2026-11-13, Preston: "Yes, chameleon next")
**Why:** two slots come only from the animal: swivel eyes (the passive) and tongue lash (slot 1). Camouflage and
colour flash already cross the animal's colour change with the optical power. Its "Took" line names Loki's
invisibility, but camouflage is the chameleon's own trait, so it stands on the animal and the power, not the ode.

**Start point:** `moba-kits.md`'s chameleon section and the "unseen" pass above. Built: nothing (no kit script was
found). The eye pulse basic is Preston's pick (2026-11-05). The body is the optical cloaking recreation, revised as
muted prisms (`chameleon_m/take-d-muted-prisms/`, pending his pick): dark smoked optics and subdued channels, with
bright light kept for brief casts and cloak transitions.

| Layer | The chameleon's answer |
|---|---|
| Body | **The one trait:** colour change, as camouflage and as the colour flash. Basics: the eye pulse from the eye turrets. |
| Power | optical cloaking and refraction: smoked optics, subdued channels and nodes |
| Rig | proposal: a **wildlife film unit**, built to watch animals without being seen. It hands the kit a long lens and a camera flash. |
| Ode | Loki as a theme only: the trickster's misdirection, a hit from where it isn't. |

| Slot | Draft | Was | Layers |
|---|---|---|---|
| Basic, eye pulse | His pick, unchanged: a small turquoise pulse from the eye turrets, 5.5 m, 24 damage. It breaks camouflage on the windup. | same | Body + Power |
| Passive, Long Lens (*replaces swivel eyes*) | The same job: it sees farther than other machines, and enemies it spots stay revealed to its team a little longer. The source moves to the rig's long lens; the tell is the smoked optics turning and zooming. | swivel eyes | Rig + Power |
| 1, Bent Ray (*replaces tongue lash*) | A thin ray from the eye turrets toward the aim. Where it passes a wall's corner, it bends around it, up to 60 degrees, toward the nearest enemy behind. On hit: light damage, the target is slowed, and the chameleon gets a matching burst of speed (the tongue lash's effects, kept). | tongue lash: a long, fast poke | Power + Ode (theme) |
| 2, camouflage | Unchanged: it fades out; standing still keeps it hidden; moving runs a timer down; attacking or a skill ends it. New look: the optical cloak, the channels dimming as it fades. | same | Body + Power |
| 3, colour flash | Unchanged: a cone that blinds (basic attacks miss, sight shrinks), longer out of camouflage. New source: the rig's camera flash through the optics, with the skin's colour burst. | same, from the skin only | Body + Rig + Power |
| 4, shared camouflage | Unchanged, with the cloak look on its allies. | same | Body + Power |

**The ult stays.** Shared camouflage already crosses two layers. The "unseen" pass's refraction field (a fixed area
where allies stay hidden even when moving) stays an option only.

**How it plays:** sits camouflaged and scouts with the long lens. Bent Ray a target round a corner to slow it and close
in. Colour flash blinds coming out of camouflage, and shared camouflage walks the team in.

**Overlap check:**
- **Curving shots:** the pangolin's slot 2 bounces off walls and curves to magnetised enemies (`moba-kits.md`,
  pangolin redo). Bent Ray bends once, round a corner, as light. Close in idea; a flag.
- **Pulls:** the old note said the lobster owns the pull. Bent Ray doesn't pull either.
- **Reveals:** Long Lens keeps the old passive's job, so nothing joins the reveal pile (the squirrel, the fennec, the
  wolf, the falcon's Seed Flare).
- **Slows:** the same slow the tongue had.

**Art and build cost:**
- No kit script exists, so nothing built changes.
- The tongue effect is no longer needed. New effects: the ray and its bend, the lens zoom, and a white flash at the
  optics for colour flash.
- Clips a 3D lane would need: the eye-turret cast (shared by the basic and Bent Ray), the flash cast, the slow walk.

**Approved:** Preston, 2026-11-13: "Yes, approve it". It is now in `moba-kits.md`.
**Still open:** names and numbers. The film unit rig was taken 2026-11-14.

### Bison: where it stands, and the picks left (2026-11-13)
**His words:** "bison drafts next also read bison 3d model and bison effects session too". Read: both drafts above, the
bison 3D lane's and the bison effects lane's recent work, and the effects lane's hand-over
(`side-session-notes/local_cffe19dd-40a3-4628-9c16-ada3cfd03ade/bison-fx-lane-handover-2026-11-13.md`).

**What is already moving (draft 2, Ares + Vulcan):**
- Preston: "build Eruption" (2026-11-12) and "Magma orange" (2026-11-13, the effects colour; blue was dropped).
- The 3D lane's round 4 has 13 clips, Eruption among them, and the effects lane has built Eruption's effect in its own
  test scene. The main match is untouched until he says to turn it on.
- The effects lane goes on to Coupling Chain, Plow, Freight and footfall dust, in that order. It sends each cue
  contract to the game feel lane, which builds `bison_kit.gd` to match.
- Preston on the bot roster: "After its kit". The bison stays off it until the kit exists and passes its checks.
- **Not in `moba-kits.md` yet:** the bison has no section or roster row there. That waits on the approval below.

**Overlaps, updated with today's picks:**
- **The falcon's sky barrage is retired** (falcon approved 2026-11-13; Seeding Run is a line sweep). The effects
  lane's collision note (the same 3.5 m radius and the same "white-hot") no longer applies.
- **The ult is Freight.** The lobster took gravity well, so Ares's pull-to-self stays out.
- **Three ults move a crowd:** gravity well, Freight and the hummingbird's Kindred ring. A flag only.
- **Coupling Chain's "can't dash or leap"** stays the bison's own: the lobster's Weight was redesigned around it.
- **Coupling Chain and the lobster's claw grab** both fire a line at the first enemy. The claw reels in; the chain is a
  leash that tows only when the bison walks. The red-hot chain mesh keeps the look apart.
- **Slag and the hippo's toxic puddle** are both hurting fields. Slag comes as small pools from thrown bombs, or as a
  trail, and lasts about 4.5 s (a placeholder). The puddle is a wide lake.

**The picks left, with a recommendation each:**

| Pick | Recommendation | Why |
|---|---|---|
| The kit | **Draft 2 (Ares + Vulcan)** as the bison's kit, into `moba-kits.md` | the lanes are already building it on his "build Eruption" |
| The role | **frontline catcher who rallies**, listed with the tanks (a fourth frontliner) | the chain catches, Eruption's ring buffs the team, Freight drags a group |
| The rig | **keep the steam locomotive** | the chains are couplers, Freight is the train, the stacks are smokestacks |
| War Whistle's buff | **keep it inside Eruption** | four slots stay four; the whistle clip stays in the file, unused |
| Slag next to the puddle | **keep slag short and small** | the difference is size and source; numbers settle it |
| Cooldown stacks (looks only) | **yes** | each stack goes dark while its ability cools down, readable from every camera; enemies can read it too, which is fair counterplay |
| Names and numbers | later | as for every kit |

**Approved:** Preston, 2026-11-13: "Yes, with your picks". Draft 2 with every recommendation in the table is now in
`moba-kits.md` (Frontline), with a roster row; the count is now 4 tanks. Still open: names and numbers.

### Fennec: the pending portal draft, checked (2026-11-14, Preston: "Yes, fennec next")
**Start point:** `moba-kits.md`'s fennec section. The portal kit was taken 2026-11-05 (two-faced shot, pocket gates,
far gates, great gate, with big ears as the passive). The draft under it still waits on his "Take it": gate echo
replaces big ears, and rift boom opens the ult. His words for the kit (2026-11-05): "I want fennec to be a utility
mage that opens portals for it and team" and "No sand or fox physiology abilities". The body is the gate-tech
recreation (`fennec_s/take-c-power/`: ear phase conductors, shoulder split-ring projectors, a tail-base phase anchor;
pending his pick).

| Layer | The fennec's answer |
|---|---|
| Body | **No animal trait**, by his own rule. The four-layer rule allows that (the animal gives at most one). The ears and the small frame are silhouette only. |
| Power | gate tech (phase): every slot |
| Rig | none yet (proposal below) |
| Ode | Janus as a theme: two faces (the two-faced shot), doors and passages (the gates) |

**Verdict:**
- **Too animal: no.** With big ears gone, nothing comes from the fox. It passes.
- **Linear: a light flag.** Every slot is gate power, and only slot 1 and the ult touch a second layer, through the
  ode. That is the kind of kit the rule warns about, but the portals are his own ask, so it is a flag, not a rework.
- **The ode and Janus's SMITE kit:** the SMITE 2 dump names his abilities Portal, Unstable Vortex, Threshold and
  Through Space and Time (names only, no text). The gates and the carry-the-team ult sit near Portal and Through Space
  and Time by name. The portals came from Preston a week before the inspiration-only rule (2026-11-12), so they stand.
  A note only.

**Rig (proposal, optional):** a **signal relay station**, built to carry signals across a desert network. The ear
phase conductors double as its dishes (a look, not an ability, so his no-fox rule holds). It hands two slots a second
layer:
- gate echo becomes a relay trace: an enemy hit by its bolts or the boom is traced, so it shows through fog and
  camouflage (Rig + Power);
- the great gate's link to the base tower is the relay's home line (Power + Rig + Ode).
The kit works without it.

**The draft's two picks, with a recommendation:**
- **Gate echo for big ears: yes.** Big ears was the last fox trait, and gate echo keeps a reveal job tied to its own
  hits.
- **Rift boom: on the ult, not slot 1.** The two-faced shot is the ode's best slot, it is built, and its bolt effect
  exists. Rift boom on the ult also fills the open control piece (the old ult's silence left with doors of war), so
  the silence need not come back.

**Overlap check:**
- **Reveals:** gate echo replaces big ears, so the pile stays at five (the squirrel's Tail Ping, the wolf's scent, the
  falcon's Seed Flare, the chameleon's Long Lens, the fennec). It is the only one that comes from a hit, and it shows
  camouflaged enemies, so it counters the chameleon. Fair counterplay; a flag.
- **Knockbacks:** already common (big ones on the kangaroo and the gorilla; the hippo's Vent and Toxic Flood, the
  bison's Plow, the pangolin's roll, the cobra's Breach). Rift boom's comes at the gate's mouth and reads as clearing
  the door. A light flag.
- **The lobster's Anchor:** enemies inside it can't be knocked, so rift boom does not move them. An interaction, not an
  overlap.
- **Gates and the catchers (a rule for later):** can a machine coupled by the bison's chain, or at 3 of the lobster's
  rings, step through a gate? Suggested: the coupled one can't (the chain holds it), and 3 rings halve a gate's reach
  as they halve a blink's.

**Built and art:**
- `scripts/moba3d/fennec_kit.gd` (2026-11-04 and 11-05) is the older kit: big ears, sand kick, blink gate, tunnel,
  sonic boom, the basic violet dart, and the two-faced shot on key 5. The draft retires big ears, and his 2026-11-05
  words already retired sand kick and the dig (tunnel). Blink gate's small gate is the start of the pocket gates.
  Far gates and the great gate are not built. The game feel lane rewrites the script on his yes.
- **`moba-kits.md` has no basic row for the fennec.** The built basic is a small violet dart (power, not fox), so it
  fits as it is. It goes in with the rewrite.
- The draft says rift boom reuses the sonic boom's body move "redrawn at 35° from the emitters". That was sprite work.
  Since 2026-11-09 the machines are 3D models, so it now means a 3D clip built from the sonic boom's pose.

**Approved:** Preston, 2026-11-14: "Take it", his answer to "Take the fennec's portal draft, with gate echo and
rift boom on the ult?". It is now in `moba-kits.md`, with the violet dart as its basic row. He took it without the
rig button, so the signal relay stays an option.
**Still open:** the rig (optional); enemy use of its gates (default no); the gate rule for chained or ringed
machines; names and numbers.

### Rigs: taken (2026-11-14, Preston: "Take all seven")
His answer to "Take the seven open rig proposals as written?". Each is now plain **Rig:** in `moba-kits.md`.

| Machine | Rig |
|---|---|
| Rhino | seismic thumper |
| Cobra | rescue snake robot |
| Kangaroo | launch catapult |
| Wolf | pursuit unit with a capture launcher |
| Lobster | anchor-handling tug |
| Falcon | cloud-seeding plane |
| Chameleon | wildlife film unit |

Taken earlier: the pangolin's magnetic salvage hauler (2026-11-12) and the bison's steam locomotive (2026-11-13). The
fennec has none; the signal relay stays an option.

### Cobra: crossable walls (2026-11-14, Preston: "Inner walls only")
His answer to "Which walls can the cobra cross?", asked because the map lane could not mark crossable walls without a
rule. Every inner 3 m wall can be crossed; base walls and the map's edge cannot. Read as covering Wall Line, Seam and
Breach alike. The map already sets those walls apart, so it needs nothing new. The 3v3 walls are laid in 2 m modules,
so Breach opens one module. Now in `moba-kits.md` (Cobra).
