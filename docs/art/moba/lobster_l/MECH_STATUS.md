# Lobster (`lobster_l`): mech status

Lobster session, stock-take 2026-11-05. Nothing built, nothing spent.

## What exists
- **Approved take: `take-g/`** (APPROVED.txt, Preston 2026-11-05: "take-g is the current lobster").
  - It came from C, then E (back views lowered), then F (white tail spikes removed), then G (86 pixels touched by hand in Aseprite).
  - Takes a to f are history. Only one take is approved, so there is no conflict to ask about.
- **Eight views** in `take-g/views/`. Canvas 192, feet row 160, 12 to 14 colours.
  - Body sizes (W x H): s 89x66, se/sw 114x63, e/w 124x55, ne/nw 112x65, n 81x66.
- **Camera:** the approved take-g views are the old low angle (about 6 degrees). **The 35-degree stills now exist:** `take-g/views_cam35/` (s, se, e, ne, n), accepted 2026-11-06. See Now below.
  - The lobster is not one of the fleet redraw lane's 11 machines (`cam35_fleet/HANDOFF.md`). That list was written before the lobster was approved.
- **Animations: none drawn yet.** The walk lane and the attack lane have both queued the lobster (2026-11-06).
- **In the game: no (as of the stock-take; see Now below).** There is no `art/machines/lobster*` folder and no `_frames.tres`. `match_director.gd`, `kit_feel.gd` and `kit_audio.gd` don't mention it.
- **Known weak spot: the side views are short.** e and w are 55 px tall, against 66 for s (0.83). sheet_judge still says REDO e, w. The side views were kept from take C, so F and G never fixed them.

## What the kit doc leaves open
- **Slot 4 is still Preston's call.** It is either shell guard (support: a shield on an ally that pops and knocks enemies away) or undertow (catcher: drags every enemy in an area to its centre).
- **No numbers yet.** The cooldowns are words. Nothing sets the pull range, the root time, the shield amount, the molt health threshold or the tail-flip distance.
- **Molt as a pose or an effect** is undecided.
  - A pose (shell-less body) is a real redraw: new art, probably paid.
  - An effect (shell pieces flying off, a speed shimmer) is cheaper.
- **The art list** still to make: claw shot and cable (effect), pinch, tail flip, shell guard (effect), molt.
- **Basic attack (asked by the game feel lane, 2026-11-05):** not built. The kit doc doesn't say melee or ranged.
  - Proposal: melee, a short snap of the big claw. basic_range 2.0 m, basic_cooldown 1.1 s, 40 damage (the stand-in does 30 every 0.9 s at 6 m).
  - Preston decides. It gets built with the kit once the lobster has game frames.
- **The cable has no plan yet.** It could be a pixel strip sprite or a line drawn in the engine. The second option needs the game feel lane.

## What has to happen before it plays
These steps go in order:
1. 35-degree stills.
2. Install in 192 cells (`_frames.tres` with `tilt_anims`). The lobster session does this itself (game feel lane, 2026-11-05): `art/machines/lobster/lobster_frames.tres` with anims named `<action>_<view>` and the `tilt_anims` meta, a kit script whose static `install(p)` sets frames, canvas, `feet_edge_row` and size class (FennecKit and KangarooKit are the pattern), a frames check, then the game feel lane adds the match lines. The walk lane says how it splits walk work.
3. The walk (walk lane).
4. The kit code (game feel lane).
5. Attacks and VFX.

## Now (2026-11-05)
- **Slice 1 (the 35-degree redraw) ran on 2026-11-05: 70,525 tokens, one image.**
  - The views are in `take-g/views_cam35/` and the board is `take-g/cam35/board_cam35.png`.
  - Near pass. The side view is fixed. s, se and n look down more steeply than e.
  - Turn test: the measure was withdrawn. By eye, from a contact sheet of the clip, no pop is visible. The HP bar needs at least 2.3 m. **ACCEPTED by Preston 2026-11-06 ("Accept them").** Next: install in game (free). Detail: `take-g/cam35/LANE_REPORT.md`.

- **Installed (2026-11-06, Preston: "Yes, install it"):**
  - The frames: `art/machines/lobster/lobster_frames.tres` and `lobster_sheet.png`, from `tools/art/pack_lobster_3d.py`.
  - The kit: `scripts/moba3d/lobster_kit.gd`, size L, canvas 192, feet edge 161.
  - The check: `tools/debug/lobster_frames_check.gd` passes 47/47.
  - Not in the match yet: the game feel lane is adding the match lines.
  - The feet meta is an art estimate; the camera lane has been asked to measure it.
  - The game feel lane added the match lines (`match_director.gd`, by path).
  - **Basic attack built (2026-11-06, "Melee claw snap"):** 2 m, 40 damage, every 1.1 s.
    - It lunges on the still until the attack lane draws a snap.
    - Cues `basic_snap` and `basic_whiff` have been asked of the sound lane.
    - The check is `tools/debug/lobster_basic_check.gd`.
  - Still missing: abilities and a walk (it glides on the still).
  - **Walk:**
    - Preston picked the tripod gait ("Tripod, 3 legs at once"), at 8 fps and 0.48 m/s on the ground.
    - The walk lane's prep is done in `docs/art/moba/walk/lobster_l/`.
    - It's paid: likely 250k to 320k tokens, worst case about 430k, and waits on his yes.
    - Run 1 (e, se, ne) is done, 170,761 tokens (walk lane, 2026-11-06).
      - The side view is good.
      - The se rear near leg (R3) and the ne front near leg (R1) break into shards in most frames.
      - Preston chose the free fix ("Touch up free", 2026-11-06). The touch-up lane is rebuilding se R3 and ne R1 as whole
        legs and giving the ne far left legs the tripod step; e is copied unchanged. Output: `touchup/lobster_l_walk/frames`.
        Then the walk lane rechecks it and puts it to Preston. Review: `docs/art/moba/walk/lobster_l/run1/REVIEW.txt`. Nothing to pack yet.
    - When the frames come back: repack, then set `full_speed_walk_rate = walk_speed / 0.48` in LobsterKit.
  - **Playable (game feel lane, 2026-11-06):**
    - In a match, Tab 6 times from the rhino to reach the lobster. Space or left click snaps; keys 1 to 4 do nothing yet.
    - No bot uses it until Preston names a roster slot.
  - **When abilities come:**
    - Add `var current := ""` to LobsterKit, or bots never use them.
    - Send the game feel lane the cooldown tier words for its TIERS row (without one, any slot falls back on medium, 9 s).
  - **Drawn claw snap:** queued in the attack lane, 50k to 105k tokens, worst case 345k, on his yes.

## Next slices (Preston picks one)
1. **35-degree redraw of the five views, with the short side view fixed in the same image.** PAID: one Codex image.
   - **Cost:** expect 60k to 80k tokens. The hippo, the closest long body, took 71,498. The worst case is about 175k if a 100k cap overshoots. A second image happens only on his yes.
   - **Method:** the fleet recipe (`cam35_fleet/prep_machine.py`, the gorilla take-2 brief changes), plus its long-body lessons:
     - se drawn as tall as the guide says;
     - a line giving how many times longer the side view is than the front is wide.
   - **Checks:** `fleet_board.py` gives a board and `verify.txt`. Then the game feel lane runs the turn test.
   - **Before it runs:** it needs the hub's paid slot.
   - **Why first:** everything that makes the lobster playable waits on it.
2. **Slot 4 and numbers board.** FREE (a few Firecrawl searches).
   - It puts shell guard and undertow side by side, with how 2 or 3 shipped MOBAs build a hook-plus-protect support (structure only).
   - It adds draft numbers labelled as proposals: pull range, cooldowns in seconds, root time, shield amount, molt threshold.
   - This is a decision page. It doesn't change the game.
3. **Claw-and-cable VFX test sheet.** FREE.
   - It is a synthesis pass: study hook effects in shipped games, then draw by hand in the lobster's palette. The tools would be the free PixelLab pixel tools (vfx_workbench) or a Python script.
   - The frames: the claw in flight, the cable strip, the clamp flash, the drag dust. They go on a board beside the approved views.
   - It isn't in the game until the lobster is, and it reads best after slice 1.

My pick: slice 1, because it unblocks everything else. Slice 2 is free and can run alongside it, since Preston only has to read and choose.

## Notes
- The roster file the hub named, `docs/team/mech-sessions-2026-11-05.md`, is not in the main checkout.
- The lane owners are listed in the hub's brief. The fleet redraw lane owns the cam35 recipe. If slice 1 goes ahead, tell it and the hub before the run.
