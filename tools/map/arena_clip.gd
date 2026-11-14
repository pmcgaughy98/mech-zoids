extends SceneTree
## A short phone-size clip from the chase camera. Map design lane, 2026-11-04 (quality pass). Needs a window:
## Godot --fixed-fps 30 --path . -s res://tools/map/arena_clip.gd -- <frames folder>
## The rhino rides from blue's spawn down the lane to the plaza as a blue vision source (12 m), so the fog of war
## shows, and the camera turns with it. Saves one JPEG per frame into the folder; ffmpeg makes the mp4. Moves the
## rhino by hand, so it shows the map, not game feel's movement. Edits nothing.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const LANE_PATH := [Vector2(0, 69), Vector2(4, 58), Vector2(4, 46), Vector2(4, 38), Vector2(-4, 30), Vector2(-7.5, 20), Vector2(-3, 8),
	Vector2(2, -1)]
const TOWER_PATH := [Vector2(2, -6), Vector2(7, -19), Vector2(5, -28), Vector2(4.2, -33)] ## arg "tower": up red's lane
const SPEED := 6.5 ## metres a second; the path keeps 4 m clear of blue's core and tower
const FPS := 30.0
const HOLD := 12 ## frames standing still at the start
const HOLD_END := 1.5 ## seconds standing still at the end

var path: Array = LANE_PATH


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir()
	if args.size() > 1 and args[1] == "tower":
		path = TOWER_PATH
	var arena: Node3D = load(SCENE).instantiate()
	root.add_child(arena)
	await process_frame # the arena builds its structures on its first frame
	if args.has("felled"): # the wrecked tower at the path's end
		arena.set_structure_down("RedTower", true)
	var player: Node3D = arena.get_node("Player")
	for g in ["map_units", "vision_sources"]:
		player.add_to_group(g)
	player.set_meta("team", "blue")
	player.set_meta("is_player", true)
	player.set_meta("unit_kind", "machine")
	player.set_meta("vision_radius", 12.0)
	var cam = arena.get_node("Camera")
	var total := 0.0
	for i in path.size() - 1:
		total += path[i].distance_to(path[i + 1])
	var yaw := 0.0
	var frame := 0
	var dist := 0.0
	while dist < total + SPEED * HOLD_END:
		var p := _at(minf(dist, total))
		var ahead := _at(minf(dist, total) + 6.0) - p
		var want := atan2(-ahead.x, -ahead.y)
		yaw = want if frame == 0 else lerp_angle(yaw, want, 0.08)
		player.global_position = Vector3(p.x, 0, p.y)
		cam.yaw_degrees = rad_to_deg(yaw)
		cam.snap()
		await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		img.save_jpg(out.path_join("f_%04d.jpg" % frame), 0.92)
		frame += 1
		if frame > HOLD:
			dist += SPEED / FPS
	print("arena_clip: %d frames to %s" % [frame, out])
	quit(0)


func _at(d: float) -> Vector2:
	for i in path.size() - 1:
		var a: Vector2 = path[i]
		var b: Vector2 = path[i + 1]
		var seg := a.distance_to(b)
		if d <= seg or i == path.size() - 2:
			return a + (b - a).normalized() * d
		d -= seg
	return path[-1]
