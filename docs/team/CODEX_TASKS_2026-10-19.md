# Codex tasks, 2026-10-19: hand-finish the model-pass art (Claude for Preston)

**Read this first. It follows `CODEX_TASKS_2026-10-15.md`**; that file's Task 1 method (battle frames first, then the
eight views, one machine at a time; its shading rules and checks) still applies. What is new is the art under it.

## Branch and lock
- Work on git branch `cloud/model-pass-2026-10-16` (the cloud session's model pass plus today's fixes). Nothing on it
  is committed past `b09aa9b` yet; Preston decides when it goes to `main`.
- **While you work on a machine, create the empty file `art/machines/<id>/CODEX_IN_PROGRESS`.** Every install script
  and render round stops for that machine. Delete it when you hand over.
- Installs back up hand-edited live folders automatically (`tools/art/live_guard.py`); small model fixes after your
  finish go in through `tools/art/patch_frames.py`, which replaces only the frames a rebuild changed.

## What is installed now (all raw detail-pixelizer output, nothing hand-finished yet)

| Machine | Build | Changed since your last finish | Builder switch to get the previous build |
|-|-|-|-|
| ape_l (gorilla) | v71 | nothing; the black shoulder hub is waiting on Preston | none |
| wolf_m | v92 | cloud v85: three red saddles, square shoulder/hip plates, three-claw paws, wedge head, four big tail spikes; v91: head in body grey (24242b); v92: far-side claws dark red (8c1010) | `WOLF_V92=0`, `WOLF_V91=0` |
| hippo_m | p46 | cloud p41: pillar legs, knee wheels, toe caps; p46: body 15 cm lower, toes graded small-big-small | `HIPPO_P46=0` |
| pangolin_m | p44 | cloud p42/p43: shingle scales, raised head, collar ruff, solid red tail cone; p44: far collar trimmed | `PANGOLIN_P44=0` |
| shoebill_m | p89 | cloud p86/p87: lofted hull in seven plates, navy feather blades; p89: far leg's knee 12 cm lower and far thigh mid blue (Preston: the left leg looked like it floated) | `SHOEBILL_P89=0` |
| kangaroo_m | p71 | cloud p69/p70: segmented tail, flat torso slabs, joint discs dark rim / mid face / white bead; p71: boosters, rocket pod and shoulder gun mid grey; orange plate on each shin | `KANGAROO_P71=0` (see the open question below) |

Before/after sheets: `docs/art/2d/model_pass_2026-10-17_before_after.png` (cloud pass) and
`docs/art/2d/hippo_wolf_2026-10-19_before_after.png`. Log: `docs/plan/creature-factory-2026-10-12.md`, last two sections.

## Task: finish the new art, one machine at a time
Order: **shoebill, kangaroo, pangolin, wolf, hippo**; the gorilla last, after Preston's hub decision. Each machine:
battle frames first (`art/machines/<id>/anim/`, 40 frames), then the eight views. The things only a hand can fix,
found by measurement this week (`docs/reference/sprite-detail-2026-10-16.md`: per-part shape changes in the model or
the pixelizer stopped moving the sprite; silhouette, value grouping and hand-placed pixels are what still show):

- **Shoebill:** a deep-blue band across the upper back in E and SE. Two model fixes did not move it (flatter plates;
  the upper wing bone in mid blue); it is most likely the dark outline and seam along the top of the body. Lighten that
  run to the plate's own darker shade, as the Legacy selective outline does. Also: the shoulder plate splits into 2 to
  3 tones; one tone with a lit top row.
- **Kangaroo:** the far shin still shows as a tall dark slab in SE (E is better since p71). Give it the orange plate
  read by hand, grey at the joints, as Preston's painting shows. The tail reads as stripes: a lit top edge on each
  segment so they read as overlapping plates.
- **Pangolin:** one gold bar still stands above the head in E and SE (not a collar scale; its source is unknown).
  Remove it or merge it into the head's outline.
- **Wolf:** check that the far claws (now darker) still read as claws at 1x; the head is now body grey: keep its wedge
  readable with the lit top edge only.
- **Hippo:** the five toes per foot should read as separate rounded caps (graded now); give each a 1 px dark gap.

## Checks after each machine
`Godot --headless --path . --import`, then `view_art_check`, `views_check`, `battle_check`, `battle_fit_check`,
`foundation_check`, `vfx_check` (all in `tools/debug/`). Report per machine what you changed and which checks passed.

## Do not
- Change shapes the model gives (silhouette, part positions): those go back to Claude as a source fix.
- Use the reference paintings' versions of parts Preston called wrong: the gorilla's back blocks, the kangaroo's
  shoulder gun and hip boosters (2026-10-15 corrections).
- Touch a machine without its `CODEX_IN_PROGRESS` lock.
