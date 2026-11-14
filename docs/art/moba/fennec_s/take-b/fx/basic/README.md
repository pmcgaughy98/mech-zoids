# Fennec basic attack: the dart

Built 2026-11-05 by the Fennec session, from Preston's request relayed by the game feel lane: "we need basic attacks.
Rhino, gorilla will be melee." The fennec's is ranged: a small violet dart of gate light.

## How it plays
- **Hook:** `fennec_kit.gd` `basic_attack(target) -> bool`, which the match director calls. It refuses (false) while
  any move is running, so a press during the swing does nothing.
- **Numbers:** range 6 m (`basic_range`), every 0.9 s (`basic_cooldown`), 30 damage, sent as
  `target.hit(player, 30 / MatchRules.kit_hit_damage)` = 0.5 of a kit hit. Dart speed 14 m/s; it flies 1.2 m past the
  range before it fades.
- **Swing:** on the press the body shows cast frame 2 (the ears flash). 0.06 s later it shows cast frame 4 and the dart
  leaves. 0.15 s after that the fennec is free (6 frames at 30 fps from the press).
- **The dart:** half the bolt's size, violet with a mint-white core, no line of sparks behind it
  (`fennec_bolt.gd` dart mode, `art/fx/moba3d/fennec_bolt/dart_sheet.png`, 16 screen angles x 4 frames).
- **The hit:** a small violet burst on the target (`dart_hit_sheet.png`, 5 frames, 250 ms): star, ring, shards. It is
  the bolt impact's shape at two thirds the size, so the basic never looks like the ability. It sits part way into
  the target and is nudged 0.4 m toward the camera, so a dart flying at the camera doesn't end hidden behind the body.
  A dart that runs out or meets a wall only sparks.
- **Sound:** `cue("basic_cast")` on the press and `cue("basic_hit")` on the strike. The sound lane wired them into
  `kit_audio.gd` (placeholder option A: "Glass tick" and "Crystal spark").
- **Feel:** no hitstop or screen shake. It's a ranged poke every 0.9 s, so the hit burst and sound carry it.

## Files
| File | What |
|---|---|
| `basic_board.png` | Game pixels at 1x. Columns: the views s (dummy 2.5 m away), e and n (4.5 m). Rows: press, release, flight, hits and bursts, idle. A gold frame marks the hit frame |
| `basic_hit_2x.png` | The hit frames at 2x, all three views |
| `basic_dart_4x.png` | The dart sheet at 4x (4 of its 16 angles, all 4 frames) |
| `basic_clip.mp4` | s, e and n side by side, real time, two presses 0.9 s apart. Also `_half_speed` and `_2x` (pixels doubled) |

Source: `tools/art/draw_fennec_bolt.py` draws `dart_sheet.png` and `dart_hit_sheet.png` and leaves the bolt's sheets
byte for byte as they were. The board and clips come from `D:/dev/_scratch/game_feel/gate/make_basic_board.py`.

## Checked
In game at the game camera, 2026-11-05: `gate_clip_test --basic` (arena_play, not headless, 1280x720, `--fixed-fps 30`),
30 checks, 0 fail. In each of s, e and n, two presses 27 frames (0.9 s) apart:
- The dart left 1 frame after the press.
- It struck the dummy ("target") at 2.5 m (s) and 4.5 m (e, n).
- The hit burst showed on the strike frame.
- The fennec was free 6 frames after the press.
- Each hit carried scale 0.5.
- A second press during the swing was refused.

Also run the same day: `kit_api_check` 0 failures, `match_check` 67 pass 0 fail, and the shot clip (the bolt) 18/18,
unchanged.

## Not done
- **Body frames:** it borrows the cast pose. The attack lane will draw a dedicated `basic` animation (a small ear
  flick, no lunge). It's third in that lane's queue, a paid job (about 50k-120k tokens, 230k worst case), and runs only
  on Preston's yes.
- **The dummy doesn't react** to any hit (no flash or shake). That's the shared training dummy, not the fennec.
- **Toward the camera** only about 3 m of floor shows below the fennec, so a dart fired that way leaves the screen
  early (camera lane's framing).
