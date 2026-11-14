# Gorilla reactor spell art — v1

Created with the built-in image-generation tool on 2026-11-10. Original generated RGBA atlas is preserved as `reactor-atlas-v1.png` (1774 × 887). The exact prompt is in `reactor-atlas-v1-prompt.txt`. Palette/shape reference was Preston's approved green/orange Gorilla image; it is not an edit to the model or its texture.

Technique reference: Preston's [Instagram / Tripo clip](https://www.instagram.com/p/DbX99e5g6YK/), located in Mech Hub and inspected as sampled video frames. The clip shows image-derived spell circles and surface detail assembled in Blender, alongside a Tripo character workflow, then animated in a finished scene. This implementation adapts the layered-image technique; no imagery from that video is included in the game and no Tripo generation was run.

One 4 × 2 component atlas, read directly through shader UV regions; no separately generated frame sheets or destructive bitmap processing:

| Index | Cell | Component | Use |
|---|---|---|---|
| 0 | 0,0 | Protective reactor seal | Ally-hover floor seal, ground release bloom, upright release sigil |
| 1 | 1,0 | Fractured knuckle stamp | Grab hover and confirmed ground-slam/heavy impact |
| 2 | 2,0 | Vented drive crest | Directional Drive preview |
| 3 | 3,0 | Ten-part containment seal | Ultimate preview and three beat pulses |
| 4 | 0,1 | Shield recipient crest | Floating selected-recipient art |
| 5 | 1,1 | Painted impact bloom | Confirmed shield/slam/Drive accents |
| 6 | 2,1 | Split energy wake | Actual Drive travel |
| 7 | 3,1 | Containment lock | Upright perimeter accents on the third ult beat |

`gorilla_painted_fx.gd` layers planes, rotation, scale and fades around the existing kit events. The shader softens cell borders and suppresses low-alpha generated haze without rewriting the image. The generated artwork has imperfect gutters, so edge fade is necessary. Preview and cast opacities differ; the existing exact gameplay boundary outlines remain authoritative. The upright shield seal follows the selected machine during its short release effect. Perimeter locks are decorative and do not change collision.

The first native art review is `D:/dev/_scratch/gorilla/ability-indicators-2026-11-10/painted-art.mp4`. `art_review.gd` exercises real ally/self shielding, Grab Slam, Drive and all three ultimate beats. Six art-event/lifetime checks, 25 targeting checks and seven real-match checks pass after integration. The native review reports two leaked objects/one resource at process exit, with no script/shader errors during play. One match run also reported exit resource warnings; a subsequent verbose audit did not reproduce them. This is not a clean shutdown certification. A headless editor import also reports sandbox-blocked writes to the user's global Godot help/settings caches; the workspace atlas imported successfully.

This is a creative first pass, not final VFX approval. Review brightness, perceived scale, duplicate cyan ground-ring clutter, brief existing shield-bubble flash and visibility under multiple simultaneous casts. Current model geometry, materials, animation clips, damage, cooldown and movement values are unchanged.
