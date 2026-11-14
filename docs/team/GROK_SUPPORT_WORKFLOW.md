# Grok support workflow for Claude and Codex

Preston authorizes shared checking, audit and research support. Grok's staged
tools are at `D:/dev/_scratch/grok-mech-foundations-2026-11-10/output/team_support_v1/`.
Codex independently reran its 18 tests successfully on November 13. This does
not certify visual quality, runtime balance, or exhaustively verify its code.
Grok's original TEAM_GUIDE.md there contains exact commands and limitations.

Use an explicit input contract: source GLB/events/profile and hashes, named clips,
event seconds and duplicate policy, optional exact live copy. The clip checker
does not infer names or compare a historical export to current runtime by default.
Pose presets require per-mech region mapping, stated units/FPS and method limits.
Kangaroo's preset samples every sixth glove vertex with two inside-test rays;
it is not an exhaustive collision proof or a universal fennec bone map.

Before accepting a finding, reproduce it and check its source/version/measurement
space. Keep pass/fail/unknown separate from approved/rejected/unknown. Use actual
visual and engine review for claims they alone can establish. Don't count passing
synthetic tests as proof the art reads correctly. Record current versus historical
and superseded claims so later registration doesn't falsify earlier notes.

From the Grok workspace:

```
python output/team_support_v1/clip_contract/check_clip_contract.py --contract <contract.json> --out <result.json>
python -m unittest output.team_support_v1.clip_contract.test_clip_contract output.team_support_v1.pose_preset.test_pose_preset output.team_support_v1.kit_assertions.test_formula_checks output.team_support_v1.handoff.test_handoff
```

The kit arithmetic checks use a frozen November 13 code snapshot, not actual
Godot matches. The balance review and its untested hypotheses live under
`balance-review-2026-11-13/` in the Grok workspace. Recheck current files before
acting on them. Technique notes and a handoff template are in `briefs/` and
`handoff/`; older animation-foundation GLBs remain unapproved drafts.

For every reusable lesson, retain the input/version, executable check or concrete
example, independent review evidence, limitations and next refinement. New chats
must read this material; they do not automatically inherit other conversations.

Next large assignment: combat interaction harness and confirmed wiring fixes,
staged for owner review. Its brief/launch/status are in
`D:/dev/_scratch/grok-combat-lab-2026-11-13/`. No speculative balance nerfs or
silent live installation are authorized by that staged job.
