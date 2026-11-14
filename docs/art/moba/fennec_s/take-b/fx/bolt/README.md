# Fennec bolt (effect 2 of 5)

Built 2026-11-05 by the game feel lane's effects spin-off, after Preston picked it ("Draw the bolt"). The bolt is the
shot of the 11-05 kit's first ability, the two-faced shot: one bolt forward from the fennec and one backward out of the
small gate (`../small_gate/`). It is in every version of the kit draft, so it was safe to build while the hub holds the
ears ping and the big gate ring.

## Press play
- Arena (`scenes/moba3d/arena_play.tscn`), Tab to the fennec, then **5**: the fennec turns to the mouse and plays the
  cast. On cast f3 (260 ms) a bolt leaves forward and the small gate opens 1.1 m behind. When the gate finishes opening
  (400 ms later) a second bolt flies backward out of its middle. Each bolt stops at the first enemy in its line, hits it
  and slows it. Training dummies count as enemies outside a match.
- Key 5 is still a preview outside the four match slots. It plays no sound of its own yet: slot 1's sounds are the old
  sand kick's, which the kit no longer uses.

## What it looks like
A comet of the gate's energy: a mint head with a white core, a soft mint glow one texel round it, and a violet ribbon
for a tail with a lilac line down the middle. A white pulse runs down the tail every 200 ms (4 frames, 50 ms each), and
two sparks peel off it. It leaves a dotted line of sparks every 0.2 m. Same palette, ink and texel (0.016 m) as the
fennec and its gate.
- Flash where it leaves (210 ms): a white star, a ring, four sparks.
- Impact where it stops (330 ms): a star, a violet core in a mint ring, the ring breaking into six arcs, sparks.
- The sprite faces the camera on the same tilted quad as the gate. It is drawn at 16 screen angles, and the game shows
  the one nearest its flight on screen, so it points the way it flies from every view, toward the camera included.

**Second take.** The first drawing was 7 texels wide with a dark violet tail. At the game camera it read as a thin line,
and the floor's blue swallowed the tail. This take is about 10 texels wide, has the glow, a lighter tail and a pulse
you can see, and the flash and impact are about 1.3x bigger. `bolt_take1_vs_take2.png` shows both, drawn and in game.

## Files
| File | What |
|---|---|
| `bolt_board.png` | Game pixels at 1x. Columns s, e, n; rows: cast f3 (forward bolt out, gate starts), forward bolt in flight, it strikes, gate open (backward bolt out), backward bolt in flight, it strikes. The bolt toward the camera (forward in s, backward in n) has no dummy and is shown flying off the bottom of the screen |
| `bolt_sheets_4x.png` | As drawn, 4x: the 16 angles, the 4 frames, the bursts |
| `bolt_take1_vs_take2.png` | The first drawing next to this one, at 4x and in game |
| `bolt_s_e_n.mp4` | The three views side by side, real time, 1x. Phone copy: `_phone.mp4`. Slow copy: `_half_speed.mp4` |

Source and code:
- Art: `tools/art/draw_fennec_bolt.py` writes `art/fx/moba3d/fennec_bolt/bolt_sheet.png` (4 frames x 16 angles, 40
  texel cells) and `burst_sheet.png` (flash, impact, trail spark).
- Effect: `scripts/moba3d/fennec_bolt.gd`. `fire(parent, from, direction, targets, speed, reach)` flies level and stops
  at the first target within 0.2 m of its line (plus the target's own radius), at a wall, or at its reach. It deals
  nothing itself: its `struck` signal tells the kit what it hit. One shared material, sheet cells set per instance
  (`uv_rect` in `scripts/moba3d/tilted_fx_3d.gdshader`).
- Kit: `FennecKit.two_faced_shot()` (key 5) and `_bolt()` in `scripts/moba3d/fennec_kit.gd`. The kit does the hit and
  the slow.
- Check: `scripts/moba3d/gate_clip_test.gd --shot`, run from `arena_play.tscn -- --gate-clip-test --shot --out=<dir>`,
  not headless, 1280x720, `--fixed-fps 30`. A dummy stands in each bolt's path, except the bolt toward the camera.

## Placeholders, not balance
Speed 12 m/s, reach 7 m, hit width 0.2 m either side, slow 1.5 s. The forward bolt leaves 0.35 m ahead and 0.45 m up;
the backward one leaves from the middle of the doorway, 0.7 m up. All are exports on the kit or constants in the bolt.

## Checked
In the game, at the game camera, 2026-11-05 (`gate_clip_test --shot`, 18 checks, 0 fail):
- s, e and n: the forward bolt and the gate come on cast f3, 8 game frames after the key (the same frame as the gate
  alone). The backward bolt leaves on the frame the gate finishes opening, 12 frames (400 ms) later.
- Every bolt with a dummy in its path stopped at it ("target") and the dummy was slowed: both in e, the backward one in s,
  the forward one in n. The bolt toward the camera in s and n flew its whole 7 m ("reach").
- Both bolts and the gate were gone 1.9 s after the key (57 frames), and the cast went back to idle.
- After the shared shader and the gate changed for the bolt, the gate alone was checked again (`gate_clip_test`, 0 fail)
  and so was the blink gate (`tools/debug/blink_gate_check.gd`, 0 fail).

How it reads, looked at frame by frame:
- e reads best: both bolts cross the screen, with the spark trail and the strike star at each dummy.
- n: the forward bolt climbs away over the ears; the backward one comes out of the gate's face toward the camera, the
  clearest frame of the set (white core, violet tail up).
- s: the forward bolt drops past the fennec's feet and off the screen. The backward bolt leaves through the gate's far
  side, so for about 4 frames (0.13 s) it is inside the swirl, then shows above the gate on its way to the dummy.

## Not done
- No sound. The kit's audio still points at the old abilities.
- No damage numbers: the kit calls the dummy's `hit()` and `slow()`, which are what the dummy has.
- The gate's opening sets the backward bolt's timing (400 ms after the forward one). If the shot should feel quicker,
  the gate's open frames are the place to change it, not the bolt.
- Shooting toward the camera (the s view) leaves little screen: the chase camera keeps the fennec above the middle, so
  a target more than about 3 m toward the camera stands under the screen's bottom edge. That is the camera's framing,
  not the bolt's, and it is for the game feel lane to weigh.
