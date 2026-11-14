# Tripo, Meshy and MeshForge for our mechs

**Decision after this review, 2026-11-09:** Preston dropped Tripo and chose **Meshy and MeshForge**. The findings and unrun trial proposals below are historical evidence, not authorization to pursue Tripo.

## Account access, verified

Preston signed into Tripo Studio in the connected browser on 2026-11-09. Its header showed **200 credits**, and its account menu showed the **Free** plan. The supplied API credential separately passes authentication and reports **0 API credits**, 0 frozen. No billable tasks, credit purchases, transfers or model uploads were made.

Official guidance confirms separate balances: https://www.tripo3d.ai/help/api-plugins/tripo-studiotripo-api . Tripo advertises a one-time 1,000-API-credit benefit for eligible paid Studio subscribers (https://studio.tripo3d.ai/cli); this is not available merely because a Free Studio account has 200 credits. We did not claim a benefit or upgrade.

Preston's restriction: **browser for credits only, not tool use**. Consequently do not generate, rig, animate, export or otherwise operate asset tools through Studio UI. Use the connected CLI/API. The current 200 Studio credits cannot fund that API workflow. Do not suggest buying more as if purchase were already authorized.

## Findings

| Need | Tripo | Meshy | Existing MeshForge connector |
|---|---|---|---|
| Generate an asset from references | Text/image/multiview models; PBR and post-processing | Text/image/multiview models, textures and post-processing | Image-to-3D generation uses the user's fal.ai account and is paid; the connector also imports existing GLBs |
| Custom motion from a written action | Studio documents 1-10-second Text to Motion and sequences of up to five segments. Installed CLI 0.11.2 exposes check/rig/preset retarget; no custom-motion command was listed | A documented Text to Motion API generates standalone FBX (Prime) or BVH (Swift) clips, with no input character required | Presets plus explicit bone keyframe specifications; not the same as an ML text-to-motion generator |
| Creature rigs | API lists quadruped, hexapod, octopod, avian, serpentine, aquatic and others. This does not imply all can use every animation preset | Web UI supports quadruped and Smart Rig for other shapes, but Smart Rig cannot use the animation library. The documented rigging API is humanoid-focused | Humanoid, humanoid-with-tail, quadruped and chain templates, editable draft joints and weights |
| Our rigid armor and approved rig | Auto-rig is a candidate, not permission to replace the approved rig/weights | Same limitation; standalone generated motion may be useful as a donor | Direct pose/rig control and inspection is useful for precise correction; it still requires us to author a convincing action |

There is substantial overlap. Tripo's newer Studio motion workflow and skeleton choices warrant a controlled trial, but we have not tested a new Tripo output on our mechs and cannot claim better animation quality than Meshy. Meshy now has custom text-generated motion too, including an actual documented API route.

## Video observations

https://www.instagram.com/p/DbX99e5g6YK/ plays in the browser. Author: tomsilf_motion. Sampled portions showed a sword being edited in Blender, material-node work, and a smoke-ring effect in a Blender viewport. This is evidence of a combined workflow, not proof that Tripo exports those combat particles or complete game effects. We did not obtain a full transcript or successful media download. Shader nodes, smoke simulations and video polish do not become Godot gameplay VFX just by exporting a model.

## Recommended first test, not run

Generate one short protective arm gesture as donor motion, then adapt it to a copy of the accepted gorilla rig. Compare with the currently authorized hand-authored shield-cast trial, keeping both models, camera and playback speed consistent. Judge intended action, weight, palm/armor contact, supported knuckle, joint limits and recovery. Preserve approved chest-beat timing, model proportions and rigid plate behavior.

For an API-only custom-motion trial, Meshy's documented standalone motion endpoint is currently the clearer route. A Tripo API trial can test a rig and preset motion, but that is not a test of Studio's Text to Motion. Neither route is authorized to spend credits by this research task. Quote the exact account cost before any paid run; credits from different services and product wallets are not interchangeable.

Potential later Tripo asset tests: segmentation/local mesh repair and topology cleanup on a disposable copy. These may help repair generated anatomy, but do not prove a general improvement over Meshy's corresponding tools. Do not remesh or auto-rig the accepted game source without preserving originals.

## Sources actually read

- Tripo Studio motion workflow and limits: https://www.tripo3d.ai/blog/rigging-animation (Firecrawl full page); Studio rigging guide: https://www.tripo3d.ai/product-doc/module-post-processing/rigging-animation
- Tripo API rigging: https://developers.tripo3d.ai/en/docs/animations-rig ; retarget: https://developers.tripo3d.ai/en/docs/animations-retarget
- Tripo CLI installed source/help (0.11.2) at D:/dev/_tools/tripo/node_modules/tripo-cli ; connection usage in that tool folder's README.
- Meshy Text to Motion API: https://docs.meshy.ai/en/api/text-to-motion ; Prime costs 10 Meshy API credits and exports FBX, Swift costs 3 and exports BVH; duration 2-10 seconds in 0.5-second steps. These are documented rates, not a charge or account-balance check.
- Meshy animation API: https://docs.meshy.ai/en/api/animation (motion_task_id retarget is biped-only)
- Meshy web rigging: https://docs.meshy.ai/en/webapp/guides/3d-model/rigging ; API rigging: https://docs.meshy.ai/en/api/rigging
- Live MeshForge connector method catalog and preset metadata, read only. No model or clip was modified for the comparison.
