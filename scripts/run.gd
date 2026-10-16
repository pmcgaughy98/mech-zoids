extends Node
## The run record: everything that carries from scene to scene (team, deck, story flags, last battle).
## One copy lives at /root/Run for the whole game, so every scene reads the same state. It also saves.

signal flags_changed

const Commands := preload("res://scripts/data/commands.gd")
const Roster := preload("res://scripts/game/roster.gd")
const Items := preload("res://scripts/data/items.gd")
const Modes := preload("res://scripts/game/modes.gd")
const Progression := preload("res://scripts/game/progression.gd")
const Rules := preload("res://scripts/data/battle_rules.gd")
const SAVE_VERSION := 2

var team: Array = []               # machine ids in the player's squad
var owned: Array = []              # every deck command the player has
var deck: Array = []               # the ones equipped for battle (up to Commands.DECK_LIMIT)
var flags: Dictionary = {}         # story flags that have happened: name -> true
var location := "base"             # where Continue puts you
var battle_request: Dictionary = {}  # what the battle scene should fight, and where to go after
var last_battle: Dictionary = {}   # the result the next scene should react to (cleared once shown)
var battles: Array = []            # every battle result this run, oldest first
var came_from := ""                # the scene we just left, so the next one knows where to place you
var save_path := "user://save.json"

# --- The full player state (2026-10-13). Shape from Zoids Legacy's player state (read for structure only):
# pilots and machines stored, a team of six pilot-and-machine slots, items, parts, cores, money, and catalogs of
# what has been seen. The systems that use it: scripts/game/roster.gd, progression.gd, economy.gd.
var money := 0
var pilots: Dictionary = {}        # pilot id -> record
var roster: Array = []             # machine records (uid, id, parts, pulse, pilot)
var team_slots: Array = []         # six {"pilot": id or "", "machine": uid or -1}
var items: Dictionary = {}         # recovery items: id -> count
var parts: Dictionary = {}         # parts not fitted: id -> count
var cores: Dictionary = {}         # machine id -> count
var catalog := {"machines": [], "pilots": [], "parts": []}
var unlocked_data: Array = []      # machine ids the lab can build
var next_uid := 0
var mode := "title"                # the current mode (scripts/game/modes.gd)
var mode_args: Dictionary = {}
var last_awards: Array = []        # the last battle's payout lines

# The chain check drives every scene itself when autopilot is on.
var autopilot := false
var autopilot_lose := false        # chain check only: the player's side does nothing, to test losing
var battle_seed := 1


func new_game() -> void:
	team = ["lion_m"]
	owned = Commands.STARTER_DECK.duplicate()
	deck = Commands.STARTER_DECK.duplicate()
	flags = {}
	location = "base"
	battle_request = {}
	last_battle = {}
	battles = []
	_seed_player_state()
	flags_changed.emit()


## The full player state for a new game: the lead pilot in the first team machine, starting money and items.
func _seed_player_state() -> void:
	money = Items.STARTING_MONEY
	pilots = {}
	roster = []
	items = {"repair_kit": 2}
	parts = {}
	cores = {}
	catalog = {"machines": [], "pilots": [], "parts": []}
	unlocked_data = []
	next_uid = 0
	last_awards = []
	team_slots = []
	for i in Roster.TEAM_SLOTS:
		team_slots.append({"pilot": "", "machine": -1})
	Roster.add_pilot(self, "pilot_lead")
	for i in team.size():
		var r := Roster.new_machine_record(self, team[i])
		roster.append(r)
		team_slots[i].machine = r.uid
		if i == 0:
			team_slots[i].pilot = "pilot_lead"
			r.pilot = "pilot_lead"


func set_flag(flag: String) -> void:
	if not flags.get(flag, false):
		flags[flag] = true
		flags_changed.emit()


func has_flag(flag: String) -> bool:
	return flags.get(flag, false)


## Adds a command to what the player owns, and equips it if there is room.
func give_command(id: String) -> void:
	if not owned.has(id):
		owned.append(id)
		if deck.size() < Commands.DECK_LIMIT:
			deck.append(id)


## Equips or unequips one command. Returns false if the deck is already full.
func toggle_deck(id: String) -> bool:
	if deck.has(id):
		deck.erase(id)
		return true
	if deck.size() >= Commands.DECK_LIMIT:
		return false
	deck.append(id)
	return true


## Every scene change goes through here, so the chain check sees the real handoffs.
func goto(scene: String) -> void:
	var current := get_tree().current_scene
	came_from = current.scene_file_path.get_file().get_basename() if current else ""
	if scene in ["base", "field", "field2"]:
		location = scene
	get_tree().call_deferred("change_scene_to_file", "res://scenes/%s.tscn" % scene)


## Changes mode (scripts/game/modes.gd): shops, lab, database, arena and the rest open their scene with `args`.
func go_mode(m: String, args: Dictionary = {}) -> void:
	mode = m
	mode_args = args
	var scene := Modes.scene_of(m)
	if scene != "":
		goto(scene)


## The squad for a battle: the team's units (pilots, parts and pulse applied) when there is a roster, else ids.
func battle_team(cap: int = Roster.TEAM_SLOTS) -> Array:
	return Roster.team_units(self, cap) if not roster.is_empty() else team.duplicate()


## A battle from a story script or the arena: {enemy, purse, core, rule, flag, reward, win_scene}.
func start_story_battle(spec: Dictionary) -> void:
	var rule: Dictionary = Rules.RULES.get(spec.get("rule", "open"), {})
	battle_request = {"player": battle_team(int(rule.get("team_cap", Roster.TEAM_SLOTS))), "enemy": spec.enemy,
		"enemy_deck": Commands.STARTER_DECK, "flag": spec.get("flag", ""), "reward": spec.get("reward", ""),
		"win_scene": spec.get("win_scene", "base"), "purse": int(spec.get("purse", 0)), "core": spec.get("core", ""),
		"rule": spec.get("rule", "open"), "ban_commands": rule.get("ban_commands", false)}
	goto("battle")


## Pays out a finished battle (experience, levels, pulse, money, cores, catalog). Returns the result lines.
func apply_battle_result(units: Array, winner: String, request: Dictionary) -> Array:
	last_awards = Progression.award(self, units, winner, request)
	return last_awards


## Asks the battle scene for a fight. On a win: `flag` is set, `reward` (a command id, or "") is given, and you
## go to `win_scene`. On a loss you are towed back to base.
func start_battle(enemy_ids: Array, enemy_deck: Array, flag: String, reward: String, win_scene: String) -> void:
	battle_request = {"player": battle_team(), "enemy": enemy_ids, "enemy_deck": enemy_deck, "flag": flag,
		"reward": reward, "win_scene": win_scene}
	goto("battle")


## Called by the scene that showed the after-battle talk.
func debrief_done() -> void:
	if last_battle.get("winner", "") == "player":
		set_flag(last_battle.flag + "_debriefed")
	last_battle = {}


# --- Saving ---------------------------------------------------------------------------------------

func has_save() -> bool:
	return FileAccess.file_exists(save_path)


func save_game() -> bool:
	var f := FileAccess.open(save_path, FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify({"version": SAVE_VERSION, "team": team, "owned": owned, "deck": deck, "flags": flags,
		"location": location, "money": money, "pilots": pilots, "roster": roster, "team_slots": team_slots,
		"items": items, "parts": parts, "cores": cores, "catalog": catalog, "unlocked_data": unlocked_data,
		"next_uid": next_uid}, "\t"))
	return true


func load_game() -> bool:
	var f := FileAccess.open(save_path, FileAccess.READ)
	if f == null:
		return false
	var data = JSON.parse_string(f.get_as_text())
	if typeof(data) != TYPE_DICTIONARY:
		return false
	new_game()
	team = data.get("team", team)
	owned = data.get("owned", owned)
	deck = data.get("deck", deck)
	flags = data.get("flags", {})
	location = data.get("location", "base")
	if data.has("roster"):   # version 2; a version-1 save keeps the state new_game() seeded from its team
		money = int(data.get("money", money))
		pilots = data.pilots
		roster = data.roster
		team_slots = data.get("team_slots", team_slots)
		items = data.get("items", {})
		parts = data.get("parts", {})
		cores = data.get("cores", {})
		catalog = data.get("catalog", catalog)
		unlocked_data = data.get("unlocked_data", [])
		next_uid = int(data.get("next_uid", 0))
		for r in roster:   # JSON reads numbers back as floats
			r.uid = int(r.uid)
			r.pulse = int(r.pulse)
		for s in team_slots:
			s.machine = int(s.machine)
		for p in pilots.values():
			p.level = int(p.level)
			p.exp = int(p.exp)
	flags_changed.emit()
	return true
