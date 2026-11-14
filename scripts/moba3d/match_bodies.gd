class_name MatchBodies
extends RefCounted
## Body collision between the match's machines, minions and camp monsters (Claude, 2026-11-04, game feel lane).
## Two parts:
##   block(): a walk may not carry a body into another one. The move keeps its sideways part, so a body slides round
##            whatever stands in its way, and one stuck squarely behind another steps to a side.
##   separate(): bodies that overlap anyway (spawns, respawns, tosses, a charge or leap the kits drive) are eased apart
##            each physics frame, the lighter one moving more. The director calls it.
## Kit-driven moves (charge, bound, tunnel, tosses, shoves) are not blocked; they push through and separate() sorts it
## out after. Towers and cores are the map lane's solid bodies, which ArenaMotion already slides along.
## Outside a match no unit is in "match_unit", so the reveals and field tests are untouched.
## THE NUMBERS ARE PLACEHOLDERS: MASS and SEPARATE_SPEED.

const MASS := {"machine": 4.0, "monster": 3.0, "minion": 1.0}
const SEPARATE_SPEED := 3.0 ## m/s: how fast overlapping bodies are eased apart


## Whether u is a body others bump into: alive, on the ground, shown, and a machine, minion or monster.
static func solid(u: Variant) -> bool:
	if is_instance_valid(u) and u.has_meta("held_by"):return false
	if not is_instance_valid(u) or u.get("alive") != true or not MASS.has(str(u.get("kind"))):
		return false
	var n := u as Node3D
	return n.is_visible_in_tree() and float(n.get("air") if n.get("air") != null else 0.0) <= 0.05


## Where a walk from `from` toward `to` ends once no other body is entered. r is the walker's radius.
static func block(node: Node3D, from: Vector3, to: Vector3, r: float, ignore_minions:=false) -> Vector3:
	if not node.is_in_group("match_unit"):
		return to
	var p := to
	for u: Node3D in node.get_tree().get_nodes_in_group("match_unit"):
		if ignore_minions and u.get("kind")=="minion":continue
		if u == node or not solid(u):
			continue
		var c := MatchTeams.flat(u.global_position)
		var gap: float = r + u.radius()
		var off := MatchTeams.flat(p) - c
		var d := off.length()
		if d >= gap:
			continue
		var back := MatchTeams.flat(from) - c
		var was := back.length()
		if d >= was - 0.0001:
			continue  # moving away from it or round it: always allowed, so overlapping bodies can part
		var keep := minf(gap, was)  # never closer than the edge, or than it already was
		var n := off / d if d > 0.001 else (back / was if was > 0.001 else Vector3.RIGHT)
		var q := c + n * keep
		var step := MatchTeams.flat(to - from).length()
		if MatchTeams.flat(q - from).length() < step * 0.3 and keep > 0.01:
			# squarely behind it: step round it, on whichever side lands nearer where the walk was going (a fixed side
			# per body when both are level, so it never dithers between the two)
			var b := back / was if was > 0.001 else n
			var q1 := c + b.rotated(Vector3.UP, step / keep) * keep
			var q2 := c + b.rotated(Vector3.UP, -step / keep) * keep
			var d1 := q1.distance_to(MatchTeams.flat(to))
			var d2 := q2.distance_to(MatchTeams.flat(to))
			if absf(d1 - d2) < 0.0005:
				q = q1 if node.get_instance_id() % 2 == 0 else q2
			else:
				q = q1 if d1 < d2 else q2
		p = Vector3(q.x, to.y, q.z)
	return p


## Eases every overlapping pair apart this frame. A body mid-ability (busy), mid-throw or mid-shove holds still and the
## other one moves the whole way.
static func separate(tree: SceneTree, delta: float) -> void:
	var units := tree.get_nodes_in_group("match_unit").filter(func(u: Node) -> bool: return solid(u))
	for i in units.size():
		var a: Node3D = units[i]
		for j in range(i + 1, units.size()):
			var b: Node3D = units[j]
			var off := MatchTeams.flat(a.global_position - b.global_position)
			var gap: float = a.radius() + b.radius()
			var d := off.length()
			if d >= gap:
				continue
			var n := off / d if d > 0.001 else Vector3.RIGHT.rotated(Vector3.UP, float(a.get_instance_id() % 628) * 0.01)
			var push := minf(gap - d, SEPARATE_SPEED * delta)
			var ia := _give(a)
			var ib := _give(b)
			if ia + ib <= 0.0:
				continue
			_nudge(a, n * push * ia / (ia + ib))
			_nudge(b, -n * push * ib / (ia + ib))


## How readily a body gives way: 1 / its weight, and 0 for one that must not be moved now.
static func _give(u: Node3D) -> float:
	var m := _mass(u)
	return 1.0 / m if m > 0.0 else 0.0


## A body's weight in separate(); 0 for one that must not be moved now.
static func _mass(u: Node3D) -> float:
	if u.get("busy") == true or (u.has_method("_forced") and u._forced()):
		return 0.0
	var tw: Variant = u.get("_move_tw")
	if tw is Tween and (tw as Tween).is_valid() and (tw as Tween).is_running():
		return 0.0
	return MASS[str(u.get("kind"))]


## Moves u by v on the ground; arena walls still stop it.
static func _nudge(u: Node3D, v: Vector3) -> void:
	if v.length() < 0.00001 or _mass(u) <= 0.0:
		return
	var y := u.global_position.y
	var q := ArenaMotion.slide(u, u.global_position, v, u.radius())
	u.global_position = Vector3(q.x, y, q.z)
