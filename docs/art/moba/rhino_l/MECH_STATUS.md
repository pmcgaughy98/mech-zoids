# Rhino (`rhino_l`): mech status

Owner: the Rhino session (Preston, 2026-11-05: "those sessions will be for just overall touch ups upgrades and refinement for those mechs. Like VFX's, kit upgrades and touch ups."). Updated 2026-11-05. Nothing in this file is built or spent yet.

## In the game now
Everything below is packed by `tools/art/pack_rhino_3d.py` into `art/machines/rhino/`, last packed 2026-11-04 at 22:19.

| Part | Angle | Source | Approved |
|---|---|---|---|
| Idle, 5 views | 35 degrees, tilted | `take-a/views_cam35_touchup` with a 1 px breath (`anim/cam35-idle/`) | "Keep, game sel-out" |
| Walk, 5 views | 35 degrees, tilted | `anim/walk35/walk/frames_selout`, drawn from `views_cam35`, then given the touch-up colours by `anim/walk35_touchup.py` (animation lane) before packing | "Yes, pack it" |
| horn_jab, horn_toss, brace, brace_shuffle, stampede, ground_pound, death | old low angle, upright | Codex sets A to D in `anim/` | earlier takes |

Other parts:
- **Frames file:** `rhino_frames.tres` carries `tilt_anims = ["idle", "walk"]` and the camera lane's `feet` meta. Feet planting measured within 2.7 px over 24 camera steps (camera lane).
- **Kit script:** `scripts/moba3d/rhino_kit.gd`, 327 lines. It became this session's on 2026-11-05: game feel finished its work, with nothing mid-edit and nothing committed. Game feel's backup: `D:\dev\_scratch\game_feel\rhino_kit.gd.bak_2026-11-05`.
  - **Sound:** the cues dash_cast, horn_catch, toss_land and tremor_stomp are wired to KitAudio. The files wait on Preston's picks.
  - **Feel:** shake and stomp rings come from `kit_feel.gd`, which is game feel's shared code; ask before changing it.
  - **Checks:** `tools/debug/rhino_feel_check.gd` (field_test, `--fixed-fps 30`). Also `rhino3d_check.gd` and `match_check.gd`, both `--headless --fixed-fps 60`; game feel's last run had 0 failures and 67/67.
  - **Preston's to tune:** dash length, hitstop, shake strength and the 2.8 s root. Every length is an export.
  - **Coming to this session:** the attack lane's rock pop effect (4 to 6 frames, about 1 m). It replaces the `impact_puff` stand-in in `_stomp`.
  - Numbers: "Rhino kit feel" in `docs/art/moba/match/MATCH_NOTES.md`.
  - **Basic attack, horn jab (added 2026-11-05):** Preston: "we need basic attacks. Rhino, gorilla will be melee", relayed by game feel with its hook.
    - `basic_attack(target)` in the kit: reach 2.0 m edge to edge, cooldown 0.9 s, 30 damage (the stand-in's). All three are exports for Preston to tune.
    - The hit is on horn_jab frame 2, the lunge. The attack lane measured it on all five views, and frame 3 is the upward toss after contact. Changed from 3 to 2 on 2026-11-05.
    - horn_jab plays at 2x: the hit lands at 0.20 s and the swing ends at about 0.5 s.
    - **Aim assist (`jab_assist`, on):** when nothing is where the mouse aims, the jab turns to the nearest enemy in reach.
      This was added after match_check's Space test hit for 0, reported by the gorilla session.
    - After the assist, match_check went 67/67.
    - rhino_basic_check was 14/15. Its fail was a target straight behind, whose angle reads over 180 degrees; that is fixed by skipping the angle check for the full circle.
    - Re-run after all the fixes: rhino_basic_check 15/15 (the assist turns onto a target straight behind), kit_api_check 31/31, match_check 67/67 (with game feel's melee-reach update), rhino3d_check 64/64.
    - It hits buildings and monsters too. A swing at the air counts.
    - Cues: jab_swing ("Heavy air") and jab_hit ("Plate"). These are the sound lane's free placeholders, option A, in `audio/sfx/rhino/`.
      Preston's B options page may swap the files under the same names.
    - The art is the old-angle horn_jab.
    - **Checks:**
      - `tools/debug/rhino_basic_check.gd`: 13/13. rhino3d_check: 64/64.
      - kit_api_check: 30/1. match_check: 64/3. The fails are checks that assume the 6 m stand-in or no kit basic. They are game feel's to update, and it was told.
      - rhino_feel_check needs a window, so it was not run (it covers keys 1 and 2, which were unchanged).
  - **Passive:** front plating.
  - **Key 1, horn toss:** a 3.5 m dash; the first enemy is caught on the horn and thrown 3 m behind, stunned.
  - **Key 2, ground pound:** a slam, then 4 stomps 0.4 s apart over a 4 m slowing circle, about 2.8 s rooted.
  - **Key 3, brace.**
  - **Key 4, stampede.**
  - Details: `docs/plan/moba-kits.md` and `docs/art/moba/match/MATCH_NOTES.md`.
- **Fallbacks kept:**
  - the stills: `take-a/views`, `views_cam30`, `views_cam35`;
  - the packed files: `anim/cam35-idle/backup_pre_cam35` (old angle) and `backup_pre_touchup` (before the recolour).
- **Last check I ran:** rhino3d_check, 64 of 64, on 2026-11-04 before the walk was packed. It ends with "4 resources still in use at exit", which the camera lane is tracing.

## Open
1. **The walk's leg rebuild is not packed.**
   - Correction (2026-11-05): my first version of this file said the walk had the old colours. Wrong. The animation lane
     recoloured it from the touch-up views before packing. Measured: about 80% of the pixels the recolour changed show
     the touch-up colour in the packed walk; the rest is likely my comparison not allowing for the walk's 1 px dip.
   - What is still open: the touch-up lane rebuilt the legs of the se, e and ne walks (8 frames each) in
     `anim/walk35_touchup/`, from the touch-up stills. It fixes the cut plates, half discs and shards where moving legs
     cut the body (Preston: "Touch up rhino walk, lots of missing art because of movement and cutoffs").
   - It is not packed, and s and n are not in it.
   - **Touch-up lane, 2026-11-05 (from its `touchup/LOG.md`, sections 2 to 4):**
     - It is finished and parked. The last pass hand-drew the se front foot.
     - Preston has not given a verdict, and his view of `board_walk.png` is unconfirmed, so treat it as unseen.
     - s and n were left out only because the animation lane's run 2 was still going. Nobody has judged them clean; check them for the same cutoffs.
     - Known flaws:
       - lone dark specks on e f3 and ne f3 and f6;
       - never played as a loop before my GIF;
       - the far front leg in se is not drawn;
       - se and ne reach row 162, the same as the game frames;
       - the 1 to 3 px slots behind moved legs are filled with 211e27.
     - Option, Preston's call (free): a per-row body sway with the feet pinned, as on the fennec and hippo. It would run before packing.
   - **Preston, 2026-11-05: "Pack as is"** (no sway). I passed it to the walk lane word for word.
   - **Packed 2026-11-05 (walk lane):**
     - Footlock: all feet locked. Palette: 0 colours off it.
     - Only the se, e and ne walk rows of `rhino_sheet.png` changed (about 3,100 to 3,560 px each). The kit sheet and `rhino_frames.tres` are byte-identical.
     - The packer now reads the walk per view: `WALK_BY_VIEW`, with s and n from walk35.
     - Backup and restore steps: `anim/walk35_touchup/backup_pre_pack/README.txt`.
   - **My checks after the pack:** the Godot import is clean, and rhino3d_check is 64 PASS with 0 failures (log in `D:\dev\_scratch\rhino\`).
   - **Game feel's turn test, 2026-11-05: nothing blocks keeping it.** Raw output is in `D:\dev\_scratch\game_feel\rhino_walk_touchup\`; the boards are in `match/cam_angle_test/rhino35_walk_touchup_*`.
     - Mirror flips: 0 foot swaps.
     - Seams: s to se 9 px, se to e 3, e to ne 19 (the biggest), ne to n 3 (crop px, lowest foot). So the seams where rebuilt views meet old ones are small.
     - Starts and stops: 2 game px at most. Feet: none hidden by the floor in 40 frames.
     - Flagged: the ne lowest point drifts over frames 0 to 6, then snaps back, which may read as a hitch in the near hind foot.
       - I measured that it is not from the rebuild. The lowest drawn row per frame is identical before and after, in se, e and ne (ne: 158, 158, 159, 160, 161, 162, 163, 160).
       - It is the walk's original foot path, likely the planted foot sliding toward the camera as the body moves away. It belongs with open item 4 (walk speed).
   - **s and n checked 2026-11-05 (Preston: "Check s and n"):** they have the same defect.
     - The round grey knee disc on the stepping leg is cut to a flat bar or goes missing in s f0, f1, f2, f4, f5 and f6, and in n f0, f3, f4, f5 and f6. Judged by eye on a 5x legs crop, `review/walk_sn_legs_2026-11-05.png`.
     - No missing plates or shards were seen. A count of tiny colour islands matched the still (s 228 to 244 against 246; n 161 to 181 against 183), so it does not catch this defect.
     - The fix would be the touch-up lane's `walk_rebuild.py` run on s and n (free), then the walk lane packs.
     - **Preston, 2026-11-05: "Yes, rebuild them".** Passed to the touch-up lane word for word. It was busy, so the message is queued.
       Next: its board goes to Preston, and on his yes the walk lane packs s and n.
     - **Rebuilt 2026-11-05 (touch-up lane, `walk_rebuild_sn.py`):** every knee disc stays round in all 16 frames.
       - Footlock: all locked, with spreads the same as the packed walk. The feet are 98 to 100% the same pixels as packed.
       - Every frame is one piece and on palette.
       - Side effect: the grey patch on the right shoulder in packed s f2 to f4 is gone.
       - Board and GIFs sent to Preston: `review/walk_sn_rebuild_2026-11-05.png` and `walk_s_` / `walk_n_rebuild_*.gif`.
       - **Preston, 2026-11-05: "Yes, pack it".** Passed to the walk lane word for word.
       - **Packed 2026-11-05 (walk lane):**
         - All five walk views now come from `walk35_touchup/frames_selout`.
         - Only the front and back walk rows changed (1,413 and 2,250 px). The .tres and the kit sheet are byte-identical.
         - Footlock: all locked.
         - Backup: `walk35_touchup/backup_pre_pack_sn/`.
       - **My checks after the pack:** import clean. rhino3d_check 64/64, rhino_basic_check 15/15 (after the jab fixes), kit_api_check 31/31, match_check 67/67.
       - **Game feel's re-test, 2026-11-05:** same as before the s and n pack, with nothing new. Output in `D:\dev\_scratch\game_feel\rhino_walk_pack_sn\`.
         - Turning: 0 foot swaps.
         - Feet: the lowest pixel is unchanged in every frame, and none are hidden by the floor.
         - Starts and stops: no more change than run-to-run noise.
         - Not measured: whether neighbouring views (s and se, ne and n) have the same leg forward at the same frame. The foot path is unchanged from walk35's targets.
     - **Slice A is done:** all five walk views use the leg rebuild.
   - **Walk lane, 2026-11-05:** it is idle on the rhino and will pack on Preston's yes.
     - Its plan: back up, sel-out the rebuild into `walk35_touchup/frames_selout`, then change only the walk source in the packer, to s/n from walk35 and se/e/ne from the rebuild.
     - TILT_ANIMS and FEET stay the same.
     - Before packing it runs footlock and a palette check, and confirms that s and n match the rebuild's colours.
   - Review board sent to Preston 2026-11-05: `review/walk_rebuild_2026-11-05.gif` (moving) and `_f2_` (still),
     built by `D:\dev\_scratch\rhino\walk_board.py`. The rebuild changes 250 to 530 px per frame against the packed walk.
2. **The moves are still the old angle.** They pop on every move start and end (accepted for now).
   - **Count checked 2026-11-06 against `pack_rhino_3d.py`:**
     - At 35 and tilted, 3 of 9: idle, walk and horn_jab.
     - Still at the old angle, 6 of 9: horn_toss, ground_pound, brace, brace_shuffle, stampede and death.
     - Each of those 6 is drawn in s, e and n, with Codex diagonals in se and ne.
   - **Ground pound at 35 (attack lane; `docs/art/moba/attack/rhino_l/PLAN.md`, `LOG.md`):** run 1 (e, se, ne) cost 106,953 tokens. e reads well, se is usable after fixes, and ne turned toward the side view and fails. Not packed.
     - Preston said F3 reared too high because Codex added thighs.
     - **Fix1 is done** (61,810 tokens). Preston approved its e rear: "Yes, looks right". e F2 and F3 now have no thighs and the hips at standing height.
     - **Diagonals, all run 2026-11-05 (attack/LOG.md):**
       - diag1 cost 85,656 tokens. F3 failed in both views: an extra leg and stacked joints.
       - diag2 cost 31,831. ne's rise and rear came out right and were finished free in gp35/diag2_fin.
       - diag3 cost 23,442. The se rear turned side-on again.
       - diag4, an edit, cost 20,727 and gave a crouch, not a rear.
       - That makes six misses on the se rear. The ground pound has cost 330,419 tokens so far.
       - Usable now: e F0-F4, se F2, and ne F2 and F3. diag1's se and ne F1, F4 and F5 are usable if scale-matched.
       - **What's next is the attack lane's to plan:** a fresh se-rear plan, put to Preston in its own session.
         - Preston 2026-11-06, in the attack lane: "Yes, after the test". The plan gets written (free) once the gorilla snap-punch test is done.
         - Any paid run in it gets priced to him there first. Nothing runs on the ground pound until then.
     - **Correction 2026-11-06 (Rhino session):**
       - This file still listed diag1 as the next job waiting on Preston's yes. That was stale, and I didn't check it against the attack log.
       - I asked Preston "Run the ground pound diagonals next (70k to 100k, worst case about 175k)?" and he said "Yes, run it".
       - The attack lane declined to rerun a known miss. No tokens were spent.
       - Next time, check attack/LOG.md before quoting any attack job from this file.
     - **After diag1:** run 2 (s, n), and F5 drawn from F4 so the 0.12 s tremor flash doesn't jump. Not priced again yet; the old run-2 quote included ne.
     - Not packed. The attack lane will tell this session before it packs.
     - **When it is packed:**
       - The holds become 1,1,1,2,3,3 ticks, so the slam lands at 0.5 s instead of 0.7.
       - ground_pound joins tilt_anims.
       - `rhino_kit.gd` waits on frame 4 (`_wait_frame`), not on seconds, so the kit needs no change. The 0.12 s rise flash between stomps is in the kit.
   - **The other moves:** none started at 35.
   - **Death at 35:** paid, undecided.
3. **The new keys may not match their art.**
   - Key 1 is now dash, catch and throw; key 2 is now a slam plus 4 stomps.
   - The horn_toss and ground_pound animations were drawn for the old versions.
   - Which frames play during the new moves: not checked.
4. **Walk speed:** the walk is drawn for 0.48 m/s and the rhino moves at 3.5 m/s, so its feet slide. Preston's call: walk slower, add a run gait, or accept the slide.
5. **Shadow:** 1 px over the limit (camera lane, known since 2026-11-04).
6. **Sound:** 3 stomp options and a first pass of the key 1 sounds wait on Preston's pick (sound lane).
7. **The VFX** (hit and deflect sparks, impact puff, dust trail, stun loop, ground pound ring, from the packer's `fx()`) have not been looked at since the 35-degree swap.

## Next slices (pick one)
- **A. Walk leg rebuild, free** (Preston picked this, 2026-11-05).
  - Find out from the touch-up and walk lanes whether `walk35_touchup` is finished, then show Preston the packed walk
    next to the rebuild.
  - On his yes, the walk lane packs se, e and ne (only those walk rows change); then the import, rhino3d_check and
    game feel's turn test.
- **B. Keys 1 and 2 in-game check, free.**
  - Record the rhino doing the new dash-catch-throw and the slam plus 4 stomps from the chase camera.
  - List which frames and effects play and where art is missing, mismatched or at the old angle.
  - Show Preston a board and clip, so the next art spend goes where it shows most. Needs one Godot slot; about one working block.
- **C. Ground pound at 35, paid** (the attack lane runs it). Two Codex jobs, each needing Preston's own yes with no other paid job running:
  - Fix1 is done (61,810 tokens; e approved).
  - diag1 (se and ne, new sheet): 70k to 100k, worst case about 175k.
  - Then run 2 (s, n, F5 from F4), to be priced again.

**Not recommended now:** redrawing the rhino stills a second time with the gorilla's recipe (45k to 70k). The idle already turns with no pops, and the walk is built on the current stills, so it would have to be redone too.

Picked: A (Preston, 2026-11-05). It is done: all five walk views were rebuilt and packed.

**Slice B result (2026-11-06, Preston: "Start slice B"):**
- Capture: `tools/debug/rhino_moves_capture.gd` (a window, 30 fps). Raw output in `D:\dev\_scratch\rhino\slice_b\` (frames.csv, fx.csv, results.txt).
- Board: `review/moves_ingame_2026-11-06.png`. GIF: `review/moves_ingame_diag_2026-11-06.gif`.
- **Mechanics all work, at all 3 facings:**
  - Key 1 catches the dummy and throws it 3 m behind, stunned.
  - Key 2 slows both dummies in its circle for 2.5 s.
  - The jab hits for 30, with the spark at 0.20 s.
  - Busy: toss 0.9 s, pound 2.8 s, jab 0.5 s.
- **Every view has its own drawing.** horn_toss, ground_pound and horn_jab play their own s, se and e drawings; no view falls back to another.
- **The main problem: every move pops.**
  - The moves are the old upright angle; only idle and walk are tilted.
  - At every move start the rhino shrinks and flattens, and at every end it jumps back to the taller 35-degree idle.
  - The jab shows this most, because it plays about every 0.9 s in a fight, for the player and the bots.
- **The art reads acceptably apart from the angle:**
  - Key 1: the head-down frame holds through the dash, and it flicks on the catch.
  - Key 2: rear, slam, then 5/4 stomps. The high rear on F3 is the one the attack lane's fix1 corrects.
  - Jab: a small head dip, subtle in the front view.
- **Effects all fire on time:**
  - Key 1: dust trail on the dash, hit spark on the catch, stun loop on the thrown target.
  - Key 2: ring, slow disc, cracks and puffs.
  - Jab: hit spark.
  - The rock pop has not been delivered yet; impact_puff still stands in for it.
- Not checked: sound, and the match camera (the field test only).
- **Preston, 2026-11-06: "Price the jab first".** The attack lane was asked for a price on a 35-degree horn_jab: 5 views, 6 frames, the hit kept on F2. Pricing only; any run needs his own yes.
  - **Quote (attack lane, 2026-11-06):**
    - Three draw-only Codex sheets from views_cam35_touchup: e+se, ne+n, and s with a spare row. The old-angle jab is never sent to Codex. The finish is a free script.
    - First pass about 50k to 95k; with one or two fix runs about 80k to 150k. Cap 40k per sheet; worst case about 345k.
    - 6 frames, hit on F2, so the kit needs no change. The beats are the same as now but bigger, so the jab reads from the front.
    - It queues behind the gorilla strike's sheets 2 and 3. The attack lane picks the jab before the rest of the ground pound.
  - **Preston, 2026-11-06: "Yes, run the jab".** Passed to the attack lane word for word. Its rule is that it only starts a paid run on Preston's yes in its own session, so he must confirm there too. **He confirmed there (2026-11-06).**
    - Sheet 1 (se, e) and sheet 2 (ne, n) are prepared. They run after gorilla sheet 3 once the hub frees the slot.
    - The board comes to this session after the first jab sheet.
    - **Sheet 1 (se, e) done:** 27,796 tokens. Board `attack/rhino_l/jab35/s1/board_jab_3x.png`; it went to Preston from the attack lane.
      - The hit on F2 reaches 10 px (e) and 20 px (se) past the still. Feet stay on the still's band.
      - The se head swings toward side-on on F3 and F4; sheet 3 carries a second se take.
      - My read by eye: the F2 lunge reads clearly now (head low and forward, horn out), and the 35-degree angle and plating match the still.
    - Sheet 2 (ne, n) is running. Still inside the first-pass range.
    - **Final five-view set (2026-11-06):** `attack/rhino_l/jab35/final/` (jab/<view>_F0..F5, board, phone mp4).
      - Sources: s and the se retake from sheet 3, e from sheet 1, ne and n from sheet 2.
      - Hit F2; holds 2,2,1,2,1,1 at 2x, so 0.45 s with the hit at 0.20 s, and the kit needs no change.
      - Preston said "Also rhino jab works" in the attack lane. The pack waits on his yes on this exact set.
      - My read by eye: the lunge reads in every view, and the se retake holds its facing. n is the least visible from behind, as expected.
      - To check after the pack: the s F2 horn tip reaches row 172, 12 px below the feet row (F1 163, F3 and F4 161). No other view goes below 160.
      - **Total spend: 78,399 Codex tokens** (27,796 + 22,730 + 27,873), inside the first-pass estimate of 50k to 95k. The worst case was 345k.
      - **Preston, 2026-11-06: "Yes, pack it".** Passed to the attack lane word for word.
      - **Packed 2026-11-06 (attack lane):**
        - Only the horn_jab rows of rhino_kit_sheet.png changed, plus one .tres line: tilt_anims = ["idle", "walk", "horn_jab"].
        - Backup: `attack/rhino_l/jab35/backup_pre_pack/`.
      - **My checks after the pack:**
        - Import clean. rhino3d_check 64/64, rhino_basic_check 15/15, kit_api_check 31/31, match_check 67/67.
        - Re-capture: the jab now plays tilted in every frame at all 3 facings, and the pop into the idle is gone. Board: `review/jab35_ingame_2026-11-06.png`.
      - **Camera lane floor check (plant_test --anim=horn_jab):**
        - Only s F2 clips: about 2.7 texels of the horn tip are hidden by the floor, roughly 1 game px at 320x180, on a frame shown about 0.1 s.
        - F1, F3 and the other views don't clip. Up to about 4 rows below 160 survive.
        - Feet: every frame plants on the idle's spot, so no feet meta is needed.
        - **Preston 2026-11-06: "Leave it".** No art touch, no shader change. The 1 px clip stays.
        - Fix options that were offered:
          - an art touch so F2's tip stays within about row 164 (free);
          - a shader change that draws below-row pixels over the floor. That touches every machine, so it needs Preston's say-so.
        - Renders: `D:\dev\_scratch\camera-lane\rhino_jab`.
      - **Correction:** the per-frame labels on the first slice B board (`moves_ingame_2026-11-06.png`) never say "tilted", not even on the idle frames. My board script compared against "True", but Godot logs "true". The board's header line and my written findings were right.
    - It runs after the gorilla sheets.
    - Its board comes back here before any fix run past the first-pass range.
    - On pack, horn_jab joins TILT_ANIMS.

## Not verified by me
- The walk pack: rhino3d_check after it, and the turn test (the walk lane and game feel ran those).
- Whether `walk35_touchup` is finished or approved.
- The new keys' frames in game.
- Whether the effects suit the tilted views.

## MeshForge 3D test (started 2026-11-06, test only)
- From the hub, quoting Preston: "Talk to hollowtide creature factory session big discovery on animations and tools were going to use. Then try the suggestion."
- Plan: docs/research/3d-to-sprite-tools-2026-11-06.md (5 steps at the bottom). Work in `D:\dev\_scratch\rhino\meshforge\`. Nothing in the sheet, frames or packer changes, and nothing installs until Preston sees it beside the current rhino at game size.
- **Step 1 done (free):** `input/rhino_{s,e,n,w}.png` from the approved `take-a/views`.
  - Upscaled nearest-neighbour x8 at one shared scale onto 1024 px white squares, feet on one row. Built by `prep_views.py`, with the numbers in `prep.json`.
  - take-a was chosen because the earlier 3D test measured it at about 6 degrees of pitch, close to level. The cam35 views vary in pitch, so they stay the comparison target only.
  - Known flaws carried in: back 77 px tall, front 70, side 67.
- **Step 2 (paid, fal.ai key in his Chrome):** waits on Preston's pick of model and price. The slot is cleared: relayed by the hub, to "Can a MeshForge model (10 to 30 cents) run while a Codex job is going?" Preston said "Yes, alongside".
- Walk and attack lanes told it's a test.
- **Step 2 check on the live page (2026-11-06, his Chrome, nothing generated):**
  - Preston picked "TRELLIS 2, $0.30". The page confirms $0.30 at 1024, and it confirms his fal key is set (the key itself was not touched).
  - But TRELLIS 2 offers no extra-view slots, so it builds from the front view alone and guesses the sides and back.
  - Hunyuan 3D v3.1 Pro shows "+ Left / + Back / + Right". Its base is $0.375; the page says extra views add $0.15, and so does PBR. With only the front uploaded, the button read ~$0.525.
  - Rodin v2.5, Tripo and Meshy were not checked for extra views.
  - Stopped to ask Preston, as promised. The tab is left open with rhino_s uploaded and Hunyuan Pro selected; nothing runs without a click.
  - Upload note: Chrome uploads only from the session scratchpad, so the four inputs are copied to `scratchpad/meshforge/`.
  - Mapping for later: Left = w (head screen-left), Right = e.
- **Step 2 run 1, Preston "Hunyuan Pro, 4 views" (2026-11-06): failed before any charge.**
  - Set up as Hunyuan 3D v3.1 Pro with front s, left w, back n and right e, PBR off. The button read ~$0.525.
  - The slots share one hidden input (`#viewInput`). Each slot was armed by clicking it with the native picker stubbed out, then the file was uploaded; the stub was removed afterwards.
  - MeshForge then said: "Upload to fal storage failed: fal.ai rejected the API key (403)... User is locked. Reason: Exhausted balance."
  - So the fal.ai account is out of credit. Nothing was generated and nothing should have been charged.
  - Topping up is Preston's to do, at fal.ai/dashboard/billing. Then it's one retry from the library row (the inputs stay loaded while that Chrome tab is open).
- **Run 2, Preston "Topped up, retry" (2026-11-06):**
  - The old tab had closed, so the page was reopened in his Chrome and all four views uploaded again. PBR was off and the button read ~$0.525.
  - **Done, about 4 minutes later.** MeshForge reports "$0.525 spent on 1 paid runs". The model:
    - 500,000 triangles, 298,442 vertices, 1 mesh, 1 material with a colour map;
    - size 0.59 x 0.62 x 1.07 m; GLB 30 MB.
  - Rough first read from those numbers, not checked on a render:
    - Width and height against length come to 0.55 and 0.58. The take-a bounding boxes give 0.70 and 0.68 (72 and 70 against the side's 103).
    - So the model may be about 20% longer for its bulk than the drawings. Plates and outline pixels could account for part of that.
  - Not looked at yet (no screenshot). Judging it needs the GLB downloaded and rendered in Blender at 35.
  - **Preston 2026-11-06: "Perfect result now gorilla next with connector on gorilla session".**
    - Relayed to the gorilla session word for word, with the method: inputs, Hunyuan Pro with PBR off, the slot workaround, and the connector notes.
    - The rhino's next steps wait. The GLB download (30 MB, needs his yes), the Blender render of 8 views at 35, the rig and the side-by-side were not started.
    - The model stays in the MeshForge library in his Chrome.
- **Connector added, Preston "while thats going add meshforge connector" (2026-11-06):**
  - Ran `claude mcp add keyframe -- npx -y keyframe-mcp` in D:\dev
ew-mech-rpg, local scope (written to ~/.claude.json under that project). `claude mcp get keyframe` shows it connected.
  - It loads in new sessions started in that folder.
  - Gotcha from Hollowtide: it opens MeshForge in its own Chrome profile, where the fal key may not be saved.
  - To remove it: `claude mcp remove keyframe -s local`.
- **Step 4 tools (copied, not run):** in `meshforge/tools/`: Hollowtide's `tools/blender/render_creature_views.py` (8 ortho views, pitch setting, facing, frames mode), `tools/art/measure_views.py`, `tools/art/pixelize_views.py` and `tools/arena/downscale.py`. Copies only; the originals in Hollowtide are never edited.
  - Per Hollowtide via the hub: MeshForge's camera tilt shows no number, so the plan is the GLB rendered in Blender at 35. Hollowtide's lumpy fronts came from a text-prompt model, not the pixel step. Image-to-3D from real sprite views is untried.
- **Rig, walk and 35-degree render (side session, 2026-11-06, test only, all free):** everything in `D:\dev\_scratch\rhino\meshforge\`; nothing in the game, sheet or packer changed.
  - **Connector gotcha:** the keyframe connector could not open its Chrome, because an idle session ("Redraw the mech fleet at 35 degrees") still held its profile (`~/.keyframe-mcp/profile`, Chrome exit code 21). Its library also held no rhino. Instead, MeshForge in Preston's normal Chrome has the same scripting API (`window.meshforge`, the same calls the `meshforge_*` tools make), so the work was driven there through Claude in Chrome.
  - **Download gotcha:** Chrome saves to `D:\user\Downloads` and asks where to save; the 3:05 PM 31 MB GLB was there all along. Chrome then held the page's second download, so the final walk came across as sampled bone poses (`glb/walk4_samples.json`, checksum checked) and `tools/patch_walk.py` wrote it into a copy of the first export.
  - **Rig:** the reduced 40k copy (library `c0b0320ea625`), quadruped template, facing +z. The auto-fit put the front legs under the jaw (z 0.27) and the head joint above the horn. Moved by hand onto the leg columns and knee discs (front z 0.045, rear z -0.32, x 0.165) and the head inside the head. Rigid prop bones: `horn` (head, 1,286 vertices) and `back_plate` (spine1, 2,906). Bone heat bind gave 2,443 stray vertices; `fixWeights` cleared all of them. Saved as new entries `rhino_s rigged walk test (40k)` and `rhino_s rigged walk4 lateral (40k)` (`b2373ab5682c`).
  - **Flex test:** four legs bend cleanly. The worst stretch was the back plate's rigid bone reaching into the rump during the big spine bend. In the walk, the worst stretch is 39, on inner belly surfaces.
  - **Walk 1, MeshForge preset (rejected by the numbers):** the preset has no gait setting and swings diagonal pairs almost together, close to a trot (RF with LH, then LF with RH). At stride 0.33: lift 0.8 px, planted 1.0 px a frame (0.16 m/s). Kept in `preset_walk/`.
  - **Walk 2, custom keyframe spec (`walk4`, now `walk`):** a lateral-sequence four-beat walk in the game walk's order and timing: LF f1-3, LH f3-5, RF f5-7, RH f7-1. Each leg is a two-bone solve fed to MeshForge as joint aims. Feet slide back in a straight line during stance (A 0.078 m, body 1.5 cm low), lift 36 mm, with a small hip roll and head nod and a straight tail that only swings. MeshForge: feet on the floor (0 to 1 mm), loop closes within 2 degrees, legs at most 98.8% of full reach.
  - **Render:** `tools/render_rhino35.py` (Blender 5.2, Workbench, ortho at exactly 35 degrees, 8x supersampled, one scale for all views: the side length is 103 px, 1.04 cm of model a texel). The export carried a stray 2 m icosphere, which the script drops. Use absolute output paths; Blender ignores relative ones.
  - **Finish:** `tools/finish35.py`. The material comes from the flat render, the tone from the studio render's light. Within each material the tones follow the approved still's shares for that view, and the walk reuses the rest pose's cut points. Then Hollowtide's `pixelize` and the rhino's own `selout`. Colour-share gap to the stills: flat 0.81, studio 1.23, toned 0.17.
  - **Results against `views_cam35_touchup` and the packed `walk35_touchup` (`finish35/report.json`):**
    - Same body in every view: the 3D w, sw and nw match mirrored e, se and ne at 0.998 to 1.0, by construction.
    - Size (3D vs current): s 58x70 vs 67x84, se 85x72 vs 85x83, e 104x70 vs 103x75, ne 85x88 vs 83x103, n 58x93 vs 65x106. The side matches. The model is about 13% narrower than the drawings and lower at 35 (the earlier width-to-length reading, 0.55 vs 0.70). The 3D also has n taller than s (93 vs 70), so the current stills' n-taller-than-s is real perspective, not drift.
    - Outline IoU vs the current stills: e 0.86, s 0.70, se 0.68 (0.77 best shift), ne 0.70 (0.76), n 0.69.
    - Fronts are not lumpy: one 4-connected piece in every view, edge roughness equal to the stills (s 3.9 vs 3.9), stray pixels 2.3 to 5.9% (stills 3.4 to 6.3%).
    - Feet: planted step per frame s (0, -1.81), se (-2.11, -1.30), e (-2.99, -0.09), ne (-2.11, 1.12), n (0, 1.62), against the playbook's (0, -1.72), (-2.12, -1.22), (-3, 0), (-2.12, 1.22), (0, 1.72). Planted feet vary by at most 0.75 px per view. Side speed 0.478 m/s against 0.48. Front planted feet ride 37 to 51 mm (rest 45) from the hip and chest sway.
    - Ground rows: 3D bottoms s 161-162, se 157-162, e 158-160, ne 156-161, n 159-162; current s 160-163, se 157-162, e 158-160, ne 157-162, n 160-163. Bob 1 to 2 rows (current 1).
    - **Short of the stills:** interior ink 3.7 to 6.6% against 9.6 to 12.8% (plate seams are missing, so plates merge); eyes 0 px in every view (the red eye is lost in the shrink); the front is narrower than the drawings. Walk frames differ from their rest pose more than the current walk does (alpha IoU min 0.85-0.90 vs 0.92-0.95), because the current walk pastes the still's body over drawn legs.
  - **Boards sent to Preston:** `board_stills_35.png` (current vs 3D, game size and 3x, all 8 views), `board_walk_35.png` and `walk_35_compare.gif` (s, se, e, ne, n, current above, 3D below, 8 fps).
  - **Belly fix (Preston: "the belly near the rear legs moves when it shouldnt"):** two causes, measured in Blender.
    - **Weights:** bone heat tied belly skin to the thigh, shin and foot bones, so the belly was dragged up to 143 mm. `tools/fix_belly.py` measures each leg's column from its foot plate. It moves leg weight outside the column, or above a cut height, to hips (rear) or chest (front), with a 2 cm soft edge. Cut 0.30 m (belly only): rear belly worst 143 mm to 5.6 mm, no vertex over 8 mm. Cut 0.22 m (haunch and shoulder plates rigid too): haunch vertices over 8 mm 2,051 to 179, worst 37.5 mm.
    - **Body sway:** most of what still read as movement was the walk's own hip roll, chest and head nod and 6 mm bob. A still-body walk (those channels held, hips at a fixed 0.316 m) keeps the same feet: side step -2.99 px a frame, 0.478 m/s.
    - Body pixels changing per frame, top 60% of the sprite, sum of s, se, e, ne, n (`tools/body_motion_px.py`): before 2,294; belly fix 1,968; rigid plates 1,888; still body 226. The still body has no 1-row bob; the current walk has one, which could be added back as a whole-sprite shift.
    - GLBs in `glb/`: `rhino_s_walk4_bellyfix_40k.glb` (cut 0.30), `rhino_s_walk4_rigidbody_40k.glb` (cut 0.22), `rhino_s_walk4_nosway_rigid_40k.glb` (cut 0.22, still body). Results in `v2_lateral/`, `v3_bellyfix/`, `v4_rigid/`, and the still body in `render35/` and `finish35/`.
    - Sent: `belly_fix_before_after.gif` (4 rows at 4x, s, se, e, ne) and `walk_35_compare.gif` re-made with the still body.
