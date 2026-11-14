# Gorilla effects: synthesis (2026-11-11)

Preston's effects decisions today, relayed by the rhino effects lane and the gorilla 3D lane: effects may use any tool
but must not look like pixel art; the bar is SMITE 2 and the reference is Cabrakan's Tremors. He liked the rhino's
smooth brace release, cut the drifting motes, and found the big white flash too much, so impact flashes stay small
and short and a point light must not wash the mech out.

This pass does for the gorilla what `rhino-fx-synthesis-2026-11-11.md` did for the rhino. It reuses that doc's
Cabrakan measurements and adds one god whose kit is close to the gorilla's.

## Stock-take (what was on hand, what each did)

| Tool | Used for |
| --- | --- |
| Firecrawl search | Confirmed Geb is playable in SMITE 2 and found in-game footage |
| `watch` skill (yt-dlp, ffmpeg) | Pulled the footage; ffmpeg cut it into time-stamped sheets at 15 fps for measuring |
| Godot shaders, `--write-movie` | Built the slice and recorded it in the real match at the game camera |
| Project checks | `match_check.gd`, `arena_roster_check.gd` after the build |
| The rhino lane's doc, code and recorder | Structure and the rules that already held (bloom threshold, no red, fog off) |

Not used, and why: PixelLab's effect workbench (pixel look is ruled out); paid generators (nothing here needed one);
Blender (no model work); Director's Lookbook (the gorilla's lime already exists on its shield cells and in Codex's
atlas, so no new palette was needed).

## What was read and measured

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, "Geb and Ullr in-game showcase" (youtube Ry_ywMSV3N4, 1280x720 at 60 fps, beta build) | **Measured** at 15 fps (one cell = 0.067 s): Cataclysm at 10:21.6 to 10:23.7, Shock Wave at 9:52.5 to 9:53.6. Scanned at 5 fps and 0.5 fps for the rest of 9:30 to 13:40 | Wind-up, impact and clean-up timing of an area ultimate and of a ground ring; what is light and what is matter |
| Same video, Roll Out (11:16 to 11:18) | Scanned at 5 fps only | A charge leaves a trail of dust puffs behind the body; each hangs about 0.6 s |
| Same video, Stone Shield | **Not measured.** No clear cast of the ally shield was found in the section scanned | Nothing; the shield row below is a proposal from our own hex shield, not from Geb |
| SMITE 2, Cabrakan's Tremors | Read from the rhino doc (measured there, youtube 8Tfl1TgQ7sY and NSL4xBviayQ) | Cracked ground with three states: hot cracks, cooled dark fissures, debris |
| Geb's kit as text (smite2.live, TheGamer guide titles) | Search excerpts only | Roll Out (charge), Shock Wave (ground hit), Stone Shield (ally shield), Cataclysm (area ultimate): the closest SMITE 2 kit to the gorilla's shield, ground line, charge and area-locking ult |
| Our own ult today | Recorded in the match and watched (the "before" take) | What is already drawn: the kit's pixel pulse ring and pixel puff, Codex's atlas ring and panel bursts, the hex cage |

Sheets and the clip are in `D:/dev/_scratch/gorilla-fx/ref/` (`geb_cata15_1.jpg`, `geb_cata15_2.jpg`,
`geb_shock15.jpg`, `geb_scan_*.jpg`). Nothing from them is in the project.

Caveat: the footage is a streamer's capture of SMITE's third-person camera with overlays, from a beta build. Timings
are good to one cell (0.067 s); screen coverage does not transfer to our top-down camera.

## Structure learned (measured unless marked)

**Cataclysm, the area ultimate, cell by cell:**
1. **Ground tell, 3 cells (0.2 s):** a pale wash spreads over the floor of the whole area. It is faint and it goes
   quiet again before the hit.
2. **The body carries the wind-up, 9 cells (0.6 s):** Geb himself lights up, a bright yellow glow over his whole
   body and every floating rock. The floor does almost nothing in this window. Total wind-up 0.8 s.
3. **Matter first, 1 cell:** grey rock spikes punch up out of the floor across the area. They are solid shapes, not
   light.
4. **One flash cell:** a white and yellow flash, in the one cell after the spikes. It is gone the cell after.
5. **Dust and chunks, 4 cells (0.27 s):** an amber and brown dust cloud with many dark rock chunks thrown up and
   out, a few radial streaks in the first two cells.
6. **Clean-up, 4 cells:** dust thins, chunks fall. The floor is clean 10 cells (0.67 s) after the eruption.
   **Nothing lingers** on Geb's floor: no cracks, no scorch. (Cabrakan's cracks linger; Geb's do not.)

**Shock Wave, the ground ring:**
1. **Anticipation, 4 cells (0.27 s):** arms and rocks lift. No ground effect; the body sells it.
2. **Down-stroke, 1 cell:** pale vertical streaks from the hands down.
3. **Impact, 1 cell:** an amber glow at the feet about as wide as the body, not white, not screen-filling.
4. **The ring is dust:** one cell later a brown dust ring is already at about 60% of its size, with rock chunks in
   it; it is at full size 3 cells (0.2 s) after impact. The amber light is gone by then.
5. **Total life 0.6 s** from impact to clean, the same as Cabrakan's ring burst.

**What the two share, and what it means:**
- The wind-up reads on the body, not the floor. The floor only speaks at the hit.
- Light is short and small (1 cell); what travels outward and tells the reach is dust and rock.
- Geb's own colour is amber and yellow. Enemies he hits flash red and pink for 3 to 4 cells. No red on Geb.
- A ring reaches most of its size in the first third of its life, then creeps while it fades (same as the rhino doc).

## Synthesis proposal (nothing here is canon)

**Look:** smooth shader effects, soft edges, layered. The gorilla's energy colour is the **lime** already on its
shield cells (about #9EFF29), with white only at the hottest point. Earth is warm grey dust and dark floor-coloured
rock. No red, no amber (amber is the rhino's hot colour and Geb's). Bright cores above 1.05 so only they bloom.

**The gorilla's two effect families:**
- **Sound** (chest beats, taunts): thin lime ripples on the floor, always a double ripple (a rim and a fainter echo
  behind it), no dust. A chest beat moves air, not earth.
- **Weight** (slams, the charge, footfalls): dust, rock chunks and cracked floor, with lime only in the hot cracks
  and on the edge that marks the reach.

**Ult, Silverback Cage (built, slice 1):** see "First slice" below.

Alternatives named:
- **A (built):** hot cracks are lime, so the floor reads as the gorilla's own energy breaking through.
- **B:** hot cracks are amber like the rhino's and Geb's, lime only on the edge. More "earth", less the gorilla's own.
- **C:** no lingering cracks at all, as Geb does it: spikes up, dust, clean in 0.67 s. Cleaner floor inside the cage,
  but the slam leaves no mark.
- **D:** keep Codex's atlas ring decal under the smooth ripple on each beat (the script has a switch,
  `hide_codex_ring`). The built take mutes it so two rings do not stack; Preston picks.

**Effect list for later slices** (the kit's own timings; proposals only):

| Effect | Proposal |
| --- | --- |
| Always on | The ring under the gorilla is the kit's pixel `silverback_ring`. Replace with a faint lime disc at the aura's size with a few etched hex lines, a slow breath, brighter while an ability is live (Cabrakan's disc) |
| Ult wind-up on the body | Shield cells and chest glow rising over the four chest hits (Geb's whole-body glow). Needs a glow hook on the model: ask the gorilla 3D lane |
| Basic chain | Swats keep the look lane's smooth hit spark. The third hit (slam, contact at 0.417 s): a small crack burst about 1.6 m at the target and two dust puffs, the ult's ground at low power |
| 1 Hex Shield | At the release (0.25 s): a lime ripple at the ally's feet and a soft rim rising with the bubble. Codex's seal decal is the current read; show old against new |
| 2 Fault Line | A crack that runs along the line from the fists to the end point (the crack web, masked to a strip), dust along it in order, a dust wall at the end point. Geb's ring structure laid along a line |
| 3 Drive Slam | Dust puffs left behind every 0.2 s of the drive, each hanging 0.6 s (Geb's Roll Out); a short dust burst at the collision; the grab slam reuses the fist dents and cracks under the target |
| Footfalls | The body's `step` signal (hand_l, hand_r, foot_l, foot_r) fires and nothing listens: a small low dust puff per knuckle plant, none for the feet |
| Cage wall | Not studied here. Odin's Ring of Spears is the SMITE 2 wall to measure next |

## First slice (built 2026-11-11): the ult's chest beats and final slam

**Why this one:** the ult is the gorilla's signature and uses both families at once (sound on the beats, weight on
the slam). It was also where the pixel stand-ins were most visible: the kit's flat pixel ring swelling on each
beat and a pixel puff at the slam. The heavy slam's ground impact was the other candidate; it is a subset of this
(the fist dents and crack web reuse for it, see "What is next").

**Informed by:** Cabrakan's Tremors (cracked ground that starts hot and cools), Geb's Shock Wave (the reach is
carried by a wall of dust, light is one short cell), Geb's Cataclysm (the wind-up belongs to the body, the floor
speaks at the hit). The double ripple for a chest beat is our own.

**Files (all new; no kit, shared-effect or model script was edited):**
- `scripts/moba3d/gorilla_ult_fx.gd`: the observer. Listens to the kit's `used` signal and the body's clip events.
- `shaders/gorilla_beat_ring.gdshader` (the ripple), `shaders/gorilla_slam_ground.gdshader` (fist dents and crack
  web), `shaders/gorilla_dust.gdshader` (dust clouds).
- `scripts/moba3d/gorilla_fx_installer.gd`: attaches the observer to every gorilla kit in the scene. It was built
  as an optional launcher first; see "In the main match" below for where it lives now.

**Timeline (seconds after the cast; the clip's own events, measured in the match):**

| Time | Event | What is drawn |
| --- | --- | --- |
| 0.40, 0.52, 0.63, 0.73 | `drum` 1 to 4 | A small lime double ripple at the feet, 1.95, 2.3, 2.65 then 3.0 m, each a little stronger, 0.3 s long |
| 0.42 and 0.73 | `beat` 1 and 2 (the taunts) | A double ripple that races to the taunt reach (5.5 m) in 0.14 s and fades by 0.5 s. The second is quieter, as in the kit |
| 1.27 | `beat` 3 (the slam) | Two fist dents placed from the hand bones (1.0 m ahead, 1.03 m apart); a crack web 3.2 m out from the line between the fists, white-hot at the fists and lime outward for about 1 s, then thin dark fissures with a pale dust lip, gone by 2.4 s; a lime edge and 16 dust clouds out to the cage wall (5.5 m); dust at each fist; 10 rock chunks that land, lie there and sink at 2.4 to 3.0 s; a small light at the fists (energy 1.0) gone in 0.2 s |

**Hidden while the ult plays:** the kit's two pixel `silverback_ring` pulses and its pixel `impact_puff` (3 nodes,
counted in the check). **Muted by default, Preston picks:** Codex's atlas ring decal on each beat (3 bursts), so two
rings do not stack; `hide_codex_ring = false` on the node brings it back. Codex's panel bursts on the cage wall,
its shield-cell pulse on each chest hit, its hex ground mark, the hex cage and the always-on rings are untouched.

**Checked in the match recording** (`D:/dev/_scratch/gorilla-fx/rec/`, 1280x720 at 60 fps, the game camera):
- All seven events fired in order in both takes; the fists were found from the bones.
- The 5.5 m ring spans about 46% of the screen width at the game camera.
- First take: the cooled cracks read as thick black scribbles and the fist dents as two eyes. Fixed: lines about
  0.1 m at the fists down to hairlines, cooled cracks half see-through, dents a soft press with a thin rim.
- The gorilla stays readable on the impact frame; nothing fills the screen.

**Not done in this slice:** the body does not glow during the wind-up (needs a glow hook on the model); the hot
cracks do not light the gorilla from below; no sound; the cage wall itself is as it was; the HUD bar covers the
near part of the ring at this camera, which is the game's own layout.

## In the main match (2026-11-11, later)

Preston saw the before and after and answered "Yes, use it" to replacing the current ult effect in the main match.

- `scenes/moba3d/arena_play.tscn` has one new child node, `GorillaFxInstaller` (script
  `gorilla_fx_installer.gd`). It attaches `GorillaUltFX` beside every gorilla kit, the player's and the bots'. No
  script of the match, the kit or the shared effects was edited. To turn the effect off, remove that node; the scene
  as it was is saved at `D:/dev/_scratch/gorilla-fx/backup/arena_play.tscn.before-gorilla-fx`.
- `scenes/moba3d/gorilla_fx_arena.tscn` is now just the main match with `start_on_gorilla` on.
- Preston's pick, 2026-11-11: "Keep it muted". Codex's atlas ring on each beat stays muted during the ult
  (`hide_codex_ring = true`, the default). Its other decals are untouched. Still his to pick: crack colour, lime
  (built) or amber.
- Re-recorded in the main match on the gorilla 3D lane's v32 ult clip (harder torso rock, same event times): all
  seven events fired, fists found from the bones, 3 stand-ins hidden, 3 atlas rings muted.
  Video: `D:/dev/_scratch/gorilla-fx/rec/gorilla-ult-smooth-main-match-v32.mp4`.
- Checks: `launcher_check.gd` 11 pass (the main match carries the installer and keeps its own starting machine, a
  rhino gets nothing, the player's and both bot gorillas get the effect); `match_check` 67 pass, 0 fail.
- `arena_roster_check` is unsteady since the afternoon, with or without this node. Before the scene edit: the
  seven known failures. After: 8, 7 and 8 failures over three runs with the node, and 7 with the node taken out.
  "shield release emitted once within one rendered frame of .25s" failed in all four of those runs, the one
  without the node included, so it does not come from this effect. It multiplies a frame count by one sampled
  frame time, so it moves with machine load (the release landed 5, 18, 21 and 22 frames after the cast).
  "slam drops victim onto ground" passed in two runs and failed in two. Logs: `rec/roster*.log`.
- Not done: an enemy gorilla's ult draws in the same lime as the player's; a team tint is the look lane's rule to
  apply here next.

## Second slice (built 2026-11-12): cracks under the slam hits

Preston: "Yes, start it". The basic chain's third hit and the grab slam get the ult's cracked floor, smaller, under
the target. Weight family only: cracks, dust and rock chunks, no ripple.

- **Where it is on:** everywhere the installer runs, the main match included, since Preston's "Yes, turn on"
  (2026-11-12) on the old-against-new video. It was launcher-only until then. The installer's `slam_hits` switch
  turns just this part off again.
- **Code:** in `scripts/moba3d/gorilla_ult_fx.gd`, observer only. It listens to the kit's `contact(target, slam)`
  and to `kit.grab.slammed(target)`. `shaders/gorilla_slam_ground.gdshader` gained one switch, `dent_mul`.
  The ult's slam now goes through the same `_ground_burst` helper; its look is unchanged.

| Hit | When (in the recording) | What is drawn |
| --- | --- | --- |
| Chain slam | contact of the Slam clip, 0.417 s in | A crack web 1.7 m out from under the target, hot lime for under a second, gone by about 1.8 s; no dent (the target is standing there); two dust clouds thrown away from the gorilla; 4 small chunks; no light |
| Grab slam | `slammed`, 0.75 s after the drive's collision | One body-sized dent under the victim; a crack web 2.4 m out, gone by about 2.2 s; six dust clouds thrown outward; 7 chunks; a light of 0.6 for 0.2 s |

- **Muted, by Preston's "Yes, turn on":** Codex's atlas crater (cell 1) under those two hits, so two craters
  do not stack (`hide_codex_crater`). Its star burst on the grab slam, its hex ground mark and chips, and the look
  lane's hit spark all stay.
- **Recorded** in the main match scene at the game camera, old against new, on an enemy rhino:
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-slam-hits-before-after.mp4`. Both takes fired swat, swat, slam at 4.62 s,
  the drive's collision at 8.85 s and the grab slam at 9.60 s.
- **Falls short:** on a big target most of the web is under its body, so only the outer cracks show; the hits are
  small at the game camera (the chain slam's web is 3.4 m across, about 14% of the screen width, scaled from the 46% measured for 11 m); no sound.

## Third slice (built 2026-11-12): Fault Line, the crack run (key 2)

**Rejected by Preston, 2026-11-12:** "needs lot of tuning looks like a flat sheet that just travels. Original looks
noticeably better like that". Codex's original Fault Line stays everywhere. The crack run is switched off in the
launcher too (`fault_line = false`); the code is left in place, dormant, for a later retry.

Why it failed, as far as can be told from his words and the frames (this lane's reading, not his): it is one flat
layer on the floor whose reveal slides along, so nothing has height or mass, and the thing that travels is a sheet.
Codex's crater is a painted object with rock shapes and spikes, so it reads as a thing moving through the ground.
It was also built without a measured line attack, which is the step the method says not to skip.

Before a retry: measure a real SMITE 2 line ground attack cell by cell first, and build the travelling part from
shapes with height (rock slabs or spikes that rise and settle), not from a flat strip.

What was built, for the record:

Preston: "Yes, start it", then "Yes, finish it" after a stop part way.

- **Reference, stated plainly:** no line ground attack was measured. The Cabrakan demo on disk
  (`D:/dev/_scratch/rhino-fx/ref/az_demo.mp4`) was scanned at one frame a second and has none. So this is built from
  structure already measured on rings and trails: cracks that start hot and cool (Cabrakan), dust that hangs about
  half a second behind a moving thing (Geb's Roll Out), a reach carried by dust (Geb's Shock Wave). A SMITE 2 line
  attack is still to be measured.
- **The kit's own timing (measured in the match):** the wave starts 0.43 s after the cast (the Slam clip's contact),
  runs the 6 m at 9 m a second and reaches the end point at 1.08 s; the slow area lasts 1.4 s and is gone at 2.47 s.
- **Where it is on:** only in `scenes/moba3d/gorilla_fx_arena.tscn` (the installer's `fault_line` switch). The main
  match still plays Codex's look, because this hides Codex's sliding atlas crater and its slow-area decal
  (`hide_codex_fault`) and Preston has not picked. Codex's star burst at the end point and the aim marker stay.
- **Code:** `_watch_fault` in `scripts/moba3d/gorilla_ult_fx.gd` reads `kit.fault.waves` and `kit.fault.fields`
  (positions only); `shaders/gorilla_fault_run.gdshader` is new; `gorilla_slam_ground.gdshader` gained `rim_m` and
  `rim_life`. No kit, Fault Line or shared-effect script was edited.

| Moment | What is drawn |
| --- | --- |
| The wave runs (0.43 to 1.08 s) | A kinked fissure from 1.0 m ahead of the gorilla (the fists) to the end point, 0.17 m wide thinning to 0.08 m, with side cracks out to about 0.9 m either side. It appears as the wave head passes, hot lime right behind the head, cooling the further back it is. A small hot point rides the head. One dust cloud about every 0.9 m, on alternating sides |
| The end point (1.08 s) | A crack burst the size of the slow area (1.5 m), five small chunks, six dust clouds thrown outward |
| The slow area (1.08 to 2.47 s) | A thin quiet lime rim at 1.5 m with a barely-there fill, for exactly as long as the slow lasts |
| After | The fissure and the burst cool to thin dark cracks with a pale lip and are gone about 2 s after the wave stops |

- If a wall or the cage stops the wave, the fissure stops there and fades; there is no end burst.
- **Recorded** old against new in the match at the game camera, a clean line and a line with two enemies on it:
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-fault-line-before-after.mp4`.
- **First take, fixed:** a 0.1 m fissure on smooth curves read as a laser beam. Now wider, kinked (triangle waves),
  with visible side cracks and bigger dust.
- **Falls short:** while it is hot the fissure still reads partly as a bolt of energy rather than broken floor
  (no raised slabs, it is one flat layer); the slow area's rim is thin at the game camera; no sound; not measured
  against a real line attack.
- **Checks after the build:** `launcher_check.gd` 21 pass (the run and end burst fire in the launcher, the run is
  4.97 m, Codex's node is hidden, everything cleans up, the main match still plays Codex's look);
  `match_check` 67 pass; `arena_roster_check` 8 failures, the same unsteady set as on 2026-11-11.

## Fourth slice (built 2026-11-12): the ring under the gorilla, and footfall dust

Preston: "Yes, start it". Both parts stay under the gorilla; nothing travels on its own.

- **Reference, stated plainly:** no always-on ring and no footfall dust was measured in SMITE 2 for this slice. It is
  built from rules already measured: things that are on screen all the time stay quiet and under the bloom threshold
  (the rhino lane's brace ring), and kicked-up dust hangs about half a second (Geb's Roll Out). What was measured is
  our own game: the old ring in match frames, and the walk.
- **The old ring (measured in match frames):** the kit's pixel `silverback_ring`, a thin dashed dark-teal circle at
  2.5 m (`aura_radius`, the reach of the gorilla's cover for allies). Very quiet. The new one keeps that language: a
  dashed range marker, not a glowing disc.
- **The walk (measured headless, `D:/dev/_scratch/gorilla-fx/rec/walk_probe.gd`):** the Walk loop is 0.6 s with four
  plants, fired by the body's `step` signal as `foot_r` (0.03 s), `hand_l` (0.25 s), `hand_r` (0.35 s), `foot_l`
  (0.55 s). A hand bone rests at 0.37 m and swings to 0.51 m; a foot bone rests at 0.27 m and lifts to 0.45 m.
- **Where it is on:** only in `scenes/moba3d/gorilla_fx_arena.tscn` (the installer's `aura_disc` and `step_dust`
  switches). The main match still shows the kit's pixel ring and no dust, because the ring is a replacement and
  Preston has not picked.
- **Code:** `_watch_aura`, `_on_step` and `_bone_floor` in `scripts/moba3d/gorilla_ult_fx.gd`;
  `shaders/gorilla_aura_disc.gdshader` is new. The kit's pixel ring (`kit._aura`) is hidden, never freed, and comes
  back if the switch goes off. No kit, body or shared-effect script was edited.

| Part | What is drawn |
| --- | --- |
| The ring (always) | A thin lime rim at 2.5 m in sixteen soft dashes, a faint glow just inside it, a barely-there fill. It breathes slowly (12 percent, every 2.4 s) and the dashes turn very slowly. Nothing in it reaches the bloom threshold. It rides the gorilla and hides with it, as the pixel ring did |
| Each hand plant | One low dust puff, 1.2 m across at its widest, where that hand bone is, pushed a little back along the travel, gone in 0.45 s |
| Each foot plant | The same, smaller and fainter (0.95 m) |
| Standing, or any action clip | No dust |

- **Recorded** old against new in the match at the game camera (stand, walk right, walk down and left, stand), then
  close at quarter speed: `D:/dev/_scratch/gorilla-fx/rec/gorilla-ring-and-walk-before-after.mp4`.
- **First takes, fixed:** the first ring was a solid bright circle with a near-white core, far louder than the pixel
  ring it replaced; now a third as bright and dashed. The first dust (0.6 m, faint) could not be seen at the game
  camera; now twice the size and twice as strong.
- **Falls short:** the dust is still small at the game camera (about three puffs alive at once); the ring is one flat
  layer that moves with the gorilla, the same kind of layer that was rejected on Fault Line, though here it marks a
  range and does not slide along a line by itself; the ring is lime for an enemy gorilla too (no team tint); only the
  Walk loop was probed, so strafe and backpedal dust depends on the gorilla lane's footfall rows for those clips;
  no sound.
- **Checks after the build:** `launcher_check.gd` 29 pass (the ring is drawn at 2.5 m, the pixel ring is hidden and
  not freed, 1.25 s of walking drew 8 puffs with 3 alive at once, standing draws none, the main match is untouched);
  `match_check` 67 pass; `arena_roster_check` 8 failures, the same unsteady set as before.

### Turned on in the main match (2026-11-12, evening)

Preston: "Yes, turn on". The installer's `aura_disc` and `step_dust` now default to true, so every gorilla in
`arena_play.tscn` (player and bots) gets the smooth ring and the footfall dust; the kit's pixel ring is hidden, not
freed, and setting `aura_disc` false brings it back.

- **The gorilla model changed after the old-against-new video was recorded:** `art/arena_models/gorilla.glb` was
  replaced at 15:17, three minutes after that take (15:14). The effect was re-checked and re-recorded on the model the
  game loads now: 31 clips, the four bones the dust uses (LeftHand, RightHand, LeftFoot, RightFoot) are present, the
  ult's events and the walk's footfalls still fire.
- **Recorded on the current model, main match, game camera:**
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-ring-and-walk-main-match.mp4` (24 puffs over about 3.7 s of walking).
- **Checks:** `launcher_check.gd` 31 pass; `match_check` 67 pass; `arena_roster_check` 8 failures, the same unsteady
  set as before.

## Fifth slice (built 2026-11-12): Drive Slam dust (key 3)

Preston: "Yes, start it", then "Yes, turn on". A travelling effect, so it was measured first and built from shapes
with height, the lesson from the rejected Fault Line.

- **Measured (SMITE 2, Geb's Roll Out, the same video as before, 11:16 to 11:18, cut at 15 frames a second; sheets
  `D:/dev/_scratch/gorilla-fx/ref/geb_rollzoom_1.jpg` and `_2.jpg`):**
  - 0 to 0.2 s: the wind-up, a few loose rock chunks, no dust.
  - From 0.2 s: dust starts at the body. By 0.27 s there are two tall plumes, one each side of the path, behind and
    beside the body. Each is about as tall as the body or taller and about one body wide, dense at the base, soft at
    the edges, brown and clearly darker than the floor.
  - The middle of the path stays clear, so the body is always readable between the plumes.
  - Five to nine rock chunks are in the air around the body at once, each about a sixth to a quarter of its size.
  - Nothing in the trail lies flat on the floor. From the earlier 5 fps scan, each plume hangs about 0.6 s.
- **The kit's own timing (read from `arena_drive.gd`, confirmed in the match):** brace 0.24 s, drive 0.32 s at 12 m a
  second (3.8 m), then a brake on a miss or the hit, the grab and the grab slam on an enemy.
- **What the kit already draws:** the shield's drive energy and cell glow, and a contact spark on the hit (Codex's).
  All of it stays. This slice is additive: nothing is hidden or replaced.
- **Code:** `_watch_drive`, `_on_drive_phase`, `_drive_tick`, `_on_drive_hit`, `_drive_cloud` and `_chip` in
  `scripts/moba3d/gorilla_ult_fx.gd`, listening to `kit.drive.phase_changed` and `kit.drive.collision`. The switch is
  `drive_dust` on the effect and on the installer. No kit or drive script was edited.

| Moment | What is drawn |
| --- | --- |
| Kick-off (brace starts) | One low scrape of dust thrown back from the feet |
| The drive (0.32 s) | A tall brown cloud (1.8 to 2.2 m, the gorilla is 1.7 m) every 0.55 m, left then right, 0.8 m out from the path, so about seven along a full drive; each rises, drifts out and is gone in 0.62 s. A small rock chunk is kicked up with each, lands and shrinks away within a second |
| A miss (brake) | Two clouds thrown ahead of the feet as it skids, one chunk |
| A hit | Five clouds fanned out past the target, four chunks. No cracks and no light: the grab slam that follows has the cracks |

- **Recorded** old against new in the match at the game camera, a miss and a hit, each followed by quarter speed:
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-drive-slam-before-after.mp4`.
- **First take, fixed:** the dust was the pale warm grey of the slam dust and read near white on the blue floor. Now
  browner and darker for the drive only (0.50, 0.42, 0.31), as Geb's trail is against its floor.
- **Falls short:** from the game camera most of the dust sits behind the gorilla on the far side, so the near plume
  is the only one fully seen; the hit's fan is small next to the grab slam that follows; the chunks are tiny at the
  game camera; a wall stop draws the same skid as a miss; no sound.
- **On in the main match (same day):** the installer's `drive_dust` defaults to true, for the player and bot gorillas.
  Preston confirmed after seeing the old-against-new video: "Keep it on".
- **Checks:** `launcher_check.gd` 36 pass (a miss kicks off and skids and leaves 7 clouds, a hit throws the fan,
  everything cleans up, the main match draws it too); `match_check` 67 pass; `arena_roster_check` 8 failures. That
  run also printed three script errors from the pangolin kit (`install`, `_nearest_magnetised`, `salvage` not found)
  and failed "pangolin correct match identity": the pangolin lane was mid-edit, not this effect.

## Sixth slice (built 2026-11-13): team tint for an enemy gorilla

Preston: "Yes, start it". Launcher only until he picks.

- **Read (primary source, SMITE 2 Closed Alpha 1 update notes, smite2.com):** the game has "team coloration" on
  ability effects, and three notes in that one patch tone it down: Chaac's Thunder Strike ("avoid visual strain and
  overloading of red"), Chaac's Storm Call ("soften team color indicators, improve the readability of the edge of the
  damage"), Ymir's Shards of Ice ("toned down overpowering team coloration"). Not measured in footage.
- **Structure taken:** team colour is an accent on the edges that mark reach, kept soft. It is not a recolour of the
  whole effect.
- **What is drawn:** for a gorilla on the other team from the machine being played, the rim of the ring under it, the
  leading rim of each ripple and the cage edge take its team colour (the match's own red or blue,
  `MatchTeams.COLOURS`). Its cracks, inner glow, dust and chunks stay lime. Your own gorilla and allied gorillas are
  unchanged.
- **Code:** `_edge_color` in `gorilla_ult_fx.gd`; an `edge` colour was added to `gorilla_beat_ring.gdshader` and
  `gorilla_aura_disc.gdshader` (lime by default, so nothing changes until it is set). Switch: `team_tint`.
- **Recorded** from your own machine with the red team's gorilla beside you, as it looks today and tinted:
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-enemy-tint-before-after.mp4`.
- **On in the main match (2026-11-13):** Preston saw old against new and said "Yes, turn on". The installer's
  `team_tint` now defaults to true.
- **Falls short:** the red rim of the ring sits close to the red team ring the match already draws under an enemy, so
  that one part adds little; cracks under an enemy's slam are still lime; not checked for colour-blind readability.

## Seventh slice (built 2026-11-13): Reactor Fault Line with height (key 2)

Preston, relayed by the gorilla 3D lane: "have gorilla effects session upgrade slot 2. No sheets unless enhanced to
look like our other effects which look not flat because they arent pixel art". This reopens key 2 after "Leave the
original" on 2026-11-12. Launcher only until he picks, because it hides Codex's sliding crater and flat area decal.

- **Read and scanned, not timed:** Cabrakan's Tectonic Shift. Its in-game tooltip (read in
  `D:/dev/_scratch/rhino-fx/ref/smite2_cabrakan.mp4` at 2:38): "create a fissure ... From the fissure, five pieces of
  earth erupt to form a wall." In match footage (`vx_sheet.png`, same folder) the erupted pieces are jagged and as
  tall as the body or taller. The speed of the rise was not measured; the kit's own wave timing is used.
- **The kit's timing (kit v37, measured in the match):** the FaultLine clip fires "charge" at 0.10 s and "fire" at
  0.40 s; the wave starts at fire and reaches the end point 0.65 s later; the slow area lasts 1.4 s.
- **What is drawn (nothing flat travels):**

| Moment | What is drawn |
| --- | --- |
| Charge (0.10 s) | A soft lime glow swells on the back reactor |
| Fire (0.40 s) | A short lime arc, a string of glow beads lit one after another, goes up and over from the reactor to 1 m ahead |
| The wave runs | Where the wave head passes, a tall rock slab (0.85 to 1.25 m) erupts on one side and a short one on the other, swapping sides every 0.55 m. Each shoots up in a tenth of a second, glows lime and cools to dark rock in about half a second. Under each pair a small crack burst that stays where it is, and a puff of dust |
| The end point | A crown of eight slabs, the middle one 1.5 m tall, and a crack burst the size of the slow area with a quiet lime rim |
| The slow area ends | The crown sinks back into the floor as the slow ends; the line's slabs sink a little earlier |

- **Code:** the fault section of `gorilla_ult_fx.gd` was rewritten (`_fault_trail`, `_fault_arrive`, `_shard`,
  `_glow_at`, `_on_fault_clip`); `shaders/gorilla_glow.gdshader` is new. The rejected flat strip is no longer used
  (`shaders/gorilla_fault_run.gdshader` is left on disk, unreferenced). Switch: `fault_line`. No kit edits.
- **Recorded** old against new, a clean line, the same at quarter speed, and with two enemies on the line:
  `D:/dev/_scratch/gorilla-fx/rec/gorilla-reactor-fault-line-before-after.mp4`.
- **First take, fixed:** the slabs were smooth cones that glowed like traffic cones. Now flat-faced wedges in three
  shapes, darker rock, a calmer glow.
- **Falls short:** the arc is over in a tenth of a second and small at the game camera; the slabs are plain wedges with
  no texture; the cooled slabs read lighter grey than the floor; Codex's star burst at the end point still plays under
  the crown; no sound.
- **On in the main match (2026-11-13):** Preston saw old against new and said "Yes, turn on". The installer's
  `fault_line` now defaults to true for the player and bot gorillas; false brings Codex's look back.
- **Checks:** `launcher_check.gd` 45 pass with both slices in; `match_check` 67 pass; `arena_roster_check` 7 failures
  (the usual unsteady set; "slam drops victim onto ground" passed this run).

## Suggestions (2026-11-13): the ult wind-up glow and the cage wall. Nothing here is canon

Preston asked for suggestions for both. Nothing below is built. He picks; the first slice is named at the end.

### What was read and measured for these

| Source | How | What it gave |
| --- | --- | --- |
| SMITE 2, Geb's Cataclysm (measured 2026-11-11, above) | **Measured** at 15 fps | The wind-up belongs to the body: Geb and every floating rock glow for about 0.6 s; the floor does almost nothing until the hit |
| SMITE 2, Odin's Ring of Spears ("How to Odin in under 6 minutes in SMITE 2", youtube ZVz1TUxCAQU, 3:27 to 3:29; sheets in `D:/dev/_scratch/gorilla-fx/ref/odin/`) | **Measured** at 15 fps, but it is a montage with cuts and a tooltip over part of it, so only the cast and the standing wall could be read, not a clean rise | One bright cell at the caster on the cast; a wide band sweeps the ring's footprint on the floor and is gone in about 0.2 s; then the wall is standing. The wall is separate solid spears, about two bodies tall, with gaps, and a thin continuous line on the floor joining them. The top is open. The spears are in the god's material colours, the line and the burst in his ability colour |
| The same video's ability tooltip and commentary | **Read** | "Create a spear ring of walls that impedes enemies." The ring is made of segments that each have hit points and break one by one |
| Our own cage (`scripts/moba3d/hex_shield.gd`) | **Read** | A see-through hex-plated dome that rises in 0.32 s, flashes, then calms to its rim. Its plates come from a 50-texels-a-metre texture (`hex_tile.png`). The ult wall has panels with health; a broken panel is a gap |

### Structure taken

- A wind-up reads on the body and builds in steps; the floor stays quiet until the hit.
- A cage wall in a shipped game is matter with height standing on a thin floor line, not a film. It goes up fast, behind
  one short burst. Each segment is its own object, so a broken one is plainly missing.

### Ult wind-up glow: three options

The ult's own timing: chest hits at 0.40, 0.52, 0.63 and 0.73 s, the slam at 1.27 s.

- **A, the chest charge (suggested).** A soft lime glow on the chest that steps up with each of the four chest hits
  (four clear steps, from about 0.7 m across to 1.2 m), with a small spark where the fist lands on each hit. It holds
  while the gorilla rears up, then runs down both arms into the fists in the last tenth of a second, so the slam's
  cracks look fed by it. Built from the glow already made for key 2's reactor. Needs nothing from another lane.
- **B, the whole body lights up.** The lime hex cells on the chest, arms and back brighten in the same four steps, and
  the body gets a thin lime outline at the peak. This is the closest to Geb. It needs the model's own lights to be
  driven, which is the gorilla model lane's or the look lane's file, so it needs a hook from them first.
- **C, a ring gathers on the floor.** A lime ring closes in under the gorilla during the chest hits, from 3 m to
  nothing. Easy to see from far away, but it puts the wind-up on the floor, which is the opposite of what was
  measured, and it adds to a floor that already has the ring, ripples and cracks.

A and B can be combined later: A first, B on top when the hook exists.

### Cage wall: three options

- **A, pylons under the dome (suggested).** Keep the dome and all its rules. At the slam, a wide lime band sweeps the
  5.5 m edge once and is gone in 0.2 s, and a ring of rock pylons erupts along the edge, one per wall panel, each
  about 1.4 m tall, hot lime then cooling to rock (the same family as key 2's slabs). A thin lime line on the floor
  joins them for as long as the cage stands. When a panel breaks, its pylon shatters into chunks, so the gap reads at
  a glance. The dome above stays as the energy part. All of it is added around the cage; nothing of the cage is
  replaced.
- **B, pylons and curtains, no dome.** Ten taller pylons (about 2.2 m) with a soft lime curtain hanging between each
  pair and an open top, the closest to Odin's ring. A broken panel drops its curtain. This replaces the dome's look,
  which was Preston's own on 2026-11-04 and 2026-11-09, so it would be shown old against new before anything changes.
- **C, smooth the dome only.** Keep the dome as it is and only redraw its hex plates as smooth lines instead of the
  texture, plus the floor line and a skirt of dust as it rises. The smallest change. The wall stays a film.

Open questions for Preston on the cage: how tall the pylons should be against the gorilla (1.7 m), and whether the
dome's hex plates should stay as they are in option A.

### First slice, if he says go

Wind-up option A: the chest charge. One session, no other lane needed, recorded old against new in the launcher,
off in the main match until he picks. Headless check: four glow steps fire on the four chest hits in order, the run
down the arms fires once before the slam, and everything is gone within a second after it.
The cage (option A) would be the slice after that.

## Eighth slice (2026-11-14): the ult wind-up, the chest charge (wind-up option A)

Built from the Suggestions above, option A, on Preston's "Yes, build it".

- **What it does:** a soft lime glow on the gorilla's chest that steps up on each of the four chest hits (strength
  0.4, 0.55, 0.7, 0.9), with a small spark where the fist lands. In the last tenth of a second before the slam it runs
  out along both arms into the fists as a string of beads, then fades. If the ult is cut short it just fades, with
  no run down the arms.
- **Why this shape:** Geb's Cataclysm (measured 2026-11-11) puts the wind-up on the body for about 0.6 s and keeps
  the floor quiet until the hit. Our chest hits run 0.40 to 0.73 s and the slam lands at 1.27 s, so the glow lives
  on the body for about 0.9 s and hands over to the slam's cracks.
- **How it is drawn:** a camera-facing quad on the Chest bone with its own shader,
  `shaders/gorilla_glow_through.gdshader`, drawn through the body so the chest seems lit from inside. Never fully
  opaque (alpha capped at 0.8) and only a little of it turns toward white, so the gorilla is never washed out. The
  slam time is read from the clip's own events (its third "beat"), 1.27 s if the body does not say.
- **Files:** `scripts/moba3d/gorilla_ult_fx.gd` (the wind-up block, the call on each chest hit, the tick),
  `scripts/moba3d/gorilla_fx_installer.gd` (`windup_glow`, off), `scenes/moba3d/gorilla_fx_arena.tscn`
  (`windup_glow = true`), the new shader. Nothing of the kit's or Codex's is hidden or edited.
- **Checks:** the lane check passes 49 of 49, including the four steps, one run down the arms, everything gone after
  the ult, and "main match: no wind-up glow yet".
- **Video:** `gorilla-ult-windup-before-after.mp4` (in the lane's `rec/` folder and both notes folders): the ult as it
  is against the chest charge, full speed, then the wind-up at quarter speed.
- **State:** on in the launcher. **Turned on in the main match 2026-11-14** on Preston's "Yes, turn on"
  (`windup_glow` defaults to true on the installer).
- **What still falls short:** from the match's high camera the glow reads as a lime light on the chest more than as
  four separate steps; the run down the arms is quick (0.1 s) and easy to miss at full speed. Both are tuning, if he
  wants them stronger.

## Ninth slice (2026-11-14): the cage wall, rock pylons under the dome (cage option A)

Built from the Suggestions above, option A, on Preston's "Yes, build it".

- **What it does:** when the ult's cage goes up, a wide lime band lights its 5.5 m edge and narrows into a thin floor
  line in about 0.2 s. Under each of the cage's 10 panels a rock pylon erupts (one slab of about 1.4 m and two shorter
  ones of 0.8 and 0.55 m, leaning out), hot lime cooling to dark rock with a faint seam glow, staggered round the ring
  over 0.1 s. A hit on a panel flashes a glow at its pylon. When a panel breaks, its pylon shatters into seven chunks
  with a glow and dust, and that stretch of the floor line goes dark, so the gap reads at a glance. When the cage drops,
  the pylons sink and the line fades.
- **Why this shape:** Odin's Ring of Spears (measured 2026-11-13): separate solid pieces with gaps, about two bodies
  tall, on a thin continuous floor line, behind one short burst. Ours keep the dome above as the energy part and put
  the solid pieces under it. Pylons at 1.4 m sit just under the gorilla's 1.7 m.
- **How it is drawn:** the pylons reuse key 2's PrismMesh slabs (same rock, same lime). The floor line is a new
  shader, `shaders/gorilla_cage_line.gdshader`, which works out each panel from the world angle exactly as
  `HexShield.panel_at` does, so a dark stretch always matches the broken panel. It takes the team tint (an enemy
  gorilla's line is in their colour, as the ring and ripples are). The effect only reads the cage (its radius, its
  panels' health, whether it is up); nothing of the kit's or the cage's is hidden or edited.
- **Files:** `scripts/moba3d/gorilla_ult_fx.gd` (the cage block, the watch call, slabs can keep a faint glow),
  `scripts/moba3d/gorilla_fx_installer.gd` (`cage_wall`, off), `scenes/moba3d/gorilla_fx_arena.tscn`
  (`cage_wall = true`), the new shader.
- **Checks:** lane check: one pylon per panel (10 of 10), the floor line stands with the cage, a hit flashes its
  pylon and a broken panel's pylon shatters, everything is gone once the cage drops, and "main match: no cage pylons
  yet". The key 2 slab count now leaves out the pylons' slabs.
- **Video:** `gorilla-cage-pylons-before-after.mp4` (lane `rec/` folder and both notes folders): full speed, then the
  rise and a panel break at quarter speed. The camera lane's pull-back on 4 frames the cage a little differently from
  run to run (seen in two takes without the pylons too), so the video pairs the two takes whose camera matched.
- **State:** on in the launcher only. Off in the main match until Preston says turn it on.
- **What still falls short:** from the high camera the pylons read mostly as a ring of dark teeth; the shatter is
  clear, the panel-hit flash is small. The dome's own hex texture is unchanged (option C, smoothing it, is still open).

## What is next (in order)

1. Crack colour: closed. Preston saw lime against amber side by side on 2026-11-13
   (`D:/dev/_scratch/gorilla-fx/rec/gorilla-cracks-lime-vs-amber.mp4`) and said "Keep lime". The `crack_color`
   setting on `gorilla_ult_fx.gd` stays in place at its lime default. (The atlas ring on beats stays muted, his call.)
2. Built 2026-11-12 and on in the main match (second slice above).
3. Key 2: rebuilt with height and on in the main match (seventh slice above). The enemy team tint (sixth slice) is
   on in the main match too.
4. Built 2026-11-12 and on in the main match (fourth slice above).
5. Built 2026-11-12 and on in the main match (fifth slice above).
6. Ult wind-up glow: option A (the chest charge) built and on in the main match, 2026-11-14 (Eighth slice).
7. Cage wall: option A (rock pylons under the dome) built 2026-11-14, Ninth slice. Launcher only, waiting on
   Preston's yes to turn it on.
