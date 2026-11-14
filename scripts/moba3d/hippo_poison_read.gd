extends Node3D
## Hippo effects lane (2026-11-12): the poisoned read. Preston: "Yes, poison read".
## Enemies standing in a toxic zone (the Vent puddle, the airborne Vent's landing puddle, the Toxic Flood lake) get
## violet fumes streaming off their body, and a lift plus a few gas puffs on each 0.5 s damage tick, the same beat
## the kit ticks on. The fumes linger LINGER seconds after they step out, then fade. An observer only: it reads
## positions, never deals damage and never touches the unit's own nodes or materials (they belong to other lanes).
## The Vent and Flood effects each make one of these and call add_zone().

const WISP := preload("res://shaders/hippo_poison_wisp.gdshader")
const DUST := preload("res://shaders/rhino_dust.gdshader") ## soft gas puff, blend_mix
const LINGER := 0.8
const GOO_LINGER := 0.35 ## the goo lets go soon after the slow ends (the kit refreshes it every tick + 0.1 s)
const GAS := Color(0.62, 0.36, 0.78)
const GOO := preload("res://shaders/hippo_slow_goo.gdshader") ## the overcharged puddle's slow: goo on the legs

var actor: Node3D
var zones: Array = [] ## {centre, radius, age, life, tick, next, name, slows}
var marks: Dictionary = {} ## unit instance id -> {unit, node, mat, left, pulse, fade, size}
var _puffs: Array = []
var elapsed := 0.0
var log_rows: Array = [] ## {name, time} for the checks


## A zone ticks every `tick` seconds from its start, like the kit's puddle loop (first tick at `tick`).
func add_zone(centre: Vector3, radius: float, life: float, tick := 0.5, zone_name := "zone", slows := false) -> void:
	zones.append({"centre": Vector3(centre.x, 0.0, centre.z), "radius": radius, "age": 0.0, "life": life,
		"tick": tick, "next": tick, "name": zone_name, "slows": slows})
	log_rows.append({"name": zone_name + " zone", "time": elapsed, "radius": radius})


func _process(delta: float) -> void:
	elapsed += delta
	if not is_instance_valid(actor):
		return
	var inside := {}
	var ticked := {}
	var sticky := {} ## inside a slowing zone and actually slowed by the kit
	for z in zones.duplicate():
		z.age += delta
		if z.age > z.life + 0.02:
			zones.erase(z)
			continue
		var tick_now := false
		if z.age >= z.next:
			z.next += z.tick
			tick_now = true
		for e in MatchTeams.enemies_of(actor):
			if not (e is Node3D):
				continue
			var d: Vector3 = e.global_position - z.centre
			d.y = 0.0
			if d.length() <= z.radius:
				var id: int = e.get_instance_id()
				inside[id] = e
				var sl: Variant = e.get("slowed")
				if z.slows and sl != null and float(sl) > 0.0:
					sticky[id] = true
				if tick_now:
					ticked[id] = z.name
	for id in inside:
		if not marks.has(id):
			marks[id] = _mark(inside[id])
			log_rows.append({"name": "poisoned " + str(inside[id].name), "time": elapsed})
		marks[id].left = LINGER
		if sticky.has(id):
			if marks[id].goo.is_empty():
				marks[id].goo = _goo(marks[id])
				log_rows.append({"name": "slowed " + str(inside[id].name), "time": elapsed})
			marks[id].goo.left = GOO_LINGER
	for id in ticked:
		_tick(marks[id])
		log_rows.append({"name": "tick " + ticked[id] + " on " + str(marks[id].unit.name), "time": elapsed})
	_update_marks(delta)
	_update_puffs(delta)


func _mark(u: Node3D) -> Dictionary:
	var size := _size_of(u)
	var cyl := CylinderMesh.new()
	cyl.top_radius = size.x * 0.8
	cyl.bottom_radius = size.x
	cyl.height = size.y * 1.1
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 24
	cyl.rings = 1
	var mi := MeshInstance3D.new()
	mi.mesh = cyl
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = WISP
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("strength", 0.0)
	mi.material_override = m
	add_child(mi)
	mi.top_level = true
	mi.global_position = u.global_position + Vector3.UP * size.y * 0.55
	return {"unit": u, "node": mi, "mat": m, "left": LINGER, "pulse": 0.0, "fade": 0.0, "size": size, "goo": {}}


## Radius and height from the unit's meshes (minions and machines differ a lot). Health bars are not meshes.
func _size_of(u: Node3D) -> Vector2:
	var box := AABB()
	var first := true
	for v in u.find_children("*", "MeshInstance3D", true, false):
		var mv := v as MeshInstance3D
		if mv == null or mv.mesh == null or not mv.is_visible_in_tree():
			continue
		var b: AABB = mv.global_transform * mv.get_aabb()
		box = b if first else box.merge(b)
		first = false
	if first:
		return Vector2(0.6, 1.4)
	var r := clampf(maxf(box.size.x, box.size.z) * 0.45, 0.35, 1.5)
	var h := clampf(box.end.y - u.global_position.y, 0.7, 3.0)
	return Vector2(r, h)


func _tick(mk: Dictionary) -> void:
	mk.pulse = 1.0
	var u: Node3D = mk.unit
	if not is_instance_valid(u):
		return
	var s: Vector2 = mk.size
	for i in 3:
		var a: float = randf() * TAU
		var at := u.global_position + Vector3(cos(a), 0.0, sin(a)) * s.x * 0.6 + Vector3.UP * s.y * randf_range(0.35, 0.7)
		_puff(at, s.x * randf_range(1.0, 1.4), Vector3(cos(a), 0.0, sin(a)) * 0.4 + Vector3.UP * randf_range(0.6, 1.0), 0.8)


func _update_marks(delta: float) -> void:
	for id in marks.keys():
		var mk: Dictionary = marks[id]
		var u: Variant = mk.unit
		var gone: bool = not is_instance_valid(u) or not MatchTeams.hittable(u)
		mk.left -= delta
		if gone or mk.left <= 0.0:
			_free_goo(mk)
			if is_instance_valid(mk.node):
				mk.node.queue_free()
			marks.erase(id)
			continue
		mk.fade = minf(1.0, mk.fade + delta / 0.2)
		mk.pulse *= exp(-5.0 * delta)
		var s: Vector2 = mk.size
		mk.node.global_position = u.global_position + Vector3.UP * s.y * 0.55
		mk.mat.set_shader_parameter("strength", mk.fade * clampf(mk.left / LINGER, 0.0, 1.0) * 1.0)
		mk.mat.set_shader_parameter("pulse", mk.pulse)
		_update_goo(mk, delta)


func _puff(at: Vector3, size: float, vel: Vector3, life: float) -> void:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	q.mesh = quad
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("dust", GAS)
	m.set_shader_parameter("strength", 0.5)
	q.material_override = m
	add_child(q)
	q.top_level = true
	q.global_position = at
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


# ---- the overcharged puddle's slow: goo on the legs and a sticky patch under the feet ----------------------------

func _goo(mk: Dictionary) -> Dictionary:
	var s: Vector2 = mk.size
	var u: Node3D = mk.unit
	# A sleeve of goo on each foot. One cylinder round the whole unit failed both ways on a big machine: wide enough
	# to clear the body it stood 3 m out as a haze wall, tight enough to hug the legs it sat inside them, hidden.
	var fr := clampf(s.x * 0.36, 0.22, 0.6)  # wider than the foot: bones sit in the middle of the leg
	var fh := clampf(s.y * 0.32, 0.3, 0.6)
	var skel: Skeleton3D = null
	var found := u.find_children("*", "Skeleton3D", true, false)
	if not found.is_empty():
		skel = found[0]
	var feet: Array = []
	for b in _feet_of(u, skel):
		feet.append({"node": _goo_node(_sleeve(fr, fh), 0.0, fh), "bone": b})
	if feet.is_empty():  # no skeleton or no feet found: one sleeve round the middle, just outside the body
		feet.append({"node": _goo_node(_sleeve(s.x * 0.95, fh), 0.0, fh), "bone": -1})
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * s.x * 1.7
	var patch := _goo_node(plane, 1.0)
	return {"feet": feet, "skel": skel, "patch": patch, "h": fh, "left": GOO_LINGER, "fade": 0.0, "pull": 0.0}


func _sleeve(r: float, h: float) -> CylinderMesh:
	var cyl := CylinderMesh.new()
	cyl.top_radius = r * 0.8
	cyl.bottom_radius = r
	cyl.height = h
	cyl.cap_top = false
	cyl.cap_bottom = false
	cyl.radial_segments = 20
	cyl.rings = 1
	return cyl


## The feet: the lowest bones away from the unit's middle, one per cluster, up to six.
func _feet_of(u: Node3D, skel: Skeleton3D) -> Array:
	if skel == null:
		return []
	var rows: Array = []
	var low := INF
	for b in skel.get_bone_count():
		if skel.get_bone_parent(b) == -1:
			continue  # the root sits on the ground at the middle
		var p: Vector3 = skel.global_transform * skel.get_bone_global_pose(b).origin
		var off := Vector2(p.x - u.global_position.x, p.z - u.global_position.z)
		if off.length() < 0.2:
			continue
		rows.append({"b": b, "p": p})
		low = minf(low, p.y)
	rows.sort_custom(func(x, y): return x.p.y < y.p.y)
	var picked: Array = []
	var at: Array = []
	for r in rows:
		if r.p.y > low + 0.3 or picked.size() >= 6:
			break
		var near := false
		for q in at:
			if Vector2(q.x - r.p.x, q.z - r.p.z).length() < 0.35:
				near = true
		if not near:
			picked.append(r.b)
			at.append(r.p)
	return picked


func _goo_node(mesh: Mesh, disc: float, height := 0.5) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	mi.mesh = mesh
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = GOO
	m.render_priority = 3 if disc > 0.5 else 1  # the patch sits over the floor zones and the puddle
	m.set_shader_parameter("disc", disc)
	m.set_shader_parameter("height", height)
	m.set_shader_parameter("seed", randf() * 40.0)
	m.set_shader_parameter("strength", 0.0)
	mi.material_override = m
	add_child(mi)
	mi.top_level = true
	return mi


func _update_goo(mk: Dictionary, delta: float) -> void:
	var g: Dictionary = mk.goo
	if g.is_empty():
		return
	var u: Node3D = mk.unit
	g.left -= delta
	if g.left <= 0.0:
		g.fade = maxf(0.0, g.fade - delta / 0.25)  # lets go
		if g.fade <= 0.0:
			_free_goo(mk)
			return
	else:
		g.fade = minf(1.0, g.fade + delta / 0.15)  # grabs fast
	var vel: Variant = u.get("velocity")
	var speed := 0.0
	if vel is Vector3:
		speed = Vector3(vel.x, 0.0, vel.z).length()
	g.pull = lerpf(g.pull, clampf(speed / 4.0, 0.0, 1.0), 1.0 - exp(-6.0 * delta))
	var at := u.global_position
	var skel: Skeleton3D = g.skel
	for f in g.feet:
		var p := at
		if f.bone >= 0 and skel != null and is_instance_valid(skel):
			p = skel.global_transform * skel.get_bone_global_pose(f.bone).origin
		f.node.global_position = Vector3(p.x, at.y + g.h * 0.5, p.z)
		f.node.material_override.set_shader_parameter("strength", g.fade)
		f.node.material_override.set_shader_parameter("pull", g.pull)
	g.patch.global_position = Vector3(at.x, at.y + 0.06, at.z)
	g.patch.material_override.set_shader_parameter("strength", g.fade)


func _free_goo(mk: Dictionary) -> void:
	var g: Dictionary = mk.goo
	for f in g.get("feet", []):
		if is_instance_valid(f.node):
			f.node.queue_free()
	if g.has("patch") and is_instance_valid(g.patch):
		g.patch.queue_free()
	mk.goo = {}
