# Rhino animation research adapted to this game

Preston supplied `C:/Users/pmcga/Downloads/MOBA Mecha Rhino Animation Blueprint.docx` on 2026-11-08. It was generated from the mech and Sketchfab walking model with generic MOBA context, without our kit or mech design. Treat it as research suggestions, not project authority. This note records the useful lessons and their limits; its linked sources and numeric assertions have not been independently verified.

## Keep and apply

Keep weight transfer driven by actual footfalls: hind propulsion, front suspension accepting load, a quick compression with slower recovery, and a quieter rigid main chassis. Keep armor and broad feet rigid. Use the actual donor's walk and run rhythms instead of replacing them with a generic four-beat timing table.

Keep mechanical secondary motion tied to loads. Our shoulder cylinders are seismic transducers, so animate axial inner-face compression and rebound within mounted ring housings. Keep dorsal drive and horn power cues connected to those loads. Small head counter-motion stabilizes the horn. Recessed leg actuators stay behind bulky armor.

Keep visible anticipation, release and recovery, synchronized to existing gameplay events. Match movement speed to authored stride/cycle length. Use short transitions, in-place baked GLB clips and runtime review from our actual camera. Check contact, loop closure, rigid parts, silhouette and directional views together.

For future separately modeled piston rod/housing assemblies, use endpoint-driven extension with stable axial orientation and a non-collinear up reference. Bake the results for export and avoid cyclic constraints. This is a future construction technique, not proof that the current connected source surface contains independent rods.

## Adapt instead of copying

The report's 36-frame walk and 24-frame run are examples, not universal MOBA requirements. Current faster review uses a 24-frame/.8s walk and an 18-frame/.6s charge loop derived from the actual donor running action. Foot support and stride are fitted to this mech's range. Preview speeds do not replace game balance values.

Use our chase camera (FOV60, pitch30, distance6.5, look height1.2) plus side/front/detail views. Do not widen approved armor 10–15% or pitch the horn upward just because the document assumes a fixed isometric camera. Preserve the current source proportions.

Use existing ability event timing and cancellation semantics. The report's mandatory .2–.3s hit frame, frame8 impact and universal post-hit cancel are not our specification. Likewise, 64 bones is an asserted generic budget, not an established engine limit or project performance result.

## Existing kit remains authoritative

`docs/plan/moba-kits.md` and `scripts/moba3d/rhino_kit.gd` define front plating, short-dash horn toss, ground pound with continued tremble, planted brace, and long stampede ending in a heavy pound. No shield barrier or generic overdrive ultimate is added from the report. Do not replace brace with shield or rename abilities to Dota activity names.

The isolated charge loop prepares animation for stampede; it does not implement its target shoves, 9m/s gameplay setting, collision, final pound or damage. The standalone preview uses travel matched to its own stride so it can be inspected without skating. Production speed/scale integration is a separate test.

The report's steam, thermal exhaust, purge and heat venting do not fit the recovered earth/seismic body concept. Keep local mint resonance through drive, shoulders, horn and grounding feet. No unsupported tail chain or spring solver is added to a skeleton that lacks those controls.

Some inline equations and numeric values are missing from the supplied DOCX text. Do not infer those missing values or treat its citations as validation. Consult the primary source if a future implementation depends on one of its external technical claims.

## Current review location

`D:/dev/_scratch/rhino-donor-2026-11-08/seismic-life-v2/`: faster donor-derived walk, distinct donor-running charge, broader shoulder-face controls with visible axial travel, and separate playable comparison. Original accepted foundation and seismic-life-v1 remain preserved. This file records reusable lessons without installing or editing an unrelated personal skill.
