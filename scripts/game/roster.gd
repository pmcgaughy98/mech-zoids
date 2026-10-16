extends RefCounted
## The player's machines and pilots, and how they become battle units (Claude, 2026-10-13).
##
## Structure from Zoids Legacy's player state (read for structure only): stored machines and pilots, a team of six
## slots each pairing a pilot with a machine, parts fitted into a machine's slots under its load capacity, and the lab
## building a machine from its unlocked data plus a core. Every function takes `run` (the Run autoload, or any object
## with the same fields) so the headless check can drive it.

const Machines := preload("res://scripts/data/machines.gd")
const Pilots := preload("res://scripts/data/pilots.gd")
const Items := preload("res://scripts/data/items.gd")
const Pulse := preload("res://scripts/data/pulse.gd")

const TEAM_SLOTS := 6


static func new_machine_record(run, machine_id: String) -> Dictionary:
	run.next_uid += 1
	var parts := {}
	for slot in Items.SLOTS:
		parts[slot] = ""
	if not run.catalog.machines.has(machine_id):
		run.catalog.machines.append(machine_id)
	return {"uid": run.next_uid, "id": machine_id, "parts": parts, "pulse": 0, "pulse_effects": [], "pilot": ""}


static func new_pilot_record(pilot_id: String) -> Dictionary:
	var d: Dictionary = Pilots.PILOTS[pilot_id]
	return {"id": pilot_id, "name": d.name, "level": d.level, "exp": Pilots.exp_for_level(d.level), "growth": d.growth,
		"crew": "", "bonus": {"max_hp": 0.0, "mobility": 0.0, "sensor": 0.0, "weapon_accuracy": 0.0, "cp": 0.0}}


static func add_pilot(run, pilot_id: String) -> void:
	if not run.pilots.has(pilot_id):
		run.pilots[pilot_id] = new_pilot_record(pilot_id)
	if not run.catalog.pilots.has(pilot_id):
		run.catalog.pilots.append(pilot_id)


static func record_by_uid(run, uid: int) -> Dictionary:
	for r in run.roster:
		if r.uid == uid:
			return r
	return {}


## Puts a pilot in a machine in team slot `slot` (0-5). A machine already elsewhere in the team moves.
static func assign(run, slot: int, pilot_id: String, uid: int) -> bool:
	if slot < 0 or slot >= TEAM_SLOTS or record_by_uid(run, uid).is_empty() or not run.pilots.has(pilot_id):
		return false
	for i in TEAM_SLOTS:
		if run.team_slots[i].machine == uid or run.team_slots[i].pilot == pilot_id:
			run.team_slots[i] = {"pilot": "", "machine": -1}
	run.team_slots[slot] = {"pilot": pilot_id, "machine": uid}
	record_by_uid(run, uid).pilot = pilot_id
	sync_team(run)
	return true


## Keeps the old `team` list (machine ids) in step with the slots, for the scenes that read it.
static func sync_team(run) -> void:
	run.team = []
	for s in run.team_slots:
		if s.machine >= 0:
			run.team.append(record_by_uid(run, s.machine).id)


static func load_capacity(machine_id: String) -> int:
	return int(Items.LOAD_CAPACITY.get(Machines.MACHINES[machine_id].size, 45))


static func load_used(record: Dictionary) -> int:
	var w := 0
	for slot in record.parts:
		if record.parts[slot] != "":
			w += int(Items.PARTS[record.parts[slot]].weight)
	return w


## Fits a part from the inventory into its slot (the old part goes back). Fails over the load capacity.
static func equip(run, uid: int, part_id: String) -> String:
	var r := record_by_uid(run, uid)
	if r.is_empty() or not Items.PARTS.has(part_id) or int(run.parts.get(part_id, 0)) <= 0:
		return "not available"
	var slot: String = Items.PARTS[part_id].slot
	var old: String = r.parts[slot]
	var w := load_used(r) - (int(Items.PARTS[old].weight) if old != "" else 0) + int(Items.PARTS[part_id].weight)
	if w > load_capacity(r.id):
		return "too heavy: %d of %d" % [w, load_capacity(r.id)]
	if old != "":
		run.parts[old] = int(run.parts.get(old, 0)) + 1
	run.parts[part_id] = int(run.parts[part_id]) - 1
	r.parts[slot] = part_id
	return ""


static func unequip(run, uid: int, slot: String) -> void:
	var r := record_by_uid(run, uid)
	if r.is_empty() or r.parts.get(slot, "") == "":
		return
	run.parts[r.parts[slot]] = int(run.parts.get(r.parts[slot], 0)) + 1
	r.parts[slot] = ""


## The lab: a machine whose data is unlocked, from one core and the build cost. Returns the new record or {}.
static func build_machine(run, machine_id: String) -> Dictionary:
	if not run.unlocked_data.has(machine_id) or int(run.cores.get(machine_id, 0)) <= 0:
		return {}
	var cost: int = Items.CORES[machine_id].build_cost
	if run.money < cost:
		return {}
	run.money -= cost
	run.cores[machine_id] = int(run.cores[machine_id]) - 1
	var r := new_machine_record(run, machine_id)
	run.roster.append(r)
	return r


## The mods a machine carries into battle: parts, its pilot's growth and crew, and its pulse effects.
static func battle_mods(run, record: Dictionary) -> Dictionary:
	var mods := {"defense": 0.0, "speed": 0.0, "accuracy": 0.0, "max_ep": 0.0, "ep_regen": 0.0, "power_pct": 0.0, "max_hp_pct": 0.0}
	for slot in record.parts:
		if record.parts[slot] != "":
			for k in Items.PARTS[record.parts[slot]].mods:
				mods[k] = mods.get(k, 0.0) + float(Items.PARTS[record.parts[slot]].mods[k])
	for e in record.pulse_effects:
		for s in Pulse.SCHEDULE:
			if s.effect == e:
				for k in s.mods:
					mods[k] = mods.get(k, 0.0) + float(s.mods[k])
	var p: Dictionary = run.pilots.get(record.pilot, {})
	if not p.is_empty():
		mods.max_hp_pct += p.bonus.max_hp
		mods.accuracy += p.bonus.weapon_accuracy * 0.5 + p.bonus.sensor * 0.25
		mods.speed += p.bonus.mobility * 0.2
		if p.crew != "":
			var c: Dictionary = Pilots.CREW[p.crew]
			mods.accuracy += float(c.get("weapon_accuracy", 0)) * 0.5
			mods.defense += float(c.get("defense", 0))
			mods.speed += float(c.get("speed", 0)) * 0.3
	return mods


## A battle unit for a team record: Machines.make() plus battle_mods(). Carries "uid" and "pilot" so the result
## can be credited back to the record.
static func make_unit(run, record: Dictionary, side: String) -> Dictionary:
	var u := Machines.make(record.id, side)
	var m := battle_mods(run, record)
	u.max_hp = int(round(u.max_hp * (1.0 + m.max_hp_pct / 100.0)))
	u.hp = u.max_hp
	u.defense = int(round(u.defense + m.defense))
	u.speed = int(round(u.speed + m.speed))
	u.max_ep = int(round(u.max_ep + m.max_ep))
	u.ep = u.max_ep / 2
	u.ep_regen = int(round(u.ep_regen + m.ep_regen))
	var weapons: Array = []
	for w in u.weapons:
		var w2: Dictionary = w.duplicate()
		w2.power = int(round(w.power * (1.0 + m.power_pct / 100.0)))
		w2.accuracy = int(round(w.accuracy + m.accuracy))
		weapons.append(w2)
	u.weapons = weapons
	u.uid = record.uid
	u.pilot = record.pilot
	return u


## The team's units for a battle, in slot order; `cap` limits how many go (battle rules).
static func team_units(run, cap: int = TEAM_SLOTS) -> Array:
	var out: Array = []
	for s in run.team_slots:
		if s.machine >= 0 and out.size() < cap:
			out.append(make_unit(run, record_by_uid(run, s.machine), "player"))
	return out
