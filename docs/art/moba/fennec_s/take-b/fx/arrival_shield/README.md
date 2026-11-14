# Fennec arrival shield (effect 4 of 5)

Built 2026-11-05 by the game feel lane's effects spin-off, after Preston picked it ("Arrival shield"). The great gate
(slot 4) carries the team to its far gate, every ally "arriving with a short shield and a burst of speed"
(`docs/plan/moba-kits.md`). This is that arrival, on any machine. The great gate itself (its charge, its ring and the
carry) is on the hub's hold, so nothing in the kit plays this yet; the clip test puts it on the machines directly.

## What it looks like
- **The shell:** a bell of the gate's violet light standing on the floor round the machine, with a mint glint and a
  bubble highlight at its top left and a ring on the floor under it. It rises up both sides from the floor, closes at
  the top with a star (310 ms), then holds with a band of light rising through it every 640 ms.
- **When it runs out:** it flickers, its edge breaks into dashes and the dashes drift up as motes (300 ms).
- **When a hit takes it:** it cracks across like glass, and the pieces fly out, drop a little and fade (250 ms).
- **The speed burst:** while it lasts and the machine moves, mint afterimages of the machine's own frame are left behind
  it every 0.065 s, each fading in 0.4 s. They start hidden behind the body and show as it walks on.
- **Not the gorilla's shield.** The hex shield is a green sphere of hexagons. This is violet and smooth, drawn in pixels
  on the machine's own plane, and sits on the floor like a bell.
- **It fits every machine at its own texel.** Two sizes, measured over every frame of the sheets: `s` for the S and M
  machines (the fennec's tallest frame is 83 texels, the shell 93), `l` for the L ones (the rhino's horn toss is 107,
  the shell 111). Each is laid on at the wearer's texel (S 0.016 m, M 0.018, L 0.020), so it is as crisp as the
  machine inside it.

## Files
| File | What |
|---|---|
| `arrival_board.png` | Game pixels at 1x. Columns: the fennec from s, e and n, the rhino from s and e. Rows: before, rising, closing, walking with afterimages, holding, expiring, cracking, shattering |
| `arrival_clip.mp4` | The five side by side, real time, 1x. Phone copy: `_phone.mp4`; half speed: `_half_speed.mp4` |
| `arrival_sheets_3x.png` | The drawn parts at 3x, and the shell round the fennec's and the rhino's widest and tallest frames |

Source and code:
- Art: `tools/art/draw_fennec_arrival_shield.py` writes `art/fx/moba3d/arrival_shield/arrival_shield_s.png` and
  `_l.png` (rows form, hold, expire, break; 8 columns) and `arrival_floor_s.png` and `_l.png` (the ring).
- Effect: `scripts/moba3d/arrival_shield.gd`. `play(machine, life, speed_life)` puts it on a machine (a new one replaces
  an old one); `on(machine)` finds it; `hit()` shatters it; `end()` fades it early; `ended(why)` fires when the shell is
  gone. The afterimages keep going after a break until the speed burst ends.
- Check: `scripts/moba3d/gate_clip_test.gd --arrival`, run from `arena_play.tscn -- --gate-clip-test --arrival
  --out=<dir>`, not headless, 1280x720, `--fixed-fps 30`.

## Checked
In the game, at the game camera, 2026-11-05 (`gate_clip_test --arrival`, 35 checks, 0 fail). The fennec from s, e and
n, then the rhino from s and e. Each arrives, walks 1 s in a test speed burst, stands until the shield runs out at 2 s,
then arrives again in place and is hit 1 s later:
- The shield was the right size for the machine (`s` on the fennec at 0.016 m, `l` on the rhino at 0.020 m).
- It had formed and was holding 10 frames (330 ms) after the arrival.
- Walking in the burst it left 14 afterimages, up to 6 showing at once, and none once the burst was over.
- It expired on time (gone at clip frame 74, 2.3 s after the arrival).
- The hit shattered the second one, gone 7 frames (230 ms) later.
- Nothing was left after (no shield, no afterimages), the body was showing and the speed was back to normal.

How it reads, frame by frame: the e views show the speed best, with the afterimages streaming out behind; the rhino's
is long and clear, since it walks faster. From s the afterimages show above and round the body. From n (walking away)
they are between the camera and the body, so for 0.4 s they lie over its back in mint. The wide blue ring on the floor
is the arena's own ring under the machine; the shield's floor ring is the thin lilac one inside it.

## Not done, and not mine to set
- The numbers: how much it absorbs, how long it lasts (2 s here), how fast the burst is and for how long (1.2 s of
  afterimages here; the test walks at x1.5 on `speed_mult`). They belong to the great gate when it is built.
- Nothing hits it yet: whatever deals damage to a shielded machine calls `hit()`.
- No sound.
