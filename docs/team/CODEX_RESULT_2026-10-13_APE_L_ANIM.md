# Gorilla battle animation finish, 2026-10-13

Installed the color finish on all 51 gorilla battle PNGs across idle (4), gait (9), punch (9), slam (10), throw (10), hit (3) and death (6). The large plate interiors and orange fists have cleaner ramps, top edges pick up light, undersides remain dark, and existing gun/launcher and joint rims read more clearly. No geometry or gameplay changes.

## Preserved contract

- Every frame remains 149x148 with every original alpha byte and every transparent RGBA pixel exact. No cropping, alignment, resampling or pose edits.
- Existing teal pixels and their positions are exact, with no added teal or glow. Part counts and original occlusion remain unchanged, including the three ballast blocks, shoulder weapons, fingers, muzzle and joints.
- Live anim.json is byte-for-byte original: feet_y 121, all frame names/order, durations, loop declarations and strike markers. SHA256: 37ffcb50fa411431a0055ac228947e90c2113a2ae2c66375e5733d63ab6a3bec.
- All opaque colors use the 27 approved palette swatches. Five unsupported input colors were mapped within their own material family; transparent pixels were untouched.
- 48,138 opaque pixels changed across the set. Matching source poses across clips produce identical finished pixels (three repeated-pose groups).

## Evidence and preview

- Untouched full animation backup: docs/art/2d/ape_l/anim_v66_pre_codex/.
- Preserved finished frames, notes and helpers: docs/art/2d/ape_l/anim_codex/.
- Per-frame color/quality audit: anim_codex/audit.json. Guarded source/final hashes and repeated-pose groups: installation-audit.json. Final live/alpha/metadata and pose bounds: final-audit.json.
- Seven full before/after contact sheets at nearest 4x: review/<clip>-before-after-4x.png. Seven animated before/after comparisons: review/<clip>-comparison.gif. GIF durations necessarily use 10ms increments; live metadata is exact, including gait's 165ms.
- Actual game pose captures: review/battle/before/ and review/battle/after/, all 51 frames in both player/enemy slots. The review sets poses directly and does not represent a fight.
- Actual combat: review/combat.mp4 (4 seconds, 60fps) and review/combat.gif (20fps preview), plus combat-contact.png. Captured a real Piston Knuckles action through the combat queue against the current hippo, with the damage flash/number and recovery. This verifies punch playback; the other clips were inspected as poses, not exercised as real attacks.

## Checks

- Source-model reference replay: all 51 native poses reproduce the backed-up RGBA frames exactly before their part-ID maps are used. Reference renders were made in a background Blender process using the project's Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md); no .blend save. Seven weapon part IDs were tracked through poses rather than painting fixed screen rectangles.
- Guarded install: every live input PNG and metadata file rechecked against the backup before replacement. Only the 51 live PNGs replaced; all 51 subsequently match the finished copy.
- Godot import: exit 0. view_art_check.gd: PASS, all six view sets. battle_check.gd: PASS (seeded legacy battle-rule regression, not an animation-art test).
- review_battle_frames.gd: PASS, 51 frames in both actual battle slots with loaded canvas and frame durations checked. capture_combat.gd: PASS, 240 captured frames.
- Engine logs include the existing Windows certificate-store warning; import also cannot save external editor settings in the sandbox. Neither prevented imports, screenshots or checks.

No protected scripts under tools/, scripts/ or docs/art/3d/ changed for this pass. No commits. All temporary helpers and review media live in the art record folder with .gdignore.

## Existing pose/staging problems for Claude

These are visible in BOTH before and after captures and persist because silhouettes/canvases/positions are required to stay exact. The finish is complete; the animation composition still needs work on Claude's side.

- Slam 2 and 3 already reach the source canvas's left edge, cutting the rear leg. The player slam poses 1-4 extend behind the bottom UI panel. A few player gait/2 pixels are also behind the panel.
- The enemy slot translates the 149x148 canvas upward by 21 pixels. It clips the tops of slam/5-7, throw/6 and death/3-5. Death/5 also reaches source row 0; the player's upward offset can clip that row too.
- The death poses tip the model upward and remain raised; they do not yet read as a grounded collapse. Inspect the existing rig/clip before treating the finish as final animation approval.
- Evidence: review/battle/slam-comparison.png, throw-comparison.png and death-comparison.png; exact affected-pixel counts are in final-audit.json. A camera/canvas, rig or scene-position fix should come from Claude, then these color edits can be carried to the new frames. Do not simply paste old finished silhouettes over a rebuilt set.

## Latest handoff and next work

Reread CODEX_TASKS_2026-10-13.md after its 18:19 update. All six starters now load their own battle animation sets. The other five sets currently have 40 frames each and need color finishes too; finishing views/e.png no longer reaches those battles.

The four newer eight-view builds also still need their preserved finish carried forward: hippo p24, kangaroo p45, pangolin p20 and shoebill p67. Gorilla v66 and wolf v52 eight-view finishes remain live. Do not start the texture-sheet or pixel-room tasks until Claude wires their inputs as requested in the handoff.
