# Rhino seismic effects atlas v1

Original transparent art generated with the built-in image generator on 2026-11-10. `seismic-atlas-v1.png` is the unchanged raw RGBA output, 1774 x 887 pixels. Exact prompt: `seismic-atlas-v1-prompt.txt`. No separately billed external generation was used.

The eight cells are arranged in four columns and two rows:

| Index | Component | Live use |
| --- | --- | --- |
| 0 | Horn sweep | Horn hook/rip/gore animation contact |
| 1 | Seismic epicenter | Initial ground-pound slam and toss landing |
| 2 | Charge wake | Toss dash and stampede travel |
| 3 | Segmented seismic perimeter | Pound/finisher area accent |
| 4 | Brace armor crest | Actual planted brace state |
| 5 | Three-notch pressure pulse | Four real stomp cues and brace floor accent |
| 6 | Horn catch flare | Confirmed basic contact and toss catch |
| 7 | Stampede ground rupture | Finale slam event |

Gold armor, a swept horn and three-notch mint piston reactors define this atlas. Gorilla shield/honeycomb motifs were not reused. The generated atlas has soft low-alpha haze and imperfect gutters; the shader fades each cell's border and raises alpha to 1.85. Raw output is preserved. No claim of perfect cell isolation is made.

The art is composited on ground and upright planes by `scripts/moba3d/rhino_painted_fx.gd`. It observes the existing RhinoKit cues and current registered body events. It does not deal damage, move units, change cooldowns, author new hitboxes or edit animation. The existing kit's range rings remain authoritative; painted ring accents are smaller and decorative.

Play using `Launch Rhino Art Arena.cmd` in the project root. This optional scene inherits the actual Arena Play scene and adds only the rhino art observer. The shared default scene and gameplay scripts remain untouched. The observer installs on new rhino kits, including a roster swap, and is freed with the kit. The variant explicitly loads the registered native rhino at startup, covering the base arena's legacy sprite-only --rhino startup.

The current registered source was v47 at implementation time, not the earlier scratch front-knee repair. Model, rig, materials, gameplay profile and clips were not replaced by this art pass.

Scripted industrial-map review: `tools/debug/rhino_painted_fx_2026_11_10/launch-review.cmd`. Native captures and check logs: `D:/dev/_scratch/rhino-painted-fx-2026-11-10/`.
