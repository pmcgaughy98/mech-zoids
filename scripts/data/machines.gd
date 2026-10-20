extends RefCounted
## Placeholder machines, classes and faction colours. Every number is a Claude draft for testing;
## names, designs and stat values are Preston's call.

# Faction colours: Director's Lookbook "Candy Pop Primaries" on a gunmetal frame. A proposal, not decided.
const PALETTE := {
	"frame": Color("4a4f57"),
	"frame_dark": Color("2b2e33"),
	"player_main": Color("fafaf7"),
	"player_trim": Color("1e90ff"),
	"rival_main": Color("ff3b3f"),
	"rival_trim": Color("111111"),
	"light": Color("ffd400"),
}

# Size class: bigger means more health but slower.
const SIZES := {
	"S": {"hp": 0.8, "speed": 1.2},
	"M": {"hp": 1.0, "speed": 1.0},
	"L": {"hp": 1.3, "speed": 0.85},
	"XL": {"hp": 1.7, "speed": 0.7},
}

# How a machine moves sets what it shrugs off and what hurts it: damage taken per weapon type.
const BODIES := {
	"ground": {"melee": 1.0, "shell": 0.8, "missile": 1.2, "beam": 1.0},
	"flyer": {"melee": 0.7, "shell": 1.0, "missile": 1.0, "beam": 1.2},
	"swimmer": {"melee": 1.0, "shell": 1.2, "missile": 1.0, "beam": 0.8},
}
const FLYER_DODGE := 30  # extra miss chance against a flyer, unless the weapon is anti-air

# Machine designs, proposals for Preston: docs/design/machines-2026-10-11.md (Claude, 2026-10-11). Each has its
# own colours; the faction shows in the eye and running lights (player teal, rival amber). Every colour scheme
# was chosen away from the well-known Zoids schemes (no white-and-blue lion, no red-and-black raptor, no plain
# red or white bird). Weapon "mount" says where it sits and how it fires, for Codex and the battle animation.
# Numbers are drafts; the three original machines keep their tested stats.
const MACHINES := {
	"lion_m": {   # id kept so saves and checks still work; the design is now the Tiger type
		"name": "Tiger type", "animal": "cat", "size": "M", "body": "ground", "faction": "player",
		"hp": 160, "ep": 60, "ep_regen": 10, "speed": 30, "defense": 20,
		"colours": {"main": "e0a33a", "trim": "2a2c30", "accent": "3f8f84", "light": "5fe1d0"},
		"weapons": [
			{"name": "Rake Claws", "type": "melee", "power": 22, "ep": 0, "accuracy": 90,
				"mount": "front paws: three ceramic claws each, swiped low"},
			{"name": "Jaw Gun", "type": "shell", "power": 30, "ep": 15, "accuracy": 80,
				"mount": "a short twin barrel slung under the lower jaw; fires as the head drops"},
			{"name": "Spring Pounce", "type": "melee", "power": 64, "ep": 40, "accuracy": 85,
				"mount": "hind-leg pistons fire it forward, claws first"},
		],
		"slot": "res://art/machines/lion_m.png",
	},
	"raptor_s": {
		"name": "Raptor type", "animal": "raptor", "size": "S", "body": "ground", "faction": "rival",
		"hp": 200, "ep": 50, "ep_regen": 10, "speed": 34, "defense": 16,
		"colours": {"main": "5b2a4e", "trim": "d9cfb6", "accent": "8c6a3f", "light": "ffb02e"},
		"weapons": [
			{"name": "Snap Jaw", "type": "melee", "power": 20, "ep": 0, "accuracy": 95,
				"mount": "the head: a quick sideways bite"},
			{"name": "Tail Pod", "type": "missile", "power": 26, "ep": 12, "accuracy": 85,
				"mount": "a four-cell launcher at the tail tip; fires on a tail whip"},
			{"name": "Sickle Leap", "type": "melee", "power": 44, "ep": 30, "accuracy": 80,
				"mount": "a leap that lands on the toe sickles"},
		],
		"slot": "res://art/machines/raptor_s.png",
	},
	"hawk_s": {
		"name": "Hawk type", "animal": "bird", "size": "S", "body": "flyer", "faction": "rival",
		"hp": 205, "ep": 50, "ep_regen": 10, "speed": 40, "defense": 14,
		"colours": {"main": "8f3324", "trim": "3c4f57", "accent": "c08a3e", "light": "ffb02e"},
		"weapons": [
			{"name": "Grapple Talons", "type": "melee", "power": 18, "ep": 0, "accuracy": 90,
				"mount": "the feet: grab, lift and drop"},
			{"name": "Root Guns", "type": "shell", "power": 28, "ep": 12, "accuracy": 85,
				"mount": "two guns in the wing roots; fired on a strafing pass"},
			{"name": "Stoop", "type": "melee", "power": 48, "ep": 28, "accuracy": 80,
				"mount": "wings folded, a straight drop from height"},
		],
		"slot": "res://art/machines/hawk_s.png",
	},
	"ape_l": {   # new: the green gorilla Preston asked for, heavy and close-in, no missiles
		"name": "Gorilla type", "animal": "ape", "size": "L", "body": "ground", "faction": "player",
		"hp": 190, "ep": 50, "ep_regen": 10, "speed": 22, "defense": 30,
		"colours": {"main": "4a7a3c", "trim": "2c4a2a", "accent": "a8763e", "light": "5fe1d0"},
		"weapons": [
			{"name": "Piston Knuckles", "clip": "punch", "type": "melee", "power": 30, "ep": 0, "accuracy": 85,
				"mount": "the fists it walks on are hydraulic rams"},
			{"name": "Ballast Throw", "clip": "throw", "type": "shell", "power": 40, "ep": 18, "accuracy": 75,
				"mount": "tears a block off the ballast rack on its back and hurls it in an arc"},
			{"name": "Quake Slam", "clip": "slam", "type": "melee", "power": 70, "ep": 45, "accuracy": 80,
				"mount": "both fists into the ground; the shockwave runs to the target"},
		],
		"slot": "res://art/machines/ape_l.png",
		"starter": true,
	},
	# The four starters, proposals (Claude, 2026-10-11; docs/design/starters-2026-10-11.md): gorilla, shoebill,
	# pangolin, pygmy hippo. Zoids has used gorillas (7) but never the other three. Palettes from Director's
	# Lookbook cards. Stats are drafts near the tested starter's, untested in battle.
	"shoebill_m": {
		"name": "Shoebill type", "animal": "shoebill", "size": "M", "body": "flyer", "faction": "player",
		"hp": 150, "ep": 60, "ep_regen": 12, "speed": 28, "defense": 16, "starter": true,
		"colours": {"main": "4a6fa5", "trim": "1f3a68", "accent": "f2c26b", "light": "5fe1d0"},   # Blue Hour Cool
		"weapons": [
			{"name": "Apex Decapitation", "clip": "clamp", "type": "melee", "power": 24, "ep": 0, "accuracy": 90,
				"mount": "the razor-edged bill clamps down, the hooked tip crushing, then wrenches sideways"},
			{"name": "Bill Clatter", "clip": "lance", "type": "shell", "power": 34, "ep": 16, "accuracy": 95,
				"mount": "the bill slams open and shut so fast it fires like a machine gun, the way the real bird clatters"},
			{"name": "Sentry Lunge", "clip": "buffet", "type": "melee", "power": 50, "ep": 30, "accuracy": 80,
				"mount": "it stands motionless as a statue, then lunges bill-first at ballistic speed"},
		],
		"slot": "res://art/machines/shoebill_m.png",
	},
	"pangolin_m": {
		"name": "Pangolin type", "animal": "pangolin", "size": "M", "body": "ground", "faction": "player",
		"hp": 175, "ep": 50, "ep_regen": 10, "speed": 24, "defense": 30, "starter": true,
		"colours": {"main": "da8600", "trim": "a02010", "accent": "407090", "light": "5fe1d0"},   # Ochre, Madder and Delft
		"weapons": [
			{"name": "Scale Rake", "clip": "rake", "type": "melee", "power": 22, "ep": 0, "accuracy": 90,
				"mount": "the heavy tail sweeps sideways; its scale edges are the blade"},
			{"name": "Scale Shot", "clip": "shot", "type": "shell", "power": 28, "ep": 14, "accuracy": 85,
				"mount": "loose scale plates flicked off the back in a spread"},
			{"name": "Ball Roll", "clip": "roll", "type": "melee", "power": 60, "ep": 38, "accuracy": 80,
				"mount": "curls into an armoured ball and rolls through the target"},
		],
		"slot": "res://art/machines/pangolin_m.png",
	},
	"hippo_m": {
		"name": "Pygmy Hippo type", "animal": "hippo", "size": "M", "body": "swimmer", "faction": "player",
		"hp": 185, "ep": 55, "ep_regen": 10, "speed": 22, "defense": 24, "starter": true,
		"colours": {"main": "6b4e71", "trim": "2e2235", "accent": "c98b6b", "light": "5fe1d0"},   # Desert Dusk
		"weapons": [
			{"name": "Gape Crush", "clip": "gape", "type": "melee", "power": 26, "ep": 0, "accuracy": 85,
				"mount": "the jaw opens near flat and slams shut; tusks in cream"},
			{"name": "Pressure Jets", "clip": "jets", "type": "beam", "power": 30, "ep": 15, "accuracy": 85,
				"mount": "two water jets from valves above the snout, cutting like a beam"},
			{"name": "Wake Charge", "clip": "charge", "type": "melee", "power": 58, "ep": 36, "accuracy": 80,
				"mount": "surges out of the water head first, pushing a wave ahead of it"},
		],
		"slot": "res://art/machines/hippo_m.png",
	},
	"kangaroo_m": {   # the fifth starter (Claude proposal, approved by Preston 2026-10-12): red by nature, hops
		"name": "Red Kangaroo type", "animal": "kangaroo", "size": "M", "body": "ground", "faction": "player",
		"hp": 150, "ep": 55, "ep_regen": 11, "speed": 36, "defense": 16, "starter": true,
		"colours": {"main": "d4553a", "trim": "2b2429", "accent": "e6724c", "light": "5fe1d0"},   # from Preston's reference sprite
		# Loadout pivot (Preston, 2026-10-12): close-quarters boxing and jet boosters; the pouch mortar is gone.
		# Names and mounts from his text; the numbers carry over from the old slots and are a DRAFT for him to set.
		"weapons": [
			{"name": "Impact Boxing Gloves", "clip": "jab", "type": "melee", "power": 26, "ep": 0, "accuracy": 90,
				"mount": "pneumatic fists: hydraulic pistons on each forearm fire a kinetic blast on contact, knocking the target back"},
			{"name": "Pouch Cannon", "clip": "flak", "type": "shell", "power": 30, "ep": 14, "accuracy": 80,
				"mount": "a pirate-style iron cannon that swings out of a hatch in the stomach, above the pouch, and fires one heavy ball"},
			{"name": "Tail Spring", "clip": "kick", "type": "melee", "power": 58, "ep": 36, "accuracy": 80,
				"mount": "a jet-boosted leap off the tail, both feet first: the hip boosters fire on the way up"},
		],
		"slot": "res://art/machines/kangaroo_m.png",
	},
	# DRAFT (Claude, 2026-10-12): the sixth starter Preston asked for, "a black wolf with blood red accents". Names,
	# lore and numbers are his to set; these carry the other medium starters' ranges so the fight runs.
	"wolf_m": {
		"name": "Black Wolf type", "animal": "wolf", "size": "M", "body": "ground", "faction": "player",
		"hp": 130, "ep": 60, "ep_regen": 12, "speed": 44, "defense": 14,
		"colours": {"main": "1a1a1f", "trim": "5a0a0e", "accent": "b3131a", "light": "5fe1d0"},
		"weapons": [
			{"name": "Fang Lunge", "clip": "lunge", "type": "melee", "power": 28, "ep": 0, "accuracy": 90,
				"mount": "the jaw: blood-red fangs, a lunge and bite"},
			{"name": "Howl Burst", "clip": "howl", "type": "shell", "power": 26, "ep": 12, "accuracy": 85,
				"mount": "a red-grilled emitter in the throat, a concussive howl"},
			{"name": "Shadow Dash", "clip": "dash", "type": "melee", "power": 50, "ep": 30, "accuracy": 85,
				"mount": "the shoulder and hip blade fins, a full-speed pass through the target"},
		],
		"slot": "res://art/machines/wolf_m.png", "starter": true,
	},
}
const SLOT_SIZE := Vector2i(64, 48)  # pixel size Codex should draw battle machines at


## A fresh copy of a machine for one battle.
static func make(id: String, side: String) -> Dictionary:
	var d: Dictionary = MACHINES[id]
	var size: Dictionary = SIZES[d.size]
	var hp := int(round(d.hp * size.hp))
	return {
		"id": id, "name": d.name, "side": side, "faction": d.faction, "animal": d.animal,
		"size": d.size, "body": d.body, "hp": hp, "max_hp": hp, "ep": d.ep / 2, "max_ep": d.ep,
		"ep_regen": d.ep_regen, "speed": int(round(d.speed * size.speed)), "defense": d.defense,
		"weapons": d.weapons, "shield": 0, "mines": 0, "bracing": false, "air_lock": 0,
	}
