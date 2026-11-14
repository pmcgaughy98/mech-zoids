extends Node3D
## Slow swing basic attack review v18 (copy of the v17 test, swing clips swapped in). Production kit unchanged.
const MODEL="res://art/model_catalog/workspaces/gorilla_slow_swing_v18.glb"
const IDLE="Gorilla_Idle_v14"
const WALK="Gorilla_Walk_v17"
const READY="Gorilla_Combat_Ready_v17"
const ENTER="Gorilla_Combat_Enter_v17"
const EXIT="Gorilla_Combat_Exit_v17"
const LEFT="Gorilla_Swing_Left_v18"
const RIGHT="Gorilla_Swing_Right_v18"
const HIT_TIME=0.32
const COOLDOWN=1.0
const EVIDENCE="D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-swing-v18"
var player: Node3D
var model: Node3D
var camera: Camera3D
var anim: AnimationPlayer
var skeleton: Skeleton3D
var started=false
var record_mode=false
var elapsed=0.0
var mode="travel"
var mode_time=0.0
var combat_weight=0.0
var actual_velocity=Vector3.ZERO
var previous_pos=Vector3.ZERO
var held=false
var previous_held=false
var pending=false
var attack_busy=false
var left_next=true
var hit_fired=false
var next_attack=0.0
var active_hand=""
var label: Label
var runtime: FileAccess
var events: FileAccess
var sample_time=0.0

func _ready():
	get_window().content_scale_size=Vector2i(1280,720)
	get_window().size=Vector2i(1280,720)
	record_mode="--record" in OS.get_cmdline_user_args()
	var field=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	player=field.get_node("Player")
	player.position=Vector3(0,0,3.5)
	player.move_speed=3.5
	player.input_override=Vector2.ZERO
	player.move_override=Vector3.ZERO
	player.get_node("Sprite").visible=false
	player.get_node("Kit").process_mode=Node.PROCESS_MODE_DISABLED
	for name in ["Ring","Shadow"]:player.get_node(name).visible=false
	camera=field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(not record_mode)
	camera.yaw_degrees=0
	camera.distance=5.8
	camera.pitch_degrees=12
	camera.look_height=1.05
	var doc=GLTFDocument.new()
	var state=GLTFState.new()
	if doc.append_from_file(MODEL,state)!=OK:
		get_tree().quit(1)
		return
	model=doc.generate_scene(state,120.0)
	player.add_child(model)
	model.position.y=.006
	model.rotation.y=PI
	anim=model.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	skeleton=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	for name in [IDLE,WALK,READY,ENTER,EXIT,LEFT,RIGHT]:
		if not anim.has_animation(name):
			push_error("Missing combat action "+name)
			get_tree().quit(1)
			return
		anim.get_animation(name).loop_mode=Animation.LOOP_LINEAR if name in [IDLE,WALK,READY] else Animation.LOOP_NONE
	anim.play(READY)
	anim.seek(0,true)
	var quad=load("res://tools/debug/gorilla_quad_contacts_v17.gd").new()
	skeleton.add_child(quad)
	quad.setup(self,anim,EVIDENCE)
	var feet=load("res://tools/debug/gorilla_combat_feet_v17.gd").new()
	skeleton.add_child(feet)
	feet.setup(self,model,EVIDENCE)
	anim.animation_finished.connect(_finished)
	anim.play(IDLE)
	anim.seek(0,true)
	anim.pause()
	previous_pos=player.global_position
	var layer=CanvasLayer.new()
	add_child(layer)
	label=Label.new()
	label.position=Vector2(20,20)
	label.add_theme_font_size_override("font_size",20)
	layer.add_child(label)
	runtime=FileAccess.open(EVIDENCE+"/runtime.csv",FileAccess.WRITE)
	runtime.store_line("time,held,mode,hand,x,z,speed,aim_error_deg,clip,clip_time,combat_weight")
	events=FileAccess.open(EVIDENCE+"/attack-events.csv",FileAccess.WRITE)
	events.store_line("time,event,hand,clip,clip_time")
	camera.snap()
	_title.call_deferred()
	print("MOVING_COMBAT_READY clips=",anim.get_animation_list())

func _title():DisplayServer.window_set_title("Gorilla Slow Swing v18")

func _process(delta):
	if Input.is_physical_key_pressed(KEY_ESCAPE):get_tree().quit()
	if not anim:return
	actual_velocity=(player.global_position-previous_pos)/maxf(delta,.0001)
	previous_pos=player.global_position
	if not started:
		player.move_override=Vector3.ZERO
		if not record_mode or FileAccess.file_exists(EVIDENCE+"/record.trigger"):
			started=true
			anim.play(IDLE)
		else:return
	elapsed+=delta
	mode_time+=delta
	var move=Vector3.ZERO
	if record_mode:
		held=(elapsed>=1.0 and elapsed<8.6) or (elapsed>=10.4 and elapsed<13.7)
		move=_route(elapsed)
		player.move_override=move
		if elapsed>20.0:get_tree().quit()
	else:
		held=Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or Input.is_physical_key_pressed(KEY_SPACE)
		player.move_override=null
		player.input_override=null
		move=player.move_dir()
	if held and not previous_held:pending=true
	previous_held=held
	var speed=actual_velocity.length()
	var wants=held or pending or (attack_busy and anim.current_animation_position<HIT_TIME+.025)
	if wants and mode in ["travel","exit","exit_move"]:_enter(speed>.08)
	if mode=="enter":
		combat_weight=minf(1,combat_weight+delta/.24)
		if mode_time>=.30:
			mode="ready"
			mode_time=0
			anim.play(READY,.055)
	elif mode in ["ready","attack"]:
		combat_weight=minf(1,combat_weight+delta/.15)
		if mode=="ready" and (held or pending) and elapsed+.000001>=next_attack:_attack()
		if not wants and (not attack_busy or anim.current_animation_position>=HIT_TIME+.025):_exit(speed>.08)
	elif mode in ["exit","exit_move"]:
		combat_weight=maxf(0,combat_weight-delta/.30)
		if combat_weight<=.001:
			mode="travel"
			mode_time=0
			attack_busy=false
	if mode=="travel":
		var clip=WALK if speed>.10 else IDLE
		if anim.current_animation!=clip:anim.play(clip,.13)
		anim.speed_scale=maxf(.15,speed/3.5) if clip==WALK else 1.0
	else:anim.speed_scale=1.0
	if attack_busy and anim.current_animation in [LEFT,RIGHT] and not hit_fired and anim.current_animation_position>=HIT_TIME:
		hit_fired=true
		_log("contact")
	var aim=Vector3(0,0,-1) if record_mode else player.aim_dir()
	var facing=aim if wants or combat_weight>.01 else move
	if facing.length_squared()>.001:
		var desired=atan2(facing.x,facing.z)
		model.rotation.y=lerp_angle(model.rotation.y,desired,1.0-exp(-20.0*delta))
	var aim_error=absf(wrapf(atan2(aim.x,aim.z)-model.rotation.y,-PI,PI)) if aim.length_squared()>.01 else 0
	label.text="GORILLA / SLOW SWING BASIC ATTACK (v18)\n%s | %s | %.2f m/s\nHold LMB + WASD | release returns to knuckle movement" % ["Fists ready / "+active_hand if combat_weight>.5 else "Knuckle stance",_movement_name(move),speed]
	if elapsed>=sample_time:
		runtime.store_line("%.4f,%s,%s,%s,%.4f,%.4f,%.4f,%.3f,%s,%.4f,%.4f" % [elapsed,str(held),mode,active_hand,player.position.x,player.position.z,speed,rad_to_deg(aim_error),anim.current_animation,anim.current_animation_position,combat_weight])
		runtime.flush()
		sample_time+=.05
	_hide_aim.call_deferred()
	camera.snap()

func _enter(moving):
	mode="enter"
	mode_time=0
	attack_busy=false
	anim.play(READY if moving else ENTER,.18 if moving else .08)
	_log("enter_combat")

func _exit(moving):
	mode="exit_move" if moving else "exit"
	mode_time=0
	attack_busy=false
	anim.play(WALK if moving else EXIT,.25 if moving else .10)
	_log("release_combat")

func _attack():
	active_hand="Left" if left_next else "Right"
	left_next=not left_next
	attack_busy=true
	hit_fired=false
	pending=false
	mode="attack"
	mode_time=0
	next_attack=elapsed+COOLDOWN
	anim.play(LEFT if active_hand=="Left" else RIGHT,.055)
	_log("attack_start")

func _finished(clip):
	if clip not in [LEFT,RIGHT]:return
	attack_busy=false
	if mode=="attack":
		mode="ready"
		mode_time=0
		anim.play(READY,.07)

func _log(event):
	if events:
		events.store_line("%.5f,%s,%s,%s,%.5f" % [elapsed,event,active_hand,anim.current_animation,anim.current_animation_position])
		events.flush()
	print("COMBAT_EVENT ",event," hand=",active_hand," time=",elapsed)

func _route(t):
	if t<2.8:return Vector3.ZERO
	if t<3.65:return Vector3.RIGHT
	if t<5.35:return Vector3.LEFT
	if t<6.2:return Vector3.RIGHT
	if t<6.3:return Vector3.FORWARD
	if t<6.9:return Vector3.BACK
	if t<7.4:return Vector3.FORWARD
	if t<8.6:return Vector3.ZERO
	if t<9.35:return Vector3.LEFT
	if t<10.4:return Vector3.ZERO
	if t<11.15:return Vector3.RIGHT
	if t<12:return Vector3.ZERO
	if t<12.85:return Vector3(1,0,1).normalized()
	if t<13.7:return Vector3(-1,0,-1).normalized()
	if t<14.2:return Vector3.FORWARD
	return Vector3.ZERO

func _movement_name(v):
	if v.length_squared()<.01:return "Standing"
	if absf(v.x)>.5:return "Strafing right" if v.x>0 else "Strafing left"
	return "Moving forward" if v.z<0 else "Moving backward"

func _hide_aim():
	var ring=player.get("_aim_ring")
	var line=player.get("_aim_line")
	if ring:ring.visible=false
	if line:line.visible=false
