# Combat camera synthesis (camera lane, 2026-11-13)

Preston: "We're changing from aim at mouse to more like smite where camera moves with where you are looking. Then we
can use the synthesis of game knowledge to make our own better combat camera which doesn't have to be like smites at
all if our collection of knowledge from synthesizing creates something better thats unique to our game and creates a
feel that players would crave like smite did."

## What was read
| Source | Read or general knowledge | What it gave |
|---|---|---|
| "3rd Person Aiming Is Cursed" (YouTube 8rYKGVLBBpU, transcript via the watch skill) | read | With the character offset to one side (over the shoulder), aiming left takes about twice the mouse travel of aiming right (6,000 vs 3,200 counts for the same 90 deg). The worst at close range. Paladins avoids it: no side offset, the camera raised higher instead. Close targets look slower in third person, so close tracking is easier than in first person. |
| SMITE / SMITE 2 | general knowledge, plus one Reddit thread excerpt ("a top down MOBA with a different camera angle") | Mouse turns the camera; WASD moves relative to it; the god sits centred below a centre crosshair; ground-targeted abilities land where the crosshair ray meets the floor, so looking down brings the target in. The camera is a top-down MOBA's targeting with a chase camera's view. |
| John Nesky, "50 Game Camera Mistakes" (GDC 2014, Journey) | general knowledge (chapter titles seen in the search result, talk not re-watched) | Don't turn the camera without player input; don't let the pivot drift far from the avatar; offer inverted look; ignore accidental tiny input; don't focus only on the avatar. |
| Our own measurements (docs/reference/smite-camera-framing-2026-11-09.md, camera-kit-moments-2026-11-13.md) | read (ours) | Feet at 71%, head about 53-55%, flat pitch 13 deg, per-machine distance 7.3-8.4 m. Kit numbers for every ability that leaves the frame. |

## Synthesis proposal (nothing here is canon)
What SMITE gets right and we keep: the mouse is the camera, the centre of the screen is the aim, the floor under it is
where ground abilities land. The machine stays centred (no shoulder offset), which the aiming source shows is what keeps
left and right equal. Our machines are big and heavy, so the camera can lean into weight rather than speed.

Ideas to make it ours, each one a separate slice Preston can say yes or no to:
1. **Weight in the turn.** A light machine's camera turns 1:1 with the mouse; an L machine's body lags the camera by a
   few frames and plants its feet when it turns hard. The camera stays crisp (aim never lags), the body sells the mass.
   Alternative: keep body and camera locked together, like SMITE.
2. **Aim that reads the kit.** When an ability with a ground ring is held, the camera tilts and pulls back just enough
   for the whole ring to sit above the HUD (the `hold(radius)` from the kit doc). Releasing snaps back over 0.25 s.
   Alternative: fixed camera, the ring may run under the HUD (SMITE's choice).
3. **Hit confirmation through the camera.** The punch kick already nudges 2 px along the hit. Extend it: a heavy hit
   stretches the field of view by 1-2 degrees for a few frames, a kill holds a tiny slow-down. Alternative: leave
   impact to effects and sound only.
4. **Ult framing.** The steep 55-60 deg lift Preston set for ults (2026-11-04), eased in over the wind-up.
5. **Reticle that knows range.** The reticle shows when the aim is past an ability's reach (dims, or the floor marker
   stops at max range). Alternative: SMITE-style, the targeter clamps silently.

## The first slice (built 2026-11-13)
- The mouse is captured in play. Left and right turn the camera (0.2 deg a screen pixel; 450 px is a quarter turn);
  up and down tilt it between 6 and 30 deg, bringing the aim nearer or further. Esc frees the mouse, a click takes it
  back. `invert_y` is there (Nesky).
- A small reticle sits at the centre of the screen. The player's aim is the floor under it (machine_test_player and the
  gorilla targeting read `cam.aim_screen()`). Checks that set `aim_screen_override` still win.
- Each tilt reframes the machine so the feet stay 71% down the screen.
- `mouse_look = false` on the camera brings back aim-at-the-cursor.
- Check: tools/debug/mouse_look_check.gd (headless, --fixed-fps 60).

## Slice 2 (built 2026-11-14): ring pull-back
Preston picked "Ring pull-back". chase_camera_3d.gd `hold(radius, seconds, ult)`, also fired automatically from each
kit's `used(slot)` through the camera's RING_MOMENTS table (radius read from the kit's export). During a hold the
machine moves to the middle of the screen, the camera tilts to 30 deg (57 deg for ults, Preston's 2026-11-04 rule) and
pulls back until the ring's near edge sits at 80% down, just above the HUD bar. The aim stays on the same spot of floor.
Geometry finding: a ring centred on the machine needs the camera about three ring radii away, so the pull is big for big
rings. Measured (tools/debug/ring_hold_check.gd, 12/12): gorilla chest beat 3 m -> 6.9 m from the feet; rhino pound
4 m -> 9.2 m; kangaroo bout 3 m (ult) -> 8.9 m; pangolin comet 4 m (ult) -> 11.8 m; gorilla ult 5.5 m -> 16.3 m;
hippo flood 6 m -> 17.8 m (normal frame is 7.3-8.4 m). Capped at 20 m. Tunables for Preston: RING_PITCH, ULT_PITCH,
RING_FEET, MAX_ARM, EASE_IN/OUT and the seconds per move in RING_MOMENTS.
Preston on the video (2026-11-14): "Feels right". The pull distances above stand as they are.

## Slice 3 (built 2026-11-14): weight in the turn
Reference read: MechWarrior (search excerpts, Reddit and metamechs.com): legs turn by tonnage, the torso twists fast to
aim, and the two are separate stats. Ours: the body (visual only) turns at most TURN_CAP deg/s by size class, L 260,
M 400, S 600, 1.75x during an action (mech_model_3d.gd face()); facing and aim stay instant. Measured
(tools/debug/turn_weight_check.gd, 6/6): 180 deg takes 0.72-0.78 s on L, 0.50-0.58 s on M. Preston's pick for the gait
during a heavy turn (2026-11-14): "A: feet shuffle", so the gait keeps reading the body heading and steps strafe or
backpedal while it swings round (about 0.5 s of steps on a full reversal). Game feel's stage1_body_probe waits about
0.6 s for the turn.

## Unreal vs Godot camera (camera lane, 2026-11-18, read-only; nothing changed)
Found after the map lane noticed Unreal's -ArenaShot camera (ArenaMap.cpp 436-446: 12 m back, 3.2 m look height,
horizontal fov 91.5) still uses Godot's pre-2026-11-13 numbers. The in-game Unreal camera is a separate rig,
ATrialGorilla in D:/dev/mech-moba-unreal/Source/MechMoba/Trial.cpp 61-69, and differs from Godot's in five ways:
| | Godot chase_camera_3d.gd (now) | Unreal Trial.cpp (now) |
|---|---|---|
| Distance | per machine, 7.3-8.4 m from the feet, framed so the body fills 16-18% of the height | spring arm 8.5 m from a pivot about 2 m above the feet, same for every machine |
| Side offset | none: machine centred (keeps left and right aim equal, the synthesis finding) | 1.9 m to the right (over the shoulder) |
| Field of view | 60 deg vertical (91.5 horizontal at 16:9) | 65 deg horizontal, about 39 deg vertical: much tighter, reads zoomed in |
| Pitch | 13 deg, mouse 6-30, feet held 71% down the screen | starts 20 deg, mouse pitch with the engine's default limits |
| Body turn | capped by class (L 260, M 400 deg/s), aim instant | body yaw locked to the camera (instant), except during listed actions |
Also not in Unreal: the ring pull-back, the reticle aim on the floor, the per-machine framing. Any change there needs a
hub queue row; Preston decides whether Unreal should match Godot.

Pangolin framing height (2026-11-18): Godot's camera reads 1.486 m for the pangolin, because its scrap_shell (comet ball) mesh counts as visible; the body (top_height) is 0.941 m. Preston: "Keep it as is", so the pangolin keeps the 7.3 m camera, and the Unreal port (hub row 71) frames it from 148.6 cm to match.

## Unreal camera matched to Godot (hub row 71, 2026-11-20; Preston: "Yes, match Godot")
Trial.cpp/Trial.h, ATrialGorilla::UpdateCameraFrame(): machine centred (no 1.9 m shoulder offset), 60 deg vertical at any
aspect, feet 71% down, body share by class (L .18, M .16, S .14), mouse pitch held 6-30 deg down, start 13. Pangolin framed
from 148.6 cm to match Godot. -CameraFilm films every machine in Arena3v3 (4 s each, pitch 13/30/6) and logs COMPARE_CAMERA.
Measured from the engine's own projection, all 8 machines at pitch 13 and 30: feet 0.710 down, centred 0.500; heads 0.530 (L),
0.550 (M), 0.570 (fennec); arms gorilla/rhino 7.46 m, hippo 8.07, kangaroo/cobra 8.35, bison 7.24, pangolin 7.30, fennec
6.14; no wall pull-in. Full Check Migration PASS (first run missed one gorilla TrialAuto contact; a rerun of that smoke test
and the second full run passed). DLL 89C3D03F. Film: D:/dev/_scratch/camera-lane/video/unreal_camera_match_2026-11-20.mp4.
Not ported yet: ring pull-back, centre reticle aim, turn weight.
