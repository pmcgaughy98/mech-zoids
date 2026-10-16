# R1: hangar bay, Function review ready

Built the review layout for a 14 x 16 x 8 m hangar with a 6 x 7 m maintenance bay at the origin,
6 x 5 m north bay opening, four-meter exterior apron, two scheduled side windows, eight original
procedural prop families, and thirteen instances. The teal wire outline reserves the machine's
space; it is not a finished machine or proof of runtime fit.

Files:
- `art/rooms/hangar_bay/source/hangar_bay_function.blend`: editable Function study.
- `art/rooms/hangar_bay/evidence/plans/lower-room.png`: geometry-derived floor plan.
- `art/rooms/hangar_bay/evidence/plans/reflected-ceiling.png`: separate ceiling layer.
- `art/rooms/hangar_bay/evidence/images/prop-contact-sheet.png`: all eight reference prototypes.
- `art/rooms/hangar_bay/evidence/masks/opening-contact-sheet.png`: door/window mask review.
- `art/rooms/hangar_bay/evidence/renders/function-visual-target.png`: overview; 320x180 version beside it.
- `art/rooms/hangar_bay/evidence/`: portable room contracts, dimensions, provenance, measurements, and reviews.
- `tools/blender/plan_hangar_bay.py` and `package_hangar_function.py`: reproducible builders.
- `docs/reference/hangar-room-synthesis-2026-10-11.md`: primary references and tool contributions.

Checks:
- Blender build and renders complete; references, floor/ceiling plans, elevations, and opening sheets inspected.
- `package_hangar_function.py`: FUNCTION_PREFLIGHT_READY. All eight references and three exact rectangular
  aperture masks present; hashes/dimensions verified; 3,008 prototype triangles plus an 11,000 hero allowance
  fit the 40,000 budget. Paid generation: zero credits.
- Plugin `validate_room.py --gate function`: DOES NOT PASS. Human approvals remain pending, correctly.
  Additionally, its Meshy-only validator cannot accept R1's explicit procedural/zero-spend path.
  Full output is preserved in `evidence/function-gate-validation.txt`.
- The provided mask tracer was attempted but lacks `cv2`; exact rectangular boundary tracing was verified
  with Pillow/NumPy. No software was installed.

Not verified: actual gorilla pose/animation fit, final shell and Boolean apertures, Godot shading/light parity,
navigation/collision, runtime budgets. Those are Form/Runtime work after approval. No room GLB or Godot scene
has been exported. The existing 2D base, machine model, Claude's scripts, and live Blender were not edited.

Open decision: approve or revise the Function layout, all eight reference prop prototypes, and three opening
dimensions. Free procedural props are the requested production path; no Meshy spend is requested.
