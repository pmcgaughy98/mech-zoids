# Squirrel (`squirrel_s`): status, 2026-11-05

Written by the Squirrel session (stock-take only: nothing built, nothing spent).
Kit taken and pasted into `docs/plan/moba-kits.md` on 2026-11-05 (see slice 1 below).

## What exists
- **Approved take:** `take-b/` (has `APPROVED.txt`, Preston 2026-11-03: "keep ... squirrel"). `take-a/` is the
  older take, not current.
- **Approved stills:** `take-b/fixed/`, eight views (s, se, e, ne, n, nw, w, sw), drawn at the old low camera.
  - Front view: tail cut to one side by hand in Aseprite (`take-b/aseprite/s_tail_one_side.aseprite`).
  - `ne`: capped ink installed 2026-11-04 (+38 px, "Keep all five"). Originals in `take-b/fixed_pre_ink/`.
  - Canvas 160, feet row 140, 16 colours, south view 56x72 (`cam35_fleet/HANDOFF.md`).
- **35-degree stills:** none. The squirrel is the last machine in the fleet redraw queue
  (`cam35_fleet/HANDOFF.md`: group 3, after chameleon, falcon, hummingbird). Target sizes listed there:
  s 56x96, se 66x91, e 75x85, ne 66x91, n 56x96.
- **Animations:** none. No squirrel entry in the walk, attack or touch-up logs.
- **In the game:** nothing. No `art/machines/squirrel*` folder, so no `_frames.tres` and no `tilt_anims`.
- **VFX and sound:** none drawn. Placeholder dart (a plain amber dash), the shared hit spark, and three count
  lights over the head; the kit emits cue names (dart_fire, dart_hit, hearsay_jump) for the sound lane.
- **Kit code (2026-11-05):** `scripts/moba3d/squirrel_kit.gd` and `squirrel_dart.gd`: the signal dart basic attack
  and the Hearsay passive, on the approved low-angle stills (not tilted). Check:
  `tools/debug/squirrel_hearsay_check.gd`, 21/21 (jumps on darts 4 and 8 only, 18 damage, machines first, out of
  reach ignored, 0.145 s for a 4 m dart). Branch Skip, Crosstalk, Tail Ping and Broadcast not built.

## What the kit doc leaves open (`docs/plan/moba-kits.md`, Squirrel section)
1. **It predates the 2026-11-04 rule.** All five parts are animal (acorns, hop, nut scatter, tail flick, nut rush).
   The rule now: the animal gives the body and at most one trait, the rest comes from a power theme. The fennec
   was reworked this way; the squirrel has not been.
2. **"Nothing held in hand."** Basic attacks "throw acorns". Throwing reads as holding. Where the shots come
   from on the body (a launcher, the tail, cheek pods) is not decided.
3. **No names, no numbers.** Slots are plain labels; cooldowns are tiers (short, medium, long). Damage, range,
   how many throws before a hard nut, nut rush length: all open, all Preston's.
4. **Art list not started:** basic attack, hop, scatter, tail flick. Plus walk, idle and the 35-degree stills.
5. **Size, shared with other lanes:** at 72 px the squirrel stands 1.44 m, as tall as the rhino
   (`STILLS_STOCKTAKE_2026-11-04.md`). Not decided anywhere yet.
6. **Mirroring, shared:** the engine mirrors east-side views to the west, so the hand-cut tail flips sides when it
   turns (same stock-take). Fine or not is Preston's call.

## Next slices (Preston picks one)
1. **Kit rework proposal under the new rule. Free. Done 2026-11-05, taken by Preston ("Take it"):**
   `docs/plan/squirrel-ratatoskr-kit-2026-11-05.md` (signal relay theme, draft names and numbers, reviewed by
   the game feel lane: Broadcast ultimate, cooldowns on the match tiers). Original plan for it: One session, a proposal file beside the fennec one
   (`docs/plan/squirrel-ratatoskr-kit-2026-11-05.md`): a power theme drawn from Ratatoskr as the messenger who runs
   the world tree (signal relays, pings, marked targets), real draft names and numbers, one animal trait kept
   (the hop or the tail alarm), and where on the body each power fires from. Two alternatives named. Nothing
   enters `moba-kits.md` until he picks.
2. **Basic attack VFX test. Free.** After slice 1 settles what the shot is. A standalone Godot test scene: the
   projectile, its hit, and the bounce to a second target, built in code plus PixelLab's free `vfx_workbench`,
   with a headless check that measures the bounce. A synthesis pass (study 2 to 3 shipped games' ranged-carry
   basic attacks first). Does not touch shared match code.
3. **35-degree still redraw. Paid (Codex).** About 60k to 100k tokens for one image, worst case about 175k with
   the known 75k cap overshoot. A second image if the first misses doubles that. It belongs to the fleet redraw
   lane's queue, where the squirrel is last; moving it up needs the hub's paid-job slot and Preston's yes.

## Not checked in this stock-take
- I did not search the match scripts for a squirrel entry; "not in the game" rests on the missing
  `art/machines/` folder and the hub's word.
- I did not open any image. The stills' look is from the take's `REPORT.txt` and the roster.
- The `59,507` figure in the fleet table's squirrel row: meaning not read.

## Next: Branch Skip (Preston: "Build Branch Skip", 2026-11-05, not started; usage limit hit)
Nothing in the kit was changed for it. Plan for the next squirrel session:
- Key 1 in `_unhandled_key_input` (gate on bot and `player.slot_ready`, as `wolf_kit.gd` does); `used.emit("1")`;
  `current = "skip"` and `player.busy` during the hop.
- Direction `player.move_dir()`, else `player.facing`; 3 m in 0.25 s with `ArenaMotion.slide`, a small sprite arc;
  facing stays on the aim.
- After landing `primed = 2.0`: the next dart uses scale 0.7 (42), always jumps, resets `count`; lights show a
  primed colour; `_process` counts `primed` down. Cues: skip_hop, skip_primed, primed_fire.
- Dart data carries its own scale, so `_on_dart_struck` hits with it.
- New check `tools/debug/squirrel_skip_check.gd`: hop distance and time (engine time), busy then free, used "1",
  primed dart 0.7 plus a jump with count reset, window expiry after 2 s. Test moves with `player.move_override`.
