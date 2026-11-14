# Foundry objective-routing revision, November 11, 2026

**Superseded by Preston's placement correction:** [Revision 3](../foundry-5v5-2026-11-11-inner-jungle/REVISION_3.md) places both bosses back inside the outer lanes. The layout, long-rotation target and evidence below are historical.

Built in response to Preston's concern that a team winning mid could easily take beetle and wyvern back to back. Launch the separate training scene `res://scenes/map5v5/foundation.tscn`, or run `tools/map5v5/launch_foundation.ps1`. This replaces the first foundation layout; 3v3 remains the project's normal Play scene.

## Concrete changes

| Placement / route | First foundation | Revised foundation |
|---|---|---|
| Walkable footprint | 160 x 220 m | 220 x 240 m |
| Gold beetle center | (-29, 0) | (-88, 0), west of outer lane |
| Wyvern center | (29, 0) | (88, 0), east of outer lane |
| Mid to nearest boss approach | 8.68 s | Gold 27.52 s / wyvern 27.50 s |
| Shortest approach-to-approach rotation | 17.35 s | 47.62 s |
| Boss access | Adjacent open encounter floors | Two separate north/south gates per walled court |

Travel values are baked-nav shortest paths at 3.5 m/s. The old measurements target the old inside approach positions at (-29, 9) / (29, -9); the new measurements target the new court gates. They exclude boss clear time, abilities and combat. Source measurements are `v1-rotation.json` and `native-review.json`.

Added connected jungle wall masses with capped ends and buttresses, four camp loops, camp return paths, home service roads, curved lane approaches and lane-side scouting recesses. Placement has a movement or sightline job rather than adding independent decorative obstacles. Each boss has two entry markers 18.4 m apart; mid cannot see straight through the jungle to either boss. Court colors distinguish the beetle's Mint Yard from the wyvern's Reactor Vault; these working names are proposals.

The existing four Meshy environment modules dress the joined walls, camps and courts in 118 instances. Source assets, packed Blender workspaces and the original rigged boss downloads are preserved. **No additional paid tool runs or credits.** Previous generation batch remains 120 credits.

## What the wipe check establishes

Starting at mid, the fastest modeled first-objective-then-second route is approximately **75.1 seconds**, even assuming instant boss clears. A defender respawns after the current **8 s placeholder** and can reach a nearby gate in another **36.8 s**, roughly **44.8 s total**. Both defending teams and both boss orders are checked separately.

That gives a return window under today's walk/respawn assumptions. It does not establish late-game balance. Boss encounters, rewards and clear times are unbuilt; movement abilities, larger respawn timers, wards and surviving opponents matter. A long enough wipe can still legitimately earn both bosses. The goal is to remove the trivial nearby chain and create a second commitment.

## Review artifacts and checks

- `layout-board.png`: labeled schematic exported from actual scene geometry, with rotated colliders and both entries.
- `top-down.png`: actual native overhead view; `mid-route.png`, `camp-loop.png`, `gold-approach.png`, `power-approach.png` show player-camera placements.
- `hud-1280.png` / `hud-1920.png`: native resolutions, no upscale presented as a native test.
- `walkthrough.mp4`: real 3.5 m/s player walking through the west camp loop into the beetle court, then an explicitly captioned cut to wyvern and overhead view.
- `walkthrough-checks.json`: actual arrival positions for seven movement waypoints; no waypoint teleports within the west route.
- `native-review.json`: route/physics clearance, all four gate combinations, spawn clearance, two-sided gate entry, mid sightline screening, swept collision, current gorilla combat/hold release, rhino availability, camera fit, fade, HUD sizes and module/boss placement.

Final validation: **105 native checks passed, zero failures**, including every gate pairing sampled against actual player-radius collision; **7 of 7 real walking checkpoints passed**. The 39.7-second MP4 was encoded from Godot's native movie and its frames inspected. Source/module manifest verification also passed, including both original boss hashes. The labeled board, both boss approaches, camp loop, overhead, camera fade and 1080p HUD were visually inspected.

Known runtime diagnostics: Godot reports failure to read Windows' root certificate store at startup and two texture-release warnings at exit. These are recorded in `native-runtime.log`; no GDScript parse/runtime errors occurred in the final run. The first recording aimed through an occupied camp-monster center and had an oversized caption; the route now circles that body and uses the project's UI canvas scale. The final recording contains no failed movement checkpoint.

This remains a traversal/training foundation with ten real passive units, current roster/kits and the approved shared camera. Bosses are static previews; there are no three-lane waves, economy, objective rewards or new 5v5 bot strategy. Shared gameplay/camera files were not changed for this revision. The earlier 67-check 3v3 regression from the asset-delivery slice was not repeated after these isolated map edits.

Reproduce the native review with Godot `--path . --script res://tools/map5v5/foundation_review.gd -- --render --require-batch`. Record the tour with `--fixed-fps 30 --write-movie <scratch-output.avi> --script res://tools/map5v5/foundation_walkthrough.gd`, then encode with FFmpeg. Close other actual Godot previews first; the launcher never kills another process.

Implementation: `scripts/map5v5/foundation_map.gd`, `foundation_minimap.gd`. Verification and artifact builders: `tools/map5v5/foundation_review.gd`, `foundation_walkthrough.gd`, `layout_board.py`. Study and tool stocktake: [objective-routing synthesis](../../reference/5v5-objective-routing-synthesis-2026-11-11.md).
