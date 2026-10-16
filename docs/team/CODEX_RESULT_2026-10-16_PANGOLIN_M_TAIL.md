# Pangolin p41 tail-repair finish, 2026-10-16

Finished and installed all 23 replacements from the October 16 handoff: sixteen battle frames (rake/1-8 and roll/1-8) and seven views (e, ne, n, nw, w, sw, se). 24,149 opaque pixels changed: 17,358 in battle frames and 6,791 in views. The grouped gold scales, restrained dorsal edges, grey row seams and visible red claw treatment carry forward from p40 onto Claude's corrected tail shapes.

The other 24 battle PNGs remain byte-for-byte unchanged. The already re-placed S view and extra live view contact are byte-for-byte unchanged from this slice's input. S was independently checked against the old 206-wide finish: it is exactly columns 4-203, with only transparent pixels removed. No old silhouette or forked tail frame was restored.

Views retain Claude's new 200x87 canvas and anchor [100,84]. Battle frames retain 155x132, feet_y 127. All metadata and both install records remain byte-for-byte exact. Rake and roll retain durations [150,150,180,250,50,50,120,130,200], strike 5. All other clip timing is preserved.

## Carry-forward rules

| Fix | Classification | Rule |
|---|---|---|
| Scale faces | repeatable | Group main-material detail with its nearest actual scale in rest space. Compress gold surfaces into a restrained face ramp, keeping the upper body tier brighter than lower flank surfaces. Preserve non-gold hardware. |
| Dorsal rims | repeatable | Light exposed upper edges only on dorsal body scales and central upper tail scales. Avoid a bright lattice around every leaf. |
| Row seams | repeatable | Follow the native longitudinal body/tail bands. Add one-sided 3f3e43 seams where different gold scale rows actually touch; leave the outside silhouette and tiny foreshortened fragments alone. |
| Visible claws | repeatable | Use raw claw coverage and the real knuckle/hook pairs. Visible claw bodies a02010, hooks c0402a, small d86a4f tip catchlights. Add a narrow grey root valley only where sufficiently large adjacent claw groups touch. |
| Hidden parts and final reading | hand only | Review each pose and facing. Never paint red onto an occluded claw or invent hooks. Preserve the real red tail tip, head, eyes, blue spikes and weapons. Check highlight density and the whole loop at native pixel scale. |
| Input alignment | hand only | Prove exact native render correspondence and accept Claude's current canvas/anchor before using a map. Do not restore old widths or recenter the preserved south view. |

## Provenance and preservation

The sixteen raw animation files and seven raw views matched current SHA1 install records. Other 24 frames matched anim_p40_codex. Inputs were backed up to anim_p41_pre_codex/ and p41_pre_codex/. Full current finished archives: anim_p41_codex/ (40 frames) and p41_codex/ (eight views, review/helper files and metadata snapshots). Historical p40 outputs remain untouched.

All 23 original color/ID sources were preserved in p41_codex/installed-sources/. They independently re-pixelized exactly to the installed crops/alignments before map use. Animation crop [1,15,156,147]; view offsets are recorded individually in map-audit.json.

The existing Blender Scripting skill (.claude/skills/dom-blender-scripting/SKILL.md) supported read-only per-piece replays from the current model and native poses. Every replayed color image matched the original render exactly. No blend was saved, and its SHA256 is unchanged. The 388-part roster retains the same IDs, names, materials and rest bounds as the prior finish, so claw/weapon identities remain valid; eighteen bone assignments differ in the repaired model. The finish follows current part coverage, not the old binding errors. Evidence: part-roster-audit.json, piece-source.json and map-audit.json.

Every alpha byte, transparent RGBA pixel and installed position remains exact. Protection masks assert exact head, eyes, blue, weapons and ground line. Only mapped gold scales and actual visible claw pixels can change; all other source pixels, including the native red tail, are exact. Colors remain within the current palette plus permitted teal and c9cbd2. All four metadata/install-record files remain untouched, so future install guards detect and preserve this finish.

Only the 23 named live PNGs changed. No installer/exporter/round script ran; no protected pipeline/game/model source was edited. No generated/reference pixels, paid tool or commit was used. CODEX_IN_PROGRESS was removed at handover.

## Validation and review

- Godot import exits 0. view_art_check, views_check, battle_check and battle_fit_check PASS.
- All 40 loaded animation frames captured before and after in both actual battle slots at 1280x720 with canvas/duration assertions and current Stage placement. Captures: anim_p41_codex/review/battle/{before,after}/. Rake/roll contacts collect all nine poses of each clip, including their untouched starting frames.
- Required native battle captures preserved immediately in p41_codex/battle_before/ and battle_after/.
- Six seconds of actual Scale Rake and Ball Roll combat recorded at 60fps. All nine frame indices observed for each. Scale Rake deals 17 damage; the recorded Ball Roll attempt misses while playing the full clip. The fixture supplies enough EP for Ball Roll; no weapon stats changed. Result queues and observed indices are saved in review/combat_<clip>/audit.json. MP4s and contacts are in review/.
- All eight views checked in the actual lab's solo mode, using its own layout and camera rotation. Eight captures, default cast and view-lab-eight-cameras.png preserved. No scene edits.
- Both full nine-frame GIFs use fixed palettes and exact live durations at GIF's 10ms precision. Before/after loops at 3x, finished loops at 2x; full before/after contacts at 4x. Source-identical poses finish identically. temporal-audit.json records color changes through movement without claiming zero shimmer.
- All replacement frame/view contacts, loops, actual battle and lab captures were visually inspected. Four/eight-view comparisons and exact 2x E/SE comparison are in p41_codex/.
- Measurements are records only: battle mean cluster size 9.53-11.09 before, 5.87-6.55 after; stray share 1.92-2.90% before, 4.87-6.78% after. View cluster size 10.43-13.87 before, 6.31-7.07 after; stray share 1.57-2.81% before, 4.43-5.90% after. Seams/hooks add small clusters; this is not a claim of improvement in every noise measure. Full quality and Legacy records are saved.

Review: http://127.0.0.1:8880/p41_codex/review.html. Local server PID 32936 at launch.

## Remaining source limit for Claude

The W view's original raw render still cuts the red tail tip at its right camera edge: 19 opaque native edge pixels in the current 815x815 source. This predates the finish: the verified p40 color replay had 38 at that edge. Diagnostic source-west-tail-edge-comparison.png and source-west-tail-edge-audit.json preserve the evidence. It requires a source/camera correction, not recoloring or alpha growth. The sixteen replacement battle sources and other six replacement views have no raw camera-edge contact. Current 1280x720 battle captures retain complete corrected tail poses; the fit check retains its existing low-resolution allowances.

Hidden claws remain as handed off; no missing source geometry was invented. The new source binding repairs are retained.

Next slice: finish the gorilla's six replacement death frames on the 173x148 canvas, preserving the other 45 padded finished frames. Re-read the current handoff and verify inputs first. Those gorilla files were not changed by this pangolin slice.
