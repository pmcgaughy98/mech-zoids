# Finish carry-forward status, 2026-10-13

All six machines have a preserved finish record. Four live builds have since changed; those live views need the recorded finish carried forward before Task 1 is current across the roster. Do not restore old silhouettes over newer builds.

| Machine | Finish record | Current live source | Live equals finish | Current canvas / anchor |
|---|---|---|---|---|
| ape_l | v66_codex | v66_codex | 8/8 | [196, 100] / [98, 97] |
| hippo_m | p18_codex | p24 | 0/8 | [144, 72] / [72, 69] |
| kangaroo_m | p42_codex | p45 | 0/8 | [170, 116] / [85, 113] |
| pangolin_m | p16_codex | p20 | 0/8 | [250, 80] / [125, 77] |
| shoebill_m | p62_codex | p67 | 0/8 | [124, 123] / [62, 120] |
| wolf_m | v52_codex | v52_codex | 8/8 | [214, 108] / [107, 105] |

Next: carry finishes onto current hippo, kangaroo, pangolin and shoebill builds, checking alpha/anchor and changed hardware independently. Then run Task 2 at actual battle scale. Wolf still needs a battle contrast review: its charcoal scheme remains darker than the historical edge target.

## Claude handoff update, verified after Preston's correction

Read CODEX_TASKS_2026-10-13.md again before the next pass; Claude updated it at 17:44. The factory log also records the current battle wiring and newly re-rendered gorilla animation set.

- Gorilla battle art is a separate set under art/machines/ape_l/anim/, not the eight views. All 51 PNGs across seven clips are present on a 149x148 canvas; anim.json specifies feet_y 121. Clips: idle 4, gait 9, punch 9, slam 10, throw 10, hit 3, death 6.
- These new v66 battle frames still need the color-only finish. Back up the entire live animation folder before editing; preserve each alpha mask, canvas, metadata, timings and strike markers. Save the finish separately in docs/art/2d/ape_l/anim_codex/. Claude's ape_anim_round.sh regenerates the live folder after model rebuilds.
- Actual battle code scripts/ui/machine_anim.gd loads anim/anim.json when present. Otherwise it loads views/e.png and mirrors it for faces_left. Thus the other starters' side view is the battle-facing art. The older behind-left/front wording in the task file does not describe the current implementation.
- Current live sources were rechecked: gorilla v66_codex, hippo p24, kangaroo p45, pangolin p20, shoebill p67, wolf v52_codex. The four finish transfers remain needed; no old silhouettes were restored.

The paragraph above records the earlier 17:44 handoff. It has since been superseded for battle wiring by the update below.

## Gorilla animation completed; latest Claude handoff at 18:19

Gorilla's 51 battle PNGs are now finished and installed. Original alpha masks, transparent pixels, teal eyes and anim.json bytes (including timing and strike markers) are exact. The original set is saved in docs/art/2d/ape_l/anim_v66_pre_codex/ and the finish in docs/art/2d/ape_l/anim_codex/.

Godot import, six-machine view_art_check and battle_check PASS. All 51 frames were captured in both actual battle slots; a real Piston Knuckles action was recorded against the hippo. Result, evidence and original slam/throw/death clipping issues for Claude: CODEX_RESULT_2026-10-13_APE_L_ANIM.md.

Claude updated CODEX_TASKS_2026-10-13.md during this pass: ALL six starters now have animated battle sets. The five non-gorilla sets contain 40 frames each and still need their own finishes. The previous views/e.png fallback note describes the earlier wiring, not current combat art.

Remaining: carry the four rebuilt view finishes forward; finish the five other starters' battle animation sets; review battle contrast/composition. Gorilla's color finish is complete, but existing pose/camera clipping needs Claude's rig/export/scene work. Texture sheets and the pixel room remain waiting for Claude's wiring.
