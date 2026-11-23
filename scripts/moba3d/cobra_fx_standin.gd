extends Node
## LAUNCHER ONLY (cobra effects lane, 2026-11-13). Not kit code, not a roster entry: it lives only in
## scenes/moba3d/cobra_fx_arena.tscn so the cobra's effects can be seen in the real match scene and camera before the
## cobra has a kit (the game feel lane's).
## On start it takes the player's machine, freezes its kit, puts the registered cobra body on it
## (art/arena_models/cobra.glb, the r2 export) and adds a stub kit with the cue signal and fields cobra_fx.gd reads.
## Keys: 2 = Hood Gaze, 4 = Breach, P = switch the effect palette (gold, the pick; teal, the first pass).
## Breach: the stub puts a stand-in wall ahead of the cobra (the 5v5 wall model, read only, its collision turned off
## at runtime, near face at the clip's 2.163 m), moves the cobra at the clip's 8 m/s from "go" to "stop", and on
## "burst" picks enemies within 2.4 m of the exit, cues "breach_hit" and pushes them back 2.2 m. All guesses.
## The stub resolves the cone on the clip's "gaze" event: enemy units within gaze_range and gaze_angle of the cobra's
## facing; stunned if the unit faces the cobra (within 60 degrees), slowed otherwise. The cone numbers (6 m, 60, 1 s, 2 s)
## are the ones Preston approved on 2026-11-17 (relayed by the Cobra Unreal port); the rest of the rules and numbers
## are the stub's guesses; the game feel lane owns the real ones.
const MECH_LOOK := preload("res://scripts/moba3d/mech_look.gd")
const FX := preload("res://scripts/moba3d/cobra_fx.gd")

@export var palette := "gold"
var ready_done := false
var player: Node3D
var body: MechModel3D
var stub: StubKit
var fx: Node3D
const WALL_GLB := "res://art/environment/foundry_5v5/runtime/wall.glb"
const BREACH_AHEAD := 2.163
const BREACH_SPEED := 8.0
var wall: Node3D
var wall_box: AABB
var br_move := false
var br_f := Vector3.FORWARD


## Stand-in kit: no damage, no rules beyond who the cone catches. Only what the effects read. Numbers are placeholders.
class StubKit extends Node:
	signal cue(name: String)
	var current: Variant = null ## the arena's swap() reads this
	var gaze_range := 6.0
	var gaze_angle := 60.0
	var gaze_stun_time := 1.0
	var gaze_slow_time := 2.0
	var gaze_stunned: Array = []
	var gaze_slowed: Array = []
	var breach_face: Variant = null
	var breach_normal: Variant = null
	var breach_size := Vector3(2.2, 2.6, 1.6)
	var breach_gap_time := 4.0
	var breach_hits: Array = []


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--cobra-palette="):
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
		push_error("cobra stand-in: no player in the arena")
		return
	for i in 20:
		await get_tree().process_frame
	var kit := player.get_node_or_null("Kit")
	if kit != null:
		kit.process_mode = Node.PROCESS_MODE_DISABLED
	body = MechModel3D.attach(player, "cobra")
	if body == null or not body.has_clip("Hood_Gaze"):
		push_error("cobra stand-in: the registered cobra body has no Hood_Gaze clip")
		return
	player.set("body", body)
	(player.get("sprite") as Node3D).visible = false
	var sh := player.get_node_or_null("Shadow") as Node3D
	if sh != null:
		sh.visible = false
	body.snap_facing(player.get("facing"))
	MECH_LOOK.apply_model(body.model_root(), false)
	stub = StubKit.new()
	stub.name = "CobraStubKit"
	player.add_child(stub)
	fx = FX.new()
	fx.name = "CobraFX"
	fx.palette = palette
	stub.add_child(fx)
	fx.setup(stub, player)
	body.event.connect(_on_body_event)
	ready_done = true
	print("COBRA_STANDIN ready, clips: ", body.clips().size(), ", palette ", palette)


func gaze() -> void:
	if not ready_done:
		return
	body.play_action("Hood_Gaze")


func breach() -> void:
	if not ready_done or not body.has_clip("Breach"):
		return
	var f := body.model_root().global_transform.basis.z
	f.y = 0.0
	f = f.normalized()
	br_f = f
	br_move = false
	var p := player.global_position
	_place_wall(p, f)
	stub.breach_face = p + f * BREACH_AHEAD
	stub.breach_normal = -f
	stub.breach_hits = []
	body.play_action("Breach")


## The stand-in wall section: the 5v5 wall model turned so its thin side faces the cobra, near face 2.163 m ahead.
func _place_wall(p: Vector3, f: Vector3) -> void:
	if wall == null:
		if not ResourceLoader.exists(WALL_GLB):
			push_warning("cobra stand-in: no wall model at " + WALL_GLB)
			return
		wall = (load(WALL_GLB) as PackedScene).instantiate() as Node3D
		wall.name = "BreachStandInWall"
		get_parent().add_child(wall)
		for c in wall.find_children("*", "CollisionObject3D", true, false):
			(c as CollisionObject3D).collision_layer = 0
			(c as CollisionObject3D).collision_mask = 0
		wall.global_transform = Transform3D.IDENTITY
		var box := AABB()
		var first := true
		for m in wall.find_children("*", "MeshInstance3D", true, false):
			var mb: AABB = (m as MeshInstance3D).global_transform * (m as MeshInstance3D).get_aabb()
			box = mb if first else box.merge(mb)
			first = false
		wall_box = box
		print("COBRA_STANDIN wall box ", box)
	var b := wall_box
	var thin_x := b.size.x < b.size.z
	var wb := Basis(f, Vector3.UP, f.cross(Vector3.UP)) if thin_x else Basis(Vector3.UP.cross(f), Vector3.UP, f)
	var c := b.get_center()
	var near_local := Vector3(b.position.x, b.position.y, c.z) if thin_x else Vector3(c.x, b.position.y, b.position.z)
	wall.global_transform = Transform3D(wb, p + f * BREACH_AHEAD - wb * near_local)
	var thick := b.size.x if thin_x else b.size.z
	stub.breach_size = Vector3(2.2, b.size.y, thick)


func _physics_process(delta: float) -> void:
	if br_move and player != null:
		player.global_position += br_f * BREACH_SPEED * delta


## At burst: enemies near the exit get the hit (the stub's guess) and a push away from the wall.
func _breach_burst() -> void:
	var exit_p: Vector3 = (stub.breach_face as Vector3) + br_f * stub.breach_size.z
	var side := br_f.cross(Vector3.UP).normalized()
	stub.breach_hits = []
	for u in get_tree().get_nodes_in_group("match_unit"):
		var t := u as Node3D
		if t == null or t == player or not t.is_inside_tree():
			continue
		if t.get("team") == player.get("team") or t.get("alive") == false:
			continue
		var d := t.global_position - exit_p
		d.y = 0.0
		if d.length() > 2.4 or d.dot(br_f) < -0.3:
			continue
		stub.breach_hits.append(t)
	stub.cue.emit("breach_hit")
	for t in stub.breach_hits:
		var d: Vector3 = (t as Node3D).global_position - exit_p
		var push := br_f * 2.2 + side * signf(d.dot(side)) * 1.2
		var tw := create_tween()
		tw.tween_property(t, "global_position", (t as Node3D).global_position + push, 0.25) \
			.set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)


func _facing_of(n: Node3D) -> Vector3:
	var f: Variant = n.get("facing")
	var v: Vector3 = f if f is Vector3 else -n.global_transform.basis.z
	v.y = 0.0
	return v.normalized() if v.length() > 0.001 else Vector3.FORWARD


## Who the cone catches, decided on the "gaze" event (the stub's guess at the kit's rule).
func _on_body_event(clip: String, n: String, _damage: bool) -> void:
	if clip == "Breach":
		match n:
			"go":
				br_move = true
			"stop":
				br_move = false
			"burst":
				_breach_burst()
		return
	if clip != "Hood_Gaze" or n != "gaze":
		return
	var model := body.model_root()
	var f := model.global_transform.basis.z
	f.y = 0.0
	f = f.normalized()
	var half := deg_to_rad(stub.gaze_angle * 0.5)
	stub.gaze_stunned = []
	stub.gaze_slowed = []
	for u in get_tree().get_nodes_in_group("match_unit"):
		var t := u as Node3D
		if t == null or t == player or not t.is_inside_tree():
			continue
		if t.get("team") == player.get("team") or t.get("alive") == false:
			continue
		var d := t.global_position - player.global_position
		d.y = 0.0
		var dist := d.length()
		if dist < 0.3 or dist > stub.gaze_range or d.normalized().dot(f) < cos(half):
			continue
		if _facing_of(t).dot(-d.normalized()) > cos(deg_to_rad(60.0)):
			stub.gaze_stunned.append(t)
		else:
			stub.gaze_slowed.append(t)
	stub.cue.emit("gaze_hit")


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.physical_keycode == KEY_2:
		gaze()
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_4:
		breach()
		get_viewport().set_input_as_handled()
	elif k.physical_keycode == KEY_P and fx != null:
		fx.set_palette("teal" if fx.palette == "gold" else "gold")
		get_viewport().set_input_as_handled()
