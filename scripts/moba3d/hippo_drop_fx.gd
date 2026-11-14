extends Node3D
## Hippo Piston Drop (slot 2, the belly flop clip), smooth style (hippo effects lane, 2026-11-11). Visual only, no kit
## edits. Listens to the 3D body's clip events (MechModel3D.event):
##   Belly_Flop: push_off 0.22, hit 0.72, get_up 0.98 (hippo 3D lane, round 7)
## Kit plan (docs/plan/hippo-kit-pressure-2026-11-11.md): the landing pumps pressure into the floor and about 0.5 s
## later the ground erupts and stuns. Bacchus's delayed burp stun, moved to the dive (Preston). Toxic purple, like the
## Vent. The eruption is timed here from the landing until the kit emits its own cue; the stun itself is the kit's.
##   push_off: gas blasts down from the legs, a little toxic gas left on the take-off spot
##   hit:      a thin liquid shock ring rolls out, a little gas thrown up, the warning starts (a pumping rim, veins)
##   +0.5 s:   a short pale core, a ring curtain of liquid and a central geyser shoot up, then a toxic pool that
##             bubbles and shrinks away
## Radius and the 0.5 s are proposals for Preston.
const GROUND := preload("res://shaders/hippo_drop_ground.gdshader")
const JET := preload("res://shaders/hippo_vent_jet.gdshader") ## reused for the geysers: solid at its narrow end
const DUST := preload("res://shaders/rhino_dust.gdshader") ## reused as toxic gas
const LIFT := 0.045
const EXTENT := 1.3

@export var radius_m := 3.2 ## proposal
@export var erupt_delay := 0.5 ## Preston: Bacchus has "about a half second before burp stuns"
@export var pool_life := 1.1
@export var gas := Color(0.66, 0.40, 0.80)

var actor: Node3D
var _body: Object = null
var _rows: Array = []
var _puffs: Array = []
var elapsed := 0.0
var log_rows: Array = []


func setup(p: Node3D) -> void:
	actor = p


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(actor):
		return
	_watch_body()
	_update_rows(delta)
	_update_puffs(delta)


func _watch_body() -> void:
	var b: Variant = actor.get("body")
	if b == null or b == _body or not is_instance_valid(b) or not b.has_signal("event"):
		return
	if _body != null and is_instance_valid(_body) and _body.event.is_connected(_on_event):
		_body.event.disconnect(_on_event)
	_body = b
	b.event.connect(_on_event)


func _on_event(clip: String, n: String, _damage: bool) -> void:
	if clip.to_lower() != "belly_flop":
		return
	log_rows.append({"name": n, "time": elapsed, "at": actor.global_position})
	match n:
		"push_off":
			_push_off()
		"hit":
			_land()


func _push_off() -> void:
	var at := actor.global_position
	var fwd := _fwd()
	var side := fwd.cross(Vector3.UP).normalized()
	for leg0 in [fwd * 0.8 + side * 0.5, fwd * 0.8 - side * 0.5, -fwd * 0.8 + side * 0.5, -fwd * 0.8 - side * 0.5]:
		var leg: Vector3 = leg0 * _bs()
		var out: Vector3 = (leg as Vector3).normalized()
		_puff(at + leg + Vector3.UP * 0.15, 0.8, out * 2.4 + Vector3.UP * 0.2, 0.55)
	_puff(at + Vector3.UP * 0.3 * _bs(), 1.3 * _bs(), Vector3.UP * 0.4, 0.9)


func _land() -> void:
	var at := actor.global_position
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * radius_m * EXTENT * 2.0
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = GROUND
	m.set_shader_parameter("radius_m", radius_m)
	m.set_shader_parameter("extent", EXTENT)
	m.set_shader_parameter("erupt", erupt_delay)
	m.set_shader_parameter("pool_life", pool_life)
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * LIFT)
	for i in 6:  # gas thrown up low around the belly
		var a := TAU * (i + randf() * 0.5) / 6.0
		var dir := Vector3(cos(a), 0, sin(a))
		_puff(at + dir * 1.0 + Vector3.UP * 0.2, 0.9, dir * 3.0 + Vector3.UP * 0.3, 0.5)
	_rows.append({"age": 0.0, "at": at, "ground": g, "erupted": false, "geysers": []})


func _erupt(row: Dictionary) -> void:
	row.erupted = true
	log_rows.append({"name": "erupt", "time": elapsed, "at": row.at})
	# the ring curtain at the rim, and one central column (the Vent's jet shader, upside down)
	row.geysers.append(_geyser(row.at, radius_m * 0.85, radius_m * 0.95, 0.9))  # a low splash wall; 1.6 m read as a box
	row.geysers.append(_geyser(row.at, 0.35, 0.7, 1.7))
	for i in 5:  # gas rising off the eruption
		var a := TAU * (i + randf() * 0.5) / 5.0
		_puff(row.at + Vector3(cos(a), 0, sin(a)) * randf_range(0.5, radius_m * 0.8) + Vector3.UP * 0.4, 1.2, Vector3.UP * 1.2, 1.0)


func _geyser(at: Vector3, r_ground: float, r_top: float, height: float) -> Dictionary:
	var node := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = r_ground  # +Y is flipped to point down, so the "top" ring sits on the floor
	cyl.bottom_radius = r_top
	cyl.height = 1.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 48
	cyl.rings = 4
	node.mesh = cyl
	var m := ShaderMaterial.new()
	m.shader = JET
	m.set_shader_parameter("seed", randf() * 50.0)
	node.material_override = m
	_place(node, at)
	node.global_basis = Basis(Vector3.RIGHT, Vector3.DOWN, Vector3.FORWARD)  # +Y down, not mirrored
	return {"node": node, "h": height, "age": 0.0}


func _update_rows(delta: float) -> void:
	for row in _rows.duplicate():
		row.age += delta
		row.ground.material_override.set_shader_parameter("age", row.age)
		if not row.erupted and row.age >= erupt_delay:
			_erupt(row)
		for gy in row.geysers:
			gy.age += delta
			var t: float = gy.age
			var rise: float = 1.0 - pow(1.0 - clampf(t / 0.15, 0.0, 1.0), 3.0)
			var h: float = maxf(0.05, gy.h * rise)
			var n: MeshInstance3D = gy.node
			n.scale = Vector3(1.0, h, 1.0)
			n.global_position = row.at + Vector3.UP * h * 0.5
			var mat: ShaderMaterial = n.material_override
			mat.set_shader_parameter("age", t)
			mat.set_shader_parameter("fade", 0.7 * (1.0 - smoothstep(0.08, 0.38, t)))
			n.visible = t < 0.38
		if row.age >= erupt_delay + pool_life:
			row.ground.queue_free()
			for gy in row.geysers:
				if is_instance_valid(gy.node):
					gy.node.queue_free()
			_rows.erase(row)


func _fwd() -> Vector3:
	var f: Vector3 = actor.get("facing") if actor.get("facing") != null else -actor.global_basis.z
	f.y = 0.0
	return f.normalized() if f.length() > 0.01 else Vector3.FORWARD


func _puff(at: Vector3, size: float, vel: Vector3, life: float) -> void:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	q.mesh = quad
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("dust", gas)
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
		p.vel *= exp(-3.0 * delta)
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


## The hippo 3D lane sets the body size per machine (profile "scale", 1.25 since 2026-11-12). Points on the body
## (mouth, legs, back, heights) follow it; the kit's gameplay radii stay in metres.
func _bs() -> float:
	var b: Variant = actor.get("body") if actor != null and is_instance_valid(actor) else null
	if b == null or not is_instance_valid(b):
		return 1.0
	var m: Variant = b.get("_model")
	return m.scale.x if m is Node3D else 1.0
