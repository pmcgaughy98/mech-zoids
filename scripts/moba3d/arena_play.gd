extends Node3D
## The playable arena (Claude, 2026-11-04, game feel lane; Preston: "Hook up the map and game feel"). The map lane's
## blockout (scenes/moba3d/arena_blockout.tscn, theirs, never edited here) with its Player moved to the blue spawn,
## enemy training dummies standing in blue's lane past the tower, and walls that stop the machines (ArenaMotion).
## Since 2026-11-04 it is a 3 v 3 match (MatchDirector; Mech-Zoids' brief for Preston's "sel-out moba map"): minion waves,
## towers, cores, jungle camps, respawn, recall, bots and a HUD. Every number is a placeholder in MatchRules.
## Keys: WASD or arrows walk, Q and E turn the camera, 1-4 the kit, Space or left mouse the stand-in attack, B recall,
## Tab cycles the test roster, F8 selects directly, Enter after the match plays again.
## "-- --sandbox" brings back the earlier test field (dummies in the lane; F has every dummy within 20 m fire a test
## shot); "-- --demo" is its scripted walk-through; "-- --push-demo" records two waves and a tower push.

const RHINO_FRAMES := preload("res://art/machines/rhino/rhino_frames.tres")
## Where the enemy dummies stand: blue's lane runs from its tower (0, 40) toward (-7, 20) in arena_blockout.gd's LANE.
## Hand-placed until the map lane's named points land.
const LANE_DUMMIES := [Vector3(-2.0, 0, 31.0), Vector3(-4.6, 0, 27.0), Vector3(-1.0, 0, 25.5), Vector3(-6.5, 0, 22.5)]
const VOLLEY_RANGE := 20.0
var MACHINES: Array = ["rhino", "gorilla", "fennec", "wolf", "squirrel", "hummingbird", "lobster"]
const ROSTER=preload("res://scripts/moba3d/arena_roster.gd")
var roster_menu: Control
func _exit_tree() -> void:MechModel3D.clear_templates()
const CAMERA_EDGE := 0.5 ## the camera stays this far inside the map edge (map lane's 41.5 x 77.5)

var player: Node3D
var machine := "rhino"
var director: MatchDirector
var hud: MatchHud
var sandbox := false ## the earlier test field instead of the match; checks set it before adding the scene

@onready var arena: Node3D = $Arena


func _ready() -> void:
	for kind in ROSTER.kinds():
		if not MACHINES.has(kind):MACHINES.append(kind)
	_build_roster_menu.call_deferred()
	player = arena.get_node("Player")
	player.global_position = spawn_point("blue")
	var k: Dictionary = arena.get_script().get_script_constant_map()
	var cam := arena.get_node_or_null("Camera")
	if cam != null and "bounds" in cam and k.has("HALF_X"):
		cam.bounds = Vector2(k["HALF_X"] - CAMERA_EDGE, k["HALF_Z"] - CAMERA_EDGE)
	player.facing = Vector3(0, 0, -1)  # down the lane, away from the chase camera
	var args := OS.get_cmdline_user_args()
	if "--cam-angle-set-test" in args:  # the second test: a full drone set, tower and wall behind, the HUD's bar
		var o2 := "user://cam_angle_set_test"
		var dv := "res://docs/art/moba/minion_s/take-a/views_cam30"
		var wh := "drone"
		for a in args:
			if a.begins_with("--out="):
				o2 = a.trim_prefix("--out=")
			elif a.begins_with("--drone-views="):
				dv = a.trim_prefix("--drone-views=")
			elif a.begins_with("--who="):
				wh = a.trim_prefix("--who=")
		var st := CamAngleSetTest.new()
		st.name = "CamAngleSetTest"
		add_child(st)
		st.setup_set(self, o2, dv, wh)
		return
	if "--cam-angle-test" in args:  # Mech-Zoids' camera-angle sprite test: stand-ins only, no match (cam_angle_test.gd)
		var o := "user://cam_angle_test"
		for a in args:
			if a.begins_with("--out="):
				o = a.trim_prefix("--out=")
		var t := CamAngleTest.new()
		t.name = "CamAngleTest"
		add_child(t)
		t.setup(self, o)
		return
	if "--gate-clip-test" in args:  # the fennec's small gate at the game camera, no match (gate_clip_test.gd)
		var og := "user://gate_clip_test"
		for a in args:
			if a.begins_with("--out="):
				og = a.trim_prefix("--out=")
		var gt := GateClipTest.new()
		gt.name = "GateClipTest"
		add_child(gt)
		gt.setup(self, og)
		return
	if sandbox or "--demo" in args or "--sandbox" in args:  # the earlier test field: dummies in the lane, no match
		for p in LANE_DUMMIES:
			var d := TrainingDummy.new()
			add_child(d)
			d.global_position = p
		if "--demo" in args:
			_demo.call_deferred()
		return
	_start_match()
	if get_tree().get_script() == null and not "--rhino" in args:  # normal play starts on the 3D gorilla (sprites are scrapped,
		set_machine("gorilla")  # Preston 2026-11-09). The bots were copied from the rhino inside _start_match, as before. A test
	if "--push-demo" in args:  # script keeps the rhino its checks were written for; it calls set_machine("gorilla") for the 3D one.
		_push_demo.call_deferred()


## Switches the player to machine name (one of MACHINES) the way Tab does. Game feel lane, 2026-11-09.
func set_machine(which: String) -> void:
	if not MACHINES.has(which) or which == machine:
		return
	var before := machine
	var prev: String = MACHINES[(MACHINES.find(which) - 1 + MACHINES.size()) % MACHINES.size()]
	machine = prev
	swap()
	if machine == prev:  # swap() refused: the kit is mid-ability
		machine = before


func _start_match() -> void:
	director = MatchDirector.new()
	director.name = "Match"
	director.add_to_group("match_director")
	add_child(director)
	director.setup(arena, player)
	hud = MatchHud.new()
	hud.name = "Hud"
	hud.director = director
	add_child(hud)


## The basic attack. A kit with its own basic_attack() (the squirrel's darts) aims it itself, at the mouse; the director
## still keeps the gates and the cooldown. Otherwise the stand-in at the best target in reach, things in front first.
func player_attack() -> void:
	if director == null or not player.alive:
		return
	var kit := player.get_node_or_null("Kit")
	if kit != null and kit.has_method("basic_attack"):
		director.basic_attack(player, null)
		return
	var t := director.pick_target(player, MatchRules.basic_range, player.facing)
	if t != null:
		director.basic_attack(player, t)


## The team's spawn: the map lane's marker (Arena/Markers/BlueSpawn, RedSpawn), else its features list.
func spawn_point(team: String) -> Vector3:
	var m := arena.get_node_or_null("Markers/%sSpawn" % team.capitalize()) as Node3D
	if m != null:
		return Vector3(m.global_position.x, 0.0, m.global_position.z)
	for f in arena.get("features"):
		if f.get("name") == team + " spawn":
			var p: Vector2 = f["p"]
			return Vector3(p.x, 0.0, p.y)
	return Vector3(0, 0, 70) if team == "blue" else Vector3(0, 0, -70)


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	match k.physical_keycode:
		KEY_TAB:
			if player.alive:
				swap()
			get_viewport().set_input_as_handled()
		KEY_F8:
			roster_menu.visible=not roster_menu.visible
			get_viewport().set_input_as_handled()
		KEY_F:
			if director == null:
				enemy_volley()
		KEY_B:
			if director != null:
				director.start_recall(player)
		KEY_ENTER, KEY_KP_ENTER:
			if director != null and director.winner != "":
				get_tree().reload_current_scene()


## The next machine in MACHINES: rhino, gorilla, fennec, wolf, squirrel, hummingbird, lobster, and round again. Not mid-ability.
func swap() -> void:
	var kit := player.get_node_or_null("Kit")
	var doing: Variant = kit.get("current") if kit != null else null  # a kit without `current` (the squirrel) counts as idle
	if doing != null and doing != "":
		return
	if not player.has_meta("base_canvas"):  # the rhino's canvas, from before the first swap
		player.set_meta("base_canvas", [player.sprite.canvas_height, player.sprite.feet_edge_row])
	var base: Array = player.get_meta("base_canvas")
	player.sprite.canvas_height = base[0]  # each install sets its own; a kit that sets none (the rhino's) gets 192 / 161 back,
	player.sprite.feet_edge_row = base[1]  # not the squirrel's 160 / 141 (it drew the rhino at 0.83)
	machine = MACHINES[(MACHINES.find(machine) + 1) % MACHINES.size()]
	match machine:
		"gorilla":
			load("res://scripts/moba3d/arena_gorilla_kit.gd").install_arena(player)
		"fennec":
			FennecKit.install(player)
		"wolf":
			WolfKit.install(player)
		"squirrel":
			SquirrelKit.install(player)
		"hummingbird":
			load("res://scripts/moba3d/hummingbird_kit.gd").install(player)  # no class_name on that kit
		"lobster":
			load("res://scripts/moba3d/lobster_kit.gd").install(player)  # by path: LobsterKit may not be in the class cache yet
		"hippo","kangaroo","falcon","shoebill":
			load("res://scripts/moba3d/"+machine+"_kit.gd").install(player)
		"pangolin":  # slice 1 of the kit redo: the iron ball on slot 2 (game feel lane, 2026-11-12)
			load("res://scripts/moba3d/pangolin_kit.gd").install(player)
			player.sprite.size_class=ROSTER.profile(machine).get("size_class","M")
		"bison":  # the Whistle Stop kit (game feel lane, 2026-11-14; Preston: "Whistle Stop", "Yes, rebuild it")
			load("res://scripts/moba3d/bison_kit.gd").install(player)
			player.sprite.size_class=ROSTER.profile(machine).get("size_class","L")
		"rhino":
			_install_rhino()
		_:
			load("res://scripts/moba3d/arena_base_kit.gd").install(player)
			player.sprite.size_class=ROSTER.profile(machine).get("size_class","M")
	player.apply_size_class()
	player.use_model(machine)  # the rigged 3D body for a machine that has one, else its sprite (game feel lane, 2026-11-09)
	if director!=null and director.recalls.has(player):director._end_recall(player,false)
	if roster_menu!=null:roster_menu.visible=false


func _build_roster_menu() -> void:
	var layer:=CanvasLayer.new();layer.layer=12;add_child(layer)
	var panel:=PanelContainer.new();roster_menu=panel;panel.visible=false
	panel.position=Vector2(8,8);panel.size=Vector2(304,155);layer.add_child(panel)
	var column:=VBoxContainer.new();panel.add_child(column)
	var heading:=Label.new();heading.text="TEST ROSTER   /   F8 CLOSE";heading.add_theme_font_size_override("font_size",9);column.add_child(heading)
	var scroll:=ScrollContainer.new();scroll.custom_minimum_size=Vector2(290,125);column.add_child(scroll)
	var grid:=GridContainer.new();grid.columns=3;scroll.add_child(grid)
	for kind in MACHINES:
		var button:=Button.new();button.text=String(kind).replace("_"," ").capitalize();button.custom_minimum_size=Vector2(91,15);button.add_theme_font_size_override("font_size",7)
		button.pressed.connect(func():set_machine(kind))
		grid.add_child(button)


func _install_rhino() -> void:
	var old := player.get_node_or_null("Kit")
	if old is ApeKit and is_instance_valid(old._aura):
		old._aura.queue_free()  # the silverback ring is the gorilla's
	var spr: DirectionalSprite3D = player.get_node("Sprite")
	spr.stop_action()
	spr.sprite_frames = RHINO_FRAMES
	spr.size_class = "L"
	spr.play(StringName("idle_" + spr.view))
	if old != null:
		player.remove_child(old)
		old.queue_free()
	var kit := RhinoKit.new()
	kit.name = "Kit"
	player.add_child(kit)


## Every enemy dummy in range fires a test shot at the machine.
func enemy_volley() -> void:
	for d in get_tree().get_nodes_in_group("kit_target"):
		if d.has_method("fire_at") and d.global_position.distance_to(player.global_position) <= VOLLEY_RANGE:
			d.fire_at(player.global_position, player)


# ---- the scripted walk-through, for recording -------------------------------------------------------------------

var _t := 0.0


func _process(delta: float) -> void:
	_t += delta
	if roster_menu!=null and roster_menu.visible:return
	if director != null and not player.bot 			and (Input.is_physical_key_pressed(KEY_SPACE) or Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT)):
		player_attack()


func _at(t: float) -> void:
	while _t < t:
		await get_tree().process_frame


func _demo() -> void:
	for d in get_tree().get_nodes_in_group("kit_target"):
		d.queue_free()
	player.global_position = Vector3(-6, 0, 0)  # in the plaza
	var cam := arena.get_node_or_null("Camera")
	if cam != null and cam.has_method("snap"):
		cam.snap()
	# Into the plaza wall at 45 degrees: it stops against it and slides along.
	player.move_override = Vector3(-1, 0, -1).normalized()
	await _at(3.8)
	player.move_override = null
	var p: Vector3 = player.global_position
	var out := Vector3(p.x, 0, p.z).normalized()  # from the plaza's middle toward the wall
	# The rhino's horn toss throws a dummy over its back, into the wall: it stops there.
	player.facing = -out
	_dummy(p - out * 1.3)
	await _at(4.3)
	player.get_node("Kit").horn_toss()
	await _at(6.3)
	swap()  # Tab: the gorilla
	player.move_override = -out
	await _at(7.1)
	player.move_override = null
	player.facing = out
	await _at(7.3)
	player.get_node("Kit").bound()  # at the wall: it lands against it
	await _at(8.9)
	# Back toward the middle, then the hex dome: an enemy can't walk in or out, an ally can, enemy shots stop.
	player.move_override = -out
	await _at(10.3)
	player.move_override = null
	var c: Vector3 = player.global_position
	var side := out.cross(Vector3.UP)
	var e_in := _dummy(c - out * 1.6 + side * 0.8)
	var e_out := _dummy(c - out * 5.5)
	var ally := _dummy(c + side * 1.4)
	ApeKit.make_ally(ally)
	player.facing = -out
	await _at(10.6)
	player.get_node("Kit").hex_dome()
	await _at(11.8)
	e_out.walk_to(c, 1.2)
	e_in.walk_to(c - out * 6.0, 1.0)
	ally.walk_to(c + side * 6.0, 1.4)
	for i in 3:
		await _at(13.2 + 0.6 * i)
		e_in.fire_at(c - out * 9.0 + side * (1.5 * i - 1.5))
		e_out.fire_at(c, player)
	await _at(17.0)
	get_tree().quit()


func _dummy(p: Vector3) -> Node3D:
	var d := TrainingDummy.new()
	add_child(d)
	d.global_position = p
	return d


## The recording for Mech-Zoids (2026-11-04): two waves meet at the plaza and the red tower takes a push. The player's
## machine plays itself (a MatchBot), so the chase camera follows the fight, and red's three bots wait at their base so
## the push reaches the tower in one take. Run with "-- --push-demo"; the first wave leaves at 1 s instead of 5.
func _push_demo() -> void:
	MatchRules.first_wave_at = 1.0
	player.bot = true
	var b := MatchBot.new()
	b.name = "Bot"
	b.director = director
	player.add_child(b)
	for m: Node3D in director.machines:
		if m.team == "red":
			m.get_node("Bot").hold = true
	var limit := float(OS.get_environment("PUSH_DEMO_SECONDS")) if OS.get_environment("PUSH_DEMO_SECONDS") != "" else 70.0
	await _at(limit)
	get_tree().quit()
