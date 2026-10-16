# Sprite rules, measured from Zoids Legacy (Claude, 2026-10-12)

Measured from the GBA battle-sprite sheets Preston saved in `D:\Program Files (x86)\Game assets\sprite references zoids`
(Helic Republic, Zenebas Empire, BLOX Fuzors) and two Zoids Saga DS sheets. **Technique only.** No sprite, shape,
colour scheme or layout from them goes into the game; the sheets stay outside the project. Our machines keep their
own designs and palettes (`scripts/data/machines.gd`).

## Measured on all 93 Legacy battle sprites
| What | Min | Median | Max |
|---|---|---|---|
| Width (px) | 78 | 146 | 212 |
| Height (px) | 41 | 84 | 127 |
| Colours per sprite | 19 | 34 | (356: a merged sheet blob) |
| Edge pixels that are the sprite's two darkest colours | 0% | 4% | 20% |
| Top edges brighter than bottom edges (sum of RGB) | +31 | +107 | +252 |

## What that means for drawing
1. **Battle sprites are big:** a large machine is about 110 to 150 px wide, a small one 80 to 100. Our old 64x48
   battle slot is half the reference size.
2. **About 30 to 35 colours**, mostly in **long ramps**: Iron Kong (the gorilla type) has 17 greys, 7 reds, 4 blue
   greys and a 3-step green eye. The main material carries the long ramp; the accent colour is a 5 to 7 step trim.
3. **No black outline.** Edges take the darkest shade of the colour they border (selective outline). Only 4% of edge
   pixels are the darkest colours. This replaces the "1px dark outline" lesson from Hollowtide for this game.
4. **Light from above and the left**, on every sprite: top edges get a light rim, undersides fall into the dark
   end of the ramp.
5. **Detail vocabulary** (from Iron Kong at 5x): round joint discs with a pale centre highlight and a coloured ring;
   vent grilles as alternating dark and light stripes; panel lines as a dark line with a light line under it
   (a bevel); a tiny bright eye with its own 3-step ramp; no dithering.
6. **A flat ground shadow**: a one or two pixel line in a dark violet grey under the feet.
7. Overworld sprites (Saga DS) are 32x32 to 64x64 with 10 to 16 colours.

## Sources in the repos (cloned to `D:\Program Files (x86)\Game assets\zoids-source`)
- `ZoidsLegacyDecomp`: the game's structure (battle, deck, state machine); notes in `battle-structure.md`.
- `Demonstrandum/Zoids` is a boids flocking simulation in Zig, not a Zoids game; possible later use for swarms.
- `krakenjs/zoid` (named in the request) is a PayPal web-component library, unrelated; not cloned.

## Gorilla attempt v1: 3D render to sprite (2026-10-12, failed, kept for the record)
`tools/art/pixelize_render.py` turned the 3D build's view renders (`docs/art/3d/ape_l_views/se.png`, `e.png`) into
151x113 sprites with 31 colours by the rules above (`docs/art/2d/ape_l/compare_v1.png`). Not usable, for three reasons:
the renders are grey-backed close-ups that crop the machine; the model's cyan glow rings read as cyan rings on every
joint (the design has grey discs); the baked wear and AO textures turn into speckle instead of flat planes.
Fix for v2: a dedicated sprite render from the .blend: transparent background, the whole machine in frame at the
Legacy three-quarter angle, flat material colours with no textures, one key light from above-left, glow rings as grey
discs and only the eyes teal; then the same pixel rules, shading per plane instead of per pixel.

## Gorilla attempts v2 and v3: dedicated sprite renders (2026-10-12)
`tools/blender/render_sprite_views.py` renders the .blend for sprites: Workbench albedo, no normal maps, transparent,
one framing for all eight views, glow rings grey and only the eye lenses teal. `pixelize_render.py` then applies the
rules at one fixed scale (`x4.4`), with Preston's own ramps from his picked sprite (8 greens, 9 greys, 6 oranges,
3 teals), a darkening gamma of 1.35 and edges three shades down. Result `docs/art/2d/ape_l/v3/` and
`compare_v3.png`: eight views of one machine, 104 to 129 px wide and 102 to 120 tall (Iron Kong is 114 x 114),
24 to 28 colours. What still separates it from Preston's master is the shape, not the pixel rules: the 3D model's body
is a wide flat-topped slab on short legs with one long ballast slab, where the sprite is a tall hunch with three
separate blocks (outline score 0.734). Its large flat panels with baked panel lines also read busier than the sprite's
rounded plates.

## Gorilla v4 to v7 (2026-10-12)
- Preston: v3 "looks like a bulky PS1 sprite... still bulky like the 3D model." He added a side-view sprite
  (`docs/art/ape-rd-2026-10-11/source_preston_side.webp`) as a second target.
- Measured bulk (shoulder height over hip height): his sprites 1.40 to 1.41, v3 1.18 to 1.27.
- Camera lowered from 25 to 10 degrees (the high camera showed the torso's flat top as a green plateau); rump lowered
  in the build (pass 26). Hunch now 1.32 side, 1.36 three-quarter.
- Part-ID pass: the render script splits the mesh into its 391 parts and renders each in a flat random colour; the
  pixelizer draws a dark plate line where two parts meet. Few lines appear on the torso, which is one sculpted solid.
- Preston's own style over Legacy's where they differ: near-black silhouette outline (`181f1c`, as in his sprites);
  shade usage matched to his master by brightness rank (histogram matching per colour family).
- Ballast: pass 26 ran the blocks along the spine; Preston, same day: keep them straight across the back as in the
  back view (the front view only made them look like they climbed the back). Reverted.
- Result `docs/art/2d/ape_l/v7/` and `compare_v7.png`: 104 to 129 px wide, 23 or 24 colours per view.
