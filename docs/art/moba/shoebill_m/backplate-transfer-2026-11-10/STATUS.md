# Shoebill backplate transfer, 2026-11-10

November 13 update: the actual 38-joint input was supplied and the current repaired/circular-rim model is complete. See [current repair](../circular-rim-v2-2026-11-13/README.md). The missing-rig statements below are historical; the older unbound draft remains unapproved and is not the delivered asset.

Latest status: superseded by Preston's cobra double-tail correction request. A reversible static shoebill draft was staged after the follow-up authorization to work on a copy despite the missing rig. It is NOT APPROVED: isolated-plate inspection still shows adjacent blue donor fragments, and side attachment depth needs refinement. Files are explicitly named shoebill-moon-backplate-DRAFT-UNBOUND-NOT-APPROVED.blend and .glb. Do not upload these as a finished or rigged result. No bone binding or deformation test was possible. Hub is handling a separate single-material shoebill workaround. Original source/catalog files remain unchanged.

## Verified sources

Donor:

D:/user/Downloads/shoebill_front - Hunyuan 3D v3.1 Pro (1)(correct moon plate on back only use for that other model is best).glb

The marked donor exists: 51,756,772 bytes, 500,000 triangles, one mesh node, no skin or clips. It is reserved for the moon backplate only.

Designated recipient:

D:/user/Downloads/shoebill_front - Hunyuan 3D v3.1 Pro.glb

This is the recent November 10 file, 22,187,868 bytes, 24,269 triangles. Inspection of the GLB itself shows one node named output_unwrapped, no skin, no joint nodes, no node skin reference, no JOINTS_0 or WEIGHTS_0 attributes and no animation clips. It is a static mesh. The existence of a newer low-poly file does not establish that its rig was exported.

Searched both Downloads locations (D:/user/Downloads and C:/Users/pmcga/Downloads), including nested model files, plus shoebill-named scratch paths. No newer designated rigged shoebill export was found. Older local Blender/source models are not substitutes for the requested current rigged recipient.

Exact source hashes, timestamps, attributes and texture sizes are in source-inspection.json. Both files were inspected read-only. No originals or catalog were overwritten; no shared gameplay, rig, gorilla asset, animation output or registry was changed. No Godot process, paid tool, generation, credentials, commits or other chats were used.

## Reference review

Read the shoebill status, take-g power report and take-i side correction report. Visually inspected both reference boards:

- take-i-sidefix-original/white_views/review.png: long-legged body, round rear iris/condenser with brass mounts, concealed in profile by wing-root/back armor.
- take-g-power/white_views/review.png: alternate retry body and elevated condenser/support visible in profile.

These are design references, not proof of a rig or permission to substitute either body. The marked donor remains the plate source; the actual current rigged recipient must supply body, face, wings, legs and rig.

## Exact blocker and continuation

Required next input: the current shoebill GLB containing its actual skeleton and skin weights, optionally existing clips, saved under a distinct name such as shoebill_rigged.glb. Rigging that exists only in the application is not present in the named local file.

Once that export is available: preserve it and its hash; inspect hierarchy/rest transforms/weights; isolate donor plate only; reconcile fit and remove any duplicate recipient plate without re-rigging the body; bind the rigid plate to the inspected torso/spine bone; compare front/back/side and a temporary deformation test on the isolated copy; export separately named Blender and GLB artifacts.
