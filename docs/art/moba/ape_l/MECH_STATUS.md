# Gorilla (`ape_l`): mech status (Gorilla session, 2026-11-05)

This session owns the gorilla's overall refinement: VFX, kit upgrades and art touch-ups (Preston, 2026-11-05, via the hub).
Rules: `D:\dev\new-mech-rpg\.claude\worktrees\admiring-bell-074042\docs\team\mech-sessions-2026-11-05.md`.
Design: `docs/plan/moba-kits.md`, section Gorilla. Take A is the approved take (`take-a/APPROVED.txt`).

## In the game now
**Frames:** `art/machines/ape/ape_frames.tres`, packed into `ape_sheet.png` and `ape_kit_sheet.png`. Each animation has 5 views; the game mirrors the other 3.

| Animation | Frames per view | Camera | Source |
|---|---|---|---|
| idle | 5 | 35 degrees, tilted | `take-a/anim/idle35` |
| walk | 8 | 35 degrees, tilted | touch-up lane's walk frames |
| chest_beat | 8 | old low angle, tilted (stopgap) | Codex sets A and C |
| hex_shield | 6 | old low angle, tilted (stopgap) | Codex set A |
| bound | 9 | old low angle, tilted (stopgap) | Codex sets B and D |
| hex_dome | 8 | old low angle, tilted (stopgap) | Codex sets |
| death | 8 | old low angle, tilted (stopgap) | Codex sets B and D |

- **Ground contact:** feet meta and a 25-texel shadow are saved (`front 16, rear -22`). The camera lane signed them off, and the walk-turn check has 0 foot swaps (per the hub).
- **Stills:** the 35-degree views are `take-a/views_cam35_touchup/` (APPROVED). Take 2 of the cam35 redraw is in `take-a/views_cam35/`: accepted 2026-11-04, 111,880 Codex tokens over two images. Details: `take-a/cam35/HANDOFF.md`.
- **Not checked:** `art/machines/ape/ape_still_*.png` are still the low-angle approved views (dated 11-04). It is not checked where they are used.

**Kit:** `scripts/moba3d/ape_kit.gd`, 449 lines, keys 1 to 4 and Space for the basic attack. The ability lengths are placeholders with no cooldowns or damage yet. The basic attack has proposed numbers (below).
- Passive, silverback: allies inside the green ring are covered.
- 1, hex shield: thrown onto the nearest ally, or onto itself.
- 2, chest beat: taunts enemies close by.
- 3, bound: leaps to an ally or a spot ahead, and the landing knocks enemies back.
- 4, hex dome: enemies inside are trapped, enemies outside can't walk in, and shots stop at the wall.
- Basic attack, fist strike (working label, 2026-11-05): melee, one enemy in front. Proposed: 28 damage, every 1.0 s,
  reach 2.2 m edge to edge, 60-degree cone when aimed at nothing, 0.06 s hitstop, 0.2 camera shake. The rhino's horn
  jab is 30 every 0.9 s at 2.0 m (33 a second against the gorilla's 28). No strike frames yet: it borrows the hex
  shield throw at 3x, with the hit on f3 at 0.22 s and the swing done at 0.50 s.

**VFX on hand:**
- the silverback ring (a dashed green ground ring) and a taunt "!" mark, from `tools/art/draw_ape_kit_fx.py`;
- the hex tile shell for the shield and dome (`scripts/moba3d/hex_shield.gd`): it pops in over three steps with a flash, flashes when hit, and flashes before fading out;
- ground pulses (`_pulse`), a white hit flash on the sprite, and camera shake through the `impact` signal (0.7 on the bound landing, 0.8 on the dome).
- There are no particles, dust or debris anywhere in the kit.
- Match camera shake: `impact` now shakes it for the player's own machine (`shake_camera`, on by default), so the bound
  landing (0.7), the dome (0.8) and the strike (0.2) all shake in matches. `ape_reveal.gd` turns it off, because the
  reveal shakes its own camera on impact (game feel's suggestion, 2026-11-05).

## Open
1. **Kit animations are still at the old angle.**
   - When an ability fires, the sprite switches from the tilted 35-degree idle or walk to an upright low-angle drawing.
   - This session has not yet seen it in game. It is likely to pop.
   - Who redraws: the attack lane owns attack redraws. Per the roster, hits, deaths and other non-attack moves have no owner yet.
2. **Walk speed (Preston's call).** The walk is drawn for 0.48 m/s, but the gorilla moves at 3.5 m/s, so it slides about 7 times too far (hub's numbers). The choices:
   - a slower gorilla;
   - a faster gait cycle (walk lane);
   - accept the slide.
3. **A 35-degree death:** paid, undecided.
4. **Plates:** the cam35 plates are rounder than the approved ones. Accepted with take 2.
5. **`ape_kit.gd`:** game feel confirmed nothing in flight (2026-11-05); it's this session's to edit.
6. **Strike frames (paid, attack lane):** asked 2026-11-05. The kit uses `strike_<view>` by itself once it exists
   (`STRIKE_ANIM`, `STRIKE_HIT_FRAME` at the top of the kit).
   - Attack lane's price (2026-11-05): draw-only Codex sheets from `take-a/views_cam35_touchup`, three sheets (e+se,
     ne+n, s), about 5 frames each, finished by script for free. First pass 75k to 105k tokens, cap 40k per sheet;
     120k to 180k with one or two fix runs; worst case 345k (3 x 115k, cap plus overshoot). Their real numbers:
     draw-only 2 rows 31,831, 1 row 23,442.
   - Frames: one-arm forward fist. F0 pull back, F1 wind-up top, F2 contact with the arm fully out, F3 follow-through,
     F4 back to idle. Contact F2 (matches `STRIKE_HIT_FRAME`), about 1.1x for 0.45 s.
   - Handover: frames land in `docs/art/moba/attack/ape_l/strike35/`; this session packs `strike_<view>` via
     `tools/art/pack_ape_3d.py` (add to `TILT_ANIMS`, keep the feet meta), touch-up lane told first.
   - **Approved:** Preston said "Yes, gorilla strike" in the attack lane's session (2026-11-05). The attack lane asked
     the hub for the paid slot; sheet 1 (e and se) runs when it is free. Same quote, worst case 345k. When frames land,
     tell the touch-up lane, then pack. Touch-up lane: nothing in flight on the gorilla, clear to pack (2026-11-06).
   - **Sheet 1 (se, e) done, with Preston for a look (2026-11-06). Don't pack yet:** sheets 2 and 3 wait on his word.
     Frames: `docs/art/moba/attack/ape_l/strike35/s1/frames/<view>_f1..f5` = strike F0 to F4, contact F2; 160x160,
     feet on row 130 like the stills, raw with no outline. Timing: one 100 ms tick per frame at about 1.1x puts contact
     near 0.18 s and the end near 0.45 s, so set `strike_anim_speed` to about 1.1 when packing. The se contact fist
     reaches row 135, below the feet, on purpose (it drives toward the camera).
   - **All five views done, with Preston for approval (2026-11-06). Don't pack until he says yes.** Files:
     `docs/art/moba/attack/ape_l/strike35/final/strike/<view>_F0..F4.png`, 160x160, feet on row 130, raw, contact F2;
     timing and notes in the README there. The side view is a second take that matches the still better than sheet 1.
     Total spend 65,993 tokens, under the 75k to 105k first-pass quote.
7. **Strike sounds (sound lane): in, as free placeholders (2026-11-05).** `strike_swing` is a low arm whoosh
   ("Haymaker"), `strike_hit` a heavy body punch on a short low boom ("Fist"), with a 3% pitch nudge on each play.
   The sound lane's `check_kit_audio.gd` plays both: PASS. Preston has a page of B options; his pick may swap the files
   under the same names, with no kit change.
8. **Melee aim assist: added on Preston's "Yes, add it" (2026-11-05), `strike_assist`, on by default.** Was: the rhino's jab now turns to the nearest enemy in reach when nothing is in
   its aim cone (`jab_assist`, on by default, 2026-11-05). The gorilla's strike doesn't: aimed with no enemy inside its
   60-degree cone, it swings at nothing. Adding the same switch is a few lines in `ape_kit.gd`, free.

## Log
- 2026-11-05: Preston picked **A: see the cast pop**. Asked game feel for the board and clip; waiting.
- 2026-11-05: game feel says `ape_kit.gd` is clear, nothing in flight; it's the Gorilla session's now. The cast capture
  is running in arena_play: one pass upright as now, and one with the five actions tilted by a test-only override.

- 2026-11-05: **slice A result (game feel): it pops, in height and angle.** Board
  `match/cam_angle_test/ape_cast_pop_board_2026-11-05.png`, clip `ape_cast_pop_clip_2026-11-05.mp4`.
  - As now: the action is 32% shorter in s, 37% in se, 34% in n. The width barely changes (165 to 163 px in s), so it
    is the angle, not the scale. The feet rise about 3 game px. The switch is as big as the action's biggest move.
    All four abilities start on the same pose, so the pop is the same for each.
  - Tilted (test only): the height pop drops to 19 to 23%, and the feet stay put. Still face-on against the idle.
    Game feel: a fair stopgap, better than now, not a fix. Don't scale the frames to close the rest.
  - The real fix is the actions redrawn at 35 degrees, through the attack lane's pilot (slice B).
  - The stopgap is one line: add the five actions to `metadata/tilt_anims` in `art/machines/ape/ape_frames.tres`.

- 2026-11-05: **tilt stopgap applied** on Preston's "Yes, tilt now". `art/machines/ape/ape_frames.tres` line 2004:
  `metadata/tilt_anims` now lists idle, walk, chest_beat, hex_shield, bound, hex_dome and death. A headless load check
  passed (feet meta intact, frame counts unchanged). Backup: `D:/dev/_scratch/gorilla/ape_frames_before_tilt_2026-11-05.tres`.
  To undo, put the list back to `["idle", "walk"]` here and in `tools/art/pack_ape_3d.py` line 57 (`TILT_ANIMS`), which
  writes this line on every repack and already lists the seven names. Its `FEET_CAM35` matches the feet meta.
  The real fix is still slice B (a 35-degree redraw of the actions, via the attack lane's pilot).
  Camera lane: tilted actions are planted and shadowed exactly like idle and walk, with the same feet meta. That meta was
  measured on the 35-degree idle and walk, so on the low-angle actions it is approximate. Game feel's +0 to +2 px is
  inside the 4 px planting bound; the camera lane has not measured the actions itself.

- 2026-11-05: **basic attack built** (game feel's hook, Preston via game feel: "we need basic attacks. Rhino, gorilla
  will be melee."). `basic_attack(target)` in `ape_kit.gd`, mirroring the rhino's horn jab. Backup of the kit before:
  `D:/dev/_scratch/gorilla/ape_kit_before_basic_2026-11-05.gd`. My check `D:/dev/_scratch/gorilla/ape_basic_check.gd`
  passes 20 of 20 (hit frame, timing, damage, cues, reach, cone, refusal mid-ability, freed after).
  Found on the way: the shared `release_from()` sets the sprite speed back to 1, so a sped-up action plays its tail at
  normal speed. The kit sets the speed again after the hit (the swing went 0.92 s to 0.50 s). Told game feel and the rhino.
  Shared checks (--fixed-fps 60): ape3d_check passes; kit_api_check 31 of 31 (rerun at 21:04, after another lane's edit);
  match_check one FAIL, the rhino's Space basic doing 0 to a minion (the rhino is the match's player machine), not the gorilla.

- 2026-11-05: **match shake wired**, as game feel suggested. `ape_kit.gd` connects `impact` to `KitFeel.shake`
  behind `shake_camera`; `ape_reveal.gd` sets it false. The strike now shakes through `impact`, and uses game feel's new
  `release_from(frame, speed)`. Backups: `D:/dev/_scratch/gorilla/ape_kit_before_shake_2026-11-05.gd` and
  `ape_reveal_before_shake_2026-11-05.gd`. Checks (--fixed-fps 60): my check 26 of 26 (now also the impact, the match
  camera's KitShake, and no double shake in the reveal), ape3d_check 65 pass, kit_api_check 31 of 31, match_check 67 of 67.

- 2026-11-06: **melee aim assist added** on Preston's "Yes, add it". `strike_assist` (on by default): Space with no
  enemy in the aim cone turns to the nearest enemy in reach, as the rhino's jab does. Backup:
  `D:/dev/_scratch/gorilla/ape_kit_before_assist_2026-11-05.gd`. Checks (--fixed-fps 60): my check 30 of 30 (aimed left,
  it turned right to the dummy and hit; assist off, the same swing missed), ape3d_check 65 pass, kit_api_check 31 of 31,
  match_check 67 of 67.

- 2026-11-06: **both fists and MOBA feel in the kit**, on Preston's words via the attack lane: "mirror the gorilla animation
  so the other first punches too. The melee attack will be like mobas where holding basic attack keeps attacking. Give it
  moba feel, Then i want it to bunch with both hands one at a time".
  - Swings alternate: right (`strike`), then left (`strike_b`, the attack lane's mirrored set). `last_hand` records it.
    When packing, views with no left drawing of their own (se, e, ne, until the paid far-arm job) get strike's frames
    under `strike_b`, so the kit never needs per-view logic.
  - Holding Space or the left mouse button already repeats: `arena_play` polls the button each frame, and the director
    spaces swings by `basic_cooldown` (1.0 s). No shared change needed.
  - Wind-up to contact locks the gorilla (0.18 s with the drawn frames). After the hit the backswing is free: moving or an
    ability cancels it on the spot.
  - `strike_anim_speed` is now 1.1 for the drawn frames; the borrowed shield throw keeps 3.0 (`stand_in_anim_speed`).
  - Not done: no attack-speed stat exists, so nothing scales the swing yet; the swing (0.45 s) fits inside the cooldown.
  - Backup: `D:/dev/_scratch/gorilla/ape_kit_before_hands_2026-11-06.gd`. Checks (--fixed-fps 60): my check 36 of 36
    (fists alternate; backswing free; a move cancels it and walks 0.18 m in 3 ticks; chest beat cancels it), ape3d_check
    65, kit_api_check 31 of 31, match_check 67 of 67.
  - Held-Space test in the real match, `D:/dev/_scratch/gorilla/ape_hold_check.gd` (game feel's suggestion): a 3.1 s
    hold gave 4 swings exactly 60 ticks (1.0 s) apart, right, left, right, left; none after release. 5 of 5 pass.
  - Still to pack, after Preston approves the strike set: `strike` and `strike_b` into `ape_frames.tres`.
  - Far-arm left punch for se, e, ne: Preston said "Yes, run it" (2 sheets) in the attack lane. Third in the hub's paid
    queue (after the chameleon redraw and the lobster walk). A drop-in: same canvas, feet row and frames, named
    `final/strike_b/<view>_F0..F4`; swap the files and repack, no kit change. Until then those views repeat the right fist.

- 2026-11-06: **the punch kicks the camera along the hit** (Preston via the camera lane: "Kick the camera along the
  punch... rather than a random shake"). At contact the kit calls game feel's `KitFeel.basic_hit(player, target)`. It
  brings the gorilla's sprite lunging 0.2 m along the punch, the target shoved, the hit spark on the target's near side
  (it replaces the kit's own spark), and the camera lane's 2 px kick for the local player. `basic_shake` is now 0, so
  there is no random shake on the basic. Backup: `D:/dev/_scratch/gorilla/ape_kit_before_kick_2026-11-06.gd`.
  Checks: my check 37 of 37 (no impact; lunge 0.20 m; camera offset up to 0.083 m at contact), ape_hold_check 5 of 5,
  ape3d_check 65, kit_api_check 31 of 31, match_check 67 of 67. Tuning when Preston plays, one value at a time:
  `ChaseCamera3D.KICK_PX` (2.0), the kick time (0.15 s), `KitFeel.KICK_SIGN`, and `KitFeel.lunge_m` / `push_m`.
  A harmless error printed once per sprite from `KitFeel.nudge` (`get_meta` with a null default); game feel fixed it.

- 2026-11-06: **a missed punch lunges too** (game feel's optional line, for Preston's "you cant really feel when you are
  using it"): `KitFeel.nudge(sprite, dir * lunge_m, lunge_back)` when the strike finds nothing. Only `basic_hit` is called on a
  hit, no separate `KitFeel.kick`, so the camera kicks once (game feel confirmed). Backup:
  `D:/dev/_scratch/gorilla/ape_kit_before_whiff_2026-11-06.gd`. Checks: my check 39 of 39 (a whiff lunges 0.20 m and
  settles to 0.000), ape_hold_check 5 of 5, ape3d_check 65, kit_api_check 31 of 31, match_check 67 of 67.
- 2026-11-06: **the drawn strike may be replaced; don't pack it yet** (attack lane). Measured, the contact fist barely
  leaves the standing silhouette (e +6 px, se and s about 0) and the wind-ups are mild. The attack lane is asking Preston
  for a one-sheet test (se, e) of a deep wind-up and a locked-straight arm, ahead of the left-fist set. Names, canvas
  and contact F2 stay the same. Their free timing proposal for packing, placeholders: holds F0 0.5, F1 1.5, F2 1, F3 1,
  F4 1 ticks at 10 fps and 1.1x (wind-up 0.136 s, contact 0.18 s, end 0.45 s), for strike and strike_b alike.

## Next slices (Preston picks one)
**A. See the cast switch in game (free).**
- Ask game feel for one board and clip: the 35-degree idle going into each ability, in s and se. Compare upright frames as now with the same frames tilted.
- Result: Preston sees whether the old-angle kit frames pop, and whether tilting them is a fair stopgap, before any money goes on B.
- Cost: none, one Godot run in the game feel lane.

**B. Redraw the kit animations at 35 degrees (paid, Codex).**
- One ability per job, chest beat first: it fires up close, where the camera looks hardest.
- **Corrected 2026-11-05 (attack lane):** an earlier estimate here of 80k to 110k per ability was wrong. That is one
  Codex sheet, not one ability in five views.
- The attack lane's real numbers, from the rhino ground pound at 35 degrees: 168,763 tokens so far with only the e view
  finished. Its rough projection is 2 or 3 sheets of 90k to 110k each plus a 45k to 75k finish pass, so about **250k to
  350k per ability**, more in the worst case (75k over each cap). All four abilities: about 1.0M to 1.4M; death adds one more.
- **The method is not proven yet.** No price goes to Preston until the attack lane sends real per-ability numbers, after
  the rhino's five views pass. Its lessons are in `docs/art/moba/attack/ATTACK_PLAYBOOK.md`, section 5.
- The finish step brings ink and highlight shares back to the still's.
- Needs: Preston's yes per job, the attack lane's agreement on who runs it, and the touch-up lane told first.

**C. Bound landing VFX (free).**
- What it adds: a hex-green impact ring, a short burst of dust and chips, and a hexagonal ground crack that fades.
- How: drawn with Python the way `draw_ape_kit_fx.py` draws the ring, and wired into `ape_kit.gd` at the landing frame.
- Synthesis first: study the leap-and-land structure (layers, timing, how long each part lasts) in two or three shipped games.
- It must read differently from the hippo's belly flop and the end of the rhino's stampede (`moba-kits.md` flags the overlap).
- Result: Preston presses 3 in the slice and sees it.
- Cost: none, one session.

**Recommendation:** A first, because it's free and decides whether B is needed now; C is the slice he can press play on today.

## 2026-11-07: 3D walk test on Preston's Meshy-rigged gorilla (scratch only, nothing installed)
- Model: `D:\user\Downloads\Meshy_AI_gorilla_connected_100k_2k_20261107_character.glb`, copied to `D:/dev/_scratch/gorilla/walk3d/`.
  It has 31 generic bones (SmartRigArmature) and a stray Icosphere, which is hidden.
- Walk v1 (`walk.py`, `walk_v1.blend`): a lateral-sequence knuckle-walk (hind A, fore A, hind B, fore B at quarter phases).
  It is 33 frames at 30 fps (1.1 s), stance 65%, stride 0.30 m, with an IK target per limb. The body dips twice per cycle,
  sways toward the planted arm, and the chest yaws and the head nods.
- Measured: the contacts slide 0.000 m on all four limbs. The mesh dips 1 to 6 cm under the floor (fingers and toes rotate with the chain).
- The Hunyuan $0.525 run was skipped because Preston's model replaces it. Nothing was spent.
- Walk v2 (`walk2.py`, `walk_v2.blend`), from Preston's "Heavier, bigger steps":
  - 39 frames (1.3 s), stride 0.46 m (was 0.30), stance 68%.
  - Lift is 0.26 m on the arms and 0.17 m on the legs, with a fast lift and a slammed landing.
  - The body drops 7 cm right after each arm lands, then recovers slowly. Sway is 6 cm, roll 5 degrees, chest yaw 7 degrees.
  - The IK now matches the rest orientation of the hands and feet, so they stay flat.
  - Measured: contact slide 0.001 m or less; floor dip at most 1.2 cm (v1 was 6 cm).
- Walk v2 in 8 directions (Preston: "Yes, render 8 dirs"):
  - 312 frames at the 35-degree camera, with the light turning with the camera so every direction is lit the same.
  - Shrunk to the game's 160 px cells with one fixed anchor: the feet line matches `ape_still_se`.
  - Order: s, se, e, ne, n, nw, w, sw.
  - Files: `walk_v2_8dir_sheet_160.png`, `v2_160/<dir>_<frame>.png`, `walk_v2_8dir_gamesize.gif`, all in `D:/dev/_scratch/gorilla/walk3d/`.
  - Not packed into `ape_frames.tres`; it waits for Preston's yes.
- 2026-11-07, model fixes before animation (Preston: "fix chest proportions, separate pieces that shouldn't move"):
  - **Pieces:** the mesh is 2,191 loose pieces with soft weights (2 to 4 bones each), so the plates bend.
    A one-bone-per-piece pass (`common.rigidify`) cracks at the joints (`rigid_compare.png`).
    The pieces need grouping by hand into armor parts (forearm, shoulder, chest, back pack), with the cables kept soft.
  - **Chest:** Preston chose "match current gorilla". The c1 fix (`chestfix.py`: spine 12, neck 30, chest 1.12) is baked as a new rest pose in `gorilla_c1.blend` and `.glb`.
    The head is now on top and the face and chest gem read. Still open: the head sits a little high and far forward from the side, and the floor dips 7.6 cm.
  - **Armor pass on c1** (`walk2c.py`, `armor_compare.png`): soft only, solid at 60% or more on one bone (1,575 of 2,451 pieces), and solid at 75% or more (861 pieces).
    At 60% there are visible cracks across the shoulders; 75% has fewer. Neither is clean.
    Next: hand-grouped armor parts (each plate and its trim on one bone), the cables and joint covers soft, and the 7 cm floor dip fixed.
  - **Meshy key:** saved as the user env var `MESHY_API_KEY` at Preston's yes; the balance check works (1,120 credits). It is not in any project file.
  - **c2 chest** (Preston said c1 pushed the chest out too far): spine 5, neck 22, no chest scale-up. Files: `gorilla_c2.blend` and `.glb`. Floor dip 1.7 cm.
  - **Colour-grouped armor on c2** (`common.rigidify_grouped`): 1,219 plates solid, 498 trim pieces on their plate's bone, 42 cables, 406 grey and 277 straddling green pieces left soft.
    It shatters the hex panels and cracks the shoulders. The finding: Meshy's loose "pieces" are single facets, not armor parts, and the model has no seams at the joints.
    No automatic rule can make a fused shell move like separate plates. That needs real part seams, made by hand in Blender or regenerated as parts.
  - **Seam cuts on c2** (Preston: "Cut seams in Blender"):
    - The nearest-bone cut (`cut.py`) sliced through the hex panels, and its 17 joint balls sat inside the shell, invisible.
    - The joint-plane cut (`cut2.py`, `gorilla_c2plane.glb`, `plane_compare.png`) is the best so far: 16 solid parts, whole facets kept together, floor dip 1.7 cm.
      Still tearing: the wrist plane runs through the forearm hex panel, and there are shards at the shoulders.
    - Next slice: set each joint plane's position by eye (wrist below the hex, shoulder at the pad edge), look at each joint up close, then decide on gap covers.
  - **Armor parts, working version** (`cut4.py`, `gorilla_c2parts.glb`, `c2parts.blend`, `parts_walk_compare.png`):
    - Each loose piece goes to the part with the most of Meshy's own skin weight, after merging the 31 bones into 13 mech parts: pelvis, waist, chest with the head, then upper arm, forearm and hand on each side, then thigh and shin on each side.
    - The clavicle and elbow bones join the upper arm, so each shoulder pad is one piece.
    - The hex panels, shoulder pads, hands and legs move as solid parts. The floor dip is 1.7 cm.
    - Still open: a few loose shards at the back pack trim and the upper-arm/forearm edge, and small gaps showing at the bent joints.
    - Abandoned: nearest-bone cuts (`cut.py`) and plane cuts (`cut2.py`, `cut3.py`) sliced plates.
  - **Shard clean-up** (`cut5.py`, `gorilla_c2clean.glb`, `c2clean.blend`, `clean_compare.png`):
    - A piece whose touching neighbours (within 1.2 cm) mostly belong to another part, and whose own Meshy weight share is under 80%, joins that part.
    - 202 pieces moved. The back pack, shoulder pads and forearm armor now come out whole.
    - Still open: thin dark seams at the pack-to-shoulder and upper-arm-to-chest edges when the joints bend, and one forearm part reaching up toward the left shoulder.
    - This is the current best model.
- 2026-11-07: **The rigged gorilla is in the mech catalog** (`scenes/mech_catalog.tscn`) as "Gorilla (Meshy rig)", beside the old Hunyuan gorilla and sharing its four sheets.
  - Display: `art/model_catalog/display/gorilla_rigged.glb`, the rest pose at 39k triangles.
  - Touch-up workspace: `art/model_catalog/workspaces/gorilla_rigged.blend` (full model, rig and walk). Source: the Meshy original in `sources/`.
  - The catalog check passes with 27 models.
  - Touch-up list in the entry: hex shields incomplete, eye sockets empty, proportions and evenness, shoulder seams.
- 2026-11-07, **eyes** (Preston: "Yes, eyes first"; `eyes.py`, `c2eyes.blend`, `eyes_final.png`):
  - Two angled eyes with the inner ends lower, matching the front sheet. Each is 7.4 cm wide and set 1.4 cm proud of the dark face plate.
  - Colour yellow-green (0.50, 0.80, 0.00) with a glow of 1.3. At 4.0 they washed out to cream.
  - They are weighted to the chest-and-head part.
  - The catalog model and workspace were re-exported from `c2eyes.blend`; the catalog check passes with 27 models.
  - Next on the touch-up list: the hex shields, then evenness.
- 2026-11-07, **hex shields** (Preston: "Yes, shields"; `shields.py`, `c2shield.blend`, `shields_final.png`):
  - One shield piece built to the sheets: a closed orange hex frame (flat top), a dark backing, and 7 lime honeycomb cells with a glow of 0.35.
  - Forearms: fitted over each forearm's lime panel by a plane fit on the tight cluster (radius 0.23 x 1.18), weighted to the forearm bones 021 and 027. They now match the front and left sheets.
  - Back: a new 0.33 m shield on the upper back, facing back and up at 37 degrees, weighted to the chest. It replaces the look of the rectangular panel.
    From the side it stands off the curved hump at its top edge. Next fix: tilt it to the hump or cut it to sit flush.
  - The catalog model and workspace were re-exported; the catalog check passes with 27 models.
- 2026-11-07, **back shield fit** (Preston: "fit it, make it look indented into the back part, the orange frame's too big"):
  - A sunk-and-cut recess was tried first and buried the shield under the panel; dropped.
  - Now the back shield is subdivided and bent onto the hump by ray casts along its facing: rim 3.5 cm, cells 1.2 cm, 4 mm proud of the surface. Surface height across it varies 2.4 to 24.7 cm, which is why a flat shield stood off.
  - All frames are thinner: inner radius 87% of outer, was 80%.
  - Asked Preston whether "orange frame too big" also means the existing strap frame and handle around the back panel.

### 2026-11-07, Meshy gorilla: shield depth, power cells, back strap frame
- Shield frames raised: forearm frame height 0.085 x R/0.2 (was 0.05), back 0.07 m (was 0.035). Cells 0.035 x R/0.2 (forearm), 0.032 m (back).
- Power cells rebuilt as bevelled hexes: a deep-lime glowing side (0.16, 0.42, 0) and a bright lime top face (0.46, 0.92, 0), top 70% of the base, on the dark backing.
- Back orange strap frame shrunk to 0.82 in its own plane (plain scale, no re-seating; the ray-cast re-seat made spikes from far hits).
- The orange flap on the side of the back hump is in Meshy's original mesh, not from this pass.
- Scripts: _scratch/gorilla/walk3d/shields.py, frame_shrink.py; catalog display re-exported from c2frame.blend.

### 2026-11-07, Meshy gorilla: evenness pass
- Measured first: the surface already mirrors left to right (median gap 3 to 4 mm, 90% within 1.2 cm), so no geometry was moved.
- The uneven thing was the part cut: the pelvis held only the left hip (centre x -0.17 m), the right thigh took the right hip (0.72 m wide vs 0.45), and the waist ran down one side.
- Fix: part cuts mirrored (hips and legs follow the x<0 side, arms and shoulders the x>0 side), then each loose piece voted into one part. 3,254 verts moved. Pelvis now centred (x +0.002), thighs 0.449 vs 0.453 m wide.
- Picture: reports/model_catalog/gorilla_parts_even.png (pairs share a colour). Script: _scratch/gorilla/walk3d/even_parts.py, output c2even.blend.
- Still uneven: the upper arm part is 0.84 m wide on one side vs 0.69 on the other (a few stray shoulder pieces). The walk was made on the old cut and has not been re-rendered.

### 2026-11-07, Meshy gorilla: arm joints, shield sides, back cell backing
- Arm joints: after the mirror pass, forearm pieces still sat up on the shoulder, so the elbow would have bent in a ragged line. Each whole loose arm piece now goes to the arm bone it is closest to (236 pieces moved), giving straight joint lines at shoulder, elbow and wrist on both arms.
- Arm shields: frame height 0.06 x R/0.2 (was 0.085), size 1.10 (was 1.18), sunk 1.5 cm into the forearm so the orange rim sticks out less at the side.
- Back shield: the black backing sank under the bulge of the hump, so pale lime showed between the cells. The backing is now split fine enough to follow the bulge and sits 2 cm thick; the cells are green on black like the arm shields.
- Picture: reports/model_catalog/gorilla_fix3.png. Not done: the plate surfaces themselves are still Meshy's lumpy facets (geometry not flattened); the walk is not re-rendered.

### 2026-11-07, Meshy gorilla: flat plates
- Measured: the plates are already geometrically flat (mean lump 0.7 to 1.7 mm). Meshy's model is thousands of loose facets, so moving points to flatten them opened cracks between facets (tried, rejected).
- The lumpy look was the shading. Fix: faces that face within 28 degrees of each other form a plate (15,442 plates), and each plate gets one shading direction (custom normals). No points moved.
- Picture: reports/model_catalog/gorilla_flat.png (top before, bottom after). Script: _scratch/gorilla/walk3d/flatten.py MODE=normals, output c2flat.blend.

### 2026-11-07, Meshy gorilla: welded and flattened plates, arm shields fitted
- Touching facets welded inside each part (81,116 to 55,411 points), so flattening can no longer open cracks between facets.
- Plates (faces within 34 degrees) laid onto one plane each; points where plates meet solved onto the line where the planes cross, which straightens the creases. 2,960 plates flattened; points moved median 3.5 mm, 99% under 3.3 cm. Plates lumpier than 5 cm are left alone. Shields are excluded.
- Then flat shading per plate (custom normals), as before.
- Arm shields now built like the back one: subdivided and laid onto the forearm surface, so they wrap the forearm instead of standing off it. Side effect: the rim follows the forearm's bumps and looks slightly wavy from the front.
- Picture: reports/model_catalog/gorilla_flat2.png (top: last version, bottom: this one). Scripts: flatten2.py, flatten.py MODE=normals, shields.py (conform for all three).

### 2026-11-07, Meshy gorilla: built fists, flat-colour texture, Meshy multi-view texture (not in the catalog yet)
- Fists: Meshy's uneven grey fingers cut out (900 and 820 faces) and replaced by 4 even square blocks per hand (12.5 to 12.7 cm wide, 2 cm gaps, 21 cm tall, a fingertip block and a knuckle block behind it). Close up they are even; at full-body view they read as flat bricks sitting out in front, worse than Meshy's rounder fists. Not accepted. Script hands.py, output c2hands.blend.
- Flat colour texture: 14,484 plate colour groups, each painted one median colour (tex_flat.png). Cleaner than the original but close to it.
- Meshy multi-view retexture (meshy-7, the 4 sheets, original UVs kept): 10 credits, task in _scratch/gorilla/meshy_retex/task.json. Brighter green closer to the sheets, but blotchy, with an orange smear on the side of the arm.
- Comparison: reports/model_catalog/gorilla_tex_options.png (columns: sheet, current texture, flat colour, Meshy texture).

### 2026-11-07, Meshy gorilla: one back shield, flat colour texture (in the catalog)
- Preston chose the flat colour texture. Built fists dropped; Meshy's own fingers kept.
- Back: the lime panel under our hex (it reached 45 cm below the hex centre) and our hex are now one shield: radius 0.42 m (was 0.33), centre moved 10 cm down the back.
- Known fault: from the side, the shield's top edge rides up onto Meshy's original orange flap on the hump top, so an orange box sticks up. Next fix: delete that flap.
- Picture: reports/model_catalog/gorilla_final.png. Model: c2final.blend.

### 2026-11-07, Meshy gorilla: the box on the back removed
- The orange box seen from the side was our own back shield standing off the hump as a slab: a few high spots under it (Meshy's leftover flap) lifted the whole shield.
- Fix: the fit now measures the hump under every shield point first, then ignores points more than 4 cm above the median surface, so the shield lies on the hump. Back frame height 0.05 m (was 0.07). Then 269 Meshy faces that still poked through the shield were deleted (poke.py).
- Tried and rejected: deleting Meshy's whole half-made back hex first; it left a hole and the shield sank into it.
- Picture: reports/model_catalog/gorilla_final.png (sheet back, model back, sheet side, model side, shield shown blue).

## 2026-11-07: new rigged gorilla (Meshy, 2026-11-07 GLB), pass 1
Work in `D:/dev/_scratch/gorilla/v2/` (chain: v2_src -> shield_split.py -> eyes.py -> hands.py -> feet.py -> v2_feet.blend). Not in the catalog yet.
- Forearm shields: front shield's faces (orange, lime, dark; region and colour, not facing) moved 3.5 cm inward and 1.6 cm forward, so the front and side shields have a gap. A small orange chip is left inside the lower-left corner.
- Eyes: the old lime bits at x +-0.3 to 0.45 are neck hoses; the real eyes were hidden under the helmet. New angled glowing lime eyes on the helmet front (x +-0.095, z 1.145), 100% Bone_022 (head, same as the mouth).
- Hands: the grey finger blocks are 1.45x taller from the floor (top 0.205 to 0.297; the sheet's fists are about 1.5x the old ratio), and the middle two sit 3.5 cm forward, so the knuckles arc. A copied thumb shredded and was dropped (THUMB=1 brings it back).
- Feet: the sole is up to 1.22x wider at the floor (fading to none at z 0.16), the toes are 1.3x taller, and the inner toe is 3 cm further in.
- Picture: `reports/model_catalog/gorilla_v2_pass1.png` (before and after: shields, head, hands, feet).
- Pass 2 (same day), after "you made hands worse": hands.py and feet.py dropped. hands2.py (on v2_eyes) deletes the generated grey finger blocks and builds knuckle-walk hands to gorilla anatomy: 4 fingers (middle two longest and furthest forward, little finger short and set back), each a near-vertical segment, a dark knuckle axle, a middle segment flat on the floor with a dark pad, a tip curled under the palm, plus a short thumb set back on the inner side; 100% hand bone. feet2.py deletes the generated foot blocks and builds a plantigrade foot: sole, pad, heel cap, 4 short toes, big toe on the inner side angled 32 degrees out; sole on the ankle bone, toes and tips on the two toe bones. Grey 0.115/0.122/0.128 linear to match. Picture: reports/model_catalog/gorilla_v2_hands_feet2.png. Grok video: reports/model_catalog/gorilla_grok_walk_punch.mp4.
- Pass 3: fills. Hands get a back-of-hand housing up into the cuff, a palm block under it meeting the curled tips, a thumb root, and a raised plate per finger over its bone. Feet get an ankle block up into the leg, an instep plate over the toe roots, and a big-toe root. Rendered and checked from the front, three-quarter and side.
- Catalog: `gorilla_rigged` now points at the new model (source `sources/Meshy_AI_gorilla_rigged_v2_20261107.glb`, sha f147adff...). Display GLB 33,690 tris, 34 bones, rest pose; workspace from v2_feet2.blend via `_scratch/gorilla/v2/catalog_export.py`. The old v1 display and workspace are backed up in `D:/dev/_scratch/gorilla/v1_catalog_backup/`. CATALOG CHECK PASS: 27 models.
- Pass 4: the open cuff underside behind the palm (left open when the generated blocks went) is closed with a recessed dark wrist block and a heel pad. Pose test (look_any.py, POSE env): upper arm 25, wrist -30, ankle 20, toes -30 degrees. Hands move rigidly with the hand bone, no tearing; toe segments bend at their joints and open small gaps. Re-exported; catalog check passes.
- Pass 5: the dark wrist block is gone; the hand itself fills the cuff underside. Finger pad segments run 0.30 m back (were 0.17), back-of-hand housing and palm reach the rear of the forearm (y -0.31). Re-exported; catalog check passes.

## 2026-11-08: downward fists and rebuilt feet — separate review candidate
- Latest combined editable review: `art/model_catalog/workspaces/gorilla_back_rim_review.blend`, with matching skinned `.glb`. Continue touch-ups from this file to retain the finished fists, feet, rebuilt front shields, current cell colors and completed orange back rim. Previous reviews remain available. Catalog display has not been promoted.
- Hands descend beneath the wrists onto four curled knuckle pads, with short raised thumbs. Uniformly enlarged by 17.38% after Preston requested the earlier bulk. Existing hand bones retained. Previous hand-only review remains `gorilla_hands_down_review.blend`.
- Feet rebuilt as tapered heel/instep housings, four graduated forward toes and a distinct medial hallux, with recessed joints and floor pads. Original foot width, length and height retained; existing ankle/toe/tip bones retained. Hands and all non-foot geometry, UVs and weights checked unchanged from the hand-only review.
- Foot review, before/after images, flex clip and validation: `docs/art/moba/ape_l/foot-refinement-2026-11-08/README.md`. Hand history: `docs/art/moba/ape_l/hand-refinement-2026-11-08/README.md`.
- Integrated finish: shin-sampled green heel/instep armor, gray contact toes and knuckles with restrained edge paint, dark joints/soles and two small conforming lime heel insets. Existing hand/foot dimensions, geometry and weights retained. Packed texture and skinned GLB reimport visually verified. See `docs/art/moba/ape_l/finish-refinement-2026-11-08/README.md`.
- Hand finish after Preston approved the feet: green palm housings and thumb roots join the forearm armor; gray fingers/thumb tips and dark joints retained. Paint-only change: all mesh geometry, UVs, weights, normals and skeleton checked unchanged. Foot paint tiles unchanged. Review and wrist-flex clip: `docs/art/moba/ape_l/hand-finish-2026-11-08/README.md`.
- Front shield placement/proportions: replaced overlapping front/side duplicates with one mirrored three-cell assembly per forearm. Clean beveled orange hex frames, regular hex cells, dark backing, fitted green mounts/casings and small cable couplings. Frames measure 0.580 by approximately 0.553 m in their plane; original hand/foot refinements and skeleton retained. Rigid forearm poses, closed shells, mirror geometry and GLB skin/texture reimport verified. Review: `docs/art/moba/ape_l/shield-refinement-2026-11-08/README.md`.
- Retained color decision clarified by Preston: use the existing back-cell field's slightly darker green behind the front cells too. Back field is preserved, rather than repainted to a literal dark forest green. Sampled sRGB target approximately (0.2373, 0.6255, 0.0412). Back rim, including the faded upper section, is orange throughout. Paint-only pass; all geometry, UVs, weights, normals and skeleton retained. See `docs/art/moba/ape_l/cell-color-refinement-2026-11-08/README.md`.
- Back rim correction: the green raised upper diagonal rails and the raised top lip also belong to the orange outline. These are now orange, completing the rim through both upper corners. Cell faces and original green backing preserved; no geometry changes. Review: `docs/art/moba/ape_l/back-rim-completion-2026-11-08/README.md`.
- Candidate is a model/rest-pose and deformation review, not a new walk cycle. Ground contacts during locomotion and Godot gameplay appearance remain to be verified.

## Knuckle-walk refinement candidate (2026-11-08)

Continued the MeshForge foundation with body weight shift and mesh-surface contact correction. Review candidate: `art/model_catalog/workspaces/gorilla_knuckle_walk_v3.blend` and `.glb`; 34 joints, 25,757 triangles, one 1.4 s slow-walk clip. Approved back-rim/static source unchanged; candidate not promoted into gameplay or catalog.

Exact contact solve baked in Blender, reimported/re-exported and visually reviewed in MeshForge. Independent 169-sample validation of both exports found under0.1 mm support penetration and under0.1 mm adjacent stance-marker error with the intended virtual controller displacement. Gameplay speed, transitions and terrain remain untested. Evidence/limits: `docs/reference/gorilla-walk-contact-refinement-2026-11-08.md`; preview `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v3/gorilla-walk-v3.gif`.

## Combat locomotion polish candidate (2026-11-08)

V6 candidate: `art/model_catalog/workspaces/gorilla_combat_locomotion_v6.blend` / `.glb`,34joints/25,757triangles. Original0.6s combat stride matches3.5m/s and a1.25x playback preview matches4.375m/s. Stable limb-plane orientation, smoother recovery and targeted structural armor weights; original topology/proportions/colors preserved. Industry-map test and FFmpeg recording completed after Preston reapproved computer use.

Details/limits: `docs/reference/gorilla-combat-locomotion-polish-2026-11-08.md`. Recording: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-polish-v6/gorilla-refined-movement.mp4`. Straight-segment contact checks pass; sharp turns still need dedicated blending/locking. This is a review candidate, not a gameplay/catalog promotion.

## Camera/combat direction and sharp turns (Preston, 2026-11-08)

SMITE is the primary reference for perspective, camera movement, skill use and combat feel; Paragon is secondary. Direction brief: `docs/plan/moba-camera-combat-reference-direction-2026-11-08.md`.

The industry-map sharp-turn test keeps the accepted V6 gait and uses a continuous third-person chase view. Visual90-degree changes settle within5degrees in~0.133s;180-degree reversals in~0.233s. Runtime `gorilla_turn_contacts.gd` locks planted endpoints, solves fixed-length limbs and releases/repositions a contact before overreach. Logged locked-anchor error stayed below0.4mm over1738samples. These are review-scene results, not certification of a complete SMITE-style combat controller or all terrain contacts.

Evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-turns-v7/`. Preston liked the turns but flagged remaining lower-body skin stretching; the next pass must preserve the turns/gait and fix the hip/leg deformation.

## 2026-11-08 pelvis rollback / eye paint v12
User confirms original pelvis proportions are correct: fix animation stretching/one-sided drag, never reshape to compensate. Rejected v10 mirrored/shortened pelvis and added eye pieces. Current isolated review uses gorilla_restored_pelvis_painted_eyes_v12: v9 pelvis geometry/UV/weights restored exactly; old brow inserts removed; existing eye texture painted solid green, no pupils or new mesh. Pelvis audit confirms conflicting asymmetric Chest/Hips/thigh weights and up to 9.715x local edge stretch. Binding repair remains pending; broad box-cut trial was not promoted. Details and evidence: docs/reference/gorilla-pelvis-study-eye-paint-2026-11-08.md. SMITE remains primary and Paragon secondary for gameplay feel.


## 2026-11-08 grounded idle v13
Created Gorilla_Idle_v13, 4 seconds/120fps, using restored v12 mesh and painted eyes. Original proportions/weights preserved. Four planted contacts, subtle shoulder servo breathing and alert head motion; hips/chest/legs neutral to avoid unresolved walk pelvis deformation. No IK reach clamps; endpoint loop matrices identical. Separate industry test: tools/debug/gorilla_idle_industry_test.tscn. Source: art/model_catalog/workspaces/gorilla_idle_v13.blend/.glb. Existing walk clip remains 0.6 seconds and walk test is unchanged. See docs/reference/gorilla-idle-v13-2026-11-08.md for evidence and limitations.


## 2026-11-08 Rampage study / readable idle v14
User rejected v13 as effectively motionless. Studied actual supplied Rampage Idle (7.67s), sampled 121 phases and inspected four donor renders. New Gorilla_Idle_v14 moves Chest visibly (6.09cm lateral), shoulders, and head (22.30cm) using adapted donor curves with planted hands/feet and exact loop closure. In the separate idle asset only, stray lower rear Chest influences redirected to Hips; 1003 sampled pelvis vertices remain at rest through the idle. All original rest geometry/topology/proportions unchanged. Walk v12/test untouched. Industry idle review now uses gorilla_idle_v14.glb; full evidence and limitations: docs/reference/gorilla-rampage-idle-v14-2026-11-08.md.


## 2026-11-08 basic attacks v15 — ready for review
User approved idle v14, then requested basic attacks. Built three attacks from actual supplied Rampage Attack_Melee_A/B/C: left 0.9s, right 0.9s, heavy left finisher 1.1s. Retained approved idle in same export. Adapted broad shields with wider lanes, stable elbow directions, wrist/forearm orientation, and head aim; all 177 authored attack poses clear the targeted native helmet/back-cell surfaces. Bracing fist and both feet remain planted; original proportions/topology/weights preserved from v14. Source: art/model_catalog/workspaces/gorilla_basic_attacks_v15.blend/.glb, event timing in .events.json. Separate industry review tools/debug/gorilla_basic_attacks_industry_test.tscn supports left click/Space/held click; target flash/recoil is a visual review marker, production hitboxes/damage still separate. Videos and full evidence: docs/reference/gorilla-basic-attacks-v15-2026-11-08.md. Walk v12 and approved idle v14 files untouched.


## 2026-11-08 v15 rejected / one-punch study v16
Preston rejected v15's motion: limb swings, not convincing punches. Its 177 clearance checks were technical evidence only. Diagnosis found lateral/downward/reversing fist travel at the supposed hit and insufficient body-to-fist drive. v16 deliberately studies ONE punch: folded load, hip/shoulder lead, aligned fist extension, real pad contact, short push/recoil, then return to grounded stance. Keep three-hit expansion pending visual direction; do not promote the rejected chain as approved. Approved v14 proportions/rig/weights/textures preserved, with new pose animation only. Clip Gorilla_Punch_Study_v16 is 0.933333s/contact F23 at 0.383333s for study; do not treat as a kit balance change. Full-speed side/front and half-speed media in scratch v16, industry test tools/debug/gorilla_one_punch_industry_test.tscn. Existing ape_kit damage, hit-stop, feedback and cancellation confirmed and untouched. Shared Rhino/Tartarus lessons read and retained in docs/reference/gorilla-one-punch-study-v16-2026-11-08.md.


## 2026-11-08 moving alternating basics v17 — review prototype
Preston liked the v16 jab but asked for held-click/strafe suitability; authorized alternating moving punches first. Built raised combat guard, compact left/right punches, entry/exit and dedicated directional footwork. Held attacks remain ready between hits; moving release crossfades to the existing knuckle walk. Separate industry test `tools/debug/gorilla_moving_combat_v17.tscn` uses actual 3.5 m/s movement, independent aim, fixed-length planted-foot solver and existing 1.0 s cooldown reference. Production kit/damage/feedback untouched; this remains an animation/input review scene, not production integration. All approved v14 geometry/UV/material assignments and 34 rest bones preserved. Intentional lower-rear residual leg weights redirected to Hips on 1212 vertices; original pelvis proportions unchanged. Eleven clips exported; 146 targeted attack poses have zero checked helmet/back-cell crossings. Final headless plant error below 0.002 mm, no remaining reach clamp; these metrics do not replace visual approval. Native 19-second review and close-front loop recorded. Details: docs/reference/gorilla-moving-combat-v17-2026-11-08.md.

- 2026-11-09 (gorilla 3D lane, Claude): **3D basic attack and the slam chain.** The 3D model work moved from Codex to this lane.
  In-map tests: v18 Geb-style swing, then v19 knuckle swat (rooted), then v20 swat, swat, slam. Notes and videos:
  `D:/dev/_scratch/gorilla/meshforge-2026-11-08/compare-v17-v18/README.md`. On Preston's "More damage, then lets start building
  the kit", `ape_kit.gd` now chains swat, swat, slam (28, 28, 42; the slam has a 0.09 s hitstop, strength 1.5, 0.3 shake; resets after 1.5 s).
  The sprite still plays the strike frames for the slam until slam frames exist. Backup: `D:/dev/_scratch/gorilla/ape_kit_before_slam_2026-11-09.gd`.
  Checks (--fixed-fps 60): new `D:/dev/_scratch/gorilla/ape_chain_check.gd` 9 of 9 (damage per hit, fists, shake, reset);
  ape_basic_check 0 failed, ape_hold_check 0 failed, ape3d_check 0, kit_api_check 0, match_check 67 of 67.
  Kit rework decided the same day (ult = chest beat with taunt, ally shields and the dome folded in; hex look from the forearm
  plates): see `docs/plan/moba-kits.md`, Gorilla. The ult is not built yet.
- 2026-11-09: **chest beat ult built** on Preston's "Yes, build the ult". `chest_beat_ult()` on key 4 (reports slot "4"): beat 1 taunts
  enemies within `ult_radius` 5.5 m for 1.5 s, beat 2 puts the hex shield on every ally within 5.5 m and the gorilla (3 s), beat 3 raises
  the dome at its feet (`_raise_dome`, every dome rule unchanged). Key 2 is empty. `chest_beat()` and `hex_dome()` are kept, so the reveal
  (`ape_reveal.gd`, now out of date: it still shows the old slots) and `arena_play`'s dome hook still work. Without chest beat frames the
  beats are 0.1 / 0.15 / 0.15 s apart (`beat_gap`). Backup: `D:/dev/_scratch/gorilla/ape_kit_before_ult_2026-11-09.gd`.
  Checks (--fixed-fps 60): new `D:/dev/_scratch/gorilla/ape_ult_check.gd` 10 of 10 (key 2 empty; taunt at 4.5 m but not at 7 m; shields
  after the taunt on the ally at 5 m and the gorilla; one dome at its feet, last; the enemy inside trapped). ape_chain_check, ape_basic_check
  and ape_hold_check 0 failed, ape3d_check 0, kit_api_check 0, match_check 67 of 67.
  Not changed (other lanes' files): the bots' gorilla row in `match_bot.gd` still calls chest_beat on 2 and hex_dome on 4; `kit_audio.gd`
  keys the chest hits to slot "2" and the dome sounds to "4"; `match_rules.gd` still lists a slot 2 cooldown.

- 2026-11-09 (Claude, 3D lane): chest beat ult now on the 3D model. Clip Gorilla_ChestBeat_Ult_v21; ape_kit.gd beat_times (0.45, 0.70, 1.10) syncs the kit to it. Test tools/debug/gorilla_ult_3d_v21.tscn, recordings in D:/dev/_scratch/gorilla/meshforge-2026-11-08/compare-v17-v18/.
- 2026-11-09 (Claude, 3D lane): ult rework on Preston's note. No ally shields; the dome wards its side (heals 6%/s, cannot drop below 1 hp; proposal). New plate-cell hex shell look for shield and dome. SMITE-camera test tools/debug/gorilla_ult_3d_v22.tscn.
- 2026-11-09 (Claude, 3D lane): chest drum rebuilt from a real-gorilla study (docs/reference/gorilla-chest-beat-study-2026-11-09.md). Gorilla_ChestBeat_Ult_v22: 6 strikes at about 13 a second, contact solved on the mesh. Ult dome 7 m (proposal), lighter big-dome look.
