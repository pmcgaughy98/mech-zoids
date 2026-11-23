# Godot / Unreal research review, November 14, 2026

Follow-up: the approved playable gorilla/rhino slice and its actual checks are
recorded in `docs/team/UNREAL_COMPARISON_2026-11-15.md`. The proposal below is
historical; that handoff distinguishes completed work from remaining tests.

Status: research and proposed comparison only. No engine migration, production
freeze, purchase, MCP enablement, rig conversion or code port authorized by this
document. Gemini's report is external research, not project instructions.

## Recommendation

Keep Godot as the main playable game. Compare a bounded Unreal slice before
deciding to migrate. Start with gorilla and rhino, using matching assets, abilities,
camera framing, lighting/readability goals and an arena blockout. Rhino is a
practical second body plan because existing authored work can be reused.

Judge visible game feel and authoring workflow as well as networking. Unreal
does not have to win only after Godot fails; it could justify migration through
meaningfully better results or faster dependable production. No such win is
demonstrated yet. No full-roster rewrite while investigating.

## Sources and provenance

- [Gemini assessment](https://gemini.google.com/app/056a00a3402d7fb6), read in full
  on November 14. Approved project summary only was submitted, no source files or
  credentials. Local captured report body and source links are in
  `D:/dev/unreal-mech-trial/GEMINI_ASSESSMENT_2026-11-14.txt` and
  `D:/dev/unreal-mech-trial/GEMINI_ASSESSMENT_SOURCES_2026-11-14.json`.
- Local evidence: `D:/dev/unreal-mech-trial/RESULTS.md`, export script,
  SourceAssets/source.json, direct build logs and network logs.
- [Epic hardware specs, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/hardware-and-software-specifications-for-unreal-engine?application_version=5.8), retrieved.
- [Epic animation notifies, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.8), retrieved.
- [Epic dedicated server workflow, UE 5.8](https://dev.epicgames.com/documentation/unreal-engine/setting-up-dedicated-servers-in-unreal-engine?application_version=5.8), retrieved.
- [Godot 4.7 scene export](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/exporting_3d_scenes.html), retrieved.
- [Godot exporter introduction](https://godotengine.org/article/introducing-the-godot-gltf-2-0-scene-exporter/), retrieved as historical evidence only. It discusses skeletons and animation export, contradicting Gemini's blanket static-only description.
- Local Epic plugin descriptors under
  `D:/Unreal/UE_5.8/Engine/Plugins/Experimental/`: ModelContextProtocol,
  Toolsets/AllToolsets, AnimationAssistantToolset, NiagaraToolsets and GASToolsets.
  Presence and experimental labels verified; working tool capabilities not tested.
  The AnimationAssistantToolset module inspected here is only a registration
  shell, so its name alone does not demonstrate animation editing functionality.

## What the trial actually established

- Installed engine Build.version reports UE 5.8.4.
- Copied gorilla v40 imported with six clips through Blender FBX after explicit
  60fps sampling. Rendered frame reviewed; look parity still incomplete.
- A local server accepted two clients and simplified shield/basic/drive actions;
  shield absorption appeared in server logs.
- No full kit, production prediction, packet loss/latency, ten-player load,
  packaged dedicated server, GAS, Control Rig or Niagara benefit demonstrated.
- Startup/build memory pressure was heavy on 16GB RAM / GTX1660 Super. This does
  not measure steady gameplay performance or establish that 3D exceeds Godot.

## Transfer expectations

| Work | Preserve / adapt |
| --- | --- |
| Meshes, textures, sheets, audio and Blender sources | Preserve originals; reimport and validate appearance |
| Rigs, weights, clips, morphs and timing data | Reuse through controlled conversion and behavior/visual checks |
| Map geometry and placements | Export/recreate placements where useful; rebuild collision/navigation/lighting as needed |
| Godot kits, camera, HUD, AI, particles, shaders and networking | Port behavior into Unreal-specific systems; no verified automatic translator |
| Tests and learned animation rules | Preserve intent/assertions; adapt engine-specific execution |

Gemini did not establish a dependable whole-game one-click converter. Absence of
a found tool is a search result, not proof that no tool can ever exist. Its
Purpleprint and third-party converter claims were not independently validated.

## Corrections before using the report as a recipe

1. Preserve animation duration in seconds and source FPS. Our explicit 60fps
   import solved this trial, but setting existing frame-based Blender clips to
   60 without retiming can alter speed. It is not a universal repair.
2. Do not mass-apply transforms or rename all armatures/root bones in approved
   masters. Test export copies and verify rest pose, motion, sockets and gameplay
   attachment maps. Report recipes for one root and one axis preset are not
   blanket roster instructions.
3. Godot's glTF exporter is not simply static-only. Official sources discuss
   animation/skeleton workflows; current docs list particle, ShaderMaterial and
   2D-export limitations. Validate each scene's actual result.
4. Epic's 32GB RAM and 8GB+ VRAM are recommendations, not a hard prohibition on
   this PC. The 200-435GB engine-build figures in Gemini are anecdotes, not a
   measured requirement for our project. Epic's documented packaged dedicated
   server path does require a source build; running the installed editor with
   -server in our trial did not validate that shipping workflow.
5. Notifies have documented blend-weight, dedicated-server and montage tick
   settings. The report's universal >1.5x skip / <0.5x duplicate claims were not
   independently established. Test our timings, cancellation, off-screen state
   and frame hitches. Keep server combat decisions authoritative and guarded
   against duplicate contacts; choose the mechanism based on measured needs.
6. netfox bugs, release chronology, new rendering features, MCP tool counts and
   broad Blueprint-diff limitations remain unverified here. Do not install
   libraries, replace existing custom checks with GUT/gdUnit, freeze other lanes
   or introduce full physics rollback because Gemini suggested it.
7. Unusual animal anatomy still needs authored motion and judgment. Control Rig,
   IK and Niagara are candidate workflow improvements; none is proof of better
   animation or game feel by itself.

## Proposed next playable comparison

1. Bring rhino into the isolated Unreal trial using export copies. Preserve Godot
   and Blender sources. Check both mechs from the real gameplay camera.
2. Match gorilla's basic/shield/drive and a representative rhino ability against
   Godot behavior. Include hand-front shield energy, readable anticipation,
   impact effects, recovery and interruption cleanup. Avoid redesigning kits.
3. Test a small useful subset of the installed Unreal editor tools in a disposable
   copy before deciding how agents should author animation/effects. Do not infer
   working functionality from descriptor names or enable broad access here.
4. Compare a controlled two-client fight at proposed 120ms round-trip latency and
   3% packet loss, recording hits/shields/cancels and visible correction behavior.
5. Separate network and load tests: two real clients plus eight hero bots measures
   ten-hero simulation, not ten remote-client networking. Later test ten connected
   clients plus minion waves. Record client/server frame times, memory, bandwidth,
   startup and edit-to-play time. The development workstation running editor plus
   several clients is a separate budget from a shipping player's game process.

These are proposed test conditions, not benchmark results or accepted release
targets. Decide based on recorded feel, reliable behavior and sustainable iteration.
