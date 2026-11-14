extends Node3D
## Hippo Toxic Flood (ultimate), smooth style (hippo effects lane, 2026-11-12). Visual only, no kit edits. Kit plan
## (docs/plan/hippo-kit-pressure-2026-11-11.md, Preston): it blows all three tanks, a wave of toxic liquid rolls out,
## pushes enemies outward and leaves a wide poisoned lake; the hippo heals in its own lake; afterwards the tanks are empty.
## Listens to the 3D body's clip events (hippo 3D lane): Toxic_Flood 1.7 s: charge 0.05, rear_up 0.35, burst 0.75,
## drain_end 1.3. Structure from SMITE 2's Intoxicate (measured): one short bright beat, then a ragged liquid pool that
## lies for seconds.
##   charge:    the tank windows flare (MechLook.set_glow on "Hippo glow"), gas hisses from the back pipes
##   rear_up:   pressure gathers under it: the Piston Drop's pumping warning disc, small, timed to the burst
##   burst:     a small pale core (no light), a wall of liquid rolls out to the lake's edge and drops, the lake spreads
##              behind it, gas thrown out low
##   lying:     ripples, bubbles, fumes rising off the lake; the windows are dark (drained)
##   drain_end: a last hiss from the pipes. Over the lake's life the windows come back up to their normal glow.
## The lake radius and life are proposals for Preston.
const LAKE := preload("res://shaders/hippo_flood_lake.gdshader")
const GATHER := preload("res://shaders/hippo_drop_ground.gdshader")
const JET := preload("res://shaders/hippo_vent_jet.gdshader") ## the wave wall, upside down: solid at the floor
const DUST := preload("res://shaders/rhino_dust.gdshader")
const LOOK := preload("res://scripts/moba3d/mech_look.gd")
const GLOW_SURFACE := "Hippo glow"
const GLOW_NORMAL := 1.6 ## the hippo 3D lane's emission strength
const LIFT := 0.05
const HEAL := preload("res://shaders/hippo_heal_ring.gdshader")
const HEAL_TICK := 0.5 ## proposal: one visible pulse per heal tick; match the kit's tick when it exists
const POISON := preload("res://scripts/moba3d/hippo_poison_read.gd") ## fumes off enemies standing in the lake
var _poison_node = null


func _poison():
	if _poison_node == null or not is_instance_valid(_poison_node):
		_poison_node = POISON.new()
		_poison_node.name = "PoisonRead"
		_poison_node.actor = actor
		add_child(_poison_node)
	return _poison_node


@export var lake_radius := 6.0 ## proposal
@export var lake_life := 4.0 ## proposal: seconds the lake lies, its last second shrinking
@export var gas := Color(0.66, 0.40, 0.80)

var actor: Node3D
var _body: Object = null
var _lake: Dictionary = {}
var _gather: Dictionary = {}
var _wave: Dictionary = {}
var _puffs: Array = []
var _glow := GLOW_NORMAL
var _glow_target := GLOW_NORMAL
var _glow_rate := 4.0
var _fume_acc := 0.0
var _heal_acc := 0.0
var _heals: Array = []
var elapsed := 0.0
var log_rows: Array = []


func setup(p: Node3D) -> void:
	actor = p


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(actor):
		return
	_watch_body()
	_update_glow(delta)
	_update_gather(delta)
	_update_wave(delta)
	_update_lake(delta)
	_update_puffs(delta)
	_update_heals(delta)


func _watch_body() -> void:
	var b: Variant = actor.get("body")
	if b == null or b == _body or not is_instance_valid(b) or not b.has_signal("event"):
		return
	if _body != null and is_instance_valid(_body) and _body.event.is_connected(_on_event):
		_body.event.disconnect(_on_event)
	_body = b
	b.event.connect(_on_event)


func _on_event(clip: String, n: String, _damage: bool) -> void:
	if clip != "Toxic_Flood":
		return
	log_rows.append({"name": n, "time": elapsed})
	match n:
		"charge":
			actor.set_meta("hippo_glow_hold", true)  # the tank read gives the glow to the flood until the lake settles
			_glow_target = 4.5
			_glow_rate = 6.0
			for i in 3:
				_pipe_hiss(0.6)
		"rear_up":
			_start_gather()
			_pipe_hiss(1.0)
		"burst":
			_burst()
		"drain_end":
			_pipe_hiss(0.8)


# ---- the tank glow --------------------------------------------------------------------------------------------------

func _update_glow(delta: float) -> void:
	if _body == null or not is_instance_valid(_body):
		return
	var before := _glow
	_glow = move_toward(_glow, _glow_target, _glow_rate * delta)
	if not is_equal_approx(before, _glow):
		var n: int = LOOK.set_glow(_body, _glow, GLOW_SURFACE)
		if log_rows.size() < 200 and (is_equal_approx(_glow, _glow_target)):
			log_rows.append({"name": "glow %.2f (%d materials)" % [_glow, n], "time": elapsed})


# ---- gather, burst, wave, lake --------------------------------------------------------------------------------------

func _start_gather() -> void:
	var at := actor.global_position
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	var r := 2.2
	plane.size = Vector2.ONE * r * 1.3 * 2.0
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = GATHER
	m.set_shader_parameter("radius_m", r)
	m.set_shader_parameter("extent", 1.3)
	m.set_shader_parameter("erupt", 0.4)  # rear_up 0.35 to burst 0.75
	m.set_shader_parameter("pool_life", 0.01)
	m.set_shader_parameter("flash_mul", 0.0)
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * (LIFT + 0.005))
	_gather = {"node": g, "age": 0.0}


func _update_gather(delta: float) -> void:
	if _gather.is_empty():
		return
	_gather.age += delta
	_gather.node.material_override.set_shader_parameter("age", _gather.age)
	if _gather.age >= 0.42:
		_gather.node.queue_free()
		_gather = {}


func _burst() -> void:
	var at := actor.global_position
	_glow_target = 0.25  # tanks spent
	_glow_rate = 20.0
	_puff(at + Vector3.UP * 0.9 * _bs(), 2.2 * _bs(), Vector3.UP * 0.3, 0.22, Color(0.95, 0.85, 1.0), 0.55)  # the short pale beat
	for i in 10:
		var a := TAU * (i + randf() * 0.5) / 10.0
		var dir := Vector3(cos(a), 0, sin(a))
		_puff(at + dir * 1.4 + Vector3.UP * 0.3, 1.2, dir * 6.5 + Vector3.UP * 0.4, 0.6, gas, 0.55)
	# the lake
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * lake_radius * 1.25 * 2.0
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = LAKE
	m.set_shader_parameter("radius_m", lake_radius)
	m.set_shader_parameter("extent", 1.25)
	m.set_shader_parameter("life", lake_life)
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * LIFT)
	if not _lake.is_empty() and is_instance_valid(_lake.node):
		_lake.node.queue_free()
	_lake = {"node": g, "age": 0.0, "at": at}
	var kit: Node = actor.get_node_or_null("Kit")  # the kit's own lake numbers when it has them (slice 4)
	var tick: float = kit.get("lake_tick") if kit != null and kit.get("lake_tick") != null else HEAL_TICK
	var rad: float = kit.get("lake_radius") if kit != null and kit.get("lake_radius") != null else lake_radius
	_poison().add_zone(at, rad, lake_life, tick, "lake")  # enemies in the lake read as poisoned
	# the wave wall
	var w := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 1.0
	cyl.bottom_radius = 1.08
	cyl.height = 1.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 64
	cyl.rings = 4
	w.mesh = cyl
	var wm := ShaderMaterial.new()
	wm.shader = JET
	wm.set_shader_parameter("seed", randf() * 50.0)
	w.material_override = wm
	_place(w, at)
	_wave = {"node": w, "age": 0.0, "at": at}
	log_rows.append({"name": "lake", "time": elapsed, "radius": lake_radius})


func _update_wave(delta: float) -> void:
	if _wave.is_empty():
		return
	_wave.age += delta
	var t: float = _wave.age
	var k: float = 1.0 - pow(1.0 - clampf(t / 0.45, 0.0, 1.0), 3.0)
	var r: float = lerpf(1.2, lake_radius * 0.95, k)
	var h: float = lerpf(2.0, 0.3, k)  # the wall drops as it spreads (first take 1.5 barely read)
	var n: MeshInstance3D = _wave.node
	n.global_basis = Basis(Vector3.RIGHT * r, Vector3.DOWN * h, Vector3.FORWARD * r)
	n.global_position = _wave.at + Vector3.UP * h * 0.5
	var mat: ShaderMaterial = n.material_override
	mat.set_shader_parameter("age", t)
	mat.set_shader_parameter("fade", 1.0 - smoothstep(0.35, 0.55, t))
	if t >= 0.55:
		n.queue_free()
		_wave = {}


func _update_lake(delta: float) -> void:
	if _lake.is_empty():
		return
	_lake.age += delta
	_lake.node.material_override.set_shader_parameter("age", _lake.age)
	if _lake.age > 0.6:
		if actor.get_meta("hippo_glow_hold", false):
			actor.set_meta("hippo_glow_hold", false)  # hand the glow back: the tank read follows the drained tanks
		_glow_target = _glow
	# the heal read: while the hippo stands in its own lake, one pulse per heal tick
	var off: Vector3 = actor.global_position - _lake.at
	off.y = 0.0
	if _lake.age > 0.45 and _lake.age < lake_life - 0.5 and off.length() < lake_radius * 0.85:
		_heal_acc += delta
		if _heal_acc >= HEAL_TICK:
			_heal_acc = 0.0
			_heal_pulse()
	else:
		_heal_acc = HEAL_TICK * 0.8  # the first tick comes quickly after stepping (back) in
	_fume_acc += delta
	if _fume_acc >= 0.12 and _lake.age < lake_life - 0.8:
		_fume_acc = 0.0
		var a := randf() * TAU
		var d := sqrt(randf()) * lake_radius * 0.8
		_puff(_lake.at + Vector3(cos(a), 0, sin(a)) * d + Vector3.UP * 0.25, randf_range(0.9, 1.5), Vector3.UP * randf_range(0.4, 0.8), 1.2, gas, 0.4)
	if _lake.age >= lake_life:
		_lake.node.queue_free()
		_lake = {}


# ---- the heal read --------------------------------------------------------------------------------------------------

func _heal_pulse() -> void:
	var at := actor.global_position
	var c := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 1.15
	cyl.bottom_radius = 1.3
	cyl.height = 2.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 48
	c.mesh = cyl
	var cm := ShaderMaterial.new()
	cm.shader = HEAL
	cm.set_shader_parameter("mode", 0)
	cm.set_shader_parameter("seed", randf() * 40.0)
	c.material_override = cm
	_place(c, at + Vector3.UP * 1.0 * _bs())
	var f := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * 3.2
	f.mesh = plane
	var fm := ShaderMaterial.new()
	fm.shader = HEAL
	fm.set_shader_parameter("mode", 1)
	fm.set_shader_parameter("seed", randf() * 40.0)
	f.material_override = fm
	_place(f, at + Vector3.UP * (LIFT + 0.01))
	_heals.append({"band": c, "floor": f, "age": 0.0})
	log_rows.append({"name": "heal tick", "time": elapsed})


func _update_heals(delta: float) -> void:
	for h in _heals.duplicate():
		h.age += delta
		var t: float = h.age
		var at := actor.global_position
		# the floor ring draws in over the first 0.25 s, then the band runs up the body over 0.45 s
		h.floor.global_position = at + Vector3.UP * (LIFT + 0.01)
		h.floor.material_override.set_shader_parameter("rise", clampf(t / 0.25, 0.0, 1.0))
		h.band.global_position = at + Vector3.UP * 1.0 * _bs()
		h.band.material_override.set_shader_parameter("rise", clampf((t - 0.15) / 0.45, 0.0, 1.0))
		if t >= 0.6:
			h.band.queue_free()
			h.floor.queue_free()
			_heals.erase(h)


# ---- gas ------------------------------------------------------------------------------------------------------------

func _fwd() -> Vector3:
	var f: Vector3 = actor.get("facing") if actor.get("facing") != null else -actor.global_basis.z
	f.y = 0.0
	return f.normalized() if f.length() > 0.01 else Vector3.FORWARD


func _pipe_hiss(strength: float) -> void:
	var fwd := _fwd()
	var left := Vector3.UP.cross(fwd)
	var back := actor.global_position + (-fwd * 0.6 + Vector3.UP * 1.3) * _bs()  # the pack on its back
	for s in [-1.0, 1.0]:
		_puff(back + left * 0.45 * s * _bs(), 0.5 + 0.3 * strength, (left * s * 1.6 + Vector3.UP * 2.0) * strength, 0.5, gas, 0.5)


func _puff(at: Vector3, size: float, vel: Vector3, life: float, col: Color, strength: float) -> void:
	var q := MeshInstance3D.new()
	q.mesh = QuadMesh.new()
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("dust", col)
	m.set_shader_parameter("strength", strength)
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
		p.vel *= exp(-3.0 * delta)
		n.global_position += p.vel * delta
		n.scale = Vector3.ONE * p.size * (1.0 + 0.8 * p.age / p.life)
		n.material_override.set_shader_parameter("age", p.age)


func _exit_tree() -> void:
	if _body != null and is_instance_valid(_body):
		LOOK.set_glow(_body, GLOW_NORMAL, GLOW_SURFACE)  # never leave the windows dark
	if actor != null and is_instance_valid(actor):
		actor.set_meta("hippo_glow_hold", false)


func _place(node: Node3D, at: Vector3) -> Node3D:
	if node is GeometryInstance3D:
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


## The hippo 3D lane sets the body size per machine (profile "scale", 1.25 since 2026-11-12). Points on the body
## (mouth, legs, back, heights) follow it; the kit's gameplay radii stay in metres.
func _bs() -> float:
	var b: Variant = actor.get("body") if actor != null and is_instance_valid(actor) else null
	if b == null or not is_instance_valid(b):
		return 1.0
	var m: Variant = b.get("_model")
	return m.scale.x if m is Node3D else 1.0
