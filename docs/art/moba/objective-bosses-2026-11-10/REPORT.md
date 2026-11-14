# Two neutral objective boss proposals, 2026-11-10

## Direction and authorship

Preston requested two bosses: one grants a gold/economy boost, one a siege/team-fight buff. Animal identities were open. These first concepts propose a giant mechanical stag beetle and colossal mechanical elephant; neither animal choice, palette nor name is approved canon. Folder names are descriptive working identifiers, not proposed proper names.

Read the project's current CLAUDE.md, startup/working guidance, supplied `docs/reference/jungle-objective-synthesis-2026-11-10.md`, Imagegen skill, craft reference and prior minion packaging scripts. No AGENTS.md found in the project listing or checked ancestors. The supplied synthesis distinguishes an economy reward from a temporary power window; these images express that distinction through amber vault-like armor versus a heavy integral reactor. No reference-game monster design was copied. Reward amounts, payout versus income boost, duration, recipients, timing and encounter moves remain unsettled. No gameplay was implemented.

## Proposed creatures

- **Gold/economy: mechanical stag beetle.** Low, broad armored body; amber-gold/copper shell with turquoise energy insets; six walking legs; paired heavy steel mandibles and four frontal amber lenses. Vault-like shell suggests stored value through integral machinery, without currency icons or a treasure chest. Mandible sweep is a possible encounter read, not an authored or implemented attack.
- **Siege/team-fight power: mechanical elephant.** Tall, heavy four-legged body; crimson armor, orange energy channels, two tusks, segmented trunk and a low three-segment spinal reactor. Heavy power-storage silhouette suggests a contested power reward, not a promise of a particular siege mechanic. Trunk, tusks and stance are anatomy proposals, not finalized ability design.

Distinct low insect and tall quadruped silhouettes help identify the two objectives. A horned quadruped for economy or another armored crawler for power was an alternative; the chosen pair gives clearer anatomy contrast. Relative world size is not set by the image canvases or review board.

## Deliverables and source of truth

Each creature folder contains:

- `sheet_raw.png`: unchanged selected generated image.
- `prompt.txt`: complete initial prompt; beetle also records its targeted jaw correction.
- `prep_white_views.py`: adapted existing four-connected-silhouette packaging workflow.
- `white_views/`: four named front/left/back/right RGB 1024-square PNGs, review, ZIP and prep metadata.
- `tight_white_views/`: four tightly cropped white RGB upload copies and diagnostic metadata.
- Individual `boss_<identifier>_four_white_views.zip` containing both framing choices.

Set-level `review_all.png` displays all eight views. Each thumbnail is individually fitted for inspection, so this board is not a shared-scale size chart. `bosses_eight_white_sheets.zip` contains eight square sheets, eight alternate tight copies, prompts, metadata, review and this report. `package_set.py` reproduces the package; `packaging_checks.json` records raw hashes and dimensions.

Original built-in outputs:

- Beetle initial: `C:/Users/pmcga/.codex/generated_images/01a1b70c-b3dc-7a80-8f6e-e94f7d92dd53/exec-b9874259-73ab-41fa-afbb-e275c90da388.png`, retained as `gold_stag_beetle/sheet_before_jaw_fix.png`.
- Beetle selected jaw correction: same directory, `exec-18b4a254-548d-42be-be8b-6c096d90396d.png`.
- Elephant selected: same directory, `exec-05d61783-83b4-4b8a-8cd0-f71866c57257.png`.

## Validation and remaining limits

The four largest alpha>=128 connected silhouettes were extracted. Low-opacity exterior haze was excluded; selected interior alpha was preserved over white. One shared nearest-neighbor scale per creature, no per-view stretching or anatomy repainting. Tight copies crop the square export around its recorded silhouette bounds with a four-pixel white border.

All eight square sheets passed RGB and 1024-square checks; all eight tight copies passed dimensions and white-edge checks. Source height spread: beetle 4.01%, elephant 4.53%. Tight local nonwhite coverage: beetle 61.71-64.48%; elephant 67.40-81.61%. Local framing metrics do not establish remote Hunyuan acceptance.

Visually inspected the final white review board: complete silhouettes, front/left/back/right labels correct, no rear eyes or second trunk, three near beetle leg sockets in profiles, same elephant trunk/tusk arrangement, three spinal energy segments. The beetle edit replaced inconsistent vertically split profile jaws with an overlapping near/far pair and added inner teeth to front jaws.

Remaining reconstruction risks: some top surfaces remain visible despite level-camera instructions. Beetle jaw curvature/depth and hidden-leg socket alignment are still stylized rather than rigorous projection. Elephant ear/torso width versus profile depth, toe and far-leg overlap, and trunk curl need reconciliation in a mesh. These are reviewable concepts, not exact engineering orthographics or verified reconstructed models. Do not substitute them for the exact locked generation sheets of existing catalog models.

## Tools and boundaries

Built-in Imagegen used for two initial generations and one beetle correction, authorized by this request. Exact image usage/cost metering unavailable. Existing `minion_s/take-a/refs/craft_drembit.png` supplied as craft-only reference, not anatomy. Local Python/Pillow/NumPy/SciPy reused the minion extraction and ZIP workflow; source images remain unchanged.

No external billed generator, API/CLI image fallback, MeshForge job, purchase, saved fal.ai credential access, gameplay/balance edits, existing creature edits, peer messages or commits. All writes confined to this new boss asset folder. Blender/runtime checks wait for an actual model; these are image deliverables only.

Next: Preston reviews the animal identities, silhouettes and palettes before model generation or encounter implementation.
