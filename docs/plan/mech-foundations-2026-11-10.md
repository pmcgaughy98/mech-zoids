# Mech foundation implementation, started 2026-11-10

Preston requested Grok learn from the current rhino and especially gorilla, then build animations, kits and gameplay foundations for the other mechs so specialist agents can refine them. He explicitly selected Grok's recently revised recommendations, including Seamwright fennec, rather than Codex's alternative proposal. This is production authorization for a staged foundation batch, not a claim all kits or rigs are complete.

## Running work

Grok implementation workspace: `D:/dev/_scratch/grok-mech-foundations-2026-11-10/`.

Read `STATUS.md`, `output/MECH_HANDOFF.md`, `output/ANATOMY_AND_RIG_QUEUE.md` and actual files under `output/game_patch/` and `output/assets/` before relying on results. Launch log: `grok-build.log`; initial unified exec session 84191. One bounded 32-turn initial batch through the existing subscription, no subagents or automatic follow-up jobs.

Scope: preserve current gorilla/rhino and original model sources; learn their native clip aliases, phase clocks, hit/cast events, interruption and real-target wiring. First staged vertical slice targets revised fennec and falcon, then common foundation coverage for all 25 catalog identities plus legacy lobster. Code/manifests alone are not an animated/playable completion. Missing rigs and anatomy defects must remain explicit. Rig/extra-limb repair is permitted on independent copies, with anatomical checks and preservation evidence. No generic humanoid retargeting across animals.

Grok may author and check local Python/Blender implementation assets in its staging folder. Live game, existing animation exports, downloads and other lanes' files are read-only to it. Shared patches must be reviewed and tested before integration; another lane may own Godot. No paid tools/generation, credentials, purchases, installs, commits or other chats.

## Actual downloaded rig audit

Directly inspected GLB skin arrays, mesh skin bindings and JOINTS_0/WEIGHTS_0 in the current game-model downloads under `D:/user/Downloads` and the corresponding files in `C:/Users/pmcga/Downloads`. Full audit and repeatable script: `D:/dev/_scratch/mech-rig-audit-2026-11-10/`. Nested model-file enumeration did not locate a separate shoebill rig export.

| Model | Bound rig found | Joints | Animation clips in that download |
|---|---|---|---|
| Gorilla, Meshy-named export | Yes | 34 | 0 |
| Rhino, Meshy-named export | Yes | 31 | 0 |
| Kangaroo, recent front export | Yes | 29 | 0 |
| Shoebill, current front export | No glTF skin/bound rig found | None | 0 |
| Other 21 catalog identities | No bound rig found in matching downloaded GLBs | None | 0 |

The authored runtime gorilla and rhino have separate local animation work; the empty animation arrays above do not mean those completed clips are missing from the game. Rig presence alone does not certify anatomy, weights or the service that made the rig. Kangaroo's existing native rig master is preserved in `D:/dev/_scratch/kangaroo-smart-rig-2026-11-10/`; generic bone names require actual anatomical mapping.

Also present: an older 28-joint rhino MeshForge test, and a 202-joint/20-animation Paragon donor reference. These are separate from the requested Meshy starting rigs. Legacy lobster has no matching catalog GLB; pistol shrimp is a different creature.

## Shoebill backplate task

Sent directly to the existing Mech Model Art Direction and Polish chat (`01a1b70f-e70f-71b3-bdc4-5cfac2d19e4e`) at Preston's request. Transfer only the correct moon plate from the explicitly named donor to a copy of the better current recipient, preserving its model/rig. Donor: `D:/user/Downloads/shoebill_front - Hunyuan 3D v3.1 Pro (1)(correct moon plate on back only use for that other model is best).glb`.

The chat was informed of the bound-rig audit discrepancy before transfer. It must verify the recipient or stage a reversible copy without claiming the missing rig was preserved. No new rig should be fabricated to conceal the missing export. Inspect that chat's actual output before claiming this transfer is finished.
