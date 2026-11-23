# Model repair queue status: November 14, 2026

This inventory answers whether every creature has been worked on. It separates a first repair pass from final polish and uses the current downloaded files and Workshop entries.

| Group | Count | Current state |
| --- | ---: | --- |
| Creature designs with versioned geometry repairs/restorations in this lane | 23 | Each has had a repair pass; Jellyfish still lacks its final main Godot Workshop check. |
| Creature designs using authored exports from other model chats | 5 | Gorilla, Hippo, Kangaroo, Pangolin and Rhino. Existing authored work preserved; no new repair/readiness approval from this inventory. |
| Melee Minion | 1 | Local repair, 18-joint diagnostics and native Workshop check completed this turn. |
| Ranged and Siege Minions | 2 | Still queued for this repair pass; currently located texture GLBs contain no skin/skeleton. Their original static GLBs and four-view references exist. No new rig is authorized or implied. |

The Workshop has 31 entries. The 28 creature-design count excludes the separate Gorilla Meshy variant, the alternate Shoebill used only as a backplate reference, and Melee Minion. Those extra entries do not represent three additional creature designs. Ranged and Siege Minions are not yet published in this repair lineup.

## Creature repair passes

- Bison: `docs/art/moba/bison_l/topology-repair-v1-2026-11-11/bison-rigged-local-repair-v1.glb`
- Bombardier Beetle: `docs/art/moba/bombardier_beetle_m/joint-restoration-v2-2026-11-11/bombardier-beetle-joints-restored-v2.glb`
- Chameleon: `docs/art/moba/chameleon_m/local-repair-v1-2026-11-11/chameleon-rigged-local-repair-v1.glb`
- Cobra: `docs/art/moba/cobra_m/base-reshape-v2-2026-11-10/cobra-rigged-base-reshape-v2.glb`
- Dragonfly: `docs/art/moba/dragonfly_m/local-repair-v1-2026-11-13/dragonfly-rigged-local-repair-v1.glb`
- Electric Eel: `docs/art/moba/electric_eel_m/local-repair-v1-2026-11-13/electric-eel-rigged-local-repair-v1.glb`
- Falcon: `docs/art/moba/falcon_m/local-repair-v1-2026-11-13/falcon-rigged-local-repair-v1.glb`
- Fennec: `docs/art/moba/fennec_s/local-repair-v1-2026-11-13/fennec-rigged-local-repair-v1.glb`
- Hornet: `docs/art/moba/hornet_m/local-repair-v1-2026-11-14/hornet-rigged-local-repair-v1.glb`
- Hummingbird: `docs/art/moba/hummingbird_s/needle-length-v3-2026-11-10/hummingbird-rigged-needle-length-v3.glb`
- Jellyfish: `docs/art/moba/jellyfish_m/local-repair-v1-2026-11-14/jellyfish-rigged-local-repair-v1.glb`
- Mantis: `docs/art/moba/mantis_m/surface-restoration-v1-2026-11-10/mantis-restored-six-limbs-rigged-v1.glb`
- Pistol Shrimp: `docs/art/moba/pistol_shrimp_l/local-repair-v1-2026-11-14/pistol-shrimp-rigged-local-repair-v1.glb`
- Scorpion: `docs/art/moba/scorpion_m/local-repair-v1-2026-11-14/scorpion-rigged-local-repair-v1.glb`
- Shark: `docs/art/moba/shark_l/local-repair-v1-2026-11-14/shark-rigged-local-repair-v1.glb`
- Shoebill: `docs/art/moba/shoebill_m/circular-rim-v2-2026-11-13/shoebill-circular-moon-rim-v2.glb`
- Spider: `docs/art/moba/spider_m/surface-restoration-v1-2026-11-10/spider-restored-eight-legs-rigged-v1.glb`
- Squirrel: `docs/art/moba/squirrel_s/local-repair-v1-2026-11-14/squirrel-rigged-local-repair-v1.glb`
- Tortoise: `docs/art/moba/tortoise_l/local-repair-v1-2026-11-14/tortoise-rigged-local-repair-v1.glb`
- Wolf: `docs/art/moba/wolf_m/local-repair-v1-2026-11-14/wolf-rigged-local-repair-v1.glb`
- Golden Beetle: `docs/art/moba/gold_beetle_objective/front-leg-restoration-v2-2026-11-13/gold_beetle-front-legs-restored-v2.glb`
- Wyvern: `docs/art/moba/wyvern_objective/repair-v1-2026-11-11/wyvern-objective-repaired-v1.glb`
- anyklo: `docs/art/moba/anyklo_objective/local-repair-v1-2026-11-14/anyklo-rigged-tail-mallet-v1.glb`

## Remaining work

- Jellyfish: final native Godot Workshop/original-review-sheet/49-joint/ChaseCamera3D check. Its geometry, joint diagnostics and isolated Summer review passed. Existing opaque dome/window mismatch remains an additional visual limit.
- Ranged Minion, then Siege Minion: inspect actual exports and geometry against their references. Their located texture exports have zero skins/joints; do not claim them rigged or automatically rerig them.
- Later polish: existing material-bake defects, independent appendage control, authored animation and optimisation. Spider, Mantis and Hornet are high-detail review restorations, not approved production budgets.
- Existing authored lanes and the separate Gorilla Meshy variant retain their own review state; archived/current presence does not establish a new complete repair pass.

Hornet's previously pending native check was completed after Wolf and must not be reported pending again. anyklo is the renamed cyber-tortoise ankylosaur objective and remains distinct from the original Tortoise. All original generation sheets, source archives and earlier repairs are preserved.
