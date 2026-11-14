extends Node3D
const OUT="D:/dev/_scratch/rhino-painted-fx-2026-11-10/"
var actor: Node3D
var enemy: Node3D
var kit: RhinoKit
var fx: Node3D
var camera: Camera3D
var heading: Label
var tests: Array=[]
var interactive:=false
var field: Node3D
func _ready() -> void:
 get_window().size=Vector2i(1280,720);get_window().content_scale_size=Vector2i(1280,720)
 interactive="--interactive" in OS.get_cmdline_user_args()
 field=load("res://scenes/moba3d/arena_blockout.tscn").instantiate();add_child(field)
 actor=field.get_node("Player");actor.position=Vector3.ZERO;actor.team="blue";actor.input_override=Vector2.ZERO;actor.move_override=Vector3.ZERO
 actor.add_to_group("match_unit");actor.use_model("rhino");actor.max_hp=10000;actor.hp=10000
 enemy=actor.duplicate();enemy.name="EnemyRhino";enemy.team="red";enemy.bot=true;enemy.position=Vector3(0,0,-3.1);field.add_child(enemy);enemy.use_model("rhino",true);enemy.max_hp=10000;enemy.hp=10000;enemy.add_to_group("match_unit")
 kit=actor.get_node("Kit")
 fx=load("res://scripts/moba3d/rhino_painted_fx.gd").new();fx.name="RhinoPaintedFX";kit.add_child(fx);fx.setup(kit,actor)
 camera=field.get_node("Camera");camera.yaw_degrees=0;camera.bounds=Vector2.ZERO;camera.snap()
 var layer:=CanvasLayer.new();add_child(layer);heading=Label.new();heading.position=Vector2(24,28);heading.add_theme_font_size_override("font_size",22);layer.add_child(heading)
 if interactive:
  actor.input_override=null;actor.move_override=null
  shot("RHINO / PAINTED SEISMIC EFFECTS / 1–4 abilities / WASD")
 else:run.call_deferred()
func shot(text: String) -> void:heading.text=text+"\nACTUAL KIT EVENTS / CURRENT REGISTERED RHINO / ORIGINAL MECHANICS"
func wait(seconds: float) -> void:await get_tree().create_timer(seconds).timeout
func capture(name: String) -> void:
 if DisplayServer.get_name()=="headless":return
 await RenderingServer.frame_post_draw
 get_viewport().get_texture().get_image().save_png(OUT+name+".png")
func check(label: String,value: bool) -> void:tests.append({"check":label,"passed":value});print("PASS " if value else "FAIL ",label)
func count(name: String) -> int:return fx.event_log.filter(func(row):return row.name==name).size()
func reset() -> void:
 actor.position=Vector3.ZERO;actor.facing=Vector3.FORWARD;actor.body.snap_facing(actor.facing);actor.stunned=0;actor.cooldowns.clear()
 enemy.position=Vector3(3.2,0,-1.2);enemy.hp=10000;enemy.alive=true;enemy.stunned=0;enemy.slowed=0
 enemy.facing=(actor.position-enemy.position).normalized();enemy.body.snap_facing(enemy.facing)
func idle(limit:=5.0) -> void:
 var time:=0.0
 while kit.current!="" and time<limit:await get_tree().process_frame;time+=get_process_delta_time()
 check("action finished without art changing kit state",kit.current=="")
func run() -> void:
 await wait(.7);reset()
 check("current registered body has the horn chain",actor.body.has_clip("horn_hook"))
 check("atlas loaded RGBA dimensions",fx.texture.get_width()==1774 and fx.texture.get_height()==887)
 shot("HORN CHAIN / THREE CONTACT-DRIVEN SWEEPS / GAME CAMERA")
 var before: float=enemy.hp
 for i in 3:
  enemy.position=Vector3(0,0,-3.1);enemy.facing=Vector3.BACK;enemy.body.snap_facing(enemy.facing);enemy.stunned=0
  check("basic accepted",kit.basic_attack(enemy));await idle();await wait(.12)
 check("three animation-contact arcs",count("basic_arc")==3)
 check("three confirmed impact hooks",count("confirmed_basic_hit")==3)
 check("real target takes basic damage",enemy.hp<before)
 reset();camera.distance=9;camera.pitch_degrees=20;camera.look_height=1.3;camera.yaw_degrees=35;camera.snap()
 enemy.position=Vector3(0,0,-3.1);shot("HORN TOSS / CHARGE WAKE / CATCH / LANDING")
 kit.horn_toss();await idle();await wait(.9)
 check("one dash cast",count("toss_travel")==1)
 check("one confirmed catch",count("toss_catch")==1)
 check("one landing effect",count("toss_land")==1)
 check("travel wake clears",not fx.wake.visible)
 reset();shot("SEISMIC PISTONS / FIRST SLAM + FOUR PRESSURE PULSES")
 kit.ground_pound();await wait(.53);await capture("painted-pound");await idle();await wait(.8)
 check("one initial slam",count("pound_slam")==1)
 check("four actual stomp cues",count("tremor_stomp")==4)
 reset();shot("BRACE / ARMOR CREST / POUND WHILE PLANTED")
 kit.brace();await wait(.9)
 check("brace visual starts on planted state",kit.braced and fx.brace_mark.visible)
 check("brace crest shows",fx.brace_face.visible);await capture("painted-brace")
 kit.ground_pound();await idle();await wait(1.2)
 check("brace art clears after duration",not kit.braced and not fx.brace_face.visible)
 reset();enemy.position=Vector3(.4,0,-4);shot("STAMPEDE / TRAVEL WAKE / FINALE GROUND RUPTURE")
 kit.stampede();await wait(.3);check("stampede has travel art",fx.wake.visible)
 await idle(6);await wait(2.7)
 check("one stampede finale",count("finale_slam")==1)
 check("transient art expires",fx.live.is_empty() and not fx.wake.visible)
 reset();shot("INTERRUPTION CHECK / NO FALSE SLAM")
 var slams:=count("pound_slam");kit.ground_pound();await wait(.1);actor.body.stop_action();await idle();await wait(.7)
 check("stopped windup produces no slam art",count("pound_slam")==slams)
 fx.burst(1,actor.global_position,Vector2.ONE,1,.5);actor.alive=false;await get_tree().process_frame;await get_tree().process_frame
 check("death clears all transient effects",fx.live.is_empty() and not fx.brace_face.visible)
 var file:=FileAccess.open(OUT+"checks.json",FileAccess.WRITE);file.store_string(JSON.stringify({"checks":tests,"events":fx.event_log},"  "))
 print("RHINO_PAINTED_REVIEW_COMPLETE ",tests.size())
 field.queue_free();await get_tree().process_frame;await get_tree().process_frame;MechModel3D.clear_templates()
 get_tree().quit(0 if tests.all(func(row):return row.passed) else 1)
