# Gorilla front shields — placement and proportion refinement

Rebuilt each forearm shield as a single clean assembly matching the front concept's three-cell design. Removed the intersecting front/side duplicate frames, warped orange edges and fragments between them. The new shields have straight beveled hex frames, regular hexagonal cells, consistent cell gaps, recessed dark backing and symmetric placement with a slight outward angle. The lower green forearm casings were rebuilt locally to provide flat mounting seats and close the old panel holes. Small dark cable couplings finish the elbow connections.

## Latest review model

- Editable source: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_shields_review.blend`.
- Skinned interchange file: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_shields_review.glb`.
- `before-after.jpg`: matching front/full-character and three-quarter detail views. Images retain their original aspect ratio.
- `after_outer.png`: outer-side fit.
- `inspection.mp4`: front-to-outer orbit with moderate forearm/wrist flex. This is a geometry/rig review, not a walk cycle or editing tutorial.
- `export_threequarter.png`: rendered from a freshly reimported GLB.

Source was `gorilla_matched_hands_feet_review.blend`, which remains unchanged. Continue further touch-ups from the shield review to retain the finished hands, feet and current shield work. Approved catalog display and gameplay files have not been replaced.

## Shape and placement

Frame size in its local plane is 0.580 m wide by approximately 0.553 m high. Outer/inner radial dimensions are 0.290/0.253 m, with small bevels and 0.042 m overall frame depth. The radial rim difference is 0.037 m; this is not a claim of identical perpendicular strap width on every edge. Three cells retain regular hexagon proportions rather than inheriting the shield's vertical adjustment. Their base radius is 0.112 m, with inset upper faces of radius 0.103 m.

The outward normal on the positive-X forearm is approximately (0.350, -0.880, 0.320), mirrored on the opposite arm. This keeps the main face readable from the front while exposing its depth in three-quarter view. The casing is clipped and capped behind the mounting plane, so it cannot protrude through the frame/cells. Closed green mount housings overlap the casing rather than leaving floating panels. Shields and casings bind rigidly to the original Bone_031/Bone_027 forearm bones; wrists/hands remain separate.

The original generated forearm geometry below the elbow collar was replaced in the weighted forearm region. Original elbow/upper-arm geometry above the local edit retains some source irregularities; this is not a whole-body artist retopology pass.

## Verification

`validation.json` records unchanged hands/feet, unchanged 34-bone skeleton, and unchanged geometry/UVs/weights for 16,054 body faces outside the forearm edit envelope. Source custom normals outside that region remain within 0.001 vector length after Blender quantization. All 18 replacement casing, mount, frame, backing, cell and coupling objects have closed shells and rigid bone weights. Left/right geometry mirrors with zero measured vertex-position error. Each cell's six top edges have equal lengths within 0.000001 m. Forearm poses at -20/0/+20 degrees produce rigid motion with maximum evaluated error below 0.000001 m. GLB reimport retained the skin and paint texture.

Inspected neutral front, close front, three-quarter, outer and full-character views, plus a combined forearm/wrist flex pose. Reimported GLB detail was rendered and inspected. Full locomotion contacts, all possible attack poses, game lighting and Godot runtime integration remain unverified. No new animation is exported in this model GLB.

## Reference and working files

Used the project's approved front and left gorilla concept views under `docs/art/moba/ape_l/take-b-power/white_views`. The front sheet supports one visible orange three-cell assembly per forearm, rather than the overlapping duplicated panels in the generated mesh. Existing body/finished-foot greens informed the new paint texture.

Scripts, working Blender file, paint image, measurements and logs are in `D:/dev/_scratch/gorilla/shield-refinement-2026-11-08`.
