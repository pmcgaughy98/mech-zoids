# Additional source checks by Codex, 2026-11-10

These are independent source checks, not a claim that Grok read the full sources. No external game assets or code were downloaded. Search results are excerpts unless marked full text. This file can support the review or a later verification pass.

## First-party design accounts

- Riot Scruffy, 2021-05-14, Champion Counterplay, full text retrieved: https://www.leagueoflegends.com/en-us/news/dev/quick-gameplay-thoughts-may-14/ . Distinguishes strategic strengths/weaknesses from tactical responses during combat. Use to test whether a kit has understandable enemy decisions, not just a weakness in a spreadsheet.
- Riot, Clarity in League, full text retrieved: https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/ . Recognizable silhouette, facing, hitbox/effect alignment and hierarchy of visual importance matter. Apply to center aiming and readable attack contact. Do not add ultimate-scale effects to every basic.
- Riot, Champion Insights: Sett, search excerpt: https://www.leagueoflegends.com/en-ph/news/dev/champion-insights-sett/ . Designer account identifies clarity, frustration and animation-resource costs of grappling opponents. Relevant to preserving our existing Grab Slam rather than adding many new carry/throw interactions across unready rigs.
- Steve Superville, Paragon creative director, Q&A, 2016-08-16, full interview retrieved: https://digitalchumps.com/2016/08/16/qanda-with-paragon-creative-director-steve-superville/ . Direct developer account of third-person targeting/action and MOBA strategy; historical intent, not proof of product success.
- Steve Superville interview, search excerpt: https://www.tentonhammer.com/articles/paragon-an-interview-with-creative-director-steve-superville . Kit-first hero design and the tactile purpose of third-person perspective. Interview transcript is first-person evidence, the outlet's commentary is secondary.
- Riot, 2026 season gameplay preview, search excerpt: https://www.leagueoflegends.com/en-us/news/dev/dev-2026-season-one-gameplay-preview/ . Immediate visible value can make vision systems easier to learn. Relevant to camp/objective readability, not a reason to inherit its map.

## Public data/repo boundaries

- Riot Developer Portal, Data Dragon, search excerpt verified: https://developer.riotgames.com/docs/lol . Official champion/item/static-data distribution, not complete gameplay source. Versions can lag releases. Inspect small selected descriptions when needed, not a wholesale asset bundle.
- CommunityDragon's own documentation, search excerpt: https://communitydragon.org/docs/assets . Community-generated convenient data from Riot files; not identical to first-party game source. No assets imported.
- Hi-Rez official SMITE API guide, search excerpt: https://webcdn.hirezstudios.com/hirez-studios/legal/smite-api-developer-guide.pdf . API documentation exists but requires approved developer credentials. Do not create sessions or read user credentials. An API wrapper repo is not SMITE source code.
- https://github.com/BartekZawadzki/TartarusArena . Existing local review is the evidence already inspected. AI-built Unreal prototype, not Epic's official Paragon source or a shipped-human-game authority.
- Epic developer-authored Paragon bot chapters surfaced in search: https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter24_Being_Where_It_Counts_Telling_Paragon_Bots_Where_to_Go.pdf and https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter32_Paragon_Bots_A_Bag_of_Tricks.pdf . Search excerpts only; useful primary architecture leads, not full chapters read.

## Firsthand player accounts, qualitative only

- https://www.reddit.com/r/Smite/comments/1vo0qmf/janus_abilities_firing_time_change_ob41/ . Search excerpt of a player reporting that changed portal activation timing disrupted their practiced escape inputs. Version-specific report; not independently reproduced. Lesson to investigate: input timing consistency and reliable placement.
- https://www.reddit.com/r/Smite/comments/189cqh7/ . Search excerpts of multiple participants disagreeing about Janus difficulty and frustration. One describes the combination of mobility and damage as the frustration; another reports portal-placement bugs. Full page retrieval failed. Use as hypotheses for counterplay/reliability tests, not evidence of current balance or consensus.
- https://www.reddit.com/r/PredecessorGame/comments/148jd7o/ . Search excerpt of a former Paragon/new Predecessor player asking how items work; replies discuss auto-buy/counterbuilding. Hypothesis: small understandable purchase decisions and optional guidance may serve onboarding better than a large unexplained store.
- https://www.reddit.com/r/PredecessorGame/comments/1cf12u0/ . Search excerpts of players enjoying match length while still reaching late builds. Historical anecdotes, not a target-duration measurement or representative survey.

Full-page retrieval of the SMITE wiki and some Reddit/League wiki pages failed in this environment; this is not license or access evidence, merely a retrieval limitation. Primary designer principles plus current-game playtests should carry more weight than forum balance claims.
