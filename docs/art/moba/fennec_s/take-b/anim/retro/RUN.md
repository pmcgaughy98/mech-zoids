# Fennec back views in Retro Diffusion (animation lane, 2026-11-04)

Preston: "Do walks in retro and sand kick there too as too many cutoffs and misproportions. mainly backviews."
Spent $0.78 (balance $1.61 to $0.83): walking $0.14 x 2, custom_action $0.25 x 2 (I had assumed $0.14 for the kick).

- Inputs (`prep_retro.py`): centred in 128, feet on row 110. Walk inputs are the current trot frame 0 after the ink
  carry; kick inputs are the new inked stills. `offsets.json` maps back to the 192 canvas.
- Walk n (job b8541032) and ne (b4146312), `rd_advanced_animation__walking`, 8 frames, prompt expansion off.
  - n: design held, hind feet alternate, tail swings and lifts toward the camera (round tip in f3). Used.
  - ne: head and ears held; the near legs read as spikes in f1-f3. Used, as better than the cut-off Codex row.
- Sand kick n (f2282af9) and ne (33c6a464), `rd_advanced_animation__custom_action`, 6 frames: FAILED. From frame 2 it
  stands the fennec on its hind legs, shows the cream chest and gives it clawed arms. Raw in `raw/`, finished copies in
  `frames_retro_kick_failed/`. Not used.
- Kick instead built by `kick_from_walk.py` from the Retro walk frame 0 and the still: still, standing, head down 3,
  head up 2, head down 1, still. On-model, small motion; the sand is the game feel lane's effect.
- `finish_retro.py` (palette snap, white-background removal for custom_action, despeck, grounding, 192 mapping),
  `gold_specks.py` (gold islands under 6 px below row 140 repainted), `apply_retro.py` (originals in
  `<move>/frames_pre_retro/`).
- Packed: `pack_fennec_3d.py` check OK, Godot load 40 animations, 0 bad.
- Board `fennec-backviews-before-after.png`, gif `fennec-walk-back-ne.gif`.

## Rejected (Preston, 2026-11-04): "Nvm retry with codex"
- The live n/ne walk and sand kick were restored from `<move>/frames_pre_retro/` (0 px differ) and repacked (check OK).
- Redo by Codex: `anim/make_codex_backviews_fennec.py`, output `anim/codex-backviews/`.
