# Gorilla heavy-basic refinement — 2026-11-10

Playable review candidate; production gorilla and roster registration remain unchanged.

Run `launch-review.cmd` for the industrial map with the real gorilla kit and an articulated damage target. WASD moves, hold left mouse for the three-hit chain, 3 forces the heavy basic, Tab switches current/refined, R resets, right mouse drags camera, Escape closes. Close any other Godot game first. The review intentionally hides VFX so the body motion can be judged.

## Change

`Gorilla_Slam_Compact_Trial` is a grounded alternative to `Gorilla_Slam_v25`: rear feet stay planted in clip space, torso load is distributed through rotations rather than translating the chest away from its parent, shoulder-centered arm arcs avoid the folded IK singularity, fists orient before contact, and contact briefly holds before recovery. Controller movement still moves the actor during strafing; clip-space contact locks do not mean world-space foot locking while moving.

Same 0.95-second clip duration and 50/120-second contact marker. Existing damage, kit cooldowns, movement speed, model size and other clips are preserved. The candidate has a shorter visual reach and a lower contact pose; those require artistic review, especially at maximum melee range. No full armor-clearance certification or claim of matching shipped SMITE/Paragon quality.

## Art contract and evidence

Source: `D:/dev/_scratch/gorilla/codex-grab-slam-trial-2026-11-09/grab-slam-trial.blend`, matching the starting runtime GLB SHA256 `846f76ebf48f1b31719447a7dfdd2a67f8345deef546f307b4860d5b03b4cd39`.

Candidate and reproducible authoring/validation scripts: `D:/dev/_scratch/gorilla/combat-polish-2026-11-10/` (`combat-polish.blend`, `combat-polish.glb`, `build.py`, `export.py`, `validate.py`). Uses existing local animation study and the approved SmartRig; Cascadeur was set aside and did not generate this clip.

Export/reimport checks preserve geometry, UVs, weights, material assignments, packed image bytes, 34 rest bones and all 19 original action curves. GLB has 69 actual skinned mesh nodes; Blender's reimport scene also contains its helper mesh. New clip has an exact ready-pose boundary, sub-micrometer rear support-patch drift, and no left/right shield surface crossings in the sampled clip. Parent-to-child spine spacing error falls from about 0.188 m in the original heavy to below 0.000001 m. These checks do not certify all body/armor intersections.

`export-validation.json` and `build-report.json` contain measured results. Native review checks cover single heavy, full chain, moving chain and sharp reversal; actual kit callbacks apply damage. All 11 shots passed at 15, 30 and 120 FPS; the 60 FPS run also passed. Single heavy applies 42 damage; full chains apply 28 + 28 + 42. Saved per-FPS results are in the scratch directory. Logs include a Windows root certificate store warning in headless mode.

Videos: `heavy-before-after.mp4` (same side view at normal and half speed, no interpolation), `combat-review-final.mp4` (full 33-second rear/front/side, chain and strafe review). All paths above are local, not uploaded.
