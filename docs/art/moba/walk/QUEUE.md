# Walk queue (walk lane, 2026-11-06)

**STOPPED 2026-11-09.** Preston, via the hub: "2D sprites are scrapped btw". The machines are now 3D models, rigged
and animated (the gorilla-3d and rhino-3d sessions lead). No sprite walk work, no sprite jobs, no paid sprite runs.
Everything below is a record only: the lobster touch-up fix was cancelled, and lobster run 2 and the wolf runs will
never run. The tripod and trot timing in walk/tools/walk_tools.py (foot paths per gait) may still help a 3D walk.

Preston, 2026-11-06: "Start working on walk animations for mechs and angles that dont have one or need fixed".
Audited from `art/machines/*/*_frames.tres` and each mech's approved stills. Paid runs need his own yes, one at a time
across the team.

## In the game with a real 35-degree walk (all five views): nothing to fix in the art
| Mech | Walk | Open |
|---|---|---|
| rhino | touch-up rebuild, all five views (s and n packed 2026-11-05) | none |
| hippo | packed 2026-11-05 | the kit's full_speed_walk_rate = walk_speed / 0.48 (Hippo session) |
| gorilla (ape) | touch-up's 35 walk, packed | the 7.3x foot slide is a kit speed question (Gorilla session, game feel) |
| fennec | touch-up's trot with sway, all views | none |
| minion | packed | not checked this pass |

## Needs a walk
| # | Mech | Where it stands | Next step | Rough price |
|---|---|---|---|---|
| 1 | wolf | Free prep done (walk/wolf_m). Paid run parked by Preston, "Not now" (2026-11-05) | his yes for run 1 | 150k cap run 1, 110k run 2; likely 230k-270k, worst ~410k |
| 2 | lobster | Stand-in in game (glides). 35 stills approved 2026-11-06. Gait: tripod (Preston, 2026-11-06). Run 1 (e, se, ne) DONE 2026-11-06, 170,761 tokens; at the touch-up lane for a free fix (se R3, ne R1, ne far left legs) | recheck touch-up's frames, show Preston, then the Lobster session packs with pack_lobster_3d.py. Run 2 (s, n) needs his yes | run 2: 110k cap, worst ~185k |
| 3 | kangaroo | Stand-in in game (glides). Hop or walk is still Preston's call (MECH_STATUS item 4); a hop also needs game feel's hop switch | his call on hop, then prep | after the call |
| - | pangolin, shoebill, falcon, squirrel, chameleon | No approved 35-degree stills found, so nothing to draw a walk from yet | their mech sessions or the fleet redraw lane | - |
| - | hummingbird | Hovers, no walk (Preston, 2026-11-05) | none | - |

Paid slot (hub, 2026-11-06): the attack lane's rhino jab sheet 3 is running, the chameleon redraw is next, then the
walk run Preston picks. Start only when the hub says the slot is ours. Worst case for run 1: wolf about 225k, lobster
about 245k (cap plus about 75k).

## Lobster gait (Preston chose the tripod, 2026-11-06: "Tripod, 3 legs at once")
The 35 stills show three walking legs a side (stubby, red-tipped), the two big claws held forward with their tips on
the ground, and a rigid tail. Proposal: an alternating tripod, the six-legged gait. Tripod A (L1, R2, L3) is planted f0-f3
and tripod B (R1, L2, R3) f4-f7, with lifts 2, 3, 3, 2. The claws and tail ride with the body, dipping 1 px as each tripod
lands. Size L timing: 8 fps, P 3 (0.48 m/s, like the rhino and hippo). Alternative: a four-beat wave, one leg at a time
front to back (slower, reads as creeping).

## Not verified this pass
- The kangaroo's accepted stills: no APPROVED.txt under a cam35 folder was found.
- The cam35_fleet lane's state for pangolin, shoebill, falcon, squirrel and chameleon.
- The minion walk.
