# Arena Play refresh, 2026-11-10

Preston requested a thorough check of what Arena Play was missing, integration of current Codex/Claude work, and a repeatable base for putting the other models into the scene. No paid tools or generation were used; nothing was committed.

## Scan and decisions

Read the current arena, model adapter, player, kits, bot/director/minion/monster and HUD code; catalog entries and source exports; current Codex Gorilla Animations and Game Feel and Kits messages; and recent Claude game-feel, gorilla/rhino, camera and hub conversation records. In particular, Claude's latest game-feel notes said the real dash/held hooks were still waiting on the next export. The local completed Codex review already supplied those selected moves. Rhino v39/piston/ring work remained in progress, so the completed v38 export was used for the base.

| Before | Now |
|---|---|
| Main gorilla registered v26, with old Fling and no selected Drive/cast clips | Runtime copy of completed authored review includes corrected chest-beat exit, self/ally cast, grab-slam and all four Drive phases |
| Grab/slam and Drive worked only with isolated review controllers/training mannequin | Arena-owned controllers act on actual match machines and minions; hold state blocks movement, bot thinking, inputs and basics; damage occurs once at contact |
| Bound still performed its old unanimated leap | Slot 3 uses Shield Drive: brace, game-controlled movement, first collision or wall, hit/brake recovery |
| HUD said gorilla slot 2 was none and slot 3 Bound | Grab Slam / Shield Drive, with existing placeholder icon vocabulary |
| Rhino and most other playable units still displayed sprites | Completed v38 rhino copy and 23 static catalog bases attach through shared body interface |
| Seven-machine Tab roster | F8 direct selector; 25 catalog bodies plus preserved legacy lobster choice, with correct match identity |
| New body could consume another animal's kit by falling through to rhino | Unfinished identities receive a provisional test basic and disabled ability slots; existing implemented kits remain their own |
| New inherited gorilla kit would be silent because audio checked only its immediate script class | Audio resolves base kit classes and uses current contact cues; old leap/chest-beat-on-2 mappings removed for this kit |
| Real rendered multi-mech scene exceeded shader instance-uniform buffer | Hit flash uses lazy per-mech material copies; separate units still flash independently; shield overlay remains available |
| Action playback could queue the first update and delay low-fps release | Action is applied immediately with advance(0), animation updates before event polling; 0.25-second release tested at 15/60/120 fps |

The existing SMITE-style camera fit, industrial arena, shared model look, match rules, towers/cores, waves, camps, pits/beacon, recall/respawn and fog remain in use. The two new boss concepts are still art/reward proposals, not silently added encounters. New minion art is not treated as an available rigged runtime asset.

## Shared manufacture route

Read `docs/art/moba/ARENA_MODEL_PIPELINE.md` for the command-line builder, inspection and registration workflow, profile format, explicit readiness levels and test recipe. `art/arena_models/roster.json` is generated from the existing catalog and keeps each model's exact four sheet links, original source hash and editable workspace.

Current game copies: `art/arena_models/gorilla.glb` and `rhino.glb`. Original artist sources/scratch exports are preserved. Rebuild/check verifies the copied files' hashes. Static bodies use the catalog's existing reduced viewing copies, with runtime normalization and hover/root presentation. No meshes were remeshed, newly generated or auto-rigged.

## Validation and visual evidence

- Existing `match_check.gd`: **67 pass, 0 fail**, including full match simulation, waves, objectives, towers/core, kit/basic cooldowns, health, healing, recall, death/respawn and win.
- New `arena_roster_check.gd`: **104 checks pass at each of 15, 60 and 120 fps**. All profiles loaded with finite arena dimensions and correct identities; native current gorilla clip set; pre-release interruption; once-only timed release; no delayed cage after interruption; real machine hold/impact/cancel; real minion hold/cancel; Drive contact and no doubled shove damage; return of control/manual clock; correct HUD names; independent per-mech flash; inherited kit audio registration. Logs: `D:/dev/_scratch/arena-roster-check-{15,60,120}.log`.
- `build_arena_roster.py --check`: 25 entries, 2 authored exports; registry/copy hashes current.
- Validated dry-run registration with the rhino example profile. It checks a real rig, idle/walk aliases and action/event bounds without changing registration.
- Native NVIDIA/OpenGL render captured **every model in the actual arena**, plus selector, normal startup, real-victim lift/ground contact and cage. Images/logs: `D:/dev/_scratch/arena-refresh-2026-11-10/`, `arena-native-review.log`; board `roster-board.jpg`. Native capture is for visual inspection, not a stable performance benchmark while loading models.
- Final native run with normal local shader-cache access completed with **no script, shader-buffer or shutdown errors**. Earlier sandbox-only cache/certificate write/read failures are retained in earlier test logs and were not addressed by changing gameplay settings.
- The earlier isolated review body now uses the inherited manual-clock field, preserving compatibility with its launcher after that interface moved into the shared adapter.

One test fixture initially used the wave spawner's random scatter when checking a precisely placed minion capture. It now explicitly sets the minion position after spawning. A separate 15-fps check exposed the real queued-playback delay; that implementation was fixed rather than simply expanding the deadline.

The initial rendered pass hit the GPU's shader-instance allocation limit. Godot's own [instance-buffer report](https://github.com/godotengine/godot/issues/114949) explains the same Compatibility limitation; the local fix avoids those allocations for armor hit flash. It was validated with two separately flashing mechs. Off-tree model templates are freed on arena exit to prevent cache-owned node leaks.

## Deliberately rough and still open

- 23 base bodies have no authored skeletal locomotion; grounded bodies slide and flyers have simple hover/root motion. This is base arena access, not a completed animation fleet.
- Native rhino horn/brace/charge presentation is bridged from its old kit clock. Ground pound still lacks a completed body clip/piston export. v39 and the chosen notched mint disc are not claimed to be integrated.
- The real match grab carries the target's existing whole body and grounds/stuns it at impact. It does not create the articulated training mannequin's crumple motion on arbitrary enemy rigs. Already-busy non-interruptible kits and braced rhinos are not captured by this base hook.
- Existing authored armor intersections, anatomy/eye corrections and source-art polish remain open. Numeric scale/health/damage/cooldowns are provisional, as before.
- Other unfinished kits have no fabricated full abilities. Existing one-slot/one-basic kits show only their implemented slots.
- No new rigging/retargeting service, paid animation generation, boss encounter, store/economy, networking or multiplayer authority was added.

Use `Launch Arena Play.cmd`; F8 chooses bodies, Tab cycles, WASD moves, 1–4 use implemented kit slots, Space/LMB attacks, B recalls. One actual Godot process at a time; helper MCP processes are not previews.
