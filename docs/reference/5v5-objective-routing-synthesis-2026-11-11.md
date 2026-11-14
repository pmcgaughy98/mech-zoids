# Objective routing study and tool catch-up, November 11, 2026

**Current access correction:** [Revision 4](../plan/foundry-5v5-2026-11-11-open-bosses/REVISION_4.md) keeps the inner-jungle centers and opens the boss areas toward mid and jungle, with SMITE's interconnected objective approaches as the reference. Full enclosure / screening from mid is no longer the requested behavior.

**Latest direction:** Preston subsequently corrected the placement: both bosses belong in the inner jungle between mid and the solo / carry-support lanes. [Revision 3](../plan/foundry-5v5-2026-11-11-inner-jungle/REVISION_3.md) is current. The external-court proposal and anti-chain timing targets below record the preceding request, not an ongoing design requirement.

Preston's request: catch up with Claude Mech Hub, use the added tools and skills, and upgrade the map's placements. A wipe in mid should not make beetle followed by wyvern an almost free nearby rotation. This document records reference evidence separately from our proposed design.

## Read and checked

- Claude transcript with custom title **Run the mech MOBA hub**, session `a9294f90-ebb8-4ad7-8949-e74eebc65276`, including the recent substantive hub updates and extractor additions. The different `21a32…` session concerns rhino FX; it was not treated as the hub. Current checked-in files and live roster registrations take precedence over chat summaries.
- Project `CLAUDE.md`, `START_HERE.md`, `docs/team/how-preston-works.md`, current map handoff and map/HUD lane notes. Existing 3v3 and other lanes remain separate.
- Local skills read for this slice: `atlas-godot`, `blender-game-asset-artist`, `design-level`, `environment-kit`, `scene-composition`. Used their path/readability, collider/navigation, reused-kit and player-camera review guidance. `claude-3d-harness` and `watch` were inspected for capability; neither full workflow was invoked. No new model or transcription setup was needed.
- `D:/dev/_tools/extract/README.md` and the older October 12 synthesis tool roster. The older roster is historical, not proof of today's connected services.

## Finished-game evidence

**Read:** Riot's [Season 2024 Map Changes](https://www.leagueoflegends.com/en-us/news/dev/dev-season-2024-map-changes/). The useful structure is multiple objective approaches, fair routes for both sides, and terrain that actually changes movement. Small disconnected rocks need not create useful decisions. Our inference: joined Foundry wall groups should screen mid, while distinct entries let either side approach or retreat.

**Read, focused on map section:** Predecessor's [V1.14 Daybreak changes](https://www.predecessorgame.com/en-US/news/patch-notes/Patch_notes_1.14). Jungle flow, lane entry sightlines, dead ends, pit layout and lane curvature are treated together. Our inference: give camps return loops and bosses readable staging routes rather than merely scatter extra props.

**Search excerpt only, not a full-page study:** Predecessor's [V1.13 notes](https://www.predecessorgame.com/en-US/news/patch-notes/V1-13-patchnotes) describe reducing map size to improve rotation. This cautions against solving every problem by making the whole arena enormous. Here width increases mainly to move bosses outside the outer lanes; the longitudinal footprint grows only 20 m.

**Limited evidence:** the SMITE 2 closed-alpha page returned mostly site navigation, so its search excerpt was not used as measured layout evidence. Local SMITE camera study already exists, but no exact Conquest boss spacing is asserted here.

No reference game art, maps, code, names or extracted data were put into our game. The timings below are measurements of our own scene, not estimates of those games.

## Current tool stocktake

| Tool / resource | Actual contribution or reason not used | Cost for this revision |
|---|---|---|
| Godot 4.7.2 CLI | Runs the actual training scene, navigation/physics checks, native 720p/1080p captures and real movement movie | No service charge |
| Godot AI MCP | Session-list probe returned no connected editor; did not pretend it edited this scene | No paid job |
| Summer Engine MCP | Context probe returned engine not running; existing project tested through Godot CLI instead | No paid job |
| Blender 5.2 and packed local workspaces | Existing optimized modules and preserved rigged objective copies reused; no need to regenerate or alter rigs | No new job |
| Meshy | Four previously approved modules reused in 118 placements; their original eight stages cost 120 credits. No new task submitted | **0 new credits** |
| UE Viewer / umodel | Verified help and enumerated the installed, closed SMITE game's Conquest package with `-game=smite`; scratch logs only. Enumeration proves access, not object positions or travel times | Local tool |
| FModel | Installed; target SMITE 2 / Predecessor / Rivals games not present per extractor inventory. No claimed inspection | Not run |
| Source 2 Viewer | Installed; Deadlock absent per inventory | Not run |
| OWLib DataTool / TankView | Available for installed Overwatch; hero asset extraction does not answer this MOBA route question | Not run |
| Blender UEFormat / PSK-PSA importer archives | Available if later animation study needs them; no extracted mesh was needed here | Not run |
| Built-in web | Read official Riot and Predecessor design explanations | No paid generation |
| Firecrawl connector | Available; built-in browsing supplied the needed primary sources | Not run |
| Keyframe / MeshForge, Retro Diffusion, PixelLab/SpriteCook skill inventory | New art/animation generation does not resolve boss placement; historical availability is distinguished from a tested connection | No jobs, no credits spent |
| Python/Pillow and FFmpeg | Geometry-derived labeled layout board and encoded walkthrough; no invented reference image | Local tools |

SMITE enumeration logs are outside the project under `D:/dev/_scratch/map5v5/smite-map-study/`. A minimap texture / objective transform was not established, so no numeric SMITE map claim follows from those logs.

## Implemented proposal, not canon

The separate 5v5 foundation now has three curved routes, four camp loops, home-side service roads, substantial joined cover masses, scouting recesses, and two externally placed boss courts. Gold beetle is west at (-88, 0); wyvern is east at (88, 0). Each court has north and south entries 18.4 m apart. The floor footprint is 220 x 240 m. These are editable proposals in `scripts/map5v5/foundation_map.gd`.

The old short rotation measured 17.35 s. The revised shortest gate-to-gate path measures 47.62 s at the current 3.5 m/s walk speed. Mid-to-gate grows from 8.68 s to approximately 27.5 s. Physics clearance and actual player walking supplement navigation queries; a diagram alone does not prove a playable route.

Alternative considered: only move the two boss models farther apart across open ground. That changes distance but leaves direct access and no terrain decisions. The implemented connected terrain and separate entry routes address that missing structure.

Still falls short of match balance: bosses are static placement previews, no health/reward/clear-time loop; no three-lane waves, economy or 5v5 decisions. Mobility, late respawn timers, surviving defenders, wards and real clear times can change the outcome. Current tests describe an unboosted walk under an 8 s respawn placeholder, not a guarantee that nobody can ever earn both objectives.

See [revision delivery](../plan/foundry-5v5-2026-11-11/REVISION_2.md), native evidence and walkthrough for the actual result.
