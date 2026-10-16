# Shoebill p84 finish, 2026-10-15

Finished and installed all 40 battle frames in six clips and all eight views. The pale torso now has mid-blue plate faces, navy seams and retained upper-edge highlights. Narrow gold shoulder and hip accents follow the existing cap surfaces. The native head gun points forward over the bill and uses its darkest steel shade. The hooked gold bill, gold knee/ankle rings and claw tips, teal eyes and stepped navy wing remain intact.

22,863 opaque pixels changed: 19,358 in battle frames and 3,505 in views. Alpha, canvas, alignment, feet metadata, timing and source geometry are unchanged. No reference or generated pixels were copied into game art.

## Carry-forward fixes for Claude

| Fix | Classification | Rule |
|---|---|---|
| Mid-blue torso | repeatable | Follow visible body main/pale surfaces, preserving head, eyes, original gold, hardware and wing steps. Compress the bright blue ramp toward the middle. Measured torso luminance falls 20.3–24.1% in battle frames (mean 22.8%); views vary 16.9–26.0% with face visibility (mean 20.9%). Retain narrow top-face catchlights rather than uniformly darkening every part. |
| Torso plate separation | repeatable | Follow the native dorsal cap, upper/lower flank and breast surfaces. Use one-sided navy seams at visible plate interfaces and darken the actual chest vents. Do not add a dark silhouette ring or subdivide surfaces hidden by the wings. |
| Shoulder and hip gold | repeatable | Add a narrow gold upper edge only on exposed upper-arm cap and hip-cap surfaces. Preserve every original gold pixel, including the bill, muzzle, rings and toes. |
| Forward head gun | repeatable | Recover actual visible gun coverage from the raw piece map, including thin pixels missed by dominant category IDs. Shade exposed mount/barrel pixels 262a32, retaining the gold muzzle. Use the existing footprint; no alpha expansion. |
| Gun thickness and final pose judgment | hand only | E, NE, NW, W, SE and SW still contain one-pixel portions of the native barrel, as do some action poses. Existing thicker portions are darkened, but thinner portions are not widened onto the bill or background. N/S are foreshortened. Review direction and thickness per facing rather than inventing hidden hardware. |
| Protection and temporal consistency | repeatable | Protect original gold/teal/ground-line colors globally in addition to semantic head, frame-dark hardware and navy stepped-wing masks. Repeated source poses must produce identical finished bytes. Review all clips after quantization. |

## Preservation and provenance

All 48 initial live PNGs matched their SHA1 install records. CODEX_IN_PROGRESS protected this slice and was removed at handover. Originals are preserved in docs/art/2d/shoebill_m/anim_p84_pre_codex/ and p84_pre_codex/. Finished copies are anim_p84_codex/ and p84_codex/.

Views remain 116x130 with anchor [58,127]. Battle frames remain 110x120 with feet_y 117. Every alpha byte and transparent RGBA pixel is exact. Both live metadata files and both .installed_hashes.json files are byte-for-byte unchanged; durations, loops and strike markers are exact. Live PNGs equal the finished copies. The deliberate PNG hash mismatch lets the next install guard detect and preserve this finish.

All original gold pixels, eye colors and violet view ground-line pixels are exact. The color set is the live views.json palette plus the allowed teal ramp. Semantic masks protect the remaining native head, dark hardware and stepped navy wing. Native leg struts were not recolored.

All 48 native color renders re-pixelized exactly to the installed source crops and alignment before map use. Extra flat per-piece maps came from a read-only Blender replay; every replayed color image matched the native source. The blend was never saved. Native render/ID hashes and model SHA256 remain unchanged. Evidence: input-audit.json, map-audit.json, piece-source.json, finish-audit.json and final-audit.json.

No installer, exporter or round script ran. No protected pipeline, game or model source file changed. No commit or paid generator was used. Local review helpers are confined to the new finished-record folders.

## Review and validation

- Godot import exits 0; view_art_check, views_check and battle_check PASS. Logs are in p84_codex/.
- All 40 installed frames were loaded and captured in both actual battle slots, before and after. Canvas and duration checks PASS. Captures/manifests: anim_p84_codex/review/battle/{before,after}/.
- Required native battle snapshots were immediately preserved in p84_codex/battle_before/ and battle_after/.
- All eight actual view-lab facings load installed art. The review fixture uses the existing shoebill actor alone, facing zero, with the lab shifted down 28 pixels and its HUD hidden for full-body review. Native game source is unchanged. The unmodified default cast is preserved in lab_default_cast.png. Eight captures and view-lab-eight-cameras.png record the fixture.
- Actual Bill Clamp action was recorded through the combat queue: 240 frames at 60fps, including 21 damage, recovery and the following enemy action. Video/GIF/contact: anim_p84_codex/review/combat.mp4, combat.gif and combat-contact.png.
- Six fixed-palette before/after GIFs use the original frame durations rounded only to GIF's 10ms precision; live timings are unchanged. All frame sheets and loop previews were inspected. Identical source poses finish identically; temporal-audit.json records remaining screen-pixel changes as surfaces move, not a zero-shimmer claim.
- Eight-view and six clip contact sheets are saved at exact nearest 4x. Complete 40-frame sheets are finished-frames-1-2x.png and finished-frames-2-2x.png.
- Browser review: http://127.0.0.1:8874/p84_codex/review.html. Local-only server PID at launch: 31136.

Measurements are records, not targets. Animation mean cluster size changes from 7.27–8.75 to 6.82–7.97 pixels; stray share from 3.08–4.92% to 3.94–5.71%. View cluster size changes from 8.24–10.28 to 7.46–9.79 pixels; stray share from 2.74–4.09% to 2.98–4.81%. Plate separation adds small clusters; this is not a claim of less noise on every metric. Full quality and Legacy measurements are saved in finish-audit.json and legacy-gap-record.json.

## Existing issues for Claude

No raw animation camera-edge cuts and no player-slot top clipping were found. The higher enemy slot clips the native head/gun in 37 of 40 frames, from 10 to 386 opaque pixels; the worst is clamp/4. Loaded frame checks pass but do not certify composition. Source body bottoms range from the metadata feet row to six pixels above it. Per-frame counts are in final-audit.json; no alignment or alpha was changed.

The model's opposite-side shoulder bolt pieces 91–93 are bound to upper_arm.R despite positive-X rest positions. New gold accents follow the actual upper-arm cap surfaces, avoiding those bolt pieces. A binding repair belongs on Claude's side.

The handoff was updated during this slice: the gorilla has a new nine-frame punch and its other frames were padded to 163x148. Those new punch frames still need their finish; do not restore the old punch or overwrite the padded live files. This shoebill slice did not touch gorilla assets.

Next scheduled machine: hippo p40, then pangolin p40. Also track the new gorilla punch finish request. Re-read current handoffs and verify live hashes before each slice.
