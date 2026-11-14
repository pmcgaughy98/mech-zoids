extends Node3D
## Knuckle swat basic attack review v19 under the match rule (game feel, 2026-11-09):
## rooted from wind-up to the fist plant plus a 0.06 s hitstop, backswing free and cancelled by moving.
## Production kit unchanged.
const MODEL="res://art/model_catalog/workspaces/gorilla_knuckle_swat_v19.glb"
const IDLE="Gorilla_Idle_v14"
const WALK="Gorilla_Walk_v17"
const LEFT="Gorilla_Swat_Left_v19"
const RIGHT="Gorilla_Swat_Right_v19"
const HIT_TIME=0.30
const HITSTOP=0.06
const COOLDOWN=1.0
const EVIDENCE="D:/dev/_scratch/gorilla/meshforge-2026-11-08/industry-swat-v19"
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
	var skeleton=model.find_children("*","Skeleton3D",true,false)[0] as Skeleton3D
	for n in [IDLE,WALK,LEFT,RIGHT]:
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

func _title():DisplayServer.window_set_title("Gorilla Knuckle Swat v19")

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
		held=(elapsed>=1.0 and elapsed<8.6) or (elapsed>=10.4 and elapsed<13.7)
		move=_route(elapsed)
		if elapsed>20.0:get_tree().quit()
	else:
		held=Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) or Input.is_physical_key_pressed(KEY_SPACE)
		player.move_override=null
		move=player.move_dir()
	# hitstop: freeze the model on the plant frame
	if hitstop_left>0:
		hitstop_left-=delta
		if hitstop_left<=0:
			anim.speed_scale=1.0
			rooted=false
			_log("released")
	if held and not swinging and elapsed+.000001>=next_attack:_attack()
	if swinging and not hit_fired and anim.current_animation_position>=HIT_TIME:
		hit_fired=true
		anim.seek(HIT_TIME,true)
		anim.speed_scale=0.0
		hitstop_left=HITSTOP
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
	label.text="GORILLA / KNUCKLE SWAT BASIC ATTACK (v19)\n%s | %.2f m/s\nHold LMB + WASD | rooted to the plant, moving cancels the backswing" % [("SWAT "+active_hand+(" (rooted)" if rooted else "")) if swinging else "Knuckle walk",speed]
	_hide_aim.call_deferred()
	camera.snap()

func _attack():
	active_hand="Left" if left_next else "Right"
	left_next=not left_next
	swinging=true
	rooted=true
	hit_fired=false
	next_attack=elapsed+COOLDOWN
	anim.speed_scale=1.0
	anim.play(LEFT if active_hand=="Left" else RIGHT,.06)
	_log("attack_start")

func _finished(clip):
	if clip not in [LEFT,RIGHT]:return
	swinging=false
	rooted=false

func _log(event):
	if events:
		events.store_line("%.5f,%s,%s,%s,%.5f,%.4f,%.4f" % [elapsed,event,active_hand,anim.current_animation,anim.current_animation_position,player.position.x,player.position.z])
		events.flush()
	print("SWAT_EVENT ",event," hand=",active_hand," time=",snappedf(elapsed,.001)," x=",snappedf(player.position.x,.001))

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
