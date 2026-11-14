# Melee, ranged and siege minion references

Preston requested the workflow from **Connect Claude to Codex plugin**, then selected a distinct melee/ranged/siege set. Read the relevant creature-generation turns and the local four-white-sheet packaging scripts, including the Eel framing correction. Existing placeholder minion and runtime assets remain unchanged.

## Concepts for review

- Melee: four-legged armored rammer, integrated impact bumper, cyan slit optic.
- Ranged: hovering twin-blaster drone, circular optic, armored lift pods. One targeted edit corrected the original profiles' vertically stacked guns: the horizontal barrel pair now overlaps into one visible profile barrel.
- Siege: two continuous tracks, three visible road wheels per side, fixed forward cannon, closed rear breech.

These designs and proportions are proposals, not approved kits or finalized game size. They share blue team armor, charcoal mechanics, pale steel trim and cyan optics. No red-team set was generated.

## Files and checks

Each role folder contains preserved `sheet_raw.png`, verbatim `prompt.txt`, reproducible `prep_white_views.py`, four RGB 1024-square PNGs in `white_views/`, individual role ZIP and four tightly framed rectangular RGB PNGs in `tight_white_views/`. Combined archive includes both framing choices, prompts, review and preparation metadata. Raw hashes and bounds are recorded. The ranged pre-correction image is retained separately.

Four primary connected silhouettes extracted per raw image using alpha>=128; low-opacity exterior haze excluded. One shared nearest-neighbor scale per machine, no independent view resizing or anatomy repainting. Tight copies remove white margins from the square exports with a four-pixel border. Review board thumbnails are individually fitted for inspection and do not establish relative game size.

All twelve views passed RGB, dimensions and white border checks. Source height spread: melee 2.21%, ranged 0.52%, siege 1.58%. Tight sheets' local nonwhite coverage is 66.59-81.49%. This is a local framing diagnostic, not remote Hunyuan acceptance.

Visual review of final board: complete silhouettes, correct front/left/back/right assignment, distinct role silhouettes, no front optic on rear views, no rear muzzle. Remaining reconstruction risks: some top surfaces remain visible despite level-camera instruction; ranged profiles show a far lift pod offset behind the near pod, so pod placement needs geometry reconciliation; the melee four-leg socket spacing and siege barrel/casemate depth need mesh review. These are generated modeling concepts, not mathematically exact orthographic projections. No successful reconstruction is claimed.

Built-in image generation: three initial calls and one ranged correction. Exact cost/token metering unavailable. Craft-only reference was existing `minion_s/take-a/refs/craft_drembit.png`; melee sheet also supplied as family styling reference for ranged and siege. No external paid service, MeshForge generation, credentials, model import, gameplay integration, other chat messaging or commits.

Next: Preston reviews silhouettes and chooses any changes before a separately authorized model test.
