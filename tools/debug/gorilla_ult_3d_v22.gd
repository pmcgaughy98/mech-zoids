extends Node3D
## Gorilla 3D kit review v22 (2026-11-09): SMITE-style camera behind the gorilla; the dome now wards (heals, and the
## gorilla cannot drop below 1 hp inside) in place of ally shields; new plate-cell shell look. From v21: the chest beat ult (key 4) on the 3D model, driving the real ApeKit (taunt, ally shields, dome)
## with beat timing from the 3D clip. Also keeps v20's chain: swat, swat, slam: swat, swat, two-fist slam. Slam feel from game feel (2026-11-09): 0.09 s hitstop, short shake; chain resets after 1.5 s without a hit.
## Earlier header (v19): under the match rule (game feel, 2026-11-09):
## rooted from wind-up to the fist plant plus a 0.06 s hitstop, backswing free and cancelled by moving.
## Production kit unchanged.
## v23 (2026-11-09): key 2 Fling (Preston's pick) on the 3D model; the ult dome is a 5.5 m cage for both teams with breakable panels.
## v24 (2026-11-09): Walk v24 = v17's pace and plants plus the control-rig walk's torso roll, steady head and smooth swing.
const MODEL="res://art/model_catalog/workspaces/gorilla_kit_v26.glb"
const FLING="Gorilla_Fling_v25"
const IDLE="Gorilla_Idle_v25"
const WALK="Gorilla_Walk_v25"
const LEFT="Gorilla_Swat_Left_v25"
const RIGHT="Gorilla_Swat_Right_v25"
const SLAM="Gorilla_Slam_v25"
const ULT="Gorilla_ChestBeat_Ult_v25"
const HIT_FRONT="Gorilla_Hit_Front_v25"
const HIT_HEAVY="Gorilla_Hit_Heavy_v25"
var hit_left=0.0  # a hit clip owns the body until it ends
const ULT_BEATS: Array[float]=[0.42,0.75,1.27]  # slower strikes, 0.11 s apart (2026-11-09)
const HIT_TIME=0.30
const SLAM_HIT_TIME=50.0/120.0
const HITSTOP=0.06
const SLAM_HITSTOP=0.09
const CHAIN_RESET=1.5
const COOLDOWN=1.0
const EVIDENCE="D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-ult-v22"
var player: Node3D
var model: Node3D
var camera: Camera3D
var anim: AnimationPlayer
var started=false
var front_hit_done=false
var fling_target: Node3D
var fling_done=false
var record_mode=false
var walk_mode=false
var attack_mode=false  # --attacks: hold the basic for the full swat, swat, slam chain  # --walk: record a walk pattern only (sideways, back, away, toward)
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
var big_hit_done=false
var shield_shown=false
var label: Label
var events: FileAccess

func _ready():
	get_window().content_scale_size=Vector2i(1280,720)
	get_window().size=Vector2i(1280,720)
	record_mode="--record" in OS.get_cmdline_user_args() or "--walk" in OS.get_cmdline_user_args()
	walk_mode="--walk" in OS.get_cmdline_user_args()
	attack_mode="--attacks" in OS.get_cmdline_user_args()
	if attack_mode:record_mode=true
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
	player.max_hp=500.0
	player.hp=150.0
	var base=player.position
	for d in [[Vector3(0,0,-4.5),false],[Vector3(-1.4,0,-1.4),false],[Vector3(5.0,0,-5.0),false],[Vector3(-5.0,0,0.6),true]]:
		var dummy=Node3D.new()
		dummy.set_script(load("res://scripts/moba3d/training_dummy.gd"))
		field.add_child(dummy)
		dummy.global_position=base+d[0]
		if d[1]:ApeKit.make_ally(dummy)
	fling_target=Node3D.new()
	fling_target.set_script(load("res://scripts/moba3d/training_dummy.gd"))
	field.add_child(fling_target)
	fling_target.global_position=base+Vector3(0.3,0,-1.5)  # in grab reach, a little to the side so the camera sees it
	camera=field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(not record_mode)
	camera.yaw_degrees=180  # behind the gorilla, over the shoulder (SMITE-style)
	camera.distance=6.2
	camera.pitch_degrees=15
	camera.look_height=1.6
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
	for n in [IDLE,WALK,LEFT,RIGHT,SLAM,ULT,FLING,HIT_FRONT,HIT_HEAVY]:
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

func _title():DisplayServer.window_set_title("Gorilla Ult 3D v22")

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
	if attack_mode:
		held=elapsed>=0.3 and elapsed<3.6
		if elapsed>5.0:get_tree().quit()
	elif walk_mode:
		held=false
		for leg in [[0.3,1.5,Vector3(1,0,0)],[1.5,3.9,Vector3(-1,0,0)],[3.9,5.1,Vector3(1,0,0)],[5.1,6.3,Vector3(0,0,-1)],[6.3,7.5,Vector3(0,0,1)]]:
			if elapsed>=leg[0] and elapsed<leg[1]:move=leg[2]
		if elapsed>8.3:get_tree().quit()
	elif record_mode:
		held=false
		move=Vector3.ZERO
		if elapsed>=0.3 and not fling_done:
			fling_done=true
			_fling()
		if elapsed>=1.6 and not shield_shown:
			shield_shown=true
			HexShield.shield(player,3.0)  # the key 1 hex shield, to show the new shell look before the ult
			_log("shield_look")
		if elapsed>=2.6 and not ult_cast:_ult()
		if elapsed>=5.0 and not big_hit_done:
			big_hit_done=true
			player.take_damage(100.0)  # no 1 hp floor any more (2026-11-09)
			_log("big_hit hp=%.0f" % player.hp)
			_hit(HIT_HEAVY)
		if elapsed>=6.4 and hit_left<=0 and not front_hit_done:
			front_hit_done=true
			_hit(HIT_FRONT)
		if elapsed>9.6:get_tree().quit()
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
	if hit_left>0:
		hit_left-=delta
	elif not swinging:
		var clip=WALK if speed>.10 else IDLE
		if anim.current_animation!=clip:anim.play(clip,.13)
		anim.speed_scale=maxf(.15,speed/3.5) if clip==WALK else 1.0
	var aim=Vector3(0,0,-1) if record_mode else player.aim_dir()
	var facing=aim if (swinging or held) and (rooted or move.length_squared()<.01) else move
	if facing.length_squared()>.001:
		model.rotation.y=lerp_angle(model.rotation.y,atan2(facing.x,facing.z),1.0-exp(-(28.0 if rooted else 16.0)*delta))
	label.text="GORILLA 3D KIT (v26 wrists)  HP %d / 500%s  |  key 2: FLING | key 4: CHEST BEAT ULT | hold LMB: swat, swat, slam (hit %d of 3)\n%s | %.2f m/s\nHold LMB + WASD | rooted to the plant, moving cancels the backswing" % [player.hp,("  IN THE CAGE: heals" if HexShield.wards(player) else ""),chain,(("CHEST BEAT ULT: taunt, taunt, warding dome" if is_ult else ("SLAM" if is_slam else "SWAT "+active_hand))+(" (rooted)" if rooted else "")) if swinging else "Knuckle walk",speed]
	_hide_aim.call_deferred()
	camera.snap()
	if shake_left>0:
		shake_left-=delta
		var k=maxf(0,shake_left/.18)
		camera.global_position+=Vector3(sin(elapsed*90.0),cos(elapsed*77.0),0)*.07*k

func _hit(clip:String):
	if swinging:return
	anim.speed_scale=1.0
	anim.play(clip,.05)
	hit_left=anim.get_animation(clip).length
	_log("hit "+clip)

func _fling():
	is_ult=true  # the kit drives it, not the basic's hit
	is_slam=false
	swinging=true
	rooted=true
	hit_fired=true
	anim.speed_scale=1.0
	anim.play(FLING,.06)
	kit.fling(fling_target)
	_log("fling_cast")

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
	if clip not in [LEFT,RIGHT,SLAM,ULT,FLING]:return
	if clip==ULT or clip==FLING:
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
