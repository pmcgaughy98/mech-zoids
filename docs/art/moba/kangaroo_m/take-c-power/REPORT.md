# Kangaroo: kinetic-force visual review

One built-in image call after Preston's "next", following the approved recreation sequence. Prompt: `prompt-model-views.txt`. Craft-only input: `ape_l/take-a/refs/craft_drembit.png`. No old kangaroo art supplied; no retries or MeshForge jobs. Built-in image token usage and cost are unavailable.

Original: `C:/Users/pmcga/.codex/generated_images/01a1b3d2-bd2d-78f1-922f-9db2d803864e/exec-06233ad6-8b69-4d92-a551-5b098617474e.png`.

Unchanged raw: `sheet_raw.png`, SHA256 `459ce60ea5a3049e2f65448c866405f4701a96c98a4f291504e4b7638c723e46`.

## Visual findings

- Upright orange mechanical kangaroo, two long ears, narrow steel muzzle, huge thighs, broad hind feet, two closed fists. Neutral low guard reads as a kinetic brawler.
- Large cyan induction rings integrated into both gauntlets, paired cyan thigh windows, split chest charge bars, spinal junction and a cyan channel along the tail. Its power equipment is readable while idle.
- Side views repeat the main equipment and show a long tapered conducting tail with a ground brace. Rear shows no face or lens eyes. The far limbs overlap in profiles; a model must still preserve both arms and legs.
- Tail stays uncurled but has slight bends between segments; not a perfectly straight axis. Head/body looks slightly more humanoid than the previous crouched kangaroo, an intentional upright guard proposal rather than a locked design decision.
- Source height: front 495, left 495, back 521, right 497 px; spread about 5%. Side widths both 547 px. Rear's tail contact pad projects 26 px below the heels, so part of the height difference comes from the tail. Shared lowest-contact placement is not proof all feet lie on the same physical plane. Check in the actual model.
- Margins are narrow around the raw upper-row ears, but no measured body component touches the source image border. White outputs add generous margins.
- Source contains semi-transparent edge haze; white preparation discards alpha below 128 and keeps the four main components. Body remains otherwise unchanged. This is a detailed model reference, not a validated sixteen-colour final sprite.

## Delivered

Four 1024x1024 white modeling inputs in `white_views/`: `kangaroo_front.png`, `kangaroo_left.png`, `kangaroo_back.png`, `kangaroo_right.png`. One common nearest-neighbour scale, lowest body contact on row 935 (936 exclusive). Crop/placement metadata: `prep.json`. Review: `review.png`. Bundle: `kangaroo_four_white_views.zip`.

No existing takes, kit code, installed art or shared files changed. Next approved body: pangolin, magnetism and repulsion.
