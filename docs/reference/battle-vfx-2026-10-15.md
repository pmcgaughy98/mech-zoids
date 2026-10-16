# Battle framing and weapon effects: what shipped games do (2026-10-15)

Preston (2026-10-15): "Skill up with the synthesis, use zoid games repositories and source code. Fix up the battle
scenes. The perspective is too close, and I want to start adding VFX's and effects to weapons/animations etc.
everything that needs it." Structure only: no code, data, text, names or art from any source went into the game.

## What was read

Three study agents (2026-10-15), primary source unless marked. Paths are relative to each repo.

**Zoids Legacy decomp** (`D:\Program Files (x86)\Game assets\zoids-source\ZoidsLegacyDecomp`, MIT, read):
- **Two screens.** Battle has a field overview and a separate side-view attack scene. In the overview, small sprites
  stand on a perspective floor and scale with depth, and the camera eases a quarter of the remaining distance each
  frame, settling in 17 to 24 frames. The attack scene is a two-shot cut: the attacker, a wipe, then the target. The
  attack clip plays full screen with the text windows closed. Sources: `src/game/modes/run_battle_scene.c`,
  `src/battle/start_battle_camera_transition.c`, `update_battle_camera_transition.c`, `run_battle_camera_task.c`.
- **Effects are a shared library plus a record per weapon.** About 137 effect routines exist: beams, smoke-trail
  projectiles, missile volleys, explosion columns, white flashes, palette-cycled beams, inward charge particles,
  slash-spark-fragment bursts, ring waves and orbs. Each weapon's record points to an attack script and an impact
  script. A script is a list of timed spawn commands. Sources: `src/battle/battle_animation.h`,
  `update_battle_animation_script.c`, `start_battle_equipment_animation.c`, `create_battle_animation_group.c`.
- **The machine's own pose releases the effects (the fire frame).** Melee effects spawn sparks, fragments, shake and
  sound together on the strike frame. Sources: `start_zoid_equipment_animation.c`,
  `update_battle_slash_spark_and_fragment_effect.c`.
- **Timing numbers:**
  - Projectiles fly about 16 px a frame and start 256 px from the impact.
  - Beams grow 32 px a frame across 8 segments.
  - Charge particles spawn on a 48 to 68 px arc and all arrive at the same moment.
  - Explosion columns climb in waves 4 frames apart.
  - The impact shake lasts 17 frames and moves only the target's layer.
  - Damage digits start 2 frames apart, hop 8 px and live 45 frames.
  - Every animation ends with a 30-frame tail.
  - White flashes fill the palette white and fade back over about 31 frames.
  - Glow sprites blend about half onto what is behind them.

  Sources: `update_battle_segmented_beam_effect.c`, `spawn_battle_inward_charge_particle.c`,
  `update_battle_rising_missile_five_explosion_column_effect.c`, `update_battle_animation_camera.c`,
  `popups/update_battle_popup_glyph.c`, `start_battle_animation.c`. The shake sizes and the per-weapon command lists
  are ROM data and are not in the source.
- **Legacy battle sprites** (`docs/reference/sprite-rules-legacy-2026-10-12.md`, measured earlier): about 84 px tall on
  a 160 px screen. That is the same share of the screen our machines took before this change, so "too close" asks
  for wider than Legacy.

**The `Zoids` Zig project** (same folder, read): a flocking demo; "Zoids" is a pun on boids. It has no battle
structure.

**Pokemon Emerald** (`pret/pokeemerald`, read online):
- Each of 354 moves is a data script over about 40 opcodes. The art pool is shared: 289 particle sheets and about two
  dozen backgrounds. Sources: `src/battle_anim.c`, `data/battle_anim_scripts.s`.
- Hits combine a hit splat, a shake of 1 to 4 px for 12 to 18 frames, and the target's palette blended toward white.
- Beams darken the background first (`Move_THUNDERBOLT`, `Move_HYPER_BEAM`).
- The HP bar drains after the blow (`BattleScript_HitFromAtkAnimation`).
- The battle layout uses the same diagonal as ours (`src/battle_anim_mons.c` `sBattlerCoords`).

**Fire Emblem 8** (`FireEmblemUniverse/fireemblem8u`, read online):
- Body animations are data frame lists with embedded commands, and the hit command is the single sync point.
- A hit gets a white flash of 4 to 8 frames and a quake from a per-frame offset table.
- Effects sit in front of or behind the units (`src/banim-main.c`, `banim-efxbattle.c`, `banim-ekrutils.c`).

**General knowledge only:** Golden Sun and Mega Man Battle Network were not read.

## What all three agree on

- Effects are a small library of reusable pieces combined per weapon by data, not drawn once per move.
- Effects start on the body's strike or fire frame.
- An impact is short stacked beats: a burst, a brief flash on the target, a small shake of the target, then the number.
- Screen-wide effects (darken, flash, big shake) are kept for big moves.

## What we built (2026-10-15)

- **Framing.** The battle field is a zoomed-out layer (`scripts/battle/stage.gd`). It draws at about 0.7 of full size,
  rounded so every art pixel covers whole screen pixels:
  - 0.75 at the default 1280x720 window, three screen pixels per art pixel instead of four.
  - 0.667 at 1920x1080, four screen pixels per art pixel instead of six.

  Machines now take 37 to 43% of the screen's height, against Legacy's 52% (Pokemon's front sprites are about 40%).
  The background and panel stay at full size. Alternatives: a fixed 0.75 draws uneven pixels at 1920x1080, and 0.5
  is even everywhere but small. A Legacy-style two-shot cut was not built; it is the option if the wide frame feels
  flat.
- **Effects** (`scripts/battle/vfx.gd`): pieces drawn in code on whole art pixels at 30 steps a second:
  - Shots and blows: sparks, star, burst, rings, slash, streak, projectile (pellet, plate, block, missile, orb), beam
    (palette-cycled rim, optional twin jets), ground wave, sound waves.
  - Fire, smoke and debris: explosion, smoke, dust, debris, spray, flame.
  - Energy and motion: charge-in, sparkle, speed lines, after-image (additive).
  - Beats: the target blinks toward white (after the burst has read), both machines freeze, the target shakes on its
    own and is knocked back. The screen shakes only on heavy blows, beams dim the background, and the biggest moves
    flash the stage.
- **Recipes** (`scripts/battle/vfx_recipes.gd`): one per starter weapon (18), keyed by clip frame, plus fallbacks by
  weapon type for the older drawn machines.
- **Melee crossing.** With the wider field, the two machines stand too far apart for a blow to land in place. As
  Legacy moves the acting unit out, a melee attacker now crosses during its wind-up, and its frontmost point lands
  just inside the target's edge at the strike frame. It is aimed into the target's body, kept on screen, and goes
  back during recovery.
- **The rest of the screen.** Damage digits hop one after another, the HP bar drains, and Charge draws light inward
  with a cyan blink. Repair items rise as green sparkles. A destroyed machine goes out in a string of blasts, a white
  flash, a climbing fireball column and a smoke column.

## Checks

- `tools/debug/vfx_check.gd` plays all 18 weapons from both sides, as a hit and as a miss, at 1280x720, 1920x1080 and
  320x180, and the three older drawn machines' weapons both ways (288 attacks). It checks that:
  - recipes name only real effects and frames;
  - the number shows inside the step;
  - melee blows land inside the target;
  - shots leave from the art;
  - the attacker stays on screen and never steps below the player's row;
  - everything returns home and frees itself.
- `tools/debug/battle_fit_check.gd` runs at every field scale a window can give.
- `tools/debug/vfx_capture.gd` with `tools/art/vfx_sheets.py` records frames, contact sheets and GIFs. The results are in
  `docs/art/2d/battle_vfx/`: a reel (`battle_vfx_reel_2026-10-15.mp4`), one frame per weapon just after its impact
  (`all_impacts_2026-10-15.png`) and a sheet per weapon.

## Not used

- **PixelLab `vfx_workbench`:** inspected. It is free and draws crisp effects, but its exports save to Preston's
  pixellab.ai account. Effects drawn in code stretch to any distance between the two machines.
- **Paid generators:** not used. They would need Preston's yes and a cost estimate.
