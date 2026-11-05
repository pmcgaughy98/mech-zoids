extends SceneTree
## A chase-camera frame for the HUD mock-up. Map design lane, 2026-11-05. Needs a window and no other Godot running:
## Godot --fixed-fps 60 --path . -s res://tools/map/hud_mock_shot.gd -- <out_dir>
## Writes to <out_dir>: frame_b.png (minimap bottom right, as in game), frame_a.png (the minimap moved to the upper
## right), anchors.json (viewport points: the player's overhead bar, the player's chest, the red tower's head) and
## port_<kind>.png, one standing frame per machine, for stand-in portraits. Edits nothing.
## tools/map/hud_mock.py paints the HUD over these.

const SCENE := "res://scenes/moba3d/arena_blockout.tscn"
const AT := Vector2(2.0, -30.5) ## the rhino, in blue's half, about 11 m short of red's tower
const LOOK := Vector2(0.0, -41.0)
const MAP_TOP := 21.0 ## variant A: the minimap's top edge, under the enemy frames (base pixels)


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir()
	var arena: Node3D = load(SCENE).instantiate()
	root.add_child(arena)
	await process_frame
	var player: Node3D = arena.get_node("Player")
	player.global_position = Vector3(AT.x, 0, AT.y)
	for g in ["map_units", "vision_sources"]:
		player.add_to_group(g)
	player.set_meta("team", "blue")
	player.set_meta("is_player", true)
	player.set_meta("unit_kind", "machine")
	player.set_meta("vision_radius", 12.0)
	var rig = arena.get_node("Camera")
	var d: Vector2 = (LOOK - AT).normalized()
	rig.yaw_degrees = rad_to_deg(atan2(-d.x, -d.y))
	rig.snap()
	for i in 30:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out + "/frame_b.png")

	var cam := root.get_camera_3d()
	var tower: Node3D = arena.find_child("RedTower", true, false)
	var vp := root.get_visible_rect().size
	var anchors := {
		"viewport": [vp.x, vp.y],
		"bar": _pt(cam, player.global_position + Vector3(0, 2.3, 0)),
		"chest": _pt(cam, player.global_position + Vector3(0, 1.0, 0)),
		"tower": _pt(cam, tower.global_position + Vector3(0, 3.2, 0)) if tower else [],
	}
	var layer := arena.find_child("Minimap", true, false)
	var map: Control = layer.get_node("Map") if layer else null
	if map:
		map.set_process(false)
		map.position = Vector2(floorf(vp.x - map.size.x - map.margin), MAP_TOP)
		map.queue_redraw()
		anchors["map"] = [map.size.x, map.size.y]
	for i in 6:
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(out + "/frame_a.png")

	var dir := DirAccess.open("res://art/machines")
	for kind in dir.get_directories():
		var tres := "res://art/machines/%s/%s_frames.tres" % [kind, kind]
		if not ResourceLoader.exists(tres):
			continue
		var sf: SpriteFrames = load(tres)
		var names := sf.get_animation_names()
		var pick := ""
		for n in names:
			var s := String(n)
			if "idle" in s:
				pick = s
				if s.ends_with("_s") or s.ends_with("_0") or "south" in s:
					break
		if pick == "" and names.size() > 0:
			pick = names[0]
		var tex := sf.get_frame_texture(pick, 0)
		if tex == null:
			continue
		var img := tex.get_image()
		if img.is_compressed():
			img.decompress()
		img.save_png(out + "/port_%s.png" % kind)
		print("portrait ", kind, " <- ", pick, " (", names.size(), " anims, first: ", names.slice(0, 4), ")")

	var f := FileAccess.open(out + "/anchors.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(anchors))
	f.close()
	print("hud_mock_shot: saved to ", out, " ", anchors)
	quit(0)


func _pt(cam: Camera3D, p: Vector3) -> Array:
	var s := cam.unproject_position(p)
	return [s.x, s.y]
