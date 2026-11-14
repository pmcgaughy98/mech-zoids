extends Node3D
## Kangaroo kinetic discharge (kangaroo effects lane, 2026-11-12). Visual only. Preston sent kit design's kinetic
## power to this lane as effects on the clips that already exist ("approve send to effects"): boxing stays the animal
## trait, but each punch fires stored kinetic force through capacitor gauntlets, and the hop and the tail kick are the
## charged legs releasing it. Kit design's line: guard stays a plain block (the rhino's Seismic charge owns
## absorb-and-release), so nothing here touches guard_block.
## - Charge: a ring closing in on each glove, faster and brighter with the rhythm stacks (kit.rhythm / rhythm_max).
## - Release: on every landed punch a pressure ring bursts from the leading glove along the punch, with a pin of
##   white light for a few frames. The hop and the kick release from the feet.
## Made by kangaroo_ring_fx.gd (its child), so the kit needs no extra hookup. Sizes and times are proposals.
const SHADER := preload("res://shaders/kangaroo_kinetic.gdshader")
const FISTS := ["Bone_019", "Bone_024"] ## left, right finger bones
const FEET := ["Bone_013", "Bone_008"]
## cue -> [ring size m, life s, from: "fist" | "feet" | "ground"]
const RELEASE := {
	"jab_hit": [0.8, 0.14, "fist"],
	"hook_hit": [1.0, 0.16, "fist"],
	"hopjab_hit": [0.8, 0.14, "fist"],
	"counter_hit": [1.1, 0.16, "fist"],
	"bout_beat": [1.0, 0.16, "fist"],
}
const CRIT_SCALE := 1.35
## The tail kick blast: [metres ahead of the feet, ring size m, start delay s], a widening cone.
const BLAST_RINGS := [[0.25, 1.0, 0.0], [0.65, 1.5, 0.035], [1.1, 2.0, 0.07]]
const BLAST_LIFE := 0.2
const BLAST_SPEED := 3.0 ## m/s the rings travel on along the kick, easing out
const BLAST_GROUND := 2.2
const LEG_CHARGE_SIZE := 0.9
const LEG_CHARGE_LIFE := 0.32
## The hop jab's push-off: rings fired back and down from the feet (HOP_TILT is how far down), smaller than the kick.
const HOP_RINGS := [[0.15, 0.8, 0.0], [0.45, 1.1, 0.03], [0.8, 1.4, 0.06]]
const HOP_TILT := 0.6
const HOP_SPEED := 2.5
const HOP_GROUND := 1.8
const HOP_CHARGE_LIFE := 0.16 ## the HopJab wind-up before its hop event (0.14 s)
const CORE_SIZE := 0.45
const CORE_LIFE := 0.07
const CHARGE_SIZE := 1.0 ## take 2 (Preston: "Yes, bigger charge"); 0.55 was too small to read at the match camera

var kit: Node
var actor: Node3D
var tint := Color(0.45, 1.0, 0.82)
var releases := 0 ## count, for the recording check
var _charge_nodes: Array = []
var _charge_mats: Array = []
var _live: Array = []
var _clock := 0.0
var _was := ""


func setup(k: Node, p: Node3D) -> void:
	kit = k
	actor = p
	kit.cue.connect(_on_cue)
	for i in FISTS.size():
		var m := _mat(1, true)
		var n := _quad(CHARGE_SIZE, m)
		_charge_nodes.append(n)
		_charge_mats.append(m)


func _on_cue(cue_name: String) -> void:
	if cue_name == "rhythm_full":
		for f in FISTS:
			_core(_bone(f), CORE_SIZE * 0.8)
		return
	if cue_name == "tail_brace":
		_leg_charge()
		return
	if cue_name == "tail_hit":
		_leg_blast()
		return
	if cue_name == "hop":
		_hop_blast()
		return
	if not RELEASE.has(cue_name):
		return
	var spec: Array = RELEASE[cue_name]
	var size: float = spec[0]
	if cue_name == "bout_beat" and bool(kit.get("last_crit")):
		size *= CRIT_SCALE
	var fwd := _forward()
	var at: Vector3
	var axis := fwd
	match spec[2]:
		"fist":
			at = _lead_fist(fwd) + fwd * 0.12
		"feet":
			at = _bone(FEET[0]).lerp(_bone(FEET[1]), 0.5) + fwd * 0.2
		_:
			at = actor.global_position + Vector3.UP * 0.06
			axis = Vector3.UP
	_shock(at, axis, size, spec[1])
	_core(at, CORE_SIZE * (1.3 if spec[2] != "fist" else 1.0))
	releases += 1


func _process(delta: float) -> void:
	if kit == null or not is_instance_valid(kit):
		return
	_clock += delta
	var now := String(kit.get("current"))
	if now != _was and now == "HopJab":
		_leg_charge(HOP_CHARGE_LIFE)  # no cue before the hop, so the wind-up starts with the move itself
	_was = now
	var mx: float = maxf(float(kit.get("rhythm_max")), 1.0)
	var c: float = clampf(float(kit.get("rhythm")) / mx, 0.0, 1.0)
	for i in _charge_nodes.size():
		var n: MeshInstance3D = _charge_nodes[i]
		n.visible = c > 0.0
		n.global_position = _bone(FISTS[i])
		_charge_mats[i].set_shader_parameter("charge", c)
		_charge_mats[i].set_shader_parameter("segs", mx)
		_charge_mats[i].set_shader_parameter("t", _clock + i * 0.37)
	var keep: Array = []
	for g in _live:
		if g.get("delay", 0.0) > 0.0:
			g.delay -= delta
			g.node.visible = g.delay <= 0.0
			keep.append(g)
			continue
		g.t += delta
		var k: float = clampf(g.t / g.life, 0.0, 1.0)
		if k >= 1.0:
			g.node.queue_free()
			continue
		if g.has("bone"):
			g.node.global_position = _bone(g.bone)
		if g.has("vel"):
			g.node.global_position += g.vel * delta * (1.0 - k)
		g.mat.set_shader_parameter("t", g.t if g.get("secs", false) else k)
		keep.append(g)
	_live = keep


## Tail kick, part 1 (Preston 2026-11-12, "do the tail kick blast next"): on the brace, both feet gather force,
## a full ring closing in on each foot for the wind-up (TailKick brace to hit is about 0.3 s).
func _leg_charge(life := LEG_CHARGE_LIFE) -> void:
	for f in FEET:
		var m := _mat(1, true)
		m.set_shader_parameter("charge", 1.0)
		m.set_shader_parameter("segs", 1.0)
		var n := _quad(LEG_CHARGE_SIZE, m)
		n.global_position = _bone(f)
		_live.append({"node": n, "mat": m, "t": 0.0, "life": life, "bone": f, "secs": true})


## Tail kick, part 2: the charged legs release. Three pressure rings fire forward one after another in a widening
## cone, travelling on along the kick so the blast has depth from the match camera, not one flat disc; a ring on
## the ground where the tail and feet push off; a white pin at the feet. Same look for the slot 2 kick and the
## title bout's finisher (Preston: "Yes, same blast"); both fire tail_hit.
func _leg_blast() -> void:
	var fwd := _forward()
	var at := _bone(FEET[0]).lerp(_bone(FEET[1]), 0.5)
	_cone(at, fwd, BLAST_RINGS, BLAST_SPEED)
	_shock(actor.global_position + Vector3.UP * 0.06, Vector3.UP, BLAST_GROUND, 0.24)
	_core(at + fwd * 0.2, CORE_SIZE * 1.6)
	releases += 1


## Hop jab (Preston 2026-11-13, "Hop jab leg blast"): the same charged legs, used to jump. The feet gather force in the
## wind-up (HopJab starts to its hop event, 0.14 s), then on "hop" the release fires back and down from the feet like
## thrust, the way a jump pushes off the ground, while the body flies forward. Smaller than the kick's blast.
func _hop_blast() -> void:
	var fwd := _forward()
	var at := _bone(FEET[0]).lerp(_bone(FEET[1]), 0.5)
	var axis := (-fwd + Vector3.DOWN * HOP_TILT).normalized()
	_cone(at, axis, HOP_RINGS, HOP_SPEED)
	_shock(actor.global_position + Vector3.UP * 0.06, Vector3.UP, HOP_GROUND, 0.22)
	_core(at, CORE_SIZE * 1.3)
	releases += 1


## Pressure rings fired one after another along `axis` from `at`, each [metres along, size, delay], travelling on.
func _cone(at: Vector3, axis: Vector3, rings: Array, speed: float) -> void:
	var up := Vector3.UP if absf(axis.dot(Vector3.UP)) < 0.95 else Vector3.FORWARD
	for spec in rings:
		var m := _mat(0, false)
		var n := _quad(spec[1], m)
		n.global_position = at + axis * spec[0]
		n.global_basis = Basis.looking_at(axis, up)
		n.visible = spec[2] <= 0.0
		_live.append({"node": n, "mat": m, "t": 0.0, "life": BLAST_LIFE, "delay": spec[2], "vel": axis * speed})


func _shock(at: Vector3, axis: Vector3, size: float, life: float) -> void:
	var m := _mat(0, false)
	var n := _quad(size, m)
	n.global_position = at
	var up := Vector3.UP if absf(axis.dot(Vector3.UP)) < 0.95 else Vector3.FORWARD
	n.global_basis = Basis.looking_at(axis, up)
	_live.append({"node": n, "mat": m, "t": 0.0, "life": life})


func _core(at: Vector3, size: float) -> void:
	var m := _mat(2, true)
	var n := _quad(size, m)
	n.global_position = at
	_live.append({"node": n, "mat": m, "t": 0.0, "life": CORE_LIFE})


func _mat(mode: int, bb: bool) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter("mode", mode)
	m.set_shader_parameter("billboard", bb)
	m.set_shader_parameter("tint", Vector3(tint.r, tint.g, tint.b))
	m.render_priority = 2
	return m


func _quad(size: float, m: ShaderMaterial) -> MeshInstance3D:
	var q := QuadMesh.new()
	q.size = Vector2(size, size)
	var n := MeshInstance3D.new()
	n.mesh = q
	n.material_override = m
	n.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(n)
	n.top_level = true
	return n


func _forward() -> Vector3:
	var face: Variant = actor.get("facing") if is_instance_valid(actor) else null
	if face is Vector3 and Vector3(face.x, 0.0, face.z).length() > 0.01:
		return Vector3(face.x, 0.0, face.z).normalized()
	return Vector3(0, 0, 1)


func _lead_fist(fwd: Vector3) -> Vector3:
	var a := _bone(FISTS[0])
	var b := _bone(FISTS[1])
	return a if a.dot(fwd) >= b.dot(fwd) else b


func _bone(bone: String) -> Vector3:
	var fallback: Vector3 = actor.global_position + Vector3.UP if is_instance_valid(actor) else Vector3.ZERO
	var body: Variant = actor.get("body") if is_instance_valid(actor) else null
	if body == null or not is_instance_valid(body):
		return fallback
	var sk: Variant = body.get("skeleton")
	if not (sk is Skeleton3D):
		return fallback
	var s := sk as Skeleton3D
	var i := s.find_bone(bone)
	if i < 0:
		return fallback
	return s.global_transform * s.get_bone_global_pose(i).origin
