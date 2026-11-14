# Sprite canon: what every new creature sheet carries

Preston, 2026-11-02, after Huskward take E drifted from Drembit's style and read "a bit too detailed": "reevaluate all we've collected and learned ... then lets make it". Every Codex sprite job reads this first and puts its numbers in the brief. References are measured for structure only: no pixels from PokeAPI, PMD, Emerald or any ROM go into the repo, a prompt or a reference image.

## 1. Draw for the size it is seen at

- Handheld monster sprites of the 16-colour era use one palette of 15 visible colours. Our PokeAPI sample measured 14 to 15 a sprite.
- Sky's creatures stand 20 to 26 px on a 24 px tile. Ours are drawn at 128 to 176 px and shrunk 3.3 to 5 times for the dungeon (stage masses 15.5, 21, 30).
- So a part or shading cluster narrower than about 4 drawn px vanishes or turns to speckle at game size. No grain, crease lines or texture strokes, but keep the volume: give each main material 4 tones (highlight, base, shadow, deep shadow) in big masses, small parts 2 or 3. (Changed 2026-11-02: the old "2 or 3 tones" rule made the Rimefin and Cinderhide sheets read flat next to Drembit. Preston: "the creatures are starting to look flatter".)
- Judge the sheet shrunk to game size as well as full size.

## 2. Numbers to hit

Measured 2026-11-02 on s, se, e, ne and n (`view_check.py` for lone pixels).

| | Reference sample | Tallowroot A | Drembit | Huskward E | Target |
|---|---|---|---|---|---|
| Colours across all views | 14 to 15 a sprite | 12 | 19 | 15 | 16 or fewer, shared |
| Share of the top 5 colours | 0.73 mean | 0.70 | 0.40 | 0.50 | 0.65 or more |
| Lone pixels | 0.11 mean | 0.04 | 0.14 | 0.17 | 0.11 or less |
| Front/back outline | | 0.79 | 0.86 | 0.87 | 0.80 or more, raw |
| Back height over front | 0.99 mean | | | | 0.95 to 1.05 |

Drembit is the model for shapes and for eight views agreeing, not for colour: two near-blacks cover 15% of it. Take E spread its colour over six bark browns and dark crease lines (13% on one crease colour), which is what reads as too detailed.

Depth, measured on e, se and s 2026-11-02 (luminance 0 to 255, 5th to 95th percentile): Drembit 1 to 225 with about 5 tones on its main material; Tallowroot A 33 to 197; Cinderhide take B 41 to 192 with one tone on 60% of the body; Cinderhide A 56 to 167. Aim for a range of 180 or more and no single tone on more than about 40% of the body.

## 3. Style

- Tallowroot is the house style reference, never Preostmar. Drembit is the reference for views agreeing and for clear shapes.
- Chunky clean clusters, angular volumes, light from the upper left on every view, a clear shadow side and underside away from it. No painted outline around the silhouette (the shader draws it), but a dark line inside the body wherever one part overlaps another (leg over belly, head over neck, crest base on the back), as Drembit has. The shader (`sel_out.gdshaderinc`) adds a dark texel round the silhouette and has an internal "detail ink" mode, but that mode is off for creatures by default, so the inside lines have to be painted.
- Fantasy colours in the line's family, given as hex values. Later stages go darker in shade.
- Eyes: an almond tucked under the brow, with a dark rim, an iris in a mid colour and a dark pupil. Flat pale blocks read as googly (Preston, 2026-11-02). Huskward take F's eyes are restamped this way in Aseprite.

## 4. Eight views, one image

- One 3x3 sheet with Drembit's layout and its "eight copies" paragraph word for word. Neutral standing pose. The signature shows from all eight views and clears the head.
- Raw front/back at least 0.80, heights within 10%, no face on ne or nw, north points north.
- Back views (`.claude/skills/sprite-back-view`): feet keep the front's claw family seen from behind (outer toes whole, the heel hides the middle toe); armour and bark lines sit at one height on a leg in every view; on the rear diagonals the farther feet stand 5 to 9 px higher; the tail slopes toward the camera; no chest V on the rump.

## 5. Evolution

- `stage_step.py` against the stage before: 0.28 to 0.55, as in real lines. Area grows 1.3 to 2.7 times a stage. Every Huskward take so far missed (A 0.72, B 0.70, C 0.77, E 0.60). Rampartroot take A, measured against Huskward F with F given only as a rendering reference, came in at 0.49: the first take on the line inside the range.
- Keep two or three anchors (face and eye motif, the signature, the colour family). Change the silhouette, head, proportions, posture and palette shade, and turn the signature into something new.
- Later stages read older: smaller head against the body, small deep-set eyes, thick neck, angular planes, and real weight: thick legs and a heavy body, never skinny or lanky (Preston 2026-11-02 on Caller take A, which this line used to push toward long jointed legs: "its too skinny"). Image references outweigh words, so attach Stage I art only for lineage, never as the craft reference, and never attach the old drawing of the creature being remade: Codex copies it ("You went back to remaking the original sprites again").

## 6. Process

- Codex draws, code judges, Aseprite fixes (a layered `.aseprite`, one frame per view), Preston approves. Nothing goes into `assets/` without his yes.
- A fresh `codex.cmd exec` with a written brief costs about 60k to 110k tokens a sheet. Resuming the Claude-jobs chat cost 786,677 tokens for Huskward take F on 2026-11-02, because it carries the chat's whole history: use a fresh exec.
- Image references outweigh words. Take F was given take E as its design picture and came back as take E made squatter, crease lines and oval patches included, against a brief that said otherwise. Give the design in words, or as a picture already at game size. Say the cost first; one image job at a time; two tries at most.
- After the sheet: `slice_grid.py`, `view_check.py`, `sheet_judge.py`, `stage_step.py`, the palette edge audit (fringe), the numbers in section 2, then look at full size and game size.
- Walks stay Retro's. Sky's timing (a 24-frame step, about 3 drawings held 4 to 10 frames, lift set per creature) is a game setting, not sprite art.

## Sources

`docs/art/reference-measurements-2026-10-30.md` (PokeAPI sample), `docs/research/sky-walk-measure-2026-10-30.md`, `docs/research/sky-fight-measure-2026-11-02.md`, `docs/research/emerald-arena-study-2026-10-30.md` (its creature sprites are PMDCollab sheets: never usable), `docs/art/pro-sprite-standards-2026-10-31.md`, `docs/art/back-view-feet-study-2026-11-02.md`, `docs/creatures/codex-new-creature-2026-10-31/DESIGN.md` (Drembit), `docs/creatures/codex-remake-2026-10-31/tallowroot/huskward/REPORT.md`, `docs/research/japanese-tools-2026-10-31.md`. Memory notes: evolve-not-grow, stage-two-reads-older, eight-views-one-image, creature-palettes, sprite-reference-choices.

Not used for stills, and why: the Opal Forge (it stops on 2026-11-17, and Codex beat it on Drembit), SpriteCook and Retro Diffusion (paid; Retro stays the walk source and is on hold), Hugging Face Spaces (sending art to one needs Preston's yes), Pixel Refiner (tried, not adopted).
