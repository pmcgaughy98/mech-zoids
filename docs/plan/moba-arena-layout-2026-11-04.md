# First arena and lane layout: proposal (map design lane, 2026-11-04)

Nothing here is canon. The decision is Preston's. The art pass and the themes (below, "Art, minimap and themes")
are scripted pixel tiles at the shared 50 texels per metre, all ours.

- **Sketch:** `docs/plan/moba-arena-sketch-2026-11-04.svg` (top down; blue at the bottom).
- **Walkable greybox:** `scenes/moba3d/arena_blockout.tscn`. It starts with the rhino at blue's base.
  Controls: WASD to move, Q/E or right-drag to turn the camera.
  ```
  "C:/Users/pmcga/Games/Tools/Godot_v4.7.2/Godot_v4.7.2-stable_win64.exe" --path D:/dev/new-mech-rpg res://scenes/moba3d/arena_blockout.tscn
  ```
- **Layout numbers:** the constants at the top of `scenes/moba3d/arena_blockout.gd`. Change a number there and
  the greybox and the sketch both follow it.
- **Check:** `tools/map/arena_check.gd`, run headless. It passes 24 of 24 and rewrites the sketch.
- **Look:** `tools/map/arena_look.gd` (needs a window) renders eight chase-camera shots with the rhino and the
  gorilla into `docs/plan/moba-arena-look-2026-11-04.png`.
- **Played in:** game feel's `scenes/moba3d/arena_play.tscn` instances this blockout and brings the machines.

## The proposal
**One lane, 3 v 3, 84 x 156 m.** It grows straight out of the approved skeleton (one lane, a core and one tower
per team, waves every 30 s) and gives the kits a jungle to play in.

- **Bases:** a walled base 15 m across at each end, holding the spawn and the core. It has a gate onto the lane
  and a side door into each jungle.
- **Tower:** one per team, on the lane's first bend. Its 12 m range is a placeholder.
- **Lane:** 14 m from wall to wall, with the 4.4 m dirt path down the middle. Walls are 3 m tall.
  - From each core: 16 m straight to the tower bend, then 21 m to a sharper bend (39 degrees).
  - Then one 42 m straight runs diagonally through the middle.
- **Plaza:** a paved circle 26 m across at the middle. Waves from both sides reach it about 20 s after leaving
  the spawn, so the fights start there. It has a door into each jungle.
- **Jungle, each side of the lane:**
  - 2 camps per team.
  - 1 side pit per team, sitting in the wide pocket the lane's bend leaves. The pit has a low 1.5 m rim with a
    home door and a stream-side door, so the other team can steal it.
  - Rocks shape the paths.
  - A shallow stream crosses the middle (looks only).
- **Symmetry:** red's half is blue's half turned 180 degrees, so both teams see the same map from home. The
  check confirms every wall piece and rock has a twin.

## Why this shape (from moba-kits.md)
| The kits need | The map gives |
|---|---|
| Long lines: rhino stampede, lobster claw grab, shoebill lunge strike, falcon piercing dart | The 42 m diagonal through the plaza; shorter stretches near the towers, so the line skills are strongest in the middle |
| Something to hide behind from those lines | Lane walls, wall corners at each bend, jungle rocks |
| Flanks: rhino front plating is beaten from the side; wolf, pangolin | 2 jungle doors per half, plaza side doors, base side doors |
| Fennec tunnel ("exit far away") | Walls are 1.2 m thick with jungle behind them, so a tunnel from lane to jungle is a real shortcut |
| A spot to hold: gorilla hex dome, hummingbird bloom, hippo wallow | The plaza (26 m) and the side pits (12 m) |
| Chameleon camouflage stays special | No stealth bushes. The counters already exist: squirrel tail alarm, fennec ears, wolf scent |

## The chase camera numbers that set the sizes
The camera sits 6.5 m from a point 1.2 m above the machine, pitched 30 degrees. That puts it 4.45 m up and
5.6 m behind.

**Pixel sharpness at 1280x720** (60 degree field of view, 50 texels per metre):
- one world texel is one screen pixel about 6 m in front of the machine;
- it is half a pixel at about 19 m.

So the fight spaces are kept about 20 m deep:
- the plaza is 26 m across;
- the bends cut the view down the lane;
- the light fog (0.005, the same as field_test) softens anything past that.

**Walls are 3 m, under the camera's 4.45 m,** so the lane walls never block the view ahead. One problem:
- A 3 m wall less than about 3.1 m behind your machine (on the camera's side) hides the machine from the camera.
  The check is `1.2 + 0.577 x distance < 3`.
- The 6 m edge cliffs do the same.
- **Agreed fix (map design and game feel lanes, 2026-11-04): a dither fade, not a camera pull-in.** A camera
  pulling in would jump the framing mid-fight and would snap at the cliffs. Built 2026-11-04 (Preston: "Build
  it now"). `tools/map/wall_fade_check.gd` (needs a window) passes:
  - 74% of the pixels round a machine hidden behind a lane wall change when the fade is on, both when the
    player script publishes `machine_pos` and when the check sets it directly;
  - a patch of the same wall 2.5 m away changes 0%.
  - Game feel publishes the machine's feet position each frame as the global shader parameter `machine_pos`
    (vec3). Game feel also adds its `[shader_globals]` entry to project.godot.
  - This lane wrote `shaders/world/wall_fade.gdshader`. The blockout's walls, rocks, cliffs, towers and cores
    use it; floors do not.
    - It dithers pixels inside a cone from the camera to the machine's body (`machine_pos` plus 1.0 m up). The
      cone is 1.6 m across at the body, so the cut is the same size on screen wherever the wall stands.
    - A 4x4 dither clears 75% of the pixels in the middle of the cut.
    - It skips the sun's shadow pass, so shadows stay whole. That test only knows the sun: lamps with shadows
      would need another check.
    - It fades only between the camera and the machine, so walls beyond the machine stay solid.
    - Walls, rocks, cliffs and later trees use it, with no per-wall flags.
  - Collision is game feel's: a shape cast against the StaticBody3D walls, sliding along each axis. The Player
    stays a Node3D, so no scene changes.

## Measured (arena_check, on the baked nav mesh for a machine 1 m in radius, at the 3.5 m/s placeholder speed)
| From blue spawn to | Metres | Seconds |
|---|---|---|
| blue tower | 29 | 8.3 |
| blue camp (nearest) | 43 | 12.4 |
| blue side pit | 65 | 18.6 |
| plaza | 71 | 20.2 |
| red side pit (steal) | 90 | 25.6 |
| red tower | 112 | 32.0 |
| red core | 124 | 35.5 |

- **Lane:** 116.8 m along the centre line, core to core. On the nav mesh, core front to core front, it is 104.7 m
  (29.9 s).
- **Clearance:** nothing solid comes within 5.6 m of the lane's centre line. The closest point is the inside of
  the 39-degree bend.
- **Reachability:** every spawn, core, tower, camp, pit and the plaza can be reached from both spawns. Two separate
  checks agree: the nav mesh, and a 1 m walk grid.
- **Fairness:** each team's own pit is the same walk (65.0 m).

## Hooked up for the machines (2026-11-04)
- **Named points:** `Markers/` holds Marker3D nodes:
  - BlueSpawn, RedSpawn, BlueCore, RedCore, BlueTower, RedTower;
  - BluePit, RedPit, BlueCamp1, BlueCamp2, RedCamp1, RedCamp2;
  - Plaza.

  They are saved in the scene, and the builder moves them onto the layout numbers, so a layout change carries
  them along. Each one faces up its team's lane.
- **Collision:**
  - Everything solid is on physics layer 1.
  - One flat ground body on layer 2 (top at y = 0) is there only for the nav bake.
  - Rocks, towers and cores taper, and their bodies taper with them.
- **Nav mesh:** `Built/Nav` is baked from the bodies on load, in about 70 ms, for a machine 1 m in radius.
  - It is ready about 20 physics frames after load.
  - A new wall or prop with a body joins it with no nav work.
- **Audit (arena_check):**
  - every standing mesh has one body the shape of its mesh, and there are no stray bodies;
  - floors lie flat, and nothing solid stands on a spawn, camp, pit or the plaza;
  - 3,856 rays out through the map edge all hit a cliff;
  - there are no nav islands on rock tops.

## Looked at from the chase camera (2026-11-04)
Eight shots, with the real rhino and the gorilla: `docs/plan/moba-arena-look-2026-11-04.png`.
- **The lane reads.** The dirt path, both walls and the next bend show in every lane shot. The 3 m walls never block
  the view ahead.
- **A 3 m wall between the camera and the machine:** the fade cut shows the machine, and the map shows over the wall.
- **6 m cliffs: fixed.** Turning the camera inward along the east or west edge used to put it outside the map,
  with the cliff filling the screen apart from the fade hole.
  - Game feel's chase camera now has `bounds`, a clamp with no pull-in. arena_play and this blockout's camera both
    set it to 41.5 x 77.5.
  - Checked in arena_play: with the camera turned inward at the east edge, it stops at x 41.50 and looks down at
    the machine.
- **The fade near curved walls** (game feel saw a dither patch on the plaza ring beside the rhino):
  - The cut used to ease out as a share of the way to the body, all the way up to the body itself. Now it eases out
    by distance and stops 0.6 m in front of the body.
  - In game feel's frame, the cut on the ring beside the rhino fell from 1.17% to 0.22% of the pixels round it.
    `wall_fade_check` holds both numbers.
  - The rest was the faint edge of the cut, where the ring really does stand nearer the camera than the machine.
  - Game feel now publishes `machine_hidden`: a ray from the camera to the machine's body, tested against the
    walls and eased over 0.15 s. The shader closes the cut while the machine is in plain view.
    - In game feel's frame the cut is now 0.00%.
    - With the machine behind a wall it still opens 74%.
  - Limit: it's one ray, aimed at the middle of the body. A wall that hides only the feet or the head leaves the
    cut closed.
- **Looked at in arena_play:** `tools/map/arena_play_look.gd` grabs game feel's demo and the edge clamp into
  `docs/plan/moba-arena-play-look-2026-11-04.png`.
- **The top edge of the frame is level with the camera** (30 degree pitch, 60 degree field of view). So nothing
  higher than 4.45 m shows near the camera.
  - The labels moved down to 3.2 m for this reason.
  - Trees and tall props will be cut off near the camera. That matters for the art.
- **The core hides the gate from the spawn.** The 5 m core stands between them. Its height is a placeholder.
- **Machines draw at 1.5 screen pixels per texel at 1280 x 720,** so sprite pixels come out 1 or 2 pixels wide. The
  camera distance and window size that set this are not this lane's to change.
- **Fixed after the first look:**
  - labels covered the machine up close (now a fixed 16 px);
  - the plaza and base floors were the same grey as the walls (now a warm paving tint).

## Art, minimap and themes (2026-11-04)
The parent session relayed Preston's ask: "sel-out moba map. Hook it up so it feels legit".

**Images:**
- Before and after: `moba-arena-look-greybox-2026-11-04.png` and `moba-arena-look-2026-11-04.png`.
- Style frames: `moba-style-frames-2026-11-04.png`.

**Ground.** `shaders/world/ground.gdshader` paints the whole ground from the layout numbers in this file:
- jungle, the lane floor, the path, the plaza, team-tinted bases, spawn pads, camp clearings, pit floors and the stream.
- Edges step on the pixel grid.

**Walls, rocks, cliffs, towers and cores** take the cliff tile, plus:
- a top tile with a lip over the edge;
- darker stone near the ground;
- a painted team stripe on base walls, towers and cores.
- The fade lives in `shaders/world/fade_cut.gdshaderinc`, shared with the sprite props.

**Towers and cores:**
- A stone pillar with a team stripe and a turning team crystal.
- Crystal tops: 4.3 m on towers, 4.35 m on cores, because nothing above the 4.45 m frame top ever shows. The greybox had 7 m towers and 5 m cores.
- The range ring (`shaders/world/range_ring.gdshader`) reads `machine_pos`. It fades in within range + 5 m and tints the floor once the player is inside.
- `set_tower_alert(name, 0..1)` turns the ring red; game feel calls it when a tower locks on.
- `set_structure_down(name, true)` leaves a dark stump.

**Readability:**
- Dashed gold rings on camps.
- Dashed orange rings and an orange rim stripe on pits.
- A team ring on each spawn pad.
- Team banners inside each base wall and a team light over each core.
- The floating labels are off by default (`show_labels`).

**Light:**
- Warm sun with hard shadows and a cool fill.
- A sky gradient and fog at 0.004.

**Dressing** (under `Built/Dressing`, with no bodies):
- Trees in three rows past the edge cliffs, and bushes on rock and cliff tops.
- Tufts and flowers on open ground.
- Nothing taller than a tuft stands where a machine walks, so nothing reads as a stealth bush. arena_check holds this for 922 items.

**Edge cliffs** are 3.5 m, down from 6, so the tree line shows over them. That is one number, `EDGE_HEIGHT`.

**Minimap** (`scenes/moba3d/arena_minimap.gd`, bottom right, 31 x 57 base pixels):
- The picture is painted from the layout, and arena_check confirms it is the same map turned 180 degrees.
- Towers and cores show in team colour, grey once down.
- It shows game feel's `map_units` (machines, minions, monsters) and the camera's view on the ground.
- Red players see their own base at the bottom.
- Once `vision` exists, it hides enemies outside vision.

**Themes.** Preston asked for "cyber futuristic technology". The `theme` export takes `nature`, `circuit`, `neon` or `foundry`.
- Tiles and props come from `tools/map/make_theme_tiles.py`; glow is carried in the tiles' alpha.
- `tools/map/style_frames.gd` renders the same shot in each theme, and `tools/map/style_sheet.py` lays them out side by side.
- Layout, bodies, markers and the API are the same in every theme.
- The minimap has a palette per theme.

## Open choices for Preston
What SMITE Joust, Vainglory and Twisted Treeline do with choices 2 to 6, with a recommendation for each: `moba-map-skillup-2026-11-05.md` (2026-11-05).
1. **Settled 2026-11-05: 3 v 3 on this one-lane map, as a side mode** (Preston, via the hub: "For this particular map
   3v3 you are right"). **The main mode will be 5 v 5 on a new map** (Preston, same day, via the hub). That map is
   future work: don't start it until he says so. When he does, give him the lane count, a cost and a first slice.
2. One tower per team (as approved) or two.
3. No stealth bushes, so camouflage stays the chameleon's alone? Bushes would hand every machine a weaker
   version of it.
4. **Settled 2026-11-05: a point you take and hold** (Preston: "Side pit capture"). Built: see `moba-map-skillup-2026-11-05.md`, "Built 2026-11-05".
5. **Built 2026-11-05: the plaza beacon** (after the pits, on Preston's "continue"): see `moba-map-skillup-2026-11-05.md`, "Built 2026-11-05: the plaza beacon".
6. The stream: looks only, or does it slow machines?
7. The look: picked, foundry (2026-11-04).
8. The art pass's numbers: edge cliffs 3.5 m (were 6), and towers and cores topping out at 4.3 m (were 7 and 5).

## Not done or not checked
- **Machine collision** against the walls is game feel's ArenaMotion. This lane has not checked it.
- **Still to build:** fog of war, and waves and lane logic in 3D (the 2D skeleton holds that logic). Waves can
  follow the LANE numbers or the nav mesh.
- **The wall-fade ray covers only the middle of the body.** If a wall hiding a machine's feet shows up in play,
  game feel can add a ray at the feet and take the larger value.
- **Foundry, Preston's pick (2026-11-04), is the default theme.** Before and after: `moba-arena-before-after-foundry-2026-11-04.png`.
  - Towers: a turning turret head, top at 3.98 m.
  - Cores: a reactor with posts turning round a team-lit drum, top at 4.35 m.
  - Walls: cool steel with hazard-striped tops.
  - Pits: a glowing amber grate with a light inside.
  - Camps: amber rings.
  - Bases: hanging team signs.
  - Stream: a runoff channel, which matches the sound lane's water bed.
  - Minimap: in the theme's colours.
- **Fog of war** (`scenes/moba3d/arena_vision.gd`, `shaders/world/fog.gdshaderinc`, picture `moba-fog-look-2026-11-04.png`):
  - Each team has a grid of 1 m cells. Every 0.12 s, rays go out from game feel's `vision_sources` (machines 12 m, minions 8 m) and from standing towers (13 m) and cores (15 m).
  - Walls and rocks 2 m or taller stop sight. Pit rims and the structures themselves don't.
  - `arena.vision.can_see(team, pos)` answers for game feel and the minimap.
  - The world dims where the player's team can't see. The dimming stays off when that team has no unit among the sources, or when the `fog_of_war` export is off.
  - arena_check covers it:
    - rays against a straight-line test;
    - the two teams' views as mirror images;
    - a tower losing sight when it falls;
    - cost: about 0.2 ms per update once sources are on known cells, with new casts capped at 2 ms per update.
- **The forest shows only as a strip about 20 px tall** at the top of the frame, because the frame's top edge is level
  with the camera.

## 8. Quality pass (2026-11-04)

Preston asked for the map to look higher quality. Foundry only (themes with a "detail" entry); every number is a look placeholder.

- Floor and wall tiles are 128 px (a 2.56 m repeat) instead of 32 px (0.64 m, which read as graph paper): plates of mixed sizes, tread, stains, rust, scuffs; wall ribs every 8 px instead of 4, which also stops the shimmer at a distance. The shaders now read any square tile size.
- Steel posts along every wall run, about every 8 m, each with an amber lamp. They are MultiMeshes with no bodies, and they fade like walls.
- Floor marks (shaders/world/floor_decal.gdshader, foundry/decals.png): lane arrows, hazard bands at the base gate and the plaza mouth, bay numbers, oil, scorch, patches, drains and glowing vents. They are drawn on the 50-per-metre grid.
- A baked floor map (`_floor_map`): contact shade within 2.2 m of walls, rocks and structures; light pools under the lamps; plus a slow three-step brightness drift so big floors don't repeat.
- Light: sun 1.3, ambient 0.62 and cooler, bloom on (small levels only), contrast 1.08, saturation 1.1.
- Why baked: the Compatibility renderer has no SSAO and no Decal nodes, and the one ground mesh takes only a few real lights (8 per object by default). So shade, marks and lamp light are painted or meshed, not real lights.
- Before/after: moba-arena-quality-before-after-2026-11-04.png. Clip: moba-arena-quality-clip-2026-11-04.mp4 (tools/map/arena_clip.gd).

## 9. Tower and core pass (2026-11-04)

Preston: "it looks like a old classic roblox asset". What made it read that way, measured from the code and the
before shots: a plain 10-sided cylinder in the corrugated wall tile with one painted band (a rolled-up wall), a head
0.9 m wide on a shaft 1.96 m across at the top (head narrower than the shaft, so no turret shape), no base, flat
untextured StandardMaterial head parts that did not match the pixel art, and two small glows.

Rebuilt in arena_blockout.gd (foundry only; the crystal themes are untouched), structure only from how finished MOBAs
and mech games build a tower, no shapes copied:
- three-part silhouette: stepped plinth with four buttresses, a faceted shaft (thin on towers, stocky on cores), a
  head wider than the shaft top (`_machine_body`, `_shaft`, `_turret`, `_reactor`, built with `_lathe` and `_extrude`);
- team colour in light where every side sees it: a glowing ring under the collar (wall_fade `band_glow`), four strips
  up the shaft faces, a ring and visor on the head, the core's drum; the strips and drum use `_team_glow(col, true)`,
  which keeps the hue under the bloom's clip so red stays red at range;
- a new 128 px "armor" tile (plates, bevels, rivets, worn edges, a chevron, a vent) in make_theme_tiles.py; the head's
  tiles follow the head (wall_fade `use_local`) so its pixels turn with it;
- felled: head, light, ring and strips go dark (`<Name>Trim` hides with the head); the body takes the grey stone.

Kept: TOWER_HEIGHT 2.95, CORE_HEIGHT 2.65, the 12 m range, the `...Gem` holder names, HEAD_TURN. Head tops: tower 4.0 m,
core 4.35 m. The plinth's corners sit at r, as the round body's did, and the body is now the mesh's hull, so the
footprint and nav mesh are the same radius (8 corners where there were 10). arena_check skips dressing whose bottom is
over 2.5 m (a turret's barrels overhang the base; a machine walks under them).

Deliverables: moba-tower-quality-before-after-2026-11-04.png (six chase-camera shots, before and after),
moba-tower-quality-clip-2026-11-04.mp4 (up red's lane to its tower; `arena_clip.gd -- <dir> tower`).
Open: the felled body is still a plain dark post; the tower head's top edge touches the frame top at about 11 m.

## 10. Polish pass (2026-11-05)

The five rough spots from sections 8 and 9, fixed in foundry; heights, the 12 m range, fog density and fog of war, the
side pit and the props are as they were.
1. Felled tower and core: the body swaps to a wreck (`_wreck`): the plinth stays, the buttresses snap, the shaft breaks
   off near 40% of its height in a jagged sooty rim round a crater that still glows ember orange, and armour slabs (and
   on a tower, a barrel) lie on the plinth. The collision swaps to the wreck's hull, same footprint; set_structure_down
   swaps both back when a structure stands again. Head, light, ring and strips hide as before.
2. Black specks: the paving tile's grease blob (one per 2.56 m tile) was near-black; it is now a step or so under the
   plate. The oil and scorch decals are now dithered stains (solid core, two-colour middle, checker rim; oil has a
   sheen) on their own seed, so the rest of the atlas is unchanged.
3. Soft lamp pools: the band dither in ground.gdshader went from 0.6 to 0.2 of a band, so the three rings stay crisp at
   range.
4. Beige haze band: foundry's sky and fog colours went to dusk (sky_top 0.22/0.21/0.34, horizon 0.8/0.46/0.38, fog
   0.46/0.42/0.48); fog density stays 0.005.
5. Tower head against the frame top: the head is 0.25 m lower (housing 0.62 m, top 3.8 m); TOWER_HEIGHT stays 2.95.

Deliverables: moba-polish-before-after-2026-11-05.png (five chase-camera shots, before and after; from
tools/map/polish_look.gd), moba-polish-clip-2026-11-05.mp4 (up red's lane to its felled tower;
`arena_clip.gd -- <dir> tower felled`).
