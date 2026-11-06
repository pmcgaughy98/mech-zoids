extends SceneTree
## Frames of the plaza beacon in a running arena_play. Map design lane, 2026-11-05. Needs a window and no other
## Godot: Godot --fixed-fps 60 --path . -s res://tools/map/beacon_shot.gd -- <out.png>
## Saves two 1280 x 720 frames stacked:
## - the beacon brought up early, with the player on it and the fill held at half (beam, ring, the HUD's
##   "BEACON UP" row with its fill line, the minimap's plus);
## - the player at the other team's tower after a take, with the tower switched off (its look, and the HUD's
##   countdown when game feel's MatchStructure.off_left exists).
## Those states are set for the picture only. Edits nothing.


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir() + "/beacon_shot.png"
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	for i in 2:
		await process_frame
	var d = play.director
	for i in 600:
		if d.ready_to_play:
			break
		await physics_frame
	var bs := get_nodes_in_group("arena_beacons")
	if bs.is_empty():
		print("beacon_shot: no beacon")
		quit(1)
		return
	var b = bs[0]
	var p = play.player
	b.up_at = b.now() + 0.2
	p.global_position = b.global_position + Vector3(0, 0, 2.0)
	for i in 50:
		await physics_frame
	b.set_physics_process(false)
	b.capturing = p.team
	b.progress = 0.5
	b._show()
	await process_frame
	var a := await _grab()

	b._take(p.team)
	var other: String = "red" if p.team == "blue" else "blue"
	var tw = d.structures.get(other.capitalize() + "Tower")
	if tw != null:
		if tw.get("off_left") != null:
			tw.off_left = 24.0
		tw.arena.set_structure_off(tw.marker, true)
		var to: Vector3 = tw.global_position
		var home: Vector3 = d.structures.get(p.team.capitalize() + "Core").global_position
		p.global_position = to + (home - to).normalized() * 9.0
	for i in 50:
		await physics_frame
	var c := await _grab()
	print("beacon_shot: taker=", b.last_taker, " off_left=", tw.get("off_left") if tw else null, " feed=", play.hud.feed_lines())

	var sheet := Image.create(1280, 1440, false, Image.FORMAT_RGB8)
	sheet.blit_rect(a, Rect2i(0, 0, 1280, 720), Vector2i.ZERO)
	sheet.blit_rect(c, Rect2i(0, 0, 1280, 720), Vector2i(0, 720))
	sheet.save_png(out)
	print("beacon_shot: saved ", out)
	quit(0)


func _grab() -> Image:
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	if img.get_size() != Vector2i(1280, 720):
		img.resize(1280, 720, Image.INTERPOLATE_NEAREST)
	return img
