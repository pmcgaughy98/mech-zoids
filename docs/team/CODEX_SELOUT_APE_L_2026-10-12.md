# Codex: sel-out pass on the gorilla's eight views (Claude for Preston, 2026-10-12)

Preston asked for a Codex sel-out pass on the gorilla (`ape_l`). Read this file, then look at
`art/machines/ape_l/views/views_contact.png` (the eight views at 4x with their labels and the yellow feet point).

## What you are finishing
The gorilla is no longer hand-drawn per view. One 3D model is rendered into eight views and turned into pixel art by
code, so all eight agree (the problem with the first hand-drawn set). Pipeline: `docs/plan/creature-factory-2026-10-12.md`.
The code gets the shape, palette, light and plate lines right; your pass is the hand finish a script cannot do.

- **Your inputs:** `art/machines/ape_l/views/{e,ne,n,nw,w,sw,s,se}.png`, 190x100 each, transparent, feet at (95, 97).
  Untouched copies: `docs/art/2d/ape_l/v31/` (cropped) and the renders in `docs/art/2d/ape_l/renders/`.
- **Facings:** e = facing screen right, s = toward the camera, n = away; ne, nw, sw, se between. All eight are drawn;
  none is a mirror.
- **Preston's look:** `docs/art/ape-rd-2026-10-11/source_preston_pick.webp` (front three-quarter) and
  `source_preston_side.webp` (side). Match their feel and colours, not their posture (they are AI art; the posture comes
  from real gorilla anatomy, `docs/reference/gorilla-posture-2026-10-12.md`).

## The rules
1. **Silhouette, size and feet stay exact.** Do not change any pixel's transparency, the canvas size or where the feet
   stand. Change colours inside the silhouette only. That keeps the eight views aligned when the camera turns.
2. **Sel-out, lit from above and a little left.** The outline follows the light and the material: top edges one shade
   lighter than the plate, side edges a few shades darker, undersides the darkest shade of that material. No uniform
   black ring. Near-black only for purposeful internal detail (plate seams, the mouth line, vents, joint hubs).
3. **Palette only from these ramps** (dark to light), about 30 to 40 colours in all:
   - green `1f2a1b 303e29 3b5a31 4c713c 598644 6c9b4a 79ac54 8eb960 9fc96f b3d686`
   - grey `1c2129 272d38 181f1c 2a2c31 3f3e43 4c4b52 5a585f 69686f 828188 9a9aa2 b4b5bb c9cbd2`
   - orange `4a2f17 704c2b 8c5626 aa692c d4853b eba655 f6c27c`
   - teal eyes `1f6e66 5fe1d0 bff7ef`; ground shadow `2c2838 403a52`
4. **No copying.** The Zoids Legacy sheets in `D:\Program Files (x86)\Game assets\sprite references zoids` are for
   technique only (study how they light and outline). No shape, marking or colour scheme from them.

## What to fix, in order
1. **The fine grid inside the plates.** The 3D texture's panel lines read as a faint grid of light and dark lines across
   the big green plates. Replace with a smooth ramp per plate: light at the top, darker toward the bottom, a highlight
   on the upper edge. Keep the real plate seams (the near-black lines between plates); remove the faint grid.
2. **The fists.** They read noisy. Each fist should read as one heavy orange block: the knuckle row in front, the
   fingertips curled under, a highlight across the top of the knuckles, a dark underside on the ground.
3. **Stray pixels.** Single pixels that match none of their neighbours, other than deliberate highlights and eyes.
4. **Joints and details.** Grey joint discs with a dark hub and a pale centre (the shoulder pods, knees, ears); the two
   teal eyes small and bright with their 3-step ramp; the chest lights.

## Must match in every view where visible (check each view against this list)
Three ballast blocks straight across the back with orange caps; two small teal eyes under a green brow; a mid-grey face
and nose pad with nostrils; a green jaw; a six-plate green dome with a raised crest ridge down the middle; a round grey
ear disc each side; orange throat, chest and belly plates on the front; orange fists and orange toes; grey joint discs.

## Targets (measured on eight Zoids Legacy battle sprites; ours before your pass in brackets)
| Measure | Legacy | v31 before you |
|---|---|---|
| Colours | 27-54 | 24-28 |
| Mean same-colour cluster | 3.3-4.5 | 5.4-6.7 |
| Stray pixels | 11-16% | 6-9% |
| Light from above (top edges minus bottom, RGB sum) | +49 to +107 | +81 to +100 |
| Highlights | 3-24% | 9-14% |
| Near-black edge pixels | 9-23% | 27-41% |
Measure with `python tools/art/sprite_quality.py <png> ...`. Aim for near-black edges under 25% and keep the rest in the
Legacy band. Numbers are a check, not the goal: Preston judges by eye.

## Working and handing back
- Work on copies in `docs/art/2d/ape_l/selout-2026-10-12/` (the eight PNGs, same names). Keep the v31 originals as they
  are. Save before-and-after pairs at 4x for every view.
- Install with `python tools/art/import_views.py ape_l docs/art/2d/ape_l/selout-2026-10-12 <map.json>` (map: each facing
  to its file, as in `docs/art/2d/ape_l/v31/map.json`). It prints a consistency line per view.
- Checks: `Godot --headless --path . --script res://tools/debug/view_art_check.gd` (feet, palette, heights) and
  `views_check.gd`; then `scenes/view_lab.tscn` with F6 (Q / E turn the camera) to watch all eight in turn. One Godot
  process at a time.
- **Note for later:** the views are re-rendered whenever the 3D model changes, which would replace your pass. Write down
  each kind of fix you make (one line each) in your result file, so Claude can move the repeatable ones into the
  pixelizer (`tools/art/pixelize_render.py`) and only the true hand finish needs redoing.
- Hand back `docs/team/CODEX_RESULT_SELOUT_APE_L_2026-10-12.md`: what you changed per view, the before-and-after sheet,
  the `sprite_quality.py` numbers, the checks run. Don't commit. Paid tools only after Preston agrees to the cost.
