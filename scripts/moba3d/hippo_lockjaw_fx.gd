extends Node3D
## Hippo Lockjaw (slot 3), smooth style (hippo effects lane, 2026-11-12). Visual only, no kit edits. Preston: Lockjaw
## drags the enemy "into the lake" (docs/plan/hippo-kit-pressure-2026-11-11.md). Listens to the 3D body's clip events
## (MechModel3D.event; hippo 3D lane's clips):
##   Lockjaw_Clamp 0.5 s: capture 0.24.  Lockjaw_Carry 0.5 s loop: step 0.0, 0.25.  Lockjaw_Slam 0.85 s: slam 0.28, release 0.31.
## Moving the victim with the jaws is the kit's; this only draws.
##   capture: a short pale core at the bite, the jaw hinges hiss out toxic gas, a violet pressure band snaps shut
##            round the victim (the hold read sits on the victim, as SMITE does it)
##   held:    the band pulses; gas leaks from the hinges; purple liquid drips from the jaws and leaves a trail of
##            small puddles behind the drag
##   slam:    a toxic splash ring and pool where the victim hits the floor, the band bursts, the hinges vent again
## The mouth is tracked on the Jaw bone, calibrated at capture to the hippo 3D lane's measured mouth point.
const SPLASH := preload("res://shaders/hippo_drop_ground.gdshader")
const RING := preload("res://shaders/hippo_clamp_ring.gdshader")
const DUST := preload("res://shaders/rhino_dust.gdshader")
const CAPTURE_MOUTH := Vector3(0.012, 0.367, 1.643) ## hippo-local, +Z forward, +X the hippo's left (roster.json)
const LIFT := 0.05

@export var gas := Color(0.66, 0.40, 0.80)
@export var drip_color := Color(0.42, 0.12, 0.62)
@export var slam_radius := 1.8 ## proposal

var actor: Node3D
var _body: Object = null
var _held := false
var _kit: Node = null
var _off_clip := 0.0
var _jaw := -1
var _jaw_offset := Vector3.ZERO ## the mouth in the jaw bone's space, from the capture calibration
var _ring: MeshInstance3D
var _ring_age := 0.0
var _ring_burst := -1.0
var _leak_acc := 0.0
var _drip_acc := 0.0
var _drips: Array = []
var _splats: Array = []
var _puffs: Array = []
var _drip_mesh: SphereMesh
var _drip_mat: StandardMaterial3D
var elapsed := 0.0
var log_rows: Array = []


func setup(p: Node3D) -> void:
	actor = p
	_drip_mesh = SphereMesh.new()
	_drip_mesh.radius = 0.05
	_drip_mesh.height = 0.13
	_drip_mesh.radial_segments = 8
	_drip_mesh.rings = 4
	_drip_mat = StandardMaterial3D.new()  # wet and dark, never glowing: these are drops, not light balls
	_drip_mat.albedo_color = drip_color
	_drip_mat.roughness = 0.15
	_drip_mat.metallic_specular = 0.9


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(actor):
		return
	_watch_body()
	_update_ring(delta)
	if _held and _body != null and is_instance_valid(_body) and not str(_body.get("action")).begins_with("Lockjaw"):
		_off_clip += delta  # a frame or two of no clip between clamp and carry is normal
		if _off_clip > 0.2:
			_held = false  # broken free, or cut short: no slam or release came, so never drip forever
			log_rows.append({"name": "hold ended without release", "time": elapsed})
	else:
		_off_clip = 0.0
	if _held:
		_leak_acc += delta
		_drip_acc += delta
		if _leak_acc >= 0.16:
			_leak_acc = 0.0
			_hinge_gas(randf() < 0.5, 0.6)
		if _drip_acc >= 0.09:
			_drip_acc = 0.0
			_drip()
	_update_drips(delta)
	_update_splats(delta)
	_update_puffs(delta)


## The kit's cues (game feel lane, 2026-11-12): lockjaw_clamp only when the jaws caught someone, lockjaw_whiff on a miss,
## lockjaw_slam when the slam lands on a held enemy.
func _on_cue(n: String) -> void:
	match n:
		"lockjaw_clamp":
			log_rows.append({"name": "cue clamp", "time": elapsed})
			_capture()
		"lockjaw_slam":
			log_rows.append({"name": "cue slam", "time": elapsed})
			_slam()
		"lockjaw_whiff":
			log_rows.append({"name": "cue whiff", "time": elapsed})
			_hinge_gas(true, 0.5)  # the jaws snap on air: a small hiss, no band (the kit puts its own puff at the jaws)
			_hinge_gas(false, 0.5)


func _watch_body() -> void:
	var k: Node = actor.get_node_or_null("Kit")
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
	_jaw = -1
	var sk: Skeleton3D = b.get("skeleton")
	if sk != null:
		for i in sk.get_bone_count():
			if sk.get_bone_name(i).to_lower().contains("jaw"):
				_jaw = i
				break


func _on_event(clip: String, n: String, _damage: bool) -> void:
	if not clip.begins_with("Lockjaw"):
		return
	log_rows.append({"name": clip + ":" + n, "time": elapsed})
	match n:
		"capture":
			if _kit == null:  # with the kit, its cue says whether the jaws caught anyone (a whiff also fires capture)
				_capture()
		"slam":
			if _kit == null:
				_slam()
		"release":
			_held = false
			_hinge_gas(true, 1.0)
			_hinge_gas(false, 1.0)


# ---- where the jaws are ---------------------------------------------------------------------------------------------

func _fwd() -> Vector3:
	var f: Vector3 = actor.get("facing") if actor.get("facing") != null else -actor.global_basis.z
	f.y = 0.0
	return f.normalized() if f.length() > 0.01 else Vector3.FORWARD


func _local_to_world(v: Vector3) -> Vector3:
	var fwd := _fwd()
	var left := Vector3.UP.cross(fwd)
	var s := _bs()
	return actor.global_position + (left * v.x + Vector3.UP * v.y + fwd * v.z) * s


func _jaw_xform() -> Transform3D:
	var sk: Skeleton3D = _body.get("skeleton") if _body != null and is_instance_valid(_body) else null
	if sk == null or _jaw < 0:
		return Transform3D()
	return sk.global_transform * sk.get_bone_global_pose(_jaw)


## The mouth now: on the jaw bone once calibrated, else the measured capture point.
func mouth() -> Vector3:
	if _jaw >= 0 and _jaw_offset != Vector3.ZERO:
		return _jaw_xform() * _jaw_offset
	return _local_to_world(CAPTURE_MOUTH)


func _hinges() -> Array:
	var fwd := _fwd()
	var left := Vector3.UP.cross(fwd)
	var m := mouth()
	var back := m + (-fwd * 0.55 + Vector3.UP * 0.15) * _bs()
	return [back + left * 0.4, back - left * 0.4]


# ---- the moments ----------------------------------------------------------------------------------------------------

func _capture() -> void:
	if _jaw >= 0:
		_jaw_offset = _jaw_xform().affine_inverse() * _local_to_world(CAPTURE_MOUTH)
	_held = true
	var m := mouth()
	_puff(m, 0.7, Vector3.UP * 0.3, 0.25, Color(0.95, 0.85, 1.0), 0.6)  # the bite: a short pale core, no light
	_hinge_gas(true, 1.0)
	_hinge_gas(false, 1.0)
	if is_instance_valid(_ring):
		_ring.queue_free()
	_ring = MeshInstance3D.new()
	var t := TorusMesh.new()
	t.inner_radius = 0.62
	t.outer_radius = 0.78
	t.rings = 40
	t.ring_segments = 10
	_ring.mesh = t
	var mat := ShaderMaterial.new()
	mat.shader = RING
	mat.set_shader_parameter("seed", randf() * 30.0)
	_ring.material_override = mat
	_place(_ring, m)
	_ring_age = 0.0
	_ring_burst = -1.0


func _slam() -> void:
	var m := mouth()
	var at := Vector3(m.x, actor.global_position.y, m.z)
	_splash(at, slam_radius, 1.0, 0.9)
	for i in 6:
		var a := TAU * (i + randf() * 0.5) / 6.0
		var dir := Vector3(cos(a), 0, sin(a))
		_puff(at + dir * 0.6 + Vector3.UP * 0.2, 0.9, dir * 2.6 + Vector3.UP * 0.4, 0.5, gas, 0.55)
	_ring_burst = 0.0
	log_rows.append({"name": "slam_splash", "time": elapsed, "at": at})


func _update_ring(delta: float) -> void:
	if not is_instance_valid(_ring):
		return
	_ring_age += delta
	var mat: ShaderMaterial = _ring.material_override
	mat.set_shader_parameter("age", _ring_age)
	var snap: float = lerpf(1.7, 1.0, 1.0 - pow(1.0 - clampf(_ring_age / 0.08, 0.0, 1.0), 3.0))  # snaps shut
	var fade := 1.0
	if _ring_burst >= 0.0:
		_ring_burst += delta
		snap = 1.0 + 1.4 * clampf(_ring_burst / 0.15, 0.0, 1.0)
		fade = 1.0 - clampf(_ring_burst / 0.15, 0.0, 1.0)
		if _ring_burst >= 0.15:
			_ring.queue_free()
			return
	elif not _held:
		fade = 0.0
	mat.set_shader_parameter("fade", fade)
	_ring.global_position = mouth() - Vector3.UP * 0.1
	_ring.global_basis = Basis.IDENTITY.scaled(Vector3(snap, snap * 0.8, snap))


# ---- drips, splats, gas ---------------------------------------------------------------------------------------------

func _drip() -> void:
	var n := MeshInstance3D.new()
	n.mesh = _drip_mesh
	n.material_override = _drip_mat
	var m := mouth()
	_place(n, m + Vector3(randf_range(-0.25, 0.25), -0.15, randf_range(-0.25, 0.25)))
	_drips.append({"node": n, "vel": Vector3(randf_range(-0.3, 0.3), randf_range(-0.5, 0.2), randf_range(-0.3, 0.3))})


func _update_drips(delta: float) -> void:
	var floor_y := actor.global_position.y
	for d in _drips.duplicate():
		var n: MeshInstance3D = d.node
		d.vel.y -= 14.0 * delta
		n.global_position += d.vel * delta
		n.scale = Vector3(1.0, clampf(1.0 + absf(d.vel.y) * 0.12, 1.0, 1.8), 1.0)  # stretches as it falls
		if n.global_position.y <= floor_y + 0.03:
			_splash(Vector3(n.global_position.x, floor_y, n.global_position.z), randf_range(0.3, 0.45), 0.0, 1.0)
			n.queue_free()
			_drips.erase(d)


func _splash(at: Vector3, r: float, flash: float, life: float) -> void:
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * r * 1.3 * 2.0
	g.mesh = plane
	var m := ShaderMaterial.new()
	m.shader = SPLASH
	m.set_shader_parameter("radius_m", r)
	m.set_shader_parameter("extent", 1.3)
	m.set_shader_parameter("erupt", 0.0)
	m.set_shader_parameter("pool_life", life)
	m.set_shader_parameter("flash_mul", flash)
	m.set_shader_parameter("seed", randf() * 50.0)
	g.material_override = m
	_place(g, at + Vector3.UP * (LIFT + randf() * 0.01))
	_splats.append({"node": g, "age": 0.0, "life": life})


func _update_splats(delta: float) -> void:
	for s in _splats.duplicate():
		s.age += delta
		s.node.material_override.set_shader_parameter("age", s.age)
		if s.age >= s.life:
			s.node.queue_free()
			_splats.erase(s)


func _hinge_gas(left: bool, strength: float) -> void:
	var h: Vector3 = _hinges()[0 if left else 1]
	var out := (h - mouth()).normalized()
	out.y = 0.0
	out = out.normalized()
	var side := Vector3.UP.cross(_fwd()) * (1.0 if left else -1.0)
	_puff(h, 0.5 + 0.3 * strength, (side * 2.4 + Vector3.UP * 0.8) * strength, 0.45, gas, 0.5)


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
