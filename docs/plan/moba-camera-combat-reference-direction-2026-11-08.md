# MOBA camera and combat reference direction — Preston, 2026-11-08

**Primary reference: original SMITE. Secondary reference: Paragon.** Preston explicitly set this priority during the gorilla sharp-turn review, and said it applies to the game's perspective, camera movement, skill use and overall combat feel.

Use the third-person chase/aim viewpoint as the normal review perspective. Avoid automatic orbit-showcase cuts when evaluating movement or combat. Camera orientation, character facing, strafing, aiming, movement responsiveness, skill targeting and feedback must be considered together in future combat work. This is a direction brief, not a claim that those systems are already implemented or a specification of final balance numbers.

The accepted gorilla locomotion test uses3.5m/s as the project's existing controller baseline, with an illustrative+25% speed-modifier preview. Do not return to stride-derived slow travel as the gameplay baseline. Preserve the reduced1.0 model display scale. The current sharp-turn review blends visual heading while retaining responsive movement and adds planted-contact correction.

Current review evidence: `D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-turns-v7/gorilla-sharp-turns.mp4`. Detailed tested behavior and limitations should be read alongside the gorilla's status file. New camera/combat changes should follow SMITE first; use Paragon as a secondary comparison rather than equal priority.
