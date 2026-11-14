# Rhino seismic-power body: first review

One built-in image after Preston's "rhino next". Prompt saved in `prompt-model-views.txt`; only reference was Drembit for pixel craft. No old rhino artwork supplied, no retries, no MeshForge job. Actual built-in token usage/cost is not exposed.

Original: `C:/Users/pmcga/.codex/generated_images/01a1b3d2-bd2d-78f1-922f-9db2d803864e/exec-89b7ecbb-8c90-4991-acd0-34ad7dbc9023.png`.

Unchanged raw: `sheet_raw.png`, RGBA 1536x1024, SHA256 `fc34e86745e6ca6b2a41b17a9ebad1332a3518bb9f9b73df0dddb821d0e4ba3a`.

## Visual review and measurements

- Golden-yellow armoured rhino, long low wedge head, large central snout horn plus small secondary horn, barrel torso and four thick pillar legs. Short segmented tail and compact ear plates.
- Circular shoulder transducers, layered dorsal drive with illuminated slit, mint-teal horn channel, small chest resonator, compression pistons and broad ground-coupling feet make the seismic power source visible at rest.
- No flames, furnaces, weapons or held objects. Earth/tremor is the proposed visual direction, not a final kit decision. Rear has no eyes or face.
- Heights: front, left and back 433 px, right 430 px; spread about 0.7%. Both profiles 767 px wide. No alpha>=128 body pixels touch any source-sheet border. All four feet present in the profiles, far feet higher in projection.
- Low-opacity external haze appeared despite the prompt; the white packaging excludes alpha below 128 and keeps the four main body components at one shared scale. No body redraw. The source is preserved unchanged.
- Pixel-influenced modeling reference, not a validated sixteen-colour final sprite. Fine edge shading, many intermediate colours and outside ink remain. Matching projections do not prove a coherent 3D mesh; inspect horn count, ring geometry and separate legs on any generated model.

## Deliverables

`white_views/rhino_front.png`, `rhino_left.png`, `rhino_back.png`, `rhino_right.png`: RGB 1024-square white sheets, same nearest-neighbour scale, lowest contact on row 935. `prep.json` records crop boxes and scale; `review.png` is the overview; `rhino_four_white_views.zip` bundles the four individual PNGs.

Existing rhino art, kit and game assets are unchanged. New body awaits visual pick. Pangolin remains next in the proposed order unless Preston redirects.
