class_name TestShot
extends Node3D
## A plain test projectile (Claude, 2026-11-04, game feel lane). The dummies have no attacks yet, so the arena check and
## the playable arena fire these to try the walls and the gorilla's hex dome. A small glowing ball flying flat at chest
## height, like a missile in Doom's P_XYMovement: it stops at the first thing that blocks it, it never slides.
##   Arena walls stop every shot.
##   Hex dome (moba-kits.md, Gorilla; Preston, 2026-11-04): no shot crosses the wall, from either side. An enemy shot
##   wears it down (HexShield.damage); an ally shot only flashes it (Preston: "nvm allies shouldn't pass through
##   thatd be too op"; ally shots leaving the health alone is Mech-Zoids' default, his to change).
## Speed, reach and damage are placeholders; the numbers are Preston's.

const CHEST := 0.9 ## flight height above the ground
const HIT_R := 0.5 ## how close to its target counts as a hit

@export var speed := 14.0 ## placeholder
@export var damage := 10.0 ## placeholder: what one shot takes off a hex dome wall's health
@export var reach := 30.0 ## placeholder: it fades out after this far

var enemy := true ## fired by the enemy team
var target: Node3D ## optional: something to hit when it gets there
var team := "" ## in a match: the shooter's team (a dome of the same team only flashes)
var hp_damage := 0.0 ## in a match: health it takes off what it hits (MatchRules.basic_damage, a placeholder)
var source: Node3D = null ## in a match: who fired it, for the kill feed and tower switching
var stopped_by := "" ## "dome", "wall", "target", "reach", or "" while flying (the checks read it)
var _dir := Vector3.FORWARD
var _gone := 0.0


## Fires a shot from a machine or dummy standing at `from` toward `toward` (both at ground height).
static func fire(parent: Node, from: Vector3, toward: Vector3, enemy_team := true, hit_node: Node3D = null) -> TestShot:
	var s := TestShot.new()
	s.enemy = enemy_team
	s.target = hit_node
	var d := Vector3(toward.x - from.x, 0.0, toward.z - from.z)
	s._dir = d.normalized() if d.length() > 0.01 else Vector3.FORWARD
	parent.add_child(s)
	s.global_position = Vector3(from.x, from.y + CHEST, from.z)  # from the shooter itself, so no wall is skipped
	return s


func _ready() -> void:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.albedo_color = Color(1.0, 0.45, 0.25) if enemy else Color(0.45, 0.75, 1.0)
	var mesh := SphereMesh.new()
	mesh.radius = 0.12
	mesh.height = 0.24
	mesh.radial_segments = 8
	mesh.rings = 4
	mesh.material = m
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	add_child(mi)


func _process(delta: float) -> void:
	if stopped_by != "":
		return
	var a := global_position
	var b := a + _dir * speed * delta
	var wall := ArenaMotion.ray(self, a, b)
	if not wall.is_empty():
		if _at_building(wall.position):  # a tower or core is solid: reaching its side is the hit
			_land(a)
			_stop(wall.position, "target")
		else:
			_stop(wall.position, "wall")
		return
	for dome: HexShield in HexShield.live_domes():
		var c := dome.global_position
		var ra := Vector2(a.x - c.x, a.z - c.z).length()
		var rb := Vector2(b.x - c.x, b.z - c.z).length()
		if (ra <= dome.radius) != (rb <= dome.radius) and dome.blocks_at((a + b) * 0.5):  # it would cross the wall (a broken panel lets it through)
			var mid := (a + b) * 0.5
			var out := Vector3(mid.x - c.x, 0.0, mid.z - c.z).normalized()
			var hostile := enemy if team == "" else team != str(dome.get_meta("team", ""))
			if hostile:
				dome.damage(damage, c + out * dome.radius + Vector3(0, mid.y - c.y, 0))  # the ripple where it struck (2026-11-09)
			else:
				dome.hit(c + out * dome.radius + Vector3(0, mid.y - c.y, 0))  # the flash only
			_stop(Vector3(c.x, a.y, c.z) + out * dome.radius, "dome")
			return
	if is_instance_valid(target) and Vector2(b.x - target.global_position.x, b.z - target.global_position.z).length() <= HIT_R:
		_land(a)
		_stop(b, "target")
		return
	global_position = b
	_gone += speed * delta
	if _gone >= reach:
		_stop(b, "reach")


func _stop(at: Vector3, why: String) -> void:
	stopped_by = why
	if why == "dome" or why == "wall":
		Fx3D.spawn(get_parent(), "deflect_spark", at, 0.3)
	elif why == "target":
		Fx3D.spawn(get_parent(), "hit_spark", at, 0.3)
	visible = false
	get_tree().create_timer(2.0).timeout.connect(queue_free)  # kept a moment so checks can read stopped_by


## What reaching the target does: a machine's kit passive has the first say (plating, shields); in a match it then
## takes hp_damage (a blocked hit takes MatchRules.blocked_share of it).
func _land(a: Vector3) -> void:
	var kit := target.get_node_or_null("Kit")
	var blocked := false
	if kit != null and kit.has_method("take_hit"):
		blocked = kit.take_hit(a)
	elif target.has_method("hit") and hp_damage <= 0.0:
		target.hit()
	if hp_damage > 0.0 and target.has_method("take_damage"):
		target.take_damage(hp_damage * (MatchRules.blocked_share if blocked else 1.0), source if is_instance_valid(source) else null)  # the shooter may be gone


func _at_building(p: Vector3) -> bool:
	if not is_instance_valid(target) or not target.has_method("radius") or not (target.get("kind") in ["tower", "core"]):
		return false
	return Vector2(p.x - target.global_position.x, p.z - target.global_position.z).length() <= target.radius() + 0.6
