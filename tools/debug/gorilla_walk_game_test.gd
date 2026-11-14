extends Node3D
## Isolated review scene: existing field/controller, candidate 3D visual only.
const EVIDENCE := "D:/dev/_scratch/gorilla/meshforge-2026-11-08/game-test"
const MODEL := "D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_knuckle_walk_v3.glb"
const CLIP := "Gorilla_KnuckleWalk_ContactRefined_v3"
const MODEL_SCALE := 1.8
const WALK_SPEED := 0.2095238095 * MODEL_SCALE
var field: Node3D
var player: Node3D
var model: Node3D
var anim: AnimationPlayer
var camera: Camera3D
var elapsed := 0.0
var started := false
var record_mode := false
var info: Label
var telemetry: FileAccess
var next_log := 0.0
var view_name := "Gameplay camera"

func _ready() -> void:
	DisplayServer.window_set_title("Gorilla Walk V3 - In-Game Test")
	get_window().content_scale_size = Vector2i(1280,720)
	get_window().size = Vector2i(1280,720)
	record_mode = "--record" in OS.get_cmdline_user_args()
	field = load("res://scenes/moba3d/field_test.tscn").instantiate()
	add_child(field)
	player = field.get_node("Player")
	player.position = Vector3(-3,0,5)
	player.move_speed = WALK_SPEED
	player.full_speed_walk_rate = 1.0
	player.input_override = Vector2.ZERO
	player.move_override = Vector3.ZERO
	player.get_node("Sprite").visible = false
	player.get_node("Kit").process_mode = Node.PROCESS_MODE_DISABLED
	for n in ["Ring","Shadow"]:
		player.get_node(n).visible = false
	camera = field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(false)
	camera.distance = 9.0
	camera.look_height = 1.45
	camera.pitch_degrees = 30
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(MODEL,state)
	if err != OK:
		push_error("Candidate GLB load failed: " + str(err))
		get_tree().quit(1)
		return
	model = doc.generate_scene(state)
	player.add_child(model)
	model.scale = Vector3.ONE * MODEL_SCALE
	model.position.y = 0.006
	model.rotation.y = PI
	anim = _find_animation(model)
	if anim == null or not anim.has_animation(CLIP):
		push_error("Candidate walk missing: " + str(anim.get_animation_list() if anim else []))
		get_tree().quit(1)
		return
	anim.get_animation(CLIP).loop_mode = Animation.LOOP_LINEAR
	anim.play(CLIP)
	anim.seek(0.0,true)
	anim.pause()
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := ColorRect.new()
	panel.position = Vector2(16,16)
	panel.size = Vector2(760,94)
	panel.color = Color(0.035,0.05,0.06,.88)
	layer.add_child(panel)
	info = Label.new()
	info.position = Vector2(30,25)
	info.add_theme_font_size_override("font_size",20)
	layer.add_child(info)
	var help := Label.new()
	help.position = Vector2(22,675)
	help.add_theme_font_size_override("font_size",17)
	help.text = "V3 slow-walk review | Existing game field + movement controller | Esc closes"
	layer.add_child(help)
	telemetry = FileAccess.open(EVIDENCE + "/runtime.csv",FileAccess.WRITE)
	telemetry.store_line("time,x,y,z,clip_time,clip_playing,fps,view")
	camera.snap()
	print("GORILLA_GAME_READY clips=",anim.get_animation_list()," speed=",WALK_SPEED)

func _find_animation(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n
	for c in n.get_children():
		var found := _find_animation(c)
		if found:
			return found
	return null

func _process(delta: float) -> void:
	if not anim:
		return
	if Input.is_physical_key_pressed(KEY_ESCAPE):
		get_tree().quit()
	if not started and (not record_mode or FileAccess.file_exists(EVIDENCE + "/record.trigger")):
		started = true
		anim.play(CLIP)
		print("GORILLA_TEST_STARTED")
	if started:
		elapsed += delta
		player.move_override = Vector3(0,0,-1) if elapsed < 20 else Vector3.ZERO
		if elapsed >= 20:
			anim.pause()
		if elapsed > 27 and record_mode:
			get_tree().quit()
		if elapsed < 4:
			camera.yaw_degrees = 0
			camera.distance = 9.0
			camera.pitch_degrees = 30
			view_name = "Gameplay chase"
		elif elapsed < 8:
			camera.yaw_degrees = 135
			camera.distance = 8.5
			camera.pitch_degrees = 30
			view_name = "Front quarter"
		elif elapsed < 13:
			camera.yaw_degrees = 90
			camera.distance = 7.0
			camera.pitch_degrees = 15
			view_name = "Side contact check"
		elif elapsed < 17:
			camera.yaw_degrees = 180
			camera.distance = 8.0
			camera.pitch_degrees = 25
			view_name = "Front contact check"
		else:
			camera.yaw_degrees = 35
			camera.distance = 9.0
			camera.pitch_degrees = 30
			view_name = "Gameplay quarter"
	model.rotation.y = atan2(player.facing.x,player.facing.z)
	camera.snap()
	info.text = "GORILLA / REFINED KNUCKLE WALK\n%s | %.2f m/s | 1.4 s cycle\n%s" % [view_name,WALK_SPEED,"Walk test running" if started and elapsed < 20 else "Ready" if not started else "Test complete"]
	if telemetry and elapsed >= next_log:
		telemetry.store_line("%.3f,%.4f,%.4f,%.4f,%.4f,%s,%s,%s" % [elapsed,player.position.x,player.position.y,player.position.z,anim.current_animation_position,str(anim.is_playing()),str(Engine.get_frames_per_second()),view_name])
		telemetry.flush()
		next_log += 1.0
