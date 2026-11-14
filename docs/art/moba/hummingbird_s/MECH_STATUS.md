# Hummingbird (`hummingbird_s`): mech status

Hummingbird session. Stock-take 2026-11-05; kit taken and the link slice built the same day. Nothing paid spent.

## Decided
- **Kit: bonds, taken 2026-11-05** ("Bonds + hover"). Link beams from the ruby throat plate; flutter is the one
  animal trait. Kit section: `docs/plan/moba-kits.md`. Draft with sources and the light alternative:
  `docs/plan/hummingbird-cupid-kit-2026-11-05.md`.
- **Body: hovers low all the time, never walks** (same day). No walk cycle (the walk lane confirmed). It breaks his
  "birds rest on their feet" rule for this one bird only. The approved standing still is now a stand-in; its
  35-degree redraw is a new hover pose.

## Built: the link slice (2026-11-05, "Do the link slice")
- `scripts/moba3d/hummingbird_kit.gd`: passive kindred link and 1 link needle. Slots 2 to 4 are not built.
- Press play: `scenes/moba3d/hummingbird_test.tscn` (two wounded blue allies, one enemy dummy; 1 fires the needle at
  the mouse aim; R puts the allies back to 300 health). Helper: `scripts/moba3d/hummingbird_ally_dummy.gd`.
- Body stand-in: the approved low-angle stills, lifted 12 texels (0.19 m) off the floor, not tilted.
- Numbers on the match's 600-health machines: needle heals 60 (10%) or hits for 36 (kit hit x 0.6), 10 m; link heals
  6 a second (1%), breaks past 9 m or behind a wall.
- Check: `tools/debug/check_hummingbird_kit.gd`, 26 of 26 pass (frames, hover lift, needle heal 300 to 360, link
  5.97 a second over 3.00 s, full-health cap, link moves to a second ally, breaks at 9.5 m, enemy hit 36 with no
  link, first unit on the line wins, 2 m off the line and 11.5 m away are missed). The test scene also ran 180 frames
  headless with no errors.
- **Basic attack, beak shot (2026-11-05, "Yes, ranged beak shot"):** `basic_attack(target)` to the game feel lane's
  hook. A short steel dart at the enemy nearest the mouse aim (30 degree cone) within 6 m edge to edge, 30 damage,
  every 0.9 s; enemies only; no target in reach means no shot. In the test scene: hold Space or left click.
- **Healing goes through the shared `heal(amount, by)`** (game feel lane, 2026-11-05); the ally dummy has the same.
- Check after both: 34 of 34 pass (the beak shot follows the mouse aim, turns the machine, refuses out of reach, out
  of the cone and allies; a bot's target is shot in reach and refused out of it). The test scene ran 180 frames clean.
- Shared checks in the same run: `kit_api_check` 1 fail and `match_check` 64 pass, 3 fail, all about the stand-in
  attack. Not from this kit (it isn't in the match): eight other kits gained basic attacks during the run, so no
  machine uses the stand-in anymore. Reported to the game feel lane.
- Cooldowns use the shared tiers: 1 short (5 s), 2 medium (9 s), 3 short-medium (7 s), 4 long (40 s).
- **Not verified:** a wall cutting the link or the needle (the field has no wall to place in the check), and how it
  looks in a window (no one has pressed play yet).
- **Not in the match:** the game feel lane adds it on Preston's say (machine kind, tier row, bot install, Tab entry).
  The sound lane has the cue names.

## What exists (art)
| Thing | State |
|---|---|
| Approved take | `take-a/` only. Approved 2026-11-03 ("keep rhino, and hummingbird"). Stands on folded wings, so it no longer matches the body call. |
| Stills | `take-a/views/`: all 8 views, drawn at the old low angle (about 9 degrees). n has +64 px of capped ink (2026-11-04); original in `take-a/views_pre_ink/`. |
| Known flaws, flagged and kept | Heart-shaped ruby throat plate from the front (kept on purpose). Side views 69 px vs front 72. Back views taller than front. Back-view feet show claws. The redraw can fix all but the plate. |
| Size | Class S: 72 px tall, 160 px cell, floor row 141 (153 with the stand-in's hover). |
| 35-degree stills | None. The fleet lane handed the redraw to this session (2026-11-05). |
| Animations | None drawn. No `art/machines/hummingbird_s/` folder. |

## Still open (his call)
1. Ability names and every number.
2. Role: healer support, off Cupid's ranged-hunter role (open choice 3 in the kit doc).
3. Whether it goes into the match now, with only the passive, slot 1 and the basic built.

## Next slices (Preston picks)
**1. In the match since 2026-11-06** (game feel lane, on his "Yes, into the match"). Play: open
`scenes/moba3d/arena_play.tscn`, run it, press Tab 5 times (rhino, gorilla, fennec, wolf, squirrel, hummingbird);
Space or left click is the beak shot, 1 the needle toward the mouse; 2 to 4 do nothing yet. The game feel lane's probe
passes 10/10, and kit_api_check, match_check (67/67) and this kit's check (2026-11-06) all pass. It uses the
low-angle stand-in stills, so it will not match the 35-degree machines until the hover redraw.
No bot plays it for now (Preston, 2026-11-06: "Not yet, I'll play it"); a hummingbird bot would only use its basic
until match_bot gets a needle plan (proposed: heal the most hurt ally within 9 m under 70% health, else needle the
nearest enemy in range).

**2. 35-degree hover stills (paid: Codex on his plan usage).** Now this session's job. Recipe:
`docs/art/moba/cam35_fleet/HANDOFF.md` (prep_machine.py, fleet_board.py, hull_guide.py, then the gate: top shows in
every view, far wingtip or tail sits higher, no new parts, full-size eyes, no eye in ne or n, then game feel's turn
test). For the camera lane: draw the hover gap above a fixed floor row, give the frames a "feet" meta for the hull's
footprint on the floor, and send it the packed `.tres`. Price: fleet images have cost 54k to 78k tokens each with
plain `codex exec` (no cap). With a cap at 100k the worst case is about 175k. Needs his yes and the hub's paid slot;
send the token count from codex-log.txt to the fleet lane after (fleet total 450,532 of his 0.9M to 1.5M).

**3. Bonds effects (free).** Link needle, link beam, ring of beams, charm mark, with the free PixelLab effect
workbench and Godot particles, replacing the plain beam and needle.

**4. Slots 2 to 4 (free code).** Surge line, flutter, kindred ring, one per session.

## Notes for whoever picks this up
- Any art or effects slice starts with a tool stock-take (synthesis).
- This session runs in the worktree `.claude/worktrees/admiring-bell-074042`, whose guard blocks the main folder.
  Preston said to write to the main folder anyway (2026-11-05); files are written in the worktree or
  `D:\dev\_scratch\hummingbird\src\` and copied in by shell.
- Godot: check no other Godot is running before any run, including `--check-only`.
