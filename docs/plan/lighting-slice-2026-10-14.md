# The gorilla lighting slice (Claude, 2026-10-14)
Preston: "do the gorilla lighting slice" (the first step toward "a remastered version of zoids sprite ... if it was
released today"). Research: `reports/Lit pixel sprites in Godot.md` (notes in `research_notes/Lit pixel sprites in
Godot/`): Dead Cells rendered small with no anti-aliasing and lit each frame with its normal map and a toon shader;
HD-2D's modern feel comes as much from stage light (flashes, glow, rim) as from the sprite's own shading.

## Wired
- **Blender normal pass:** `render_sprite_views.py` with `SPRITE_NORMALS=1` also writes `<view>_n.png` from the
  bundled `check_normal+y.exr` matcap (white single colour, no shadows, cavity, specular or AA; restored after). The
  colour render stays byte-identical (checked on the gorilla's side view against v70's render).
- **Pixelizer:** when `<render>_n.png` exists, each sprite pixel's normal is the mean of only the render pixels that won
  its colour, snapped to 17 directions; writes `<out>_n.png` (alpha asserted equal to the sprite's) and the eye pixels
  as `<out>_e.png`. Without a normal render nothing changes.
- **Godot:** `shaders/banded_light.gdshader` (N.L rounded to 3 bands, alpha 1.0) and `tools/debug/lit_capture.gd`:
  a 320x180 SubViewport (light per art pixel), the gorilla as a CanvasTexture (colour plus normal) with the banded
  shader, ambient 0.68/0.70/0.80 on the machine only (the stage is on its own canvas layer), a key light from the upper
  left as the bake (energy 0.45, height 0.6), a cool rim light, the visor unshaded with a 1 px additive halo and a teal
  light, and a hit flash. Lights are masked to the machine. Assets: `art/machines/ape_l/lit/` (side view only).

## Checks (Compatibility renderer, Godot 4.7.2)
- Flip: the flipped sprite lit from the left mirrors the plain one lit from the right (0.262 and 0.262): normals mirror
  with flip_h, no pre-flipped maps needed. PASS.
- Energy: key light 0.5 adds 0.074, 1.0 adds 0.168 (ratio 2.25 with 8 bands): energy is applied once. PASS.
- Images: `docs/art/2d/lit_capture.png` (baked, lit, lit with a flash, key from the upper right, key from below, flip),
  `docs/art/2d/lit_capture_closeup.png` (baked, lit, lit with a flash at 4x).

## Open
- Taste: Preston's call on baked against lit. The lit sprite is a little darker with banded highlights; the visor
  glow, rim and hit flash are the parts that read as new.
- The ground flash on the background layer did not visibly show in the capture.
- Not in the battle yet: the battle draws animation frames (`art/machines/ape_l/anim/`); lighting them needs a normal
  map per frame (the same pass in `ape_anim_round.sh` and `export_anim.py`) and the SubViewport in `battle.gd`.
