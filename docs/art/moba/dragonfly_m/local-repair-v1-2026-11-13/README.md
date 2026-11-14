# Dragonfly six-leg repair

November 13, 2026. Preston selected outer-front leg pair 2 for removal. Pairs 1, 3 and 4 remain: six legs, four wings, two antennae and one segmented tail. All four source references and the intact generated archive were reviewed; the archive's extra limbs are not approved anatomy.

![Matched before and after](before-after.png)

Input: `D:/user/Downloads/Mecha Beast GLB Meshy Rigged/Meshy_AI_dragonfly_remeshed_25k_20261111_character.glb`, SHA256 `4aa5552ba0601f5006e7e4a06eb93c67f7721a1cf50e811ef67349cf6c47eeaf`, 25,263 triangles, 46 bound joints, no clips. A byte-identical copy is archived in `art/model_catalog/sources/` under its original name. Original generation PNGs and intact quality archive are unchanged.

Result: `dragonfly-rigged-local-repair-v1.glb`, SHA256 `d21585337fb2f4d48ef8a333afc05c89823e3a2ecd18bf807ea0493d5744ec67`, 24,662 triangles. Editable scene: `dragonfly-rigged-local-repair-v1.blend`, with four packed original reference views and provenance.

Removed the selected pair, 88 detached tip-scrap triangles and 15 malformed surface flaps. Both attachment contours are rounded into fitted oval sockets with small beveled teal closures. Only new cut vertices were rounded; original source position, normal and UV rows remain exact. Source-face regression confirms all 3,203 guarded neighboring upper-joint faces remain unchanged, protecting the retained ball joints.

The original 46-joint hierarchy, rest transforms, inverse binds, original materials and embedded textures are preserved. Removed chains Bone_022 through Bone_027 remain in the hierarchy; their residual influence on used surfaces was reassigned locally to their existing body parent Bone_001. No original skeleton node was moved. Original binary data is retained as an exact prefix with new attributes/indices appended; one local socket material was added. The archived topology-only staging copy is historical, not the final anatomy.

Independent actual-export checks verify zero open edges, over-shared edges and collapsed triangles, finite normalized weights and no remaining used-surface influence from the removed chains. Seventeen isolated diagnostic poses cover all six retained legs, all four wings, head, antennae, tail and both removed controls. Maximum measured coincident-surface separation is 0.000000123 m, below one micrometre; both removed controls produce zero displacement. Original imported rest matrices are restored between tests. See `independent-export-audit.json`, `visual-deformation-check.json` and `pose-proof.png`.

Textured front, both sides, back, top, underside, both socket closeups and joint motion were inspected. Final Godot native three-version/original-review-sheet/46-joint/chase-camera check passed, with screenshots inspected in `reports/model_catalog/dragonfly-six-legs-v1/`. Workshop Dragonfly now displays this repair. C compares intact quality archive, downloaded four-pair rig and six-leg repair; R switches original reference PNGs and labeled comparison sheets. The intact archive is a quality reference; exact historical remesh-upload linkage is not verified.

This is a local anatomy/topology repair at the download's resolution. Original bake roughness remains; polished locomotion/flight is separate work. No authored map or gameplay asset is replaced. Other roster work is preserved. Scripts/configuration are packaged here, with canonical work in `D:/dev/_scratch/mech-art-direction/dragonfly-review-2026-11-13/`. Local Blender/Python/Godot only; no paid generation, credentials, rerigging or commits.
