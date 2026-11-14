extends Node3D
## Kangaroo boxing ring (slot 4), smooth style (kangaroo effects lane, 2026-11-11). Visual only: it deals no damage
## and moves nothing. It listens to KangarooKit's existing "ring_cast" cue and reads the kit's ring_on, ring_centre,
## ring_radius, ring_target and rhythm. No kit edits.
## Structure measured on SMITE 2's Ring of Spears (docs/reference/kangaroo-fx-synthesis-2026-11-11.md):
##   cast frame:   a short thin beam on the caster and a small core at the centre
##   0 to 0.2 s:   a floor wave runs out to the radius (ours; Odin's wall just appears at full radius)
##   0.1 to 0.4 s: the wall comes up at full radius, span by span, a little out of step
##   held:         bright base line and rope tops, a soft sheet between; eight posts and three ropes (the boxing ring)
##                 the ropes light one per rhythm stack; the wall ripples where the ringed enemy is held back
##   end:          the wall sinks and fades in 0.3 s
## Hides the kangaroo lane's flat stand-in ring (kangaroo_fx.gd, kind "ring") and its tail puff on the cast.
## Use: KangarooRingFx.attach(kit) is not a class name on purpose (no import needed); call
##      load("res://scripts/moba3d/kangaroo_ring_fx.gd").attach(kit)
const WALL := preload("res://shaders/kangaroo_ring_wall.gdshader")
const FLOOR := preload("res://shaders/kangaroo_ring_floor.gdshader")
const PILLAR := preload("res://shaders/kangaroo_ring_pillar.gdshader")
const DIM := preload("res://shaders/kangaroo_bout_dim.gdshader")
const CRIT := preload("res://shaders/kangaroo_crit_burst.gdshader")
const DIM_IN := 0.3    ## Ne Zha's world bleeds away in about 0.3 s
const DIM_OUT := 0.2
const SNAP_TIME := 0.25
const CRIT_LIFE := 0.2
const CRIT_SIZE := 1.3
const SELF_PATH := "res://scripts/moba3d/kangaroo_ring_fx.gd"
const WALL_H := 1.1   ## metres; the kangaroo stands about 1.8 m, Odin's wall is about two thirds of him
const LIFT := 0.03
const APRON := 1.2    ## the floor quad reaches this far past the radius
const WAVE_TIME := 0.2
const RISE_START := 0.1
const RISE_TIME := 0.3
const CLOSE_TIME := 0.3
const PILLAR_LIFE := 0.25
const PILLAR_SIZE := Vector2(1.1, 3.4)
const MINT := Color(0.32, 1.0, 0.78)

var kit: Node
var actor: Node3D
var hide_stand_in := true
var log_rows: Array = []
var elapsed := 0.0
var hidden_stand_ins := 0
var wall_hits := 0
var _ring := {}
var _pillar: MeshInstance3D
var _pillar_age := 99.0
var _light: OmniLight3D
var _light_age := 99.0
var _dim: MeshInstance3D
var _dim_k := 0.0
var _dim_on := false
var _bursts: Array = []
var crits := 0
var ghosts: Node3D
var kinetic: Node3D
const KINETIC_PATH := "res://scripts/moba3d/kangaroo_kinetic_fx.gd"
const GHOST_PATH := "res://scripts/moba3d/kangaroo_ghost_fx.gd"


static func attach(k: Node) -> Node:
	var old := k.get_node_or_null("KangarooRingFX")
	if old != null:
		return old
	var fx: Node3D = load(SELF_PATH).new()
	fx.name = "KangarooRingFX"
	k.add_child(fx)
	fx.setup(k, k.get_parent())
	return fx


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p
	kit.cue.connect(on_cue)
	# Afterimages (Preston 2026-11-12, the boxer / speedster trail): a child, so the kit needs no second hookup.
	ghosts = load(GHOST_PATH).new()
	ghosts.name = "KangarooGhostFX"
	add_child(ghosts)
	ghosts.setup(k, p)
	# Kinetic discharge (Preston 2026-11-12, "approve send to effects"): gauntlet charge and release on the hits.
	kinetic = load(KINETIC_PATH).new()
	kinetic.name = "KangarooKineticFX"
	add_child(kinetic)
	kinetic.setup(k, p)


func on_cue(cue_name: String) -> void:
	if not is_instance_valid(actor):
		return
	var bout := "bout_beat" in kit  # the title bout kit: the ring comes up on bout_start, not on the cast
	match cue_name:
		"ring_cast":
			if not bout:
				start_ring(kit.ring_centre, kit.ring_radius)
		"bout_start":
			start_ring(kit.ring_centre, kit.ring_radius)
			_dim_on = true
			_set_dim_centre(kit.ring_centre, kit.ring_radius)
		"bout_beat":
			var crit := bool(kit.get("last_crit"))
			if crit:
				crits += 1
				_crit_burst()
				if not _ring.is_empty():
					_ring.pulse = 1.0
					_ring.crit_lit = mini(int(_ring.get("crit_lit", 0)) + 1, 3)
			log_rows.append({"name": "bout_beat", "time": elapsed, "beat": kit.get("bout_beat"), "crit": crit})
		"bout_launch":
			if not _ring.is_empty():
				_ring.snap_age = 0.0
			_dim_on = false
			log_rows.append({"name": "bout_launch", "time": elapsed})
		"bout_end":
			_dim_on = false
			if not _ring.is_empty() and not _ring.closing:
				_ring.closing = true
				log_rows.append({"name": "ring_end", "time": elapsed, "held": _ring.age})


func _set_dim_centre(centre: Vector3, r: float) -> void:
	if _dim == null or not is_instance_valid(_dim):
		_dim = MeshInstance3D.new()
		var q := QuadMesh.new()
		q.size = Vector2.ONE
		_dim.mesh = q
		var m := ShaderMaterial.new()
		m.shader = DIM
		m.render_priority = -100  # before the ring's own glow, so the ring is never dimmed
		_dim.material_override = m
		_dim.extra_cull_margin = 16384.0
		_dim.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(_dim)
		_dim.top_level = true
	_dim.global_position = centre
	_dim.material_override.set_shader_parameter("centre", centre)
	_dim.material_override.set_shader_parameter("radius_m", r)


func _crit_burst() -> void:
	var t: Variant = kit.get("ring_target")
	var at: Vector3 = actor.global_position + Vector3.UP * 1.1
	if t != null and is_instance_valid(t):
		at = (t.global_position + actor.global_position) * 0.5 + Vector3.UP * 1.1
	var node := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2.ONE * CRIT_SIZE
	node.mesh = q
	var m := ShaderMaterial.new()
	m.shader = CRIT
	m.set_shader_parameter("spin", randf() * TAU)
	node.material_override = m
	_place(node, at)
	_bursts.append({"node": node, "t": 0.0})


func start_ring(centre: Vector3, r: float) -> void:
	_free_ring()
	var ext := r + APRON
	var floor_node := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * ext * 2.0
	floor_node.mesh = plane
	var fm := ShaderMaterial.new()
	fm.shader = FLOOR
	fm.set_shader_parameter("radius_m", r)
	fm.set_shader_parameter("extent", ext)
	floor_node.material_override = fm
	_place(floor_node, centre + Vector3.UP * LIFT)

	var wall := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 1.0
	cyl.bottom_radius = 1.0
	cyl.height = 1.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 96
	cyl.rings = 1
	wall.mesh = cyl
	var wm := ShaderMaterial.new()
	wm.shader = WALL
	wm.set_shader_parameter("radius_m", r)
	wm.set_shader_parameter("height_m", WALL_H)
	wm.set_shader_parameter("rise", 0.0)
	wm.set_shader_parameter("posts", 6.0 if r < 4.0 else 8.0)
	wall.material_override = wm
	_place(wall, centre + Vector3.UP * (WALL_H * 0.5 + LIFT))
	wall.scale = Vector3(r, WALL_H, r)

	_pillar = MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = PILLAR_SIZE
	_pillar.mesh = q
	var pm := ShaderMaterial.new()
	pm.shader = PILLAR
	_pillar.material_override = pm
	_place(_pillar, actor.global_position + Vector3.UP * PILLAR_SIZE.y * 0.5)
	_pillar_age = 0.0

	_light = OmniLight3D.new()  # small and short: Preston cut the big light on the rhino
	_light.light_color = MINT
	_light.light_energy = 1.0
	_light.omni_range = 3.0
	_light.shadow_enabled = false
	add_child(_light)
	_light.top_level = true
	_light.global_position = actor.global_position + Vector3.UP * 1.2
	_light_age = 0.0

	_ring = {"age": 0.0, "centre": centre, "r": r, "floor": floor_node, "wall": wall, "fm": fm, "wm": wm,
		"closing": false, "close_age": 0.0, "lit": -1, "pulse": 1.0, "hit_k": 0.0, "hit_cool": 0.0,
		"snap_age": -1.0, "crit_lit": 0}
	if hide_stand_in:
		_hide_stand_in(true)
	log_rows.append({"name": "ring_cast", "time": elapsed, "radius": r, "centre": centre,
		"target": String(kit.ring_target.name) if kit.ring_target != null and is_instance_valid(kit.ring_target) else ""})


func _place(node: MeshInstance3D, at: Vector3) -> MeshInstance3D:
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


## The kangaroo lane's procedural ring (a flat band from kangaroo_fx.gd) and, on the cast frame, the tail puff it
## drops with it. Both are hidden, not freed, so its own bookkeeping keeps working.
func _hide_stand_in(cast_frame: bool) -> void:
	var f: Variant = kit.get("fx")
	if f == null or not is_instance_valid(f):
		return
	var items: Variant = f.get("_live")
	if not (items is Array):
		return
	for item in items:
		var node: Node3D = item.get("node")
		if node == null or not is_instance_valid(node) or not node.visible:
			continue
		if item.kind == "ring" or (cast_frame and item.kind == "puff" and float(item.t) < 0.1):
			node.visible = false
			hidden_stand_ins += 1


func _free_ring() -> void:
	for key in ["floor", "wall"]:
		if _ring.has(key) and is_instance_valid(_ring[key]):
			_ring[key].queue_free()
	_ring = {}


func _process(delta: float) -> void:
	elapsed += delta
	if kit == null or not is_instance_valid(kit):
		return
	if hide_stand_in and not _ring.is_empty():
		_hide_stand_in(false)
	_tick_pillar(delta)
	_tick_bout(delta)
	if not _ring.is_empty():
		_tick_ring(delta)


func _tick_bout(delta: float) -> void:
	_dim_k = move_toward(_dim_k, 1.0 if _dim_on else 0.0, delta / (DIM_IN if _dim_on else DIM_OUT))
	if _dim != null and is_instance_valid(_dim):
		_dim.material_override.set_shader_parameter("k", _dim_k * _dim_k * (3.0 - 2.0 * _dim_k))
		_dim.visible = _dim_k > 0.0
	var keep: Array = []
	var cam := get_viewport().get_camera_3d()
	for b in _bursts:
		b.t += delta
		var node: MeshInstance3D = b.node
		if b.t >= CRIT_LIFE:
			node.queue_free()
			continue
		node.material_override.set_shader_parameter("t", b.t / CRIT_LIFE)
		if cam != null:
			node.look_at(cam.global_position, Vector3.UP)
		keep.append(b)
	_bursts = keep


func _tick_pillar(delta: float) -> void:
	if _pillar != null and is_instance_valid(_pillar):
		_pillar_age += delta
		var k := 1.0 - clampf(_pillar_age / PILLAR_LIFE, 0.0, 1.0)
		_pillar.material_override.set_shader_parameter("k", k * k)
		var cam := get_viewport().get_camera_3d()
		if cam != null:  # turn about the vertical to face the camera
			var to := cam.global_position - _pillar.global_position
			to.y = 0.0
			if to.length() > 0.01:
				_pillar.look_at(_pillar.global_position + to, Vector3.UP)
		if _pillar_age >= PILLAR_LIFE:
			_pillar.queue_free()
			_pillar = null
	if _light != null and is_instance_valid(_light):
		_light_age += delta
		_light.light_energy = 1.0 * maxf(1.0 - _light_age / 0.18, 0.0)
		if _light_age >= 0.18:
			_light.queue_free()
			_light = null


func _tick_ring(delta: float) -> void:
	var R := _ring
	R.age += delta
	var age: float = R.age
	var fm: ShaderMaterial = R.fm
	var wm: ShaderMaterial = R.wm
	var w := clampf(age / WAVE_TIME, 0.0, 1.0)
	fm.set_shader_parameter("wave", 1.0 - pow(1.0 - w, 3.0))
	fm.set_shader_parameter("wave_k", 1.0 - smoothstep(WAVE_TIME * 0.8, WAVE_TIME + 0.25, age))
	fm.set_shader_parameter("flash", 1.0 - clampf(age / 0.12, 0.0, 1.0))
	var rise := clampf((age - RISE_START) / RISE_TIME, 0.0, 1.0)
	var held := smoothstep(WAVE_TIME * 0.6, WAVE_TIME + 0.2, age)
	var fade := 1.0
	if R.snap_age >= 0.0:
		R.snap_age += delta
		wm.set_shader_parameter("snap", clampf(R.snap_age / SNAP_TIME, 0.0, 1.0))
		if R.snap_age >= SNAP_TIME * 0.6 and not R.closing:
			R.closing = true
			log_rows.append({"name": "ring_end", "time": elapsed, "held": age})
	if not R.closing and age > 0.5 and not bool(kit.get("ring_on")):
		R.closing = true
		log_rows.append({"name": "ring_end", "time": elapsed, "held": age})
	if R.closing:
		R.close_age += delta
		var c: float = clampf(R.close_age / CLOSE_TIME, 0.0, 1.0)
		rise *= 1.0 - c * c
		fade = 1.0 - c
		held *= 1.0 - c
		if c >= 1.0:
			_free_ring()
			return
	# rhythm: one rope per stack, a pulse when a stack is added (and when the wall finishes rising)
	var lit := mini(int(kit.get("rhythm")), 3)
	if "bout_beat" in kit:
		lit = int(R.crit_lit)
		var nb: Variant = kit.get("bout_next_beat")
		var beat := 0.0
		var win: float = float(kit.get("bout_window")) if kit.get("bout_window") != null else 0.25
		if nb != null and float(nb) >= 0.0 and not R.closing:  # -1 outside a bout
			beat = 1.0 - clampf(float(nb) / win, 0.0, 1.0)  # lights over the kit's crit window and peaks as it closes
		wm.set_shader_parameter("beat", beat)
	if R.lit >= 0 and lit > R.lit:
		R.pulse = 1.0
	R.lit = lit
	if age >= RISE_START + RISE_TIME and age - delta < RISE_START + RISE_TIME:
		R.pulse = 1.0
	R.pulse = maxf(R.pulse - delta * 4.0, 0.0)
	# the ringed enemy held back at the wall
	R.hit_cool = maxf(R.hit_cool - delta, 0.0)
	R.hit_k = maxf(R.hit_k - delta * 2.2, 0.0)
	var t: Variant = kit.get("ring_target")
	if not R.closing and t != null and is_instance_valid(t):
		var out: Vector3 = t.global_position - R.centre
		out.y = 0.0
		if out.length() >= R.r - 0.5 - 0.06 and R.hit_cool <= 0.0 and out.length() > 0.01:
			R.hit_k = 1.0
			R.hit_cool = 0.35
			wm.set_shader_parameter("hit_dir", Vector2(out.x, out.z).normalized())
			wall_hits += 1
			log_rows.append({"name": "wall_hit", "time": elapsed})
	wm.set_shader_parameter("rise", rise)
	wm.set_shader_parameter("fade", fade)
	wm.set_shader_parameter("lit", float(lit))
	wm.set_shader_parameter("pulse", R.pulse)
	wm.set_shader_parameter("hit_k", R.hit_k)
	fm.set_shader_parameter("held", held)
	fm.set_shader_parameter("pulse", R.pulse * fade)
