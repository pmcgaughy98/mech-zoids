extends RefCounted
## Pulse: the bond between a pilot and their machine (Claude, 2026-10-13). DRAFT: thresholds, abilities and numbers
## are proposals, names Preston's to set.
##
## Structure from Zoids Legacy (src/zoids/update_pulse_effects_from_emotion_growth.c, add_pulse_effect.c and the
## player state's pulse schedule, read for structure only): a pair's emotion growth rises with what they do together;
## a schedule of thresholds grants effects (ability-like bonuses) as it passes them. Story events can also grant one.
## Ours: pulse points come from battles fought together; each threshold unlocks one effect for that pair.

const MAX_PULSE := 1000

# Points per battle: base, plus for a win, plus per enemy machine destroyed.
const GAIN := {"battle": 10, "win": 15, "kill": 5}

# The schedule: crossing `at` grants `effect`. Effects are flat stat bonuses or flags read in battle.
const SCHEDULE := [
	{"at": 40, "effect": "steady_aim", "name": "Steady Aim", "mods": {"accuracy": 4}},
	{"at": 100, "effect": "second_wind", "name": "Second Wind", "mods": {"ep_regen": 2}},
	{"at": 180, "effect": "braced_frame", "name": "Braced Frame", "mods": {"defense": 5}},
	{"at": 300, "effect": "quick_start", "name": "Quick Start", "mods": {"speed": 4}},
	{"at": 450, "effect": "full_power", "name": "Full Power", "mods": {"power_pct": 6}},
	{"at": 650, "effect": "last_stand", "name": "Last Stand", "mods": {"max_hp_pct": 8}},
]


## Effects unlocked at `points`.
static func effects_at(points: int) -> Array:
	return SCHEDULE.filter(func(e): return points >= e.at)
