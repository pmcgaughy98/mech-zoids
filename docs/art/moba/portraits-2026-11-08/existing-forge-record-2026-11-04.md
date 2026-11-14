# Mech Legend Card Forge (Opal), 2026-11-04

Edit link: https://opal.google/edit/1RcIDskmAl_88l4vGOCydQxdE35gz8hB_ (Preston's Google account, real Chrome only).
Made by duplicating Hollowtide's Attack / Title Card forge and rewriting every step. The Hollowtide original is untouched.
Opal leaves Labs on 2026-11-17; after that the prompt below is the forge, and it can be rebuilt as a Gemini skill the way
`D:\dev\hollowtide\docs\forges\gemini-skills\` does it (not built yet).

Job: one tall loading-screen portrait per legend per skin, the picture a player's card shows while a MOBA match loads
(Preston, 2026-11-04: League of Legends and SMITE loading portraits, a different one per skin).

## Graph (verified after a reload)
| Node | Id | Kind |
|---|---|---|
| Card Brief | ask_user_creature_brief | user input, text, required |
| Approved View | bbeafb34-461a-4a26-b5e1-678b41362ae9 | user input, image |
| Pose Reference | 510f5aba-88c2-4ae2-aa27-4d3a6d773f8e | user input, any type (NONE or an approved animation frame) |
| Generate Loading Portrait | node_step_cinderhide_sprite | Nano Banana Pro ("image-pro"), aspect 9:16 |
| Review Card Portrait | node_step_cinderhide_display | shows the picture unchanged, reads Generate and Card Brief |

Brief, Approved View and Pose Reference feed Generate; Generate feeds Review.
Not updated: the app description and the node card summaries still carry Hollowtide text. The Generate prompt governs.
Image generation has a daily limit in Opal. Runs are free.

Chips in the prompt are templates of the form `{{"type":"in","path":"<node id>","title":"<title>"}}`; below they are
shown by title.

## Card Brief, what to type
MACHINE: working id and animal (for example rhino_l, rhinoceros). SKIN: DEFAULT, or a skin Preston named, with its
colours. VIEW. POSE: from Pose Reference, or APPROVED STANCE. FRAMING: FULL BODY. BACKDROP: SCENE or PLAIN. NOTES.
Never type a name, role text or lore; the card adds those later.

Run 3 brief (rhino_l): MACHINE: rhino_l, a rhinoceros war machine. SKIN: DEFAULT. VIEW: SIDE, head and horns pointing
RIGHT as on both attached sheets, camera level with the body and square to its flank, only the near flank visible, no
three-quarter turn. POSE: from Pose Reference: reared up on the hind legs at the top of a ground pound, front legs
lifted, about to slam down. FRAMING: FULL BODY, large, the whole machine filling most of the width, hind feet in the
lower third. BACKDROP: SCENE. NOTES: one small red eye on the head where the sheet has it; yellow and orange plates,
grey joints and the near-black outline exactly where the sheet has them; same plate count, same two horns.

## Generate prompt (verbatim, 4566 characters)
```
MECH LEGEND LOADING PORTRAIT FORGE. Make ONE tall loading-screen portrait of the machine shown in Approved View: the picture a player's card shows while a MOBA match loads, one per legend and per skin. One single picture only: no text, no name, no letters or numbers, no frame, no border, no card template, no logo, no UI, no extra machines, no panels.

Card brief: {{Card Brief}}

Approved view: {{Approved View}}

Pose reference (NONE, or an approved animation frame of the same machine): {{Pose Reference}}

IDENTITY, the most important rule. Approved View is the only authority for the design. Redraw THIS exact machine, larger and with more pixel detail, not a new design. Keep, part for part: the silhouette and proportions, the head shape, the horn count and shape, every armour plate and the seams between plates, the leg shapes and joint discs, the feet, the tail, the eye colour and its place on the head. It is a mechanical animal war machine with a hard plated body. Do not turn it into a realistic animal, a glossy toy, a generic robot or a different species. Do not add parts the sheet does not show: no weapons, guns, pilots, cockpits, wings, spikes, cables, text, decals or extra armour. Do not remove parts. Pose Reference, if given, sets only the pose; the design always comes from Approved View.

SKIN. DEFAULT means exactly the colours of Approved View, each colour where the sheet has it. Any other skin is named in the brief with its colours: recolour plate for plate and keep every shape and part. Never make up a skin, a colour scheme or decoration the brief does not give.

CAMERA. Draw it from exactly the camera of Approved View and the view the brief names. SIDE means a true side profile: the camera is level with the body and square to its flank, we see one flank only, no front face and no three-quarter turn. Keep the facing direction of the sheet: if the head points right on the sheet, it points right in the picture. Never mirror, never rotate the machine toward the viewer.

POSE. The pose of Pose Reference if one is given, otherwise the approved standing pose from the sheet. Anatomy and plates stay the same through the pose.

FRAMING. Tall portrait. The machine is large and whole, nose to tail, filling most of the width, with its lowest point in the lower third; never crop the horn tip, the face, the eye, the feet or the tail. Keep the machine's own proportions: never stretch or squash it to fill the frame.

BACKDROP. Follow the brief. SCENE, the default: a simple, dark, low-contrast battleground behind the machine: the ground it stands on, a little dust and cracked ground where its feet strike, distant rock or wall silhouettes, and a sky in three or four stepped colour bands. The machine stays the brightest, most detailed and most saturated thing in the picture, with its near-black outline clear against the backdrop. No other machines, creatures, people, text or logos. PLAIN: flat pure #FF00FF magenta everywhere outside the machine.

FINISH. This is NOT an upscale. The sheet is a small low-resolution game sprite; the portrait is a new close-up drawing of the same machine at about three times the sheet's pixel resolution. One sheet pixel becomes roughly a 3x3 block, and those blocks are redrawn with finer detail, never left as flat enlarged squares: bevelled plate edges, a thin highlight along the lit edge of each plate, panel lines and small bolts along the seams the sheet already has, darker recesses inside the joints, a little wear on exposed edges. Detail goes only on parts the sheet already has. Pixel art: the skin's palette plus at most two in-between shades per colour ramp, flat cel shading in clean clusters, the sheet's near-black outline around the whole silhouette and between major plates, hard crisp pixel edges on one even pixel grid, the sheet's lighting direction. The backdrop uses fewer colours and less detail than the machine. No gradients, no gloss, no specular shine, no soft airbrush, no painterly blur, no 3D render look, no anti-aliasing, no noise.

CHECK before finishing: compare against Approved View plate by plate: same horn, same eye, same plates, same colours for the skin, same camera, same facing, same proportions. Returning the sheet enlarged, stretched or traced at its own resolution is a failure. If anything was invented or lost, fix it. Return only the one picture.
```

## FINISH v2 (IN OPAL since 2026-11-04, checked after a reload: prompt 4690 characters, three input chips intact)
The verbatim prompt above is the old version; in it, replace the FINISH paragraph with the text below and add the CHECK
words below to get the live prompt.
Preston on run 3: "clean it up to look like our texture get rid of the bolts and such". The FINISH paragraph above
asked for bolts, panel lines and wear, so the forge drew them. Replace the FINISH paragraph with:
```
FINISH. This is NOT an upscale. The sheet is a small low-resolution game sprite; the portrait is a new close-up drawing of the same machine at about three times the sheet's pixel resolution, in the sheet's own texture. Texture: large flat plates; each plate face is flat colour, with a lit facet in the sheet's highlight colour and a shadow facet in its shade colour, split by a clean tone change, exactly as the sheet does it; near-black seams only where the sheet has seams between plates. Larger means cleaner, not busier: no bolts, rivets, screws, panel lines, scratches, wear, chips, grime, decals or surface noise, and no surface detail the sheet does not have. Pixel art: the skin's palette plus at most two in-between shades per colour ramp, flat cel shading in clean clusters, the sheet's near-black outline around the whole silhouette and between major plates, hard crisp pixel edges on one even pixel grid, the sheet's lighting direction. The backdrop uses fewer colours and less detail than the machine. No gradients, no gloss, no specular shine, no soft airbrush, no painterly blur, no 3D render look, no anti-aliasing, no noise.
```
And in CHECK, after "same proportions", add: "no bolts, rivets or panel lines".

## Review prompt (abridged; the live app is authoritative)
Shows the original generated portrait unchanged, large, centred on a plain dark page, with CSS
`image-rendering: pixelated`, and labels it a candidate to compare plate by plate with the approved view before use.

## Inputs that work
- Approved View: the approved sheet view on a canvas of the output aspect (9:16), 6x, magenta background. A square
  canvas made run 1 stretch the sprite into the square.
- Pose Reference: an approved animation frame on the same 9:16 6x canvas, or NONE.
- Upload: Claude in Chrome's file_upload fills a file input added to the top page (scratchpad paths only), and
  Opal's own input receives it when "Upload from Device" is clicked. On the any-type input the menu has more entries,
  and Webcam sits where Upload sits on the image input.
- Saving edits in the Opal editor: set the editor value, then a real keystroke (End, space, Backspace), then click the
  canvas, and check after a reload.

## After the forge
`loading_build.py` (in `docs/art/moba/cards/`) crops, snaps to the approved palette plus backdrop colours and
downsizes to the 205x373 loading card. Runs and results: `docs/art/moba/cards/RUNS.md`.
