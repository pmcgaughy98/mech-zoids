# Hippo recreation: first visual review

Exactly one built-in image generation after Preston approved starting the redesigns one by one. Prompt: `prompt-model-views.txt`. Only image input: `ape_l/take-a/refs/craft_drembit.png`, craft reference only. No earlier hippo image supplied, no retries, no MeshForge run. Actual token usage/cost is not exposed.

Original output: `C:/Users/pmcga/.codex/generated_images/01a1b3d2-bd2d-78f1-922f-9db2d803864e/exec-43d2177a-20d1-4954-a667-9cd5aaf3e79a.png`.

Unchanged project copy: `sheet_raw.png`, RGBA, 1536x1024. SHA256 `777fb79ca47e91e6b17151326612aeaa5dd5d2da7f96ee99a5f8751c577a1424`.

## What the image shows

- Huge blunt hippo muzzle and barrel torso, short planted mechanical legs, steel foot segments and joint discs, violet armour, small aqua lenses. The hippo identity is clear.
- A large luminous liquid chamber below the jaw, matching oval flank reservoirs, bright channels and a compact dorsal manifold. Paired round jaw vents have lavender rims. The hardware conveys the approved power theme while standing.
- Matching basic equipment in front, left, back and right; rear has no eyes or face. No weapons, divine clothing, goblets or other decorative god imagery.
- Body height estimates: front 413, left 410, back 415, right 417 source pixels. Height spread about 1.7%. Profile widths 735 and 746 (about 1.5% apart). These measurements do not establish exact 3D consistency.
- Four feet are visible in each profile; far feet sit slightly higher on the page. The rear overlaps far legs. Check separation and actual foot contact on any generated model.
- The source includes low-opacity external glow despite requesting no aura. The four white inputs exclude alpha below 128 and preserve the body colour and remaining alpha. They are component crops with one common nearest-neighbour scale, not regenerated images. The unmodified raw retains the complete original.
- Small highlights, intermediate colours and outer ink remain: this is a modeling concept, not a validated sixteen-colour finished game sprite. The tail has a slight downward bend rather than a perfectly straight axis.

## Delivered

`white_views/hippo_front.png`, `hippo_left.png`, `hippo_back.png`, `hippo_right.png`: each RGB 1024x1024, pure white margin, common scale and near-feet baseline 936 exclusive. ZIP: `white_views/hippo_four_white_views.zip`. Review: `white_views/review.png`. Reproducible crop/placement metadata in `white_views/prep.json`.

The existing hippo and game files are unchanged. This body awaits Preston's visual pick. Kangaroo with kinetic-force equipment is the next approved recreation in order. Kit redesign, model generation and game integration have not been performed.
