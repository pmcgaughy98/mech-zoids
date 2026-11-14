# Squirrel kit rework: ode to Ratatoskr (draft, 2026-11-05)

**Status, 2026-11-05:** Preston took this kit ("Take it"), after the game feel lane's review (folded in below).
The numbers are still starting values for a test, not balance.

Pasted into `docs/plan/moba-kits.md` (squirrel section, role map row, camouflage counter line) by the
Squirrel session on 2026-11-05, after Preston okayed the shell route ("Yes, go ahead").

## Why
The squirrel kit in `moba-kits.md` was written before the 2026-11-04 rule, and all five parts come from the animal:
acorns, hop, nut scatter, tail flick, nut rush. The rule now: the animal gives the body and at most one trait, the
rest comes from a power theme, and nothing is held in hand. "Throws acorns" also breaks that last point.

## What was used
**Read this session:** the squirrel section and the kit rule in `docs/plan/moba-kits.md`; the fennec rework
(`docs/plan/fennec-janus-kit-2026-11-04.md`) for format and to avoid overlap; the roster's camouflage counter list;
the approved still's `take-b/REPORT.txt` (huge segmented tail, steel front teeth, amber lenses, cobalt plates).

**From the game feel lane (2026-11-05):** the match's current numbers, read by that lane from `match_rules.gd`:
move 3.5 m/s, machine health 600, stand-in basic attack 30 damage at 6 m every 0.9 s, flat kit hit 60, vision
12 m, tower range 12 m, respawn 8 s, cooldown tiers short 5 s, short-medium 7 s, medium 9 s, medium-long 12 s,
long 40 s. Its MOBA comparisons are general knowledge.

**General knowledge, nothing read online:**
- **Ratatoskr in the Norse poems** (the Poetic Edda and the Prose Edda): a squirrel who runs up and down the world
  tree carrying words between the eagle at the top and the serpent gnawing the roots, keeping the two at war. The
  theme taken: a messenger.
- **Dash that powers up the next shot** (League of Legends, among others). The structure taken: a short dash, a
  short window, a stronger next attack.
- **Bouncing attacks** (Dota 2, among others: a thrown blade that jumps between nearby enemies). The structure
  taken: the jump only goes to enemies close to the first one, at reduced damage.
- **Reveal pulses** in MOBAs and shooters: a ring that shows hidden enemies for a few seconds.
- **Self-boost ultimates for ranged carries:** a few seconds of faster or heavier attacks.

No names, numbers or art from any of these.

## The power theme: signal relay
The squirrel is a courier machine. Its huge segmented tail is an **antenna array**, and every power comes from it:
shots leave from the tail tip, the segments light up amber as it counts toward Hearsay, and the whole tail flares
for the ultimate. Amber matches the eye lenses already in the approved stills.

**The one animal trait:** the hop (the sudden skip and change of direction).

## Proposed kit

| Slot | Draft name | What it does | Cooldown | Replaces |
|---|---|---|---|---|
| Basic attack | signal dart | A fast amber dart fired from the tail tip, aimed at the mouse. Stops at the first thing it hits. | none | thrown acorn |
| Passive | **Hearsay** | Every 4th dart carries on: it jumps to a second enemy close to the first, at reduced damage. Machines first, then minions. Three tail segments light up one per dart so the count shows. | none | hard nut |
| 1 | **Branch Skip** (the animal trait) | A quick hop in the direction it is moving (toward the mouse when standing still). For a moment after, the tail glows: the next dart hits harder and always jumps. | short | hop |
| 2 | **Crosstalk** | The tail fans out and fires a spread of darts in a cone. Once an enemy has taken its share, the rest pass through to the next one. | short-medium | nut scatter |
| 3 | **Tail Ping** | The tail sends out a ring pulse that shows enemies through walls and fog and marks them: the next dart on a marked enemy always jumps. The squirrel gets a burst of speed. The roster's camouflage counter. | medium-long | tail alarm |
| 4 | **Broadcast** | The whole tail flares. For a few seconds every shot is a burst of three darts, and Branch Skip comes back almost at once. | long | nut rush |

**Draft numbers** (damage in the match's current points, where a machine has 600 health):

| Part | Numbers |
|---|---|
| Signal dart | 30 damage, range 6.5 m, 1.1 darts per second, 24 m/s (as fast as the tower bolts) |
| Hearsay | every 4th dart; jumps up to 4 m from the first target; 18 damage (60%) |
| Branch Skip | 3 m in 0.25 s; the next dart within 2 s does 42 damage (+40%), always jumps, and resets the count; 5 s (short) |
| Crosstalk | 5 darts across 40 degrees, 7 m, 15 damage each; one enemy takes at most 3 (45); 7 s (short-medium) |
| Tail Ping | 13 m ring; shows and marks enemies for 3 s; +30% speed for 2 s; 12 s (medium-long) |
| Broadcast | 5 s; each shot is 3 darts in a narrow spread at 60% each (18); a burst counts once toward Hearsay; Branch Skip cooldown 1 s; 40 s (long) |

**How it plays:** skip and shoot, skip and shoot, every skip sending the word along to a second target. Crosstalk
on a wave or a group. Tail Ping before a bush or a corner, or to start a chase. Broadcast to win a fight: bursts
of darts, a hop every second, Hearsay jumping all the time.

## What the game feel lane changed, and why
- **Dart speed 18 to 24 m/s.** At 18 m/s a target strafing at 3.5 m/s moves 1.3 m before the dart lands, more than
  a machine's body. At 24 m/s it moves 0.95 m. Homing darts are the other fix.
- **Ultimate: Broadcast instead of Feud.** In a 3v3, Feud links the whole enemy team almost every time, so its
  value depends on the squirrel's team, not the squirrel. It is hard to read (who is linked?) and needs care so
  shared damage doesn't loop. Broadcast is clear, rewards kiting, stacks with Hearsay, and is cheap to build.
- **Tail Ping reach 8 to 13 m, through walls and fog, plus the mark.** Machines already see 12 m, and nothing has
  camouflage yet, so an 8 m reveal did almost nothing.
- **Cooldowns on the match's tiers** (5, 7, 12, 40 s) instead of 6, 9, 16 and 80. The long tier is 40 s because
  respawn is 8 s and matches are short.
- **Hop goes where it is moving.** Kit keys turn the machine to the mouse first, so as first written the hop would
  always go toward the enemy. An escape hop has to follow the movement keys.
- **Readability:** the Hearsay count shows on the tail, the jump draws an arc, the primed dart glows and has its
  own sound, Crosstalk's extra darts pass through instead of vanishing into one body.
- **Screen shake only on a point-blank Crosstalk and on Broadcast,** never on plain darts.

## Roster checks
- **Camouflage counter kept** (Tail Ping), next to the fennec's big ears and the wolf's scent. (Corrected
  2026-11-05: big ears are still in the fennec kit Preston took; gate echo is only in an untaken redraft.)
- **No pull** (the lobster's) and **no teleport** (the fennec's gates).
- The fennec also fires bolts. The squirrel's darts need their own look: short amber dashes, not round bolts.
- The falcon is the other ranged carry. Its kit predates the rule too; the two should not end up with the same
  ultimate.

## Alternatives (pick any instead)
- **Ultimate, Feud (the first draft):** ties up to three enemy machines together for 5 s; 30% of the damage any of
  them takes is dealt to the others too. The most Ratatoskr idea (the eagle and the serpent turned on each other),
  but the game feel lane judged it a support's or mage's ultimate, not a carry's. It could move to another machine.
- **Homing darts instead of fast ones:** easier to land, less skill; the mouse aim would matter less.
- **Shots from the teeth:** the two steel front teeth are a twin muzzle instead of the tail tip. Reads at close
  range, but at game size the teeth lose detail (the take's report says so at 40 px).
- **Keep acorns as the one animal trait:** seed charges fired from cheek pods. Then the hop becomes a tail-thruster
  skip, so only one trait stays animal.
- **Lightning instead of signal:** each hop builds charge, and darts discharge it. Simpler, but loses the
  messenger link to Ratatoskr.

## What changes for the art
- **Body animations:** basic attack (a tail snap forward), Branch Skip (the hop), Crosstalk (tail fans out). Tail
  Ping and Broadcast can play on the idle and attack poses, with most of the work in effects.
- **Effects:** signal dart, dart hit, the three Hearsay count lights on the tail, the jump arc, the primed-dart
  glow, Crosstalk fan, Tail Ping ring and marks, Broadcast tail flare. The free PixelLab effect tool can make them.
- The 35-degree stills (fleet redraw queue, last) come before any body animation.

## What it needs from shared code (the game feel lane builds these, on Preston's pick)
1. **Damage scale on hits:** today every kit hit deals a flat 60, and going around that skips the rhino plating and
   the gorilla shields.
2. **A real basic attack per kit:** Space is a 30-damage stand-in for every machine. The squirrel's darts and the
   Hearsay count need Space routed to the kit.
3. **Move direction** on the player, for the hop.
4. **Speed boosts and slows that stack:** today one value holds both, and the brace also sets it.

Tail Ping's reveal needs nothing shared: it works like the pits' vision. Seconds come from the tiers, so no
per-machine override is needed.

**Built by the game feel lane, 2026-11-05** (its check `tools/debug/kit_api_check.gd` 24/24, match_check 67/67,
as that lane reports; not re-run here):
1. `hit(by, scale := 1.0)` on `machine_test_player`, `match_minion` and `training_dummy`. Damage is
   `MatchRules.kit_hit_damage` (60) times scale, then plating and shields. Squirrel scales: dart 0.5, Hearsay 0.3,
   primed dart 0.7, Crosstalk 0.25, Broadcast dart 0.3. `training_dummy.last_hit_scale` records each hit for tests.
2. Kit basic attack: the kit defines `func basic_attack(target: Node3D) -> bool` and optionally `var basic_cooldown`
   (default `MatchRules.basic_cooldown`, 0.9 s; the squirrel's 1.1 per second is about 0.91 s). Space and left click
   call it with null, so the kit aims with `player.aim_dir()` or `aim_point()`; bots pass their target. Return
   false when nothing fired. Outside a match Space does nothing, so a test scene calls it itself.
3. `player.move_dir() -> Vector3`, zero when standing. Branch Skip: use it, or `player.facing` when its length is
   under 0.05 (facing already points at the mouse after a kit key).
4. `player.boost(mult, seconds, key)`. Tail Ping: `player.boost(1.3, 2.0, &"tail_ping")`. Same key refreshes,
   different keys multiply with brace and slows.
5. Bots walk to the kit's own reach: set `var basic_range := 6.5` in the kit (edge to edge, as
   `MatchTeams.edge_distance`). `director.basic_range_of(m)` and `basic_cooldown_of(m)` are what bots and the HUD read.
6. Still to do: the game feel lane adds the squirrel to `arena_play`'s Tab list once a kit script exists.

## First slice, once Preston picks
**Hearsay in a test scene. Free.** A standalone Godot scene in the main folder, no shared match code: a squirrel
stand-in fires at a dummy target with two more dummies nearby, one inside 4 m and one outside; the dummies record
the damage they take.
Headless check (`tools/debug/squirrel_hearsay_check.gd`), which measures the thing itself:
- of 8 darts, exactly darts 4 and 8 jump;
- each jump lands on the dummy inside 4 m, never the one outside, for 18 damage;
- with a machine and a minion both in range, the jump takes the machine;
- with nothing in range, the 4th dart does not jump and nothing errors;
- a dart right after Branch Skip jumps even when it is not a 4th dart, and the count starts again after it.
Putting it in the match waits on shared asks 1 and 2.

## Section for moba-kits.md (pasted 2026-11-05)
Replaced the squirrel section from `**Role:**` down to the line before `## Supports`. The heading line
(`### Squirrel (`squirrel_s`), ode to Ratatoskr`) stays.

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
attack, the player's move direction, speed boosts and slows that stack.
