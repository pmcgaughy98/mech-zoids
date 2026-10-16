# Hangar R1 handoff, 2026-10-12

- Built: Preston approved Form with 'next'. Exported the original procedural
  hangar with code-painted colour, emission and baked room-only AO/ORM atlases.
  Room rotates 180 degrees into the native door-facing-+Z contract; machine,
  cameras and lights are excluded from the GLB. The approved Form source remains.
- Files: `art/rooms/hangar_bay/hangar_bay.glb` (3,280 triangles, 4,273,448 bytes),
  `hangar_bay.runtime.json`, `textures/hangar_*.png`,
  `source/hangar_bay_runtime.blend`, and `evidence/runtime/` checks/hashes.
  Builders: `tools/blender/export_hangar_runtime.py`, `audit_hangar_export.py`.
  Stage/check changes: `scripts/scenes/room_stage_3d.gd`, `tools/debug/room_check.gd`.
- Stage: reads optional room camera/fixture metadata; scopes viewport stretching
  to 320x180 while this stage is loaded and restores the prior settings on exit.
  Camera x=3.8m clears the crane cable. Four work lights derive from the original
  fixture manifest. Room textures use nearest filtering; machine finish remains
  the shared metal one. The default test-box behavior is retained.
- Checks: `room_check: PASS` at 1280x720 and 640x360 window sizes; captured
  viewport 320x180 in both. Actual scene 20,782 triangles; all five material
  surfaces finished; atlases loaded; idle playing; floor at origin.
  Export audit PASS: 375 visible machine samples, zero occlusions, nine clear
  door rays; current rest-pose floor gap 2mm. Largest structural mesh probe:
  3,165/3,165 hard edges split-shaded (100%). Headless test-box fallback PASS.
- Review: `http://127.0.0.1:8719/review.html`; native still at
  `docs/art/3d/room_hangar_bay.png` and `evidence/runtime/godot-production.png`.
- Plugin validator: retained unmodified failures in `runtime/gate-validation.txt`.
  Its Meshy assets and static lightmap do not match the explicit procedural/native
  task contract. `runtime/native-adapter.json` documents the single geometry/
  texture tier and baked AO plus real-time lighting route. No paid services used.
- Not verified: full animation envelopes, gameplay collision/navigation,
  integration with the 2D base, and handheld performance. Triangle and byte
  budgets checked; no hardware benchmark claimed. Godot emits a Windows root
  certificate-store warning; local runtime checks and capture succeed.
- Open decision: Preston's Runtime approval. `gates.runtime` stays false until
  approval; do not infer it from a render or a check. No deployment performed.
- Next after approval: R1 can be delivered. R2 needs Preston's choice among three
  battle-stage briefs (quarry, dry riverbed, ruined yard). A dedicated hangar
  `.tscn` is deferred until gameplay requires triggers, navigation or a camera
  path, as the task contract specifies.
