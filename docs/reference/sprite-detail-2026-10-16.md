# Sprite detail: past Zoids Legacy (2026-10-16)

Preston (2026-10-16): "Skill up with the synthesis, goal better versions and more enhanced and detailed than zoids
sprites." Structure and technique only; no reference art is copied or stored in the project. The Legacy and Saga
sheets were split and measured in the session scratchpad; only the numbers are kept here.

## Measured: what "more detailed than Legacy" means
New tool `tools/art/detail_metrics.py`, run on 98 Legacy battle sprites from Preston's sheets and on ours. The values
are medians over each set (side views for ours).

| Measure | Legacy | Live (Codex finish) | Current raw | Detail v4 | Detail v6 |
|---|---|---|---|---|---|
| Height (px) | 82 | 96 | 96 | 96 | 96 |
| Colours | 34 | 26 | 26 | 29 | 29 |
| Brightness steps per hue family | 7.5 | 4.4 | 4.4 | 4.8 | 4.8 |
| Same-colour shapes per 1000 px | 300 | 127 | 89 | 341 | 283 |
| The same, diagonals joined (c8) | 173 | 82 | 68 | 245 | 176 |
| Mean shape size (px) | 3.3 | 7.9 | 11.3 | 2.9 | 3.5 |
| Lone single pixels, 8-connected (s8) | 0.06 | 0.02 | 0.01 | 0.11 | 0.06 |
| Panel-line share | 0.10 | 0.05 | 0.05 | 0.13 | 0.11 |
| Real glints per 1000 px | 18 | 9 | 5 | 25 | 17 |
| Near-black silhouette share | 0.06 | 0.01 | 0.00 | 0.01 | 0.14 |
| Local contrast | 23 | 22 | 22 | 27 | 27 |

Ours were already bigger than Legacy's. The gap was in how the pixels were used: about a third of Legacy's separate
shapes per area, clusters two to three times larger, half the panel lines, half the ramp length. The Saga DS sheets
were split as whole sheets, so they are left out.

## Read
Three study agents (Workflow tool, about 0.5M subagent tokens).
- **Shipped technique.** Read sources:
  - Slynyrd, Pixelblog 1: ramps of about 9 swatches, the hue shifting about 20 degrees a step.
  - Arne Niklas Jansson, Pixel Art Tutorial: per-material ramps, gloss gets a few-pixel highlight and dull surfaces none;
    black only on shadowed outlines.
  - the-pixel.art: hue shifting and selective outlining.
  - Pedro Medeiros, Pixel Grimoire #4: small focused speculars.
  - 6th Division's Den, Metal Slug spriting tutorial: about 15 colours a sprite, shared versatile swatches.

  Consensus: long hue-shifted ramps per material, panel lines in the plate's own dark shade with a lit lip, deliberate
  1-4 px glints on metal only, one clear light, cleanup that removes stray mid-tone pixels but keeps designed ones,
  big plates broken into designed shapes. No primary sources were found for Super Robot Wars OG, Zoids Saga DS or
  Mega Man ZX.
- **Our pipeline.** The current pixelizer erased detail it already had: `PIXEL_MIN_CLUSTER=4` removed about 65% of all
  clusters, and `SEAM_SHARE 0.35` can never mark a single straight part boundary. Ramp length is capped by the toon
  matcap's few bands and the family gamma. A finer sprite scale (x3.3) adds pixels but lowers detail per area, and only
  fits the battle at zoom 0.5.
- **Codex's finish.** Codex marked 31 treatments repeatable; nearly all come down to five mechanisms:
  - the lit top row of each part;
  - own-colour outer edges;
  - one-sided seams;
  - per-part recolours by bone and material;
  - thin parts winning their pixel.

  Measured on two machines, the finish added 21-27 clusters per 1000 px. None of it could run automatically, because
  the part-ID render is antialiased and cavity-shaded (about 40,000 colours on the gorilla), so it cannot say which
  part a pixel is.

## Built
- **Piece pass.** `render_sprite_views.py` with `SPRITE_PIECES=1` writes `<view>_piece.png`: one exact colour per
  piece, coded in 16 levels a channel, with no antialiasing or shading. It also writes `parts.json` (each piece's
  bone, material and vertex count). It decodes exactly, about 300-430 visible pieces per machine.
- **`tools/art/pixelize_detail.py`.** The same input and output as the factory pixelizer. In order:
  1. Vote, with thin pieces winning a block they cover a fifth of.
  2. Tone: the factory's own tone, block by block.
  3. A gentle cleanup within each part.
  4. Each part flattened to three tones around its own median.
  5. A gradient within each part from the normal pass, light from the upper left and front.
  6. One-sided own-colour seams between plates of 16+ px.
  7. A lit top row on parts of 25+ px.
  8. Up to 4 glints per 1000 px on metal.
  9. A dark own-colour silhouette with a lit row inside its top edge, and a dark recess round the eyes.
  10. Stray-pixel cleanup over eight neighbours.

## Judged
- **Round 1, blind** (six judges, one per machine, about 0.66M subagent tokens). Detail v4 against the live
  Codex-finished side views, with four Legacy sprites shown as the standard. v4 won on all six machines (confidence 2
  on five, 1 on the kangaroo). Every judge still rated both below Legacy and named the same gaps: speckle, no
  consistent dark outline, flat cobblestone plates without a light direction, muddy heads. v6 answers those.
- **Round 2, blind** (six judges, about 0.67M subagent tokens). Detail v6 against v4. v6 won on all six (confidence 2 on
  five, 1 on the hippo): cleaner plates, a holding outline, fewer stray pixels (one judge counted 6.5% isolated pixels
  on the pangolin against 11.2%). Still rated below Legacy. Their remaining notes:
  - Pixel level, done in v7: ragged one-pixel silhouette fringe; mottled fill in big plates.
  - Model and design: the gorilla's guns and joints should read as cylinders; the wolf's red is scattered rather than
    a few defined plates, and its feet and head are weak; the shoebill's body reads as puffy blocks; the hippo's feet
    are flat bricks; the pangolin's scales are not in ordered rows and its snout merges with its leg; the kangaroo's
    tail and the joint discs need definition.
- **v7** adds the silhouette cleanup (one-pixel spurs off, notches filled) and a 3x3 majority inside each plate. Its
  medians: c8 174, s8 0.06, lines 0.11, glints 16, outline 0.14. That is Legacy's structure density; ramps (4.8
  against 7.5) and colours (29 against 34) remain short.

## Next
- **Model pass on the judges' notes.** Part detail sized to survive the downscale (the study's model-side lever), plus
  the design points above.
- **Ramps.** Longer hue-shifted ramps need palette work and a less banded render; the toon matcap caps them today.

## Model pass 1, gorilla round joints (2026-10-16, later)
- Changed: `disc()` in `tools/blender/build_ape_l_v2.py` now builds 16-sided joint discs with a rounded outer rim and a
  raised rounded hub (`round_rim()`), gated by `ROUND_JOINTS` so only the gorilla's own build uses it. In
  `tools/blender/weapons.py` the gatling drum and cannon muzzles get a rounded front rim when the kit has `ROUND_JOINTS`.
  The cylinders were already smooth-shaded (sharpen() at 40 degrees), so faceting was not the cause.
- Rendered and pixelized as a candidate only: `docs/art/2d/ape_l/renders_detail_round/`, `v72_round_detail/`.
  Not installed; the game's sprites are unchanged. The build rewrote `ape_l_v2.blend` and `art/machines/ape_l/ape_l.glb`
  as every gorilla build does; the previous pair is in `docs/art/3d/backup_pre_round_joints/`.
- Result, by eye (no blind round): small. The fist discs read a little rounder, with a lighter upper rim. The shoulder disc
  is still a dark blob and the back gatling is unchanged. The rims are about one sprite pixel, too small to survive x4.4.
- Next lever, untried: a lighter steel face on the discs against the dark hub (value contrast, not geometry), or a
  pixelizer rule that shades round pieces as a crescent.

## Model pass 2, light steel joint faces (2026-10-16, later)
- Changed: a `steel` material (`c2c6cb`) on the disc() face (`tools/blender/build_ape_l_v2.py`, gorilla build only).
  Candidate: `renders_detail_steel/`, `v73_steel_detail/`. Not installed.
- Result: the knee, flank and neck discs turned steel, but at sprite size the knee reads as a pale smudge, not a joint.
  The two joints that read most, the shoulder and the forearm, are not disc(): the shoulder is a `frame_dark` pod ring,
  deliberately black since the Mechabeast V2 pass (2026-10-14, "a black hub as his"). Changing it is Preston's call.
- The model files were restored from `docs/art/3d/backup_pre_round_joints/` so they match the live sprites. The code
  changes for passes 1 and 2 are still in the build script and apply on the next gorilla build.

## Pixelizer pass, round joints as crescents (2026-10-16, later)
- Added stage 6b to `tools/art/pixelize_detail.py`, off unless `PIXEL_ROUND=1`: a grey part of 12 to 260 sprite px whose
  outline fills its bounding ellipse (fill 0.8 to 1.12, aspect 0.55 or more) is drawn as one tone with its outer band
  two shades lighter on the light's side, two darker opposite, and one top-highlight pixel inside the lit edge.
- With it off, all eight gorilla views re-pixelize byte-identical to the live `v71_detail` (checked).
- v74 (no size or family limit) caught the big rounded armour and flattened it into blobs: rejected.
- v75 (grey, 260 px cap): `docs/art/2d/ape_l/v75_joint_crescent_detail/`, 102 to 369 px changed per view. By eye the
  shoulder and fist joints read a little rounder (lit upper-left rim, dark lower-right, a shine dot); the guns are
  unchanged. Not installed, not blind-judged.
- Blind judge (one, about 96k subagent tokens; Legacy strip as the standard; A/B shuffled): crescent v75 won SE (slight)
  and NE (near clear), lost E (slight: "scattered light-grey specks" on the shoulder block and forearm hub), tied S.
  Its wins came from less noise on the grey metal, not from roundness: "the joint discs and hubs still don't read as
  round" in either version. Not installed. Legacy's joint, per the judge: a dark rim, a clear inner face, one specular
  highlight from a consistent light. Three tries today (rounded geometry, steel faces, crescents) each moved about one
  sprite pixel; at 126 px wide the joint is too small for render-side changes to draw it.

## Model pass, gorilla, first result (2026-10-16 evening)
- Shape rules in pixelize_detail.py (PIXEL_SHAPES, step 6b). v1 painted a top-shade centre on every squarish plate of
  9 to 120 px: polka dots on all six machines and darkened hippo toenails (scratchpad compare8). v2 needs a true round
  outline (corners empty, fill 0.66 to 0.9, metal only) and draws one step either side of the median; tube stripes
  are one under the top shade. v2 is close to invisible: c8 177.8 to 172.9, glints 12.7 to 12.5 on the gorilla E view.
- The rounder joint geometry in build_ape_l_v2.py (16-sided discs, rounded rims, steel faces; renders_detail_steel)
  pixelizes almost identically to the installed sprite (c8 175.3, contrast 25.7 against 26.2). Joints are 4 to 6 px
  across at this size, so their 3D shape does not survive the downscale.
- Nothing from this pass is installed, and PIXEL_SHAPES now defaults to 0 so PC reinstalls match the cloud-installed art. Conclusion: per-part micro shape, in the model or the pixelizer, has stopped
  moving the sprite. What still shows at sprite size is silhouette and big masses (the judges' notes: hippo feet,
  shoebill body, wolf red scatter, pangolin scale rows, kangaroo tail) and hand-placed pixels (Codex's finish).
