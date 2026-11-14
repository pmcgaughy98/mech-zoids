# Sprite touch-up lane: toolkit and craft checklist

Started 2026-11-04 by the sprite touch-up lane (Claude). Preston: "Make a session for touching up sprites using a
synthesis of all we've learned, all our tools etc. Especially Aseprite. Sel-out, cap ink, and all the other
professional terms or tasks they would use."

The run log is `LOG.md` in this folder. Each machine's work goes in `<machine>/<take>/*_touchup/` folders only.

## The one rule this lane adds
**A touch-up recolours; it never moves the silhouette.** Every opaque pixel stays opaque and every transparent one
stays transparent (alpha IoU 1.0 against the input). So the canvas, the offsets, the feet row, the proportions and
the packer's sel-out stay exactly as they were, and only the inside of the sprite changes. A fix that needs the
outline moved (the rhino's head and hump drift) is a redraw, not a touch-up, and gets flagged instead.

## 1. Tools on hand (checked live 2026-11-04)

| Tool | What it is good for here | Cost |
|---|---|---|
| **Aseprite MCP** (Aseprite 1.3.18.6-dev, batch Lua) | The working file. One layered `.aseprite` per view: approved ref, cam35 before, touch-up, game sel-out preview. `run_lua_script` for the palette lock (every pixel checked against the 12 colours), `get_color_stats` for the colour counts in the score, `compare_frames` for an independent changed-pixel count and box, `draw_pixels` / `get_pixels_rect` for hand fixes, `outline_native` for an outline preview. Opens in the real editor if Preston or another lane wants to hand-edit. | Free |
| **PixelLab `pixelart_workbench`** | A second opinion that is not my own code: `lint` (orphan pixels, outline gaps and the rest, each named) and `score` (0-100 discipline score) on before and after. Files go up with `get_upload_url` + curl, never as pasted base64. The tool's own note says "Free for subscribers". | Free |
| **Retro Diffusion** `fix_pixel_art`, `run_edit_tool` (pixel_correction, color_reducer) | Built to recover a pixel grid or palette from soft or AI-rendered art. These views are already on the grid and on the 12 colours, so they have nothing to recover. Not used unless a sprite arrives off-grid. | $0.002-0.005 a fix, $0.001 an edit; balance $0.65; needs Preston's yes |
| **The factory's Python passes** | `rhino_l/take-a/anim/selout_rhino.py` `selout()`: the game's outline, applied to every board exactly as the packer does. `capped_ink_trial.py` + `anim/detail_ink.py`: the capped ink rule (darkest colour, strongest contrast first, stop at a target). `measure_ink.py`: interior ink share. `cam35_fleet/fleet_board.py`: board layout. | Free |
| **Hollowtide sel-out** (read only) | `hollowtide/docs/art/crew-selout-2026-10-11/README.md`: the "black sel-out" Preston kept there. Only silhouette edge pixels change, the pass is idempotent, every other pixel stays exact, and before/after hashes are kept. Same rule as the packer's. | Free |
| **Python + numpy + Pillow** | The engine for the passes below: exact, repeatable, measured. | Free |
| **Installed skills** | `verification-before-completion` (measure, then claim). Art direction for this game lives in the playbook and the fleet HANDOFF, not in a skill. | Free |

**Not used, and why:** Codex, SpriteCook, Gemini API, PixelLab AI edits (`edit_image`, `inpaint_image`): a touch-up
needs exact pixels in the locked palette; a generator redraws and drifts (playbook section 3). Each is paid or
metered and needs Preston's yes. The Gemini MCP failed to connect this session.

**Where files go:** the session worktree has no `docs/art/moba`. Write in the scratchpad and copy with Bash into
`D:\dev\new-mech-rpg\docs\art\moba` (same as the fleet lane).

## 2. The craft checklist

Each item scores 0 (misses), 1 (partly there) or 2 (at the approved views' standard). Max 28. Where a number
exists it is measured by the machine's `touchup.py` and written to its `metrics.json`.

| # | Item | What it means | How it is measured |
|---|---|---|---|
| 1 | **Sel-out** | Selective outlining: the outline follows the fill and the light. A dark shade of the fill on lit edges; dark, or merged into the shadow, on the far side. | The packer's outline is uniform #141218 with dark edges merged (Hollowtide's black sel-out). A light-following variant is shown beside it as an option; the packer keeps the current one until Preston picks. |
| 2 | **Capped ink: plate seams and panel lines** | Each plate boundary on a lit face gets a dark seam, capped so the view never goes past the approved views' dark share. | Valley pixels (a yellow pixel darker than both neighbours across it) in lines of 3+, and the frame + seam share against the approved. |
| 3 | **Manual anti-aliasing** | An in-between shade at the corners of steps on curves (horn, knee discs). Never on hard plate edges, never on the outer silhouette. | By eye at 4x. |
| 4 | **Jaggies** | Line steps run evenly (1-1-1, 2-2-2, not 1-3-1). | By eye; single-pixel spurs on the silhouette counted. |
| 5 | **Cluster cleanup** | No orphan pixels or 1-2 pixel specks inside a plate. | Yellow and steel clusters of 1-2 pixels. |
| 6 | **No banding, no pillow shading** | Planes are flat with hard edges; shading does not ring the outline of each plate. | Valley count, and by eye. |
| 7 | **Hue-shifted ramps in the locked palette** | Shadows move toward orange-brown, lights toward pale yellow, all inside the locked colours. | Palette check: 0 pixels off the palette. |
| 8 | **One light direction** | Top-left-front for the whole fleet: tops and left faces lit, right faces and undersides dark. | By eye, per view. |
| 9 | **Rim light and specular on hard metal** | A bright edge where a plate turns toward the light, not a whole plate filled with the highlight. | Highlight share against the approved, and by eye. |
| 10 | **Contact shadow and planted feet** | Lowest pixel on the feet row; the foot sole dark. The ground shadow is the engine's. | Lowest row per view. |
| 11 | **Eyes and lens** | Full size and glowing; the largest eye group at least 85% of approved x 0.82 (fleet HANDOFF); no eye pixel in ne or n. | Eye cluster sizes. |
| 12 | **Silhouette and value read at game size** | The machine, its plates and its joints read at 1x on the map grey. | Board rows at 1x and 2x. |
| 13 | **Dithering only where it reads** | No checkerboard noise inside plates. | 2x2 checker patterns in the yellow ramp. |
| 14 | **Same machine and proportions in all 5 views** | Same parts, same proportions. | Alpha IoU 1.0 against the input (a touch-up cannot change this); drift already in the input is flagged. |
