# Cobra ability effects: synthesis (2026-11-13)

Cobra effects lane, on the method the rhino, gorilla, hippo, kangaroo, pangolin and bison lanes used (their synthesis
docs in this folder; read for this lane: `bison-fx-synthesis-2026-11-13.md` and `hippo-fx-synthesis-2026-11-11.md`).
Bar (Preston, held across every lane): smooth, layered, HDR, SMITE 2 grade, never pixel art. Impact flashes small and
short, no drifting glowing motes, no point light washing the mech out, no red on the player's own mech, and anything
that travels has a shape with height.

**Current state (2026-11-14): read "Phase pass" below first.** The teal slice described from "Synthesis proposal" to
"Recorded and frame-checked" is the first pass. Its structure and timing still hold, but its colour and its stun read
were replaced. Breach (slot 4) is built too: see "Breach" below.

## Where the cobra stands (read first)
- **Kit code: none.** No `cobra_kit.gd`. Bots and the player use `arena_base_kit.gd` with the cobra's body. The kit is
  the approved Medusa entry in `docs/plan/moba-kits.md` ("Fighters and assassin", "Cobra (`cobra_m`), ode to
  Medusa", line 409; the brief's 362 to 387 is the pangolin and wolf):
  passive Wall Line, 1 Ghost Run, 2 Hood Gaze, 3 Seam, 4 Breach. Every name and number is a placeholder except Seam's
  2 s inside the wall (Preston, 2026-11-13: "Seam stays inside the wall 2 seconds").
- **Body:** `art/arena_models/cobra.glb`, the r2 export (sha256 21b20d38..., checked), 14 clips (15 at runtime), +Z
  forward, metres. Installed by the game feel lane as `authored_trial`; on BOT_ROSTER red (Preston: "Keep the cobra on
  red"). `art/arena_models/cobra.events.json` already carries `inside_s` (identical to the 3D lane's r2 copy).
- **Hood Gaze clip** (0.95 s): gather 0.12 (hood flares), gaze 0.30 (cone fires), release 0.62 (hold ends). Snout at
  gaze (0.079, 1.575, 1.261) in model space (`D:/dev/_scratch/cobra-3d/out/check_r2.log`).
- **Sockets found for this lane** (from the base texture, not guessed): the hood projectors are the two cyan panels on
  the inner hood plates. Cyan vertices by bone: Bone_016 (left plate) centroid (0.322, 1.189, 1.007), Bone_018 (right
  plate) (-0.236, 1.178, 1.014), each a strip 1.0 to 1.4 m up; the neck core is the cyan strip on Bone_004 (0.057,
  0.949, 1.207). The model has no emissive texture: the cyan is painted, so the effects draw the light.

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Medusa, "SMITE 2 MEDUSA GUIDE \| How to play - Where to play - What to build" (Daxonn, youtube E-JaXeYDuc0, 1280x720 at 29.97 fps) | Confirmed SMITE 2: the title and the in-game ability card for Petrify on screen from 136 s. Section 2:05 to 2:50 downloaded. Scan at 1 fps (`ref/dax_scan1fps.jpg`), then **measured** at 15 fps, cell by cell: casts at 137.4 s (`ref/pet15_a.jpg`), 146.9 s (`pet15_c.jpg`), 156.8 s (`pet15_e.jpg`, zoomed `pet15_e_zoom.jpg`) | Petrify's order and timing, below |
| SMITE 2, Medusa, Shenmoki "SMITE 2 Medusa Guide (OB7)" (youtube SFQAaNswwnY) | Captions only (the video download was cut off by a usage stop and not retried) | Text: Petrify charges a cone in front, then fires; it does not go through walls; enemies facing her are stunned |
| Bacchus, Belch of the Gods | **Not re-measured**: the hippo lane's measurement (their synthesis) | A cone is on the floor at full size within a cell; fill, rims, far arc; clean exit |
| Our clip, events, snout log, base texture, look notes | Read and measured | Event times, socket positions, the cyan projector panels |

Scratch: `D:/dev/_scratch/cobra-fx/ref/` (the clip, both caption files, every sheet). Nothing from either video is in
the project. Structure only, never a copy.

## Structure learned from Petrify (measured)
Three casts, the same order every time. Cast cell = the cell the caster changes.
1. **Cell 0, the tell:** the caster's whole body flushes gold and stays lit for the whole charge. Before it, the game
   shows an aim cone on the floor (targeting UI, not ours).
2. **Cells 2 to 5 (0.13 to 0.33 s):** thin pale needles start out from her chest and head, short, many directions.
3. **Cells 5 to 12 (0.33 to 0.8 s):** a wide translucent veil spreads forward and to the sides, green haze with thin
   pale streaks in it, widest at cells 8 to 10, then thinning. It has height, not only a floor mark.
4. **Cell 15 or 16 (1.0 to 1.07 s; 16, 15 and 15 cells on the three casts):** the blast. A white core with a radial
   flare round her head, and in the same cell a burst on each target at range. No projectile, no travel time.
5. **Cells 16 to 19:** the head flare decays in 3 to 4 cells (about 0.25 s); the body's gold goes out with it.
6. The aim cone and the veil are wider than the gaze reaches; the victims carry the hit read.

## Synthesis proposal (nothing here is canon)
**Our clip is shorter than Petrify:** gather to gaze is 0.18 s, not 1.0 s, and the cone holds from gaze to release.
So the order is kept and compressed: the tell and the needles go in the 0.18 s charge; the blast and the hit at range
land on `gaze`; the veil becomes the held cone; Belch's clean exit ends it.

**Look: soft light from the hood's own projectors.** The cobra's power makes solid matter go soft; its hood plates
carry cyan projector panels. Everything comes out of those panels.

**Colour, two built side by side (Preston picks):**
- **A, teal (default):** the cobra's own panel cyan (warm 0.10 0.82 0.74) with white-teal cores (hot 0.86 1.0 0.97).
  Body and effect read as one machine. Risk: next to the kangaroo's mint at a glance, and in the blue team's family.
- **B, stone:** a cold pale grey-white (warm 0.66 0.74 0.72, hot 1.0 1.0 0.98): Medusa's stone, without her green.
  Reads as a ghostly light on the blue floor. Risk: pale on bright floors, close to plain white.
- Kept out: red (enemies), lime (gorilla), amber (rhino), purple (hippo), copper (pangolin), magma (bison), mint
  (kangaroo), and Petrify's green and gold.

## The slice: Hood Gaze (built 2026-11-13, launcher only)
Files, all new: `scripts/moba3d/cobra_fx.gd` (the observer), `shaders/cobra_glow.gdshader`,
`cobra_gaze_floor.gdshader`, `cobra_gaze_wall.gdshader`, `cobra_gaze_ray.gdshader`, `cobra_gaze_mark.gdshader`.
Launcher: `scenes/moba3d/cobra_fx_arena.tscn` (the main match plus `scripts/moba3d/cobra_fx_standin.gd`, which takes
the player's machine, freezes its kit, puts the registered cobra body on it and adds a stub kit; keys: 2 Hood Gaze,
P switch palette). `arena_play.tscn` and every other lane's file are unchanged.

| Event (s into the clip) | What shows |
| --- | --- |
| gather 0.12 | The two projector strips and the neck core light up and build over 0.18 s; a soft ring lights round the hood's outline (from behind, the hood hides its own strips, so the ring is the charge's read at the chase camera); 8 thin primer needles flick 0.7 to 1.4 m out of the strips and go in 0.2 s |
| gaze 0.30 | A small glint at the hood, 0.14 s (a white core with a thin sideways line); the strips flare to 1.45 and settle; the floor wedge is there at once; the gaze front, a curved sheet 1.7 m tall, sweeps from the hood to the range in 0.1 s and flashes as it arrives; 5 tapered beams run from the strips to the front; in the same frame each stunned enemy gets a 0.12 s burst, a lock line from the hood (0.3 s) and a shell, each slowed enemy soft-ground ripples |
| gaze to release | Dashes run outward along the beams and the floor streaks; the front shimmers; the cone eases to 70% |
| release 0.62 | The cone, front and beams are gone in 0.08 s; the strips and ring cool over 0.3 s |
| after | Shells hold for the stun time (bands sliding down, fade in the last 0.25 s); ripples for the slow time |

**Placeholder numbers, for the kit to match later:** range 6 m from the cobra's origin, 70 degrees across, stun 1.2 s,
slow 2.0 s, the front 1.7 m tall, the wedge starting 0.9 m out (under the hood). Shell 0.62 m radius, 1.7 m tall
(placeholders for a target's size).

**Contract proposed to the game feel lane** (the bison's pattern; the effects never call the kit):
- Body events from `MechModel3D.event` on clip "Hood_Gaze": gather, gaze, release. They carry all the timing. If the
  action ends early (`action_finished` before release), the cone clears at once.
- `signal cue(name)`: `"gaze_hit"` right after the kit resolves the cone on the `gaze` event.
- Fields read on `gaze_hit`: `gaze_stunned: Array` (enemies in the cone facing the cobra), `gaze_slowed: Array` (the
  rest in the cone).
- Fields read on `gaze`, if present: `gaze_range` (m), `gaze_angle` (degrees, full width), `gaze_stun_time`,
  `gaze_slow_time` (s).
- The stub's guess at the rule, for the kit to replace: in range and angle of the cobra's facing; stunned if the
  enemy's facing points at the cobra within 90 degrees, slowed otherwise.
- Install line for whoever writes the kit: `var fx = load("res://scripts/moba3d/cobra_fx.gd").new();
  kit.add_child(fx); fx.setup(kit, machine)`.

## Recorded and frame-checked (2026-11-13)
- Video: `D:/dev/_scratch/cobra-fx/rec/cobra-hood-gaze.mp4` (20.2 s, 60 fps, also in the shared notes folder): a cast
  at full speed and one at quarter speed at the chase camera (distance 12, pitch 13, look height 3.2, fov 60, forced
  in the recorder, `per_machine` off), a close-up from the cobra's side at quarter speed, then the stone palette at
  full speed, chase and close. Proof board: `rec/cobra-hood-gaze-proofs.jpg` (rows: chase 0.20 / 0.33 / 0.45 /
  0.80 s; close 0.20 / 0.30 / 0.45 / 0.60 s; teal against stone).
- Recorder: `rec/record.sh <tag> [--shots]` (waits for any other Godot, `--check-only` on the three scripts, then
  `--write-movie`) with `rec/gaze_rec.gd`. Four red minions: two ahead facing the cobra, one ahead facing away, one
  outside the cone; every other unit hidden for the take.
- Logged on each of the four casts: gather, gaze and release fired 0.17 s and 0.33 s apart (60 fps rounding of 0.18
  and 0.32); `gaze_hit` in the same frame as gaze; 2 stunned and 1 slowed, as placed (the one outside the cone got
  nothing); the cone cleared 0.08 s after release.
- Seen in the frames: smooth shapes, no pixel look, no point light, no motes, nothing red on the cobra.
- Takes corrected on the way (4 takes):
  1. Every layer bloomed to white and seven beams piled into a white wedge at the hood; from behind, the charge was
     invisible (the strips face forward and the hood hides them). Beams cut to five, dimmer, fading in out of the
     strips; flash cut to 0.8 by 0.42 m at amount 1.0.
  2. The stun shells were the brightest thing on screen: softened. The gaze front was faint: raised.
  3. Added the soft ring just behind the hood: from the chase camera it spills round the hood's edge, so the charge
     reads at 0.2 s (Petrify's outline lighting up, in our colour). Then a faster rise and a softer ring.
- **Still falls short:**
  - From the side and front the ring reads as a round aura behind the head, not hood-shaped.
  - From straight behind, the cobra's body hides the middle of the wedge; the rims, the front and the aura carry it.
  - Shells and ripples are sized by placeholder, not by the target.
  - No sound.
- Seen in the log, not mine: `match_hud.gd:634` (`_enemies`, from `_paint`) throws "Cannot blit_rect in compressed
  image formats" twice at start, in every take.

## Phase pass (2026-11-14, current)
How it got here:
- **First pass:** teal. Preston: "different energy color and feel. It has energy that can petrify."
- **Petrify pass (2026-11-13):** the cone turned the floor and the enemies to grey stone with glowing cracks, in gold,
  jade and rose. Preston picked **gold**, then: "i didnt realize its powers were phase, so i guess may not need
  petrify."
- **Kit check:** `moba-kits.md` confirms him. The Power is "pass-through, making solid matter go soft", and Medusa's
  statues are under Left. Hood Gaze fires from the hood projectors, so the eye source tried in the petrify pass went
  back to the projector strips.
- The stone shader was deleted.

What the gaze does now (all gold: warm 0.92 0.84 0.18, hot 1.0 0.98 0.80; teal stays on P for comparison):
- **Charge:** unchanged from the first pass. The projector strips and neck core light up, primer needles flick out,
  and a halo sits round the hood for the chase camera.
- **Floor (`cobra_gaze_floor`):** the ground the cone crosses goes soft. Waves roll out from the hood; the floor
  behind them wavers (the scene is sampled shifted along the waves) and their crests catch the gold. A bright line
  marks the front, and the rims mark the edges.
- **Front (`cobra_gaze_wall`):** a soft membrane 1.7 m tall. The world seen through it wavers, and two sets of gold
  bands at near frequencies slide against each other and beat into slow swells.
- **Beams (`cobra_gaze_ray`):** three thin lines from the strips and the hood to the front, with grain running out
  along them. They are dimmer than the first pass.
- **Stunned (`cobra_phase_skin`):** the enemy is held out of phase.
  - It is drained into the gold, its surface wobbles and its picture wavers.
  - A rim and sliding bands run over it.
  - A see-through double drifts 0.13 m beside it, flickering.
  - When the stun ends it snaps back solid with one short flash (0.18 s).
  - A small burst and a lock line from the hood mark the hit, as before.
- **Slowed (`cobra_gaze_mark` and the skin to 0.42 m):** its feet are in soft ground. Rings run out round it, the
  floor under it wavers, and the phase shimmer covers it to the ankles.

How the enemy look is applied:
- The skin is worn by copies of the enemy's meshes (same mesh, skin and skeleton, added beside the original), owned
  and freed by the fx.
- The enemy's own materials and its `material_overlay` (team colour, hit flash, hex shield) are never touched.
- While stunned, the gold drains most of an enemy's red team tint; its red health bar stays. If the game feel lane
  wants the red kept, the drain is one number in the skin shader.

The screen-space warp (`hint_screen_texture`) is new to the effects lanes. It costs one screen copy per frame while
the cone or a mark is up.

Recorder: `D:/dev/_scratch/cobra-fx/rec/phase_rec.gd`.
- Its window takes no outside input. In one petrify take a key or the mouse reached the always-on-top window and
  turned the cobra mid-take.
- The cobra is re-aimed before every cast.

## Breach (2026-11-14, built, launcher only)
Preston picked Breach next ("Breach"). The game feel lane's brief: "burst 0.55 is the snout coming out of the far
face; damage lands there and the soft wall section dissolves." It is consistent with the phase power: the wall goes
soft, it does not break.

**Clip** (`Breach`, 1.5 s, in place horizontally, `cobra.events.json`): wind 0.30, go 0.36, contact 0.4167, burst
0.55 (damage), clear 1.0167, stop 1.046. The game moves the cobra at 8 m/s from go to stop (5.5 m). Near face 2.163 m
ahead at the start, wall 2.6 m tall and 1.6 m thick. Snout in model space: contact (0.079, 1.499, 1.740), burst
(0.079, 1.083, 2.099) (`check_r2.log`). At burst the snout is 0.14 m short of the far face plane; the far ring is
placed by projecting it onto the face.

**What it does, keyed to the events:**
- **wind:** the hood strips charge to 0.9 (the halo at half the gaze's, since the halo is the gaze's display). The
  section's three faces (near, far, top; 2.2 m wide by default) soften over 0.12 s: the scene under each is sampled
  shifted, so the face wavers like liquid, slow sag waves run over it, a faint gold tint, and a thin gold frame
  marks the section edge.
- **go:** strips to 1.15.
- **contact:** one fast ring spreads from where the snout meets the near face, a churn of rings stays round that
  hole while the body passes, and a small glint (0.65 of the gaze flash, 0.14 s) sits on the face.
- **burst:** the same ring and churn on the far face, a glint there (0.8 size), the strips flare to 1.45 and settle
  to 0.6, one floor wave runs out 3 m in 0.3 s on the far side (forward half only, the knock-back), and each enemy in
  `breach_hits` gets the small burst (0.55 m, 0.12 s) on kit cue `breach_hit`.
- **clear:** the churn dies over 0.3 s, the strips cool.
- **the gap:** from burst, `breach_gap_time` (4.0 s placeholder): the faces settle to 0.6 softness and the frame to
  0.45, then the section hardens over 0.2 s with one short pass of the frame, and everything is gone.
- A cast cut short (the clip ends before clear) hardens it at once.

**Contract for the kit (proposed).** Read at `wind`, all optional:
`breach_face: Vector3` (near face centre, at floor level), `breach_normal: Vector3` (out of the near face, toward
the cobra), `breach_size: Vector3` (width, height, thickness), `breach_gap_time: float`. Without them the clip's
numbers are used (face 2.163 m ahead, normal back toward the cobra, 2.2 x 2.6 x 1.6 m). Kit cue `breach_hit` after it
resolves burst, with `breach_hits: Array`. The fx never touches the wall: the game hides or dissolves the section
and turns off its collision (the clip note says so). The faces work either way: on a wall still drawn they waver on
its surface; on a hidden section they read as a soft gold membrane box where it was.

**Files:** `scripts/moba3d/cobra_fx.gd` (the Breach block), `shaders/cobra_breach_face.gdshader` (the soft face:
screen warp, sag, churn and burst rings round `hole`, gold frame; blend_mix, nothing above HDR 1.05 but the frame),
`shaders/cobra_breach_wave.gdshader` (the far-side floor wave). The launcher stub (`cobra_fx_standin.gd`, key 4) puts a
stand-in wall ahead of the cobra (the 5v5 wall model, read only, collision off at runtime), moves the cobra at 8 m/s
from go to stop, and on burst hits enemies within 2.4 m of the exit and pushes them 2.2 m. Those rules are guesses.

**Recorded and frame-checked (2026-11-14):** `D:/dev/_scratch/cobra-fx/rec/breach_rec.gd`, proofs
`breach-board-t2.jpg` and `breach2.mp4` (take 1 in `rec/take1/`). Three casts (chase camera at distance 12 and pitch 13,
full speed; a high three-quarter view of the near face at quarter speed; the far side at full speed). Each cast:
section at 2.163 m, near ring at contact (UV 0.46, 0.42), far ring at burst (UV 0.54, 0.58), 2 of 2 minions past the
exit hit, the off-path one not, section hard again 4.75 s after the clip starts. No script or shader errors.
- **Take 1** read as a flat yellow glass pane inside a hard rectangular outline, and the rings were thick and
  saturated. **Take 2** (current): no outline, a feathered irregular edge, thin wavering seams on the two sides only
  (where the section meets wall that stays hard), the wall's own surface bending round the snout, a light drain toward
  gold (the same read as the phase stun), pale highlights on the sag crests only, thin pale rings, and a floor wave
  that is one thin line over a warp.
- **The chase camera does not see the exit.** At distance 12 and pitch 13 the 2.6 m wall hides the far face and the
  floor wave once the cobra is through; from behind, Breach reads as the cobra sinking into a face that ripples and
  then a soft gap with seams. The far-side frames show the burst. Whether the game hides the section as the cobra
  passes (the clip note) decides how much of the exit the player sees.
- The stand-in wall is the 5v5 model (6 x 2.6 x 1.6 m, `[P: (-3, 0, -0.8), S: (6, 2.6, 1.6)]`, thin along its Z).
  It has legs and an open base, so parts of the cobra show through below it.
- A take that rendered all black (the window drew nothing, HUD included) was a one-off of the machine. A probe frame
  right after rendered normally, and the re-run matched take 1's brightness.

## Other effects that belo