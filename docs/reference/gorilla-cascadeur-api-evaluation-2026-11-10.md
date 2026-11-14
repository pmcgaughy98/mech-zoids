# Cascadeur API evaluation — 2026-11-10

Connection succeeded. The installed local runner on127.0.0.1:8765 executed Python3.11 inside Cascadeur2026.2.3. The user activated the free/basic license and started the runner. This evaluation used local files; no paid upgrade, generation, cloud upload or license modification was performed.

## Result

The API is useful for direct scene automation. It is not itself a text-to-motion generator and does not establish a right or technical ability to export paid formats on the free plan. No blocked export was attempted.

A disposable copy of the existing Gorilla_Slam_v25 was exported from our original Blender source as FBX (34 bones,69 mesh objects,114/120s), imported into a new Cascadeur tab and saved successfully as CASC. Cascadeur warned about120fps→30fps and imported30 frames; frame-sensitive contacts require resampling-aware review. This is our existing authored motion, not new Cascadeur-generated motion.

Two automatic physics-rig preparations were evaluated: an initial name template and an explicit native-path template with pelvis realignment disabled. Generation's modify callback returnedTrue and created49 points,21 rigid bodies and one AutoPhysics component. That did NOT preserve the native joint motion. Relative to the imported baseline, maximum foot-head displacement was about11–12cm, shoulder displacement about14.7cm and an auxiliary joint exceeded60cm. These are sampled joint-head distances in Cascadeur centimeters, not surface clearances or sole-contact errors. The original baseline itself has48cm foot-head movement across this slam, so those baseline movements must not be mislabeled as rig-induced sliding.

Re-importing the animation onto the first generated rig did not repair preservation; foot-head error rose toabout21–22cm versus the imported baseline. The explicit template also failed the preservation check. Neither rig is approved.

The AutoPhysics preview solver logged successful stages, but also `bimap<>: invalid key`. The subsequent Snap to Auto Physics action produced ZERO measured change in joint-head positions across34 joints×30 frames versus its pre-physics state. This is not proof of a successful physics correction. The candidate is rejected for game hookup; no claim of artistic improvement is made. Do not feed this unsuccessful rig result into Plask and expect it to fix the mapping.

Native source SHA-256 still matches `baseline-export.json`. Main match, original rigs, geometry, weights, textures and accepted animation curves were not edited. Saved experimental scenes remain separate.

## Current scene and evidence

`gorilla-baseline-review.casc`: unchanged imported baseline, clean mesh view, front-quarter camera. Timeline.Play was issued and a frame-change command was logged. The exact visual playback could not be independently inspected because Windows Graphics Capture repeatedly timed out. No new comparison video is claimed.

Experimental scenes:
- gorilla-rig-generated.casc
- gorilla-rig-animation-restored.casc
- gorilla-explicit-rig.casc
- gorilla-physics-evaluation.casc

Evidence: probe.json, cascadeur-import.json, generated-rig.json, rig-preservation-audit.json, reimport-vs-baseline.json, explicit-rig-audit.json, physics-audit.json and corresponding HTTP responses. `client.py` contacts only the installed local runner; numbered scripts reproduce the steps. Do not rerun scene-mutating scripts blindly; several expect the preceding scene to be current. A saved baseline tab and saved unsuccessful trial tab were closed to reduce memory; the original user tab was retained.

Cascadeur repeatedly reported low available RAM and cleared undo history during rig generation. Saved copies are essential for these experiments. No unrelated user apps were closed.

## Next useful work

Fit a native rig that preserves every deform/helper joint and supports this mech's proportions before judging AutoPhysics or AutoPosing quality. Verify bone mapping, support constraints, source timing and visible armor behavior. Then compare a clearly constrained corrected take against the unchanged baseline at full and half speed. This first automatic setup is not ready for production.

The free plan remains CASC-only/non-commercial per the official plans page. Python automates authoring, not license entitlement. Plask would be an approximate video-to-motion reconstruction step, not lossless export. No Cascadeur animation data was extracted into a substitute game format here.

References:
- https://cascadeur.com/help/tools/animation_tools/python_scripting_in_cascadeur
- https://cascadeur.com/help/category/215
- https://cascadeur.com/help/category/301
- https://cascadeur.com/plans
- Installed SDK stubs/examples and scripts/mcp/script_server/README.md were used as the authority for this installed version.

## SmartRig preservation and playback caveat

Preston explicitly reaffirmed Meshy SmartRig as the baseline. The original source armature is `SmartRigArmature`; this was already the34-bone baseline imported above. The regression belongs to Cascadeur's generated control-rig fit, not evidence that the Meshy skeleton/weights should be replaced. Future tests must preserve that skeleton, weights, proportions and source action while fitting compatible Cascadeur controls.

The final Timeline.Play HTTP request timed out, and subsequent local health requests also timed out. The frame-change log confirms a command was issued, not verified playback. Accessibility returned no editor content; a keyboard attempt intended to stop playback instead logged Snap to autophysics, so no further shortcut input was attempted. The saved baseline and all experimental scenes predate that recovery attempt. Native source hash remains unchanged. User restart requested; API connection was proven earlier but is not currently responsive. Do not claim the baseline is visibly playing or that the runner remains healthy until reconnection is verified.

## Reconnected continuation — 2026-11-10

The user reopened the saved scene and restarted the local runner. A fresh probe verified that the saved CASC loads with all34 joints. The connection is responsive again; Timeline.Play was not used in this continuation. Last status is in final-connection-status.json.

### Current usable checkpoint

`gorilla-smartrig-preserved.casc` is the original imported SmartRig baseline, with no generated Cascadeur control-rig override. A temporary2-degree native LeftArm FK edit at frame3 moved its hand; the edit was then restored before saving. Every sampled global joint matrix across34 joints×30 frames matches the baseline exactly (maximum component difference0.0 for this roundtrip). The source animation was not artistically changed. This proves direct native-bone authoring through the API, not a quality upgrade or physics correction. Script25 refreshes viewers after edits; script26 verifies the current scene and working connection. The view is left at frame12 with mesh display and a front-quarter camera, not playing.

### Control-rig diagnosis

Generating controls with functional overrides off preserved matrices within floating-point error (maximum component difference0.000270844). However, those disabled generated functions also blocked a test FK propagation. That version is an isolated diagnostic, not a fully editable finished control rig, and is not the current working checkpoint.

The earlier create_from_qrt methods auto-detected a human chest mapping to Spine1. Using open_quick_rigging_tool followed by load_template_by_fileName correctly loaded our explicit native mapping, including Chest→Chest. Generate_rig_elements then built the intended prototypes. Activating those generic controls still significantly changed the native matrices; the candidate remains rejected. Correct bone-name mapping alone does not calibrate this mech's rest orientations, support or extra helper joints.

A full DataSourceManager scene load and explicit full-track/full-frame selection did not remove the gorilla AutoPhysics bimap error. The installed vendor Backflip_animation.casc, evaluated in its own CASC copy, completed AutoPhysics core without that error. Its applied result differed only at numerical scale (max matrix component0.000183105 across58 joints×124 frames), so this already-polished sample does not demonstrate an artistic improvement. It does separate a general API failure from the generated gorilla rig issue. No vendor motion or mesh was exported into our game.

Several saved test tabs were closed to reduce memory. Path comparison was normalized before closing; source files and failed candidates remain on disk. The original Meshy SmartRig source, weights and game registration were not changed. Windows Graphics Capture still times out, so no new visual quality certification or comparison video is claimed.

Next work, if pursuing Cascadeur's unique physics/AutoPosing benefit, is a native-proportion control rig that remains editable while preserving original transforms. Direct FK authoring on the original SmartRig is already available. Plask is not needed for API control; it would remain a separate approximate video reconstruction option for outputs on the free plan. No animation data or alternate game-format export was extracted from Cascadeur during this test.
