> **2026-10-15: the current task list is `docs/team/CODEX_TASKS_2026-10-15.md`.** The list below is older.

**Current (2026-10-12): sel-out pass on the gorilla, `docs/team/CODEX_SELOUT_APE_L_2026-10-12.md`.**

> **Codex: read `docs/team/CODEX_START_HERE.md` first** (2026-10-11). It has the current task order; the tables
> below are the full slot list, and the machine rows for `lion_m` and `raptor_s` are retired.

# Codex tasks: art slots

Every placeholder loads from a named file. Drop a PNG at the path, at the size given, and the game shows it
instead of the coloured box. No code changes needed. Screen is 320x180. Names and designs are Preston's;
machines should read as animal war machines in faction colours, not copies of any real Zoid.

| Slot (path) | Size | What goes there | Scene |
|---|---|---|---|
| `res://art/title/background.png` | 320x180 | Title backdrop | title |
| `res://art/title/logo.png` | 200x40 | Logo (no name decided yet) | title |
| `res://art/opening/scene.png` | 320x180 | Opening scene backdrop | opening |
| `res://art/ui/dialogue_box.png` | 312x44 | Dialogue window frame | opening, base |
| `res://art/rooms/hangar.png` | 320x180 | Home base hangar room | base |
| `res://art/rooms/hangar_door.png` | 14x32 | East door out to the field | base |
| `res://art/people/pilot.png` | 12x16 | The player's pilot, walking | base, field |
| `res://art/people/mechanic.png` | 12x16 | The hangar mechanic | base |
| `res://art/field/grassland.png` | 320x180 | First field area | field |
| `res://art/field/canyon.png` | 320x180 | Second field area: a canyon; walkable floor is y 40 to 156 | field2 |
| `res://art/ui/pause_menu.png` | 200x150 | Pause menu window (Deck, Team, Save) | base, field, field2 |
| `res://art/battle/background.png` | 320x180 | Battle backdrop | battle |
| `res://art/machines/lion_m.png` | 64x48 | Player machine: cat line, size M, ground. White and blue armour on a gunmetal frame, yellow eye. Faces right. | base, battle |
| `res://art/machines/raptor_s.png` | 64x48 | Rival machine: raptor line, size S, ground. Red and black armour on a gunmetal frame. Faces right (the game mirrors it). | field, battle |
| `res://art/machines/hawk_s.png` | 64x48 | Canyon rival: bird line, size S, flyer. Red and black armour, gunmetal frame. Faces right (mirrored in game). | field2, battle |

Palette proposal (from `scripts/data/machines.gd`): frame `#4a4f57` / `#2b2e33`, player `#fafaf7` + `#1e90ff`,
rival `#ff3b3f` + `#111111`, lights `#ffd400`.

## Delivered 2026-10-11

All 12 slots above are filled with original draft pixel art at the listed native sizes. The logo is a
text-free mechanical crest pending Preston's game name. Generated with the built-in image_gen tool;
the full prompt set and source paths are in `art-generation-2026-10-11.json`. View `art-contact-sheet.png`
and `art-preview-{title,opening,base,field,battle}.png` beside this file.

Integration fixes: mirrored machine art retains its local offset when scenes position it; the old
battle ground block is used only when its background image is missing; battle HP/EP text fits below
the gauges; the hangar caption no longer says placeholder.

Verified: all 12 imported textures load at their required dimensions; five actual scenes rendered and
visually inspected; `start_chain_check` and `battle_check` pass. `systems_check` passes with its
temporary save redirected into the workspace because the sandbox cannot write Godot's user-data folder.
The story dialogue and working game name are still Preston's to decide.

## Multi-view machines (Claude, 2026-10-11; plan: `docs/plan/multi-view-machines.md`)
Each machine gets eight views so the camera can turn. Drop PNGs at `res://art/machines/<id>/views/<dir>.png`;
the view lab (`scenes/view_lab.tscn`, F6) and later the battle pick them up with no code change.

| Slot | Size | What goes there |
|---|---|---|
| `art/machines/<id>/views/e.png` | 96x72 | Side view, facing screen right |
| `.../ne.png` | 96x72 | Three-quarter back, facing up-right |
| `.../n.png` | 96x72 | Back view, facing away |
| `.../nw.png` | 96x72 | Optional: mirrored from `ne` if missing |
| `.../w.png` | 96x72 | Optional: mirrored from `e` if missing |
| `.../sw.png` | 96x72 | Optional: mirrored from `se` if missing |
| `.../s.png` | 96x72 | Front view, facing the camera |
| `.../se.png` | 96x72 | Three-quarter front, facing down-right |

For `lion_m`, `raptor_s` and `hawk_s`. Feet (the middle of the footprint) at pixel (48, 54) in every view, so
the machine doesn't jump when the view changes. Camera looks down about 30 degrees. Guides with the angle and
proportions of each view: `docs/team/view-guides/<id>.png` (yellow dot = feet point). Draw the mirrored sides
too if a machine has markings that must not flip. Retro Diffusion's rotate gives eight directions in one
job; its names match these.

## Machine redesigns (Claude, 2026-10-11): redraw all four from `docs/design/machines-2026-10-11.md`
Preston: Codex will redo the machines from these designs, in eight views. The current `lion_m.png` (white and
blue) and `raptor_s.png` (red and black) sit too close to well-known Zoids schemes; replace them.
- Machines: `lion_m` (Tiger type, saffron with charcoal back bands), `raptor_s` (plum and bone, bronze tail
  pod), `hawk_s` (oxide red, slate wings, brass), `ape_l` (new: moss green gorilla, bronze fists and chest plate,
  ballast rack on its back). Hex values and weapon mounts are in the design doc and in `scripts/data/machines.gd`.
- Views: the eight-view slots above, 96x72, feet at (48, 54). Guides with shape, angle and where each weapon
  sits: `docs/team/view-guides/<id>.png` (`ape_l.png` is new).
- The single side-view slot (`art/machines/<id>.png`, 64x48) is still used by the battle until it switches to
  the views; the `e` view scaled to fit is enough for it.
- Don't copy anything from Zoids: shapes, weapon layouts, markings or colours. Start from the real animal.

## Update (Claude, 2026-10-11, later): the four starters replace the tiger
Preston dropped the tiger, raptor and hawk as too mainstream. Draw the four starters from
`docs/design/starters-2026-10-11.md`: `ape_l` (gorilla, green), `shoebill_m` (shoebill, slate blue with an amber
bill; not red, not an eagle), `pangolin_m` (pangolin, ochre with madder scale bands), `hippo_m` (pygmy hippo,
mauve and aubergine). Eight views each at 96x72, feet at (48, 54); guides in `docs/team/view-guides/<id>.png`,
all four on one sheet in `starters_preview.png`. Hold the raptor and hawk until they are redesigned.

## 3D rooms (Claude, 2026-10-11, night): read `docs/team/CODEX_TASKS_3D_ROOMS.md`
Preston pointed out your Build 3D Game Rooms plugin. The machines are 3D now, so your next job is their rooms:
Task R1 is the hangar bay where the machine stands at home base, run through your plugin's Function, Form and
Runtime gates with Preston approving each. No paid Meshy spend without his yes.
