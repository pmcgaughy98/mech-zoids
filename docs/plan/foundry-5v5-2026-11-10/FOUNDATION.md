# Current layout: inner-jungle objectives

Preston corrected the placement after Revision 2. Both bosses are inside the outer lanes and now open toward mid/jungle. See [Revision 4](../foundry-5v5-2026-11-11-open-bosses/REVISION_4.md) for current layout and verification. The original asset-delivery record below is preserved.

# Foundry 5v5 foundation, November 10

Status: delivered November 11 after the November 10 batch start. Dimensions, topology, spawn assignments and travel targets are proposals for Preston, not settled design. This is a separate walkable training foundation, not a complete 5v5 match. See DELIVERY.md for verification and costs.

## Current context used

The current Arena Play starts at `scenes/moba3d/arena_play.tscn`. The latest registry has 25 bodies: 20 base proxies and five authored trials, plus the legacy lobster selection. Gorilla v32, rhino v52, kangaroo r9, hippo r10 and pangolin r4 are registered. That does not certify every kit, effect or animation as finished. This foundation inherits the current roster/swap/input code and shared player, camera, model and combat contracts. It does not overwrite those files, the catalog, rigs, kit scripts or the playable 3v3 map. F8 remains the test selector.

Read the November 10 arena refresh, model pipeline, Shield Drive energy and jungle-objective synthesis, then the newer Claude records and current scripts on November 11. Preston explicitly confirmed wyvern and gold beetle as the objective identities. Their existing rigged GLBs were found in `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/` and are placed as separate grounded viewing copies. The 23 beetle bones and 46 wyvern bones are preserved; neither file has authored animation clips. Boss encounter logic and rewards are not implemented here. No boss generation or replacement art was ordered.

Recent Claude records checked include the November 9 lighting messages, November 10 hub/map audit and evening catch-up, and November 11 model, look, kit and effect reports. The new scene uses the current Foundry grade values from `arena_blockout.gd` and the approved distance 12 / pitch 13 / look height 3.2 / FOV 60 camera, including its newer edge/wall handling. Atmospheric fog is reduced to 0.0018 for the longer draft space; gameplay fog of war is explicitly absent here. Existing 3v3 fog remains intact. Claude fixed the shared HUD's unnamed-kit fallback; the redundant foundation workaround was removed. The current gorilla Fault Line / Drive Slam redesign and red team's kangaroo choice are inherited, not reverted to the earlier grab/Drive kit or fennec roster.

## Proposed layout

| Part | Draft dimensions / placement |
| --- | --- |
| Overall rectangle | 160 x 220 m; x +/-80, z +/-110 |
| Bases | Blue south at z +91, red north at z -91; 17 m radius |
| Five spawn slots each | x 0, -4, +4, -8, +8 at z +/-98; 4 m spacing |
| Mid route | x 0; core-to-core 170 m; 16 m floor width |
| Outer routes | Bow through x +/-54 at z +/-66, x +/-58 at z +/-30; 16 m floor width |
| Jungle connectors | z +/-52 and +/-12, from mid to each outer route; 8 m marked width |
| Camp clearings | x +/-27, z +/-48; 5 m radius; installation placed beyond the encounter floor |
| Gold beetle/economy space | (-29, 0), 11 m encounter radius, with existing model preview |
| Wyvern/power space | (+29, 0), 11 m encounter radius, with existing model preview |
| Objective approaches | From north/south connectors, open to mid and the outer route |
| Cover islands | Mirrored 12 x 14, 9 x 12 and 7 x 13 m envelopes, 2.6-3 m high |
| Perimeter | 3.6 m wall; distant industrial silhouette outside playable bounds |
| Camera clearance | 14 m non-walkable margin outside the perimeter; skyline moved beyond it |

The original map's 30-degree camera arguments are obsolete. The flatter camera sees a horizon, longer lane lengths and more border silhouette. Three routes, separated camp pockets and two contested major spaces are structural lessons from the existing SMITE/Paragon/League studies, not a copied map. The three-lane topology remains a proposal. Alternatives: two outer routes with a central objective region, or a smaller three-route footprint after walking this one.

The whole foundation stays flat at y=0 because the current player movement owns flat-ground motion. No decorative slope is falsely presented as working elevation. Ramps/elevation need a separate ground-height movement slice before they can be gameplay truth.

## What runs

- Five real match-unit bodies per team, one controlled by the player, nine passive training bodies. Current model/kit trials, health, hold state, cooldowns, death/respawn and recall are reused.
- No lane waves, economy, boss combat, autonomous 5v5 strategy, match win or networking is claimed. The training director deliberately holds bots and disables the draft structures' firing logic. Camp targets reuse existing neutral behavior; major bosses are static rigged placement previews with authored local body collision.
- Current pixel player HUD plus four ally cards and five enemy cards. Larger map at bottom right, drawn from the same route/island/site data. Full visibility, explicitly training mode. The map is north-up for the controlled blue player.
- F6 calls passive training bodies near the player when their destination is clear. F8 selects models; Tab cycles; WASD moves, Q/E/right-drag turns, 1-4 use current kit targeting, Space/LMB basics, B recall.
- Authored box collision, baked 1 m-radius navigation and shader occlusion fade stay independent from generated mesh geometry. Dressing cannot silently create a new nav hole. Installation collision is locally authored before baking.

## Tools and asset policy

Applied local skills: game-3d-asset-design, blender-export-pipeline and atlas-asset-optimization, including their relevant engine-import/checklist notes. Local Godot/Blender/Python handle construction, scale, pivots, triangle/texture reduction and native review with no generation fee. Built-in web retrieval verified official Meshy endpoints and costs; paid Firecrawl retrieval was not used. No separately billed fal/Anthropic tool, image generation, purchase, new chat, subagent, peer message or commit.

Meshy direct API: four individual modules, one preview/refine stage at a time. Fixed Meshy-6, 20-credit mesh plus 10-credit 2K PBR refinement each, 120-credit planned batch under the 200-credit ceiling. Initial verified balance 1,010 credits. Raw exports, request intent, submissions, terminal task metadata and hashes are preserved under `art/environment/foundry_5v5/source/`. Task ids are persisted before polling; uncertain POSTs are never automatically repeated. Sources/workspaces have `.gdignore`; only reduced runtime GLBs import into Godot. No rerolls.

Modules: wall (6 x 2.6 x 1.6 m), pillar (2.4 x 4 x 2.4 m), camp installation (3.6 x 3.2 x 3.6 m), objective reactor landmark (5.2 x 5 x 5.2 m). Ground-centered pivots, meters, glTF +Y up. Triangle targets after local reduction: 5k / 4k / 6k / 8k, at most four materials, maximum 1K runtime textures. Raw source textures remain in the provider exports. GLBs and packed Blender workspaces are separate. Runtime JSON files record actual budgets, hashes and source metadata. No per-file license string is invented if the API supplies none.

Official sources checked November 10:

- [Text to 3D API](https://docs.meshy.ai/en/api/text-to-3d): two-stage endpoint, explicit model, remesh/polycount, texture controls and task retrieval.
- [API pricing](https://docs.meshy.ai/en/api/pricing): Meshy-6 preview 20 credits, 2K refinement 10 credits.
- [Balance API](https://docs.meshy.ai/en/api/balance): authenticated free balance query.
- Existing game research: `docs/reference/smite-camera-framing-2026-11-09.md`, `docs/reference/jungle-objective-synthesis-2026-11-10.md` and `docs/plan/moba-map-skillup-2026-11-05.md`. Their source-read limitations still apply; no new map copying or current balance claims.

## Launch and repeat review

Open `scenes/map5v5/foundation.tscn` and use F6 in Godot, or run the lane-owned `tools/map5v5/launch_foundation.ps1`. The project's main scene remains 3v3 Arena Play.

One real Godot application at a time. Do not terminate other previews. Headless review: `--headless --path . --script res://tools/map5v5/foundation_review.gd`. Native review: omit --headless and append `-- --render`; captures are real 1280 x 720 and 1920 x 1080, never enlarged substitute images. Logs and metadata identify the current run. See `DELIVERY.md` for final spend, test totals, travel measurements, visual findings and rough edges.
