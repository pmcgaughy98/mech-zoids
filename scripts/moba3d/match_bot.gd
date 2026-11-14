class_name MatchBot
extends Node
## Drives a machine in the match (Claude, 2026-11-04, game feel lane), so 3 v 3 has people in it. A plain bot: it walks
## the lane just behind its own wave, fights what its wave fights, uses its kit when the reach fits, hits a tower or
## core only while its minions are taking the tower's fire, steps out of a tower's aim, and goes home to heal when
## hurt (recalling when no enemy machine is near). Behaviour picks, not designs; every number is a placeholder.

## When a bot uses each slot. "reach": metres to the target's middle (picks, close to each kit's own placeholder
## lengths); "min": enemies that must be inside; "machines": count only machines; "aim": turn to the nearest first;
## "low": only under this share of health; "high": only at or above it; "edge": reach is edge to edge, not to the middle;
## "arg": "target" passes the nearest's position, "away" a point toward base, "node" the nearest itself.
const PLAN := {
	"rhino": {
		"1": {"call": "horn_toss", "reach": 2.8, "min": 1, "aim": true},
		"2": {"call": "ground_pound", "reach": 2.0, "min": 1},
		"3": {"call": "brace", "reach": 6.0, "min": 1, "machines": true, "low": 0.75},
		"4": {"call": "stampede", "reach": 9.0, "min": 1, "machines": true, "aim": true},
	},
	"gorilla": {
		"1": {"call": "hex_shield", "reach": 8.0, "min": 1, "low": 0.6},
		"2": {"call": "fault_line", "reach": 6.0, "min": 1, "arg": "target"},
		"3": {"call": "bound", "reach": 6.0, "min": 1, "machines": true, "aim": true},
		"4": {"call": "chest_beat_ult", "reach": 5.0, "min": 2, "high": 0.5},  # the cage holds both teams (Preston, 2026-11-09): only while healthy
	},
	"fennec": {
		"1": {"call": "sand_kick", "reach": 2.6, "min": 1, "aim": true},
		"2": {"call": "blink_gate", "reach": 4.0, "min": 1, "arg": "target"}, # snaps back after bot_return_after
		"3": {"call": "tunnel", "reach": 8.0, "min": 1, "machines": true, "low": 0.35, "arg": "away"},
		"4": {"call": "sonic_boom", "reach": 4.0, "min": 2, "aim": true},
	},
	"kangaroo": { # picks from the kit's proposal numbers (kangaroo lane, 2026-11-11)
		"1": {"call": "hop_and_jab", "reach": 9.0, "min": 1, "machines": true, "aim": true}, # r13: leaps to a machine within 10 m under the aim
		"2": {"call": "tail_kick", "reach": 2.4, "min": 1, "aim": true},
		"3": {"call": "guard", "reach": 4.0, "min": 1, "machines": true, "low": 0.8},
		"4": {"call": "boxing_ring", "reach": 7.0, "min": 1, "machines": true, "aim": true}, # the title bout: a dive on a machine within bout_range (8 m edge)
	},
}
const SIGHT := 9.0 ## pick: how far it looks for a fight
const RETREAT_AT := 0.3 ## pick: health share that sends it home
const BACK_AT := 0.95 ## pick: health share at base before it returns to the lane

var director: MatchDirector
var hold := false ## a demo or check can park it
var side := 0.0 ## metres sideways in the lane, so two bots don't stand in one spot
var state := "lane" ## "lane" or "home"
var target: Node3D = null
var _m: Node3D
var _think := 0.0
var _path := PackedVector3Array()
var _path_i := 0
var _path_goal := Vector3(INF, 0, INF)
var _path_age := 0.0


func _ready() -> void:
	_m = get_parent()


func _physics_process(delta: float) -> void:
	if get_parent().has_meta("held_by"):return
	if director == null or not director.ready_to_play:
		return
	if MatchDirector.over or hold or not _m.alive:
		_m.move_override = Vector3.ZERO
		return
	_path_age += delta
	_think -= delta
	if _think <= 0.0:
		_think = 0.15
		_decide()
	_act()


func _home() -> Vector3:
	return director.spawns[_m.team]


func _decide() -> void:
	var share: float = _m.hp / _m.max_hp
	if state == "home":
		if MatchTeams.flat(_m.global_position - _home()).length() <= MatchRules.base_heal_radius - 1.0 and share >= BACK_AT:
			state = "lane"
	elif share < RETREAT_AT:
		state = "home"
		if _enemies_within(10.0, true).is_empty():
			director.start_recall(_m)
	if _m.taunted > 0.0 and MatchTeams.hittable(_m.taunted_by):
		target = _m.taunted_by
	elif state == "home":
		target = null
	else:
		target = _pick_target()


## Enemy machines and minions in sight, machines first when about as close; a tower or core only while our minions
## are under its fire. Camp monsters are left to the player.
func _pick_target() -> Node3D:
	var best: Node3D = null
	var best_score := INF
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if not MatchTeams.hittable(u) or not MatchTeams.is_enemy(u, _m) or MatchTeams.team_of(u) == "":
			continue
		var d := MatchTeams.edge_distance(_m, u)
		if d > SIGHT or not director.team_sees(_m.team, u):  # nothing its team cannot see (fog)
			continue
		var score := d
		if u.get("kind") == "tower" or u.get("kind") == "core":
			if not _wave_tanking(u):
				continue
			score += 4.0
		elif not MatchTeams.clear_line(_m, _m.global_position, u.global_position, 0.8):
			continue
		elif u.get("kind") == "minion":
			score += 1.5
		if score < best_score:
			best = u
			best_score = score
	return best


## Our minions are under this building and its tower isn't aiming at a machine.
func _wave_tanking(s: Node3D) -> bool:
	if s.get("kind") == "tower" and s.target != null and s.target.get("kind") == "machine":
		return false
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u.get("kind") == "minion" and MatchTeams.team_of(u) == _m.team \
				and MatchTeams.flat(u.global_position - s.global_position).length() <= MatchRules.tower_range + 1.0:
			return true
	return false


func _act() -> void:
	if director.recalls.has(_m):
		_m.move_override = Vector3.ZERO
		return
	for s: MatchStructure in director.structures.values():  # a tower aiming at it with no minions to take the fire
		if s.kind == "tower" and s.alive and s.target == _m and not _wave_tanking(s):
			_go(_home())
			return
	if state == "home":
		_go(_home())
		return
	if target != null and MatchTeams.hittable(target):
		_use_kit()
		if MatchTeams.edge_distance(_m, target) <= director.basic_range_of(_m) - 0.4:  # a melee kit's reach brings it in close
			_m.move_override = Vector3.ZERO
			_face(target)
			director.basic_attack(_m, target)
		else:
			_go(target.global_position)
		return
	_go(_lane_spot())


func _use_kit() -> void:
	var kit := _m.get_node_or_null("Kit")
	if kit == null or kit.get("current") != "":
		return
	var plan: Dictionary = PLAN.get(MatchTeams.machine_kind(_m), {})
	var share: float = _m.hp / _m.max_hp
	for slot in ["4", "3", "2", "1"]:
		var p: Dictionary = plan.get(slot, {})
		if p.is_empty() or not _m.slot_ready(slot) or (p.has("low") and share > p["low"]) or (p.has("high") and share < p["high"]):
			continue
		var near := _enemies_within(p["reach"], p.get("machines", false), p.get("edge", false))
		if near.size() < p.get("min", 1):
			continue
		var aim: Node3D = near[0]
		if p.get("aim", false):
			_face(aim)
		match p.get("arg", ""):
			"target":
				kit.call(p["call"], aim.global_position)
			"node":
				kit.call(p["call"], aim)
			"away":
				var length: float = kit.get("tunnel_length") if kit.get("tunnel_length") != null else 8.0
				kit.call(p["call"], _m.global_position + MatchTeams.flat(_home() - _m.global_position).normalized() * length)
			_:
				kit.call(p["call"])
		return


## Living enemy machines and minions within r (to the middle, or edge to edge with edge), nearest first.
func _enemies_within(r: float, machines_only: bool, edge := false) -> Array:
	var out: Array = []
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		var k: String = str(u.get("kind"))
		if k == "tower" or k == "core" or k == "monster" or (machines_only and k != "machine"):
			continue
		if MatchTeams.hittable(u) and MatchTeams.is_enemy(u, _m) and (MatchTeams.edge_distance(_m, u) if edge else MatchTeams.flat(u.global_position - _m.global_position).length()) <= r:
			out.append(u)
	out.sort_custom(func(a: Node3D, b: Node3D) -> bool:
		return a.global_position.distance_squared_to(_m.global_position) < b.global_position.distance_squared_to(_m.global_position))
	return out


## Just behind the front minion of its own wave, a little to one side; at its own tower when no wave is out.
func _lane_spot() -> Vector3:
	var front: Node3D = null
	for u: Node3D in get_tree().get_nodes_in_group("match_unit"):
		if u.get("kind") == "minion" and MatchTeams.team_of(u) == _m.team and (front == null or u.path_index > front.path_index):
			front = u
	if front != null:
		var back := MatchTeams.flat(_home() - front.global_position).normalized()
		return front.global_position + back * 2.5 + Vector3(side, 0, 0)
	var tower: MatchStructure = director.structures.get(_m.team.capitalize() + "Tower")
	var ahead := Vector3(0, 0, -1) if _m.team == "blue" else Vector3(0, 0, 1)
	return tower.global_position + ahead * 5.0 + Vector3(side, 0, 0)


func _face(t: Node3D) -> void:
	var to := MatchTeams.flat(t.global_position - _m.global_position)
	if to.length() > 0.01:
		_m.facing = to.normalized()


## Walks toward p: straight when the way is clear and short, else along the nav mesh.
func _go(p: Vector3) -> void:
	var pos := _m.global_position
	var to := MatchTeams.flat(p - pos)
	if to.length() < 0.6:
		_m.move_override = Vector3.ZERO
		return
	if to.length() < 10.0 and MatchTeams.clear_line(_m, pos, p, 0.8):
		_m.move_override = to.normalized()
		return
	if _path_age > 1.0 or MatchTeams.flat(p - _path_goal).length() > 2.0 or _path_i >= _path.size():
		_path = NavigationServer3D.map_get_path(_m.get_world_3d().navigation_map, pos, p, true)
		_path_i = 0
		_path_goal = p
		_path_age = 0.0
	while _path_i < _path.size() and MatchTeams.flat(_path[_path_i] - pos).length() < 0.7:
		_path_i += 1
	if _path_i >= _path.size():
		_m.move_override = to.normalized()
		return
	_m.move_override = MatchTeams.flat(_path[_path_i] - pos).normalized()
