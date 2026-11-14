# Fennec (`fennec_s`): status

Kept by the Fennec session (the game feel lane's effects spin-off, made the fennec's owner by the hub on 2026-11-05).
Rules: `D:\dev\new-mech-rpg\.claude\worktrees\admiring-bell-074042\docs\team\mech-sessions-2026-11-05.md`.
Checked on disk 2026-11-05.

## Where it stands
The fennec plays in the arena (Tab to it) with its 35-degree body and four of its five new effects. Its keys still
run the old kit, apart from the blink (key 2) and a preview of the new slot 1 on key 5. Its basic attack, a small
violet dart at 6 m, is built and goes through the shared `basic_attack(target)` hook. The taken kit (portals for
itself and the team) is only partly built, and its last open choices (the redraft) wait on Preston.
**Nothing of the fennec is committed:** its art, sounds, kit script, effects and checks are all untracked in git.

## The kit: taken versus in game
Taken 2026-11-05 (`docs/plan/moba-kits.md`, fennec section). A redraft waits on his "Take it": the passive becomes
gate echo (no fox-body traits), and sonic boom returns as the rift boom, on the great gate or in slot 1.

| Slot | Taken kit | In game now (`scripts/moba3d/fennec_kit.gd`) | State |
|---|---|---|---|
| Basic | (not in the kits doc; Preston asked for basics 2026-11-05) | ranged dart: `basic_attack(target)`, 6 m, every 0.9 s, 30 damage (0.5 of a kit hit) | built 2026-11-05, 30/30 in game (`take-b/fx/basic/`); body reuses cast frames 2 and 4. The attack lane will draw a `basic` animation later (third in its queue, after the gorilla and hippo; paid, about 50k-120k tokens, 230k worst case, only on Preston's yes) and will send the release frame. Sounds wired by the sound lane (option A placeholders) |
| Passive | big ears (pings) | big ears (`_listen`) | the redraft drops it for gate echo |
| 1 | two-faced shot | key 1 is the old sand kick; the shot is on preview key 5 | the shot works (bolt effect, 18/18); slot 1 waits on the redraft (the rift boom might take it) |
| 2 | pocket gates (it and allies step through) | blink gate: the fennec only, recast to snap back | the fennec's half works (small gate and blink flash); allies can't use it yet |
| 3 | far gates (exit anywhere it sees, or on an ally or tower) | key 3 is the old tunnel | not built |
| 4 | great gate (carries the team, arrival shield and speed) | key 4 is the old sonic boom | held by the hub until the redraft; the arrival shield is ready, not wired |

## Art in game (`art/machines/fennec/fennec_frames.tres`, 9 animations x 5 views)
- At 35 degrees, tilted: idle, cast, walk (with body sway) and death.
- **Death, front view: redrawn and installed (2026-11-05, touch-up lane, Codex, Preston: "Install it").** It keeps
  the poses and matches the approved still's lighting and texture. The new frames are `death35/frames/front_f1-f6`,
  with the old ones backed up in `death35/frames_pre_codex_front/`. The animation lane is repacking the sheet.
- **Death, back view: pose redrawn and installed (2026-11-05, touch-up lane, Codex, Preston: "Back only").** The new
  frames are `death35/frames/back_f1-f6`, with the old ones backed up in `death35/frames_pre_codex_back/`. The
  animation lane is repacking the kit sheet.
- **Death, se view: redrawn and installed (2026-11-05, touch-up lane, Preston: "Install it").** f0-f4 are the Codex
  se poses, f5 is the old lying pose with a hand fix, and f6 is f5 with the eyes out. The old frames are backed up in
  `death35/frames_pre_codex_se/`. The animation lane was asked to repack `fennec_kit_sheet.png`.
- The death frames are free again (front, back and se). Check with the touch-up lane before editing any of them.
- The trot sway from the touch-up lane is in the live sheet.
- Still the old low angle, held until the redraft is taken: sand_kick, dig, sonic_boom, pop_out and ear_burst.
  The redraft drops sand kick, dig and pop out, and redraws sonic boom as the rift boom.

## Effects (`docs/art/moba/fennec_s/take-b/fx/`)
| Effect | State |
|---|---|
| small gate | done; slots 1 to 3 use it |
| bolt | done; slot 1 (two-faced shot), 18/18 |
| blink flash | done; slot 2 and its recast, 15/15 |
| arrival shield | done, 35/35 on the fennec and the rhino; waits for the great gate |
| basic dart and hit | done; the basic attack (`fennec_bolt.gd` dart mode, `dart_sheet.png`, `dart_hit_sheet.png`), 30/30; board in `fx/basic/` |
| big gate ring | held until the redraft |
The ears ping is on hold as well (the redraft drops the big ears).

## Sound (sound lane's)
The fennec has the old kit's sounds (`audio/sfx/fennec/`: boom, burst, dig, kick, pop out) and a `portal/` folder in
progress (`tools/audio/fennec_portal_recorded.py`). Slot 1's shot still plays the sand kick's sounds, and the blink
flash and the arrival shield have none. Those are the sound lane's to make; I would only add the triggers.
The basic attack emits `cue("basic_cast")` and `cue("basic_hit")`. The sound lane wired them on 2026-11-05: the
`FennecKit` "cues" row in `kit_audio.gd`, free placeholder option A (basic_cast "Glass tick" 140 ms, basic_hit
"Crystal spark" 320 ms), and `check_kit_audio.gd` passes. Preston has a page with B options ("Zip", "Chime spark"); his
pick swaps the files under the same names.

## Open
Preston's calls:
- The redraft: take it or not, and the rift boom on the great gate or in slot 1.
- Whether the ultimate keeps a control piece (the redraft's rift boom knockback would be it).
- Whether enemies can use its gates (the draft says no).
- Committing the fennec's files (only on his yes, and only the fennec's own).

If he takes the redraft, also change the roster checks' "Camouflage counters" line in `docs/plan/moba-kits.md`
(line 408 on 2026-11-05, "fennec big ears (pings moving enemies)") to gate echo, which reveals enemies its bolts or
boom hit through fog and camouflage. Check the edit order with the hub first: one session edits that file at a time.
Until then the line is right. The squirrel session asked on 2026-11-05, thinking gate echo was already taken.

Known issues:
- While the body is hidden 130 ms after a blink, its shadow stays on the floor (camera lane's shadow, or a small fix).
- Toward the camera only about 3 m of floor shows below the fennec, so a bolt or blink that way leaves the screen
  early (camera lane's framing).
- Walking away from the camera, the arrival afterimages lie over its back in mint for 0.4 s.
- `fennec_kit.gd` still carries the old kit's code (sand kick, ear burst, tunnel, sonic boom) until each slot is
  replaced.

Closed since the effects reports: `tools/debug/fennec3d_check.gd` now expects 45 animations, and the effect art is
imported.

## Next slices (pick one; each is free and stays clear of the hub's hold)
1. **Pocket gates for allies (slot 2). Free.** Allies near either gate can step through, both ways, for the gate's few
   seconds. The fennec's blink and recast stay as they are, and both ends show the small gate and the blink flash.
   The check is a clip of an ally dummy going through from s, e and n. Pocket gates are the same in every version of
   the kit, so this can't be undone by the redraft. Size: about one effect build (one long session turn), no paid
   tools.
2. **Far gates (slot 3). Free.** This replaces the old tunnel: an entrance gate at the fennec, and an exit anywhere it
   can see, or on an ally or a friendly tower. Allies step through for a few seconds. It reuses the small gate and the
   blink flash, with no new art unless the exit needs a marker. It is also the same in every version of the kit.
   Size: one to two long turns, no paid tools.
3. **Your call on the redraft. Free (one line from you).** "Take the redraft" or not, and where the rift boom goes.
   That unlocks slot 1's binding, the great gate (with the arrival shield wired in) and the big gate ring. The rift
   boom's 35-degree body art is the attack lane's, and is the only part that might need a paid tool. That lane would
   quote it before anything runs.

Before I edit `fennec_kit.gd`, I confirm with the game feel lane that it has nothing in flight there.
