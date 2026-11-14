# Kit and skill animations at 35 degrees: plan (animation lane, 2026-11-05)

**Superseded 2026-11-09.** Preston: "2D sprites are scrapped btw". Machines are now rigged 3D models (the
gorilla-3d and rhino-3d sessions). Nothing below gets built. What was packed by then stays in art/machines/.

Preston: "Do you have fennecs new attack animations? lets redo all / and just kit and skill animations in general".

## The rule that sets the order
`docs/plan/moba-kits.md`: no attack moves at 35 degrees get drawn for a machine until its kit is redone to the
power-theme rule (the animal gives the body and at most one trait; the rest of the kit comes from a power theme).
Only the fennec's kit is redone (portals, taken 2026-11-05). So the fennec goes first, and each other machine needs its
kit taken before its moves are drawn.

## Where each machine stands

Preston, later on 2026-11-05: "We are going to have to redo all animations for all who dont already have for 35
look". So every animation of every machine gets a 35-degree version. Moves that do not depend on a kit (idle, walk,
death) can go now; kit moves wait for each kit to be redone, or they would be drawn twice.

| Machine | 35-degree views | Idle | Walk | Death | Kit moves |
|---|---|---|---|---|---|
| Rhino | touch-up, kept | installed (matches the touch-up) | installed | low angle | low angle; kit predates the rule |
| Fennec | touch-up, kept | installed | installed (touched-up trot, "Install both") | installed (death35, front redrawn by the touch-up lane, "Install both") | cast installed, charge built; rift boom if he takes the 11-05 draft; the old sand and dig moves come out |
| Gorilla | touch-up, kept | built, not installed | walk lane, in progress | low angle | low angle; hex kit, his call whether it stands |
| Wolf | touch-up, kept | built, not installed | low angle | low angle | low angle; kit predates the rule |
| Hippo | shade1, kept | installed | none | none | none; kit predates the rule |
| Drone minion | yes | done | done | done | attack and hit done |
| Kangaroo | views_cam35 drawn, no APPROVED.txt | | | | |
| Pangolin, shoebill, lobster, falcon, squirrel, chameleon, hummingbird | not yet (fleet lane) | | | | |

Walks are the walk lane's (`docs/art/moba/walk/`).

## Two ways to make a move
- **Script-built from the approved views (free).** Body breath, ear stretch, glow recolour (`tools/art/build_idle35.py`,
  `tools/art/build_cast35.py`). Good for casts, charges, channels and holds. It cannot make a new limb pose, a lunge,
  a jump or a death.
- **Drawn by Codex at 35 degrees (Preston's plan usage, needs his yes per run).** Any new pose. Past runs:
  rhino walk at 35, 1 move in 5 views, 274,960 tokens with the leg cleanup; fennec set A at the low angle, 3 moves in
  3 views, 124,616; wolf se/ne trot, 116,093. Estimate at 35 degrees: 100k-280k tokens for one move in 5 views, about
  230k-400k for three moves in 5 views (a 3-view run plus an se/ne run), so 0.5M-0.8M for a machine with six drawn
  moves. Runs go through the token cap (`rhino_l/take-a/anim/walk35/codex_cap/`).

## Order
1. **Fennec, now.** The cast is installed; the charge loop is built (`anim/charge35/`) and waits for Preston's look.
   - The death is the paid run Preston approved ("Yes, run it"): run 1 took 106,847 tokens. An ear cleanup is running, capped so the total stays under 280k.
   - Rift boom (the old sonic boom's charge and blast at 35 degrees, energy from its emitters) is a second drawn move if he takes the 2026-11-05 kit draft in `moba-kits.md`. It is another 100k-280k tokens and needs its own yes.
2. **Kit-free moves for rhino, gorilla, wolf and hippo.**
   - Idles: the gorilla and wolf idles are built; installing them is free and is his call per machine.
   - Deaths: one Codex run each with the fennec's brief, once the fennec death passes. Expect about 110k-280k each (the fennec's run 1 plus cleanup), 0.45M-1.1M for the four. Each needs his yes.
   - Walks: the walk lane.
3. **Kits, then kit moves.** Draft power-theme kits one machine at a time as proposals in `moba-kits.md`, in this order: rhino, then the gorilla (or he keeps the hex kit), then wolf and hippo. For each taken kit:
   - build the free moves by script;
   - price the drawn moves and run Codex on his yes;
   - pack them with tilt and hand them to the game feel lane.
4. **Machines without 35-degree views** wait for the fleet lane. After that, each gets its idle (free), then its death and walk, then its kit.
