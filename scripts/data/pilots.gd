extends RefCounted
## Pilots: who drives the machines (Claude, 2026-10-13). DRAFT: names, numbers and growth are proposals; Preston sets
## them. Structure from Zoids Legacy's player state (read for structure only): a pilot has a level (to 99) and
## experience, a growth class that decides what rises per level (machine health, mobility, sensor accuracy, weapon
## accuracy, command points), and may carry one support crew member (an auxiliary pilot) for flat bonuses. A machine
## can require a pilot level. Bonuses are percents applied to the machine in battle (scripts/game/progression.gd).

const LEVEL_LIMIT := 99

# Percent gained per level, by growth class.
const GROWTH := {
	"steady": {"max_hp": 1.0, "mobility": 1.0, "sensor": 1.0, "weapon_accuracy": 1.0, "cp": 1.0},
	"sharp": {"max_hp": 0.6, "mobility": 1.4, "sensor": 1.4, "weapon_accuracy": 1.6, "cp": 1.0},
	"sturdy": {"max_hp": 1.6, "mobility": 0.6, "sensor": 0.8, "weapon_accuracy": 0.8, "cp": 1.2},
}

const PILOTS := {
	"pilot_lead": {"name": "Lead Pilot", "growth": "steady", "level": 1, "draft": true},   # the player; renamed at name entry later
	"pilot_ace": {"name": "Ace (draft)", "growth": "sharp", "level": 3, "draft": true},
	"pilot_anchor": {"name": "Anchor (draft)", "growth": "sturdy", "level": 2, "draft": true},
}

# Support crew: ride along with a pilot, flat percent bonuses.
const CREW := {
	"crew_mechanic": {"name": "Mechanic (draft)", "hp_recovery": 5, "defense": 3},
	"crew_spotter": {"name": "Spotter (draft)", "weapon_accuracy": 5, "sensor": 5},
	"crew_runner": {"name": "Runner (draft)", "speed": 6},
}


## Experience needed to reach `level` from level 1.
static func exp_for_level(level: int) -> int:
	return int(round(30.0 * pow(float(max(level, 1) - 1), 1.6)))
