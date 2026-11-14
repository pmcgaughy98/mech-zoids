extends Node3D
const P="res://tools/debug/gorilla_visual_review_2026_11_09/"
const OUT="D:/dev/_scratch/gorilla/codex-move-visuals-2026-11-09/"
const DRIVE="D:/dev/_scratch/gorilla/codex-shield-drive-trial-2026-11-09/drive_controller.gd"
const GRAB="D:/dev/_scratch/gorilla/codex-grab-slam-trial-2026-11-09/slam_controller.gd"
const SHOTS=[
	[4.3,"BODY ONLY / BASIC CHAIN","chain",false],
	[4.3,"CONTACT FX / BASIC CHAIN","chain",true],
	[4.1,"SHIELD / RELEASE THEN CALM","shield",true],
	[2.5,"ALLY SHIELD / DIRECTED RELEASE","ally_shield",true],
	[2.3,"SHIELD DRIVE / BRACE > CONTACT > BRAKE","drive",true],
	[2.3,"SHIELD DRIVE / MISS > BRAKE","drive_miss",true],
	[3.0,"GRAB / LIFT > GROUND SLAM","grab",true],
	[3.0,"GRAB / BODY ONLY","grab",false],
	[6.0,"CHEST BEATS > OVERHEAD SLAM > CAGE","ult",true],
	[2.0,"INTERRUPTED CAST / NO SHIELD","interrupt_shield",true],
	[2.2,"INTERRUPTED ULT / NO CAGE","interrupt_ult",true],
	[2.0,"GRAB MISS / NO DAMAGE OR IMPACT","grab_miss",true]
]
var actor: Node3D
var body: MechModel3D
var kit: ApeKit
var fx: Node3D
var enemy: Node3D
var drive: Node
var grab: Node
var camera: Camera3D
var label: Label
var interactive:=false
var elapsed:=0.0
var shot:=-1
var shot_time:=0.0
var step:=0
var attack_cd:=0.0
var rows: Array=[]
var shot_results: Array=[]
var seen: Dictionary={}
var drum:=0
var shot_start:=0
var snapshot_taken:=false
func _ready() -> void:
	process_priority=-20
	interactive="--interactive" in OS.get_cmdline_user_args()
	get_window().title="Gorilla / playable visual review"
	get_window().size=Vector2i(1280,720)
	get_window().content_scale_size=Vector2i(1280,720)
	var field: Node3D=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	actor=field.get_node("Player")
	actor.team="blue"
	actor.process_priority=-15
	actor.set_meta("is_player",true)
	var old:=actor.get_node("Kit")
	actor.remove_child(old)
	old.queue_free()
	if actor.body!=null:actor.body.visible=false
	for n in ["Sprite","Ring","Shadow"]:actor.get_node(n).visible=false
	actor.get_node("Sprite").sprite_frames=ApeKit.APE_FRAMES
	actor.get_node("Sprite").size_class="L"
	body=load(P+"body.gd").new()
	body.name="ReviewBody"
	actor.add_child(body)
	assert(body.configure_review())
	actor.body=body
	fx=load(P+"effects.gd").new()
	add_child(fx)
	fx.setup(body.model_root())
	kit=load(P+"review_kit.gd").new()
	kit.name="Kit"
	kit.visuals=fx
	kit.shake_camera=false
	actor.add_child(kit)
	kit.set_process_unhandled_key_input(false)
	kit.used.connect(on_used)
	kit.cue.connect(on_cue)
	kit.impact.connect(on_impact)
	body.event.connect(on_event)
	enemy=load(P+"target.gd").new()
	add_child(enemy)
	enemy.hurt.connect(on_hurt)
	drive=load(DRIVE).new()
	add_child(drive)
	drive.setup(actor)
	drive.valid_targets=[enemy]
	drive.phase_changed.connect(drive_phase)
	drive.collision.connect(drive_contact)
	drive.finished.connect(custom_finish)
	grab=load(GRAB).new()
	add_child(grab)
	grab.setup(actor,body.grip,func():return body.model_root().rotation.y)
	grab.sampled.connect(func(t):body.sample_external("Fling_Whiff" if grab.whiff else "GrabSlam",t))
	grab.caught.connect(func(_v):body.emit_external("grab");fx.cells(.15);sound("shield_wind"))
	grab.slammed.connect(grab_contact)
	grab.finished.connect(custom_finish)
	camera=field.get_node("Camera")
	camera.distance=6.6
	camera.pitch_degrees=12
	camera.look_height=1.3
	camera.set_process_unhandled_input(interactive)
	var layer:=CanvasLayer.new()
	add_child(layer)
	label=Label.new()
	label.position=Vector2(20,20)
	label.add_theme_font_size_override("font_size",22)
	layer.add_child(label)
	set_shot(0)
	print("GORILLA_VISUAL_REVIEW_READY")
func log_event(name: String, detail: Dictionary={}) -> void:
	rows.append({"time":elapsed,"shot":shot,"event":name,"clip":body.action,"clip_time":body.anim.current_animation_position,"detail":detail})
func sound(name: String) -> void:
	if not fx.enabled:return
	var path:="res://audio/sfx/ape/"+name+".wav"
	if ResourceLoader.exists(path):get_node("/root/KitAudio").play(path,&"SFX")
	log_event("sound",{"name":name})
func on_used(slot: String) -> void:
	log_event("cast",{"slot":slot})
	if slot=="1":sound("shield_wind")
	if slot=="4":drum=0
func on_cue(name: String) -> void:
	log_event("cue",{"name":name})
	if name=="strike_swing":sound("strike_swing")
	if name=="strike_hit":sound("strike_hit")
func on_event(clip: String, name: String, _damage: bool) -> void:
	log_event(name)
	if name=="release" and clip.begins_with("Shield"):
		shield_release.call_deferred(body.serial)
	if clip=="Ult" and name=="drum":
		drum+=1
		fx.cells(.1)
		sound("chest_hit")
func shield_release(serial: int) -> void:
	if serial!=body.serial or not actor.alive or actor.stunned>0:return
	var shield_target: Node3D=enemy if enemy.team=="blue" else actor
	if ApeKit.shield_on(shield_target)!=null:
		fx.cells(.28)
		fx.pulse(shield_target.global_position,.9,.20)
		sound("shield_up")
		log_event("shield_applied")
func on_impact(strength: float) -> void:
	if body.action=="Ult" and strength>.7:
		var key:="dome_%d" % body.serial
		if seen.has(key):return
		seen[key]=true
		fx.ground(actor.global_position,.9)
		sound("dome_slam")
		log_event("cage_raised",{"domes":HexShield.live_domes().size()})
func on_hurt(amount: float, _by: Node3D) -> void:
	log_event("damage",{"amount":amount})
	if body.action not in ["Swat_Left","Swat_Right","Slam"]:return
	var key:="contact_%d" % body.serial
	if seen.has(key):return
	seen[key]=true
	var normal: Vector3=(enemy.global_position-actor.global_position).normalized()
	var hand: Vector3=body.hand("Left" if body.action=="Swat_Left" else "Right")
	var at:=Vector3(enemy.global_position.x,clampf(hand.y,.45,1.25),enemy.global_position.z)-normal*.20
	fx.contact(at,normal,body.action=="Slam")
	if body.action=="Slam":fx.ground(enemy.global_position,.45)
func drive_phase(phase: String) -> void:
	log_event("drive_phase",{"phase":phase})
	var clips:={"brace":"DriveBrace","drive":"Drive","hit":"DriveHit","brake":"DriveBrake"}
	if clips.has(phase):body.start_external(clips[phase])
	if phase=="brace":fx.cells(.24);sound("shield_wind")
	if phase=="drive":fx.cells(.35)
func drive_contact(target: Node3D, _damage: float) -> void:
	body.emit_external("collision",true)
	fx.contact(target.global_position+Vector3.UP*.8-drive.direction*.22,drive.direction,true)
	fx.cells(.18)
	sound("bound_land")
	log_event("drive_contact")
func grab_contact(target: Node3D) -> void:
	body.emit_external("ground",true)
	var at: Vector3=target.body.global_position
	fx.ground(at,.72)
	fx.cells(.18)
	sound("dome_slam")
	log_event("grab_ground",{"damage_calls":target.damage_calls})
func custom_finish(reason: String) -> void:
	body.finish_external()
	kit.current=""
	actor.busy=false
	log_event("custom_end",{"reason":reason})
func request(which: String) -> void:
	if actor.stunned>0 or not actor.alive or drive.phase!="idle" or grab.active:return
	if which=="basic":
		if attack_cd<=0 and kit.basic_attack(enemy if enemy.visible and enemy.alive else null):attack_cd=kit.basic_cooldown
	elif which=="shield":kit.hex_shield()
	elif which=="ult":kit.chest_beat_ult()
	elif which in ["grab","drive"]:
		if not kit._begin(which):return
		body.snap_facing(actor.facing)
		if which=="grab":
			body.start_external("GrabSlam")
			if not grab.begin(enemy if enemy.visible and enemy.alive else null):custom_finish("refused")
		else:drive.begin(actor.facing)
func interrupt() -> void:
	actor.stunned=.45
	kit.abort_review()
	drive.interrupt("stun")
	grab.interrupt("stun")
	body.finish_external()
	fx.clear_transient()
	log_event("interrupt")
func set_shot(index: int) -> void:
	if shot>=0:save_result()
	kit.abort_review()
	drive.interrupt("reset")
	grab.interrupt("reset")
	for h in get_tree().get_nodes_in_group("hex_shield"):
		if is_instance_valid(h):h.queue_free()
	for h in HexShield.live_domes():h.queue_free()
	for h in actor.get_children():
		if h is HexShield:h.queue_free()
	fx.clear_transient()
	body.finish_external()
	shot=index
	shot_time=0
	step=0
	shot_start=rows.size()
	snapshot_taken=false
	attack_cd=0
	kit.chain_hit=0
	kit._chain_timer=null
	kit._left_next=false
	actor.position=Vector3.ZERO
	actor.facing=Vector3(0,0,1)
	actor.stunned=0
	actor.busy=false
	actor.move_override=null if interactive else Vector3.ZERO
	actor.input_override=null if interactive else Vector2.ZERO
	body.snap_facing(actor.facing)
	enemy.team="blue" if SHOTS[shot][2]=="ally_shield" else "red"
	enemy.reset(Vector3(1.5,0,1.7) if enemy.team=="blue" else Vector3(0,0,1.28))
	for h in enemy.get_children():
		if h is HexShield:h.queue_free()
	enemy.shove_left=0
	enemy.visible=not SHOTS[shot][2].ends_with("miss")
	drive.valid_targets=[] if SHOTS[shot][2]=="drive_miss" else [enemy]
	fx.set_enabled(SHOTS[shot][3])
	enemy.visual_fx=fx.enabled
	actor.set_meta("is_player",fx.enabled)
	camera.yaw_degrees=(45 if fx.enabled else 90) if SHOTS[shot][2]=="grab" else 180
	camera.snap()
func save_result() -> void:
	shot_results.append({"shot":shot,"name":SHOTS[shot][2],"fx":fx.enabled,"hp":enemy.hp,"damage_calls":enemy.damage_calls,"controls_disabled":enemy.controls_disabled,"attachment_error":grab.max_attachment_error,"domes":HexShield.live_domes().size(),"events":rows.slice(shot_start)})
func _process(delta: float) -> void:
	if actor==null:return
	elapsed+=delta
	shot_time+=delta
	attack_cd=maxf(0,attack_cd-delta)
	drive.tick(delta)
	if drive.phase!="idle":body.sample_external(body.action,drive.phase_time)
	grab.tick(delta)
	if interactive:
		if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):request("basic")
		if drive.can_cancel_recovery() and actor.move_dir().length()>.05:drive.request_movement()
	else:
		var kind: String=SHOTS[shot][2]
		if shot_time>.5 and step==0:
			step=1
			request("basic" if kind=="chain" else "shield" if kind in ["interrupt_shield","ally_shield"] else "ult" if kind=="interrupt_ult" else "drive" if kind=="drive_miss" else "grab" if kind=="grab_miss" else kind)
		if kind=="chain" and step<3 and shot_time>.5+step*1.05:
			step+=1
			request("basic")
		if kind=="interrupt_shield" and step==1 and shot_time>.62:step=2;interrupt()
		if kind=="interrupt_ult" and step==1 and shot_time>1.35:step=2;interrupt()
		if shot_time>SHOTS[shot][0]:
			if shot+1==SHOTS.size():
				save_result()
				var f:=FileAccess.open(OUT+"visual-results.json",FileAccess.WRITE)
				f.store_string(JSON.stringify(shot_results,"  "))
				print("GORILLA_VISUAL_REVIEW_COMPLETE")
				get_tree().quit()
			else:set_shot(shot+1)
	label.text="GORILLA / VISUAL REVIEW\n"+("WASD • Hold LMB basic • 1 shield • 2 grab slam • 3 drive • 4 cage\nF body-only toggle • I interrupt • R reset • right drag camera" if interactive else SHOTS[shot][1])+"\n"+("FX ON" if fx.enabled else "BODY ONLY")+"  /  "+body.action
	if not fx.enabled:
		for n in actor.get_children():
			if n is HexShield:n.visible=false
		for dome in HexShield.live_domes():dome.visible=false
func _unhandled_input(event: InputEvent) -> void:
	if not interactive or not event.is_pressed() or event.is_echo():return
	if event is InputEventKey:
		match event.keycode:
			KEY_1:request("shield")
			KEY_2:request("grab")
			KEY_3:request("drive")
			KEY_4:request("ult")
			KEY_I:interrupt()
			KEY_R:set_shot(0);fx.set_enabled(true);actor.set_meta("is_player",true)
			KEY_F:
				fx.set_enabled(not fx.enabled)
				enemy.visual_fx=fx.enabled
				actor.set_meta("is_player",fx.enabled)
				for n in actor.get_children():
					if n is HexShield:n.visible=fx.enabled
				for dome in HexShield.live_domes():dome.visible=fx.enabled
			KEY_ESCAPE:get_tree().quit()

func _exit_tree() -> void:
	for template in MechModel3D._templates.values():
		if is_instance_valid(template):template.free()
	MechModel3D._templates.clear()
