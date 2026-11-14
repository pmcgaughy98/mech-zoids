# Spider input review

Superseded input status: Preston has now supplied Meshy_AI_spider_textured_25k_20261111_character.glb in the rigged-download folder. Verified 52 bound joints. Surface restoration using that actual rig is completed in the adjacent surface-restoration-v1-2026-11-10 folder; the static-input-only findings below are historical evidence, not a current blocker.

Preston selected Spider next, replacing the proposed Mantis. No mantis asset was changed.

Located `D:/user/Downloads/spider_front - 8 legs touchup.glb`, 4,871,276 bytes, SHA256 `eaa15d8d49dacb25d08d5da2a9b3cc7a648561623f4bb57847c15815e54a956a`. This contains one static mesh, 33,332 triangles, zero skins, zero joints, zero weights and zero clips. `D:/dev/_scratch/proportions-2026-11-10/spider/spider_after.glb` is the same historical static touch-up, not a current rig. No spider-named export exists in the inspected `Mecha Beast GLB Meshy Rigged` folder. Other spider files located are the original static catalog source, gallery proxy and Blender workspace.

Inspected all four exact original reference sheets plus front, side, back, underside, top and three-quarter captures of the touch-up. It has four physical feet per side, eight legs total. The prior proportion lane's NOTES.md records removal of the original frontmost leg pair and the extra rear prong pair. Do not restore extra generated legs from the untouched archive when repairing it.

The static touch-up has extensive fragmented topology: 30,914 position-matched boundary edges and one over-shared edge at the 1 micrometre audit tolerance. These are edge counts, not counts of individual holes. Prior proportion-lane notes already document a cracked reduced display mesh with 821 islands. Its local cut caps do not establish that the whole surface is intact. No blanket hole-fill or broad weld was performed: that could bridge separate armor/legs or bake the proxy's damage into a new source.

Current status: actual rigged spider input not located; asked Preston for its path while continuing independent inspection. No Spider geometry, rig, catalog entry or gameplay model was modified. To preserve the rig during repair, start from that actual skinned export when supplied, compare against this accepted eight-leg revision and the intact high-detail original, then select a local repair. Do not replace a rigged version with this static file or invent a replacement skeleton.

Evidence: topology-audit.json, spider-inspection.json and six rendered views here. Native inspection scene/script remain in D:/dev/_scratch/mech-art-direction/spider-review-2026-11-10/. All work used local tools, no paid services.
