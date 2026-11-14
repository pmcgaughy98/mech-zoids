# Gorilla cell backings and back-frame color

The retained backing color is the slightly darker green already behind the back cells. Front shield backplates now match that source shade. The existing back field remains unchanged. The back rim, including its faded upper section, is consistently orange with source shading retained.

Latest combined files:

- `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_cell_color_review.blend`
- `D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_cell_color_review.glb`
- `front-back-color.jpg`: matching review of both shield treatments.

The backing target was sampled from 24 existing inter-cell back-shield faces: sRGB approximately (0.2373, 0.6255, 0.0412). This is the source back field's medium green, darker than its luminous cells. Keep that reference in later edits. Back rim target sRGB is (0.720, 0.435, 0.175), with restrained source shading variation.

Only texture colors changed. Front atlas edits are confined to the two backplate objects' UV tiles. Back body texture edits are confined to the orange-rim mask; zero back-background pixels were repainted. Bright cells, original back layout, and all mesh shapes remain as before. Both new images are packed in Blender and embedded in GLB.

Validation confirms all mesh vertex positions, topology, weights, normals, UVs and material indices remain unchanged, along with the 34-bone skeleton. GLB reimport retained 60 skinned hand, foot, shield and forearm objects and their textures. Front/back close views and back oblique/full-character views were inspected. Gameplay lighting and runtime animation remain outside this paint-only review.

Source `gorilla_shields_review.blend` remains unchanged. Continue from the cell-color review above. Original catalog display and gameplay assets have not been replaced. Working scripts and images are under `D:/dev/_scratch/gorilla/dark-green-backing-2026-11-08`.
