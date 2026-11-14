extends Node3D
## The kangaroo's effects (kangaroo-3d session, 2026-11-11). Visual only: it deals no damage and moves nothing.
## It listens to the body's clip events (MechModel3D.event) and watches which action is playing, so it works the
## same whether a clip was started by the kit or by a test script. Built the way the gorilla's effect nodes are:
## procedural pieces, unshaded, freed when they finish. Preston's pick for the look: the mint ring with three
## notches on the forearm circle (the rhino's drum ring design).
##
## Why arcs and flashes: measured from SMITE footage (docs/reference/kangaroo-combat-references-2026-11-10.md, 3a),
## a punch seen from the match camera is read by the arc behind the fist and the flash on the target, not the fist.
##
## Use:   var fx = preload("res://scripts/moba3d/kangaroo_fx.gd").new()
##        player.add_child(fx); fx.setup(player.body, player)
## The ported kit can also call: set_rhythm(stacks), ring(centre, radius, seconds), flash(at, size).
## Every size, colour and time here is a placeholder for Preston.

const MINT := Color(0.66, 0.98, 0.84)
const WHITE := Color(1.0, 1.0, 1.0)

## The two forearm circles in their bone's own space, measured from the mesh by build_r4_ring.py
## (D:/dev/_scratch/kangaroo-3d/out/r4_ring_fit.json). Metres.
const RINGS := {
	"Bone_021": {"c": Vector3(0.11783, 0.17109, -0.09738), "n": Vector3(0.56551, 0.15011, -0.81097), "up": Vector3(-0.50884, -0.71034, -0.48631), "r_in": 0.0791, "r_out": 0.1145},
	"Bone_026": {"c": Vector3(-0.12935, 0.17254, -0.08516), "n": Vector3(-0.65121, 0.15887, -0.74208), "up": Vector3(0.45871, -0.69659, -0.55167), "r_in": 0.0775, "r_out": 0.1171},
}
## Which bone leaves an arc in each clip, and between which seconds of the clip. Fists are the finger bones
## (left Bone_019, right Bone_024); feet are the foot bones (left Bone_013, right Bone_008).
const TRAILS := {
	"Jab_Left": [["Bone_019", 0.10, 0.27]],
	"Jab_Right": [["Bone_024", 0.10, 0.27]],
	"Jab_Right_Quick": [["Bone_024", 0.03, 0.17]],
	"Hook_Right": [["Bone_024", 0.10, 0.36]],
	"Guard_Counter": [["Bone_024", 0.11, 0.29]],
	"HopJab": [["Bone_019", 0.44, 0.58], ["Bone_024", 0.56, 0.70], ["Bone_019", 0.68, 0.82], ["Bone_024", 0.80, 0.94]],
	"TailKick": [["Bone_013", 0.38, 0.57], ["Bone_008", 0.38, 0.57]],
	"Flurry": [["Bone_019", 0.02, 0.16], ["Bone_024", 0.14, 0.28], ["Bone_019", 0.26, 0.40], ["Bone_024", 0.38, 0.52]],
	"Guard_Sweep": [["Tail_Pad", 0.12, 0.46]],
}
const TRAIL_LIFE := 0.16      ## seconds a point of the arc lasts
const TRAIL_WIDTH := 0.20     ## metres at the fist
const RING_RADIUS := 5.0      ## the boxing ring, metres (placeholder: the kit has no number yet)
const RING_SECONDS := 4.0

var body: Node3D              ## the MechModel3D
var actor: Node3D
var skeleton: Skeleton3D
var _action := ""
var _t := 0.0
var _trail_nodes := {}        ## bone name -> {"node": MeshInstance3D, "pts": Array}
var _ring_mats: Array = []
var _pulse := 0.0
var _rhythm := 3
var _live: Array = []         ## timed pieces: {"node", "t", "life", "kind", ...}
var _trail_mat: StandardMaterial3D
var _ring_shader: Shader
var _burst_shader: Shader


func setup(b: Node3D, a: Node3D) -> void:
	body = b
	actor = a
	skeleton = b.skeleton
	_trail_mat = _vertex_mat(true)
	_ring_shader = Shader.new()
	_ring_shader.code = """shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;
uniform vec4 tint : source_color = vec4(0.66, 0.98, 0.84, 1.0);
uniform float energy = 0.6;
uniform float r_in = 0.55;
uniform float r_out = 0.83;
uniform float lit = 3.0;
uniform float notch = 0.085;
void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	p.y = -p.y;
	float r = length(p);
	float band = smoothstep(r_in - 0.03, r_in + 0.03, r) * (1.0 - smoothstep(r_out - 0.03, r_out + 0.03, r));
	float keep = 1.0;
	for (int i = 0; i < 3; i++) {
		float a0 = 1.5707963 - float(i) * 2.0943951;
		vec2 d = vec2(cos(a0), sin(a0));
		float dist = abs(p.x * d.y - p.y * d.x);
		if (dot(p, d) > 0.0 && dist < notch) { keep = 0.0; }
	}
	float a = atan(p.y, p.x);
	float seg = floor(mod(1.5707963 - a, 6.2831853) / 2.0943951);
	float on = step(seg + 0.5, lit);
	float m = band * keep * mix(0.12, 1.0, on);
	ALBEDO = tint.rgb * energy * m;
	ALPHA = m;
}
"""
	_burst_shader = Shader.new()
	_burst_shader.code = """shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled, depth_test_disabled;
uniform vec4 tint : source_color = vec4(0.66, 0.98, 0.84, 1.0);
uniform float t = 0.0;
uniform float rays = 6.0;
void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float r = length(p);
	float a = atan(p.y, p.x);
	float grow = mix(0.25, 0.92, pow(t, 0.5));
	float ring = smoothstep(grow - 0.16, grow - 0.04, r) * (1.0 - smoothstep(grow, grow + 0.05, r));
	float star = pow(abs(cos(a * rays * 0.5)), 14.0) * (1.0 - smoothstep(0.0, grow, r));
	float core = (1.0 - smoothstep(0.0, 0.30, r)) * (1.0 - t);
	float fade = 1.0 - t * t;
	float m = clamp(ring + star * 0.8 + core, 0.0, 1.0) * fade;
	ALBEDO = mix(tint.rgb, vec3(1.0), core) * m * 1.6;
	ALPHA = m;
}
"""
	for bone in RINGS:
		_add_forearm_ring(bone, RINGS[bone])
	if b.has_signal("event"):
		b.event.connect(_on_event)
	set_rhythm(3)


## How many of the three ring segments are lit (the rhythm passive's stacks, if the kit wants to show them).
func set_rhythm(stacks: int) -> void:
	_rhythm = clampi(stacks, 0, 3)
	for m in _ring_mats:
		m.set_shader_parameter("lit", float(_rhythm))


## A burst at a world point, facing the camera.
func flash(at: Vector3, size := 1.0, tint := MINT, life := 0.18) -> void:
	var node := MeshInstance3D.new()
	var q := QuadMesh.new()
	q.size = Vector2(size, size)
	node.mesh = q
	var m := ShaderMaterial.new()
	m.shader = _burst_shader
	m.set_shader_parameter("tint", tint)
	node.material_override = m
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = at
	var cam := get_viewport().get_camera_3d()
	if cam != null:
		node.look_at(cam.global_position, Vector3.UP)
		node.rotate_object_local(Vector3.UP, PI)
	_live.append({"node": node, "t": 0.0, "life": life, "kind": "burst", "mat": m})
	_pulse = 1.0


## The boxing ring on the ground: a mint band with three notches and a low wall of light.
func ring(centre: Vector3, radius := RING_RADIUS, seconds := RING_SECONDS) -> void:
	var node := MeshInstance3D.new()
	node.mesh = _ring_mesh(radius, 0.16, 0.5, true)
	node.material_override = _vertex_mat(false)
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = centre + Vector3.UP * 0.05
	node.scale = Vector3(0.2, 1.0, 0.2)
	_live.append({"node": node, "t": 0.0, "life": seconds, "kind": "ring"})


func _puff(at: Vector3) -> void:
	var node := MeshInstance3D.new()
	node.mesh = _ring_mesh(1.0, 0.10, 0.0, false)
	node.material_override = _vertex_mat(false)
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(node)
	node.top_level = true
	node.global_position = Vector3(at.x, at.y + 0.04, at.z)
	_live.append({"node": node, "t": 0.0, "life": 0.3, "kind": "puff"})


func _on_event(clip: String, event_name: String, _damage: bool) -> void:
	if event_name == "hit":
		flash(_strike_point(clip), 1.5 if clip == "TailKick" else (1.25 if clip == "Hook_Right" else 1.0))
	elif event_name == "block":
		var facing: Vector3 = actor.facing if "facing" in actor else Vector3.FORWARD
		flash(_bone_pos("Bone_020").lerp(_bone_pos("Bone_025"), 0.5) + facing * 0.3, 1.6, WHITE, 0.22)
	elif event_name == "ring":
		_puff(_bone_pos("Tail_Pad"))  # the kit draws the ring itself now (title bout, 2026-11-11): it knows where and how big
	elif event_name == "land" or event_name == "brace" or event_name == "tail_thump":
		_puff(actor.global_position if event_name == "land" else _bone_pos("Tail_Pad"))
	elif event_name == "glove_tap":
		flash(_bone_pos("Bone_019").lerp(_bone_pos("Bone_024"), 0.5), 0.6, WHITE, 0.12)


func _strike_point(clip: String) -> Vector3:
	var best := ""
	var gap := 1e9
	for entry in TRAILS.get(clip, []):
		var d: float = 0.0 if (_t >= entry[1] and _t <= entry[2]) else minf(absf(_t - entry[1]), absf(_t - entry[2]))
		if d < gap:
			gap = d
			best = entry[0]
	if clip == "TailKick":
		return _bone_pos("Bone_012").lerp(_bone_pos("Bone_007"), 0.5)
	return _bone_pos(best) if best != "" else actor.global_position + Vector3.UP


func _bone_pos(bone: String) -> Vector3:
	var i := skeleton.find_bone(bone)
	if i < 0:
		return actor.global_position + Vector3.UP
	return skeleton.global_transform * skeleton.get_bone_global_pose(i).origin


func _process(delta: float) -> void:
	if body == null or not is_instance_valid(body):
		return
	var now: String = body.action if "action" in body else ""
	if now != _action:
		_action = now
		_t = 0.0
	else:
		_t += delta
	_update_trails(delta)
	_pulse = maxf(_pulse - delta * 5.0, 0.0)
	for m in _ring_mats:
		m.set_shader_parameter("energy", 0.55 + 1.6 * _pulse)
	var keep: Array = []
	for item in _live:
		item.t += delta
		var k: float = clampf(item.t / item.life, 0.0, 1.0)
		var node: MeshInstance3D = item.node
		if item.kind == "burst":
			item.mat.set_shader_parameter("t", k)
		elif item.kind == "ring":
			var grow: float = clampf(item.t / 0.25, 0.0, 1.0)
			var s: float = lerpf(0.2, 1.0, 1.0 - pow(1.0 - grow, 3.0))
			node.scale = Vector3(s, 1.0, s)
			var fade: float = clampf((item.life - item.t) / 0.5, 0.0, 1.0)
			node.material_override.albedo_color = Color(1, 1, 1, fade)
		elif item.kind == "puff":
			var s2: float = lerpf(0.3, 1.15, pow(k, 0.5))
			node.scale = Vector3(s2, 1.0, s2)
			node.material_override.albedo_color = Color(1, 1, 1, (1.0 - k) * 0.8)
		if item.t >= item.life:
			node.queue_free()
		else:
			keep.append(item)
	_live = keep


func _update_trails(delta: float) -> void:
	var cam := get_viewport().get_camera_3d()
	var active := {}
	for entry in TRAILS.get(_action, []):
		if _t >= entry[1] and _t <= entry[2]:
			active[entry[0]] = true
	for bone in active:
		if not _trail_nodes.has(bone):
			var node := MeshInstance3D.new()
			node.mesh = ImmediateMesh.new()
			node.material_override = _trail_mat
			node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(node)
			node.top_level = true
			node.global_transform = Transform3D.IDENTITY
			_trail_nodes[bone] = {"node": node, "pts": []}
		_trail_nodes[bone].pts.append({"p": _bone_pos(bone), "age": 0.0})
	for bone in _trail_nodes.keys():
		var tr: Dictionary = _trail_nodes[bone]
		var pts: Array = []
		for pt in tr.pts:
			pt.age += delta
			if pt.age < TRAIL_LIFE:
				pts.append(pt)
		tr.pts = pts
		var im: ImmediateMesh = tr.node.mesh
		im.clear_surfaces()
		if pts.size() < 2:
			if pts.is_empty() and not active.has(bone):
				tr.node.queue_free()
				_trail_nodes.erase(bone)
			continue
		im.surface_begin(Mesh.PRIMITIVE_TRIANGLE_STRIP)
		for i in pts.size():
			var p: Vector3 = pts[i].p
			var dir: Vector3 = (pts[mini(i + 1, pts.size() - 1)].p - pts[maxi(i - 1, 0)].p)
			var to_cam: Vector3 = (cam.global_position - p) if cam != null else Vector3.UP
			var side: Vector3 = dir.cross(to_cam)
			side = side.normalized() if side.length() > 1e-5 else Vector3.UP
			var life: float = 1.0 - pts[i].age / TRAIL_LIFE
			var w: float = TRAIL_WIDTH * 0.5 * life
			var col := Color(MINT.r, MINT.g, MINT.b, life * 0.85)
			im.surface_set_color(col)
			im.surface_add_vertex(p + side * w)
			im.surface_set_color(col)
			im.surface_add_vertex(p - side * w)
		im.surface_end()


func _add_forearm_ring(bone: String, fit: Dictionary) -> void:
	if skeleton.find_bone(bone) < 0:
		return
	var att := BoneAttachment3D.new()
	skeleton.add_child(att)
	att.bone_name = bone
	var node := MeshInstance3D.new()
	var q := QuadMesh.new()
	var half: float = fit.r_out * 1.2
	q.size = Vector2(half * 2.0, half * 2.0)
	node.mesh = q
	var m := ShaderMaterial.new()
	m.shader = _ring_shader
	m.set_shader_parameter("tint", MINT)
	m.set_shader_parameter("r_in", fit.r_in / half)
	m.set_shader_parameter("r_out", fit.r_out / half)
	node.material_override = m
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	att.add_child(node)
	var z: Vector3 = fit.n.normalized()
	var y: Vector3 = (fit.up - z * fit.up.dot(z)).normalized()
	var x: Vector3 = y.cross(z).normalized()
	node.transform = Transform3D(Basis(x, y, z), fit.c + z * 0.008)
	_ring_mats.append(m)


## A flat ring of the given radius and band width, with three notches if asked, plus a low wall if wall > 0.
func _ring_mesh(radius: float, band: float, wall: float, notched: bool) -> ImmediateMesh:
	var im := ImmediateMesh.new()
	var steps := 96
	var gap := 0.055      ## half the notch, radians
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in steps:
		var a0 := TAU * i / steps
		var a1 := TAU * (i + 1) / steps
		var mid := (a0 + a1) * 0.5
		if notched:
			var skip := false
			for k in 3:
				if absf(angle_difference(mid, PI * 0.5 + TAU * k / 3.0)) < gap:
					skip = true
			if skip:
				continue
		var p0 := Vector3(cos(a0), 0, sin(a0))
		var p1 := Vector3(cos(a1), 0, sin(a1))
		var col := Color(MINT.r, MINT.g, MINT.b, 0.9)
		var soft := Color(MINT.r, MINT.g, MINT.b, 0.0)
		for v in [[p0 * radius, col], [p1 * radius, col], [p0 * (radius - band), col], [p1 * radius, col], [p1 * (radius - band), col], [p0 * (radius - band), col]]:
			im.surface_set_color(v[1])
			im.surface_add_vertex(v[0])
		if wall > 0.0:
			var low := Color(MINT.r, MINT.g, MINT.b, 0.35)
			var up := Vector3.UP * wall
			for v in [[p0 * radius, low], [p1 * radius, low], [p0 * radius + up, soft], [p1 * radius, low], [p1 * radius + up, soft], [p0 * radius + up, soft]]:
				im.surface_set_color(v[1])
				im.surface_add_vertex(v[0])
	im.surface_end()
	return im


func _vertex_mat(additive: bool) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	m.vertex_color_use_as_albedo = true
	m.cull_mode = BaseMaterial3D.CULL_DISABLED
	if additive:
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	return m
