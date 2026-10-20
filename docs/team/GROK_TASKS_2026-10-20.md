# Grok Build tasks, 2026-10-20: images for the visual upgrade (Claude for Preston)

Grok Build (`grok`, v1.0.62, `C:\Users\pmcga\.grok\bin`) runs on Preston's Grok Lite login: model Grok 4.7, with the
Imagine image tool, and it can read image files. Tested headless today (`grok -p ... --output-format json`): a
text-only call reported $0.03, and one Imagine run (read our sheet, generate, save) reported $0.07 in 5 turns. On a
subscription login those figures should be plan usage rather than a card charge; Lite's caps are unknown, so batches
go one task at a time.

**Scope rule (Preston, 2026-10-20): "we'll use grok for world assets not creatures. Like U.I stuff or non-creature
assets."** Task 1 below (creature model sheets) is retired; its outputs stay in the pack folder as reference only. The
machines come from the 3D factory, with Codex for reference sheets and hand finish.

## Who does what
- **Grok:** new images. Reference sheets the factory measures, and concept art for the screens that are not creatures.
- **Claude:** builds the 3D models from the references, converts finished images to the game's pixel look and palette,
  and installs them (Grok never writes into `art/`).
- **Codex:** hand-finishes installed pixel art (`CODEX_TASKS_2026-10-20.md`).

## Pixel anchor (every world and UI asset; from the pixel-art skill's anchor idea, 2026-10-20)
- Screens and fields 320x180 at 32 to 48 colours; UI panels at their slot size at 16 to 32 colours.
- Outlines a darker shade of each area's own colour, never black; 3 tones per material; light from the upper left; no
  gradients, blur or anti-aliasing (Claude's reduction: box downscale to the slot, median-cut palette, no dither).
- UI: dark navy panels with thin light borders and small corner brackets (the installed dialogue box, mode menu and
  pause panel); text areas plain and low contrast.
- World: the grassland's top-down camera and grass, dirt and rock colours for fields; side-on scenes at a low camera.

## Rules for every Grok prompt
- Start with an honesty line: "If a step fails or you cannot see the attached image, say so plainly."
- Original designs only: no Zoids, Pokemon or other franchise names, logos or recognisable designs. Names, lore and
  any title text are Preston's: no text or lettering in images.
- Save outputs to `docs/art/2d/grok_pack_2026-10-20/` with the file name the task gives. Never write into `art/`.
- One image per run; Preston (or Claude, with his go) looks at it before the next.

## What the test showed (hippo, `grok_pack_2026-10-20/hippo_m_grok_modelsheet_test.png`)
A true flat side, front and back view at one scale, which Codex's sheets have not been (its views came back angled).
It drifted from our design: grey armour plates instead of plum, one gun on the back instead of two short crown jets,
a softer cartoon animal, and text labels despite "no text". So each prompt below spells out the colours and parts
per area, and repeats the no-text rule at the end.

## Task 1 (retired 2026-10-20): flat orthographic model sheets, all six
For each machine, attach `docs/art/2d/codex_reference_pack_2026-10-19/<id>_sheet.png` and use its prompt from that
folder's `PROMPTS.md` (first sentence: the blueprint sentence), plus: "Every armour plate keeps the colours on the
attached sheet; do not add or remove weapons; no labels, no text anywhere." Save as `<id>_grok_modelsheet.png`.
Order: hippo (redo), pangolin, gorilla, wolf, kangaroo, shoebill. Claude measures each against our side view, as with
Codex's sheets.

## Task 2: the four 320x180 screens
They already read as pixel art (a hangar opening onto a valley; a dark plain under mountains for battle; a top-down
grassland with a dirt track; a hangar base over a valley at dusk for the title), but they are not palette art: 15,000
to 28,000 colours each from soft gradients and anti-aliased edges, where the machines use 30 to 35 colours in long
ramps. The upgrade keeps each composition and gives it the sprites' discipline. For each, attach the current file and
ask for the same scene at 16:9 with flat colour areas, hard-edged clusters, no gradients or soft blur, light from the
upper left, no text, no creatures; Claude reduces the result to a 32 to 48 colour palette at 320x180 and compares it
with the current file side by side.
1. `battle_bg.png` from `art/battle/background.png`: keep the level plain clear where the machines stand (player near
   the bottom left, enemy higher at the right); a little more light on the ground so the dark machines separate from it.
2. `field_grassland.png` from `art/field/grassland.png`: same top-down layout, it tiles or scrolls, so keep the edges
   matching.
3. `title_bg.png` from `art/title/background.png`: keep the upper middle clear for the 200x40 logo.
4. `opening_scene.png` from `art/opening/scene.png`.
Claude shows Preston old against new and installs only what he picks.

## Not for Grok
- The machines' own sprites (they come from the 3D factory so all eight views and the battle frames agree).
- The 12x16 people sprites (too small for a generated image to help) and the logo (title text is Preston's).

## Results, 2026-10-20 (Claude ran Tasks 1 and 2 headless; `runs.jsonl` has each run's reply and reported cost)
- Task 1 (gorilla, wolf, kangaroo, shoebill, from fresh sheets of the installed builds, `<id>_our_sheet_2026-10-20.png`):
  flat side, front and back every time. The wolf matches our design; the others drift (an upright gorilla, a
  feathered real-bird shoebill, a cartoon kangaroo with text labels). Next prompts: name the stance ("walks on its
  knuckles, body low and long"), say "hard mech armour plates, no feathers or fur", and end with the no-text rule
  twice. Hippo and pangolin still to do from their new builds (p47, p45).
- Task 2: all four screens generated and reduced (`*_320_48c.png`). Preston picks which, if any, to install.

## Task 3: the empty world and UI slots (running 2026-10-20)
Slots the scripts declare with no art yet (they show a flat colour today):
- `art/field/canyon.png` 320x180 (`scripts/scenes/field2.gd`): a top-down canyon field in the grassland's style; the
  walkable floor band runs y 40 to 156, the exit to the grassland is at the left edge, mid-height.
- `art/ui/menu_mode.png` 320x180 (`scripts/scenes/menu_mode.gd`): a dark menu screen; text sits at the title (10, 6),
  rows from y 20 every 11 px, an info line at y 145 and a footer at y 168, so the middle stays plain and dark.
- `art/ui/pause_menu.png` 200x150 (`scripts/ui/pause_menu.gd`): a framed panel; title strip at the top, list rows from
  y 14, an info box from y 110.
Each run attaches an installed image as the style reference (the grassland, or the dialogue box for UI). Claude
reduces each to its slot size and palette and shows Preston before installing.

## Later candidates (world and UI only)
- The battle background again, keeping the current dark mood (Preston kept the current one over the bright redo).
- The dialogue box restyled to match the menu panel; move-type and item icons; the hangar door (14x32, small enough
  that it may be better hand-made).
