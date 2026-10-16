# R1 hangar synthesis: Function review

Proposal, nothing here is canon. R1's supplied brief is the design contract: 14 x 16 x 8 m,
one 6 x 7 m central machine bay, hero at origin facing the camera, a 6 m open bay door,
eight chunky prop families, and a 40,000-triangle complete scene budget.

## Finished human-made references read

- **Armored Core Nexus**, FromSoftware's official manual, garage and assembly sections
  (PDF pages 5 and 8): the garage groups assembly, parts purchase, paint, and test operations;
  the assembly view keeps the currently configured machine visible. The manual also separates
  preparing a machine from mission deployment. We take this workflow and visual hierarchy,
  not its room geometry, weapons, colors, UI, or names.
  [Official manual](https://media.fromsoftware.jp/fromsoftware/jp/static/pdf/031_ARMORED_CORE_NEXUS.pdf)
- **Metroid Prime Hunters**, Nintendo's official manual, Inside the Gunship and Saving Data
  (PDF pages 8 and 9): returning to the ship replenishes resources and exposes equipment,
  logbook, save, exit, and launch operations. A return portal brings the player back near
  this service point. We take the compact return/service/depart loop. Its rooms and assets
  are not imported or reproduced.
  [Official manual](https://www.nintendo.com/eu/media/downloads/games_8/emanuals/nintendo_ds_21/Manual_NintendoDS_MetroidPrimeHunters_EN.pdf)

These sources substantiate gameplay organization, not dimensional room layouts. All dimensions
come from the project's R1 brief and our own geometry. No downloaded game models or ripped assets
were used. The room's original symmetry, props, and placements are proposals.

## Synthesis proposal

One centered machine remains the focus. A sparse service family sits around it: crane for heavy
parts, cart and rack for the mechanic, twin ballast pallets for the gorilla's removable blocks,
coolant service, and one pilot console. Cable trays and flat lights describe the ceiling.
The room palette is gray and gunmetal with restrained orange trim and teal screens, so the
machine's green remains distinct. The door opens onto a four-meter apron rather than a flat wall.

The shell and paired lighting/window/gantry rhythms are bilateral. Asymmetry is functional:
cart and parts on the west, console and coolant on the east, trolley parked at rear-left.
Two 1.2 m staff lanes run beside the parked machine at x = +/-2.95 m, inside the crane posts.
They avoid the outer storage pallets. The selected machine stays parked during base interactions.

Alternative: a service alcove down one side, with all support equipment grouped there. It would
leave more open floor but give the two sides unequal visual weight. The balanced proposal is
the first review candidate.

## Stock-take and contribution

- Build 3D Game Rooms: doctrine, display-gallery adapter, evidence schemas, approval gates.
- Local Blender 5.2.2 LTS CLI: original procedural prop prototypes and actual-mesh orthographic
  floor/ceiling/elevation projections; separate factory-startup process leaves live Blender untouched.
- `blender-game-asset-artist`: metric scale, target-camera contract, editable source, honest verification limits.
- `dom-blender-scripting` and `dom-blender-render-automation`: deterministic bpy builder and repeatable views.
- `atlas-asset-optimization`: silhouette-first polygon budgets and few material families.
- Harness lessons: inspect dim orientations before changing them; preserve existing scene/data; verify support.
- Web: primary-source manuals and live verification that the skill's pinned Meshy model is retired.
- Pillow/NumPy: labeled reference sheet, crisp engineering-line presentation, exact rectangular aperture masks.
- Skill mask tracer: attempted for all openings, unavailable because OpenCV (`cv2`) is not installed;
  a verified pixel-boundary rectangle tracer was used without downloading dependencies.
- Godot/ape model: existing shader and light calibration read; actual machine and runtime are deliberately
  deferred to Form/Runtime, as Task R1 requires. Source model and Claude's build scripts remain untouched.
- Imagegen's earlier workbench experiment is not part of this R1 reference sheet; the task now requests
  free procedural props, and the reference sheet shows those exact prototypes.
- Paid generators, Summer Engine, Retro Diffusion, and Meshy: not used for this room. No paid budget approved,
  no requests submitted, and no account keys accessed. There is no connected Blender MCP in this session.

## Measured Function evidence and limits

The current prototype layout is 3,008 triangles. With an 11,000-triangle hero allowance it is 14,008,
leaving 25,992 for the final shell/detail below the 40,000 total. This is planning headroom, not a
measurement of the completed room. Eight asset families have thirteen placed instances.

The lower plan and reflected-ceiling plan are derived from the same actual prototype geometry.
The lower plan excludes the door lintel/sign and overhead crane bridge so the passage remains clear.
The source projections, metadata, four elevation views, and aperture contours are preserved.

Function preflight verifies the references, dimensions, rectangular mask hashes/apertures, and planning
budget. Actual runtime hero fit, calibrated colors, navigation, final shell/Boolean/manifold checks,
lighting, and complete-scene performance are still unverified and belong to later gates.

The bundled gate validator was run unchanged. It correctly stops on pending human approvals. It also
requires paid Meshy props and a positive credit ceiling even for procedural geometry; that policy
does not match R1's explicit preference for free procedural props. The incompatibility is recorded,
not bypassed with invented approvals or credits. Meshy says its pinned `meshy-5` retired October 10, 2026.
[Verified official pricing/model notice](https://docs.meshy.ai/en/api/pricing)

Next step: Preston reviews the Function layout, eight prop references, and three openings. Only after
approval does Form build the sealed shell, subtract real apertures, place the machine, and audit the room.
