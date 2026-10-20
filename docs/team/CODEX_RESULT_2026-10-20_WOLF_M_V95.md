# Wolf v95 finish

Finished the current installed wolf on `cloud/model-pass-2026-10-16`. The October 20 handoff names v94, but Claude had installed v95 before this pass: larger head/fangs/claws and thicker light leg guards. Preserved that build and its stalking body/head pitch. Battle frames first, then eight views.

## Changes

- Repeatable: merged isolated light pixels inside sufficiently broad, uniform part interiors into the dominant neighboring shade of the same color family. Only exact same-part neighborhoods were used; no palette additions. The existing pixelizer deliberately preserves these generated glints, so this is a targeted cleanup above its current output.
- Hand only: inspected the candidate locations and pose comparisons to retain plate-edge/rim highlights, seams, eyes, fangs and claws. Pixels near part boundaries remain intact. No general plate repaint or silhouette changes.

134 RGB pixels across 40 battle frames and 18 across eight views, 152 total. Every frame/view changed by one to six pixels. Exact alpha, canvas, ground-line pixels, paw positions, metadata, timings and installed hash files preserved. Edge/rim/seam/eye masks are byte-identical in the final audit.

## Source verification and copies

All 48 initial live PNGs matched their installed SHA-1 hashes. Independently replayed all 48 current color/piece/normal renders with the wolf palette and current legacy settings; every installed crop matched exactly before using its maps. Records: `docs/art/2d/wolf_m/v95_codex/map-audit.json`.

- Raw backups: `docs/art/2d/wolf_m/anim_v95_pre_codex/`, `v95_pre_codex/`.
- Finished copies: `docs/art/2d/wolf_m/anim_v95_codex/`, `v95_codex/`.
- Four-times nearest-neighbor before/after contacts and six looping clip GIFs are alongside the finished copies.
- Review: `http://127.0.0.1:8883/v95_codex/review.html`.
- Actual battle recording: `v95_codex/lunge-combat.mp4`.
- Audit: `v95_codex/final-audit.json`.

Inspected the six looping comparisons and actual battle recording. All 40 frames were captured before and after through both real battle slots; the view lab visited all eight directions. Real combat observed all nine lunge frames.

## Paw planting: source follow-up for Claude

Paws are not perfectly planted in the raw v95 idle. Near front claw bottom rows are 121, 120, 121, 122 against `feet_y=121`. A read-only evaluation of the existing blend confirms source movement rather than only palette noise: the near front foot group's minimum world Z ranges from 0.00565 to 0.08804 m across the four idle samples, about 8.2 cm travel. Rear foot groups vary about 1.4 cm. No source model was saved or changed.

Evidence: `v95_codex/paw-contact-audit.json`, `source-paw-audit.json`, `source-paws.log`. The source audit includes the exact clip/source-frame picks and all four foot groups. Please check per-foot grounding after the idle pose/body pitch, rather than relying on grounding only the lowest vertex of the whole machine. Review lunge/dash separately so intended attack lifts remain. This finish does not move paws or repaint alpha to conceal the issue.

## Validation

PASS: import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check and vfx_check. The complete VFX check covers 288 attacks across all three window scales. Tests ran sequentially at fixed 60 FPS.

Foundation, systems and start-chain use exact source copies with only their disposable save-path literals redirected into this workspace, avoiding the sandbox's blocked `user://` writes. The inverse replacement verifies identical check logic, and original source hashes are recorded. No production script or original check source changed. Logs/results: `v95_codex/checks.json`.

During this pass Claude installed kangaroo p74. The final audit records that concurrent update separately, verifies all 48 kangaroo PNGs against its fresh install records, and preserves it. All nine checks were repeated after that install. `concurrent-installs.json` records the 53 changed pre-existing kangaroo files. No rollback or edits to those files were made by this finish.

Python performed native pixel edits and exact audits, Blender only inspected the source foot geometry, Godot checked/captured real scenes, and the browser displayed the comparisons. No generated replacement sprites, source/model changes or commit.

Wolf lock removed at handover. Next machine: the current kangaroo p74, superseding p73 in the handoff. Keep its taller stance and lower tail when addressing the far shin and tail plate lighting.
