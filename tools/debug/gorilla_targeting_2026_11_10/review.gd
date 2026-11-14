extends Node3D
const OUT="D:/dev/_scratch/gorilla/ability-indicators-2026-11-10/"
var actor: Node3D
var ally: Node3D
var second: Node3D
var enemy: Node3D
var kit: ApeKit
var targeter: Node3D
var camera: Camera3D
var tests: Array=[]
var uses: Array=[]
var interactive:=false
var heading: Label
func _ready() -> void:
	get_window().size=Vector2i(1280,720);get_window().content_scale_size=Vector2i(1280,720)
	interactive="--interactive" in OS.get_cmdline_user_args()
	var field: Node3D=load("res://scenes/moba3d/arena_blockout.tscn").instantiate();add_child(field)
	actor=field.get_node("Player");actor.position=Vector3.ZERO;actor.team="blue";actor.add_to_group("match_unit")
	ally=actor.duplicate();ally.name="AllyRhino";ally.bot=true;ally.position=Vector3(-2,0,-3.5);field.add_child(ally);ally.use_model("rhino")
	second=actor.duplicate();second.name="AllyGorilla";second.bot=true;second.position=Vector3(2.8,0,-4.2);field.add_child(second);second.use_model("gorilla")
	enemy=actor.duplicate();enemy.name="EnemyRhino";enemy.bot=true;enemy.team="red";enemy.position=Vector3(0,0,-2.1);field.add_child(enemy);enemy.use_model("rhino",true)
	actor.use_model("gorilla");kit=load("res://scripts/moba3d/arena_gorilla_kit.gd").install_arena(actor)
	kit.used.connect(func(s):uses.append(s);actor.cooldowns[s]=MatchRules.cooldown("gorilla",s))
	kit.shake_camera=false
	actor.input_override=null if interactive else Vector2.ZERO
	for unit in [ally,second,enemy]:unit.input_override=Vector2.ZERO
	camera=field.get_node("Camera");camera.yaw_degrees=0;camera.bounds=Vector2.ZERO;camera.snap()
	var layer:=CanvasLayer.new();add_child(layer);heading=Label.new();heading.position=Vector2(20,50);heading.add_theme_font_size_override("font_size",21);layer.add_child(heading)
	for unit in [actor,ally,second,enemy]:
		unit.add_to_group("match_unit")
		unit.team="red" if unit==enemy else "blue"
		var badge:=Label3D.new();badge.text=("GORILLA" if unit==actor else "ALLY / RHINO" if unit==ally else "ALLY / GORILLA" if unit==second else "ENEMY")
		badge.position.y=2.3;badge.font_size=30;badge.pixel_size=.007;unit.add_child(badge)
	await get_tree().process_frame;targeter=kit.targeting
	if interactive:
		heading.text="GORILLA / ABILITY INDICATORS\n1–4 select / hover ally / LMB cast / RMB cancel\nWASD move / Q–E camera"
	else:run.call_deferred()
func wait(seconds: float) -> void:await get_tree().create_timer(seconds).timeout
func check(label: String,passed: bool) -> void:
	tests.append({"check":label,"passed":passed});print("PASS " if passed else "FAIL ",label)
func aim(at: Vector3) -> void:
	targeter.point_override=at;actor.aim_screen_override=camera.unproject_position(at)
func reset() -> void:
	kit.abort_arena();actor.cooldowns.clear();actor.stunned=0;actor.alive=true;actor.busy=false
	for unit in [actor,ally,second]:
		var shield:=ApeKit.shield_on(unit)
		if shield!=null:shield.end()
func shot(title: String) -> void:heading.text="GORILLA / ABILITY INDICATORS\n"+title
func run() -> void:
	shot("ALLY HOVER / HEX SHIELD");aim(second.global_position);targeter.arm("1")
	check("arm consumes no cooldown or cast",uses.is_empty() and actor.cooldowns.is_empty())
	check("aim picks farther ally rather than nearest",targeter.hovered==second)
	check("preview suppresses held basic",not kit.basic_attack(enemy))
	await wait(2)
	shot("CONFIRM / SHIELD ARRIVES ON RELEASE");targeter.confirm()
	check("confirm consumes one shield slot",uses==["1"])
	check("no shield before release",ApeKit.shield_on(second)==null)
	await wait(.12);check("windup remains unshielded",ApeKit.shield_on(second)==null)
	await wait(.25);check("shield applies only to selected ally",ApeKit.shield_on(second)!=null and ApeKit.shield_on(ally)==null and ApeKit.shield_on(actor)==null)
	await wait(1.4);reset();await wait(.3)
	shot("SELF CAST / EMPTY AIM FALLBACK");aim(Vector3(4,0,1));targeter.arm("1")
	check("empty aim explicitly previews self",targeter.hovered==actor);await wait(1.3)
	targeter.confirm();await wait(.4);check("self shield applies",ApeKit.shield_on(actor)!=null)
	await wait(.8);reset();await wait(.3)
	shot("OUT OF RANGE / CONFIRM REFUSED");var saved:=second.position;second.position=Vector3(3,0,-6.5);aim(second.global_position);targeter.arm("1")
	check("out-of-range ally remains visible but invalid",targeter.hovered==second and not targeter.valid)
	var count:=uses.size();check("invalid confirm preserves cooldown",not targeter.confirm() and uses.size()==count and actor.cooldowns.is_empty())
	await wait(1.8);targeter.cancel();second.position=saved
	check("cancel clears targeting",targeter.slot=="")
	shot("GRAB / CONE + RECIPIENT");aim(enemy.global_position);targeter.arm("2");await wait(2);targeter.cancel()
	shot("SHIELD DRIVE / TRAVEL FOOTPRINT");aim(Vector3(5,0,-2));targeter.arm("3");await wait(2);targeter.cancel()
	shot("ULTIMATE / CAGE BOUNDARY + PANEL TICKS");targeter.arm("4");await wait(2);targeter.cancel()
	reset();aim(ally.global_position);targeter.arm("1");targeter.cancel();check("cancel does not consume a slot",actor.cooldowns.is_empty())
	# Release revalidation: a locked recipient can leave range or die during windup.
	reset();aim(ally.global_position);targeter.arm("1");targeter.confirm();ally.position=Vector3(-9,0,-3)
	await wait(.4);check("recipient leaving range before release gets no shield",ApeKit.shield_on(ally)==null);ally.position=Vector3(-2,0,-3.5)
	reset();aim(ally.global_position);targeter.arm("1");targeter.confirm();actor.stunned=1
	await wait(.4);check("interrupted cast gives no shield",ApeKit.shield_on(ally)==null)
	reset();aim(ally.global_position);targeter.arm("1");actor.stunned=1;await wait(.1);check("stun clears armed preview",targeter.slot=="")
	reset();targeter.point_override=null;actor.aim_screen_override=camera.unproject_position(ally.global_position+Vector3.UP*.9);targeter.arm("1")
	check("hover on body silhouette selects ally",targeter.hovered==ally)
	targeter.cancel();shot("REVIEW COMPLETE")
	reset();aim(ally.global_position);targeter.arm("1");targeter.confirm();ally.alive=false
	await wait(.4);check("recipient death before release gives no shield",ApeKit.shield_on(ally)==null);ally.alive=true
	reset();aim(enemy.global_position);targeter.arm("1");check("enemy cannot receive shield",targeter.hovered!=enemy);targeter.cancel()
	var blocker:=StaticBody3D.new();blocker.collision_layer=1
	var shape:=CollisionShape3D.new();var box:=BoxShape3D.new();box.size=Vector3(1.5,3,.4);shape.shape=box;blocker.add_child(shape);add_child(blocker);blocker.position=ally.position*.5+Vector3.UP
	await get_tree().physics_frame;await get_tree().physics_frame
	aim(ally.global_position);targeter.arm("1");check("wall blocks shield hover and commit",not targeter.valid and not targeter.confirm());targeter.cancel();blocker.queue_free()
	await get_tree().physics_frame;await get_tree().physics_frame
	reset();aim(ally.global_position)
	var key:=InputEventKey.new();key.keycode=KEY_1;key.physical_keycode=KEY_1;key.pressed=true;Input.parse_input_event(key)
	await get_tree().process_frame;await get_tree().process_frame
	check("number key enters targeting instead of casting",targeter.slot=="1" and actor.cooldowns.is_empty())
	var click:=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_LEFT;click.pressed=true;Input.parse_input_event(click)
	await get_tree().process_frame;check("confirmation click stays consumed while held",targeter.consume_click and targeter.slot=="")
	click=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_LEFT;click.pressed=false;Input.parse_input_event(click)
	await get_tree().process_frame;await get_tree().process_frame;check("release clears held basic suppression",not targeter.consume_click)
	await wait(.7);reset();targeter.arm("1")
	click=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_RIGHT;click.pressed=true;Input.parse_input_event(click)
	await get_tree().process_frame;check("right click cancels without cooldown",targeter.slot=="" and actor.cooldowns.is_empty())
	click=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_RIGHT;click.pressed=false;Input.parse_input_event(click)
	reset();aim(ally.global_position);targeter.arm("1")
	var menu_layer:=CanvasLayer.new();menu_layer.layer=12;add_child(menu_layer)
	var button:=Button.new();button.text="MENU";button.position=Vector2(10,10);button.size=Vector2(120,60);menu_layer.add_child(button)
	await get_tree().process_frame
	click=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_LEFT;click.pressed=true;click.position=Vector2(50,40);Input.parse_input_event(click)
	await get_tree().process_frame;await get_tree().process_frame
	check("GUI click does not confirm armed ability",targeter.slot=="1" and actor.cooldowns.is_empty())
	click=InputEventMouseButton.new();click.button_index=MOUSE_BUTTON_LEFT;click.pressed=false;click.position=Vector2(50,40);Input.parse_input_event(click)
	menu_layer.queue_free();targeter.cancel()
	var f:=FileAccess.open(OUT+"checks.json",FileAccess.WRITE);f.store_string(JSON.stringify(tests,"  "))
	print("TARGETING_REVIEW_COMPLETE ",tests.size())
	var code:=0 if tests.all(func(t):return t.passed) else 1
	get_child(0).queue_free();await get_tree().process_frame;await get_tree().process_frame
	MechModel3D.clear_templates();get_tree().quit(code)
func _exit_tree() -> void:MechModel3D.clear_templates()
