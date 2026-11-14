# Gorilla feet refinement — 2026-11-08

Rebuilt Claude's feet into a tapered plantigrade mech foot: narrower heel, sloped instep, four forward toes with graduated lengths, and a broad medial big toe. Replaced the stacked boot blocks and small dark nail-like caps with chamfered toe armor, recessed joints and underside contact pads. Each foot retains its previous overall width, length and height. The enlarged downward fists from the preceding review are retained unchanged.

## Review and editable files

- `before-after.jpg`: matching medial view and isolated top view. The top view intentionally hides the rest of the character to make the toe layout visible.
- `after_full_rear.png`: complete character with both feet visible.
- `inspection.mp4`: inspection orbit with ankle and toe flex. This is a joint check, not a walk cycle or recorded editing tutorial.
- Editable combined model: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_hands_feet_review.blend`.
- Skinned interchange model: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_hands_feet_review.glb`.

Source: `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_hands_down_review.blend`. Source remains unchanged. Approved catalog display and gameplay files have not been replaced.

## Construction and validation

Only the body's previous `foot_` material faces were replaced. The new feet contain 24 named editable objects, each weighted rigidly to one existing ankle, toe or tip bone. The skeleton remains at 34 bones. The four forward toes and hallux share the existing two toe bones; independent toe articulation would require additional bones.

The retained foot bounds are 0.489128 m wide, 0.558253 m long and 0.230000 m high, mirrored across the character. All five toe pads and the heel pad meet the floor in rest pose. The heel/instep mesh tapers without introducing a tall human-style arch.

`validation.json` records passing checks for unchanged hands (geometry, weights, materials and normals), unchanged skeleton, unchanged 21,401 non-foot body faces with original UVs and weights, closed individual foot shells, original bounds, heel/toe contacts and rigid binding. Posed both ankle/toe/tip chains at 0/0/0, 18/-25/-12 and -15/25/15 degrees about a transverse axis. Maximum evaluated skinning error was below 0.000001 m; body custom-normal quantization difference remained below 0.001 in vector length. The GLB was reimported into Blender, retaining all 24 skinned foot objects, 14 hand objects and the 34-bone skeleton.

Inspected side, medial, isolated top, rear three-quarter, full-character and flex views. Full walking contacts, material response in gameplay lighting and Godot runtime integration remain unverified. A Godot editor process was already open but had no connected MCP session, so no second engine was launched. This is a separate model review candidate, with no new walk animation exported.

## Structural references

- D. L. Gebo, [Plantigrady and foot adaptation in African apes: implications for hominid origins](https://pubmed.ncbi.nlm.nih.gov/1530061/) (1992): supports heel contact in gorillas during terrestrial locomotion. Firecrawl could not retrieve this page; the abstract was read through the web fallback.
- Museu de Ciències Naturals de Barcelona, [G. g. gorilla articulated foot, left hindlimb](https://sketchfab.com/3d-models/g-g-gorilla-articulated-foot-left-hindlimb-8c905317451a4485af7e19b2280163e2): five-digit anatomical specimen MZB 2010-1163, with digit and tarsal annotations. Used as a structural reference only; no mesh downloaded or incorporated.
- Approved project concept views in `docs/art/moba/ape_l/take-b-power/white_views`: heavy green mech silhouette and gray foot armor. Generated digit counts are not treated as anatomical ground truth.

Specific dimensions and splay are mech design decisions, not measured gorilla ratios. Scripts, logs, original-bound measurements and working files are preserved in `D:/dev/_scratch/gorilla/foot-refinement-2026-11-08`.
