---
name: factory-pass
description: Part-by-part refine of one machine against a reference (Codex's returned sheets, Legacy sprites for structure). Use when Preston says "factory pass", "go <machine> next", or sends reference images for a machine.
---

# Factory pass, one machine at a time (Claude, 2026-10-20)

Preston's words: "factory refine pass part by part 1 creature at time", "use the synthesis". Creatures come from the
3D factory (`tools/blender/build_<id>.py`); Codex makes reference sheets and hand-finishes; Grok makes world and UI art
only, never creatures. Names, lore and stats are Preston's. Never copy studied material (Legacy sprites are structure
only).

## Steps
1. **Measure, do not eyeball.** Grid sheet at equal height (10% lines) of our installed side view and battle idle beside
   the reference; width to height; colour shares per family. Then three region crops (rear, middle, front). An eye
   estimate was wrong once (the wolf's "torso a quarter longer" was 4%).
2. **Find which part owns a problem area** with the piece map: `renders_detail/<view>_piece.png` codes piece index k as
   `(round(R/17) << 8) | (round(G/17) << 4) | round(B/17)`; `parts.json` gives bone, material and vertex count per k.
3. **Pick the 2 to 4 biggest part gaps.** Each change goes behind a new switch (`WOLF_V95`, `HIPPO_P48`, ...) so the
   previous build rebuilds exactly. Builders are CRLF (the hippo's is LF): edit with Python on bytes; copy the builder
   to the scratchpad first.
4. **Build, render the eight detail views, check every view's box against the frame edge**, pixelize E and SE, and
   look at before against after before rendering any battle frames.
5. **Battle frames, install, verify:** `anim_render_only.sh` (the gorilla: the per-frame loop over
   `tools/art/ape_l_anim_jobs.txt`), `detail_install.sh <id> <build>` (copy the previous build's `map.json` into the new
   build folder), the bind audit, then Godot `--import` and the eight checks. One Godot at a time
   (`tasklist | grep -qi "Godot_v4"`).
6. **Before/after sheet** (side, three-quarter, battle idle, plus the attack the change touches) and a factory log entry
   in `docs/plan/creature-factory-2026-10-12.md`.

## Frame sizes (SPRITE_ORTHO; the resolution grows with it, so the sprite scale never changes)
| Machine | Views | Battle frames |
|-|-|-|
| ape_l | 5.6 (stance `base=22;R_leg=22;L_leg=34;L_arm=21`) | 6.82 |
| wolf_m | 6.2 | 6.2 |
| kangaroo_m | 5.6 | 5.6 |
| shoebill_m | 5.6 | 5.6 |
| hippo_m | 6.0 | 6.0 |
| pangolin_m | 7.6 | 7.6 |

## Lessons (each cost at least one round)
- **Lengthening a body pushes views out of frame.** Check all eight boxes after any stretch: the gorilla's SW and NE
  were clipped at 4.9 for a whole build.
- **Lengthening the rear raises clips that pivot about the middle.** The gorilla's haymaker lean lifted 9 cm with the
  hind feet 30 cm further back; scale the lean by the lever.
- **A turned side camera hides length.** Re-measure width to height after a stretch (the hippo's 0.9 to 1.04 gave 1.53,
  it needed 1.2 for 1.65).
- **The camera turn draws the deep end of a machine high:** feet off the ground line and floating tails (the pangolin
  at 35 degrees; 20 like the rest fixed it).
- **A longer tail changes other views and clips:** from behind its tip draws below the feet (view_art_check's 1.35x
  height rule; the pangolin's non-side camera 14 to 12 degrees), and in a curl, less curl stands it up while a tighter
  curl wraps it over.
- **Hit-test surface parts against the outermost plate, not the core.** The shoebill's chest slots were buried under
  its chest plate for eight builds.
- **White specks are usually the pixelizer's glints** (`PIXEL_GLINT_CAP` in `tools/art/legacy_look.json`), not
  geometry: count single light pixels before and after a change.
- **A big flat face toward the camera lights pale.** Legacy keeps limbs a step darker than the body with highlights on
  top edges (Iron Kong, `docs/art/reference/legacy/iron_kong.png`): use the machine's darker family colour.
- **Scenes can paint opaque placeholders over new art** (the canyon's floor band): check the scene script when a slot
  gets art.
- **A part name that repeats another gets ".001" from Blender, and the bone rule cannot read it**, so the part rides
  the body and comes loose in motion (the gorilla's ankle wheel). The bind audit treats the body as the catch-all and
  never flags it: grep a builder for names it creates twice before adding parts near joints.
- **Renaming a part can change the detail pass everywhere:** it skips names containing words like "seam", "ring",
  "barrel", and assigns panels and vents by each host's place in a sorted list. Compare triangle counts before and
  after a rename.
- **After a source fix on a Codex-finished machine, install with `tools/art/patch_frames.py`**, which replaces only
  the frames that changed.
- Never `rm -rf` a variable path; renders overwrite their files anyway.

## Synthesis: what each source contributes
- Codex's returned sheets and sprites: the design target per machine (proportions, parts, colour shares).
- Legacy sprites (`docs/art/reference/legacy/`): structure and value rules only.
- Grok: none for creatures; world and UI art (see `docs/team/GROK_TASKS_2026-10-20.md`).
- The piece map, bind audit and eight Godot checks: which part to change, and proof nothing broke.
