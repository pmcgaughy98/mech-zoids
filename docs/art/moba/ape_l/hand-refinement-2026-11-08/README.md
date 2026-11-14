# Gorilla hands — downward knuckle support review

The hands now descend beneath the wrists instead of projecting forward as long palm slabs. Four curled fingers on each hand meet the floor on the backs of their middle segments. The short medial thumb and palm remain above the floor. Dimensions are mech design choices, not claimed biological measurements.

Size revision: uniformly enlarged the downward fists by 17.38% to restore the previous fist's overall bulk, measured by bounding-envelope volume (0.1164034 cubic metres per hand). Kept their new aspect ratios, downward orientation and ground contact. This matches bulk rather than stretching individual axes to the old forward-pointing dimensions. Recessed wrist bearings stay at their fitted size. Exact measurements are in `size-match.json`; the smaller downward iteration remains in the scratch folder as `downward_compact.blend`.

## Review files

- `before-after.jpg`: matching side and medial views; Claude's latest forearm pass at left, downward-hand refinement at right.
- `after_full.png`: full-character scale check.
- `inspection.mp4`: three-second inspection orbit with modest wrist flex. This is a geometry/joint inspection, not a walk cycle or recorded editing tutorial.
- Editable Blender candidate: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_hands_down_review.blend`.
- Skinned GLB candidate: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_hands_down_review.glb`.

## Changes and preservation

Started from `D:/dev/_scratch/gorilla/v2/v2_fore.blend`, including Claude's forearm widening and latest feet. Removed the previous handmade hand-material geometry. Trimmed generated lower cuff fragments at height 0.300 m in the bounded hand region to expose the downward fingers. Rebuilt 14 named editable parts: palm, wrist bearing, four curled fingers and thumb per side. Fingers use graduated widths, lengths and setbacks; contact returns are shorter than the earlier extended pads.

Retained the existing 34-bone skeleton and hand bones Bone_026 and Bone_030. Each new part binds rigidly to its hand bone, so this is a closed knuckle-walking hand, with no independent finger articulation. There are 4,112 replacement hand triangles in total.

The approved catalog display, original source and gameplay assets were not replaced. The candidate is saved separately for visual review.

## Validation

`validation.json` records passing checks for unchanged skeleton, 23,322 unchanged body faces outside the cuff edit region (positions, UVs and vertex weights), four grounded finger pads per hand, raised thumbs and palms, closed individual hand shells, rigid bind at -25/0/+25 degree wrist tests, and GLB skin export/reimport. Maximum rigid evaluation error was below 0.000001 m. Reassigned custom normals differ by less than 0.001 in vector length after Blender quantization; exact measurement is recorded in the JSON.

Inspected matching front, side, medial, three-quarter, full-character and wrist-flex renders. A walking stance/contact pass remains separate work: the ground pads must stay planted during support, then lift during swing. No new walk animation is included in this model-only GLB. The rest of the generated mesh retains its existing irregularities and has not received a complete artist retopology pass.

## References

- Simpson, Latimer and Lovejoy, [Why Do Knuckle-Walking African Apes Knuckle-Walk?](https://anatomypubs.onlinelibrary.wiley.com/doi/10.1002/ar.23743), Anatomical Record (2018): anatomical basis for dorsal middle-phalange contact and the flexed finger configuration. Used as structural guidance, not as a source of exact mech proportions.
- Museu de Ciències Naturals de Barcelona, [G. g. gorilla articulated hand and right forelimb](https://sketchfab.com/3d-models/g-g-gorilla-articulated-hand-right-forelimb-60249cab8b4147cd88f184124ec578e0): five-digit skeletal reference. No source geometry downloaded or incorporated.
- Approved project four-view gorilla art under `docs/art/moba/ape_l/take-b-power/white_views`: mech style and visual mass reference; AI-generated digit anatomy is not treated as ground truth.

Build, render and validation scripts plus the first forward-hand iteration are preserved in `D:/dev/_scratch/gorilla/hand-refinement-2026-11-08`. Source SHA256: `39c327297a6842ec7c4af84be6294d956e8384d3db036ac867d0abfa98979071`.
