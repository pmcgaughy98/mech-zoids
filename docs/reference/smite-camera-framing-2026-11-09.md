# SMITE camera framing, measured against our chase camera (camera lane, 2026-11-09)

Preston: "Yes, measure SMITE" (after the 3D gorilla heights check). Direction doc: original SMITE first, Paragon second
(docs/plan/moba-camera-combat-reference-direction-2026-11-08.md).

## What was read
- **Measured:** a SMITE 1 Conquest match, solo perspective, 1280x720 (YouTube Jerv-E09K7s, "SMITE Conquest Changes: Full
  Match Solo Perspective"). Frames at 2:00, 4:30, 7:00, 9:30, 12:00, 15:00, 18:30 and 22:00, each with a 5% grid.
  The frames stay in D:/dev/_scratch/camera-lane/smite1/ (not copied into the project).
- **Search, excerpts only:** a 2015 r/Smite thread asking for a camera-height setting (so SMITE 1 seems to have had
  none), and a SMITE 2 post about its "Action Camera" field-of-view toggle (SMITE 2 is not our reference).
- **Not found:** SMITE 1's field of view, pitch or camera distance. Everything below is fitted from the frames.

## SMITE 1 framing, measured (god: Sun Wukong, human-sized)
| | SMITE 1 | Ours before the switch (3D gorilla, 1.7 m, fov 60) |
|---|---|---|
| Feet, down the screen | about 71% | 63% |
| Head, down the screen | about 59-60% | 44% |
| Height on screen | about 11-12% | 19% |
| Across | centred, 50% | centred |
| Horizon (far ground meets sky) | about 28-30% | at the top edge |
| Ground at the screen centre | well ahead of the god | 2.1 m ahead of the gorilla |

So SMITE sits the god low and a little smaller, and tilts the camera much flatter. You see far ahead, and the aim
point at the screen centre is out in front of the god rather than on it. A ground-circle reading at 2:00 (33 degrees)
was thrown out: the orange effect is a swirl that rises off the ground, not a flat circle.

## Correction (2026-11-10)
The first version of this doc assumed our field of view was 75, the Camera3D default. The match scenes
(arena_blockout, field_test, rhino_walk_test) set it to 60, so the "ours" numbers and the fitted values were off.
Everything below is measured at fov 60 with the real ChaseCamera3D (D:/dev/_scratch/camera-lane/smite_fit_check.gd).

## Applied (Preston: "Yes, switch it", 2026-11-10)
| | pitch | distance | look height | feet | head 1.7 m | ult 3.1 m | horizon | ground at centre |
|---|---|---|---|---|---|---|---|---|
| SMITE fit, now the default | 13 | 12.0 | 3.2 | 71% | 60% | 51% | 30% | 13.9 m ahead |
| Before | 30 | 6.5 | 1.2 | 63% | 44% | 24% | top edge | 2.1 m ahead |

- The camera sits 5.9 m up and 11.7 m behind. Near a map edge the clamp pulls it in: the feet drop to 73-83% and
  the top of the frame over the gorilla is 5.0-6.5 m, so a 3.1 m ult still fits.
- The gorilla now reads the size of a SMITE god, about 11% of the screen height (was 19%). For a bigger mech, shorten
  the distance and raise the look height together to keep the feet near 71%.
- SMITE's own field of view is still unknown. If it is wider than 60, the same framing at our fov is still right; only
  the perspective (how fast far things shrink) would differ.
- Mouse aim behind the machine now uses the bottom 29% of the screen, and the bottom edge shows ground about 5.4 m
  behind it. Game feel was told; its aim_check.gd needs updating for the 3D models anyway.

## Checks after the switch
match_check 67 pass, 0 fail. kick_check 0 failures (the kick reads the camera's distance and fov, so it stays 2 px).
aim_check hung headless (it reads the scrapped sprite and saves frames); that is game feel's to update.
The old file is backed up at D:/dev/_scratch/camera-lane/chase_camera_3d.before_smite.gd.
