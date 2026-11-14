# Golden Beetle and Wyvern review

Golden Beetle now uses front-leg correction v2; Wyvern remains on its completed objective repair. Both are available in the Mech Workshop. Select their buttons in the Objectives row. C compares the downloaded rig with the repair; R switches original reference sheets and the labeled comparison sheets. Both models are also centered in their own row in Lineup view.

![Repaired Golden Beetle and Wyvern](both-repaired-preview.png)

| Model | Repair | Preserved native rig | Detail |
|---|---|---|---|
| Golden Beetle | Local folds/gap repaired; fused front shins/feet reconstructed as single legs | 23 joints; local donor weights mapped to existing front chains | [Files and checks](../gold_beetle_objective/front-leg-restoration-v2-2026-11-13/README.md) |
| Wyvern | Extra chest walking-leg pair removed; two hind legs and two wing arms retained | 46 joints; removed-leg influence reassigned locally to its existing body parent | [Files and checks](../wyvern_objective/repair-v1-2026-11-11/README.md) |

Golden Beetle v2 passed eleven native diagnostic poses below one-micrometre seam tolerance; Wyvern passed ten with zero measured seam gaps. Both final Godot comparison, source/review sheet, joint-count and chase-camera checks passed; screenshots were inspected. These are repair review assets, with original remesh/bake roughness and animation polish still separate work.

True pre-remesh GLBs were not found for either objective. The archived inputs here are the rigged downloads, explicitly labeled as such; existing map copies derive from those inputs. No high-detail original is fabricated or implied. The downloaded GLBs and eight reference PNGs are preserved byte-for-byte, with hashes in each model's catalog entry and reports. Existing authored map assets and gameplay models were not replaced.

`reproduction/` includes the scripts, parser and per-model input/face-component configurations. Original Downloads inputs/reference paths and the project output paths are recorded in those configurations. Repair both GLBs, run Blender's `review_objective.py` once for each id, then run the independent audit and packaging script. The native Blender files are available for direct editing with packed source references.
