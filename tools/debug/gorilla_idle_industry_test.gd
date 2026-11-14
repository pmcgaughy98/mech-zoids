extends Node3D
const MODEL = "res://art/model_catalog/workspaces/gorilla_idle_v14.glb"
const CLIP = "Gorilla_Idle_v14"
const EVIDENCE = "D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-idle-v14"
var anim: AnimationPlayer
var camera: Camera3D
var player: Node3D
var started = false
var elapsed = 0.0
var record_mode = false
var next_sample = 0.0
var skeleton: Skeleton3D
var chest_index = -1
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
	skeleton = model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	chest_index = skeleton.find_bone("Chest")
	if not anim.has_animation(CLIP):
		push_error("Missing idle: " + str(anim.get_animation_list()))
		get_tree().quit(1)
		return
	anim.get_animation(CLIP).loop_mode = Animation.LOOP_LINEAR
	anim.play(CLIP)
	anim.seek(0,true)
	anim.pause()
	var layer = CanvasLayer.new()
	add_child(layer)
	var label = Label.new()
	label.position = Vector2(22,22)
	label.add_theme_font_size_override("font_size",20)
	label.text = "GORILLA / GROUNDED IDLE\n7.67-second loop | Rampage motion study | planted knuckles"
	layer.add_child(label)
	camera.snap()
	_set_title.call_deferred()
	print("GORILLA_IDLE_READY clips=",anim.get_animation_list()," duration=",anim.get_animation(CLIP).length)
func _set_title():
	DisplayServer.window_set_title("Gorilla Idle Industry Review")
func _process(delta):
	if Input.is_physical_key_pressed(KEY_ESCAPE): get_tree().quit()
	if not anim: return
	if not started and (not record_mode or FileAccess.file_exists(EVIDENCE + "/record.trigger")):
		started = true
		anim.play(CLIP)
	if started:
		elapsed += delta
		if elapsed >= next_sample:
			print("IDLE_PLAYBACK elapsed=",elapsed," clip_time=",anim.current_animation_position," playing=",anim.is_playing()," chest=",skeleton.get_bone_global_pose(chest_index).origin)
			next_sample += 1.0
		if record_mode and elapsed>21: get_tree().quit()
	_hide_aim.call_deferred()
	camera.snap()
func _hide_aim():
	var ring = player.get("_aim_ring")
	var line = player.get("_aim_line")
	if ring: ring.visible = false
	if line: line.visible = false
