# Gorilla: Drive Slam + Fault Line prototype

Preston explicitly requested merging Shield Drive and Grab Slam into one move, freeing a slot and completing the kit. This supersedes the earlier optional two-button combo proposal. The merge is the requested behavior; Fault Line is the implemented replacement prototype chosen here for playtesting, not a final balance decision.

| Slot | Current move | Role |
|---|---|---|
| 1 | Hex Shield | Aimed ally/self protection and slow cleanse |
| 2 | Fault Line | Short ranged ground rupture and slowing zone; poke, wave clear, peel and engage setup |
| 3 | Drive Slam | Mobility into a single enemy-mech grab/lift/ground slam |
| 4 | Silverback Cage | Chest-beat taunts followed by the existing containment/ward cage |

## Drive Slam

One confirmation and slot-3 cooldown. Keeps the existing 29/120 s brace, 12 m/s travel for at most 38/120 s (3.8 m), collision and damage. A mech hit deals 24, stops Gorilla close and has no outward shove. A .055 s hitstop and .10 s impact recovery lead into the existing Grab Slam. A local .10 s bone-pose blend bridges the handoff; it is fully finished before the .18 s capture event, preserving the measured grip and the .60 s ground impact. Slam deals the inherited 28 once. Both hits together total 52 before any applicable effects; no bonus damage was added for combining the moves. Existing placeholder slot-3 cooldown is nine seconds.

Only enemy machines consume the takedown collision. Minions do not stop this charge or get grabbed; ordinary body collision behavior is unchanged elsewhere. A miss remains usable mobility, followed by braking. Bracing, death, stun, walls/cages and a recipient who escapes behind Gorilla or out of grab reach can prevent the follow-up. The target is the unit actually hit, with a frontal/range/line-of-sight check at handoff and the original measured grip check at capture. No target teleport, reach scaling, extra target switch or unconditional remote grab.

The old `fling(target)` public entry now starts this same slot-3 move for compatibility. It no longer offers a separate slot-2 grab. Bots and HUD now use the revised kit.

## Fault Line — first tuning pass

Gorilla already had protection, engage and an ultimate commitment, but little interaction while mobility was unavailable. This prototype gives him an aimed ground threat that can set up Drive or contest space in the cage without adding another stun. This follows the general principle of preserving clear opportunities to answer a champion's strengths ([Riot's counterplay discussion](https://www.leagueoflegends.com/en-gb/news/dev/quick-gameplay-thoughts-may-14/)); the proposed values below are ours.

- Uses the existing heavy ground-strike animation for now; this is not a newly authored bespoke Fault Line clip.
- Rupture releases on the clip's existing 50/120 s hit event. Interrupting before release launches nothing.
- Aim center clamps to six meters. A 9 m/s wave pierces eligible enemies; every unit can take damage only once across the traveling wave and landing burst.
- Damage starts at 22, respects the target's normal `hit` pathway when present, and does not damage buildings/allies.
- Landing field radius 1.5 m, lifetime 1.4 s. It refreshes the existing shared slow for .16 s while inside: current shared slow multiplier is .6 (40% reduction). Walking out clears it promptly. No knockup, stun, grab or repeated damage tick.
- Walls and closed cage panels block the wave; line/cage checks also prevent field effects across barriers. A released rupture may finish after the caster is interrupted; it is no longer an uncommitted cast.
- Keeps the existing medium/nine-second slot-2 cooldown provisionally. Range, damage, slow strength/duration, cooldown and minion-clear budget need playtesting.

Selection art now shows Fault Line's landing radius and uses the painted fracture stamp; Drive's preview identifies its combined move. Existing reactor atlas, shader and authored model/rig/other clips are preserved.

## Verification and review

`tools/debug/gorilla_targeting_2026_11_10/merged_run.gd` runs 25 focused checks. Current 15 and 60 FPS runs pass: single cooldown/damage counts, misses, minions, bracing, stun, walls, escaped/dead recipients, interruption during hold, Fault Line release timing, damage deduplication, slowing/exit, range clamp, piercing and cleanup. Native 30 FPS recording passed its then-current 19 cases. `match_check.gd` passes 12 checks against the actual arena, including both new slots with MatchDirector cooldowns and real unit damage. The existing 25 target-selection/input checks still pass.

Actual native review: `D:/dev/_scratch/gorilla/ability-indicators-2026-11-10/merged-kit.mp4`. Results and logs are beside it (`merged-checks-15fps.json`, `merged-checks-60fps.json`, `merged-main-match-console.log`). Exit resource warnings are intermittent in debug runs; do not claim memory/leak certification. Artistic review checked the Drive→grab transition frames and native camera recording. Full moving-opponent match balance and a bespoke Fault Line animation remain future polish.

Playable target field: `tools/debug/gorilla_targeting_2026_11_10/launch-review.cmd`; 1–4 select, mouse aims, left click confirms, right click cancels, WASD moves and Q/E turn the camera. The same kit is installed in normal Arena Play. The Rhino chat has received the animation/art handoff and its own atlas request; Rhino art production is independent of these Gorilla gameplay changes.
