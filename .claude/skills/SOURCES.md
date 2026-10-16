# Where these skills came from

Preston added these as skill-ups for synthesis on 2026-10-11. Claude read every file before installing. They are
plain-text guidance with no code that runs, no downloads and no hidden characters. The only change from upstream is
the `name:` line, which now carries a source prefix so generic names like "modeling" don't collide with other skills.

| Installed as | From | Licence |
|---|---|---|
| `claude-3d-harness` | github.com/MAX-786/claude-3d-harness | see its own folder; its Blender server is not set up |
| `atlas-modeling`, `atlas-texturing`, `atlas-rigging`, `atlas-animation`, `atlas-asset-optimization`, `atlas-blender` | github.com/MonumentalSystems/Atlas-Agent-Teams (teams/3d-design) | MIT |
| `atlas-godot` | github.com/MonumentalSystems/Atlas-Agent-Teams (teams/game-dev) | MIT |
| `dom-blender-3d-modeling`, `dom-blender-animation`, `dom-blender-scripting`, `dom-blender-render-automation` | github.com/Andrew1326/dominations (.claude/skills) | **none stated**: for our own use only, do not publish or redistribute |
| `blender-game-asset-artist` | github.com/badowhp/skill-mania, found through the claude-skill-registry index | see the repo's LICENSE.md |
| `game-3d-asset-design` | github.com/jeremylongworth-source/AgentSkills, found through the registry | MIT |
| `blender-export-pipeline` | github.com/arjun988/blender-skills (export-pipeline), found through the registry | MIT |

**Looked at and skipped:**
- **Jeffallan/claude-skills `game-developer`:** Unity, Unreal, C# and multiplayer; we use Godot and GDScript.
- **Atlas `engine-patterns` and `gamedev-conventions`:** generic team conventions.
- **dominations `blender-compositing`:** not needed for game assets.
- **phuetz/code-buddy:** nothing for 3D or games, and it carries test folders named "remote-pwn" and "godmode-lite".
- **majiayu000/claude-skill-registry:** an index of about 1,000 gaming skills, not skills itself. Its best matches are
  installed above. Its gaming list (`docs/categories/gaming/part-000.json`) is the place to look for more.
