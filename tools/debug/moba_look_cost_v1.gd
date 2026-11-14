extends Node3D
## MOBA look cost v1 (2026-11-09, look lane): 10 mechs (5 gorillas, 5 rhinos; half enemies) in the arena at the game
## camera, vsync off. Prints the average CPU and GPU render time over frames 90 to 390.
## Run windowed: --path . res://tools/debug/moba_look_cost_v1.tscn -- --look=base|grade|full
const LOOK=preload("res://scripts/moba3d/mech_look.gd")
const GORILLA="res://art/model_catalog/workspaces/gorilla_kit_v26.glb"
const RHINO="D:/dev/_scratch/rhino-donor-2026-11-08/armor-seam-polish-v38/rhino-polish-v38.glb"
var frame=0
var cpu=0.0
var gpu=0.0
var n=0
var mode="base"

func _ready():
	get_window().size=Vector2i(1280,720)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--look="):mode=a.substr(7)
	var field=load("res://scenes/moba3d/arena_blockout.tscn").instantiate()
	add_child(field)
	var player=field.get_node("Player")
	player.position=Vector3(0,0,3.5)
	player.move_override=Vector3.ZERO
	player.input_override=Vector2.ZERO
	for k in ["Sprite","Ring","Shadow"]:player.get_node(k).visible=false
	player.get_node("Kit").process_mode=Node.PROCESS_MODE_DISABLED
	var cam=field.get_node("Camera")
	cam.set_process(false)
	cam.yaw_degrees=180;cam.distance=6.2;cam.pitch_degrees=15;cam.look_height=1.6
	if mode!="base":
		var we:=field.find_children("*","WorldEnvironment",true,false)[0] as WorldEnvironment
		we.environment=LOOK.grade(we.environment)
	var states={}
	for i in 10:
		var path=GORILLA if i%2==0 else RHINO
		var doc=GLTFDocument.new();var st=GLTFState.new()
		doc.append_from_file(path,st)
		var m:Node3D=doc.generate_scene(st,120.0)
		field.add_child(m)
		m.global_position=player.global_position+Vector3(-4.0+2.0*(i%5),0,2.0+2.5*(i/5))
		var ap=m.find_children("*","AnimationPlayer",true,false)[0] as AnimationPlayer
		var idle="Gorilla_Idle_v25" if path==GORILLA else "idle"
		ap.get_animation(idle).loop_mode=Animation.LOOP_LINEAR
		ap.play(idle)
		if mode=="full":LOOK.apply_model(m,i>=5,1.0 if path==GORILLA else 0.55)
	cam.snap()
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(),true)

func _process(_d):
	frame+=1
	if frame>90 and frame<=390:
		var rid=get_viewport().get_viewport_rid()
		cpu+=RenderingServer.viewport_get_measured_render_time_cpu(rid)
		gpu+=RenderingServer.viewport_get_measured_render_time_gpu(rid)
		n+=1
	if frame==391:
		print("LOOK_COST mode=%s frames=%d cpu_ms=%.3f gpu_ms=%.3f draw_calls=%d" % [mode,n,cpu/n,gpu/n,Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)])
		get_tree().quit()
