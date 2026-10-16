# Gemini Deep Research: skill-up for building game mech models (2026-10-12)

Preston: "lets do gemini deepresearch task so we can skill-up your ability to make these models." Sent to Gemini Deep
Research in Chrome. The report lands in his Google Drive under the title in the prompt. Claude reads it, then turns
the findings into build tools and checks for `tools/blender/build_ape_l_v2.py`.

## The prompt as sent

Title the report: "Hollowtide mech skill-up: AAA-quality animal mechs built by script, 2026-10-12".

Be honest throughout. If you cannot verify something, say so plainly. Mark estimates as estimates, cite a source for
every concrete number, and do not invent studio practices, settings or figures.

Context: I build 3D animal-shaped war machines (a knuckle-walking gorilla mech first) for an indie Godot 4.7 game.
The models are built entirely by Python scripts in Blender 5.2 (bpy and bmesh, no hand sculpting, no paid add-ons,
no AI 3D generators). The quality target is Transformers: War for Cybertron and Fall of Cybertron (High Moon
Studios, Unreal Engine 3), especially the Dinobots' and Insecticons' beast modes, with Zoids as the design core.
Current state: about 15,000 triangles, one 2048 px texture set (colour, normal, ORM), profile-intersection solids
for the head, torso and limbs, layered framed armour plates, segmented glow rings, a rigid 14-bone rig with five
clips. It reads as a good fan model, not yet as a shipped AAA asset.

Research and report on:

1. How High Moon built the Cybertron characters: modelling and texturing pipeline, triangle and texture budgets,
   high-to-low baking, material layout, how panel lines, wear, decals and emissive lights were made, and anything
   documented about their Unreal 3 metal shading. Prefer artist portfolios (ArtStation, Polycount threads),
   GDC talks and developer interviews.
2. Hard-surface techniques that can be done procedurally in bpy, with concrete parameter values:
   - shape-from-silhouette (profile intersection) and when it fails
   - boolean cut and panel workflows
   - support loops versus bevel plus weighted normals
   - mid-poly workflow with custom normals
   - Geometry Nodes for panel lines, bolts and greebles
   - trim sheets and decals
   - plate layering with thickness
   - making separate parts read as one machine
3. Baking and texturing by script: high-to-low normal bakes (cage and ray distance), curvature, AO and ID maps,
   procedural edge wear and grime, colour variation, and texel density targets for third-person action games. Also
   cover the normal-map green-channel convention between Blender and Godot.
4. Design: shape language and silhouette for beast-mode mechs; mapping real animal anatomy (gorilla shoulders,
   forearms, knuckles) onto machine parts; readability at a distance; the big, medium and small detail ratio.
5. Rendering in Godot 4.7 so the asset looks AAA: PBR settings for painted metal, tone mapping, rim and outline
   options, reflections, and light setup for a character showcase.
6. Animation for a quadruped mech: knuckle-walk mechanics, mechanical secondary motion (pistons, plates), foot
   planting and IK in Godot 4.7, and the clip list a shipped character has.
7. Measurable quality checks a script can run to compare a model with a reference (silhouette overlap, edge-angle
   distribution, texel density, normal-map detail, colour statistics), and what thresholds professionals would use.
8. Any papers, open-source tools or Blender add-ons (free, with licences) for procedural hard-surface modelling,
   shape grammars or kitbashing that a script could use.

Deliverable: a structured report with numbered, actionable steps, concrete parameter values where they exist, what is
verified versus inferred, and sources. End with a prioritised list: the ten changes most likely to move a scripted
model from fan-quality to shipped-AAA quality.
