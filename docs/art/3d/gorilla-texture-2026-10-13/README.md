# Gorilla texture preview, 2026-10-13

Status: separate preview. Preston chose to keep this separate while the other session continues building the gorilla. The finished snapshot and pixel sprites are not installed as the live model or view sprites.

Open `scenes/gorilla_texture_preview.tscn` in Godot and press F6. Q/E turn, O orbits; keys 1-5 play walk, idle, punch, hit and death; 6-8 play slam, throw and gait. The scene reads the immutable `after/ape_l.glb` using GLTFDocument, so the .gdignore does not prevent previewing it.

## Actual sprite preview

`pixel-before-after-4x.png`: original texture on top, new texture on bottom, side/front/three-quarter. Nearest-neighbor enlargement, no manual paint-over or generated illustration. Native sprites are in `before/sprites` and `after/sprites`; the new three-quarter sprite is 131x86 with 31 colors.

These were rendered from the exported model snapshot with `tools/blender/render_sprite_views.py` and converted with `tools/art/pixelize_render.py`. The wrapper imports the GLB, restores vertex connectivity for the loose-part ID pass, and changes the imported rig's rotation mode to Euler so the factory renderer's direction turns actually work. The renderer itself is snapshotted as `sprite-renderer-snapshot.py`. Stance `base=19;R_leg=16;L_leg=3;L_arm=27`, scale x4.4, flat-eye mode, highlight ranks 0.93/0.975 match `tools/art/ape_round.sh` inspected this day. Every before/after view has identical alpha and position; all three directions differ, verified in `pixel-audit.json`.

## Texture changes

Three 2048x2048 maps: quiet forest-green and warm orange paint, grey coated-steel joints and dark frame, broad light/shadow planes, modest baked occlusion, sparse geometry-based panel insets, and reduced repeated bump-grid strength. Physical plate edges and recesses carry the detail at small size. Paint is non-metallic; grey housings retain moderated metal response to remain legible under the current compatibility renderer. No extra geometry, copied game art, generator spend, or random scratch texture.

`tools/art/finish_gorilla_textures.py` derives component/material masks from the original model's own UVs and maps and authors the new maps on the same layout. The GLB is rebuilt by replacing its three embedded PNG buffers; all 212 non-image buffer views are compared byte-for-byte. Mesh, UV, bone, skin and animation JSON stays identical. All eight clips survive: walk, gait, idle, punch, slam, throw, hit, death. Source SHA256 and final asset SHA256 are in `after/audit.json`.

This snapshot predates ongoing concurrent model builds; never install its geometry over a newer build. To try the finish on a later model, run the tool with that later GLB as `--source` and a new isolated folder as `--out`, then review again.

## Evidence

- `preview.png`: the playable separate preview in the actual Godot lab camera.
- `before/native-*.png`, `after/native-*.png`: identical idle pose/camera at native 320x180 in Godot using the existing metal finish.
- `native-review.log`: gorilla_texture_check PASS, both versions open and all eight clips exist.
- `preview-check.log`: gorilla_texture_scene_check PASS, preview boots and plays all eight clips.
- Existing model_lab_check passed before and during the first provisional pass. The first live installation was replaced by the other session's newer build; subsequent work stayed entirely separate after Preston's choice.
- Logs also contain pre-existing sandbox user-log/certificate warnings and two small GL texture leak messages on preview process shutdown; there were no remaining GDScript parse errors in the final run.

## Methods and references

Used the project's Blender Texture & Materials skill for UV, color/non-color map separation and PBR checks; Blender Export Pipeline for preservation and engine verification. Reused the measured human-game lessons in `docs/reference/sprite-rules-legacy-2026-10-12.md` (Legacy's readable ramps, sparse bevel details and upper-left light) and `docs/team/CLAUDE_MECH_SKILLUP_HANDOFF_2026-10-12.md` (Cybertron's quiet paint, recessed structure, sharp edges). These inform technique only. Existing repository scripts, Blender, NumPy/Pillow and Godot produced the evidence. Godot MCP had no connected editor sessions, so checks used the project executable. No paid generator or external downloads were used.

The new texture is visibly calmer; whether it beats the reference's art quality is a visual judgment, not established by these checks. Workbench sprite rendering uses color texture and lighting, not the PBR roughness/normal response. No claim that this texture pass alone changes silhouette or positional issues.

Reproduce:

    python tools/art/finish_gorilla_textures.py --source docs/art/3d/gorilla-texture-2026-10-13/before/ape_l.glb --out docs/art/3d/gorilla-texture-2026-10-13/after
    blender --background --factory-startup --python tools/blender/preview_gorilla_texture_sprites.py
    python tools/art/review_gorilla_texture_sprites.py

The package's .gdignore prevents backup/preview assets being auto-imported as live game assets.
