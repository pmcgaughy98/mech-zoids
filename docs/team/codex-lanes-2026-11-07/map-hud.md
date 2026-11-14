# Map and HUD lane: current November 11, 2026

**Latest direction, Revision 4:** Preston likes the rest of the layout and wants a SMITE-inspired correction to bosses being closed off from mid/jungle. Centers stay (-34,0)/(34,0); full rings become open inward half-bowls, mid barriers removed, broad mid and diagonal north/south jungle approaches added, backing walls retained outside. Current evidence: `docs/plan/foundry-5v5-2026-11-11-open-bosses/REVISION_4.md`. Earlier screening/side-only entrance goals are historical, not constraints. Shared camera/combat and original art preserved; no new paid generation.

Revision 4 verified: **142 native checks / zero failures, 6/6 real walking checkpoints**, player-camera approaches, overhead/board and movie frames inspected. The walking route enters from jungle and exits directly to mid. No new generation or peer messages.

**Latest user correction, Revision 3:** both boss courts moved back **inside** the outer lanes: gold west (-34,0), wyvern east (34,0). Mid-facing wall masses opened to fit courts; two gates now approach from each outer lane. Camp loops, return roads and other placement refinements retained. The 45-second minimum / mid-wipe timing requirement is withdrawn, not a design constraint to preserve. Current evidence and validation: `docs/plan/foundry-5v5-2026-11-11-inner-jungle/REVISION_3.md`. Revision 2 below is historical.

Revision 3 verification completed: **102 native checks / zero failures, 7/7 actual walking checkpoints**. Local navigation radius increased to 1.25 m after the physics review caught diagonal voxel-corner clipping. Updated board, player-camera approaches, overhead and walkthrough are in the inner-jungle evidence folder. No paid generation or shared-owner edits.

## Current authorized revision: objective routing

Preston asked for Mech Hub/tool catch-up and a deeper map after noting that a mid wipe made beetle and wyvern an easy chain. Read the actual **Run the mech MOBA hub** transcript, installed level-design skills and the new extractor inventory; verified umodel against the installed closed SMITE package in scratch only. Godot AI has no editor session and Summer Engine is not running, so the actual native Godot CLI supplies tests/captures. No paid generation in this revision.

Updated `scenes/map5v5/foundation.tscn` through its map script: 220 x 240 m footprint, three curved routes, four camp loops and returns, home service roads, connected jungle wall groups, scouting recesses and two separately entered outer boss courts. Beetle (-88,0), wyvern (88,0). Shortest gate rotation now 47.6 s versus 17.4 s; mid approach approximately 27.5 s versus 8.7 s at 3.5 m/s. This is draft traversal timing, not proof of objective balance. Both models remain static previews. Current revision details and validation: `docs/plan/foundry-5v5-2026-11-11/REVISION_2.md`; study/tool stocktake: `docs/reference/5v5-objective-routing-synthesis-2026-11-11.md`. No other lane's gameplay/camera/model files changed; no peer messages or new agents.

## Prior asset-delivery slice

Revision 2 completed: **105 native checks / zero failures**, **7/7 real movement waypoints**, source hashes/budgets verified. Inspected native player-camera/overhead/HUD views and frames from the 39.7 s `walkthrough.mp4`. Runtime log records the Windows certificate-store startup diagnostic and two texture-release exit warnings, with no final script errors. Full evidence and remaining balance limits are in REVISION_2.md. No further generation queued.

Caught up to Claude again on Preston's request. Current registrations: gorilla v32, rhino v52, kangaroo r9, hippo r10, pangolin r4; 20 other catalog bodies remain base proxies. Preserve Fault Line / Drive Slam, red's kangaroo, the newer camera edge handling, current albedo treatment and smooth shared FX. Removed this foundation's now-redundant HUD workaround after Claude's fallback fix. No shared combat, camera, roster or art-owner files changed.

Preston confirmed wyvern and gold beetle as the objectives and supplied the rigged-downloads folder. Both existing models are placed as viewing copies in the separate foundation, originals hash-verified unchanged. No new boss generation, animation or reward logic. Meshy environment batch completed: four textured modules, eight successful stages, exactly 120 credits; final observed account balance 860. Final native foundation review: 60 assertions pass; current 3v3 regression: 67 assertions pass, with existing shared diagnostics documented. The source/task manifest and final native evidence are in the new map folder. Launch: `scenes/map5v5/foundation.tscn`; final details: `docs/plan/foundry-5v5-2026-11-10/DELIVERY.md`.

Active on Preston's explicit November 10 5v5/Meshy request. The initialization below is historical, not the current authorization or main-scene state. Project Play now starts 3v3 Arena Play. Read `docs/team/MAP_5V5_MESHY_HANDOFF_2026-11-10.md` and `docs/plan/foundry-5v5-2026-11-10/FOUNDATION.md`.

Current slice: separate `scenes/map5v5/foundation.tscn`, proposed three-route 160 x 220 m Foundry map, five spawn slots per team, real current roster/player/camera, ten passive training bodies, training HUD/minimap, authored collision/nav and reserved gold/power boss floors. Preserve 3v3 and current authored trials; do not claim a complete 5v5 match or fully animated fleet. Current camera: 12 m / 13 degrees / look 3.2 / FOV 60.

Initial Meshy authorization was up to four environment assets, maximum 200 existing credits, direct API only, one task at a time, no rerolls/purchases/fal/Anthropic jobs. Verified starting balance 1,010; completed batch cost 120 credits. Tasks/requests/raw downloads/hashes live in `art/environment/foundry_5v5/source/`; optimized GLBs and packed native workspaces are separate. Final actual spend and validation are recorded in DELIVERY.md. No further jobs are queued.

Catch-up includes current arena refresh/model pipeline, hand energy, camera/lighting, boss research, latest Game Feel/Factory chats and relevant current Claude conversation records. No peer messages or additional agents/chats. Next after this slice: Preston reviews topology/readability, then explicitly choose the next gameplay or visual slice. Shared three-lane waves, 5v5 bot decisions, economy, boss encounters and networking are not silently added.

## Historical initialization, November 7

Ready for Preston. Scope: arena presentation and layout, HUD, minimap, pits and map readability in `D:\dev\new-mech-rpg` only.

Read CLAUDE.md, START_HERE.md, how-preston-works.md, mech-sessions-2026-11-05.md and HUB_HANDOFF_2026-11-04.md as historical context, plus the existing arena layout, map skill-up and HUD notes. No applicable AGENTS.md was found in the project or checked parent locations. Current setup directions take precedence over old instructions to contact lanes or run Godot.

## Current state from files

- The current map is the 3 v 3 side mode: one lane, 84 x 156 m, a tower and core per team, two camps and one pit per team, and a central plaza. The proposed 5 v 5 main-mode map has not been started in this lane's notes.
- `scenes/moba3d/arena_blockout.gd` builds the layout, structures, dressing, nav and objective presentation. Foundry is the selected look. Minimap, fog of war, `border_kit` and `floor_zones` are enabled by default. Latest recorded visual slices are the November 6 border kit and floor zones: slag jungle, plaza stage and spawn chevrons. The notes still flag repeating jungle patches and a backdrop barely visible over the edge wall.
- `scripts/moba3d/match_hud.gd` explicitly records map-lane ownership since November 5. Preston chose layout B: player block bottom centre, minimap bottom right, score and wave information above, ally/enemy frames at the sides, kill feed below allies. Low-health, cooldown, tower-aggro, recall/death/victory and aim-over-panel presentation exist. Ability icons remain stand-ins; SLOT_NAMES and ICON_OF currently cover rhino, gorilla and fennec, while arena_play's current Tab list contains seven machines.
- `scenes/moba3d/arena_minimap.gd` paints the layout and shows units, structures, vision-filtered enemies, pits and beacon. It turns 180 degrees for red. Its scale is 0.36 px/m: 31 x 57 map pixels plus a four-pixel frame at the 320 x 180 base canvas.
- `arena_pit.gd`: two runtime capture points, 9 s solo / 6 s with two / 4.5 s with three, contested pause, 3 s empty hold then decay, 90 s lock and 10 m sight while locked. Ownership feeds stronger new waves through game feel's reward code (0.25 hp/damage bonus per pit, a tuning placeholder).
- `arena_beacon.gd`: plaza capture appears at 4:00, returns 5 minutes after a take, and uses pit-style capture. Game feel's reward disables the enemy tower for 30 s. HUD/minimap presentation is wired. Objective values remain untuned.
- The November 6 simulation notes report six 15-minute all-bot matches without a winner, no pit takes and almost no tower damage. This is historical evidence, not a run today. Bot objective decisions and match balance belong to game feel; sound belongs to the sound lane.
- The checkout already contains many modified and untracked files. They were left untouched. Older notes conflict about commits and older unfinished lists include work later built; current files and later dated entries are the better starting point.

## Test scene and verification boundary

Use `res://scenes/moba3d/arena_play.tscn` for the real match and HUD. It instances `arena_blockout.tscn`, then creates MatchDirector and MatchHud. Use `arena_blockout.tscn` alone for map inspection. Project Play still starts at `res://scenes/title.tscn`, so select the arena scene explicitly for a lane test.

Existing checks/tools: `tools/map/arena_check.gd`, `pit_check.gd`, `beacon_check.gd`, `wall_fade_check.gd`, `zones_look.gd`, `hud_shot.gd`, and `tools/debug/match_check.gd`. Historical notes report arena 24/24, pit 22/22 and match 67/67; none was rerun today. `hud_shot.gd` currently resizes captures to 1280 x 720, so its output alone cannot validate native 1920 x 1080 overlap.

## Next useful slice, proposed only

Complete the HUD's outstanding native-resolution readability check at 1280 x 720 and 1920 x 1080 in arena_play. Cover the player block and minimap, tower aggro and aim under a panel, pit capture/lock, and beacon countdown/structure bar. Check the seven currently selectable machines for blank ability slots. Keep any resulting fixes within this lane's HUD/minimap presentation; do not change kits, bots, camera fit or reward numbers. Deliver inspected frames and a concise list of any remaining issues. Before a future run, follow the single-Godot-process rule and check changed scripts with --check-only.

Initialization changed only this file. Godot was not launched; no gameplay, assets, audio or other lane files were changed. No commits, paid tools, generation, purchases, fal.ai credential access, new chats or peer messages. Stopped ready for Preston.
