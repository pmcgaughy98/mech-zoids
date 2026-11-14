# Camera kick along a hit (camera lane, 2026-11-06)

Preston: "Kick the camera along the punch. A nudge of a couple of pixels in the punch's direction, rather than a
random shake, reads as a hit instead of a rumble."

## What was built
- `KitFeel.kick(from, dir, px := 2.0, time := 0.15)` in scripts/moba3d/kit_feel.gd. It turns the hit's ground
  direction into a screen direction, jumps the picture px game pixels that way at once, then eases back
  (quadratic) over time seconds. It rides on the same h_offset/v_offset as the shake and adds to it; a new kick
  replaces the last one.
- `KitFeel.metres_per_px(cam)`: one screen pixel at the camera's look distance, 0.0554 m at 6.5 m, fov 75, 320x180.
- `KitFeel.KICK_SIGN` (1.0): the picture moves with the punch, so the camera moves against it. Set -1.0 to flip.
- `ChaseCamera3D.kick(dir, strength := 1.0)` in chase_camera_3d.gd, with `KICK_PX := 2.0`. Game feel's
  `KitFeel.basic_hit` already calls `cam.kick(d, strength)` when the local player lands or takes a basic.

## Check
tools/debug/kick_check.gd, headless at 60 fps: right, away from the camera and toward-left each give 2.00 px on the
first frame in the right screen direction (toward the camera is squashed by sin 30 on screen, so (-1,0,1) reads as
(-0.89,-0.45)), back to 0 after 9 frames; a kick on a 0.35 shake settles to 0. Result: 0 failures.

## Not done here
The gorilla punch has to call it (ape_kit.gd is the Gorilla Session's): only `KitFeel.basic_hit(player, t, dir)` at
the contact line, since basic_hit already calls the kick (agreed with game feel, 2026-11-06), with basic_shake set to 0 so the rumble does not sit on top.
Not yet seen by Preston in play. Tune one value at a time: KICK_PX, time, KICK_SIGN.
