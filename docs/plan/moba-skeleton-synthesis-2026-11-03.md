# MOBA skeleton from Shotcaller's structure (Claude, 2026-11-03)

Preston: "use this also like a template to wire up the map and other basic stuff we'll need to start building the
moba." Link: github.com/spicylobstergames/shotcaller-godot.

## What was read
Read: the repo record (306 stars, last push 2026-10-09, not archived), `LICENSE.md`, `prototype/project.godot`,
the function and signal lists of `game.gd`, `map/map_manager.gd`, `map/spawns.gd`, `unit/unit.gd`,
`controls/crafty_camera.gd`, `controls/selection.gd`, `collision/*.gd`, and the node tree of
`map/maps/three_lane_map.tscn`. Not read: the function bodies, `goap/` (the bot AI, 35 scripts), `skills/` bodies,
the README design doc.

Cloned for study, depth 1, 10 MB: `D:\Program Files (x86)\Game assets\game-source\shotcaller-godot\`.

**Licence:** code under PolyForm NonCommercial 1.0, art under CC BY-NC. Copying its code or art would bar ever
selling the game. So it is a structure reference like ZoidsLegacyDecomp (CLAUDE.md, "The reference: structure
only"): we write our own code. It runs Godot 4.7, the same as this project, so its node layout carries over directly.

## How Shotcaller is built
- **Match controller** (`game.gd`): start, pause, resume, a one-second tick signal everything listens to, end with
  a winner.
- **Map scene**: tile layers (ground, walls, trees), buildings grouped under a `blue` and a `red` node, each lane a
  `Line2D` (`top`, `mid`, `bot`) whose points are the path, fog as a `CanvasModulate`. One-lane and three-lane maps
  share a `BaseMap` script.
- **Map manager**: loads the map, turns each lane line into a point list, sets up each team's buildings.
- **Spawner**: waves of lane units on a timer per lane and team, heroes placed at the base, dead units pooled and
  reused.
- **Unit** (one class for every unit): team, health, attack, and signals for attack released, hit, was attacked,
  stunned, died; moves with `NavigationAgent2D`.
- **Collision**: a quadtree answers "which units are within this radius".
- **Controls**: a camera that zooms and follows, and a selection script that turns clicks into move and attack
  orders.
- **Skills**: active and passive skills as Resources with modifiers. **Bot AI**: goal-oriented action planning.
- **Design difference:** in Shotcaller you command heroes that act on their own (hence the name). A SMITE-style game
  is direct control of one machine. That choice is Preston's.

## Synthesis proposal (nothing here is canon)
New folders `scenes/moba/` and `scripts/moba/`, 2D top-down, our own code following that layout:
1. `moba_match.gd`: start, a one-second tick, end with a winner.
2. `arena.tscn`: a placeholder ground layer (flat tiles until arena art exists), lanes as `Line2D`, a `blue` and
   `red` group holding each team's core and towers, a `NavigationRegion2D`.
3. `moba_unit.gd`: team, health, attack range, damage and cooldown, `NavigationAgent2D` movement, signals for was
   attacked and died. Towers, cores, lane units and machines all use it.
4. `lane_spawner.gd`: a wave from each core every 30 seconds per lane, walking the lane points and fighting what
   comes in range.
5. Later slices: the player's machine (one approved sprite set, eight directions, right-click to move, camera
   follow); four kit slots as Resources with cooldowns, where the rhino ground pound and its effect plug in; a bot
   for the enemy machine.

For "units in radius", plain distance checks or `Area2D` are enough at this size; a quadtree only when counts grow.

**Alternatives:** three lanes from the start instead of one; Shotcaller's commander style instead of direct
control; online play (then the GodotPrompter multiplayer skills come back) instead of bots.

**Decisions, approved by Preston 2026-11-03:** direct control of one machine, against bots, 1v1. Commander control,
online play and teams stay out until he reopens them.

## First slice
A one-lane arena: two cores, one tower per team, lane-unit waves every 30 seconds walking the lane and fighting;
the match ends when a core falls. Placeholder shapes, no art.

**Headless check:** a script runs the arena at high time scale for 300 simulated seconds and asserts that waves
spawned on both sides, the two waves met near mid-lane, a tower took damage, the match either ended or both cores
still stand with the result logged, and the run printed no errors.

## Second reference: League-of-Jinx (checked 2026-11-03, not cloned)
github.com/DaughterOfZaun/League-of-Jinx: "League of Legends MOBA clone in Godot Engine providing API similar to the
old original scripts". 50 stars, last push 2025-09-28, Godot 4.4, 283 MB, **no licence** (all rights reserved). It
runs on League of Legends' own game data (its `data/` holds characters, spells, particles), and its `docs/` holds
torrents of Riot's unpacked game client and a private server. So: do not clone it, never take its data, read its
folder layout online only.

What its layout teaches is the kit system, the part Shotcaller is thin on (names from `engine/`, bodies not read):
- `spells/`: spell data (a Resource), a spell slot per unit (cooldown, rank), a spell manager, an aim indicator,
  and separate folders for basic attacks and missiles.
- `buffs/`: buff data, a buff slot (timer, stacks), a buff manager per unit.
- `unit/`: a base unit, a champion that extends it, unit data.
- also `passive/`, `status.gd` (stun, root, slow flags), `stats.gd` (stats with modifiers), `events/` (on hit, on
  damage).

For our kit slice, the proposal (nothing here is canon): `KitAbility` Resource (cooldown, cost, range, cast time,
effect scene) + an ability slot per machine + a `Buff` Resource with a timer and stacks + status flags + stats with
modifiers. The rhino ground pound (body animation + forge effect + stun buff) is the first ability through it.
Shotcaller stays the template for the map, lanes, waves and match flow.
