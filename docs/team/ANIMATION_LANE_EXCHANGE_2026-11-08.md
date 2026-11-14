# Gorilla and rhino animation knowledge exchange

Preston explicitly requested that the Hub read both conversations, update both animation chats with the TartarusArena review, and share each chat's accomplishments and lessons with the other. Reviewed the available histories through their earliest pages: 39 gorilla turns and 27 rhino turns, including current in-progress updates. Also read selected saved validation files and the rhino v6 README. Chat reports and saved checks below are not a new independent video approval by Hub. Both chats remain active; newer work may supersede this snapshot.

## Gorilla: accomplishments and current correction

Chat: Mech Gorilla Animations, local `01a1b70c-6583-7122-bd1e-ccda65dacba4`.

- Corrected downward knuckle-walking fists, restored their requested bulk, rebuilt the feet and brought their finish into the mech's green/gray armor language. Refined symmetric hex shields, green cell backing and orange rear-cell rim. The current instruction for eyes is to paint the existing eye areas solid green without pupils and remove eyebrow markings; misplaced added eye pieces were rejected.
- Preserved the existing 34-bone rig when working in MeshForge, rather than treating a new automatic rig as an improvement by itself. Rampage's actual supplied clips became motion references after the generic kaiju attack proved unsuitable for gorilla punches.
- Developed a knuckle-walk foundation and tested in the industry map. Preston requested MOBA travel speed rather than the initial slow walk; 3.5 m/s and 4.38 m/s buffed travel were tested as existing preview baselines, not universal new balance decisions. Raising travel speed without enough stride/cadence adaptation caused skating. Recovery/weight cleanup improved it; sharp turns and lower-body stretching still required work.
- The first four-second idle was technically clean but too subtle to read. The later v14 uses the supplied Rampage idle's 7.67-second rhythm, visible torso/shoulder motion and head scanning. Saved validation reports about 6.1 cm chest side travel and 22.3 cm head side travel, planted hands/feet and a seamless loop. The visible-motion audit also measures actual armor surfaces, because joint motion alone did not prove the main chest mass moved.
- A pelvis-shape correction was explicitly reverted. Uneven thigh/chest influence was identified as a binding problem; preserve approved rest proportions and repair ownership rather than sculpting a distorted rest pose. v14 redirects 645 pelvis/chest weight assignments in the separate idle asset. Its validation says the walk asset was untouched; do not generalize this as a complete walk/pelvis fix.
- v15 built alternating strikes and a heavier finisher, with contact timestamps, video and 177 targeted armor-clearance poses passing. Preston then rejected the motion quality: the actions read as arm swings rather than punches. The clearance-driven wider arcs made fist travel lateral/downward or reversing around the marked hit. Current work is v16: one convincing full-speed punch first, with a loaded wind-up, body/shoulder drive, fist-led strike line, readable contact and recoil, inspected from side and game camera. Do not promote the v15 chain as approved combat.

Useful paths:

- `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v14/idle-validation.json`, `visible-motion-audit.json`, `gorilla-idle-front-v14.mp4`.
- `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v15/final-validation-summary.json`, `exported-clips.json`; these preserve evidence of technical checks, not approval of punch mechanics.
- `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v16/rejected-v15-motion-diagnosis.json`, `one-punch-study.json`; in-progress study, not a completed replacement.
- Older Claude heavy-walk reference: `D:/dev/_scratch/gorilla/walk3d/walk_v1_vs_v2.gif`, with `walk.py`, `walk2.py`, `cut4.py`, `cut5.py`. Useful timing and grouping lessons; do not copy gorilla bone mappings to a rhino.

## Rhino: accomplishments and current correction

Chat: Mech Rhino Animation — Donor Retargeting, local `01a1bbae-6a78-7c83-97f6-070e8039ba5f`.

- Moved from inadequate geometric splitting and a clearly labelled bull fallback to the actual user-downloaded LasquetiSpice rhinoceros archive. Inspected donor idle/walking/running; built an isolated playable idle/move/horn-attack/recovery sequence. The horn attack is separately authored, not a donor rhino attack. Running became a distinct charge loop instead of just accelerating the walking clip.
- Recovered the mech's original concept: shoulder cylinders are seismic transducers. Added axial compression/rebound, dorsal load/release, chassis settling and head stabilization. Preserve that functional intent; arbitrary spinning rings or a replacement kit were not requested.
- Preserved source rig and original textures after the automatic-rig trial bent the armor too much. The current family has the original 31 bones plus three named part controls, with four accepted motion clips extended by MeshForge brace enter/hold/exit to seven clips. Original textures were explicitly retained after Preston initially mentioned retexturing.
- Found that moving armor gaps can be binding/ownership errors even when faces were not deleted. Correct plate ownership, separate rigid boundary corners and close exposed shell interiors before inventing broad covers. Rear plates, axle/supports and boot interiors have received local repair; a duplicate lower tail was removed and its former attachment integrated as beveled matching armor.
- Preston rejected the thin, exposed-support/squiggly-leg revision. The selected direction combines the earlier improved shoulders/mechanical fixes with restored full bulky leg armor. Preserve a credible weight-bearing silhouette, shell thickness, hinge/load paths and surface finish. Passing contacts/loop checks does not approve a changed silhouette or rough panel construction.
- Latest delivered v6 recesses cylinders another 150 mm per side and wraps them in closed torso sockets, retaining moving faces. Its README records original texture bytes, all seven animation sample buffers and 34 joints preserved; 51 checked parts have closed geometric boundaries. This was an integrated-body visual review, not a universal clearance pass.
- Current v7 is hidden hip/socket clearance work, preserving selected outer rims. The inspected `socket-motion-check.json` is empty for the sampled idle/walk/horn/brace cases but still lists several charge-pose overlaps. The chat is actively refining those inner corners and a hidden front-boot axle. Do not report the charge fully clear yet.
- FFmpeg successfully recorded a real 14-second Blender ankle-edit tutorial despite Computer Use screenshot failures. Slipa edits existing video; it is not a screen recorder. Short safe-copy tutorials with undo remain Preston's preference for manual edits.

Useful paths:

- `D:/dev/_scratch/rhino-donor-2026-11-08/actual-rhino-full-rig/README.md` and `playable-input-test.mp4`.
- `D:/dev/_scratch/rhino-donor-2026-11-08/seismic-life-v2/README.md` and `faster-gait-cylinders.mp4`.
- `D:/dev/_scratch/rhino-donor-2026-11-08/body-cylinder-integration-v6/README.md`, `final-preservation-check.json`, `body-integration-comparison.mp4` and editable review model.
- `D:/dev/_scratch/rhino-donor-2026-11-08/hip-clearance-v7/socket-motion-check.json`, `cuff-clearance-shaping-check.json` and `manifest.json`; in-progress diagnostics.
- `docs/team/RHINO_ANIMATION_CODEX_HANDOFF_2026-11-08.md` is cumulative and has superseded historical sections. Prefer newest direct user corrections and current chat/files.

## TartarusArena lessons for both chats

Read `docs/reference/tartarus-arena-review-2026-11-08.md` for inspected source links and qualifications.

1. Make attack acceptance, wind-up, contact and recovery explicit. Align actual fist/horn contact, damage, sound and VFX to the same intended event; a time marker or passing counter alone does not prove contact. Tartarus itself uses configured hit delays, so do not assume it is automatically animation-notify accurate.
2. Define cancellation and priority: recovery can release to movement/another allowed action; stun/death must safely interrupt; ordinary hit reactions must not cut important actions. Scale and throttle hit-stop so repeated small hits do not freeze the match.
3. Blend from the current visible pose into the next clip, including death and return to locomotion. Compatible rigs and good source motion are prerequisites; blending does not repair an unconvincing punch or bad weights.
4. Test idle, forward, backward, strafe, stop, sharp turns and speed buffs separately at the real SMITE-style camera. Preston named SMITE as the main control/feel reference, with Paragon secondary. Do not inherit Tartarus's orient-to-movement workaround for forward-only pack jogs without deciding our desired behavior.
5. Build small real-game animation tests with measurements and video. Keep technical checks (contact, loop, clearance, curve/texture preservation) separate from artistic checks (weight, anatomy, readable intent, proportion and silhouette). User visual rejection overrides a technical pass.
6. Tartarus's combos/perfect dodges/action buffer belong to its separate action prototype. Treat them as optional reference, not permission to change our kits. Its Unreal/C++ code and external Paragon assets are not a drop-in Godot animation solution. It is an AI-built prototype, not our shipped-human-game synthesis authority.

## Coordination boundaries

Share methods and read each other's references; do not overwrite the other lane's models/scripts or blindly transfer bone names, gait values, support poses or clearance solutions across animal anatomies. Preserve originals and accepted motions, work in revisions, coordinate the single Godot process, and keep kit mechanics and final art decisions with Preston. This knowledge exchange authorizes no new purchase, generation, download, external upload, commit or expanded roster batch. Both chats should incorporate the lessons into their current assigned work rather than abandon their in-flight punch or hidden-clearance task for a framework rewrite.
