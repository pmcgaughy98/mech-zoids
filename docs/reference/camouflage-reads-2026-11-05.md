# Camouflage reads: how shipped games show a hidden unit (2026-11-05)

For the chameleon's camouflage (kit slot 2) and shared camouflage (slot 4). Board and GIF:
`docs/art/moba/chameleon_m/camo/`. Script: `D:\dev\_scratch\chameleon\camo_board.py` (scratch, not in the project).

## What was read

| Source | Status | What it gave |
|---|---|---|
| League of Legends wiki, "Stealth" (redirect from Invisibility) | **Read** (Firecrawl, 2026-11-05) | Camouflage is the long-lasting kind and fails when an enemy champion comes inside a detection radius (400 to 800 units, against about 1,350 sight, so 30 to 60% of sight). Allies and the user see it normally plus the radius. Breaks on the start of an attack windup or any cast. A damaging hit makes the silhouette shimmer for 0.6 s with a sound. Turrets and control wards see through it. |
| Liquipedia Dota 2, "Invisibility" | **Read** (Firecrawl, 2026-11-05) | Allies see the unit transparent but visible. Enemies see nothing, and its minimap icon goes too. **Invisible units cast no shadow.** A fade delay comes first, then a fade time: 0.2 to 0.6 s for skills (Windranger 0.2, Shadow Blade 0.3, Clinkz 0.6), up to 2 s for a rune. Breaks at the attack point or cast point. |
| StarCraft (1998), cloaked units | **General knowledge** (the Liquipedia page returned 404) | In a 2D sprite game, the cloaked unit is drawn as a moving distortion of the ground behind it. The enemy can notice the shimmer but cannot target it without detection. |

## Structure taken (not their art or code)
1. **Two audiences, two drawings.** The enemy sees nothing; the ally sees it clearly but marked as hidden. Every look on
   the board has an "ally sees" version.
2. **Hidden means gone.** No shadow either (Dota). Ours has a contact shadow under every machine, so it must fade with
   the body, or the shadow gives it away.
3. **A short fade, then fully hidden.** Skills sit at 0.2 to 0.6 s. The board uses 0.6 s, matching the kit's
   "fades out over a moment".
4. **A tell only up close.** LoL's detection radius is 30 to 60% of sight. On our 12 m sight that would be 4 to 7 m.
5. **Breaks on the attack windup, not the hit**, in both games.

## Synthesis proposal (nothing here is canon)

Three looks, measured on the approved take-b e view on lane grass and se view on dirt. "Seen" means the share of body
pixels that differ visibly from the bare ground. The proposed targets: 0 to 3% hidden, 8 to 30% for the tell, 45% or
more for the ally view with the eyes kept.

| Look | Hidden | Close-up tell | Ally sees | Eyes kept (ally) | Character |
|---|---|---|---|---|---|
| A. Dither dissolve | 0% / 0% | 12% / 13% | 51% / 51% | 100% | Pixels drop out in a checker order. A classic handheld ghost, the most "pixel game" of the three. Tell is a sparse twinkle. |
| B. Colour match | 0% / 0% | 31% / 32% | 98% / 91% | 100% | The plates take on the ground's colours, washing up from the feet behind a thin pale line. Ally sees a ground-coloured chameleon with a travelling turquoise rim. The most chameleon of the three, and it ties into the colour flash. Tell sits at the top of the range. |
| C. Heat haze | 0% / 0% | 24% / 25% | 88% / 78% | 100% | The body fades in three steps; up close the ground behind it ripples a pixel side to side. The StarCraft read. |

(Figures are e on grass / se on dirt.)

**Picked by Preston, 2026-11-05: "B, colour match".** The rest of this section is the reasoning it was picked on.

**Recommendation:** B for the chameleon. It is the animal's own trick, it stays in the machine's palette (the pale
turquoise rim and gold eyes), and allies get the clearest read. A is the fallback if B costs too much in the shader.
C works best as the tell for any look, not as a look of its own.

**Alternatives not drawn:** a full-body flicker (old handheld invisibility, which strains the eyes over long hides);
a hard outline-only ally view (reads well, but looks like a selection marker rather than camouflage).

## Spec, agreed with the game feel lane (2026-11-05)
- **One material.** The camouflage shader is a superset of `tilted_sprite_3d.gdshader`, because the per-sprite
  material_override is the only slot. It keeps their vertex(), `tex`, `lift` and `render_mode unshaded, cull_disabled`,
  plus one line that sets `camo_up`. At hand-off the feel lane moves the tilt code into an include both shaders use,
  and swaps the chameleon's material over.
- **A cutout, never blended.** No screen reads and no alpha. The enemy-side fade and the tell are an ordered 4x4
  dither (discard), so depth and sorting against towers and walls stay the tilt shader's.
- **The script computes, the shader only reads:**
  - `camo_hide` 0 to 1: the wash, tweened over about 0.6 s.
  - `camo_ally_view` on or off.
  - `camo_tell` 0 to 1: the feel lane works it out from the nearest enemy's distance against Preston's ~4 m.
  - `camo_shimmer` 0 to 1, or TIME when below 0.
  - `camo_rim_flash` 0 to 1.
  - `camo_floor_a/b/c`: up to three floor colours sampled under the machine, commonest first.
  - `camo_rim`, `camo_flash`: the rim and flash colours.
- **Not the fog `seen` flag.** It sets visible = false, which kills both the tell and the ally view. The feel lane
  adds a separate camouflage state on the player, and the bots' targeting skips it.
- **The health bar and minimap marks** belong to the map lane (`match_hud.gd`) and read that camouflage state.
- **Breaking on a windup** is the feel lane's to wire (the basic attack, the kits' used signal, busy going true).
- **Shadow, agreed with the camera lane (2026-11-05):** `ContactShadow3D` gets `fade` (0 to 1, default 1), which
  multiplies its alpha and hides the node at 0. The kit sets it on the machine's "Shadow" node (the same node the
  fennec's dig uses): 0 on an enemy's screen, 1 for allies, eased alongside `hide`. "Per viewer" means the local
  player's team. The camera lane builds it when the kit is ready to call it; message them then.
- Tell: the enemy's own machine within about 4 m (a third of the 12 m sight; Preston's number to set).
- Break: on the start of an attack or skill windup, with a 2-frame bright rim flash (the GIF shows it).
- Shared camouflage (slot 4) uses the same shader on the allies it covers.

## Built and checked (2026-11-05)
- **Shader:** `scripts/moba3d/tilted_sprite_camo_3d.gdshader`. It isn't wired to any machine yet; the game feel lane
  swaps the chameleon's material over when its kit exists.
- **Check:** `tools/debug/chameleon_camo_check.gd`. It renders the take-b e view through the shader over lane grass at
  a 35-degree orthographic camera, and measures each state against the bare ground. It needs a window (the headless
  renderer draws nothing), and it fails if the view is empty or the eyes are missing, so it can't pass on nothing.
  `godot --path . --script res://tools/debug/chameleon_camo_check.gd -- <out_dir>`
- **Result, run in a scratch copy of the project** (`D:\dev\_scratch\chameleon\camo_godot`, compatibility renderer,
  GTX 1660 SUPER): body 35,101 screen px, eyes 361 px. Normal 100%, halfway 56%, hidden 0%, tell 18%, ally 94%,
  eyes kept 100%. **PASS.** Board: `docs/art/moba/chameleon_m/camo/camo_godot_check_e_grass.png`.
- **Not checked yet:** a run inside the main project, the 35-degree frames (none exist; the old e view is tilted by
  the shader), the real chase camera and the game's floor texel scale. The ally view's three scattered floor colours
  show as a fine grid; if it looks busy in game, drop to two colours.
