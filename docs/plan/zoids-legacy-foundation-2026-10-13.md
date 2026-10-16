# The Zoids Legacy foundation (Claude, 2026-10-13)

Preston: "I want Zoids Legacy to be core but that's an old GBA game, so we're going to use that already built
foundation, then refine it into modern day and use modern innovations to upgrade it once we start refining what you
wire." This is the wiring. It copies nothing: no code, text, names, numbers or art. The decompilation was read for how
the game is put together (its modes, its player state, its event commands, its battle), and every system here is
written fresh in GDScript with our own draft content.

## Synthesis: what each source gave
- **ZoidsLegacyDecomp** (`D:\Program Files (x86)\Game assets\zoids-source\ZoidsLegacyDecomp`, jmacato, MIT; read
  2026-10-13): `src/game/run_game_state_machine.c` (the 19 modes and how they hand over), `src/game/modes/` (one
  screen each: shops, lab, database, challenge menu, town map, form change), `src/game/player_state.h` (everything a
  save holds: stored machines and pilots, a six-slot team, recovery items, equipment, cores, money, catalogs,
  unlocked data and commands, the selected deck of ten; pilot levels to 99 with growth classes; support crew; the
  pulse emotion growth and its effect schedule), `src/events/run_event_scripts.c` and its 117 commands (a script
  runner: text, choices, flags, give and unlock, start battles, open shops, camera and screen effects).
- **Earlier reads** (`docs/reference/zoids-legacy-structure.md`, `battle-structure.md`): the battle round, deck rules,
  act-then-show results, formation, energy rules. Our battle already followed these.
- **The other stored repo**, `zoids-source/Zoids`: a Zig boids flocking demo; unrelated, not used.
- **Our game** (2,300 lines before this): title, opening, base and field scenes, battle with its logic and deck,
  pause menu, dialogue box, run state and save. Everything new hooks into it; nothing old was removed.

## What is wired now
| Zoids Legacy system | Ours | Status |
|---|---|---|
| Game state machine, 19 modes | `scripts/game/modes.gd`, `Run.go_mode()` | every mode has a scene; shops, lab, team, database, arena work; town map, battle scene, form change, options, credits are wired placeholders |
| Player state | `scripts/run.gd` (money, pilots, roster, six team slots, items, parts, cores, catalog, unlocked data) | saved; save version 2, version-1 saves still load |
| Pilots: levels to 99, growth classes, support crew | `scripts/data/pilots.gd`, `scripts/game/progression.gd` | experience from battles, level-ups add growth percents that change the machine in battle |
| Pulse (pilot and machine bond) | `scripts/data/pulse.gd`, `progression.give_pulse()` | grows with battles fought together; thresholds unlock effects |
| Equipment in slots, load capacity | `scripts/data/items.gd` (parts, slots, weights), `scripts/game/roster.gd` | fit and unfit in the lab; weight checked; parts change defense, speed, accuracy, energy, power |
| Item and equipment shops | `scripts/game/economy.gd`, the menu scene | buy, sell for half, quantity and money caps |
| Lab: build a machine from data and a core | `roster.build_machine()` | cores come from battles, story or the arena |
| Team of six, pilots into machines | `roster.assign()`, team setup mode | the battle fields the team in slot order |
| Database (catalog) | menu scene | machines fought, pilots met, parts bought |
| Challenge menu and battle rules | `scripts/data/battle_rules.gd`, arena mode | size, flyer and command bans, team caps; purses and cores |
| Event scripts | `scripts/events/event_runner.gd`, `scripts/data/events.gd` | 21 commands; text and choices on any UI; a draft lab welcome and an arena bout |
| Battle results feeding everything | `battle.gd` `_finish` -> `Run.apply_battle_result()` | experience, pulse, credits, cores, catalog |
| Battle units from the team | `roster.make_unit()`, `battle_logic.setup()` | pilots, parts and pulse change the fight |
| Reaching the modes | pause menu, Facilities page | towns will open them through events later |
| Items in battle | battle menu Items entry, `battle_logic.use_item()` | using one takes the turn; green +N pop (added later the same day) |
| Field triggers: walk into an area or interact | `scripts/data/field_triggers.gd`, `scripts/field/field_triggers.gd`, `scripts/ui/event_box.gd` | talk and touch triggers with flag conditions; the hangar's lab terminal plays the lab welcome and opens the lab (`tools/debug/trigger_capture.gd`) |
| Formation: front and back rows | `battle_logic.gd` `front_line`, `can_use`, `valid_targets`, `_target_for`; `battle.gd` `_stage`, formation strip, target menu | first three a side in front, the rest behind; melee only from and into the front line; guns, beams and missiles reach any row; an empty front row pulls the back forward; the AI weighs every weapon against every target in reach; the stage shows the acting pair, the strip at the top lists every machine by row with health; capture: `HT_PLAYER=a,b,c,d HT_ENEMY=... tools/debug/battle_capture.gd` |

Check: `Godot --headless --path . --script res://tools/debug/foundation_check.gd` (player state, shops, parts and
load, a real battle and its payout, levels and pulse, the lab, team slots, rules, events, save and load, modes).
The existing systems, battle, start-chain and view-art checks still pass.

## Not wired yet (next foundations, in Zoids Legacy's order)
- Formation, the rest: XL machines in a middle row, moving between rows as an action, picking rows in team setup.
- Machine forms and combining (form change mode, combining command).
- Field: moving actors and travel limits; more trigger placements; the town map.
- Name entry, link battle and trade (link becomes online play later).

## The modern pass, once this is refined
Zoids Legacy's rules stay the core; these are the upgrades to weigh when each system is refined:
- **Battle:** skip and speed controls for animations, a damage and hit-chance preview before you commit, an undo for
  the menu, auto-battle for grinding, clear status icons, battle replays from the result queue.
- **Growth:** visible pulse thresholds and what each unlocks, respec of pilot growth at a cost, loadout presets.
- **Economy and parts:** compare-before-buy, a recommended loadout, salvage parts for materials.
- **World:** the 3D pixel world (`docs/plan/creature-factory-2026-10-13-world.md`), quick travel, quest log,
  autosave on mode changes.
- **Accessibility:** remappable keys, text speed, colour-safe status markers, larger text option.
- **Link:** online battles and trades in place of the link cable.
- **Content tools:** events, rules, parts and pilots are data, so new content needs no code.

## DRAFT content
Pilot names, crew, items, parts, prices, pulse thresholds and effects, arena challenges, and every event line are
Claude placeholders for Preston to replace; all are labelled draft in their files.
