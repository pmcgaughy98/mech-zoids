# Gorilla ability indicators

**Current kit update:** `docs/plan/GORILLA_MERGED_KIT_2026_11_10.md` supersedes the original separate Grab/Drive slot mapping below. Slot 2 is now the Fault Line prototype; slot 3 automatically chains Drive into Grab Slam. Art/target selection and the real-match checks have been updated. Earlier video recordings remain historical snapshots.

Implemented in the real arena's `arena_gorilla_kit.gd`, with an isolated playable review in `tools/debug/gorilla_targeting_2026_11_10`. This is the first art and targeting pass, not a completed ability-VFX package.

## Research and design

SMITE is the primary feel reference; Paragon is secondary. [Geb's original Stone Shield](https://www.smitefire.com/smite/skill/stone-shield-245) targets Geb or an ally. The [Geb wiki](https://smite.fandom.com/wiki/Geb) describes resolving multiple recipients near the target area's center. The [official Geb reveal](https://www.youtube.com/watch?v=xfj6bEwn9CU) is a further visual reference located during research; it was not frame-analyzed for this implementation. No SMITE art or extracted assets are used.

[Riot's gameplay-clarity discussion](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/) and [VFX update process](https://www.leagueoflegends.com/en-us/news/dev/dev-behind-the-scenes-of-vfx-updates/) prioritize readable boundaries, accurate hitboxes and brightness proportional to gameplay importance. These inform the design, rather than importing League's camera or controls.

Gorilla translates the ally-or-self pattern into its own hex-cell language: a lime hex around the recipient's feet, inward chevrons, four silhouette brackets, and a floating shield crest containing one power cell. A faint segmented circle shows the existing six-meter shield range. Confirmation holds the recipient in pale light through windup; a brief expanding flash is driven by the actual shield-release signal. Orange is reserved for offensive selection and cage-panel ticks. Invalid shield selection uses a warm red crest and an explicit reason, not color alone.

## Player flow

- Press 1–4 to select an ability, then aim and left-click to commit. Right-click or Escape cancels. Selecting and cancelling spend no cooldown.
- Shield: hover an allied machine's body or feet. Aim at empty ground for an explicit SELF preview. It selects the aimed ally rather than the nearest one. Enemy units, minions and buildings are not shield recipients.
- An out-of-range or wall-blocked hovered ally remains visibly invalid; clicking does not silently redirect that cast to someone else. Confirmed recipient is locked through the 0.25-second release; death, interruption, lost line of sight or leaving range before release prevents application. The confirmed cast still spends its cooldown.
- Grab: the existing 70-degree half-angle / 1.6-meter edge-distance rule drives the selection. The short cone is the reach guide; target radius extends eligible center positions beyond its arc. Candidate is marked only if eligible and line of sight is clear. A whiff remains possible if the opponent moves before capture.
- Shield Drive: rails show the maximum shield-front footprint (1.28 m wide; 3.8 m travel plus the measured 1.29904 m front). This is labeled a maximum path. Actual walls, bodies, cages and first-hit collision can stop it early; this preview does not simulate the full future sweep.
- Ultimate: a 5.5-meter ring with ten orange panel ticks matches the current cage radius and panel count.

The confirmation click is consumed through mouse release so holding it cannot also trigger the basic-attack poll. The old placeholder floor aim marker hides during selection. Bots retain direct programmatic casts; the controller and its screen art are created for the local gorilla only. Model geometry, materials, animations, damage, movement speed and cooldown values are unchanged by this pass. Legacy `ApeKit` callers keep nearest-ally fallback when no recipient is supplied.

## Validation and review

`review.gd` passed 25 checks covering recipient selection, actual shield release timing, self cast, invalid range, cancellation, walls, recipient death/range loss, interruption, body hover, keyboard selection, held-click suppression, right-click cancellation and GUI priority. `match_check.gd` passed seven checks verifying the real arena installation, MatchDirector cooldown, real ally shield, suppression of normal attack polling and cleanup on machine swap. The recorded 30 FPS run passed its 24 then-current checks; the final headless 60 FPS run adds the GUI-priority case. Headless logs contain the environment's Windows certificate-store warning; the final native recording has no script errors.

Local recordings and results: `D:/dev/_scratch/gorilla/ability-indicators-2026-11-10/`. `indicators.mp4` shows all four previews in the industrial map from the current SMITE-style camera. `shield-hover.png` is a still. Use `tools/debug/gorilla_targeting_2026_11_10/launch-review.cmd` for an interactive target field; close other Godot games first.

Painted-art follow-up: `art/fx/gorilla/README.md` documents the generated eight-part reactor atlas and its integration into the actual release/contact/Drive/ultimate events. The floating shield crest now uses that artwork, and floor/impact/perimeter art shares the same visual language. See `painted-art.mp4` in the same local review directory. The public Instagram reference from Mech Hub was located and inspected during this follow-up.

Next artistic work: tune selected-ally silhouette treatment in dense fights and test the art over every arena floor and at small display sizes. Controller quick/instant-cast preferences and gamepad confirm/cancel are not implemented in this pass.
