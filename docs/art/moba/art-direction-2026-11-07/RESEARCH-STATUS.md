# Preliminary source review, not a style decision

Production paused for the toolbox audit at Preston's request. No inspected model comparisons are ready. `source-atlas-preview.png` is a reduced preview of the existing GLB albedo, not a concept image or an engine test.

Primary pages retrieved via free web access on 2026-11-07:

- [Riot: Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/). Developer discussion of silhouette recognition, facing direction and visual hierarchy. Proposed application: test the gorilla's head, shoulders and fists at match distance before adding detail. Do not copy champion shapes.
- [Riot: Better Living Through Materials](https://www.riotgames.com/en/news/better-living-through-materials). Developer material-system discussion prioritizing painterly presentation, gameplay clarity and hardware performance. Proposed application: compare coherent broad material responses rather than assume more texture detail equals finish. No League shader or budgets were copied.
- [Epic/Titan Forge: SMITE 2 spotlight](https://www.unrealengine.com/spotlights/smite-2-is-being-built-for-the-long-haul-with-community-and-unreal-engine-5-at-its-core?lang=en-US), published August 29, 2024. Read the page text: third-person MOBA context, community iteration, Niagara, Control Rig and Gameplay Abilities System. The embedded video was not viewed. This page does not establish numeric character material, triangle or texture budgets; those remain unknown. SMITE is a presentation benchmark, not a source of god designs for this game.
- [Valve: Dota 2 Workshop technical requirements](https://www.dota2.com/workshop/requirements). Read the requirements index: budgets and rig constraints are supplied per hero. Proposed application: choose asset budgets using actual camera coverage and crowd cost, rather than borrow one universal MOBA number. No hero files downloaded. The linked Character Art Guide returned only an image placeholder through text retrieval, so its full content is not claimed as read.

## What remains to establish

Character materials: silhouette/part hierarchy, armor bevel response, value and color separation, roughness/metalness, edge highlights, wear, emissive power cues. No proposals are validated yet.

Arena lighting: the current foundry palette and warm sun/cool fill will be held fixed within each material comparison. Any recommended lighting changes must be shown separately and remain map-lane proposals.

VFX/team readability: permanent surface glows must leave contrast available for active shields and attacks. Team identity needs redundant shape/UI cues, not just a whole-body tint. These are candidate tests, not implemented or verified outcomes.

Performance: the inspected gorilla is 80,068 triangles with three 2048 textures, eight clips and two mesh surfaces. Do not mistake the historical 17,502-triangle handoff figure for the current inspected GLB. No frame-time/crowd measurements have been completed and no production budget is set.
