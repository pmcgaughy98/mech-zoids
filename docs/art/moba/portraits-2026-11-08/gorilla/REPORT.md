# Gorilla portrait pilot, 2026-11-08

One real new result from Preston's existing [Mech Legend Card Forge](https://opal.google/app/1RcIDskmAl_88l4vGOCydQxdE35gz8hB_). One image generation; no retry, payment or separately billed API. Not installed.

## Evidence and method

- Located Claude's exact workflow and prior approved cards in `D:/dev/new-mech-rpg/.claude/worktrees/loving-mayer-4eccfb/docs/forges/card-forge/` and its `docs/art/moba/cards/`. Saved a copy of the existing forge record one directory above this file.
- Read the Claude portrait session `4f880223-511c-4616-85a9-a3caaed81552` and inspected its kept gorilla splash5. That old orange-chest design was format evidence only, never an input. The initial supplied rhino run1 image was an unsuccessful old square test, not the current tall target.
- Canonical identity: `art/model_catalog/catalog.json`, gorilla entry. Source GLB `art/model_catalog/sources/Gorilla_s - Hunyuan 3D v3.1 Pro.glb`; no mesh edits or re-export. All four images at `art/model_catalog/references/gorilla/{front,left,back,right}.png` inspected. Exact paths and checked SHA256 values: `source-manifest.json`.
- Isolated unchanged image copies in `input/`. Composite `input/gorilla_catalog_approved_view_9x16.png` is 1152x2048: full front at 1:1, with left/back/right thumbnails beneath. Visually inspected after packaging. White reference sheet background retained.
- Exact Opal text: `submitted-brief.txt`. `card-brief.txt` is the longer preparation brief, not the exact submission. Pose Reference: NONE. No graph or shared prompt edits.
- Existing forge: 9:16 generation, flat faceted pixel finish. Final old loading slot: 205x373, bottom 62 pixels reserved by game UI. No dialogue bust assumption.
- Result: `opal-run1-2fbb4ea6.jfif`, 768x1376 JPEG, preserved byte-for-byte. Blob ID `2fbb4ea6-8f94-4fe9-bd73-61a63aa814d0`; seed and separate job ID not exposed. `run1.json` records hash and dimensions.
- `package_candidate.py` reuses the existing `legend_card.py` block-mode downsampler verbatim. It contains the entire original frame within the 205x373 aspect, extending the backdrop at the bottom by 21 source pixels. It does not apply the old builder's retired sprite palette or destructive cleaning rules. Outputs `gorilla_loading_205x373_candidate.png` and nearest-neighbour 2x review. No overlaid name band, invented labels or HUD edits.

## Visual inspection

Looked at the full downloaded source and packaged card. The gorilla species, green facets, charcoal joints, silver jaw, narrow lime eyes, green chest rim and visible outer forearm hex panel read correctly. The three lime cells remain in the orange forearm frame. Blue industrial ruins give contrast.

Framing FAILS: the arm on the image's right and one hind leg are outside the picture. The result shifts the stance into a forward lean with strong asymmetry rather than matching the front sheet. Both arms and all limb counts therefore cannot be verified. Cyan edge lighting becomes a drawn outline; the face and jaw have added small seams and highlights. The chest core and silhouette are more enlarged than the front reference. No claim of exact plate-for-plate consistency or production readiness.

Stop after this first inspected pilot. A next run, if Preston directs it, should pull the camera back and center both forearms/all four supports, then reduce the cyan contour. Rhino and fennec remain queued.

## Access notes

Native Chrome capture/click automation failed. The internal browser worked after Preston confirmed login. Automatic review initially rejected Start because inputs were uncertain; inspecting the saved Card Brief user-input node established that Start only collects inputs, and the subsequent input flow and generation succeeded. Downloading the full asset required opening its original-asset link, not the HTML Download file button. No outstanding approval blocker. Skills used: Google Drive discovery (connector authentication did not complete) and computer-use for the actual existing Opal workflow. No credentials inspected.
