# Gorilla walk contact refinement — 2026-11-08

Candidate sources: `art/model_catalog/workspaces/gorilla_knuckle_walk_v3.blend` and matching `.glb`. The approved static/back-rim model remains untouched. No catalog or gameplay promotion.

## What changed

Starting from the MeshForge v1 walk trial, tested v2 with longer support and small torso rotations. Replaced that provisional solve with a precise contact-aware bake in Blender, then imported/saved/exported it through MeshForge for visual review and independent roundtrip validation.

V3 keeps 34 joints and 25,757 triangles. No geometry/proportion/color edits. Animation: `Gorilla_KnuckleWalk_ContactRefined_v3`, 1.4 seconds, 60 fps bake, 85 endpoint-inclusive keys. The four limbs have staggered 75% support/25% swing phases; shared 0.22 m stance travel; hands lift up to 0.075 m and feet 0.055 m. Body has 24 mm lateral sway, 12 mm compression, restrained hip/spine rotation and head counter-motion. These are an authored gait design, not measured biological timing or copied Rampage animation.

Two-bone solves compensate for the moving body while contact parts retain their rest world orientation. This keeps the actual soles and knuckle plates flat during support instead of trusting the tool's foot-joint ground statistic. No limb reach clamping was required.

## Verification

Private evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/v3/`.

- `contact-audit.json`: exact bake-frame mesh surface heights, target errors and contact marker positions.
- `roundtrip-validation.json`: independent Blender import of both Blender export and MeshForge re-export; 169 samples including between-key times. Largest sampled support penetration approximately 0.066 mm. Largest adjacent virtual-world stance marker displacement approximately 0.057 mm. The virtual controller moves forward at 0.209524 m/s in this asset's units; this is not a verified game-controller speed.
- `gorilla-walk-v3.gif`: 28 side-view frames at 50 ms each, real 1.4-second loop.
- `before-after.gif`: synchronized v1/v3 comparison. V1 frame cadence/resolution is lower, so judge contact behavior rather than image sharpness.
- `meshforge_contact_sheet-rest-0.png`: inspected side/front poses at six times.
- `review.log`, `meshforge_state.json`, `meshforge_export.json`: MeshForge import, library save and export confirmation.

Earlier v1 coarse sampling found approximately 10.6 mm left sole penetration during its intended support phase. V3 dense/subframe sampling found under0.1 mm. This compares different sample densities; it establishes a corrected contact issue, not a benchmark of final visual quality.

MeshForge expands material primitives into separate mesh objects on roundtrip (61 to112 Blender objects). Triangle/joint totals and contact measurements remain consistent. Deliver the Blender-exported candidate to preserve the source object organization. MeshForge joint statistics still report in-place sliding and zero root travel: those metrics inspect joint/root motion, not the intended controller-compensated support surfaces. Do not describe them as a failed surface contact test or as proof of perfect planting.

## Remaining review

Still a slow-walk refinement, not a final MOBA run. The actual gameplay scale/speed, transition blending, terrain contacts and collision behavior have not been tested. Side/front preview shows no obvious new gross armor crossings, but full shield/body collision clearance was not numerically certified. A gameplay-camera speed/stride test and shoulder/hip polish should precede more directions or attacks. No Godot engine was launched. No paid generation or re-rigging used.

Build procedure: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/refine_contacts.py`; validation `v3/validate.py`; original MeshForge and v2 specs/scripts preserved beside it. The GLB is an animation review candidate, not promoted production content.
