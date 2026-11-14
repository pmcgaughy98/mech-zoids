extends Node3D
## Kangaroo afterimages (kangaroo effects lane, 2026-11-12). Visual only. Preston: "multiple faded red copies bobbing
## delayed trailing the fighters movements", as boxing shows do for fighters, "or sometimes for flash when hes moving
## fast". While the kangaroo boxes (the title bout), leaps (slot 1) or kicks, a frozen copy of its pose is left behind
## every SPAWN_EVERY seconds and fades over LIFE, so four or five copies trail each move.
## Colour: `tint`. The look lane's rule is no red in the kangaroo's own effects (red marks enemies), so it defaults to
## the kangaroo's mint; Preston picks.
## Made by kangaroo_ring_fx.gd (its child), so the kit needs no extra hookup.
const GHOST := preload("res://shaders/kangaroo_ghost.gdshader")
const ACTIVE := ["Bout", "HopJab", "TailKick"] ## kit.current values that leave afterimages
const SPAWN_EVERY := 0.06
const LIFE := 0.3
const PEAK := 1.0
const DRIFT := 0.25 ## metres each copy slides back behind the fighter over its life
const STILL := 0.04 ## a copy only drops when the body moved this far (m) since the last one: a plain jab leaves none
## Bob and weave (Preston 2026-11-12: "bobbing and weaving around them ... to emphasize ... its bobbing and weaving
## agile"). Visual only: during the bout the inner model slips to alternate sides between punches and ducks on the
## way, so the afterimages trail a weaving fighter. The machine's real position and hits are untouched.
const WEAVE_SIDE := 0.55 ## metres to each side of the line to the target
const WEAVE_DUCK := 0.22 ## metres it dips mid-slip
const WEAVE_LEAN := 0.16 ## radians of roll into the slip
const WEAVE_MOVE := 0.7  ## share of each beat spent moving; the rest it holds and throws the punch
const WEAVE_BACK := 0.15 ## seconds to ease back to centre after the bout
## Off since 2026-11-12: the kit now moves the kangaroo round the target for real (cue "bout_slip", Slip_Left and
## Slip_Right clips that drop and lean the body), so this sway on top would double it. Kept for reference only.
const WEAVE_ON := false

var kit: Node
var actor: Node3D
var tint := Color(0.32, 1.0, 0.78)
var spawned := 0
var _live: Array = []
var _since := 0.0
var _last_snap := Vector3(INF, INF, INF)
var _weave := Vector3.ZERO ## x side (-1..1), y duck (0..1), z unused
var _weave_from := 0.0
var _weave_beat := -1


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p


func _process(delta: float) -> void:
	if kit == null or not is_instance_valid(kit):
		return
	var on: bool = String(kit.get("current")) in ACTIVE or bool(kit.get("ring_on"))
	if WEAVE_ON:
		_tick_weave(delta)
	_since += delta
	if on and _since >= SPAWN_EVERY:
		_since = 0.0
		_snap()
	var keep: Array = []
	for g in _live:
		g.t += delta
		var k: float = clampf(g.t / LIFE, 0.0, 1.0)
		if k >= 1.0:
			for n in g.nodes:
				n.queue_free()
			continue
		var f: float = PEAK * pow(1.0 - k, 1.5)
		g.mat.set_shader_parameter("fade", f)
		var off: Vector3 = g.back * DRIFT * (1.0 - pow(1.0 - k, 2.0))
		for i in g.nodes.size():
			g.nodes[i].global_position = g.base[i] + off
		keep.append(g)
	_live = keep


## One frozen copy: every skinned mesh of the body baked in its current pose, placed where it stands now.
func _snap() -> void:
	if DisplayServer.get_name() == "headless":
		return  # nothing is drawn, and skins are not registered
	var b: Variant = actor.get("body") if is_instance_valid(actor) else null
	if b == null or not is_instance_valid(b) or not b.has_method("_meshes"):
		return
	var mdl: Variant = b.get("_model")
	if mdl is Node3D:
		var at: Vector3 = (mdl as Node3D).global_position
		if at.distance_to(_last_snap) < STILL:
			return
		_last_snap = at
	var mat := ShaderMaterial.new()
	mat.shader = GHOST
	mat.set_shader_parameter("tint", Vector3(tint.r, tint.g, tint.b))
	mat.set_shader_parameter("fade", PEAK)
	var nodes: Array = []
	for m in b.call("_meshes"):
		var mi := m as MeshInstance3D
		if mi == null or not mi.is_visible_in_tree() or not mi.has_method("bake_mesh_from_current_skeleton_pose"):
			continue
		# The bake needs a live skin registration, not just a skin and a skeleton: headless runs (match_check) have
		# none, which threw 382 errors on 2026-11-12. Skinned but unregistered means skip, not mi.mesh (a rest pose).
		var ref: SkinReference = mi.get_skin_reference()
		var skinned: bool = ref != null and ref.get_skeleton().is_valid()
		if mi.skin != null and not skinned:
			continue
		var baked: Mesh = mi.bake_mesh_from_current_skeleton_pose() if skinned else mi.mesh
		if baked == null:
			continue
		var g := MeshInstance3D.new()
		g.mesh = baked
		g.material_override = mat
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(g)
		g.top_level = true
		g.global_transform = mi.global_transform
		nodes.append(g)
	if not nodes.is_empty():
		var face: Variant = actor.get("facing")
		var back := Vector3.ZERO
		if face is Vector3 and (face as Vector3).length() > 0.01:
			back = -(face as Vector3).normalized()
		back.y = 0.0
		var base: Array = []
		for n in nodes:
			base.append(n.global_position)
		_live.append({"nodes": nodes, "mat": mat, "t": 0.0, "back": back, "base": base})
		spawned += 1


## Slip side to side between punches: beat n's punch is thrown from side (-1)^n, reached over the first WEAVE_MOVE of
## the gap before it with a duck in the middle of the move.
func _tick_weave(delta: float) -> void:
	var b: Variant = actor.get("body") if is_instance_valid(actor) else null
	if b == null or not is_instance_valid(b):
		return
	var mdl: Variant = b.get("_model")
	if not (mdl is Node3D):
		return
	var nb: Variant = kit.get("bout_next_beat")
	var gap: float = 0.65
	var side := 0.0
	var duck := 0.0
	if bool(kit.get("ring_on")) and nb != null and float(nb) >= 0.0:
		var beat: int = int(kit.get("bout_beat"))
		if beat != _weave_beat:
			_weave_beat = beat
			_weave_from = _weave.x
		var target: float = 1.0 if beat % 2 == 0 else -1.0
		var u: float = clampf(1.0 - float(nb) / gap, 0.0, 1.0)
		var m: float = smoothstep(0.0, WEAVE_MOVE, u)
		side = lerpf(_weave_from, target, m)
		duck = sin(PI * clampf(u / WEAVE_MOVE, 0.0, 1.0)) * absf(target - _weave_from) * 0.5
	else:
		_weave_beat = -1
		var k: float = 1.0 - exp(-delta / maxf(WEAVE_BACK / 3.0, 0.001))
		side = lerpf(_weave.x, 0.0, k)
		duck = lerpf(_weave.y, 0.0, k)
	_weave = Vector3(side, duck, 0.0)
	var face: Variant = actor.get("facing")
	var fwd := Vector3(0, 0, 1)
	if face is Vector3 and Vector3(face.x, 0.0, face.z).length() > 0.01:
		fwd = Vector3(face.x, 0.0, face.z).normalized()
	var right := fwd.cross(Vector3.UP).normalized()
	var world := right * side * WEAVE_SIDE + Vector3.DOWN * duck * WEAVE_DUCK
	var m3 := mdl as Node3D
	m3.position = (b as Node3D).global_transform.basis.inverse() * world
	m3.rotation.z = -side * WEAVE_LEAN
