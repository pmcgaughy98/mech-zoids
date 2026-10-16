extends Node3D
## A 3D room stage (Claude, 2026-10-12). Loads a room built with Codex's Build 3D Game Rooms plugin from
## art/rooms/<room>/<room>.glb, stands the machine at the origin, and gives the room and the machine the model lab's
## metal finish and lights, so a room drops into the game looking the way the machine does, with no hand fixing.
## The room id is ROOM, or HT_ROOM overrides it. `tools/debug/room_check.gd` is the headless check for a room.
##
## Contract for a room .glb:
##   - metres; the machine's stand point is the origin; the floor's top face is at y = 0
##   - the machine faces +Z (Blender -Y), so the open side or bay door faces +Z and the camera looks in from +Z
##   - plain materials with base colours (baked textures optional); the finish is applied here
##   - under 40,000 triangles for the whole room
const ROOM := "test_box"
const MACHINE := "ape_l"
const ModelLab := preload("res://scripts/scenes/model_lab_3d.gd")

var room: Node3D
var model: Node3D
var finish_count := 0
var room_id := ROOM
var runtime_config: Dictionary = {}
var _stage_window: Window
var _previous_scale_mode: int
var _previous_scale_size: Vector2i


func _ready() -> void:
	if OS.get_environment("HT_ROOM") != "":
		room_id = OS.get_environment("HT_ROOM")
	var config_path := "res://art/rooms/%s/%s.runtime.json" % [room_id, room_id]
	if FileAccess.file_exists(config_path):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(config_path))
		if parsed is Dictionary:
			runtime_config = parsed
	if runtime_config.has("viewport"):
		var size: Array = runtime_config["viewport"]
		_stage_window = get_window()
		_previous_scale_mode = _stage_window.content_scale_mode
		_previous_scale_size = _stage_window.content_scale_size
		_stage_window.content_scale_mode = Window.CONTENT_SCALE_MODE_VIEWPORT
		_stage_window.content_scale_size = Vector2i(size[0], size[1])
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -35, 0)
	sun.shadow_enabled = true
	add_child(sun)
	var room_path := "res://art/rooms/%s/%s.glb" % [room_id, room_id]
	if ResourceLoader.exists(room_path):
		room = (load(room_path) as PackedScene).instantiate()
		add_child(room)
		for mi in room.find_children("ceiling*", "MeshInstance3D", true, false):   # the sun still reaches inside
			(mi as MeshInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var fixtures: Array = runtime_config.get("fixtures", [])
		if fixtures.is_empty():
			for x in [-4.5, 4.5]:
				fixtures.append({"position": [x, 6.0, 1.5], "color": [1.0, 210.0 / 255.0, 160.0 / 255.0], "energy": 3.0, "range": 16.0})
		for fixture: Dictionary in fixtures:
			var lamp := OmniLight3D.new()
			var pos: Array = fixture["position"]
			var rgb: Array = fixture["color"]
			lamp.position = Vector3(pos[0], pos[1], pos[2])
			lamp.light_color = Color(rgb[0], rgb[1], rgb[2])
			lamp.light_energy = fixture["energy"]
			lamp.omni_range = fixture["range"]
			lamp.shadow_enabled = true
			add_child(lamp)
	model = (load("res://art/machines/%s/%s.glb" % [MACHINE, MACHINE]) as PackedScene).instantiate()
	add_child(model)
	finish_count = ModelLab.metal_finish(self, env.environment, sun)   # room and machine alike
	if room != null and not runtime_config.is_empty():
		for mi in room.find_children("*", "MeshInstance3D", true, false):
			for i in (mi as MeshInstance3D).mesh.get_surface_count():
				var material := (mi as MeshInstance3D).get_active_material(i) as StandardMaterial3D
				if material:
					material.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
	var players := model.find_children("*", "AnimationPlayer", true, false)
	if not players.is_empty() and (players[0] as AnimationPlayer).has_animation("idle"):
		(players[0] as AnimationPlayer).get_animation("idle").loop_mode = Animation.LOOP_LINEAR
		(players[0] as AnimationPlayer).play("idle")
	var cam := Camera3D.new()   # the game's view of the base: high three-quarter, looking in from the open side
	cam.fov = 40.0
	cam.position = Vector3(5.5, 6.5, 9.0)
	var camera_config: Dictionary = runtime_config.get("camera", {})
	var camera_target := Vector3(0, 1.2, 0)
	if not camera_config.is_empty():
		var pos: Array = camera_config["position"]
		var target: Array = camera_config["target"]
		cam.position = Vector3(pos[0], pos[1], pos[2])
		camera_target = Vector3(target[0], target[1], target[2])
		cam.fov = camera_config["verticalFovDegrees"]
	add_child(cam)
	cam.look_at(camera_target)
	cam.current = true


func _exit_tree() -> void:
	if is_instance_valid(_stage_window):
		_stage_window.content_scale_mode = _previous_scale_mode
		_stage_window.content_scale_size = _previous_scale_size


## Triangles in every mesh under `root`.
static func triangle_count(root: Node) -> int:
	var n := 0
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m: Mesh = (mi as MeshInstance3D).mesh
		if m:
			n += m.get_faces().size() / 3
	return n


## World-space bounds of every mesh under `root`.
static func bounds(root: Node) -> AABB:
	var box := AABB()
	var first := true
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if m.mesh == null:
			continue
		var b: AABB = m.global_transform * m.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box
