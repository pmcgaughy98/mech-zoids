# Gorilla against Mechabeast V2 (Claude, 2026-10-14)
Preston: "gorilla V2 is a great reference. The yellow pillars on its back unfortunately aren't aligned correctly though so
account for that." Reference installed as `docs/art/reference/starters/ape_l.png` (source `ape_l_mechabeast2_source.png`,
from Downloads "Gorilla-Mechabeast V2", alpha cut 200); the previous one kept as `ape_l_mechabeast1.png`. Our back
pillars stay as they are.
- Its angle: our front view turned 20 degrees toward front-right (new `SPRITE_TURN` in render_sprite_views.py): outline
  0.797 (straight front 0.791, front-right 0.676).
- Values: the reference measures mean 85, near-black 0.19, lit 0.09 (tools/art/legacy_gap.py); ours mean 86, 0.20, 0.04.
  Highlights were the gap: the gorilla's highlight ranks 0.93/0.975 to 0.84/0.94 (lit 0.09), in ape_round.sh and
  ape_anim_round.sh. New pixelizer env knobs PIXEL_SEAM_SHADE, PIXEL_SIDE_DROP, PIXEL_UNDER_DROP (defaults unchanged).
- v69: as his, the shoulder hub rings black, the knuckle caps black rollers (0.075 radius), a black hub on each fist's
  outer side. v70: elbows bowed out (x 1.1 to 1.3), his arms arch shoulder to fist: matched view 0.798; against the first
  Mechabeast reference S 0.618 to 0.631, SE 0.784 both. v70 installed with its battle animation re-rendered; view_art_check
  and battle_check PASS. Sheet `docs/art/2d/sheets/ape_l_v70.png`.
- Still different: his arms read as separate chunky green plates down to the fist; ours are hidden from the front by the
  forearm armour and the fists.

## Mechabeast V3 (2026-10-15, Preston: "best reference yet")
- Installed as `docs/art/reference/starters/ape_l.png` (source `ape_l_mechabeast3_source.png`, from the chat image; alpha cut 200, two pieces kept); V2 kept as `ape_l_mechabeast2.png`.
- It is a pixel-art front-right view: v71's SE view scores 0.784; turned 10 degrees further (SPRITE_TURN 10) 0.808; 20 degrees 0.690; higher cameras worse (26 degrees: 0.703 to 0.742).
- Seen side by side: his greens are brighter and his orange more saturated (ours olive and tan), his plates read as crisp faces with lit top edges and dark seams, and his arms as separate segments. The Codex task file now names V3 as the gorilla's finish target.
