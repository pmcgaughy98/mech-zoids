# Hippo ability effects: synthesis (2026-11-11)

Hippo effects lane. Bar: SMITE 2, smooth and layered, not pixel art (Preston, 2026-11-11). Built on the rhino lane's
method (`rhino-fx-synthesis-2026-11-11.md`) and its corrections: small, short impact flashes, no drifting glowing
motes, no point light washing the mech out.

## Where the hippo stands (read first)
- **Kit:** `scripts/moba3d/hippo_kit.gd` has only the basic bite. Its only signals are `cue` (bite, bite_whiff) and
  `impact`. No ability has code yet.
- **Kit direction:** Preston picked **pressure** (hub notes, `hippo-pressure-kit-2026-11-11.md`): Vent (slot 1, the
  yawn), Piston Drop (2, belly flop), Coolant Dump (3, wallow), Lockjaw (4, chomp), the tank meter as the passive.
  `docs/plan/moba-kits.md` still shows the older names.
- **Clips with events** (hippo 3D lane, round 7, arena copy r10), fired through `MechModel3D.event`:
  Yawn jaw_open 0.10, cone_start 0.35, hit 0.45, cone_end 0.95; Belly_Flop push_off 0.22, hit 0.72, get_up 0.98;
  Wallow mud 0.22, rise 1.00; Chomp capture 0.24, release 1.12.
- So the existing signal an ability effect can hang on is the body's clip `event`, not the kit. That is what the
  first slice uses.

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Bacchus "Belch of the Gods" (youtube Zqv_rMwYDtQ, "How to play Bacchus in Smite 2", 720p, 114.6 to 117.0 s) | **Measured** at 15 fps (one cell = 0.067 s), sheet `D:/dev/_scratch/hippo-fx/ref/belch15.jpg` | The cone's timing and layers, below |
| SMITE 2, Bacchus "Intoxicate" (same video, 131.5 to 135.5 s and 143.5 to 147.5 s) | **Measured** at 7.5 fps, `belch_a.jpg`, `belch_b.jpg` | A liquid pool on the floor: the structure for Coolant Dump later |
| The tooltip in the same frames | Read | Belch is channelled and hits several times plus a final hit over about 1.5 s |
| Overwatch, Mei's frost stream; SMITE, Ymir's Frost Breath | **General knowledge only**, not watched | A spray reads as a dense core near the source that breaks into billowing vapour farther out |
| The hippo 3D lane's notes (rounds 6 and 7, pressure kit) | Read | Clips, events, the mouth position, the pressure theme |

Clips are in `D:/dev/_scratch/hippo-fx/ref/`. Nothing from them is in the project.

## Structure learned from Belch of the Gods (measured)
1. **No grow-in.** The cone is on the floor at full size one cell after the cast (0.067 s). The body's wind-up is
   the anticipation; the effect does not build.
2. **Three layers.** A translucent fill (roughly 35 to 45% over the floor), brighter rims on both side edges and a
   bright far arc, and white-pink sweep bands inside.
3. **Sweeps per hit.** A bright band crosses the cone on each hit: at cells 3, 12, 19 and 25 to 26, so about every
   0.45 to 0.5 s, with the last one the biggest.
4. **The victim reads it, not only the cone.** Each target hit shows a swirl ring at chest height for about 3 cells
   after the last hit, and SMITE's red enemy outline.
5. **Clean exit.** The cone is gone within one cell of the last hit; only the victim marks linger.
6. **Total about 1.7 s** (cells 2 to 27). Small drifting bubbles ride the cone (we leave those out: Preston cut the
   rhino's "light balls").

From Intoxicate, for later: one magenta flash cell, then a liquid pool with ragged, splashy edges, lighter streaks
on its surface, lying 2 s or more.

## Synthesis proposal (nothing here is canon)

**Look:** smooth shader layers, the rhino lane's rules (bright cores above HDR 1.05 so they bloom, everything else
under; additive quads write ALPHA with fog_disabled). Colour for the pressure kit: **vapour, white core and pale
aqua** (#e0ffff core, #8ceaf2 mist, #9edbe0 puffs). Not Bacchus's wine purple (no god colours), not red.

Alternatives named:
- **A (built): white and aqua vapour.** Reads as pressure and steam; clear on the dark blue floor. Risk: near the
  blue team ring's family.
- **B: the tank pink (#ff3fa8)** the look lane gave the hippo's windows, so the spray is visibly the tank's fluid.
  Ties to the body best, but sits close to Bacchus's magenta.
- **C: amber hot steam.** Distinct from every team colour; reads as heat rather than water.

**Effect list (proposal):**

| Ability | Hooks (clip events) | Proposal |
| --- | --- | --- |
| 1, Vent (built) | Yawn cone_start, hit, cone_end | Floor cone at once, white jet from the jaws, streaks running out, a sweep band per tick, vapour thrown along the cone, gone in 0.12 s after cone_end; enemies inside get a burst of vapour |
| 2, Piston Drop | Belly_Flop push_off, hit | Push-off: two short piston jets down from the thighs. Landing: a small flash, a shock ring from the feet, a ring of vapour rolling outward low; reuse the rhino lane's crack web only lightly (it is the rhino's signature) |
| 3, Coolant Dump | Wallow mud, rise | A glowing pool with ragged splash edges and surface streaks (Intoxicate's structure), lying for the kit's duration; the tank windows dim through `mech_look.set_glow` as it drains |
| 4, Lockjaw | Chomp capture, release | Capture: pressure clamps, two short jets from the jaw hinges; while held, steam leaks at the hinges; release: a vapour trail on the flung target |
| Passive | none needed | The tank windows brighten with the meter (look lane's glow); at full, a faint vapour wisp at the back pipes |
| Soaked | needs the kit | A thin wet sheen or drip on enemies hit, for the damage-down's length (SMITE marks the victim) |

## First slice (built 2026-11-11): Vent
- `scripts/moba3d/hippo_vent_fx.gd`, `shaders/hippo_vent_ground.gdshader`, `shaders/hippo_vent_jet.gdshader`; the
  vapour puffs reuse `shaders/rhino_dust.gdshader` with an aqua colour. Observer only: it connects to the hippo
  body's `event` signal and acts on the Yawn clip. No kit, clip or signal was changed.
- Proposal numbers: range 5.5 m, 60 degree cone (the kit has none for the Vent yet).
- Not installed in a launcher yet: nothing plays the Yawn from a key until the kit is ported. The recording adds
  the node to the hippo by script. Install line for whoever ports the kit:
  `var fx = load("res://scripts/moba3d/hippo_vent_fx.gd").new(); player.add_child(fx); fx.setup(player)`.
- Recording and frame check: see the end of this file.

## Recorded and frame-checked (2026-11-11)
- Videos: `D:/dev/_scratch/hippo-fx/rec/hippo-vent-in-match.mp4` (8.4 s, arena_play at the game camera, recorded with
  `--write-movie --fixed-fps 60`) and `hippo-vent-side-quarter-speed.mp4` (the side vent at quarter speed).
  Recorder: `D:/dev/_scratch/hippo-fx/rec/record.sh` and `hippo_vent_rec.gd`.
- Three vents: straight ahead (from behind), sideways to the right, then diagonal with nobody in it. Every Yawn event
  fired (jaw_open, cone_start, hit, cone_end); all three minions in the cone were soaked on each of the first two;
  none on the third, as placed.
- Seen in the frames (15 fps sheets): the cone is on the floor within one frame of cone_start, the jet leaves the
  jaws, the sweep band crosses on the hit, and everything is gone about 2 frames after cone_end. Smooth, no pixel
  shapes, no point light.
- First take corrected: from behind, the floor cone was too faint and the jet's throat bloomed into a white blob over
  the hippo's head. Fill and rims raised, the throat cut to a small core, vapour puffs 0.42 to 0.3.
- Still falls short: from directly behind the hippo its body hides most of the cone (the sideways vent reads best);
  where the jet overlaps a target it reads near white rather than aqua; no sound; the soaked damage-down has no mark
  of its own on the victim (needs the kit's duration).

## Next (proposal, in order)
1. Preston's call on colour (A vapour aqua, B tank pink, C amber steam) and on the 5.5 m, 60 degree size.
2. Piston Drop: piston jets at push_off, a small landing flash and a low vapour shock ring at hit.
3. Coolant Dump: the pool, after Intoxicate's ragged liquid edge, plus the tank windows dimming.
4. Lockjaw: hinge jets at capture, leaking steam while held, a trail on the fling.
5. The soaked mark on victims and the full-tank passive wisp, once the kit is ported (game feel lane).

## Toxic purple version (Preston, 2026-11-11)
"Make it the purple liquid I want it to have a poisonous or toxic type effect. Or noxious ode". His named visual, so
it goes in as said; colour alternatives A to C above are closed.
- The spray is now a violet liquid stream (blend_mix, so it is wet and dark, not light) that breaks into filaments,
  with a small lilac-white throat and highlights over HDR 1.05 for a toxic sheen. Colours: liquid #4d1275, sheen
  #c75cff, hot #ffd1ff.
- New: the spray leaves a **toxic puddle** in the cone (Intoxicate's ragged liquid structure) that glows, pops small
  bubble rings, and shrinks from its edges over 1.6 s (PUDDLE_LIFE, a proposal); violet noxious gas lifts off it.
- First toxic take: a dark puddle and dark gas vanished on the arena's dark blue floor. The puddle now glows with a
  bright lip at its edge, the gas is light violet. Checked in frames at 7.5 fps on the sideways vent.
- Videos: `D:/dev/_scratch/hippo-fx/rec/hippo-vent-toxic-in-match.mp4` (11.4 s) and
  `hippo-vent-toxic-side-quarter-speed.mp4`.
- Watch: the purple is close to the hippo's own body and to the purple fennec ally; the puddle is visual only (no
  damage or slow is tied to it; that is a kit call).

## Piston Drop (slice 2, 2026-11-11)
Built to the new kit plan (`docs/plan/hippo-kit-pressure-2026-11-11.md`): the landing pumps pressure into the floor and
the ground erupts about 0.5 s later, Bacchus's delayed burp stun moved to the dive (Preston).
- Code: `scripts/moba3d/hippo_drop_fx.gd`, `shaders/hippo_drop_ground.gdshader`; the geysers reuse the Vent's jet
  shader upside down, the gas reuses `rhino_dust.gdshader`. Observer on the body's Belly_Flop events (push_off, hit).
- push_off: toxic gas blasts out from the four legs. hit: a thin liquid shock ring rolls out to 3.2 m, gas thrown low,
  then the warning: a violet disc, a rim pumping faster and faster, veins brightening. +0.5 s: a short pale core, a
  low splash wall at the rim and a narrow central geyser (gone by 0.38 s), then a toxic pool that bubbles and shrinks
  away over 1.1 s. The eruption is timed in the effect from the landing until the kit emits its own cue.
- First take: the eruption pool flooded the bottom of the screen and the 2.6 m central geyser read as a flat purple
  box. Pool kept inside the rim and thinner, the splash wall 0.9 m, the geyser 1.7 m, both faster.
- Videos: `D:/dev/_scratch/hippo-fx/rec/hippo-drop-in-match.mp4` (drop into three minions, then the Vent as the
  combo; then a drop toward the camera) and `hippo-drop-quarter-speed.mp4`. Recorder: `record_drop.sh`. The hippo is
  moved 4.5 m between push_off and hit by the recorder (the clip is in place).
- Not done: the stun read on victims is the kit's (Fx3D stun_loop); no sound; the pool does nothing in play.
- Seen in the log, not mine (fixed since, per the look lane): `rhino_fx_installer.gd` threw "Cannot convert argument 1 from Object to Object" in
  `_attach` on arena_play runs before that fix.

## Lockjaw (slice 3, 2026-11-12)
Preston: Lockjaw drags the enemy "into the lake". The hippo 3D lane split it into Lockjaw_Clamp (capture 0.24),
Lockjaw_Carry (a 0.5 s walk loop, carry_speed 1.75 m/s) and Lockjaw_Slam (slam 0.28, release 0.31).
- Code: `scripts/moba3d/hippo_lockjaw_fx.gd`, `shaders/hippo_clamp_ring.gdshader`; splashes reuse
  `hippo_drop_ground.gdshader` (new `flash_mul` uniform, default 1, so the Piston Drop is unchanged), gas reuses
  `rhino_dust.gdshader`. Observer on the body's Lockjaw clip events; the mouth is tracked on the Jaw bone (calibrated at
  capture to the measured mouth point), with the measured point as the fallback.
- capture: a short pale core at the bite (no light), toxic gas hissing out of both jaw hinges, and a violet pressure
  band that snaps shut round the victim. The hold reads on the victim, as SMITE does it.
- held: the band pulses; gas leaks from the hinges; dark purple drops (wet, not glowing) fall from the jaws and leave
  a trail of small puddles behind the drag.
- slam: a 1.8 m toxic splash ring and pool where the victim hits the floor, the band bursts outward, the hinges vent.
- First take: the band read near white over the pale minion; the hot term was cut so it stays violet.
- Videos: `D:/dev/_scratch/hippo-fx/rec/hippo-lockjaw-in-match.mp4` (two Lockjaws: sideways, then toward the camera)
  and `hippo-lockjaw-quarter-speed.mp4`. Recorder `record_lockjaw.sh`; it stands in for the kit by walking the hippo
  1 s at 1.75 m/s and holding the minion at the jaws.
- Not done: the slam into an existing lake gets no extra splash yet (needs the kit to say the victim is in a pool);
  no sound; whether the Jaw bone was found was not logged, though the band tracked the mouth in the frames.

## Toxic Flood (slice 4, 2026-11-12)

Files: `scripts/moba3d/hippo_flood_fx.gd`, `shaders/hippo_flood_lake.gdshader` (new); reuses `hippo_drop_ground` (the
gather disc), `hippo_vent_jet` (the wave wall, upside down) and `rhino_dust` (gas). Hooks the body's `Toxic_Flood`
events, no kit edits. Install: `var fx = load("res://scripts/moba3d/hippo_flood_fx.gd").new(); player.add_child(fx); fx.setup(player)`.

Structure, from Intoxicate (measured, above): one short beat, then a liquid pool that lies for seconds.
- charge 0.05: the tank windows flare (MechLook.set_glow on "Hippo glow", 1.6 to 4.5), gas hisses from the back pipes.
- rear_up 0.35: the Piston Drop's pumping warning disc under it, small (2.2 m), timed to end on the burst.
- burst 0.75: a small pale beat (0.22 s, no light), ten gas puffs thrown out low, a liquid wall rolls out to the lake
  edge in 0.45 s and drops, the lake spreads behind it. Windows go dark (0.25): the tanks are spent.
- lying: ripples run outward, streaks drift, bubbles pop, fumes rise; last second it shrinks back into blotches.
  Windows refill slowly to 1.6 over the lake's life.
- drain_end 1.3: a last hiss from the pipes.

Proposals for Preston (not canon): lake radius 6 m, lake life 4 s.

Recorded checks: first take was flat bright violet that hid the floor (read as paint); body made darker and thinner
so crests, streaks and lip carry it, and the wave wall raised 1.5 to 2.0 m. Recording note: the movie writer wrote
0 to 51 frames twice with a normal window; `--always-on-top --windowed` fixed it.

Heal read (added same day, `shaders/hippo_heal_ring.gdshader`): while the hippo stands inside 85% of the lake radius,
one pulse per heal tick (HEAL_TICK 0.5 s, a proposal to match the kit's tick when it exists). Each pulse: a violet ring
on the floor drawn in to its feet (0.25 s), then a mint band runs up its body (0.45 s), brightest at the silhouette.
Same grammar as the gorilla shell's heal pulse (green band running up), so heals read alike across the roster; the
drawn-in ring says the heal comes from the lake. Stops outside the lake, resumes on stepping back in (recorded).
First take washed the hippo near-white mid-body; cut to a thin, half-strength band with almost no white core.

Not done: anything on enemies standing in the lake (a poisoned tick read). The push-out of enemies is the kit's (game
feel lane).

## Vent puddle matched to the kit (2026-11-12)

Preston: "match it". The Vent puddle is now the kit's damage circle: pool_radius 1.6 m, centred 0.6 of range_m from the
hippo's centre, lasting 3 s (PUDDLE_LIFE) like the kit's ticks; fumes rise only over what is left. Recorded sideways in
a match with the kit's own copy of the effect. Next for this lane: the downward spray for Vent pressed in the air
(kit emits "vent_air" on the press; puddle at the landing spot).

## Vent in the air (2026-11-12)

The kit (game feel lane) fires Vent pressed during the Piston Drop's flight as cues, not a clip: "vent_air" on the press,
then on "drop_land" it hits within 2.6 m and lays the 1.6 m, 3 s puddle at the landing spot. hippo_vent_fx.gd now
listens to the kit's `cue` signal (player's "Kit" node). Look: a jet spraying down and a little ahead from the jaws that
rides the arc (hippo_vent_jet), gas puffs where it strikes; on landing, twelve gas puffs thrown out to the 2.6 m hit
circle and a round puddle (hippo_flood_lake, 1.6 m, spread 0.2 s, 3 s) with fumes. Recorded through the real kit
(piston_drop then vent mid-flight): both cues fired 0.33 s apart. The puddle sits under the hippo at landing, so it
mostly shows once the hippo moves off; that follows the kit's placement.

## Lockjaw on the real kit (2026-11-12)

With the kit's Lockjaw in, the clip's "capture" event also fires on a whiff, so the effect drew the clamp band and its
drips never stopped (no slam or release follows a miss, or a break-free). Now, when the player has a "Kit" node, the
effect follows its cues instead: lockjaw_clamp (caught someone) starts the band and drips, lockjaw_slam the splash,
lockjaw_whiff only a small hiss. A safety ends the hold if the body is off any Lockjaw clip for 0.2 s. Without a kit
(the scratch recorders) it still runs from the clip events. Headless check through the kit: a catch gave cue clamp,
cue slam, release; a whiff gave cue whiff with nothing held.

## Poisoned read on enemies in the toxic zones (2026-11-12)

Preston: "Yes, poison read". Enemies standing in the Vent puddle, the airborne Vent's landing puddle or the Toxic
Flood lake now show it on their own body.

- **What it is:** an open cylinder sized to each unit's meshes (`shaders/hippo_poison_wisp.gdshader`, blend_mix). It
  carries violet fumes streaming upward, thickest low and at the silhouette, gone by the top. On each damage tick
  the fumes lift for a moment and three soft gas puffs (`rhino_dust.gdshader`, violet) rise off the unit. The fumes
  linger 0.8 s after the unit steps out, then fade. Every colour stays under 1.0: it reads as gas, never light. It
  has no motes and no flash.
- **Script:** `scripts/moba3d/hippo_poison_read.gd`. The Vent and Flood effects each make one as a child named
  `PoisonRead` and call `add_zone(centre, radius, life, tick)`.
  - Vent zones start on the kit's `vent_puddle` cue at `kit.last_puddle`, which covers the ground spray and the
    airborne landing alike.
  - The Flood zone starts at the burst and uses the kit's own `lake_radius` and `lake_tick` (slice 4).
  - It is an observer only: it reads positions and never deals damage. It never touches a unit's nodes or materials,
    which belong to other lanes.
- **Checked in a match** (`hippo_poison_rec.gd`, real kit, tough minions):
  - The read ticked 8 times in the puddle and 24 times in the lake. The kit's own counters said `puddle_hits 8` and
    `lake_hits 24`, so every visible tick is a real hit and the reverse.
  - A minion moved out of the puddle stopped ticking and its fumes faded.
- **Falls short:** the fumes tint the unit rather than mark it strongly. On a pale minion inside the bright Flood
  lake the read is softer than on the floor. A stronger option is a toxic sheen on the unit's own surface, but that
  means an overlay on another lane's materials, so I left it out.

## Overcharged Vent puddle (2026-11-12)

The kit's slice 4 makes an overcharged Vent's puddle last `overcharge_puddle` (2) times longer. The Vent effect now
reads that length from the kit: `_puddle_life()` returns `puddle_life`, doubled while the kit's overcharge window is
open. That length drives the ground puddle's shrink, the airborne landing puddle and the poison zone. Checked
headless through the kit: a normal Vent gave 3.0 s for both the puddle and the zone, and an overcharged one gave 6.0 s.
The slow on an overcharged puddle has no read of its own yet.

## Pressure Tanks: liquid level and glow in the tank windows (2026-11-12)

Preston: "tank glow", then "not only glow but the liquid too".

- **What it shows.** The kit's `pressure` (0 to `pressure_max`) is a toxic liquid level inside both flank tank windows:
  - empty: dark glass;
  - filling: the level rises with a pale meniscus that sways, bubbles rising;
  - overcharged: full to the top, boiling faster, the glow pulsing;
  - `overcharge_spent` and `tanks_drained`: it empties in about 0.4 s and sloshes.

  The window glow (`MechLook.set_glow` on "Hippo glow") follows the same level, from 0.3 empty to 1.6 full (the hippo 3D lane's own strength), and pulses up to 2.5 when overcharged. Toxic Flood keeps its charge flare and burst drop. While it does, it sets the actor meta `hippo_glow_hold`. It hands the glow back once the lake settles, and the windows then stay dark because the kit says the tanks are drained. The old slow refill over the lake's life is removed, since it contradicted the kit.
- **Files.**
  - `scripts/moba3d/hippo_tank_read.gd`, created by `hippo_vent_fx.gd` as the child "TankRead".
  - `shaders/hippo_tank_liquid.gdshader`: unshaded, `blend_mix`, `fog_disabled`; only the boiling meniscus goes above 1.0.
- **How it sits in the window.** The window glass is painted into the body texture. It is black there, and the pink seen in game is the sky reflecting off it. I measured this: there are no pink texels anywhere in the window box. Drawing on the model's own window triangles therefore failed: the glow-surface triangles cover the ring and stripes, and the black texels cover only panel seams.
  - The liquid is an own rounded-rectangle panel per window, fitted from close shots: centre (±0.70, 0.60, -0.30), half size 0.40 by 0.20 in the body mesh's space.
  - Each frame it follows the Chest bone.
  - The hippo's mesh, skeleton and materials are read, never changed.
  - If the hippo 3D lane moves the windows, `WIN_CENTRE` and `WIN_HALF` need re-fitting.
- **Check.** Recorded through the real kit (`_fill` in steps, then full, an overcharged Vent, refill to 75, then Toxic Flood). The read gave:
  - fill 0.24, 0.48, 0.72 and 0.96 at pressure 24, 48, 72 and 96;
  - 1.0 overcharged, then 0 after the spend;
  - the glow held by the flood at +1 s and 0.3 drained at +3.5 s.

  Close shots of both flanks confirm the fit.
- **Falls short.**
  - At the game camera the level reads best between about 25% and full. The window's rounded bottom makes low levels look lower than they are.
  - The bubbles are regular dots; they could be fewer and less even.
  - The panel is flat while the glass is slightly curved, so a very low side angle may show the panel's edge.

## Overcharged Vent slow: goo on the legs (2026-11-13)

Preston: "build the overcharge slow read next". In kit slice 4, an overcharged Vent's puddle lasts twice as long and slows anyone standing in it.

- **What it shows.** Thick dark-violet goo grabs the legs of an enemy that is in an overcharged puddle and actually slowed by the kit:
  - a coat on the lower legs, with strands reaching up the body and beads sliding back down them;
  - a wet sheen along the top edge;
  - a sticky patch on the floor under the unit.

  It grabs in 0.15 s and lets go 0.35 s after the slow stops being refreshed, which happens when the enemy steps out or the puddle ends. The strands stretch when the enemy moves. The poison fumes rise, so the goo is made heavy and sinking to read as a different thing.
- **Files.**
  - `shaders/hippo_slow_goo.gdshader`: unshaded, `blend_mix`, `fog_disabled`. No `pow` on negatives. The patch draws at render priority 3, above the floor zones.
  - The goo is part of `hippo_poison_read.gd`. `add_zone` now takes `slows`.
  - `hippo_vent_fx.gd` passes `_overcharged_now()`, the same test the kit makes (`_clock < _boost_until`).
- **Check.** Recorded through the real kit, with an enemy rhino machine and a minion in the puddle:
  - normal Vent: fumes only;
  - overcharged Vent: goo on both from the first slow tick (the log reads "slowed RedRhino" and "slowed minion" at +0.5 s, and the kit's `slowed` was 0.6);
  - the rhino steps out: the goo lets go and the fumes linger.

  The recording keeps the hippo's health topped up and lets the enemies run at zero speed, so their hit flash fades normally.
- **Falls short (first pass).** The strands read a little like violet crystal shards rather than soft goo at the game camera. The coat is drawn on a cylinder round the unit, so it does not follow leg shapes.
- **Refined 2026-11-13: one sleeve per foot.** Two faults were found by painting the sleeves solid green in a recording:
  - **UVs.** Godot's CylinderMesh does not run UV.y 0 to 1 down its side, so the shader's height test never drew the solid coat; only stray strand tips showed, which is why they read as shards. The shader now takes height and angle from the vertex (a `height` uniform per sleeve).
  - **One cylinder cannot fit a big machine.** Round the whole rhino it had to be 3.2 m across to clear the body and read as a haze wall; pulled in, it sat inside the body, hidden. Now each foot gets its own sleeve: the feet are the lowest non-root bones away from the middle, one per 0.35 m cluster, up to six. Each sleeve follows its bone, about 0.36 of the mark radius wide so it clears the foot. A unit with no skeleton falls back to one sleeve round the middle.
  - **The look.** The coat is thicker and darker at the ground and thins up the leg, and its edge fades where the sleeve is seen side-on. Strands are fewer and wider, with rounded tips.
  - Checked at the game camera (`hippo-slow-in-match.mp4`, 7.4 to 8.6 s): dark goo grips all four rhino feet and lets go when it steps out. The kit still logs "slowed RedRhino".
  - **Still short (then):** at the game camera it read more as dark boots than as wet, dripping goo.
- **Drips and wet shine (2026-11-13, Preston: "Yes, add drips").** About two in three of nine columns round each sleeve drip on their own clock. Each drop sags at the lip for the first third, then runs down the coat to the ground, leaving a thin trail. A glossy streak, broken up with noise, runs down the side facing the camera. Up close, a pale drop on the dark coat is plain to see. At the game camera the sleeves now read glossier and wetter, but each single drop is small: a few pixels.

## Hippo at scale 1.25 and r12 (2026-11-13)

The hippo 3D lane made the hippo bigger (profile "scale" 1.25) and installed the r12 repaint.

- **Tank panels.** They grow with the body and still fit both windows; checked in close shots of both flanks.
- **Effect points on the body.** These are now multiplied by the model scale through `_bs()`:
  - Vent's mouth;
  - Piston Drop's leg puffs;
  - Lockjaw's mouth, and its gas point behind it;
  - Flood's back pipes, burst core and heal band.

  The kit's gameplay radii stay in metres. Vent and Flood were re-recorded at 1.25 and the spray leaves the jaws. Piston Drop and Lockjaw were re-recorded at 1.25 on 2026-11-13 (`hippo-drop-jaw-125.mp4`): the landing ring and eruption, the jaw band and the back gas all sit on the bigger body.
- **Recording gotcha.** `spawn_minion(team, at, power)` multiplies a minion's damage as well as its health, so power-20 minions hit for about 400 and killed the hippo on landing. Test minions with high power must be process-disabled (or run at zero speed with their attack off), and match bots and towers disabled too.
- **Roster-check warning.** The "no 'Hippo glow' surface" warning came from the tank read building on a non-hippo body while the check swaps machines. It is now a quiet log row.

## Chin tank: live liquid (2026-11-14)

Preston said "Yes, chin tank" after the hippo 3D lane painted a small front tank under the jaw (r14). The tank read now builds five panels, all riding the Chest bone: the two flank windows, two small side windows on the chin tank housing, and the chin tank's front glass. All five share the same level, bubbles and glow.

- **Side windows (17 by 12 cm, centre |x| 0.40, y 0.455, z 0.715).** They fit and follow pressure. Checked at 60, 35 and 15 percent: dark glass when low, liquid and surface line when full.
- **Front glass.** The plane comes from the hippo 3D lane's fit to the 10,016 glass texels. Centre (-0.023, 0.289, 0.694), normal (0.013, -0.936, 0.352), 0.666 by 0.711, in body space before the 1.25 scale.
  - A first guess from the bounding box sat inside the glass, hidden.
  - A flat panel on the fitted plane, pushed out 5.5 cm, stuck out past the housing as a blade, because the glass is a dome: 5 cm out in the middle and 14 cm back at the edges.
  - It is now bent into a matching dome, 2 cm proud, and sits inside the housing.
- **Falls short.**
  - The glass faces almost straight down, so the game camera never sees it; only low close shots, such as a workshop view, do. In those shots, at partial pressure it shows mostly dark glass with only a tip of the surface line.
  - r16, which repaints the chin glass plain dark, was not installed yet when this was checked, so the panel was judged over the old painted liquid.
- **Decision.** Preston, 2026-11-14: "Leave it as is." The front glass stays as built; no more polish, since the game camera never sees it. r16, the plain dark glass, is now installed.

## Unreal: hippo event timings for the effects (from the hippo 3D lane, 2026-11-16)

The MOBA is moving to Unreal (Preston, 2026-11-15). When the hippo effects are ported, they should fire on these HippoKit.cpp times, in seconds from each action's start. They match hippo.events.json and the Unreal film within one 30 Hz frame.

| Action | Events |
|---|---|
| Bite | hit .26, end .45 |
| Jaw_Swing | hit .24, end .42 |
| Stomp | hit .42, end .65 |
| Yawn (Vent) | spray .45, end 1.3 |
| Belly_Flop (Piston Drop) | push-off .22, landing .72, eruption landing + .5, end 1.4 |
| Lockjaw_Clamp | capture .24, end .5; carry up to 1.0; slam .28, end .85 |
| Toxic_Flood | burst .75, end 1.7 |

HippoKit logs each one as a HIPPO_* line: HIPPO_BITE, HIPPO_VENT, HIPPO_DROP_LAND, HIPPO_ERUPT, HIPPO_CLAMP, HIPPO_SLAM, HIPPO_FLOOD_BURST. The hippo 3D lane reports that the Unreal Hippo_glow material looks unlit (a flat pale tank window); they are checking its emissive, so the tank glow should not be ported on top of it yet.

## Toxic Flood concept sheet from Gemini (2026-11-17, sent with Preston's approval)

An AI-made 8-frame sheet, kept as a concept and timing reference only. It is not a texture or a look target, because AI work is never the reference. The sheet is in the hub's shared notes: `gemini-hippo-toxic-flood-effect-sheet-2026-11-17.jpg`.

| Frame | What it shows |
|---|---|
| F0 | three violet glows at the tanks, with green vapour |
| F1 | three violet geysers |
| F2-F4 | a standing wave ring with a curling, foamy crest |
| F5 | the wave breaks into spray |
| F6 | a glossy lake with popping bubbles and low green vapour |
| F7 | the lake fades from the rim |

- **Worth taking.** The wave as a real standing wall with height, and a bubbling lake surface. The flat-effect rejection of 2026-11-12 points the same way.
- **Not to take.**
  - The wave barely grows between frames, so it reads as a pool, not a spreading lake.
  - F0 reads as flames, not tanks under pressure.
  - The green vapour fights the toxic-purple rule. It could only be a faint accent, and only if Preston wants it.

## Unreal: the Flood's standing wave (2026-11-18, hub row 42)

What was built (in `D:/dev/mech-moba-unreal`; nothing committed):
- `Source/MechMoba/HippoFx.h/.cpp`: `UHippoFxSubsystem` watches each hippo's replicated state. When Toxic Flood is used (Kind 3, action 53), it waits .75 s after `State.Started` and then spawns `AHippoFloodWaveFx` at the hippo's feet. It is cosmetic and client only.
- The wave is a procedural ring, 72 segments by 10 profile rows. Its curl profile is rebuilt every tick at the current radius, so the lip never stretches. It grows from 170 cm to 600 cm with a cubic ease-out over .55 s, rises in .12 s, then breaks over .45 s (the crest drops forward and the wall tears into holes). Its height is 150 cm.
- `Tools/make_hippo_fx.py` creates `/Game/Hippo/Fx/M_HippoFloodWave`, a Custom node that is translucent, unlit and two-sided:
  - Flowing streaks run down the face.
  - A lighter crest band carries noise foam.
  - The lip breaks into drops.
- Shared files: the ProceduralMeshComponent plugin is turned on in `MechMoba.uproject` and added to `MechMoba.Build.cs`.

Lessons:
- **The scene's exposure lifts unlit translucent colour a lot.** In v1 the goo purple was (0.42,0.13,0.58) and it filmed near white, around (240,200,245) on screen. v2 is about a third of that and more saturated: deep (0.035,0.006,0.06), goo (0.13,0.025,0.21), sheen (0.34,0.14,0.48). It films around (200,125,220), in the same family as the hippo's body. Start Unreal effect colours at roughly a third of their Godot values.
- **A new material, or a procedural-mesh material, draws nothing in its first `-game` take** while its shaders compile. Always do a throwaway take first.
- `-HippoFloodTint` paints the wave flat green, which confirms where it sits before you judge the look.

Still open:
- The kit's own small white hit sparks on the target remain. They belong to the kit, not to this lane.
- The curl is hard to read from the default camera because the wave reads mostly as a band. A lower camera, or a taller lip, is the next tuning step if Preston wants more "wave".

## Taller curl and arena lighting (2026-11-18 to 11-20, hub rows 54, 59 and 73b)
- **Lighting (row 54):** the Flood wave was filmed in Arena3v3 under the current and the proposed lighting. It read as toxic purple in both, so the colour was not tuned. Preston chose the proposed lighting, tone 0 and EV 0.0, which is now the arena default.
- **Curl v2 (Preston: "make curl taller"):** the wave is 210 cm tall, up from 150. The profile was changed so the crest throws to +0.56 of the wave height and the lip hangs down to 0.46. From the play camera it now reads as a rolling tube. Video: `D:/dev/_scratch/hippo-fx/ue/flood_taller_curl_arena.mp4`.
- **Row 59:** the full check failed 3 times on network-startup tests while the machine was overloaded, so v2 was rolled back.
- **Row 73b:** after the grab steady-server fix, v2 went back in and passed the full check first time, on DLL 82719D8B.
- **Next slice, offered:** a lingering 600 cm lake patch for the 4 s lake, `HLakeLife` in HippoKit. The client already knows when and where each burst lands, so no gameplay change is needed. The Vent puddle does need a replicated field from the kit owner.
