# Free gorilla animation experiment, 2026-11-07

Status: playback test completed on the legacy local gorilla rig. Not approved production animation and not the latest power-gorilla model.

## Watch

- `free-attack-test.mp4`: a 1.03-second attack shown three times with holds, in two views. Top: the older local mechanical gorilla. Bottom: the original kaiju donor. Clay shading is deliberate for inspecting shape and contact.
- `attack-contact-sheet.png`: five sampled times from both views.
- `legacy-gorilla-attack-test.blend`: playable copied scene, frames 0 through 31, 30 fps. Press Space in Blender. Donor mesh is hidden in the saved scene.

## What was actually done

Downloaded the nine selected free kaiju clips and inspected their GLB animation data. `source-clip-manifest.json` records pinned upstream revisions, URLs, sizes, SHA-256 hashes, exact animation names, lengths, channels and skin joints. Full upstream CC0 text and README are included. The README identifies software as MIT and models, rigs and animations as CC0. No paid tools, generators, credentials or packs were used.

Found `docs/art/3d/ape_l_v2.blend`: an older 14-bone gorilla rig with walk, gait, punch, slam, throw, hit, idle and death actions. All 41,510 vertices have exactly one bone weight. The original file was opened read-only and never saved over. The latest `take-b-power/white_views` are concept PNGs, not a model or rig. Checked the ape art directory, project 3D art, scratch model files and top-level Downloads model files; no latest power-gorilla model was found there. This is not a claim that no other personal copy exists. The separate MeshForge connector profile was previously established to contain only the demo Orc, so it was not used for generation or credential access.

Transferred changes in the CC0 Attack clip's right upper-arm, forearm and hand rotations onto a copy of that older rig. Used 70 percent rotation amplitude. Kept the torso, head, opposite hand and feet at rest. This is a partial arm-motion retarget, not a full-body gorilla retarget. It has no shield tracks, hit event, recovery cancel, walking integration or match timing changes.

The first transfer penetrated the floor by 0.219 m. A minimal sampled shoulder-pitch correction removed that penetration without scaling armor or moving the supporting limbs. Scripts, floor corrections and contact samples are included for review and reproduction. `build_test.py` runs with Blender; `fetch_and_inspect.py` downloads the pinned-source manifest inputs, and `package_review.py` creates the review frames. Scratch renders and original downloads are in `D:/dev/_scratch/gorilla-free-animation`.

## Verification and result

Inspected sampled rendered poses from both sides of the transfer and the two-angle contact sheet, then decoded the final video into a review sheet. The support knuckles stay on the floor, with 0.000 m center drift; feet have 0.000 m drift and a fixed 0.026 m clearance inherited from the model. The striking fist clears the floor by at least 0.003 m at the 32 sampled frames. Armor retains single-bone rigid weights and no scale animation. These are sampled mesh measurements, not a continuous collision guarantee or a Godot test. Full figures are in `verification.json`.

The transferred arm motion is visible as a small lift/swipe, but it fails the heavy gorilla punch goal: the torso remains static and the donor's actual attack reads mainly as a head/jaw lunge on a tailed biped. Its arm movement is secondary, so this clip is not recommended as a punch donor. The kaiju walk is not a verified knuckle-walk. Do not import these clips wholesale as gorilla locomotion. The negative fit result is useful: free access and a working retarget pipeline do not establish that the source contains the needed motion.

The free download and partial transfer pipeline is proven on an actual local gorilla rig. Production use on the latest power-gorilla still needs that design's actual GLB/BLEND/FBX mesh, rigid armor assignments, fitted rig, support-limb IK and authored body weight. Nothing was integrated into shared gameplay or committed. No Godot process was launched.

Guidance used: CLAUDE.md, START_HERE.md, how-preston-works.md, ANIMATION_PLAYBOOK.md, mech-sessions-2026-11-05.md, previous animation source research, and local atlas-animation / blender-export-pipeline skills. Local Blender supplied the copy, transfer, measurements and diagnostic rendering; Python/Pillow and FFmpeg supplied the review video. Bypassed paid Firecrawl retrieval in favor of free upstream web/source access to honor the free-only request.

Sources: https://github.com/Mesh2Motion/mesh2motion-app and https://github.com/Mesh2Motion/mesh2motion-assets . Exact immutable raw URLs are in the manifest.
