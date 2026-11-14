# Area barrage ultimates: references for the falcon's sky barrage (2026-11-05)

Falcon session, pass 1. The art is in `docs/art/moba/falcon_m/vfx/sky_barrage/`: `board.png`, the two GIFs and
`metrics.json`. All of it was drawn by `build_sky_barrage.py` in that folder.

## What was read
- **Read: League of Legends wiki, Gangplank, Cannon Barrage (R).** Firecrawl, 2026-11-05, as an extracted answer
  (not checked by hand).
  - Global range. Radius 580, with an inner radius of 170. Lasts 8 s.
  - 12 waves in clusters of 3. A cluster lands every 2 s, and the waves within a cluster land 0.25 s apart.
  - Slows 30% for 0.5 s and grants sight of the area. Cast time 0.25 s.
- **Read: same wiki, Miss Fortune, Make It Rain (E).**
  - Range 1000. Radius 350. Lasts 2 s, with damage every 0.25 s (8 ticks).
  - Slows 40% and grants sight. Champion gameplay radius 65.
- **Read: the camera lane's `scripts/moba3d/ult_view_test.gd`.**
  - Placeholder darts: 14 a second at 24 m/s, each a 0.08 x 0.7 m box.
  - Impact flash: 0.3 s at a 0.55 m radius.
  - The falcon circles 6 m out and 12 m up.
- **Measured: the falcon's approved stills (take-b).**
  - 16 colours: crimson ff6a72 e01e3c 9c0f26 520716, ivory ece6d6 b8ae98, steel c9c8cf 8a8892 3d3a44, frame
    211e27 141218, yellow ffe680 ffc21a c4820a, green 6aff6a, white ffffff.
  - Front width 50 px, so the body radius is 0.5 m at 50 texels per metre.
- **General knowledge, not read:**
  - Area rain abilities in other MOBAs show the area before the first hit, and scatter the hits at random points inside it.
  - Pixel-art hit effects in GBA-era games run about 6 to 10 frames.

## The structure they share
1. The area is shown before anything lands.
2. Hits land on a fixed beat: 0.25 s in both games.
3. Each hit lands at a random spot inside the area, and its effect is small, so the area stays readable.
4. The caster gets sight of the area.

Measured as ratios:
- Area radius over body radius: 350 / 65 = 5.4 and 580 / 65 = 8.9.
- Hits per beat: 1 for Miss Fortune, 3 for Gangplank.

## Synthesis proposal (nothing here is canon)
- **Timing:**
  - The ring opens in 0.2 s, and the first darts land 0.6 s after that.
  - Then a cluster of 3 or 4 darts lands every 0.25 s, about 14 a second.
  - Each hit lasts 0.27 s, so it is gone before the next beat at the same spot.
- **Size:** 3.5 m radius, which is 7 falcon body radii (the references span 5.4 to 8.9).
- **Look:** falcon colours only, so the effect reads as the falcon's.
  - **Dart:** white-hot tip, steel point, ivory quill, crimson fletching, crimson speed trail. 0.78 m long with its trail.
  - **Impact:** a white flash, a yellow burst, two feather bits flung up, and the dart left stuck in the ground for a
    moment. Under it, an ivory dust ring 0.82 m wide.
  - **Ring:** dashed crimson, with eight ivory chevrons pointing in, for keen sight.
- **Alternatives:**
  - (a) Draw the ring in the casting team's colour instead of the falcon's crimson. That is clearer for enemies,
    because teams are red and blue.
  - (b) Use Gangplank-style heavy clusters instead of a steady drizzle. That means fewer, bigger hits with gaps to
    dodge through.
  - (c) Show the falcon's shadow sweeping around the ring while it circles.
- **Open, and Preston's call:** duration, damage, whether the darts slow (both references slow), and the ring's colour.

## First slice from here
Give the pieces to the camera lane, so it can swap the placeholder boxes in its ult test. Then look at it in the real
game view at 55 to 60 degrees.

Headless check: count darts landing per second and the gap between clusters in a run of the test. Targets: 14 a
second and 0.25 s.

## Tools, pass 1
- **Firecrawl:** two wiki reads (10 credits) gave the timing and size targets.
- **Python and PIL:** drew every pixel, simulated the barrage at both cameras, built the GIFs and the board, and
  scored 11 checks: 10 pass, 1 is info only.
- **PixelLab VFX workbench (free):** I read its guide but did not draw with it. Its parts are its own drawings and
  save to the PixelLab account. Drawing in code kept every pixel in the falcon's 16 colours and made it all
  measurable. It is worth trying next for a second take on the impact.
- **PixelLab pixel-art workbench (second scorer):** not run this pass. It needs an upload round trip.
- **Not used:**
  - The Aseprite connection failed.
  - Godot: the ult test is the camera lane's file, and only one Godot runs at a time.
  - Director's Lookbook: the palette is the falcon's own.
  - Retro Game Gather and the `watch` skill: the wiki numbers covered timing, and video frames are costly.

## What still falls short
- **Not seen in the real game view yet.** The mock is orthographic and uses a guessed floor colour (4a5048),
  because the camera lane's rendered frames were not found on disk.
- **Trail contrast:** the trail is only 0.24 brighter than that floor, against 0.69 for the tip.
- **The machines in the mock are not re-angled:** they are approved stills.
- **Darts that travel up the screen** use a vertically flipped sprite, so their light falls on the wrong side.
- **In the still board frame, the hits are small.** They read better in motion, in the GIFs.
