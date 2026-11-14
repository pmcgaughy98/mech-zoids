extends Node3D
## Isolated review scene: existing field/controller, candidate 3D visual only.
const EVIDENCE := "D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-painted-eyes-v12"
const MODEL := "D:/dev/new-mech-rpg/art/model_catalog/workspaces/gorilla_restored_pelvis_painted_eyes_v12.glb"
const CLIP := "Gorilla_CombatLoco_v12"
const MODEL_SCALE := 1.0
const WALK_SPEED := 3.5 # Existing MOBA controller baseline, independent of authored stride.
const STEP_RATE := 1.0
const BUFF_MULT := 1.25 # Illustrative item-speed test, not a balance decision.
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
var contact_log: FileAccess
var contact_previous := {}
var skeleton: Skeleton3D
var turn_contact_modifier: SkeletonModifier3D
var turn_log: FileAccess
var turn_error := 0.0
var waypoint := 0
var route := [Vector3(-4,0,-4), Vector3(4,0,-4), Vector3(4,0,4), Vector3(-4,0,4)]

func _ready() -> void:
	DisplayServer.window_set_title("Gorilla Walk V3 - In-Game Test")
	get_window().content_scale_size = Vector2i(1280,720)
	get_window().size = Vector2i(1280,720)
	record_mode = "--record" in OS.get_cmdline_user_args()
	field = load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	player = field.get_node("Player")
	player.position = Vector3(-3.5,0,3.5)
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
	camera.set_process_unhandled_input(true)
	camera.distance = 5.8
	camera.look_height = 1.05
	camera.pitch_degrees = 12
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(MODEL,state)
	if err != OK:
		push_error("Candidate GLB load failed: " + str(err))
		get_tree().quit(1)
		return
	model = doc.generate_scene(state,120.0) # Preserve the dense contact solve.
	player.add_child(model)
	model.scale = Vector3.ONE * MODEL_SCALE
	model.position.y = 0.006
	model.rotation.y = PI
	anim = _find_animation(model)
	if anim == null or not anim.has_animation(CLIP):
		push_error("Candidate walk missing: " + str(anim.get_animation_list() if anim else []))
		get_tree().quit(1)
		return
	skeleton = model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D
	contact_log = FileAccess.open(EVIDENCE + "/contacts.csv",FileAccess.WRITE)
	contact_log.store_line("time,bone,phase,support,x,y,z,drift,straight,buffed")
	turn_contact_modifier = load("res://tools/debug/gorilla_turn_contacts.gd").new()
	skeleton.add_child(turn_contact_modifier)
	turn_contact_modifier.setup(self,anim,EVIDENCE)
	turn_log = FileAccess.open(EVIDENCE + "/turn-response.csv",FileAccess.WRITE)
	turn_log.store_line("time,desired_yaw_deg,visual_yaw_deg,error_deg,speed")
	anim.speed_scale = STEP_RATE
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
	help.text = "Turn blending + planted contacts | SMITE primary / Paragon secondary | Esc closes"
	layer.add_child(help)
	telemetry = FileAccess.open(EVIDENCE + "/runtime.csv",FileAccess.WRITE)
	telemetry.store_line("time,x,y,z,clip_time,clip_playing,fps,view,speed,step_rate")
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
		var buffed := elapsed >= 12.0 and elapsed < 16.0
		player.move_speed = WALK_SPEED * (BUFF_MULT if buffed else 1.0)
		anim.speed_scale = BUFF_MULT if buffed else STEP_RATE
		player.move_override = _turn_test_direction(elapsed) if elapsed < 20 else Vector3.ZERO
		if elapsed >= 20:
			anim.pause()
		if elapsed > 27 and record_mode:
			get_tree().quit()

	camera.distance = 5.8
	camera.pitch_degrees = 12.0
	view_name = "Third-person chase / sharp-turn test"
	var travel: Vector3 = player.move_override
	var desired_yaw := atan2(travel.x,travel.z) if travel.length_squared()>.01 else model.rotation.y
	var yaw_error := wrapf(desired_yaw-model.rotation.y,-PI,PI)
	var yaw_step := clampf(yaw_error*(1.0-exp(-22.0*delta)),-deg_to_rad(900)*delta,deg_to_rad(900)*delta)
	model.rotation.y += yaw_step
	turn_error = wrapf(desired_yaw-model.rotation.y,-PI,PI)
	model.rotation.z = lerpf(model.rotation.z,clampf(-turn_error*.06,-.055,.055),1.0-exp(-16.0*delta))
	_hide_old_aim.call_deferred()
	if turn_log and started and elapsed<20:
		turn_log.store_line("%.5f,%.4f,%.4f,%.4f,%.4f" % [elapsed,rad_to_deg(desired_yaw),rad_to_deg(model.rotation.y),absf(rad_to_deg(turn_error)),player.speed])
		turn_log.flush()
	camera.snap()
	info.text = "GORILLA / RIGID LEG ARMOR / THIRD PERSON\n%s | %.2f m/s | %.2f s step cycle\n%s" % [view_name,player.move_speed,.6 / anim.speed_scale,"+25% item-speed preview" if elapsed >= 12 and elapsed < 16 else "Base movement" if started and elapsed < 20 else "Ready" if not started else "Test complete"]
	if telemetry and elapsed >= next_log:
		telemetry.store_line("%.3f,%.4f,%.4f,%.4f,%.4f,%s,%s,%s,%.3f,%.3f" % [elapsed,player.position.x,player.position.y,player.position.z,anim.current_animation_position,str(anim.is_playing()),str(Engine.get_frames_per_second()),view_name,player.speed,anim.speed_scale])
		telemetry.flush()
		next_log += 1.0




func _sample_contacts() -> void:
	if not skeleton or not contact_log:
		return
	for data in [["RightHand",0.0],["LeftHand",.03],["RightFoot",.5],["LeftFoot",.53]]:
		var bone: String = data[0]
		var phase: float = fposmod(anim.current_animation_position / .6 + float(data[1]),1.0)
		var support: bool = phase <= .38
		var index := skeleton.find_bone(bone)
		var at: Vector3 = skeleton.global_transform * skeleton.get_bone_global_pose(index).origin
		var drift := -1.0
		var straight := false
		if contact_previous.has(bone):
			var prev: Dictionary = contact_previous[bone]
			straight = (prev["facing"] as Vector3).dot(player.facing) > .99999
			if support and prev["support"] and phase >= prev["phase"]:
				drift = at.distance_to(prev["at"])
		contact_log.store_line("%.5f,%s,%.5f,%s,%.6f,%.6f,%.6f,%.6f,%s,%s" % [elapsed,bone,phase,str(support),at.x,at.y,at.z,drift,str(straight),str(elapsed >= 12 and elapsed < 16)])
		contact_previous[bone] = {"at":at,"support":support,"phase":phase,"facing":player.facing}
	contact_log.flush()



func _turn_test_direction(t: float) -> Vector3:
	if t<2:return Vector3(0,0,-1)
	if t<4:return Vector3(1,0,0)
	if t<6:return Vector3(0,0,1)
	if t<8:return Vector3(-1,0,0)
	if t<9:return Vector3(0,0,-1)
	if t<10:return Vector3(0,0,1)
	if t<11:return Vector3(1,0,0)
	if t<12:return Vector3(-1,0,0)
	if t<13.6:return Vector3(0,0,-1)
	if t<15.2:return Vector3(1,0,0)
	if t<16:return Vector3(-1,0,0)
	if t<17:return Vector3(1,0,0)
	if t<19:return Vector3(0,0,1)
	return Vector3(0,0,-1)

func _hide_old_aim() -> void:
	var ring: Node3D = player.get("_aim_ring")
	var line: Node3D = player.get("_aim_line")
	if ring:ring.visible=false
	if line:line.visible=false

