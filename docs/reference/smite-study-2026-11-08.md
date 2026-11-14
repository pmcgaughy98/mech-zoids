# Original SMITE — verified local study, 2026-11-08

Purpose: study professional animation craft to improve our original mech beasts. Extracted references stay in the private scratch workspace. No production model, rig, animation or runtime scene was changed in this pass.

## Verified results

Read original SMITE from `D:\Program Files (x86)\SMITE\BattleGame\CookedPCConsole`. Package version 893/licensee 0; installed Win64 executable version 1,0,6890,0. The game installation was not modified.

| Base character | LOD0 triangles | Mesh joints | Blender animation clips | Examined run |
| --- | ---: | ---: | ---: | --- |
| Hun Batz | 12,978 | 113 | 74 | runf: 0.835 s sampled span |
| Raijin | 16,500 | 82 | 85 | run_com_f: 0.735 s sampled span |

Counts were checked against package dumps, glTF and Blender 5.2.2 LTS imports. AnimSet track-name counts are larger than the actual mesh skeletons. Timing is first-to-last exported key, not a verified engine loop period or source frame rate.

Rendered and inspected 16 phases of each forward run, assigning the action to the rig and disabling NLA. Hun Batz shows a bounding, reaching motion; Raijin runs upright with raised drumsticks. Neither provides our gorilla's grounded knuckle gait. Both inventories include directional runs, combat/non-combat variants, turns, transitions, attacks, reactions and idles. This demonstrates animation coverage, not the runtime blend/controller settings.

## Decisions for our gorilla

Preserve the approved fist/foot bulk, downward knuckle orientation, shields, green backing and completed orange back rim. Latest source: `D:\dev\new-mech-rpg\art\model_catalog\workspaces\gorilla_back_rim_review.blend`.

1. Use actual gorilla locomotion/anatomy references for contact order and wrist orientation. Use these SMITE characters for presentation and animation-set coverage rather than their body plan.
2. Create an original slow knuckle walk with explicit support/swing phases. Lock supporting knuckles and feet in world space during stance; shift shoulders/pelvis over the support region.
3. Add elbow/knee clearance and controlled shoulder/pelvis counter-motion. Keep mech plates rigid and shield edges clear of torso, wrists and ground throughout the cycle.
4. Verify one forward loop at game speed and slow motion before multiplying directions. Check contact drift, penetration and loop seam. Provisional drift target: less than 1% of body height during intended stance; revise against real scale and terrain behavior.
5. Match stride distance to our controller speed. Add directions, turns, start/stop, attack/recovery and hit response with compatible transition poses.
6. Keep the current 34-bone rig unless a specific contact/deformation test exposes missing controls. Reference joint counts include face, fingers and accessories; matching counts is not a quality target.

No claim that this study has already improved our original animation. A real in-game comparison remains outstanding. These are rendered reference inspection previews, not a recorded tutorial. Preston's request for real screen-recorded instruction during manual visual work remains relevant.

## Private evidence

Workspace: `D:\dev\_scratch\smite-study-2026-11-08`.

- `package-headers.json`, mesh and AnimSet logs: source metadata.
- `clip-metrics.json`, `measure_clips.py`: all clip names and timing measured across every sampler input, not just the root track.
- `blender-import.json`: imported objects, actions, slots and skeletons.
- `previews/run-phases.jpg`: inspected 0%, 25%, 50%, 75% samples.
- `previews/hun-batz-run.gif`, `previews/raijin-run.gif`: 16-phase loops, approximate exported timing.
- `previews/hun-batz/study.blend`, `previews/raijin/study.blend`: editable reference scenes.
- `render_study.py`, `render-report.json`, `render.log`: render procedure/camera bounds.
- `references/`: private extracted meshes/animations. Keep out of production art and exports.

## Tool setup and limitations

Preston explicitly approved downloading and using UModel. The official prebuilt ZIP returned 404, so it was built from official [UEViewer source](https://github.com/gildor2/UEViewer) and [BuildTools](https://github.com/gildor2/BuildTools). Source archives, source and build logs are under `D:\dev\_tools\umodel`. This is a locally patched source build, not an official prebuilt version.

Local patches: locate existing relocated VS2022 tools; limit JOM to four jobs and disable build notification sound; load the game's existing Win64 Oodle 7 DLL through process PATH; attach the requested AnimSet during headless skeletal glTF export and skip redundant separate animation-only export. No proprietary DLL was copied into the project. Executable: `D:\dev\_tools\umodel\UEViewer-master\umodel_64.exe`.

Export used `-game=smite`, the CookedPCConsole path, `-export -gltf -png`, and `-anim=as_god_monkey` with `HUN_BATZ_ASSETS_SF.upk skl_god_monkey SkeletalMesh`; Raijin used `as_god_raijin`, `RAIJIN_ASSETS_SF.upk`, `skl_god_raijin`.

Texture export could not resolve the named automated TFC cache and used embedded small mips. Previews use neutral clay and do not reproduce game textures, transparency, lighting or shaders; layered surfaces are especially affected. Windows viewer screenshot capture timed out twice; offline export and Blender rendering worked. Blender saved both scenes despite a thumbnail-cache write warning outside the workspace.

[UModel compatibility](https://www.gildor.org/projects/umodel/compat) lists original SMITE support. [Documentation](https://www.gildor.org/en/projects/umodel) describes limitations including additive animations and some materials. Isolated exports cannot establish runtime blending or final gameplay quality. Fenrir/Cerberus packages were located but not visually studied in this pass.
