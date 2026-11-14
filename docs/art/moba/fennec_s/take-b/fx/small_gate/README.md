# Fennec small gate (effect 1 of 5)

Built 2026-11-05 by the game feel lane's effects spin-off. The first of the five effects the fennec's kit needs (small
gate, big gate ring, bolt, blink flash, arrival shield). It came first because it is the one piece abilities 1, 2 and 3
all reuse, and because it stands on the floor, so it reads from the back views where the cast pose only lifts the ears.

## Press play
- Arena (`scenes/moba3d/arena_play.tscn`), Tab to the fennec, then **5**: the fennec turns to the mouse, plays the
  35-degree cast, and on cast f3 (260 ms) the gate opens 1.1 m behind it, holds 0.8 s and closes. Key 5 is a preview
  that sits outside the four match slots until the new kit's abilities replace the old ones. Since the bolt landed
  (`../bolt/`), key 5 is the whole two-faced shot: a bolt forward and the gate behind, then a bolt back out of the gate.
  The gate alone is `FennecKit.gate_cast()`, which the gate clip test plays.
- **2** (blink gate) now leaves this gate instead of the old cyan ring. It holds for the 3 s recast window and closes
  on the recast or when the window runs out.

## What it looks like
A doorway of the fennec's own mint glow between two short violet posts with gold bands, with a turning swirl of its
violets inside and a ring on the floor. Only the fennec's palette is used, with its #141218 ink round the outside, at
its texel size (0.016 m), so the gate's pixels are the same size as the body's.
- Open, 400 ms: the posts rise, a line of light climbs between them, the oval swings open past full size and settles.
- Hold, looped at 100 ms a frame: the swirl turns, a highlight runs round the rim, the lamps pulse and sparks rise.
- Close, 400 ms: it narrows to a line, pinches to a star, the sparks burst and the posts sink.
- The doorway faces the camera from every side, on the same tilted quad as the machines. Its swirl is part
  see-through, so from the n view, where it opens between the camera and the fennec, the body still shows through.

## Files
| File | What |
|---|---|
| `small_gate_board.png` | Rows s, e, n at the game camera; columns: still, cast f3 (spawn), opening, open, closing, after |
| `small_gate_s_e_n.mp4` | The three views side by side, real time, 2x. Phone copy: `_phone.mp4`. Slow copy: `_half_speed.mp4` |
| `gate_strip_3x.png`, `gate_preview_3x.gif` | All 18 frames as drawn, before the game camera |

Source and code:
- Art: `tools/art/draw_fennec_gate.py` writes `art/fx/moba3d/small_gate/door_fNN.png` and `floor_fNN.png` (18 each).
- Effect: `scripts/moba3d/small_gate.gd` (`SmallGate.open_at(parent, pos, hold)`, `close()`, signals `opened` and
  `closing`) on `scripts/moba3d/tilted_fx_3d.gdshader`.
- Kit: `FennecKit.gate_cast()` (key 5) and the blink gate's marker in `scripts/moba3d/fennec_kit.gd`.
- Check: `scripts/moba3d/gate_clip_test.gd`, run from `arena_play.tscn -- --gate-clip-test --out=<dir>`, not headless,
  1280x720, `--fixed-fps 30`.

## Placeholders, not balance
Gate 1.1 m behind the fennec, held 0.8 s; the doorway is 0.67 m wide and 1.28 m tall, and the floor ring 1.4 m across.
The open and close timings are art timings. All of these are Preston's to change.
