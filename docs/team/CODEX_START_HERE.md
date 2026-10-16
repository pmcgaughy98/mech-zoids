# Codex: start here (mech game, 2026-10-11)

Written by Claude for a new Codex session on this project. Read this whole file first, then
`docs/design/starters-2026-10-11.md`. You made this project's first art pass; this file says what changed since
and what to do next, in order.

> **Newest (2026-10-15): read `docs/team/CODEX_TASKS_2026-10-15.md` first.** (It replaces the 2026-10-13 list.) Six machines (gorilla, hippo, kangaroo,
> pangolin, shoebill, black wolf) are built by Claude's creature factory and installed; your task is the sel-out and
> finish pass on their eight views. Everything below this box is older and partly out of date.
>
> **Earlier (2026-10-11, night):** the machines went 3D. Your current tasks are 3D rooms with your Build 3D Game
> Rooms plugin: `docs/team/CODEX_TASKS_3D_ROOMS.md`. Start there; the eight-view sprite tasks below are on hold.

## New, 2026-10-12: do this first
**Sel-out pass on the gorilla's eight views:** `docs/team/CODEX_SELOUT_APE_L_2026-10-12.md`. The gorilla is now made by
the creature factory (one 3D model rendered into eight views, `docs/plan/creature-factory-2026-10-12.md`), so Task 1
below is replaced for the gorilla: you finish the factory's views by hand instead of drawing them. The other three
starters will come through the factory the same way.

## The project in one paragraph
A 2D pixel-art Godot 4.7.2 game at 320x180, built by Preston (designer and director, not a programmer) with Claude
(code, wiring, designs as proposals) and you (art into named slots). The battles, field and story start are
already wired with placeholders; your art drops into file slots and appears with no code change. Zoids Legacy (GBA)
is Preston's favourite game and the structural reference, but **nothing from Zoids may be copied**: no shapes,
weapon layouts, markings, names or colour schemes. Start every design from the real animal.

## What changed since your first pass
- Your `art/machines/lion_m.png` (white and blue lion) and `art/machines/raptor_s.png` (red and black raptor) sat
  too close to well-known Zoids designs, and Preston then dropped the tiger, raptor and hawk as too mainstream.
  **Retire both images** (move them to `docs/art/retired-2026-10-11/`, don't delete).
- The player now picks one of **four starters**: gorilla, shoebill, pangolin, pygmy hippo. Designs, weapons,
  palettes and reasons: `docs/design/starters-2026-10-11.md` and `scripts/data/machines.gd`.
- Machines now have **eight views** so the camera can turn (`docs/plan/multi-view-machines.md`). The placeholders
  you see in the game are 3D block guides at the exact angles; draw over their proportions, not their blockiness.

## Task 1: the four starters, eight views each (do this first)
| Machine | id | Colours (hex) | Read the design for |
|---|---|---|---|
| Gorilla | `ape_l` | moss `4a7a3c`, pine `2c4a2a`, bronze `a8763e` fists and chest plate | knuckle-walk, ballast rack of blocks on its back, raised bulwark chest plate. **No missiles.** |
| Shoebill | `shoebill_m` | slate `4a6fa5`, navy `1f3a68`, amber bill `f2c26b` | tall legs, upright body, the huge broad hooked bill; broad wings with armoured edges. **Not red, not an eagle.** |
| Pangolin | `pangolin_m` | ochre `da8600`, madder `a02010` scale rows, delft `407090` snout | low body under overlapping scale plates, small pointed head, long heavy tail; can curl into a ball |
| Pygmy hippo | `hippo_m` | mauve `6b4e71`, aubergine `2e2235`, adobe rose `c98b6b` jaw, cream tusks | compact barrel body, broad head, short legs, two jet valves above the snout |

Shared by all: gunmetal frame `4a4f57` / `2b2e33`; the eyes and running lights are teal `5fe1d0` (the player's
faction colour). Weapons and where they sit are listed per machine in `scripts/data/machines.gd` ("mount").

**How the eight views are made now (Preston, 2026-10-11).** Your first gorilla set looked great but the views
didn't agree with each other, and the back was wrong. So each machine is built from **one master drawing**:
1. **You draw one master per machine**: the front three-quarter view (facing screen right and a little toward
   the camera, like `docs/art/ape-rd-2026-10-11/source_preston_pick.webp`), on a transparent background, at its
   true pixel size (roughly 60 to 110 px tall depending on the machine; no upscaled copies). Show it to Preston.
2. **Retro Diffusion's rotate turns it into all eight views at once** (about $0.10, Preston approves each run).
   All eight come from the same drawing, so colours, parts and proportions match.
3. **Fix what rotate gets wrong, by hand, view by view**: parts that should line up (the gorilla's three
   ballast blocks were uneven in two front views), eyes (always teal `5fe1d0`, never white), stray pixels.
   Keep the before-images. Write each machine's must-match list at the top of your notes (part counts, eye
   colour, markings) and check every view against it.
4. **Import**: `python tools/art/import_views.py <id> <folder> <map.json>`. map.json says which file is which
   facing (`e` = facing screen right, `s` = toward the camera, `n` = away). It puts every view on one canvas
   with the feet on the same point, so nothing jumps when the camera turns, and writes
   `art/machines/<id>/views/` (the eight PNGs, `views.json` with the canvas size and feet point, and
   `views_contact.png` to look at). A facing you leave out is mirrored from its opposite (`se` from `sw`).
5. **Check**: `Godot --headless --path . --script res://tools/debug/view_art_check.gd` (feet on the line and
   centred, only the machine's own colours, no view far taller than the rest) and `views_check.gd`. Then open
   `scenes/view_lab.tscn` (F6, Q / E turn the camera) and watch it go round.

**Done so far:** the gorilla (`ape_l`): rotated, blocks and eyes fixed by Claude, imported, checks pass.
Files: `docs/art/ape-rd-2026-10-11/` (master, sheet, fixed views, map.json). Next: the shoebill, pangolin
and pygmy hippo masters.

The old single battle slot `art/machines/<id>.png` (64x48) is still used by the battle until it switches to
the eight views; fill it from the `e` view.

## Task 2 (after Preston reviews task 1): rivals
The raptor and hawk will be redesigned the same way; wait for the design doc before drawing.

## How to check your work
- In Godot open `scenes/view_lab.tscn`, press F6: Q / E turn the camera, O orbits, L labels each machine's view
  and whether it shows your art, a mirror, or the placeholder.
- Headless: `views_check.gd` and `view_art_check.gd` must both pass.
- Run `--path . --script res://tools/debug/views_check.gd` with a window to refresh the guide sheets.
- Make a contact sheet of every view per machine (nearest-neighbour, 4x) and look at each one before handing over.

## Lessons from Hollowtide's art passes (the other project; learned from Preston's corrections)
- **No "AI look":** crisp pixel clusters on the grid, hard edges, limited palette, no blur, no gradients, no
  stray noise. Downscale generated art with nearest-neighbour or a palette-locked downscale, then clean by hand.
- **Measure debris:** count pale-grey and off-palette pixels in every image; a stray white block or speckle in one
  frame was the most common fault. Remove specks under a few pixels.
- **A 1px dark outline** (selective: darker shade of the local colour inside, near-black outside) reads best at
  this size. Keep it consistent across all eight views.
- **Views must agree:** the same markings, plate count and colours from every angle; back views follow the front
  (tail and marking placement). Check one machine's eight views side by side before the next machine.
- **Keep originals:** never overwrite a source; save before-images and a short manifest (file, size, what
  changed). Record generator prompts as you did in `docs/team/art-generation-2026-10-11.json`.
- **Paid tools** (Retro Diffusion, PixelLab, Higgsfield): tell Preston the cost first and wait. Retro Diffusion's
  8-direction rotate (about $0.10) produces these exact eight views from one finished side view.
- Names and lore are Preston's; your notes label new ideas as proposals.

## Handing back
Write `docs/team/CODEX_RESULT_<date>.md`: what you made, a contact sheet path, what you checked, anything left.
Don't commit; Preston commits when he asks.
