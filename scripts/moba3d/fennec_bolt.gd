class_name FennecBolt
extends Node3D
## The fennec's bolt (Claude, 2026-11-05, game feel lane, effects spin-off; Preston: "Draw the bolt"). The kit's
## two-faced shot fires one forward and one backward out of the small gate. A bolt flies level and stops at the first
## target its line passes, at a wall, or at the end of its reach, and bursts there. It deals nothing itself: it tells
## the kit what it struck (struck), and the kit does the hit and the slow.
## Art: tools/art/draw_fennec_bolt.py (art/fx/moba3d/fennec_bolt/), the gate's palette and texel (0.016 m). The sprite
## faces the camera on the tilted quad (tilted_fx_3d.gdshader); it is drawn at 16 screen angles and shows the one
## nearest the way it is moving on screen, so it points along its flight from every view. It leaves a line of sparks.
## Every length is a placeholder, not a balance number.
## dart (2026-11-05, Preston: "we need basic attacks"): the basic attack's shot on the same code. Half the bolt's size
## and violet (dart_sheet.png, same layout), no line of sparks. Where it strikes a target it bursts in its own small
## violet hit (dart_hit_sheet.png), laid on the target and nudged toward the camera so the body never hides it; a dart
## that runs out or meets a wall just sparks.

signal struck(target: Node3D) ## the first target in its line; the kit deals the hit
signal ended(at: Vector3, why: String) ## why: "target", "wall" or "reach"

const SCRIPT := "res://scripts/moba3d/fennec_bolt.gd"
const DIR := "res://art/fx/moba3d/fennec_bolt/"
const SHADER := preload("res://scripts/moba3d/tilted_fx_3d.gdshader")
const PX := 0.016 ## the fennec's texel
const CELL := 40 ## bolt and burst cells, texels
const ANGLES := 16 ## bolt_sheet rows: k x 22.5 degrees on screen, 0 pointing right, turning clockwise
const BOLT_MS := 50 ## each of the bolt's 4 frames
const FLASH := 0 ## burst_sheet rows
const IMPACT := 1
const SPARK := 2
const DART_HIT := 3 ## not a burst_sheet row: dart_hit_sheet.png, one row of its own
const BURST_MS := [[40, 50, 60, 60], [40, 50, 50, 60, 60, 70], [40, 50, 60, 70], [30, 40, 50, 60, 70]] ## per row, ms a frame
const HIT_ON_BODY := 0.6 ## how far the dart hit sits from where the dart stopped toward the target's middle (0 to 1)
const HIT_NUDGE := 0.4 ## metres the dart hit is moved toward the camera, so it draws over the target
const RADIUS := 0.2 ## metres either side of its line that still hit a target, plus the target's own radius
const SPARK_EVERY := 0.2 ## metres between the sparks it leaves

static var _bolt_mat: ShaderMaterial
static var _burst_mat: ShaderMaterial
static var _dart_mat: ShaderMaterial
static var _hit_mat: ShaderMaterial

var dir := Vector3.FORWARD ## level, normalised
var speed := 12.0 ## metres a second
var reach := 7.0 ## metres
var targets: Array = [] ## the enemies it can strike, read when fired
var travelled := 0.0
var why := "" ## how it ended (the checks read it)
var dart := false ## the basic attack's dart, not the two-faced shot's bolt
var _t := 0.0
var _spark_left := 0.0
var _quad: MeshInstance3D


## A bolt at from, flying along direction. A flash marks where it leaves. It is made from its path, not its class_name:
## until the editor or an import refreshes the class cache, FennecBolt is unknown as a value and the script won't compile.
static func fire(parent: Node, from: Vector3, direction: Vector3, aim_at: Array, spd := 12.0, rng := 7.0, is_dart := false) -> Node3D:
	var b = load(SCRIPT).new()
	b.dart = is_dart
	b.dir = _flat(direction).normalized()
	b.speed = spd
	b.reach = rng
	b.targets = aim_at
	parent.add_child(b)
	b.global_position = from
	burst(parent, SPARK if is_dart else FLASH, from)
	return b


## A one-shot burst from burst_sheet (FLASH, IMPACT or SPARK) or the dart's hit (DART_HIT) at pos, facing the camera.
static func burst(parent: Node, row: int, pos: Vector3) -> Node3D:
	if _burst_mat == null:
		_burst_mat = _material("burst_sheet.png")
	if row == DART_HIT and _hit_mat == null:
		_hit_mat = _material("dart_hit_sheet.png")
	var n := Burst.new()
	n.row = 0 if row == DART_HIT else row
	n.rows = 1 if row == DART_HIT else 3
	n.ms = BURST_MS[row]
	n.quad = _quad_for(_hit_mat if row == DART_HIT else _burst_mat)
	parent.add_child(n)
	n.global_position = pos
	return n


static func _flat(v: Vector3) -> Vector3:
	return Vector3(v.x, 0.0, v.z)


static func _material(file: String) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter("tex", SmallGate.tex_or_disk(DIR + file))
	m.set_shader_parameter("lift", 0.0)  # pivots on its middle: a bolt flies, it doesn't stand
	return m


static func _quad_for(mat: ShaderMaterial) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2.ONE * CELL * PX
	mi.mesh = q
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return mi


func _ready() -> void:
	if _bolt_mat == null:
		_bolt_mat = _material("bolt_sheet.png")
	if dart and _dart_mat == null:
		_dart_mat = _material("dart_sheet.png")
	_quad = _quad_for(_dart_mat if dart else _bolt_mat)
	_quad.name = "Dart" if dart else "Bolt"
	add_child(_quad)
	_show()


func _process(delta: float) -> void:
	_t += delta
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
			if not is_instance_valid(e) or not (e as Node3D).visible or e.get("alive") == false:
				continue
			var r: float = RADIUS + (float(e.call("body_radius")) if e.has_method("body_radius") else 0.35)
			var k := clampf(_flat(e.global_position - a).dot(seg) / seg.length_squared(), 0.0, 1.0)
			if _flat(e.global_position - (a + (b - a) * k)).length() <= r and k < best:
				best = k
				hit = e
	if hit != null:
		b = a + (b - a) * best
		how = "target"
	if not dart:
		_trail(a, b)
	global_position = b
	travelled += _flat(b - a).length()
	if how != "":
		_end(how, hit)
	else:
		_show()


func _end(how: String, hit: Node3D) -> void:
	why = how
	if hit != null:
		struck.emit(hit)
	if dart and hit != null:
		burst(get_parent(), DART_HIT, _on_body(hit))
	elif dart:
		burst(get_parent(), SPARK, global_position)
	else:
		burst(get_parent(), IMPACT if how != "reach" else FLASH, global_position)
	ended.emit(global_position, how)
	queue_free()


## Where the dart's hit shows: part way from where it stopped into the target, at the dart's height, then toward the
## camera. Without the nudge a dart coming at the camera ends behind the target and its body hides the hit.
func _on_body(hit: Node3D) -> Vector3:
	var mid := Vector3(hit.global_position.x, global_position.y, hit.global_position.z)
	var p := global_position.lerp(mid, HIT_ON_BODY)
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		p += (cam.global_position - p).normalized() * HIT_NUDGE
	return p


## Sparks every SPARK_EVERY metres along the stretch just flown.
func _trail(a: Vector3, b: Vector3) -> void:
	var d := _flat(b - a).length()
	var at := _spark_left
	while at < d:
		var p := a + (b - a) * (at / d)
		var lift := 0.03 if int(travelled / SPARK_EVERY + at / SPARK_EVERY) % 2 == 0 else -0.03
		burst(get_parent(), SPARK, p + Vector3.UP * lift)
		at += SPARK_EVERY
	_spark_left = at - d


## The frame for now and the angle nearest its flight on screen.
func _show() -> void:
	var f := int(_t * 1000.0 / BOLT_MS) % 4
	var k := 0
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		var p0 := cam.unproject_position(global_position)
		var p1 := cam.unproject_position(global_position + dir)
		k = posmod(roundi((p1 - p0).angle() / (TAU / ANGLES)), ANGLES)
	_quad.set_instance_shader_parameter("uv_rect", Vector4(f / 4.0, float(k) / ANGLES, 0.25, 1.0 / ANGLES))


## A one-shot row of burst_sheet that frees itself. burst() hands it its quad and timings.
class Burst extends Node3D:
	var row := 0
	var rows := 3 ## rows in its sheet: burst_sheet has 3, dart_hit_sheet 1
	var ms: Array = [] ## ms a frame
	var quad: MeshInstance3D
	var t := 0.0
	var _f := -1

	func _ready() -> void:
		add_child(quad)
		_frame(0)

	func _process(delta: float) -> void:
		t += delta
		var s := 0.0
		for i in ms.size():
			s += ms[i] / 1000.0
			if t < s:
				_frame(i)
				return
		queue_free()

	func _frame(i: int) -> void:
		if i == _f:
			return
		_f = i
		quad.set_instance_shader_parameter("uv_rect", Vector4(i / 6.0, float(row) / rows, 1.0 / 6.0, 1.0 / rows))
