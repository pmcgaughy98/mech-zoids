# Mech Creature Factory status, 2026-11-07

Initialized in `D:\dev\new-mech-rpg`. Ready for Preston; no production work started.

## Scope and boundaries

Own model/reference preparation, consistent multi-view white sheets, MeshForge import/export, and assigned per-creature art refinement. Gorilla animations belong to **Mech Gorilla Animations**. Combat implementation belongs to the kit/game-feel owners; weapon placement here is reference design only. Existing per-mech ownership still applies.

Read CLAUDE.md, START_HERE.md, how-preston-works.md, mech-sessions-2026-11-05.md, HUB_HANDOFF_2026-11-04.md, the startup handoffs/reference, current lane INDEX.md, MeshForge research note, roster and latest relevant asset reports. No AGENTS.md was found in the project file listing or checked ancestor locations. Dated instructions are historical context; today's initialization-only direction controls.

## Actual local assets and source paths

Paths below are relative to the project root. These are latest documented reference candidates, not newly approved models. Each creature take has `sheet_raw.png`, prompt and report; `white_views/` contains four named PNGs, review, ZIP and preparation metadata except the latest Eel, which uses the upload directory below.

| Queue | Current source | Recorded remaining review |
|---|---|---|
| Dragonfly orientation | `docs/art/moba/dragonfly_m/take-b-angles/white_views/` | Upright body correction exists. Wing depth, side emitter faces and abdomen projection still need cross-view review. No replacement 3D verified. |
| Bombardier Beetle, ADC | `docs/art/moba/bombardier_beetle_m/take-b-forward/white_views/` | Forward shoulder nozzles replace rear barrels. Check bore direction, rear shell pitch and six-leg consistency. Forward ranged gameplay is not implemented by these images. |
| Mantis, jungle | `docs/art/moba/mantis_m/take-a/white_views/` | Four walking legs plus two integral blade arms; sockets and blade clearance need geometry review. |
| Hornet, ADC | `docs/art/moba/hornet_m/take-b-forward/white_views/` | Forward cheek injectors exist. Profiles show four apparent legs versus six in front/back; topology, wings and body pitch unresolved. |
| Electric Eel, mage | `docs/art/moba/electric_eel_m/take-b-level/hunyuan_uploads_v1/` | Use this take's ZIP and matching named rectangular white PNGs. Local foreground coverage is 56.68-74.28%; remote acceptance and reconstructed topology remain unverified. Old square uploads are unsuitable. |
| Later Red Ranger sheets | `docs/art/characters/red_armored_ranger/take-f-browfix/white_views/` | Latest report preserves broad pointed visor and removes tiny center brow notch. Earlier take-b narrow visor is superseded. No 3D integration. |

`docs/art/moba/creature-batch-2026-11-07/` contains another set of the five creature views and reports. Use the per-creature take/report paths above to identify revisions rather than treating batch filenames as the latest source.

Existing fleet reference selection is recorded in `docs/art/moba/ROSTER.md`, with per-mech takes under `docs/art/moba/<code>/`. Its early statement that nothing is installed is stale: local packed SpriteFrames exist for ape, fennec, hippo, kangaroo, lobster, minion and rhino under `art/machines/`. This was a file inventory, not a runtime verification.

The local machine GLB under `art/machines/` is `ape_l/ape_l.glb`. Older Blender sources for ape, hippo, wolf, kangaroo, pangolin, shoebill and combiners are in `docs/art/3d/`; rhino/drone experimental GLBs remain in their `docs/art/moba/.../3d_test/` folders. No local GLB/FBX/OBJ was found for the five queued creatures or Ranger in the project listing. This does not establish what exists in Preston's external model library.

## MeshForge and next useful task

Connection history: `docs/research/meshforge-codex-mcp-2026-11-07.md`. The separate connector browser last reportedly held only demo Orc; Preston's usual Chrome library access is unestablished. No live browser/library inspection was needed for initialization. Saved fal.ai credentials were not accessed.

Suggested first task for Preston to assign: review Dragonfly take-b against its four named views, record precise projection mismatches, and agree the correction before any generation or import. Then address Beetle, Mantis, Hornet and Eel; Ranger stays later. This queue is context, not permission to generate.

Only this file was created. No gameplay, art, audio, peer files, commits, paid calls, generation, downloads, chats or peer messages were changed or started.

## Later assignment: minion art set

Preston requested reading **Connect Claude to Codex plugin** for the creature/four-white-sheet workflow, then selected melee, ranged and siege minions. New concept references and twelve white sheets are in `docs/art/moba/minion-set-2026-11-07/`; source of truth is its `REPORT.md`, `review_all.png` and `minions_twelve_white_sheets.zip`. Three built-in generations plus one ranged barrel-projection edit; raw files/prompts preserved. Package includes square and tightly framed upload versions. Local checks and visual review completed; projection caveats remain documented and no reconstruction has been verified. Existing placeholder, gameplay, art-direction pilot and gorilla animations untouched. Ready for Preston's visual review.
