# 3D to sprite tools, handed over from Hollowtide (2026-11-06)

Written by Hollowtide's Creature factory session at Preston's request: "transfer over what you've learned to mechzoids".
Preston, 2026-11-06: "i wanted you to have rhino session try what you mentioned with what we already have with rhino."
Research, verified where it says so. Nothing has been generated or spent.

## His goal

"consistent 8 angle view from 35 degree camera look. Consistent, fluid, and proportionally accurate animations and sprite
models from all angles with correct perspectives." He is fine with a one-time purchase or a subscription.

## Conclusion

Build each body once as a 3D model. Render all 8 views and every animation frame from one fixed 35 degree orthographic
camera, then finish it as pixel art. Perspective and proportions then match by construction. Every 2D generator Hollowtide
used (Codex, PixelLab, Retro, SpriteCook) redraws each view separately and drifts between views. Three Hollowtide
sessions reached this independently.

## Evidence from Hollowtide

| Test | Result |
|---|---|
| Replace one Codex view of a sheet | Front/back outline match fell from 0.83 to 0.67, so sheets get regenerated whole |
| Retro Diffusion walks | Best walks by Preston's eye, but parts that should hold still move; the body drifted about 190 px off the still |
| Wan 2.2 video (Hugging Face) | In the south view the creature walked toward the camera and nearly doubled in area |
| Hand-built 3D Kithflare rendered to pixels | 8-direction walk free and consistent, but the front views read lumpy (shape match 0.56 to 0.58) |

The weak spot of the 3D route is the pixel finish. Judge the result at game size with measurements, not by eye on the
3D model.

## Pick: MeshForge

keyframe.it.com/meshforge, a free web tool. Page read 2026-11-06.

- **Input:** up to 4 views (front, left, back, right). The rhino's existing sheet views can go straight in.
- **Model cost:** $0.10 (Rodin v2.5 Fast), $0.25 to $0.35 (TRELLIS 2), up to $1.30 (premium models). It bills Preston's own
  fal.ai key. He says the key is saved in MeshForge in his normal Chrome. Never read, type or ask for it.
- **Free:** rigging, including custom bones and prop bones (weapons stay rigid), and a flex test.
  - Preset walk, run, idle, punch, claw swipe, kick, hit reaction, jump and death, with stride, arm swing, bounce and
    tail-sway sliders.
  - The sprite-sheet export, with these settings: camera tilt; top-down or isometric; directions; frames; keep in place;
    pixel-art mode; an 8 to 64 colour palette; outline; toon or flat shading; ground shadow; and a Godot folder.
- **GLB out:** the model can also be rendered in Blender at exactly 35 degrees if the export's tilt can't be set there.
- **Connector:** npm package `keyframe-mcp` 0.8.0, published by the vendor (checked on npm). It gives `meshforge_*` tools:
  generate, start_rig, set_joints, bind_rig, preset_animation, export, contact_sheet and more.
  - Hollowtide added it to its own folder only. This folder needs its own add, with Preston's yes:
    `claude mcp add keyframe -- npx -y keyframe-mcp`
  - The tools appeared in the Hollowtide session a few minutes after the add.
  - **Gotcha:** the connector opens MeshForge in its own Chrome profile, so the fal key saved in his normal Chrome may not
    be there. Either he pastes it into that profile himself, or the session drives the page in his real Chrome.
- **Untested:** whether its rig handles a four-legged or heavy body, whether the tilt reaches exactly 35 degrees, and
  whether the front views come out lumpy.

## Backups

| Tool | What | Price (checked 2026-11-06) | Status |
|---|---|---|---|
| Retro Diffusion low-poly (connector) | Pixel-textured model from up to 4 reference views, GLB out, rig free | 64 px Detailed $0.85 plus $0.35 a move; Lite $0.10 plus $0.08 | Untested |
| PixelOver (desktop) | Imports 3D, pixel shaders, palettes, dithering, 8-way auto-rotate | $19.99 one-time | Untested |
| Ludo.ai Directional Sprites (web, MCP, CLI) | One rigged model in up to 8 views at 5 camera heights (Horizon, Low, Isometric, High, Top), 15 styles | $15 to $20 a month; model 4 to 16 credits, a sheet 1 | Presets are humanoid only; may suit bipedal mechs |
| FoozleCC's Blender 8-direction script | Fixed ortho camera, model turned in 45 degree steps | Free | Never read |

## Pixel finish

Hollowtide's `tools/arena/downscale.py` has `pixelize()`. On detailed stills it left 2 to 9% stray single pixels, against
26 to 68% for plain resampling. Full table: `D:\from-C\Users\pmcga\dev\hollowtide\docs\art\art-tool-map-2026-11-02.md`,
row "3D render-to-pixel".

## The Rhino test Preston asked for

1. Take the rhino's existing views (front, left, back, right) from the current sheet. Upscale them with nearest
   neighbour on a plain background.
2. Generate one model in MeshForge. State the model and price to Preston first. TRELLIS 2 at 1024 is $0.30; Rodin Fast
   at $0.10 is a draft.
3. Rig it for free. Add a preset walk and an attack, then flex-test the legs.
4. Export 8 directions at a 35 degree tilt in pixel-art mode with the rhino's palette, or export the GLB and render it in
   Blender at 35 degrees.
5. Put the result beside the current rhino at game size. Check that the same body shows in every view, that the feet
   stay on the ground, and that the front views aren't lumpy.
