extends RefCounted
## What a battle pays out, and how pilots and pairs grow (Claude, 2026-10-13). DRAFT numbers.
##
## Structure from Zoids Legacy (pilot experience and levels to 99 with growth classes; the pulse emotion growth and
## its effect schedule; money and cores from fights; read for structure only).

const Pilots := preload("res://scripts/data/pilots.gd")
const Pulse := preload("res://scripts/data/pulse.gd")
const Items := preload("res://scripts/data/items.gd")
const Machines := preload("res://scripts/data/machines.gd")
const Roster := preload("res://scripts/game/roster.gd")

const SIZE_EXP := {"S": 12, "M": 20, "L": 32, "XL": 50}
const SIZE_MONEY := {"S": 60, "M": 100, "L": 160, "XL": 260}


## Applies a finished battle to the run: experience and levels for the pilots who fought, pulse for each pair,
## money, and any core the request names. `units` are the battle's units (battle_logic.units); `request` the battle
## request (purse, core). Returns lines for the results screen.
static func award(run, units: Array, winner: String, request: Dictionary) -> Array:
	var lines: Array = []
	var won := winner == "player"
	var exp_pool := 0
	var money := 0
	var kills := 0
	for u in units:
		if u.side == "enemy":
			exp_pool += int(SIZE_EXP.get(u.size, 20))
			if u.hp <= 0:
				kills += 1
				money += int(SIZE_MONEY.get(u.size, 100))
	if not won:
		exp_pool = int(exp_pool * 0.4)
		money = 0
	money += int(request.get("purse", 0)) if won else 0
	var fighters := units.filter(func(u): return u.side == "player" and u.has("uid"))
	for u in fighters:
		var r := Roster.record_by_uid(run, u.uid)
		if r.is_empty():
			continue
		var p: Dictionary = run.pilots.get(r.pilot, {})
		if not p.is_empty():
			var share := int(ceil(exp_pool / float(max(1, fighters.size()))))
			for l in give_exp(p, share):
				lines.append(l)
		for l in give_pulse(r, Pulse.GAIN.battle + (Pulse.GAIN.win if won else 0) + Pulse.GAIN.kill * kills):
			lines.append(l)
	if money > 0:
		run.money = min(Items.MONEY_LIMIT, run.money + money)
		lines.append("Gained %d credits." % money)
	var core: String = request.get("core", "")
	if won and core != "":
		run.cores[core] = min(Items.QUANTITY_LIMIT, int(run.cores.get(core, 0)) + 1)
		if not run.unlocked_data.has(core):
			run.unlocked_data.append(core)
		lines.append("Recovered a %s." % Items.CORES[core].name)
	for u in units:
		if u.side == "enemy" and not run.catalog.machines.has(u.id):
			run.catalog.machines.append(u.id)   # the database records every machine fought
	return lines


## Experience for one pilot; level-ups add their growth class's percents. Returns result lines.
static func give_exp(pilot: Dictionary, amount: int) -> Array:
	var lines: Array = []
	pilot.exp += amount
	while pilot.level < Pilots.LEVEL_LIMIT and pilot.exp >= Pilots.exp_for_level(pilot.level + 1):
		pilot.level += 1
		var g: Dictionary = Pilots.GROWTH[pilot.growth]
		for k in g:
			pilot.bonus[k] = float(pilot.bonus.get(k, 0.0)) + float(g[k])
		lines.append("%s reached level %d." % [pilot.name, pilot.level])
	return lines


## Pulse for one pilot-machine pair; crossing a threshold unlocks its effect. Returns result lines.
static func give_pulse(record: Dictionary, amount: int) -> Array:
	var lines: Array = []
	record.pulse = min(Pulse.MAX_PULSE, int(record.pulse) + amount)
	for e in Pulse.effects_at(record.pulse):
		if not record.pulse_effects.has(e.effect):
			record.pulse_effects.append(e.effect)
			lines.append("Pulse: %s unlocked %s." % [Machines.MACHINES[record.id].name, e.name])
	return lines
