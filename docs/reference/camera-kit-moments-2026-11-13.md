# Camera moments per machine (camera lane, 2026-11-13)

Preston: "Lets start upgrading camera to how we need for each creature we have right now and its things."
Numbers from the kit design and game feel lanes (2026-11-13; designs in docs/plan/moba-kits.md, built values in each
scripts/moba3d/<machine>_kit.gd, the code wins). Every number is a proposal or placeholder.

## Slice 1 (built 2026-11-13): framing by body size
chase_camera_3d.gd frames each machine by its drawn body (model top above the feet; roster height_cap as fallback):
the body fills 18% of the screen height for L machines, 16% for M, 14% for S (class from art/arena_models/roster.json),
feet held 71% down the screen (HUD bar from 82%), flat SMITE pitch 13. Measured 2026-11-13: camera 7.5 m back for
rhino, gorilla, bison; 8.0 hippo; 8.4 cobra, kangaroo; 7.3 pangolin (was 12 m for everyone). Check:
D:/dev/_scratch/camera-lane/profile_check.gd, 0 misses.

Size finding: in arena_play every body is drawn about 1.70 m tall whatever its class (hippo 1.83, pangolin 1.49 to
its plates), not the roster's 2.0 m L / 1.65 m M caps. Reported to the hub; the camera does not paper over it.

Side effect to solve in slice 2: closer means less ground behind the machine is on screen. A ring behind the machine
past about 3 m now falls below the bottom of the screen.

In match scenes (no `machine` var) the camera reads MatchTeams.machine_kind(target) instead.

## Slice 2 and on: what each kit needs from the camera
| Machine | Moment | Numbers | Camera need |
|---|---|---|---|
| Rhino | Tremor charge (ult) | run up to 16 m at 9-12 m/s, steering; finale ring 3.4 m+ | follow with a pull-back; shake on the finale; steep ult rule 55-60 deg |
| Rhino | Ground pound | 4 m circle, 5 stomps | pull-back to show the circle; shake per stomp |
| Rhino | Brace release | ring 3 m + 0.4 m a charge, up to 5 m | pull-back by ring size |
| Rhino | Heave / horn toss | 3.5 m dash, 2.2 m toss over its back | keep the landing behind in view |
| Gorilla | Chest beat (ult) | taunt and shields 5.5 m, dome 3.2 m | pull-back: the rear of 5.5 m sits under the HUD today |
| Gorilla | Fault Line | 6 m line along the aim | look ahead along the aim |
| Gorilla | Fling | grab 1.6 m, throw 4 m behind on a 1.5 m arc | keep the landing behind in view |
| Gorilla | Shield Drive | charge into a slam (length in the drive script) | follow |
| Hippo | Piston Drop | leap up to 8 m, peak 2.2 m, landing 3.2 m | follow the air time; landing shake |
| Hippo | Vent | 5.5 m cone; in the air a 2.6 m circle | look ahead along the cone |
| Hippo | Toxic Flood (ult) | 6 m lake, 4 s | pull-back |
| Bison | Eruption | four bombs on a 3.5 m ring | pull-back (rear landings under the HUD) |
| Bison | Freight (ult) | chains all near enemies, slow haul, slag trail | pull-back to show the line behind |
| Kangaroo | Hop and jab | leap up to 10 m at 22 m/s, 0.5 s air; 3 m hop | fast follow, no lag on the leap |
| Kangaroo | Tail kick | enemy launched 6 m | keep where they land in view |
| Kangaroo | Title bout (ult) | leap to an enemy within 8 m, 3 m ring, 4 beats, 60 deg slips round it | close-up that holds through the orbit |
| Pangolin | Iron ball roll | up to 3 s at 4-12 m/s, wall bounces, bent by magnets | follow (widest frames in the roster) |
| Pangolin | Scrap comet | 4 s at 6-9 m/s, about 34 m of path, shell 2.6x the ball | follow plus pull-back for the shell |
| Pangolin | Comet burst, Salvage | 4 m | pull-back by ring size |
| Cobra | Wall Line, Seam, Breach | walls 2.6-3 m; Breach 8 m/s for 0.69 s (5.5 m); Wall_Over 3 m/s for 2.78 s over a 2.6 m wall (8.3 m arc); Seam 2 s in a wall | keep the cobra readable in or behind a wall (fade or lift) |

## Proposed shape for slice 2 (nothing here is canon)
One camera call the kits make, `cam.hold(pull, seconds)`: pull back so a ring of the given radius fits above the HUD
bar, ease in, hold, ease out. Every pull-back row above is that one call with its own radius. Then a `follow_fast`
for leaps and dashes, and the cobra wall case last (it needs the map lane's fade).
