extends Node3D
## MOBA look v2 (2026-11-09, look lane): v1 plus --mech=rhino (the rhino lane's v38 scratch GLB, read only) and the
## smoothed-normal outline. Same shot: game camera behind the mech, an enemy copy ahead.
## Run windowed:  --path . --script res://tools/debug/moba_look_v2.tscn -- --mech=rhino --look=after   (or --look=before)
## Add --write-movie <file.avi> --fixed-fps 30 to record. Arena, GLB and shared shaders are not edited:
## the grade is a runtime copy of the arena's Environment, the rim/outline go on duplicated materials.
const MECHS={
	"gorilla":{"model":"res://art/model_catalog/workspaces/gorilla_kit_v26.glb","idle":"Gorilla_Idle_v25","walk":"Gorilla_Walk_v25","attack":"Gorilla_Slam_v25","enemy_attack":"Gorilla_Swat_Left_v25","albedo_scale":1.0},
	"rhino":{"model":"D:/dev/_scratch/rhino-donor-2026-11-08/armor-seam-polish-v38/rhino-polish-v38.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":0.7}  # albedo value p50 0.68 vs target 0.34; 0.55 went brown,
}
var MODEL=""
var IDLE=""
var WALK=""
var SLAM=""
var SWAT=""
var ALBEDO_SCALE=1.0
const LOOK=preload("res://scripts/moba3d/mech_look.gd")
var after=false
var player:Node3D
var model:Node3D
var enemy:Node3D
var anim:AnimationPlayer
var enemy_anim:AnimationPlayer
var camera:Camera3D
var t=0.0
var step=0
var label:Label

func _ready():
	get_window().size=Vector2i(1280,720)
	after="--look=after" in OS.get_cmdline_user_args()
	var mech="rhino" if "--mech=rhino" in OS.get_cmdline_user_args() else "gorilla"
	var c:Dictionary=MECHS[mech]
	MODEL=c.model;IDLE=c.idle;WALK=c.walk;SLAM=c.attack;SWAT=c.enemy_attack;ALBEDO_SCALE=c.albedo_scale
	var field=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	player=field.get_node("Player")
	player.position=Vector3(0,0,3.5)
	player.move_speed=3.5
	player.input_override=Vector2.ZERO
	player.move_override=Vector3.ZERO
	for n in ["Sprite","Ring","Shadow"]:player.get_node(n).visible=false
	player.get_node("Kit").process_mode=Node.PROCESS_MODE_DISABLED
	camera=field.get_node("Camera")
	camera.set_process(false)
	camera.set_process_unhandled_input(false)
	camera.yaw_degrees=180
	camera.distance=6.2
	camera.pitch_degrees=15
	camera.look_height=1.6
	model=_load_gorilla()
	player.add_child(model)
	model.rotation.y=PI
	anim=_anim(model)
	enemy=_load_gorilla()
	field.add_child(enemy)
	enemy.global_position=player.global_position+Vector3(1.5,0,3.4)
	enemy.rotation.y=atan2(-1.5,-3.4)
	enemy_anim=_anim(enemy)
	if after:
		var we:=field.find_children("*","WorldEnvironment",true,false)[0] as WorldEnvironment
		we.environment=LOOK.grade(we.environment)
		print("LOOK surfaces ally=",LOOK.apply_model(model,false,ALBEDO_SCALE)," enemy=",LOOK.apply_model(enemy,true,ALBEDO_SCALE))
	anim.play(IDLE)
	enemy_anim.play(IDLE)
	var layer=CanvasLayer.new()
	add_child(layer)
	label=Label.new()
	label.position=Vector2(24,20)
	label.add_theme_font_size_override("font_size",18)
	label.add_theme_color_override("font_outline_color",Color.BLACK)
	label.add_theme_constant_override("outline_size",6)
	label.text=mech.to_upper()+("  AFTER: look v2 (grade, AO, rim, enemy outline)" if after else "  BEFORE: current arena render")
	layer.add_child(label)
	camera.snap()

func _load_gorilla()->Node3D:
	var doc=GLTFDocument.new()
	var state=GLTFState.new()
	doc.append_from_file(MODEL,state)
	return doc.generate_scene(state,120.0)

func _anim(root:Node)->AnimationPlayer:
	var a=root.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
	for n in [IDLE,WALK]:a.get_animation(n).loop_mode=Animation.LOOP_LINEAR
	return a

func _process(delta):
	t+=delta
	var move=Vector3.ZERO
	if t>=1.2 and t<3.4:move=Vector3(1,0,0) if t<2.3 else Vector3(-1,0,0)
	if t>=1.2 and step==0:
		step=1
		anim.play(WALK,.13)
	if t>=3.4 and step==1:
		step=2
		anim.play(IDLE,.13)
	if t>=3.8 and step==2:
		step=3
		anim.play(SLAM,.06)
		enemy_anim.play(SWAT,.06)
	if t>=5.6 and step==3:
		step=4
		anim.play(IDLE,.2)
		enemy_anim.play(IDLE,.2)
	if t>=6.6:get_tree().quit()
	player.move_override=move
	if move.length_squared()>.01:
		model.rotation.y=lerp_angle(model.rotation.y,atan2(move.x,move.z),1.0-exp(-16.0*delta))
	elif step>=2:
		model.rotation.y=lerp_angle(model.rotation.y,PI,1.0-exp(-16.0*delta))
	camera.snap()
	_hide_aim.call_deferred()

func _hide_aim():
	for n in ["_aim_ring","_aim_line"]:
		var v=player.get(n)
		if v:v.visible=false
