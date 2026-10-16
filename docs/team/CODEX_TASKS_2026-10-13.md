# Codex tasks, 2026-10-13: finish the factory's six machines (Claude for Preston)

**Superseded 2026-10-15 by `CODEX_TASKS_2026-10-15.md`: read that instead.** Kept for history.

**Read this first; it replaces the task lists in `CODEX_START_HERE.md` and `CODEX_TASKS.md`.** Those describe four
starters and hand-drawn masters; both are out of date.

## How we split the work (the Hollowtide way)
Claude builds and wires: each machine is a 3D model built by a Python script, rendered into eight views, pixelized
with the machine's palette and installed into the game (the creature factory, `docs/plan/creature-factory-2026-10-12.md`).
That gets shape, proportion, palette, light direction and alignment right across all eight views. **Your part is the
hand finish a script cannot do:** sel-out, clean plate shading, readable weapons and details. You change colours
inside the silhouette; Claude's pipeline owns the silhouette, canvas and feet.

## The six machines (all installed, Godot checks pass)
| id | Machine | Installed build | Palette | Preston's reference (drawn from our model) |
|---|---|---|---|---|
| `ape_l` | Gorilla | v68 | `tools/art/palettes/ape_l.json` | `docs/art/reference/starters/ape_l.png` |
| `hippo_m` | Pygmy hippo | p27 | `tools/art/palettes/hippo_m.json` | `docs/art/reference/starters/hippo_m.png` |
| `kangaroo_m` | Red kangaroo | p48 | `tools/art/palettes/kangaroo_m.json` | `docs/art/reference/starters/kangaroo_m.png` |
| `pangolin_m` | Pangolin | p23 | `tools/art/palettes/pangolin_m.json` | `docs/art/reference/starters/pangolin_m.png` |
| `shoebill_m` | Shoebill | p69 | `tools/art/palettes/shoebill_m.json` | `docs/art/reference/starters/shoebill_m.png` |
| `wolf_m` | Black wolf | v66 | `tools/art/palettes/wolf_m.json` | `docs/art/reference/starters/wolf_m.png` |

**2026-10-14:** all six were rebuilt in the Zoids Legacy look (lighter values, a raised camera with the side view
turned toward the viewer, toon matcap light) with a detail pass (panels, vents, bolts, pistons). Preston is
generating new reference images from the four-view sheets `docs/art/2d/sheets/<id>_<version>.png` (versions in the
table). Use the new references when they land; the measured gap to Legacy is in
`docs/reference/sprite-rules-legacy-2026-10-14-gap.md` and `tools/art/legacy_gap.py` scores a sprite against it.

The references are ChatGPT pictures Preston generated from our renders; use them for **finish and feel** (how
plates are shaded, how joints and weapons read), not for shape. Look at the sheets in `docs/art/2d/sheets/` first.

## Task 1: sel-out and finish pass, all eight views per machine (start with the gorilla)
**Inputs:** `art/machines/<id>/views/{e,ne,n,nw,w,sw,s,se}.png` (the installed views, transparent, all on one canvas
with the feet on one point; `views.json` beside them). Untouched copies are in `docs/art/2d/<id>/<build>/`.
**Before you start a machine:** copy its `views/` folder to `docs/art/2d/<id>/<build>_pre_codex/`.
**Write your finished views** back into `art/machines/<id>/views/` and keep a copy in `docs/art/2d/<id>/<build>_codex/`.
If Claude installs a newer build of a machine you finished, Claude carries your work forward or flags which views
need it again; your `_codex` folder is never overwritten.

**Rules** (the full version, with the gorilla's colour ramps, is `docs/team/CODEX_SELOUT_APE_L_2026-10-12.md`):
1. **Silhouette, canvas and feet stay exact.** Do not change any pixel's transparency or the canvas size.
2. **Sel-out, lit from above and a little left.** Top edges a shade lighter than the plate, side edges darker,
   undersides darkest. No uniform black ring. Near-black only for real seams, vents, mouths and joint hubs.
3. **Palette:** only the colours in the machine's palette JSON, plus the teal eye ramp `1f6e66 5fe1d0 bff7ef`.
4. **Fix in this order:** (a) the faint grid of panel lines inside big plates: replace with a smooth ramp per plate,
   light at the top, a highlight on the upper edge; keep the real seams. (b) Weapons and new hardware so each reads as
   one object: barrels with a lit top edge and a dark muzzle, launcher boxes with visible tube mouths, emitter lenses
   that glow (the list per machine is in `docs/art/3d/<id>_weapons.json` and `docs/team/CODEX_WEAPONIZED_REFERENCES_2026-10-13.md`).
   (c) Joints: grey discs with a dark hub and a pale centre. (d) Stray single pixels that match nothing around them.
5. **Per machine, a must-match list at the top of your notes** (eye colour, part counts such as the gorilla's three
   back blocks, the kangaroo's two ears, the wolf's four legs and red claws) and check every view against it.
6. **No copying** from the Zoids sheets in `D:\Program Files (x86)\Game assets\sprite references zoids`: technique only.

**Order:** gorilla (Preston's favourite and the best match, start here), hippo, kangaroo, pangolin, shoebill, wolf.
**Per machine, show Preston** a contact sheet: the eight views before and after, nearest-neighbour at 4x.

**Check before handing over:**
- `Godot_v4.7.2-stable_win64_console.exe --headless --path . --script res://tools/debug/view_art_check.gd` must PASS
  (feet on the line and centred, only the machine's colours, no view far taller than the rest).
- Open `scenes/view_lab.tscn` (F6; Q / E turn the camera) and watch each machine go round.

## Task 2 (after Preston reviews Task 1's gorilla): the battle slots
The battle screen (`scripts/scenes/battle.gd`, Zoids Legacy staging) shows the player's machine from behind-left
and the enemy from the front. Check each finished machine there (run the battle test) and fix anything that reads
badly at battle size. Note what you changed per view.

**All six starters now play animation sets in battle** (2026-10-13; `docs/plan/battle-animation-starters-2026-10-13.md`):
`art/machines/<id>/anim/<clip>/<k>.png` with `anim.json` beside them, rendered by `tools/art/anim_round.sh <id>`
(the gorilla's by `tools/art/ape_anim_round.sh`); finish them the same way as below. The gorilla's set:
`art/machines/ape_l/anim/<clip>/<k>.png`
(51 frames over seven clips, one 149x148 canvas, feet on row 121; `anim.json` beside them), rendered from the model by
`tools/art/ape_anim_round.sh`. Finishing its eight views does not reach the battle. Finish the frames with the same
rules, keep each frame's silhouette and canvas exact, and keep a copy in `docs/art/2d/ape_l/anim_codex/`: Claude's
script rewrites the folder whenever the gorilla is rebuilt.

## Coming next (Claude wires these first; do not start them yet)
- **Texture sheets for the 3D models:** a paintable texture per material slot (panel lines, wear, decals) that the
  build scripts apply, so finish work survives every rebuild. You will paint those sheets.
- **A 3D world drawn as pixel art:** a test room rendered through a low-resolution pixel filter with the machine
  sprites standing in it. You will dress and texture it with your 3D room tools (`docs/team/CODEX_TASKS_3D_ROOMS.md`).

## Do not
- Change any `.py`, `.gd` or `.json` under `tools/`, `scripts/` or `docs/art/3d/` (Claude's side; ask in a note).
- Move or rename files Claude's scripts read.
- Commit. Preston commits.
