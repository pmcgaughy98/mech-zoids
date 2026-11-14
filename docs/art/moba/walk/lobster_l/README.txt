Lobster (lobster_l take-g) 35-degree walk: FREE PREP DONE, nothing launched (2026-11-06).
Gait: Preston, 2026-11-06: "Tripod, 3 legs at once".
- feet.json: near walking legs per view, from take-g/views_cam35 (approved "Accept them"). Unlabelled legs are noted.
- plan_walk/: targets.json, guide_<view>.png, plan.gif, from
  walk_tools.py gait --gait tripod6 --P 3 --fps 8 --size L (lifts 2,3,3,2, dips f0 and f4). Tripod A (L1, R2, L3)
  planted f0-f3, B (R1, L2, R3) f4-f7. On the ground +5 +2 -1 -4, in the air -2.2 -0.4 +1.4 +3.2 side px.
  Drawn ground speed 0.48 m/s (STRIDE for the kit: full_speed_walk_rate = walk_speed / 0.48).
- run1/: brief.txt (e, se, ne), stills, targets.json, guides. Cap 170k. Not launched.
- run2/: brief.txt DRAFT (s, n; finish it from run 1's review), stills, targets.json, guides. Cap 110k. Not launched.
- Price: likely 250k-320k tokens over the two runs, worst case about 430k (each cap plus one step of about 75k).
- Packing: the Lobster session repacks with tools/art/pack_lobster_3d.py; hand it raw and sel-out frames.
- Launch (only on Preston's own yes): sh D:/dev/new-mech-rpg/docs/art/moba/rhino_l/take-a/anim/walk35/codex_cap/run_codex_capped_d.sh
  <run dir> <brief> <log name> <cap> <key>, as hippo_l/run1/RUN.txt did.
