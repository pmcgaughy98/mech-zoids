extends SceneTree
## Frames of the match HUD in a running arena_play. Map design lane, 2026-11-05. Needs a window and no other Godot:
## Godot --fixed-fps 60 --path . -s res://tools/map/hud_shot.gd -- <out.png>
## Lets the 3 v 3 play itself for 35 s, then saves two 1280 x 720 frames stacked: the match as it stands, then the
## player walked into red's tower range at low health, with two kit slots cooling, a feed line and the mouse aim put
## under the player bar. Those states are set for the picture only. Edits nothing.


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var out: String = args[0] if args.size() > 0 else OS.get_user_data_dir() + "/hud_shot.png"
	var play: Node = load("res://scenes/moba3d/arena_play.tscn").instantiate()
	root.add_child(play)
	for i in 2:
		await process_frame
	var d = play.director
	var p = play.player
	for i in 600:
		if d.ready_to_play:
			break
		await physics_frame
	# first, before any wave or bot reaches red's tower: the player in its range at low health
	var tower: Node3D = d.structures["RedTower"]
	p.global_position = tower.global_position + Vector3(0, 0, 6.0)
	p.hp = p.max_hp * 0.25
	p.cooldowns["2"] = 4.0
	p.cooldowns["4"] = 38.0
	d.feed.emit("Blue fennec destroyed Red gorilla", MatchTeams.COLOURS["blue"])
	p.aim_screen_override = Vector2(170, 166)
	for i in 40:
		await physics_frame
	var b := await _grab()
	print("hud_shot: warning=", play.hud.warning, " alive=", p.alive, " feed=", play.hud.feed_lines())
	p.aim_screen_override = null
	p.hp = p.max_hp
	for i in 35 * 60:
		await physics_frame
	var a := await _grab()

	var sheet := Image.create(1280, 1440, false, Image.FORMAT_RGB8)
	sheet.blit_rect(a, Rect2i(0, 0, 1280, 720), Vector2i.ZERO)
	sheet.blit_rect(b, Rect2i(0, 0, 1280, 720), Vector2i(0, 720))
	sheet.save_png(out)
	print("hud_shot: saved ", out)
	quit(0)


func _grab() -> Image:
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.convert(Image.FORMAT_RGB8)
	if img.get_size() != Vector2i(1280, 720):
		img.resize(1280, 720, Image.INTERPOLATE_NEAREST)
	return img
