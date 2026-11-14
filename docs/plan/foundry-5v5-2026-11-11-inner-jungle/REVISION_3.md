# Inner-jungle objective placement, November 11, 2026

**Access revised:** [Revision 4](../foundry-5v5-2026-11-11-open-bosses/REVISION_4.md) preserves these centers and opens both areas toward mid and jungle. The enclosed, outer-lane-facing entry arrangement below is historical.

Preston corrected the placement request: put the objectives back in the jungle inside solo and carry/support lanes. This supersedes Revision 2's external boss courts and its long-rotation target. The separate playable scene remains `scenes/map5v5/foundation.tscn`.

Gold beetle stays west, now at **(-34, 0)**. Wyvern stays east, now at **(34, 0)**. Both encounter floors, ring walls, landmark installations and entrances fit between mid and their outer lane, whose center is x = +/-62 near mid. The court's outermost wall is approximately x = +/-48, inside the outer lane's jungle-side edge at approximately +/-55.

Opened the large central wall masses to accommodate the courts, retaining a narrow mid-facing barrier and capped wall groups north/south. The two boss entrances now face their nearby outer lane and connect inward from it. Four camp loops, home service roads, scouting recesses, current roster/camera and the rest of the intricate placement pass remain. No new paid assets or jobs.

The navigation buffer is now 1.25 m to keep diagonal baked corners clear of the real 0.8 m player sphere. A first review exposed three routes clipping the same wall corner; collision geometry and player movement were preserved, and the local navigation clearance was corrected.

The old 45-second minimum and mid-wipe return assertions were removed because Preston withdrew that placement rationale. Tests now require the courts to be inside the outer lanes and all entrances/routes to remain traversable. Travel times are recorded as observations, not enforced balance goals. Boss models remain static previews, with no new encounters or rewards.

Evidence: `layout-board.png`, native `top-down.png`, both boss-approach frames, `native-review.json`, `native-runtime.log` and updated `walkthrough.mp4` / `walkthrough-checks.json`. Earlier revisions and their evidence remain in their original folders; they no longer describe the current placement.

Final verification: **102 native checks passed, zero failures; 7/7 actual walking waypoints passed.** Both boss approaches, overhead and labeled board were visually inspected. Shortest gate-to-gate travel is now 37.64 s and mid-to-gate about 23.1 s at 3.5 m/s; these are descriptive measurements only. The known Windows certificate-store startup diagnostic and two texture-release exit warnings remain recorded; the final run has no script errors. No shared gameplay, camera, rigs or source art were changed.
