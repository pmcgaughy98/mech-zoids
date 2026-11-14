# Current layout: inner-jungle objectives

Preston corrected the placement after Revision 2. Both bosses are inside the outer lanes and now open toward mid/jungle. See [Revision 4](../foundry-5v5-2026-11-11-open-bosses/REVISION_4.md) for current layout and verification. The original asset-delivery record below is preserved.

# Foundry 5v5 foundation delivered November 11, 2026

Launch `res://scenes/map5v5/foundation.tscn` with F6 in Godot, or run `D:/dev/new-mech-rpg/tools/map5v5/launch_foundation.ps1`. Project Play remains the current 3v3 Arena Play. The launcher refuses to start a second actual Godot app and never terminates another preview.

This is a walkable ten-body training foundation, with a proposed three-route 160 x 220 m footprint, authored collision/navigation, four camp spaces, two objective spaces, team bases, current model selector, and a ten-player HUD/minimap. Topology, scale and travel targets remain drafts. It is not a complete 5v5 match: three-lane waves, competitive bot decisions, economy, boss combat/rewards, networking and final art are not implemented.

## Current Claude work preserved

Caught up on November 11 from current Claude text records, the November 10 evening catch-up, project notes, actual scripts and model registry. Important changes from the original morning brief:

- Gorilla v32 and its current **Fault Line / Drive Slam** kit, including the chained hold/slam, stronger chest beat, native movement clips, targeting and hand energy. The earlier standalone grab/Drive assertions were replaced with checks of the current contract, not a gameplay rollback.
- Rhino v52; registered kangaroo r9, hippo r10 and pangolin r4. The registry has five authored trials and twenty base proxies. Registration does not make every animation, kit or effect finished.
- Red team's kangaroo is preserved; the extra training slots avoid duplicating it. The current Foundry grade, albedo treatment, smooth shared effects and camera edge behavior are inherited.
- Claude's unnamed-kit HUD fallback fix superseded the workaround in this foundation; the workaround was removed. Shared arena/HUD/camera/kit/model/rig files were not edited by this lane.
- Hippo pressure/Toxic Flood and kangaroo Title Bout effects remain their owners' in-flight work. The broken Grok wolf bite and other unapproved animation drafts are not promoted here.

## Four generated environment modules

| Module | Runtime envelope, meters (width / height / depth) | Triangles | Materials | Copies in the map |
| --- | --- | ---: | ---: | ---: |
| Armored wall | 6 / 2.6 / 1.6 | 5,000 | 1 | 24 |
| Matching pillar | 2.4 / 4 / 2.4 | 4,000 | 1 | 24 |
| Camp power installation | 3.6 / 3.2 / 3.6 | 6,000 | 1 | 4 |
| Objective reactor landmark | 5.2 / 5 / 5.2 | 8,000 | 1 | 2 |

All four have grounded pivots, glTF +Y up, at most 1K runtime textures, packed Blender workspaces and separate raw exports. Source/output SHA-256 and actual budgets are verified by `tools/map5v5/asset_manifest.py`. Native game-camera review is in `batch-game-camera.png`. Modules share charcoal steel and amber accents; the reactor is bulkier and darker than the smaller pieces, so further art direction is still useful.

There are 54 generated-module placements in the map, plus the two existing boss models. Generated geometry never supplies navigation collision. Island skins stay within conservative locally authored body envelopes; their visuals are a foundation, not an exact mesh-contact simulation. Tower/core silhouettes, large housing blocks and skyline remain local structural placeholders.

**Actual spend: 120 existing Meshy credits**, from eight successful stages, four previews at 20 credits and four refinements at 10. No rerolls, paid retries, purchases or additional asset generation. Initial observed balance was 1,010; final queried balance was 860 (710 monthly, 150 permanent). The eight exact task records prove this batch's 120-credit cost. The additional net 30-credit difference is account activity outside this batch's records, not attributed to this lane. Official pricing and endpoint links are in FOUNDATION.md.

Exact ids, requests, provider metadata, raw model/preview hashes, local optimization and source links: `art/environment/foundry_5v5/manifest.json` and its `source/`, `runtime/`, `workspaces/` folders. No Meshy key was printed or persisted. No saved fal.ai credentials were inspected, no separately billed provider was used, no new chat/agent/peer message was sent, and nothing was committed.

## Gold beetle and wyvern

Preston confirmed these objective identities and supplied `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/`. Used its existing files:

- `Meshy_AI_coinclaw_mech_remeshed_25k_20261111_character.glb`: 23 bones preserved, no authored clips. Draft preview height 3.8 m, about 3.63 x 3.99 m on the ground.
- `Meshy_AI_Cyber_Wyvern_Sentinel_1110211655_texture.glb`: 46 bones preserved, no authored clips. Draft preview height 6.5 m, about 4.56 x 5.64 m on the ground.

Separate 1K-texture viewing copies and packed native workspaces retain the bone hierarchies and uniformly scale the originals, without changing original geometry/weights or source files. Both originals were hash-verified after export. Local body footprints are deliberately simpler than the visible legs/wings. These are static objective placements, not animated encounters. No new boss generation or rewards were added.

Both stand in 22 m-diameter objective floors. The reactor landmarks were moved to the outside edge of those floors after native review showed they blocked the chase-camera arms at the north/south entrances. Latest `gold-approach.png` and `power-approach.png` show the clear approaches.

## Validation and visual review

Final native run: **60 assertions passed, 0 failed**, with all four modules and both bosses imported. `native-review.json` records the actual run and model-source hashes. Checks cover ten real training units, five per team, all spawn slots, approved camera defaults, outer-wall camera/rear-foot clearance above the HUD, route endpoints and physics sampling along navigation paths, camp/boss approaches, swept collision, the current Drive Slam real-unit hold/cancel/damage contract, current HUD names, full 3.1 m Ult framing, current rhino, native capture sizes and actual boss body collision.

Native captures are real **1280 x 720** and **1920 x 1080**, not resized substitutes. Inspected the HUD at both sizes, boss approaches, module gallery, center/outer lanes, Ult, occlusion and edge views. Four allies and five opponents fit without panel overlap. Tall objective dressing originally hid the player at an entrance; it was relocated. The outer wall originally pulled the camera into a close-up that covered the feet with the player panel; this map now reserves a 14 m non-walkable camera margin beyond its low wall and puts distant skyline props farther away. The shared approved camera settings and code remain intact. Dither fading still handles the wall between the camera and player; a deliberately obstructed body region changed 10,473 pixels with the fade enabled.

The latest run baked navigation in about 370 ms. That is one observed bake, not a performance benchmark. Sampled shortest-path times below use a 3.5 m/s draft walk speed from the blue apron at (0,96), not future minion routes or an approved balance target:

| Destination | Path length | Draft walk time |
| --- | ---: | ---: |
| Mid at map center | 96.8 m | 27.7 s |
| West route at center | 112.8 m | 32.2 s |
| East route at center | 119.4 m | 34.1 s |
| Opposite base apron | 193.6 m | 55.3 s |
| Gold beetle south / north entrance | 96.4 / 110.6 m | 27.6 / 31.6 s |
| Wyvern south / north entrance | 92.9 / 117.0 m | 26.5 / 33.4 s |
| Near blue camps | 55.1 to 59.2 m | 15.7 to 16.9 s |

These sampled shortest paths differ slightly between sides because of navigation triangulation and different objective footprints. No competitive fairness or final match pacing is claimed. All tested routes reached their destinations and sampled clear against the actual physics.

Current 3v3 regression was rerun on November 11: **67 assertions passed, 0 failed**, including the updated red kangaroo roster. Log: `D:/dev/_scratch/map5v5/current-3v3-regression-nov11.log`. That run also emits 78 shared `kangaroo_cover` missing-metadata diagnostics from the existing player/kit interaction, plus the local certificate-store diagnostic. Passing assertions do not erase those messages. They are recorded for the shared-code owner; no unrelated kit fix was attempted. Native foundation runs report two texture-release diagnostics at engine shutdown; no script errors or failed foundation assertions occurred in the final native run. Neither issue is presented as fixed.

## Review artifacts and next slice

- `layout-board.png`: readable schematic derived from the built scene's exported route/cover/site data.
- `top-down.png`: native overhead render; `layout.json` is the same scene's exported data.
- `hud-1280.png`, `hud-1920.png`: actual native HUD frames.
- `gold-approach.png`, `power-approach.png`: existing bosses in their spaces.
- `batch-game-camera.png`: all four generated modules at the actual chase camera.
- `edge-clamp.png`, `occlusion-no-fade.png`, `occlusion-fade.png`: edge framing and fade review.
- `FOUNDATION.md`: dimensions, ownership, methodology and reproducible launch/review commands.

Next useful slice: Preston walks this draft and picks topology/scale. Then implement one three-lane wave-routing slice with the shared match owner, or one boss encounter with contest/reset/secure behavior, before economy or balance. No further Meshy jobs are queued. The foundation's HUD is intentionally inherited from the current pixel HUD; this task does not claim a new high-resolution UI art system.
