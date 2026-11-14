# Announcer lines (draft, 2026-11-05)

Voice: the **foundry overseer**, the plant's control AI speaking on the PA. It's cold, calm and clipped, like a
safety announcement. Preston picked this direction on 2026-11-05.

The lines below were my draft. They were generated as-is on 2026-11-05 (one v3 take, 450 credits, preview 3 voice),
treated light with the PA preset, and written to `audio/voice/announcer/<name>.ogg`. None is hooked to the game yet.
- **Cost:** about 1 credit per character per take on v3. These 21 lines come to about 400 characters, so about
  400 credits for one take of everything.
- **Bus:** the Voice bus, not positional (heard everywhere, like the PA). Music already ducks under Voice.
- **"Signal"** says whether the game emits something to hang the line on. The rows marked "exists" are in
  `map_audio.gd` today. All the other rows are unchecked and need the gameplay lane to emit them.

## Match flow
| Line | When | Signal |
|---|---|---|
| "Foundry systems online." | match start | needs one |
| "Thirty seconds until the first wave." | 30 s before wave 1 | needs one |
| "Production line active. Minions deployed." | first wave only | `wave_spawned` exists (first time only) |
| "Shift complete. Victory." | you win | `match_ended(true)` exists |
| "Shift failed. Defeat." | you lose | `match_ended(false)` exists |

## Towers and core
| Line | When | Signal |
|---|---|---|
| "Enemy tower destroyed." | your team kills a tower | `tower_destroyed` exists; it needs the tower's team |
| "Your tower has been destroyed." | you lose a tower | same |
| "Warning: your core is under attack." | your core takes damage (once per 20 s or so) | needs one |
| "Enemy core exposed." | the last enemy tower before their core falls | needs one |

## Side pits
| Line | When | Signal |
|---|---|---|
| "Pit secured." | your team takes a pit | `pit_taken(team)` exists (map lane) |
| "Pit lost." | the enemy takes a pit | same |

## Kills
| Line | When | Signal |
|---|---|---|
| "First blood." | first kill of the match | needs one |
| "Enemy unit destroyed." | your team kills a mech | needs one |
| "Unit lost." | your team loses a mech | needs one |
| "Double kill." | two kills close together by one player | needs one |
| "Triple kill." | three | needs one |
| "Team wipe." | the whole enemy team down at once | needs one |
| "Shutdown." | you kill a player on a streak | needs one |

## You
| Line | When | Signal |
|---|---|---|
| "Unit rebuilt." | you respawn | `respawned` exists |
| "Your unit has been destroyed." | you die | needs one |
| "Low armor." | your health drops under 25% (rare, maybe skip) | needs one |

Kill-streak lines like "First blood" and "Double kill" are genre words used across MOBAs. No line here copies
another game's wording, and no other game's announcer audio is used.
