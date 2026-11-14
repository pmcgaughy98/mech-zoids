# Rhino pixel-art effects: synthesis (2026-11-11)

Preston, relayed by the rhino 3D lane: "for tremor and abilities we can use pixel art as the effects. Its must look
legit and smite 2 level effects. Also idle effects too have moba grade look."

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Cabrakan 1vX clip (youtube NSL4xBviayQ, 1280x720 at 60 fps) | **Measured**: two ring bursts sampled at 15 fps (one cell = 0.067 s), 7.0 to 9.4 s and 29.6 to 32.0 s | Timing and layering of a ground ring burst, ally versus enemy colour, the stun read |
| SMITE 2, "How to Cabrakan in under 5 minutes" (fWK2hV8vrdw) | Watched around Tremors (1:56 to 2:14); the tooltip covers the ring, so only the numbers were usable | Tremors radius 4.8 m, the same size class as our 3.0 to 5.0 m release |
| Dead Cells | **General knowledge only.** The clip pulled (B8C-2udm_gM) was mostly menus, so nothing was measured | Pixel effects held on twos, a single white impact frame, chunky debris that lands and stays briefly |
| Hades, Eastward | General knowledge, not watched this pass | Hades: a bright leading rim with a soft trailing fill; Eastward: pixel dust puffs in a few hand-picked colours |
| Our own stand-in videos (rhino 3D lane) | Watched | The release fires at 0.20 s in `brace_release`; the old ring was the Codex `brace_ring` set |

Clips and frame sheets are in `D:/dev/_scratch/rhino-fx/ref/`. Nothing from them is in the project.

## Structure learned (measured unless marked)

1. **Impact frame first.** A white-hot core shows for 1 frame (0.067 s) before anything spreads. In SMITE the core
   is the only near-white thing on screen at that moment.
2. **Ring spreads fast, then slows.** The ring's leading edge reaches about 80% of full size by about 0.27 s
   (4 cells), then creeps the last 20% while fading. Ease-out, never linear.
3. **The leading edge is the brightest part.** The fill behind the edge is darker and fades first; the edge
   survives longest and breaks up last.
4. **Total life 0.5 to 0.6 s** for a burst ring. Anything that lingers (a slow patch, a scorch) is a separate,
   quieter layer.
5. **Debris and dust ride inside the ring**, thrown outward with drag, and are warmer and darker than the energy.
6. **Ally versus enemy.** The caster's own effects use the team colour (blue and teal for Cabrakan); enemies get a
   red ring or rim. SMITE paints an enemy's hit flash red on the caster's body. That matches the look lane's rule:
   red is the enemy marker, never the rhino's own colour.
7. **The stun reads on the victim, not the ring:** stars or a swirl over the head, plus "STUNNED" text, for the
   stun's whole length. The ring itself only says how big and how strong it was.
8. **Screen coverage.** A full-size SMITE ground ring takes about 50 to 70% of the screen width at the default
   camera. Our 5 m release covers 73% of the width at the game camera (measured in Godot); the 3 m one covers 44%.

## Synthesis proposal (nothing here is canon)

**Look:** pixel art at about 19 to 32 art pixels per metre (a 192 px sheet stretched to the ring's size), nearest
filter, a dark selective outline, 6 tones per ramp. Rhino colours: a **mint energy ramp**
(#0c3a3a, #167a6c, #2fc79a, #7ef5c4, #d6fff0, #ffffff), matching the drum ring's piston glow, and an **ochre dust
ramp** (#3a2a14 to #f2dca0), matching its gold armour. Near-white pixels are pushed to about 1.7 in the shader so
only the core and the leading edge bloom under the arena grade (threshold 1.05); everything else stays under 1.

**Brace and release (built, slice 1):** 9 frames at 15 fps (0.6 s). Frame 1 is the flash; frames 2 to 5 spread
the ring with cracks and dust; frames 6 to 8 break up. At 5 charge a second sheet adds five piston notches on the
ring (one per charge point) and a gold inner ring: a "full" read. The stun itself is read on the victims (the
existing stars over the minions).

Alternatives named:
- **A (built):** the size comes from scaling one drawing. Cheap, but pixel density drops at 5 m.
- **B:** draw three sizes (3, 4 and 5 m) at a fixed pixel density. Sharper at 5 m; three times the art.
- **C:** charge levels 1 to 4 also show their notch count (1 to 4 notches), not only at 5. Better read of the gauge;
  needs four more sheets or a notch layer drawn separately.

**Effect list for later slices** (times from `rhino_game_v50.events.json`):

| Effect | Proposal |
| --- | --- |
| Idle | Drum ring breathes (2 breaths per 6 s) through `mech_look.set_glow`; a 4-frame mint vent puff at each piston on the exhale; at 3+ charge, tiny sparks crawl on the drum |
| Basic chain | Horn sparks at hook 0.20 (to its left), rip 0.333 (up and right), gore 0.533 (straight up, biggest); a stamp puff at 0.267, dust at 0.80 |
| Horn toss | Dash streak from 0.133, a catch flash at 0.40, a release puff at 0.533 |
| Ground pound | Slam at 0.40: 4.0 m ring with cracks, using the release's structure in ochre; stomp rings at 0.80, 1.20, 1.60, 2.00 under alternating front feet; a slow patch decal that lingers in dark ochre |
| Brace | Sparks where hits land on the plating; one mint notch lights on the drum per charge |
| Tremor charge | Paw scrapes at 0.133 and 0.333; a 2.2 m ring plus dust each stride; a finale ring from 3.4 to 4.6 m |
| Stun loop, death | A dazed read over the head; a dust thud at 1.0 |

## First slice (superseded the same day): the pixel ring

Preston rejected the pixel look after seeing it; the files below were removed and the smooth version replaced it.
The PixelLab effects stay in his "My effects" for reference.


- Art: `art/fx/rhino/pixel/brace_release.png` and `brace_release_full.png` (3x3 sheets of 192 px), drawn in
  PixelLab's free `vfx_workbench` (no paid generation). Saved in Preston's PixelLab "My effects" as
  "Rhino brace release" and "Rhino brace release full charge", so the sliders can be tweaked there.
- Code: `scripts/moba3d/rhino_pixel_fx.gd` listens to RhinoKit's existing `cue` signal ("brace_release"). It reads
  the charge from the frame before (the release zeroes it before the cue) and sizes the ring to
  `release_radius + release_radius_per * charge`. It hides the Fx3D stand-in ring the kit still spawns.
  Shader: `shaders/rhino_pixel_flipbook.gdshader`. Installed by `rhino_art_installer.gd`
  (the Rhino Art Arena launcher). No kit code, signals or numbers were changed.
- Check (in the recording script `D:/dev/_scratch/rhino-fx/rec/rhino_brace_release_pixel_fx.gd`): 5 hits give
  charge 5 and a 5.0 m full ring; a brace with no hits gives a 3.0 m plain ring; one stand-in ring hidden each time.

## Second pass: Cabrakan's Tremors, the ground and the always-on look (2026-11-11)

Preston, after the pixel ring: "we don't want it too look like pixel art thats the issue. Look at the cabrakans
tremor effect. What the ground is doing during it, also what the model looks like the idle effects and effects that
are always going even when its walking."

Source: SMITE 2 in-game demo (youtube 8Tfl1TgQ7sY, 0:50 to 2:50, 1920x1080 at 60 fps), **measured** at 15 fps
(one cell = 0.067 s) from 39.0 s. Sheets in `D:/dev/_scratch/rhino-fx/ref/` (`az_slam15.png`, `az_crack_full.png`).

**Why the pixel ring reads wrong:** SMITE's effects are smooth, soft-edged and layered, with a white-hot core and
colour that falls off in gradients. None of it is on a pixel grid. The pixel ring's hard steps and dark outline read
as a 2D sticker lying on a 3D floor.

**One slam, cell by cell:**
1. **Anticipation, 3 cells (0.2 s):** the shields lift. No effect yet; the body sells it.
2. **Impact, 1 cell:** a white-to-amber radial burst covering about half the screen, white speed streaks shooting
   outward, rock chunks thrown up. In the same cell a **teal shell edge** appears at full radius: a bright rim with
   a soft gradient falling inward, like the front of a dome, not a thin line.
3. **The ground breaks, from the impact cell on:** a network of **glowing cracks drawn into the floor**,
   white-hot at the centre and amber outward, wide near the impact and thinning to hairlines at the edge. The
   burst's glow lights the floor around them.
4. **Repeats:** Tremors slams again about every 4 to 5 cells (0.27 to 0.33 s). Each slam repeats the burst and
   re-lights the cracks.
5. **Finale (another ability's detonation, magenta):** one bigger flash dome, then the floor is left with **dark,
   black fissures** whose centres still glow, scattered rock chunks resting on the floor, and white motes drifting
   up. That aftermath lingers about 0.5 to 1 s and fades.

So the ground has three states: **hot cracks** while it is being hit, **cooled dark fissures** after, and
**debris** lying on top. That sense of the ground being damaged is what the pixel ring lacked.

**Always on, idle and walking:**
- A **translucent glowing disc under him**, about his own width, with etched rune lines (his passive aura). It
  stays on while walking and is the steadiest "this character is powerful" read.
- **Emissive lines on the body and shields** (teal circuit lines) and a **glowing gem** on each shield, lit all the
  time and brighter during abilities.
- The aim indicator while choosing a target: a teal arc on the ground at the ability's range.
- Not verified: whether the disc turns or pulses (the camera moves too much to tell from these frames).

**What this means for the rhino (proposal, nothing here is canon):**
- **Style:** smooth shader effects, not pixel flipbooks: HDR gradients, soft falloff, additive cores. Pixel art
  stays out of the ground and impact layers.
- **Brace release, redone in that structure:** the 0.2 s lift is already in the clip; at the release event, a
  1-frame white-hot core and speed streaks; a mint shell edge at full radius with a gradient inward; a glowing crack
  decal in the floor that cools from white and amber to dark fissures over about 1 s; 6 to 10 small rock chunks
  (simple 3D meshes) thrown and landing; motes rising.
- **Always on:** a faint mint ground disc under the rhino (its Seismic aura), brighter per charge point; the drum
  ring and piston lines emissive (already wired through `mech_look.set_glow`); during Brace, the disc tightens and
  the five notches light one per charge.
- **Reuse:** the same crack decal and debris serve the ground pound, the tremor stomps and the stampede finale.

## Brace release, rebuilt smooth (built 2026-11-11)

- `scripts/moba3d/rhino_release_fx.gd`, installed by `rhino_art_installer.gd`; listens to the kit's
  "brace_release" cue, no kit edits. Shaders: `shaders/rhino_release_ground.gdshader` (flash, streaks, mint edge,
  crack web, warm floor wash in one quad) and `shaders/rhino_release_shell.gdshader` (the dome wall on the edge).
- Timeline: impact frame white core, amber bloom and streaks; an omni light at 5 (8 at full charge) fading over
  0.35 s lights the rhino and floor; the mint edge reaches the release radius in 0.1 s with a wall up to 0.9 m
  (1.26 m at full charge), gone by 0.45 to 0.55 s; cracks glow amber with a white seam near the centre, cool by
  about 1.2 to 1.5 s, and linger as dark fissures with a pale dust lip until about 2 to 2.5 s; 8 faceted rocks
  (14 at full charge) glow briefly, bounce once and lie there, then sink at 2.0 to 2.6 s; 26 to 42 mint sparks rise.
- Cracks are Voronoi borders in stretched polar space (radius in metres by angle), so they run outward from the
  impact; an earlier take in plain space read as floor tiles. The dust lip exists because black fissures vanished
  on the arena's dark blue floor.
- Checked in the match recording: radius 5.0 m at 5 charge and 3.0 m at 0; the stand-in ring hidden each time.
- Not done: the hot cracks do not yet light the rhino from below; no sound; the full-charge read is only "bigger
  and hotter" (the five-notch idea is not in the smooth version yet).

## Brace hold, smooth (2026-11-11)

Preston saw "pixel art smoke underneath" the smooth release. A probe of every effect node near the rhino found it:
the kit's Fx3D `brace_ring` (Codex pixel art, 6 frames cycling, 2.36 m), parented to the player while braced.
`rhino_release_fx.gd` now hides it every frame and draws `shaders/rhino_brace_hold.gdshader` instead: a soft mint disc
(rim at about 2.4 m across) that fades in when planted, breathes, and lights one of five rim notches per Seismic charge,
flashing on each new charge. Still pixel-looking near the rhino and not in this lane: the arena's blue team ring under
every unit (the Player's "Ring" node in the arena scene), the Fx3D `deflect_spark` on blocked hits, and the
`stun_loop` stars over stunned enemies.

## The pixel puff during the brace (2026-11-11, later)

The "steam puff" near the start was the kit's pixel `deflect_spark` (white chevrons at chest height on each blocked
hit while braced). The look lane has since made `hit_spark`, `deflect_spark` and `stun_loop` smooth for every mech
inside `fx3d.gd` (`scripts/moba3d/look_fx.gd`), so the rhino lane adds nothing for it; a rhino-only swap was tried and
removed so the two would not overlap. Checked in the re-recorded clip (3.65 to 3.85 s): a white-hot core with cyan
rays and a thin ring, no pixel shapes. Note: a new `class_name` file needs `--headless --import` before headless
runs, or every script that uses it fails to compile (the recorder now does this).

## Preston's notes on the smooth release (2026-11-11)

"This is the right direction", but unsure about "the shining light thing" and "the light balls". Changes: drifting
motes removed; impact core halved in size and strength (x5 to x2), amber bloom about half, rays x3 to x1.6, the
point light 5+3p to 1.5+1p and gone by 0.2 s instead of 0.35 s. The rhino stays readable on the impact frame now.
Coverage unchanged (5 m = 73% of width, 3 m = 44%). He also said the tremor "would need some more love" and that sound
will help; the tremor is the next slice here, sound is not this lane's.

## Tremor, smooth (slice 2, 2026-11-11)

Built in `scripts/moba3d/rhino_release_fx.gd` (observer only; no kit edits) with `shaders/rhino_dust.gdshader` and new
uniforms on the ground shader (flash_mul, streak_mul, crack_mul, hold, reheat; defaults keep the brace release).
Structure from Cabrakan's Tremors: the slam opens one crack web that lasts as long as the slow (2.4 s); each of the
4 stomps re-heats the same cracks and sends a mint edge out over the 4 m circle; dust rises where the kit's puffs were.
Tremor charge: each pulse is a small crack burst (2.2 m) that fades while it cools; the finale slam is the full web.
Hidden near the rhino while the tremor or run plays: gp_ring, impact_puff and dust_trail sprites, the flat yellow
KitFeel ground wave, and the cracks.png/slow_disc.png decals. Recorded: slam, 4 stomps, 5 pulses, finale all fired.
First take: cooled pulse cracks read as black scribbles; fixed by fading them while they cool (hold -0.6).
Not done: paw scrapes in the run wind-up (need clip events); the slow area has no edge of its own once the
cracks fade (the slow_disc decal used to show it). The additive shaders now also carry fog_disabled (look lane tip).

## Paw scrapes (2026-11-11)

The run wind-up clip fires `paw_1` and `paw_2` on the model's `event` signal (0.2 s apart); `rhino_release_fx.gd` listens
to the body directly, no kit edits. Each scrape: three claw furrows dragged backward in 0.12 s (`shaders/rhino_scrape.gdshader`,
soft brown with a dust lip, gone by 1.6 s), two low dust kicks thrown back and out, three small pebbles, nothing glowing.
First take: the dust sat over the front legs and the near-black furrows read as sticks; dust made lower, smaller and
fainter, furrows wider, shorter and brown. Still true: the recording camera faces the rhino, so the furrows run away
from the lens and show as short dark lines under him; from behind (the usual play view) they sit under the body.

## Always-on Seismic disc (2026-11-11)

Outside the brace, the brace disc now stays faintly under the rhino while he carries Seismic charge (fade 0.22 +
0.06 per charge, off at 0), with one rim notch lit per charge and a flash when one is gained. It follows him while
walking and fades in or out over 0.25 s. Recorded walking at charge 0, 1, 3, 5, 0: at 1 it is barely there, at 3 and 5
it reads as a mint glow around the team ring. The match now gets these effects from `rhino_fx_installer.gd` (rhino 3D
lane, after Preston said "add rhino effects work its good"); the test scripts reuse that copy instead of adding a second.

## Tremor slow-zone rim (2026-11-12)

After the cracks cool, nothing showed where the slow ends (the old slow_disc decal did). The tremor's ground quad now
holds a thin mint rim at the 4 m radius plus a faint fill just inside it, for the slow's 2.4 s, fading over the last
0.4 s (`zone_life` uniform; off by default, so the brace release is unchanged). Recorded and checked: the rim stays
through all four stomps and is gone with the slow. Still left: paw scrapes seen from behind, horn sparks.

## Horn chain slashes (2026-11-12)

What it is: each hit of the basic chain (hook, rip, gore) draws a short crescent slash, `shaders/rhino_swipe.gdshader`,
spawned from the model's `event(clip, "hit")` in `rhino_release_fx.gd` (`_horn_event`, `_swipe`, `_update_swipes`).
Structure from MOBA melee basics: a bright head races across the arc in about 0.07 s, white at the head and mint toward
the tail, then the arc thins and is gone by 0.22 s, before the next swing.

- Hook: flat sweep from the rhino's right across the front to its left (size 3.3).
- Rip: rising from low left to high right (size 3.3, a little brighter).
- Gore: rising straight up, biggest and brightest (size 3.6, strength 1.6). Its quad faces sideways (x = up, y = right)
  so the arc is seen face-on from the play camera; laid in the forward plane it was edge-on and vanished.
- The gore's `land` event stamps two small dust puffs either side of the horn.
- Drawn over the body (`depth_test_disabled`): the play camera sits behind the rhino, so a depth-tested slash in front of
  him was hidden by his own back. Additive, fog_disabled, no red.

Approved by Preston 2026-11-12: drawing over the body reads right.
Video: `D:/dev/_scratch/rhino-fx/rec/rhino-horn-chain.mp4`.

## Paw scrapes from the play camera (2026-11-12)

Checked from the match camera behind the rhino: the first version barely showed, because the furrows and dust started at
the front paws and sat under his belly. Now the furrows are 2.1 m long and run out past the hind feet, and the pebbles and
dust are thrown from behind the hind legs, higher, so they arc up into view. Video: `D:/dev/_scratch/rhino-fx/rec/rhino-paw-scrapes-from-behind.mp4` (wind-up at about 8.3 to 9.5 s).
Approved by Preston 2026-11-12.

## Horn Toss (2026-11-12, retired the same day: slot 1 is now Heave, below)

The kit's Fx3D pixel puffs and hit spark are now hidden while Horn Toss plays (the stand-in swap runs for it too), and the
observer draws its own on the kit's cues (`_toss_cue` in `rhino_release_fx.gd`):
- `dash_cast`: two dust clouds shoved back off the hind feet as the dash starts.
- `horn_catch` (toss only, not the stampede's catch): a rising mint slash, the gore's shape at size 3.0.
- `toss_land`: a small cracked-ground burst (r 1.4, the tremor shader with the pulse's settings) plus two dust puffs, at
  `kit.toss_land_behind` (3 m) behind the rhino.

Found in the match recording: from the default camera the landing spot sits under the ability bar, so only the burst's
edge shows. That is camera and HUD layout, not the effect. Videos: `D:/dev/_scratch/rhino-fx/rec/rhino-horn-toss-before.mp4`
and `rhino-horn-toss-after.mp4` (catch at about 1.5 s; the second toss is a miss).

## Heave (2026-11-12, replaces Horn Toss)
Preston picked Heave for slot 1 ("Heave", 2026-11-12; spec in `docs/plan/kit-design-2026-11-11.md`, "Rhino rework
draft"). The Horn Toss effects above are **retired** and removed from `rhino_release_fx.gd`; the old version is kept at
`D:/dev/_scratch/rhino-fx/rhino_release_fx.before_heave.gd`. Horn Toss was never approved.

The kit has no Heave yet, so the effects run on proposed cues, sent to the kit design lane for game feel:
- `heave_tell`: a mint glow on the horn that hums, with rings swelling out like a struck tuning fork (`shaders/rhino_ring.gdshader`).
- `heave_thump`: dust off both shoulders, a small crack burst in front, then a ridge of rock slabs punching up in pairs and running ahead at 12 m/s to the target or the reach. Built from slabs with height, not a flat strip (flat travelling effects were rejected 2026-11-12).
- `heave_lift`: a ring of seven tall slabs bursts up and leans out under the target, with cracked ground, rocks and dust.
- `heave_land`: a cracked-ground burst with dust where the target lands, behind the rhino.
- Optional kit vars read: `heave_target`, `heave_reach` (default 5.0), `heave_tell_time` (default 0.4), `heave_land`.

Status: **approved** (Preston, 2026-11-12: "Looks right"), on cues fired by hand; recheck once game feel builds Heave and the rhino lane adds its clip. Recorder: `D:/dev/_scratch/rhino-fx/rec/record_heave.sh` (cues fired by hand, no Heave clip yet).
- Play camera check (2026-11-12): the first take's ripple and heave were hidden behind the rhino's body (the target is straight ahead of a camera that sits behind). The heave slabs are now 1.5 to 2.0 m and splay outward so they crown over his back, the ripple slabs sit 0.35 to 0.6 m off the line so they show past both flanks, and the heave dust is thrown higher. The horn glow and rings read from behind. Video: `D:/dev/_scratch/rhino-fx/rec/rhino-heave.mp4`.
