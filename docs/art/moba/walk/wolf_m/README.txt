Wolf (wolf_m take-b) 35-degree trot: FREE PREP ONLY, nothing launched (Preston, via the Wolf session, 2026-11-05:
"Free prep only"). PARKED: Preston said "Not now" to the paid run (via the Wolf session, 2026-11-05). Keep this prep
as it is; launch only on his own yes, relayed in his words.
- feet.json: foot labels per view, from views_cam35_touchup (approved "Keep it"). Hidden and partly hidden feet noted.
- plan_walk/: targets.json, guide_<view>.png, plan.gif, from
  walk_tools.py gait --gait trot4 --P 5 --fps 10 --size M (lifts 2,4,4,2, dips f1 and f5). This is the old approved
  side trot table exactly (+8 +3 -2 -7 on the ground, -4 -1 +2 +5 in the air); drawn ground speed 0.9 m/s; stride
  length 40 side px = 0.72 m per 0.8 s cycle.
- run1/: brief.txt (e, se, ne), stills, targets.json, guides. Cap 150k. Not launched.
- run2/: brief.txt DRAFT (s, n; finish it from run 1's review), stills, targets.json, guides. Cap 110k. Not launched.
- Price: likely 230k-270k tokens over the two runs, worst case about 410k (each cap plus one step of about 75k).
- Game: WolfKit full_speed_walk_rate = walk_speed / 0.9 (STRIDE 0.9 m/s), set when the walk is packed.
- Launch (only on Preston's own yes): sh D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped_d.sh
  <run dir> <brief> <log name> <cap> <key>, as hippo_l/run1/RUN.txt did.
