extends Node3D
## The squirrel's signal dart (Claude, squirrel mech session, 2026-11-05; Preston: "Build it"). Kit design: the squirrel
## section of docs/plan/moba-kits.md and docs/plan/squirrel-ratatoskr-kit-2026-11-05.md.
## A short amber dash that flies level and stops at the first target its line passes, at a wall, or at the end of its
## reach. It deals nothing itself: it tells the kit what it struck (struck), and the kit does the hit and the Hearsay
## jump. Placeholder look: a plain glowing dash and the shared hit spark, until the dart's own effect is drawn (an art
## job, as the fennec's bolt was). Made from its path (SCRIPT), not a class_name, so it works before the editor
## refreshes the class cache. Every length is a starting number, not balance.

signal struck(target: Node3D) ## the first target in its line; the kit deals the hit
signal ended(at: Vector3, why: String) ## why: "target", "wall" or "reach"

const SCRIPT := "res://scripts/moba3d/squirrel_dart.gd"
const COLOUR := Color(1.0, 0.72, 0.22) ## amber, the accent of the eye lenses in the approved stills
const RADIUS := 0.15 ## metres either side of its line that still hit a target, plus the target's own radius
const LENGTH := 0.34 ## the dash, metres
const THICK := 0.06

static var _mat: StandardMaterial3D

var dir := Vector3.FORWARD ## level, normalised
var speed := 24.0 ## metres a second (the tower bolts' speed: a target strafing at 3.5 m/s moves under 1 m)
var reach := 7.0 ## metres
var targets: Array = [] ## the enemies it can strike, read when fired
var ignore: Array = [] ## never struck: the Hearsay jump skips the enemy it jumps from
var travelled := 0.0
var why := "" ## how it ended (the checks read it)
var data := {} ## the kit's notes on this dart: its number, whether it carries the jump


## A dart at from, flying along direction.
static func fire(parent: Node, from: Vector3, direction: Vector3, aim_at: Array, spd := 24.0, rng := 7.0) -> Node3D:
	var d = load(SCRIPT).new()
	d.dir = _flat(direction).normalized()
	d.speed = spd
	d.reach = rng
	d.targets = aim_at
	parent.add_child(d)
	d.global_position = from
	return d


static func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


func _ready() -> void:
	if _mat == null:
		_mat = StandardMaterial3D.new()
		_mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		_mat.albedo_color = COLOUR
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(THICK, THICK, LENGTH)
	mi.mesh = box
	mi.material_override = _mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	mi.name = "Dash"
	add_child(mi)
	if dir.length() > 0.001:
		basis = Basis.looking_at(dir, Vector3.UP)


func _process(delta: float) -> void:
	var step := speed * delta
	var last := step >= reach - travelled
	if last:
		step = maxf(reach - travelled, 0.0)
	var a := global_position
	var b := a + dir * step
	var how := "reach" if last else ""
	var wall := ArenaMotion.ray(self, a, b)
	if not wall.is_empty():
		b = (wall["position"] as Vector3) - dir * 0.05
		b.y = a.y
		how = "wall"
	var hit: Node3D = null
	var best := INF
	var seg := _flat(b - a)
	if seg.length() > 0.0001:
		for e in targets:
			if not is_instance_valid(e) or e in ignore or not (e as Node3D).visible or e.get("alive") == false:
				continue
			var r: float = RADIUS + (float(e.call("body_radius")) if e.has_method("body_radius") else 0.35)
			var k := clampf(_flat(e.global_position - a).dot(seg) / seg.length_squared(), 0.0, 1.0)
			if _flat(e.global_position - (a + (b - a) * k)).length() <= r and k < best:
				best = k
				hit = e
	if hit != null:
		b = a + (b - a) * best
		how = "target"
	global_position = b
	travelled += _flat(b - a).length()
	if how != "":
		_end(how, hit)


func _end(how: String, hit: Node3D) -> void:
	why = how
	if how != "reach":
		Fx3D.spawn(get_parent(), "hit_spark", global_position, 0.3)
	if hit != null:
		struck.emit(hit)
	ended.emit(global_position, how)
	queue_free()
