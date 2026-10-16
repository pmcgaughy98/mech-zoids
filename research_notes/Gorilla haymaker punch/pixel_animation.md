# Gorilla haymaker punch: how 2D and pixel animators make a fast arcing punch read

Date: 2026-10-15. Scope: structure only (poses, timing, effects). No art copied.
Tag key: **[SRC]** = read in a source this session, with the source named. **[GK]** = general
animation knowledge, not read in a source this session. Treat [GK] as a starting guess to test.

---

## 1. Why the current punch reads as a wrist flick (diagnosis)

- The fist only rotates on one axis around the shoulder while pointing down from the
  knuckle-walk stance. The fist path is short and stays low, so the silhouette barely changes.
  At about 150 px, a fist that moves less than two or three fist-widths reads as a twitch. [GK]
- Jonathan Cooper (Game Anim): speed is distance over time; a recoiled-to-outstretched punch
  over 2 frames reads faster than over 5. **[SRC: gameanim.com, 12 Principles in Video Games]**
  The flip side: if the distance is small, no amount of frame trimming makes it read as big.
- Same source: most actions follow arcs, and overlapping action means the head and torso lead
  while the bent arm drags behind and snaps forward just before impact. A common junior mistake
  is everything starting and arriving at once. **[SRC: gameanim.com]**
  The current punch has the arm moving alone, with no body lead and no drag.

**Fix in one line:** make the fist travel a big overhand arc (behind and above the shoulder,
over the top, down and forward into the target) while the torso rotates first and the arm
arrives last. That is a multi-axis shoulder move (raise, rotate, swing), not one hinge. [GK]

---

## 2. Frame counts and timing (question 1)

What the sources say:
- Sprite timing table: attack wind-up 1-2 frames at 60-80 ms, impact 1-2 frames held
  120-200 ms, recovery 1-2 frames at 80-100 ms. Example attack: anticipation 80 ms, launch 50 ms
  (possible smear), follow-through 100 ms, recovery 120 ms. Main rule: vary frame durations;
  even timing is the most common beginner mistake. **[SRC: sprite-ai.art, 12 principles for pixel sprites]**
  (A tooling vendor's guide, not a studio postmortem. Numbers agree with the other sources.)
- Little Nemo and Kudzu developer: with only 2 frames for an attack, use a slow-out so the
  attack itself feels quicker; one attack was built entirely from follow-through (first frame is
  the end of the swing, the rest is recovery as the trail fizzles), and 3 frames were cut off
  the end for the demo to make it faster. **[SRC: Game Developer, "12 principles for game animation"]**
- Hollow Knight basic attack: one frame of anticipation, instant recovery. Attack phase must be
  "instant" (a few frames), clear hit location, consistent direction. **[SRC: GDKeys, Anatomy of an Attack]**
- Anticipation for enemy attacks should be longer (telegraph); player attacks shorter.
  **[SRC: gameanim.com; GDKeys]** For a turn-based RPG battle clip there is no input lag
  concern, so anticipation can be generous and readable.

What that means for a 9-frame, 1.5 s clip:
- Spend frames on poses, not on even in-betweens. Roughly: 2-3 frames anticipation and leap,
  1-2 frames for the fast part (passing + smear), 1-2 frames contact and hold, 2-3 frames
  follow-through and settle. [GK, consistent with the SRC numbers above]
- The fast part is the shortest on screen (40-80 ms per frame). The wind-up top and the contact
  are the longest (150-250 ms). The ratio between the slowest and fastest frame should be around
  3x to 5x. [GK]

---

## 3. Poses that must exist (question 2)

Cooper: keyframes are where the acting lives and should have strong silhouettes; breakdowns
sit between them. **[SRC: Game Developer 12 principles]** For the arc to read, these key poses
must exist as their own sprite frames [GK, standard punch breakdown]:

1. **Anticipation crouch**: body low and compressed, punching fist lifting off the ground.
2. **Top of wind-up (hold)**: punching fist high and behind the head, elbow above shoulder,
   torso twisted away from the target, free arm planted and pushing. This is the single most
   important pose; it is the "telegraph" and sets up the arc. [GDKeys: anticipation must be a
   unique pose that hints at the attack, SRC]
3. **Passing position over the shoulder**: body already moving forward in the jump, fist at
   the top of its arc above the shoulder line. Body leads, arm drags. [gameanim.com overlap, SRC]
4. **Smear or trail**: fist between the passing position and contact (see section 4).
5. **Contact**: arm fully extended toward the target, fist at the hit point, torso rotated
   through, whole body stretched into one long diagonal line. Strike frame.
6. **Overshoot / hit pose**: fist a few pixels past contact or pressed in, body starting to
   squash as it lands. Optional if the hit hold covers it.
7. **Follow-through and settle**: fist down on the ground in front, body squashed, then head and
   back hardware arriving one frame late (overlap), then back toward knuckle stance.

Squash and stretch on a rigid mech: Cooper notes many engines cannot scale bones, so on
non-deformable rigs you get the effect by extending limbs to accentuate stretched poses.
**[SRC: gameanim.com]** For the gorilla: stretch = arm locked straight, body extended in the jump,
shoulders reaching; squash = landing crouch with knees and elbows bent, chest low. Optional true
squash: a 3-5 percent non-uniform scale on the whole armature for one frame each, which reads at
150 px without breaking "metal". [GK]

Overlapping action on the mech [GK, applied from gameanim.com overlap principle]:
- Free arm: pushes off on the wind-up, swings back as the punch arm swings forward (counter
  rotation), lands a frame after or before the body.
- Head: leads into the punch (looks at target from the wind-up), then snaps forward a frame
  after contact. Cooper notes the head snapping after the body stops is a real motion-capture
  trait. **[SRC: gameanim.com, arcs section]**
- Back hardware (vents, pipes, antenna, pack): one to two frames behind the torso. Lags up on
  the wind-up, lags back during the lunge, swings forward on contact, settles last.

---

## 4. Smear and motion-trail frames, and how to make one from a 3D render (question 3)

What the sources say:
- Smears combine the visual information of several frames into one stretched mass, build smooth
  motion from fewer drawings, and can look rough alone but read well in motion.
  **[SRC: Game Developer 12 principles, Little Nemo Bridge Guardian]**
- Two smear types: elongated in-between (one stretched drawing between extremes) and multiples
  (several copies of the object along the path). In 3D, animators deform the mesh or rig,
  duplicate it along the arc, and use motion blur. **[SRC: RebusFarm smear frames guide]**
- Leave spacing between the smear and each extreme because of acceleration and deceleration;
  trails follow the motion path. **[SRC: Clip Studio TIPS, motion blur and smearing]**
- Guilty Gear Xrd style: the 3D game animates frame by frame with model swaps and per-frame
  control. **[SRC: Ben Golus post, search excerpt only]** The GDC 2015 talk by Junya Motomura
  covers this; it was not watched this session. Details such as stepped keys and per-frame
  deformation are [GK].
- Saint11 (Pedro Medeiros) has a dedicated "Motion blur / slash" tutorial, an "Impact" tutorial,
  an "Attack sheet" and "Squash" tutorial on saint11.art. They are image-only and were not read
  this session. **[SRC: only the index page was read; content is GK until viewed]**

Ways to build the smear frame from the Blender gorilla (ranked by how well they survive
pixelization) [GK]:
1. **Bone stretch for one frame**: on the smear frame only, scale the forearm and fist bones
   along the motion direction (about 1.4x to 1.8x) and rotate slightly ahead along the arc.
   One rendered frame, crisp edges, pixelizes cleanly. Closest to the Xrd approach.
2. **Multiples composite**: render the arm at 2-3 subframes along the arc (for example the
   frames between passing and contact), stack them with the front one opaque and the back ones
   at decreasing opacity, then quantize to the sprite palette. Risk: alpha blending creates mud
   colors at 150 px; fix by quantizing after the blend and using 1-2 light trail colors only.
3. **Trail sprite in Godot**: keep the arm render clean and draw a separate arc swoosh sprite
   (orange and white, the fist colors) along the fist path for the smear and contact frames.
   Easiest to iterate, works for any mech. Can fade over the next frame like the Nemo trail.
4. **Render motion blur**: Blender motion blur on the arm only, then pixelize. Usually turns to
   noise after downscale; least reliable. Use only as a reference for where to paint.

Recommendation: 1 or 3, or both (stretched fist plus a 2-color arc trail).

---

## 5. Selling the impact (question 4)

What the sources say:
- Hitstop: both attacker and target freeze briefly on hit. Longer for more damage, with a cap.
  **[SRC: Sakurai, Famitsu column 490-491, via Source Gaming]**
- Damage vibration: in sprite games the hit character vibrates during hitstop. Sakurai also
  shakes the attacker slightly; grounded characters shake side to side, airborne up and down;
  the shake starts large and decays across the hitstop. The attacker can creep forward very
  slightly during hitstop. **[SRC: Sakurai column]**
- Capcom beat em ups measured: Final Fight uses 6 frames of hitstop on every hit (60 fps,
  about 100 ms). The Punisher scales by move: jab 6, cross 8, combo ender 9, air attack 10
  frames on the attacker (100-167 ms), with the target frozen 2 frames longer than the attacker.
  Final Fight also shakes the hit sprite left and right during hitstop. Different hitstun poses
  (forward vs back) make the target react to the blow. **[SRC: Shane Sicienski, Hitstop in Capcom Beat Em Ups]**
- Impact frame "hangs" briefly at full extension; Dead Cells example. **[SRC: sprite-ai.art]**

For this game (it already flashes and pops the damage number on the strike frame):
- Make the strike frame itself the hitstop: hold it about 130-170 ms (8-10 frames at 60 fps,
  the heavy end of the Capcom range, since this is the gorilla's big hit).
- Shake the target, not the gorilla: 2-3 px horizontal, decaying (3, -2, 1, 0) over the hold.
  Optional 1 px on the gorilla. Grounded target = horizontal. [SRC rule, GK px values]
- Freeze the target's animation for the hold plus about 2 frames, then cut to its hit pose
  (back-leaning) and knockback. [SRC pattern from The Punisher numbers]
- Screen shake: small (2-4 px, 100-150 ms) and only on this heavy move, so it stays special. [GK]
- Keep the flash on the strike frame only; one frame of white on the target reads, longer
  washes out at 150 px. [GK]

---

## 6. Nine-frame keyframe plan (1.5 s total)

Assumes the existing jump/lunge stays and the arm is re-keyed on top of it. Source frame
numbers assume 36 frames at 24 fps (about 41.7 ms each); shift to match the real lunge timing.

| # | Phase | Pose | Duration | Source frame (approx) |
|---|-------|------|----------|------|
| 1 | Anticipation | Knuckle stance compressing: chest down, legs coiled, punching fist lifting off ground, free fist planted | 160 ms | 3-4 |
| 2 | Wind-up top (hold) | Leap starts. Punch fist cocked high behind head, elbow above shoulder, torso twisted away, head on target, back hardware lagging up | 240 ms | 9-10 |
| 3 | Lunge, arm dragging | Airborne, body travelling forward and rising, torso starting to unwind, fist still back (body leads, arm drags), free arm swinging back | 130 ms | 13-14 |
| 4 | Passing over shoulder | Near jump apex, fist at the top of the arc above the shoulder line, elbow bending forward, body stretched | 70 ms | 16-17 |
| 5 | Smear | Fist between apex and target: stretched forearm and/or 2-color arc trail along the path, body almost fully extended | 50 ms | 18-19 |
| 6 | Contact = strike frame (hitstop) | Arm straight down-forward into target, torso rotated through, body one long diagonal; flash, damage number, target shake here | 150 ms | 20-21 |
| 7 | Overshoot / land | Fist pressed a few px past contact or into ground, body squashing on landing, free arm landing, trail fading | 120 ms | 23-24 |
| 8 | Follow-through | Deep squash, head snaps forward a frame late, back hardware swings forward past rest | 200 ms | 27-28 |
| 9 | Settle | Rising back into knuckle stance, hardware settling last | 380 ms | 33-35 |

Total: 160 + 240 + 130 + 70 + 50 + 150 + 120 + 200 + 380 = 1500 ms.

Shares of clip: anticipation and wind-up 27 percent, lunge to contact (frames 3-5) 17 percent,
contact and land 18 percent, recovery 39 percent. If the recovery feels long, move 80-120 ms
from frame 9 into frame 2 (bigger telegraph) or frame 6 (heavier hitstop).

Checks to run on the rendered sprites [GK]:
- Fist path across frames 2-6 should cover at least 3-4 fist widths and visibly curve over the
  top. Plot the fist center per frame on one image; it should be an arc, not a line.
- Frames 2 and 6 silhouettes should be readable as black shapes alone.
- Fastest frame (5) to slowest frame (2 or 9) ratio around 1:5.

---

## Sources read this session

- Sakurai, "Thinking About Hitstop", Famitsu vol. 490-491, translated by Source Gaming:
  https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/
- Shane Sicienski, "Hitstop in Capcom Beat 'Em Ups":
  https://shane-sicienski.com/blog/blog-post-title-one-55pmn
- Jonathan Cooper, "The 12 Principles of Animation (In Video Games)", Game Anim book excerpt:
  https://www.gameanim.com/2019/05/15/the-12-principles-of-animation-in-video-games/
- "12 principles for game animation" (Little Nemo, Kudzu developer), Game Developer:
  https://www.gamedeveloper.com/game-platforms/12-principles-for-game-animation
- GDKeys, "Keys to Combat Design: Anatomy of an Attack":
  https://gdkeys.com/keys-to-combat-design-1-anatomy-of-an-attack/
- sprite-ai.art, "The 12 animation principles adapted for pixel art sprites" (vendor guide):
  https://www.sprite-ai.art/guides/animation-principles
- RebusFarm, smear frames guide: https://rebusfarm.net/blog/smear-frames-in-animation-how-animators-create-fast-and-dynamic-motion
- Clip Studio TIPS, motion blur and smearing: https://tips.clip-studio.com/en-us/articles/6170
- Saint11 tutorial index (titles only): https://saint11.art/blog/pixel-art-tutorials/
- Ben Golus post on Guilty Gear Xrd model swaps (search excerpt only):
  https://x.com/bgolus/status/1396740797970534402

Not read (worth a look if a second pass happens): Saint11 "Motion blur", "Impact", "Attack
sheet" and "Squash" tutorial images; Motomura GDC 2015 Xrd talk (gdcvault 1022031); New Frame
Plus "Animation of Guilty Gear Xrd and DBFZ" video; Animator's Survival Kit punch notes.
