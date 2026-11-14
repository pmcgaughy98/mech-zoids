# Model workbench verification, 2026-11-07

Completed shared source setup, not model anatomy repair.

- Archive: 26 source GLBs and 104 exact generation-sheet copies. Byte hashes verified during archiving; sheet hashes matched the saved project takes. 25 unique designs plus the explicitly labelled shoebill back-plate-only alternate.
- Native workspaces: all 26 `.blend` files reopened in Blender 5.2. Full source triangle counts retained before proxy reduction. Four locked reference boards per file, each image packed and its packed bytes checked against the catalog SHA256. Editable working mesh, camera, source metadata and instructions present. Results: `workspace-verification.json`.
- Visual evidence: inspected `workbench-gorilla0001.png`, a render from the full-detail gorilla artist workspace. This is a scene render, not a screenshot of Blender's editor UI.
- Runtime: all 26 gallery displays loaded with nonempty geometry and four valid reference textures per selection. Captured each focused model, lineup and enlarged reference. Inspected lineup, gorilla focus and enlarged sheet after fixing focus clutter and sheet sizing. Runtime check passed; see `runtime.log`.
- Navigation: actual title choice opens Mech Workshop, focus/turn/select functions operate, return opens title and restores 320x180 content scale. See `navigation.log` and `tools/debug/catalog_navigation_check.gd`.
- Python scripts compile and the PowerShell launcher parses. The launcher was not used to open an interactive Blender editor during this check.

The sandbox prevented optional Blender file-browser thumbnail caching, Godot shader-cache writes and Godot editor-settings writes. Godot also reported a root-certificate-store error. Native files, imports, rendering and navigation checks still completed. No network or paid tool was used.

No limb, eye, socket, rig or animation correction is claimed. The gallery's 40k/1K proxies are inspection copies; full-detail native workspaces and archived sources remain separate. Game scale, anatomy and final polish remain under review. Existing model-polish outputs and gameplay assets were not replaced.
