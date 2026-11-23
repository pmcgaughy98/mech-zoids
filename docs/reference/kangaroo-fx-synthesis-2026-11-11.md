# Kangaroo ability effects: synthesis (2026-11-11)

Kangaroo effects lane, started from the rhino effects lane's method (`docs/reference/rhino-fx-synthesis-2026-11-11.md`).
Preston's bar, as of 2026-11-11: effects may be made with any tool but must not look like pixel art; SMITE 2 grade
(smooth, layered, HDR). On the rhino he cut drifting glowing motes and a big white flash, so impact flashes stay small
and short and no light may wash the mech out. No red in the kangaroo's own effects (red marks enemies).

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, "How to Odin in under 6 minutes" (youtube ZVz1TUxCAQU, 1280x720 at 60 fps) | **Measured**: two Ring of Spears casts sampled at 15 fps (one cell = 0.067 s), 219.4 to 221.8 s and 248.6 to 251.0 s; the hold sampled at 7.5 fps, 251.0 to 255.8 s | Cast order and timing, how the wall comes up, what it looks like held, how it ends |
| Same video, captions | Read | The ring is a wall only enemies are stopped by; enemies who leave another way are chased by a spear; a section breaks after five basic hits |
| SMITE wiki, Odin (smite.fandom.com/wiki/Odin) | Search excerpt read | Ring of Spears: radius 30 units, 5 s, cannot heal inside, enemies who leave are slowed |
| Our own kit and clip | Read | `Ring_Cast` events: glove_tap 0.18 s, ring 0.42 s; the kit's `ring_cast` cue fires on the ring event; radius 5.0 m, 4.0 s, the ringed enemy is pulled back to 4.5 m |
| League, Mordekaiser's Realm of Death; League, Sett's Facebreaker | **General knowledge only**, not watched | Two other "you and me, nowhere to go" ultimates: Mordekaiser moves the pair to a separate space (a full screen tint and a ring border); Sett slams both sides together. Neither is a held wall |

Clips and frame sheets: `D:/dev/_scratch/kangaroo-fx/ref/` (`ring15_a.png`, `ring15_b.png`, `ring_hold.png`). Nothing from
them is in the project.

Why Odin and not Ravana: the kangaroo is an ode to Ravana's kit, but Ravana has no trap. The boxing ring's job
(one enemy cannot leave a circle for a few seconds) is Ring of Spears' job, so that is the structure to study.

## Structure learned (measured unless marked)

1. **The cast is a beam on the caster, not a flash on the ring.** On the cast frame a tall column of light stands on
   Odin for about 3 to 4 cells (0.2 to 0.27 s), with a glow around his body. Nothing happens at the ring's edge yet.
2. **The wall appears at full radius, it does not grow outward.** About 3 to 4 cells (0.2 to 0.27 s) after the beam,
   faint arcs appear on the ground at the full radius and brighten over the next 2 to 3 cells.
3. **It is built in segments.** The wall is a ring of overlapping arcs (scallops), not one smooth band; their tops
   dip between joins.
4. **Held, it is a translucent sheet with bright lines.** A bright line along the foot and a bright line along the
   top, a soft see-through sheet between, so units inside stay readable. It is the team colour (purple on this skin).
5. **It holds steady.** No pulsing while held in these frames; the brightness only changes when something happens.
6. **It ends by thinning.** In the last 2 to 3 cells at 7.5 fps (about 0.3 s) the sheet goes and the base line
   thins to a hairline, then vanishes.
7. **Scale.** At SMITE's camera the wall runs off both sides of the screen. Ours is 5 m: about 73% of the screen width
   at the game camera (the rhino lane's measure for 5 m).
8. **Not verified:** what the wall does when an enemy walks into it (none did in these frames), and whether there is
   a sound cue tied to the rise.

## Synthesis proposal (nothing here is canon)

**Look:** smooth shader effects in the kangaroo's mint (#52ffc7 region, the same mint as its forearm rings), white-hot
only in thin cores (ropes, posts, the beam's centre line), everything else under HDR 1.05 so it does not bloom.
Additive, fog off, writes ALPHA.

**Boxing ring (built, slice 1):** Odin's order, re-dressed as a boxing ring.
- Cast frame (the kit's `ring_cast` cue): a thin mint beam on the kangaroo for 0.25 s, a small centre core and a
  0.18 s light of energy 1 (small on purpose).
- 0 to 0.2 s: a floor wave runs out to the radius. **Ours, not Odin's** (his wall just appears); it ties the wall to
  the kangaroo so the player sees where it came from.
- 0.1 to 0.4 s: the wall comes up at full radius, eight spans out of step, like Odin's segments.
- Held: a 1.1 m wall with a bright foot, a soft sheet, **eight posts and three ropes** that sag between posts (the
  scallops become rope sag). The ropes light one per rhythm stack (0 to 3), with a pulse on each new stack, so the
  passive reads on the ult. A glow either side of the wall's foot on the floor and a faint apron inside.
- When the ringed enemy is held at the wall, the wall brightens there with ripples running out from the point.
- End: the wall sinks and fades in 0.3 s, then the finisher kick fires (its flash is the kangaroo lane's).

Alternatives named:
- **A (built):** posts and ropes. Reads "boxing ring" at a glance; the ropes give the rhythm a second home.
- **B:** Odin's plain segmented wall in mint, no posts or ropes. Closer to the reference, less ours.
- **C:** no wall, only a floor ring and a tether line from the kangaroo to the ringed enemy (Mordekaiser's
  "the two of you" read). Lighter on screen; loses "nobody gets out".

## Effect list for later slices

| Ability | Proposal |
| --- | --- |
| Ringed enemy mark | A thin mint ring under the trapped enemy plus a faint tether to the kangaroo, so it is clear which enemy is held (the wall already says where) |
| Finisher kick | A bigger version of the tail kick impact: hot core 1 frame, an arc of light following both feet, a dust ring where the enemy lands; the wall drops on the same frame |
| Basic chain | Smooth fist arcs (the kangaroo lane's trails rebuilt as soft additive ribbons), a small core on each hit, the hook's bigger |
| 1, hop and jab | A take-off puff and a landing ring of dust (smooth, warm grey, no light), then four quick fist cores |
| 2, tail kick | A tail-pad scrape on the floor at brace (0.14 s), a two-foot arc at the hit (0.50 s), a dust ring at land (0.74 s) |
| 3, guard | A soft mint shell in front of the gloves while held; on a block, a short hex-free flare on the gloves and the counter's core |
| Rhythm (passive, always on) | Already on the forearm rings (kangaroo lane); at full stacks the next basic's fists glow before the kick |

## First slice: the boxing ring (built 2026-11-11)

- Code: `scripts/moba3d/kangaroo_ring_fx.gd`, an observer on KangarooKit's `cue` signal (`ring_cast`). It reads
  `ring_centre`, `ring_radius`, `ring_on`, `ring_target` and `rhythm`. No kit edits. It hides the kangaroo lane's flat
  stand-in ring (kangaroo_fx.gd, `_live` items of kind `ring`) and the tail puff dropped on the same frame.
- Shaders: `shaders/kangaroo_ring_wall.gdshader` (posts, ropes, sheet, ripple), `kangaroo_ring_floor.gdshader`
  (wave, centre core, edge glow, apron), `kangaroo_ring_pillar.gdshader` (cast beam).
- Hookup: `load("res://scripts/moba3d/kangaroo_ring_fx.gd").attach(kit)`. Not yet called from the live game; see the
  next list.
- Recorded in `arena_play.tscn` at the game camera, `--fixed-fps 60` (`D:/dev/_scratch/kangaroo-fx/rec/`:
  `kangaroo-ring-smooth-in-match.mp4`, `kangaroo-ring-cast-quarter-speed.mp4`; recorder `kangaroo_ring_smooth.gd`,
  `record.sh`). One red minion; ring cast, three jabs (rhythm 3), the minion pushed out twice, the finisher kick.

**What the frames showed (checked by eye, 15 fps around the cast, 4 fps across the clip):**
- Cast: the beam shows for about 4 frames at 15 fps, thin, the kangaroo still readable; the floor wave runs out and
  the posts come up out of step over the next 4 to 5 frames. Ring held 4.0 s (logged), then gone in 0.3 s; the
  finisher kick fired after it.
- The far half of the ring and both sides read clearly; the near half is below the screen at this camera, as SMITE's
  is. Posts and ropes read as a boxing ring at a glance.
- Stand-ins hidden: 2 (the flat ring and its tail puff). No pale squares, no wash-out.
- The wall-contact ripple is visible but weak at the far wall (one frame brighter around the held minion). It fired
  twice (logged). It may need to be stronger to read in a real fight.
- With 3 stacks all ropes are lit, so the ropes are the brightest thing on screen for 4 s; they bloom (cores above
  1.05). If that is too much, drop the lit rope core from 1.6 to about 1.2 or narrow it.

## Second pass: the ult as an ode to Ne Zha (2026-11-11)

Preston, after the ring video: "gorilla ult and this are too similar to odin ult but I liked the arena. I was thinking
maybe we could somehow synthesis this into a nezha ode".

**Read and measured:**
- smite2.live, Ne Zha ability page (read): the ult is **Wind Fire Wheels**. Range 8.8 m, cooldown 90 s. Initial
  damage, then combo damage per hit, then landing damage. Pressing attack at the right time turns a combo hit into a
  crit. It ends early if the target dies. The target gets a brief window to cleanse after the first hit.
- "SMITE 2 NE ZHA GUIDE | How to play" (youtube vXgD4iHLCSQ, 1280x720): captions read; one cast **measured** at
  10 fps (one cell = 0.1 s) from 146.6 s. Sheet: `D:/dev/_scratch/kangaroo-fx/ref/nz10.png`.

**One cast, cell by cell (times from the dash start):**
1. **Dash, 0.4 s:** a fire trail at his feet as he closes in.
2. **Hit and launch, 0.4 to 0.9 s:** a burst on the target, which is lifted; he follows it up.
3. **Into the private space, 0.9 to 1.3 s:** the camera tilts up and the world **bleeds into a flat deep-red space**
   over about 0.3 s. Only he and the target remain. Nobody else can touch either of them (the guide: it "removes both
   of you from the fight briefly").
4. **The combo, about 2.5 s:** a **timing bar** sits under the target, a marker sliding along it. Strikes land
   about every 0.6 to 0.8 s, each a streak across the target and a burst, with the damage number popping. Crit
   presses add petal bursts.
5. **Back, 0.2 s:** the red snaps away to the real world on the slam frame.
6. **Landing, about 0.4 s:** they slam down, a fire ring knocks up anyone nearby, and he returns to where he started.

**Why this suits the kangaroo:** the timing bar is a rhythm game, and the kangaroo's passive is called rhythm. The
private space is the arena Preston liked. The difference from Odin (and from the gorilla's ult) is that the ring holds
**two machines and nobody else**, for a short fixed combo, instead of a big zone that the team fights in.

### Proposal (nothing here is canon)

**A, "Title bout" (recommended):** about 3 s in all.
- **Dash, up to about 8 m, 0.3 s:** the kangaroo bounds at one enemy machine under the aim. Mint streak at the feet.
- **Bell, 0.2 s:** on contact, a small 3 m roped ring snaps up around the pair (the posts and ropes from slice 1,
  scaled down). Outside the ropes the world dims and cools to dark teal on the player's screen (our version of Ne
  Zha's red space, in the kangaroo's colours; red stays the enemy marker). Both are untouchable while it stands.
- **Rounds, about 2 s:** four punches on a beat. A beat bar under the target (the kit's own rhythm); pressing attack on
  the beat makes that punch a crit and lights one rope. Crits get a white-hot core and a rope flash; misses a plain hit.
- **Knockout, 0.3 s:** a tail kick launches the target out through the ropes. The ropes snap, the ring drops, the world
  comes back to full colour on the same frame.
- **Landing, 0.4 s:** a dust ring and small knock-up where the target lands.

**B, airborne (closest to Ne Zha):** the kangaroo launches the target with an uppercut and the combo happens in the
air (its hop), slamming down at the end. The ring only appears as the landing ring. Less arena.

**C, no screen change:** A without the dimmed world: only the small ring and a shimmer on both to say "untouchable".
Lighter on screen, less of a "we left the fight" moment.

**What it needs from the kit (the kangaroo 3D lane drafts it, game feel installs it):** dash to target, both
untargetable for the bout, the beat window and crit on press, the four punches and the launch kick. Its own draft of
a 3 m roped ring around the pair, ending in a tail kick that launches the target out, is already close to A. The ring
effect from slice 1 carries over (`radius_m` and the post count change); the dimmed world is a new screen-space layer.

**Cue contract agreed with the kangaroo 3D lane (if Preston picks A):** "ring_cast" stays as the cast start;
"bout_start" (ring_centre, ring_radius = 3.0, ring_target set first); "bout_beat" per punch (kit.bout_beat 1-based,
kit.last_crit set first); "bout_launch" on the kick's hit; "bout_end" when the ring drops; ring_on true from
bout_start to bout_end; kit.bout_next_beat = seconds to the next beat window, one clock for the beat read and the
input. Dash 8 m, 4 punches on a 0.6 to 0.8 s beat. "Nobody outside can touch the pair" is game feel's (can_be_hit()).
Slots 1 to 3 (round 13) are live now with "tail_slam", "leap_cover" and per-hit "guard_block".

**Title bout look test (Preston picked A, 2026-11-11).** Added to `kangaroo_ring_fx.gd`: the bout cues, a 3 m ring
with 6 posts, ropes that swell into each beat window (`beat`), crits light a rope and fire a small burst
(`shaders/kangaroo_crit_burst.gdshader`), the ropes snap on the launch, and a full-screen dim pass
(`shaders/kangaroo_bout_dim.gdshader`). Recorded with a stand-in kit emitting the agreed cues
(`D:/dev/_scratch/kangaroo-fx/rec/kangaroo-title-bout-look-test.mp4`, recorder `kangaroo_bout_look.gd`); all cues
fired (3 crits, launch, snap, end).
- First take blacked out the whole screen. Two causes: the project runs `gl_compatibility`, so OpenGL depth needed
  remapping (`d * 2 - 1`) before rebuilding the world position, and `blend_mul` drew black in that renderer. Fixed by
  remapping and switching to a plain alpha veil (dark teal, 50% outside the ropes, none inside).
- Checked by eye: inside the ring the floor and both machines stay at full colour; outside is about half as bright and
  cooler; the veil comes in over 0.3 s and goes in 0.2 s on the launch.
- Not yet checked: on-beat versus off-beat reads side by side at full size; the crit burst size at the game camera.

**On the real draft kit (kangaroo 3D lane round 14, 2026-11-11).** Recorded with that lane's
`game-export-r9/kangaroo_kit_3d.gd` swapped in as Kit, a red rhino 6 m up the lane, beats 1, 2 and 4 pressed inside
the crit window (`D:/dev/_scratch/kangaroo-fx/rec/kangaroo-title-bout-real-kit.mp4`, recorder `kangaroo_bout_real.gd`).
Cues in order: ring_cast, hop, hop_land, glove_tap, bout_start, 4 x bout_beat, tail_brace, tail_hit, bout_launch,
tail_slam, tail_land, bout_end. The effect counted 3 crits, the kit 3; its placeholder ring and puff were hidden; ring
held 3.4 s from bout_start to the snap. The beat swell now uses the kit's own `bout_window` (0.25 s) and stays off when
`bout_next_beat` is -1. Note: the lane's check spot (0, 0, 12) is behind a wall from the game camera; film from the spawn.

## Next

**Kit rework under way (kangaroo 3D lane, 2026-11-11, not installed yet).** Slot 4 may become a small 3 m roped ring
around the pair (after Ne Zha's ult: one target isolated and finished, ending in a tail kick that launches it out);
the 5 m hold-in ring built here is the fallback. `ring_centre`, `ring_radius`, `ring_on` and `ring_target` keep their
names either way, so this observer should still fire; the posts, ropes and wall height would need resizing for 3 m.
Hold ring polish until Preston picks. New cues in the draft: `tail_slam` (slot 2 slam into a wall or machine,
`kit.last_slam`), `leap_cover` (slot 1 lands beside an ally), `guard_block` per blocked hit, and `counter_hit` hitting
all around within 3 m. Slot 1 becomes a leap of up to 10 m (`kit.leap_target`, `kit.last_leap`). The attach line goes
to game feel with the kangaroo lane's next kit handoff.

1. Hook it into the live game: one line where the kit's effects are made, `load(".../kangaroo_ring_fx.gd").attach(kit)`.
   That is the game feel lane's or the kangaroo 3D lane's call (kit or `kangaroo_fx.gd`); asked, not done here.
2. Preston's look at the ring: posts and ropes (A) versus the plain segmented wall (B) versus floor ring and tether (C);
   rope brightness at full rhythm.
3. Ringed enemy mark and a stronger wall-contact ripple.
4. Finisher kick impact, then the tail kick (slot 2), which shares it.
5. Basic chain fist arcs rebuilt smooth, then hop and jab, then guard.
6. Sound is not this lane's; the cast beam, rope pulse and wall contact are the moments a sound lane would want.

## Afterimages, the boxer and speedster trail (2026-11-12)

Preston: "multiple faded red copies bobbing delayed trailing the fighters movements. Or sometimes for flash when hes
moving fast". From general knowledge, not a study pass: boxing anime and speedster shows leave see-through copies of
the whole body a beat behind each fast move, a handful at a time, each fading quickly.

Built: `scripts/moba3d/kangaroo_ghost_fx.gd` plus `shaders/kangaroo_ghost.gdshader`, made by KangarooRingFX, so the
kit needs no extra hookup. While the kit's `current` is Bout, HopJab or TailKick, or the ring is up, it bakes the
body's current pose every 0.06 s, and each copy fades over 0.3 s, so about five copies trail at once. Each copy also
slides 0.9 m back from the facing direction, so punches thrown in place still trail. The copies are a see-through fill
with a brighter edge, using blend_mix. Additive light only drew thin wisps on the bright floor (take 1).

Colour: one setting, `tint`. Two takes were recorded (mint, and red). Red breaks the look lane's rule (red marks
enemies) and blends into the kangaroo's red-orange body. Preston picks.

Not done: the copies read a little smoky where they overlap. Fewer, crisper copies (every 0.1 s) are worth trying once
the colour is picked. Leap and bout were recorded; tail kick was not.

### Take 3: bob and weave (2026-11-12)

Preston picked mint, then said plain jabs with copies "doesnt look right": the afterimages should emphasise that it
is "bobbing and weaving agile". In kangaroo_ghost_fx.gd, during the bout, the inner model (visual only) slips to
alternate sides between punches (0.55 m), ducks on the way (0.22 m) and leans into the slip. A copy only drops when
the body has moved 0.04 m, so a still jab leaves none. Copies are skipped when headless, and when a mesh's skin isn't
registered (this fixed 382 match_check errors).
Next, with kit design: Preston wants it to weave around a target that can't attack back, as in Ne Zha's combo. That is
a kit change; it was sent to the kit design session.

## Kinetic discharge, first slice (2026-11-12)
Preston sent kit design's kinetic power to effects ("approve send to effects"; the bout finisher too: "Yes, same blast").
Built as effects on the clips that already exist: `scripts/moba3d/kangaroo_kinetic_fx.gd` and
`shaders/kangaroo_kinetic.gdshader`, made by kangaroo_ring_fx.gd like the afterimages.
- Charge: a ring closing in on each glove, faster and brighter with kit.rhythm / rhythm_max; both gloves pop on rhythm_full.
- Release: a pressure ring bursting from the leading glove along the punch on jab_hit, hook_hit, hopjab_hit, counter_hit,
  bout_beat (x1.35 on a crit), with a white pin of light for 0.07 s. The legs release on tail_hit (both kicks) and hop
  (a flat ring on the ground). Guard is untouched (kit design: absorb-and-release is the rhino's).
- Recorded in the match (`D:/dev/_scratch/kangaroo-fx/rec/kangaroo-kinetic-discharge.mp4`): 17 releases for 17 hit,
  kick and hop cues. The release ring reads at the game camera, nearer white than mint where it overlaps the bright
  hit flash. The charge ring is small at this distance and hard to pick out: next pass, make it larger or add a glove glow.
- Take 2 (Preston: "Yes, bigger charge"): the glove charge is twice the size (1.0 m) with a stack meter, one arc per
  rhythm stack (kit.rhythm_max arcs), and a white pulse in the glove at full charge. Reads at the match camera.
- Tail kick blast (Preston: "do the tail kick blast next"): on tail_brace a ring closes in on each foot (0.32 s); on
  tail_hit three pressure rings fire forward in a widening cone (0.25/0.65/1.1 m ahead, 1.0/1.5/2.0 m wide, 35 ms
  apart) and travel on at 3 m/s easing out, plus a 2.2 m ground ring and a white pin at the feet. Rings travel with
  depth, not a flat sliding sheet (the 2026-11-12 rejection). Same blast for the slot 2 kick and the bout finisher.
- Hop jab leg blast (Preston 2026-11-13: "Hop jab leg blast"): no cue comes before the hop, so the feet charge from the
  moment kit.current turns to HopJab (0.16 s, the clip's wind-up to its hop event). On "hop" three rings fire back and
  down from the feet (tilt 0.6, 0.8/1.1/1.4 m, 30 ms apart, 2.5 m/s) like thrust, with a 1.8 m ground ring and a white
  pin. The bout's opening hop gets the release without the charge (its move is "Bout"). Recorded: reads at the match
  camera; the back rings are thinner than the kick's and partly behind the afterimages.

## Gemini concept sheet for the tail kick (received 2026-11-17)
Preston approved sending a Gemini 8-frame sheet (concept and timing only, not a texture, never copied in):
side-session-notes/local_b046f4d1-.../gemini-kangaroo-tail-kick-effect-sheet-2026-11-17.jpg.
Compared with what is built in Godot (`kangaroo_kinetic_fx.gd`):
- F1 compression rings round the legs: built (leg charge on tail_brace).
- F2 sharp forward cone of force: built as three widening rings; the sheet's version is a single solid cone with a
  hard point and dust blown back. Worth taking for the port.
- F3 curved crescent pressure wave with volume: not built. Fits the kick's hit frame.
- F4-F5 launch streak with spiral rings (bout_launch): not built. Skip the flat F4 line; F5's spiral rings fit.
- F6 wall slam with cracks and a stun ring (tail_slam): not built.
- Lightning crackle in F0, F1 and F6: leave out; kinetic must not read as electric.
Since the 2026-11-15 move to Unreal, these go to the Unreal port rather than more Godot work, unless Preston says otherwise.

## Paragon effects bar, for the next review (received 2026-11-18)
Hub, sent at Preston's ask: `D:/dev/_scratch/hub/paragon-fx-bar-2026-11-18.md` (private reference, never copied).
Median 5 layers per effect; a three-beat impact (flash gone by about 0.6 s, falling debris, smoke to about 1.5 s);
only 14% additive. Against that, the kangaroo's kinetic effects are 2 to 3 layers (ring, pin, sometimes a ground
ring), all additive, and end by 0.32 s with no debris or smoke beat. In Arena3v3, additive over the pale floor
already films cream ([[arena-effects-wash-pale]]). Next review: add a debris beat and a short dust or smoke beat to
the kick and wall slam, and move the rings to translucent. Not sent to the Unreal lane mid-row (hub: no plan
changes mid-run).
