# Current MeshForge gorilla material pilot

Preston supplied `D:/user/Downloads/rhino_s - Hunyuan 3D v3.1 Pro.glb` and confirmed that it is the current gorilla despite its filename. This supersedes the old local gorilla test. Folder name preserves the submitted filename for traceability, not creature identity.

![Material alternatives](material-comparison.png)

## Recommendation, awaiting Preston's choice

C is the strongest starting point for match readability. Its shoulders, hands and hex panels remain easier to distinguish farther away. Tone down its lime highlights, retain dark joints, and bring back restrained metal response on exposed hardware in a subsequent pass. It is a starting point, not finished art direction. B is closer to the original export; its material change is too subtle to produce a substantial clarity improvement in this setup.

| Look | Controlled material treatment | Visual finding |
|---|---|---|
| A | Original export materials | Clear broad green armor and orange panel frames; shaded upper surfaces lose separation against the dark arena. |
| B | Satin green armor, metallic exposed surfaces, reduced normal strength | Small improvement; close to A in play. Color-derived masks need authored replacements before production. |
| C | Toon diffuse/specular response, low metalness, broad rough highlights, weak rim | Best visibility of armor masses at distance; saturated lime and bright silver pull attention too strongly, and broad surfaces can feel plastic. |

## Evidence and limits

- 30 Godot captures: three looks, four near angles, one distant angle, each at 1280x720 and 320x180. Capture dimensions are measured outputs; this does not prove the live game's rendering resolution under every window/stretch configuration.
- Uses the actual `arena_blockout.tscn`, foundry theme, camera FOV 60, pitch 30 degrees, chase distance 6.5 m, target height 1.2 m. Subject stands at `(0,0,8)`; distant case moves it 8 m farther along -Z. Frozen world and source static pose for all variants. No HUD, minimap, fog of war, moving opponents or active abilities in this isolation test. Atmospheric fog remains.
- The supplied source is approximately 0.719 m tall after its authored node rotation. Applied the same uniform scale to make it 2 m tall in every comparison. Production size is undecided.
- Mesh: 499,148 triangles, 306,875 position entries, one mesh/surface/material, no skin or clips. Embedded albedo, normal and metallic/roughness maps are each 4096x4096. The initial attachment and isolated copy matched at first verification. During review the attachment path changed from 50,001,268 to 55,104,504 bytes, with a different hash. This lane never wrote to that path. Captures consistently use the initial preserved copy, SHA256 `5c223ba84c7cde87be15d75b9414b13630c6e75760c019eb9bedc2828ff6d915`. Do not represent these as a test of the later replacement file. See `inventory.json`.
- No mesh, UV, bevel, rig, skin or animation modifications. No retexture baked to the export. Shader overrides are isolated runtime proposals. Existing normal detail was reduced in B/C rather than adding microdetail.
- Shader-cache-write errors and a root-certificate warning appeared, plus cleanup warnings at exit. Despite those warnings, the process completed all 30 captures and a manifest; images were visually inspected. No shader compile failure appeared. Frame time and crowd performance have not been measured.
- Original source GLB, shared runtime, renderer settings and animation lane outputs remain unchanged. No paid services, installations, downloads, account-key inspection or commits.

## Proposed reusable rules, not approved standards

Character surfaces:

1. Keep the broad animal silhouette and bulky shoulder/hand hierarchy. No back-mounted hardware added to replace the supplied design. Recognizable forms come before surface detail.
2. Separate green painted armor, orange panel frames, exposed steel and dark mechanisms by value as well as hue. Replace color-guessing masks with authored material masks before shipping.
3. Use satin painted armor and selective metal on joints/trim. Avoid one shiny metal response over the whole animal. C's low-metal response is a clarity experiment, not the final metal treatment.
4. Preserve the large hex power panels and connecting channels. Keep permanent emission localized so active shield and attack effects can exceed it. Reduce the yellow/lime clipping seen in C before adding bloom.
5. Keep broad bevel highlights at shoulders, hands and major plates. The supplied geometry has uneven/faceted areas; no geometry cleanup has been attempted. Do not disguise those with more noise.
6. Retain existing wear until inspected closely; no scratches, bolts or texture noise were added. Prioritize details that remain visible at opponent distance.
7. Do not adopt 499k triangles or 4K maps as a roster budget. Benchmark several animated units, then test isolated simplification and 2K/1K map variants against this source. Preserve silhouette and panel boundaries in that test. No reduction is approved from this static comparison alone.

Arena lighting findings, for the map lane:

- Warm foundry light and cool dark floor were held fixed. Shaded green surfaces can merge with the background. Raising every surface's emission would conceal that problem rather than establish material quality.
- Contact grounding and moving/cast shadows need a separate test. No new lights, exposure changes, renderer switch or shadow settings were installed.

VFX and team readability findings, for their owners:

- Green hex identity is visible in the static source; active supernatural shield behavior is not tested here.
- Team indicators and overlapping opponents were omitted. Do not conclude that body palette alone identifies friend/enemy. Test team rings, health bars and targeting cues with both teams using the same character.

## Reproduce

Scripts are copied here as `capture.gd` and `review_board.py`. The capture script reads the preserved source at `D:/dev/_scratch/mech-art-direction/rhino-generated/source.glb`. Check that no Godot renderer is running before launch. Run the project's installed Godot with `--path D:/dev/new-mech-rpg --script` followed by the absolute path to `capture.gd`. This makes transient scene/material instances only. It writes captures to this folder. `capture-manifest.json` records the transforms and each output.

Primary-source research and its coverage limits remain in `../RESEARCH-STATUS.md`. The rendered comparison is our own supplied asset, not a shipped-game character or extracted game art.
