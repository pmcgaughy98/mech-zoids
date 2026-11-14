# Rampage quadruped locomotion study — 2026-11-08

User supplied `D:\user\Downloads\paragon_rampage_elemental_20_animations.glb` (19,564,268 bytes). Imported into Blender 5.2.2 LTS. Preserved original file; no production art changes.

## Verified

20 animations, 8 glTF meshes/materials, one skin with 202 joints. Embedded metadata credits Prizrakh/Sketchfab and labels this particular upload CC-BY-NC-4.0. This metadata is provenance, not a determination of the original Epic asset's licensing. This pass uses it solely as the requested private reference.

`Jog_Quad_Fwd` has a 0.533333-second key span. It imports as an action spanning frames 0–12.800001 at 24 fps. Rendered 24 samples from fixed oblique and side cameras and inspected the phase board. Other clips include Idle, quadruped/biped melee attacks, smash, jump start/fall/end, hit reactions, death and emotes. There is no separately named slow walk in the 20-clip inventory.

Visible poses are substantially closer to our desired body plan than the examined Hun Batz/Raijin clips: low forward torso, long arms reaching toward support, curled hands, flexed hind limbs and pronounced vertical body movement. This is a fast quadruped jog. It is not proof of anatomically accurate gorilla slow-walk timing, perfect planted contact or controller transitions.

## Application to our original mech gorilla

Use the reference to inspect shoulder/hip relationship, hand orientation, limb reach and compression/extension. Author original motion on our own rig. Establish our approved knuckles/feet on a ground plane first; solve contact order and support shifts before copying the apparent speed. Adjust wrist angle and stride to our large forearm shields and rigid armor. Verify feet/knuckles do not drift in world space during support. Add game-camera playback and controller-speed matching before claiming runtime quality.

This pass does not retarget or ship the reference clips, and does not alter the approved gorilla's proportions or colors.

## Evidence

Private workspace: `D:\dev\_scratch\rampage-study-2026-11-08`.

- `inventory.json`: embedded provenance, joints, all clip names and times.
- `blender-import.json`: actual objects, actions, slots/ranges.
- `rampage-study.blend`: editable imported model with Jog_Quad_Fwd assigned.
- `render.py`, `render.log`, `render-info.json`: reproducible camera and render setup.
- `gait-phases.jpg`: inspected side/oblique samples at 0%,25%,50%,75%.
- `rampage-oblique.gif`, `rampage-side.gif`: 24-phase loops, approximately 0.53 s after GIF timing quantization.

Previews use Workbench material-color shading, not the original game's shaders/VFX. Removed an unrelated Icosphere injected into the empty scene before calculating framing. Blender saved the study file successfully despite an unrelated thumbnail-cache write warning. No Godot/runtime verification was performed.
