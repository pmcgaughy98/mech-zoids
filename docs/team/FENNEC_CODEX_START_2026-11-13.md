# Fennec dedicated Codex lane: start here

Preston explicitly requested this lane after asking whether a new fennec chat
would inherit the skills and current work of Claude's per-mech sessions.
Its first job is to catch up from actual files and recent session evidence,
then begin a small useful fennec refinement. Do not ask him to reteach learned
animation anatomy, game feel or integration conventions.

Work in `D:/dev/new-mech-rpg`; scratch in `D:/dev/_scratch/fennec-3d/`.
Read applicable AGENTS.md, CLAUDE.md, START_HERE.md and
docs/team/how-preston-works.md. Respect all current project ownership rules.
No paid generation, rerig/remesh, purchases, commits or automatic new kit design.
Preserve intact source downloads, other lane work and live authored assets.
One actual Godot app at a time. Local background Blender is available.

## Catch up before edits

- `docs/plan/moba-kits.md`: living intended kit. Inspect fennec section and
  latest approval evidence. `fennec-janus-kit-2026-11-04.md` and the old
  `docs/art/moba/fennec_s/MECH_STATUS.md` describe earlier states; the latter
  is November 5 sprite-era history, not a current rig/kit readiness certificate.
- Inspect current `scripts/moba3d/fennec_kit.gd`, shared player/model/clock/event
  APIs, roster.json and authored_profiles.json. Separate live gameplay,
  approved intended behavior, proposals, and staged prototypes. Existing
  fennec code still contains old sprite-era behavior; don't silently resurrect
  that pipeline. Machines moved to 3D November 9.
- `docs/art/moba/MODEL_WORKBENCH.md`, `art/model_catalog/catalog.json`, the
  fennec workspace and four exact reference sheets. Prefer current bound rig
  from `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/`; inspect actual skins,
  bind transforms, weights and physical limb anatomy. Original sheets can
  contain proportion, limb count and perspective mistakes. Resolve all views
  against intended anatomy rather than copying obvious generation errors.
- `docs/art/moba/ANIMATION_PLAYBOOK.md`: prioritize current 3D sections.
  Read `docs/reference/animation-skillup-2026-11-09/REPORT.md`, ACTION_CARDS.md,
  `docs/team/ANIMATION_LANE_EXCHANGE_2026-11-08.md` and the Gemini REVIEW.md
  referenced there. Raw AI research had unsupported rig/frame measurements.
- Read relevant local .claude/skills: atlas-animation, atlas-godot,
  blender-export-pipeline and appropriate artist/rigging skills. Use the
  available connector/tool inventory where it helps; don't assume installing
  a skill or reading a report makes a clip correct.
- Learn CURRENT implementation and recent lane notes from gorilla, rhino,
  kangaroo, hippo and pangolin before adapting techniques. Newer Claude notes
  are in the side-session-notes hub folder under
  `C:/Users/pmcga/AppData/Local/Claude-Data/claude_pzs8sxrjxfjjc/`.
  Select the relevant actual 3D-lane notes and latest user/assistant session
  messages as needed; avoid secrets, unrelated Hollowtide and thinking logs.
  Read accepted versus rejected work explicitly. Authored_profiles and recent
  source scripts often supersede older handoff version numbers.

## Lessons already learned

Use anatomy-specific labeled bone mapping, source-correct up/forward and units,
source FPS with exact seconds/subframes, in-place locomotion with game-owned
translation and stride-matched playback. Preserve rigid armor where intended;
don't transfer a humanoid/gorilla gait blindly. Correct action anatomy and
silhouette require visual review, not only clean loops or passing clearance.
Check skin deformation through the action, contacts, rest/transition poses,
cast/contact/recovery events, once-only hits, interruption and death cleanup.
The latest gorilla kit is shield / Fault Line / Drive Slam / chest beat; old
standalone grab/Drive contracts are historical, not shared integration truth.

Grok is now a checker/auditor/researcher, not the animator. Read
`docs/team/GROK_ROLE_2026-11-13.md` and the reports under
`D:/dev/_scratch/grok-mech-foundations-2026-11-10/output/checks/`.
Its staged fennec GLB has seven draft clips, NOT approved production animation.
Its fennec Walk and TwinDoors metadata mixes measurement spaces: glTF deltas
96/106 degrees versus Blender pose-basis 48/58. A bind/rest mismatch was also
flagged; inspect the actual rest and influencing bones before reuse. See
codex_independent_review/REVIEW.md and independent measurement JSON there.
Large rotations and tests do not certify visual quality. Don't promote these
drafts because files or matching clip names exist.

Latest auditor v2 removed historical/stale-note false positives and reran
kangaroo Death skin clearance on copies. Use the measurement methods with
explicit units/regions, not unconditional pass/fail totals. Claimed defaults
at 24fps missed falcon's peak; 0.1 seconds measures 55 degrees independently.
Unknown chronology or method remains unknown.

Grok's fresh balance review is RUNNING in
`D:/dev/_scratch/grok-mech-foundations-2026-11-10/balance-review-2026-11-13/`.
Read completed reports when they exist; don't assume STATUS is the final answer
or treat predictions as approved tuning changes.

## First deliverable

Write a current evidence-based fennec baseline: exact chosen rig/hash, sheets,
bone-role map, anatomy/texture/remesh defects, actual vs intended kit, clip
readiness and latest approval references. Render the actual rig and inspect
sample poses from several useful views. Then select ONE safe, useful local
animation/refinement slice grounded in approved fennec intent and start it on
a copy, with before/after or baseline proof. Do not invent fennec's personality
or take over shared runtime/stat changes during onboarding. Ask only a real
design ambiguity; continue independent inspection meanwhile. Maintain a
versioned fennec status/handoff so the next session needn't repeat the catch-up.
