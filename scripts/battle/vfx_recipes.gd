extends RefCounted
## Which effects each weapon plays, and when (Claude, 2026-10-15). scripts/battle/vfx.gd draws them; battle.gd looks a
## recipe up by "<machine>/<clip>", falling back to the weapon's type (melee, shell, beam, missile) for machines without
## their own. Zoids Legacy keeps a data record per weapon (the attack, then the impact) that points into its shared
## effect library; the Pokemon GBA games script each move as timed calls into theirs. Same idea, our own pieces.
##
## A recipe:
##   "cues":    effects timed by the attacker's clip: {"frame": k} plays as frame k starts ("t" adds seconds); no
##              frame means the strike frame. "at" and "to" are anchors (vfx.gd anchor(): "contact", "target",
##              "target_front", "target_feet", "actor_feet", "actor_center", or {"of", "pt", "y", "frame", "dx", "dy"}).
##   "shot":    something that travels from "from" to "to", fired at its frame: a projectile ("time" in flight, "arc",
##              "style", "count" with "spread" and "stagger" for a volley, "bursts" and "gap" for an automatic), a beam
##              ("grow" until it reaches, "life" it holds), a ground "wave" or "sound" waves. "muzzle": its flash.
##              "land": what each pellet does where it lands.
##   "impact":  effects at the moment of contact (after the shot's flight); "t" delays one.
##   "advance": a melee blow carries the attacker across to the target ("go" and "back" frames, "depth" how far into
##              the target's lane it steps, "overlap" pixels past the target's edge, "lead" the band of the attacker's
##              height, as fractions from its top, whose frontmost point lands the blow; default [0, 0.8]).
##   "hitstop", "jolt", "knock", "shake", "white": the hit freeze (s), the target's own shake (px), how far it is knocked
##              back (art px), the screen shake (screen px, heavy blows only) and a white stage flash (strength).
##   "miss":    effects where a missed shot or blow lands (default: dust).
## Numbers are field units (art pixels) and seconds. Frames refer to the clips in art/machines/<id>/anim/anim.json; the
## five medium starters share one template (0-3 wind-up, 4-5 the snap and the strike, 6-8 recovery).

const MUZZLE_FLASH := {"fx": "star", "r": 6.0, "ramp": "fire"}

const BY_CLIP := {
	# Gorilla: a jumping haymaker on hydraulic-ram fists.
	"ape_l/punch": {
		"advance": true, "go": 2, "back": 7, "depth": 0.5,
		"cues": [
			{"frame": 2, "fx": "dust", "r": 4.5, "at": "actor_feet", "count": 6, "both": false, "speed": 45.0},   # the push-off
			{"frame": 3, "fx": "afterimage", "count": 2, "gap": 7.0, "color": "a8763e", "life": 0.2},
			{"frame": 7, "fx": "dust", "r": 4.5, "at": "actor_feet", "count": 5},   # the landing
		],
		"impact": [
			{"fx": "burst", "at": "contact", "r": 18.7},
			{"fx": "star", "at": "contact", "r": 15.0},
			{"fx": "sparks", "at": "contact", "count": 14},
			{"fx": "rings", "at": "contact", "count": 1, "r0": 4.0, "r1": 30.0, "life": 0.22},
			{"fx": "debris", "at": "contact", "count": 4},
		],
		"hitstop": 0.09, "jolt": 3.0, "knock": 14.0, "shake": 2.0,
	},
	# Tears a block off the ballast rack and hurls it in an arc.
	"ape_l/throw": {
		"cues": [
			{"frame": 1, "fx": "sparks", "at": {"of": "actor", "pt": "top", "frame": 1, "dy": 4}, "count": 10, "angle": -90.0, "spread": 50.0},
			{"frame": 1, "fx": "debris", "at": {"of": "actor", "pt": "top", "frame": 1, "dy": 4}, "count": 3, "speed": 50.0},
		],
		"shot": {"frame": 4, "fx": "projectile", "style": "block", "ramp": "steel", "time": 0.42, "arc": 34.0,
			"from": {"of": "actor", "pt": "top", "frame": 4, "dy": 3}, "to": "target"},
		"impact": [
			{"fx": "burst", "at": "target", "r": 17.0, "ramp": "dust"},
			{"fx": "debris", "at": "target", "count": 10, "speed": 110.0},
			{"fx": "dust", "r": 4.5, "at": "target_feet", "count": 7},
			{"fx": "sparks", "at": "target", "count": 12},
		],
		"hitstop": 0.08, "jolt": 3.0, "knock": 14.0, "shake": 3.0,
		"miss": [{"fx": "debris", "count": 6, "speed": 80.0}, {"fx": "dust", "r": 4.5, "count": 7}],
	},
	# Both fists into the ground; the shockwave runs to the target.
	"ape_l/slam": {
		"cues": [
			{"frame": 4, "fx": "dust", "at": "actor_feet", "dx": 30, "count": 10, "speed": 55.0, "r": 4.5},
			{"frame": 4, "fx": "debris", "at": "actor_feet", "dx": 30, "count": 8, "ramp": "dust"},
			{"frame": 4, "fx": "rings", "at": "actor_feet", "dx": 30, "count": 2, "r0": 6.0, "r1": 51.0, "squash": 0.25, "ramp": "dust"},
			{"frame": 4, "fx": "shake", "amp": 3.0, "life": 0.25},
		],
		"shot": {"frame": 4, "fx": "wave", "time": 0.32, "from": "actor_feet", "to": "target_feet"},
		"impact": [
			{"fx": "debris", "at": "target_feet", "count": 12, "speed": 130.0, "ramp": "dust"},
			{"fx": "dust", "at": "target_feet", "count": 10, "speed": 50.0, "r": 4.5},
			{"fx": "burst", "at": "target_low", "r": 20.4, "ramp": "dust", "squash": 0.6},
		],
		"hitstop": 0.1, "jolt": 4.0, "knock": 12.0, "shake": 4.0, "white": 0.25,
	},
	# Shoebill: the hooked bill clamps shut and twists.
	"shoebill_m/clamp": {
		"advance": true, "go": 3, "back": 7, "depth": 0.5,
		"impact": [
			{"fx": "star", "at": "contact", "r": 12.0},
			{"fx": "sparks", "at": "contact", "count": 12},
			{"fx": "slash", "at": "contact", "r": 10.5, "a0": -100.0, "a1": -10.0, "squash": 1.0, "w": 2},
			{"fx": "slash", "at": "contact", "r": 10.5, "a0": 100.0, "a1": 10.0, "squash": 1.0, "w": 2},
		],
		"hitstop": 0.07, "jolt": 2.0, "knock": 8.0,
	},
	# Bill Clatter (2026-10-19 pivot): the bill slams shut and open like machine-gun fire; three bursts from its tip.
	"shoebill_m/lance": {
		"shot": {"frame": 3, "fx": "projectile", "style": "pellet", "time": 0.14, "count": 4, "spread": 6.0, "stagger": 0.03,
			"bursts": 3, "gap": 0.09, "muzzle": {"fx": "star", "r": 5.0, "ramp": "fire"},
			"from": {"of": "actor", "pt": "front", "y": 0.3, "frame": 4}, "to": "target",
			"land": {"fx": "star", "r": 2.5}},
		"impact": [
			{"fx": "sparks", "at": "target", "count": 10},
			{"fx": "sparks", "at": "target", "count": 8, "t": 0.09},
			{"fx": "sparks", "at": "target", "count": 8, "t": 0.18},
		],
		"hitstop": 0.04, "jolt": 2.0, "knock": 8.0,
		"miss": [{"fx": "dust", "count": 6}],
	},
	# Sentry Lunge (2026-10-19 pivot): statue-still, then a ballistic lunge, bill first.
	"shoebill_m/buffet": {
		"advance": true, "go": 4, "back": 7, "depth": 0.5,
		"cues": [
			{"frame": 4, "fx": "speed_lines", "at": "actor_center", "h": 14.0, "count": 7},
			{"frame": 4, "fx": "dust", "r": 4.0, "at": "actor_feet", "count": 6, "speed": 50.0},
		],
		"impact": [
			{"fx": "star", "at": "contact", "r": 14.0},
			{"fx": "slash", "at": "contact", "r": 14.0, "a0": -30.0, "a1": 30.0, "squash": 0.6, "w": 3},
			{"fx": "sparks", "at": "contact", "count": 14},
		],
		"hitstop": 0.08, "jolt": 3.0, "knock": 14.0, "shake": 1.5,
	},

	# Pangolin: the heavy tail sweeps sideways; its scale edges are the blade.
	"pangolin_m/rake": {
		"advance": true, "go": 2, "back": 7, "depth": 0.5,
		"impact": [
			{"fx": "slash", "at": "contact", "r": 24.0, "a0": -110.0, "a1": 40.0, "squash": 0.5, "w": 3, "ramp": "ochre"},
			{"fx": "sparks", "at": "contact", "count": 13},
			{"fx": "star", "at": "contact", "r": 10.5},
		],
		"hitstop": 0.06, "jolt": 2.0, "knock": 10.0,
	},
	# Loose scale plates flicked off the back in a spread.
	"pangolin_m/shot": {
		"shot": {"frame": 4, "fx": "projectile", "style": "plate", "ramp": "ochre", "time": 0.3, "arc": 22.0,
			"count": 5, "spread": 14.0, "stagger": 0.08,
			"from": {"of": "actor", "pt": "top", "frame": 4, "dy": 4}, "to": "target",
			"land": {"fx": "star", "r": 4.0}},
		"impact": [
			{"fx": "sparks", "at": "target", "count": 14},
			{"fx": "debris", "at": "target", "count": 4, "ramp": "ochre"},
		],
		"hitstop": 0.05, "jolt": 2.0, "knock": 8.0,
		"miss": [{"fx": "dust", "r": 4.5, "count": 6}, {"fx": "debris", "count": 3, "ramp": "ochre"}],
	},
	# Curls into an armoured ball and rolls through the target.
	"pangolin_m/roll": {
		"advance": true, "go": 2, "back": 7, "depth": 0.6, "overlap": 6.0,
		"cues": [
			{"frame": 3, "fx": "afterimage", "count": 3, "gap": 9.0, "color": "da8600"},
			{"frame": 3, "fx": "dust", "r": 4.5, "at": "actor_feet", "count": 8, "both": false, "speed": 40.0},
			{"frame": 4, "fx": "speed_lines", "at": "actor_center", "h": 16.0},
		],
		"impact": [
			{"fx": "burst", "at": "contact", "r": 18.7},
			{"fx": "sparks", "at": "contact", "count": 16},
			{"fx": "debris", "at": "contact", "count": 6},
			{"fx": "dust", "r": 4.5, "at": "target_feet", "count": 8},
		],
		"hitstop": 0.09, "jolt": 3.0, "knock": 16.0, "shake": 3.0,
	},
	# Pygmy hippo: the jaw opens near flat and slams shut.
	"hippo_m/gape": {
		"advance": true, "go": 2, "back": 7, "depth": 0.5,
		"impact": [
			{"fx": "star", "at": "contact", "r": 13.5},
			{"fx": "burst", "at": "contact", "r": 15.3},
			{"fx": "sparks", "at": "contact", "count": 14},
		],
		"hitstop": 0.08, "jolt": 3.0, "knock": 10.0,
	},
	# Two water jets from valves above the snout, cutting like a beam.
	"hippo_m/jets": {
		"cues": [{"frame": 3, "fx": "spray", "at": {"of": "actor", "pt": "front", "y": 0.3, "frame": 3}, "count": 6, "speed": 40.0, "angle": -90.0}],
		"shot": {"frame": 4, "fx": "beam", "ramp": "water", "width": 4, "pair": 7.0, "wave": 1.0, "grow": 0.12, "life": 0.45, "dim": false, "glow": false,
			"from": {"of": "actor", "pt": "front", "y": 0.25, "frame": 4}, "to": "target"},
		"impact": [
			{"fx": "spray", "at": "target", "count": 16, "speed": 100.0, "spread": 80.0},
			{"fx": "rings", "at": "target", "count": 2, "r0": 3.0, "r1": 21.0, "ramp": "water"},
			{"fx": "smoke", "at": "target", "count": 3, "ramp": "water", "r": 3.0, "life": 0.5},
		],
		"hitstop": 0.05, "jolt": 2.0, "knock": 10.0,
		"miss": [{"fx": "spray", "count": 14, "angle": -90.0, "spread": 50.0}],
	},
	# Surges out of the water head first, pushing a wave ahead of it.
	"hippo_m/charge": {
		"advance": true, "go": 2, "back": 7, "depth": 0.6,
		"cues": [
			{"frame": 3, "fx": "spray", "at": "actor_feet", "count": 14, "speed": 70.0, "angle": -60.0},
			{"frame": 3, "fx": "afterimage", "count": 2, "gap": 9.0, "color": "8fd0f0"},
		],
		"impact": [
			{"fx": "spray", "at": "contact", "count": 22, "speed": 120.0, "spread": 70.0},
			{"fx": "burst", "at": "contact", "r": 18.7, "ramp": "water"},
			{"fx": "rings", "at": "target_feet", "count": 2, "r0": 6.0, "r1": 45.0, "squash": 0.3, "ramp": "water"},
		],
		"hitstop": 0.09, "jolt": 3.0, "knock": 16.0, "shake": 3.0,
	},
	# Red kangaroo: pneumatic fists fire a kinetic blast on contact, knocking the target back.
	"kangaroo_m/jab": {
		"advance": true, "go": 2, "back": 7, "depth": 0.5, "lead": [0.1, 0.6],   # the gloves, not the long feet
		"impact": [
			{"fx": "rings", "at": "contact", "count": 2, "r0": 3.0, "r1": 27.0, "life": 0.3, "gap": 0.06},
			{"fx": "burst", "at": "contact", "r": 13.6},
			{"fx": "sparks", "at": "contact", "count": 12},
			{"fx": "smoke", "at": "contact", "count": 2, "r": 3.0, "life": 0.45, "rise": 8.0, "ramp": "steel"},   # the piston's vent
		],
		"hitstop": 0.08, "jolt": 3.0, "knock": 18.0,
	},
	# Pouch Cannon (kangaroo p72, 2026-10-19): a pirate-style cannon swings out of a stomach hatch above the pouch and fires
	# one heavy iron ball on a low arc; a big flash and a cloud of powder smoke at the muzzle, a heavy hit.
	"kangaroo_m/flak": {
		"shot": {"frame": 4, "fx": "projectile", "style": "ball", "ramp": "steel", "time": 0.3, "arc": 5.0, "count": 1,
			"muzzle": {"fx": "star", "r": 10.0, "ramp": "fire"},
			"from": {"of": "actor", "pt": "front", "y": 0.55, "frame": 4}, "to": "target",
			"land": {"fx": "star", "r": 6.0}},
		"cues": [{"frame": 4, "fx": "smoke", "at": {"of": "actor", "pt": "front", "y": 0.55, "frame": 4, "dx": 4}, "count": 5, "r": 4.0, "life": 0.6, "rise": 6.0, "ramp": "steel"}],
		"impact": [
			{"fx": "sparks", "at": "target", "count": 16},
			{"fx": "smoke", "at": "target", "count": 3, "r": 3.5, "life": 0.5, "ramp": "steel"},
		],
		"hitstop": 0.08, "jolt": 3.5, "knock": 16.0,
	},
	# A jet-boosted leap off the tail, both feet first; the hip boosters fire on the way up.
	"kangaroo_m/kick": {
		"advance": true, "go": 2, "back": 7, "depth": 0.6, "lead": [0.3, 1.0],   # both feet first
		"cues": [
			{"frame": 2, "fx": "dust", "r": 4.5, "at": "actor_feet", "count": 8, "speed": 50.0},
			{"frame": 2, "fx": "flame", "at": {"of": "actor", "pt": "back", "y": 0.6, "frame": 2}, "angle": 120.0, "life": 0.18},
			{"frame": 3, "fx": "flame", "at": {"of": "actor", "pt": "back", "y": 0.6, "frame": 3}, "angle": 135.0, "life": 0.25, "length": 9.0},
			{"frame": 3, "fx": "afterimage", "count": 2, "gap": 8.0, "color": "e6724c"},
			{"frame": 8, "fx": "dust", "r": 4.5, "at": "actor_feet", "count": 6},
		],
		"impact": [
			{"fx": "burst", "at": "contact", "r": 18.7},
			{"fx": "star", "at": "contact", "r": 15.0},
			{"fx": "sparks", "at": "contact", "count": 16},
			{"fx": "rings", "at": "contact", "count": 1, "r0": 4.0, "r1": 33.0},
			{"fx": "debris", "at": "contact", "count": 5},
		],
		"hitstop": 0.1, "jolt": 4.0, "knock": 18.0, "shake": 3.0,
	},
	# Black wolf: the jaw, blood-red fangs, a lunge and bite.
	"wolf_m/lunge": {
		"advance": true, "go": 2, "back": 7, "depth": 0.5,
		"cues": [{"frame": 4, "fx": "afterimage", "count": 2, "gap": 8.0, "color": "b3131a"}],
		"impact": [
			{"fx": "slash", "at": "contact", "r": 12.0, "a0": -110.0, "a1": -20.0, "squash": 1.0, "w": 2, "ramp": "red"},
			{"fx": "slash", "at": "contact", "r": 12.0, "a0": 110.0, "a1": 20.0, "squash": 1.0, "w": 2, "ramp": "red"},
			{"fx": "sparks", "at": "contact", "count": 12},
			{"fx": "star", "at": "contact", "r": 9.0},
		],
		"hitstop": 0.07, "jolt": 2.0, "knock": 10.0,
	},
	# A red-grilled emitter in the throat: a concussive howl.
	"wolf_m/howl": {
		"cues": [{"frame": 2, "fx": "charge_in", "at": {"of": "actor", "pt": "front", "y": 0.2, "frame": 3}, "r": 18.0, "count": 10, "life": 0.4, "ramp": "red"}],
		"shot": {"frame": 4, "fx": "sound", "time": 0.28, "count": 5, "gap": 0.05, "ramp": "red", "r0": 6.0, "r1": 22.0,
			"from": {"of": "actor", "pt": "front", "y": 0.2, "frame": 4}, "to": "target"},
		"impact": [
			{"fx": "rings", "at": "target", "count": 3, "r0": 4.0, "r1": 33.0, "ramp": "red", "gap": 0.05, "glow": true},
			{"fx": "burst", "at": "target", "r": 11.9, "ramp": "red"},
		],
		"hitstop": 0.06, "jolt": 4.0, "knock": 10.0, "shake": 2.0,
	},
	# The shoulder and hip blade fins: a full-speed pass through the target.
	"wolf_m/dash": {
		"advance": true, "go": 2, "back": 7, "depth": 0.6, "overlap": 10.0,
		"cues": [
			{"frame": 3, "fx": "afterimage", "count": 4, "gap": 10.0, "color": "5a0a0e"},
			{"frame": 3, "fx": "speed_lines", "at": "actor_center", "h": 16.0, "count": 8},
		],
		"impact": [
			{"fx": "streak", "at": "contact", "length": 57.2, "ramp": "red"},
			{"fx": "streak", "at": "contact", "dy": 6, "length": 39.0, "tilt": 0.15, "t": 0.04},
			{"fx": "sparks", "at": "contact", "count": 16},
		],
		"hitstop": 0.08, "jolt": 3.0, "knock": 12.0, "shake": 2.0,
	},
}

## Machines without their own recipe (the older drawn ones) play their weapon type's.
const BY_TYPE := {
	"melee": {
		"impact": [
			{"fx": "burst", "at": "target_front", "r": 13.6},
			{"fx": "star", "at": "target_front", "r": 10.5},
			{"fx": "sparks", "at": "target_front", "count": 12},
		],
		"hitstop": 0.07, "jolt": 2.0, "knock": 8.0,
	},
	"shell": {
		"shot": {"fx": "projectile", "style": "pellet", "time": 0.22, "muzzle": MUZZLE_FLASH, "t": -0.1,
			"from": {"of": "actor", "pt": "front", "y": 0.4}, "to": "target"},
		"impact": [
			{"fx": "explosion", "at": "target", "r": 12.8, "life": 0.5},
			{"fx": "sparks", "at": "target", "count": 10},
		],
		"hitstop": 0.05, "jolt": 2.0, "knock": 8.0,
	},
	"missile": {
		"shot": {"fx": "projectile", "style": "missile", "ramp": "steel", "time": 0.4, "arc": 26.0, "count": 2, "spread": 8.0,
			"stagger": 0.12, "t": -0.1, "from": {"of": "actor", "pt": "top"}, "to": "target"},
		"impact": [
			{"fx": "explosion", "at": "target", "r": 17.6},
			{"fx": "explosion", "at": "target", "r": 12.8, "dx": -6, "dy": -5, "t": 0.12},
		],
		"hitstop": 0.06, "jolt": 3.0, "knock": 10.0, "shake": 2.0,
	},
	"beam": {
		"shot": {"fx": "beam", "ramp": "cyan", "width": 4, "grow": 0.1, "life": 0.4, "t": -0.1,
			"from": {"of": "actor", "pt": "front", "y": 0.35}, "to": "target"},
		"impact": [
			{"fx": "burst", "at": "target", "r": 13.6, "ramp": "cyan"},
			{"fx": "sparks", "at": "target", "count": 12, "ramp": "cyan"},
		],
		"hitstop": 0.05, "jolt": 2.0, "knock": 8.0,
	},
}


## The recipe for a machine's weapon clip, or its weapon type's.
static func find(machine_id: String, clip: String, weapon_type: String) -> Dictionary:
	var key := "%s/%s" % [machine_id, clip]
	if BY_CLIP.has(key):
		return BY_CLIP[key]
	return BY_TYPE.get(weapon_type, BY_TYPE.melee)
