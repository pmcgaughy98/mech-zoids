# Kangaroo p74 finish

Finished the current installed kangaroo on `cloud/model-pass-2026-10-16`. The October 20 handoff names p73, but Claude installed p74 before this pass. Kept its taller stance, folded hind legs, lower tail angle, larger ankle discs, rounded pouch, hatch and approved shoulder/hip hardware. Battle frames first, then eight views.

## Changes

- Hand only: a small orange inset inside the far shin's visible grey core, retaining a grey perimeter and end caps. The p74 stance already shortens the old tall slab considerably; this is a restrained interior color change. Applied through the battle poses and front-facing views where exposed. Circular joints remain untouched.
- Repeatable: a one-pixel lit orange lip just inside each visible tail armour piece's upper boundary. Each lip follows its independently verified piece mask, leaving the dark intervening bands and outer silhouette intact. Small or occluded fragments are skipped.
- Hand only: inspected all pose contacts and six looping comparisons for misplaced lips or flashes. Reviewed the real battle and all eight view-lab directions.

2,100 RGB pixels changed: 1,729 across 40 battle frames and 371 across eight views. Of these, 1,916 are tail lips and 184 are shin insets. Only existing palette colors were used. Exact alpha, canvas, foot positions, ground lines, joint discs, eyes, weapons, cannon/hatch pixels, timings, metadata and installed hash files are preserved.

## Source verification and copies

All 48 original PNGs matched their installed SHA-1 records. Independently replayed all 48 current color/piece/normal renders with the kangaroo palette and current legacy settings. Every installed crop matched exactly before its maps were used. Audit: `docs/art/2d/kangaroo_m/p74_codex/map-audit.json`.

- Full raw backups: `docs/art/2d/kangaroo_m/anim_p74_pre_codex/` and `p74_pre_codex/`.
- Finished copies: `docs/art/2d/kangaroo_m/anim_p74_codex/` and `p74_codex/`.
- Four-times nearest-neighbor before/after contacts and six looping comparisons accompany the finished files.
- Review: `http://127.0.0.1:8884/p74_codex/review.html#actual-battle`.
- Actual combat recording: `p74_codex/flak-combat.mp4`.
- Exact edits and final checks: `p74_codex/edit-audit.json` and `final-audit.json`.

Captured every frame before and after through both actual battle slots. All nine Pouch Cannon frames played through the real combat queue, including hatch deployment. Captured all eight directions through the real view lab. The existing kick/3 top overhang allowance remains unchanged; no pose or canvas was adjusted.

## Validation

PASS: Godot import, view_art_check, views_check, battle_check, battle_fit_check, foundation_check, systems_check, start_chain_check and vfx_check. The complete VFX check covers 288 attacks. Tests ran sequentially at fixed 60 FPS.

Foundation, systems and start-chain checks use exact source copies with only the disposable save-path literal redirected into workspace scratch files, avoiding blocked sandbox user-directory writes. Inverse replacement verifies identical logic; original source hashes are recorded. No production script or original check changed. Results: `p74_codex/checks.json`.

Claude concurrently installed shoebill p96. Verified all 48 new shoebill PNGs against its fresh installed hashes, recorded its 53 changed pre-existing files in `concurrent-installs.json`, and preserved that install. Repeated import and all eight checks after the update. The final audit permits only that documented concurrent update outside the kangaroo PNGs.

Python/Pillow edited and audited the native pixels; Godot ran checks and captured actual scenes; the browser displayed the looping comparisons and played the combat recording. No generated replacement sprites, source model changes or commit.

Kangaroo lock removed at handover. Next machine: shoebill, currently p96. Recheck its live build before starting; retain the latest crest and chest slits when addressing upper-back shading.
