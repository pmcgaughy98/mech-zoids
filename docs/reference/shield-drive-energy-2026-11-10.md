# Shield Drive hand energy

Preston: "Make it have shield energy like a shield bash in front on hands."

Arena Play's current gorilla now has two green hex energy faces ahead of the existing hand shields. Their centers follow the actual LeftHand/RightHand poses, using the original shield-cell geometry to locate each face. They face the drive direction rather than wobbling with wrist twist. Thin bright double rims, a transparent face and small inner hex outlines keep the body visible.

The faces build during brace, remain forward during travel, flare/fade on confirmed hit and fade on braking. The controller's idle/interruption transition hides them immediately. They are visual only; existing movement, collision, shield mechanics, damage, source mesh and animation clips are unchanged.

Implementation: `scripts/moba3d/shield_drive_energy.gd`, attached by `arena_gorilla_kit.gd` and driven by its real phase changes. Uses local Godot geometry/materials, no asset generation or paid tools.

Validation: existing 104 arena integration checks pass at 60 fps. Native front-quarter, regular game-camera and side views captured by `tools/debug/shield_drive_energy_review.gd`. Results and preview media are in `D:/dev/_scratch/shield-drive-energy-2026-11-10/`. Both faces appear during Drive and hide after each hit/miss case; interruption is checked separately in the native review.
