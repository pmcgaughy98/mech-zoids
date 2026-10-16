# Light the gorilla twice: sprite, then stage

Shipped games that make pixel sprites look current do two different jobs, and the gorilla needs both. At the **sprite level**, Dead Cells renders each 3D-animated frame at tiny size with no anti-aliasing, exports a matching normal map per frame, and lights it in game with "a basic toon shader". Brigador's prerendered mechs reportedly carry normal and depth data rendered from their 3D models for the same purpose. At the **stage level**, Octopath Traveler keeps its sprites as flat cards. Its modern feel comes from what surrounds them: cast shadows, spell effects that flash the whole room with light, battle hue shifts, bloom, and exaggerated depth of field. For the gorilla, the version-correct pipeline has three parts. First, a **third Workbench pass per view** that uses Blender 5.2.2's bundled `check_normal+y.exr` matcap under the **Standard** view transform, with white single colour and AA off. That pass measured 1.36/255 error locally and is already green-up, which is what Godot expects. Second, a **normal downsample that reuses `pixelize_render.py`'s exact blocks** and builds each output normal only from the source pixels that won that block's colour. Third, in Godot 4.7, a **CanvasTexture** (diffuse plus normal) on the sprite, a `light()` shader that **rounds N·L into 3 bands**, and a **320x180 SubViewport** so light lands per art pixel. Two facts from the project's own files change what the research notes alone would prescribe. The project runs the **GL Compatibility renderer**, where HDR 2D selective glow is not available, so the visor glow is built from unshaded and additive pixel sprites plus a small teal PointLight2D. And the colour render **already bakes a studio key light and cast shadows** that the pixelizer uses to pick palette shades, so the first slice keeps that baked sprite and points the runtime key light the same way. The biggest unverified item: every engine-source reading came from the Forward+/Mobile shader, not the Compatibility shader this project actually uses.

## Shipped games split the work between sprite and stage

The closest primary-source precedent is Dead Cells. Thomas Vasseur built characters in 3DS Max and rendered them with "a little homebrew program" at **"a very small size and without antialiasing"**. A character stands **50 px tall** in game. Each frame was exported "to a .png, along with its normal map, allowing us to render the volume using a basic toon shader" ([Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)). The same article names the cost the team accepted: **flickering pixels** in the low-resolution, cel-shaded result, which they chose not to clean by hand. On the earlier ScarKrow prototype they had hand-drawn shadows on every frame, and the lighting system was designed so Dead Cells would not need that ([Game Developer](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)). The article gives no band count, light count, or normal-filtering method, so those parts of any "Dead Cells recipe" are craft knowledge, not quotes.

Brigador is the closer subject match: mechs prerendered from 3D models into ordinary sprite sheets. A Steam poster writing as the team says they "use depth mapping and various tricks with information rendered out for the sprites from the original 3D models, so the lighting engine has '3D model' information for each sprite" ([Steam thread](https://steamcommunity.com/app/274500/discussions/0/133261370000956352/?l=brazilian)). The poster's developer status is unverified, so this is medium-confidence corroboration of the Dead Cells pattern rather than a second primary source. Authoring tools such as SpriteIlluminator, which supports "algorithmic and hand-painted normal maps", show the same normal-map route serves hand-drawn sprites too ([CodeAndWeb](https://www.codeandweb.com/spriteilluminator)).

HD-2D shows the stage half. Digital Foundry describes Octopath's heroes as "purely sprite-based" but given a physical value in 3D space so they cast **perspective-correct shadows**. Fire and smoke in battle "brighten up the entire room, flashing the area with light", spells and boosts change the environment's hue, and an exaggerated bokeh depth of field gives a miniature look ([Digital Foundry](https://www.digitalfoundry.net/articles/digitalfoundry-2018-octopath-traveler-a-hybrid-game-for-a-hybrid-console)). Acquire admits the first game "had to play tricks with the lighting" to make flat characters sit in 3D backgrounds. It set Octopath II's target as art that "just barely looked like it could belong in a pixel-art game", and treated camera rotation as the thing that strains flat sprites ([Unreal Engine](https://www.unrealengine.com/developer-interviews/octopath-traveler-ii-builds-a-bigger-bolder-world-in-its-stunning-hd-2d-style)). No source read confirms normal maps on Octopath's character sprites. Sea of Stars markets "full-on dynamic lighting" from a "custom-made render pipeline" ([Sabotage press kit](https://sabotagestudio.com/presskits/sea-of-stars/)), but its technique stayed behind a blocked Reddit thread ([r/PixelArt](https://www.reddit.com/r/PixelArt/comments/odn30d/dynamic_lighting_on_pixel_art_in_our_upcoming/)).

Super Robot Wars, the living heir to GBA mech battles, does not light pixel art at all. It moved from an in-house engine dating to the Alpha era to **Unity for SRW Y**, and its battle animations are still made by veteran staff. For Y the team cut screen blackouts and widened the animation area ([Dengeki Online](https://dengekionline.com/article/202508/47898)). Players credit camera, dynamics and sound over sprite resolution: "HD sprite doesn't make the animation good" ([Steam community](https://steamcommunity.com/app/898750/discussions/0/3189115819978629901/?l=hungarian&ctp=2)). For a "Zoids Legacy remaster", the conclusion is that per-pixel lit sprites deliver volume, while the "released today" read comes as much from stage events (hit flashes that light the mech, a hue shift on specials, a ground shadow) and from camera work.

## A matcap pass gives Godot-ready normals within 1.4/255

Blender 5.2.2 offers two ways to get a normal map. Only one of them is free of conversion work. Workbench can render with the bundled `check_normal+y.exr` matcap. That EXR is pre-linearized: its centre texel is (0.2158, 0.2133, 1.0), the linear value of sRGB 0.5. Under the **Standard** view transform it therefore writes `n*0.5+0.5` directly. A headless test on an orthographic sphere measured a **mean error of 1.36/255** against the analytic camera-space encoding. Green rises toward the top of the image, so the map is **Y-up, OpenGL-style** (local test, `research_notes/Lit pixel sprites in Godot/blender_normal_tests/nm_test.py`). Godot decodes 2D normals as `tex.xy * vec2(2,-2) - vec2(1,-1)` in a Y-down screen space. Y-up green is exactly what it expects, so **no green flip is needed** ([canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)).

Every default is a trap, and the test put a number on each one. The factory **AgX** view transform gives 24.6/255 error. **Raw**, the intuitive choice for data, gives 48.8/255 because the EXR expects Standard. The default single colour of **0.8 grey** multiplies the matcap and gives 15.7/255. With `render_aa = 'OFF'` and transparent film, alpha held only 0 and 1, a hard silhouette with no fringe (local test, `nm_test.py`). The Cycles and EEVEE Normal passes work but are **world space**, so they need a per-camera rotation by script. Blender 5.2.2 also writes multilayer EXRs as multi-part files, which first fooled the test reader into seeing only Combined (local test, `nm_pass_test.py`, `read_parts.py`). The engine enum no longer accepts `BLENDER_EEVEE_NEXT`.

The gorilla's renderer is already almost the right shape. The sprite script (snapshot at `docs/art/3d/gorilla-texture-2026-10-13/sprite-renderer-snapshot.py`, live as `tools/blender/render_sprite_views.py`) already uses Workbench, Standard view transform, transparent film and one orthographic camera at 10 degrees elevation. For each of eight views it renders a colour image and a flat part-ID image (`<view>.png`, `<view>_id.png`). A third render in the same loop, with the same camera and frame, is pixel-aligned by construction. Three settings must be switched for that pass and restored afterward. The colour pass turns on **cast shadows** (`show_shadows = True`, intensity 0.55) and never sets `render_aa`, and both would corrupt normals. The script also rotates the studio light by -20 degrees. A matcap is a view-space lookup and should ignore that rotation, but this was not tested, so the recipe includes a one-sphere check.

## Normals must follow the colour winner, block by block

Godot samples the normal texture with **the same UV and the same sampler** as the colour texture, reads only **R and G**, and rebuilds Z as `sqrt(1 - x² - y²)` ([canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)). Two rules follow. The normal frame must have exactly the colour frame's size, crop and padding. Only X and Y accuracy matter.

The pixelizer is not a simple box filter, and the normal step has to respect that. `pixelize_render.py` downsamples at a **non-integer scale** (render pixels per sprite pixel, for example x4.4), with per-block bounds computed from `int(oy * scale)`. It picks the **most common (family, shade)** in each block. It lets an **eye pixel win its block** so the visor survives. It applies a 2x2 Bayer dither to the shade, and it adds plate lines, a near-black silhouette outline and a ground shadow (`tools/art/pixelize_render.py`, lines 133 to 196 and 236 to 241). A separate normal script would have to reproduce all of that, so the normal step belongs **inside the same block loop**. For each output pixel, take the source pixels in that block whose (family, shade) equals the winning key (or the eye pixels, for an eye-won block). Decode them as `n = rgb/255*2-1`, average them, and renormalize. If the mean is shorter than 0.3, opposite normals cancelled, so use the most common quantized normal instead. Then snap to a 17-direction set: facing, plus 8 at about 45 degrees and 8 at about 70 degrees. This method is reasoned in the notes, not taken from a published pipeline. It works because colour and normal then always describe the same surface, while whole-block averaging blends the arm into the torso and invents bevels at every silhouette.

Quantization does two jobs. It gives cel-like facets under light, and it removes the 1/255 jitter that would otherwise shimmer between animation frames. That shimmer is the flicker Dead Cells accepted. Pixels the pixelizer invents (outline, ground shadow) have no source surface. They should get the flat facing normal (128,128,255). Their near-black albedo makes any lighting on them negligible anyway. The ground shadow probably belongs on its own unlit sprite eventually. Finally, `export_anim.py` crops every frame with one union box so the ground line holds across clips (`tools/art/export_anim.py`, lines 5 to 9). The normal frame has to go through the identical crop, or every frame will be lit one offset away.

## The Compatibility renderer and baked shading reshape the Godot side

The documented 2D lighting stack is small. A **CanvasModulate** sets the ambient base, without which lights only brighten an already full-bright scene. **PointLight2D** and **DirectionalLight2D** add light, and a **CanvasTexture** on the sprite's texture slot holds diffuse, normal and specular maps. Each light's **Height** must be raised, because normal-mapped surfaces look weak at the near-zero default. DirectionalLight2D Height runs from 0 (grazing) to 1 (straight on) ([Godot docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)). Defining `light()` in a canvas_item shader replaces the built-in Lambert term. That is where banding goes. The shader gets `NORMAL`, `LIGHT_DIRECTION`, `LIGHT_COLOR`, `LIGHT_ENERGY`, `LIGHT_IS_DIRECTIONAL` and `COLOR` ([Godot docs: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)). Reading the engine source turned up one trap. For a DirectionalLight2D the energy arrives both as `LIGHT_ENERGY` and as `LIGHT_COLOR.a`, and the output is blended as `rgb * LIGHT.a`. The docs' example shader therefore **applies directional energy twice**. Writing `LIGHT.a = 1.0` avoids it ([canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)). The same source mirrors normals for `flip_h`, negative scale and rotation, so mirrored normal maps should not be pre-flipped. It also caps positional lights per item at 15.

Pixel crispness is not automatic. The docs state that Godot computes 2D lighting "at the Viewport's pixel resolution, not at the source texture's texel resolution". Nearest filtering therefore does not make lighting blocky. The documented fix snaps `LIGHT_VERTEX` and `SHADOW_VERTEX` to a pixel grid in `fragment()` ([Godot docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)). This matters here because `project.godot` sets a 320x180 base with stretch mode **canvas_items** and integer scaling. At 1080p, lights are computed on a 1920x1080 grid, 6 window pixels per art pixel. The cleanest answer is to render the battle stage into a **320x180 SubViewport** and upscale it with nearest filtering. Lighting, light height (measured in screen pixels) and any glow then all live on the art grid, and the UI keeps its high-resolution text. The shader snap is the lighter fallback. Its open risk is grid alignment under integer-scale letterboxing.

Glow is where the project's renderer matters most. `project.godot` declares **`gl_compatibility`**. The docs say HDR 2D, the clean way to make only overbright parts bloom, works only on Forward+ and Mobile (Godot 4.2+). They hint that Compatibility has some glow, while an older forum answer says it does not ([Godot docs: environment and post-processing](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html); [r/godot](https://www.reddit.com/r/godot/comments/1gpq1kr/world_environment_glow_effect/)). A 4.2-era report is titled "Makes Everything Glow" ([GitHub #86098](https://github.com/godotengine/godot/issues/86098)). Even on Forward+, canvas_items glow would be smooth at window resolution and would fight the pixel look. The first slice should skip post-process bloom and build glow from pixels. The visor pixels are drawn as an **unshaded** child sprite, so CanvasModulate cannot dim them; lit items are multiplied by CanvasModulate after `fragment()`, which is why emission inside the lit shader gets darkened. A one-pixel dilated halo goes on an **additive, unshaded** sprite. A small **teal PointLight2D** at the visor throws real, normal-mapped light onto the head and shoulder plates. That last piece is what reads as "modern", and it works in any renderer. Switching to Forward+ for HDR 2D glow stays a later, separate experiment.

The second project fact is about taste rather than API. The colour render bakes a studio key light from the upper left plus cast shadows "as Legacy sprites are lit". The pixelizer then assigns Preston's palette ramp **by brightness rank** to match his picked sprite's shade distribution (`sprite-renderer-snapshot.py`, lines 112 to 116; `pixelize_render.py`, lines 26 to 64). Flattening the albedo the Dead Cells way would leave every pixel of a material tied in brightness and break that ranking. Lighting the baked sprite at full strength double-shades it. The slice therefore keeps the approved baked sprite as diffuse, holds CanvasModulate high (about 0.6 to 0.75), keeps the key light modest (energy about 0.3 to 0.5), and **aims the key light from the upper left so it agrees with the bake**. The dramatic light is left to transient sources: hit flashes, the visor, and a rim. A flat-albedo pixelizer mode is the second experiment, compared side by side.

## Conclusion

The research changes where the effort should go. The normal-map plumbing is nearly solved: one extra Workbench pass with three toggled settings, and a dozen lines inside a loop that already exists. Taste and the renderer are the open risks. The project's own pixelizer turns baked light into Preston's palette, so "lit pixel art" here means layering runtime light onto a look he already approved, not replacing it. That makes the stage half (hit flashes, visor spill, hue shifts, a rim) worth more per hour than perfecting the sprite's self-shading. It is also the half Octopath and SRW players point to.

The second implication is procedural. Every claim about Godot's 2D light math was read from the Forward+/Mobile shader, and this project ships on Compatibility. The first two hours of the slice should therefore be checks, not tuning. A flipped sprite, a doubled energy value and a 360-degree light sweep will each confirm or overturn a source reading in under a minute.

## First-slice recipe: the gorilla lighting slice

**Step 1, Blender (in `tools/blender/render_sprite_views.py`, inside the per-view loop, after the `_id` render).** Output `<view>_n.png`.

| Setting | Value for the normal pass | Then restore for the next colour pass |
|---|---|---|
| `scene.display.shading.light` | `'MATCAP'` | `'STUDIO'` (the loop already resets it) |
| `scene.display.shading.studio_light` | `'check_normal+y.exr'` | set in MATCAP mode only |
| `shading.color_type` / `single_color` | `'SINGLE'` / `(1, 1, 1)` | `COLOR_TYPE` (loop resets it) |
| `shading.show_shadows` | `False` | `True` (colour pass uses it) |
| `show_cavity`, `show_specular_highlight`, `show_object_outline`, `show_xray` | all `False` | unchanged |
| `scene.display.render_aa` | `'OFF'` | the value saved before the pass |
| `view_settings.view_transform` / `look` / `exposure` / `gamma` | `'Standard'` / `'None'` / `0` / `1` | already Standard |
| `render.film_transparent` | `True` | already True |
| Output | PNG, RGBA, 8-bit, `<view>_n.png` | unchanged |
| Camera, resolution, frame, pose | untouched (same as colour) | not applicable |

**Step 2, downsampling rule (in `tools/art/pixelize_render.py`, inside the block loop at lines 133 onward).** If `<name>_n.png` exists, then for each output pixel, use the same `y0:y1, x0:x1` block. Mask = opaque source pixels whose (family, shade) equals the block's winning key, or the eye pixels if an eye won. Compute `v = mean(rgb/255*2-1)` over the mask. If `|v| < 0.3`, use the most common quantized normal in the mask; otherwise set `v /= |v|`. Snap `v` to the nearest of 17 directions by maximum dot product. Encode as `round((v*0.5+0.5)*255)`. Outline and ground-shadow pixels get (128,128,255). Copy alpha exactly from the colour output. Write `<out>_n.png`. Also write the emissive frame `<out>_e.png`: the final pixels in the eye family, everything else transparent. In `export_anim.py`, apply the identical crop to `_n` and `_e` and write `<k>_n.png` and `<k>_e.png`.

**Step 3, Godot import.** Diffuse, `_n` and `_e` PNGs: Compress Mode **Lossless**, Mipmaps **off**, Normal Map hint **Disabled** (no RGTC or VRAM compression on the normals).

**Step 4, project settings.** Keep what `project.godot` already has: 320x180, `stretch/mode="canvas_items"`, `scale_mode="integer"`, `default_texture_filter=0` (Nearest), `gl_compatibility`. Add nothing project-wide. The SubViewport carries the snapping.

**Step 5, scene tree (battle stage).**

| Node | Key properties |
|---|---|
| `SubViewportContainer` | `stretch = true`, `texture_filter = Nearest`, size 320x180 |
| └ `SubViewport` | size 320x180, `snap_2d_transforms_to_pixel = true`, `snap_2d_vertices_to_pixel = true`, `canvas_item_default_texture_filter = Nearest` |
|   ├ `CanvasModulate` | cool grey, about (0.6 to 0.75, 0.62 to 0.77, 0.7 to 0.85) |
|   ├ `Gorilla` (`Sprite2D`) | `texture = CanvasTexture(diffuse_texture, normal_texture)`, `material = ShaderMaterial(banded_light.gdshader)`; a script swaps both textures per frame from `anim.json` |
|   │ ├ `Visor` (`Sprite2D`) | `_e` frame; `CanvasItemMaterial.light_mode = Unshaded`; `self_modulate` stepped through 2 to 3 brightness values |
|   │ ├ `VisorHalo` (`Sprite2D`) | eye mask dilated 1 px minus the mask, darker teal, about 50% alpha; `blend_mode = Add`, `light_mode = Unshaded` |
|   │ └ `VisorLight` (`PointLight2D`) | teal; energy 0.4 to 0.8; `height` 4 to 10 px; texture = radial `GradientTexture2D` (white to transparent white, 64x64); radius about 20 to 30 art px |
|   ├ `KeyLight` (`DirectionalLight2D`) | aimed down-right (from the upper left, matching the bake); `height` 0.5 to 0.7; energy 0.3 to 0.5; warm white |
|   ├ `RimLight` (`PointLight2D`) | behind and right of the mech; `height` 2 to 6 px so it grazes; cool blue; energy 0.3 to 0.6 |
|   └ `HitFlash` (`PointLight2D`) | at the impact point; `height` 16 to 32 px; energy keyed 0, 1.5, 0.8, 0 on consecutive frames with discrete update mode |
| `CanvasLayer` (UI) | outside the SubViewport, keeps crisp canvas_items text |

**Step 6, `banded_light.gdshader` (untested starting point).**

```glsl
shader_type canvas_item;

uniform float bands : hint_range(1.0, 8.0, 1.0) = 3.0;

void light() {
    float ndl = max(dot(NORMAL, LIGHT_DIRECTION), 0.0);
    float falloff = LIGHT_IS_DIRECTIONAL ? 1.0 : LIGHT_COLOR.a; // point-light texture alpha
    float i = ndl * falloff * LIGHT_ENERGY;
    i = floor(i * bands + 0.5) / bands;                      // 3 hard steps
    LIGHT = vec4(LIGHT_COLOR.rgb * COLOR.rgb * i, 1.0);      // alpha 1.0: no double energy
}
```

Fallback if the SubViewport is rejected: add `uniform float px = 6.0;` set from script to the window-to-art scale, and `void fragment() { LIGHT_VERTEX.xy = floor(LIGHT_VERTEX.xy / px) * px; SHADOW_VERTEX = floor(SHADOW_VERTEX / px) * px; }`.

**Step 7, acceptance checks, cheapest first.**

| Check | Pass condition |
|---|---|
| Sphere matcap check, using the gorilla script's exact shading state (including the -20 degree studio rotation) | centre pixel within 2/255 of (128,128,255); top of the sphere is green-high |
| Colour render unchanged by the new pass | `e.png` byte-identical before and after the edit |
| Alignment | alpha of `e_px.png` equals alpha of `e_px_n.png` at every pixel (assert in the pixelizer) |
| Light sweep (DirectionalLight2D rotated 360 degrees) | every art pixel shows one flat value at any moment; the bright side follows the light |
| Flip test | `flip_h` gorilla lit from the left is bright on the left |
| Energy test | directional energy 0.5 vs 1.0 doubles the lit increment, not quadruples it |
| Taste | side-by-side screenshot of the baked-only sprite vs the lit sprite vs Preston's original, for his call |

## What is unverified

| Item | Why it is open | How to close it |
|---|---|---|
| Compatibility (GLES3) canvas shader behaviour | All engine-source readings (normal Y decode, `flip_h` mirroring, `LIGHT_COLOR.a` vs `LIGHT_ENERGY`, 15-light cap) came from the Forward+/Mobile shader on master, not the 4.7 Compatibility shader | Flip test and energy test above; read `drivers/gles3/shaders/canvas.glsl` at the 4.7 tag |
| `banded_light.gdshader` | Never compiled or run | Load it on the gorilla in 4.7 |
| `LIGHT_VERTEX` / `SHADOW_VERTEX` in Compatibility | Documented generally, not confirmed for this renderer | Only needed for the fallback |
| Glow in Compatibility, HDR 2D | Docs imply some glow exists in Compatibility; a 2024 forum post says none; HDR 2D is Forward+/Mobile only | Not needed for the slice; test separately if bloom is wanted |
| SubViewport property names and nearest upscale under canvas_items stretch | General knowledge, not read in 4.7 docs | Light sweep check |
| Per-frame texture swapping on one CanvasTexture vs `AnimatedSprite2D` with CanvasTexture frames vs `AtlasTexture` wrapping a CanvasTexture | Only the first is near-certain; the other two were not checked | Use the swap; test the others only if needed |
| Matcap under the script's -20 degree studio rotation, and whether setting `studio_light` in MATCAP mode leaves the STUDIO choice intact | Tested only on a sphere with defaults | Sphere check and byte-compare above |
| Masked-average plus 17-direction normal downsample | Reasoned; no shipped pipeline publishes one | Visual check for shimmer across a walk cycle, quantize on vs off |
| Whether runtime light on the baked sprite reads well | Taste; double shading may posterize | Preston's side-by-side call; flat-albedo pixelizer mode as the comparison |
| Texture import option names in 4.7 (Lossless, mipmaps, Normal Map hint) | General knowledge | Check the Import dock |
| Godot 4.5 to 4.7 release notes for 2D lighting or glow changes | Not checked | Skim the changelogs |
| Octopath sprite normals, Sea of Stars technique, Brigador posters' developer status | Not found or not verifiable in sources read | None needed for the slice |
| Dead Cells band count, light count, normal filtering | Not published in the article | None; treat as craft knowledge |
| Live `render_sprite_views.py` matching the 2026-10-13 snapshot that was read | Only the snapshot was read | Diff before editing |
