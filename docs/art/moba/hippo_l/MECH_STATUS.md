# Hippo (`hippo_l`): status, 2026-11-05

## 3D body, 2026-11-11 (hippo-3d session)
The sprite notes below are history: machines are 3D models since 2026-11-09.
- **Registered in the arena** as an authored trial: `art/arena_models/hippo.glb`, `hippo.events.json`, the hippo row in
  `roster.json` and `authored_profiles.json`. Source and profile: `D:/dev/_scratch/hippo-3d/game-export-r6/`.
  Backups and undo steps: `D:/dev/_scratch/hippo-3d/backup-pre-register-2026-11-11/` and `backup-pre-register-r6-2026-11-11/`.
- **Body:** the catalog Hunyuan model reduced to 41,434 triangles, one mesh, one material, one 2048 atlas, 23 bones
  built in Blender. Legs and jaw are cut free from the hull and capped; the mouth has a painted inside.
- **Clips (13):** Idle, Idle_Fidget, Walk (a trot at 3.5 m/s), Walk_Back, Strafe_Left, Strafe_Right, a three-move basic
  chain (bite hit 0.26 s, Jaw_Swing hit 0.24 s, Stomp hit 0.42 s; Preston, 2026-11-11: "Bite chain"), Hit_Front,
  Hit_Heavy, Stun, Death. All numbers are placeholders.
- **Not done:** the kit port onto MechModel3D (game feel lane), the four ability clips, effects, colour and emissive
  (look lane), a real-match video, the match roster.
- Round notes: `hippo-3d-round1` to `round6` in the hub's shared notes folder.

Hippo session (per-mech refinement lane). Stock-take only: nothing built, nothing spent.

## What exists

**Approved take: take-b.** Preston, 2026-11-03: "perfect keep it". Low-angle views in `take-b/views/`.
- ne and n carry capped detail ink (Preston, 2026-11-04, "Keep capped ink"). His originals: `take-b/views_pre_ink/`.
- Known shorts written at approval: back views taller than the front (76-77 px against 70), small amber eye
  slivers on the rear diagonals, speckle on the back deck, profiles 62 px against 70.

**35-degree stills: final set is `take-b/views_cam35_touchup_shade1/`** (s, se, e, ne, n).
- Chain: one Codex image (71,498 tokens) gave `views_cam35/`, accepted after the turn test (2026-11-05). The
  touch-up lane's pass gave `views_cam35_touchup/`; the 1 px shade pass on that gave shade1, kept by Preston
  2026-11-05 ("Keep 1 px version").
- Known shorts: s still a little light; shadow purple below the approved share in ne and n; more 1-2 px specks than
  the approved views; the side view (e) came back short and low (71 px tall against the guide's 82, 110 long
  against 123), so the biggest height step around the turn is e to ne, 28 px.

**Animations drawn**
| Move | Low angle | 35 degrees |
|---|---|---|
| idle | none | done: `take-b/anim/idle35/`, 5 views x 5 frames, from shade1 |
| walk | none | **in the game.** Approved by Preston 2026-11-05 ("Approve, to touch-up", then "Approve, pack it" on touch-up's cleanup plus 1 px sway). Packed by the walk lane: walk_s/se/e/ne/n, 8 frames each at 8 fps, looping; source `take-b/anim/walk35/frames/`, backup and restore in `take-b/anim/walk35/backup_pre_pack/README.txt` |
| yawn, belly flop, chomp, wallow pose | none | none |
| death | none | none; a paid 35-degree death is undecided |

**In the game:** `art/machines/hippo/hippo_frames.tres` holds idle and walk in all five views (65 frames, sheet 1536x1920),
`tilt_anims = ["idle", "walk"]`, feet metadata unchanged. Checked 2026-11-05 by measuring the sheet in Python (`D:\dev\_scratch\hippo\check_walk_pack.py`): no empty frame, walk size within 3% of idle, tops within 1 px, lowest row 158-164 against the idle's 161 (steps). Godot not run yet (two Godot processes were already open), so `hippo_sheet.png` reimports on the next run. Only test scripts load it (`cam_angle_test`, `plant_test`, `ult_view_test`,
`cam_angle_set_test`). `scripts/moba3d/hippo_kit.gd` (2026-11-05) holds the melee bite basic only, plus the walk rate; check `tools/debug/hippo_bite_check.gd`, 15 of 15 PASS. Adding the hippo to the match waits on Preston's yes: the game feel lane is putting it to him with the kangaroo, hummingbird, shoebill and falcon, then adds it to the roster and Tab. Already done by that lane (2026-11-05): `MatchTeams.machine_kind` returns "hippo" for HippoKit (before, it read as the rhino), and `MatchRules.TIERS` has the hippo row: 1 short, 2 medium, 3 medium-long, 4 long (5 / 9 / 12 / 40 s), marked as the doc's words with the rework undecided. kit_api_check 0 failures, match_check 67/67. Sound (sound lane, 2026-11-05): free placeholder bite sounds in `audio/sfx/hippo/`, "bite" a deep clamp and crunch, "bite_whiff" a heavy clap; wired in `kit_audio.gd`, `check_kit_audio.gd` PASS. Preston has a page of B options that may swap the files under the same names.
`match_director.gd` and `machine_test_player.gd` don't name the hippo, so it is likely not playable in a match.
Not run to confirm.

## What the kit doc leaves open
Kit: `docs/plan/moba-kits.md`, Hippo section (passive territorial meter, 1 gaping yawn, 2 belly flop,
3 wallow, 4 chomp).
1. **It predates the 2026-11-04 rule.** The rule: the animal gives the body and at most one trait, the rest comes
   from a power theme. All five hippo pieces are animal and physical (jaws, mud, flop). The only rework idea on file
   is one line: "boiler body that vents steam" (`docs/plan/fennec-janus-kit-2026-11-04.md`). Undecided.
2. **Chomp overlaps the rhino.** The rhino's horn toss (Preston, 2026-11-05) now catches one target and flicks it
   behind, which is close to the hippo's clamp-and-fling. The lobster also owns the pull. Two "grab one and throw
   it" moves on the front line may read as one move.
3. **Passive:** which skill gets the bigger area and which gets the longer effect when the meter is full.
4. **Wallow:** does the mud stay put or follow the hippo; does healing stop when it steps out.
5. **Names and numbers:** all still plain descriptions; cooldowns are tiers; no damage or ranges.
6. **Art:** none of yawn, belly flop, mud patch, chomp and fling is drawn. The hub has held all 35-degree attack
   art until kits are redone (2026-11-04).
7. **Shared calls that touch the hippo:** walk speed (drawn 0.48-0.56 m/s, moves at 3.5 m/s) and the paid death.
8. **Basic attack:** Preston, 2026-11-05: "we need basic attacks. Rhino, gorilla will be melee", and each mech session builds its own. The doc says nothing about the hippo's, and he named only the rhino and gorilla as melee. He picked "Melee bite" (2026-11-05); recorded in the kit doc and built as the only piece of `hippo_kit.gd`. The passive meter fills on damage dealt, so the basic feeds it. Hook (game feel lane): `basic_attack(target) -> bool` in the kit, optional `basic_cooldown` and `basic_range`; the hippo also has to be added to the match by that lane.

## Next slices (Preston picks)
**A. Kit direction page (free, about 10 minutes of his time).** Two drafted takes side by side, with real proposal
names: keep the jaws and mud kit as is, or a steam-boiler rework under the 11-04 rule, plus a fix for the
chomp/rhino overlap. He picks one; nothing gets built on the kit until he does.

**B. Wallow in the game (free, one session).** `hippo_kit.gd` with slot 3 only: a mud patch on the ground, heal
over time inside it, enemies slowed. Effect only, so it needs no new body frames; it uses the idle. A synthesis
pass for the mud: ground-zone effects in 2 to 4 shipped games, measured, then drawn with the free PixelLab pixel
tools. The game feel lane hooks it into the shared match code; the sound lane gets cue names. The kit must set
`full_speed_walk_rate = walk_speed / 0.48` (the walk's stride in m/s, as `fennec_kit.gd` does), or the feet slide
the way the gorilla's do (walk lane, 2026-11-05). Best after A,
because wallow survives either kit take (a steam take would swap mud for a scald cloud on the same shape).

**C. Still cleanup at 35 degrees (free part, after the walk is packed).** Despeckle and lift the s and ne/n shade
shares with the touch-up lane's tools. The walk is now drawn from these stills, so any still cleanup has to go
through the idle and walk frames together, with the touch-up lane. Raising the short side view is a redraw (paid Codex, about 70k tokens, worst case about
150k with the overshoot), only on his yes and the hub's slot.
