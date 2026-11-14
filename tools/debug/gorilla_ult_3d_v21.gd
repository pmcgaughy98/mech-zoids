extends Node3D
## Gorilla 3D kit review v21: the chest beat ult (key 4) on the 3D model, driving the real ApeKit (taunt, ally shields, dome)
## with beat timing from the 3D clip. Also keeps v20's chain: swat, swat, slam: swat, swat, two-fist slam. Slam feel from game feel (2026-11-09): 0.09 s hitstop, short shake; chain resets after 1.5 s without a hit.
## Earlier header (v19): under the match rule (game feel, 2026-11-09):
## rooted from wind-up to the fist plant plus a 0.06 s hitstop, backswing free and cancelled by moving.
## Production kit unchanged.
const MODEL="res://art/model_catalog/workspaces/gorilla_chest_beat_ult_v21.glb"
const IDLE="Gorilla_Idle_v14"
const WALK="Gorilla_Walk_v17"
const LEFT="Gorilla_Swat_Left_v19"
const RIGHT="Gorilla_Swat_Right_v19"
const SLAM="Gorilla_Slam_v20"
const ULT="Gorilla_ChestBeat_Ult_v21"
const ULT_BEATS: Array[float]=[0.45,0.70,1.10]
const HIT_TIME=0.30
const SLAM_HIT_TIME=50.0/120.0
const HITSTOP=0.06
const SLAM_HITSTOP=0.09
const CHAIN_RESET=1.5
const COOLDOWN=1.0
const EVIDENCE="D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-ult-v21"
var player: Node3D
var model: Node3D
var camera: Camera3D
var anim: AnimationPlayer
var started=false
var record_mode=false
var elapsed=0.0
var combat_weight=0.0
var actual_velocity=Vector3.ZERO
var previous_pos=Vector3.ZERO
var held=false
var swinging=false
var rooted=false
var hit_fired=false
var hitstop_left=0.0
var left_next=true
var next_attack=0.0
var active_hand=""
var chain=0
var last_contact=-99.0
var is_slam=false
var shake_left=0.0
var kit: ApeKit
var is_ult=false
var ult_cast=false
var key4_was=false
var label: Label
var events: FileAccess

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
	for n in ["Ring","Shadow"]:player.get_node(n).visible=false
	kit=ApeKit.install(player)
	player.get_node("Sprite").visible=false
	kit.process_mode=Node.PROCESS_MODE_DISABLED  # this scene drives it, so the 3D clip and the kit start together
	kit.beat_times=ULT_BEATS
	var base=player.position
	for d in [[Vector3(0,0,-4.5),false],[Vector3(-1.4,0,-1.4),false],[Vector3(5.0,0,-5.0),false],[Vector3(-5.0,0,0.6),true]]:
		var dummy=Node3D.new()
		dummy.set_script(load("res://scripts/moba3d/training_dummy.gd"))
		field.add_child(dummy)
		dummy.global_position=base+d[0]
		if d[1]:ApeKit.make_ally(dummy)
	camera=field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(not record_mode)
	camera.yaw_degrees=0
	camera.distance=11.0
	camera.pitch_degrees=34
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
	var skeleton=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	for n in [IDLE,WALK,LEFT,RIGHT,SLAM,ULT]:
		if not anim.has_animation(n):
			push_error("Missing clip "+n)
			get_tree().quit(1)
			return
		anim.get_animation(n).loop_mode=Animation.LOOP_LINEAR if n in [IDLE,WALK] else Animation.LOOP_NONE
	var quad=load("res://tools/debug/gorilla_quad_contacts_v17.gd").new()
	skeleton.add_child(quad)
	quad.setup(self,anim,EVIDENCE)
	anim.animation_finished.connect(_finished)
	anim.play(IDLE)
	previous_pos=player.global_position
	var layer=CanvasLayer.new()
	add_child(layer)
	label=Label.new()
	label.position=Vector2(20,20)
	label.add_theme_font_size_override("font_size",20)
	layer.add_child(label)
	events=FileAccess.open(EVIDENCE+"/attack-events.csv",FileAccess.WRITE)
	events.store_line("time,event,hand,clip,clip_time,x,z")
	camera.snap()
	_title.call_deferred()
	print("KNUCKLE_SWAT_READY clips=",anim.get_animation_list())

func _title():DisplayServer.window_set_title("Gorilla Ult 3D v21")

func _process(delta):
	if Input.is_physical_key_pressed(KEY_ESCAPE):get_tree().quit()
	if not anim:return
	actual_velocity=(player.global_position-previous_pos)/maxf(delta,.0001)
	previous_pos=player.global_position
	if not started:
		if not record_mode or FileAccess.file_exists(EVIDENCE+"/record.trigger"):started=true
		else:return
	elapsed+=delta
	var move=Vector3.ZERO
	if record_mode:
		held=false
		move=Vector3.ZERO
		if elapsed>=1.5 and not ult_cast:_ult()
		if elapsed>9.0:get_tree().quit()
	else:
		held=Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or Input.is_physical_key_pressed(KEY_SPACE)
		player.move_override=null
		move=player.move_dir()
		var k4=Input.is_physical_key_pressed(KEY_4)
		if k4 and not key4_was and not swinging:_ult()
		key4_was=k4
	# hitstop: freeze the model on the plant frame
	if hitstop_left>0:
		hitstop_left-=delta
		if hitstop_left<=0:
			anim.speed_scale=1.0
			rooted=false
			_log("released")
	if held and not swinging and elapsed+.000001>=next_attack:_attack()
	var hit_time=SLAM_HIT_TIME if is_slam else HIT_TIME
	if swinging and not hit_fired and anim.current_animation_position>=hit_time:
		hit_fired=true
		last_contact=elapsed
		anim.seek(hit_time,true)
		anim.speed_scale=0.0
		hitstop_left=SLAM_HITSTOP if is_slam else HITSTOP
		if is_slam:shake_left=.18
		_log("contact_plant")
	# backswing is free: moving cancels it
	if swinging and not rooted and move.length_squared()>.01:
		swinging=false
		anim.play(WALK,.12)
		_log("cancel_backswing")
	player.move_override=Vector3.ZERO if rooted else move
	var speed=actual_velocity.length()
	if not swinging:
		var clip=WALK if speed>.10 else IDLE
		if anim.current_animation!=clip:anim.play(clip,.13)
		anim.speed_scale=maxf(.15,speed/3.5) if clip==WALK else 1.0
	var aim=Vector3(0,0,-1) if record_mode else player.aim_dir()
	var facing=aim if (swinging or held) and (rooted or move.length_squared()<.01) else move
	if facing.length_squared()>.001:
		model.rotation.y=lerp_angle(model.rotation.y,atan2(facing.x,facing.z),1.0-exp(-(28.0 if rooted else 16.0)*delta))
	label.text="GORILLA 3D KIT (v21)  key 4: CHEST BEAT ULT | hold LMB: swat, swat, slam (hit %d of 3)\n%s | %.2f m/s\nHold LMB + WASD | rooted to the plant, moving cancels the backswing" % [chain,(("CHEST BEAT ULT: taunt, shields, dome" if is_ult else ("SLAM" if is_slam else "SWAT "+active_hand))+(" (rooted)" if rooted else "")) if swinging else "Knuckle walk",speed]
	_hide_aim.call_deferred()
	camera.snap()
	if shake_left>0:
		shake_left-=delta
		var k=maxf(0,shake_left/.18)
		camera.global_position+=Vector3(sin(elapsed*90.0),cos(elapsed*77.0),0)*.07*k

func _ult():
	ult_cast=true
	is_ult=true
	is_slam=false
	swinging=true
	rooted=true
	hit_fired=true  # the ult's beats come from the kit, not the basic's hit
	anim.speed_scale=1.0
	anim.play(ULT,.08)
	kit.chest_beat_ult()
	_log("ult_cast")

func _attack():
	is_ult=false
	if elapsed-last_contact>CHAIN_RESET:chain=0
	chain=chain%3+1
	is_slam=chain==3
	if is_slam:active_hand="Both"
	else:
		active_hand="Left" if left_next else "Right"
		left_next=not left_next
	swinging=true
	rooted=true
	hit_fired=false
	next_attack=elapsed+COOLDOWN
	anim.speed_scale=1.0
	anim.play(SLAM if is_slam else (LEFT if active_hand=="Left" else RIGHT),.06)
	_log("attack_start")

func _finished(clip):
	if clip not in [LEFT,RIGHT,SLAM,ULT]:return
	if clip==ULT:
		is_ult=false
		_log("ult_end")
	swinging=false
	rooted=false

func _log(event):
	if events:
		events.store_line("%.5f,%s,%s,%s,%.5f,%.4f,%.4f" % [elapsed,event,active_hand,anim.current_animation,anim.current_animation_position,player.position.x,player.position.z])
		events.flush()
	print("SWAT_EVENT ",event," chain=",chain," hand=",active_hand," time=",snappedf(elapsed,.001)," x=",snappedf(player.position.x,.001))

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

func _hide_aim():
	var ring=player.get("_aim_ring")
	var line=player.get("_aim_line")
	if ring:ring.visible=false
	if line:line.visible=false
