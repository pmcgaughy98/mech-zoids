extends Node3D
## Rhino brace release, smooth style (rhino effects lane, 2026-11-11). Visual only: listens to RhinoKit's "cue"
## signal. Replaces the pixel ring after Preston: "we don't want it too look like pixel art". Structure measured on
## SMITE 2's Cabrakan Tremors (docs/reference/rhino-fx-synthesis-2026-11-11.md):
##   impact frame: white-hot core, amber bloom, streaks, a short light that lights the rhino and the floor
##   0 to 0.1 s:   a mint edge races to the release radius, with a dome wall standing on it
##   ground:       a crack web in the floor, hot at first, cooling to dark fissures, gone by about 2 s
##   debris:       rock chunks thrown out, landing and lying there, then sinking away (the drifting motes were cut)
## Radius from the kit: release_radius + release_radius_per * charge (3.0 m to 5.0 m). Charge 5 is hotter and wider.
const GROUND := preload("res://shaders/rhino_release_ground.gdshader")
const SHELL := preload("res://shaders/rhino_release_shell.gdshader")
const HOLD := preload("res://shaders/rhino_brace_hold.gdshader")
const DUST := preload("res://shaders/rhino_dust.gdshader")
const STAND_INS := ["gp_ring", "impact_puff", "dust_trail"] ## the kit's pixel tremor sprites, hidden near the rhino
const HOLD_SIZE := 2.8 ## metres across; the rim sits at 85%, about the old pixel ring's 2.36 m
const LIFT := 0.035
const EXTENT := 1.25
const LIFE := 2.6
const GRAVITY := 16.0
var kit: Node
var actor: Node3D
var hide_stand_in := true ## the kit still spawns the Fx3D brace_ring; hidden so only this effect shows
var last_charge := 0
var live: Array = []
var log_rows: Array = []
var elapsed := 0.0
var _rock_mesh: Mesh
var _rock_mat: StandardMaterial3D
var _hold: MeshInstance3D
var _hold_age := 0.0
var _hold_flash := 0.0
var _hold_fade := 0.0
var _hold_charge := 0


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p
	kit.cue.connect(on_cue)
	kit.impact.connect(_on_impact)
	var rock := SphereMesh.new()  # few segments: a faceted chunk, not a cube
	rock.radius = 0.5
	rock.height = 0.8
	rock.radial_segments = 5
	rock.rings = 2
	_rock_mesh = rock
	_rock_mat = StandardMaterial3D.new()
	_rock_mat.albedo_color = Color(0.16, 0.14, 0.13)
	_rock_mat.roughness = 0.95
	_rock_mat.emission_enabled = true
	_rock_mat.emission = Color(1.0, 0.5, 0.15)
	_rock_mat.emission_energy_multiplier = 0.0
	_hold = MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * HOLD_SIZE
	_hold.mesh = plane
	var hm := ShaderMaterial.new()
	hm.shader = HOLD
	_hold.material_override = hm
	_place(_hold, Vector3.ZERO)
	_hold.visible = false


func on_cue(cue_name: String) -> void:
	if not is_instance_valid(actor):
		return
	match cue_name:
		"brace_release":
			brace_release(last_charge)
		"tremor_stomp":
			_tremor_stomp()
		"tremor_pulse":
			_tremor_pulse()
		"heave_tell", "heave_thump", "heave_lift", "heave_land":
			_heave_cue(cue_name)


func brace_release(charge: int) -> void:
	var r: float = kit.release_radius + kit.release_radius_per * charge
	var power: float = clampf(float(charge) / float(kit.SEISMIC_MAX), 0.0, 1.0)
	if hide_stand_in:
		_hide_stand_in()
	var at: Vector3 = actor.global_position
	var row := {"age": 0.0, "at": at, "r": r, "power": power, "rocks": [], "life": LIFE}
	row.ground = _ground(at, r, power)
	row.shell = _shell(at)
	row.light = _light(at, r, power)
	row.motes = null  # drifting motes cut 2026-11-11: Preston did not like the "light balls"
	var count := 8 + int(6 * power)
	for i in count:
		row.rocks.append(_rock(at, r, power, i, count))
	live.append(row)
	log_rows.append({"name": "brace_release", "time": elapsed, "charge": charge, "radius": r, "full": charge >= kit.SEISMIC_MAX})


func _ground(at: Vector3, r: float, power: float) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * r * EXTENT * 2.0
	node.mesh = plane
	var mat := ShaderMaterial.new()
	mat.shader = GROUND
	mat.set_shader_parameter("radius_m", r)
	mat.set_shader_parameter("extent", EXTENT)
	mat.set_shader_parameter("power", power)
	mat.set_shader_parameter("seed", randf() * 100.0)
	node.material_override = mat
	return _place(node, at + Vector3.UP * LIFT)


func _shell(at: Vector3) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	var cyl := CylinderMesh.new()
	cyl.top_radius = 1.0
	cyl.bottom_radius = 1.0
	cyl.height = 1.0
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 64
	cyl.rings = 1
	node.mesh = cyl
	var mat := ShaderMaterial.new()
	mat.shader = SHELL
	node.material_override = mat
	return _place(node, at)


func _light(at: Vector3, r: float, power: float) -> OmniLight3D:
	var l := OmniLight3D.new()
	l.light_color = Color(1.0, 0.78, 0.5)
	l.omni_range = r * 1.3
	l.shadow_enabled = false
	l.light_energy = 0.0
	l.set_meta("peak", 1.5 + 1.0 * power)  # toned down: the big white wash read as a "shining light"
	add_child(l)
	l.top_level = true
	l.global_position = at + Vector3.UP * 0.8
	return l


func _rock(at: Vector3, r: float, power: float, i: int, count: int) -> Dictionary:
	var node := MeshInstance3D.new()
	node.mesh = _rock_mesh
	var mat := _rock_mat.duplicate() as StandardMaterial3D
	node.material_override = mat
	var s := randf_range(0.12, 0.26) * (1.0 + 0.3 * power)
	node.scale = Vector3(s, s * randf_range(0.6, 1.0), s * randf_range(0.7, 1.2))
	var ang := TAU * (float(i) + randf() * 0.7) / float(count)
	var out := Vector3(cos(ang), 0, sin(ang))
	_place(node, at + out * randf_range(0.3, 0.9) + Vector3.UP * 0.1)
	node.rotation = Vector3(randf() * TAU, randf() * TAU, randf() * TAU)
	return {"node": node, "mat": mat, "vel": out * randf_range(1.6, 3.2) * (r / 3.0) + Vector3.UP * randf_range(3.0, 5.5), "spin": Vector3(randf_range(-9, 9), randf_range(-9, 9), randf_range(-9, 9)), "ground": at.y + s * 0.3, "landed": false}


func _place(node: Node3D, at: Vector3) -> Node3D:
	if node is GeometryInstance3D:
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	return node


func _hide_stand_in() -> void:
	var parent: Node = kit.world() if kit.has_method("world") else null
	if parent == null:
		return
	for i in range(parent.get_child_count() - 1, -1, -1):
		var c := parent.get_child(i)
		if c is Fx3D.FlatFx:
			c.visible = false
			return


## The kit parents its pixel brace_ring to the player while braced; hide it every frame it exists.
func _hide_hold_stand_in() -> void:
	for c in actor.get_children():
		if c is Fx3D.FlatFx and c.visible:
			c.visible = false


## The smooth braced read: fades in when planted, breathes, lights a notch per charge, fades out on release.
func _update_hold(delta: float) -> void:
	var braced: bool = bool(kit.get("braced"))
	# always on (2026-11-11): outside the brace the same disc stays faintly under him while he carries charge, one rim
	# notch per charge, so the Seismic meter reads on the floor as well as on the drum (Cabrakan keeps a passive disc)
	var idle := 0.0 if int(kit.seismic) <= 0 else 0.22 + 0.06 * float(kit.seismic)
	_hold_fade = move_toward(_hold_fade, 1.0 if braced else idle, delta / (0.15 if braced else 0.25))
	_hold.visible = _hold_fade > 0.001
	if not _hold.visible:
		_hold_age = 0.0
		_hold_charge = 0
		return
	_hold_age += delta
	var c := int(kit.seismic)
	if c > _hold_charge:
		_hold_flash = 1.0
	_hold_charge = c
	_hold_flash = maxf(0.0, _hold_flash - delta * 3.0)
	_hold.global_position = actor.global_position + Vector3.UP * (LIFT + 0.005)
	var m: ShaderMaterial = _hold.material_override
	m.set_shader_parameter("age", _hold_age)
	m.set_shader_parameter("charge", float(c))
	m.set_shader_parameter("flash", _hold_flash)
	m.set_shader_parameter("fade", _hold_fade)


func _process(delta: float) -> void:
	elapsed += delta
	if is_instance_valid(kit):
		last_charge = int(kit.seismic)  # the release zeroes it before the cue, so keep the frame-before value
		if is_instance_valid(actor):
			if hide_stand_in:
				_hide_hold_stand_in()
			_update_hold(delta)
			_swap_tremor_stand_ins()
			_watch_body()
	_update_dust(delta)
	_update_swipes(delta)
	_update_slabs(delta)
	_update_horn(delta)
	for row in live.duplicate():
		row.age += delta
		var t: float = row.age
		row.ground.material_override.set_shader_parameter("age", t)
		if row.has("reheat"):
			row.reheat = maxf(0.0, row.reheat - delta * 2.5)
			row.ground.material_override.set_shader_parameter("reheat", row.reheat)
		var front: float = 1.0 - pow(1.0 - clampf(t / 0.10, 0.0, 1.0), 3.0)
		var shell_r: float = maxf(0.05, row.r * front)
		var shell_h: float = lerpf(0.35, 0.9, front) * (1.0 + 0.4 * row.power)
		if row.shell != null:
			row.shell.scale = Vector3(shell_r, shell_h, shell_r)
			row.shell.global_position = row.at + Vector3.UP * shell_h * 0.5
			row.shell.material_override.set_shader_parameter("fade", 1.0 - smoothstep(0.08, 0.45, t))
			row.shell.visible = t < 0.45
		if row.light != null:
			row.light.light_energy = float(row.light.get_meta("peak")) * (1.0 - smoothstep(0.0, 0.2, t))
		var heat := 1.0 - smoothstep(0.0, 0.8, t)
		for rock in row.rocks:
			var n: MeshInstance3D = rock.node
			rock.mat.emission_energy_multiplier = 0.0 if row.get("cold", false) else 1.2 * (1.0 - smoothstep(0.0, 0.4, t))
			if not rock.landed:
				rock.vel.y -= GRAVITY * delta
				n.global_position += rock.vel * delta
				n.rotation += rock.spin * delta
				if n.global_position.y <= rock.ground and rock.vel.y < 0.0:
					n.global_position.y = rock.ground
					if rock.vel.y < -3.0:
						rock.vel = Vector3(rock.vel.x * 0.35, -rock.vel.y * 0.25, rock.vel.z * 0.35)
						rock.spin *= 0.4
					else:
						rock.landed = true
			if t > row.life - 0.6:
				n.global_position.y -= delta * 0.25  # sink into the floor at the end
		if t >= row.life:
			for n in [row.ground, row.shell, row.light, row.motes]:
				if is_instance_valid(n):
					n.queue_free()
			for rock in row.rocks:
				if is_instance_valid(rock.node):
					rock.node.queue_free()
			live.erase(row)


# --- Tremor (slice 2, 2026-11-11). Structure from Cabrakan's Tremors: one slam opens a crack web that stays for the
# slow, each stomp re-lights the same cracks and sends a fresh edge out, dust is thrown up where the feet land.
var _tremor: Dictionary = {} ## the live slam's row, so the stomps can re-heat its cracks
var _dust: Array = []
var tremor_log: Array = [] ## {name, time, radius} for the checks


## The kit emits impact(0.7) on the tremor's slam and impact(1.0) on the stampede finale's slam.
func _on_impact(strength: float) -> void:
	if not is_instance_valid(actor) or not String(kit.get("current")) in ["ground_pound", "stampede"] or strength < 0.69:
		return
	var finale := strength >= 0.99
	var c: Vector3 = kit.feet() + kit.ahead() * 0.5 if finale else kit.feet()
	var fr: float = kit.get("_finale_r")
	var r: float = (fr if fr > 0.0 else kit.finale_radius) if finale else kit.pound_radius
	var life: float = (kit.patch_time if finale else kit.tremor_stomps * kit.tremor_interval + kit.tremor_linger) + 0.3
	var power := 0.9 if finale else 0.55
	var row := _burst(c, r, power, life, 10 if finale else 6, {"flash_mul": 0.6 if finale else 0.45, "streak_mul": 0.6 if finale else 0.4, "hold": maxf(life - 2.0 - 0.5 * power, 0.0), "zone_life": life - 0.3})
	row.light.set_meta("peak", 1.4 if finale else 0.9)
	row.reheat = 0.0
	_tremor = row
	tremor_log.append({"name": "finale" if finale else "slam", "time": elapsed, "radius": r})


## Each stomp: the slam's cracks flare hot again, a thin edge races out over the same circle, a few rocks jump.
func _tremor_stomp() -> void:
	if _tremor.is_empty() or not live.has(_tremor):
		return
	_tremor.reheat = 0.85
	var edge := _burst(_tremor.at, _tremor.r, 0.3, 0.6, 3, {"crack_mul": 0.0, "flash_mul": 0.25, "streak_mul": 0.0})
	edge.light.set_meta("peak", 0.0)
	tremor_log.append({"name": "stomp", "time": elapsed, "radius": _tremor.r})


## A pulse of the Tremor charge run: a small crack burst at the feet, no light.
func _tremor_pulse() -> void:
	var r: float = kit.tremor_pulse_radius
	var row := _burst(actor.global_position, r, 0.3, 1.6, 3, {"flash_mul": 0.35, "streak_mul": 0.35, "hold": -0.6})  # fade while cooling: dark cooled pulse cracks read as black scribbles
	row.light.set_meta("peak", 0.0)
	tremor_log.append({"name": "pulse", "time": elapsed, "radius": r})


func _burst(at: Vector3, r: float, power: float, life: float, rocks: int, params: Dictionary) -> Dictionary:
	var row := {"age": 0.0, "at": at, "r": r, "power": power, "rocks": [], "life": life, "shell": null, "motes": null}
	row.ground = _ground(at, r, power)
	for k in params:
		row.ground.material_override.set_shader_parameter(k, params[k])
	row.light = _light(at, r, power)
	for i in rocks:
		row.rocks.append(_rock(at, r * 0.7, power, i, rocks))
	live.append(row)
	return row


## While the tremor or the run plays, the kit's pixel ring, puffs, flat yellow wave and texture decals near the rhino
## are hidden the frame they appear; each pixel puff becomes a smooth dust cloud at the same spot.
func _swap_tremor_stand_ins() -> void:
	var cur := String(kit.get("current"))
	if cur != "ground_pound" and cur != "stampede" and not bool(kit.get("_tremor_running")):
		return
	var parent: Node = kit.world() if kit.has_method("world") else null
	if parent == null:
		return
	for i in range(parent.get_child_count() - 1, -1, -1):
		var c := parent.get_child(i)
		if c.has_meta("rhino_fx_seen") or not (c is Node3D):
			continue
		c.set_meta("rhino_fx_seen", true)
		if c.global_position.distance_to(actor.global_position) > 8.0:
			continue
		if c is AnimatedSprite3D:
			var anim := String(c.animation)
			if anim in STAND_INS:
				c.visible = false
				if anim != "gp_ring":
					_dust_at(c.global_position, c.scale.x, anim == "dust_trail")
		elif c is MeshInstance3D and c.mesh is TorusMesh:
			c.visible = false  # KitFeel.ground_wave: the smooth edge replaces it
		elif c is MeshInstance3D and c.mesh is PlaneMesh and c.mesh.material is StandardMaterial3D:
			var tex: Texture2D = c.mesh.material.albedo_texture
			if tex != null and (tex.resource_path.contains("cracks") or tex.resource_path.contains("slow_disc")):
				c.visible = false


func _dust_at(at: Vector3, size: float, small: bool, vel := Vector3.ZERO, strength := -1.0) -> void:
	var q := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	var m_size := (1.1 if small else 1.7) * clampf(size, 0.5, 1.5)
	mesh.size = Vector2.ONE * m_size
	q.mesh = mesh
	var mat := ShaderMaterial.new()
	mat.shader = DUST
	var life := 0.55 if small else 0.8
	mat.set_shader_parameter("seed", randf() * 50.0)
	mat.set_shader_parameter("life", life)
	mat.set_shader_parameter("strength", strength if strength > 0.0 else (0.6 if small else 0.8))
	q.material_override = mat
	_place(q, Vector3(at.x, actor.global_position.y + m_size * 0.4, at.z))
	_dust.append({"node": q, "age": 0.0, "life": life, "vel": vel})


func _update_dust(delta: float) -> void:
	for d in _dust.duplicate():
		d.age += delta
		if d.age >= d.life or not is_instance_valid(d.node):
			if is_instance_valid(d.node):
				d.node.queue_free()
			_dust.erase(d)
			continue
		d.node.material_override.set_shader_parameter("age", d.age)
		d.node.global_position += d.vel * delta
		d.vel *= maxf(0.0, 1.0 - delta * 3.0)  # thrown dust slows fast


# --- Paw scrapes (2026-11-11). The Tremor charge's wind-up clip fires paw_1 and paw_2 on the model's event signal (at
# about 0.133 s and 0.333 s). Each scrape: three claw furrows dragged backward, a low dust kick thrown back, pebbles.
# Bull and boar scrapes in film read as dirt thrown BEHIND the animal, so everything moves backward, nothing glows.
const SCRAPE := preload("res://shaders/rhino_scrape.gdshader")
var _ev_body: Object = null
var scrape_count := 0


func _watch_body() -> void:
	var b: Variant = actor.get("body")
	if b == null or b == _ev_body or not is_instance_valid(b) or not b.has_signal("event"):
		return
	_ev_body = b
	b.event.connect(_on_body_event)


func _on_body_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "stampede_windup" and (n == "paw_1" or n == "paw_2"):
		_paw_scrape(n == "paw_1")
	elif clip.begins_with("horn_"):
		_horn_event(clip, n)


func _paw_scrape(left: bool) -> void:
	var fwd: Vector3 = kit.ahead()
	var side := fwd.cross(Vector3.UP).normalized() * (-1.0 if left else 1.0)
	var paw: Vector3 = actor.global_position + fwd * 0.9 + side * 0.45
	paw.y = actor.global_position.y
	var back := -fwd
	# the furrows: a plane whose +Z (UV.y) points backward from the paw
	var g := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(0.75, 2.1)  # long enough to run out past the hind feet: the play camera sits behind him
	g.mesh = plane
	var mat := ShaderMaterial.new()
	mat.shader = SCRAPE
	mat.set_shader_parameter("seed", randf() * 30.0)
	mat.set_shader_parameter("life", 1.6)
	g.material_override = mat
	_place(g, paw + back * 1.05 + Vector3.UP * (LIFT + 0.01))
	g.global_basis = Basis.looking_at(-back, Vector3.UP)  # looking_at points -Z at the target, so +Z points back
	var row := {"age": 0.0, "at": paw, "r": 1.0, "power": 0.0, "rocks": [], "life": 1.6, "shell": null, "light": null, "motes": null, "ground": g, "cold": true}
	for i in 3:
		var rk := _rock(paw + back * 0.9, 1.0, 0.0, i, 3)  # thrown from behind the hind legs so they arc up into view
		rk.node.scale *= 0.5
		rk.vel = back * randf_range(3.0, 4.6) + side * randf_range(-0.6, 0.6) + Vector3.UP * randf_range(2.6, 4.0)
		row.rocks.append(rk)
	live.append(row)
	# the dust kick: two clouds thrown low and backward
	_dust_at(paw + back * 1.0 + side * 0.3, 0.7, true, back * 2.2 + side * 0.8 + Vector3.UP * 0.5, 0.5)
	_dust_at(paw + back * 1.4 + side * 0.4, 0.6, true, back * 1.6 + side * 0.6 + Vector3.UP * 0.6, 0.45)
	scrape_count += 1
	tremor_log.append({"name": "paw_scrape_" + ("left" if left else "right"), "time": elapsed, "radius": 0.0})


# --- Horn chain (2026-11-12). The basic is hook, rip, gore; each clip fires "hit" on the model's event signal, and the
# gore fires "land" when the head comes down. Each hit draws a crescent slash in the swing's own plane: the hook flat
# to the rhino's left, the rip rising to its right, the gore straight up and biggest. The gore's land stamps dust.
const SWIPE := preload("res://shaders/rhino_swipe.gdshader")
var _swipes: Array = []
var horn_log: Array = []


func _horn_event(clip: String, n: String) -> void:
	var f: Vector3 = kit.ahead()
	f.y = 0.0
	f = f.normalized()
	var right := f.cross(Vector3.UP).normalized()
	var chest := actor.global_position + Vector3.UP * 1.1
	if n == "hit":
		match clip:
			"horn_hook":  # flat, sweeping from the rhino's right, across the front, to its left
				_swipe(chest + f * 0.9, right, f, -20.0, 160.0, 3.3, 1.25)
			"horn_rip":  # rising from low left to high right
				var up_right := (right + Vector3.UP).normalized()
				_swipe(chest + f * 0.9, up_right, f, 200.0, 10.0, 3.3, 1.35)
			"horn_gore":  # straight up from low in front
				_swipe(chest + f * 0.8 + Vector3.UP * 0.1, Vector3.UP, right, 165.0, -15.0, 3.6, 1.6)  # faces the camera: an arc in the forward plane is edge-on from behind
		horn_log.append({"name": clip, "time": elapsed})
	elif n == "land" and clip == "horn_gore":
		_dust_at(actor.global_position + f * 1.0 + right * 0.4, 0.8, true, right * 0.8, 0.5)
		_dust_at(actor.global_position + f * 1.0 - right * 0.4, 0.8, true, -right * 0.8, 0.5)
		horn_log.append({"name": "gore_land", "time": elapsed})


## A crescent slash on a quad whose +X is x_axis and +Y is y_axis (the swing's plane), centred at c.
func _swipe(c: Vector3, x_axis: Vector3, y_axis: Vector3, a0: float, a1: float, size: float, strength: float) -> void:
	var q := MeshInstance3D.new()
	var mesh := QuadMesh.new()
	mesh.size = Vector2.ONE * size
	q.mesh = mesh
	var m := ShaderMaterial.new()
	m.shader = SWIPE
	m.set_shader_parameter("a0", a0)
	m.set_shader_parameter("a1", a1)
	m.set_shader_parameter("strength", strength)
	q.material_override = m
	_place(q, c)
	var y := (y_axis - x_axis * x_axis.dot(y_axis)).normalized()
	q.global_basis = Basis(x_axis.normalized(), y, x_axis.normalized().cross(y))
	_swipes.append({"node": q, "age": 0.0})


func _update_swipes(delta: float) -> void:
	for sw in _swipes.duplicate():
		sw.age += delta
		if sw.age >= 0.25 or not is_instance_valid(sw.node):
			if is_instance_valid(sw.node):
				sw.node.queue_free()
			_swipes.erase(sw)
			continue
		sw.node.material_override.set_shader_parameter("age", sw.age)



# --- Heave (slot 1, 2026-11-12; replaced Horn Toss, whose effects were retired the same day). Proposed cues, until game
# feel builds it: heave_tell (the horn rings and glows; kit.heave_tell_time long), heave_thump (shoulder dust, a ridge of
# rock slabs runs ahead to kit.heave_target or kit.heave_reach metres), heave_lift (the ground bursts up in a ring of slabs
# under the target), heave_land (a cracked-ground burst at kit.heave_land, behind the rhino). The moving ripple is built
# from slabs that rise and sink, not a flat strip: flat travelling effects were rejected on 2026-11-12.
const RING := preload("res://shaders/rhino_ring.gdshader")
const RIPPLE_SPEED := 12.0
const RIPPLE_STEP := 0.45
var test_target: Node3D = null ## the checks set these while the kit has no Heave yet
var test_land := Vector3.INF
var heave_log: Array = []
var _slabs: Array = []
var _rings: Array = []
var _horn_light: OmniLight3D
var _horn_core: MeshInstance3D
var _tell_age := -1.0
var _tell_time := 0.4
var _ring_clock := 0.0


func _flat_ahead() -> Vector3:
	var f: Vector3 = kit.ahead()
	f.y = 0.0
	return f.normalized()


func _horn_pos() -> Vector3:
	return actor.global_position + Vector3.UP * 1.25 + _flat_ahead() * 1.35


func _heave_reach() -> float:
	var r = kit.get("heave_reach")
	return float(r) if r != null else 5.0


func _heave_target() -> Node3D:
	var t = kit.get("heave_target")
	if t is Node3D and is_instance_valid(t):
		return t
	return test_target if is_instance_valid(test_target) else null


func _heave_cue(cue_name: String) -> void:
	var f := _flat_ahead()
	var right := f.cross(Vector3.UP).normalized()
	var base := actor.global_position
	match cue_name:
		"heave_tell":
			var tt = kit.get("heave_tell_time")
			_tell_time = float(tt) if tt != null else 0.4
			_tell_age = 0.0
			_ring_clock = 0.0
			_ensure_horn()
		"heave_thump":
			_tell_age = maxf(_tell_age, _tell_time)  # the glow fades from here
			_dust_at(base + right * 0.9 + f * 0.3, 0.8, true, right * 1.6 + Vector3.UP * 0.4, 0.5)
			_dust_at(base - right * 0.9 + f * 0.3, 0.8, true, -right * 1.6 + Vector3.UP * 0.4, 0.5)
			var thump := _burst(base + f * 0.9, 1.1, 0.35, 1.2, 0, {"flash_mul": 0.4, "streak_mul": 0.3, "hold": -0.6})
			thump.light.set_meta("peak", 0.0)
			var end := _heave_reach()
			var t := _heave_target()
			if t != null:
				end = clampf((t.global_position - base).dot(f), 1.6, end)
			_ripple(base + f * 1.2, f, right, end - 1.2)
		"heave_lift":
			var t := _heave_target()
			var at: Vector3 = t.global_position if t != null else base + f * _heave_reach()
			at.y = base.y
			_mound(at)
		"heave_land":
			var at = kit.get("heave_land")
			if not (at is Vector3):
				at = test_land if test_land != Vector3.INF else base - f * 3.0
			_burst(at, 1.3, 0.35, 1.3, 4, {"flash_mul": 0.6, "streak_mul": 0.5, "hold": -0.6})
			_dust_at(at + right * 0.5, 0.8, true, right * 0.9, 0.5)
			_dust_at(at - right * 0.5, 0.8, true, -right * 0.9, 0.5)
	heave_log.append({"name": cue_name, "time": elapsed})


## The ripple: pairs of slabs punch up one after another along the line, each sinking as the next rises.
func _ripple(start: Vector3, f: Vector3, right: Vector3, length: float) -> void:
	var steps := maxi(2, int(length / RIPPLE_STEP) + 1)
	for i in steps:
		var at := start + f * (i * RIPPLE_STEP)
		var delay := i * RIPPLE_STEP / RIPPLE_SPEED
		for s in [-1.0, 1.0]:
			var side: float = s * randf_range(0.35, 0.6)  # wide enough to show past both flanks from the play camera
			var tilt: Vector3 = (f * 0.35 + right * s * 0.45).normalized()
			_slab(at + right * side, delay, randf_range(0.5, 0.75), tilt, 0.32, 0.07, 0.12, 0.35, i % 2 == 0 and s > 0.0)


## The heave under the target: a ring of tall slabs bursts up and leans out, with cracked ground, rocks and dust.
func _mound(at: Vector3) -> void:
	var n := 7
	for i in n:
		var ang := TAU * (float(i) + randf() * 0.4) / float(n)
		var out := Vector3(cos(ang), 0.0, sin(ang))
		_slab(at + out * randf_range(0.55, 0.8), randf() * 0.04, randf_range(1.5, 2.0), out, 0.7,  # tall and splayed: the play camera sees it over the rhino's back
			 0.09, 0.45, 0.5, false)
	var row := _burst(at, 1.4, 0.55, 1.6, 6, {"flash_mul": 0.6, "streak_mul": 0.5, "hold": -0.4})
	row.light.set_meta("peak", 0.8)
	for i in 3:
		var ang := TAU * float(i) / 3.0 + randf()
		var out := Vector3(cos(ang), 0.0, sin(ang))
		_dust_at(at + out * 0.8, 1.1, true, out * 1.4 + Vector3.UP * 2.2, 0.55)


func _slab(at: Vector3, delay: float, height: float, tilt_dir: Vector3, tilt: float, rise: float, hold: float, sink: float, dust: bool) -> void:
	var node := MeshInstance3D.new()
	node.mesh = _rock_mesh
	var mat := _rock_mat.duplicate() as StandardMaterial3D
	node.material_override = mat
	var w := randf_range(0.22, 0.32) * (0.7 + 0.5 * height)
	var up := (Vector3.UP + tilt_dir * tilt).normalized()
	var side := up.cross(Vector3.FORWARD if absf(up.z) < 0.9 else Vector3.RIGHT).normalized()
	var fwd := side.cross(up).normalized()
	_place(node, at)
	node.global_basis = Basis(side * w, up * height * 1.25, fwd * w * 0.8).rotated(up, randf() * TAU)
	node.visible = false
	_slabs.append({"node": node, "mat": mat, "at": at, "up": up, "h": height, "age": -delay, "rise": rise, "hold": hold, "sink": sink, "dust": dust})


func _update_slabs(delta: float) -> void:
	for sl in _slabs.duplicate():
		sl.age += delta
		var n: MeshInstance3D = sl.node
		if sl.age < 0.0:
			continue
		if not n.visible:
			n.visible = true
			if sl.dust:
				_dust_at(sl.at, 0.55, true, Vector3.UP * 0.5, 0.4)
		var a: float = sl.age
		var k := 0.0
		if a < sl.rise:
			var u: float = a / sl.rise
			k = 1.0 - (1.0 - u) * (1.0 - u)
		elif a < sl.rise + sl.hold:
			k = 1.0
		else:
			var u: float = clampf((a - sl.rise - sl.hold) / sl.sink, 0.0, 1.0)
			k = 1.0 - u * u
		var h: float = sl.h
		n.global_position = sl.at + sl.up * (-h * 0.55 + h * 0.85 * k)
		sl.mat.emission_energy_multiplier = 1.1 * (1.0 - smoothstep(0.0, 0.45, a))
		if a >= sl.rise + sl.hold + sl.sink:
			n.queue_free()
			_slabs.erase(sl)


func _ensure_horn() -> void:
	if _horn_light == null:
		_horn_light = OmniLight3D.new()
		_horn_light.light_color = Color(0.55, 1.0, 0.85)
		_horn_light.omni_range = 3.0
		_horn_light.shadow_enabled = false
		add_child(_horn_light)
		_horn_light.top_level = true
		_horn_core = MeshInstance3D.new()
		var q := QuadMesh.new()
		q.size = Vector2.ONE
		_horn_core.mesh = q
		var m := ShaderMaterial.new()
		m.shader = RING
		m.set_shader_parameter("strength", 0.0)
		_horn_core.material_override = m
		_place(_horn_core, Vector3.ZERO)


func _update_horn(delta: float) -> void:
	for r in _rings.duplicate():
		r.age += delta
		if r.age >= 0.35:
			r.node.queue_free()
			_rings.erase(r)
		else:
			r.node.material_override.set_shader_parameter("age", r.age)
	if _horn_light == null:
		return
	if _tell_age < 0.0 or not is_instance_valid(actor):
		_horn_light.visible = false
		_horn_core.visible = false
		return
	_tell_age += delta
	var build := clampf(_tell_age / _tell_time, 0.0, 1.0)
	var fade := 1.0 - clampf((_tell_age - _tell_time) / 0.25, 0.0, 1.0)
	if fade <= 0.0:
		_tell_age = -1.0
		return
	var hum := 0.75 + 0.25 * sin(elapsed * 55.0)
	var horn := _horn_pos()
	_horn_light.visible = true
	_horn_core.visible = true
	_horn_light.global_position = horn
	_horn_light.light_energy = 2.2 * build * hum * fade
	_horn_core.global_position = horn
	var cm: ShaderMaterial = _horn_core.material_override
	cm.set_shader_parameter("size", 0.45 + 0.35 * build)
	cm.set_shader_parameter("core", 0.9 * build * hum * fade)
	if _tell_age < _tell_time:
		_ring_clock -= delta
		if _ring_clock <= 0.0:
			_ring_clock = 0.1
			var q := MeshInstance3D.new()
			var mesh := QuadMesh.new()
			mesh.size = Vector2.ONE
			q.mesh = mesh
			var m := ShaderMaterial.new()
			m.shader = RING
			m.set_shader_parameter("size", 1.0 + 0.5 * build)
			m.set_shader_parameter("strength", 0.6 + 0.6 * build)
			q.material_override = m
			_place(q, horn)
			_rings.append({"node": q, "age": 0.0})
