# Current-game product and kit review, 2026-11-10

Grok completed a current-state review and a second critical pass. These are proposals for Preston, not approved kit changes. No gameplay, balance, model, animation or audio files changed in this review.

Read [the later recommendations](GROK_ADDENDUM.md) before [the full initial report](GROK_REVIEW.md). The addendum revises the initial fennec favorite and the suggestion to defer all economy work. The initial report contains the complete roster audit and broader format, combat and match-loop comparison. [Source checks and access limits](SOURCE_CHECKS.md) distinguish developer accounts, player anecdotes, public data and community/prototype code.

## Strongest recommendation

Keep the third-person mechanical-animal MOBA foundation and existing models. Make a cohesive small test roster feel excellent before authoring 25 full kits. Grok proposes gorilla, rhino, fennec and falcon as the first four choices, with hummingbird or chameleon as possible next additions. This is a production/testing sequence, not removal of anyone from the roster.

Preserve the gorilla's model, rig, sources, weighted movement, basic-chain character, green shield technology, Grab Slam, Shield Drive and chest-beat/cage foundations. Resolve aim, actual hit detection, visual contact, cancellation and readability together. The newly polished heavy basic remains a review candidate, not an automatic replacement of the runtime export.

## Fennec: useful revision, still an open design choice

Grok's final favorite keeps one walk-through team-portal ability, with delayed projectile pressure, a line attack and a telegraphed area-control ultimate. It removes the extra personal blink and team-teleport ult. Each combat button works without a live portal. Full passive/basic/four-slot descriptions and counters are in the addendum. Names and numbers are illustrative.

Codex judgment: that is an improvement, but its passive, line and ult still all refer back to doors. If Preston's concern is the entire kit's identity rather than just the number of teleports, reduce those dependencies further. A concrete alternative for discussion is a disruption mage:

| Part | Proposal |
|---|---|
| Passive | Brief sensor information after a successful ability hit, with a clear expiration. No portal requirement. |
| Basic | A precise emitter dart, aimed consistently with its visible path. |
| 1 | A small delayed energy-burst projectile for clear and poke. Enemies can leave its marked blast area. |
| 2 | A short-lived pair of team portals. Visible destination and entrances, predictable traversal and a meaningful cooldown. |
| 3 | A line tag that makes the fennec's next basic hit against that target stronger. Miss the line and the follow-up is lost. No teleport or hard control. |
| 4 | A charged area barrage that controls a marked patch of ground. Leave the area or interrupt the charge. It does not relocate the team. |

This is Codex's alternative, not Grok's delivered kit or Preston's approval. Its first test would be ordinary fighting with slot 2 unavailable, then compare how much better a well-placed portal makes that same fight. Do not add automatic damage copies through every gate before that baseline is fun.

## Economy, objectives and counterplay

Keep Preston's two objective roles: gold and temporary siege/team-fight power. Grok's addendum proposes a small four-option spending board rather than a large item catalog. That is one candidate, not a decision to abandon personal item builds.

Codex judgment: test a minimal useful gold sink before implementing the gold reward. Be cautious about the suggested paid wave upgrade, tower repair and temporary overclock: those can duplicate side pits, prolong matches or overlap the power boss. Compare a few personal upgrades against the team-requisition approach before choosing. Pits, beacon and power boss together must still leave a defensive response.

The suggested center-line capsule and dimensions are untested hypotheses. Do not silently replace the current aim/hit shape, add hidden reach, or declare the skinny-target issue solved. A center hit needs plausible visible contact while preserving the animation Preston likes. Rhino's currently active animation/aim work owns its in-flight changes; this review does not supersede or modify them.

## Evidence and execution

Prepared a dated snapshot of 188 project text files (about 1.7 MB), reconciled current Codex Hub/Gorilla/Rhino/Factory context, and locally reviewed selected game-relevant messages from the 16 newest scoped Claude session records. Provided a curated game summary rather than raw chat logs. Grok made 46 local read/discovery calls during its substantive initial pass, then read the additional source checks and challenged its recommendations. Staging and run logs: `D:/dev/_scratch/grok-game-design-2026-11-10/`.

Grok used the existing subscription connection. Two initial attempts stopped on headless report-write permission before the substantive review; the completed passes were read-only and their returned text was saved by Codex. Native web search was unavailable to Grok. Codex performed live source searches and retrieved selected primary articles, then supplied those findings for the second pass. Neither agent audited entire official SMITE, League or Paragon source repositories. No reference-game assets were imported and no credentials were inspected.

No human playtest was performed for this review. The proposed identity, roster, economy, targeting and kits need playtesting; an appealing design document is not evidence of an irresistible product.
