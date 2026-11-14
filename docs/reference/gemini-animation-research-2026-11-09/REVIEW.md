# Review of the Gemini animation report

The report is a useful planning draft, not verified animation instruction. Preserve its raw text and original Word export; apply the corrections below before using it. Reviewed on 2026-11-09, America/Chicago.

Original Gemini conversation: https://gemini.google.com/app/5efbf305227b1ab6

Exported Google Doc: https://docs.google.com/document/d/1CaFlyELL4UUHy3xXxwYLU7__rYBN3xMqcoEY1aMIDas/edit

`GEMINI_RAW.txt` is the connector's text extraction from the exported Doc, including its source list. `GEMINI_ORIGINAL.docx` is a byte-identical archive of the Word export Preston provided. Formatting was not edited. Provenance and content checks are in `provenance.json`.

## Useful guidance to retain

- Break actions into preparation, force transfer, contact/release and recovery. Preserve the intended verb and accepted ordering.
- Use generated motion as a donor candidate on a disposable copy. Preserve our approved mesh, rig, weights, armor ownership and textures.
- Inspect contact surfaces, support transfer, rigid lengths and actual root/controller movement. Review body-only movement at full speed as well as slowed diagnostics and game-camera views.
- Evaluate whether retargeting and cleanup save effort compared with authoring the action. A single sample cannot establish model-wide quality.
- Treat two-body grip, armor clearance and exact ability events as constraints to implement and verify locally, not properties guaranteed by a text prompt.

## Findings that must be corrected or withheld

| Report claim | Check and required correction |
|---|---|
| Chest-beat table says both variants have zero mesh penetration | False as a certification. Our uploaded brief and original README explicitly retain unresolved armor/shield intersections. The supplied sub-micrometer checks concern bone lengths and foot slip, not mesh clearance. |
| Shield-cast gap is under 2 mm; slip values for each clip; grab release is two frames late | Unsupported as reported measurements. Gemini had video and a brief, not a full mesh or transform capture. No frame-to-time convention or reproducible measurement is supplied. These can only become hypotheses to check, not instructions to alter accepted timing. |
| Grab-slam impact at frame 42 | Frame numbering is ambiguous and does not map reliably to the provided edited recording. The uploaded MP4 is 30 fps. Controller source sets grab at 0.18 s and impact at 0.60 s after cast start; the recording begins its first cast after 0.50 s. A direct inspected frame at video 1.10 s already shows impact; video 1.40 s (approximately frame 42) shows later recovery with the victim down. The diagnostic images are retained in the scratch upload folder. Do not advance the release based on this report. |
| Shield-cast movement can cancel after frame 22 | Do not adopt. Source `build-report.json` defines release at 0.25 s, frame 30 at 120 fps. Review sampled event clocks at 30 fps can quantize to 0.2667 s. Source event/pose timing is authoritative; do not replace it with an unspecified frame count. |
| Shield Drive was audited at quarter speed | The delivered review contains a half-speed replay, per its README and recording assembly. Do not label this 0.25x evidence. |
| Fixed gait schedules, 60/40 or 65/35 weight splits, duty factors, exact armor joint limits and millimeter offsets | These were not established for our assets. Some repeat other species' measurements; others are unlabelled authored proposals. The uploaded camera is not a mandated 45-degree isometric view. Use the actual configured game camera and species-specific viewed gait, and measure each rig. Do not add a diagonal gorilla gait or universal plate-angle limit from this table. |
| Meshy always outputs a 24-joint SMPL-H skeleton at 1.7-1.8 m | Not established by the cited Text to Motion endpoint specification. Inspect the actual donor file before defining bone maps, units or counts. Rigging API defaults are not proof about the standalone motion generator's output. |
| Prioritize a rhino quadruped charge as the first Meshy trial | Withhold. The same report flags humanoid donor limits. A short humanoid-compatible upper-body gesture is a more controlled first test; quadruped generation is a separate hypothesis and cannot justify replacing the existing rhino donor work. |
| Discard all anticipation and recovery from generated clips | Not a general fix. Isolate the useful action and retime phases only while preserving the load, contact and recovery needed for weight and gameplay. Uniform compression can erase the benefit we are testing. |
| All combat timing must use Call Method tracks; timers are never valid | Too absolute. Authored tracks can be appropriate, as can a single action clock that detects crossed event times with one-shot guards, interruption cleanup and time scaling. Keep our tested event contracts. No event mechanism alone guarantees exactly-once behavior under seeks, restarts and interrupted blending. |
| `AnimationTree.process_callback = ANIMATION_PROCESS_PHYSICS` | Prefer current `callback_mode_process` with `AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`. The old process-callback enum/accessors are deprecated. Verify against the installed version before editing. |
| `get_root_motion_position_accumulated()` gives controller velocity | Incorrect API name and quantity. Current methods are `get_root_motion_position()` for a delta and `get_root_motion_position_accumulator()` for an accumulated position. Convert delta to velocity with the time step and correct rotation when using animation-driven movement. Do not substitute absolute accumulated position for velocity; loop behavior needs care. |
| Adding an elbow angle guarantees collision clearance; 0.08-0.12 s inertialization eliminates float | Unsupported guarantees. Bounds and transitions must be tested against the real armor and contact constraints. Joint constraints do not perform mesh collision detection. Inertialization is an optional technique, not proof of a native, already-working Godot implementation here. |
| Zero-error limits and a 45-minute repair cutoff establish production approval | Unadopted policy proposals, not director decisions. Use numerical tolerances appropriate to floating-point/export behavior and measured geometry. Preserve separate technical and artistic verdicts. |

## Primary documentation checks

- Meshy Text to Motion: https://docs.meshy.ai/en/api/text-to-motion confirms 400-character prompts, 2-10 seconds in 0.5-second steps, Prime FBX at 10 credits and Swift BVH at 3 credits. It does not establish the report's universal skeleton claims.
- Godot AnimationMixer: https://docs.godotengine.org/en/stable/classes/class_animationmixer.html documents `callback_mode_process`, root-motion delta versus accumulator, coordinate conversion and loop caveats.
- Godot AnimationTree: https://docs.godotengine.org/en/stable/classes/class_animationtree.html marks the old process-callback enum/accessors deprecated. An AnimationTree is an option, not mandatory architecture for every current clip controller.
- The source ledger mixes primary sources, inherited notes and secondary/PDF-mirror sources. Its generic author labels and bundled entries do not independently establish every cited anatomical claim. No new gait numbers from that ledger are adopted by this review.

## Practical next use

Read `MESHY_TRIAL_PLAN.md` for a controlled first donor test. Do not generate quadruped motion or change grab-slam release timing merely because the report recommends it. This review does not certify every source or every pose suggestion. Paid motion generation remains unrun and held at this point.
