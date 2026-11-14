# Gorilla polish, first refinement

Current source: D:/user/Downloads/Gorilla_s - Hunyuan 3D v3.1 Pro.glb. This is the correctly named file Preston confirmed, SHA256 5c223ba84c7cde87be15d75b9414b13630c6e75760c019eb9bedc2828ff6d915. gorilla-source.glb is its isolated byte-identical copy. The earlier misnamed input was the same model. No old locally built gorilla is used.

## Result

![Compared finishes](gorilla-polish-comparison.png)

Refined D keeps C's graphic armor lighting, reduces the broad rim from 0.14 to 0.075, reduces its bright lime material contribution, and replaces toon specular with a smoother metal highlight. Painted armor has low metalness and roughness 0.64; light neutral hardware receives metalness up to 0.78 and roughness down to 0.36. Dark mechanisms retain a rough, darker response. This produces a less blown-out edge treatment than C while keeping the shoulder and fist masses readable.

The change is visible but modest. Some bright lime persists, particularly the back panel. The generated mesh still has faceted/uneven shoulder and head surfaces, visible in the close views. This pass does not repair geometry or claim final MOBA quality.

Material regions are inferred from the existing texture colors in the shader. They are provisional color masks, not a hand-painted ID map. No new bolts, scratches, bevel geometry, model parts or baked texture detail were added. Existing large hex panels and power channels are preserved.

## Playable review

Close any existing Godot renderer, then run open-preview.ps1 with PowerShell. It opens a separate review window, not the match. Keys:

- 1: original material; 2: earlier graphic C; 3: refined D.
- Left/right: rotate the model.
- Up/down: move it farther/nearer.
- Escape: quit.

The launcher checks for an existing Godot process. preview.gd can also be run with Godot using the project path and -- --interactive. Without that flag it saves the controlled screenshots and exits. The interactive preview was run using -- --preview-check; its actual visible window was captured and inspected at 1280x720. That check sends 1, 2, 3 and Right through Godot's input pipeline, verifies the resulting rotation, and returns to the review angle for the screenshot.

gorilla-finish.gdshader is a reusable shader version with refined enabled by default. Bind the source model's base-color, normal and metallic/roughness textures to base_map, normal_map and orm_map. The preview contains the same shader text and configures those inputs explicitly. This Godot material response is not baked into gorilla-source.glb; loading the GLB alone shows its original materials.

## Verification

- 30 saved frames across original/C/D, four near angles and one 8 m farther angle, each at 1280x720 and 320x180.
- Uses the actual arena scene, foundry theme, fixed FOV 60, pitch 30, distance 6.5 m, look height 1.2 m. Uniform test scale remains 2 m tall, not an approved production size. Geometry, pose, camera and lighting are identical for each comparison.
- Reviewed front, three-quarter, rear and distant D images, plus the visible preview screenshot. capture-manifest.json records outputs and transforms. verification.json records source hashes and output counts.
- No shared arena/renderer edits; no model installation, animation-lane changes, paid services, account-key inspection, commits or downloaded software.
- Existing certificate-store and shader-cache-write errors appeared, and resource cleanup warnings occurred at exit. Captures and preview checks completed. This is not a frame-time benchmark, and the warnings have not been diagnosed in this lane.

## Ownership and remaining work

Character materials: next test an authored material mask, more controlled lime/green power color, and isolated geometry cleanup. Keep the broad bulky silhouette and meaningful negative spaces. Do not smooth the entire machine into plastic or add tiny detail that disappears at range.

Map lighting: held fixed. No exposure, new light, sky, ambient, floor, shadow or global renderer changes. Distant subject contact/grounding still deserves a dedicated shadow check.

VFX and team cues: no active shield, attack or ability effects; no opposing same-character teams, HUD or fog of war in this isolated review. Permanent glows must leave room for active ability emphasis. Team readability remains unverified.

Performance: the source still has 499,148 triangles, three 4K maps, no skin or animation. These are source assets, not a match-ready budget. All 26 correctly named Hunyuan exports were inventoried separately in ../DOWNLOADED-MODELS.md and ../downloaded-model-inventory.json. Most are about 500k triangles, all are static, and each has three 4K maps. Optimize and rig an isolated source after this look is chosen; verify silhouette, shading and crowd frame time before rolling out across the roster. The extra shoebill is only a back-plate reference per its filename.

Research principles and source coverage are in ../RESEARCH-STATUS.md; no further web claims or paid research were needed for this refinement.
