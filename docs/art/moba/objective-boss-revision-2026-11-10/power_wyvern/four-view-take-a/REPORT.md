# Corrected wyvern: four white modeling sheets

Preston requested four angles after the wing-arm correction. One built-in Imagegen call used `../wing-fix/concept_raw.png` as its sole identity reference. Raw output preserved unchanged as `sheet_raw.png`; full prompt in `prompt.txt`. Original output: `C:/Users/pmcga/.codex/generated_images/01a1b70c-b3dc-7a80-8f6e-e94f7d92dd53/exec-3c0a90c5-d967-44f6-8040-8ed8a7587296.png`. Exact usage/cost unavailable.

Four individual white RGB 1024-square PNGs in `white_views/`: `wyvern_front.png`, `wyvern_left.png`, `wyvern_back.png`, `wyvern_right.png`. `tight_white_views/` provides rectangular copies with four-pixel borders. `wyvern_four_white_sheets.zip` includes both framing choices, prep metadata, prompt, report and review.

Reused prior packaging method: four largest alpha>=128 connected silhouettes, low-opacity exterior haze excluded, one shared nearest-neighbor scale, same baseline, no anatomy repainting or individual view stretching. `prep_white_views.py` and `package_uploads.py` reproduce extraction and packaging. Raw hash and source bounds recorded in prep metadata.

Visual QA of white review: four complete silhouettes, correct view assignment, wing panels attach along forearms, two hind legs and two wing forelimbs, rear has no face or chest reactor. Raw height spread 1.74%. Square RGB/dimension checks, tight white-border checks and ZIP integrity passed.

Limitations: generated references are not exact engineering projections. Profile feet are staggered in depth; wing folding, chest reactor visibility and shoulder depth differ somewhat across projections. Front neck obscures most chest reactor. Back tail is shown lower than profile's raised tip, so tail pose must be reconciled when modeling. No 3D reconstruction or remote acceptance tested. Tight local nonwhite coverage: front 52.3%, back 54.0%, left 37.0%, right 36.7%; bounding rectangles are tight but open space around wings, neck and tail remains. A provider requiring over-half subject area may still reject profile uploads. Do not stretch or fill the anatomy to inflate that metric.

Earlier concepts preserved. No model generation, saved credentials, external billed generator, gameplay changes, peer messages or commits.
