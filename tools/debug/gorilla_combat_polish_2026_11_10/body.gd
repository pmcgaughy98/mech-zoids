extends "res://scripts/moba3d/mech_model_3d.gd"
const MODEL="D:/dev/_scratch/gorilla/combat-polish-2026-11-10/combat-polish.glb"
# external_clock is now supplied by the shared runtime body.
var serial:=0
var emitted: Dictionary={}
func configure_review() -> bool:
	kind="gorilla"
	_row=ROWS["gorilla"].duplicate(true)
	_row["glb"]=MODEL
	var tpl:=_template(MODEL)
	if tpl==null:return false
	_model=tpl.duplicate() as Node3D
	_model.name="Model"
	_model.position.y=.006
	add_child(_model)
	anim=_model.find_child("AnimationPlayer",true,false) as AnimationPlayer
	skeleton=_model.find_child("Skeleton3D",true,false) as Skeleton3D
	anim.process_priority=-10
	_clips={"Idle":"Gorilla_Idle_v25","Walk":"Gorilla_Walk_v25","Swat_Left":"Gorilla_Swat_Left_v25","Swat_Right":"Gorilla_Swat_Right_v25","Slam":"Gorilla_Slam_v25","Shield_Ally":"Gorilla_Shield_Ally_CodexTrial","Shield_Self":"Gorilla_Shield_Self_CodexTrial","Ult":"Gorilla_ChestBeat_Ult_Codex_ExitTrial","GrabSlam":"Gorilla_GrabSlam_CodexTrial","Fling_Whiff":"Gorilla_Fling_Whiff_v25","DriveBrace":"Gorilla_ShieldDrive_Brace_Trial","Drive":"Gorilla_ShieldDrive_Drive_Trial","DriveHit":"Gorilla_ShieldDrive_Hit_Trial","DriveBrake":"Gorilla_ShieldDrive_Brake_Trial"}
	for clip in _clips:assert(anim.has_animation(_clips[clip]),clip)
	_events={"Swat_Left":[["hit",.30,true]],"Swat_Right":[["hit",.30,true]],"Slam":[["hit",50.0/120.0,true]],"Shield_Ally":[["release",.25,false]],"Shield_Self":[["release",.25,false]],"Ult":[["drum",50.0/120.0,false],["beat",.42,false],["drum",64.0/120.0,false],["drum",77.0/120.0,false],["drum",.75,false],["beat",.75,false],["beat",1.27,false]],"GrabSlam":[["grab",.18,false],["ground",.60,true]]}
	_walk_speed=3.5
	_rest=1.7
	_peaks={"Slam":2.51,"GrabSlam":2.94,"Ult":3.06}
	for clip in ["Idle","Walk"]:anim.get_animation(_clips[clip]).loop_mode=Animation.LOOP_LINEAR
	locomote(0)
	return true
func play_action(clip: String, speed:=1.0, blend:=.06) -> float:
	serial+=1
	emitted.clear()
	return super.play_action(clip,speed,blend)
func start_external(clip: String) -> void:
	external_clock=true
	anim.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	play_action(clip,1.0,0)
	anim.advance(0)
func sample_external(clip: String, time: float) -> void:
	if action!=clip:
		play_action(clip,1.0,0)
	anim.seek(time,true)
	anim.advance(0)
func emit_external(name: String, damage:=false) -> void:
	if emitted.has(name):return
	emitted[name]=true
	event.emit(action,name,damage)
func finish_external() -> void:
	stop_action()
	external_clock=false
	anim.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE
	locomote(0)
func _process(delta: float) -> void:
	if external_clock:
		position=feel_offset
	else:super._process(delta)
func grip() -> Vector3:
	return skeleton.global_transform*((skeleton.get_bone_global_pose(skeleton.find_bone("LeftHand")).origin+skeleton.get_bone_global_pose(skeleton.find_bone("RightHand")).origin)*.5)
func hand(side: String) -> Vector3:
	return skeleton.global_transform*skeleton.get_bone_global_pose(skeleton.find_bone(side+"Hand")).origin

func use_compact(value: bool) -> void:
	_clips["Slam"]="Gorilla_Slam_Compact_Trial" if value else "Gorilla_Slam_v25"
