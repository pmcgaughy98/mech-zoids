# Downloaded lineup / rig audit and final hornet cut

Preston requested removing the hornet's small underside legs, adding the previously omitted touched-up mantis to Downloads, and checking whether any lineup animals lack a3D model rather than merely a rig. He is rigging shoebill, spider and mantis himself; do not duplicate those jobs or start new paid generation.

## Delivered

- `D:/user/Downloads/hornet_front - 6 legs touchup.glb`: removed the four tucked-under legs R2/R4/L2/L4 plus the previously removed floating claws. Keeps front/middle/rear legs on each side, six total. Eight cut openings capped. Preserves textures, materials, UVs, original object placement and per-corner normals outside the cuts. Three textures embedded. Unrigged. Use this export instead of the earlier floating-claws-only version for the next rigging pass.
- `D:/user/Downloads/mantis_front - floating legs removed.glb`: byte-identical copy of Claude's `proportions-2026-11-10/mantis/mantis_after.glb`; two floating legs removed, three embedded textures. Unrigged. Older files are retained.
- Fixed shoebill and eight-leg spider remain in the same loose Downloads folder from the prior delivery.

Hornet build, cut log, before/after/reference render and scripts are under `D:/dev/_scratch/hornet-inner-leg-touchup-2026-11-10/`. Textured front, side, back and underside views were inspected. This is an exported mesh correction, not a game registration or an animation claim. No source archive or shared game scripts were changed.

## Model versus rig inventory

Checked GLB JSON contents, not just folder names, for files in the loose Downloads folder and the two `Mecha Beast GLB` folders. Compared the25 unique catalog designs plus the older approved lobster identity and the three new minion classes. Reference-only shoebill and duplicate rigged-gorilla catalog entries are excluded. No Hollowtide files were inspected.

**No local downloaded or catalog source model found:** lobster. The pistol shrimp is a different animal and does not cover that missing entry. This does not establish whether a lobster exists in an online generation library; it may simply not have been downloaded.

**Model present, no skinned rig found in the checked exports:** cobra, dragonfly, hornet, hummingbird, mantis, pistol shrimp, scorpion, shoebill, spider.

Preston is already handling **shoebill, spider and mantis**. After those, the remaining six to check/rig are **cobra, dragonfly, hornet, hummingbird, pistol shrimp and scorpion**.

**Scorpion caution:** `Mecha Beast GLB Meshy Rigged/Meshy_AI_scorpion_front_Huny_1111013939_texture.glb` is present but has no glTF skin/joints. Being in the rigged folder is not evidence it is the rigged export. Retrieve/check the Smart Rig output before paying to rig it again.

**Minions:** melee, ranged and siege3D models are present. Melee has a rig; no rig was found for ranged or siege.

Other newly named rigged creature/objective exports exist, including Coinclaw, Cyber Tortoise and Cyber Wyvern Sentinel. They are not counted as missing variants of the original animal roster. Unselected concept alternatives are not automatically assigned missing-model tasks.

Complete per-file paths, actual skin/joint presence and delivery hashes: `D:/dev/_scratch/lineup-model-rig-audit-2026-11-10.json`. Rig presence alone does not certify deform quality, appropriate anatomy, animation or game readiness. Local filesystem/export evidence only; no browser library import, paid rigging or generation ran.
