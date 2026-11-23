# MOBA kits (living file, edit in place)

Started 2026-11-03. All 13 approved machines drafted 2026-11-03. Roster and art status: `docs/art/moba/ROSTER.md`.
The "ode to" rules: `CLAUDE.md`, "MOBA roster".

## The rule for kits (Preston, 2026-11-03)
The SMITE god is inspiration only. Take what makes sense for the animal and drop the rest; the machine does
not have to play like the god or share his role.
- Lobster / Khepri: the pull is needed, not the revive.
- Rhino / Cabrakan: keep the tremble, the stun and the heavy burst. Not the shield walls in his hands, not the
  long rhythmic one-wall-at-a-time tremble.
- Chameleon / Loki: it goes invisible, but it does not have to play like Loki or be an assassin.

**Added 2026-11-04.** Preston: "were making the kit and their abilities too much like a bare parts animal like
mecha beast would. For example it digs and has sand attacks. which are fine but in my mind with it being an ode to
janus I wanted it to have blinking teleport abilites or portals. Same for the others it seems like all their
attacks are more physical and dependent on their animal."

The rule update below is the hub's wording, written from his direction. He took the fennec kit built on it.
- **The animal gives the body, the silhouette and at most one trait.** That trait is usually the passive or one
  slot.
- **The rest of the kit comes from a power theme:** the god's domain, an element (heat, lightning, light), or a
  machine system (shields, portals, holograms).
- **Still true:** nothing is held in hand. Every power comes from the machine's own body: emitters, vents, cores.
- **The model already in the roster:** the gorilla's green hex shields are tech, not ape. The other machines
  should feel like that.
- The other machines' kits below predate this. Ideas for reworking them are proposals only, in
  `docs/plan/fennec-janus-kit-2026-11-04.md`.

## Shape of a kit
A passive plus four slots; slot 4 is the ultimate. This matches the four `KitAbility` slots in
`docs/plan/moba-skeleton-synthesis-2026-11-03.md`.
Names and numbers are Preston's. The labels below are plain descriptions, not names, and timing is given as
tiers (short, medium, long) until he sets the numbers. Nothing is held in hand: every attack comes from the
machine's own body.

## Role map
Five of the gods are guardians in SMITE, so roles were spread by the animal and its size: the large machines
hold the front, the small ones are quick.

| Machine | Size | Ode to | Role | Signature |
|---|---|---|---|---|
| Rhino | L | Cabrakan | engage tank | Seismic charge: tremble circle, Aftershock (grounds), Tremor charge with the carry |
| Gorilla | L | Geb | protector tank | green hex shields |
| Hippo | L | Bacchus | sustain tank | pressure tanks, toxic Vent, Lockjaw drag, Toxic Flood |
| Bison | L | Ares, Vulcan | catcher tank | Coupling Chain and Haul, Whistle Stop, Freight's train and pile-up |
| Lobster | L | Khepri | catcher support | gravity: Weight rings, claw grab, Anchor, gravity well |
| Kangaroo | M | Ravana | brawler | punch rhythm, the leap to friend or foe, wall-stun tail kick, title bout |
| Pangolin | M | Kuzenbo | diving fighter | salvage (armour theft), rail dive, iron ball |
| Pistol shrimp | L | Thor | solo bruiser | Ringing, Cavitation Shot stuns, Ram, Hammer Down pins, Thunderclap |
| Wolf | M | Thanatos | assassin | hunts the wounded: scent, Shade Step, Snare, run down |
| Cobra | M | Medusa | jungler | crosses walls: Wall Line over, Seam along, Breach through |
| Shoebill | M | Thoth | long-range mage | patience, moonbeam, moonlance |
| Falcon | M | Rama | ranged carry | storm/ion: Ion Lance, Seed Flare, stoop, Seeding Run |
| Chameleon | M | Loki | scout support | camouflage, Bent Ray round corners, camera flash |
| Squirrel | S | Ratatoskr | mobile ranged carry | signal darts, Tail Ping |
| Hummingbird | S | Cupid | healer support | nectar heals, bloom |
| Fennec | S | Janus | utility mage | portals for itself and the team: pocket gates, far gates, great gate with rift boom; gate echo |

Count (16): 4 tanks, 3 fighters, 1 assassin, 1 jungler, 2 mages, 2 ranged carries, 3 supports. The pistol shrimp's
kit is approved (2026-11-16); its model is not built yet.

---

## Frontline

### Rhino (`rhino_l`), ode to Cabrakan
**Role:** engage tank. Starts the fight, holds the line, hits hard on arrival.
**Took:** the tremble circle (Cabrakan's Tremors), a stun, heavy burst. **Left:** the hand-held shield walls.
**From the animal (the one trait):** the charge, with enemies carried on the horn. Basics stay animal: the horn chain.
**Power:** earth and tremor (seismic drive, shoulder transducers, resonant horn). Blocked hits store **Seismic
charge** in the pistons. **Rig:** a seismic thumper (taken 2026-11-14: "Take all seven").
*Brought up to the build on 2026-11-12 (Preston: "Yes, update them"), from `scripts/moba3d/rhino_kit.gd`. Numbers are
the build's proposals. The reasoning for Heave is in `kit-design-2026-11-11.md`, "Rhino rework draft".*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, horn chain | Hook, rip, gore: three hits, the gore heaviest, each with a short hitstop. The chain starts over 1.5 s after a basic ends. | a chain |
| Passive, front plating | Hits from inside a 100-degree arc in front spark off the plates and are blocked. Every blocked hit adds one **Seismic charge**, up to 5, at most one per attacker every 0.5 s. After 5 s with no gain, one drains every 2 s. The charge glows on the drum ring. | none |
| 1, Heave (*replaces horn toss; Preston, 2026-11-12: "Heave"*) | The shoulder transducers thump the ground. A ripple runs a short way ahead, and the first enemy it reaches is heaved up out of the ground and pitched over the rhino's back, landing behind it (toward its team), stunned briefly. The horn rings and glows as the tell. No dash: the rhino stays planted, so the Tremor charge is its only charge. *Not built yet:* the code still runs horn toss until the rhino 3D lane's clip lands; game feel then swaps it, with the effects lane's cues (heave_tell, heave_thump, heave_lift, heave_land). | medium |
| 2, ground pound | **The tremble slow.** Rears and slams, then stomps 4 more times in place: a 4 m circle that shakes and slows everyone in it while it lasts and 0.8 s after. One hit of damage, on the slam. Preston, 2026-11-05: "a bigger circle like cabrakan where its stomping on the ground trembling and slowing those in the circle". | short |
| 3, Aftershock (*replaces Brace and release; Preston, 2026-11-20: "Aftershock"*) | A whole-body forward drive (0.35 s: the body pitches down, the shoulder pistons thump, the drum ring flares, the horn dips). Then a seismic wave rolls forward in a cone along the aim: 8 m long, about 6 m wide at the end, at 16 m/s. Each enemy it hits takes 30 damage once, is slowed 30% for 1.5 s, and is **grounded** for 2 s: no dashes, leaps or rolls, though walking and basics still work. It spends Seismic charge: each charge adds 1 m, 6 damage and 0.2 s grounded. At full charge (5) it also stuns for 0.75 s. Walls stop the wave, and machines in the air dodge it. Spec: `docs/plan/rhino-brace-replacement-2026-11-20.md`. *Built in Godot 2026-11-20 (game feel lane); not in Unreal yet.* | medium-long (12 s) |
| 4, Tremor charge | A run of up to 16 m, speeding up from 9 to 12 m/s and steering toward the aim. Every 3 m it sends a tremor pulse (2.2 m across, light damage, a 1 s slow), and every 4 m adds a Seismic charge. Enemy machines the front touches ride along on the horn (Preston, 2026-11-11). A second press after 0.5 s ends the run early. The finale is a pound that stuns everyone in the ring; its size and its stun grow with the distance run and the charge, which it spends. The carried machines are flicked up and dropped into it. | long |

**How it plays:** Tremor charge in and carry their front line into the finale, ground pound to slow the group, Heave a
straggler back into the team, Aftershock the escape or the dive so nobody leaps out.
**Art it needs:** the 3D body (the rhino 3D lane) has the horn chain, ground_pound, ground_pound_finale, the brace
clips (enter, hold, walk, release, exit; kept in the GLB but unmapped since Aftershock, 2026-11-20), piston_charge, stampede_windup and the charge loop (v53, per the rhino 3D lane). New: Heave, a planted shoulder thump with the
horn ringing. The horn_toss and toss clips are retired, not deleted.

### Gorilla (`ape_l`), ode to Geb
**Role:** protector tank. Stands in front of its team and keeps them alive.
**Took:** shields for allies, knocking enemies back, the protector role, and the green hexagonal tech shields
he named. **Left:** the rolling and the rest of the kit.
**From the animal:** the chest-beat display, knuckle walking, huge arms, the silverback leaping in to defend its troop.

| Slot | What it does | Cooldown |
|---|---|---|
| Passive, silverback | Allies standing near the gorilla take a little less damage. | none |
| 1, hex shield | Throws a green hex shield onto an ally or itself: it absorbs damage and clears one slow or root. | short-medium |
| 2, chest beat | Beats its chest; enemies close around it are taunted (forced to attack the gorilla) for a moment. | medium |
| 3, bound | Leaps to an ally or a nearby spot; landing knocks enemies back. | medium |
| 4, hex dome | Raises a dome of green hex panels over an area for a few seconds. Enemies inside are trapped until it ends, and enemies outside cannot walk in; allies inside take less damage and can walk in and out. Enemy shots stop at the wall from either side and damage it; at zero it breaks early. Allies' shots stop at the wall too (no shots cross it either way), without damaging it. | long |

**How it plays:** bound to the ally under attack, hex shield them, chest beat to pull the enemies' attacks onto
the gorilla. Hex dome when the team gets dived or has to hold a spot.
**Art it needs:** hex shield (green hex effect), chest beat, bound (leap and land), hex dome (effect).

**Kit rework (Preston, 2026-11-09, in the gorilla 3D lane):**
- Basic attack is now a chain: swat, swat, slam. "Yes, add the slam", then "More damage". In `ape_kit.gd` (proposed numbers):
  swats 28, slam 42 (1.5x). Held, that is 28 + 28 + 42 = 98 every 3 s, 32.7 a second, level with the rhino's 33.
  The slam alone gets a 0.09 s hitstop, a bigger lunge and shove, and a 0.3 shake. The chain resets after 1.5 s without a hit.
- The ult becomes the chest beat: "definitely should be him beating his chest an some support of shield for health for allies...
  I want the chest beat to be a wide taunt but also shield allies too." Asked what happens to hex dome, he picked
  **fold the dome into the ult**. Enemy effect besides the taunt: **taunt only for now**.
- Hex shields "based of the cells shields": he picked **they look like his forearm hex cell plates** (ability 1, the ult's
  ally shields and the dome all use that look).
- **The ult, built 2026-11-09 on Preston's "Yes, build the ult"** (`chest_beat_ult()` on key 4; numbers are drafts for Preston): three beats, one job each.
  Beat 1 taunts every enemy within 5.5 m for 1.5 s (the old chest beat was 3.0 m). Beat 2 puts the ability 1 hex shield on every
  ally within 5.5 m, the gorilla included, for 3 s. Beat 3 slams both fists down and raises the hex dome at its feet (3.2 m, 4 s,
  every existing dome rule unchanged). Cooldown long. Slot 2 was left empty until he named a new ability.
- **The build is ahead of this table (checked 2026-11-12 in `scripts/moba3d/arena_gorilla_kit.gd`, Codex's kit):**
  slot 2 is Fault Line, a crack that runs along the aim. From kit v37 (2026-11-13) it is cast from the back reactor
  (Reactor Fault Line, clip `Gorilla_FaultLine`; Preston: "I choose A", per the gorilla 3D lane; details in
  `kit-design-2026-11-11.md`). Slot 3 is Shield Drive, a braced forearm-shield
  charge that ends in a slam. Per the gorilla 3D lane, Preston said in Codex: "Shield drive", then "make that shield
  drive and just add slams too make it one move".

**Hex shield look (Preston, 2026-11-04):** the machine that gets the shield is ringed by a green hexagon circle
shield. Later the same day: "also Remove the three shield things that rotate on gorilla shields" (said in the
animation lane session), so the three orbiting gem copies are gone and only the hex shell remains.

**Hex dome trap (Preston, 2026-11-04, said in the game feel lane):** "the ult will also trap enemies and allow
allies to leave." Built that day in `ape_kit.gd` and `training_dummy.gd`: enemies inside when the dome rises are
held at the wall until it ends; allies are never held. Then the two open questions, answered the same day: "No
enemies can get walk into dome either. Trapped enemies shots are trapped inside wall. Wall can be damaged of
course." So the wall stops enemies both ways, stops enemy shots both ways, and has health that enemy shots from
either side wear down; at zero the dome breaks early. The health and damage numbers are placeholders for Preston.
Allies' shots, settled the same day: first "Allies shots pass through the dome wall", then reversed: "nvm allies
shouldn't pass through thatd be too op" (Preston). So no shot crosses the wall either way. Allies' shots don't
damage it (the hub's default, his to change); allies themselves still walk in and out.

### Hippo (`hippo_l`), ode to Bacchus
**Source of truth: `docs/plan/hippo-kit-pressure-2026-11-11.md`.** That file is the hippo effects lane's, built from
Preston's calls on 2026-11-11, and this section mirrors it. It was rewritten on 2026-11-12, after the hub flagged
that the section was behind those calls. Names and numbers are still proposals.

**Role:** sustain tank. Preston, on the Bacchus combo it keeps: "a great initiator but all in'er".
**Power theme, pressure:** three tanks of glowing violet fluid with windows (one on each side, one under the
throat), pipes from a pack on its back, and legs that work as pistons. Every power comes out of them.
**From the animal (the one trait):** the jaws.
**The Bacchus ode, made its own.** Preston: "Hippo obviously should be its own like how kuzenbo seems like an ode to
Rasmus but the spike roll is kuzenbos ult". So the Bacchus ingredients stay but move to new slots and forms:
- the drunk meter becomes the tanks;
- the burp's delayed stun moves to the dive;
- Intoxicate's burst and lingering ground become the ult.

| Slot | Name | What it does | Clip |
|---|---|---|---|
| Passive | Pressure Tanks | Fills as it deals and takes damage, and the tank windows glow brighter. Full tanks overcharge the next skill, then drain. | none |
| 1 | Vent | A toxic purple spray cone from the jaws that leaves a puddle. Overcharged, the puddle lasts longer and slows. Preston: "Make it the purple liquid I want it to have a poisonous or toxic type effect. Or noxious." The effect is built in `scripts/moba3d/hippo_vent_fx.gd`. | Hippo_Yawn (cone 0.35 to 0.95 s, hit 0.45 s) |
| 2 | Piston Drop | Leaps to a spot and lands. About 0.5 s later the ground under the impact erupts and stuns: the Bacchus burp timing. | Hippo_Belly_Flop (push-off 0.22 s, hit 0.72 s) |
| 3 | Lockjaw | Clamps one enemy and walks about 1 s with them held (slowed). Then it slams them down where it stands, or tosses them a short way toward the aim. Preston: "Drag them into the lake". There is no fling away, because that would break the combo. | Hippo_Chomp, plus the clamp, carry and slam clips registered by the hippo 3D lane (per the hub, 2026-11-12) |
| 4 (ult) | Toxic Flood | Blows all three tanks. A toxic wave pushes enemies outward and leaves a wide poisoned lake, with heavy damage to anyone who stays. The hippo heals standing in its own lake. Afterwards the tanks are empty, and it is weak until they refill. | a Toxic Flood clip registered by the hippo 3D lane (per the hub, 2026-11-12) |

**Basic attack, bite:** melee (Preston, 2026-11-05: "Melee bite"). It's a short jaw snap on the nearest enemy in
front; with nothing in reach it snaps the air. The proposed numbers are his to set: 40 damage, 2.2 m reach edge to
edge, every 1.0 s. It's built in `scripts/moba3d/hippo_kit.gd`. The basic chain is unchanged (Hippo_Bite,
Hippo_Jaw_Swing, Hippo_Stomp), and its hits fill the tanks.

**Combo:** Piston Drop in, then Vent while they sit in the eruption window. Lockjaw the carry and drag them into the
puddle, then Toxic Flood. A missed dive leaves it drained.

**Dropped:**
- Coolant Dump (the wallow) as its own slot; its heal now lives in the ult.
- Lockjaw's fling away.

**Still open:**
- Names and numbers (Preston's).
- Whether Vent can be cast during the Piston Drop's air time (0.23 to 0.70 s), as Bacchus's burp can mid-flop. That
  question is for the game feel lane.

**Superseded on 2026-11-11:** the morning Pressure draft from the kit design pass. It had Head of Pressure with three
flask bands, Coolant Dump in slot 3, Lockjaw with a fling, and Vent's soak and pushback blast. It's kept in
`docs/plan/kit-design-2026-11-11.md` for the record.

**The 2026-11-03 kit, replaced:**
- passive territorial (a meter that empowers the next skill);
- 1 gaping yawn (a cone that weakens);
- 2 belly flop (leap and stun);
- 3 wallow (a mud patch that heals it and slows);
- 4 chomp (hold, then fling behind it).

It took the jaws, the mud and the territory from the real animal. Preston asked what would set that apart from
"just uploading real hippos".

### Bison (`bison_l`), odes to Ares and Vulcan
**Role:** catcher tank who plays back. It waits for someone to step up, chains them, hauls them into its team and
stuns them at the buffers. Its whistle brings the team in.
**From the animal (the one trait):** the hump-powered head sweep bison use to plow snow (Plow). Basics stay animal:
the horn hook.
**Power:** heat, flame and steam, in magma orange (Preston, 2026-11-13: "Magma orange"; blue was dropped).
**Rig:** a steam locomotive: coupling chains, a haul that builds steam, the whistle, the buffers, and the four hex
stacks on the hump as smokestacks.
**Odes:** Ares and Vulcan as themes only (Preston: odes are "just inspiration to skill up the creativity"). The
catch, drag and stun beat Preston described from Ares stays; none of Ares's SMITE functions do. No charge anywhere:
the rhino keeps the charge.
*Approved 2026-11-13 (draft 2), refined 2026-11-14 (Preston: "Whistle Stop", his pick in `kit-design-2026-11-11.md`,
"Bison refine draft"): an active Haul with a buffer stun, Whistle Stop in place of Eruption's bombs and buff, and a
Freight that catches a line. Names, numbers and cooldown tiers are proposals.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, horn hook | A short, heavy horn hook that alternates sides. | basic |
| Passive, Scorch and Steam | The chain burns coupled enemies, and its basics hit burning enemies harder. While it hauls, it builds steam: it walks faster each second, up to a cap, and the stacks chuff faster. Bonus move speed from items counts in full toward the haul. | none |
| 1, Coupling Chain, then Haul | Fires a red-hot chain from the muzzle. The first enemy hit is coupled for about 3 s and burns; a dash or leap only goes as far as the chain's slack. **Recast to Haul:** it turns toward the aim and hauls for up to about 1.5 s, dragging the coupled enemy behind it at its own speed. When the haul ends, the enemy runs into its rear buffers: a short stun. A stun or knock-up on the bison during the haul snaps the chain. | medium |
| 2, Whistle Stop | The whistle shrieks and all four stacks blast tall columns of steam with fire at their base, seen across the map. Allies in a wide circle run faster toward the bison for a few seconds. Enemies close around it are scalded: damage and burning. | medium |
| 3, Plow | The hump-powered head sweep, far bigger than the basic: a wide arc in front that throws enemies sideways and scorches them, with the stacks flaring. A coupled enemy it hits is thrown to the far end of its chain. | short |
| 4, Freight | Fires one long coupling chain in a line. It passes through enemies and couples every one it hits, nose to tail, into a train behind it. Then it hauls the train, building steam, over a short slag track. When it brakes (recast, or at the end), the cars run into each other: every coupled enemy is stunned briefly. A stun or knock-up on the bison snaps the train. | long |

**Cooldown stacks (looks only; picked):** each stack belongs to one ability and goes dark while it cools down, so
anyone can read the bison's cooldowns off its back. All four blast together for Whistle Stop.
**How it plays:** it plays back behind its front line. When someone steps up, chain them and Haul them into its team;
the buffer slam stuns them as the team arrives on Whistle Stop. Plow peels a diver off its carry, or throws a coupled
enemy to the chain's far end, toward its team. Freight catches a line of enemies in a choke or a lane, hauls the train
into its team, then brakes for the pile-up.
**Items (no item system yet):** a tank build plus movement speed. Its threat is the chain's reach and how fast it
hauls, and speed feeds both.
**Built so far:** the bison 3D lane's round 4 body and 13 clips, among them Bison_Chain_Throw, Bison_Freight_Haul,
Bison_Freight_Brace (the brake), Bison_Whistle (Whistle Stop), Bison_Plow and Bison_Stun, plus Bison_Haul (the
hauling trot, round 6). `bison_kit.gd` exists
(the game feel lane, 2026-11-14; rebuilt to this refine the same day, Preston: "Yes, rebuild it") and the match
installs it. The bison effects are on in the real match (a BisonFxInstaller node in `arena_play.tscn`): Coupling
Chain's chain from `muzzle_purge` with the heat pulse and hot collar, Plow, footfall dust and the cooldown stacks.
Eruption's vent fire becomes the fire at the base of the steam columns; its bombs retire. It joined the bots on
2026-11-16 (Preston: "Yes, bison bots"): one bison bot on blue, so the match is 4 v 4.
**Art it needs:** Whistle Stop's steam columns, the haul's chuff and the buffer slam, and Freight (the line chain, the
train, the pile-up, the slag track). The effects lane's order, waiting on Preston's start: Whistle Stop, the Haul,
then Freight.
**Placeholders built in `bison_kit.gd` (the game feel lane's, not Preston's numbers):**
- Coupling Chain and Haul: the haul lasts 1.5 s; the buffer slam stuns 0.8 s.
- Steam: full in 2 s, up to 1.4x move speed. A 1.5 s Haul tops out at 1.3x. Item move speed counts in full.
- Whistle Stop: allies within 9 m get 1.3x speed for 3 s, only while heading toward the bison. Enemies within 3 m take
  40 damage and burn for 10 a second for 3 s.
- Freight: a 12 m line, 1 m to each side. It hauls for 2 s (Preston, 2026-11-16: "Cut to 2 s"; 4 s dragged a train
  about 18 m, and 2 s drags it about 8.4 m) and the pile-up stuns 1 s. With no move input it hauls away
  from the train, and a Freight that catches nobody doesn't haul (the lane's choices).
- Freight's slag track: one continuous burning track (Preston, 2026-11-18: "Yes, continuous track").
  - Each 0.6 s drop is a capsule from the previous drop point, 60 cm radius plus the enemy's body radius, lasting
    4.5 s at 12 damage a second.
  - The burn is per frame, once a frame however many segments touch.
  - The hauled cars burn too: up to 24 each over the 2 s haul. The ult says it hauls the train over the slag track.
  - Godot changed to this on 2026-11-18 (game feel lane; bison probes 0 fail, match_check 68/0). Before that it
    dropped spaced 0.6 m circles every 0.6 s, as the Unreal port still does (`BHaulTime` also still 4 s there, from
    before the 2 s cut). I first wrote that Godot already worked this way; I'd read the edit mid-test.
  - The track is about 8.4 m long.
  - The drawing matches the hitbox edge. Advice and numbers: `bison-slag-trail-advice-2026-11-18.md`.
- The old rally code (allies hit harder) stays in the shared player and match scripts, unused.
**The haul's speed: move speed (Preston, 2026-11-14, to the bison 3D lane: "Yes, build it").** The Haul and Freight
run at the bison's move speed (3.5 m/s, a placeholder in `machine_test_player.gd`), so a 1.5 s haul drags someone about
5.3 m, or about 6 m with steam. The old `Bison_Freight_Haul` was a 0.518 m/s trudge and would have played 6.8x to 11.5x
too fast. The bison 3D lane built **Bison_Haul** (role `Haul`), a hauling trot authored at 3.407 m/s with the
chain-pull lean, head low and the hump driving. It plays at 1.03x at base speed, 1.44x at the 1.4x cap and 1.75x at
1.7x, and the stride holds across that range. One clip serves both the Haul and Freight (lane note
`bison-3d-r6-2026-11-14.md` in the shared notes).
**To watch:** team speed (Whistle Stop, the wolf's Shade Pack, the hummingbird's Surge line); three ults that move a
crowd (gravity well, Freight, Kindred ring); slag only on Freight's short track, beside the hippo's puddles.

### Lobster (`lobster_l`), ode to Khepri
**Role:** catcher support. Pulls targets out of position and keeps its own team from being moved.
**From the animal (the one trait):** the claws. Basics stay animal: the claw snap. The heavy shell is the look.
**Power:** gravity and attraction (violet emitter strips inside both pincers, field collars, a dorsal attraction core;
`lobster_l/take-i-heavy/`, pending his pick).
**Rig:** an anchor-handling tug, built to tow rigs and set their anchors (taken 2026-11-14: "Take all seven").
**Ode:** Khepri as a theme only: the scarab rolling the sun, a heavy body that drags things after it.
*Reworked under the four-layer rule. Preston, 2026-11-13: "Yes, falcon next", his yes to the draft with Anchor in
place of the tail flip. The reasoning and the overlap check are in `kit-design-2026-11-11.md`, "Lobster rework
draft". The molt, the tail flip and the shell guard are retired.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, claw snap | A short snap of the big claw, melee, 2 m edge to edge, 40 damage, every 1.1 s (Preston, "Melee claw snap", 2026-11-06; proposed numbers). Built in `scripts/moba3d/lobster_kit.gd`. Adds no rings. | 1.1 s |
| Passive, Weight | Its abilities put gravity rings on enemies, up to 3, fading a few seconds after the last. A ringed enemy is pulled toward the lobster: walking away from it is slower for each ring, walking toward it is not. At 3 rings, a dash or blink away from it goes half as far. | none |
| 1, claw grab | **The pull.** Fires the crusher claw on its tow line. The first enemy hit is clamped, ringed and reeled back to the lobster. The signature skill. | medium |
| 2, pinch | The other claw clamps the enemy in front: damage, a short root and a ring. The root lasts longer on an enemy that already has rings. | short |
| 3, Anchor | Drives its tail fan into the ground as a gravity anchor for a few seconds. Inside a ring around it, the lobster and its allies can't be knocked, pulled, carried or thrown, and each enemy inside takes a ring every second. The lobster has no escape. | medium |
| 4, gravity well | Slams the crusher claw into the ground. For a few seconds, enemies inside a wide circle are dragged toward its centre and take a ring every half second. | long |

**Slot 4** is read as gravity well, the draft's recommendation. The alternative was shell guard with a violet field
look; say so to switch.
**How it plays:** plant Anchor in front of the team so their divers can't throw or carry anyone, claw grab the carry
out of position, pinch to hold them. Every ring makes running from the lobster harder. Gravity well pulls a group
into the team's burst.
**Built so far:** the claw snap only.
**Art it needs:** a 3D lane: the claw shot and reel-in, the pinch, the tail-fan plant and lift (Anchor), the claw
slam (well). Effects: 1 to 3 gravity rings at the feet, the tow line, the anchor ring, the well and its rim.

## Fighters and assassin

### Kangaroo (`kangaroo_m`), ode to Ravana
**Role:** brawler. Wins fights up close, one on one.
**Took:** fast punch combos, a buff that builds as it lands hits. **Left:** the ten heads, the dash ultimate.
**From the animal (the one trait):** boxing with its front paws (the gloves in the art). The leaps and the tail kick
are fired by its kinetic power.
**Power:** kinetic force (capacitor gauntlets, charged leg assemblies, a conducting and bracing tail). **Rig:**
a launch catapult (taken 2026-11-14: "Take all seven").
*Brought up to the build on 2026-11-12 (Preston: "Yes, update them"), from `scripts/moba3d/kangaroo_kit.gd`. Slots 1
to 3 were reworked on his ideas of 2026-11-11. Numbers are the build's proposals. The kinetic look is in
`kit-design-2026-11-11.md`, "Kangaroo rework draft".*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, three beats | Jab_Left, Jab_Right_Quick, Hook_Right (medium, quick, heavy), approved 2026-11-11. The chain starts over 1.5 s after a basic ends. | the beat lengths |
| Passive, rhythm | Each landed hit adds a stack, lighting a ring on the gauntlets. Four fill it, and they drop after 4 s without a landed hit. At full, the next basic is the tail kick, fired as the kinetic blast (Preston: "approve send to effects"): damage and a 2.5 m knockback. | none |
| 1, hop and jab | Aimed at a machine within 10 m, it leaps to it on charged legs. An enemy: lands in front and throws four fast punches. An ally: lands beside it, no punches, and both take 20% less damage for 2.5 s. Nobody under the aim: a short 3 m hop and four punches. His references: Da Ji, Mr Fantastic, The Thing. | short |
| 2, tail kick | Leans back on its tail and double-kicks, fired as the kinetic blast. The nearest enemy is launched 6 m. If a wall or another machine stops it, it takes an extra 40 and a 1.2 s stun, and so does the machine it hit. Preston, 2026-11-11: "the tail kick should stun enemies when they hit god or wall like gilgamesh". | medium |
| 3, guard | Raises its gloves for up to 2 s: every hit is blocked and counted, each lighting a gauntlet ring. A second press after 0.5 s, or the time running out, throws the counter at every enemy within 3 m: 60 damage, 20% more per blocked hit up to double, and a 0.6 s stun if anything was blocked. His idea: a multi-target punisher. | medium |
| 4, title bout | Leaps to an enemy within 8 m and touches gloves; a 3 m ring goes up, and nobody outside can touch either of them. Four punches land on a beat (a press on the beat crits for 1.5x). After each of the first three it slips 60 degrees round the enemy, so the last lands from behind. The enemy is locked for the bout. A tail kick, with the same blast (Preston: "Yes, same blast"), launches it out through the ropes with slot 2's slam rule. Details below. | long |

**How it plays:** leap in and jab to build rhythm, or leap to an ally under attack and take cover together. Guard the
enemy's burst and counter everyone around. Tail kick someone into a wall or into their own team. Ring the one it
wants to beat.
**Art it needs:** hop and jab, tail kick, guard, ring (effect); the finishing kick reuses tail kick. For the weave
(built by the kangaroo 3D lane, 2026-11-12). **Registered:** Preston said "Yes, register it", per the kangaroo 3D
lane. The round 11 model (25 clips, Slip and Reel included) is the game's kangaroo, `art/arena_models/kangaroo.glb`,
checked 2026-11-12. *Corrected:* this first said they waited on his OK.
- Slip_Left and Slip_Right: 0.25 s each, in place, start and end on the boxing stance. Events "push" at 0.04 s
  and "land" at 0.21 s; game feel carries the body between them.
- Reel: 0.6 s, for a kangaroo target only; it starts and ends on the Stun clip's first frame (Stun, Reel on each
  punch, back to Stun).
- Ownership: the kangaroo's Reel clip is the kangaroo 3D lane's. Turning any target to face each punch, the lock,
  and what other machines play are game feel's. Today other machines play Hit_Heavy into Stun.
- Review film: `D:/dev/_scratch/kangaroo-3d/out/kangaroo_r11_slip_reel.mp4`.

#### Title bout: bob and weave toward Ne Zha (Preston, 2026-11-12)
**His words:** "its great don't remove what you've done but I want you to synthesize more towards ne-zha in the
sense that I want it to be bobbing and weaving around the target while it can't attack like nezha strikes."
Ne Zha is the feel reference, like Rammus for the pangolin's ball: structure and feel only, no names or art taken.

**Kept as built** (the kangaroo 3D lane's round 14, `scripts/moba3d/kangaroo_kit.gd`, action "Bout"): the ring
cast, the hop in, the glove tap, four timed beats with the crit window, the tail launch and slam, and every cue
name the effects already listen to.

**Added:**
- **The weave is real movement.** After each beat lands, the kangaroo slips about 60 to 90 degrees around the
  target on a small circle (about 1.6 m, inside the 3 m ring), ducking as it goes. The next punch comes from the
  new angle. Sides alternate, and the fourth beat comes from behind the target, so the four beats hit from four
  directions. The slip takes about 0.25 s, so it fits between beats at the existing pace. The target's hit
  reaction faces each punch, so it gets turned around in place.
- **The target can't attack** from the bout start to the bout end. It reels in place: no attacks, no abilities,
  no walking out. That is what Ne Zha's strikes do to their target.
- **Outsiders are blocked** (Preston, 2026-11-12, "Yes, block them", answering the game feel lane: area attacks
  don't hit the two machines in the ring). The installed bout marks the pair "untouchable" (`can_be_hit` and
  `MatchTeams.enemies_of` respect it) and also pushes every other unit out of the 3 m ring each frame, per the
  kangaroo 3D lane. *Corrected:* this spec first
  said the ring lets outsiders in, which contradicted his answer.
- **What that leaves as counterplay:** with the target locked and outsiders blocked, nothing can answer the bout
  while it runs. Its length and cooldown are the only limits, so keep it short (about 2.5 s of beats) and on a
  long cooldown. The game feel lane has put the question to Preston of whether "block them" still holds with the
  lock; until he answers, the block stays.
- **Hard control:** mechanically the lock is a stun, which the rhino and the hippo's Piston Drop own as short
  stuns. The kangaroo's is different in kind: only on its ultimate, only inside the ring, only as long as the
  bout. Listed here so the roster check knows.

**Reading Preston's second half:** "while it can't attack" is read as *the target* can't attack, which is what Ne
Zha's strikes do. If he meant the kangaroo's punches play out on their own, that already fits: the beats are
scripted, and the press only adds the crit.

**Cue proposal for the game feel lane (names unchanged, additions only):**
- A new cue `bout_slip` after each beat: `slip_from`, `slip_to` (world positions), `slip_time` (about 0.25),
  `slip_side` (-1 or 1).
- A field `target_locked` on `bout_start` (true) and `bout_end` (false).
- The effects lane's visual sway turns off once the real slip exists; its afterimages follow the real movement.

### Pangolin (`pangolin_m`), ode to Kuzenbo
**Superseded (Preston, 2026-11-12, "Approved"):** the fun pass replaces the table below where they differ: iron ball
moves to slot 2 (short cooldown, wall bounce, bowls minions, curves to magnetised enemies), rail dive is cut, scale
flare spikes the ball, new ultimate scrap comet. Spec: `docs/plan/pangolin-kit-fun-pass-2026-11-12.md`.
**Near-field snap (Preston, 2026-11-18: "Near-field snap"):**
- The ball's pull toward a magnetised enemy keeps 1.6 rad/s out to 10 m, grows inside 4 m (`mag_turn × (4 m /
  distance)²`, capped at 3×), and locks at about 2.3 m with a clang.
- The field never lifts, throws or pulls a machine.
- Spec: `docs/plan/pangolin-magnetism-showcase-2026-11-18.md`.
**Role:** diving fighter. Gets into the back line and survives there.
**Took:** the spiked shell that hurts whoever hits it. **Left:** the summoned kappa, the grab-and-slam, the water ultimate.
**From the animal:** armoured overlapping scales, curling into a ball, claws.
**Power:** magnetism (Codex's body: copper-bronze plates, spine rails, flank field couplers). **Rig:** a
magnetic salvage hauler, built to strip plating off wrecks and haul it along rails.
**Slots 1 and 2 redone (2026-11-12).** Preston: "Dig and claw are too much like animal". Claw rake and dig in came
from the animal only, the "linear" problem he named on 2026-11-12. The new slots come from the power and the rig.
Full reasoning: `docs/plan/kit-design-2026-11-11.md`, "Pangolin redo". **Approved by Preston, 2026-11-12: "Yes, approve both".**

| Slot | What it does | Cooldown |
|---|---|---|
| Basic attack | **Pry chain** (Preston, 2026-11-18: "A, Pry chain"). Left swipe, right swipe (23 each, 1.6 m), then the pry: a full-rear both-claws drop, 30 to every enemy in a 60 degree half angle at 1.9 m, which refreshes magnetise on magnetised enemies. 29 a second on one target. The reach stays 1.6/1.9 m though the claw tips measured 1.29 m (Preston, 2026-11-18: "Keep 1.6 ／ 1.9"). Spec: `docs/plan/pangolin-basic-attack-2026-11-18.md`. | none |
| Passive, sharp scales | Enemies who hit it in melee take a little damage back. (The ode: Kuzenbo's spiked shell.) | none |
| 1, salvage | Its field tears armour plates off enemies in a short cone in front: they lose armour and it gains that armour for a few seconds, with the plates visibly stuck to its shell. Each enemy hit is magnetised (about 4 s). | short |
| 2, rail dive | Rides its spine rails' field in a straight line. On a magnetised enemy it locks on from long range and streaks to them; without one it is a short dash to a spot. Arriving on a magnetised enemy spends the charge for extra damage. | medium |
| 3, scale flare | Flares its scales out: damage around it, and it blocks the next couple of hits. Each hit it blocks magnetises the attacker. | medium |
| 4, iron ball | Curls into a ball and rolls where it is steered, building speed; takes very little damage while rolling. It curves toward the nearest magnetised enemy. The first enemy it hits ends the roll and is knocked into the air, harder the faster it was going. | long |

**How it plays:** salvage the front line to bank their armour, rail dive past them onto a magnetised carry, scale
flare when they turn on it. It survives in the back line on stolen armour, not by hiding underground. Iron ball to
crash into one target or to escape (stop-on-first-hit ruling, 2026-11-06).
**Art it needs:** salvage (plates flying to its back), rail dive (streak along a rail line), scale flare (pose and
effect), curl and roll loop. Claw_Rake is now the basic attack. **Dig_In and Dig_Erupt are parked, not deleted:**
ask the pangolin 3D lane before dropping them.
**Feel direction (Preston, 2026-11-06):** one of its abilities should feel like Rammus's Powerball in League of
Legends. Structure and feel only; no names, art or numbers taken. The game feel lane knows that ability well. Rammus
details below are from general knowledge, not checked against the live game.
**Proposal: iron ball as a momentum roll (not canon, Claude, 2026-11-06):**
- It tucks and starts rolling on the first frame: no rooted pause, the tuck (about 0.25 s) plays while it moves.
  It starts at normal speed and builds to about twice that over 2 seconds. It turns toward the steering at a capped
  rate, tighter as it speeds up, and keeps rolling straight when no key is held.
- While rolling it takes very little damage and can't use its other moves.
- The first enemy machine it hits ends the roll: that enemy is knocked into the air, enemies right around it are
  knocked back a step, and the hit is bigger the faster it was going. Short hitstop and a strong shake on contact.
- Using it again stops the roll early; it uncurls by itself after about 6 seconds if it hits nothing.
- After the hit it pops out right beside the target and claw rake can fire at once: the follow-up is the payoff.
- Game feel lane's notes and the choices still open (slows, walls, minions, Space while rolling):
  `docs/plan/pangolin-iron-ball-notes-2026-11-06.md`.
- **Decided (Preston, 2026-11-06): "Stop on first hit".** The roll ends on the first enemy it hits; the table is
  updated. Still open: Rammus's is a short-cooldown move, while ours stays the long-cooldown ultimate for now.
- Already close: the sharp scales passive and scale flare echo his spiked shell and defensive curl.

### Wolf (`wolf_m`), ode to Thanatos
**Role:** assassin. Hunts down the wounded and finishes them.
**Took:** sensing low-health enemies, a finisher that grows with missing health, healing on a kill.
**Left:** the scythe, the flight, the death theme.
**From the animal (the one trait):** the scent, tracking the wounded. Basics stay animal: the bite.
**Power:** spectral (the red phase chambers and the paw and spine energy hardware on `wolf_m/take-c-power/`).
**Rig:** a pursuit unit built to catch runners, with a capture launcher in its spine (taken 2026-11-14: "Take all seven").
*Reworked 2026-11-12 under the four-layer rule (Preston: "wolf drafts approved"). The reasoning and overlap check are
in `kit-design-2026-11-11.md`, "Wolf rework draft".*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, bite | Bites the nearest enemy in reach in front of the aim (built; Preston: "Yes, melee bite"). | basic |
| Passive, scent | Senses enemies below a health threshold through the fog of war and runs faster toward them. The phase chambers glow brighter as the target weakens. | none |
| 1, Shade Step (*replaces lunge*) | Dissolves into red smoke and reappears beside a target enemy in short range; its next bite lands harder. On a wounded target, part of the cooldown comes back. *Was:* lunge, a leap and bite (built, Preston: "Lunge in the match"). | short |
| 2, Snare (*replaces hamstring*) | The spine launcher fires a weighted cable snare that wraps the first enemy's legs: a strong slow for a few seconds. | medium |
| 3, Shade Pack (*replaces howl*) | The chambers release spectral wolves that run beside each nearby ally for a few seconds. Allies move faster, and the shades lead them toward the scented targets. Movement only, no attack speed (the bison's War Whistle keeps the fight buff). | medium-long |
| 4, run down | Marks one enemy and sprints at them; its next bite deals damage that grows with the target's missing health. A kill heals the wolf. A giant spectral wolf head projects from the chambers and leads the way (proposal). | long |

**How it plays:** follow the scent to whoever is low, Shade Step onto them, Snare so they can't run, run down to
finish. Shade Pack to start a team chase.
**Built so far:** the bite and the old lunge (`scripts/moba3d/wolf_kit.gd`, header of 2026-11-05). Shade Step
replaces the lunge when the kit is next built.
**Art it needs:** Shade Step (dissolve and reappear, mostly effect), Snare (a spine launcher recoil), Shade Pack
(head up, chambers venting), run, bite and sprint, and the run down head projection (effect).

### Cobra (`cobra_m`), ode to Medusa
**Role:** jungler. Moves through the map's walls to gank and to open routes for its team.
**Took:** Petrify's gaze, which stuns only the enemies looking at it. **Left:** the vipers, the acid spit, Lacerate's
slither-through damage, the statues.
**From the animal:** crossing walls, the one trait (Preston's wall-slither idea), and the basic chain: bite, hood
swipe, head slam.
**Power:** pass-through, making solid matter go soft (the concept's hood projectors, neck core and belly pads).
**Rig:** a rescue snake robot, built to get through rubble and open a way for the people behind it (taken 2026-11-14: "Take all seven").
Confirmed by Preston, 2026-11-12: "Also approve cobra", then "Yes, both". The four-layer reasoning and the overlap
check are in `kit-design-2026-11-11.md`, "Cobra kit draft". Cooldown tiers are proposals.

| Slot | What it does | Cooldown |
|---|---|---|
| Passive, Wall Line | Moving into a crossable wall slithers it over, ending on walkable ground. Its first basic after coming out of anything solid (a wall crossing, Ghost Run or Seam) hits harder. | its own, short |
| 1, Ghost Run | Goes soft for about a second and moves faster: it passes through enemy machines and their shots, but can't attack. No damage on the way through. | medium |
| 2, Hood Gaze | The hood flares and its projectors fire a cone forward. Enemies in it facing the cobra are stunned; the rest are slowed. | medium |
| 3, Seam | Sinks into the wall it touches and travels inside it, unseen, for a few seconds, then surfaces anywhere along that wall. A ripple along the wall face gives it away. | medium-long |
| 4, Breach | Softens a section of wall and drives through it. Enemies on the far side are damaged and knocked back, and for a few seconds allies can walk through the gap. | long |

**How it plays:** Seam along a jungle wall to a lane, surface behind the target, Hood Gaze as they turn to face it,
then the Wall Line hit. Ghost Run out through their team. Breach to open a gank route or steal an objective.
**Art it needs:** Wall_Over at the real wall height (2.6 m or 3 m), Ghost Run (fast slither; the softness can be an
effect), Hood Gaze (a full hood flare: the hood is being re-weighted, Preston, 2026-11-12), Seam (into and out of a
wall face), Breach (a drive into a wall face).
**Map (3v3, map lane 2026-11-14):** walls are laid in 2 m modules, so Breach opens one module.
**Crossable walls (Preston, 2026-11-14: "Inner walls only"):** every inner 3 m wall; not base walls or the map's
edge. Read as covering all three crossings (Wall Line, Seam, Breach), so it can't get into a base through its wall.
The map already sets those walls apart (team-colour strips on base walls, the edge fence).
**Open:** names and numbers, the power's name, how long Seam may stay inside a wall.

### Pistol shrimp (`pistol_shrimp_l`), ode to Thor
**Role:** solo bruiser (Preston's pick: solo/top). Few hits, each one huge, and every one shows itself before it lands.
**From the animal (the one trait):** the snap. It cocks the giant claw, and the snap fires a cavitation bubble that
collapses with a white flash and a bang (Cavitation Shot). Basics stay animal: jabs from the small claw.
**Power:** cavitation pressure, in white: the pressure vessels and bulky supports on its sheet. It never keeps a
reservoir and never leaves a field, which keeps it apart from the hippo and the shark.
**Rig:** a pile driver, built to drive piles into a seabed with one huge strike after a slow lift: the ram, the lift
and drop, the braced frame.
**Ode:** Thor as a theme only: the flash before the thunder. None of Thor's SMITE 2 kit is used.
*Approved 2026-11-16 (Preston: "Yes, approve it", then "wait stun not silence"): the draft in
`kit-design-2026-11-11.md`, "Pistol shrimp kit draft", with stuns in place of the deafen (a silence). The rig came with
the draft. Names, numbers and cooldown tiers are proposals.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, pincer jabs | The small claw jabs twice, quick, then a short pause. Melee. | basic |
| Passive, Ringing | Its hits leave an enemy ringing for a few seconds (white sound lines around them). Cavitation Shot on a ringing enemy stuns it briefly. The stun uses up the ring (a proposal), so it can't chain. | none |
| 1, Cavitation Shot | Cocks the claw (a short tell: the claw's vessels glow), then snaps: a bubble flies a short way and bursts at the first enemy or at the end of its reach. Damage in a small circle, a white flash and a bang. No push. | short |
| 2, Ram | The pile driver's piston fires it forward a medium distance. It stops at the first enemy it meets and leaves them ringing; that enemy is not pushed. Its way in and its way out. | medium |
| 3, Hammer Down | Lifts the giant claw like the pile driver's hammer, about half a second, standing still and taking less damage, then drops it on the spot in front: heavy damage, and enemies hit are pinned (rooted) for a moment. Ringing enemies take more. | medium |
| 4, Thunderclap | Projects a giant claw over a spot in range. The flash comes first: the circle under it flashes white as the warning. About 0.6 s later the claw snaps and the bubble collapses with a bang: heavy damage in a wide circle, and everyone inside is stunned briefly, ringing enemies for longer. It can't be moved while it cocks (the rig's frame braces). No push, nothing left on the ground. | long |

**How it plays:** in lane, jab to ring the enemy, then Cavitation Shot to stun them and win the trade; Ram in for a
trade, or out of one. In a fight, Ram onto the carry, Hammer Down to pin them, then the shot. With the ult, flank and
drop Thunderclap on the back line, stunning them while the team goes in.
**Counterplay:** every big hit shows first: the claw's glow, the lift, the white flash. Step out of it and the shrimp
has spent its turn. It has one dash, so kiting beats it. It has no heal, on purpose.
**Built so far:** nothing. The four white sheets in `pistol_shrimp_l/take-a/` are the start; model review is pending.
An older display model from before the sheets is at `art/model_catalog/display/pistol_shrimp.glb` (2025-09-01).
**Art it needs:** clips for the jabs, the cock and snap, the ram launch and stop, the hammer lift and drop, the ult
cast and a stunned reaction. Effects for the bubble, the white flash, the bang (rings in the air, look only), the
ringing mark, the warning circle and the projected claw.
**To watch:**
- **A stun on a short cooldown.** A jab rings the enemy and the shot stuns it, so the stun repeats in lane. Using up
  the ring and a short duration keep it fair; the durations are open.
- **Stuns pile up.** The rhino, the hippo's Piston Drop, the bison (the buffer slam, the pile-up) and now the shrimp:
  four owners. Thunderclap is a delayed circle stun like Piston Drop, but it stays put, it is an ult, and its circle is
  wide with a white flash.
- **A lot of control on one bruiser:** a stun, a root and an ult stun. Keep each short.
- **The gorilla's hex shield** clears one slow or root, so it answers Hammer Down but not the stun.
- **Other overlaps:** no knockbacks (nothing pushes); roots are a third, after the lobster's pinch and the shoebill's
  moon pool; the lobster grabs and pulls, the shrimp never pulls, and no shrimp slot is named "snap" (the lobster's
  basic); the falcon's wings sweep a line and the shrimp's claw snaps a circle (two giant projection ults, a flag); the
  chameleon owns the blind, so the white flash is a warning light only.

## Mages

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

### Fennec (`fennec_s`), ode to Janus
**Role:** utility mage. It opens portals for itself and the team: gets them in, out and across the map, and pokes
from behind.
**From the animal:** nothing, by his rule (Preston, 2026-11-05: "No sand or fox physiology abilities"). The ears and
the small frame are silhouette only.
**Power:** gate tech (phase): ear phase conductors, shoulder split-ring projectors, a tail-base phase anchor
(`fennec_s/take-c-power/`, pending his pick).
**Rig:** none for now. The signal relay station in `kit-design-2026-11-11.md` stays an option.
**Ode:** Janus as a theme only: two faces (the two-faced shot), doors and passages (the gates).
*Preston, 2026-11-05: "I want fennec to be a utility mage that opens portals for it and team", and later: "No sand
kick, and dont reuse their animations. I like sonic boom its whole kit and animations were really done. But lets
transition it too a correlation with the portal energy abilites the whole kit. No sand or fox physiology abilities".
Approved 2026-11-14 (Preston: "Take it"): the portal kit taken 2026-11-05, with gate echo in place of big ears and rift
boom on the ult. The check is in `kit-design-2026-11-11.md`, "Fennec: the pending portal draft, checked". The
2026-11-04 kit (blink gate, twin gates, doors of war) is in `docs/plan/fennec-janus-kit-2026-11-04.md`.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, violet dart | A small violet dart toward the aim. Built in `scripts/moba3d/fennec_kit.gd` (6 m edge to edge, 30 a hit, every 0.9 s: placeholders). | 0.9 s |
| Passive, gate echo | An enemy hit by its bolts or its boom shows through fog and camouflage for a few seconds. | none |
| 1, two-faced shot | A bolt forward and one backward from a small gate; damage and a slow. | short |
| 2, pocket gates | Opens a gate at its feet and a second a short way off. For a few seconds it and allies step through either way; the fennec can recast to jump through at once. The quick in-fight portal: escape, chase, pull a diver's target out. | short-medium |
| 3, far gates | An entrance gate here and an exit anywhere it can see, or on an ally or a friendly tower. Allies step through for a few seconds. The rotation and rescue portal. | long |
| 4, great gate | After a short charge, a ring opens under its team and tears open with a boom (rift boom) that knocks enemies back off it. Then every ally inside goes with the fennec to a gate it opens anywhere it can see or at its base tower, arriving with a short shield and a burst of speed. | long |

**Enemies can't use its gates** (the default; say so to change it).
**How it plays:** poke with the dart and the two-faced shot, and gate echo keeps whoever it hits in sight. Pocket gates
pull a teammate out of a dive. Far gates rotate the team or rescue a lane. The great gate clears its ring with the
boom and carries the team into a fight or home.
**Built so far:** the violet dart, the two-faced shot (on key 5), and blink gate's small gate (the start of pocket
gates). The script still has big ears, sand kick, tunnel and sonic boom, which this kit retires; the game feel lane
rewrites it. Far gates and the great gate are not built.
**Art it needs:** since 2026-11-09 the machines are rigged 3D models, so these are 3D clips: a cast pose (all four
slots), the ult's charge loop and the rift boom blast (the sonic boom's charge and blast he liked, with the energy
from its emitters, not its ears). Not reused: sand kick, ear burst, dig, pop out. Effects: small gate, big gate ring,
bolt, blink flash, arrival shield, the boom, the gate echo mark.
**To watch:** gate echo shows camouflaged enemies, so it counters the chameleon. Knockbacks are common (rift boom joins
them). Whether a machine on the bison's chain or at 3 of the lobster's rings can use a gate is a rule for later
(suggested in `kit-design-2026-11-11.md`).

## Ranged carries

### Falcon (`falcon_m`), ode to Rama
**Role:** ranged carry. Steady damage from range.
**From the animal (the one trait):** the stoop. Basics stay animal: the feather darts from the wings.
**Power:** storm/ion (crimson folded emitter wings, a breast charge window, a dorsal induction chamber;
`falcon_m/take-c-power/`, pending his pick).
**Rig:** a cloud-seeding plane, built to fly survey runs and fire seeding flares into the clouds (taken 2026-11-14: "Take all seven").
**Ode:** Rama as a theme only: the archer prince's long, patient draw.
*Reworked under the four-layer rule. Preston, 2026-11-13: "Yes, chameleon next", his yes to the falcon draft. The
reasoning and the overlap check are in `kit-design-2026-11-11.md`, "Falcon rework draft". Piercing dart, take off and
sky barrage are retired.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, feather dart | A dart from a wing, left and right in turn, along the aim; the first enemy on the line within range is hit, and a wall stops it. Built in `scripts/moba3d/falcon_kit.gd` (7 m, 26 damage, every 0.9 s: placeholders). | 0.9 s |
| Passive, keen eye | Built: the farther the target, the harder the dart hits, up to 50% more near full range. New look: each dart gathers charge from the wing emitters as it flies and glows brighter the farther it goes. | none |
| 1, Ion Lance | Hold to draw the breast window's charge, up to about 1 s, moving slowly, then loose an ion bolt that pierces every enemy on its line. The longer the draw, the longer the line and the harder the hit. | short |
| 2, Seed Flare | Fires a seeding flare at a spot in range. About 1 s later, lightning strikes there: damage in a small circle. A charged cloud then hangs over the spot for a few seconds and shows enemies under it. | medium |
| 3, stoop | Dives a short way toward the aim: its dodge. The dive charges the induction chamber, and the first enemy hit takes a talon strike that discharges it: damage and a slow. | medium |
| 4, Seeding Run | Picks a long line anywhere it can see. A giant projection of its emitter wings sweeps along it from end to end, striking enemies beneath with lightning. Struck enemies stay charged for a few seconds, and the falcon's darts hit them as if from full range (keen eye's top bonus). | long |

**Camera:** his steep ult camera (Preston, 2026-11-04: "55 to 60, no new art") was set for sky barrage. Whether
Seeding Run lifts the camera is open, since the falcon stays where it is. Detail: `docs/art/moba/match/MATCH_NOTES.md`,
"Steep ult camera".
**How it plays:** hold range and draw Ion Lance down a lane. Seed a flare on a bush or a choke to see and hit what is
there. Stoop out when divers reach it. Seeding Run across a fight far away, then shoot the charged enemies for keen
eye's full bonus.
**Built so far:** the feather dart and keen eye.
**Art it needs:** clips for the draw and loose, the flare shot, the stoop and talon strike, and the run cast.
Effects: dart glow by distance, the lance bolt, the flare, the strike and its cloud, the stoop's discharge, the giant
wing projection.

### Squirrel (`squirrel_s`), ode to Ratatoskr
**Reworked 2026-11-05 under the power-theme rule.** Preston took the draft ("Take it"), reviewed by the game feel
lane first. Draft numbers, the reasons for each change and the alternatives: `docs/plan/squirrel-ratatoskr-kit-2026-11-05.md`.

**Role:** mobile ranged carry (not his assassin role).
**Took:** Ratatoskr as the messenger who runs the world tree. **Left:** the acorns, the assassin role, the
dash-through ultimate.
**Power theme, signal relay:** a courier machine. Its huge segmented tail is an antenna array, and every power
comes from it: darts from the tail tip, amber segment lights, a full tail flare for the ultimate.
**From the animal (the one trait):** the hop and the sudden change of direction.

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, signal dart | A fast amber dart from the tail tip, aimed at the mouse; stops at the first thing it hits. | none |
| Passive, Hearsay | Every 4th dart jumps to a second enemy close to the first, at reduced damage; machines first, then minions. Three tail lights show the count. | none |
| 1, Branch Skip | A quick hop the way it is moving (toward the mouse when standing still). The next dart hits harder, always jumps and restarts the count. | short |
| 2, Crosstalk | The tail fans out and fires a spread of darts in a cone; once an enemy has taken its share, the rest pass through to the next. | short-medium |
| 3, Tail Ping | A ring pulse shows enemies through walls and fog and marks them (the next dart on a marked enemy jumps), plus a burst of speed. The camouflage counter. | medium-long |
| 4, Broadcast | The tail flares: for a few seconds every shot is a burst of three darts and Branch Skip comes back almost at once. | long |

**How it plays:** skip and shoot, skip and shoot, every skip sending the word along to a second target. Crosstalk
on a wave or a group, Tail Ping before a corner or to start a chase. Broadcast to win a fight.
**Art it needs:** tail snap (basic attack), hop, tail fan (Crosstalk). Effects: dart, hit, tail count lights, jump
arc, primed-dart glow, cone fan, ping ring and marks, tail flare.
**Shared code it needs (the game feel lane's):** a damage scale on hits, Space routed to the kit's own basic
attack, the player's move direction, speed boosts and slows that stack. All four built 2026-11-05.

## Supports

### Chameleon (`chameleon_m`), ode to Loki
**Role:** scout and ambush support, not an assassin. Sees first, hides the team, disrupts.
**From the animal (the one trait):** colour change, as camouflage and as the colour flash. Basics: the eye pulse.
**Power:** optical cloaking and refraction (dark smoked optics, subdued channels and nodes; bright light only for
brief casts and cloak transitions; `chameleon_m/take-d-muted-prisms/`, pending his pick).
**Rig:** a wildlife film unit, built to watch animals without being seen: a long lens and a camera flash (taken 2026-11-14: "Take all seven").
**Ode:** Loki as a theme only: the trickster's misdirection, a hit from where it isn't.
*Reworked under the four-layer rule. Preston, 2026-11-13: "Yes, approve it", his yes to the chameleon draft. The
reasoning and the overlap check are in `kit-design-2026-11-11.md`, "Chameleon rework draft". Swivel eyes and tongue
lash are retired.*

| Slot | What it does | Cooldown |
|---|---|---|
| Basic, eye pulse | Picked by Preston 2026-11-05. The eye turrets fire a small turquoise pulse: 5.5 m range, 24 damage (proposal numbers to tune). Breaks camouflage on the windup. | 0.9 s |
| Passive, Long Lens | Sees farther than other machines; enemies it spots stay revealed to its team a little longer. The tell is the smoked optics turning and zooming. | none |
| 1, Bent Ray | A thin ray from the eye turrets toward the aim. Where it passes a wall's corner, it bends around it, up to 60 degrees, toward the nearest enemy behind. On hit: light damage, the target is slowed, and the chameleon gets a matching burst of speed. Not a pull (the lobster owns the pull). | short |
| 2, camouflage | **The invisibility.** Fades out over a moment, the optics' channels dimming. Standing still keeps it hidden as long as it likes; moving runs a timer down; attacking or using a skill ends it. No damage bonus out of it: it is for scouting, setting up ambushes and escaping. | medium |
| 3, colour flash | A camera flash through the optics and a burst of colour from the skin, in a cone. Enemies hit are blinded for a short time: basic attacks miss and sight range shrinks. Coming out of camouflage with it makes the blind last longer. | medium |
| 4, shared camouflage | Cloaks itself and nearby allies for a few seconds; they stay hidden while moving slower, and each machine's first action reveals it. Team ambush or team escape. | long |

**How it plays:** sits camouflaged in a lane and scouts with the long lens. Bent Ray a target round a corner to slow
it and close in. Colour flash blinds coming out of camouflage, and shared camouflage walks the team in.
**Built so far:** nothing (no kit script).
**Art it needs:** clips for the eye-turret cast (shared by the basic and Bent Ray), the flash cast and the slow walk.
Effects: the ray and its bend, the lens zoom, the white flash at the optics with the colour burst, and the camouflage
fade (shader or palette fade, no new frames) on itself and its allies.

### Hummingbird (`hummingbird_s`), ode to Cupid
**Taken 2026-11-05, bonds and hover** (Preston, in the hummingbird session: "Bonds + hover"). The draft, with its
sources, the light alternative and the hover call, is `docs/plan/hummingbird-cupid-kit-2026-11-05.md`. It replaces
the 2026-11-03 kit (nectar, hum, flutter, bloom), kept after it for the record.

**Role:** healer support. **Power theme:** bonds: link beams from the ruby throat plate (Cupid's binding, with no
bow, arrows or hearts). **The one animal trait:** flutter. **Body:** hovers low all the time and never walks.

| Slot | Proposed name | What it does | Starting numbers (placeholders: amounts on a 1000-health scale, the kit code uses the same shares of 600; cooldowns are MatchRules tiers) |
|---|---|---|---|
| Passive | Kindred link | The last ally it healed stays linked by a beam from its throat plate and slowly heals. A new heal moves the link. | ally heals 10/s; breaks past 9 m or behind a wall |
| 1 | Link needle | A needle of light from the beak. Ally hit: healed and linked. Enemy hit: damaged. | 10 m line; heal 100; damage 60; cooldown short (5 s) |
| 2 | Surge line | The link pulses: the linked ally runs faster, and enemies who cross the beam are slowed. With no link, the speed goes to itself. | 3 s; +30% speed; crossing slow 30% for 1 s; cooldown medium (9 s) |
| 3 | Flutter | Darts in any direction, even backward, without turning. | 4 m in 0.2 s; cooldown short-medium (7 s) |
| 4 | Kindred ring | A ring of beams at its feet. Every ally inside is linked at once and heals; the first time each enemy enters, it is charmed: it walks toward the centre and cannot act. | 3.5 m radius; 5 s; heal 30/s; charm 1.0 s; cooldown long (40 s) |

**How it plays:** needle the carry to link it, poke enemies with the needle between heals, surge the line to chase
or to wall off a diver, flutter out. Kindred ring wins a fight over a spot.
**Art it needs:** a 35-degree hover pose (the planned redraw, in a new pose), a hover bob (script) and a wing beat
(2 or 3 drawn wing frames or a blur effect), one cast pose (beak and throat plate glow), a flutter lean. Effects:
link needle, link beam, ring of beams, charm mark. No walk cycle.
**Still open (his call):** names and all numbers; the role (open choice 3 below).

**The 2026-11-03 kit, replaced:** passive nectar (hits store nectar for stronger heals), 1 nectar dart (heals an
ally or damages an enemy), 2 hum (speed aura), 3 flutter, 4 bloom (flower field that heals allies and charms
enemies on entry). It took everything from the animal, which the 2026-11-04 kit rule no longer allows.

---

## Roster checks
- **Hard control, one main owner each:** stun on the rhino (Heave, Tremor charge's finale, Aftershock at full
  charge), the hippo's Piston Drop, the bison (buffer slam, Freight's pile-up), the pistol shrimp (Cavitation Shot on a
  ringing enemy, Thunderclap), the kangaroo (tail kick into a wall, 1.2 s; the guard counter, 0.6 s; plus the title
  bout lock, ultimate only, inside its ring, 2026-11-12) and the cobra (Hood Gaze, on enemies facing it). So stun has
  **six owners, not four.** *Corrected 2026-11-23 (kit council, `kit-council-2026-11-23.md`): this line said four and
  missed the kangaroo's and the cobra's stuns.* Nothing in the roster shortens or removes a stun; the gorilla's hex
  shield clears a slow or root only. Knock-up on the pangolin;
  taunt on the gorilla; grounded (no dashes, leaps or rolls) on the rhino (Aftershock, 2026-11-20); the pull on the lobster; the hold (Lockjaw) on the hippo; roots on the lobster (pinch),
  the shoebill (moon pool) and the pistol shrimp (Hammer Down); blind on the chameleon; charm on the hummingbird; no silence since 2026-11-05 (the fennec's doors of
  war left with the portal kit). Big knockbacks: kangaroo, gorilla.
- **Camouflage counters:** squirrel Tail Ping (reveals through walls and fog), fennec gate echo (shows enemies its bolts or boom hit, from 2026-11-14), wolf scent
  (wounded only).
- **Healing:** hummingbird (main), hippo (in its coolant pool), wolf (on a kill). **Shields:** gorilla, lobster.
- **Overlaps to watch:** three leap-and-land skills (hippo Piston Drop, gorilla bound, the end of rhino stampede),
  two area ultimates from the sky are kept apart (falcon barrages an area, squirrel's ultimate is a self power-up).
  The two-diggers overlap is gone (2026-11-04): the fennec's tunnel became twin gates. Since the pangolin redo
  (2026-11-12) nobody digs. Rail dive is a dash, so it adds to the dashes, not the leaps.
- **Only one true assassin** (wolf); the pangolin is the second dive threat.

## Open choices for Preston
1. Ability names and all numbers.
2. Lobster ultimate: shell guard or undertow.
3. Role changes from the gods: squirrel as a ranged carry (Ratatoskr is an assassin), hummingbird as a healer
   (Cupid is a ranged hunter), lobster, chameleon, kangaroo and pangolin off their god's role.
