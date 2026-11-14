# Fennec blink flash (effect 3 of 5)

Built 2026-11-05 by the game feel lane's effects spin-off, after Preston picked it ("Blink flash"). The blink is
instant: the fennec leaves one spot and stands at another on the same frame. This is the light at both ends. The blink
gate (key 2) and its recast use it now; the 11-05 kit's pocket gates (jump through) will use the same pair. It is in
every version of the kit draft, so it was safe to build while the hub holds the ears ping and the big gate ring.

## Press play
- Arena (`scenes/moba3d/arena_play.tscn`), Tab to the fennec, then **2**: it blinks toward the mouse, the small gate
  opens where it stood, and the flash plays at both ends. Press **2** again within 3 s to snap back through the gate:
  the same flash, the other way.

## What it looks like
Two parts, 340 ms each, in the gate's palette and texel (0.016 m):
- **Out**, where it leaves: the fennec's own shape flashes white with a mint rim, squeezes to a shimmering sliver, turns
  into a slit of light with a star at chest height, and the star bursts into sparks and violet motes. A ring spreads
  on the floor.
- **In**, where it lands: motes pull in to a star, the star opens to a slit, the slit widens into the fennec's shape
  in white, and the shape fades to frosted mint over the body as sparks rise off it. A ring on the floor pulls in, then
  pulses out. The body stays hidden for the first 130 ms, so it appears out of the light, not before it.
- **The shape is the fennec's real frame.** The game draws whatever frame the sprite is showing in light, so it matches
  every view and pose, mirrored ones included. A first take used a plain column of light there; it read as a pill,
  not as the fennec.
- The camera follows the jump at once, so the end it left is the one that moves on screen.

## Files
| File | What |
|---|---|
| `blink_board.png` | Game pixels at 1x. Columns s, e, n; rows: before, blink frames 1, 2, 3 and 7, recast frames 1 and 3 |
| `blink_s_e_n.mp4` | The three views side by side, real time, 1x. Phone copy: `_phone.mp4`. The flash is 340 ms, so there is a quarter-speed copy: `_quarter_speed.mp4` |
| `blink_sheets_3x.png` | The drawn parts at 3x: slit, star, sparks, motes, and the floor rings |

Source and code:
- Art: `tools/art/draw_fennec_blink.py` writes `art/fx/moba3d/blink_flash/blink_sheet.png` (rows out and in, 6 frames,
  64 x 112 cells) and `blink_floor.png` (the rings, 72 x 72 cells).
- Effect: `scripts/moba3d/blink_flash.gd`. `play(parent, pos, OUT or IN, sprite)`: call OUT before the machine moves
  (its ghost is the body there) and IN after. The ghost is a quad on `tilted_fx_3d.gdshader` with its new tint, rim,
  fade and scan settings; they are off by default, so the gate and the bolt draw as before.
- Kit: `blink_gate()` and `gate_back()` in `scripts/moba3d/fennec_kit.gd` (the old impact puffs are gone).
- Check: `scripts/moba3d/gate_clip_test.gd --blink`, run from `arena_play.tscn -- --gate-clip-test --blink --out=<dir>`,
  not headless, 1280x720, `--fixed-fps 30`.

## Checked
In the game, at the game camera, 2026-11-05 (`gate_clip_test --blink`, 15 checks, 0 fail). From s, e and n it blinks
(2 m from s, 4 m from e and n) and recasts 1.2 s later:
- It blinked the full distance, and the recast put it back where it started.
- Each jump left a flash at both ends, with the fennec's ghost where it left.
- The body was hidden for 3 frames (130 ms) after each jump, then showed under the full-width ghost.
- Every flash and ghost was gone 10 frames (about 340 ms) after the recast, with the body showing.
- The shared shader changed, so the bolt clip, the gate clip and `blink_gate_check` were rerun (all 0 fail), and their
  frames were compared with the runs before the change: identical, pixel for pixel.

How it reads, frame by frame: e is clearest, with both ends on screen. From n the first blink's start is under the
screen's edge (the camera jumps with the fennec), but the recast shows that end. From s the start shows above the
fennec.

## Not done
- No sound.
- While the body is hidden, its shadow stays on the floor. It is 130 ms and under the light; if it shows, hiding
  the shadow too is a small change.
- Blinking toward the camera has the same limit as the bolt: about 3 m of floor show below the fennec, so the clip test
  blinks 2 m from the s view.
