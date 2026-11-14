extends Node3D
## Hippo Vent (slot 1, the yawn clip), smooth style (hippo effects lane, 2026-11-11). Visual only, no kit edits.
## The hippo kit has no ability code yet, so this listens to the 3D body's clip events (MechModel3D.event):
##   Yawn: jaw_open 0.10, cone_start 0.35, hit 0.45, cone_end 0.95 (hippo 3D lane, round 7)
## When the game feel lane ports the kit and plays the clip, this fires with it. Structure from SMITE 2's Belch of the
## Gods, measured at 15 fps (docs/reference/hippo-fx-synthesis-2026-11-11.md):
##   cone_start: the whole cone is on the floor within a frame or two; a white-hot jet leaves the jaws
##   while open: streaks run outward, vapour puffs are thrown along the cone
##   each hit:   a bright band sweeps from the jaws to the far edge (Belch sweeps about every 0.4 s; ours, in a
##               0.6 s window, sweeps at cone_start, on hit and once more 0.25 s after)
##   cone_end:   the cone and jet are gone in about 0.12 s; the vapour already thrown drifts on and thins out
## Look (Preston, 2026-11-11): "Make it the purple liquid I want it to have a poisonous or toxic type effect. Or
## noxious". So a toxic violet liquid with a glowing sheen, noxious gas, and a bubbling puddle left behind that shrinks
## away over PUDDLE_LIFE. Purple is his named visual (it also matches the hippo's purple body); never red.
## Range and width are proposals for Preston (the kit has no numbers for the Vent yet).
const GROUND := preload("res://shaders/hippo_vent_ground.gdshader")
const JET := preload("res://shaders/hippo_vent_jet.gdshader")
const DUST := preload("res://shaders/rhino_dust.gdshader") ## reused as vapour: a soft billboard puff, blend_mix
const POOL := preload("res://shaders/hippo_flood_lake.gdshader") ## the landing puddle: the Toxic Flood lake, small and short
const LIFT := 0.04
const POISON := preload("res://scripts/moba3d/hippo_poison_read.gd") ## fumes off enemies standing in the puddle
var _poison_node = null


func _poison():
	if _poison_node == null or not is_instance_valid(_poison_node):
		_poison_node = POISON.new()
		_poison_node.name = "PoisonRead"
		_poison_node.actor = actor
		add_child(_poison_node)
	return _poison_node
const PUDDLE_LIFE := 3.0 ## seconds the toxic puddle takes to shrink away; matches the kit's 3 s damage puddle (game feel lane, 2026-11-12)

@export var range_m := 5.5 ## proposal: about 2.5 bites long
@export var half_angle_deg := 30.0 ## proposal: a 60 degree cone
@export var mouth_ahead := 1.65 ## metres from the hippo's centre to its jaws at the widest gape (hippo 3D lane: 1.6 to 1.7)
@export var pool_radius := 1.6 ## the kit's puddle_radius, centred 0.6 of range_m from the body (Preston: match the damage)
@export var mouth_up := 0.9 ## hippo 3D lane: 0.85 to 0.95 m during the yawn
@export var vapour := Color(0.66, 0.40, 0.80) ## noxious gas, light violet (dark violet vanished on the floor), under 1 so it never blooms

var actor: Node3D
var _body: Object = null
var _cone: Dictionary = {}
var _puffs: Array = []
var _spawn_acc := 0.0
var _kit: Node = null
var _air: Dictionary = {} ## the downward spray while Vent is held for the Piston Drop's landing
var _pools: Array = [] ## landing puddles
var elapsed := 0.0
var log_rows: Array = [] ## {name, time} for the checks


func setup(p: Node3D) -> void:
	actor = p


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(actor):
		return
	_watch_body()
	_tank()
	_update_cone(delta)
	_update_air(delta)
	_update_pools(delta)
	_update_puffs(delta)


func _watch_body() -> void:
	var k: Node = actor.get_node_or_null("Kit")  # the kit's cues: Vent pressed in the air has no clip of its own
	if k != null and k != _kit and k.has_signal("cue"):
		_kit = k
		k.cue.connect(_on_cue)
	var b: Variant = actor.get("body")
	if b == null or b == _body or not is_instance_valid(b) or not b.has_signal("event"):
		return
	if _body != null and is_instance_valid(_body) and _body.event.is_connected(_on_event):
		_body.event.disconnect(_on_event)
	_body = b
	b.event.connect(_on_event)


func _on_event(clip: String, n: String, _damage: bool) -> void:
	if clip.to_lower() != "yawn":
		return
	log_rows.append({"name": n, "time": elapsed})
	match n:
		"cone_start":
			_open()
		"hit":
			_sweep()
			_soak_victims()
			get_tree().create_timer(0.25).timeout.connect(_sweep)
		"cone_end":
			if not _cone.is_empty():
				_cone.closing = true


# ---- Vent in the air (game feel lane kit, 2026-11-12) ---------------------------------------------------------------
# Pressed during the Piston Drop's flight: the kit emits "vent_air", then on landing hits within vent_air_radius (2.6 m)
# and lays its puddle (puddle_radius 1.6 m, 3 s) at the landing spot. Here: a jet spraying down from the jaws that rides
# the arc, then a ring of gas thrown out to the hit circle and a round puddle on the landing (Toxic Flood's lake shader,
# small and short).

const AIR_HIT_R := 2.6 ## the kit's vent_air_radius

func _on_cue(n: String) -> void:
	match n:
		"vent_air":
			log_rows.append({"name": "vent_air", "time": elapsed})
			_air_open()
		"vent_puddle":  # the kit sets last_puddle just before this cue, ground spray and airborne landing alike
			var c: Variant = _kit.get("last_puddle")
			if c is Vector3:
				_poison().add_zone(c, pool_radius, _puddle_life(), 0.5, "puddle", _overcharged_now())
		"drop_land":
			if not _air.is_empty():
				log_rows.append({"name": "vent_air landing", "time": elapsed})
				_air_land()


func _air_open() -> void:
	_air_close()
	var j := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.14
	cyl.bottom_radius = 0.8
	cyl.height = 1.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 32
	cyl.rings = 4
	j.mesh = cyl
	var jm := ShaderMaterial.new()
	jm.shader = JET
	jm.set_shader_parameter("seed", randf() * 50.0)
	j.material_override = jm
	_place(j, actor.global_position)
	var gy: Variant = _kit.get("_ground_y") if _kit != null else null
	_air = {"jet": j, "age": 0.0, "ground": float(gy) if gy != null else 0.0, "acc": 0.0}
	_update_air(0.0)


func _update_air(delta: float) -> void:
	if _air.is_empty():
		return
	_air.age += delta
	if _air.age > 2.0:  # the landing never came (the drop was cut short): never leave a jet hanging
		_air_close()
		return
	var fwd := _aim()
	var mouth: Vector3 = actor.global_position + fwd * (mouth_ahead * _bs()) * 0.8 + Vector3.UP * (mouth_up * _bs()) * 0.7
	var spot := Vector3(mouth.x, float(_air.ground) + 0.05, mouth.z) + fwd * 0.6  # sprayed down and a little ahead
	var dir := spot - mouth
	var length := maxf(dir.length(), 0.3)
	dir = dir / length
	var j: MeshInstance3D = _air.jet
	var y := -dir
	var x := Vector3.UP.cross(dir)
	if x.length() < 0.01:
		x = fwd.cross(Vector3.UP)
	x = x.normalized()
	j.global_basis = Basis(x, y * length, x.cross(y).normalized())
	j.global_position = mouth + dir * length * 0.5
	var m: ShaderMaterial = j.material_override
	m.set_shader_parameter("age", _air.age)
	m.set_shader_parameter("fade", minf(1.0, _air.age / 0.06))
	_air.acc += delta
	while _air.acc >= 0.06:
		_air.acc -= 0.06
		var side := Vector3(randf_range(-1, 1), 0, randf_range(-1, 1)) * 0.4
		_puff(spot + side + Vector3.UP * 0.2, randf_range(0.5, 0.8), side * 3.0 + Vector3.UP * 0.4, 0.45)


func _air_land() -> void:
	var at := actor.global_position
	at.y = float(_air.ground)
	_air_close()
	for i in 12:  # gas thrown out to the hit circle
		var a := TAU * (i + randf() * 0.5) / 12.0
		var d := Vector3(cos(a), 0, sin(a))
		_puff(at + d * 0.8 + Vector3.UP * 0.3, randf_range(0.8, 1.1), d * AIR_HIT_R * 2.6, 0.5)
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * pool_radius * 1.25 * 2.0
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = POOL
	m.set_shader_parameter("radius_m", pool_radius)
	m.set_shader_parameter("extent", 1.25)
	m.set_shader_parameter("spread", 0.2)
	m.set_shader_parameter("life", _puddle_life())
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * (LIFT + 0.02))
	_pools.append({"node": g, "age": 0.0, "at": at, "acc": 0.0, "life": _puddle_life()})


func _air_close() -> void:
	if not _air.is_empty() and is_instance_valid(_air.jet):
		_air.jet.queue_free()
	_air = {}


func _update_pools(delta: float) -> void:
	for p in _pools.duplicate():
		p.age += delta
		p.node.material_override.set_shader_parameter("age", p.age)
		p.acc += delta
		if p.acc >= 0.25 and p.age < p.life - 0.6:
			p.acc = 0.0
			var a: float = randf() * TAU
			var r: float = sqrt(randf()) * pool_radius * 0.7
			_puff(p.at + Vector3(cos(a), 0, sin(a)) * r + Vector3.UP * 0.25, randf_range(0.8, 1.2), Vector3.UP * randf_range(0.5, 0.9), 1.1)
		if p.age >= p.life:
			p.node.queue_free()
			_pools.erase(p)


# ---- the cone ------------------------------------------------------------------------------------------------------

func _aim() -> Vector3:
	var f: Vector3 = actor.get("facing") if actor.get("facing") != null else -actor.global_basis.z
	f.y = 0.0
	return f.normalized() if f.length() > 0.01 else Vector3.FORWARD


func _open() -> void:
	_close_now()
	var fwd := _aim()
	var feet := actor.global_position
	var half := deg_to_rad(half_angle_deg)
	var apex := feet + fwd * ((mouth_ahead * _bs()) - 0.25)
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(2.0 * range_m * sin(half), range_m)
	g.mesh = plane
	var gm := ShaderMaterial.new()
	gm.shader = GROUND
	gm.set_shader_parameter("range_m", range_m)
	gm.set_shader_parameter("half_angle", half)
	gm.set_shader_parameter("pool_at", range_m * 0.6 - ((mouth_ahead * _bs()) - 0.25))  # the kit's puddle centre, from the apex
	gm.set_shader_parameter("pool_r", pool_radius)
	gm.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = gm
	_place(g, apex + fwd * range_m * 0.5 + Vector3.UP * LIFT)
	g.global_basis = Basis.looking_at(-fwd, Vector3.UP)  # +Z (UV.y) forward from the apex
	# the jet: an open cone mesh from the jaws, sloping down toward the far edge
	var mouth := feet + fwd * (mouth_ahead * _bs()) + Vector3.UP * (mouth_up * _bs())
	var far := feet + fwd * ((mouth_ahead * _bs()) + range_m * 0.8) + Vector3.UP * 0.35
	var dir := (far - mouth).normalized()
	var length := mouth.distance_to(far)
	var j := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.16
	cyl.bottom_radius = range_m * 0.8 * tan(half) * 0.7
	cyl.height = length
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 40
	cyl.rings = 6
	j.mesh = cyl
	var jm := ShaderMaterial.new()
	jm.shader = JET
	jm.set_shader_parameter("seed", randf() * 50.0)
	j.material_override = jm
	_place(j, mouth + dir * length * 0.5)
	var y := -dir  # the cylinder's top (+Y) at the jaws
	var x := Vector3.UP.cross(dir).normalized()
	j.global_basis = Basis(x, y, x.cross(y)).orthonormalized()
	_cone = {"age": 0.0, "ground": g, "jet": j, "fade": 1.0, "pulse": 0.0, "closing": false, "fwd": fwd, "apex": apex, "half": half, "residue": 0.0, "gas_acc": 0.0, "life": _puddle_life()}
	_sweep()


func _sweep() -> void:
	if not _cone.is_empty() and not _cone.closing:
		_cone.pulse = 1.0


func _update_cone(delta: float) -> void:
	if _cone.is_empty():
		return
	_cone.age += delta
	_cone.pulse = maxf(0.0, _cone.pulse - delta / 0.3)
	if _cone.closing:
		_cone.fade = maxf(0.0, _cone.fade - delta / 0.12)
		_cone.residue = maxf(0.0, _cone.residue - delta / _cone.get("life", PUDDLE_LIFE))  # the puddle shrinks from its edges
		_cone.gas_acc += delta
		if _cone.residue > 0.25 and _cone.gas_acc >= 0.22:  # fumes keep lifting off the puddle
			_cone.gas_acc = 0.0
			_gas_over_puddle()
	else:
		_cone.residue = minf(1.0, _cone.residue + delta / 0.4)
	for k in ["ground", "jet"]:
		var m: ShaderMaterial = _cone[k].material_override
		m.set_shader_parameter("age", _cone.age)
		m.set_shader_parameter("fade", _cone.fade)
		m.set_shader_parameter("pulse", _cone.pulse)
	_cone.ground.material_override.set_shader_parameter("residue", _cone.residue)
	_cone.jet.visible = _cone.fade > 0.0
	if not _cone.closing:
		_spawn_acc += delta
		while _spawn_acc >= 0.05:
			_spawn_acc -= 0.05
			_vapour_in_cone()
	if _cone.fade <= 0.0 and _cone.residue <= 0.0:
		_close_now()


func _close_now() -> void:
	if _cone.is_empty():
		return
	for k in ["ground", "jet"]:
		if is_instance_valid(_cone[k]):
			_cone[k].queue_free()
	_cone = {}


# ---- vapour --------------------------------------------------------------------------------------------------------

func _vapour_in_cone() -> void:
	var fwd: Vector3 = _cone.fwd
	var d := randf_range(0.6, range_m * 0.75)
	var a := randf_range(-_cone.half, _cone.half) * 0.8
	var dir := fwd.rotated(Vector3.UP, a)
	var at: Vector3 = _cone.apex + dir * d + Vector3.UP * lerpf(0.7, 0.35, d / range_m)
	_puff(at, lerpf(0.7, 1.5, d / range_m), dir * randf_range(2.5, 4.0) + Vector3.UP * 0.3, 0.6)


func _gas_over_puddle() -> void:
	var centre: Vector3 = _cone.apex + _cone.fwd * (range_m * 0.6 - ((mouth_ahead * _bs()) - 0.25))
	var a: float = randf() * TAU
	var r: float = sqrt(randf()) * pool_radius * 0.8 * float(_cone.residue)  # fumes stay over what is left of the puddle
	_puff(centre + Vector3(cos(a), 0, sin(a)) * r + Vector3.UP * 0.25, randf_range(0.8, 1.3), Vector3.UP * randf_range(0.5, 0.9), 1.1)


func _soak_victims() -> void:
	if _cone.is_empty():
		return
	var cos_half := cos(_cone.half)
	for e in MatchTeams.enemies_of(actor):
		if not (e is Node3D) or not MatchTeams.hittable(e):
			continue
		var to: Vector3 = e.global_position - _cone.apex
		to.y = 0.0
		if to.length() > range_m or to.length() < 0.01 or to.normalized().dot(_cone.fwd) < cos_half:
			continue
		for i in 3:
			var off := Vector3(randf_range(-0.3, 0.3), randf_range(0.4, 0.9), randf_range(-0.3, 0.3))
			_puff(e.global_position + off, 0.8, _cone.fwd * 1.5 + Vector3.UP * 0.6, 0.5)
		log_rows.append({"name": "soaked", "time": elapsed})


func _puff(at: Vector3, size: float, vel: Vector3, life: float) -> void:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	q.mesh = quad
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("dust", vapour)
	m.set_shader_parameter("strength", 0.55)
	q.material_override = m
	_place(q, at)
	q.scale = Vector3.ONE * size
	_puffs.append({"node": q, "age": 0.0, "life": life, "vel": vel, "size": size})


func _update_puffs(delta: float) -> void:
	for p in _puffs.duplicate():
		p.age += delta
		var n: MeshInstance3D = p.node
		if p.age >= p.life or not is_instance_valid(n):
			if is_instance_valid(n):
				n.queue_free()
			_puffs.erase(p)
			continue
		p.vel *= exp(-3.0 * delta)  # air drag: thrown fast, slows quickly
		n.global_position += p.vel * delta
		n.scale = Vector3.ONE * p.size * (1.0 + 0.8 * p.age / p.life)
		n.material_override.set_shader_parameter("age", p.age)


func _place(node: Node3D, at: Vector3) -> Node3D:
	if node is GeometryInstance3D:
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


## The kit's puddle length: puddle_life, times overcharge_puddle when the Vent went out overcharged (kit slice 4).
func _puddle_life() -> float:
	if _kit == null or not is_instance_valid(_kit):
		return PUDDLE_LIFE
	var base: Variant = _kit.get("puddle_life")
	var life: float = float(base) if base != null else PUDDLE_LIFE
	var clock: Variant = _kit.get("_clock")
	var until: Variant = _kit.get("_boost_until")
	var mul: Variant = _kit.get("overcharge_puddle")
	if clock != null and until != null and mul != null and float(clock) < float(until):
		life *= float(mul)
	return life


const TANK := preload("res://scripts/moba3d/hippo_tank_read.gd") ## the passive: liquid level and glow in the tank windows
var _tank_node = null


func _tank() -> void:
	if _tank_node == null or not is_instance_valid(_tank_node):
		_tank_node = TANK.new()
		_tank_node.name = "TankRead"
		_tank_node.actor = actor
		add_child(_tank_node)


## The overcharged Vent's puddle slows (kit slice 4): the same test the kit makes when it lays the puddle.
func _overcharged_now() -> bool:
	if _kit == null or not is_instance_valid(_kit):
		return false
	var clock: Variant = _kit.get("_clock")
	var until: Variant = _kit.get("_boost_until")
	return clock != null and until != null and float(clock) < float(until)


## The hippo 3D lane sets the body size per machine (profile "scale", 1.25 since 2026-11-12). Points on the body
## (mouth, legs, back, heights) follow it; the kit's gameplay radii stay in metres.
func _bs() -> float:
	var b: Variant = actor.get("body") if actor != null and is_instance_valid(actor) else null
	if b == null or not is_instance_valid(b):
		return 1.0
	var m: Variant = b.get("_model")
	return m.scale.x if m is Node3D else 1.0
