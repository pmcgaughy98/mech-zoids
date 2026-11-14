# Game feel lane: initialized 2026-11-07

Status: ready for Preston. Initialization only; no production work started.

Update 2026-11-10: Preston requested a broad Grok product/kit rethink preserving the gorilla foundations and existing models, with fennec's portal-heavy identity as a test case. Completed a staged Grok review and source-informed critical follow-up. Read `docs/plan/product-review-2026-11-10/README.md` for the current recommendation, exact scope and evidence limitations; full Grok report and addendum are beside it. These are proposals only. No gameplay, balance or art changes were made in this review. The initialization findings below are historical, superseded where the November 10 arena refresh and current source differ.

## Current shared-system status

- `machine_test_player.gd` has camera-relative WASD/arrows, normalized diagonal input, mouse-to-floor aim, right-stick aim priority, and a 0.4 s facing hold after ability presses. Movement direction remains independent of that facing hold. The existing aim check substitutes screen coordinates for the mouse; the real mouse path, gamepad and walking while aiming remain unverified in the latest match notes.
- `match_director.gd` routes basics through `Kit.basic_attack(target) -> bool`, with shared alive/busy/stun/cooldown gates. Accepted attacks start the kit's cooldown; rejected attacks do not. Range is edge-to-edge. Kits without a basic retain the stand-in shot.
- Shared hooks include scaled kit damage, healing, keyed speed boosts, cooldowns and match lifecycle signals. `arena_play.gd` repeats basic attacks while Space or left click is held. Latest notes list Tab selection through hummingbird and lobster; their addition did not change team rosters.
- `directional_sprite_3d.gd` preserves walk phase through view changes, compensates mirror flips, keeps separate tilted materials per sprite, and exposes action play/hold/resume plus `feel_offset` for contact nudges.
- `kit_feel.gd` now includes attacker lunge, target push and spark feedback at contact. It calls the camera's `kick` method when available for a local participant. This is newer than the November 4 hub handoff.
- Rhino dash/toss and tremor are implemented. Named `cue` events and sound mappings for dash, catch, landing and stomps already exist; `sound-lane.md` records installed choices. The old pending sound-trigger exception is not evidence of unfinished work now.
- Historical checks report match 67/67 and kit API 0 failures. These were not rerun during initialization and are not a fresh validation claim. Known open issues include stride versus ground speed and camera/bar overlap near the base wall.

## Ownership boundaries

- Own shared match controls, movement/combat feel, common kit integration and timing contracts. Primary shared files: `scripts/moba3d/machine_test_player.gd`, `directional_sprite_3d.gd`, `match_director.gd`, `kit_feel.gd`; integration also touches `arena_play.gd` and `match_teams.gd` when assigned.
- Each mech session owns its `*_kit.gd`, kit design and tuning. Shared kit implementation means reusable hooks and match integration; it does not authorize changing a mech's kit or balance.
- Walk/attack lanes own authored frames, packing and clip timing data. Preserve action frame/progress and explicit contact/hold/resume moments when integrating their output. Any frame-count or rate change needs its contact timing checked with the kit owner.
- Sound lane owns audio assets, choices and audio production. `scripts/audio/kit_audio.gd` is historically shared under game feel and already has sound-lane edits; coordinate the precise change before touching it. Preserve `used(slot)` for cast/cooldown, `impact(strength)` for impact feedback, and named `cue(name)` for exact sound moments. Never infer a named cue solely from impact strength.
- Camera lane owns chase-camera behavior, feet, shadows and camera fit. Preserve its camera kick interface. Map/HUD lane owns arena presentation, minimap and all of `match_hud.gd`, including aim overlays. Do not fix their files incidentally.
- No peer messages or additional chats during setup. No other lane's files, gameplay, art or audio changed.

## Likely next slice, proposed only

Verify the existing move-and-aim contract in the current arena before tuning it: diagonal movement while aiming elsewhere, ability press facing, movement during and after the facing hold, and held Space/left-click basics. Include busy, stun and cooldown rejection so a blocked action cannot turn or consume an attack unexpectedly. Start with the current rhino as a fixture; leave its kit and numbers unchanged.

Use actual input events through the viewport in a focused check rather than relying only on `aim_screen_override` or `input_override`; record the remaining physical-device limits honestly. Observe position, facing, selected view, accepted action and cooldown. Extend the existing shared API check only where these behaviors are not already covered. If a shared defect is demonstrated, fix only that defect and show one playable result. Gamepad hardware verification requires an available controller or Preston's playtest.

When assigned: inspect current shared-file changes first, ensure no other Godot process is running, run `--check-only` on changed scripts, then bounded relevant aim/API/match checks. Scratch: `D:/dev/_scratch/game_feel/`. No runtime launched for this setup.

## Context read

`CLAUDE.md`, `START_HERE.md`, `docs/team/how-preston-works.md`, `docs/team/mech-sessions-2026-11-05.md`, `docs/plan/HUB_HANDOFF_2026-11-04.md`, `docs/reference/zoids-legacy-structure.md`, `docs/team/CLAUDE_MECH_SKILLUP_HANDOFF_2026-10-12.md`, recent `docs/art/moba/match/MATCH_NOTES.md`, HUD handoff notes, sound-lane trigger updates, rhino status and relevant shared scripts/checks. No applicable `AGENTS.md` was found in the project/ancestor or destination paths inspected.

Current setup directions override historical instructions to build immediately, contact lanes or start sessions. No commits, downloads, paid tools, generation, purchases or saved fal.ai credential access performed.
