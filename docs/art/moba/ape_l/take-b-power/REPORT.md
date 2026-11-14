# Gorilla shield-tech recreation: first review

One built-in image after Preston requested gorilla next and expanded body recreations to the whole roster. Prompt: `prompt-model-views.txt`. Only image supplied: the Drembit craft reference, not old gorilla art. No retry, no MeshForge generation or game installation. Built-in token usage/cost not exposed.

Original: `C:/Users/pmcga/.codex/generated_images/01a1b3d2-bd2d-78f1-922f-9db2d803864e/exec-083bba7b-c10e-4d1f-86ea-a0772d0eee8d.png`.

Unchanged raw: `sheet_raw.png`, RGBA 1278x1230, SHA256 `03022032076509649bcee8dbc06682e578bdf8feeccfef11dfad2bdccaf359b2`.

## Visual findings

- Emerald mechanical gorilla with enormous shoulders and forearms, small low head, steel jaw, compact hind legs, planted steel knuckle pads and no tail.
- Two forearm hex projector housings, lime multi-cell lenses, copper-orange bevels, sternum core, broad shoulder conduits and a large dorsal hex reactor. The back now communicates the shield system as clearly as the front.
- Shields are mounted to forearms, no held shield or weapon. No active dome or floating effect included. Rear has no face or eyes.
- Profile far limbs are heavily occluded; verify all four distinct limbs and both projectors in the eventual model. Feet project above the nearer knuckle contacts in the slightly elevated source camera, so the shared lowest-contact row is not proof all ground contacts have the same screen row.
- Heights front 474, left 474, back 472, right 483 source px: about 2.3% spread. Profile widths 513 and 516. No body pixel with alpha>=128 touches the raw sheet border. Two profiles repeat equipment and silhouette closely by eye; the chest core is partly occluded in profile, as expected.
- Intermediate colours and edge haze remain in the raw. Modeling reference only, not a verified sixteen-colour final game sprite. White extraction excludes low-opacity external haze without redrawing the body.

## Files

Four separate RGB 1024x1024 white sheets in `white_views/`: `gorilla_front.png`, `gorilla_left.png`, `gorilla_back.png`, `gorilla_right.png`. Same nearest-neighbour scale, lowest contact at row 935 (936 exclusive). Metadata: `prep.json`. Review: `review.png`. ZIP: `gorilla_four_white_views.zip`.

The original take, kit and game assets are unchanged. This new body is for Preston's visual review. Pangolin is next in the remaining proposed order unless he redirects it.
