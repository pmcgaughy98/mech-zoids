# Pangolin (`pangolin_m`): status, 2026-11-05

Written by the Pangolin session on its stock-take turn. Nothing was built or spent.
The current copy is `D:\dev\new-mech-rpg\docs\art\moba\pangolin_m\MECH_STATUS.md` in the main checkout. The
Pangolin session edits a copy in its worktree and copies it over through the shell, so the two match; if they ever
differ, the main checkout's copy wins.

## In one look

| Thing | State |
|---|---|
| Approved stills | `take-a/views/`, 8 directions. Approved 2026-11-03: "pangolin looks good". |
| 35-degree stills | **None.** The take-a brief and prompt sheet never name a camera angle (only "same camera height"), so treat take-a as the old low angle until someone checks. |
| Animations from the approved design | **None.** No walk, idle, rake, dig, flare or ball. |
| In the MOBA match | **No.** There is no `pangolin_frames.tres`; the match has frames only for ape, fennec, hippo, rhino and minions. |
| Old October pangolin | A different, older design lives in `art/machines/pangolin_m/` (views plus idle 4, rake 9, roll 9, shot 9, hit 3, death 6 frames, dated 2026-10-20, from `docs/art/2d/pangolin_m/p46_detail`). It is wired into the old turn-based battle (`machines.gd`, `events.gd`, `battle_rules.gd` arena_1 enemy, `items.gd`, `vfx_recipes.gd`). Its rake is a tail sweep, not claws. Not the approved look; do not reuse it for the MOBA. |

## Known faults in the approved take (from its own REPORT and APPROVED notes)

- Side views are short: east 43 px tall against front 56 and back 59 (side-to-front 0.77, flagged FAIL).
- Back view is 5.4 percent taller than the front (rule is under 5).
- Rear diagonals show cyan eye pixels that should be hidden: ne 1 pixel, nw 3 pixels.
- Hind heels still carry toe-like claws.
- North view: head not clearly separate from the back.

All of these can be fixed inside a 35-degree redraw rather than patched now.

## What the kit doc leaves open

From the `### Pangolin` section of `docs/plan/moba-kits.md`:
- No numbers anywhere. Cooldowns are "short / medium / long"; no damage, durations or ranges.
- Passive: how much damage comes back, and from melee only (ranged hits excluded)?
- Claw rake: how much the armour shred adds, and for how long.
- Dig in: time under ground, how far it can erupt, knock-up length, and whether it can be cancelled.
- Scale flare: "the next couple of hits": two or three? How long the block lasts if unused.
- Iron ball: "a few seconds": how many; steerable or straight line; does it hit the same enemy twice.
- No basic attack, and no base stats (health, speed, attack range). Proposed to Preston on 2026-11-05: a short melee claw swipe, about 2 m reach.
- Iron ball (2026-11-06): Preston wants it to feel like Rammus's Powerball, and ruled "Stop on first hit". The roll builds speed, is steered, and ends on the first enemy it hits with a knock-up. The kit section is updated. It stays the long-cooldown ultimate for now.
- Iron ball feel notes from the game feel lane (2026-11-06) are saved in `docs/plan/pangolin-iron-ball-notes-2026-11-06.md`, and the kit proposal now follows them: no rooted curl, a capped turn rate, it keeps rolling with no key held, and it pops out beside the target with claw rake ready. Choices for Preston before it is built:
  1. Does an enemy slow cut the ball's speed?
  2. Does Space end the roll, or does nothing happen while rolling?
  3. Does a wall end the roll with a small bump, or bounce it?
  4. Does it roll through minions, or does a minion count as the first hit? (Towers stop it with no knock-up.)
  5. Should the game feel lane add a shared `knock_up(height, time)`, or use stun plus a sprite hop?
- Passive needs to know a hit was melee (game feel lane, 2026-11-05). Kit hits reach the pangolin as take_hit(attacker_position) and shots as take_damage, with no melee flag. Two routes: the pangolin treats an attacker within about 2.5 m as melee (no shared change, but a point-blank shot would count), or the game feel lane adds a melee flag to hit() that melee basics pass. Leaning toward the flag, because it is exact. Tell the game feel lane which one when the kit is built.
- Art list names four moves (claw rake, dig and erupt, scale flare pose plus effect, curl and roll loop). Walk, idle, hit and death are not listed but the game needs them.

## Next slices (Preston picks one)

**1. 35-degree stills redraw. Paid (Codex), the gate for everything else.**
Redraw take-a's 8 views at the 35-degree game camera, keeping the approved design, and fix the five faults above in the same pass.
Estimate (corrected 2026-11-05): the first guess of 150k to 250k came from the log's size and was wrong. The fleet's real 35-degree runs used 54,566 to 78,028 tokens per image. With a Codex cap of 80k, expect about 60k to 80k, and the worst case is the cap plus the 75k overshoot, about 155k. Preston picked this slice on 2026-11-05 ("35-degree redraw").

**Redraw status (2026-11-05): ready, on hold.**
- Done for free: the prep script wrote `take-a/cam35/refs/approved_views.png`, `refs/angle_guide.png` (two rows, 6 and 35 degrees), `palette.json` and `guide_sizes.txt`. All 13 approved colours are in the palette.
- The prompt sheet and brief are in `D:\dev\_scratch\pangolin\cam35\`. They are based on the hippo's 35-degree brief, with the side-view length fix added (1.8 times the front width).
- Heights: the approved side view is short, so the guide is short too. Targets are the approved heights times the guide's growth from 6 to 35 degrees: s 45x68, se 70x68, e 82x54, ne 67x68, n 45x75. They are information only; the eye and the turn test decide.
- Done: the guide is cut to one row at 35 degrees, as in the gorilla's take 2 (`refs/angle_guide.png`; the two-row prep guide is kept as `guide_6and35_prep.png`). The brief and prompt sheet are copied into `take-a/cam35/`. The brief uses full paths to the Hollowtide tools, because the cap script runs Codex from the empty folder `D:/dev/_scratch/codex-cwd`.
- Run plan: `rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped_d.sh`, cap 80k, so the worst case is about 155k.
- Hold 1, cleared: Preston okayed the shell route in his own words: "Okay the shell route" (2026-11-05).
- Ran 2026-11-05, 20:30 to 20:37: **55,009 tokens**. Result partial: s, se, ne and n read from above; e (side) is still the low camera (78x42, target 82x54); ne has 2 eye pixels. Board: `take-a/cam35/board_cam35.png`; detail: `take-a/cam35/LANE_REPORT.md`. Preston chose "Second image, side only".
- Side-only retry, 20:57 to 21:02: **63,527 tokens**, folder `take-a/cam35/side2/`. Miss again: 82x41, spine still the top outline. Pangolin total 118,536 over two images. No third Codex image recommended.
- Preston chose "Hand-draw it (free)", then "Yes, finish it" (2026-11-06). **Done, not installed:** `take-a/cam35/hand/e.png`, `board_hand.png`, `draw_band.py`. New rows of scale plates are drawn between the old spine and the guide's 35-degree top outline, and nothing is cut and placed. There were six versions; v6 is the one kept.
  - Numbers: 82x54 (target 54). Palette clean. No lone pixels added. Brightest yellow 15.7% (se 13.5%, ne 14.1%). Accent 1.36% (approved side 1.8%).
  - PixelLab's free score: 95.9, against 95.6 for Codex's side2.
  - Still short: lighter plate seams, and a steep step at the neck.
  - Detail and the per-tool report are in `take-a/cam35/LANE_REPORT.md`.
- Waiting on Preston: whether to install it as `views_cam35/e.png` (w mirrors it), whether to remove the 2 ne eye pixels, and a turn test with the game feel lane.

**2. Kit numbers proposal. Free, about 20 to 30 minutes.**
Draft real numbers for the passive, four slots, a basic attack and base stats, as a labelled proposal for Preston to edit. Synthesis: compare 2 to 3 shipped divers that do the same jobs (a burrow-and-erupt engage, a shell or curl that rolls and knocks up, a damage-back passive) for cooldown and duration structure, and record the sources in `docs/reference/`. Firecrawl wiki reads use a few credits from the existing plan.

**3. First VFX look for scale flare and dig erupt. Free.**
Make the scale-flare burst and the dig-erupt dust ring as stand-alone effect frames with PixelLab's free `vfx_workbench` (no paid generation), shown at game size next to the approved still. Kept in `D:\dev\_scratch\pangolin\` until Preston likes it; wiring into the match is the game-feel lane's call. Synthesis pass: tool stock-take and measured references first.

Recommendation: 1 first if the paid slot is free (nothing reaches the game without it), with 2 done for free while it waits.

<details><summary>What was read for this file</summary>

- Project `CLAUDE.md` (loaded at session start).
- `docs/plan/moba-kits.md` lines 170 to 186 (the Pangolin section).
- `take-a/APPROVED.txt`, `take-a/REPORT.txt`, `take-a/sizes.txt`; a keyword search of `brief.txt` and `prompt-sheet.txt` for camera angle.
- Listings of `docs/art/moba/pangolin_m/` and `art/machines/pangolin_m/`; `anim.json` and `views.json` headers.
- `grep` for "pangolin" across scripts and tools; list of `*_frames.tres` in `art/machines/`.
- Camera lane's `FINDINGS.md` (keyword search only) in the shared notes folder.
- Not opened: any image, `codex-log.txt` (size only), `docs/art/2d/pangolin_m/` beyond its listing.
</details>
