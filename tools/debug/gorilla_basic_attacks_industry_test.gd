extends Node3D
## Isolated animation/contact review; production combat is unchanged.
const MODEL = "res://art/model_catalog/workspaces/gorilla_basic_attacks_v15.glb"
const IDLE = "Gorilla_Idle_v14"
const ATTACKS = ["Gorilla_Basic_A_v15","Gorilla_Basic_B_v15","Gorilla_Basic_C_v15"]
const IMPACTS = [.345,.345,.440]
const EVIDENCE = "D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-attacks-v15"
var anim: AnimationPlayer
var camera: Camera3D
var player: Node3D
var started = false
var elapsed = 0.0
var record_mode = false
var attack_busy = false
var attack_step = 0
var active_step = 0
var attack_time = 0.0
var hit_fired = false
var buffered = false
var event_index = 0
var hit_flash = 0.0
var target_mat: StandardMaterial3D
var label: Label
var telemetry: FileAccess
var events = []
var dummy: Node3D
var recoil = 0.0
var recoil_velocity = 0.0

func _ready():
	get_window().content_scale_size = Vector2i(1280,720)
	get_window().size = Vector2i(1280,720)
	record_mode = "--record" in OS.get_cmdline_user_args()
	var field = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	player = field.get_node("Player")
	player.position = Vector3(-3.5,0,3.5)
	player.input_override = Vector2.ZERO
	player.move_override = Vector3.ZERO
	player.get_node("Sprite").visible = false
	player.get_node("Kit").process_mode = Node.PROCESS_MODE_DISABLED
	for n in ["Ring","Shadow"]: player.get_node(n).visible = false
	camera = field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(true)
	camera.distance = 5.8
	camera.look_height = 1.05
	camera.pitch_degrees = 12
	var doc = GLTFDocument.new()
	var state = GLTFState.new()
	if doc.append_from_file(MODEL,state) != OK:
		get_tree().quit(1)
		return
	var model = doc.generate_scene(state,120.0)
	player.add_child(model)
	model.position.y = .006
	model.rotation.y = PI
	anim = model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	for clip in ATTACKS + [IDLE]:
		if not anim.has_animation(clip):
			push_error("Missing combat clip " + clip)
			get_tree().quit(1)
			return
	anim.get_animation(IDLE).loop_mode = Animation.LOOP_LINEAR
	for clip in ATTACKS: anim.get_animation(clip).loop_mode = Animation.LOOP_NONE
	anim.animation_finished.connect(_finished)
	anim.play(IDLE)
	anim.seek(0,true)
	anim.pause()
	_build_target()
	var layer = CanvasLayer.new()
	add_child(layer)
	label = Label.new()
	label.position = Vector2(22,22)
	label.add_theme_font_size_override("font_size",20)
	layer.add_child(label)
	for cycle in range(4):
		var start = 1.2+cycle*4.3
		events.append([start,0])
		events.append([start+.9,1])
		events.append([start+1.8,2])
	telemetry = FileAccess.open(EVIDENCE+"/attack-events.csv",FileAccess.WRITE)
	telemetry.store_line("elapsed,event,clip,clip_time")
	camera.snap()
	_set_title.call_deferred()
	print("GORILLA_ATTACKS_READY clips=",anim.get_animation_list())

func _set_title(): DisplayServer.window_set_title("Gorilla Basic Attacks Industry Review")

func _attack(step):
	active_step = step
	attack_step = (step+1)%3
	attack_busy = true
	attack_time = 0.0
	hit_fired = false
	anim.play(ATTACKS[step],.065)
	_log("start")

func _finished(clip):
	if not clip in ATTACKS: return
	attack_busy = false
	_log("recovery_complete")
	if not record_mode and (buffered or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)):
		buffered = false
		_attack(attack_step)
	else: anim.play(IDLE,.10)

func _unhandled_input(event):
	if record_mode: return
	if (event is InputEventMouseButton and event.button_index==MOUSE_BUTTON_LEFT and event.pressed) or (event is InputEventKey and event.physical_keycode==KEY_SPACE and event.pressed and not event.echo):
		if attack_busy: buffered = true
		else: _attack(attack_step)

func _process(delta):
	if Input.is_physical_key_pressed(KEY_ESCAPE): get_tree().quit()
	if not anim: return
	if not started and (not record_mode or FileAccess.file_exists(EVIDENCE+"/record.trigger")):
		started = true
		anim.play(IDLE)
	if started:
		elapsed += delta
		if record_mode and event_index<events.size() and elapsed>=events[event_index][0]:
			_attack(events[event_index][1])
			event_index += 1
		if record_mode and elapsed>24: get_tree().quit()
	if attack_busy:
		attack_time += delta
		if not hit_fired and attack_time>.06 and anim.current_animation==ATTACKS[active_step] and anim.current_animation_position>=IMPACTS[active_step]:
			hit_fired = true
			hit_flash = .13
			recoil_velocity -= 4.2 if active_step==2 else 3.2
			_log("impact_marker")
	hit_flash = maxf(0,hit_flash-delta)
	var spring_delta = minf(delta,.0333333)
	recoil_velocity += (-130.0*recoil-20.0*recoil_velocity)*spring_delta
	recoil += recoil_velocity*spring_delta
	dummy.rotation.x = recoil
	target_mat.albedo_color = Color(1,.72,.16) if hit_flash>0 else Color(.25,.32,.32)
	target_mat.emission_enabled = hit_flash>0
	target_mat.emission = Color(.55,.18,.015)
	label.text = "GORILLA / BASIC ATTACKS\n%s | Left click / Space chains attacks" % (["A — left strike","B — right strike","C — heavy finisher"][active_step] if attack_busy else "Grounded idle")
	_hide_aim.call_deferred()
	camera.snap()

func _log(event):
	if telemetry:
		telemetry.store_line("%.4f,%s,%s,%.4f" % [elapsed,event,ATTACKS[active_step],anim.current_animation_position])
		telemetry.flush()
	print("GORILLA_ATTACK_EVENT ",event," clip=",ATTACKS[active_step]," elapsed=",elapsed)

func _build_target():
	target_mat = StandardMaterial3D.new()
	target_mat.albedo_color = Color(.25,.32,.32)
	target_mat.metallic = .65
	target_mat.roughness = .45
	var target = MeshInstance3D.new()
	var mesh = CylinderMesh.new()
	mesh.top_radius = .60
	mesh.bottom_radius = .63
	mesh.height = 2.0
	target.mesh = mesh
	target.material_override = target_mat
	dummy = Node3D.new()
	dummy.position = player.position+Vector3(0,0,-1.65)
	add_child(dummy)
	target.position = Vector3(0,1.0,0)
	dummy.add_child(target)
	var ring = MeshInstance3D.new()
	var band = CylinderMesh.new()
	band.top_radius = .635
	band.bottom_radius = .635
	band.height = .11
	ring.mesh = band
	ring.position = Vector3(0,.80,0)
	var mat = StandardMaterial3D.new()
	mat.albedo_color = Color(.8,.39,.05)
	mat.metallic = .65
	ring.material_override = mat
	target.add_child(ring)

func _hide_aim():
	var ring = player.get("_aim_ring")
	var line = player.get("_aim_line")
	if ring: ring.visible = false
	if line: line.visible = false
