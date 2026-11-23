# Pangolin ability effects: synthesis (2026-11-12)

Pangolin effects lane, on the rhino effects lane's method (`rhino-fx-synthesis-2026-11-11.md`) and its corrections.
Bar (Preston, 2026-11-11 and 12): any tool, but it must not look like pixel art; SMITE 2 grade, smooth, layered, HDR.
Impact flashes small and short, no drifting glowing motes, no point light washing the mech out, no red in the
pangolin's own effects (red marks enemies).

## Where the pangolin stands (read first)
- **Kit code: none.** No `pangolin_kit.gd`; the arena row says "Clips and events only; the kit code is not ported".
  So there are no kit signals to hang effects on yet.
- **Kit design:** `docs/plan/moba-kits.md` (ode to Kuzenbo): sharp scales passive, 1 claw rake, 2 dig in,
  3 scale flare, 4 iron ball (Rammus Powerball feel, stop on first hit, Preston 2026-11-06).
  `docs/plan/kit-design-2026-11-11.md` proposes the power theme **magnetise and home** (rake magnetises, the ball
  curves toward a magnetised enemy). Not decided.
- **Body:** the pangolin 3D lane's r5 file is in the arena (`art/arena_models/pangolin.glb`, r6 waits on Preston).
  Clip events (`pangolin.events.json`): Claw_Rake hit 0.20, hit_shred 0.36; Dig_In scoop 0.08/0.14/0.22, under 0.47;
  Dig_Erupt break_ground 0.20, erupt 0.25, land 0.50; Scale_Flare tighten 0.13, flare 0.20, closed 0.62;
  Curl_In closed 0.36; Ball_Roll loop (roll_speed 7.67 m/s); Curl_Out open 0.10, land 0.30. Flare blend shapes.
- **Body colours (measured on its texture):** copper and terracotta (hue 7 to 24 degrees, e.g. #cb7251) on 90% of
  the saturated pixels, blue accents (#2263d9) on the rest.

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Geb, "How To Play Geb In Smite 2" (youtube GviMlBOD0rA, 1280x720 at 60 fps) | **Measured**: Roll Out casts sampled at 15 fps from 382.2 s (3 s) and at 10 fps from 404.2 s and 416.0 s. Sheets `D:/dev/_scratch/pangolin-fx/ref/roll15_a.png`, `rollbc.png`, `zgrid.png` | The order and timing of a rolling-ball dash: aim, tuck, travel, trail |
| League of Legends, Rammus, Powerball | **General knowledge only**, not watched | The feel Preston named: builds speed, a dust cloud behind, a knock-up on the first enemy, bigger the faster |
| Our own clips and the kit table | Read | Curl_In closed 0.36 s, Ball_Roll at 7.67 m/s, the "starts at walk speed, doubles over 2 s" proposal |

Caveat: the player in that video uses a **mechanical skin** for Geb, so the curled body itself reads as a crouched
machine, not a stone ball; the effect layers around it still read. Captions were rate-limited, so the tooltip text
was not read. Nothing from the clip is in the project.

## Structure learned (measured unless marked)
1. **Aim first:** a translucent blue strip on the floor ahead shows the roll's line while choosing (cells 0 to 1).
2. **Short tuck, no flash:** 2 to 3 cells at 10 to 15 fps (0.2 to 0.3 s) from standing to curled. No effect marks the
   tuck; the body sells it. Ours: Curl_In closes at 0.36 s, a little slower.
3. **Long travel, quiet layers:** about 1.5 to 2 s of rolling. What shows: a dark contact shadow under the ball, a
   **thin pale trail line drawn on the floor behind it** (the clearest "it is rolling" read from behind), and debris
   thrown up and around (on this skin, orange shards; the base-skin debris is not verified).
4. **No glowing shell around the ball** while it rolls. The speed reads from the trail and the debris, not light.
5. **Not seen:** a hit on an enemy (none was struck in these casts), so the crash structure comes from the rhino
   lane's measured impact order (one hot frame, a fast ease-out edge, debris, a short life) and from Rammus (general
   knowledge: the knock-up is the victim's read).

## Decided: colour (Preston, 2026-11-12)
"copper with ambersparks is color choice for ability effects if other colors added to it that color should be theme."
Copper with amber sparks is the pangolin's effect colour for every ability. Other colours may be added, but copper and
amber stay the theme they sit on. Option B below; the built slice was recoloured to it the same day.

## Synthesis proposal (nothing here is canon)

**Look:** smooth shader layers in **steel-white and magnet blue** (#40a0ff region, the body's own blue accents and
the kit draft's "magnetise" charge), dust in warm grey with a touch of copper, one warm white-amber line only where
the plates grind at speed. Bright cores above HDR 1.05 so they bloom, all else under; additive quads write ALPHA and
use fog_disabled.

Alternatives named:
- **A (first build, replaced): blue and steel.** Ties to the blue accents and the magnetise idea. Risk: close to the blue team ring.
- **B (chosen by Preston): copper and amber sparks.** The body's main colour; reads as hot metal grinding. Risk: amber is the rhino's
  crack colour, and copper on copper loses the ball.
- **C: no colour at all, only dust and the furrow** (closest to Geb's quiet roll). Cleanest, but the ult has no
  "power" read.

**Iron ball (built, slice 1):**
- Tuck (`ball_start`, then Curl_In `closed`): a small ring of dust puffs at the feet. Nothing bright.
- Roll (each frame while the kit says `rolling`):
  - a **furrow** pressed into the floor behind, one soft segment every 0.35 m that blends into one track: a darker
    groove with a pale dust lip either side (Geb's trail line), plus a thin white-amber grind line down the middle at
    speed that cools in about 0.4 s;
  - **dust kicked back**, more often and bigger as it speeds up (0.16 s to 0.07 s apart);
  - **two blue flank streaks** on a flat wake behind the ball that stretch from 1.4 m to 4.0 m with speed, and a soft
    blue glow where it touches the floor. White-hot thread only at full speed. **Ours, not Geb's** (he has no glow): it
    is what makes the ult read as powered and as "faster now".
- Crash (`ball_hit`): a 2-frame small core, a blue shock edge pushed forward like a bow wave (1.6 m slow to 3.0 m at
  full speed), forward speed streaks in a 70 degree cone, a pale scuff, 4 to 8 rocks, 3 to 6 dust puffs, a light of
  1.0 to 1.8 gone in 0.16 s. The victim's knock-up is the read of the hit.
- Unroll (Curl_Out `land`): a small landing puff.

## First slice: the iron ball (built 2026-11-12)
- Code: `scripts/moba3d/pangolin_ball_fx.gd`, an observer. Shaders: `shaders/pangolin_track.gdshader`,
  `pangolin_wake.gdshader`, `pangolin_crash.gdshader`; dust reuses the rhino lane's `rhino_dust.gdshader` as is.
- **Run on a stand-in kit, because the pangolin has no kit code.** The stand-in
  (`D:/dev/_scratch/pangolin-fx/rec/ball_stub_kit.gd`) carries what the real kit should expose; proposed to the game
  feel lane as the contract:
  - `signal cue(name)`: `ball_start` (tuck begins), `ball_hit` (first enemy struck), `ball_end` (roll ended, no hit)
  - `rolling: bool`, `roll_speed: float` (m/s), `roll_dir: Vector3`, `hit_speed: float`, `hit_at: Vector3`
  - Hookup when the kit exists: `load("res://scripts/moba3d/pangolin_ball_fx.gd").new()`, add as a child of the kit,
    `setup(kit, player)`. Not called from the live game yet.
- Recorder: `D:/dev/_scratch/pangolin-fx/rec/pangolin_ball_look.gd` and `record.sh`, in `arena_play.tscn` at the game
  camera, `--fixed-fps 60`.

**What the frames showed (checked by eye: 4 fps across the clip, 15 fps around the full-speed crash):**
- Logged: roll 1 reached 7.67 m/s in 1.83 s and crashed at full power (shock edge 3.0 m); roll 2 crashed at
  5.2 m/s (power 0.42, edge 2.2 m). Both `ball_hit` cues fired; the effect drew both.
- Roll: the ball reads from behind; the furrow shows as a darker track with a pale lip, dust kicked back. The blue
  flank streaks were faint on the blue floor in the first take and were brightened once.
- Crash: shock edge and forward streaks show for 4 cells at 15 fps (0.27 s), the core 1 to 2 frames, dust after.
  The pangolin stays readable on the impact frame; no pale squares, no wash-out.
- First take froze (the write-movie stall: a 9 s mp4 of one still frame, 0.5 Mb/s); re-recorded. Second take: roll 2
  ran into the tower and was hidden; roll 2 now goes left into open floor. The furrow's grind line was too white and
  too long (about 3 m); now amber and about 0.2 s.
- **Not shown:** the minion's knock-up. The recorder's pin does not lift the minion's model, so the victim read
  (Rammus's main crash read) is missing from the video. It belongs to the kit's knock-up anyway.
- The thin white line to a circle at the bottom of the screen is the arena's mouse aim marker, not this effect.

## Hold on claw rake and dig in (Preston, 2026-11-12)
"Dig and claw are too much like animal": slots 1 and 2 are due a redo by the kit design lane (local_f13fcfe4), who was
messaged. Their effects in the list below wait for the new kit; iron ball and scale flare stand.
Kit design's proposal (same day, waiting on Preston's yes; see kit-design-2026-11-11.md "Pangolin redo"):
1 **salvage** (magnetic field tears armour plates off enemies in a cone; plates fly in and snap onto the pangolin's
shell; hit enemies are magnetised about 4 s), 2 **rail dive** (rides its spine rails' field in a line, locks onto a
magnetised enemy from range; no ground track, only an amber spark streak off its spine). Claw_Rake becomes the basic;
Dig clips parked. Additions: iron ball curves toward magnetised enemies, scale flare magnetises attackers, and
magnetised enemies wear a copper/amber mark (a ring was proposed).

## Next (proposal, in order)
1. **Kit hookup:** the game feel lane ports the iron ball with the cue contract above; then this observer goes on
   it, through a `pangolin_fx_installer.gd` in `arena_play.tscn` like the rhino's.
2. **Victim read on the crash:** a short vertical dust lift under the knocked-up enemy and a small landing puff.
3. **Scale flare (3):** Kuzenbo's spiked shell as structure: on `flare` (0.20 s) a ring of short steel-blue blade
   glints along the plates plus a low shock ring; while it blocks, a faint plate sheen; a spark on each blocked hit.
   Uses the Flare blend shapes' timing.
4. **Dig in / erupt (2):** dirt spray on each `scoop`, a moving burrow bulge (cracked mound) while under, and at
   `break_ground` / `erupt` a crack web and rocks, reusing the rhino lane's crack ground shader in our colours.
5. **Claw rake (1):** two smooth claw arcs on `hit` and `hit_shred`; if the magnetise theme is chosen, a blue charge
   ring on the raked target that the ball's curve can home on.
6. **Passive, sharp scales:** a small steel spark on the attacker when it hits the pangolin in melee.
7. Aim strip for the ult (Geb's measured step 1), if the kit gets an aimed start.

## Recoloured to copper and amber (2026-11-12, after Preston's pick)
The wake's glow, the crash's inner wash and the crash light are now copper; the flank streaks, shock edge and forward
sparks are amber; cores are warm white. Recorded again (`D:/dev/_scratch/pangolin-fx/rec/pangolin-iron-ball-copper.mp4`)
and checked at 10 fps around the full-speed crash: the shock edge reads warm gold, the sparks amber, and it stays
separate from the blue team ring. The edge blooms toward cream at full power; if it should read more copper, lower its
white mix (0.3 in `pangolin_crash.gdshader`). Rule for later abilities: copper and amber first, any added colour on top.

## Slice 2: scale flare (built 2026-11-12)
Reference: SMITE, Kuzenbo's Shell Spikes (youtube --lTPiHRzb4, a skin showcase), **measured** at 10 fps from 66.5 s:
the cast is 1 cell of a waist ring and dark shards thrown up; the spikes stand the next cell; from cell 3 the shell
itself glows (no bubble), steady for about 2.8 s; hits show small puffs; it goes out within 1 cell. Sheet:
`D:/dev/_scratch/pangolin-fx/ref/kuz_spikes10.png`.
- Built in the same observer, renamed `scripts/moba3d/pangolin_fx.gd` (it holds every pangolin ability). Shaders:
  `pangolin_flare_shell.gdshader` (plate glow, on the body as material_overlay only while up), `pangolin_spark.gdshader`;
  the burst reuses `pangolin_crash.gdshader` with a new `omni` uniform (round, rays all round; the crash is unchanged).
- On Scale_Flare `flare` (0.20 s): a 2.5 m copper ring with amber rays and 6 plate flakes; the plates glow copper with
  amber glints. Each blocked hit (`flare_block`): an amber spark where it struck and a pulse; the glow steps down with
  one block left and goes out when none are left or on `flare_end` (3 s without a kit count).
- Recorded on a stand-in (`rec/pangolin_flare_look.gd`, `pangolin-scale-flare.mp4`): two flares, three blocks, all logged.
  First take: the glow barely showed (copper on a copper body); made about twice as strong. Checked: on reads gold, off
  is back to copper, sparks and burst read. Not done: the 2.5 m radius is a draft; no kit code yet.

## Slice 3: the magnetised mark (built 2026-11-12, after Preston approved the kit redo)
Preston: "yes approve it, start with the magnetised mark". Salvage and rail dive replace claw rake and dig in.
- `shaders/pangolin_mag_mark.gdshader`, driven from `pangolin_fx.gd`: the kit cue (settled with game feel: cue only, no direct calls; the kit emits once per target for salvage hits, scale flare blocks and refreshes)
  `magnetise` with `mag_target` and `mag_time` (4 s draft). A copper ring (1.1 m) under the enemy with four amber arcs
  circling it like a field; one arc goes out per quarter of the time, so it doubles as a timer. Applying or refreshing
  snaps it in from wider with a short pulse (the only part that blooms). It follows the enemy and is removed when the
  time runs out or the enemy dies or leaves.
- No reference measured for this one: it is a status mark, built to the kit draft's "a ring" and the team-ring rule
  (team rings are still circles; this one moves, so the two never read alike).
- Recorded on a stand-in (`rec/pangolin_mag_look.gd`, `pangolin-magnetised-mark.mp4`): three red minions, one far,
  one refreshed; all four applies logged, all marks gone at the end. First take: rings too thin and hidden under the
  minions, the far minion behind the tower; ring made wider and brighter, far minion moved.
- Seen in the frames but not from this effect: small orange dots and white sparks on the Claw_Rake hits come from the
  shared hit effects, not the pangolin lane.
- Next: salvage (plates torn off in a cone, flying in to snap onto the shell), then rail dive (amber spark streak off
  the spine, no ground track), then the iron ball's curve toward a marked enemy.

## Clip times for salvage and rail dive (pangolin 3D lane, round 9, draft, not in the arena yet)
File `D:/dev/_scratch/pangolin-3d/game-export-r7/pangolin-kit-r7.glb` (+ events json beside it). Scale 0.565.
- Salvage, 0.65 s: field on at 0.15 (the hit), holds to about 0.35 with the shell lifted open; plates land at 0.36
  (front), 0.42 (middle), 0.48 (rear), each with a shell snap. Flying plates should arrive at those times, front to rear.
- Rail_Launch 0.25 s: release at 0.12. Rail_Streak 0.40 s loop: body 3 to 4 cm off the floor, 2.88 m long, a ripple
  head to tail twice a loop. Rail_Arrive 0.50 s: claws slam at 0.10, 1.18 m ahead of the body centre; shell settles by 0.24.

## Slice 4: salvage (built 2026-11-12, Preston: "Salvage")
Built on the approved kit text: the field tears plates off enemies in a short cone in front; the pangolin wears them.
- **Contract (proposal for the game feel lane):** the kit sets `salvage_targets: Array` (the enemies the cone hit) and
  optionally `salvage_time` (seconds the stolen armour lasts), then emits `cue("salvage")` at the start of the cast.
  It still emits `magnetise` per hit enemy as before. The effect runs on the r7 Pangolin_Salvage times from the cue:
  field at 0.15, plates land at 0.36 / 0.42 / 0.48.
- **Field:** a floor cone 4 m long, about 70 degrees across (both drafts, no kit numbers yet): faint copper fill, thin
  edges, amber bands running inward (the pull), the far rim flashes on the first frames. On 0.15 to about 0.5 s.
- **Plates:** three solid lit copper plates (not glowing motes), torn off the hit enemies with an amber spark there,
  pulled in on an arc that speeds up, snapping onto the shell front, middle, rear with a spark and a small pop. They sit
  on the shell with a low amber edge for 4 s, then drop off and fade. One target gives all three plates.
- **Checked in the recording:** snaps at 0.35 / 0.42 / 0.47 s after the cue (clip says 0.36 / 0.42 / 0.48).
  Video: `D:/dev/_scratch/pangolin-fx/rec/pangolin-salvage.mp4`. Body plays Claw_Rake as a stand-in; r7 is not in the arena.
- **Fixes found on the way:**
  - `pow(x, 2.0)` with a negative x gives nothing on this GPU (GLSL leaves it undefined). The cone drew blank.
    Every pangolin shader now uses `sq(x)`. This may also have been thinning the inner half of the earlier rings and edges.
  - The arena's see-through floor zones drew over floor effects. The field, crash and mark materials now use render_priority 3.
  - The first plates read as yellow cards; emission was lowered so they read as copper metal.
- **Weak spot:** from the default camera (behind the pangolin) the cone is mostly hidden under its body. The plates
  and the marks carry the read. A wider cone or a raised field (a vertical sheet at the far rim) is the alternative if
  Preston wants the field itself to show.

## Slice 5: rail dive (built 2026-11-12, Preston: "Rail dive next")
Structure: a marked-target dash read in two beats, a lock line first and then the travel streak (general knowledge:
Lee Sin's Resonating Strike in League, the dash-to-marked-target pattern). Kit text: no ground track, an amber spark
streak off its own spine (the bison owns ground rails).
- **Contract (proposal for the game feel lane):** the kit sets `dive_target` (the magnetised enemy, or null for a short
  dash to a spot) and emits `cue("rail_dive")` at the cast start; on arrival it sets `rail_charged` (true when it
  arrived on a magnetised enemy and spent the charge) and emits `cue("rail_arrive")`. The kit moves the pangolin.
- **Lock line** (`shaders/pangolin_rail.gdshader`, mode 0): a camera-facing ribbon from the spine to the enemy's chest,
  mid-air, thin copper with amber pulses running toward the enemy, a white-amber flash on the first frames. 0.26 s.
- **Streak** (mode 1): from Rail_Launch release (0.12 s) a ribbon from the spine back along the path, at most 2.6 m:
  hot head at the spine, broken amber dashes trailing back. Small amber sparks thrown off the spine every 0.07 s. On
  arrival the tail catches up and it goes out in about 0.16 s.
- **Arrival:** charged: a big spark on the enemy and the iron ball's impact at half power (one family of hits), and the
  enemy's mark snaps once and goes out (the charge is spent). Not charged: a small dust ring where the claws land, 1.18 m ahead.
- **Recorded:** `D:/dev/_scratch/pangolin-fx/rec/pangolin-rail-dive.mp4`, cast 1 locked onto a marked minion 9 m away,
  cast 2 a 4.5 m dash to a spot. Draft speed 22 m/s. Body plays Walk and Basic_Left as stand-ins; r7 is not in the arena.
- **Weak spot:** from the default camera behind the pangolin, diving away from the camera, the streak trails toward the
  camera and is seen end-on: it reads as a bright spot on the spine, not a line. The lock line and the arrival read.
  Fix to try: throw the spine sparks out sideways and bigger, so the ride shows from behind.

## Slice 6: the slot-2 iron ball (kit redo, 2026-11-12)
Rail dive is cut (Preston approved the fun pass, `docs/plan/pangolin-kit-fun-pass-2026-11-12.md`). Its ribbon shader
and rail functions stay parked in the code. Game feel's PangolinKit now hangs `pangolin_fx.gd` itself and fires
ball_start, ball_roll, ball_bounce, ball_bowl, ball_hit, ball_end, plus salvage and magnetise on slot 1.
- **Speed range:** the effects read `ball_start_speed` and `ball_max_speed` off the kit (4 to 12 m/s) through `_power()`;
  the old 3.5 to 7.67 range saturated the crash at half the new top speed.
- **Wall bounce** (`bounce`): a spark at the contact, 3 to 5 copper chips thrown off the wall, one puff. No ring and
  no light, so a run of bounces never stacks into a wash.
- **Minion bowl** (`bowl`): a spark on the minion, a puff, one chip. Kept smaller than the crash, which stays the one
  big hit of the roll.
- **Recording:** `D:/dev/_scratch/pangolin-fx/rec/pangolin-ball-slot2.mp4` (8.9 s, real kit, real clips, match camera).
  The log shows a bounce at power 0.54, a bowl, then a crash at 8.8 m/s (power 0.6, ring radius 2.45 m).
- **Weak spot:** at the match camera's distance the bounce and bowl read small. If Preston wants them louder, the
  first lever is the spark size, then the chip count.
- **Next:** a faint pull line while `kit.mag_pull` bends the roll; the spiked-ball flare; scrap comet.

## Slice 7: the spiked ball (game feel's slice 3, 2026-11-12)
- **ball_spiked** (`spiked`): slot 3 pressed mid-roll. An amber crackle on the shell and the flare's plate glow on the
  rolling ball; the scales stay lit after the roll until flare_end (the kit owns the timeout).
- **spike_burst** (`spike_burst`): the flare's burst ring (radius from `kit.flare_radius`, 2.5 m) around the target,
  stacked on the iron ball's crash, plus 8 flakes and a spark. The ring and flakes are shared with the standing flare
  through `_flare_ring`, which now also draws at render_priority 3 over the floor zones.
- **Recording:** `D:/dev/_scratch/pangolin-fx/rec/pangolin-spiked-ball.mp4`. Frames show the glowing ball rolling
  through the minion and a bright double ring at the crash.

## Slice 8: magnet pull line (2026-11-13)
- `_update_pull`: while `kit.rolling` and `kit.mag_pull` is set, a ribbon in a new mode 2 of `pangolin_rail.gdshader`
  runs from the enemy's chest to the shell, faint copper with amber pulses travelling toward the ball. On in 0.08 s,
  off in 0.15 s, below HDR 1.05, with no light.
- **Recording:** `rec/pangolin-magnet-pull.mp4`. The roll visibly bends to the magnetised gorilla, but **the line is
  too faint at match distance**. It needs a brightness and width pass (width 0.12 to about 0.2, base 0.3 to about 0.5).

## Slice 9: scrap comet (2026-11-13)
- Cues as proposed and adopted by game feel: comet_start, comet_roll, comet_hit, comet_burst; ball_bounce and
  ball_bowl also fire.
- **comet_start:** 12 plates, plus 2 for each salvage plate still worn (up to 18), arc onto the ball in 0.35 s. They
  stick on and turn with the roll. The shell glow runs hot, and the furrow widens with comet_size.
- **comet_hit:** the iron ball's crash plus a spark. **comet_burst:** the flare ring at comet_radius (4 m), a 2.2
  spark, a 0.18 s light, and the stuck plates thrown outward as falling chunks.
- **The model takes over the plates:** the 3D lane's arena model (round 11) has the stuck-on plates as real geometry,
  with Comet_Gather, Comet_Roll and Comet_Burst. When the body has Comet_Gather, the effect draws no plates. It draws a
  pull field instead (10 scrap chunks and dust drawn in to land at 0.3 s), a slam flash at 0.32 s, and 12 debris
  chunks at the burst. The kit still plays Ball_Roll for the comet; game feel has been asked to switch to the new clips.
- **Recording:** `rec/pangolin-scrap-comet.mp4` (the real kit, from before that switch).
- **Pull line fix (2026-11-13, Preston: "Yes, brighten it"):** brightening alone did not help. The match camera sits
  behind the ball, so a straight line to the enemy is seen end-on. The ribbon now bows up into a field arc: the
  `arc` uniform is 30 percent of the span, kept between 0.6 and 2.0 m. The quad is subdivided 24 times so it bends,
  and the width went from 0.12 to 0.22 with a base glow of 0.5. The re-recording shows the arc clearly over both machines.
- **Round 11 clips in (2026-11-13):** game feel now plays Comet_Gather, Comet_Roll and Comet_Burst. The pull field and
  the slam flash fire on Comet_Gather's "pull" (0.04 s) and "plates_on" (0.32 s) events, not on a timer from the
  cast. Re-recorded `rec/pangolin-scrap-comet.mp4`: the model plates gather with the dust pull, the slam flash, then the
  crash, two bounces, and the burst ring with debris.

## Slice 10: magnet field on the scrap shell (2026-11-14)

Preston: the scrap ball is the big part, the pangolin stays normal size inside, and the magnetism holding the shell together must be visible through the gaps.

- `shaders/pangolin_field_shell.gdshader`: rim-only additive sphere (fresnel squared), copper latitude bands drifting along the roll axis, amber flare on hits. The middle never fills, so the pangolin stays visible.
- `pangolin_fx.gd` `_update_field`: finds the model node `scrap_shell` each frame, takes its position and orientation, and sizes the sphere to `0.67 * scale.x` (the node scale, 2.0 to 2.6 from game feel). Eight mode-2 ribbons run from just inside the shell (0.97 of the radius) in to 0.64 m, the curled body.
- Bug fixed on the way: the first version used the world scale (0.56), which put the field inside the plates where it could not be seen.
- Recorded: `pangolin-scrap-comet.mp4` (log: field_on_shell true). The rim glow reads clearly on the ball edge from the match camera; the inner lines are subtle at this zoom and can be thickened if Preston wants them louder.
- 2026-11-14, Preston "Yes, thicken them": inner field lines widened from 0.12 to 0.26 m and their fade raised 1.4x. Re-recorded; the copper arcs now read around the ball from the match camera.

## Slice 11: bank-shot charge (2026-11-14, Preston: "A, bank-shot charge")
- New shader `shaders/pangolin_charge_band.gdshader`: one level copper hoop per charge (cue ball_charge), one inside the next, with dashes turning with the roll, an amber flash on each new charge, and hotter at 3 charges. Hoops around the roll axis were edge-on to the camera and read as a line, so they now lie flat.
- `charged_crash`: ball_hit with charges adds the copper flare ring, sized by charge count. At 3 charges it adds a white-amber flash and a 0.14 s light.
- `pop`: ball_pop draws a ring out to pop_radius, a puff ring and a spark, and the hoops flash once.
- Recorded: `pangolin-bank-charge.mp4`. The second and third charges in the recording are added by the recorder on an open lane; the real bounce charge is shown on the wall bank.

## Reference: Gemini scrap comet concept sheet (2026-11-17, sent by the Gemini test session, approved by Preston)
File: side-session-notes/local_b046f4d1.../gemini-pangolin-scrap-comet-effect-sheet-2026-11-17.jpg. AI-made concept, so it is a timing and idea reference only, never the reference for the look.
- **Worth taking:** clear dipole field loops (two lobes) before the plates arrive. Ours is a rim glow with latitude bands, and the loops read better as magnetism. Glow in the plate seams on the finished ball. A ground ring on the burst. Plates left smoking on the floor for a moment after it.
- **Not taken as is:** the field and trail are electric blue. Our rule is copper with amber. Blue would be a palette change, and that is Preston's call. The comet trail is a flat ribbon, and flat travelling effects were rejected on 2026-11-12. The sheet does not show the 2x size.
- **When:** the engine move to Unreal (2026-11-15) means a comet rework belongs in the Unreal port, not in the Godot reference.
- 2026-11-18: Preston picked "Copper, like the rest" for the comet field. The Unreal port (PangolinFx.cpp, row 44) films copper only.

## Slice 12: comet field in Unreal (2026-11-18, row 44)
- `D:/dev/mech-moba-unreal/Source/MechMoba/PangolinFx.h/.cpp`: a client-side subsystem with eight dipole field loops (the Gemini sheet's structure). Each loop is a camera-facing ribbon, sized from the drawn PangolinShell (ShellCentre bone, 118.861 x shell world scale). The loops grow over the gather, flash at the slam (0.32 s), hold and turn while it rolls, and fly out and fade on the burst.
- `Tools/make_pangolin_fx.py`: the additive material M_PangolinField. Copper per Preston. The Blue parameter stays off.
- The first take read cream-white, so the copper was deepened (base 0.42, pulses 0.8). Film: `D:/dev/_scratch/pangolin-fx/ue/pangolin-comet-field-unreal.mp4`. Full Check Migration passed on the second run; the first failed only on a grab network flake.
- Still to port from the sheet: seam glow, burst ground ring, plates smoking on the floor.

## Slice 13, Unreal burst ground ring (2026-11-18, hub row 50)
The concept sheet's burst frame, structure only: a low copper shock wall (55 cm) runs from the ball's edge to the kit's
400 cm reach in 0.3 s and fades by 0.75 s, with an amber leading edge, a floor glow behind it and a broken, uneven
crest. It replaces the kit's generic Impact ring for this burst (hidden from PangolinFx, no kit edit).
Filmed in Arena3v3 (Preston's pick). Additive read cream over the pale floor, so the ring is a translucent blend at
0.55 emissive; crest measured (218,181,99) on film. Video: D:/dev/_scratch/pangolin-fx/ue/pangolin-comet-burst-ring-unreal.mp4.

## Slice 14: comet field re-tuned for the arena (row 60, 2026-11-19)
- Preston: "Yes, re-tune field". M_PangolinField moved from additive to translucent, like the burst ring (row 50):
  opacity from strength, emissive = the colour's own hue times Level (0.55), pulses and slam flash to a peak of 1.045.
  Copper kept (Preston's pick); strength only. Every material connection is now checked in Tools/make_pangolin_fx.py.
- Filmed in Arena3v3 at the new default (ARENA_LOOK ev=0.00 tone=0.00) after a warm-up take. Warm pixels around the
  ball: median about (170 to 229, 117 to 162, 70 to 103), hue 20 to 31, zero near-white. The box also catches the
  ball's own orange plates, so these numbers are approximate.
- Against the Paragon bar (hub, private reference): the field is one looping layer, below the median 5.
