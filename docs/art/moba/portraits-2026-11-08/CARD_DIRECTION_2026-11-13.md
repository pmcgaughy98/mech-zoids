# Card direction catch-up, November 13

## Standing correction: unique backgrounds

Kangaroo assignment completed as a crisp full-resolution card candidate: sunny rooftop boxing ring over a dense city, with blue canvas, cyan projected ropes, skyline, rooftop water tower and canopy. Distinct from Gorilla/Rhino/Hippo scenes.

Latest finish direction: Preston prefers the **non-blurry** version. Deliver the crisp full-resolution illustrated master. Do not add artificial pixelation, blurry resizing, depth-of-field or smeared surfaces; the existing small loading-slot package is a separate implementation concern, not the review artwork.

Current unique scene assignments: Gorilla = stormy mountain hydroelectric spillway; Rhino = dry salt flat/copper sunset/red mesas; Hippo = abandoned chemical pumping station interior with round pressure vats, curved pipes and purple Toxic Flood. Earlier shared-foundry scenes are superseded. Keep scenery unique in architecture, silhouette, weather and light, not merely recolored.

Preston: “Different scene behind gorilla. All unique background scenes.” Every mech card must have its own distinct location, environmental silhouettes and mood. Keep a coherent illustration finish, but do not copy another card's scenery. Current Gorilla candidate is a stormy mountain hydroelectric spillway; Rhino retains its seismic quarry/foundry setting. The earlier shared-foundry Gorilla background is superseded by this direction.

Preston: many mechs are close to game-ready; explore more creativity for loading cards and god cards. These are creative proposals, not approved skins, new kit decisions or completed art.

## Current evidence

Read the current model workbench, catalog, authored runtime profiles, repair lane updates, kit design notes and relevant current kit specifications. `art/arena_models/authored_profiles.json` currently registers gorilla v38, rhino v57, kangaroo r12, hippo r13, pangolin r10, bison r4 and cobra r2. Registration and clip mappings are evidence of authored work, not independent certification of every animation or gameplay behavior.

The Workshop now has 29 entries. Revised anatomy references accompany several repaired models, including Spider, Mantis, Hummingbird, Bison, Cobra, Chameleon, Bombardier Beetle and the objective creatures. Preserve selected limb counts and attachments. Some catalog entries still describe older static display proxies while runtime profiles point to newer authored exports.

Portrait source order: identify the current approved body through its owning lane and actual export; inspect it with its revised review sheets and original identity sheets. Use original sheets for intended colors and parts, but never restore a limb or attachment explicitly removed in a later approved correction. When model and references conflict without a recorded decision, flag the conflict before making artwork.

The existing Mech Legend Card Forge remains the established generation workflow. Do not redesign its shared graph during this catch-up. The saved workflow uses 9:16 generated art and 205x373 loading cards, with a 62-pixel bottom band reserved by the existing layout. Those are existing dimensions, not a permanent limit for future art masters.

## Creative proposals

| Machine | Card moment | Composition and mechanical storytelling |
|---|---|---|
| Rhino | Seismic release | A low three-quarter view of a braced rhino as concentric fractures lift quarry grit. Its shoulder transducers and horn provide the mint light. Strong gold silhouette against navy stone. Keep two horns, thick legs and the short tail readable. Heave is a newer approved direction; do not portray the retired horn-toss dash as its current identity. |
| Gorilla | Hold the line | Gorilla between the viewer and an incoming impact, one forearm cell plate forward, lime hex protection expanding around it. The back reactor powers a fault line through the arena. Preserve the green chest rim and attached forearm cells. Avoid cluttering one card with every skill. |
| Kangaroo | Title bout | A suspended moment between slips: glove near the camera, hips turned, tail balancing the body, ring geometry behind it. Suggest the circling movement with dust and composition rather than extra arms or repeated bodies. |
| Hippo | Pressure release | A low, heavy stance with tank windows glowing and hydraulic vapor forcing water outward. Sell stored pressure and mass, with the actual tank attachments and jaw shape intact. |
| Pangolin | Magnetic force | A tightly controlled curled-body moment, loose metal fragments orbiting along a clear arc. Recheck the latest kit and plate layout before choosing a specific effect. |
| Fennec | Threshold | The machine crossing a portal seam, near side lit by the arena and far side by the destination. Keep its ears as silhouette and preserve current emitter locations; verify the latest Seamwright direction before authoring the effect. |

These take their identity from this game's machines and current kits. No borrowed god appearance, costume or regalia. Effects come from existing mechanical parts. Names above describe art moments, not proposed canon names.

## Card family

- Loading splash: a single dramatic action and environment, with deliberate room for the actual loading layout.
- God/select card: a quieter, distinctive hero pose; face and major attachments remain legible at selection size.
- HUD portrait: its own readable face/shoulder crop, checked small; a full splash downscale alone is insufficient.
- Skin card: retain species, silhouette and attachments; change only the skin Preston chooses, with a setting that supports it.

Create a larger reusable art master before packaging variants. Confirm current UI slot sizes from the actual consuming code before integrating. Treat pixel finish, painterly finish or model-render treatments as explicit visual choices; this catch-up does not authorize silently replacing the established finish.

## Prior portrait state and next slice

Gorilla November 8 pilot accepted by Preston with “Thats it rhino next.” Preserve it. Rhino's subsequent Opal image rendered at blob `73be485a-6564-4350-a247-995e67d0feac`, but the original download was interrupted. No corresponding local source or completed review card was found during this catch-up. Do not call it delivered or regenerate it automatically just to conceal the interrupted save.

Recommended next creative slice: Rhino seismic-release card from the current v57 body, after inspecting its latest silhouette and attachments, with the earlier static portrait treated as historical. One reviewable composition first; no roster batch, live replacements, paid calls or commits launched by this catch-up.

## Design archive located

Preston pointed out the lined-up design archive. Confirmed exact on-screen title MECH DESIGN ARCHIVE in `scripts/scenes/mech_catalog.gd`; scene `scenes/mech_catalog.tscn`, opened through title menu Mech Workshop (`scripts/scenes/title.gd`). This is the shared archive already referenced as Workshop, not a separate missing collection. Current catalog has 29 entries including Golden Beetle and Wyvern. Tab switches Lineup/Focus; Q/E rotates; C compares versions where available; R switches original/review sheets. Inspected saved `reports/model_catalog/lineup.png`; it is an older screenshot with 25 designs plus alternate/rigged entries and does not prove the current 29-entry layout. Use the current archive and its preserved original/review views as the visual identity desk for cards, consulting newer authored runtime exports for poses and later approved changes.


## Pangolin scene revision

Preston requested a dry junkyard rather than a frozen area, preserving and showcasing magnetism. Current candidate: `pangolin/salvage-2026-11-13/junkyard-v2/pangolin-junkyard-master.png`. Warm rusted vehicle stacks, conveyors and gantry crane; scrap plates, bolts and washers levitate along blue field arcs. Preserve unique scenes and crisp masters. Frozen shipyard candidate is historical.


## Bison and Cobra scenes

Bison r4: Eruption in an abandoned locomotive roundhouse at blue hour, four magma-orange stack shots and slag ring. Cobra r2: Breach through an intact wall in an overgrown hilltop observatory at lavender twilight, cyan phase ripples. Both use verified current deployed model renders; crisp full-resolution candidates saved in their dated folders.


## Fennec scene

Threshold card: cliffside skyport at rosy dawn, airship and sail towers, cyan portal showing bright floating islands. Current catalog body rendered and intended sheets inspected; no authored runtime profile registered. Full sharp master in `fennec/threshold-2026-11-13/`. Ornate gate frame is illustrative scene detail, not a new kit requirement.
