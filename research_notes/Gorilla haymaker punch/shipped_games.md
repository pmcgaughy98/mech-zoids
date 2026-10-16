# Gorilla haymaker punch: how shipped games stage a heavy wind-up punch

Date: 2026-10-15. Scope: copy STRUCTURE only (timing ratios, pose order, holds). No art copied.
Tags: [SRC] = read in a source this session. [GK] = general knowledge, not read in a source.

## 1. Frame data read this session (all games run at 60 fps)

| Move | Startup | Active | Recovery | Total | Hit lands at | Source |
|---|---|---|---|---|---|---|
| SF3 Hugo 5HP (overhead) | 16 | 7 | 15 | 38 | 42% | SuperCombo |
| SF3 Hugo Giant Palm Bomber HP | 22 | 2 | 6 | 30 | 73% | SuperCombo |
| SF6 Zangief 5[HP] held (gains 1 armor hit) | 32 | 3 | 22(24) | 57 | 56% | SuperCombo |
| SF6 Zangief 5HP tap | listed as "(6~22)+10", unclear formatting | 3 | 22(24) | ? | ? | SuperCombo |
| GGST Potemkin 6H | 23 | 7 | 35 | 64 | 36% | Dustloop |
| GGST Potemkin 5D charged (overhead) | 28 | 8 | 21 | 56 | 50% | Dustloop |
| GGST Potemkin 5D tap | 20 | 8 | 21 | 48 | 42% | Dustloop |
| GGST Potemkin Hammer Fall (lunge) | 18~37 | 2 | 34 | 53-73 | n/a | Dustloop |
| SSBU DK Giant Punch, no charge | hits 19-20 | 2 | rest | 62 | 31% | Dragdown, UFD |
| SSBU DK Giant Punch, max charge | hits 19-20 after charge | 2 | rest | 47 | ~40% | Dragdown |
| SSBU DK forward smash | hits 22-23 | 2 | rest | 54 | 41% | Dragdown |

Math, hit-lands share = startup / total. Ranges across the heavy moves:
- Wind-up (startup): 31% to 73% of the move. Uncharged heavies cluster at 31-42%; charged or "hold" versions at 50-56%.
- Active: tiny, 2 to 8 frames, so 3% to 18%. The swing itself is almost no time.
- Recovery: 20% to 66%. Heavies spend as long or longer recovering than winding up.

Staging notes from the same pages [SRC]:
- Potemkin 6H "moves Potemkin forward on frame 20 until recovery": the body lunge starts ~3 frames
  BEFORE the hit and carries through the active frames. The travel and the strike overlap.
- Potemkin Hammer Fall: a forward lunge with 1 hit of armor from frame 5 to 38, used to close distance.
- DK Giant Punch: "significant pullback hurtbox shifting on startup" (the body draws back before
  the punch); the arm is intangible frames 4-20 uncharged, full armor 9-20 at max charge.
- Hugo 5HP is described as an overhead with deceptive range that ground-slams airborne opponents.
- Zangief holding HP charges the punch and adds armor: longer wind-up is paid for with power.

## 2. How the animation is built (animator / thesis sources)

Guilty Gear Strive thesis (Uppsala, diva2:1769414) [SRC, via page summary]:
- Arc System Works uses "limited animation": few drawn poses, each held longer, no smooth
  inbetweens. Stronger poses, snappier moves. This is exactly the 9-sprite situation.
- Strong characters build anticipation by pulling the body back (charging), acrobatic ones by spinning.
- Ky holds his preparation pose for 9 of 11 anticipation frames: the wind-up is ONE held pose,
  not a slow drift.
- Hitstop: follow-through frame counts grow on hit. Potemkin 6H follow-through 5 frames on whiff vs
  19 on hit (+14 f = 0.23 s). Ky f.S 13 vs 25-26 (+12 f = 0.20 s). Chipp 6H 15 vs 29.
- Potemkin 6H: 14-frame anticipation, only 5 frames of arm deformation (smear) during the swing,
  31 frames of recovery, total 52 whiff / 67 hit. Heavies use few speed effects; impact is sold
  with a compact explosion, shockwave, background distortion and camera shake instead.

Slynyrd Pixelblog 9, melee attacks (32 px characters) [SRC]:
- Heavy = slower anticipation and recovery, "however the smear frames should always be few and fast."
  Usually one smear frame does it; the smear must follow the natural path from stance to follow-through.
- "Freeze time": hold the anticipation pose and sometimes the impact frame on strong collisions.
- Overshoot on the recovery frame (one frame shifted past rest, then settle).
- Exaggerate: lengthen the arm a little at max extent; realistic poses look stiff in pixels.
- A cross can include a step lunge.

GDKeys, Anatomy of an Attack (Nicolas Kraj) [SRC]:
- Reaction time ~0.25 s. Minimum readable anticipation = reaction time + defender's response time
  + buffer (their example: 18 frames at 30 fps = 0.6 s).
- Anticipation must be unique in shape and must hint at the attack that follows (axe drawn behind
  the body before a split). Attack itself should be near-instant with a clear hit location and a
  consistent direction.

Game Developer, 12 principles for game animation [SRC excerpt]: anticipation is vital for enemy
attacks; spend frames around key poses (slow in/out) so the eye lands on the silhouettes.

Overhand mechanics [SRC excerpt only, Heavybag Pro]: the overhand "isn't a straight punch, it's a
curve over the guard", drilled by looping the hand over a bar on the shoulder. Everything else in
section 3 about the body is [GK].

## 3. Answers to the four questions

### (1) Fist path
- Start: off the ground, swung BACK and UP so the fist sits behind and above the shoulder, at or
  above head height, elbow high and bent ~90 degrees pointing back. [GK for the exact angle]
- Arc: a loop over the top of the shoulder, forward and DOWN onto the target, like a hammer or
  overhand. It is a curve, not a straight line or a forward flick. [SRC excerpt + GK]
- End: past the target, continuing down toward the ground in front (the gorilla can finish
  knuckles-down, which fits the knuckle-walk stance and makes the return cheap). [GK]
- Fist orientation: knuckles must face the target at contact. The current clip fails because the
  fist still points down from the stance and only the upper arm rotates on one axis. Fix with
  wrist/forearm rotation during the wind-up so the knuckles lead. [GK]

### (2) Body in each phase [GK unless marked]
- Anticipation: weight drops back onto hind legs, torso yaws AWAY from the target (striking shoulder
  goes back), chest opens, punching arm rises up and back. The planted fist stays down as a brace.
  Matches "strong characters pull the body back" [SRC thesis] and DK's pullback [SRC].
- Launch: hind legs extend, body leaves the ground. Keep the fist cocked high during takeoff so the
  threat pose stays readable while the body travels.
- Swing: torso yaws hard TOWARD the target, shoulder drives forward and over, elbow leads, forearm
  whips through last (overlapping action, shoulder then elbow then fist). The lunge and the swing
  overlap, as with Potemkin 6H moving forward from frame 20 into active [SRC].
- Impact: arm fully extended forward-down, slightly overlong (exaggeration [SRC Slynyrd]), body at
  the end of the lunge, the off fist reaching for the ground.
- Follow-through: fist keeps going down, front lands, small overshoot.
- Recovery: settle back to the knuckle-walk stance, held long enough to read the weight.

### (3) Timing
- Wind-up: 31-56% of the move in shipped heavies [SRC]. Pick ~40% for a jump plus swing.
- Swing: 1 smear frame, fast [SRC Slynyrd, thesis]. Active 2-8 frames of 60 [SRC].
- Impact hold / hitstop: 0.15-0.23 s added on hit [SRC thesis numbers]. Since the strike frame
  fires the flash and damage number, give it the long duration.
- Recovery plus follow-through: 35-66% [SRC]. Pick ~45%.

### (4) Reading at small sizes
- Limited animation with held key poses is the norm even at full HD in Strive [SRC]; at 150 px it is
  mandatory.
- One smear frame, few and fast [SRC]. Hold the wind-up pose and the impact pose [SRC].
- The wind-up fist must break the silhouette above the head/back line; a fist inside the body
  outline disappears at 150 px. Use the near arm (the side turned 20 degrees toward the camera) so
  the body does not hide it. [GK]
- Sell impact with flash, shockwave, screen shake, not with extra arm frames [SRC thesis on Potemkin].

## 4. Keyframe plan for the 1.5 s clip (36 source frames at 24 fps, 9 sprites)

| # | Phase | Pose | Duration | Source frame | Share |
|---|---|---|---|---|---|
| 1 | Stance / settle | knuckle stance, slight dip | 0.10 s | 0 | 7% |
| 2 | Anticipation start | punching fist lifts off, swings back; hips drop | 0.12 s | 2-3 | 8% |
| 3 | Wind-up TOP, held | fist behind and above shoulder, elbow high, torso yawed away, weight on hind legs, off fist planted | 0.25 s | 6 | 17% |
| 4 | Launch | hind legs extend, body airborne, fist still cocked high | 0.10 s | 12 | 7% |
| 5 | Swing smear | fist arcing over the top, arm stretched, torso yawing toward target | 0.06 s | 14-15 | 4% |
| 6 | STRIKE (flash, damage) | arm extended forward-down, knuckles to target, body at end of lunge | 0.17 s | 16-17 | 11% |
| 7 | Follow-through | fist past target down toward ground, front landing, overshoot | 0.12 s | 20-21 | 8% |
| 8 | Recovery | body low, both fists down, weight settling | 0.25 s | 25 | 17% |
| 9 | Return | knuckle stance | 0.33 s | 31-35 | 22% |

Sum: 0.10+0.12+0.25+0.10+0.06+0.17+0.12+0.25+0.33 = 1.50 s.
Strike lands at 0.10+0.12+0.25+0.10+0.06 = 0.63 s = 42% of the clip (inside the 31-56% shipped range).
Wind-up before launch 0.47 s (above the 0.25 s reaction floor). Recovery after strike 0.70 s = 47%.

If the existing lunge peaks at a different source frame, keep the RATIOS and move the strike to
the last frame before the front lands; the swing should start no later than the jump apex.

## 5. Not covered, not verified
- Tekken Kuma / Jack, Super Robot Wars rocket punches, Monster Hunter Rajang, Zoids: not read.
- Abigail (SFV) not read.
- No video was watched; pose descriptions of these moves are inferred, not observed.
- Zangief 5HP tap startup string "(6~22)+10" was garbled in the extraction.

## Sources
- https://wiki.supercombo.gg/w/Street_Fighter_3:_3rd_Strike/Hugo
- https://wiki.supercombo.gg/w/Street_Fighter_6/Zangief
- https://www.dustloop.com/w/GGST/Potemkin
- https://dragdown.wiki/wiki/SSBU/Donkey_Kong
- https://ultimateframedata.com/donkey_kong
- https://uu.diva-portal.org/smash/get/diva2:1769414/FULLTEXT01.pdf
- https://www.slynyrd.com/blog/2018/9/8/pixelblog-9-melee-attacks
- https://gdkeys.com/keys-to-combat-design-1-anatomy-of-an-attack/
- https://www.gamedeveloper.com/game-platforms/12-principles-for-game-animation (search excerpt)
- Heavybag Pro overhand drill (Facebook search excerpt only)
