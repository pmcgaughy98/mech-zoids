# Open mid / jungle boss approaches

Preston likes the revised layout and asks for the boss placement to take its structural cue from SMITE: specifically fix beetle and wyvern being closed off from mid and jungle. This revision keeps **gold beetle (-34,0)** and **wyvern (34,0)** in place inside the outer lanes. It changes their access and facing, not the broader map arrangement.

Both full-ring enclosures are now open half-bowls. Their **mid/jungle-facing halves are open**, with the backing walls toward the outer lanes retained. Removed the long barriers directly between mid and the bosses. Added a broad 12 m marked mid approach and two diagonal jungle approaches per boss. The north/south jungle paths connect around the capped wall groups. Both models face the inward opening. Camp loops, home service roads, lane layout, source models and shared gameplay/camera remain intact.

## Reference read and boundary

Read Batectazo's historical [Dignitas Conquest warding guide, October 2018](https://dignitas.gg/articles/conquest-warding-a-smite-guide), particularly mid's multiple jungle exits, Oracles in front of Gold Fury and the solo-side route near Fire Giant. This is a player's original tactical guide, not a current official map specification. It supports interconnected objective approaches; our half-bowl geometry and opening dimensions are our own inference and implementation. Read the [SCAN support guide](https://www.scan.co.uk/info/guide/smite-supportmindset) for how mid/Gold Fury-side fights and support rotations connect. Neither guide's old stats or item rules were adopted.

Also inspected the existing local SMITE gameplay frame `D:/dev/_scratch/camera-lane/smite1/grid/f_1200.png` for player-view terrain/route context. Attempts to fetch the guide's full-size diagrams failed; they were not represented as measured diagrams. No exact SMITE pit angle, clearance or travel time is claimed. No extracted SMITE files or assets were copied into the game, and no paid tools or new art generation were used.

## Verification

Review explicitly checks **clear sight and collision-safe paths from mid into each opening**, both north/south jungle approaches, both teams' paths to all three entry markers, every cross-objective entry pairing, court placement inside the outer lanes, current combat/camera/HUD and module presence. These replace the obsolete assertion that bosses must be screened from mid.

Native screenshots, `native-review.json`, `layout-board.png`, `native-runtime.log` and the actual-player `walkthrough.mp4` / `walkthrough-checks.json` live beside this document. The walkthrough enters beetle from the north jungle, leaves through the broad mid opening, then cuts explicitly to wyvern. Both models remain placement previews without encounters or rewards. Launch `scenes/map5v5/foundation.tscn` or `tools/map5v5/launch_foundation.ps1`.

Final result: **142 native checks passed, zero failures; 6/6 real walking checkpoints passed**. Inspected both boss approach screenshots, actual overhead, generated board and frames from the encoded walkthrough. Source rigs/art and shared gameplay/camera were not modified. Existing Windows certificate-store startup and two texture-release exit diagnostics are recorded in the runtime log; no final script errors.
