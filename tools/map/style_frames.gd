extends SceneTree
## Style frames for the arena's look. Map design lane, 2026-11-04. Needs a window:
## Godot --fixed-fps 60 --path . -s res://tools/map/style_frames.gd
## Builds the arena once per theme (arena_blockout.gd's THEMES) and grabs the same chase-camera shot in each: the
## rhino in the plaza at the red lane's mouth, looking down the lane to red's tower, with red's minion drones coming
## out of the lane and two of blue's beside the rhino (the approved drone is the style anchor). Saves one full-size
## frame per theme to docs/plan/moba-style-<theme>-2026-11-04.png. tools/map/style_sheet.py lays them out with names.
## Edits nothing.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const THEMES := ["foundry"] 
const AT := Vector3(3, 0, -8) ## the rhino, in the plaza
const LOOK := Vector2(1, -40) ## toward red's tower, down the lane
const RED_DRONES := [Vector3(5.2, 0, -16.5), Vector3(7.0, 0, -18.8), Vector3(3.8, 0, -19.6)]
const BLUE_DRONES := [Vector3(1.4, 0, -6.6), Vector3(4.8, 0, -6.2)]


func _initialize() -> void:
	for theme in THEMES:
		var arena: Node3D = load(SCENE).instantiate()
		arena.theme = theme
		root.add_child(arena)
		await process_frame
		var player: Node3D = arena.get_node("Player")
		var cam = arena.get_node("Camera")
		player.global_position = AT
		var d := (LOOK - Vector2(AT.x, AT.z)).normalized()
		cam.yaw_degrees = rad_to_deg(atan2(-d.x, -d.y))
		cam.snap()
		var rhino: AnimatedSprite3D = arena.get_node("Player/Sprite")
		if rhino.has_method("show_facing"):
			rhino.show_facing(Vector3(d.x, 0, d.y), cam.global_basis, false)
		for team in ["red", "blue"]:
			for p in (RED_DRONES if team == "red" else BLUE_DRONES):
				var drone := DirectionalSprite3D.new()
				drone.sprite_frames = load("res://art/machines/minion/minion_%s_frames.tres" % team)
				drone.canvas_height = 96
				drone.feet_edge_row = 88
				drone.size_class = "S"
				var holder := Node3D.new()
				arena.add_child(holder)
				holder.global_position = p
				holder.add_child(drone)
				drone.play(&"idle_s")
				var face := Vector3(0, 0, 1) if team == "red" else Vector3(d.x, 0, d.y)
				drone.show_facing(face, cam.global_basis, false)
		for i in 10:
			await process_frame
		await RenderingServer.frame_post_draw
		var img: Image = root.get_texture().get_image()
		img.convert(Image.FORMAT_RGB8)
		var out := "res://docs/plan/moba-style-%s-2026-11-04.png" % theme
		img.save_png(ProjectSettings.globalize_path(out))
		print("  %-8s saved %s (%d x %d), camera at %s" % [theme, out, img.get_width(), img.get_height(), cam.global_position.snapped(Vector3.ONE * 0.1)])
		arena.queue_free()
		await process_frame
		await process_frame
	quit(0)
