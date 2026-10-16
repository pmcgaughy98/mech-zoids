extends RefCounted
## The battle rules, with no drawing in them. The battle scene and the headless check both run this file.
## Every action adds steps to `queue`; the scene plays them back one at a time ("act, then show"),
## which is the rhythm read from Zoids Legacy's result queue.

const Machines := preload("res://scripts/data/machines.gd")
const Commands := preload("res://scripts/data/commands.gd")

const MAX_ROUNDS := 40  # a safety stop; the check reports any battle that reaches it

var units: Array = []          # every machine in the fight, both sides
var deck := {"player": [], "enemy": []}  # commands not yet played this battle
var command_used := {"player": false, "enemy": false}  # one command per side per round
var order: Array = []          # machines still to act this round, fastest first
var queue: Array = []          # result steps waiting to be shown
var round_no := 0
var winner := ""               # "player", "enemy", or "" while the fight goes on
var stats := {"commands": 0, "charges": 0}  # what got used, for the check
var rng := RandomNumberGenerator.new()


func setup(player_ids: Array, enemy_ids: Array, player_deck: Array, enemy_deck: Array, seed_value: int) -> void:
	rng.seed = seed_value
	for id in player_ids:   # an id, or a unit already built from a team record (scripts/game/roster.gd)
		units.append(id if typeof(id) == TYPE_DICTIONARY else Machines.make(id, "player"))
	for id in enemy_ids:
		units.append(Machines.make(id, "enemy"))
	deck.player = player_deck.duplicate()
	deck.enemy = enemy_deck.duplicate()
	# Formation (Zoids Legacy, read for structure only): up to six a side, the first three in the front row, the
	# rest behind. A unit may arrive with its own row.
	for side in ["player", "enemy"]:
		var k := 0
		for u in units:
			if u.side == side:
				if not u.has("row"):
					u.row = "front" if k < 3 else "back"
				k += 1
	_start_round()


func alive(side: String) -> Array:
	return units.filter(func(u): return u.side == side and u.hp > 0)


func foe_of(u: Dictionary) -> Dictionary:
	var foes := front_line("enemy" if u.side == "player" else "player")
	return foes[0] if foes.size() > 0 else {}


## A side's front line: its living front row, or its back row once the front is gone (an empty front row
## pulls the back row forward).
func front_line(side: String) -> Array:
	var a := alive(side)
	var f := a.filter(func(x): return x.get("row", "front") == "front")
	return f if not f.is_empty() else a


## Melee reaches only the enemy's front line, and only from your own front line; guns, beams and missiles reach
## any row.
func can_use(u: Dictionary, w: Dictionary) -> bool:
	return w.type != "melee" or front_line(u.side).has(u)


func valid_targets(u: Dictionary, w: Dictionary) -> Array:
	var side := "enemy" if u.side == "player" else "player"
	return front_line(side) if w.type == "melee" else alive(side)


## The target an action names, if it is still valid for the weapon; else the best one for the weapon.
func _target_for(u: Dictionary, action: Dictionary) -> Dictionary:
	var w: Dictionary = u.weapons[action.weapon]
	var ts := valid_targets(u, w)
	var i: int = action.get("target", -1)
	if i >= 0 and i < units.size() and ts.has(units[i]):
		return units[i]
	var best: Dictionary = ts[0] if not ts.is_empty() else {}
	for t in ts:
		if _target_value(u, w, t) > _target_value(u, w, best):
			best = t
	return best


## Expected damage, with a large bonus when it would finish the target.
func _target_value(u: Dictionary, w: Dictionary, t: Dictionary) -> float:
	if t.is_empty():
		return -1.0
	var e := expected_damage(w, t, u)
	return e + (1000.0 if e >= t.hp else 0.0)


## Moves on to the next machine that can act and applies its start-of-turn effects (mines).
## Returns that machine, or {} once the battle is over.
func begin_turn() -> Dictionary:
	while winner == "":
		if order.is_empty():
			_end_round()
			if winner != "":
				break
			_start_round()
		var u: Dictionary = order[0]
		u.bracing = false  # bracing lasts until the machine's own next turn
		if u.hp <= 0:
			order.pop_front()
			continue
		if u.mines > 0:
			u.mines -= 1
			_damage(u, max(1, int(u.max_hp * 0.06)), "%s runs over a mine" % u.name)
			if u.hp <= 0:
				order.pop_front()
				_check_winner()
				continue
		return u
	return {}


func can_play_command(side: String) -> bool:
	return not command_used[side] and deck[side].size() > 0


## Plays one deck command for `u`'s side. It does not use up the machine's action.
func play_command(u: Dictionary, id: String) -> void:
	var side: String = u.side
	if command_used[side] or not deck[side].has(id):
		return
	deck[side].erase(id)
	command_used[side] = true
	stats.commands += 1
	var name: String = Commands.COMMANDS[id].name
	match id:
		"shield_wall":
			u.shield = 2
			_push("command", "%s: %s is shielded" % [name, u.name])
		"field_repair":
			var amount := int(u.max_hp * 0.35)
			u.hp = min(u.max_hp, u.hp + amount)
			_push("command", "%s: %s repairs %d" % [name, u.name, amount])
		"mine_field":
			for f in alive("enemy" if side == "player" else "player"):
				f.mines = 3
			_push("command", "%s: mines laid under the enemy" % name)
		"power_surge":
			u.ep = u.max_ep
			_push("command", "%s: %s's energy is full" % [name, u.name])
		"air_lock":
			u.air_lock = MAX_ROUNDS  # the rest of the battle
			_push("command", "%s: %s locks onto anything in the air" % [name, u.name])


## The machine's action for its turn: {"kind": "attack", "weapon": i} or {"kind": "charge"}.
func do_action(u: Dictionary, action: Dictionary) -> void:
	if action.kind == "charge" or not _affordable(u, action.weapon):
		var gain: int = min(u.max_ep - u.ep, u.ep_regen * 3)
		u.ep += gain
		u.bracing = true
		stats.charges += 1
		_push("charge", "%s braces and charges energy (+%d)" % [u.name, gain], u)
	else:
		_attack(u, u.weapons[action.weapon], _target_for(u, action))
	order.pop_front()
	_check_winner()


## A recovery item used on `u`'s turn (Zoids Legacy's turn: use an item, or act). The scene spends the item and
## applies it through scripts/game/economy.gd, then calls this to record the step and end the turn.
func use_item(u: Dictionary, item_name: String, restored: int, what: String) -> void:
	_push("item", "%s uses %s: +%d %s" % [u.name, item_name, restored, what], u, restored)
	order.pop_front()
	_check_winner()


func _affordable(u: Dictionary, i: int) -> bool:
	return i >= 0 and i < u.weapons.size() and u.weapons[i].ep <= u.ep and can_use(u, u.weapons[i])


func _attack(u: Dictionary, w: Dictionary, target: Dictionary) -> void:
	u.ep -= w.ep
	if rng.randi_range(1, 100) > hit_chance(w, target, u):
		_push("miss", "%s uses %s. Miss!" % [u.name, w.name], target, 0, {"actor": units.find(u), "clip": w.get("clip", ""), "wtype": w.type})
		return
	var dmg := int(round(base_damage(w, target) * rng.randf_range(0.9, 1.1)))
	if target.shield > 0:
		dmg = int(dmg * 0.5)
	if target.bracing:
		dmg = int(dmg * 0.75)
	_damage(target, max(1, dmg), "%s uses %s" % [u.name, w.name], {"actor": units.find(u), "clip": w.get("clip", ""), "wtype": w.type})


func hit_chance(w: Dictionary, target: Dictionary, attacker: Dictionary = {}) -> int:
	var anti_air: bool = w.get("anti_air", false) or attacker.get("air_lock", 0) > 0
	var dodge := Machines.FLYER_DODGE if target.body == "flyer" and not anti_air else 0
	return w.accuracy - dodge


func base_damage(w: Dictionary, target: Dictionary) -> float:
	return w.power * Machines.BODIES[target.body][w.type] * 100.0 / (100.0 + target.defense)


## What a weapon is worth on average against a target: damage times the chance to hit.
func expected_damage(w: Dictionary, target: Dictionary, attacker: Dictionary = {}) -> float:
	var shield := 0.5 if target.shield > 0 else 1.0
	var brace := 0.75 if target.bracing else 1.0
	return base_damage(w, target) * shield * brace * hit_chance(w, target, attacker) / 100.0


func _damage(u: Dictionary, amount: int, text: String, extra: Dictionary = {}) -> void:
	u.hp = max(0, u.hp - amount)
	_push("damage", "%s: %d damage" % [text, amount], u, amount, extra)
	if u.hp == 0:
		_push("destroyed", "%s is down!" % u.name, u)


func _start_round() -> void:
	round_no += 1
	command_used = {"player": false, "enemy": false}
	order = units.filter(func(u): return u.hp > 0)
	order.sort_custom(func(a, b): return a.speed > b.speed or (a.speed == b.speed and a.side == "player"))
	for u in order:
		u.ep = min(u.max_ep, u.ep + u.ep_regen)
	_push("round", "Round %d" % round_no)


func _end_round() -> void:
	for u in units:
		if u.shield > 0:
			u.shield -= 1
		if u.air_lock > 0:
			u.air_lock -= 1
	if round_no >= MAX_ROUNDS and winner == "":
		# Safety stop: the side with more health left (as a share) wins.
		var p := _health_share("player")
		winner = "player" if p >= _health_share("enemy") else "enemy"
		_push("result", "Time is up. %s side wins" % winner.capitalize())


func _health_share(side: String) -> float:
	var hp := 0.0
	var mx := 0.0
	for u in units:
		if u.side == side:
			hp += u.hp
			mx += u.max_hp
	return hp / mx


func _check_winner() -> void:
	if winner != "":
		return
	if alive("enemy").is_empty():
		winner = "player"
		_push("result", "Victory!")
	elif alive("player").is_empty():
		winner = "enemy"
		_push("result", "Defeat...")


## Every step carries a snapshot of all gauges, so the scene can show health and energy as they were then.
func _push(kind: String, text: String, u: Dictionary = {}, value := 0, extra: Dictionary = {}) -> void:
	var snap := []
	for m in units:
		snap.append([m.hp, m.ep])
	var step := {"kind": kind, "text": text, "unit": units.find(u), "value": value, "snap": snap}
	step.merge(extra)   # attack steps add "actor" (the attacker's index), "clip" (its animation) and "wtype" (the weapon's type)
	queue.append(step)


# --- Choosing (the enemy, and the player on autopilot) --------------------------------------------

## Picks a command and an action for `u`. Policies: "smart" uses commands and Charge, "deck" only commands,
## "charge" only Charge, "basic" neither (just the strongest weapon it can pay for), "idle" only charges.
func choose(u: Dictionary, policy: String) -> Dictionary:
	if policy == "idle":
		return {"command": "", "kind": "charge"}
	var foe := foe_of(u)
	var use_deck := policy == "smart" or policy == "deck"
	var use_charge := policy == "smart" or policy == "charge"
	var cmd := _pick_command(u, foe) if use_deck else ""
	var ep: int = u.max_ep if cmd == "power_surge" else u.ep
	var best_i := 0
	var best := -1.0
	var top := -1.0
	var top_i := 0
	var best_t: Dictionary = foe
	for i in u.weapons.size():   # every usable weapon against every target it can reach
		if not can_use(u, u.weapons[i]):
			continue
		for t in valid_targets(u, u.weapons[i]):
			var e := _target_value(u, u.weapons[i], t)
			if e > top:
				top = e
				top_i = i
			if u.weapons[i].ep <= ep and e > best:
				best = e
				best_i = i
				best_t = t
	if best < 0.0:   # nothing it can use reaches (a back-row machine with only melee)
		return {"command": cmd, "kind": "charge"}
	# Charge when the big weapon is much better, can't be paid for now, will be next turn, and the
	# weapon in hand would not finish the foe anyway.
	if use_charge and best < top * 0.6 and best < foe.hp and ep + u.ep_regen * 4 >= u.weapons[top_i].ep:
		return {"command": cmd, "kind": "charge"}
	return {"command": cmd, "kind": "attack", "weapon": best_i, "target": units.find(best_t)}


func _pick_command(u: Dictionary, foe: Dictionary) -> String:
	if not can_play_command(u.side):
		return ""
	var have: Array = deck[u.side]
	if have.has("field_repair") and u.hp < u.max_hp * 0.45:
		return "field_repair"
	if have.has("air_lock") and foe.body == "flyer" and u.air_lock == 0:
		return "air_lock"
	if have.has("mine_field") and foe.mines == 0 and foe.hp > foe.max_hp * 0.5:
		return "mine_field"
	if have.has("shield_wall") and u.shield == 0 and u.hp < u.max_hp * 0.75:
		return "shield_wall"
	if have.has("power_surge") and u.ep < u.max_ep / 2:
		return "power_surge"
	return ""
