# Shoebill (`shoebill_m`): status, 2026-11-05

Owner: the Shoebill session. Stock-take only; nothing built or spent.
Copied here from the shared notes folder on 2026-11-05 on Preston's okay. This is now the main copy.

## What exists
- **Approved take: E** (`take-e/views/`, all eight views, "Keep E", 2026-11-03, approved as drawn).
  - `take-c/` also has an APPROVED.txt, but take E's note says it replaces C (C carried Thoth's look). E is current.
  - Sizes about 58 to 96 px wide and 78 to 82 px tall. M class, so 0.018 m per texel in the 3D world.
  - Known flaws, all accepted at approval:
    - the back views' wings flare like a cape (front/back 0.63; the check wants 0.80);
    - from the front, the bill is 0.93 of the head width, not wider than the head;
    - the top five colours cover 57% of the body (the check wants 65%);
    - neck rings and toes blur at game size.
  - Size option B leaves it standing at tank height (ROSTER.md).
- **Remaster of the stills (sel-out, capped ink):** not done. The shoebill is not on the remaster list.
- **35-degree stills:** none. Seven others have them: rhino, gorilla, hippo, kangaroo, wolf, fennec, drone.
- **Animations for the MOBA:** none drawn.
- **In the match:** no. Nothing in `scripts/moba3d/` names it; only rhino, gorilla and fennec have kit scripts.
- **Kit in code (2026-11-05):** `scripts/moba3d/shoebill_kit.gd` has moon phases (patience), moonbeam and the lens
  flick basic attack, on a stand-in body. Try it in `scenes/moba3d/shoebill_field_test.tscn`. Check:
  `tools/debug/shoebill_kit_check.gd`. Not in the match yet.
- **Watch out:** `art/machines/shoebill_m/` is the **old October design**, not take E.
  - It holds 8 views from `docs/art/2d/shoebill_m/p96_detail` and the old RPG moves: idle, clamp, lance, buffet, hit, death.
  - Its hashes differ from take E. It has no `_frames.tres` and no `tilt_anims`.
  - The old battle scripts use it (`machines.gd`, `machine_views.gd`, `view_lab.gd`). Leave it alone. Don't pack the MOBA shoebill from it.

## What the kit doc leaves open
The kit section is in `docs/plan/moba-kits.md`.
- **No names or numbers.** Every slot has a plain label only. Cooldowns are tiers. Nothing sets damage, range, root time or slow strength.
- **The theme question.** The kit predates the 2026-11-04 rule: the animal gives the body plus one trait, and a
  power theme gives the rest.
  - Today all five parts are animal: stillness, bill clatter, marsh, wing hop and lunge.
  - Answered by the kit pass (2026-11-05): `docs/plan/shoebill-kit-2026-11-05.md`.
  - **Preston picked Version B, Thoth's moon (2026-11-05).** The paste-ready section is at the end of that file. It
    goes into `moba-kits.md` on the hub's go (the squirrel session edits that file first).
  - The rework file (`fennec-janus-kit-2026-11-04.md`) proposes Thoth's moon: a moonlight beam, and the line
    strike as a light lance. Preston has not picked it.
- **Patience (passive):** how long it takes to reach the cap, whether any step resets it, and how the player sees the charge.
- **Marsh patch:** how many at once, how long it lasts, and who can see it.
- **Lunge strike:** is it the body lunging forward, or a strike thrown down the line from where it stands?
- **Art it lists, none drawn:** the clatter, the wing hop, the wind-up and lunge, the marsh patch effect and the line strike effect.

## Next slices (Preston picks)
1. **Kit pass. Free, one short session.** Done 2026-11-05: Version B, the moon, picked and in `moba-kits.md`.
   - Write a real proposal with names, numbers and timings for him to edit.
   - Give two versions: the current animal kit made concrete, and a Thoth moon version (the trait kept: patience or the lunge).
   - Nothing is built until he picks.
2. **35-degree stills of take E. Paid (Codex), one image.**
   - Same recipe as the wolf and kangaroo: one sheet, then free finishing (defringe, despeckle, audit) and a review board.
   - Past runs used 55k to 78k tokens. Cap 100k. Worst case about 175k with the known overshoot.
   - Needs the hub's free paid slot and Preston's yes. Same design: the cape wings and bill stay unless he says otherwise.
   - Tell the touch-up lane before the touch-up finish.
3. **Stand it in the match. Free. Needs slice 2.**
   - A 35-degree idle (breath built from the stills, like the rhino's), packed with `tilt_anims = ["idle"]`.
   - Placed in the arena with no kit yet.
   - The packing and arena hooks are shared code, so ask the walk and game feel lanes first.

VFX for the kit (marsh patch, bolt, line strike) waits for slice 1, because the theme decides what they look like.
