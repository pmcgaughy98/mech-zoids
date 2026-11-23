# MOBA look study: how SMITE and Paragon make 3D characters read (2026-11-09)

Look lane. Brief from Preston: "hooks our visuals, shaders, textures for our models to look on a level that'd be
competitive with Mobas especially like smite or paragon." Study only: no SMITE or Paragon mesh, texture, shader or
animation is in the project. Reference files stay in `D:\dev\_scratch\moba-look\` and the 2026-11-08 SMITE scratch.

Note on location: this doc was written in the look lane's worktree because the worktree guard blocks writes to the
main checkout. The code and video are in the main checkout (`D:\dev\new-mech-rpg`), listed under "First slice".

**Press play:** `D:\dev\new-mech-rpg\docs\art\moba\look\moba_look_v1_before_after_2026-11-09.mp4` (20 s: side by
side, then before, then after). Still: `before_after_zoom.jpg` in the same folder.

## Stock-take (what was on hand, what each did)

| Tool | Used for | Result |
| --- | --- | --- |
| SMITE install + 2026-11-08 UModel exports | Albedo of Hun Batz and Raijin, measured | Used. Only 64 px mips exported (TFC cache missing): fine for colour stats, not for detail |
| Steam store API (SMITE 386360, Predecessor 961200) | 4 gameplay frames each, measured | Used. 386360 is now the SMITE 2 page (UE5); Predecessor is the successor built on Paragon's released assets, so it stands in for Paragon |
| Firecrawl search | Primary talks | Used: found Hi-Rez's "Art of SMITE" panel and Epic's Paragon lighting talk |
| yt-dlp transcript (the watch skill's route) | Art of SMITE panel | Used. The Paragon lighting talk hit HTTP 429 twice, not read |
| Python + PIL | Frame and albedo stats, body hue check | Used: `albedo_stats.py`, `frame_stats.py` in scratch |
| Godot 4.7.2 Movie Maker + ffmpeg | Before/after recording at the game camera | Used |
| Blender MCP, atlas-texturing, blender-export-pipeline | Texture or GLB edits | Not used on purpose: the textures measure in range already, so the fix is in Godot, and the GLBs belong to the gorilla and rhino lanes |
| atlas-godot, shader-basics skills | Shader patterns | Not opened this pass; next_pass fresnel and inverted hull from general knowledge |
| Paid generators | none | Nothing paid ran |

## What was read

- **Read:** "The Art of SMITE", Hi-Rez Expo 2019 panel (youtube.com/watch?v=Hvh29zoc2ac), transcript. The useful part
  for us: the team turns characters all black to judge silhouettes, because in game the silhouette is what comes at
  you. They also line every god up in one scene in idle pose to compare height and build.
- **Read (measured):** SMITE albedo textures (2), SMITE 2 store frames (4 gameplay), Predecessor store frames (3
  gameplay with HUD, 1 close).
- **General knowledge, not verified this pass:** Paragon (2016 to 2018) used UE4 physically based shading with a
  cinematic grade and filmic tonemapping; readability came from rim and silhouette, not ink lines. SMITE and Paragon
  show team mostly through health bar colour, with an enemy highlight outline on target or hover. Epic's "Paragon
  Feature Examples: Cinematic Lighting and Rendering" (youtube.com/watch?v=22jvxFoTHBk) is the source to read next.

## Measurements (centre crop, HUD trimmed)

| Frame set | Brightness p50 | Spread p5 to p95 | Saturation p50 | Near-black share |
| --- | ---: | ---: | ---: | ---: |
| SMITE 2, 4 frames (median) | 0.34 | 0.66 | 0.34 | 0.01 |
| Predecessor, 4 frames (median) | 0.25 | 0.55 | 0.49 | 0.02 |
| **Ours before** (arena as it is) | 0.20 | 0.47 | 0.37 | 0.09 |
| **Ours after** (look v1) | 0.27 | 0.54 | 0.37 | 0.07 |

Albedo (the texture itself, before lighting):

| Texture | Saturation p50 | Brightness p50 |
| --- | ---: | ---: |
| SMITE Hun Batz | 0.66 | 0.34 |
| SMITE Raijin | 0.68 | 0.29 |
| Our gorilla atlas | 0.77 | 0.34 |

**The finding:** our textures already sit in SMITE's colour range. The gap is the render. The arena runs a linear
tonemap (`tonemap_mode = 0`), a flat 0.9 ambient, no AO and no rim, so the gorilla's body rendered at brightness 0.14:
dark green plates that merge into one blob at game distance. After the grade the body reads at 0.29 with the same hue
(148 vs 150 degrees).

## Targets (drafts to keep checking against)

- Frame brightness p50 **0.25 to 0.34**; spread **0.55 to 0.66**; near-black share **under 0.05** (we are at 0.07).
- Frame saturation p50 **0.34 to 0.49**; the mech's own albedo saturation 0.6 to 0.8.
- Mech body brightness at the game camera **0.28 to 0.40**.
- Silhouette: passes an all-black lineup test (SMITE's method). Still to build.
- Team read: one cue that works at 10 m, kept separate from faction colour (the gorilla stays green on either team).

## Proposal (nothing here is canon)

1. **Grade, per map:** Filmic tonemap, exposure 1.25, SSAO for contact, glow only above HDR 1.05 so emissive eyes and
   shield cores bloom and nothing else. ACES was tried first: at the exposure it needed it pushed brightness spread past
   both references. Alternative: AgX, untested.
2. **Rim on every mech:** a thin fresnel on the material's next_pass, biased to upward edges (power 4, strength 0.5).
   At power 2.2 / strength 1.0 it coated the faceted plates and turned the gorilla pale, so it stays thin.
   Alternative: a camera-relative back light, which costs more and lights the floor too.
3. **Team read:** enemies get a warm red rim plus a thin red outline (constant width on screen). Allies get a cool rim
   and no outline. Alternatives: outline only on the targeted enemy (closer to SMITE), or a team-coloured ground ring.
4. **Textures:** no change now. Later, if wanted: roughness breakup on the plates (Paragon leans on specular
   variation). That is a Blender job for the model lanes.

## First slice (built, in the main checkout)

- `scripts/moba3d/mech_look.gd`: `apply_model(root, enemy)` duplicates each surface material (GLB untouched) and
  chains the rim, plus the outline for enemies, through `next_pass`; `grade(env)` returns a graded copy.
- `shaders/look/mech_rim.gdshader`, `shaders/look/mech_outline.gdshader`.
- `tools/debug/moba_look_v1.tscn` + `.gd`: the gorilla at the v22 game camera (behind, 6.2 m, 15 degrees) with an
  enemy gorilla ahead; walk, slam, idle, 6.6 s. Run windowed:
  `--path . res://tools/debug/moba_look_v1.tscn -- --look=after` (or `--look=before`).
- Not touched: `arena_blockout.tscn` (map lane; the grade is a runtime copy), the GLBs, `material_overlay` (hex
  shield, hit flash), shared match code.

## What still falls short

- Rim and outline add a pass on each of 119 surfaces per gorilla. Fine for a test; measure frame cost before 10 mechs.
- The outline gaps at hard-edged normals on some plates (visible on the enemy's arms).
- The rhino has not been run through it. No silhouette lineup yet.
- Only store stills were measured, not live SMITE play at our exact camera.

## Round 2 (2026-11-09, after Preston's "approved")

**Press play:** `docs/art/moba/look/moba_look_v2_gorilla_rhino_2026-11-09.mp4` (20 s: a 2x2 grid of gorilla and rhino,
before on the left, after on the right; then each "after" full size). Still: `docs/art/moba/look/v2_before_after_zoom.jpg`.
Scene: `tools/debug/moba_look_v2.tscn -- --mech=gorilla|rhino --look=before|after`.

**Rhino.** Its albedo is twice as bright as SMITE's and the gorilla's (value p50 0.68 vs 0.29 to 0.34), so the grade
that lifts the gorilla pushed the rhino body to 0.48. `apply_model()` now takes an `albedo_scale`; the test uses 0.7 on
the rhino (0.55 went brown). Proposal for the rhino lane: darken the texture's base colour about 30% in Blender so no
runtime trim is needed. Their call: by eye the trimmed rhino reads copper rather than gold.

**Colour.** The Filmic curve drained the mech bodies (gorilla saturation 0.84 to 0.54). Saturation 1.3 in the grade puts
them back to 0.61 (gorilla) and 0.64 (rhino), with the whole frame at 0.41, still inside 0.34 to 0.49. The ally rim is
now near-neutral (0.92, 0.94, 1.0): the v1 cool blue greyed warm colours.

| At the game camera | Body value p50 | Body saturation p50 | Frame brightness p50 | Frame saturation p50 |
| --- | ---: | ---: | ---: | ---: |
| Gorilla before | 0.14 | 0.84 | 0.20 | 0.37 |
| Gorilla after v2 | 0.29 | 0.61 | 0.26 | 0.42 |
| Rhino before | 0.30 | 0.88 | 0.21 | 0.37 |
| Rhino after v2 | 0.37 | 0.64 | 0.26 | 0.41 |

**Outline gaps.** Two causes. (1) Hard plate edges are split vertices, so the hull tore at corners: `smooth_outline_mesh()`
now bakes an averaged normal into CUSTOM0, stored relative to each vertex's normal and tangent so it bends with the
bones (cached per mesh, GLB untouched). (2) At 0.0022 of view distance the line was about 1 px and broke into dots;
now 0.0034 (about 2 px). The outer silhouette is solid. Still showing: inner lines where separate parts' hulls overlap.
If that reads as noise, the next route is a stencil-based outer-only outline (Godot 4.5+ stencil), untested.

**Frame cost** (`tools/debug/moba_look_cost_v1.tscn`, 10 mechs: 5 gorillas, 5 rhinos, half enemies, vsync off, 300
frames, 4 runs each). The machine was busy (Chrome, Spotify, other lanes), so single runs swing 4 to 9 ms; read the medians.

| Mode | Draw calls | GPU ms, median of 4 | Runs |
| --- | ---: | ---: | --- |
| Base (arena as it is) | 2,021 | 20.7 | 25.5, 18.8, 16.8, 22.6 |
| Grade only | 2,021 | 18.4 | 18.1, 21.2, 16.9, 18.6 |
| Grade + rim + outline | 3,708 | 23.6 | 19.5, 25.3, 30.8, 21.9 |

The grade costs nothing measurable. Rim and outline add about 5 ms and 83% more draw calls, because each is a pass
per surface and the gorilla has 119 surfaces (rhino 56). The cheapest fix sits with the model lanes: merge each mech to a
handful of surfaces (one atlas material for the body), which cuts the base cost too. Until then, an option is the rim
only on enemies plus the player, or the outline only on the targeted enemy.

**Not done.** The arena grade waits on the map lane (asked, no reply yet). Near-black share is 0.077, above the 0.05
target: it is the arena's dark walls, the map lane's area.

## Round 3 (2026-11-09): the look at a playable cost

**Press play:** `docs/art/moba/look/moba_look_v3_gorilla_rhino_2026-11-09.mp4` (same layout as round 2). Still:
`v3_before_after_zoom.jpg`. Scene: `tools/debug/moba_look_v3.tscn -- --mech=gorilla|rhino --look=before|after`.

**Why.** The map lane measured round 2 on a GTX 1660 Super (gl_compatibility, six gorillas, 3v3): 13.7 ms base, 31.0 ms
with rim and outline as next_pass on every surface. That is about 70 fps down to 32.

**What changed.**
- `shaders/look/mech_body.gdshader`: the body material with the rim built into emission. `apply_model()` now swaps
  each StandardMaterial3D for it, one for one, copying albedo, metallic/roughness (glTF G/B channels), emission and
  double-sided. It covers exactly the features the two GLBs use (dumped from both). So the rim costs no extra draw.
  Materials are shared per source material and team.
- Outline: `set_outline(root, on)`, meant for the targeted or hovered enemy only (SMITE's way, and the map lane's
  first pick). `apply_model(..., outline=true)` turns it on at spawn.
- Grade: SSAO off. The map lane measured it changing 0.69% of pixels in this renderer.
- A correction to round 2: the extra additive rim pass was also adding the arena fog over the whole body, a pale haze
  that lifted and desaturated it. The saturation 1.3 boost was partly compensating. With the rim in the material the
  haze is gone, so the grade went back to saturation 1.1 and exposure moved 1.25 to 1.45.

| At the game camera | Body value p50 | Body saturation p50 |
| --- | ---: | ---: |
| Gorilla before | 0.14 | 0.84 |
| Gorilla v3 | 0.22 | 0.74 |
| Rhino before | 0.30 | 0.88 |
| Rhino v3 (albedo trim 0.7) | 0.30 | 0.76 |

Frame: brightness 0.28, spread 0.56, saturation 0.36, all inside the SMITE 2 / Predecessor bands. The gorilla body is
still under the 0.28 target. Lifting it with exposure would brighten the whole frame, so that is left for the texture.
Near-black share 0.074 (the arena's walls).

**Cost** (the map lane's benchmark, copied to `D:\dev\_scratch\moba-look\v3\look_cost_v3.gd`; GTX 1660 Super, six
gorillas, 500 frames; 2 runs x 2 reps; logs: `docs/art/moba/look/look_cost_v3_run*.txt`):

| Mode | Draws | Frame median, ms (4 reps) | Median |
| --- | ---: | --- | ---: |
| Base | 1,684 | 15.8, 15.6, 15.9, 15.2 | 15.7 |
| Grade | 1,684 | 13.6, 14.8, 15.8, 15.0 | 14.9 |
| Grade + rim in material | 1,684 | 13.9, 23.1, 16.5, 16.9 | 16.7 |
| + outline on one targeted enemy | 1,922 | 19.8, 21.9, 17.6, 17.7 | 18.8 |

Round 2 was +126% on the base; v3 with a target outline is about +20% (about 64 to 53 fps). One rep (23.1) had other
GPU load. One outlined gorilla still costs about 1 to 2 ms for 238 draws. Each extra pass of a skinned mesh is
expensive in this renderer, so merging surfaces (gorilla-3d, rhino-3d) is still the bigger lever.

**Still open.** Where the rim and outline get applied in matches belongs to arena_play / match_director (game feel lane).
"Enemy" has to mean relative to the local player, and all-bot sims have none. The grade goes into the arena's theme
table (map lane, agreed), after Preston confirms the map's re-texture scope.

## Round 4 (2026-11-10): Codex's finish folded into the shared mech shader

Preston picked folding the Codex art-direction gorilla finish ("refined D", `docs/art/moba/art-direction-2026-11-07/
gorilla-polish-v1/`) into `shaders/look/mech_body.gdshader`, so there is one mech material, not two competing ones.
- New uniforms `finish` (0 = plain v3, 1 = on, default 1) and `steel_min`. Masks come from the albedo colour, as in
  Codex's pass: painted armour matte (metal 0.12, rough 0.64), light neutral hardware polished (0.78 / 0.36), dark
  neutral mechanisms darker and rough (albedo x0.87, 0.42 / 0.70), lime power panels toned (albedo x0.72, small glow).
- Left out on purpose: Codex's albedo x1.13 lift (the v3 grade already brightens) and toon diffuse (v3 is Burley).
- Measured at the game camera: frame brightness 0.29 / spread 0.56 / saturation 0.35 for the gorilla, unchanged
  from v3 and inside the targets; the rhino reads 0.285 / 0.557 / 0.356. The rhino is bronze, not grey, so the steel
  mask does not chrome it. Board: `docs/art/moba/look/finish_v4_compare_2026-11-10.jpg`.
- Still guesses: the masks are colour rules, not a painted ID map (Codex said the same).

## Round 5 (2026-11-11): shared effects no longer pixel art

Preston (via the rhino effects lane): "we don't want it too look like pixel art". Three shared pieces replaced:
- Team ring and shadow under every unit: art/field/moba3d/ring.png and shadow.png redrawn as smooth 512 px
  textures, linear filtering with mipmaps (field_test.tscn, arena_blockout.tscn). Originals kept in
  D:/dev/_scratch/moba-look/smooth-fx/originals/.
- Fx3D hit_spark and deflect_spark: shaders/look/fx_spark.gdshader (HDR core that blooms, thin rays, a shock ring).
- Fx3D stun_loop: shaders/look/fx_star.gdshader, three gold stars circling.
- Hook: scripts/moba3d/fx3d.gd keeps its sprite as an invisible carrier and parents scripts/moba3d/look_fx.gd, so no
  kit code changed. look_fx.gd is loaded by preload, not class_name (a new global class broke parsing until an
  editor rescan).
- Pitfalls hit: an additive shader must write ALPHA or it is drawn opaque; additive quads need fog_disabled or the
  scene fog paints a pale square over whatever is behind them.
- Board and video: docs/art/moba/look/fx_pixel_vs_smooth_2026-11-11.jpg / .mp4 (left pixel, right smooth).

Hippo r10 (dark window glass): body value 0.37, saturation 0.77, the same as r9. Passes.

Rhino v52 (registered, art/arena_models/rhino.glb), no runtime trim: body value 0.357, saturation 0.79, steady across
idle and attack frames. The 0.7 albedo trim (only ever used by the look test scene for v38; the game passes 1.0)
is gone: the test scene's "rhino" entry now loads the registered v52 at 1.0.
- From the kangaroo effects lane (2026-11-11), gl_compatibility only: a screen pass reading hint_depth_texture must
  remap depth (ndc.z = d * 2.0 - 1.0) before INV_PROJECTION_MATRIX, and blend_mul drew the whole screen black; use a
  blend_mix veil with ALPHA instead (shaders/kangaroo_bout_dim.gdshader).

## 2026-11-12: registered models re-measured
- Rhino (arena rhino.glb, sha f3c87b06, re-saved 11-11 18:03): body value 0.357, saturation 0.79. Unchanged, passes.
- Merged gorilla (arena gorilla.glb, sha d09ce128): green body value 0.19 (target 0.28 to 0.40), saturation 0.58
  (target 0.6 to 0.8). Darker than the v26 kit measured in round 3 (0.22). Reads as deep green at game distance,
  but under target. It also arrives as 122 surfaces per mech (12 materials), which costs draw calls in a
  ten-mech match. Measure script for green bodies: D:/dev/_scratch/moba-look/v4/body_value_green.py.

## 2026-11-13: hippo r12 (touch-up) re-measured
- Arena hippo.glb sha ba76c29b: body value 0.373, saturation 0.76 at 3.5 s (r10 was 0.369 and 0.77). Passes. Frame lum p50 0.289, unchanged.
- The red pixels left in the crop are the enemy target outline, not the body. Board: D:/dev/_scratch/moba-look/v4/hippo10_vs_12.jpg. Script: body_value_purple.py.
- moba_look_v3 now takes --model=<absolute GLB path> to measure any scratch candidate with an existing entry's clips.

## 2026-11-17: Unreal paleness (row 19c), cause is auto-exposure
- In Unreal every mech read paler than Godot. On the cobra plate (Godot review render 45,117,74), Unreal with auto-exposure gave about (110,186,127).
- Manual exposure on the trial map (one unbound post-process volume): bias 0 gave (25,81,40), +1.0 gave (40,111,58), and +1.2 gave (46,118,64). Red and green match, and blue is about 10 low (the colour finish).
- The map was left restored. A ready copy with the volume at +1.2 is at D:/dev/_scratch/moba-look/unreal-19c/TrialMap.bias1.2.umap. Applying it is Preston's call. Scripts: set_exposure.py, run_19c.ps1, measure.py. Board: row19c_before_after_godot.jpg.
