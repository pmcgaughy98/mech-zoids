# Deploy weapons, combinations: GitHub and reference scan (Claude, 2026-10-19)

Preston: "the middle pillar like gun thing bottom of torso looks like a phallus. So we will put a pouch there but the
cannon will shoot from there but more near stomach. Do github scan to get ability to create animations like that.
Transformers War and Fall of Cybertron will help ... do full scan. ... other mecha games have mechanics where a cannon
opens from stomach but we're going to add that mechanic to the game in general. I plan on adding combinations and
many other things so skill up with github etc."

## What the pillar actually is (measured, 2026-10-19)
Not a gun: it is the kangaroo's own **left (far) shin**. The battle stance's split puts the left foot forward, so its
charcoal shin column stands straight under the middle of the belly. In S and SW it hangs at the centre below the
torso; in E it was the tall near-black slab (3564 render px on `shin.L`). The ventral Pouch Flak Gun hatch is flat to
the belly and is not what reads as the pillar.

## Scan results (Firecrawl, three searches, 2026-10-19)

**Mechanical rigs for hatches and deploying weapons (GitHub):** nothing to install. What exists is general Blender
rigging (bones, constraints, drivers, hinge and slide joints), which our factory already does: parts are tagged to bones
by name (`quad_rig.bone_for`) and each battle clip is a list of bone poses rendered frame by frame
(`tools/blender/attacks.py`, `render_jobs.py`). A hatch that swings open and a barrel that slides out are two more
bones on that rig and a few keyed poses in one clip. Seen, not useful here: OpenPLX (rigid-body mates, prototype),
Rigged Systems (paid add-on), Arma Reforger weapon-rig add-ons (game-specific).

**Transformers: War for Cybertron / Fall of Cybertron (read, excerpts):** no source code or decompilation exists; the
GitHub hits are a DLC-enabling mod, a launcher and a cheat trainer (not to be used). Gildor's forum (the UE Viewer
author) says the games' animation format was never decoded, so their transformation animations cannot be extracted;
our FoC model rips (`D:\Program Files (x86)\Game assets\Mech references\`) are static meshes. The usable study
material is video: the "War for Cybertron Modding" YouTube series covers unused animations, bonus transformations and a
cut attack sequence, and gameplay footage shows the transformation and weapon-deploy timing. The `watch` skill can
measure those (frames per phase: unlock, open, extend, fire, retract).

**Mecha games with deploy and combination mechanics (GitHub):** no open-source mecha game implements chest or belly
weapon deploys or combiners in a form worth reading. These are design references to study by video and wiki
(**general knowledge, not read in this scan**): Fall of Cybertron's Bruticus (a playable combiner), Super Robot Wars
(combination attacks between units), Zoids Genesis (Unison) and Zoids Legacy-era CAS armour swaps, Medabots (part
swapping), Gundam games (transforming units).

## Synthesis proposal (nothing here is canon; Preston picks)
1. **Kangaroo p72, the fix:** (a) the stance's left foot goes back beside the right instead of forward under the belly,
   or out to the side, so no shin stands at the centre; (b) a **pouch**: a rounded orange shell over the lower belly,
   lighter orange with a rim, as a real kangaroo's; (c) the **cannon moves up to the stomach**, above the pouch, behind
   a two-leaf hatch.
2. **Deploy animation for the Pouch Flak Gun clip:** two new bones (`hatch` hinged at its top edge, `cannon` sliding
   forward). Phases, timed from the video study: hatch unlocks and swings open, barrel slides out, fires (the battle
   VFX muzzle recipe already exists), barrel retracts, hatch closes.
3. **Deploy as a game mechanic, in general:** any machine can carry concealed weapons that cost a deploy step (a turn,
   or part of one) and then fire stronger or from cover; while deployed the hatch is a weak point. Alternatives: the
   deploy is only a visual flourish with no rule; or deploy is a stance that stays open across turns.
4. **Combinations (later):** two or more machines link into one combined unit for a set number of turns (Bruticus,
   Super Robot Wars), or one machine docks armour or weapons from another (Zoids CAS). Needs Preston's design call
   before any build.

## First slice
Kangaroo p72 (stance, pouch, stomach hatch and cannon with two bones), the flak clip re-keyed with the deploy phases,
rendered and checked with `battle_fit_check`, `vfx_check` and the bind audit; before/after in E, SW and S.
