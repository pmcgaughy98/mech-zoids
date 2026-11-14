extends Node3D
## Bison ability effects, smooth (bison effects lane, 2026-11-13). Visual only, an observer like pangolin_fx.gd: it
## edits no kit and no body, and deals nothing. All four abilities, footfall dust and the cooldown stacks.
## In the match, bison_fx_installer.gd hangs it under each BisonKit (Preston's "also turn on", 2026-11-14).
##
## CONTRACT (agreed with the game feel lane; bison_kit.gd fires it, and the launcher's stub stands in for it there):
##   kit signal cue(name)   "eruption" when the cast starts (optional; the body's clip events carry the timing)
##   kit fields, read if present:
##     eruption_radius: float   metres from the bison to where the bombs land (default RING_R)
##     slag_time: float         seconds a slag patch stays (default SLAG_TIME)
##     eruption_points: Array   four Vector3 landing points in erupt order fl, rr, fr, rl, if the kit aims them itself
##   body (MechModel3D) signal event(clip, name, damage), clip "Eruption" (r4 profile): gather 0.04, roar 0.32,
##     erupt_fl 0.38, erupt_rr 0.48, erupt_fr 0.58, erupt_rl 0.68, recover 1.05
##
## ERUPTION. Structure from Vulcan's Magma Bomb and Earthshaker (SMITE 2, measured at 15 fps), see
## docs/reference/bison-fx-synthesis-2026-11-13.md. Nothing copied, structure only:
##   gather:  the four stack mouths heat up (a small glow on each, building to the first shot)
##   roar:    two short steam jets from the steam vents behind the stacks
##   erupt_*: at that stack, a short muzzle burst and a soot puff; its glow goes out; a molten bomb (dark crust, hot
##            seams) climbs on a thick hot trail, falls steeply on a thin one, and lands on a ring round the bison at
##            that stack's corner, 0.72 s after launch (Magma Bomb flew 0.73 s)
##   falling: the floor under it heats for the last 0.3 s (Earthshaker's floor reddened just before landing)
##   landing: a 2 to 4 cell spiky burst, a floor glow that cools, molten chunks that fly and fall, basalt dust, and a
##            slag patch with crust lumps that cools and fades after SLAG_TIME (Magma Bomb left a dark scorch with hot
##            spots)
## COUPLING CHAIN (slot 1). Kit cues (proposed; the launcher stub sends them):
##   "chain_fire"   at Chain_Throw "fire" (0.283 s). Fields: chain_target (Node3D or null), chain_end (Vector3, where a miss
##                  reaches). A fire at a target already coupled is a refire: a heat pulse runs out along that chain.
##   "chain_couple" the chain caught chain_target;  "chain_miss" it caught nothing;  "chain_break" chain_target's chain
##                  ends (null: every chain).
## Structure from Ares' Shackles (SMITE 2, measured at 15 fps): a solid dark chain with real thickness, there within one
## cell, a heat pulse running caster to target in 5 to 6 cells on each refire, the target lit while chained. Ours: heavy
## iron links (a MultiMesh of tori, alternating 90 degrees) from the muzzle_purge socket, out in 0.09 s, hanging in a sag
## once coupled (the sag gives it height from the chase camera, where a straight chain would read end-on), a dim
## red-hot glow at rest, a pulse on couple and on each refire, a ring of links snapped round the target as a collar.
## A miss reaches chain_end and pulls back in 0.18 s; a break drops the chain and shrinks it away in 0.3 s.
## PLOW (slot 3). Body events on clip "Plow": windup (0.05) heats the four stacks; flare (0.40) flares them (a short
## burst stretched up and a soot puff each); throw (0.62) throws side dust off the far end of the sweep. Kit cue
## (proposed): "plow_hit" at the Plow "hit" event (0.467), field plow_targets (Array of Node3D): a burst on each and
## molten clods thrown to the bison's left. Field plow_radius (m, placeholder 2.4) if present.
## The sweep follows the real head: each frame the muzzle_purge socket's angle in the bison's frame is read (measured on
## the registered body: winds up 32 degrees right at 0.28 s, sweeps left through a low scoop at 0.40 to 0.48 s, ends
## 40 degrees left at 0.62 s), scaled by PLOW_GAIN onto an arc of radius plow_radius. While the head moves left faster
## than PLOW_SPEED, the arc grows: a standing wall of fire rises at the head and sinks behind it (bison_plow.gdshader,
## a strip with height, never a flat streak), clods and basalt dust are thrown along the sweep, and a band of charred,
## furrowed ground with cooling embers is left under it (bison_scorch.gdshader, gone by 2.4 s, so slag stays the only
## lasting mark). The plow is the animal's own trait, not a god's; its pieces reuse measured structure: Vulcan's
## Earthshaker exhaust for the stack flare and its reddening floor, Magma Bomb's short dark scorch with hot spots.
## FREIGHT (ult). Body events on clip "Freight_Brace": gather (0.04) heats the stacks and the rear coupler; stamp_l
## (0.46) and stamp_r (0.56) throw basalt dust off the front feet; braced (0.75) is the whistle: steam from both vents
## and a flare from every stack. Kit cue (proposed): "freight_chains" at Freight_Brace "chains_out" (0.26), field
## freight_targets (Array of Node3D): a Coupling Chain to each, from a rear coupler, coupled 0.09 s later without a
## further cue. The haul is read off the body: while its action is "Freight_Haul" (a held loop), all four stacks burn
## and rear stacks smoke, and on the clip's slag beats (0.15 and 0.75 of each loop, read off the clip position because
## a held loop's events fire once) a molten glob pours off a rear stack, alternating sides, and lands behind as a small
## slag patch (1.2 m, the same 4.5 s): the patches overlap into a short burning track. "chain_break" with a null
## target drops every chain at the haul's end; "freight_snap" (a stun or knock-up on the hauler) bursts each coupled
## chain at its middle and drops it. The coupler is taken from the model's bounds until the 3D lane adds a socket.
## FOOTFALLS. The bison's clips carry their footfalls as "step" events (Walk 4, Trot, Walk_Back, Strafe_Left and
## Strafe_Right 2 each), but the body fires events for actions only, and its `step` signal reads a "steps" row the
## bison does not have. So the locomotion loop playing is followed here by clip position, and each step time it passes
## raises a low basalt puff under the hooves that land then (STEP_FEET, measured on r5: the walk is rear-left,
## front-left, rear-right, front-right; the rest land in diagonal pairs). The trot's puffs are larger. If the body's
## `step` signal ever fires with a hoof name (fl, fr, rl, rr), that is used instead. Hit_Heavy "replant" (0.34 s, the
## front hooves land at 0.32 and 0.36) stamps Freight's dust under both front hooves. The hooves are the lowest rest
## bone in each quadrant (FEET).
## COOLDOWN STACKS (approved via the kit-design lane, 2026-11-13). Each stack wears a lit cap, a small glow over its
## mouth, while its ability is ready, and goes dark while that ability cools down. On or off only, never a gauge (the
## hippo owns fill-and-spend). Coming back ready, the cap pulses bright for a quarter second, then settles. The source
## needs no cue: `machine.cooldowns[slot]` (seconds left, the director fills it) with the slot from the kit's
## `stack_slot` (placeholder STACK_SLOT until the kit has one). An empty dict (no director) reads all ready. Dead or
## hidden, the caps are off.
## Colours: magma, Preston's pick 2026-11-13 ("Magma orange"): deep orange with yellow-white cores. "white" (white-hot
## seams) is kept for comparison; blue was
## shown and dropped, Preston 2026-11-13: "blue doesnt fit it at all"); both on dark basalt crust.
## Never red (red marks enemies), and none of the taken colours (lime, amber, purple, copper).
const BOMB := preload("res://shaders/bison_bomb.gdshader")
const TRAIL := preload("res://shaders/bison_trail.gdshader")
const BURST := preload("res://shaders/bison_burst.gdshader")
const GLOW := preload("res://shaders/bison_glow.gdshader")
const SLAG := preload("res://shaders/bison_slag.gdshader")
const DUST := preload("res://shaders/rhino_dust.gdshader") ## the rhino lane's smooth dust puff, used as is
const RING_R := 3.5 ## metres, placeholder: where the bombs land (the kit has no number yet)
const SLAG_TIME := 4.5 ## seconds, placeholder: how long a slag patch stays
const FLIGHT := 0.72 ## seconds from the stack to the floor
const APEX := 3.2 ## metres the arc climbs above the straight line at its middle
const BOMB_R := 0.17
const TRAIL_LIFE := 0.3 ## seconds a trail point lasts (Magma Bomb's rising trail went in about 4 cells)
const TRAIL_R := 0.13
const GRAVITY := 16.0
const SLAG_SIZE := 1.9 ## metres across the scorch; the crusted slag is about 60% of it
const SOOT := Color(0.16, 0.15, 0.145)
const BASALT_DUST := Color(0.36, 0.33, 0.30)
const FOOT_DUST := Color(0.56, 0.50, 0.43) ## the arena dust (rhino_dust's default, the rhino's and gorilla's): hoof and
## stamp dust has to read on the blue floor, and the darker basalt did not
const STEAM := Color(0.74, 0.74, 0.72)
## stack -> [bone, socket at rest in model space (Godot xyz, head toward +Z), corner it throws to (model x, z)]
const STACKS := {
	"fl": ["Bone_042", Vector3(0.171, 1.687, 0.237), Vector2(1, 1)],
	"rl": ["Bone_042", Vector3(0.168, 1.700, -0.038), Vector2(1, -1)],
	"fr": ["Bone_036", Vector3(-0.169, 1.687, 0.238), Vector2(-1, 1)],
	"rr": ["Bone_036", Vector3(-0.167, 1.700, -0.036), Vector2(-1, -1)],
}
const VENTS := {"steam_l": ["Bone_042", Vector3(0.17, 1.693, 0.10)], "steam_r": ["Bone_036", Vector3(-0.168, 1.694, 0.101)]}
const ORDER := ["fl", "rr", "fr", "rl"]
const CHAIN := preload("res://shaders/bison_chain.gdshader")
const MUZZLE := ["Bone_026", Vector3(0.0, 0.509, 1.413)] ## muzzle_purge, the chain's root
const LINK_GAP := 0.22 ## metres between link centres (links 0.31 m long, so they interlock)
const CHAIN_OUT := 0.09 ## seconds to reach (Ares' chain was there within one 15 fps cell)
const PULSE_TIME := 0.38 ## seconds for a heat pulse to run muzzle to target (measured 5 to 6 cells)
const CHAIN_SAG := 0.3 ## metres the coupled chain hangs at its middle
const CHAIN_LEN := 9.0 ## metres of chain before it tows (game feel lane, 2026-11-14); the kit's chain_length if it has one
const TAUT_IN := 1.5 ## metres short of its length where the chain starts to straighten
const CHAIN_LINKS := 96
const REST_HEAT := 0.32
const COLLAR_R := 0.55 ## metres, placeholder for the target's waist
const COLLAR_Y := 0.75 ## metres above the target's feet
const COLLAR_LINKS := 14
const HAUL_SLAG := [0.15, 0.75] ## seconds into the haul loop: the clip's slag events
const TRACK_SIZE := 1.2 ## metres, a haul slag patch (Eruption's are 1.9)
const GLOB_FLIGHT := 0.3 ## seconds a glob takes to reach a slag spot the kit chose (the patch burns from the cue)
const STACK_SLOT := {"fl": "1", "fr": "2", "rl": "3", "rr": "4"} ## placeholder until the kit's stack_slot (game feel lane)
const CAP_LIFT := 0.05 ## metres from a stack socket (the box centre of a 9 cm stack) up to its mouth
const CAP_SIZE := 0.26 ## metres, the ready glow over each stack mouth (a billboard)
const CAP_GLOW := 0.75 ## the steady glow while ready; the ready pulse adds up to 1.1 on top
const FEET := {"fl": "Bone_037", "fr": "Bone_031", "rl": "Bone_015", "rr": "Bone_010"} ## hoof bones (measured 2026-11-14)
const STEP_FEET := { ## the hooves landing on each "step" event, in the clip's order (measured on r5, 2026-11-14)
	"Walk": [["rl"], ["fl"], ["rr"], ["fr"]],
	"Trot": [["fl", "rr"], ["fr", "rl"]],
	"Walk_Back": [["fl", "rr"], ["fr", "rl"]],
	"Strafe_Left": [["fl", "rr"], ["fr", "rl"]],
	"Strafe_Right": [["fl", "rr"], ["fr", "rl"]],
}
const PLOW := preload("res://shaders/bison_plow.gdshader")
const SCORCH := preload("res://shaders/bison_scorch.gdshader")
const PLOW_R := 2.4 ## metres from the bison's origin to the wave, placeholder for the kit's plow_radius
const PLOW_GAIN := 1.6 ## the wave's angle is the head's angle times this (head 32 right to 40 left: arc 51 right to 64 left)
const PLOW_SPEED := 120.0 ## degrees a second; the head sweeping left faster than this grows the wave
const WALL_H := 1.3 ## metres, the wave column; the ragged tongues reach about 0.6 to 0.9 of it
const WALL_LIFE := 0.45 ## seconds a column of the wave lives after the head passes
const SCORCH_LIFE := 2.4
const SCORCH_IN := 0.9 ## metres inside the wave's radius the scorch band starts
const SCORCH_OUT := 0.6 ## and outside it ends
const PALETTES := {
	"white": {"hot": Color(1.0, 0.97, 0.92), "warm": Color(0.95, 0.88, 0.74)},
	"magma": {"hot": Color(1.0, 0.93, 0.70), "warm": Color(1.0, 0.36, 0.06)},
}

@export var palette := "magma" ## Preston picked magma orange, 2026-11-13; "white" stays for comparison
var kit: Node
var machine: Node3D
var body: Node3D
var live: Array = []
var bombs: Array = []
var log_rows: Array = []
var _rock_mat: ShaderMaterial
var _trail_mat: ShaderMaterial
var _slag_mat: ShaderMaterial
var _sphere: SphereMesh
var _chunk_mesh: SphereMesh
var _sk: Skeleton3D
var _sockets := {} ## name -> [bone index, offset in that bone's space]
var _glows := {} ## stack -> live entry of its mouth glow
var _clock := 0.0
var chains: Array = []
var _link_mesh: TorusMesh
var _chain_mat: ShaderMaterial
var _plow: Dictionary = {}
var _box := AABB() ## the model's bounds in model space, from bind time
var _haul_on := false
var _haul_pos := 0.0
var _haul_fire_t := 0.0
var _haul_smoke_t := 0.0
var _glob_side := 1.0
var _kit_slag := false ## the kit places the haul's slag itself ("slag" cue with slag_spots): globs go there, not on the beats
var _clip_full := {} ## clip -> animation name, from the roster row
var _gait := ""
var _gait_pos := 0.0
var _gait_steps: Array = []
var _body_steps := false
var _caps := {} ## stack -> {"node", "mat", "ready", "flash", "amount"}
var _cap_palette := ""
var footfalls := {} ## gait -> footfalls dusted (a count, so the log stays short)
var _wall_mat: ShaderMaterial
var _scorch_mat: ShaderMaterial


func setup(k: Node, m: Node3D) -> void:
	kit = k
	machine = m
	body = m.get("body")
	_kit_slag = k != null and "slag_spots" in k  # a kit that places the haul's slag itself: no beat globs, not even the first
	top_level = true
	global_transform = Transform3D.IDENTITY
	_rock_mat = ShaderMaterial.new()
	_rock_mat.shader = BOMB
	_trail_mat = ShaderMaterial.new()
	_trail_mat.shader = TRAIL
	_slag_mat = ShaderMaterial.new()
	_slag_mat.shader = SLAG
	_slag_mat.render_priority = 3
	_sphere = SphereMesh.new()
	_sphere.radius = 1.0
	_sphere.height = 2.0
	_sphere.radial_segments = 12
	_sphere.rings = 7
	_chunk_mesh = SphereMesh.new()
	_chunk_mesh.radius = 1.0
	_chunk_mesh.height = 2.0
	_chunk_mesh.radial_segments = 5
	_chunk_mesh.rings = 3
	_chain_mat = ShaderMaterial.new()
	_chain_mat.shader = CHAIN
	_wall_mat = ShaderMaterial.new()
	_wall_mat.shader = PLOW
	_scorch_mat = ShaderMaterial.new()
	_scorch_mat.shader = SCORCH
	_scorch_mat.render_priority = 3
	_link_mesh = TorusMesh.new()
	_link_mesh.inner_radius = 0.06
	_link_mesh.outer_radius = 0.115
	_link_mesh.rings = 10
	_link_mesh.ring_segments = 6
	set_palette(palette)
	if kit != null and kit.has_signal("cue"):
		kit.connect("cue", _on_cue)
	if body != null and body.has_signal("event"):
		body.connect("event", _on_event)
		if body.has_signal("step"):
			body.connect("step", _on_body_step)
		_bind_sockets()
	else:
		push_warning("BisonFX: no 3D body with clip events on %s" % m.name)


func set_palette(p: String) -> void:
	if not PALETTES.has(p):
		return
	palette = p
	for mat in [_rock_mat, _trail_mat, _slag_mat, _chain_mat, _wall_mat, _scorch_mat]:
		if mat != null:
			_tint(mat)
	for e in live:
		if e.has("mat"):
			_tint(e["mat"])


func _tint(mat: ShaderMaterial) -> void:
	var c: Dictionary = PALETTES[palette]
	mat.set_shader_parameter("hot_col", c["hot"])
	mat.set_shader_parameter("warm_col", c["warm"])


func _bind_sockets() -> void:
	_sk = body.get("skeleton")
	if _sk == null:
		return
	var model: Node3D = body.call("model_root")
	var rel: Transform3D = model.global_transform.affine_inverse() * _sk.global_transform
	var all := {}
	for s in STACKS:
		all["stack_" + s] = [STACKS[s][0], STACKS[s][1]]
	for v in VENTS:
		all[v] = VENTS[v]
	all["muzzle_purge"] = MUZZLE
	all["coupler"] = _coupler(model, rel)
	for n in all:
		var i := _sk.find_bone(String(all[n][0]))
		if i < 0:
			push_warning("BisonFX: no bone %s for %s" % [all[n][0], n])
			continue
		var rest: Transform3D = rel * _sk.get_bone_global_rest(i)
		_sockets[n] = [i, rest.affine_inverse() * (all[n][1] as Vector3)]
	for q in FEET:
		var fi := _sk.find_bone(String(FEET[q]))
		if fi >= 0:
			_sockets["foot_" + q] = [fi, Vector3.ZERO]  # the hoof bone's own origin
	var row: Dictionary = load("res://scripts/moba3d/arena_roster.gd").profile(String(body.get("kind"))).get("body", {})
	_clip_full = row.get("clips", {})
	_make_caps()


## World position of a socket on the moving body (the stacks ride the scapula bones).
func _socket(n: String) -> Vector3:
	if _sk == null or not _sockets.has(n):
		return machine.global_position + Vector3.UP * 1.7
	var s: Array = _sockets[n]
	return _sk.global_transform * (_sk.get_bone_global_pose(int(s[0])) * (s[1] as Vector3))


func _on_cue(n: String) -> void:
	log_rows.append("cue %s at %.2f" % [n, _clock])
	match n:
		"chain_fire":
			var t: Node3D = _kit_target()
			var e := _chain_of(t, "coupled") if t != null else {}
			if not e.is_empty():
				_pulse(e)
			else:
				_chain_out(t)
		"chain_couple":
			var e := _chain_of(_kit_target(), "out")
			if not e.is_empty():
				_couple(e)
		"chain_miss":
			for e in chains:
				if e["state"] == "out" and e["target"] == null:
					_end_chain(e, "retract")
		"plow_hit":
			_plow_hit()
		"freight_chains":
			_freight_chains()
		"freight_snap":
			_freight_snap()
		"slag":  # bison_kit.gd: a haul slag patch that burns, at slag_spots; the glob pours onto it
			var spots: Variant = kit.get("slag_spots") if is_instance_valid(kit) else null
			if spots is Array:
				_kit_slag = true
				for at in spots:
					if at is Vector3:
						_glob(at)
		"chain_break":
			var t: Node3D = _kit_target()
			for e in chains:
				if e["state"] == "coupled" and (t == null or e["target"] == t):
					_end_chain(e, "break")


func _on_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "Chain_Throw" and n == "windup":
		_sock_glow("muzzle_purge", 0.3, 0.3)
	if clip == "Freight_Brace":
		_freight_event(n)
		return
	if clip == "Hit_Heavy":
		if n == "replant":  # both front hooves come down: Freight's stamp dust
			_stamp(1.0)
			_stamp(-1.0)
			log_rows.append("replant at %.2f" % _clock)
		return
	if clip == "Plow":
		match n:
			"windup":
				_plow_start()
			"flare":
				_plow_flare()
			"throw":
				_plow_throw()
		return
	if clip != "Eruption":
		return
	log_rows.append("event %s at %.2f" % [n, _clock])
	if n == "gather":
		for s in ORDER:
			_mouth_glow(s)
	elif n == "roar":
		_roar()
	elif n.begins_with("erupt_"):
		_fire(n.substr(6))


func _floor_y() -> float:
	return machine.global_position.y


func _landing(s: String) -> Vector3:
	var pts: Variant = kit.get("eruption_points") if kit != null else null
	if pts is Array and (pts as Array).size() == 4:
		return (pts as Array)[ORDER.find(s)]
	var rad: Variant = kit.get("eruption_radius") if kit != null else null
	var r: float = float(rad) if rad != null else RING_R
	var c: Vector2 = STACKS[s][2]
	var d := Vector3(c.x, 0.0, c.y).normalized()
	if body != null:
		var model: Node3D = body.call("model_root")
		d = model.global_transform.basis * d
	d.y = 0.0
	d = d.normalized()
	var at: Vector3 = machine.global_position + d * r
	at.y = _floor_y()
	return at


func _slag_time() -> float:
	var t: Variant = kit.get("slag_time") if kit != null else null
	return float(t) if t != null else SLAG_TIME


# --- spawns ---

func _quad(size: Vector2) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = size
	q.mesh = quad
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return q


func _flat(size: float) -> MeshInstance3D:
	var q := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2.ONE * size
	q.mesh = plane
	q.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return q


func _mouth_glow(s: String) -> void:
	var q := _quad(Vector2.ONE * 0.34)
	var m := ShaderMaterial.new()
	m.shader = GLOW
	m.set_shader_parameter("billboard", true)
	m.set_shader_parameter("amount", 0.0)
	_tint(m)
	q.material_override = m
	add_child(q)
	q.global_position = _socket("stack_" + s) + Vector3.UP * 0.07
	var e := {"kind": "mouth", "node": q, "mat": m, "age": 0.0, "life": 9.0, "stack": s, "out": -1.0}
	live.append(e)
	_glows[s] = e


func _roar() -> void:
	for v in VENTS:
		for i in 3:
			_puff(_socket(v) + Vector3.UP * 0.12, 0.42 + 0.08 * i, 0.55, STEAM, 0.55, Vector3.UP * (1.6 - 0.3 * i), 0.07 * i)


func _fire(s: String) -> void:
	if not STACKS.has(s):
		return
	var from := _socket("stack_" + s)
	var land := _landing(s)
	if _glows.has(s):
		_glows[s]["out"] = 0.0
		_glows.erase(s)
	_burst(from + Vector3.UP * 0.22, Vector3(0.5, 0.9, 0.5), 0.16, 7.0)
	_puff(from + Vector3.UP * 0.35, 0.75, 0.7, SOOT, 0.7, Vector3.UP * 1.1, 0.0)
	var b := MeshInstance3D.new()
	b.mesh = _sphere
	b.material_override = _rock_mat
	b.scale = Vector3.ONE * BOMB_R
	b.set_instance_shader_parameter("heat", 1.0)
	b.set_instance_shader_parameter("seed", randf() * 40.0)
	add_child(b)
	b.global_position = from
	var tm := MeshInstance3D.new()
	tm.mesh = ImmediateMesh.new()
	tm.material_override = _trail_mat
	tm.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(tm)
	var spin := Vector3(randf_range(-1, 1), randf_range(-1, 1), randf_range(-1, 1)).normalized()
	bombs.append({"node": b, "trail": tm, "pts": [], "from": from, "land": land, "t": 0.0, "spot": null, "spin": spin,
		"stack": s, "landed": false})
	log_rows.append("bomb %s from %s to %s" % [s, from.snapped(Vector3.ONE * 0.01), land.snapped(Vector3.ONE * 0.01)])


func _burst(at: Vector3, size: Vector3, life: float, spikes: float) -> void:
	var q := _quad(Vector2.ONE)
	var m := ShaderMaterial.new()
	m.shader = BURST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 50.0)
	m.set_shader_parameter("spikes", spikes)
	_tint(m)
	q.material_override = m
	add_child(q)
	q.global_position = at
	q.scale = size
	live.append({"kind": "burst", "node": q, "mat": m, "age": 0.0, "life": life})


func _puff(at: Vector3, size: float, life: float, col: Color, strength: float, vel: Vector3, delay: float) -> void:
	var q := _quad(Vector2.ONE)
	var m := ShaderMaterial.new()
	m.shader = DUST
	m.set_shader_parameter("life", life)
	m.set_shader_parameter("seed", randf() * 50.0)
	m.set_shader_parameter("dust", Vector3(col.r, col.g, col.b))
	m.set_shader_parameter("strength", strength)
	m.set_shader_parameter("age", 0.0)
	q.material_override = m
	q.visible = delay <= 0.0
	add_child(q)
	q.global_position = at
	q.scale = Vector3.ONE * size
	live.append({"kind": "puff", "node": q, "dust": m, "age": -delay, "life": life, "vel": vel})


func _floor_glow(at: Vector3, size: float) -> Dictionary:
	var q := _flat(size)
	var m := ShaderMaterial.new()
	m.shader = GLOW
	m.render_priority = 3
	m.set_shader_parameter("billboard", false)
	m.set_shader_parameter("amount", 0.0)
	_tint(m)
	q.material_override = m
	add_child(q)
	q.global_position = at + Vector3.UP * 0.03
	return {"node": q, "mat": m}


func _impact(at: Vector3) -> void:
	_burst(at + Vector3.UP * 0.32, Vector3.ONE * 1.5, 0.27, 9.0)
	var g := _floor_glow(at, 2.4)
	g["kind"] = "flash"
	g["age"] = 0.0
	g["life"] = 0.45
	live.append(g)
	for i in 7:
		_chunk(at + Vector3.UP * 0.15)
	_puff(at + Vector3(0.25, 0.4, 0.1), 1.5, 0.85, BASALT_DUST, 0.6, Vector3.UP * 0.4, 0.0)
	_puff(at + Vector3(-0.3, 0.35, -0.15), 1.2, 0.75, BASALT_DUST, 0.5, Vector3.UP * 0.3, 0.03)
	_slag(at)


func _chunk(at: Vector3, vel_in := Vector3.ZERO) -> void:
	var c := MeshInstance3D.new()
	c.mesh = _chunk_mesh
	c.material_override = _rock_mat
	var r := randf_range(0.05, 0.1)
	c.scale = Vector3(r, r * randf_range(0.7, 1.2), r * randf_range(0.8, 1.2))
	c.set_instance_shader_parameter("heat", 1.0)
	c.set_instance_shader_parameter("seed", randf() * 40.0)
	add_child(c)
	c.global_position = at
	var a := randf() * TAU
	var vel := Vector3(cos(a), 0.0, sin(a)) * randf_range(1.8, 4.2) + Vector3.UP * randf_range(3.5, 6.5)
	if vel_in != Vector3.ZERO:
		vel = vel_in
	live.append({"kind": "chunk", "node": c, "age": 0.0, "life": randf_range(0.9, 1.3), "vel": vel, "r": r,
		"floor": at.y - 0.15, "spin": Vector3(randf(), randf(), randf()) * 9.0, "s0": c.scale})


func _slag(at: Vector3, size := SLAG_SIZE, lump_count := 3) -> void:
	var life := _slag_time()
	var q := _flat(size)
	q.material_override = _slag_mat
	_slag_mat.set_shader_parameter("life", life)
	q.set_instance_shader_parameter("age", 0.0)
	q.set_instance_shader_parameter("seed", randf() * 40.0)
	add_child(q)
	q.global_position = at + Vector3.UP * 0.025
	q.rotation.y = randf() * TAU
	var lumps := []
	var k := size / SLAG_SIZE
	for i in lump_count:
		var l := MeshInstance3D.new()
		l.mesh = _sphere
		l.material_override = _rock_mat
		var r := randf_range(0.11, 0.18) * k
		l.scale = Vector3(r * randf_range(1.0, 1.4), r * randf_range(0.45, 0.6), r * randf_range(1.0, 1.3))
		l.rotation.y = randf() * TAU
		l.set_instance_shader_parameter("heat", 1.0)
		l.set_instance_shader_parameter("seed", randf() * 40.0)
		add_child(l)
		var a := randf() * TAU
		l.global_position = at + Vector3(cos(a), 0.0, sin(a)) * randf_range(0.0, 0.42) * k + Vector3.UP * 0.01
		lumps.append(l)
	live.append({"kind": "slag", "node": q, "age": 0.0, "life": life, "lumps": lumps})


# --- per frame ---

func _process(delta: float) -> void:
	_clock += delta
	_step_bombs(delta)
	_step_chains(delta)
	_step_plow(delta)
	_step_haul(delta)
	_step_gait()
	_step_caps(delta)
	if log_rows.size() > 400:
		log_rows = log_rows.slice(-200)
	var keep: Array = []
	for e in live:
		e["age"] = float(e["age"]) + delta
		if _step(e, delta):
			keep.append(e)
		else:
			_free(e)
	live = keep


func _free(e: Dictionary) -> void:
	var n: Node = e.get("node")
	if n != null and is_instance_valid(n):
		n.queue_free()
	for l in e.get("lumps", []):
		if is_instance_valid(l):
			l.queue_free()


## Advances one live effect. Returns false when it is done.
func _step(e: Dictionary, delta: float) -> bool:
	var age: float = e["age"]
	var life: float = e["life"]
	var n: Node3D = e["node"]
	match String(e["kind"]):
		"mouth":
			var s: String = e["stack"]
			n.global_position = _socket("stack_" + s) + Vector3.UP * 0.07
			var amt := clampf(age / 0.3, 0.0, 1.0) * 0.85
			if float(e["out"]) >= 0.0:
				e["out"] = float(e["out"]) + delta
				amt = 0.85 * (1.0 - clampf(float(e["out"]) / 0.12, 0.0, 1.0))
				if float(e["out"]) > 0.12:
					return false
			(e["mat"] as ShaderMaterial).set_shader_parameter("amount", amt)
			return age < life
		"burst":
			(e["mat"] as ShaderMaterial).set_shader_parameter("age", age)
			return age < life
		"glob":
			var gv: Vector3 = e["vel"]
			gv.y -= GRAVITY * delta
			e["vel"] = gv
			var gp := n.global_position + gv * delta
			n.global_position = gp
			n.rotation += Vector3(7.0, 5.0, 3.0) * delta
			if gp.y <= float(e["floor"]) + 0.08:
				_glob_land(Vector3(gp.x, float(e["floor"]), gp.z))
				return false
			return age < life
		"sockglow":
			n.global_position = _socket(String(e["sock"]))
			(e["mat"] as ShaderMaterial).set_shader_parameter("amount", 0.85 * sin(PI * clampf(age / life, 0.0, 1.0)))
			return age < life
		"puff":
			if age < 0.0:
				return true
			n.visible = true
			n.global_position += (e["vel"] as Vector3) * delta
			e["vel"] = (e["vel"] as Vector3) * (1.0 - 2.5 * delta)
			(e["dust"] as ShaderMaterial).set_shader_parameter("age", age)
			return age < life
		"flash":
			var k := 1.0 - clampf(age / life, 0.0, 1.0)
			(e["mat"] as ShaderMaterial).set_shader_parameter("amount", k * k)
			return age < life
		"chunk":
			var v: Vector3 = e["vel"]
			v.y -= GRAVITY * delta
			var p := n.global_position + v * delta
			var fl: float = float(e["floor"]) + float(e["r"]) * 0.6
			if p.y < fl:
				p.y = fl
				if v.y < 0.0:
					v = Vector3(v.x * 0.45, -v.y * 0.3, v.z * 0.45)
			e["vel"] = v
			n.global_position = p
			n.rotation += (e["spin"] as Vector3) * delta * clampf(v.length() / 4.0, 0.0, 1.0)
			var t := age / life
			n.set_instance_shader_parameter("heat", clampf(1.0 - t * 0.9, 0.0, 1.0))
			if t > 0.75:
				n.scale = (e["s0"] as Vector3) * clampf((1.0 - t) / 0.25, 0.0, 1.0)
			return age < life
		"slag":
			n.set_instance_shader_parameter("age", age)
			var heat := clampf(1.0 - age / (life * 0.8), 0.0, 1.0)
			var t := clampf(age / life, 0.0, 1.0)
			for l in e["lumps"]:
				var lm: MeshInstance3D = l
				lm.set_instance_shader_parameter("heat", heat * 0.9)
				if t > 0.8:
					lm.position.y -= delta * 0.12
			return age < life
	return age < life


func _step_bombs(delta: float) -> void:
	var keep: Array = []
	for b in bombs:
		var pts: Array = b["pts"]
		for p in pts:
			p["age"] = float(p["age"]) + delta
		while not pts.is_empty() and float(pts[0]["age"]) > TRAIL_LIFE:
			pts.pop_front()
		if not b["landed"]:
			b["t"] = float(b["t"]) + delta
			var s := clampf(float(b["t"]) / FLIGHT, 0.0, 1.0)
			var from: Vector3 = b["from"]
			var land: Vector3 = b["land"]
			var pos := from.lerp(land, s)
			pos.y = lerpf(from.y, land.y + BOMB_R * 0.6, s) + 4.0 * APEX * s * (1.0 - s)
			var bn: MeshInstance3D = b["node"]
			var rising := pts.is_empty() or pos.y >= (pts.back()["p"] as Vector3).y
			bn.global_position = pos
			bn.rotate((b["spin"] as Vector3), delta * 7.0)
			pts.append({"p": pos, "age": 0.0, "w": 1.0 if rising else 0.4})
			if s > 0.58:
				if b["spot"] == null:
					b["spot"] = _floor_glow(land, 1.5)
				var spot: Dictionary = b["spot"]
				(spot["mat"] as ShaderMaterial).set_shader_parameter("amount", clampf((s - 0.58) / 0.42, 0.0, 1.0) * 0.55)
			if s >= 1.0:
				b["landed"] = true
				bn.queue_free()
				if b["spot"] != null:
					(b["spot"]["node"] as Node).queue_free()
					b["spot"] = null
				_impact(land)
				log_rows.append("land %s at %.2f" % [b["stack"], _clock])
		_tube((b["trail"] as MeshInstance3D).mesh as ImmediateMesh, pts, b["node"] if not b["landed"] else null)
		if b["landed"] and pts.is_empty():
			(b["trail"] as Node).queue_free()
		else:
			keep.append(b)
	bombs = keep


## Rebuilds a trail tube through the points (oldest first). Thick and hot where it was climbing, thin where falling.
func _tube(im: ImmediateMesh, pts: Array, _head: Variant) -> void:
	im.clear_surfaces()
	if pts.size() < 2:
		return
	const SIDES := 8
	var rings: Array = []
	for i in pts.size():
		var p: Vector3 = pts[i]["p"]
		var a: Vector3 = pts[maxi(i - 1, 0)]["p"]
		var c: Vector3 = pts[mini(i + 1, pts.size() - 1)]["p"]
		var tg := (c - a)
		if tg.length() < 0.0001:
			tg = Vector3.UP
		tg = tg.normalized()
		var side := tg.cross(Vector3.UP)
		if side.length() < 0.01:
			side = tg.cross(Vector3.RIGHT)
		side = side.normalized()
		var up := side.cross(tg).normalized()
		var k := 1.0 - clampf(float(pts[i]["age"]) / TRAIL_LIFE, 0.0, 1.0)
		var r := TRAIL_R * float(pts[i]["w"]) * (0.35 + 0.65 * k)
		if i == pts.size() - 1:
			r *= 0.85
		rings.append({"p": p, "s": side, "u": up, "r": r, "heat": k, "a": k * k})
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in rings.size() - 1:
		var r0: Dictionary = rings[i]
		var r1: Dictionary = rings[i + 1]
		for j in SIDES:
			var a0 := TAU * float(j) / SIDES
			var a1 := TAU * float(j + 1) / SIDES
			var quad := [[r0, a0], [r1, a0], [r1, a1], [r0, a0], [r1, a1], [r0, a1]]
			for v in quad:
				var rr: Dictionary = v[0]
				var ang: float = v[1]
				var nrm: Vector3 = (rr["s"] as Vector3) * cos(ang) + (rr["u"] as Vector3) * sin(ang)
				im.surface_set_normal(nrm)
				im.surface_set_color(Color(float(rr["heat"]), 0.0, 0.0, float(rr["a"])))
				im.surface_set_uv(Vector2(float(i) / float(rings.size()), ang / TAU))
				im.surface_add_vertex((rr["p"] as Vector3) + nrm * float(rr["r"]))
	im.surface_end()


# --- Coupling Chain ---

func _kit_target() -> Node3D:
	var t: Variant = kit.get("chain_target") if kit != null else null
	if t == null or not is_instance_valid(t):
		return null
	return t as Node3D


func _chain_of(t: Node3D, state: String) -> Dictionary:
	for e in chains:
		if e["state"] == state and e["target"] == t:
			return e
	return {}


func _sock_glow(sock: String, size: float, life: float) -> void:
	var q := _quad(Vector2.ONE * size)
	var m := ShaderMaterial.new()
	m.shader = GLOW
	m.set_shader_parameter("billboard", true)
	_tint(m)
	q.material_override = m
	add_child(q)
	q.global_position = _socket(sock)
	live.append({"kind": "sockglow", "node": q, "mat": m, "age": 0.0, "life": life, "sock": sock})


func _links(count: int) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_custom_data = true
	mm.mesh = _link_mesh
	mm.instance_count = count
	mm.visible_instance_count = 0
	var mi := MultiMeshInstance3D.new()
	mi.multimesh = mm
	mi.material_override = _chain_mat
	add_child(mi)
	return mi


func _chain_out(t: Node3D, root := "muzzle_purge", auto := false) -> Dictionary:
	var a := _socket(root)
	var end: Variant = kit.get("chain_end") if kit != null else null
	var e := {"mm": _links(CHAIN_LINKS), "target": t, "end": end if end is Vector3 else a + Vector3.FORWARD * 9.0,
		"state": "out", "t": 0.0, "st": 0.0, "tip": a, "from_tip": a, "pulses": [], "collar": null, "cheat": 0.0,
		"shrink": 1.0, "root": root, "auto": auto}
	chains.append(e)
	_burst(a + Vector3.UP * 0.05, Vector3.ONE * 0.5, 0.14, 7.0)
	log_rows.append("chain out at %.2f" % _clock)
	return e


func _target_point(e: Dictionary, a: Vector3) -> Vector3:
	var t: Node3D = e["target"]
	if t == null or not is_instance_valid(t):
		return e["end"]
	var c := t.global_position + Vector3.UP * COLLAR_Y
	var d := a - c
	d.y = 0.0
	return c + (d.normalized() if d.length() > 0.01 else Vector3.BACK) * _collar_r(e)


func _collar_r(e: Dictionary) -> float:
	var k := clampf(float(e["st"]) / 0.1, 0.0, 1.0) if e["state"] == "coupled" else 1.0
	return COLLAR_R * lerpf(1.6, 1.0, k * (2.0 - k))


func _couple(e: Dictionary) -> void:
	e["state"] = "coupled"
	e["st"] = 0.0
	e["collar"] = _links(COLLAR_LINKS)
	e["cheat"] = 0.75
	_burst(_target_point(e, _root(e)), Vector3.ONE * 0.9, 0.2, 8.0)
	_pulse(e)
	log_rows.append("chain couple at %.2f" % _clock)


func _pulse(e: Dictionary) -> void:
	var q := _quad(Vector2.ONE * 0.5)
	var m := ShaderMaterial.new()
	m.shader = GLOW
	m.set_shader_parameter("billboard", true)
	_tint(m)
	q.material_override = m
	add_child(q)
	(e["pulses"] as Array).append({"age": 0.0, "node": q, "mat": m, "hit": false})
	log_rows.append("chain pulse at %.2f" % _clock)


func _end_chain(e: Dictionary, how: String) -> void:
	e["state"] = how
	e["st"] = 0.0
	e["from_tip"] = e["tip"]
	log_rows.append("chain %s at %.2f" % [how, _clock])


func _step_chains(delta: float) -> void:
	var keep: Array = []
	for e in chains:
		e["t"] = float(e["t"]) + delta
		e["st"] = float(e["st"]) + delta
		var st: float = e["st"]
		var a := _root(e)
		var sag := 0.0
		var base_heat := REST_HEAT
		var done := false
		match String(e["state"]):
			"out":
				var k := clampf(float(e["t"]) / CHAIN_OUT, 0.0, 1.0)
				e["tip"] = a.lerp(_target_point(e, a), k * (2.0 - k))
				base_heat = 0.6
				if e.get("auto", false) and k >= 1.0 and e["target"] != null:
					_couple(e)
				if float(e["t"]) > CHAIN_OUT + 0.5:  # no couple or miss cue came: pull it back
					_end_chain(e, "retract")
			"coupled":
				e["tip"] = _target_point(e, a)
				# taut near its length (the kit tows past it): the sag goes, and the strain shows as heat
				var len_v: Variant = kit.get("chain_length") if is_instance_valid(kit) else null
				var slack := clampf((float(len_v if len_v != null else CHAIN_LEN) - a.distance_to(e["tip"])) / TAUT_IN, 0.0, 1.0)
				sag = (CHAIN_SAG + 0.2 * sin(st * 20.0) * exp(-st * 7.0)) * slack
				base_heat = maxf(lerpf(0.6, REST_HEAT, clampf(st / 0.5, 0.0, 1.0)), lerpf(0.55, REST_HEAT, slack))
			"retract":
				var k := clampf(st / 0.18, 0.0, 1.0)
				e["tip"] = (e["from_tip"] as Vector3).lerp(a, k * k)
				done = k >= 1.0
			"break":
				var k := clampf(st / 0.3, 0.0, 1.0)
				e["tip"] = _target_point(e, a)
				sag = CHAIN_SAG + 1.4 * k * k
				e["shrink"] = 1.0 - k
				base_heat = REST_HEAT * (1.0 - k)
				done = k >= 1.0
		var tip: Vector3 = e["tip"]
		var heats := _pulse_heats(e, delta, sag)
		_lay_chain(e["mm"], a, tip, sag, base_heat, heats, float(e["shrink"]))
		if e["collar"] != null:
			e["cheat"] = maxf(float(e["cheat"]) - delta * 1.2, REST_HEAT + 0.08)
			_lay_collar(e)
		if done:
			(e["mm"] as Node).queue_free()
			if e["collar"] != null:
				(e["collar"] as Node).queue_free()
			for pz in e["pulses"]:
				(pz["node"] as Node).queue_free()
		else:
			keep.append(e)
	chains = keep


## Advances the pulses on a chain; returns their positions along it (0 muzzle, 1 target). Moves each pulse's glow.
func _pulse_heats(e: Dictionary, delta: float, sag: float) -> Array:
	var out: Array = []
	var keep: Array = []
	var a := _root(e)
	var tip: Vector3 = e["tip"]
	for pz in e["pulses"]:
		pz["age"] = float(pz["age"]) + delta
		var s := float(pz["age"]) / PULSE_TIME
		if s >= 1.0 and not pz["hit"]:
			pz["hit"] = true
			e["cheat"] = 1.0
		if s > 1.15 or e["state"] == "retract" or e["state"] == "break":
			(pz["node"] as Node).queue_free()
			continue
		var c := clampf(s, 0.0, 1.0)
		var p := a.lerp(tip, c) + Vector3.DOWN * sag * 4.0 * c * (1.0 - c)
		(pz["node"] as Node3D).global_position = p
		(pz["mat"] as ShaderMaterial).set_shader_parameter("amount", 0.8 * (1.0 - clampf((s - 1.0) / 0.15, 0.0, 1.0)))
		out.append(s)
		keep.append(pz)
	e["pulses"] = keep
	return out


func _link_basis(tg: Vector3, i: int, scale: float) -> Basis:
	var side := tg.cross(Vector3.UP)
	if side.length() < 0.01:
		side = tg.cross(Vector3.RIGHT)
	side = side.normalized()
	var up := side.cross(tg).normalized()
	var b := Basis(up, side, tg) if i % 2 == 0 else Basis(side, -up, tg)
	return Basis(b.x * scale, b.y * scale, b.z * scale * 1.35)


func _lay_chain(mi: MultiMeshInstance3D, a: Vector3, tip: Vector3, sag: float, base_heat: float, pulses: Array,
		shrink: float) -> void:
	var mm := mi.multimesh
	var n := mini(int((tip - a).length() / LINK_GAP), CHAIN_LINKS)
	mm.visible_instance_count = n
	for i in n:
		var s := (float(i) + 0.5) / float(n)
		var p := a.lerp(tip, s) + Vector3.DOWN * sag * 4.0 * s * (1.0 - s)
		var tg := ((tip - a) + Vector3.DOWN * sag * 4.0 * (1.0 - 2.0 * s)).normalized()
		var h := base_heat
		for ps in pulses:
			var d := (s - float(ps)) / 0.09
			h += 0.9 * exp(-d * d)
		mm.set_instance_transform(i, Transform3D(_link_basis(tg, i, shrink), p))
		mm.set_instance_custom_data(i, Color(clampf(h, 0.0, 1.0), 1.0, 0.0, 0.0))


func _lay_collar(e: Dictionary) -> void:
	var t: Node3D = e["target"]
	var mi: MultiMeshInstance3D = e["collar"]
	if t == null or not is_instance_valid(t):
		mi.multimesh.visible_instance_count = 0
		return
	var c := t.global_position + Vector3.UP * COLLAR_Y
	var r := _collar_r(e)
	var shrink: float = e["shrink"]
	var drop := 0.0
	if e["state"] == "break":
		drop = 0.6 * (1.0 - shrink)
	var mm := mi.multimesh
	mm.visible_instance_count = COLLAR_LINKS
	for i in COLLAR_LINKS:
		var ang := TAU * float(i) / float(COLLAR_LINKS)
		var p := c + Vector3(cos(ang), 0.0, sin(ang)) * r + Vector3.DOWN * drop
		var tg := Vector3(-sin(ang), 0.0, cos(ang))
		mm.set_instance_transform(i, Transform3D(_link_basis(tg, i, shrink), p))
		mm.set_instance_custom_data(i, Color(float(e["cheat"]) * shrink, 1.0, 0.0, 0.0))


# --- Plow ---

## The bison's frame: model space, +Z forward, +X its left.
func _frame() -> Transform3D:
	var mr: Node3D = null
	if body != null and body.has_method("model_root"):
		mr = body.call("model_root")
	if mr == null:
		mr = machine
	return mr.global_transform.orthonormalized()


func _head_angle(f: Transform3D) -> float:
	var l := f.affine_inverse() * _socket("muzzle_purge")
	return rad_to_deg(atan2(l.x, l.z))


func _plow_point(f: Transform3D, ang_w: float, r: float, y: float) -> Vector3:
	var a := deg_to_rad(ang_w)
	var p := f * Vector3(sin(a) * r, 0.0, cos(a) * r)
	p.y = y
	return p


## Unit vector along the sweep (toward a bigger angle, the bison's left).
func _plow_tangent(f: Transform3D, ang_w: float) -> Vector3:
	var a := deg_to_rad(ang_w)
	return (f.basis * Vector3(cos(a), 0.0, -sin(a))).normalized()


func _plow_radius() -> float:
	var r: Variant = kit.get("plow_radius") if kit != null else null
	return float(r) if r != null else PLOW_R


func _plow_start() -> void:
	if not _plow.is_empty():
		_plow_free(_plow)
	for s in STACKS:
		_sock_glow("stack_" + s, 0.3, 0.45)
	var f := _frame()
	var wall := MeshInstance3D.new()
	wall.mesh = ImmediateMesh.new()
	wall.material_override = _wall_mat
	wall.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(wall)
	var sc := MeshInstance3D.new()
	sc.mesh = ImmediateMesh.new()
	sc.material_override = _scorch_mat
	sc.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(sc)
	_plow = {"frame": f, "y": _floor_y(), "r": _plow_radius(), "samples": [], "last": _head_angle(f), "moving": false,
		"done": false, "wall": wall, "scorch": sc, "dust_t": 0.0, "chunk_t": 0.0, "t": 0.0}
	log_rows.append("plow windup at %.2f" % _clock)


func _plow_flare() -> void:
	for s in STACKS:
		var at := _socket("stack_" + s)
		_burst(at + Vector3.UP * 0.2, Vector3(0.35, 0.75, 0.35), 0.15, 7.0)
		_puff(at + Vector3.UP * 0.3, 0.55, 0.6, SOOT, 0.6, Vector3.UP * 1.0, 0.0)
	log_rows.append("plow flare at %.2f" % _clock)


func _plow_throw() -> void:
	if _plow.is_empty():
		return
	_plow["done"] = true
	var smp: Array = _plow["samples"]
	if smp.is_empty():
		log_rows.append("plow throw at %.2f, no sweep seen" % _clock)
		return
	var f: Transform3D = _plow["frame"]
	var last := float(smp[-1]["a"])
	var at := _plow_point(f, last, float(_plow["r"]), float(_plow["y"]))
	var tg := _plow_tangent(f, last)
	_puff(at + Vector3.UP * 0.35, 1.3, 0.8, BASALT_DUST, 0.6, tg * 3.0 + Vector3.UP * 0.5, 0.0)
	_puff(at + tg * 0.4 + Vector3.UP * 0.25, 1.0, 0.7, BASALT_DUST, 0.5, tg * 4.0 + Vector3.UP * 0.3, 0.04)
	log_rows.append("plow throw at %.2f, arc %.0f to %.0f deg" % [_clock, float(smp[0]["a"]), last])


func _plow_hit() -> void:
	var ts: Variant = kit.get("plow_targets") if kit != null else null
	if not (ts is Array):
		return
	var f := _frame()
	var side := (f.basis * Vector3.RIGHT).normalized() # the sweep throws toward the bison's left
	var n := 0
	for t in ts:
		if not is_instance_valid(t):
			continue
		n += 1
		var at: Vector3 = (t as Node3D).global_position
		_burst(at + Vector3.UP * 0.6, Vector3.ONE * 0.9, 0.2, 8.0)
		for i in 4:
			_chunk(at + Vector3.UP * 0.15, side * randf_range(2.5, 4.5) + Vector3.UP * randf_range(2.5, 4.0)
				+ Vector3(randf_range(-0.8, 0.8), 0.0, randf_range(-0.8, 0.8)))
	log_rows.append("plow hit at %.2f, %d targets" % [_clock, n])


func _plow_free(p: Dictionary) -> void:
	for k in ["wall", "scorch"]:
		var nd: Node = p.get(k)
		if nd != null and is_instance_valid(nd):
			nd.queue_free()


func _step_plow(delta: float) -> void:
	if _plow.is_empty():
		return
	var p := _plow
	p["t"] = float(p["t"]) + delta
	var f: Transform3D = p["frame"]
	var r: float = p["r"]
	var y: float = p["y"]
	var smp: Array = p["samples"]
	if not p["done"]:
		var ang := _head_angle(f)
		var speed := (ang - float(p["last"])) / maxf(delta, 0.001)
		p["last"] = ang
		if speed > PLOW_SPEED:
			p["moving"] = true
			var aw := ang * PLOW_GAIN
			if not smp.is_empty():
				var prev: Dictionary = smp[-1]
				var steps := int(ceil((aw - float(prev["a"])) / 2.5))
				for k in range(1, steps):
					var u := float(k) / float(steps)
					smp.append({"a": lerpf(float(prev["a"]), aw, u), "b": lerpf(float(prev["b"]), _clock, u)})
			smp.append({"a": aw, "b": _clock})
			var at := _plow_point(f, aw, r, y)
			var tg := _plow_tangent(f, aw)
			var out := at - f.origin
			out.y = 0.0
			out = out.normalized()
			p["dust_t"] = float(p["dust_t"]) - delta
			if float(p["dust_t"]) <= 0.0:
				p["dust_t"] = 0.05
				_puff(at + Vector3.UP * 0.3, 0.9, 0.6, BASALT_DUST, 0.5, tg * 2.5 + out * 0.8 + Vector3.UP * 0.6, 0.0)
			p["chunk_t"] = float(p["chunk_t"]) - delta
			if float(p["chunk_t"]) <= 0.0:
				p["chunk_t"] = 0.035
				_chunk(at + Vector3.UP * 0.15, tg * randf_range(2.5, 4.5) + out * randf_range(0.5, 1.5)
					+ Vector3.UP * randf_range(2.5, 4.5))
		elif p["moving"] and speed < -20.0:
			p["done"] = true # the head turned back: the sweep is over
		if float(p["t"]) > 1.0:
			p["done"] = true
	var wall_rows: Array = []
	var scorch_rows: Array = []
	var u := 0.0
	var prev_pt := Vector3.ZERO
	var newest := -INF
	for i in smp.size():
		var a := _clock - float(smp[i]["b"])
		newest = maxf(newest, float(smp[i]["b"]))
		var ang_w := float(smp[i]["a"])
		var bottom := _plow_point(f, ang_w, r, y)
		if i > 0:
			u += bottom.distance_to(prev_pt)
		prev_pt = bottom
		var out := bottom - f.origin
		out.y = 0.0
		out = out.normalized()
		var hgt := WALL_H * smoothstep(0.0, 0.03, a) * (1.0 - smoothstep(0.1, WALL_LIFE, a))
		wall_rows.append([bottom, bottom + Vector3.UP * hgt + out * hgt * 0.25, u,
			Color(clampf(1.0 - a / WALL_LIFE, 0.0, 1.0), 0.0, 0.0, 1.0 - smoothstep(WALL_LIFE * 0.6, WALL_LIFE, a))])
		var lift := Vector3.UP * 0.02
		scorch_rows.append([_plow_point(f, ang_w, r - SCORCH_IN, y) + lift, _plow_point(f, ang_w, r + SCORCH_OUT, y) + lift,
			u, Color(clampf(1.0 - a / 1.0, 0.0, 1.0), 0.0, 0.0,
				smoothstep(0.0, 0.05, a) * (1.0 - smoothstep(SCORCH_LIFE * 0.65, SCORCH_LIFE, a)))])
	for row in wall_rows: # soft ends: no hard vertical edge at the head or the tail
		var c: Color = row[3]
		c.a *= smoothstep(0.0, 0.6, float(row[2])) * smoothstep(0.0, 0.35, u - float(row[2]))
		row[3] = c
	for row in scorch_rows:
		var c: Color = row[3]
		c.a *= smoothstep(0.0, 0.5, float(row[2])) * smoothstep(0.0, 0.5, u - float(row[2]))
		row[3] = c
	_strip((p["wall"] as MeshInstance3D).mesh, wall_rows, false)
	_strip((p["scorch"] as MeshInstance3D).mesh, scorch_rows, true)
	var gone: bool = p["done"] and ((smp.is_empty() and float(p["t"]) > 1.2) or (not smp.is_empty() and _clock - newest > SCORCH_LIFE))
	if gone:
		_plow_free(p)
		_plow = {}


## Rows of [edge0, edge1, u, colour]: a quad strip, UV.y 0 on edge0 and 1 on edge1.
func _strip(im: ImmediateMesh, rows: Array, on_floor: bool) -> void:
	im.clear_surfaces()
	if rows.size() < 2:
		return
	im.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in rows.size() - 1:
		var r0: Array = rows[i]
		var r1: Array = rows[i + 1]
		for k in [[r0, 0], [r0, 1], [r1, 0], [r1, 0], [r0, 1], [r1, 1]]:
			var rr: Array = k[0]
			var side: int = k[1]
			im.surface_set_color(rr[3])
			im.surface_set_uv(Vector2(float(rr[2]), float(side)))
			if on_floor:
				im.surface_set_normal(Vector3.UP)
			im.surface_add_vertex(rr[side])
	im.surface_end()


# --- Freight (ult) ---

func _root(e: Dictionary) -> Vector3:
	return _socket(String(e.get("root", "muzzle_purge")))


## A rear coupler for Freight's chains. The bison has no socket there yet (proposed to the 3D lane, 2026-11-14), so it
## is taken from the model's bounds at bind time: centred, 40% up, 8 cm inside the rear face, bound to the nearest bone.
func _coupler(model: Node3D, rel: Transform3D) -> Array:
	var inv := model.global_transform.affine_inverse()
	var first := true
	for mi in model.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		var b: AABB = (inv * m.global_transform) * m.get_aabb()
		_box = b if first else _box.merge(b)
		first = false
	var p := Vector3(0.0, _box.position.y + _box.size.y * 0.4, _box.position.z + 0.08)
	var best := 0
	var best_d := INF
	for i in _sk.get_bone_count():
		var d := (rel * _sk.get_bone_global_rest(i)).origin.distance_to(p)
		if d < best_d:
			best = i
			best_d = d
	log_rows.append("coupler at %s on %s (model box %s)" % [p.snapped(Vector3.ONE * 0.01), _sk.get_bone_name(best), _box])
	return [_sk.get_bone_name(best), p]


func _freight_event(n: String) -> void:
	match n:
		"gather":
			for s in STACKS:
				_sock_glow("stack_" + s, 0.32, 0.6)
			_sock_glow("coupler", 0.45, 0.5)
		"stamp_l":
			_stamp(1.0)
		"stamp_r":
			_stamp(-1.0)
		"braced": # the whistle: steam from both vents and a flare from every stack
			_roar()
			for s in STACKS:
				_burst(_socket("stack_" + s) + Vector3.UP * 0.2, Vector3(0.4, 0.9, 0.4), 0.16, 7.0)
	log_rows.append("freight %s at %.2f" % [n, _clock])


## A front foot stamps down: basalt dust thrown out low around it.
func _stamp(side: float) -> void:
	var f := _frame()
	var hoof := "foot_fl" if side > 0.0 else "foot_fr"
	var foot := _socket(hoof) if _sockets.has(hoof) else f * Vector3(side * _box.size.x * 0.3, 0.0, _box.position.z + _box.size.z * 0.72)
	foot.y = _floor_y()
	var out := (f.basis * Vector3(side, 0.0, 0.3)).normalized()
	_puff(foot + Vector3.UP * 0.3, 1.2, 0.7, FOOT_DUST, 0.7, out * 1.6 + Vector3.UP * 0.4, 0.0)
	_puff(foot + Vector3.UP * 0.25 - out * 0.3, 0.9, 0.6, FOOT_DUST, 0.6, -out * 0.8 + Vector3.UP * 0.3, 0.03)


func _freight_chains() -> void:
	var ts: Variant = kit.get("freight_targets") if kit != null else null
	if not (ts is Array):
		return
	var n := 0
	for t in ts:
		if is_instance_valid(t):
			_chain_out(t, "coupler", true)
			n += 1
	log_rows.append("freight chains to %d at %.2f" % [n, _clock])


func _freight_snap() -> void:
	for e in chains:
		if e["state"] != "coupled":
			continue
		var mid := _root(e).lerp(e["tip"] as Vector3, 0.5)
		_burst(mid, Vector3.ONE * 0.8, 0.18, 9.0)
		_end_chain(e, "break")
	log_rows.append("freight snap at %.2f" % _clock)


## The haul is a held loop, and the body fires a held loop's events on its first pass only, so the slag beats (0.15
## and 0.75 of each loop) are read off the clip's position here.
func _step_haul(delta: float) -> void:
	var hauling := body != null and String(body.get("action")) == "Freight_Haul"
	if not hauling:
		if _haul_on:
			_haul_on = false
			log_rows.append("haul end at %.2f" % _clock)
		return
	var ap: AnimationPlayer = body.get("anim")
	var pos := ap.current_animation_position
	if not _haul_on:
		_haul_on = true
		_haul_pos = pos
		log_rows.append("haul start at %.2f (loop %.2f s)" % [_clock, ap.current_animation_length])
	for st in ([] if _kit_slag else HAUL_SLAG):
		var beat := float(st)
		if (_haul_pos < beat and pos >= beat) or (pos < _haul_pos and (beat > _haul_pos or beat <= pos)):
			_glob()
	_haul_pos = pos
	_haul_fire_t -= delta
	if _haul_fire_t <= 0.0:
		_haul_fire_t = 0.11
		for s in STACKS:
			_burst(_socket("stack_" + s) + Vector3.UP * 0.16, Vector3(0.26, 0.55, 0.26) * randf_range(0.85, 1.15), 0.16, 6.0)
	_haul_smoke_t -= delta
	if _haul_smoke_t <= 0.0:
		_haul_smoke_t = 0.22
		var back := -(_frame().basis.z).normalized()
		for s in ["rl", "rr"]:
			_puff(_socket("stack_" + s) + Vector3.UP * 0.3, 0.6, 0.9, SOOT, 0.55, Vector3.UP * 1.2 + back * 0.8, 0.0)


## A molten glob poured off a rear stack, alternating sides; it lands behind the bison as a small slag patch.
## to: a floor point the kit chose (it burns there); the glob is thrown to land on it in GLOB_FLIGHT seconds.
func _glob(to: Variant = null) -> void:
	var f := _frame()
	_glob_side = -_glob_side
	var from := _socket("stack_" + ("rl" if _glob_side > 0.0 else "rr")) + Vector3.UP * 0.12
	var back := -(f.basis.z).normalized()
	var side := (f.basis.x).normalized() * _glob_side
	var b := MeshInstance3D.new()
	b.mesh = _sphere
	b.material_override = _rock_mat
	b.scale = Vector3.ONE * 0.11
	b.set_instance_shader_parameter("heat", 1.0)
	b.set_instance_shader_parameter("seed", randf() * 40.0)
	add_child(b)
	b.global_position = from
	_burst(from + Vector3.UP * 0.1, Vector3(0.35, 0.6, 0.35), 0.14, 7.0)
	var vel := back * 2.6 + side * 0.5 + Vector3.UP * 2.2
	if to is Vector3:
		var d: Vector3 = (to as Vector3) - from
		d.y = _floor_y() - from.y
		vel = Vector3(d.x, 0.0, d.z) / GLOB_FLIGHT + Vector3.UP * (d.y + 0.5 * GRAVITY * GLOB_FLIGHT * GLOB_FLIGHT) / GLOB_FLIGHT
	live.append({"kind": "glob", "node": b, "age": 0.0, "life": 2.0, "vel": vel, "floor": _floor_y()})


func _glob_land(at: Vector3) -> void:
	_burst(at + Vector3.UP * 0.2, Vector3.ONE * 0.7, 0.18, 8.0)
	_puff(at + Vector3.UP * 0.25, 0.8, 0.6, BASALT_DUST, 0.45, Vector3.UP * 0.3, 0.0)
	for i in 2:
		_chunk(at + Vector3.UP * 0.12, Vector3(randf_range(-1.5, 1.5), randf_range(2.0, 3.0), randf_range(-1.5, 1.5)))
	_slag(at, TRACK_SIZE, 2)
	log_rows.append("glob lands at %.2f" % _clock)


# --- Footfalls ---

## Follows the locomotion loop by clip position and dusts the hooves on each "step" time it passes (see FOOTFALLS).
func _step_gait() -> void:
	if _body_steps or body == null or _sk == null:
		return
	var ap: AnimationPlayer = body.get("anim")
	if ap == null or String(body.get("action")) != "" or not ap.is_playing():
		_gait = ""
		return
	var cur := String(ap.current_animation)
	if _gait == "" or not cur.ends_with(String(_clip_full.get(_gait, "?"))):
		_gait = ""
		_gait_steps = []
		for c in STEP_FEET:
			if _clip_full.has(c) and cur.ends_with(String(_clip_full[c])):
				_gait = c
		if _gait != "":
			for e in body.call("events_of", _gait):
				if String(e[0]) == "step":
					_gait_steps.append(float(e[1]))
		_gait_pos = ap.current_animation_position
		return  # nothing lands on the frame a loop starts
	var now := ap.current_animation_position
	var prev := _gait_pos
	_gait_pos = now
	if is_equal_approx(prev, now):
		return
	var feet: Array = STEP_FEET[_gait]
	for i in _gait_steps.size():
		var t: float = _gait_steps[i]
		if (prev < t and t <= now) if now > prev else (t > prev or t <= now):
			for q in feet[i % feet.size()]:
				_footfall(String(q), _gait)


func _on_body_step(clip: String, n: String) -> void:
	if FEET.has(n):
		_body_steps = true
		_footfall(n, clip)


## A low basalt puff under one hoof as it lands, pushed out from the body. The trot's is larger. Puffs stay where they
## rise, so a moving bison leaves them behind.
func _footfall(q: String, gait: String) -> void:
	if not _sockets.has("foot_" + q):
		return
	var f := _frame()
	var at := _socket("foot_" + q)
	at.y = _floor_y()
	var out := at - f.origin
	out.y = 0.0
	out = out.normalized() if out.length() > 0.01 else Vector3.ZERO
	var k := 1.25 if gait == "Trot" else 1.0
	var size := 0.85 * k  # the gorilla's foot puff is 0.95 at 0.65
	_puff(at + Vector3.UP * size * 0.32, size, 0.45, FOOT_DUST, 0.65 * k, out * 0.5 * k + Vector3.UP * 0.25, 0.0)
	footfalls[gait] = int(footfalls.get(gait, 0)) + 1


# --- Cooldown stacks ---

func _make_caps() -> void:
	for c in _caps.values():
		(c["node"] as Node).queue_free()
	_caps = {}
	for st in STACKS:
		if not _sockets.has("stack_" + st):
			continue
		var q := _quad(Vector2.ONE * CAP_SIZE)
		var m := ShaderMaterial.new()
		m.shader = GLOW
		m.set_shader_parameter("billboard", true)
		m.set_shader_parameter("amount", 0.0)
		_tint(m)
		q.material_override = m
		q.visible = false
		add_child(q)
		_caps[st] = {"node": q, "mat": m, "ready": false, "flash": 0.0, "amount": 0.0}
	_cap_palette = palette


## Lights each cap while its slot is off cooldown (see COOLDOWN STACKS).
func _step_caps(delta: float) -> void:
	if _caps.is_empty():
		return
	var cds: Variant = machine.get("cooldowns") if is_instance_valid(machine) else null
	var map: Variant = kit.get("stack_slot") if is_instance_valid(kit) else null
	if not (map is Dictionary):
		map = STACK_SLOT
	var shown: bool = is_instance_valid(machine) and machine.is_visible_in_tree() and machine.get("alive") != false
	var up := _frame().basis.y.normalized()
	for st in _caps:
		var c: Dictionary = _caps[st]
		if _cap_palette != palette:
			_tint(c["mat"])
		var slot := String((map as Dictionary).get(st, ""))
		var left := float((cds as Dictionary).get(slot, 0.0)) if cds is Dictionary else 0.0
		var ready: bool = shown and slot != "" and left <= 0.0
		if ready and not bool(c["ready"]):
			c["flash"] = 1.0
		c["ready"] = ready
		c["flash"] = maxf(float(c["flash"]) - delta * 4.0, 0.0)
		var want := CAP_GLOW + 1.1 * float(c["flash"]) if ready else 0.0
		c["amount"] = move_toward(float(c["amount"]), want, delta * 9.0)
		var n: MeshInstance3D = c["node"]
		n.visible = float(c["amount"]) > 0.01
		n.global_position = _socket("stack_" + st) + up * CAP_LIFT
		(c["mat"] as ShaderMaterial).set_shader_parameter("amount", c["amount"])
	_cap_palette = palette
