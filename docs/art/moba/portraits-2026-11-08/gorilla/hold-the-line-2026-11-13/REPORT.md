# Gorilla: Hold the line

Preston: “Start with gorilla.” November 13, 2026. One new card illustration, not an edit or replacement of the accepted November 8 pilot.

## Reference and production

Current v38 game model `art/arena_models/gorilla.glb` verified byte-identical to `docs/art/moba/archive-refresh-2026-11-13/models/gorilla-v38.glb`; hash and paths in `source-check.json`. Rendered fresh front/side/back/hero references locally. Initial rest-pose renders looked down and obscured the face; corrected the reference script to evaluate the existing `Gorilla_Idle` action at frame 1 with its original action slot. The model was not edited. Current final reference files show the actual idle face and attachments.

Hero, front and back supplied to one built-in image-generation call. The November 13 Rhino card was supplied explicitly for illustrated finish only, not anatomy or colors. Exact prompt `brief.txt`. Saved full master `gorilla-hold-the-line-master.png`; generation ID `exec-46ccf132-edd9-4b50-8e2a-3dfd49631382`. Original remains at default Codex generated-images path. Dimensions/hash in `manifest.json`.

Opal access was unavailable in this chat on the preceding card; this continues the explained built-in path with saved Mech Legend Card Forge v2 art direction. No graph edits, separately billed API, paid tool, credential access or commits. Built-in image usage/cost not exposed.

## Inspected result

The gorilla raises its near forearm to catch an impact on a localized green hex shell while the opposite knuckles and both hind feet brace against broken foundry stone. Both arms, attached fists and two hind feet are visible inside the frame. Green armor, orange forearm rims, three lime cells on each large forearm panel, lime eye slits, silver jaw/knuckles/toes and green-rimmed lime chest core carry through. The back reactor housing is visible above the shoulders; its rear cell pattern is naturally hidden from this angle. No separate handheld shield, orbiting gems, extra limbs, tail or text.

Pose, lighting and perspective are illustrated rather than a literal animation-frame render. The source's smaller rear-side forearm cells are not independently visible in this view. Some forearm proportions and plate facets are idealized, so this is not proof of exact mesh tracing. Shared blue-violet foundry architecture intentionally matches the Rhino style reference closely. The finish is a clean faceted illustration, not a guaranteed strict pixel grid.

Requested tall 9:16; returned master 992x1586. `package_loading.py` reuses the existing block-mode loading-card packager, retaining the entire master and extending its quiet lower background to reach the established 205x373 slot. `gorilla_loading_205x373_candidate.png` and nearest-neighbour 2x review inspected. No destructive cleanup or palette remap. No live card/HUD installation. Stop for Preston's direction before further cards or retries.
