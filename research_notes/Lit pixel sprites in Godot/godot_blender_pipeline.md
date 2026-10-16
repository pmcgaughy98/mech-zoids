# Lit pixel sprites: Blender 5.x normal renders to Godot 4.7 2D lighting

Evidence key used below:
- **[Docs]/[Source]**: read this session at the URL given.
- **Local test**: run headless this session in Blender 5.2.2 LTS (`blender -b --factory-startup`) on a smooth UV sphere, 64x64 px, orthographic camera at (0,-5,0) looking along +Y (so world space and camera space differ). Scripts are saved in `D:\dev\new-mech-rpg\research_notes\Lit pixel sprites in Godot\blender_normal_tests\` (`nm_test.py`, `nm_pass_test.py`, `read_parts.py`).
- **General knowledge**: not read in a source this session; treat as unverified until checked in the editor.

## 1. Blender: getting a normal map aligned pixel-for-pixel with each colour render

### Takeaway
Use a second Workbench render of the same camera with the bundled `check_normal+y.exr` matcap, the **Standard** view transform (not Raw, not the AgX default), white single colour and AA off. A local test shows this gives a correct camera-space, Y-up (OpenGL-style) normal map within about 1.4/255 of the analytic answer. The Cycles/EEVEE Normal pass also works but is **world space** and must be rotated into camera space by script.

### Cited Findings
- Blender 5.2.2 ships exactly one normal matcap, `check_normal+y.exr` (512x512, RGB float). Its centre texel is (0.2158, 0.2133, 1.0), which is the sRGB-to-linear value of 0.5. The file is pre-linearized so that an sRGB display transform writes n*0.5+0.5. Local test (`nm_test.py`).
- Working settings (all accepted without error in 5.2.2): `scene.render.engine = 'BLENDER_WORKBENCH'`; `scene.display.shading.light = 'MATCAP'`; `scene.display.shading.studio_light = 'check_normal+y.exr'`; `scene.display.shading.color_type = 'SINGLE'`; `scene.display.shading.single_color = (1,1,1)`; `show_cavity`, `show_shadows`, `show_object_outline`, `show_specular_highlight`, `show_xray` all False; `scene.display.render_aa = 'OFF'`; `scene.render.film_transparent = True`; `scene.view_settings.view_transform = 'Standard'`, `look = 'None'`, `exposure = 0`, `gamma = 1`; PNG, RGBA, 8-bit. Local test.
- Result with those settings: mean abs error 1.36/255 against the ideal camera-space encoding. Centre pixel (129,129,255); a point at x=+0.69 gave (213,129,223) vs ideal (213,130,222); a point at y=+0.69 (screen up) gave (130,213,223) vs ideal (130,213,222). Green rises toward the top of the image, so the output is **Y+ up (OpenGL convention)**. Local test.
- Pitfall: Blender 5.2.2 factory default view transform is **AgX**; rendering the matcap under AgX gives centre (134,144,202), error 24.6/255. Local test.
- Pitfall: the **Raw** view transform is wrong for this matcap (centre (56,56,255), error 48.8/255) because the EXR is pre-linearized and expects Standard. Local test.
- Pitfall: `single_color` defaults to (0.8,0.8,0.8) and the matcap is multiplied by it, giving centre (117,117,231), error 15.7/255. Set it to white. Local test.
- With `render_aa = 'OFF'` and transparent film the alpha channel contained only 0.0 and 1.0 (hard silhouette, no fringe pixels). Local test.
- Cycles and EEVEE Normal pass in Blender 5.2.2 are **world space**: with the camera looking along +Y the camera-facing centre read (0.017, -1.0, -0.017), the screen-up point read world +Z (0.017, -0.742, 0.67) and the screen-right point read world +X (0.671, -0.742, -0.017). Same result for both engines. Local test (`nm_pass_test.py`, `read_parts.py`).
- Blender 5.2.2 writes multilayer EXR as **multi-part** files: `ViewLayer.Combined`, `ViewLayer.Depth`, `ViewLayer.Normal` (channels X,Y,Z) are separate parts. A reader that opens only part 0 sees only Combined (this first fooled the test). Local test.
- Engine enum in 5.2.2 is ('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES'); `'BLENDER_EEVEE_NEXT'` (the 4.2 to 4.x name) is rejected. Local test.
- Godot decodes 2D normal maps as `normal.xy = tex.xy * vec2(2.0, -2.0) - vec2(1.0, -1.0)` in a screen space whose Y points down, so a texture with **green = up** (OpenGL, Y+) is what Godot expects; no green flip is needed for the Blender matcap output. [Source: canvas.glsl, master](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)

### Inferences
- Pixel alignment is automatic if the colour and normal renders use the same camera object, resolution, resolution_percentage, frame and shift values. The only render that differs is lighting mode (`shading.light = 'STUDIO'` or `'FLAT'` for colour, `'MATCAP'` for normals), so a bpy loop can render both per frame by toggling `scene.display.shading.light` and `studio_light` and changing `scene.render.filepath`.
- If the colour render uses AA (`render_aa` other than 'OFF') and the normal render does not, silhouettes differ by fringe pixels. Either render both with AA off, or apply the colour sprite's final alpha to the normal map after pixelization.
- Cycles/EEVEE route, if ever needed (for example to bake normals from a different shading setup): `n_cam = R^T * n_world` with `R = camera.matrix_world.to_3x3().normalized()`; Blender camera space is +X right, +Y up, +Z toward the viewer, so encode `rgb = n_cam * 0.5 + 0.5` and write the array straight to PNG as data (no view transform). Background pixels have a zero normal and should be written as (128,128,255) with alpha 0. The Workbench matcap route avoids all of this and is faster.
- A third Workbench pass (flat lighting, material colours set to white on emissive parts and black elsewhere) would give an emissive mask aligned to the same grid for the glow step in section 5.

### Gaps
- Whether Workbench itself offers a Normal render pass was not settled: the first test read only EXR part 0. Not needed for the matcap route.
- The matcap is a view-space lookup. It was only tested with an orthographic camera (the target case); behaviour with a perspective camera was not tested.

## 2. Downsampling the normal map to the pixelized grid without breaking it

### Takeaway
Do not average all normals in a block blindly. Pick the block's winning colour first (the existing mode step), then build that block's normal only from the high-res pixels that had that winning colour, average them as decoded vectors, renormalize, and optionally snap to a small set of directions. Dead Cells sidestepped downsampling by rendering at final size with no anti-aliasing.

### Cited Findings
- Dead Cells (Motion Twin): a homebrew tool "renders the mesh in a very small size and without antialiasing", and each frame is exported to PNG "along with its normal map", lit in game with a basic toon shader. The artist notes they had not solved flickering pixels. [Game Developer, Thomas Vasseur, "Art Design Deep Dive: Using a 3D pipeline for 2D animation in Dead Cells"](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Godot's built-in 2D path reads only the **R and G** channels and rebuilds Z as `sqrt(max(0, 1 - dot(xy, xy)))`, so the blue channel is ignored and only XY accuracy matters. [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- The normal texture is sampled with the same `uv` and the same sampler as the colour texture, so the normal map must have exactly the same size, frame layout and padding as the colour sheet. [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)

### Inferences
- Recommended per-block algorithm (numpy, one pass alongside the colour mode step):
  1. Decode the high-res normal render: `n = rgb/255 * 2 - 1` (the encoding is linear, verified in section 1).
  2. For each block, the colour step already finds the mode colour; build a mask of pixels in that block whose colour equals the mode (and alpha = 1).
  3. `v = n[mask].mean(axis=0)`; if `|v| < 0.3` fall back to the mode of quantized normals in the mask (opposite normals cancelled); else `v /= |v|`.
  4. Optional quantize (see below), re-encode `rgb = round((v*0.5+0.5)*255)`, alpha = the pixelized colour alpha. Transparent pixels get (128,128,255,0).
  This keeps colour and normal from the same surface. Plain whole-block averaging blends across silhouettes and across overlapping parts (arm over torso), which produces fake bevels and wrong lighting at edges.
- Keeping flat faces flat: a flat face renders as one uniform normal in the high-res image, so the masked average already keeps it exact. Quantization is the extra guard: snap each output normal to the nearest of a small direction set by maximum dot product, for example (0,0,1) plus 8 directions around it at about 45 degrees tilt (and optionally 8 more at about 70 degrees). This gives cel-like bands under lights and removes 1/255 jitter that causes shimmer between animation frames.
- Alternative: render the normal pass directly at the final low resolution with AA off (the Dead Cells approach). It is simpler but samples the pixel centre, which can disagree with the colour mode winner on mixed blocks.

### Gaps
- No published pipeline was found that uses mode-per-block colour downsampling plus a matching normal downsample; the algorithm above is reasoned, not cited.
- Dead Cells does not publish how its normals were filtered beyond "small size, no antialiasing".

## 3. Godot 4 2D lighting API (target 4.7.2)

### Takeaway
Put the colour sheet and normal sheet into one `CanvasTexture` on the sprite, darken the scene with `CanvasModulate`, light with `PointLight2D`/`DirectionalLight2D`, and raise each light's `height` (normal-mapped surfaces look weak at the default height).

### Cited Findings
- Nodes in a 2D lighting setup: `CanvasModulate` (ambient base colour; without it lights only brighten an already fully lit scene), `PointLight2D`, `DirectionalLight2D`, `LightOccluder2D`, plus receivers such as Sprite2D or TileMapLayer. The background colour receives no light. [Docs: 2D lights and shadows (4.7)](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- PointLight2D inspector properties: Texture (size defines light size), Offset, Texture Scale, Height ("virtual height with regards to normal mapping", default is very close to surfaces, so raise it when using normal maps). A radial `GradientTexture2D` can be used as the light texture. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- DirectionalLight2D: Height from 0.0 (parallel to surfaces, the default) to 1.0 (perpendicular); Height does not affect shadows; Max Distance culls shadow casters; directional shadows are always infinitely long. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- Shader math for DirectionalLight2D: `light_vec = normalize(mix(vec3(direction, 0.0), vec3(0, 0, 1), height))`; for PointLight2D: `light_vec = normalize(vec3(light_position, height) - vec3(fragment_position, 0))`, both in screen space; default diffuse is `max(0, dot(normal, light_vec))` (Lambert). [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- Light2D common properties: Enabled, Editor Only, Color, Energy, Blend Mode (Add default, Subtract, Mix), Range > Z Min/Max, Range > Layer Min/Max, Range > Item Cull Mask. Shadow properties: Enabled, Color, Filter (None is "well suited for games with a pixel art aesthetic"; PCF5, PCF13), Filter Smooth, Item Cull Mask (matched against LightOccluder2D's Occluder Light Mask). [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- CanvasTexture inspector fields: Diffuse > Texture, Normal Map > Texture, Specular > Texture, Specular > Color, Specular > Shininess, Texture > Filter and Texture > Repeat (override the node and the project default `Rendering > Textures > Canvas Textures > Default Texture Filter`). Create it on the node's texture property (for example Sprite2D.texture). Normal and specular maps work on any Node2D or Control. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- Specular is only computed when a specular texture is present (or the shader reads SPECULAR_SHININESS); it is Blinn with a fixed view vector (0,0,1). [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- Order of operations per fragment: the item colour is multiplied by the CanvasModulate colour (`color *= canvas_data.canvas_modulation`, skipped for `unshaded`), then each light is blended (Add: `color.rgb += light.rgb * light.a`). [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- Per item, the positional light count is read from 4 bits (`flags & 15u`, commented "max 15 lights"). [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- Shader render modes `unshaded` (no lighting) and `light_only` (visible only where lit) exist for canvas_item shaders. In Godot 4 all lighting happens in the regular draw pass, not one extra draw per light as in 3.x. [Docs: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
- Additive sprites (CanvasItemMaterial Blend Mode = Add) are a cheaper fake light but ignore normal and specular maps and cast no shadows. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)

### Inferences
- Script property names (general knowledge, match the inspector labels above): `CanvasTexture.diffuse_texture`, `normal_texture`, `specular_texture`, `specular_color`, `specular_shininess`, `texture_filter`, `texture_repeat`; `Light2D.color`, `energy`, `blend_mode`, `range_item_cull_mask`, `range_layer_min/max`, `range_z_min/max`, `shadow_enabled`, `shadow_color`, `shadow_filter`, `shadow_filter_smooth`, `shadow_item_cull_mask`; `PointLight2D.texture`, `texture_scale`, `offset`, `height`; `DirectionalLight2D.height`, `max_distance`; `CanvasItem.light_mask` (what `range_item_cull_mask` is compared against); `CanvasItemMaterial.light_mode` = LIGHT_MODE_NORMAL / LIGHT_MODE_UNSHADED / LIGHT_MODE_LIGHT_ONLY.
- Animation: the most robust setup is one `Sprite2D` with `hframes`/`vframes` and a single CanvasTexture whose diffuse and normal sheets share the identical grid, animated by AnimationPlayer on `frame`. Per-frame `CanvasTexture` resources inside `SpriteFrames` for `AnimatedSprite2D` should work because CanvasTexture is a Texture2D (general knowledge), but this was not verified this session.
- PointLight2D `height` is in screen pixels (it is compared against fragment positions in screen space). In a 320x180 viewport, heights in the tens of pixels are a reasonable starting range; tune by eye.

### Gaps
- Not checked: whether `AtlasTexture` wrapping a CanvasTexture keeps the normal map, and whether AnimatedSprite2D frames that are CanvasTextures light correctly in 4.7.2.
- Whether the C++ side scales PointLight2D `height` by the canvas transform (matters in `canvas_items` stretch mode) was not read.

## 4. Keeping lighting pixel-crisp at 320x180

### Takeaway
Lighting is computed per viewport pixel, not per texel, so Nearest filtering alone does not make light blocky. Use stretch mode `viewport` (lights then run at 320x180 game pixels), or snap `LIGHT_VERTEX`/`SHADOW_VERTEX` in a shader. Add a custom `light()` that bands N·L into a few steps.

### Cited Findings
- "The engine computes 2D lighting and shadows at the Viewport's pixel resolution, not at the source texture's texel resolution"; Nearest filtering "will not" make lighting pixelated; the documented fix is a canvas_item shader that snaps `LIGHT_VERTEX.xy` and `SHADOW_VERTEX` with `floor(v / pixel_size) * pixel_size` in `fragment()`. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- fragment() built-ins: `NORMAL` (inout, read from NORMAL_TEXTURE), `NORMAL_TEXTURE`, `NORMAL_MAP` (out, converts a 0-1 normal texture and overrides NORMAL), `NORMAL_MAP_DEPTH`, `LIGHT_VERTEX` (inout vec3, z is height), `SHADOW_VERTEX` (inout vec2), `SPECULAR_SHININESS`, `TEXTURE_PIXEL_SIZE`. [Docs: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
- light() built-ins: `NORMAL`, `COLOR` (output of fragment), `UV`, `LIGHT_COLOR` (light colour; for PointLight2D multiplied by its texture), `LIGHT_ENERGY`, `LIGHT_POSITION` (screen space, zero for directional), `LIGHT_DIRECTION` (screen space), `LIGHT_IS_DIRECTIONAL`, `LIGHT_VERTEX`, `SPECULAR_SHININESS`, `LIGHT` (inout output), `SHADOW_MODULATE`. Defining light() replaces the built-in light function even if empty. Official example: `float cNdotL = max(0.0, dot(NORMAL, LIGHT_DIRECTION)); LIGHT = vec4(LIGHT_COLOR.rgb * COLOR.rgb * LIGHT_ENERGY * cNdotL, LIGHT_COLOR.a);` [Docs: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
- In the engine source, for PointLight2D the value passed as LIGHT_COLOR is `light_texture_sample.rgb * light_color.rgb` with alpha from the light texture, and LIGHT_ENERGY is the light colour's alpha slot; for DirectionalLight2D the same alpha slot is passed both as `LIGHT_COLOR.a` and as `LIGHT_ENERGY`. The result is then blended as `color.rgb += LIGHT.rgb * LIGHT.a`. [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- Vertex pixel snap: when enabled, vertices are snapped with `floor(vertex + 0.5)` after the canvas transform (screen pixels). [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)

### Inferences
- Banded light shader (described, untested): in light(), compute `ndl = max(dot(NORMAL, LIGHT_DIRECTION), 0.0)`; take `a = LIGHT_IS_DIRECTIONAL ? 1.0 : LIGHT_COLOR.a` (falloff for point lights); `i = ndl * a * LIGHT_ENERGY`; band it with `i = floor(i * bands + 0.5) / bands` (uniform `bands` around 3 to 4); output `LIGHT = vec4(LIGHT_COLOR.rgb * COLOR.rgb * i, 1.0)`. Writing alpha 1.0 matters: if the docs example is copied as-is, a DirectionalLight2D's energy is applied twice (once via LIGHT_ENERGY, once via LIGHT_COLOR.a in the blend), based on the source reading above.
- With stretch mode `canvas_items` at 1920x1080 (6x), add `LIGHT_VERTEX.xy = floor(LIGHT_VERTEX.xy / 6.0) * 6.0` (and the same for SHADOW_VERTEX) so each sprite texel gets one light value; better still, use stretch mode `viewport`, where lighting, glow and snapping all happen on the 320x180 grid and the result is scaled up with nearest sampling.
- Project settings (names are general knowledge): `display/window/size/viewport_width = 320`, `viewport_height = 180`, `display/window/stretch/mode = "viewport"`, `display/window/stretch/scale_mode = "integer"` (believed added in 4.2), `rendering/textures/canvas_textures/default_texture_filter = Nearest`, `rendering/2d/snap/snap_2d_transforms_to_pixel = true`, `rendering/2d/snap/snap_2d_vertices_to_pixel = true`. Godot texture import for both sheets: mipmaps off, Lossless, normal-map hint disabled (VRAM/RGTC compression would alter values).

### Gaps
- The integer scale mode version and the exact snap setting paths were not re-read in the 4.7 docs this session.
- The banded shader was not compiled or run.

## 5. Glow and bloom for emissive parts in 2D

### Takeaway
Use a WorldEnvironment whose Environment has Background mode **Canvas** and glow enabled. For selective glow, enable **Rendering > Viewport > HDR 2D** (Forward+ or Mobile, Godot 4.2+) and push emissive parts above 1.0 with Modulate/Self Modulate or a shader. Emissive overlays should be unshaded, because lit items are multiplied by CanvasModulate.

### Cited Findings
- "Since Godot 4.2, you can enable HDR for 2D rendering when using the Forward+ and Mobile rendering methods." Enable `Rendering > Viewport > HDR 2D` and restart the editor; then control which objects glow with their Modulate or Self Modulate (the Intensity slider in the colour picker). HDR also reduces banding and has a performance cost. [Docs: Environment and post-processing, Using glow in 2D](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html)
- Without HDR 2D: enable glow, set Background mode to Canvas, then lower Glow HDR Threshold so non-overbright pixels glow; put UI under a CanvasLayer and use Background > Canvas Max Layer to choose which layers glow. [Docs: Environment and post-processing](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html)
- Canvas background mode "displays the 2D scene as a background to the 3D scene" and is how environment effects such as glow reach 2D. [Docs: Environment and post-processing](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html)
- With HDR 2D enabled the 2D renderer works in linear colour space; `source_color` is recommended on colour uniforms in canvas_item shaders. [Docs: Environment and post-processing (search excerpt)](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html)
- The Glow Upscale Mode project setting "is only effective when using the Forward+ or Mobile renderers, as Compatibility uses a different glow implementation", which implies Compatibility has glow in 4.7. [Docs: Environment and post-processing](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html); contradicted by an older forum answer saying glow "doesn't work in Compatibility" [Reddit r/godot, 2024](https://www.reddit.com/r/godot/comments/1gpq1kr/world_environment_glow_effect/) (likely outdated).
- A 4.2-era bug report is titled "World Environment Glow Effect - Makes Everything Glow" (HDR 2D enabled). Only the title and snippet were read. [GitHub issue #86098](https://github.com/godotengine/godot/issues/86098)
- Lit items are multiplied by the CanvasModulate colour after fragment() runs, unless the item is unshaded. [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)

### Inferences
- Recommended emissive setup: export an emissive mask from Blender (section 1), and draw emissive parts as a child sprite with `CanvasItemMaterial.light_mode = LIGHT_MODE_UNSHADED` (optionally Blend Mode Add) and `self_modulate` with values above 1.0 (for example 2.0 to 4.0), with HDR 2D on and `glow_hdr_threshold` left at 1.0 so only overbright pixels bloom. Adding emission inside the lit sprite's fragment() gets darkened by CanvasModulate.
- Use Forward+ or Mobile if selective HDR glow is wanted; Compatibility cannot use HDR 2D per the docs.
- With stretch mode `viewport`, glow is computed at 320x180 and upscaled, so the bloom stays blocky (fits pixel art). With `canvas_items` it is smooth at window resolution.
- Likely Environment property names (general knowledge): `background_mode = Environment.BG_CANVAS`, `background_canvas_max_layer`, `glow_enabled`, `glow_hdr_threshold`, `glow_hdr_scale`, `glow_intensity`, `glow_strength`, `glow_bloom`, `glow_blend_mode`, `glow_levels/1..7`.

### Gaps
- The Godot version that added glow to the Compatibility renderer, and whether HDR 2D reached Compatibility after 4.2, were not confirmed.
- Release notes for 4.5, 4.6 and 4.7 were not checked for 2D lighting or glow changes.

## 6. Known pitfalls (flip_h, scaling, per-frame normals)

### Takeaway
On current master the RenderingDevice renderers already correct normals for flip_h/flip_v, transposed rects, rotation and negative scale, so do not pre-flip mirrored normal maps. The Blender-side traps (AgX, Raw, the 0.8 grey default, multi-part EXR) are the likelier sources of wrong lighting.

### Cited Findings
- Normals are multiplied by `sign(src_rect.zw)` (a flipped draw rect negates X or Y), swapped for transposed rects, then rotated by the item's normalized world axes `mat2(normalize(world_x), normalize(world_y))` and the canvas normal transform. A flipped sprite or `scale.x = -1` gets a mirrored X normal, and uniform or integer scale does not change normal direction. [Source: canvas.glsl, master](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl)
- The `NORMAL_MAP` conversion in custom shaders uses the same Y flip as the default path (`normal_map * vec3(2,-2,1) - vec3(1,-1,0)`), so one OpenGL-style map works for both. Docs warn that writing a raw normal texture straight into `NORMAL` "will appear inverted"; use `NORMAL_MAP = texture(NORMAL_TEXTURE, UV).rgb;`. [Source: canvas.glsl](https://raw.githubusercontent.com/godotengine/godot/master/servers/rendering/renderer_rd/shaders/canvas.glsl); [Docs: CanvasItem shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/canvas_item_shader.html)
- After enabling normal maps lights look weaker; raise Height and slightly raise Energy. [Docs: 2D lights and shadows](https://docs.godotengine.org/en/stable/tutorials/2d/2d_lights_and_shadows.html)
- Blender traps (AgX default, Raw wrong, 0.8 grey single colour, multi-part EXR, EEVEE_NEXT enum gone) are listed with numbers in section 1. Local test.

### Inferences
- Per-frame normals: every animation frame needs its own normal render (pose changes the normals), and the normal sheet must be packed with the identical frame grid, since Godot samples both with the same UV.
- Rotating a sprite rotates its normals correctly (the world-axis transform above), so lights stay consistent on rotating parts.

### Gaps
- The `sign(src_rect.zw)` flip handling was read on **master**, not on the 4.7 branch tag, and the Compatibility (GLES3) shader was not read. Check once in 4.7.2: a flipped sprite lit from the left should be bright on the left.
- That Sprite2D.flip_h produces a negative source rect (and so triggers the sign flip) is general knowledge of the canvas renderer, not read this session.
