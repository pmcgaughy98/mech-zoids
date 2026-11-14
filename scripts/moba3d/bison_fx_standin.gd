extends Node
## LAUNCHER ONLY (bison effects lane, 2026-11-13). Not kit code, not a roster entry: it lives only in
## scenes/moba3d/bison_fx_arena.tscn so the bison's effects can be seen in the real match scene and camera before the
## bison is registered (Preston's call) or has a kit (the game feel lane's).
## On start it takes the player's machine, freezes its kit, puts the bison's body on it and adds a stub kit with the cue
## signal and fields that bison_fx.gd reads. The body is the registered one (art/arena_models/bison.glb, the r4 export,
## registered 2026-11-13); if that ever fails to load, the r4 GLB is read at runtime from the 3D lane's export folder.
## Keys: 1 = Coupling Chain (at the nearest enemy unit in front within chain_range, else a miss; again while coupled is
## a refire), 2 = Eruption, 3 = Plow (enemies within plow_radius + 0.6 m and 70 degrees of facing are hit at the clip's
## "hit" and shoved 2.5 m to the bison's left at "throw", a stand-in for the kit's throw), 4 = Freight (every enemy
## within freight_radius is chained at the brace's "chains_out"; at "braced" the haul loop starts, the stand-in walks the
## machine forward at haul_speed for haul_time and tows the targets into a line behind it like rail cars, then drops the
## chains; 4 again while hauling is a snap, a stand-in for a stun landing on the hauler), H = a heavy hit (plays
## Hit_Heavy, for the front-hoof replant dust), P = switch the effect palette (white / magma). Walking shows the
## footfall dust. Each cast puts its slot on MatchRules' cooldown in player.cooldowns, as the director would, so the
## cooldown stacks go dark and relight (placeholder order: fl 1, fr 2, rl 3, rr 4). Casting again still works.
## The chain cues below are the stub's guess at the kit's rules (couple 0.09 s after "fire", break after couple_time);
## the game feel lane owns the real ones.
const GLB := "D:/dev/_scratch/bison-3d/game-export-r4/bison-kit-r4.glb"
const PROFILE := "D:/dev/_scratch/bison-3d/game-export-r4/bison-profile.json"
const MECH_LOOK := preload("res://scripts/moba3d/mech_look.gd")
const FX := preload("res://scripts/moba3d/bison_fx.gd")

@export var palette := "magma"
var ready_done := false
var player: Node3D
var body: MechModel3D
var stub: StubKit
var fx: Node3D
var _throwing := false
var _throw_target: Node3D = null
var _coupled: Array = [] ## [target, seconds left]
var _freight_targets: Array = []
var _hauling := false
var _haul_left := 0.0


## Stand-in kit: no damage, no rules. Only what the effects read. Numbers are placeholders for the kit.
class StubKit extends Node:
	signal cue(name: String)
	var current: Variant = null ## the arena's swap() reads this
	var eruption_radius := 3.5
	var slag_time := 4.5
	var chain_target: Node3D = null
	var chain_end := Vector3.ZERO
	var couple_time := 3.0
	var chain_range := 9.0
	var plow_radius := 2.4
	var plow_targets: Array = []
	var freight_targets: Array = []
	var freight_radius := 7.0
	var haul_time := 4.0
	var haul_speed := 0.518 ## m/s, the profile's haul_speed


## A MechModel3D fed from the r4 profile instead of the roster (the bison is not registered).
class StandInBody extends MechModel3D:
	var row := {}

	func _setup(k: String) -> bool:
		kind = k
		_row = row
		var tpl := MechModel3D._template(String(_row["glb"]))
		if tpl == null:
			push_warning("bison stand-in: no GLB at %s" % _row["glb"])
			return false
		_model = tpl.duplicate() as Node3D
		_model.name = "Model"
		_model.scale = Vector3.ONE * float(_row.get("scale", 1.0))
		add_child(_model)
		var players := _model.find_children("*", "AnimationPlayer", true, false)
		if players.is_empty():
			return false
		anim = players[0]
		anim.process_priority = -10
		var sk := _model.find_children("*", "Skeleton3D", true, false)
		skeleton = sk[0] if not sk.is_empty() else null
		for full in anim.get_animation_list():
			_clips[_short(full)] = full
		for short_name in _row.get("clips", {}):
			var full: String = _row["clips"][short_name]
			if anim.has_animation(full):
				_clips[short_name] = full
		_rest = float(_row.get("rest_height", 1.65))
		_walk_speed = float(_row.get("walk_speed", 1.174))
		_run_speed = float(_row.get("run_speed", 0.0))
		_events = (_row.get("events", {}) as Dictionary).duplicate(true)
		_peaks = (_row.get("peaks", {}) as Dictionary).duplicate()
		for loop in [_row.get("idle", ""), _row.get("walk", ""), _row.get("run", "")]:
			if _clips.has(loop):
				anim.get_animation(_clips[loop]).loop_mode = Animation.LOOP_LINEAR
		locomote(0.0)
		return true


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--bison-palette="):
			palette = a.substr(16)
	_install.call_deferred()


func _install() -> void:
	var arena := get_parent()
	for i in 300:
		player = arena.get("player")
		if player != null and player.get("sprite") != null:
			break
		await get_tree().process_frame
	if player == null:
		push_error("bison stand-in: no player in the arena")
		return
	for i in 20:
		await get_tree().process_frame
	var kit := player.get_node_or_null("Kit")
	if kit != null:
		kit.process_mode = Node.PROCESS_MODE_DISABLED
	body = MechModel3D.attach(player, "bison")
	var source := "registered"
	if body == null or not body.has_clip("Eruption"):
		source = "runtime r4 GLB"
		var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(PROFILE))
		if not (data is Dictionary):
			push_error("bison stand-in: cannot read %s" % PROFILE)
			return
		var row: Dictionary = data
		row["glb"] = GLB
		var old := player.get_node_or_null("Body")
		if old != null:
			player.remove_child(old)
			old.queue_free()
		body = StandInBody.new()
		body.row = row
		body.name = "Body"
		player.add_child(body)
		if not body._setup("bison"):
			push_error("bison stand-in: the r4 body did not load")
			return
	player.set("body", body)
	(player.get("sprite") as Node3D).visible = false
	var sh := player.get_node_or_null("Shadow") as Node3D
	if sh != null:
		sh.visible = false
	body.snap_facing(player.get("facing"))
	MECH_LOOK.apply_model(body.model_root(), false)
	stub = StubKit.new()
	stub.name = "BisonStubKit"
	player.add_child(stub)
	fx = FX.new()
	fx.name = "BisonFX"
	fx.palette = palette
	stub.add_child(fx)
	fx.setup(stub, player)
	body.event.connect(_on_body_event)
	ready_done = true
	print("BISON_STANDIN ready, body: ", source, ", clips: ", body.clips().size(), ", palette ", palette)


func erupt() -> void:
	if not ready_done:
		return
	stub.cue.emit("eruption")
	_cool("2")
	body.play_action("Eruption")


## Throws the chain at target (null: a miss along facing). The cues go out on the clip's "fire" event.
func chain(target: Node3D) -> void:
	if not ready_done:
		return
	_throwing = true
	_throw_target = target
	_cool("1")
	body.play_action("Chain_Throw")


func pick_target() -> Node3D:
	var f: Vector3 = player.get("facing")
	f.y = 0.0
	f = f.normalized()
	var best: Node3D = null
	var best_d := INF
	for u in get_tree().get_nodes_in_group("match_unit"):
		var n := u as Node3D
		if n == null or n == player or not n.is_inside_tree():
			continue
		if n.get("team") == player.get("team") or n.get("alive") == false:
			continue
		var d := n.global_position - player.global_position
		d.y = 0.0
		var dist := d.length()
		if dist < 0.5 or dist > stub.chain_range or d.normalized().dot(f) < cos(deg_to_rad(35.0)):
			continue
		if dist < best_d:
			best = n
			best_d = dist
	return best


func plow() -> void:
	if not ready_done:
		return
	stub.cue.emit("plow")
	_cool("3")
	body.play_action("Plow")


func _plow_targets() -> Array:
	var f: Vector3 = player.get("facing")
	f.y = 0.0
	f = f.normalized()
	var out: Array = []
	for u in get_tree().get_nodes_in_group("match_unit"):
		var n := u as Node3D
		if n == null or n == player or not n.is_inside_tree():
			continue
		if n.get("team") == player.get("team") or n.get("alive") == false:
			continue
		var d := n.global_position - player.global_position
		d.y = 0.0
		if d.length() > stub.plow_radius + 0.6 or d.normalized().dot(f) < cos(deg_to_rad(70.0)):
			continue
		out.append(n)
	return out


## Launcher stand-in for the kit's throw: 2.5 m to the bison's left over 0.32 s, with a small hop.
func _shove(t: Node3D) -> void:
	var f: Vector3 = player.get("facing")
	f.y = 0.0
	var left := Vector3.UP.cross(f.normalized()).normalized()
	var start := t.global_position
	create_tween().tween_method(_shove_step.bind(t, start, start + left * 2.5), 0.0, 1.0, 0.32)


func _shove_step(u: float, t: Node3D, start: Vector3, end: Vector3) -> void:
	if is_instance_valid(t):
		t.global_position = start.lerp(end, 1.0 - (1.0 - u) * (1.0 - u)) + Vector3.UP * 0.6 * 4.0 * u * (1.0 - u)


## Brace and haul; while hauling, a snap.
func freight() -> void:
	if not ready_done:
		return
	if _hauling:
		_end_haul("freight_snap")
		return
	_freight_targets = []
	for u in get_tree().get_nodes_in_group("match_unit"):
		var n := u as Node3D
		if n == null or n == player or not n.is_inside_tree():
			continue
		if n.get("team") == player.get("team") or n.get("alive") == false:
			continue
		if n.global_position.distance_to(player.global_position) <= stub.freight_radius:
			_freight_targets.append(n)
	stub.cue.emit("freight")
	_cool("4")
	body.play_action("Freight_Brace")


## The director's job in a match: the slot's cooldown from MatchRules, counted down by the player itself.
func _cool(slot: String) -> void:
	var cds: Variant = player.get("cooldowns")
	if cds is Dictionary:
		cds[slot] = MatchRules.cooldown("bison", slot)


func _end_haul(how: String) -> void:
	_hauling = false
	body.stop_action()
	stub.chain_target = null
	stub.cue.emit(how if how == "freight_snap" else "chain_break")


func _on_body_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "Freight_Brace":
		if n == "chains_out":
			stub.freight_targets = _freight_targets
			stub.cue.emit("freight_chains")
		elif n == "braced":
			body.play_hold("Freight_Haul")
			_hauling = true
			_haul_left = stub.haul_time
		return
	if clip == "Plow":
		if n == "hit":
			stub.plow_targets = _plow_targets()
			if not stub.plow_targets.is_empty():
				stub.cue.emit("plow_hit")
		elif n == "throw":
			for t in stub.plow_targets:
				if is_instance_valid(t):
					_shove(t)
		return
	if clip != "Chain_Throw" or n != "fire" or not _throwing:
		return
	_throwing = false
	var t: Node3D = _throw_target if is_instance_valid(_throw_target) else null
	var f: Vector3 = player.get("facing")
	stub.chain_target = t
	stub.chain_end = player.global_position + f.normalized() * stub.chain_range + Vector3.UP * 0.75
	var refire := false
	for c in _coupled:
		if c[0] == t:
			c[1] = stub.couple_time
			refire = true
	stub.cue.emit("chain_fire")
	if refire:
		return
	await get_tree().create_timer(0.09, false).timeout
	stub.chain_target = t
	if t != null and is_instance_valid(t):
		stub.cue.emit("chain_couple")
		_coupled.append([t, stub.couple_time])
	else:
		stub.cue.emit("chain_miss")


func _process(delta: float) -> void:
	if stub != null and _hauling:
		_step_haul(delta)
	if stub == null or _coupled.is_empty():
		return
	var keep: Array = []
	for c in _coupled:
		c[1] = float(c[1]) - delta
		if float(c[1]) > 0.0 and is_instance_valid(c[0]):
			keep.append(c)
			continue
		stub.chain_target = c[0] if is_instance_valid(c[0]) else null
		stub.cue.emit("chain_break")
	_coupled = keep


## Launcher stand-in for the kit's haul: the machine walks forward and the coupled targets fall in behind it, 2.6 m
## behind its feet and 1.7 m apart, like rail cars.
func _step_haul(delta: float) -> void:
	var f: Vector3 = player.get("facing")
	f.y = 0.0
	f = f.normalized()
	player.global_position += f * stub.haul_speed * delta
	var k := 1.0 - exp(-3.0 * delta)
	for i in _freight_targets.size():
		var t: Node3D = _freight_targets[i]
		if not is_instance_valid(t):
			continue
		var want := player.global_position - f * (2.6 + 1.7 * float(i))
		want.y = t.global_position.y
		t.global_position = t.global_position.lerp(want, k)
	_haul_left -= delta
	if _haul_left <= 0.0:
		_end_haul("chain_break")


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.physical_keycode == KEY_1:
		chain(pick_target())
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_4:
		freight()
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_3:
		plow()
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_2:
		erupt()
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_H and ready_done:
		body.play_action("Hit_Heavy")
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_P and fx != null:
		fx.set_palette("white" if fx.palette == "magma" else "magma")
		get_viewport().set_input_as_handled()
