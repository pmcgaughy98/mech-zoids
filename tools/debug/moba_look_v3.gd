extends Node3D
const LOOK_FX := preload("res://scripts/moba3d/look_fx.gd")
## MOBA look v3 (2026-11-09, look lane): rim built into the body material (no extra draw), outline only on the
## targeted enemy, no SSAO. From v2: v1 plus --mech=rhino (the rhino lane's v38 scratch GLB, read only) and the
## smoothed-normal outline. Same shot: game camera behind the mech, an enemy copy ahead.
## Run windowed:  --path . --script res://tools/debug/moba_look_v3.tscn -- --mech=rhino --look=after   (or --look=before)
## Add --write-movie <file.avi> --fixed-fps 30 to record. Arena, GLB and shared shaders are not edited:
## the grade is a runtime copy of the arena's Environment, the rim/outline go on duplicated materials.
const MECHS={
	"garena":{"model":"res://art/arena_models/gorilla.glb","idle":"Gorilla_Idle","walk":"Gorilla_Walk","attack":"Gorilla_Slam","enemy_attack":"Gorilla_Swat_Left","albedo_scale":1.0},  # 2026-11-12 registered merged gorilla
	"gorilla":{"model":"res://art/model_catalog/workspaces/gorilla_kit_v26.glb","idle":"Gorilla_Idle_v25","walk":"Gorilla_Walk_v25","attack":"Gorilla_Slam_v25","enemy_attack":"Gorilla_Swat_Left_v25","albedo_scale":1.0},
	"hippo10":{"model":"D:/dev/_scratch/hippo-3d/out/hippo-r10-look.glb","idle":"Hippo_Idle","walk":"Hippo_Walk","attack":"Hippo_Bite","enemy_attack":"Hippo_Bite","albedo_scale":1.0},  # dark window glass
	"hippo9":{"model":"D:/dev/_scratch/hippo-3d/out/hippo-r9-look.glb","idle":"Hippo_Idle","walk":"Hippo_Walk","attack":"Hippo_Bite","enemy_attack":"Hippo_Bite","albedo_scale":1.0},  # window core band, conduits x0.6
	"hippo8":{"model":"D:/dev/_scratch/hippo-3d/out/hippo-r8-look.glb","idle":"Hippo_Idle","walk":"Hippo_Walk","attack":"Hippo_Bite","enemy_attack":"Hippo_Bite","albedo_scale":1.0},  # trim x0.73/x0.90 + Hippo glow
	"hippo":{"model":"res://art/arena_models/hippo.glb","idle":"Hippo_Idle","walk":"Hippo_Walk","attack":"Hippo_Bite","enemy_attack":"Hippo_Bite","albedo_scale":1.0},  # 2026-11-11 hippo-3d registered body
	"rhino48":{"model":"D:/dev/_scratch/rhino-donor-2026-11-08/game-export-v48/rhino_game_v48.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":1.0},  # leg under-armour sleeves
	"rhino46":{"model":"D:/dev/_scratch/rhino-donor-2026-11-08/game-export-v46/rhino_game_v46.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":1.0},  # socket liners flipped outward
	"rhino45":{"model":"D:/dev/_scratch/rhino-donor-2026-11-08/game-export-v45/rhino_game_v45.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":1.0},  # socket liners darkened
	"rhino44":{"model":"D:/dev/_scratch/rhino-donor-2026-11-08/game-export-v44/rhino_game_v44.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":1.0},  # 2026-11-10: one-mesh export, colour trim baked in by the rhino lane
	"rhino":{"model":"res://art/arena_models/rhino.glb","idle":"idle","walk":"walk","attack":"horn_attack","enemy_attack":"horn_attack","albedo_scale":1.0},  # 2026-11-11 registered v52; the 0.7 runtime trim for v38 removed (colour now baked in by the rhino lane)
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
	var mech="garena" if "--mech=garena" in OS.get_cmdline_user_args() else "hippo10" if "--mech=hippo10" in OS.get_cmdline_user_args() else "hippo9" if "--mech=hippo9" in OS.get_cmdline_user_args() else "hippo8" if "--mech=hippo8" in OS.get_cmdline_user_args() else "hippo" if "--mech=hippo" in OS.get_cmdline_user_args() else "rhino48" if "--mech=rhino48" in OS.get_cmdline_user_args() else "rhino46" if "--mech=rhino46" in OS.get_cmdline_user_args() else "rhino45" if "--mech=rhino45" in OS.get_cmdline_user_args() else "rhino44" if "--mech=rhino44" in OS.get_cmdline_user_args() else ("rhino" if "--mech=rhino" in OS.get_cmdline_user_args() else "gorilla")
	var c:Dictionary=MECHS[mech]
	MODEL=c.model;IDLE=c.idle;WALK=c.walk;SLAM=c.attack;SWAT=c.enemy_attack;ALBEDO_SCALE=c.albedo_scale
	for a in OS.get_cmdline_user_args():  # --model=<absolute GLB path>: measure a scratch candidate with this entry's clips
		if a.begins_with("--model="):MODEL=a.substr(8)
	var field=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	field.look_grade=false  # the arena now applies the grade itself (map lane); off here so "before" is a true before and "after" comes from grade() once
	add_child(field)
	player=field.get_node("Player")
	player.position=Vector3(0,0,3.5)
	player.move_speed=3.5
	player.input_override=Vector2.ZERO
	player.move_override=Vector3.ZERO
	var fx_test="--fx" in OS.get_cmdline_user_args()
	for n in (["Sprite"] if fx_test else ["Sprite","Ring","Shadow"]):player.get_node(n).visible=false
	LOOK_FX.off="--pixelfx" in OS.get_cmdline_user_args()
	if LOOK_FX.off:  # the old 64 px ring and shadow, kept in scratch, for the before shot
		for n in ["Ring","Shadow"]:
			var mi:MeshInstance3D=player.get_node(n)
			var m0=(mi.mesh as PrimitiveMesh).material
			if not m0 is StandardMaterial3D:continue  # already a shader (not a pixel texture)
			var m:StandardMaterial3D=m0.duplicate()
			m.albedo_texture=ImageTexture.create_from_image(Image.load_from_file("D:/dev/_scratch/moba-look/smooth-fx/originals/%s.png"%n.to_lower()))
			m.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST
			mi.material_override=m
	if fx_test:set_meta("fx_test",true)
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
		print("LOOK surfaces ally=",LOOK.apply_model(model,false,ALBEDO_SCALE)," enemy=",LOOK.apply_model(enemy,true,ALBEDO_SCALE,true))  # true: the targeted enemy
		if "--finish=0" in OS.get_cmdline_user_args():  # A/B for the 2026-11-10 finish masks
			for n in [model,enemy]:
				for mi in n.find_children("*","MeshInstance3D",true,false):
					for s in mi.mesh.get_surface_count():
						var mm=mi.get_active_material(s)
						if mm is ShaderMaterial:mm.set_shader_parameter("finish",0.0)
	anim.play(IDLE)
	enemy_anim.play(IDLE)
	var layer=CanvasLayer.new()
	add_child(layer)
	label=Label.new()
	label.position=Vector2(24,20)
	label.add_theme_font_size_override("font_size",18)
	label.add_theme_color_override("font_outline_color",Color.BLACK)
	label.add_theme_constant_override("outline_size",6)
	label.text=mech.to_upper()+("  AFTER: look v3 (grade, rim in material, target outline)" if after else "  BEFORE: current arena render")
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
	if has_meta("fx_test") and enemy!=null:
		var ft:float=get_meta("fx_t",0.0)+delta
		set_meta("fx_t",ft)
		var k:int=get_meta("fx_k",0)
		if ft>0.5+k*0.8:
			set_meta("fx_k",k+1)
			var d:Vector3=(enemy.global_position-player.global_position).normalized()
			Fx3D.spawn(self,"hit_spark" if k%2==0 else "deflect_spark",enemy.global_position-d*0.7+Vector3.UP*1.1,0.3)
		if not has_meta("fx_stars") and ft>1.0:
			set_meta("fx_stars",true)
			Fx3D.spawn(self,"stun_loop",enemy.global_position+Vector3.UP*2.3,0.0,true)
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
