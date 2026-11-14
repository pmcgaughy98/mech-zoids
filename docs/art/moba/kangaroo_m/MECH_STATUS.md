# Kangaroo (`kangaroo_m`): status, 2026-11-05

## 3D status, 2026-11-11 (kangaroo-3d session). Everything below this section is the 2D sprite era and is history.

**Registered in the arena as an authored 3D body.** `art/arena_models/kangaroo.glb` (19 clips, 34 bones, one mesh,
one material), `art/arena_models/kangaroo.events.json`, and its row in `roster.json` and `authored_profiles.json`.
Registered with `tools/art/build_arena_roster.py --register kangaroo`. Backup of the two registry files as they
were: `D:/dev/_scratch/kangaroo-3d/register-backup-2026-11-11/`. Source and profile:
`D:/dev/_scratch/kangaroo-3d/game-export-r8/`.

- **Clips:** Idle, Idle_Fidget, Walk (a hop), Walk_Back, Strafe_Left, Strafe_Right, Jab_Left, Jab_Right,
  Jab_Right_Quick, Hook_Right, HopJab (slot 1), TailKick (slot 2 and the finisher), Guard and Guard_Counter (slot 3),
  Ring_Cast (slot 4), Hit_Front, Hit_Heavy, Stun, Death. All in place; hops authored at 3.5 m/s.
- **Basic attack (Preston approved 2026-11-11):** a three-beat chain, Jab_Left, Jab_Right_Quick, Hook_Right.
- **Not done:** the kit code is not ported to MechModel3D (game feel lane, queued behind the rhino), so in the
  match it stands, hops and turns but its abilities do nothing. No effects yet. Size is 1.70 m, scale 1.0; the
  roster's M cap is 1.65 m and Preston has not set the size.
- **Rig:** Meshy Smart Rig's 29 bones kept, plus a 5-bone tail. The gloves were cut free of the thighs and the
  thigh tops repainted (free touch-up, Preston's pick). Working files and round notes:
  `D:/dev/_scratch/kangaroo-3d/` (`ROUND1_NOTES.md` to `ROUND9_NOTES.md`).
- **Checks after registering:** `arena_roster_check.gd`: the kangaroo's three checks pass. Video in the real arena:
  `D:/dev/_scratch/kangaroo-3d/out/kangaroo_r8_in_arena.mp4`.


Owner: the kangaroo refinement session (one session per mech, Preston 2026-11-05). Updated after slice 1 (free, no paid tools).
All paths below are in the main checkout, `D:\dev\new-mech-rpg`.

## What exists

**Approved design:** `take-a/`. `APPROVED.txt`: Preston 2026-11-03, "good keep it". The eight low-angle views are in
`take-a/fixed/` (the back view's gloves tucked in by hand in Aseprite, `take-a/aseprite/n_gloves.aseprite`).
`take-b/` holds only two reference images; it is not a current take.

**35-degree stills: accepted, and packed as game frames (slice 1).**
- `take-a/cam35/take2/fixed/` (s, se, e, ne, n), in 160 px cells with the feet on row 140. Preston: "Yes, accept it"
  (2026-11-05). The other three views are mirrors.
- How it got there: two Codex images (take 1 partial, take 2 better, 135,257 tokens in all), then the free fixes Preston
  asked for: front eyes repainted to 2 + 2 px, one despeckle pass on all five. Palette clean, sizes match the approved views.
- Turn test by the game feel lane: PASS. The side view (e) is still a little level (77 px tall against the guide's 83);
  it reads as turning into depth, so it was left.
- Full record: `take-a/cam35/take2/LANE_REPORT.md`. Board: `take-a/cam35/take2/board_cam35_fixed.png`.

**Animations at 35 degrees:** none. No hop, walk, idle or attack frames.

**In the game: frames, kit and match code done; waiting only on a team spot.** (Preston: "Into the match", 2026-11-05.)
- `art/machines/kangaroo/kangaroo_frames.tres` and `kangaroo_sheet.png` (imported), made by `tools/art/pack_kangaroo_3d.py`.
  `idle_<view>` and `walk_<view>` for s, se, e, ne, n, one frame each, the accepted stills as drawn. Both tilt.
- **The walk is a stand-in:** the still, so a moving kangaroo glides. The hop (slice 2) replaces it.
- `scripts/moba3d/kangaroo_kit.gd` (KangarooKit): sets the frames, the 160 canvas, feet edge 141 and size M (0.75 of the
  L rhino). No abilities and no basic attack of its own, so the match gives it the stand-in test shot.
- Check: `tools/debug/kangaroo_frames_check.gd`, 45 PASS, 0 FAIL (every frame matches its still, all 8 facings show a
  picture standing and moving, the kit sets the M canvas).
- Feet meta: the camera lane's in-game measurement, `{"front": 20, "rear": -18, "front_half_width": 18, "rear_half_width": 4}`.
  The rear reaches back to -18 because the kangaroo stands on its tail too. Planting 0.2 px; the shadow passes in every view.
- The game feel lane added it (2026-11-05): `MatchTeams.machine_kind` returns "kangaroo", `_make_bot` installs
  KangarooKit. Their probe: a red kangaroo bot enlists and walks 34 m with its wave; match_check 67/67.
- **Team spot: Preston's call**, which the game feel lane has put to him. Proposal: red ["rhino", "gorilla", "kangaroo"],
  replacing red's fennec. Until then no match spawns it. Not looked at in the running game yet.
- No MatchRules.TIERS row yet, so its slots would default to 9 s; no abilities exist, so it doesn't matter yet.

**Older work, not this design:** `art/machines/kangaroo_m/` is the October 2D battle version (8 views from
`docs/art/2d/kangaroo_m/p74_detail`, plus idle, jab, flak, kick, hit and death clips). Its effects in
`scripts/battle/vfx_recipes.gd` (piston-vent jab, Pouch Cannon, jet-boosted kick) belong to that version. The Pouch
Cannon is not in the current kit. Left alone.

## What the kit doc leaves open (`docs/plan/moba-kits.md`, Kangaroo section)

These are Preston's calls. Proposals are labelled.
1. **Numbers:** cooldowns are words (short, medium, long). No damage, hop distance, ring size or ring length.
2. **Rhythm passive:** how many stacks fill it, whether stacks fade out of combat, and which art the full-stack kick
   uses. Proposal: 4 stacks, fade after 4 s out of combat, and the kick reuses the tail kick frames.
3. **Basic attack:** not named. Proposal: a single jab, the first punch of the "hop and jab" flurry.
4. **How it moves:** the kit says "big hops", but nothing says whether its movement is a hop or a walk. Proposal: a hop.
   It suits the animal and may help the foot-slide problem: if one hop covers about 1.75 m in 0.5 s, that matches
   3.5 m/s with the feet down for only a short part of each hop. The 3.5 m/s speed call is still Preston's.
5. **Art list:** hop and jab, tail kick, guard, the ring effect. The finishing kick reuses the tail kick.

## Known catch for a hop (game feel lane)

`directional_sprite_3d.gd` jumps a walk half a loop forward when the view flips into a mirrored side (sw, w, nw), to
keep the same foot up. A hop has no left and right halves, so that would jump it from take-off to mid-air. It needs a
per-machine switch (offset 0). That file is the game feel lane's; ask them, don't edit it.

## Basic attack (Preston, fleet-wide, 2026-11-05, relayed by the game feel lane)

"we need basic attacks. Rhino, gorilla will be melee", and every mech session builds its own. The hook is
`KangarooKit.basic_attack(target)` plus `basic_cooldown` and `basic_range`; frames come from the attack lane, sounds
from the sound lane. Proposal (numbers are Preston's): a melee jab, 1.4 m reach, 0.8 s cooldown, 45 damage. The rhythm
passive counts jab hits; at 4 stacks the next basic is the tail kick (90 damage, about 2.5 m knockback); stacks fade
after 4 s without a hit. Until the attack lane draws a 35-degree jab, it lunges on the still.

## Next slices (Preston picks one)

1. **Kangaroo standing in the match (free). Frames and kit done; roster lines asked of the game feel lane.** Done when
   you can press play and see it turn in the match.
2. **Hop cycle at 35 degrees (paid).** A synthesis pass first (how shipped games draw hopping movers, measured against
   the walks we have), then one drawn hop loop. A pose change is a real redraw, so it needs an image tool. Codex has cost
   57k to 78k tokens per kangaroo image here; quote the worst case as about 155k with the overshoot. Needs the hub's
   free paid-job slot, Preston's yes, the walk lane told, and the game feel lane's hop switch.
3. **Rhythm and ring effects (free).** Stack pips for the passive and the boxing ring outline, drawn with free pixel
   tools and the project's own effect scripts. Only worth doing after slice 1, so they can be seen in a match.

Recommended order: finish 1, then 3 or 2.

## Handover from the wolf session

The wolf session answered on 2026-11-05: the 35-degree work is done and accepted, and nothing is still open. It matches the lane report.
- Current board: `take2/board_cam35_fixed.png` (approved, take 2 raw, take 2 fixed). `take2/board_cam35.png` is the
  older board (approved, take 1, take 2 raw).
- Accepted set: `take2/fixed/`. `take2/views/` and `take2/slices/` are Codex's output from before the fixes, kept as a
  record. `take-a/views_cam35/` is take 1, which was rejected. `take-a/fixed/` (the approved low-angle set) was never touched.
- Scripts: `take2/fix_take2.py` writes `fixed/` from `views/`. Running `take2/cam35_board.py fixed` rebuilds the fixed board.
- Nothing is being edited, no process is running and no paid job is open. A third paid image was offered, and Preston didn't choose it.
- Still to do: install `fixed/` in 160 px cells (not the wolf session's job). Nothing is committed. The fleet lane owns the fleet token total.
- `art/machines/kangaroo_m/` is not the wolf session's work; it predates the redraw.
- Also listed in the kangaroo row of `docs/art/moba/cam35_fleet/HANDOFF.md`.
