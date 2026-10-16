extends RefCounted
## Battle rules: limits a fight can set (Claude, 2026-10-13). DRAFT names, the arena's to use.
##
## Structure from Zoids Legacy's battle (battle.h, event_enable_battle_rule, the challenge menu; read for structure
## only): a fight can filter who may enter by size class, by flying, and by animal line, ban deck commands, and cap the
## team. Our arena lists challenges built from these.

const RULES := {
	"open": {"name": "Open Battle", "text": "No limits."},
	"no_commands": {"name": "Iron Rules", "text": "Deck commands are banned.", "ban_commands": true},
	"ground_only": {"name": "Ground Pounders", "text": "No flying machines.", "no_flyers": true},
	"light_class": {"name": "Light Class", "text": "Size M or smaller.", "max_size": "M"},
	"solo": {"name": "Solo Duel", "text": "One machine a side.", "team_cap": 1},
}

const SIZE_ORDER := ["S", "M", "L", "XL"]

# The arena's challenges: a rule, an enemy squad, a purse and a core (or "").
const CHALLENGES := [
	{"id": "arena_1", "rule": "solo", "enemy": ["pangolin_m"], "purse": 400, "core": ""},
	{"id": "arena_2", "rule": "ground_only", "enemy": ["hippo_m", "kangaroo_m"], "purse": 700, "core": "hippo_m"},
	{"id": "arena_3", "rule": "no_commands", "enemy": ["wolf_m", "shoebill_m"], "purse": 1000, "core": "wolf_m"},
]


## Whether a machine record may enter under `rule_id` (machines.gd data for its id).
static func allows(rule_id: String, machine: Dictionary) -> bool:
	var r: Dictionary = RULES.get(rule_id, {})
	if r.get("no_flyers", false) and machine.get("body", "") == "flyer":
		return false
	if r.has("max_size") and SIZE_ORDER.find(machine.get("size", "M")) > SIZE_ORDER.find(r.max_size):
		return false
	return true
