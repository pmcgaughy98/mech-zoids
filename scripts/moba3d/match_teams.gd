class_name MatchTeams
extends RefCounted
## Who is whose enemy in the match (Claude, 2026-11-04, game feel lane). Every fighting thing in a match is in group
## "match_unit" with a `team` ("blue", "red", or "" for a camp monster), a `kind` ("machine", "minion", "monster",
## "tower", "core"), `alive`, radius() and take_damage(amount, by). Outside a match a machine's team is "", and the kits
## keep their test groups (kit_target for enemies, kit_ally for allies), so the reveals and field tests work as before.

const COLOURS := {"blue": Color(0.35, 0.62, 1.0), "red": Color(1.0, 0.34, 0.28), "": Color(1.0, 0.78, 0.3)}

## The machine whose kit asked for targets last. A toss or a shove (toss_to, knock_aside) carries no attacker, so its
## hit is credited here; the kits ask for targets in the same frame they start one.
static var caster: Node3D = null


static func team_of(n: Variant) -> String: ## untyped: a unit can be freed between checks
	if not is_instance_valid(n):
		return ""
	var t: Variant = (n as Object).get("team")
	return t if t is String else ""


## What a machine's kit may hit: every living, hittable enemy unit that is not a building (kits leave towers and cores alone).
static func enemies_of(m: Node) -> Array:
	var t := team_of(m)
	if t == "":
		return m.get_tree().get_nodes_in_group("kit_target")
	caster = m
	return m.get_tree().get_nodes_in_group("match_unit").filter(func(u: Node) -> bool:
		# hittable, not just alive: the kangaroo's title bout marks its pair "untouchable", and Preston (2026-11-11):
		# "Yes, block them" for area attacks too. Same rule towers, minions and bots already use.
		return hittable(u) and team_of(u) != t and u.get("kind") != "tower" and u.get("kind") != "core")


## The machines on a machine's own team (shields, the bound, the tunnel). The kits filter out the machine itself.
static func allies_of(m: Node) -> Array:
	var t := team_of(m)
	if t == "":
		return m.get_tree().get_nodes_in_group("kit_ally")
	return m.get_tree().get_nodes_in_group("match_unit").filter(func(u: Node) -> bool:
		return u.get("alive") == true and team_of(u) == t and u.get("kind") == "machine")


static func is_enemy(a: Variant, b: Variant) -> bool:
	return team_of(a) != team_of(b)


static func flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


## From a's middle to b's edge, on the ground (the 2D skeleton's _edge_distance).
static func edge_distance(a: Node3D, b: Node3D) -> float:
	var r: float = b.radius() if b.has_method("radius") else 0.0
	return flat(b.global_position - a.global_position).length() - r


## Whether b can be hit right now (a core only once its tower has fallen).
static func hittable(b: Variant) -> bool:
	if not is_instance_valid(b) or b.get("alive") != true:
		return false
	return b.can_be_hit() if b.has_method("can_be_hit") else true


## "Blue rhino", "Red minion", "camp monster", "Red tower".
static func unit_name(u: Variant) -> String:
	if not is_instance_valid(u):
		return "something"
	var k: String = str(u.get("kind"))
	if k == "machine":
		k = machine_kind(u)
	var t := team_of(u)
	if t == "":
		return "camp monster" if k == "monster" else k
	return t.capitalize() + " " + k


## Which machine it is, read from its kit: "rhino", "gorilla" or "fennec".
static func machine_kind(m: Variant) -> String:
	if m is Node and m.has_meta("arena_machine"):return str(m.get_meta("arena_machine"))
	var kit: Node = m.get_node_or_null("Kit") if m is Node else null
	if kit is ApeKit:
		return "gorilla"
	if kit is FennecKit:
		return "fennec"
	if kit is WolfKit:
		return "wolf"
	if kit is KangarooKit:
		return "kangaroo"
	if kit is SquirrelKit:
		return "squirrel"
	if kit is HippoKit:
		return "hippo"
	if kit is ShoebillKit:
		return "shoebill"
	if kit != null and kit.get_script() != null and kit.get_script().resource_path.ends_with("/hummingbird_kit.gd"):
		return "hummingbird"  # that kit has no class_name (hummingbird session, 2026-11-06)
	if kit != null and kit.get_script() != null and kit.get_script().resource_path.ends_with("/lobster_kit.gd"):
		return "lobster"  # by path: LobsterKit is new and may not be in the class cache (2026-11-06)
	return "rhino"


## Line of sight on the ground between two points, at chest height: false when an arena wall or rock is in between.
static func clear_line(node: Node3D, a: Vector3, b: Vector3, h := 1.0) -> bool:
	return ArenaMotion.ray(node, Vector3(a.x, h, a.z), Vector3(b.x, h, b.z)).is_empty()
