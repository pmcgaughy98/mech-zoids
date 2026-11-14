# Chameleon (`chameleon_m`): status, 2026-11-05

Written by the Chameleon session's first turn (stock-take only, nothing built or spent).
Kit: `docs/plan/moba-kits.md`, section "Chameleon (`chameleon_m`), ode to Loki".
Facts below were read from the main checkout `D:\dev\new-mech-rpg`. This file sits in the session worktree because a
guard hook blocks writes to the main checkout from here; move it to `docs/art/moba/chameleon_m/` there.

## What exists

| Thing | State | Where |
|---|---|---|
| Approved still | **take-b**, approved 2026-11-03 ("keep chameleon b"). Eight views at the old low camera (about 6 degrees), all feet planted, 16 colours. | `take-b/views/`, `take-b/APPROVED.txt` |
| Flaws Preston accepted | side views 59 px tall vs front 65; top-five colour share 62%; raised back corner of the helmet; back view shows toes. | `take-b/APPROVED.txt` |
| take-a | Superseded (one front foot lifted mid-step). Keep as history only. | `take-a/` |
| 35-degree stills | **Accepted 2026-11-06** ("Accept them"): five views, canvas 160, feet row 140. | `take-b/cam35/fixed/` (`APPROVED.txt`) |
| Animations | **None.** No `anim/` folder; nothing under `docs/art/moba/walk/` or `attack/`. | |
| In the game | **No.** No `art/machines/chameleon_m/`, no `chameleon_kit.gd`, no 3D pack. Kits in code today: rhino, gorilla, fennec. | |

Approved view sizes (W x H): s 49x65, se 65x62, e 84x59, ne 65x62, n 47x63. Canvas 160, feet row 140.
Fleet guide for 35 degrees: L 84, W 49, H 57; expected sizes s 49x94, se 69x86, e 84x74, ne 69x86, n 49x94.
The original eight-view sheet cost 91,991 Codex tokens, the most of the 11 fleet machines.

**Game hooks that already exist and the kit will lean on** (both in shared files, so other lanes own them):
- Fog of war with a per-machine `vision_radius`, set from `MatchRules.vision_machine` (12 m) in `match_director.gd`.
  The passive (sees farther) and the blind (sight shrinks) are changes to that number. Map lane builds the vision; game
  feel lane owns `match_director.gd`.
- A `seen` flag on each enemy machine in `machine_test_player.gd` ("false while the map lane's fog hides this enemy").
  Camouflage would most likely set this from the kit side. Game feel lane.
- The fade itself would be a shader on the shared sprite (`directional_sprite_3d.gd`). Game feel lane.

## What the kit doc leaves open (all Preston's calls)

1. **No numbers anywhere.** Cooldowns are words (short, medium, long); no damage, slow, speed burst, range or radius.
   For scale, the game today has: sight 12 m, basic attack every 0.9 s, fennec slows of 1.5 and 2 s.
2. **Passive:** how much farther it sees than 12 m, and how much longer a spotted enemy stays revealed.
3. **Camouflage, what each side sees:** the enemy (gone completely, or a faint shimmer up close?) and the ally (see-through?).
   Fade-in time, how long moving can last, whether taking damage breaks it, whether towers see through it.
4. **Camouflage counters** are named (squirrel tail alarm, fennec ears, wolf scent) but not how a revealed chameleon looks.
5. **Tongue lash:** range and width; whether it needs a mouth-open pose (attack lane) or is effect-only from the head.
6. **Colour flash:** cone size, blind length, the bonus out of camouflage, and what a blinded player sees on screen.
7. **Shared camouflage:** radius, length, how much slower allies move.
8. **Walk speed:** the kit says "slow deliberate steps". The team-wide feet-slide speed call (walks drawn at 0.48 to
   0.56 m/s, machines move at 3.5 m/s) is still open and affects this machine most.

Getting it into the game at all is a chain: 35-degree stills, then game frames, walk (walk lane) and attacks (attack
lane), then kit code (game feel lane). This session can own the look and the proposals; the code belongs to those lanes.

## Basic attack (Preston, 2026-11-05: every mech session builds its machine's basic)

**Preston picked A, eye pulse (2026-11-05).** It's in the kit doc's chameleon table. **Still blocked:** the chameleon
has no game frames or kit script yet, so the basic can't be built or played until the 35-degree redraw (slice 3)
lands. The pulse effect itself can be drawn before then, for free. The two proposals as they were offered:

| | A. Eye pulse (recommended) | B. Tongue flick |
|---|---|---|
| What | The glowing eye turrets fire a small turquoise pulse | A short tongue snap, the long lash's little brother |
| Range | 5.5 m (ranged, like most MOBA supports) | 2.0 m (melee) |
| Damage | 24 a hit (below the stand-in's 30: it is a support) | 30 a hit |
| Every | 0.9 s (the game's default) | 0.9 s |
| Frames | a small recoil only, plus a pulse effect | a mouth-open attack pose (attack lane) |
| Why | Pokes from where it scouts; the eyes are already its signature (passive) | The animal's own weapon, but it blurs into slot 1 |

Either one breaks camouflage on the windup (the game feel lane wires that).

### Eye pulse effect: drawn 2026-11-06
- **Art:** `art/fx/moba3d/chameleon_pulse/`.
  - `pulse_sheet.png`: 16 angles x 4 frames, 40-texel cells, 50 ms a frame.
  - `pulse_burst_sheet.png`: row 0 is the eye flare (4 frames, 40/50/60/60 ms); row 1 is the hit (5 frames,
    30/40/50/60/70 ms).
  - Drawn by `tools/art/draw_chameleon_pulse_fx.py` at the chameleon's texel, 0.020 m.
- **Board, GIF and scores:** `pulse/`.
- **Checks:** PASS.
  - Only the chameleon's five colours (#141218 ink, #1fc8b4, #9ff5e6, #fff1a0, #fffbe6), with an ink edge all round.
  - No cell touches its border, and the core sits within 0.5 texel of the centre.
  - Every angle points within 2.8 degrees of its row.
  - The shot is 0.34 m long and 0.16 m wide, against the dart's 0.32 by 0.16.
  - The hit is 0.44 m across, against the dart's 0.42.
  - The halo is 0.30 lighter than lane grass.
- **Not done:** it isn't in the game (no chameleon kit or frames yet), and it isn't seen at the 35-degree tilt or
  from the real chase camera. No sound cue.

Measured before drawing (the house reference):
- **House reference:** the fennec's basic, its dart, in `art/fx/moba3d/fennec_bolt/`, played by
  `scripts/moba3d/fennec_bolt.gd` at 14 m/s.
- **Dart sheet:** `dart_sheet.png` is 160x640, one row per screen angle (`ANGLES := 16`, 22.5 degrees each, 0 pointing
  right, turning clockwise), so each row is 160x40. Four colours: body #a46bff, ink #141218, pale #e0c8ff, core #f6fffb.
- **Hit sheet:** `dart_hit_sheet.png` is 6 frames of 40x40, drawn 14 to 26 px across, 5 colours.
- **House rules** (from `tools/art/draw_fennec_kit_fx.py`): 50 texels a metre, a one-texel #141218 ink edge, and the
  machine's own colours.
- **Plan for the pulse:** the same layout (16 angle rows plus a 6-frame hit sheet) and a muzzle flash at the eye
  turret. The core is the lens's pale gold-white (#fffbe6, #fff1a0) with a turquoise halo (#9ff5e6, #1fc8b4) and the
  ink edge. Write it as `tools/art/draw_chameleon_pulse_fx.py` into `art/fx/moba3d/chameleon_pulse/`, then a board on
  lane grass.

## Next slices (pick one)

**1. Camouflage look board. Free.** **Done 2026-11-05:** boards and GIF in `camo/`, notes and scores in
`docs/reference/camouflage-reads-2026-11-05.md`. **Preston picked B, colour match (2026-11-05).** **Shader built and
checked 2026-11-05:** `scripts/moba3d/tilted_sprite_camo_3d.gdshader` with `tools/debug/chameleon_camo_check.gd` (PASS:
hidden 0%, tell 18%, ally 94%, eyes kept). It's handed to the game feel lane and not wired to any machine yet.
Synthesis pass: how two or three shipped games show stealth to the enemy and to allies (marked read versus general
knowledge), then three fade looks on the approved e and se views, each shown as "enemy sees" and "ally sees", at full
size and game size. Example looks: dither dissolve, ground-colour shift with an edge shimmer, see-through with a lens
glint. Tools: Python and PIL for the board, Director's Lookbook for the shimmer palette, the `watch` skill if a gameplay
clip helps; nothing paid. Output: one board PNG, a note in `docs/reference/`, and a short spec for the game feel lane.
One session, no spend.

**2. Tongue lash and colour flash effects, plus a numbers proposal. Free.**
Effect frames drawn in the approved palette (PixelLab's free pixel and VFX workbenches, or Python like
`tools/art/draw_fennec_kit_fx.py`), shown on the approved views. Plus a filled-in table of proposed numbers for all
five slots, anchored to the game's current values, labelled as proposals for Preston to edit. One session, no spend.

**3. The 35-degree redraw. Paid (Codex).**
The fleet recipe in `cam35_fleet/HANDOFF.md`: one image, finished and checked on a board. This is the slice that unblocks
frames and getting into the game. Mech sessions own their machine's redraw (hub, 2026-11-05).

**Price, measured 2026-11-06 (Preston: "Yes, price it"):**
- **What past runs cost:** the nine 35-degree runs so far each cost 55,009 to 78,028 Codex tokens (mean 64,474).
  - The nine: drone, rhino, gorilla, fennec, wolf, hippo, kangaroo, pangolin, lobster.
  - Second images cost 54,566 (gorilla), 57,229 (kangaroo) and 63,527 (pangolin).
- **Why this one sits high:** the chameleon's original sheet cost 91,991, the most in the fleet; the others cost
  49,222 to 72,216. On the six fleet machines, a 35-degree run cost 0.94 to 1.44 times its original sheet.
- **One image:** likely 65k to 95k. Run with an 80k cap, as the pangolin was; a capped run can land about 75k past its
  cap, so the worst case is about 155k.
- **Second image** (side view only, if it misses): about 55k to 65k more. Two images likely total 120k to 160k, with a
  worst case of about 310k.
- **Risk of a second image:** 3 of the 9 machines needed one. The side view is where long, low machines miss:
  - The pangolin's e view stayed at the low camera twice. It's the closest shape to the chameleon.
  - The fleet notes name the chameleon as one of four machines at risk of the "side view drawn about 10% small" fault.
  - The brief should use the fix the fleet lane proposed: state the side-to-front length ratio, and size the sheet
    from the side view.
- **Fleet allowance:** the fleet total was 569,068 after the pangolin, against 0.9M to 1.5M. This fits. A third image
  would need Preston's new yes.
- **Money:** the fleet counts Codex in tokens against the Codex usage limit. No dollar rate is written down in the
  project.
- **Needs:** Preston's yes to run, and a free paid slot from the hub (one Codex run at a time across lanes).
- **Slot (hub, 2026-11-06):** not free yet.
  - The attack lane holds it for gorilla strike sheet 3, then up to three rhino horn jab sheets (40k cap each).
  - The chameleon is next in line if Preston says yes.
  - Don't start until the hub sends word that the slot is ours.
- **Queued (Preston, 2026-11-06: "Yes, queue it").** One image, 80k cap. A second image needs his yes again.
- **Prepared for free, ready to run:** `chameleon_m/take-b/cam35/`.
  - `prep_machine.py` wrote `refs/`, `palette.json` (all 16 colours, none outside) and `guide_sizes.txt`.
    - Hull guide at 35 degrees: s 49x80, se 66x76, e 82x64, ne 66x77, n 49x77.
    - The side view grows only about 5%, because the tall coil already sets its height. What has to change is inside
      the outline.
  - `prompt-sheet.txt` is adapted from the pangolin's. Following its lesson, the side view has its own paragraph: the
    back must show as a wide lit band, with the band's far edge as the top outline, not the spine.
  - `brief.txt` uses take-b's own finishing scripts and a 160 canvas with feet at row 140.
    - Scale anchor: the average of s/49, n/47 and e/84.
    - The raw e/s ratio is reported before the shrink.
    - New `side.txt` test: the back band's depth in rows (0 = miss) and how far the far feet sit above the near feet.
  - At run time the guide was remade as one 35-degree row (`hull_guide.py guide ... 35 35`, top row). Prep's two-row
    guide is kept as `guide_6and35_prep.png`.
- **Run 2026-11-06, 08:15 to 08:25: 63,803 tokens** (80k cap, `run_codex_capped_d.sh`).
  - **Result: near pass.** s, se, ne and n read from above at their target heights.
  - The side view shows its back as a lit band, but it came back 14% short (85x51), with short legs.
  - The lenses are about 30% small in s, se and e.
  - Detail and options: `take-b/cam35/LANE_REPORT.md`. Board: `take-b/cam35/board_cam35.png`. Views:
    `take-b/views_cam35/`.
  - Preston picked "Lens fix, then turn test" (2026-11-06).
- **Lens fix done (free):** `take-b/cam35/fixed/`, made by `fix_lenses.py`.
  - Lenses: s 30 + 33, se 40, e 35, with the glint back.
  - Outline and palette unchanged.
- **Turn test (game feel lane, 2026-11-06): pass.**
  - No errors; feet hold on row 140; 25 px steps around e, as on the lobster.
  - The HP bar at 1.71 m clears, but only just (it needs 1.70 m at the game camera).
  - By eye the chameleon visibly ducks at e and w: the short side view.
  - Detail: `take-b/cam35/LANE_REPORT.md`; clip contact sheet `take-b/cam35/turn_contact.png`.
- **Accepted (Preston, 2026-11-06: "Accept them").** `take-b/cam35/fixed/` is the final 35-degree set, marked with
  `APPROVED.txt`. Total cost: one image, 63,803 tokens. The short side view is known and accepted.
- **What this unblocks** (other lanes' work):
  - the touch-up lane's recolour;
  - the walk and attack frames;
  - the kit script, which lets the eye pulse and the camouflage shader be wired.
- **HP bar (game feel lane, 2026-11-06):**
  - The bar height comes from the map lane's `match_hud.gd`: 1.9 m times the size scale, so 1.71 m for M.
  - It clears the tilted chameleon, which needs 1.70 m. Look again once the chameleon is playable.
  - If it looks cramped, the fix is a per-machine bar offset in the HUD, which is the map lane's job.
