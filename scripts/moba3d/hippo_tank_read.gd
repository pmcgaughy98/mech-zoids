extends Node3D
## Hippo passive, Pressure Tanks (hippo effects lane, 2026-11-12). Visual only, no kit or model edits.
## The kit's pressure (0 to pressure_max) shows as a toxic liquid level inside the two flank tank windows, and the
## window glow ("Hippo glow", through MechLook.set_glow, the look lane's per-mech call) follows the same level:
##   filling:     the level rises as the hippo deals and takes damage, bubbles rising, the glow comes up with it
##   overcharged: full to the top, the liquid boils, the meniscus brightens and the glow pulses
##   spent:       on overcharge_spent or tanks_drained the level drops fast and sloshes
##   drained:     empty dark glass, the glow low, until the kit says tanks_refilled
## The liquid is an oval panel of its own in each window (the glass is painted into the body texture and reflects the
## sky, so there is no separate glass to draw on), riding the bone nearest the window. The hippo's mesh, skeleton
## and materials are read, never changed.
## While Toxic Flood owns the glow (its charge flare and burst), it sets the actor meta "hippo_glow_hold".

const SHADER := preload("res://shaders/hippo_tank_liquid.gdshader")
const LOOK := preload("res://scripts/moba3d/mech_look.gd")
const GLOW_SURFACE := "Hippo glow"
const GLOW_NORMAL := 1.6 ## the hippo 3D lane's emission strength, the glow at full tanks
const GLOW_EMPTY := 0.3
## Preston (2026-11-12): the tank lines' bright glow should arrive at lower pressure. The glow eases in and reaches
## GLOW_NORMAL at this share of the tanks (0.4 = 40% pressure); about 64% of the way there at a fifth full.
const GLOW_FULL_AT := 0.4
## The flank windows in the body mesh's own space (fitted 2026-11-12 from close shots): the +x window; the -x one is its
## mirror. Half sizes are along the body (z) and up (y). Tilt leans the panel top inward to follow the glass.
const WIN_CENTRE := Vector3(0.70, 0.60, -0.30)
const WIN_HALF := Vector2(0.40, 0.20)
const WIN_TILT := 0.0
## The chin tank (hippo 3D lane, r14, 2026-11-13): the small front tank under the jaw, also on the Chest bone. Its glass
## faces mostly down and a little forward; the plane below was fitted by the hippo 3D lane to its 10,016 glass texels
## (2026-11-14, body space before the 1.25 scale). The glass is curved and bulges up to 0.050 out past that plane,
## so the panel is bent to the glass and sits proud of it, or it hides inside. A small window sits on each side wall
## of the housing, centre |x| 0.40, y 0.455, z 0.715, about 17 by 12 cm. All three show the same live level as the flanks.
const CHIN_CENTRE := Vector3(-0.023, 0.289, 0.694)
const CHIN_NORMAL := Vector3(0.013, -0.936, 0.352)
const CHIN_UP := Vector3(0.0, 0.352, 0.936) ## from the low back edge to the high front edge: the level fills toward the front
const CHIN_SIZE := Vector2(0.666, 0.711)
## The glass is a dome: up to 0.050 out past the plane in the middle, up to 0.140 behind it at the edges. A flat panel
## pushed clear of the middle stuck out past the housing as a blade, so the panel is bent to match, 2 cm proud.
const CHIN_APEX := 0.07 ## out along the normal at the middle
const CHIN_DROP := 0.095 ## back along the normal per unit of (u*u + v*v), u and v running -1..1 across the panel
const CHIN_SIDE := Vector3(0.40, 0.455, 0.715)
const CHIN_SIDE_HALF := Vector2(0.085, 0.06)
const PANEL_LIFT := 0.012 ## each panel sits this far proud of the painted glass so it never sinks into it

var actor: Node3D
var _kit: Node = null
var _body: Object = null
var _src: MeshInstance3D = null
var _skel: Skeleton3D = null
var _panels: Array = []
var _mat: ShaderMaterial = null
var _fill := -1.0
var _slosh := 0.0
var _glow := -1.0
var _pulse := 0.0
var elapsed := 0.0
var log_rows: Array = []


func _process(delta: float) -> void:
	elapsed += delta
	if actor == null or not is_instance_valid(actor):
		return
	_watch()
	if _kit == null or _mat == null:
		return
	var pmax: float = maxf(float(_kit.get("pressure_max")), 1.0)
	var target: float = clampf(float(_kit.get("pressure")) / pmax, 0.0, 1.0)
	var over: bool = bool(_kit.get("overcharged"))
	if over:
		target = 1.0
	if _fill < 0.0:
		_fill = target
	var rate := 0.9 if target > _fill else 2.5  # fills smoothly, empties fast
	_fill = move_toward(_fill, target, rate * delta)
	var speed := 0.0
	var vel: Variant = actor.get("velocity")
	if vel is Vector3:
		speed = Vector3(vel.x, 0, vel.z).length()
	_slosh = maxf(_slosh * exp(-2.5 * delta), clampf(speed / 8.0, 0.0, 0.6))
	_pulse += delta * (6.0 if over else 0.0)
	_mat.set_shader_parameter("fill", _fill)
	_mat.set_shader_parameter("slosh", _slosh)
	_mat.set_shader_parameter("boil", 1.0 if over else 0.0)
	_mat.set_shader_parameter("bright", 1.0 + (0.12 * (0.5 + 0.5 * sin(_pulse * 2.0)) if over else 0.0))
	_follow()
	if not bool(actor.get_meta("hippo_glow_hold", false)):
		var t := clampf(_fill / GLOW_FULL_AT, 0.0, 1.0)
		var g := lerpf(GLOW_EMPTY, GLOW_NORMAL, 1.0 - (1.0 - t) * (1.0 - t))  # eases in fast: bright early
		if over:
			g = GLOW_NORMAL + 0.9 * (0.5 + 0.5 * sin(_pulse))
		if absf(g - _glow) > 0.01:
			_glow = g
			LOOK.set_glow(_body, _glow, GLOW_SURFACE)
	else:
		_glow = -1.0  # take the glow back as soon as the flood lets go


func _watch() -> void:
	var k: Node = actor.get_node_or_null("Kit")
	if k != null and k != _kit and k.has_signal("cue"):
		_kit = k
		k.cue.connect(_on_cue)
	var b: Variant = actor.get("body")
	if b == null or b == _body or not is_instance_valid(b):
		return
	_body = b
	_build()


func _on_cue(n: String) -> void:
	match n:
		"tanks_full", "overcharge_spent", "tanks_drained", "tanks_refilled":
			_slosh = 1.0
			if log_rows.size() < 200:
				log_rows.append({"name": "%s fill %.2f" % [n, _fill], "time": elapsed})
		"vent_puddle", "flood_burst":
			_slosh = maxf(_slosh, 0.6)


## Two oval panels, one per flank window, in the body mesh's own space, riding the bone nearest the window.
func _build() -> void:
	for p in _panels:
		if is_instance_valid(p.node):
			p.node.queue_free()
	_panels = []
	_mat = null
	_src = null
	for mi: MeshInstance3D in (_body as Node).find_children("*", "MeshInstance3D", true, false):
		if mi.mesh == null:
			continue
		for s in mi.mesh.get_surface_count():
			var mat: Material = mi.get_active_material(s)
			if mat != null and mat.resource_name == GLOW_SURFACE:
				_src = mi
		if _src != null:
			break
	if _src == null:
		log_rows.append({"name": "no '%s' surface on this body (not the hippo yet, or swapped): waiting" % GLOW_SURFACE, "time": elapsed})
		return
	_skel = _src.get_node_or_null(_src.skeleton) as Skeleton3D
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.render_priority = 2
	_mat.set_shader_parameter("seed", randf() * 40.0)
	var specs: Array = []  # [local transform, quad size]
	for side in [1.0, -1.0]:
		specs.append([Transform3D(Basis(Vector3.UP, side * PI * 0.5) * Basis(Vector3.RIGHT, -side * WIN_TILT), Vector3(WIN_CENTRE.x * side, WIN_CENTRE.y, WIN_CENTRE.z)), Vector2(WIN_HALF.x, WIN_HALF.y) * 2.0])
		specs.append([Transform3D(Basis(Vector3.UP, side * PI * 0.5), Vector3((CHIN_SIDE.x + PANEL_LIFT) * side, CHIN_SIDE.y, CHIN_SIDE.z)), CHIN_SIDE_HALF * 2.0])
	# the chin glass, on the lane's fitted plane, pushed out past the bulge
	var nrm := CHIN_NORMAL.normalized()
	var up := (CHIN_UP - nrm * CHIN_UP.dot(nrm)).normalized()
	var right := up.cross(nrm).normalized()
	specs.append([Transform3D(Basis(right, up, nrm), CHIN_CENTRE), CHIN_SIZE, true])
	for spec in specs:
		var local: Transform3D = spec[0]
		var quad: Mesh = _bent(spec[1]) if spec.size() > 2 else _flat(spec[1])
		var world: Transform3D = _src.global_transform * local
		var n := MeshInstance3D.new()
		n.name = "TankLiquid"
		n.mesh = quad
		n.material_override = _mat
		n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(n)
		n.top_level = true
		n.global_transform = world
		var bone := -1
		var off := world
		if _skel != null:
			var best := 1e9
			var pool: Array = []
			for b in _skel.get_bone_count():
				var bn := _skel.get_bone_name(b).to_lower()
				if bn.contains("spine") or bn.contains("chest") or bn.contains("hip") or bn.contains("pelvis") or bn.contains("body"):
					pool.append(b)
			if pool.is_empty():
				pool = range(_skel.get_bone_count())  # no spine names: nearest bone of all
			for b in pool:
				var d: float = (_skel.global_transform * _skel.get_bone_global_pose(b).origin).distance_to(world.origin)
				if d < best:
					best = d
					bone = b
			off = (_skel.global_transform * _skel.get_bone_global_pose(bone)).affine_inverse() * world
		_panels.append({"node": n, "bone": bone, "off": off})
	log_rows.append({"name": "panels on bone %s" % (_skel.get_bone_name(_panels[0].bone) if _skel != null and _panels[0].bone >= 0 else "none"), "time": elapsed})


func _flat(size: Vector2) -> Mesh:
	var q := QuadMesh.new()
	q.size = size
	return q


## A panel bowed into a shallow dome along its own +z (the outward normal), to follow the curved chin glass.
func _bent(size: Vector2) -> Mesh:
	var q := QuadMesh.new()
	q.size = size
	q.subdivide_width = 10
	q.subdivide_depth = 10
	var arrays := q.get_mesh_arrays()
	var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	for i in verts.size():
		var v := verts[i]
		var u := v.x / (size.x * 0.5)
		var w := v.y / (size.y * 0.5)
		v.z = CHIN_APEX - CHIN_DROP * (u * u + w * w)
		verts[i] = v
	arrays[Mesh.ARRAY_VERTEX] = verts
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return m


func _follow() -> void:
	for p in _panels:
		if not is_instance_valid(p.node):
			continue
		if _skel != null and is_instance_valid(_skel) and p.bone >= 0:
			p.node.global_transform = _skel.global_transform * _skel.get_bone_global_pose(p.bone) * p.off


func _exit_tree() -> void:
	if _body != null and is_instance_valid(_body):
		LOOK.set_glow(_body, GLOW_NORMAL, GLOW_SURFACE)  # never leave the windows dark
