# TartarusArena: source review for our mech MOBA

Reviewed 2026-11-08 at Preston's request: https://github.com/BartekZawadzki/TartarusArena . Read public source through the connected GitHub reader; no clone, installation, engine execution, asset download or gameplay changes. This is an AI-built Unreal prototype and an engineering case study, not a shipped human-made synthesis reference. Its claimed play quality is not independently established here.

## Assessment

High usefulness for combat integration, animation transitions, test-room design and bot decision structure. Limited direct usefulness for authoring, rigging or retargeting new mech motion. Our project is Godot/GDScript; this project is Unreal/C++ with GAS and Epic animation packs. Study mechanisms and write project-specific implementations. Preserve Preston's kit ownership and decisions.

| Area | What was actually read | Useful lesson / limit |
|---|---|---|
| Attack resolution | `Source/ParagonArena/Abilities/ArenaAbility.cpp`, particularly activation/ResolveHit | Separate cast acceptance, resource commit, animation start, delayed hit resolution and aim handling. Recheck targets as the hit resolves and prevent repeat hits. Uses configured delays; it is not automatically perfect animation-notify synchronization. |
| Hit feedback | `Heroes/ArenaCharacter.cpp`, damage feedback, HitStop, PlayHitReact | Scale feedback by impact and prevent a stream of small hits from constantly freezing characters. Directional reactions are throttled and cannot overwrite important actions. |
| Animation transitions | `Heroes/ArenaPoseBlendInstance.cpp`, Character::PlaySingleNode | Capture the outgoing pose and blend into death/other sequences to prevent pose pops. This assumes compatible existing animation clips and skeletons; it does not author a gorilla walk. |
| Locomotion | Character::UpdateFacing, `Game/ArenaLocoLab.cpp`, QA v19 | Test forward/strafe/backward/stop separately. Its orient-to-movement solution compensates for forward-only pack jogs; do not inherit that control compromise without deciding our own desired mech strafe behavior. |
| Bot behavior | `AI/ArenaBotBrain.h`, QA v19 | Explicit decisions for spacing, melee contact, retreats, targets and aim lead; difficulty can improve decisions without perfect aim. Our current MatchBot already has lane/home behavior and per-kit plans, so compare gaps first. |
| Action prototype | `Proto/ProtoCharacter.cpp`, QA v21 | Explicit hit/cancel times, queued combos and short action buffers. This is a separate action prototype, not proof that every mechanic belongs in our MOBA. |
| QA | `Game/ArenaAnimLab.cpp`, `docs/TESTING.md` | Script real attacks/reactions/deaths and record frames, pose/floor measurements and failure conditions. Seed bot matches; test actual gameplay flows and packaged behavior. Passing counters alone cannot establish visual quality. |
| Portraits/icons | `UI/ArenaIconStudio.cpp` | Render portraits and ability poses from the same character assets, with controlled cameras, lighting and render-target sizes. Useful adjacent reference for our new Portrait Forge chat; not a replacement or authorization to contact it. |

## Compare with our existing code

Read `scripts/moba3d/kit_feel.gd`, the gorilla basic attack in `ape_kit.gd`, shared `match_director.gd` gates, `machine_test_player.gd` and `match_bot.gd`, plus the Game Feel lane status. We already have attacker lunge, target shove, sparks, directional camera kick, contact-frame holds/hit-stop, hit cues and move/ability cancellation of the gorilla backswing. Avoid presenting these as absent. The stronger opportunity is a consistent contract across kits and across the transition from sprites to skeletal models.

## First useful slice, proposed only

One current mech basic attack in a small real-game test: explicit wind-up, contact and recovery; damage, sound and VFX aligned to the same contact event; documented movement/ability cancellation boundaries; miss, stun, death and interrupted-attack cases; return to locomotion without a pose pop. Compare inspected video before and after. Keep numbers as proposals and preserve existing kit mechanics. This does not require copying Unreal code or introducing a framework as large as GAS.

## Limits

The README identifies Paragon models, animations and voices as external packs, excluded from the repository. It cannot supply missing custom-mech animation or repair generated eyes, extra limbs, weights or skeletons. `docs/BUILT-WITH-CLAUDE.md` explicitly leaves fun/feel/art-direction judgment to the human; its reported LAN tests were host/guest on one PC and its balance measurements use bots. No independent playtest or build was performed in this review.

## Sources read

- [README](https://github.com/BartekZawadzki/TartarusArena/blob/main/README.md)
- [Ability resolution](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Abilities/ArenaAbility.cpp)
- [Character feedback and transitions](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Heroes/ArenaCharacter.cpp)
- [Pose blending](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Heroes/ArenaPoseBlendInstance.cpp)
- [Bot decisions](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/AI/ArenaBotBrain.h)
- [Action prototype](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Proto/ProtoCharacter.cpp)
- [Animation lab](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Game/ArenaAnimLab.cpp)
- [Locomotion lab](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/Game/ArenaLocoLab.cpp)
- [Icon studio](https://github.com/BartekZawadzki/TartarusArena/blob/main/Source/ParagonArena/UI/ArenaIconStudio.cpp)
- [Testing guide](https://github.com/BartekZawadzki/TartarusArena/blob/main/docs/TESTING.md)
- [QA v8](https://github.com/BartekZawadzki/TartarusArena/blob/main/docs/dark-factory/13-qa-v8-feel-death-camera-env.md), [QA v19](https://github.com/BartekZawadzki/TartarusArena/blob/main/docs/dark-factory/20-qa-v19-relaxed-idle-ui-style-bot-decisions.md), [QA v21](https://github.com/BartekZawadzki/TartarusArena/blob/main/docs/dark-factory/22-qa-v21-melee-balance-proto-combat.md)
- [Author's evidence and limitations](https://github.com/BartekZawadzki/TartarusArena/blob/main/docs/BUILT-WITH-CLAUDE.md)
