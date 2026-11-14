# Gorilla: rebuild one punch before another chain

Preston rejected v15 because the motion looked like a limb swing. Preserve that correction: clearance, floor and endpoint counters do not certify intent or weight. v16 is one punch study for visual review, not an approved replacement three-hit chain.

## What failed

Near v15's supposed contact, the fists travel substantially sideways/down or already reverse away from the target. The wider shield-clearance corrections distorted the source arcs. The torso was restricted to accommodate a planted hand, hips were fixed, and no clear sequence loaded the elbow, drove through contact and recoiled. The target timer did not prove a meaningful punch.

Diagnostic: scratch `v16/rejected-v15-motion-diagnosis.json`. Mean forward fractions of fist speed in the sampled hit neighborhoods were roughly 0.50, 0.37 and 0.31 for A/B/C. These explain part of the problem; they are not a substitute for watching the gesture.

Re-inspected the supplied Rampage biped melee clips as well as the earlier quad set. Their large arcs and pose/anatomy differences are not automatically a straight punch for this wider shielded mech.

## Reference and authored beats

Read [England Boxing's Level 2 coaching handbook](https://www.englandboxing.org/wp-content/uploads/2022/03/Level-2-Coaching-Handbook-compressed.pdf), especially its punching-mechanics and straight-punch sections. Useful principles: grounded support, coordinated body rotation, arm acceleration toward contact, aligned wrist/knuckles, and return to guard. The mech animation adapts those principles to its knuckle stance and bulky hardware; this is not an exact human boxing motion.

Created `Gorilla_Punch_Study_v16`, 56 frames at 60fps (0.933333s). Source is the approved v14 model/idle. No geometry, rest proportions, materials, textures, skin weights or skeleton changes. The new file also retains `Gorilla_Idle_v14`.

- F0–12: unweight and lift the fist into a visibly folded arm; load the stance.
- F12–15: brief chamber, with hip motion leading the shoulder.
- F15–23: elbow unfolds and fist accelerates along one deliberate line into the pad. The shoulder turns forward, with a small hip/torso drive; the head stays aimed.
- F23–25: contact and a short push/reaction, not a huge looping follow-through.
- F25–36: draw the fist back along the strike lane to guard.
- F36–56: lower to the original downward knuckle stance and settle.

The other fist and both feet are solved to planted positions. The knees respond to the small hip movement. Nothing is made heavier by scaling bones or reshaping the pelvis. This prototype's 0.383333s contact is an animation-study time, not permission to change kit balance/cooldowns.

## Evidence and limitations

The loaded arm's shoulder-to-wrist span is about 42% of its chain length; it opens to about 89% at contact and 91% through the short push, without hard reach clamps. During the drive, sampled fist velocity follows the intended strike direction. Maximum fist speed is about 10.94m/s, and recoil is slower than the strike. Contact vertices on the gray fist place the studio pad's front face; its spring response starts at contact.

All 57 authored poses pass the same targeted forearm/shield-to-selected-helmet/back-cell surface test. Feet and supporting hand stay within numerical sub-micrometre endpoint error; attack endpoints agree. Those checks support the asset's integrity; Preston's visual review still determines whether it reads as a convincing mech punch. A fully fixed walk pelvis is not claimed.

Rendered loaded, drive, contact and recovery poses from side and front; rendered full-speed motion at 60fps, plus a half-speed copy. Side view deliberately comes first. Reimported into Godot and exercised punch/idle transitions and contact markers. Headless startup still has the environment's certificate-store diagnostic; do not call that log error-free.

## Artifacts

Source/interchange: `art/model_catalog/workspaces/gorilla_one_punch_v16.blend` and `.glb`.

Isolated native review: `tools/debug/gorilla_one_punch_industry_test.tscn` / `.gd`. Repeats one punch with idle gaps; left click/Space supports manual review. Its pad flash/recoil is presentation, not a new gameplay damage system.

Scratch root: `D:/dev/_scratch/gorilla/meshforge-2026-11-08`.

- `build_punch_v16.py`, `render_punch_v16.py`, `check_punch_clearance_v16.py`.
- `v16/one-punch-study.json`, `armor-clearance-audit.json`, `target-contact.json`.
- `v16/punch-side-*.png`, `punch-front-*.png`.
- `v16/one-punch-full-speed-v16.mp4`: full speed, side then front, 60fps.
- `v16/one-punch-half-speed-v16.mp4`: the same motion at half speed.
- `industry-punch-v16/one-punch-industry-v16.mp4`: FFmpeg industry-map preview.

## Retained shared lessons

Read `docs/team/ANIMATION_LANE_EXCHANGE_2026-11-08.md` and `docs/reference/tartarus-arena-review-2026-11-08.md`. Confirmed in the existing `ape_kit.gd` and `kit_feel.gd` that damage, directional hit feedback, contact hit-stop and cancellable backswing already exist. Preserve them; this pass does not rewrite the kit/framework or assume these features are missing. A future accepted skeletal clip needs its real contact bound to those existing events, with interruption/return-to-motion checks and no duplicate hit-stop layers.

The rhino exchange reinforces preserving approved bulk, original rig/textures and rigid part ownership. This pass preserves v14 geometry/weights, does not reuse rhino bone mappings, and does not edit the rhino lane. Short safe-copy/undo edit recordings remain an option when Preston wants a manual correction explained; no tutorial was requested in this pass.

Recording note: the first native capture received live right-drag camera input. The final record mode fixes chase yaw at 0 and disables unhandled camera input during capture; normal review still permits manual camera movement. Studio full-speed video is 3.866667s/232 frames at a true 60fps, side then front. Half-speed copy is 7.733333s/232 frames at 30fps. Native recording uses 30fps sampling for stable capture; this does not change simulation or authored timing. Export validation confirms the project GLB matches the source and contains the 0.933333s punch plus original idle. Existing kit feedback and attack parameters remain untouched.


Final preservation check independently reopened v14 and v16: all 69 mesh objects match in geometry, topology, UVs and named skin weights; all 34 rest bones match. See v16/preservation-validation.json. Final fixed-camera native capture is 16.0s/1280x720, 477 captured frames on the 30fps time base; inspected extracted gameplay frames and actual start/contact/recovery logs. Source studio preview retains all 232 authored samples at 60fps. The existing production ape_kit.gd and kit_feel.gd were read only, not edited.

