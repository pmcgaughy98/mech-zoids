# Wolf v84 finish, 2026-10-15

Finished and installed all 40 battle frames in six clips and all eight views, following Preston's instruction to continue the handoffs. Grey flank plates replace the large red patches; remaining red reads mainly along the back, shoulder trim and existing mechanical accents. Dark armor has restrained lit upper edges. Tail links have separate lit faces and internal joints. No generated/reference pixels were installed.

17,962 opaque pixels changed: 15,594 across battle frames and 2,368 across views. The original silhouette, four legs, red claws, pale tail blades, red tail tip, red-ringed limb hubs, eyes and antenna arrangement remain native. Hidden parts were not drawn in.

## Fixes for Claude

| Fix | Classification | How to carry it forward |
|---|---|---|
| Grey flank plates | repeatable | Use actual body-side plate/material masks, including their attached details, to replace red flank fill with the existing grey ramp. Keep the darkest grey flank edge at 34343e. Do not recolor all red: feet, tail tip, head details and red limb discs are protected. |
| Shoulder trim | repeatable | Preserve a narrow connected red strip on the real upper shoulder-fin edge, rather than retaining the full red plate. Its placement is semantic and pose-aware. |
| Lit dark steel | repeatable | Lift the upper boundary of sufficiently large main-armor pieces one grey step, capped at 686876. Do not darken the black wolf's outer boundary further. Tiny details were excluded after visual review because their highlights became busy. |
| Tail segmentation | repeatable | Follow tail.0, tail.1 and tail.2 surfaces. Light each link's upper face and use 34343e at internal link transitions. Preserve red tail.3 and all pale blades. Do not add a black silhouette ring. |
| Pale steel protection | repeatable | Protect every original grey pixel at 9a9aa6 and above, as well as blade-category masks. The final audit caught 33 blade-edge pixels outside modal blade masks; all were restored before the final captures. |
| Own-color outer-edge protection | repeatable | Restore the original shade wherever an internal tail-joint treatment would darken an existing grey silhouette pixel. All original grey silhouette pixels now remain at their original brightness or brighter. This guard restored 37 pixels across the set. |
| Per-pose/facing placement and strength | hand only | Review the full set and looping clips. These v84 spatial masks are build-specific; future builds need fresh matching part maps and artist judgment. Do not paste this finish over a new silhouette. |

Operation counts overlap: 7,498 flank conversions, 157 shoulder-trim operations, 9,195 armor-rim operations, 1,864 lit tail-link operations and 856 internal tail-joint operations. Their sum is not the number of unique changed pixels.

## Preserved contract

- All 48 live PNGs matched their SHA1 install records before work. Both original folders were backed up first. CODEX_IN_PROGRESS protected the work and was removed at handover.
- Every alpha byte, canvas, transparent RGBA pixel and position is exact. Views remain 278x121, anchor [139,118]. Battle frames remain 180x123, feet_y 111.
- views.json, anim.json and both .installed_hashes.json files are byte-for-byte unchanged. Frame ordering, durations, loops and strike markers are unchanged. The deliberately unchanged install records let the guard detect this finish on the next rebuild.
- Teal pixels are exact, with no new teal. Feet, visible limb accent/disc masks and blade masks are protected. Every original pale steel pixel is unchanged exactly. All output colors are from the live views.json palette and allowed teal ramp.
- No importer, exporter or round script ran. No protected pipeline/game source or model file was edited; no commit was made.

## Inputs, finished records and playable review

- Original views: docs/art/2d/wolf_m/v84_pre_codex/.
- Original battle frames: docs/art/2d/wolf_m/anim_v84_pre_codex/.
- Finished views and audits/helpers: docs/art/2d/wolf_m/v84_codex/.
- Finished battle frames: docs/art/2d/wolf_m/anim_v84_codex/.
- Eight-view before/after at exact nearest 4x: v84_codex/before-after-4x.png; focused sheet: four-view-focus.png.
- Six full frame sheets at exact nearest 4x: anim_v84_codex/<clip>-before-after-4x.png.
- Six fixed-palette before/after loops: <clip>-comparison.gif; finished loops: <clip>-finished.gif. Pingpong previews include the reverse interior frames. GIF timing rounds to 10 ms; game timing remains exact.
- Browser review: http://127.0.0.1:8872/v84_codex/review.html. Saved page: v84_codex/review.html. Preview server is local-only, PID 30924 at launch.
- Actual Fang Lunge against the hippo: anim_v84_codex/review/combat.mp4 (60fps, four seconds), combat.gif (20fps), and combat-contact.png. Captured through the live combat queue, including hit response and recovery.
- Native before/after battle-capture sets: v84_codex/battle_before/ and battle_after/.
- All 40 poses in both battle slots: anim_v84_codex/review/battle/{before,after}/, with duration/canvas manifests and per-clip installed contact sheets.
- Eight actual view-lab facings: v84_codex/lab_000.png through lab_315.png, combined in view-lab-eight-cameras.png. The review helper substitutes a single wolf in the actual lab scene because the default lab cast does not include the wolf. Game scene/source stayed unchanged.

## Map and model evidence

All eight native view color renders and all 40 native frame renders re-pixelized exactly to the untouched installed pixels after verifying their existing alignment/crop. The first replay erroneously retained a gorilla-only eye setting; removing it reproduced the native wolf settings exactly. No map was used until verification passed. Evidence: input-audit.json and map-audit.json.

The project's Blender Scripting skill supplied a read-only background replay of the existing wolf_m.blend camera and poses. Flat per-piece maps carry dominant material, rest-space center and weighted bone membership. Every replayed color render was checked against its corresponding native source before its piece map was trusted. At mixed red/grey source blocks, part votes follow the pixels that supplied the red material, avoiding unrelated grey/core IDs. The eight-view replay restores all native display settings between the flat and color passes. Evidence: piece-renders/, piece-source.json and finish.py. The .blend hash is unchanged and it was never saved.

Pillow/NumPy supplied deterministic color edits; the existing sprite_quality.py and legacy_gap.py were read-only measurements. Local Legacy technique studies and the freshly generated wolf concept supplied visual guidance only. No reference pixels copied and no paid generation service used for this finish.

## Verification and limits

- Final Godot headless import exits 0. view_art_check, views_check and battle_check PASS.
- All 40 loaded animation frames, dimensions and durations pass in both actual battle slots. All eight lab directions load installed art. Real Fang Lunge recording completed.
- All six GIFs and all frame sheets were reviewed. Identical source poses shared across lunge/0, howl/0, dash/0 and death/0 finish identically. The temporal audit records color changes at unchanged screen pixels as parts move; it is not a claim of zero shimmer.
- Final live files equal the preserved finished copies, all alpha/transparent pixels are exact, all metadata/guard records are exact, and the source model hash is unchanged. Evidence: final-audit.json and live-write-audit.json.
- Measurements are records, not acceptance targets. Animation mean cluster size changes from 8.74–10.11 to 6.98–8.06 pixels; stray-color share rises from 3.03–4.32% to 4.43–6.01%. View cluster size changes from 9.31–13.12 to 7.30–10.58; stray share rises from 1.80–3.74% to 3.10–5.58%. This finish improves flank color structure and link reading; it does not reduce all pixel noise. Outline measure stays 0 for the wolf palette. Full measures: finish-audit.json, final-audit.json and legacy-gap-record.json.

## Existing source/staging issues for Claude

- dash/6's raw render has two opaque pixels at the camera edge. This existed before the finish. No alpha expansion or camera edit was made.
- With the enemy's existing screen origin at y=-11, death/4 and death/5 clip 47 and 153 body pixels above the screen. The normal player slot does not top-clip any frame. Captures and final-audit.json record this; color edits cannot repair it.
- The original action poses move the body bottom relative to feet_y by up to 11 pixels above and nine pixels below it. Idle/0 meets the feet row exactly. The finish preserves all of this alignment and motion.
- The default lab cast still omits wolf and kangaroo. The review fixture proves the wolf's view wiring without changing that cast.

Next machine: kangaroo p68, then shoebill p84, hippo p40 and pangolin p40. Recheck the latest handoff and all live install hashes before each. Historical finishes and concepts remain untouched.
