# Gorilla chest beat: real motion and targets for our gorilla mech (Claude, 2026-11-09)

Preston: "First, understand how a gorilla would beat its chest in real life, then how it should feel on our model."
Study only. No footage, frames or data are copied into the project.

## What was read or measured
| Source | Read or measured | What it gave |
|---|---|---|
| Wright et al. 2021, *Chest beats as an honest signal of body size in male mountain gorillas*, Sci Rep 11:6879 (PMC8032651) | read (key numbers) | 36 chest beats, 6 silverbacks: mean **0.65 s** long (0.17 to 2.82), mean **8 beats** (3 to 27), mean **13.7 beats a second** (9.2 to 18.1); usually rise **bipedally**, **cupped hands**, rapid succession |
| National Geographic, Gorilla Fund, MPG press pages | read (excerpts) | not fists: cupped hands, which amplify the sound |
| YouTube "Silverback Oumbi Beating His Chest" (2xPCVgRre_I), 57.3 to 58.9 s, front-on, 25 fps | measured frame by frame (40 frames), plus the audio envelope | the motion breakdown below |
| OpenApePose (github.com/desai-nisarg/openapepose), 71,868 ape photos with 16 landmarks | read (README) | stills only, no motion; useful later for proportions, not timing. Not downloaded |
| CMU-style motion capture of a gorilla | searched, none found | no ape mocap on hand |

## The real motion (Oumbi, frame times from the start of the rise)
1. **0.00 to 0.36 s, the look up.** Still crouched on the knuckles; the head tips back first.
2. **0.36 to 0.72 s, the rise.** The torso lifts to near-vertical; the arms come up close to the body, hands sliding up from the belly to the chest. No wide wind-up.
3. **0.72 to 1.40 s, the drumming (about 0.68 s).** Upright, head back, chest pushed out.
   - Hands flat or cupped on the **upper chest**, fingers pointing inward, nearly meeting at the breastbone.
   - **Elbows flared out wide**, at about mid-chest height; forearms nearly **level across** the chest.
   - The strokes are **small**: each hand leaves the chest only a hand's depth. The elbows pump the motion, not the shoulders.
   - Audio: strike gaps of about 0.02 to 0.08 s, which fits 12 to 15 a second.
4. **1.40 s on, the settle.** The body lowers while the hands are still on the chest, then drops back to the knuckles.

## What v21 and the first v22 attempt got wrong
- **v21:** a big wide arm swing into each beat; the fist stopped beside the face; the torso pitched up only 24 degrees.
- **First v22 attempt:** stood him up properly, but still swung from far out, so the arms stretched to their limit and the fists hovered at face height.

## Targets for our gorilla mech (proposal; numbers are Preston's to change)
- **Rise:** from the knuckles to near-upright in about 0.30 s (a little faster than the real 0.36 s, for game feel), head tipping back first.
- **Drumming:** 6 strikes, alternating, left first, at **0.075 s apart, about 13 a second** (the real mean). Total about 0.45 s, inside the real 0.17 to 2.8 s range.
  - At 60 fps a strike is about 4.5 frames. That reads as a blur close up; from behind (SMITE camera) the pumping elbows carry it.
- **Hand pose:** the fist lands on the **upper pec plate**, inner side first, forearm level across the chest.
- **Elbows:** flared out to the side at chest height.
- **Stroke size:** small, about 0.12 to 0.15 m off the plate between strikes. Our forearms are much bigger than a real gorilla's, so the stroke is scaled up a little to stay readable.
- **Head and chest:** head back about 20 degrees, chest pushed forward through the drumming.
- **Then the slam:** both fists come down to the ground for the dome (our addition, not real gorilla behaviour).
- **Kit beats:** the taunt on strike 1, the re-taunt on strike 4, the dome on the slam.

## Model limits (measured in Blender)
- The front of the pec plate is 0.55 m in front of the shoulder joint; the arm is 0.906 m long. A fist can only reach the plate swinging in from the side with the wrist straight, which matches the real elbows-out, forearms-level pose.
- The forearm hex plates are weighted to the hand bone, so contact is measured on the fist parts only (digits, palm, thumb).
