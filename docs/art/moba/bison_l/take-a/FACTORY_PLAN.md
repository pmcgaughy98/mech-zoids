# Direct Codex production plan

Prepared 2026-11-06. No Claude session or subagent is needed.

## Tools and access

| Tool | Job | State and cost |
|---|---|---|
| Built-in image generation | One new four-view design sheet | Available. Uses this Codex session; historical factory sheet jobs are roughly 60k-105k tokens, with reported cap overshoots around 75k. Planning allowance about 180k; this is a historical estimate, not a metered quote or enforceable cap for the built-in image tool. No reliable per-image dollar/token charge exposed. Get Preston's yes first under the project rule. |
| Python, Pillow, NumPy | Crop and prepare the four inputs, audits and review boards | Python installed; verify libraries before processing. Local work, no generation fee. |
| MeshForge / Hunyuan 3D v3.1 Pro | One model using all four images | Vendor docs list $0.375 base + $0.15 extra views, PBR off: estimated $0.525. Verify the live button before submission; no automatic paid retry. Rhino precedent succeeded at that price. |
| MeshForge manual quadruped rig and preset animation editor | Fit joints, rigid parts, test gait and abilities | Documented free local-browser workflow. Do not use AI joint placement, AI animation, Meshy rig, remesh or retexture without a separate quote. Live browser/connector access not currently verified. |
| Blender | Render the same model/rig at exactly 35 degrees | Local executable location still needs verification. Copied renderer exists under `D:/dev/_scratch/rhino/meshforge/tools/`; adapt a bison-local copy, never edit the rhino/Hollowtide source. |
| Project pixel finish and Godot checks | Palette, edge treatment, sprite pack, real-camera planting | Existing method and scripts. Read relevant files before adaptation. One Godot process at a time. |
| Firecrawl, Retro Diffusion, PixelLab, SpriteCook, ElevenLabs | Potential later research/animation/audio | Not used or charged for this preparation. No need for them in the first body test. |

## 1. One reference image

Use `prompt-model-views.txt` verbatim with only the Drembit craft reference, from the same reference used by the approved fleet. Keep `sheet_raw.png` unchanged and save generation provenance/hash. No paid reroll. Separate the four cells by connected components/known grid, inspect for clipping and hidden-leg/vent errors.

Model inputs retain their detail and share ONE scale. Remove magenta and fringe, export front/left/back/right on a common plain square canvas, preserving relative dimensions and the common ground baseline. Do not separately stretch the front, rear or profiles to force agreement. Keep small final sprites for later. Record crop boxes and transforms in `input/prep.json`.

Get Preston's visual decision on the design before spending on a model. If a view is inconsistent, report it; do not send contradictory images to the model generator.

## 2. One MeshForge model

Use the existing authenticated browser profile; never inspect, extract, copy, type or request the saved fal key. Native MeshForge tools are not exposed here; the first CUA inventory attempt failed, so establish working browser access or an approved direct connector first. A Claude-side MCP configuration is not proof that Codex has access.

Upload front, LEFT profile (head left), back, RIGHT profile (head right) into the correct extra-view slots. These are four views of ONE model, not a batch of four models. Select Hunyuan 3D v3.1 Pro, PBR OFF, inspect the quoted total, and submit only after Preston's priced approval. Record job identity and outcome. Preserve/download the original GLB with approval if required by his download preference. Save edited copies separately.

Verify two horns, four separate legs, no fused armpits/inner thighs, clear hoof splits, fixed vent/grille positions, adequate underside and no smoke geometry. Compare projected proportions to the inputs numerically; report flaws before rigging.

## 3. One rig, one walk pilot

Use the manual Quadruped template. Reduce an over-dense mesh on a COPY before skin binding. Place joints inside each limb; check front and side. Preserve head/horns/shoulder housing rigidity and vent socket positions. Avoid bending plates like skin. A walking preset must demonstrate a correct four-legged gait, rather than being accepted by name.

Inspect planted-foot slip, limb separation, root bob, shoulder plate deformation, horns, tail and vent attachment. Keep root motion and playback stride consistent. First clips: standing idle, one walk loop, then basic head sweep and charge anticipation. Body effects remain separate. Price/approve any subsequent generated assets separately.

## 4. Render and finish

From the same source rig, render eight azimuths in 45-degree steps at a fixed 35-degree orthographic elevation, one shared framing/scale/light and frame-zero pose. Check front/back/profile labels on a contact sheet before the full render. Do not force equal screen heights at this elevated camera: projection changes are real; use one actual model and camera.

Target the current 192x192 animation canvas with near feet at row 160, keeping head, horns, vents, tail and eventual effects inside a measured safe extent. L size at 0.020 m/texel is only a working proposal until Preston picks the size. Record bounding boxes, ground point, camera settings and real source dimensions. Use per-view/per-frame feet metadata if needed; do not shift the model to hide a camera/ground problem.

Pixel finish: one shared palette of at most 16 colours, retain the armour shade ramp and hot apertures, no magenta fringe or lone pale rim pixels. Selective outline only at pack time unless specifically directed otherwise. Do not paste mismatched parts over frames. Frame zero and recovery stills match the approved body exactly. Model/rig correction precedes sprite patching.

## 5. Review and install

Provide game-size views and a turning/walk clip. Verify planted feet, matching silhouette through animation transitions, no face in rear views, coherent horn/vent counts, and readable heat/steam cues. Test a kit event against its actual contact/release frame. Adapt the packer and a small reveal/test scene only after the body is accepted. Do not alter the main roster, shared match files or existing lane-owned work during this first body review.

## Evidence

- Current project playbook: `docs/art/moba/ANIMATION_PLAYBOOK.md`.
- Rhino actual model result and unfinished tests: `docs/art/moba/rhino_l/MECH_STATUS.md`, MeshForge section.
- Vendor docs read: https://www.keyframe.it.com/docs/meshforge . Prices are estimates; the live action price and fal receipt take precedence. Manual quadruped rigging, exports and sprite sheets are documented free. AI animation and AI joint placement are paid.
- Production updates belong here and in `../MECH_STATUS.md`; no assumption of access to another chat's live tools.
