# Original SMITE Geb attack study — 2026-11-09

Preston asked for a slower swing like Geb and explicitly authorized studying the installed original SMITE files. Found `D:/Program Files (x86)/SMITE/BattleGame/CookedPCConsole/GEB_ASSETS_SF.upk`, base `skl_god_geb`, animation set `as_god_geb`. Used the previously approved local UModel build (`D:/dev/_tools/umodel/UEViewer-master/umodel_64.exe`) with the installed game Oodle DLL on process PATH. The game installation was read only. No asset was downloaded from GitHub or copied into production.

Private workspace: `D:/dev/_scratch/geb-study-2026-11-08/` (folder created before the client date advanced). Editable `geb-study.blend`, package inventory/export logs, glTF, sampled-motion JSON and study script are there. `geb-attacks-reference.mp4` is a 20.83-second native Godot playback: four fire clips, normal front and side followed by half-speed front. The material is neutral clay, not SMITE's actual textures/shaders. The scattered-rock body is Geb's source geometry; this is a motion study, not a recreated final in-game presentation.

## Verified observations

Base AnimSet exported 62 clips, including `fire_01`, `fire_02`, `fire_03`, `fire_04`, combat/noncombat idle, directional runs and transitions. All four fire clips have first-to-last exported sampler span 0.934444 s, independently checked from glTF accessor times and Blender import with fps set before importing. Do not infer actual engine cooldown, damage time or loop padding from that span. An earlier working render set fps after import and therefore reported a wrong 0.747556 s duration; that report/render procedure was corrected and replaced.

Sampled 61 poses per fire clip and inspected seven front/side phases, then native front/side playback frames. The fire motions visibly turn and lean the torso, carry an arm through a broad arc, follow past the front and return to the initial pose. They vary between side-led sweeps and more downward/whole-body motion. These are the base set's named fire candidates; exact runtime selection/attack-speed blending has not been inspected. No target collider or engine hit notification was extracted, so this study does not claim a measured contact event.

## Application to our mech

The useful change from the older v16 jab is a loaded shoulder/torso turn, fist-led arc through the intended target and readable follow-through. Slow anticipation/recovery can communicate mass while contact remains decisive. Preserve supporting knuckle/feet and rigid lengths; do not turn the arc into the aimless lateral waving rejected in v15. Large forearm shields require clearance in actual geometry, not just copied bone angles. Adapt authored original curves to the gorilla rather than importing Geb's rig or keys into a shipping asset.

During this task Preston's authorized Hub handoff required reading Claude's newer gorilla v26/v27 work. It already contains swat, swat, slam revisions approved later than this chat's old moving-jab prototype. This Geb study is therefore retained as additional reference; it does not overwrite those newer clips or duplicate their production work. The same handoff assigned the isolated ally/self shield-cast trial, documented separately in `gorilla-shield-cast-isolated-trial-2026-11-09.md`.

A focused Firecrawl web/GitHub search returned SMITE 2 or unrelated generic code rather than an exact original-Geb animation source. That is not proof no public copy exists; the verified local package made further searching unnecessary. Research feedback was submitted. For extraction/tool limitations see `smite-study-2026-11-08.md`; these local exports cannot establish final game blending, shaders or combat feel.
